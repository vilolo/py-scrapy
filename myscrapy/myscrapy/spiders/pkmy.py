import io
import json
import random
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
from myscrapy.settings import UAPOOL

class MysSpider(scrapy.Spider):
    startTime = int(time.time())
    name = 'pkmy'
    allowed_domains = ['shopee.com.my']
    start_urls = []
    currentPage = 1

    custom_settings = {
        'ITEM_PIPELINES': {
            'myscrapy.mypipelines.pmysPipeline.Pipeline': 300,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'myscrapy.mymiddlewares.pkmyMiddleware.DownloaderMiddleware': 300
        }
    }

    runId = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    totalPage = 3

    keyword = '3c'
    basePageUrl = ''
    page = 1

    def __init__(self):
        self.start_urls.append('https://shopee.com.my/search?keyword=' + self.keyword)

        driverPath = DRIVER_PATH

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')  # 注释后有界面
        chrome_options.add_argument('--no-sandbox')  # 非沙盘模式
        chrome_options.add_argument("service_args = ['–ignore - ssl - errors = true', '–ssl - protocol = TLSv1']")  # Python2/3
        chrome_options.add_argument('window-size=1920x3000')  # 设置浏览器分辨率
        chrome_options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
        prefs = {"profile.managed_default_content_settings.images": 2, 'permissions.default.stylesheet': 2}
        chrome_options.add_experimental_option("prefs", prefs)

        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])  # 规避检测
        self.browserPc = webdriver.Chrome(chrome_options=chrome_options,
                                          executable_path=driverPath)

        super(MysSpider, self).__init__()

    def parse(self, response):
        print('==========')
        print(type(response.meta.get('s')))
        s = response.meta.get('s') if type(response.meta.get('s')) is None else 1
        print(s)
        for item in response.xpath('//div[@class="col-xs-2-4 shopee-search-item-result__item"]/div'):
            url = item.xpath('a/@href').extract_first()
            yield self.getItemByUrl(response, url, s)
            s = s + 1

        if self.page < self.totalPage:
            yield response.follow(url='https://shopee.com.my/search?keyword=' + self.keyword + '&page=' + str(self.page),
                                  callback=self.parse, meta={'p': self.page + 1, 's' : s})
            self.page = self.page + 1

    def getItemByUrl(self, response, url, s):
        strlist = url.split('.')
        shopid = strlist[-2]
        itemid = strlist[-1]

        thisua = random.choice(UAPOOL)
        try:
            headers = {'content-type': 'application/json',
                       'User-Agent': thisua}
            goodsInfo = requests.get('https://shopee.com.my/api/v2/item/get?itemid=%s&shopid=%s' % (itemid, shopid),
                                     headers=headers)
            goodsInfoJson = goodsInfo.json()
        except:
            try:
                time.sleep(random.randint(2, 5) / 10)
                headers = {'content-type': 'application/json',
                           'User-Agent': thisua}
                goodsInfo = requests.get(
                    'https://shopee.com.my/api/v2/item/get?itemid=%s&shopid=%s' % (itemid, shopid),
                    headers=headers)
                goodsInfoJson = goodsInfo.json()
            except:
                try:
                    time.sleep(random.randint(10, 30) / 10)
                    headers = {'content-type': 'application/json',
                               'User-Agent': thisua}
                    goodsInfo = requests.get(
                        'https://shopee.com.my/api/v2/item/get?itemid=%s&shopid=%s' % (itemid, shopid),
                        headers=headers)
                    goodsInfoJson = goodsInfo.json()
                except:
                    goodsInfoJson = None
                    print('goods info 获取失败，%s' % itemid)

        time.sleep(random.randint(1, 4) / 10)

        try:
            headers = {'content-type': 'application/json',
                       'User-Agent': thisua}
            shopInfo = requests.get('https://shopee.com.my/api/v2/shop/get?is_brief=0&shopid=%s' % shopid,
                                    headers=headers)
            shopInfoJson = shopInfo.json()
        except:
            try:
                time.sleep(random.randint(2, 5) / 10)
                headers = {'content-type': 'application/json',
                           'User-Agent': thisua}
                shopInfo = requests.get('https://shopee.com.my/api/v2/shop/get?is_brief=0&shopid=%s' % shopid,
                                        headers=headers)
                shopInfoJson = shopInfo.json()
            except:
                try:
                    time.sleep(random.randint(10, 30) / 10)
                    headers = {'content-type': 'application/json',
                               'User-Agent': thisua}
                    shopInfo = requests.get('https://shopee.com.my/api/v2/shop/get?is_brief=0&shopid=%s' % shopid,
                                            headers=headers)
                    shopInfoJson = shopInfo.json()
                except:
                    shopInfoJson = None
                    print('shop info 获取失败，%s' % itemid)

        item = shopProductItem()
        item['run_id'] = self.runId
        item['query_name'] = self.keyword
        item['query_type'] = 'shop'

        if 'data' in shopInfoJson.keys():
            item['shop_add_time'] = shopInfoJson['data']['mtime']
            item['shop_location'] = shopInfoJson['data']['shop_location']
            item['shop_username'] = shopInfoJson['data']['account']['username']

        item['goods_id'] = itemid

        if 'item' in goodsInfoJson.keys():
            item['title'] = goodsInfoJson['item']['name']
            item['sales'] = goodsInfoJson['item']['historical_sold']
            if goodsInfoJson['item']['price_min_before_discount'] == -1:
                item['price'] = 0
            else:
                if goodsInfoJson['item']['price_min_before_discount'] != goodsInfoJson['item'][
                    'price_max_before_discount']:
                    item['price'] = str(
                        int(goodsInfoJson['item']['price_min_before_discount']) / 100000) + '-' + str(
                        int(goodsInfoJson['item']['price_max_before_discount']) / 100000)
                else:
                    item['price'] = str(int(goodsInfoJson['item']['price_min_before_discount']) / 100000)

            if goodsInfoJson['item']['price_min'] != goodsInfoJson['item']['price_max']:
                item['discount_price'] = str(int(goodsInfoJson['item']['price_min']) / 100000) + '-' + str(
                    int(goodsInfoJson['item']['price_max']) / 100000)
            else:
                item['discount_price'] = str(int(goodsInfoJson['item']['price_min']) / 100000)

            item['desc'] = goodsInfoJson['item']['description']
            item['add_time'] = goodsInfoJson['item']['ctime']
            if len(goodsInfoJson['item']['images']) > 1:
                item['img_list'] = json.dumps(
                    ['https://cf.shopee.com.my/file/' + goodsInfoJson['item']['images'][0],
                     'https://cf.shopee.com.my/file/' + goodsInfoJson['item']['images'][1]])
            else:
                item['img_list'] = json.dumps(
                    ['https://cf.shopee.com.my/file/' + goodsInfoJson['item']['images'][0]])
            item['liked_count'] = goodsInfoJson['item']['liked_count']

        item['url'] = 'https://shopee.com.my' + url
        item['sort'] = s
        item['page'] = response.meta.get('p')
        item['remark'] = ''
        item['created_at'] = str(int(time.time()))

        return item

    def closed(self, reason):
        self.browserPc.quit()
        self.outputHtml(1)
        self.outputHtml(2)
        self.outputHtml(3)

        print('=== take time: ' + str(round((int(time.time()) - self.startTime) / 60, 2)) + ' minutes ===')

    def outputHtml(self, type):
        conn = pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD,
                               database=DB_DATABASE,
                               charset=DB_CHARSET)
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        if type == 1:   #avgsold
            typename = 'avgsold'
            sql = '''
            select url,title,page,sort,discount_price, sales,liked_count,left(from_unixtime(add_time),10) add_time, ROUND((unix_timestamp(now())-add_time)/86400) days, img_list,`desc`, ROUND(sales/ROUND((unix_timestamp(now())-add_time)/86400),2) avgsold
            , ROUND(liked_count/ROUND((unix_timestamp(now())-add_time)/86400),2) avglike
            from shop_product
            where run_id = '%s'
            order by avgsold desc
            ''' % self.runId
        elif type == 2: #avglike
            typename = 'avglike'
            sql = '''
            select url,title,page,sort,discount_price, sales,liked_count,left(from_unixtime(add_time),10) add_time, ROUND((unix_timestamp(now())-add_time)/86400) days, img_list,`desc`, ROUND(sales/ROUND((unix_timestamp(now())-add_time)/86400),2) avgsold
            , ROUND(liked_count/ROUND((unix_timestamp(now())-add_time)/86400),2) avglike
            from shop_product
            where run_id = '%s'
            order by avglike desc
            ''' % self.runId
        else:  # days
            typename = 'days'
            sql = '''
            select url,title,page,sort,discount_price, sales,liked_count,left(from_unixtime(add_time),10) add_time, ROUND((unix_timestamp(now())-add_time)/86400) days, img_list,`desc`, ROUND(sales/ROUND((unix_timestamp(now())-add_time)/86400),2) avgsold
            , ROUND(liked_count/ROUND((unix_timestamp(now())-add_time)/86400),2) avglike
            from shop_product
            where run_id = '%s'
            order by days
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
<span class="tag1">Sort: %(sort)s</span><span class="tag2">Price: RM %(price)s</span>
<span class="tag2">Solds: %(solds)s</span>
<span class="tag2">Liked: %(liked)s</span>
<span class="tag2">AddTime: %(add_time)s</span>
<span class="tag2">Days: %(days)s</span>
<span class="tag2">AvgLike: %(avglike)s</span></div>
<span class="tag2">AvgSolds: %(avg_solds)s</span></div>
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
                             "liked": row['liked_count'],
                             "add_time": row['add_time'],
                             "days": row['days'],
                             "avglike": row['avglike'],
                             "avg_solds": row['avgsold'],
                             "img": imgHtml,
                             "desc": row['desc']
                             })

        # filename = '/Users/mac/www/demo/pys/file/'+self.name+'_'+self.shopUsername+'_'+self.runId+'.html'
        filename = FILE_SAVE_PATH+'/'+self.name+'_'+self.keyword+'_'+self.runId+'_'+typename+'.html'
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
        with open(filename, 'w', encoding='utf-8') as file_object:
            file_object.write(headHtml+bodyHtml+footHtml)

        cursor.close()
        conn.close()
