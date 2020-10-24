import scrapy


class JianshuSpider(scrapy.Spider):
    name = 'jianshu'
    allowed_domains = ['jianshu.com']
    start_urls = ['https://www.jianshu.com/p/8bc99a89fadf']

    custom_settings = {
        'ITEM_PIPELINES': {
        },
        'DOWNLOADER_MIDDLEWARES': {
            'myscrapy.mymiddlewares.jianshuMiddleware.DownloaderMiddleware': 300
        }
    }

    def parse(self, response):
        print('++++++++++++++')
        pass
