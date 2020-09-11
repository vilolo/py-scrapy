import pymysql


class Pipeline:
    def __init__(self):
        print("=============== into BuckPipeline =======================")
        self.conn = pymysql.connect(host='localhost', user='root', password='root', database='sspp',
                                    charset='utf8')

    def close_spider(self, spider):
        self.conn.close()

    # # 数据库操作参考
    # # 增单条
    # sql = 'insert into test(id,name) values(%s,%s)'
    # rows = cursor.execute(sql, ('4', 'qzcsbj4'))
    #
    # # 增多条
    # sql = 'insert into test(id,name) values(%s,%s)'
    # rows = cursor.executemany(sql, [('5', 'qzcsbj5'), ('6', 'qzcsbj6'), ('7', 'qzcsbj7')])
    #
    # # 修改单条
    # sql = 'update test set name = %s where id = %s'
    # rows = cursor.execute(sql, ('qzcsbj', '7'))
    #
    # # 修改多条
    # sql = 'update test set name = %s where id = %s'
    # rows = cursor.executemany(sql, [('全栈测试笔记5', '5'), ('全栈测试笔记6', '6')])
    #
    # # 删除单条
    # sql = 'delete from test where id = %s'
    # rows = cursor.execute(sql, ('1',))
    #
    # # 删除多条
    # sql = 'delete from test where id = %s'
    # rows = cursor.executemany(sql, [('2'), ('3')])
    #
    # # 查询单条
    # # 每条记录为元组格式
    # # 运行结果：
    # # (4, 'qzcsbj4')
    # # (5, '全栈测试笔记5')
    # rows = cursor.execute('select * from test;')
    # print(cursor.fetchone())
    # print(cursor.fetchone())
    #
    # # 每条记录为字典格式
    # # {'id': 4, 'name': 'qzcsbj4'}
    # # {'id': 5, 'name': '全栈测试笔记5'}
    # cursor = self.conn.cursor(pymysql.cursors.DictCursor)
    # rows = cursor.execute('select * from test;')
    # print(cursor.fetchone())
    # print(cursor.fetchone())
    #
    # # 查询多条
    # # [{'id': 4, 'name': 'qzcsbj4'}, {'id': 5, 'name': '全栈测试笔记5'}]
    # cursor = self.conn.cursor(pymysql.cursors.DictCursor)
    # rows = cursor.execute('select * from test;')
    # print(cursor.fetchmany(2))
    #
    # # 查询全部
    # # [{'id': 4, 'name': 'qzcsbj4'}, {'id': 5, 'name': '全栈测试笔记5'}, {'id': 6, 'name': '全栈测试笔记6'},{'id': 7, 'name': 'qzcsbj'}]
    # # []
    # cursor = self.conn.cursor(pymysql.cursors.DictCursor)
    # rows = cursor.execute('select * from test;')
    # print(cursor.fetchall())
    # print(cursor.fetchall())
    #
    # # 相对绝对位置移动, 从头开始跳过n个
    # rows = cursor.execute('select * from test;')
    # cursor.scroll(3, mode='absolute')
    # print(cursor.fetchone())
    #
    # # 相对当前位置移动
    # rows = cursor.execute('select * from test;')
    # print(cursor.fetchone())
    # cursor.scroll(2, mode='relative')
    # print(cursor.fetchone())
    def process_item(self, item, spider):
        # 获取游标
        cursor = self.conn.cursor()

        # 增单条
        sql = 'insert into test(name) values(%s)'

        # rows = cursor.execute(sql, (pymysql.escape_string(item['name'])))
        rows = cursor.execute(sql, (item['name']))

        self.conn.commit()
        cursor.close()

        return item

