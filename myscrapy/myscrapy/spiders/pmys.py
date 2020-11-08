import io
import json
import sys
import time

import pymysql
import requests
import scrapy
from selenium import webdriver
from myscrapy.myitems.shopInfoItem import shopInfoItem
from myscrapy.myitems.shopProductItem import shopProductItem
from myscrapy.settings import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_DATABASE, DB_CHARSET, DRIVER_PATH, \
    FILE_SAVE_PATH

class MysSpider(scrapy.Spider):
    name = 'pmys'
    allowed_domains = ['shopee.com.my']
    start_urls = []

    # custom_settings = {
    #     'DOWNLOADER_MIDDLEWARES': {
    #         'myscrapy.mymiddlewares.pmysMiddleware.DownloaderMiddleware': 300
    #     }
    # }

    runId = time.strftime("%Y%m%d_%H%M%S", time.localtime())

    shopUsername = 'womenbaggallery'
    basePageUrl = ''

    def __init__(self):
        self.start_urls.append('https://shopee.com.my/' + self.shopUsername)

        driverPath = DRIVER_PATH

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

        super(MysSpider, self).__init__()

    def parse(self, response):
        print('=== into parse ===')

        # 店鋪信息
        # https://shopee.com.my/api/v2/shop/get?is_brief=0&shopid=32563007

        # response = requests.get('https://shopee.com.my/api/v2/item/get?itemid=4854960706&shopid=118059163', params=json)
        # print(response.url)
        # print(type(response.text))
        # obj = json.loads(response.text)
        # print(obj['item']['itemid'])
        # return

        # 所有产品链接
        # https://shopee.com.my/shop/118059163/search
        self.basePageUrl = response.xpath('//a[@class="navbar-with-more-menu__item"][1]/@href').extract_first()
        yield response.follow(url=self.basePageUrl, callback=self.parsePage)

        pass

    def parsePage(self, response):
        print('=== into parsePage ===')
        # 循环产品
        for item in response.xpath('//div[@class="shop-search-result-view__item col-xs-2-4"]/div'):
            url = item.xpath('a/@href').extract_first()
            strlist = url.split('.')
            shopid = strlist[-2]
            itemid = strlist[-1]
            res = requests.get('https://shopee.com.my/api/v2/item/get?itemid=%s&shopid=%s' % (itemid, shopid), params=json)
            resJson = json.loads(res.text)




        # 循环页数
        # if int(response.xpath('//span[@class="shopee-mini-page-controller__current"]/text()').extract_first()) < int(
        #         response.xpath('//span[@class="shopee-mini-page-controller__total"]/text()').extract_first()):
        #     yield response.follow(url=self.basePageUrl + '?page=' + str(self.currentPage), callback=self.parsePage)
        #     self.currentPage = self.currentPage + 1

    def closed(self, reason):
        self.browserPc.quit()
        # self.outputHtml()

    def outputHtml(self):
        conn = pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD,
                               database=DB_DATABASE,
                               charset=DB_CHARSET)
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        sql = '''
        select *, round(ss/tt, 2) avgsold from (
            select *,
            (if(LOCATE('k',REPLACE(`sales`,' Sold',''))>0,REPLACE(REPLACE(sales,' Sold',''),'k','')*1000,REPLACE(sales,' Sold',''))*1) ss,
            (IF(LOCATE('months',add_time)>0,REPLACE(add_time,' months','')*30,IF(LOCATE('years',add_time),REPLACE(add_time,' years','')*365,REPLACE(add_time,' days','')))*1) tt
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

        # filename = '/Users/mac/www/demo/pys/file/'+self.name+'_'+self.shopUsername+'_'+self.runId+'.html'
        filename = FILE_SAVE_PATH+'/'+self.name+'_'+self.shopUsername+'_'+self.runId+'.html'
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
            file_object.write(headHtml+bodyHtml+footHtml)

        cursor.close()
        conn.close()
