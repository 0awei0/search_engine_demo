import pymysql


def connect():
    # 在这里修改你的连接信息
    conn = pymysql.Connect(
        host='localhost',
        port=80,
        user='root',
        passwd='hww74520i',
        db='search_engine_db',
        charset='utf8'
    )
    return conn


# 删除指定表里的所有数据
def delete_values(table_name):
    conn = connect()
    # 获取游标
    cursor = conn.cursor()
    # 执行sql语句
    sql = "delete from {}".format(table_name)
    cursor.execute(sql)

    conn.commit()
    cursor.close()
    conn.close()


# 创建指定表
def create_table(table_name):
    conn = connect()
    # 获取游标
    cursor = conn.cursor()
    sql = f"create table {table_name}(id bigint unsigned primary key , title varchar(100)," \
          "content text, link varchar(100), urls text)" \
          "character set utf8;"
    cursor.execute(sql)
    cursor.close()
    conn.close()


# drop指定表
def drop_table(table_name):
    conn = connect()
    # 获取游标
    cursor = conn.cursor()
    sql = f"drop table if exists {table_name}"
    cursor.execute(sql)
    cursor.close()
    conn.close()


if __name__ == '__main__':
    # 可以在这里测试数据库连接
    create_table("sina")
