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
        content = self.selenium_request(request, spider)
        if content.strip() != '':
            thisua = random.choice(UAPOOL)
            request.headers.setdefault('User-Agent', thisua)
            return HtmlResponse(request.url, encoding='utf-8', body=content, request=request)
        return None

    def selenium_request(self, request, spider):
        return self.pc_request(request, spider)

    def pc_request(self, request, spider):
        browser = spider.browserPc
        browser.get(request.url)
        time.sleep(1)

        js = """
            console.info('===== start PC js =====')
            var langBtn = document.getElementsByClassName("shopee-button-outline--primary-reverse")
            if(langBtn.length > 0){langBtn[0].click();}

            function scrollToBottom() {
                var Height = document.body.clientHeight,  //文本高度
                    screenHeight = window.innerHeight,  //屏幕高度
                    INTERVAL = 500,  // 滚动动作之间的间隔时间
                    delta = 100,  //每次滚动距离
                    curScrollTop = 0;    //当前window.scrollTop 值
                var down = true;
                Height = Height > 800 ? Height : 1000;
                console.info(Height)
                var scroll = function () {
                    //curScrollTop = document.body.scrollTop;
                    if (down){
                        curScrollTop = curScrollTop + delta;
                    }else{
                        curScrollTop = curScrollTop - delta;
                    }
                    window.scrollTo(0,curScrollTop);
                };
                var timer = setInterval(function () {
                    Height = document.body.clientHeight;
                    var curHeight = curScrollTop + screenHeight;
                    if (down && curHeight >= Height){   //滚动到页面底部时，结束滚动
                        down = false;
                    }
                    if (!down && curScrollTop<=0){
                        down = true;
                    }
                    scroll();
                }, INTERVAL)
            };
            scrollToBottom()
            """
        browser.execute_script(js)

        if request.url.find('robots') < 0:
            # #main > div > div._1Bj1VS > div.container._2_Y1cV > div.jrLh5s > div > div.row.shopee-search-item-result__items > div:nth-child(50)
            try:
                wait = WebDriverWait(browser, 20, 0.5)
                wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".shopee-search-item-result__items>div:nth-child(50)>div>a")),
                    message=request.url + ',PC time out')
            except:
                try:
                    wait = WebDriverWait(browser, 20, 0.5)
                    wait.until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, ".shopee-search-item-result__items>div:nth-child(1)>div>a")),
                        message=request.url + ',PC time out')
                except:
                    browser.refresh()
                    time.sleep(2)
                    browser.execute_script(js)
                    wait = WebDriverWait(browser, 30, 0.5)
                    wait.until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, ".shopee-search-item-result__items>div:nth-child(1)>div>a")),
                        message=request.url + ',PC time out')

        return browser.page_source.encode('utf-8')

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
