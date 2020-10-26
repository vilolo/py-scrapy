import json
import time

import pymysql
import scrapy
from selenium import webdriver

from myscrapy.myitems.shopInfoItem import shopInfoItem
from myscrapy.myitems.shopProductItem import shopProductItem
from myscrapy.settings import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_DATABASE, DB_CHARSET


class TwsSpider(scrapy.Spider):
    startTime = int(time.time())
    name = 'tws'
    allowed_domains = ['shopee.tw']
    start_urls = []
    shopUsername = 'vilolo99'
    runId = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    totalPage = 1
    currentPage = 1
    basePageUrl = ''
    sort = 1
    replaceFromUrl = 'shopee.tw'
    replaceToUrl = 'xiapi.xiapibuy.com'

    replaceFromImg = 'cf.shopee.tw'
    replaceToImg = 's-cf-tw.shopeesz.com'

    custom_settings = {
        'ITEM_PIPELINES': {
            'myscrapy.mypipelines.mysPipeline.Pipeline': 300,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'myscrapy.mymiddlewares.twsMiddleware.DownloaderMiddleware': 300
        }
    }

    def __init__(self, **kwargs):
        self.start_urls.append('https://shopee.tw/'+self.shopUsername)
        super().__init__(**kwargs)

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

    def parse(self, response):
        total_product = response.xpath(
            '//*[@id="main"]/div/div[2]/div[2]/div[2]/div/div[1]/div/div[2]/div[1]/div[2]/div[2]/text()').extract_first()

        total_product = int(total_product.replace(',', ''))
        self.totalPage = int(total_product / 30)
        if total_product % 30 > 0:
            self.totalPage += 1

        shop_name = response.xpath(
            '//*[@id="main"]/div/div[2]/div[2]/div[2]/div/div[1]/div/div[1]/div[3]/div[1]/div/h1/text()').extract_first()

        add_time = response.xpath(
            '//*[@id="main"]/div/div[2]/div[2]/div[2]/div/div[1]/div/div[2]/div[7]/div[2]/div[2]/text()').extract_first()

        rootUrl = self.start_urls[0]

        # 保存入库
        shopItem = shopInfoItem()
        shopItem['run_id'] = self.runId
        shopItem['shop_username'] = self.shopUsername
        shopItem['shop_name'] = shop_name
        shopItem['total_products'] = total_product
        shopItem['add_time'] = add_time
        shopItem['url'] = rootUrl
        shopItem['remark'] = ''
        shopItem['created_at'] = str(int(time.time()))

        yield shopItem

        self.basePageUrl = response.xpath(
            '//*[@id="main"]/div/div[2]/div[2]/div[2]/div/div[2]/div/div/div/a[2]/@href').extract_first()
        yield response.follow(url=self.basePageUrl, callback=self.parsePage)

    def parsePage(self, response):
        # 循环产品
        for item in response.xpath('//div[@class="shop-search-result-view__item col-xs-2-4"]/div'):
            url = item.xpath('a/@href').extract_first()
            yield response.follow(url=url, callback=self.parseDetail,
                                  meta={'isMobile': True, 'sort': self.sort, 'p': self.currentPage})
            self.sort = self.sort + 1

        # 循环页数
        if self.currentPage < self.totalPage:
            yield response.follow(url=self.basePageUrl + '?page=' + str(self.currentPage), callback=self.parsePage)
            self.currentPage = self.currentPage + 1

    def parseDetail(self, response):
        item = shopProductItem()
        item['url'] = (response.request.url).replace(self.replaceFromUrl, self.replaceToUrl)
        strlist = item['url'].split('.')
        item['goods_id'] = strlist[-1]
        item['title'] = response.xpath('//div[@class="KhR5aV typo-r16 two-line-text"]/text()').extract_first()
        item['sales'] = response.xpath('//div[@class="product-review__sold-count"]/text()').extract_first()
        item['price'] = response.xpath('//div[@class="_202EOj"]/text()').extract_first()
        item['discount_price'] = response.xpath('//div[@class="BazWcl typo-m18"]/text()').extract_first()
        item['desc'] = response.xpath('//p[@class="XS3hLg"]/text()').extract_first()
        item['add_time'] = response.xpath('//span[@class="_2L7iw7"]/text()').extract_first()
        item['img_list'] = json.dumps(response.xpath('//div[@class="_39-Tsj _24d4bo"]/img/@src').getall())\
            .replace(self.replaceFromImg, self.replaceToImg)
        # item['img_list'] = json.dumps(response.xpath('//div[@class="_2JMB9h V1Fpl5"]/@style').getall())
        item['sort'] = response.meta.get('sort')
        item['page'] = response.request.meta.get('p')
        item['run_id'] = self.runId
        item['remark'] = ''
        item['created_at'] = str(int(time.time()))
        yield item

    def closed(self, reason):
        self.browserPc.quit()
        self.browserMobile.quit()
        self.outputHtml()

        print('=== take time: ' + str(round((int(time.time()) - self.startTime)/60, 2)) + ' minutes ===')

    def outputHtml(self):
        conn = pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD,
                               database=DB_DATABASE,
                               charset=DB_CHARSET)
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        sql = '''
        select *, round(ss/tt, 2) avgsold from (
            select *,
            (if(LOCATE('萬',REPLACE(`sales`,' 已售出',''))>0,REPLACE(REPLACE(REPLACE(sales,' 已售出',''),'萬',''),'.','')*10000,REPLACE(replace(sales,',',''),' 已售出',''))*1) ss,
            (IF(LOCATE('個月',add_time)>0,REPLACE(add_time,' 個月','')*30,IF(LOCATE('年',add_time),REPLACE(add_time,' 年','')*365,REPLACE(add_time,' 天','')))*1) tt
            from shop_product
            where run_id = '%s'
        ) ta
        order by ss desc, tt;
        ''' % self.runId
        cursor.execute(sql)
        results = cursor.fetchall()
        bodyHtml = ''
        for row in results:
            imgList = eval(row['img_list'])
            imgHtml = ''
            if len(imgList) > 0:
                for img in imgList:
                    imgHtml = imgHtml + '<img src="%s">' % img

            bodyHtml = bodyHtml + ('''
<div><div class="title"><a href="%(href)s">%(title)s</a></div><div><span class="tag1">Page: %(page)s</span>
<span class="tag1">Sort: %(sort)s</span><span class="tag2">Price: %(price)s</span>
<span class="tag2">Solds: %(solds)s</span>
<span class="tag2">AddTime: %(add_time)s</span><span class="tag2">AvgSolds: %(avg_solds)s</span></div>
<div class="cover">
%(img)s
</div>
<div class="desc"><pre>
%(desc)s
</pre></div></div><hr>''' % {"href": row['url'],
                             "title": row['title'],
                             "page": row['page'],
                             "sort": row['sort'],
                             "price": row['discount_price'],
                             "solds": row['sales'],
                             "add_time": row['add_time'],
                             "avg_solds": row['avgsold'],
                             "img": imgHtml,
                             "desc": row['desc']
                             })

        filename = '/Users/mac/www/demo/pys/file/' + self.name + '_' + self.runId + '.html'
        headHtml = '''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<script src="http://lib.sinaapp.com/js/jquery/1.7.2/jquery.min.js"></script>
<style>
    body{margin: 20px;}
    .title{margin: 10px;}
    .tag1{padding: 10px; margin-right: 10px; background-color: green;}
    .tag2{padding: 10px; margin-right: 10px; background-color: brown;}
    .cover{margin: 15px;}
    .desc{margin: 15px;}
    img{width: 200px;}
</style>
</head>
<body>'''
        footHtml = '</body></html>'
        with open(filename, 'w') as file_object:
            file_object.write(headHtml + bodyHtml + footHtml)

        cursor.close()
        conn.close()
