import time

import pymysql

from myscrapy.myitems.shopInfoItem import shopInfoItem


class Pipeline:
    def __init__(self):
        self.conn = pymysql.connect(host='localhost', port=8889, user='root', password='root', database='sspp',
                                    charset='utf8mb4')
        self.cursor = self.conn.cursor()
        self.curTime = str(int(time.time()))

    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()

    def process_item(self, item, spider):
        if isinstance(item, shopInfoItem):
            sql = '''
                insert into shop_info(run_id,shop_username,shop_name,total_products,add_time,url,remark,created_at) 
                values(%s,%s,%s,%s,%s,%s,%s,%s)
                '''

            try:
                self.cursor.execute(sql, (item['run_id'], item['shop_username'], item['shop_name'],
                                          item['total_products'], item['add_time'], item['url'], item['remark'],
                                          item['created_at']))
                self.conn.commit()
            except pymysql.Error as e:
                print('======== pymysql.Error =========')
                print(e.args[0], e.args[1])

        else:
            sql = '''
                    insert into shop_product(run_id,goods_id,title,sales,price,discount_price,`desc`,
                    add_time,img_list,url,sort,page,remark,created_at) 
                    values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    '''

            try:
                self.cursor.execute(sql, (item['run_id'], item['goods_id'], item['title'], item['sales'], item['price'],
                                          item['discount_price'], item['desc'], item['add_time'],
                                          item['img_list'], item['url'], item['sort'], item['page'], item['remark'],
                                          item['created_at']))
                self.conn.commit()
            except pymysql.Error as e:
                print('======== pymysql.Error =========')
                print(e.args[0], e.args[1])

        return item

