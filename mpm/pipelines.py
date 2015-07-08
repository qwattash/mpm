# -*- coding: utf-8 -*-

"""
Item Pipelines
--------------

This module defines the operations that are performed on crawled items,
the mpm architecture requires the items scraped from a repository to be
stored in the mpm local database in which mods are stored in a
repository-agnostic model.
"""


class MpmPipeline(object):
    """
    Dummy pipeline
    :todo: missing implementation
    """

    def process_item(self, item, spider):
        """
        Dummy pipeline processing
        :todo: missing implementation
        """
        return item
