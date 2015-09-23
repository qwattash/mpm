# -*- coding: utf-8 -*-

"""
Curseforge Spider
-----------------

This module defines the spider for the curseforge mod repository,
the mod repository structure is explained in the
:class:`CurseforgeSpider` documentation.
"""

from urllib import urlencode
from urlparse import urljoin, urlparse, parse_qs, urlsplit, urlunsplit

from scrapy.spiders import Spider
from scrapy.http import Request

from ..loaders import ModItemLoader, ModFileItemLoader
from ..items import ModItem, ModFileItem


class CurseforgeSpider(Spider):
    """
    Spider for the curseforge repository

    Generate :class:`ModItem` elements for mods in
    the curseforge online archive.


    Curseforge page structure
    +++++++++++++++++++++++++

    The curseforge domain tree is as follows::

        - mc-mods
        | - mc-addons
        | - adventure-rpg
        ` - ...
    """

    name = "curseforge"
    allowed_domains = ["minecraft.curseforge.com"]
    start_urls = ["http://minecraft.curseforge.com/mc-mods"]

    def _get_pagination_range(self, response):
        """
        Return the pagination range assuming the current page
        is the first one.

        :param response: the spider response to be processed
        :type response: scrapy.http.Response
        :return: a 2-tuple containing (min_page, max_page)
        :rtype: tuple
        """
        # try to guess the page range from urls in the pagination menu
        paginator_urls = response.xpath("//ul[contains(@class, 'paging-list')]/li/a/@href")
        # init list of all page numbers found in the menu
        page_numbers = []

        # extract page numbers from the paginator in the footer
        for url in paginator_urls.extract():
            parsed = urlparse(url)
            query = parse_qs(parsed.query)
            if "page" in query:
                page_numbers.append(int(query["page"][0]))

        # page range
        first_page = min(page_numbers)
        last_page = max(page_numbers)
        return (first_page, last_page)

    def _get_pagination_base(self, response):
        """
        Return the pagination url structure as parsed by :func:`urlsplit`

        :param response: the spider response to be processed
        :type response: scrapy.http.Response
        :return: the :func:`urlsplit` return object for a pagination url
        :rtype: tuple
        """

        paginator_urls = response.xpath("//ul[contains(@class, 'paging-list')]/li/a/@href")
        url = paginator_urls.extract()[0]
        # url and query params used to build request objects
        return urlsplit(url)

    def _pagination_iter(self, response):
        """
        Generator of pagination urls for a given spider response

        :param response: the spider response to be processed
        :type response: scrapy.http.Response
        :return: an iterator over the valid pagination urls for a response
        :rtype: iter
        """
        first_page, last_page = self._get_pagination_range(response)
        scheme, netloc, path, query, fragment = self._get_pagination_base(response)

        # get the query part of the url to preserve parameters other than "page"
        base_page_query = parse_qs(query)
        self.logger.info("Found mod list pages {0}-{1}".format(first_page, last_page))

        for page in range(first_page, last_page + 1):
            base_page_query["page"] = page
            query_string = urlencode(base_page_query)
            query = query_string
            url = urlunsplit((scheme, netloc, path, query, fragment))
            url = urljoin(response.url, url)
            yield url

    def parse(self, response):
        """
        Extract paginated mods and mod links in the first page

        :param response: the spider response for the first mod list page
        It is assumed that urls in the pagination are of the form
        ``"/category?page=<integer>[&other]"``
        :type response: scrapy.http.Response
        :return: yield :class:`scrapy.http.Request`s for each paginated
        mod list url and for each mod item in the first page list.
        :rtype: iter
        """
        for request in self.parse_mod_list_page(response):
            yield request

        for url in self._pagination_iter(response):
            yield Request(url=url, callback=self.parse_mod_list_page)

    def parse_mod_list_page(self, response):
        """
        Extract urls in a mod list page.

        For each page, the urls to the mod pages are parsed;
        the :meth:`parse_mod` method will be called to handle mod pages

        :param response: the spider response for a mod list page
        :type response: scrapy.http.Response
        :return: yield :class:`scrapy.http.Request`s for each mod item in
        the mod list page received
        :rtype: iter
        """
        mod_links = response.xpath("//ul[contains(@class, 'listing-project')]/li/div/a/@href")
        for url in mod_links.extract():
            full_url = urljoin(response.url, url)
            self.logger.info("Found mod URL {0}".format(full_url))
            yield Request(url=full_url, callback=self.parse_mod_page)

    def parse_mod_page(self, response):
        """
        Extract mod informations from a mod description page.

        A mod item is partially created and then passed to the license
        parsing method :meth:`parse_mod_license` which adds the license
        to the item and finally returns the item.
        A second request is generated to extract files for the mod,
        the files will be stored in a separate item that will be
        associated with the mod item in the item pipeline.

        :param response: the spider response for a mod detail page
        :type response: scrapy.http.Response
        :return: yield :class:`scrapy.http.Request`s for the mod
        license page and the mod files list page
        :rtype: iter
        """
        loader = ModItemLoader(item=ModItem(), response=response)
        loader.add_xpath("name", "//h1[contains(@class,'project-title')]/a//text()")

        loader.add_xpath("description",
                         "//div[@class='project-description']/p/descendant::text()|"\
                         "//div[@class='project-description']/p/descendant::br|"\
                         "//div[@class='project-description']/p/a"\
                         "[contains(@href, 'http://')]/@href")

        loader.add_xpath("created", "//ul[contains(@class,'project-details')]/"\
                         "li[./div[@class='info-label' and text()='Created']]/"\
                         "div[@class='info-data']//text()")

        loader.add_xpath("updated", "//ul[contains(@class,'project-details')]/"\
                         "li[./div[@class='info-label' and text()='Last Released File']]/"\
                         "div[@class='info-data']//text()")

        loader.add_xpath("downloads", "//ul[contains(@class,'project-details')]/"\
                         "li[./div[@class='info-label' and text()='Total Downloads']]/"\
                         "div[@class='info-data']//text()")

        loader.add_xpath("categories", "//ul[contains(@class,'project-categories')]//a/@href")

        loader.add_xpath("authors", "//ul[contains(@class,'project-members')]//"\
                         "*[contains(@class,'info-wrapper')]//a//text()")

        loader.add_xpath("source_url", "//nav[contains(@class,'project-header-nav')]//"\
                         "a[normalize-space(text())='Source']/@href")

        loader.add_xpath("donation_url", "//nav[contains(@class,'project-header-nav')]//"\
                         "a[normalize-space(descendant::*/text())='Donate']/@href")

        loader.add_xpath("donation_url", "//nav[contains(@class,'project-header-nav')]//"\
                         "a[normalize-space(descendant::*/text())='Donate']/@href")

        item = loader.load_item()

        item["mod_url"] = response.url

        self.logger.info("Created item Mod {0} @ {1}".format(item["name"], response.url))

        # return the request that will extract the files for this mod
        files_url = response.xpath("//nav[contains(@class,'project-header-nav')]//"\
                                   "a[normalize-space(text())='Files']/@href").extract()[0]
        self.logger.info("Request mod files for Mod {0} @ {1}".format(item["name"], files_url))
        yield Request(url=urljoin(response.url, files_url),
                      callback=self.parse_mod_files,
                      meta={"item":item})

        # return the request that will extract the license for the mod
        # and complete the item loading
        license_url = response.xpath("//ul[contains(@class,'project-details')]/"\
                                     "li[./div[@class='info-label' and text()='License']]/"\
                                     "div[@class='info-data']//a/@href").extract()[0]
        self.logger.info("Request mod license for Mod {0} @ {1}".format(item["name"], license_url))
        yield Request(url=urljoin(response.url, license_url),
                      callback=self.parse_mod_license,
                      meta={"item":item})

    def parse_mod_license(self, response):
        """
        Extract mod license from the license page.

        :param response: the response for a mod license page,
        the response mush have a :class:`mpm.items.ModItem` instance
        in its meta["item"] entry
        :type response: scrapy.http.Response
        :return: yield the given parsed :class:`ModItem` with the
        license field updated
        :rtype: iter
        """
        item = response.meta["item"]
        loader = ModItemLoader(item=item, response=response)

        loader.add_value("mod_license", response.body)
        item = loader.load_item()
        yield item

    def parse_mod_files_page(self, response):
        """
        Extract mod files from a files list page.

        :param response: the response for a mod files list page,
        the mod to which the files belong is passed in the response
        meta["item"] as a :class:`mpm.items.ModItem` instance
        :type response: scrapy.http.Response
        :return: yield items for each mod file found
        :rtype: ModFileItem
        """
        # xpath building helpers
        files_table_xpath = response.xpath("//div[contains(@class,'listing-body')]//tbody/tr")
        name_class = "contains(@class,'project-file-name-container')"
        release_class = "contains(@class,'project-file-release-type')"
        version_class = "contains(@class,'project-file-game-version')"
        size_class = "contains(@class,'project-file-size')"
        upload_date_class = "contains(@class,'project-file-date-uploaded')"
        download_class = "contains(@class,'project-file-downloads')"
        download_url_class = "contains(@class,'project-file-download-button')"

        for file_element in files_table_xpath:
            # extract item info for each item
            loader = ModFileItemLoader(item=ModFileItem(),
                                       selector=file_element,
                                       response=response,
                                       url=response.url)
            loader.add_value("mod", response.meta["item"]["name"])
            loader.add_xpath("name", ".//div[%s]//text()" % name_class)
            loader.add_xpath("release", ".//td[%s]/div/@title" % release_class)
            loader.add_xpath("mc_version", ".//td[%s]//text()" % version_class)
            loader.add_xpath("size", ".//td[%s]/text()" % size_class)
            loader.add_xpath("upload_date", ".//td[%s]/abbr/@data-epoch" % upload_date_class)
            loader.add_xpath("downloads", ".//td[%s]/text()" % download_class)
            loader.add_xpath("download_url", ".//div[%s]//@href" % download_url_class)
            file_item = loader.load_item()

            # get the item detail
            file_detail_url_xpath = response.xpath("//div[%s]//@href" % name_class)
            file_detail_url = file_detail_url_xpath.extract()[0]

            # generate the request for the current file item
            yield Request(url=urljoin(response.url, file_detail_url),
                          callback=self.parse_mod_file_details,
                          meta={"item": file_item})


    def parse_mod_files(self, response):
        """
        Extract mod files from the paginated files list pages

        Each mod version file is indexed by this method and other
        related ones, see :meth:`parse_mod_files_page` and
        :meth:`parse_mod_file_details`

        :param response: the response for the first page of the
        mod files paginated list
        :type response: scrapy.http.Response
        :return: yield :class:`scrapy.http.Request` for each paginated
        mod files page and for each file detail page
        :rtype: iter
        """
        for url in self._pagination_iter(response):
            yield Request(url=url, callback=self.parse_mod_files_page)

        for request in self.parse_mod_files_page(response):
            yield request

    def parse_mod_file_details(self, response):
        """
        Extract dependencies, md5 and changelog for a mod release

        Each mod version file has a detail page that is parsed here,
        relevant informations are parsed and added to the partial item
        passed in the response meta.

        :param response: the response for a mod file detail page, the
        response must have a :class:`mpm.items.ModFileItem`
        in its meta["item"]
        :type response: scrapy.http.Response
        :return: yield the :class:`mpm.items.ModFileItem` for the file
        parsed by the methods :meth:`parse_mod_files` and
        :meth:`parse_mod_files_page`
        :rtype: iter
        """
        loader = ModFileItemLoader(item=response.meta["item"], response=response, url=response.url)
        loader.add_xpath("md5", "//span[contains(@class,'md5')]/text()")
        loader.add_xpath("changelog", "//div[contains(@class,'logbox')]//text()")
        dependency_dict = {
            "optional": [],
            "required": []
        }

        # xpath helpers
        dep_class = "contains(@class,'details-related-projects')"
        dep_name_class = "contains(@class,'project-tag-name')"
        dep_type_class = "contains(@class,'optionallibrary')"

        for dep in response.xpath("//section[%s]//li" % dep_class):
            dep_name_match = dep.xpath(".//div[%s]//text()" % dep_name_class).extract()
            dep_name = dep_name_match[0].strip()

            dep_type_match = dep.xpath(".//div[%s]" % dep_type_class).extract()
            dep_type = "optional" if len(dep_type_match) == 1 else "required"

            dependency_dict[dep_type].append(dep_name)

        loader.add_value("dependencies", dependency_dict)
        yield loader.load_item()
