"""
Test helpers.

Provide some shortcuts for handling scrapy tests with pytest
"""

import pytest

from functools import wraps
from scrapy.http import HtmlResponse, Request

from mpm.spiders.curseforge import CurseforgeSpider

def build_scrapy_response(url, data):
    """ Build a fake scrapy response

    Generate a scrapy response from given textual data and url
    
    :param str url: Fake response source url
    :param str data: Response body
    :return Response: A scrapy :class:`Response` instance
    """
    request = Request(url=url)
    response = HtmlResponse(url=url,
                            request=request,
                            body=data)
    return response


def scrapy_response_from_file(url, path):
    """ Build a fake scrapy response from a file
    
    The file path is either absolute or relative to the test runner
    woring dir

    :param str url: Fake response source url
    :param str path: Path of the file used as response body
    :return Response: A scrapy :class:`Response` instance
    """
    with open(path, "r") as fd:
        return build_scrapy_response(url, fd.read())


def mock_scrapy_response(url, path):
    """ Decorator that provides a mock scrapy response

    A mock scrapy :class:`Response` is given as first argument to
    the decorated function

    :decorator:
    :param str url: Fake response source url
    :param str path: Path of the file used as response body
    """
    def decorator(fn):
        
        @wraps(fn)
        def wrapped(*args, **kwargs):
            response = scrapy_response_from_file(url, path)
            return fn(response, *args, **kwargs)

        return wrapped

    return decorator


def assert_parse_requests(parser, urls):
    """ Test helper for asserting returned :class:`scrapy.http.Request`
    from a parser method.

    The test accepts a generator, such as the one given by
    :meth:`scrapy.Spider.parse`, and an iterable of request urls that
    should be returned by the parser.
    
    :param iter parser: Iterator over the spider output
    :param iter urls: Iterator over the expected urls
    :raise AssertionError: if the spider did not return all and only 
    the requests in the expected list.
    """
    requests = set([el.url for el in parser if isinstance(el, Request)])
    urls = set(urls)
    extra = requests ^ urls
    if extra:
        pytest.fail("Parser Requests not matching expected urls:\n found %s\n expected %s\n diff %s" % (requests, urls, extra))


@pytest.fixture()
def curse_spider(request):
    """
    Fixture that initialises a :class:`CurseforgeSpider`
    """
    spider = CurseforgeSpider()
    spider._follow_liks = True
    return spider
