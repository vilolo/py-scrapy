import scrapy


class TaobaoSpider(scrapy.Spider):
    name = 'taobao'
    allowed_domains = ['taobao.com', 'jianshu.com']
    start_urls = ['http://taobao.com/']

    def parse(self, response):
        for h3 in response.xpath('//a').getall():
            print('!!!!===========================')
            print(h3)

        for href in response.xpath('//a/@href').getall():
            print('bbbbbbbbb')
            print('333333333')
            yield scrapy.Request(response.urljoin(href), self.secParse)
            print('99999999999999')

    def secParse(self, response):
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        for h3 in response.xpath('//a').getall():
            print('@@@@===========================')
            print(h3)

