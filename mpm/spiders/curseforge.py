# -*- coding: utf-8 -*-

from urllib import urlencode
from urlparse import urljoin, urlparse, parse_qs, urlsplit, urlunsplit

from scrapy.spiders import Spider
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.http import Request

from ..loaders import ModItemLoader, ModFileItemLoader
from ..items import ModItem, ModFileItem


class CurseforgeSpider(Spider):
    """ Spider for the curseforge repository
    
    Generate :class:`ModItem` elements for mods in
    the curseforge online archive.


    Curseforge page structure
    +++++++++++++++++++++++++

    The curseforge domain tree is as follows::

        - mc-mods
        | - mc-addons
        | - adventure-rpg
        \ - ...

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
        Extract paginated mods and mod links
        in the first page
        
        Note: it is assumed that urls in the pagination are of the form
        ``"/category?page=<integer>[&other]"``
        """
        for request in self.parse_mod_list_page(response):
            yield request

        for url in self._pagination_iter(response):
            yield Request(url=url, callback=self.parse_mod_list_page)

    def parse_mod_list_page(self, response):
        """
        Extract urls in a mod list page.
        
        For each page, the urls to the mod pages are parsed;
        the :meth:`parse_mod` method will be called to handle mod pages.
        """
        mod_links = response.xpath("//ul[contains(@class, 'listing-project')]/li/div/a/@href")
        for url in mod_links.extract():
            full_url = urljoin(response.url, url)
            self.logger.info("Found mod URL {0}".format(full_url))
            yield Request(url=full_url, callback=self.parse_mod_page)

    def parse_mod_page(self, response):
        """
        Extract mod informations from a response.

        A mod item is partially created and then passed to the license
        parsing method :meth:`parse_mod_license` which adds the license
        to the item and finally returns the item.
        A second request is generated to extract files for the mod,
        the files will be stored in a separate item that will be
        associated with the mod item in the item pipeline.
        """
        loader = ModItemLoader(item=ModItem(), response=response)
        loader.add_xpath("name", "//h1[@class='project-title']//span/text()")
        
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
        
        The license is attached to the pre-parsed item given in the
        response meta; the finished :class:`ModItem` is then returned.
        """
        item = response.meta["item"]
        loader = ModItemLoader(item=item, response=response)

        loader.add_value("mod_license", response.body)
        item = loader.load_item()
        yield item

    def parse_mod_files_page(self, response):
        """
        """
        loader = ModFileItemLoader(item=ModFileItem(), response=response, url=response.url)

        loader.add_value("mod", response.meta["item"]["name"])
        loader.add_xpath("name", "//div[contains(@class,'project-file-name-container')]//text()")
        loader.add_xpath("release", "//td[contains(@class,'project-file-release-type')]/div/@title")
        loader.add_xpath("mc_version", "//td[contains(@class,'project-file-game-version')]//text()")
        loader.add_xpath("size", "//td[contains(@class,'project-file-size')]/text()")
        loader.add_xpath("upload_date", "//td[contains(@class,'project-file-date-uploaded')]/abbr/@data-epoch")
        loader.add_xpath("downloads", "//td[contains(@class,'project-file-downloads')]/text()")
        loader.add_xpath("download_url", "//div[contains(@class,'project-file-download-button')]//@href")
        yield loader.load_item()
        
    def parse_mod_files(self, response):
        """
        Extract mod files from the files list page
        
        Each mod version file is indexed by this method and other
        related ones. The :class:`ModFileItem` instances are returned
        for each mod file found and :class:`Request`s are returned for
        each other mod files page to be crawled.
        """
        for url in self._pagination_iter(response):
            yield Request(url=url, callback=self.parse_mod_files_page)
        
        for item in self.parse_mod_files_page(response):
            yield item
