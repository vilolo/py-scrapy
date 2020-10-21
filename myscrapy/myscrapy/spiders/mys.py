import json
import time

import scrapy
from lxml import etree
from selenium import webdriver
from myscrapy.myitems.shopInfoItem import shopInfoItem
from myscrapy.myitems.shopProductItem import shopProductItem


class MysSpider(scrapy.Spider):
    name = 'mys'
    allowed_domains = ['shopee.com.my']
    start_urls = []

    custom_settings = {
        'ITEM_PIPELINES': {
            'myscrapy.mypipelines.mysPipeline.Pipeline': 300,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'myscrapy.mymiddlewares.mysMiddleware.DownloaderMiddleware': 300
        }
    }

    runId = time.strftime("%Y%m%d-%H%M%S", time.localtime())

    totalProduct = 1
    totalPage = 1
    currentPage = 1
    lastPageProduct = 1
    shopUsername = 'bedsheetbestseller'
    basePageUrl = ''

    def __init__(self):
        self.start_urls.append('https://shopee.com.my/'+self.shopUsername)

        driverPath = '/Users/mac/www/demo/pys/chromedriver'

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')  # 注释后有界面
        chrome_options.add_argument('--no-sandbox')  # 非沙盘模式
        chrome_options.add_argument('window-size=1920x3000')  # 设置浏览器分辨率
        chrome_options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
        prefs = {"profile.managed_default_content_settings.images": 2, 'permissions.default.stylesheet': 2}
        chrome_options.add_experimental_option("prefs", prefs)

        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])  # 规避检测
        self.browserPc = webdriver.Chrome(chrome_options=chrome_options,
                                          executable_path=driverPath)

        mobile_emulation = {'deviceName': 'iPhone 6/7/8'}
        chrome_options.add_experimental_option('mobileEmulation', mobile_emulation)
        self.browserMobile = webdriver.Chrome(chrome_options=chrome_options,
                                              executable_path=driverPath)

        super(MysSpider, self).__init__()

    def parse(self, response):
        print('=== into parse ===')
        # 商品数量
        self.totalProduct = int(response.xpath('//*[@id="main"]/div/div[2]/div[2]/div[2]/div/div[1]/div/div[2]/div[1]/div[2]/div[2]/text()').extract_first())

        # 计算总页数
        self.totalPage = int(self.totalProduct / 50)

        # 最后一页数量
        self.lastPageProduct = self.totalProduct % 50

        # 店铺自定义名
        shopName = response.xpath('//*[@id="main"]/div/div[2]/div[2]/div[2]/div/div[1]/div/div[1]/div[3]/div[1]/div/h1/text()').extract_first()

        # 加入时间
        addTime = response.xpath('//*[@id="main"]/div/div[2]/div[2]/div[2]/div/div[1]/div/div[2]/div[7]/div[2]/div[2]/text()').extract_first()

        # url
        rootUrl = self.start_urls[0]

        # 保存入库
        shopItem = shopInfoItem()
        shopItem['run_id'] = self.runId
        shopItem['shop_username'] = self.shopUsername
        shopItem['shop_name'] = shopName
        shopItem['total_products'] = self.totalProduct
        shopItem['add_time'] = addTime
        shopItem['url'] = rootUrl
        shopItem['remark'] = ''
        shopItem['created_at'] = str(int(time.time()))

        yield shopItem

        # 所有产品链接
        # https://shopee.com.my/shop/118059163/search
        self.basePageUrl = response.xpath('//a[@class="navbar-with-more-menu__item"][1]/@href').extract_first()
        yield response.follow(url=self.basePageUrl, callback=self.parsePage)

        pass

    def parsePage(self, response):
        print('=== into parsePage ===')
        # 循环产品
        sort = 1
        for item in response.xpath('//div[@class="shop-search-result-view__item col-xs-2-4"]/div'):
            url = item.xpath('a/@href').extract_first()
            yield response.follow(url=url, callback=self.parseDetail, meta={'isMobile': True, 'sort': sort, 'p': self.currentPage})
            sort = sort + 1

        # 循环页数
        # if self.currentPage < self.totalPage:
        #     yield response.follow(url=self.basePageUrl+'?page='+str(self.currentPage), callback=self.parsePage)
        #     self.currentPage = self.currentPage + 1

    def parseDetail(self, response):
        item = shopProductItem()
        item['url'] = response.request.url

        strlist = item['url'].split('.')
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
        item['page'] = response.request.meta.get('p')
        item['run_id'] = self.runId
        item['remark'] = ''
        item['created_at'] = str(int(time.time()))
        yield item

        pass

