import scrapy


class MySpider(scrapy.Spider):
    name = 'my'
    allowed_domains = ['shopee.com.my']
    start_urls = ['http://shopee.com.my/unisuntoys']

    custom_settings = {
        'ITEM_PIPELINES': {
            'myscrapy.mypipelines.myPipeline.Pipeline': 300,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'myscrapy.mymiddlewares.myMiddleware.DownloaderMiddleware': 300
        }
    }

    def parse(self, response):
        for url in response.xpath('//a/@href').getall():
            print(url)
