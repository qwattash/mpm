# -*- coding: utf-8 -*-

"""
Scrapy settings for the mpm project.

This will probably be replaced by dynamic settings in the mpm main command script.
"""

# Scrapy settings for mpm project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'mpm'

SPIDER_MODULES = ['mpm.spiders']
NEWSPIDER_MODULE = 'mpm.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'mpm'

# throttle crawling to avoid being blocked
DOWNLOAD_DELAY = 5

RANDOMIZE_DOWNLOAD_DELAY = True
