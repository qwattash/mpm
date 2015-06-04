"""
Test item loaders used in the spiders with some simple html inputs
"""

from __future__ import absolute_import

import urlparse

from mpm.items import ModItem
from mpm.spiders.curseforge import CurseforgeSpider

from helpers import mock_scrapy_response, assert_parse_requests

expected_urls = ["/mc-mods",
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

@mock_scrapy_response("http://foo.org", "tests/resources/curseforge_mcmods_base.html")
def test_curseforge_simplified_index_urls(response):
    """
    Test :class:`CurseforgeSpider` url extraction from curseforge index
    with a simplified html source
    """
    spider = CurseforgeSpider()
    spider._follow_links = True
    parsed = iter(spider.parse(response))
    urls = [urlparse.urljoin(response.url, url) for url in expected_urls]
    assert_parse_requests(parsed, urls)

@mock_scrapy_response("http://foo.org", "tests/resources/curseforge_mcmods_full.html")
def test_curseforge_full_index_urls(response):
    """
    Test :class:`CurseforgeSpider` url extraction from curseforge index
    with the full html with a substed of the items for simplicity
    """
    spider = CurseforgeSpider()
    spider._follow_links = True
    parsed = iter(spider.parse(response))
    urls = [urlparse.urljoin(response.url, url) for url in expected_urls]
    assert_parse_requests(parsed, urls)

@mock_scrapy_response("http://foo.org", "tests/resources/curseforge_cosmetic_base.html")
def test_curseforge_simplified_mod_category(response):
    """
    :class:`CurseforgeSpider` url extraction from a simplified
    curseforge category page.
    Pagination is active and this extracts data from the first page,
    some next-page urls are not rendered.
    """
    expected_urls = ["/mc-mods/223628-thaumcraft",
                     "/mc-mods/225643-botania",
                     "/mc-mods/221857-pams-harvestcraft",
                     "/mc-mods/cosmetic?page=2",
                     "/mc-mods/cosmetic?page=3",
                     "/mc-mods/cosmetic?page=4",
                     "/mc-mods/cosmetic?page=5",
                     "/mc-mods/cosmetic?page=6",
                     "/mc-mods/cosmetic?page=7"]
    spider = CurseforgeSpider()
    spider._follow_links = True
    parsed = iter(spider.parse_first_category(response))
    urls = [urlparse.urljoin(response.url, url) for url in expected_urls]
    assert_parse_requests(parsed, urls)

@mock_scrapy_response("http://foo.org", "tests/resources/curseforge_cosmetic_full.html")
def test_curseforge_full_mod_category(response):
    """
    :class:`CurseforgeSpider` url extraction from the
    curseforge category page with all the other content
    Pagination is active and this extracts data from the first page,
    some next-page urls are not rendered.
    """
    expected_urls = ["/mc-mods/223628-thaumcraft",
                     "/mc-mods/225643-botania",
                     "/mc-mods/221857-pams-harvestcraft",
                     "/mc-mods/cosmetic?page=2",
                     "/mc-mods/cosmetic?page=3",
                     "/mc-mods/cosmetic?page=4",
                     "/mc-mods/cosmetic?page=5",
                     "/mc-mods/cosmetic?page=6",
                     "/mc-mods/cosmetic?page=7"]
    spider = CurseforgeSpider()
    spider._follow_links = True
    parsed = iter(spider.parse_first_category(response))
    urls = [urlparse.urljoin(response.url, url) for url in expected_urls]
    assert_parse_requests(parsed, urls)
