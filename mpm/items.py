# -*- coding: utf-8 -*-
"""
Define item models for the scraped items.

The item defines a group of attributes common to all mods
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

    description = scrapy.Field()
    """ Mod description """

    authors = scrapy.Field()
    """ Mod author(s) """

    created = scrapy.Field()
    """ Creation date """

    updated = scrapy.Field()
    """ Last update date """

    downloads = scrapy.Field()
    """ Number of downloads """

    categories = scrapy.Field()
    """ Categories and tags for indexing """

    source_url = scrapy.Field()
    """ Sources URL for the mod """

    donation_url = scrapy.Field()
    """ Donations url for the mod """

    mod_url = scrapy.Field()
    """ Mod page url """

    mod_license = scrapy.Field()
    """ Mod license terms and modpack policy """

    smp = scrapy.Field()
    """ The mod supports multiplayer and must be included in the server build """


class ModFileItem(scrapy.Item):
    """
    Define a donwloadable mod file

    Each item represent a mod version available that can be used.
    """

    mod = scrapy.Field()
    """ Name of the mod to which the file is related """

    name = scrapy.Field()
    """ Name of the file """

    release = scrapy.Field()
    """
    Realease informations

    Valid strings are:

    - RELEASE
    - BETA
    - ALPHA
    """

    mc_version = scrapy.Field()
    """ Compatible minecraft version """

    size = scrapy.Field()
    """ File size in MB """

    upload_date = scrapy.Field()
    """ Release date of the file """

    downloads = scrapy.Field()
    """ Number of times the file has been downloaded """

    download_url = scrapy.Field()
    """ URL to be used to download the file """
