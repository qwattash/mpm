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
from urlparse import urljoin

from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, Join, Compose, Identity



def normalize_blanks(value):
    """
    Remove extra spaces in the data given by the loader

    :param value: list of data strings
    :type value: list
    :return: the modified data list
    :rtype: list
    """
    # pylint: disable=missing-docstring
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


def filter_empty_lines(value):
    """
    Remove empty lines to compact the text, multiple empty lines are
    collapsed into a single empty line, single lines are removed.
    Empty lines at the beginning and the end are stripped.

    :param value: list of data strings
    :type value: list
    :return: the data list without empty lines
    :rtype: list
    """
    filtered = []
    empty_found = False
    for line in value:
        if line == "\n":
            if not empty_found:
                filtered.append(line)
                empty_found = True
        else:
            empty_found = False
            filtered.append(line)
    # strip leading and trailing empty lines
    if len(filtered) > 0:
        if filtered[0] == "\n":
            del filtered[0]
        if filtered[-1] == "\n":
            del filtered[-1]
    return filtered

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


def normalize_epoch(value):
    """
    Parse epoch timestamps in the input list as
    :class:`datetime.date` objects.

    If the string can not be parsed the output for that string is None.
    :param value: list of input strings
    :type value: list
    :return: list of either :class:`datetime.date` or None objects
    :rtype: list
    """
    date_value = []
    for val in value:
        try:
            date_time = datetime.fromtimestamp(int(val))
            date_value.append(date_time.date())
        except ValueError:
            date_value.append(None)
    return date_value


def normalize_int(value):
    """
    Parse an integer string into a python int

    :param value: list of strings to parse
    :type value: list
    :return: list of either integers or None
    :rtype: list
    """
    # pylint: disable=missing-docstring
    def _int(item):
        try:
            return int(re.sub("[,.]", "", item))
        except ValueError:
            return None

    return [_int(val) for val in value]


def normalize_url(value, loader_context):
    """
    Parse a relative url list and make it absolute

    :param value: list of input urls
    :type value: list
    :param loader_context: context of the item loader
    :type loader_context: dict
    :return: absolute url for each input url based on the context
    url value
    :rtype: list
    """
    base_url = loader_context.get("url")
    return [urljoin(base_url, val) for val in value]


class Substring(object): # pylint: disable=too-few-public-methods
    """
    Callable filter that extracts substrings from the loader data
    """

    def __init__(self, regex):
        """
        Initialise the callable with the target regex

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


class Split(object): # pylint: disable=too-few-public-methods
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
        split_lists = [val.split(self.sep) for val in value if val]
        # chain each resulting list and remove None values
        return [val for val in chain(*split_lists) if val is not None]


class JoinNormalizeNewlines(Join): # pylint: disable=too-few-public-methods
    """
    Join values in an array as the normal join function except that
    when newlines are found no separator is added
    """

    def __call__(self, values):
        # create an helper function for the reduction
        # pylint: disable=missing-docstring
        def _join(acc, val):
            if val.endswith("\n") or acc.endswith("\n") or acc == "":
                return acc + val
            else:
                return acc + self.separator + val
        return reduce(_join, values, "")


class ModItemLoader(ItemLoader): # pylint: disable=too-few-public-methods
    """
    Loader for :class:`items.ModItem` objects used in
    :class:`spiders.curseforge.CurseforgeSpider`
    """

    default_output_processor = TakeFirst()
    default_input_processor = TakeFirst()

    name_in = Compose(normalize_line_breaks, normalize_blanks)

    description_in = Compose(normalize_line_breaks, normalize_blanks)
    description_out = JoinNormalizeNewlines()

    created_in = Compose(normalize_date)

    updated_in = Compose(normalize_date)

    downloads_in = Compose(normalize_int)

    categories_in = Compose(Substring(".*/([\\w-]+)$"), Split("-"), set)
    categories_out = Identity()

    authors_in = Identity()
    authors_out = Identity()

    mod_license_in = Compose(partial(map, remove_tags), partial(map, string.strip))


class ModFileItemLoader(ItemLoader): # pylint: disable=too-few-public-methods
    """
    Loader for :class:`items.ModFileItem` objects used in
    :class:`spiders.curseforge.CurseforgeSpider`
    """

    default_output_processor = TakeFirst()
    default_input_processor = TakeFirst()

    name_in = partial(map, string.strip)

    release_in = partial(map, string.lower)

    mc_version_in = partial(map, string.strip)

    size_in = Compose(partial(map, string.strip), Substring("(.*) +(K|M|G)B$"), partial(map, float))

    upload_date_in = Compose(normalize_epoch)

    downloads_in = Compose(normalize_int)

    download_url_in = Compose(normalize_url)

    changelog_in = Compose(normalize_line_breaks, normalize_blanks, filter_empty_lines)
    changelog_out = JoinNormalizeNewlines()
