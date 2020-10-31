# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import random
import time

from scrapy import signals

from scrapy.http import HtmlResponse
from selenium.webdriver.support.wait import WebDriverWait

from myscrapy.settings import UAPOOL

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# 检查页面加载完毕
class page_loaded:

    def __init__(self, request, spider):
        self.request = request
        self.spider = spider

    def __call__(self, driver):
        img_src = driver.find_element_by_css_selector("img.product-carousel__item").get_attribute("src")
        return len(img_src) == 0

class DownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        request.headers.setdefault('User-Agent', random.choice(UAPOOL))
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
