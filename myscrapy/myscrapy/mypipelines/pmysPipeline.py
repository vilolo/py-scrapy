import time

import pymysql

from myscrapy.myitems.shopInfoItem import shopInfoItem
from myscrapy.settings import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_DATABASE, DB_CHARSET
from DBUtils.PooledDB import PooledDB


class Pipeline:
    def __init__(self):
        # self.conn = pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD,
        #                             database=DB_DATABASE,
        #                             charset=DB_CHARSET)
        #
        # self.cursor = self.conn.cursor()
        # self.curTime = str(int(time.time()))
        self.POOL = PooledDB(
            # 使用链接数据库的模块
            creator=pymysql,
            # 连接池允许的最大连接数，0和None表示不限制连接数
            maxconnections=6,
            # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
            mincached=2,
            # 链接池中最多闲置的链接，0和None不限制
            maxcached=5,
            # 链接池中最多共享的链接数量，0和None表示全部共享。
            # 因为pymysql和MySQLdb等模块的 threadsafety都为1，
            # 所有值无论设置为多少，maxcached永远为0，所以永远是所有链接都共享。
            maxshared=3,
            # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
            blocking=True,
            # 一个链接最多被重复使用的次数，None表示无限制
            maxusage=None,
            # 开始会话前执行的命令列表。如：["set datestyle to ...", "set time zone ..."]
            setsession=[],
            # ping MySQL服务端，检查是否服务可用。
            #  如：0 = None = never, 1 = default = whenever it is requested,
            # 2 = when a cursor is created, 4 = when a query is executed, 7 = always
            ping=0,
            # 主机地址
            host=DB_HOST,
            # 端口
            port=DB_PORT,
            # 数据库用户名
            user=DB_USER,
            # 数据库密码
            password=DB_PASSWORD,
            # 数据库名
            database=DB_DATABASE,
            # 字符编码
            charset=DB_CHARSET
        )

        self.conn = self.POOL.connection()
        self.cursor = self.conn.cursor()


    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()

    def process_item(self, item, spider):


        if isinstance(item, shopInfoItem):
            sql = '''
                insert into shop_info(run_id,shop_username,shop_name,total_products,add_time,url,remark,created_at) 
                values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                '''

            try:
                self.cursor.execute(sql, (item['run_id'], item['shop_username'], item['shop_name'],
                                          item['total_products'], item['add_time'], item['url'], item['remark'],
                                          item['created_at'],item['query_name'],item['query_type'],item['shop_add_time'],
                                          item['shop_location'],item['shop_username'],item['liked_count']))
                self.conn.commit()
            except pymysql.Error as e:
                print('======== pymysql.Error =========')
                print(e.args[0], e.args[1])

        else:
            sql = '''
                    insert into shop_product(run_id,goods_id,title,sales,price,discount_price,`desc`,
                    add_time,img_list,url,sort,page,remark,created_at,query_name,query_type,shop_add_time,shop_location,shop_username,liked_count) 
                    values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    '''

            try:
                self.cursor.execute(sql, (item['run_id'], item['goods_id'], item['title'], item['sales'], item['price'],
                                          item['discount_price'], item['desc'], item['add_time'],
                                          item['img_list'], item['url'], item['sort'], item['page'], item['remark'],
                                          item['created_at'], item['query_name'], item['query_type'], item['shop_add_time'],
                                          item['shop_location'], item['shop_username'], item['liked_count'],))
                self.conn.commit()
            except pymysql.Error as e:
                print('======== pymysql.Error =========')
                print(e.args[0], e.args[1])

        # return item
