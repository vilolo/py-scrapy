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
        content = self.selenium_request(request, spider)
        if content.strip() != '':
            thisua = random.choice(UAPOOL)
            request.headers.setdefault('User-Agent', thisua)
            return HtmlResponse(request.url, encoding='utf-8', body=content, request=request)
        return None

    def selenium_request(self, request, spider):
        if request.meta.get('isMobile'):
            content = self.mobile_request(request, spider)
        else:
            content = self.pc_request(request, spider)

        return content

    def pc_request(self, request, spider):
        browser = spider.browserPc
        browser.get(request.url)
        time.sleep(5)

        js = '''
            var langBtn = document.getElementsByClassName("shopee-button-outline--primary-reverse")
            if(langBtn.length > 0){langBtn[0].click();}
            '''
        browser.execute_script(js)

        js = """
            function scrollToBottom() {
                var Height = document.body.clientHeight,  //文本高度
                    screenHeight = window.innerHeight,  //屏幕高度
                    INTERVAL = 100,  // 滚动动作之间的间隔时间
                    delta = 500,  //每次滚动距离
                    curScrollTop = 0;    //当前window.scrollTop 值
                console.info(Height)
                var scroll = function () {
                    //curScrollTop = document.body.scrollTop;
                    curScrollTop = curScrollTop + delta;
                    window.scrollTo(0,curScrollTop);
                    console.info("偏移量:"+delta)
                    console.info("当前位置:"+curScrollTop)
                };
                var timer = setInterval(function () {
                    var curHeight = curScrollTop + screenHeight;
                    if (curHeight >= Height){   //滚动到页面底部时，结束滚动
                        clearInterval(timer);
                    }
                    scroll();
                }, INTERVAL)
            };
            scrollToBottom()
            """
        browser.execute_script(js)
        time.sleep(8)

        # 截屏
        # driver.get_screenshot_as_file("C:\\Users\\Administrator\\Desktop\\test.png")

        return browser.page_source.encode('utf-8')

    def mobile_request(self, request, spider):
        browser = spider.browserMobile
        browser.get(request.url)
        time.sleep(5)

        # poll_frequency：检测的间隔步长，默认为0.5s
        # WebDriverWait(browser, timeout=30, poll_frequency=2).until(page_loaded(request, spider))

        # wait = WebDriverWait(browser, 10, 0.5)
        # wait.until(EC.presence_of_element_located((By.CLASS_NAME, "_2JMB9h")), message='time out')

        js = '''
            var langBtn = document.getElementsByClassName("stardust-button")
            if(langBtn.length > 0){langBtn[0].click();}
            '''
        browser.execute_script(js)

        js = """
            function scrollToBottom() {
                var Height = document.body.clientHeight,  //文本高度
                    screenHeight = window.innerHeight,  //屏幕高度
                    INTERVAL = 100,  // 滚动动作之间的间隔时间
                    delta = 500,  //每次滚动距离
                    curScrollTop = 0;    //当前window.scrollTop 值
                console.info(Height)
                var scroll = function () {
                    //curScrollTop = document.body.scrollTop;
                    curScrollTop = curScrollTop + delta;
                    window.scrollTo(0,curScrollTop);
                    console.info("偏移量:"+delta)
                    console.info("当前位置:"+curScrollTop)
                };
                var timer = setInterval(function () {
                    var curHeight = curScrollTop + screenHeight;
                    if (curHeight >= Height){   //滚动到页面底部时，结束滚动
                        clearInterval(timer);
                    }
                    scroll();
                }, INTERVAL)
            };
            scrollToBottom()
            """
        browser.execute_script(js)
        time.sleep(3)
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
