"""
Curseforge crawler tests.

Tests for the curseforge crawling are marked as `crawl_curse`
"""

from __future__ import absolute_import

import pytest
import urlparse

from datetime import date
from scrapy.http import Request

from mpm.items import ModItem, ModFileItem

from helpers import assert_parse_requests, scrapy_response_from_file, curse_spider


expected_urls_index = ["/mc-mods/74072-tinkers-construct",
                       "/mc-mods/222213-codechickencore",
                       "/mc-mods/222211-notenoughitems",
                       "/mc-mods?page=2",
                       "/mc-mods?page=3",
                       "/mc-mods?page=4",
                       "/mc-mods?page=5",
                       "/mc-mods?page=6",
                       "/mc-mods?page=7"]

expected_urls_list_page = ["/mc-mods/74072-tinkers-construct",
                           "/mc-mods/222213-codechickencore",
                           "/mc-mods/222211-notenoughitems"]

expected_urls_mod = ["/mc-mods/74072-tinkers-construct/files",
                     "/mc-mods/74072-tinkers-construct/license"]

expected_urls_files = ["/mc-mods/74072-tinkers-construct/files?page=2",
                       "/mc-mods/74072-tinkers-construct/files?page=3"]

@pytest.mark.crawl_curse
@pytest.mark.parametrize("response", [
    scrapy_response_from_file("http://foo.org", "tests/resources/curseforge_mcmods_base.html"),
    scrapy_response_from_file("http://foo.org", "tests/resources/curseforge_mcmods_full.html"),
])
def test_curseforge_index_urls(response, curse_spider):
    """
    Test :meth:`CurseforgeSpider.parse` 

    The resulting :class:`scrapy.http.Request` instances should link to:

    - all the mod pages listed in the first index page 
    - all the following mod list pages identified from the pagination 
    menu
    """
    parsed = iter(curse_spider.parse(response))
    urls = [urlparse.urljoin(response.url, url) for url in expected_urls_index]
    assert_parse_requests(parsed, urls)


@pytest.mark.crawl_curse
@pytest.mark.parametrize("response", [
    scrapy_response_from_file("http://foo.org", "tests/resources/curseforge_mcmods_base.html"),
    scrapy_response_from_file("http://foo.org", "tests/resources/curseforge_mcmods_full.html"),
])
def test_curseforge_mod_list_page(response, curse_spider):
    """
    Test :meth:`CurseforgeSpider.parse_mod_list_page`
    
    The resulting :class:`scrapy.http.Request` instances link to
    the mod pages of the mods listed in the mod list page returned in
    the response.
    """
    parsed = iter(curse_spider.parse_mod_list_page(response))
    urls = [urlparse.urljoin(response.url, url) for url in expected_urls_list_page]
    assert_parse_requests(parsed, urls)


@pytest.mark.crawl_curse
@pytest.mark.parametrize("response", [
    scrapy_response_from_file("http://foo.org", "tests/resources/curseforge_mod_base.html"),
    scrapy_response_from_file("http://foo.org", "tests/resources/curseforge_mod_full.html"),
])
def test_curseforge_mod_page(response, curse_spider):
    """
    Test :meth:`CurseforgeSpider.parse_mod_page`
    
    The spider returns two requests:

    - one used to fetch mod files
    - one to complete the mod item generation by adding the license
    """
    parsed = curse_spider.parse_mod_page(response)
    parsed = list(parsed)
    urls = [urlparse.urljoin(response.url, url) for url in expected_urls_mod]
    
    # check request urls
    assert_parse_requests(parsed, urls)

    # check request meta
    assert parsed[0].meta["item"] == parsed[1].meta["item"]

    # check the item extracted so far
    item = parsed[0].meta["item"]
    assert item["name"] == "Tinkers Construct"
    assert item["description"] == "Description FAQ\nA link "\
        "http://link_a Minefactory Reloaded end."
    assert item["created"] == date(2014, 2, 8)
    assert item["updated"] == date(2015, 5, 10)
    assert item["downloads"] == 1000
    assert (sorted(item["categories"]) ==
            sorted(["armor", "weapons", "tools", "technology", "processing"]))
    assert sorted(item["authors"]) == sorted(["mDiyo", "boni", "jadedcat"])
    assert item["source_url"] == "https://github.com/source_url"
    assert item["donation_url"] == "https://www.paypal.com/donation_url"
    assert item["mod_url"] == "http://foo.org"


@pytest.mark.crawl_curse
@pytest.mark.parametrize("response", [
    scrapy_response_from_file("http://foo.org", "tests/resources/curseforge_mod_license.html"),
])
def test_curseforge_mod_license_and_finalization(response, curse_spider):
    """
    Test :meth:`CurseforgeSpider.parse_mod_license`

    The spider should finish to build a :class:`ModItem` and return it.
    """
    response.meta["item"] = ModItem()
    parsed = curse_spider.parse_mod_license(response)

    parsed = list(parsed)
    assert len(parsed) == 1
    
    item = list(parsed)[0]
    assert item["mod_license"] == "Creative Commons Full Text"


@pytest.mark.crawl_curse
@pytest.mark.parametrize("response", [
    scrapy_response_from_file("http://foo.org", "tests/resources/curseforge_mod_files_base.html"),
    scrapy_response_from_file("http://foo.org", "tests/resources/curseforge_mod_files_full.html"),
])
def test_curseforge_mod_files_list_page(response, curse_spider):
    """
    Test :meth:`CurseforgeSpider.parse_mod_files`
    
    The spider generates:
    
    - :class:`mpm.items.ModFileItem` instances for each mod file download
    url found
    - :class:`scrapy.http.Request` linking to other mod file list
    pages from the pagination menu
    """
    # setup item given in response meta
    mod_item = ModItem()
    mod_item["name"] = "Mod Name"
    response.meta["item"] = mod_item
    
    parsed = list(curse_spider.parse_mod_files(response))

    items = filter(lambda i: type(i) == ModFileItem, parsed)
    requests = filter(lambda i: type(i) != ModFileItem, parsed)

    urls = [urlparse.urljoin(response.url, url) for url in expected_urls_files]
    assert_parse_requests(requests, urls)
    
    assert len(items) == 1
    item = items[0]
    
    assert item["mod"] == "Mod Name"
    assert item["name"] == "Mod_file_1.6.4.jar"
    assert item["release"] == "alpha"
    assert item["mc_version"] == "1.6.4"
    assert item["size"] == 10.5
    assert item["upload_date"] == date(2015, 7, 6)
    assert item["downloads"] == 1000
    assert item["download_url"] == "http://foo.org/mc-mods/download_url"
