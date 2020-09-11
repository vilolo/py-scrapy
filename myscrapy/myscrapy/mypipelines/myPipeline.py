import pymysql


class Pipeline:
    def __init__(self):
        print("=============== into BuckPipeline =======================")
        self.conn = pymysql.connect(host='localhost', user='root', password='root', database='sspp',
                                    charset='utf8')

    def close_spider(self, spider):
        self.conn.close()

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

