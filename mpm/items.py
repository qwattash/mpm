# -*- coding: utf-8 -*-
"""
Define item models for the scraped items.

The item in the release version will probably be an adapter on
the SQLAlchemy Mod model
"""

import scrapy


class ModItem(scrapy.Item):
    """
    Define the basic informations for a mod

    A mod item defines the model for a mod, this representation is the
    input to various operations can be performed by the modpack designer.
    """

    name = scrapy.Field()
    """ Mod name """

    author = scrapy.Field()
    """ Mod author(s) """
    url = scrapy.Field()
    """ Download URL for the mod """

    version = scrapy.Field()
    """ Mod version provided by the download url found """

    minecraft_version = scrapy.Field()
    """ The Mod support these minecraft versions """

    mod_license = scrapy.Field()
    """ Mod license terms and modpack policy """

    smp = scrapy.Field()
    """ The mod supports multiplayer and must be included in the server build """
