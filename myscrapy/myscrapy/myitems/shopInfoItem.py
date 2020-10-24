import scrapy

class shopInfoItem(scrapy.Item):
    run_id = scrapy.Field()
    shop_username = scrapy.Field()
    shop_name = scrapy.Field()
    total_products = scrapy.Field()
    add_time = scrapy.Field()
    url = scrapy.Field()
    remark = scrapy.Field()
    created_at = scrapy.Field()

