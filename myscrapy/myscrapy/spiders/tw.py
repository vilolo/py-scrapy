import json
import time

import scrapy


class TwSpider(scrapy.Spider):
    name = 'tw'
    allowed_domains = ['shopee.tw']
    start_urls = []
    runId = time.strftime("%Y%m%d_%H%M%S", time.localtime())

    totalPage = 3
    keyword = 'School Supplies'

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'myscrapy.mymiddlewares.twMiddleware.DownloaderMiddleware': 300
        }
    }

    def __init__(self, **kwargs):
        # self.start_urls.append('https://shopee.tw/search?keyword='+self.keyword)
        self.start_urls.append('https://shopee.tw/api/v2/search_items/?by=relevancy&keyword=%E7%AC%94&limit=50&newest=0&order=desc&page_type=search&version=2')
        super().__init__(**kwargs)

    def parse(self, response):
        print('@@@@@@@@@@')
        print(response.body)
