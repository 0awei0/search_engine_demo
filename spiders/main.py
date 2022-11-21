from sina import AirSpiderTest
from create_db import drop_table, create_table

# 运行前，在create_db文件中，修改你的mysql连接信息
if __name__ == '__main__':
    drop_table("sina")
    create_table("sina")
    # 修改线程数量
    AirSpiderTest(thread_count=12).start()
