"""
Item loaders for the mpm core.

Currently only :class:`ModItem` items are loaded.
"""

from __future__ import absolute_import, unicode_literals

from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import TakeFirst, Join

class ModItemLoader(ItemLoader):
    """
    Loader for :class:`ModItem` objects
    """

    default_output_processor = TakeFirst()
    default_input_processor = TakeFirst()
