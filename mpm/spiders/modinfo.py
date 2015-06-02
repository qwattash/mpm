# -*- coding: utf-8 -*-

import scrapy

class RepositorySpider(scrapy.Spider):
    """ Base Spider class
    
    Spider used to retrieve mod informations from a domain that provides
    and aggregation of mod description pages. An example could be curseforge.
    This spider does not actually download the mod data but just
    fills the :class:`ModItem`
    """

    # name = ""
    # allowed_domains = []
    # start_urls = []

    def parse(self, response):
        """
        Extract mod informations from a response, if any
        """
        pass
