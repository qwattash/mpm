"""
Item loaders for the mpm core.

Currently only :class:`ModItem` items are loaded.
"""

from __future__ import absolute_import, unicode_literals

import string
import re

from datetime import datetime
from itertools import chain
from functools import partial
from w3lib.html import remove_tags

from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import TakeFirst, Join, Compose, Identity

__all__ = ("ModItemLoader",)

def normalize_blanks(value):
    """
    Remove extra spaces in the data given by the loader
    :param value: list of data strings
    :type value: list
    :return: the modified data list
    :rtype: list
    """
    def _norm(norm):
        norm = re.sub("[ \t]+", " ", norm)
        norm = re.sub("^[ \t]+", "", norm)
        norm = re.sub("[ \t]+$", "", norm)
        return norm
    return [_norm(item) for item in value]


def normalize_line_breaks(value):
    """
    This is useful to preserve newlines when parsing paragraph data;
    <br> tags are turned into \n for each item in the input list
    :param value: list of data strings
    :type value: list
    :return: the modified data list
    :rtype: list
    """
    return [re.sub("<br>", "\n", item) for item in value]


def normalize_date(value):
    """
    Parse strings in the input list as :class:`datetime.date` objects.
    If the string can not be parsed the output for that string is None.
    :param value: list of input strings
    :type value: list
    :return: list of either :class:`datetime.date` or None objects
    :rtype: list
    """
    formats = ["%b %d, %Y"]
    date_value = []
    for val in value:
        parsed_date = None
        for date_format in formats:
            try:
                parsed_date = datetime.strptime(val, date_format)
            except ValueError:
                continue
            else:
                break
        date_value.append(parsed_date.date())
    return date_value


def normalize_int(value):
    """
    Parse an integer string into a python int
    :param value: list of strings to parse
    :type value: list
    :return: list of either integers or None
    :rtype: list
    """
    def _int(item):
        try:
            return int(re.sub("[,.]", "", item))
        except ValueError:
            return None
        
    return map(_int, value)
        

class substring(object):
    """
    Callable filter that extracts substrings from the loader data
    """
    
    def __init__(self, regex):
        """
        :param regex: regular expression to match, the regex must have
        a group expression to mark the part to be extracted
        :type regex: str
        """
        self.regex = regex

    def __call__(self, value):
        """
        Extract a substring matching the given regex from each
        string in the input list
        :param value: list of input strings
        :type value: list
        :return: list of either the matched substring or None
        :rtype: list
        """
        sub_value = []
        for val in value:
            match = re.match(self.regex, val)
            if match:
                sub_value.append(match.group(1))
            else:
                sub_value.append(None)
        return sub_value

class split(object):
    """
    Callable filter that splits loader data
    """

    def __init__(self, sep):
        """
        :param sep: separator
        :type sep: str
        """
        self.sep = sep

    def __call__(self, value):
        """
        Split each string in the input string list and concatenate 
        the resulting lists
        :param value: list of input strings
        :type value: list
        :return: list of strings after splitting each one
        :rtype: list
        """
        # split each input string
        split_lists = map(lambda val: val.split(self.sep) if val else None, value)
        # chain each resulting list and remove None values
        return filter(lambda val: val is not None, chain(*split_lists))


class JoinNormalizeNewlines(Join):
    """
    Join values in an array as the normal join function except that
    when newlines are found no separator is added
    """

    def __call__(self, values):
        # create an helper function for the reduction
        def _join(acc, val):
            if val.endswith("\n") or acc.endswith("\n") or acc == "":
                return acc + val
            else:
                return acc + self.separator + val
        return reduce(_join, values, "")

    
class ModItemLoader(ItemLoader):
    """
    Loader for :class:`items.ModItem` objects from 
    :class:`spiders.curseforge.CurseforgeSpider`
    """

    default_output_processor = TakeFirst()
    default_input_processor = TakeFirst()

    description_in = Compose(normalize_line_breaks, normalize_blanks)
    description_out = JoinNormalizeNewlines()

    created_in = Compose(normalize_date)
    
    updated_in = Compose(normalize_date)

    downloads_in = Compose(normalize_int)

    categories_in = Compose(substring(".*/([\w-]+)$"), split("-"), set)
    categories_out = Identity()

    authors_in = Identity()
    authors_out = Identity()

    mod_license_in = Compose(partial(map, remove_tags), partial(map, string.strip))
