# -*- coding: utf-8 -*-

import urlparse

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
                               callback="parse_mod")
    ]

    def parse_mod(self, response):
        """
        Extract mod informations from a response
        """
        loader = ModItemLoader(item=ModItem(), response=response)
        loader.add_xpath("name")
        return loader.load_item()
