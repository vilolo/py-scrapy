import scrapy


class TwSpider(scrapy.Spider):
    name = 'tw'
    allowed_domains = ['xiapi.xiapibuy.com']
    start_urls = ['https://xiapi.xiapibuy.com/shop/39184759/search?sortBy=pop']
    # start_urls = ['https://shopee.com.my/unisuntoys']

    # custom_settings = {
    #     'ITEM_PIPELINES': {
    #         'myscrapy.mypipelines.twPipeline.Pipeline': 300,
    #     },
    #     'DOWNLOADER_MIDDLEWARES': {
    #         'myscrapy.mymiddlewares.twMiddleware.DownloaderMiddleware': 300
    #     }
    # }

    def parse(self, response):
        print('!!!!!!!!!!!!!!!! forbidden !!!!!!!!!!!!!!!')
        for url in response.xpath('//a/@href').getall():
            print(url)
