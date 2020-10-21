import scrapy

class shopProductItem(scrapy.Item):
    run_id = scrapy.Field()
    goods_id = scrapy.Field()
    title = scrapy.Field()
    sales = scrapy.Field()
    price = scrapy.Field()
    discount_price = scrapy.Field()
    desc = scrapy.Field()
    add_time = scrapy.Field()
    img_list = scrapy.Field()
    url = scrapy.Field()
    sort = scrapy.Field()
    page = scrapy.Field()
    remark = scrapy.Field()
    created_at = scrapy.Field()