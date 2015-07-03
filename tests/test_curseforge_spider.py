"""
Curseforge crawler tests.

Tests for the curseforge crawling are marked as `crawl_curse`
"""

from __future__ import absolute_import

import pytest
import urlparse

from datetime import date

from mpm.items import ModItem
from mpm.spiders.curseforge import CurseforgeSpider

from helpers import mock_scrapy_response, assert_parse_requests, scrapy_response_from_file

expected_urls_index = ["/mc-mods",
                       "/mc-mods/mc-addons",
                       "/mc-mods/mc-addons/blood-magic",
                       "/mc-mods/mc-addons/addons-buildcraft",
                       "/mc-mods/adventure-rpg",
                       "/mc-mods/armor-weapons-tools",
                       "/mc-mods/cosmetic",
                       "/mc-mods/technology",
                       "/mc-mods/technology/technology-energy",
                       "/mc-mods/technology/technology-item-fluid-energy-transport",
                       "/mc-mods/world-gen/world-biomes",
                       "/mc-mods/library-api"]

expected_urls_first_category = ["/mc-mods/223628-thaumcraft",
                                "/mc-mods/225643-botania",
                                "/mc-mods/221857-pams-harvestcraft",
                                "/mc-mods/cosmetic?page=2",
                                "/mc-mods/cosmetic?page=3",
                                "/mc-mods/cosmetic?page=4",
                                "/mc-mods/cosmetic?page=5",
                                "/mc-mods/cosmetic?page=6",
                                "/mc-mods/cosmetic?page=7"]

expected_urls_category = ["/mc-mods/223628-thaumcraft",
                          "/mc-mods/225643-botania",
                          "/mc-mods/221857-pams-harvestcraft"]

expected_urls_mod = ["/mc-mods/74072-tinkers-construct/files",
                     "/mc-mods/74072-tinkers-construct/license"]

@pytest.mark.crawl_curse
@pytest.mark.parametrize("response", [
    scrapy_response_from_file("http://foo.org", "tests/resources/curseforge_mcmods_base.html"),
    scrapy_response_from_file("http://foo.org", "tests/resources/curseforge_mcmods_full.html"),
])
def test_curseforge_index_urls(response):
    """
    Test :class:`CurseforgeSpider` url extraction from curseforge 
    index sample
    """
    spider = CurseforgeSpider()
    spider._follow_links = True
    parsed = iter(spider.parse(response))
    urls = [urlparse.urljoin(response.url, url) for url in expected_urls_index]
    assert_parse_requests(parsed, urls)


@pytest.mark.crawl_curse
@pytest.mark.parametrize("response", [
    scrapy_response_from_file("http://foo.org", "tests/resources/curseforge_cosmetic_base.html"),
    scrapy_response_from_file("http://foo.org", "tests/resources/curseforge_cosmetic_full.html"),
])
def test_curseforge_mod_category(response):
    """
    :class:`CurseforgeSpider` url extraction from the sample curseforge
    category page.
    Pagination is active and this extracts data from the first page,
    some next-page urls are not rendered.
    """
    spider = CurseforgeSpider()
    spider._follow_links = True
    parsed = iter(spider.parse_first_category(response))
    urls = [urlparse.urljoin(response.url, url) for url in expected_urls_first_category]
    assert_parse_requests(parsed, urls)


@pytest.mark.crawl_curse
@pytest.mark.parametrize("response", [
    scrapy_response_from_file("http://foo.org", "tests/resources/curseforge_cosmetic_base.html"),
    scrapy_response_from_file("http://foo.org", "tests/resources/curseforge_cosmetic_full.html"),
])
def test_curseforge_mod_category_page(response):
    """
    :class:`CurseforgeSpider` url extraction from a sample
    curseforge category page where pagination urls are not extracted.
    """
    spider = CurseforgeSpider()
    spider._follow_links = True
    parsed = iter(spider.parse_category(response))
    urls = [urlparse.urljoin(response.url, url) for url in expected_urls_category]
    assert_parse_requests(parsed, urls)


@pytest.mark.crawl_curse
@pytest.mark.parametrize("response", [
    scrapy_response_from_file("http://foo.org", "tests/resources/curseforge_mod_base.html"),
    scrapy_response_from_file("http://foo.org", "tests/resources/curseforge_mod_full.html"),
])
def test_curseforge_mod_page(response):
    """
    :class:`CurseforgeSpider` url and item extraction from a sample
    curseforge mod page
    """
    spider = CurseforgeSpider()
    spider._follow_links = True
    parsed = spider.parse_mod(response)
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
    assert sorted(item["categories"]) == sorted(["armor", "weapons", "tools", "technology", "processing"])
    assert sorted(item["authors"]) == sorted(["mDiyo", "boni", "jadedcat"])
    assert item["source_url"] == "https://github.com/source_url"
    assert item["donation_url"] == "https://www.paypal.com/donation_url"
    assert item["mod_url"] == "http://foo.org"
