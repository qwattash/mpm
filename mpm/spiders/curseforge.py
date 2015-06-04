# -*- coding: utf-8 -*-

from urllib import urlencode
from urlparse import urljoin, urlparse, parse_qs, urlsplit, urlunsplit

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.http import Request

from ..loaders import ModItemLoader
from ..items import ModItem

class CurseforgeSpider(CrawlSpider):
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
    allowed_domains = []
    start_urls = []

    rules = [
        Rule(LxmlLinkExtractor(restrict_xpaths="//ul[contains(@class, "\
                               "'listing-game-category')]//li/a"),
                               callback="parse_first_category")
    ]

    def parse_first_category(self, response):
        """
        Extract paginated category mods and mod links
        in the first category page
        
        Note: it is assumed that urls in the pagination are of the form
        ``"/category?page=<integer>[&other]"``
        """
        mod_links = response.xpath("//ul[contains(@class, 'listing-project')]/li/div/a/@href")
        for url in mod_links.extract():
            full_url = urljoin(response.url, url)
            yield Request(url=full_url, callback="parse_mod")

        # try to guess the page range from urls in the pagination footer
        paginator_urls = response.xpath("//ul[contains(@class, 'paging-list')]/li/a/@href")
        # assume that the urls are 
        page_numbers = []

        # extract page numbers from the paginator in the footer
        for url in paginator_urls.extract():
            parsed = urlparse(url)
            query = parse_qs(parsed.query)
            if "page" in query:
                page_numbers.append(int(query["page"][0]))

        # url and query params used to build request objects
        scheme, netloc, path, query, fragment = urlsplit(url)
        base_page_query = parse_qs(query)

        # page range to request
        first_page = min(page_numbers)
        last_page = max(page_numbers)
        for page in range(first_page, last_page + 1):
            base_page_query["page"] = page
            query_string = urlencode(base_page_query)
            query = query_string
            url = urlunsplit((scheme, netloc, path, query, fragment))
            url = urljoin(response.url, url)
            yield Request(url=url, callback="parse_category")

    def parse_category(self, response):
        """
        Extract urls in a mod category page
        """
        return None

    def parse_mod(self, response):
        """
        Extract mod informations from a response
        """
        loader = ModItemLoader(item=ModItem(), response=response)
        loader.add_xpath("name")
        return loader.load_item()
