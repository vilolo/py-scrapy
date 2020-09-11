import scrapy
from myscrapy.myitems.taobaoItem import Item
from selenium import webdriver

class TaobaoSpider(scrapy.Spider):
    name = 'taobao'
    allowed_domains = ['taobao.com', 'jianshu.com']
    start_urls = ['http://taobao.com/']

    custom_settings = {
        'ITEM_PIPELINES': {
            'myscrapy.mypipelines.taobaoPipeline.Pipeline': 300,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'myscrapy.mymiddlewares.taobaoMiddleware.DownloaderMiddleware': 300
        }
    }

    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')  # 关闭则不提供界面
        chrome_options.add_argument('--no-sandbox')  # 非沙盘模式
        mobile_emulation = {'deviceName': 'iPhone 6/7/8'}
        chrome_options.add_experimental_option('mobileEmulation', mobile_emulation)
        self.browser = webdriver.Chrome(chrome_options=chrome_options,
                                        executable_path="D:\\my doc\\py-scrapy\\chromedriver.exe")
        super(TaobaoSpider, self).__init__()

    def closed(self, reason):
        self.browser.close()  # 记得关闭

    def parse(self, response):
        # item = Item()
        # item['name'] = 'aaa'
        # # yield item
        # yield item

        for h3 in response.xpath('//a').getall():
            item = Item()
            item['name'] = h3
            yield item

    def secParse(self, response):
        # print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        for h3 in response.xpath('//a').getall():
            pass
            # print('@@@@===========================')
            # print(h3)


