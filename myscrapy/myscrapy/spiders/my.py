import json

import scrapy
from selenium import webdriver
from myscrapy.myitems.myItem import Item


class MySpider(scrapy.Spider):
    name = 'my'
    allowed_domains = ['shopee.com.my']
    start_urls = []

    custom_settings = {
        'ITEM_PIPELINES': {
            'myscrapy.mypipelines.myPipeline.Pipeline': 300,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'myscrapy.mymiddlewares.myMiddleware.DownloaderMiddleware': 300
        }
    }

    sort = 0

    def __init__(self):
        # https://shopee.com.my/shop/114466121/search
        self.start_urls.append('https://shopee.com.my/search?keyword=shoes')

        # driverPath = 'D:\\my doc\\py-scrapy\\chromedriver.exe'
        driverPath = '/Users/mac/www/demo/pys/chromedriver'

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')  # 关闭则不提供界面
        chrome_options.add_argument('--no-sandbox')  # 非沙盘模式
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])    #规避检测
        self.browserPc = webdriver.Chrome(chrome_options=chrome_options,
                                          executable_path=driverPath)

        mobile_emulation = {'deviceName': 'iPhone 6/7/8'}
        chrome_options.add_experimental_option('mobileEmulation', mobile_emulation)
        self.browserMobile = webdriver.Chrome(chrome_options=chrome_options,
                                              executable_path=driverPath)

        super(MySpider, self).__init__()

    # def start_requests(self):
    #     data = {
    #         'kw': 'dog'
    #     }
    #     for url in self.start_urls:
    #         yield scrapy.FormRequest(url=url, callback=self.parse, formdata=data)

    def parse(self, response):
        for url in response.xpath('//div[@class="col-xs-2-4 shopee-search-item-result__item"]/div/a/@href').getall():
            self.sort = self.sort + 1
            yield response.follow(url=url, callback=self.parseDetail, meta={'isMobile': True, 'sort': self.sort})
            # break

        for page in range(1, 2):
            yield response.follow(url='https://shopee.com.my/search?keyword=shoes&page='+str(page),
                                  callback=self.parsePage)
            # break

    def parsePage(self, response):
        urlList = response.xpath('//div[@class="shop-search-result-view__item col-xs-2-4"]/div/a/@href').getall()
        if len(urlList) == 0:
            urlList = response.xpath('//div[@class="col-xs-2-4 shopee-search-item-result__item"]/div/a/@href').getall()

        for url in urlList:
            print('url====================')
            print(url)
            self.sort = self.sort + 1
            yield response.follow(url=url, callback=self.parseDetail, meta={'isMobile': True, 'sort': self.sort})
            # break

    def parseDetail(self, response):
        item = Item()
        item['url'] = response.request.url

        strlist = item['url'].split('.')
        item['shop_id'] = strlist[-2]
        item['goods_id'] = strlist[-1]

        item['title'] = response.xpath('//div[@class="KhR5aV typo-r16 two-line-text"]/text()').extract_first()
        item['sales'] = response.xpath('//div[@class="product-review__sold-count"]/text()').extract_first()
        item['price'] = response.xpath('//div[@class="_202EOj"]/text()').extract_first()
        item['discount_price'] = response.xpath('//div[@class="BazWcl typo-m18"]/text()').extract_first()
        item['desc'] = response.xpath('//p[@class="XS3hLg"]/text()').extract_first()
        item['add_time'] = response.xpath('//span[@class="_2L7iw7"]/text()').extract_first()
        item['img_list'] = json.dumps(response.xpath('//div[@class="_39-Tsj _24d4bo"]/img/@src').getall())
        # item['img_list'] = json.dumps(response.xpath('//div[@class="_2JMB9h V1Fpl5"]/@style').getall())
        item['sort'] = response.meta.get('sort')
        item['location'] = response.xpath('//div[@class="xuIe21 typo-r12"]/text()').extract_first()
        item['level'] = response.xpath('//div[@class="badge__horizontal badge__preferred"]/text()').extract_first()
        item['shop'] = response.xpath('//div[@class="A2LqCL"]/text()').extract_first()
        yield item

    def closed(self, reason):
        self.browserPc.quit()
        self.browserMobile.quit()
        pass
