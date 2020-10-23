import time

import scrapy


class TwSpider(scrapy.Spider):
    name = 'tw'
    allowed_domains = ['shopee.tw']
    start_urls = []
    shopUsername = ''
    runId = time.strftime("%Y%m%d_%H%M%S", time.localtime())

    def __init__(self, **kwargs):
        self.start_urls.append('https://shopee.tw/'+self.shopUsername)
        super().__init__(**kwargs)

    # custom_settings = {
    #     'ITEM_PIPELINES': {
    #         'myscrapy.mypipelines.twPipeline.Pipeline': 300,
    #     },
    #     'DOWNLOADER_MIDDLEWARES': {
    #         'myscrapy.mymiddlewares.twMiddleware.DownloaderMiddleware': 300
    #     }
    # }

    def parse(self, response):
        pass
