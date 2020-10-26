import json
import time

import pymysql
import scrapy
from scrapy.http import HtmlResponse
from selenium import webdriver
from myscrapy.myitems.myItem import Item

from myscrapy.settings import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_DATABASE, DB_CHARSET


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

    totalPage = 3
    sort = 0
    html = ''
    platform = 'my'
    # stationery
    # Accessories Storage
    keyword = 'School Supplies'
    runId = time.strftime("%Y%m%d-%H%M%S", time.localtime())

    def __init__(self):
        # https://shopee.com.my/shop/114466121/search
        self.start_urls.append('https://shopee.com.my/search?keyword='+self.keyword)

        # driverPath = 'D:\\my doc\\py-scrapy\\chromedriver.exe'
        driverPath = '/Users/mac/www/demo/pys/chromedriver'

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')  # 注释后有界面
        chrome_options.add_argument('--no-sandbox')  # 非沙盘模式
        chrome_options.add_argument('window-size=1920x3000')  # 设置浏览器分辨率
        chrome_options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
        # chrome_options.add_argument('blink-settings=imagesEnabled=false')  # 不加载图片，提升运行速度

        # 禁止图片和css加载
        prefs = {"profile.managed_default_content_settings.images": 2, 'permissions.default.stylesheet': 2}
        chrome_options.add_experimental_option("prefs", prefs)

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

    def parseOld(self, response):
        for url in response.xpath('//div[@class="col-xs-2-4 shopee-search-item-result__item"]/div/a/@href').getall():
            self.sort = self.sort + 1
            yield response.follow(url=url, callback=self.parseDetail, meta={'isMobile': True, 'sort': self.sort, 'p': 1})
            # break

        for page in range(1, self.totalPage):
            yield response.follow(url='https://shopee.com.my/search?keyword='+self.keyword+'&page='+str(page),
                                  callback=self.parsePage, meta={'p': page+1})
            # break

    def parse(self, response):
        for item in response.xpath('//div[@class="col-xs-2-4 shopee-search-item-result__item"]/div'):
            url = item.xpath('a/@href').extract_first()
            self.sort = self.sort + 1
            ad = item.xpath('.//div[@class="_3ao649"]/text()').extract_first()
            yield response.follow(url=url, callback=self.parseDetail,
                                  meta={'isMobile': True, 'sort': self.sort, 'p': 1, 'ad': ad})

        for page in range(1, self.totalPage):
            yield response.follow(url='https://shopee.com.my/search?keyword=' + self.keyword + '&page=' + str(page),
                                  callback=self.parsePage, meta={'p': page + 1})


    def parsePage(self, response):
        urlList = response.xpath('//div[@class="shop-search-result-view__item col-xs-2-4"]/div/a/@href').getall()
        if len(urlList) == 0:
            urlList = response.xpath('//div[@class="col-xs-2-4 shopee-search-item-result__item"]/div/a/@href').getall()

        for url in urlList:
            print('url====================')
            print(url)
            self.sort = self.sort + 1
            yield response.follow(url=url, callback=self.parseDetail, meta={'isMobile': True, 'sort': self.sort, 'p': response.request.meta.get('p')})
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
        item['ad'] = response.request.meta.get('ad')
        item['page'] = response.request.meta.get('p')
        item['platform'] = self.platform
        item['run_id'] = self.runId
        item['keyword'] = self.keyword
        yield item

    def closed(self, reason):
        self.browserPc.quit()
        self.browserMobile.quit()
        self.outputHtml()

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
            from sp_show
            where run_id = '%s'
        ) ta
        order by tt, ss desc;
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
<div><div class="title"><a href="%(href)s">%(title)s</a></div><div>
    <span class="tag1">Page: %(page)s</span>
    <span class="tag1">keyword: %(keyword)s</span>
    <span class="tag1">location: %(location)s</span>
    <span class="tag1">Sort: %(sort)s</span>
    <span class="tag2">Price: %(price)s</span>
    <span class="tag2">Solds: %(solds)s</span>
    <span class="tag2">AddTime: %(add_time)s</span>
    <span class="tag2">AvgSolds: %(avg_solds)s</span>
</div>
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
                             "desc": row['desc'],
                             'keyword': row['keyword'],
                             'location': row['location']
                             })

        filename = '/Users/mac/www/demo/pys/file/' + self.name + '_' + self.keyword + '_' + self.runId + '.html'
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
