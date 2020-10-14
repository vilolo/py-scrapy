import scrapy

class Item(scrapy.Item):
    url = scrapy.Field()
    shop_id = scrapy.Field()
    goods_id = scrapy.Field()
    title = scrapy.Field()
    sales = scrapy.Field()
    price = scrapy.Field()
    discount_price = scrapy.Field()
    desc = scrapy.Field()
    add_time = scrapy.Field()
    img_list = scrapy.Field()
    sort = scrapy.Field()
    location = scrapy.Field()
    level = scrapy.Field()
    shop = scrapy.Field()
