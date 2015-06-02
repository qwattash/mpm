# -*- coding: utf-8 -*-

import scrapy
import urlparse

from ..loaders import ModItemLoader
from ..items import ModItem

class CurseforgeSpider(scrapy.Spider):
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
    # allowed_domains = []
    # start_urls = []

    def parse(self, response):
        """
        Extract mod category urls from the main page
        """
        link_selector = response.xpath("//ul[contains(@class, "\
                                       "'listing-game-category')]//li/a/@href")
        
        for url in link_selector.extract():
            final_url = urlparse.urljoin(response.url, url)
            yield scrapy.Request(final_url, callback=self.parse)

    def parse_mod(self, response):
        """
        Extract mod informations from a response
        """
        loader = ModItemLoader(item=ModItem(), response=response)
        loader.add_xpath("name")
        return loader.load_item()
