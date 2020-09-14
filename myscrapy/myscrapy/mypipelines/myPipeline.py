import time

import pymysql


class Pipeline:
    def __init__(self):
        self.conn = pymysql.connect(host='localhost', user='root', password='root', database='sspp',
                                    charset='utf8')
        self.cursor = self.conn.cursor()
        self.curTime = str(int(time.time()))

    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()

    def process_item(self, item, spider):
        print('====== into myPipeline ======')
        print(item)
        sql = '''
            insert into sp_show(shop_id,goods_id,title,sales,price,discount_price,`desc`,add_time,img_list,url,sort,`level`,location,shop,created_at) 
            values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            '''

        try:
            self.cursor.execute(sql, (item['shop_id'],item['goods_id'],item['title'],
                                        item['sales'],item['price'],item['discount_price'],item['desc'],
                                        item['add_time'],item['img_list'],item['url'],item['sort'],
                                        item['level'], item['location'], item['shop'],
                                        self.curTime))
            self.conn.commit()
        except pymysql.Error as e:
            print('======== pymysql.Error =========')
            print(e.args[0], e.args[1])

        return item

