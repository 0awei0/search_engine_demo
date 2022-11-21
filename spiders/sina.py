import feapder
import unicodedata
import urllib3
import threading
import time
import jieba
import logging
import hashlib
import os

from tools import get_feature, SpiderDataItem
from feapder import setting
from simhash import Simhash, SimhashIndex
from create_db import delete_values

# 去除警告
urllib3.disable_warnings()
jieba.setLogLevel(logging.INFO)

# 已经爬取的页面数量
num_pages = 0

# 爬虫配置
setting.SPIDER_MAX_RETRY_TIMES = 0
setting.MYSQL_IP = "localhost"
setting.MYSQL_PORT = 80
setting.MYSQL_DB = "search_engine_db"
setting.MYSQL_USER_NAME = "root"
setting.MYSQL_USER_PASS = "hww74520i"
setting.EXPORT_DATA_MAX_FAILED_TIMES = 1  # 导出数据时最大的失败次数，包括保存和更新，超过这个次数报警
setting.EXPORT_DATA_MAX_RETRY_TIMES = 1  # 导出数据时最大的重试次数，包括保存和更新，超过这个次数则放弃重试

# 数据库表名
TABLE_NAME = "sina"
# 声明条件变量
cLock = threading.Condition()
# 列表中存在的url
exist_urls = []
# 用于保存simhash
index = SimhashIndex(objs=[], k=3)

# 最大爬取的页面数量(实际爬取的页面数量会小于这个值，所以建议设大一点)
max_pages = 15000


class AirSpiderTest(feapder.AirSpider):

    def start_requests(self):
        yield feapder.Request("https://news.sina.com.cn/")

    def parse(self, request, response):
        global exist_urls

        href_list = response.xpath('//a/@href').extract()
        href_list = list(set(href_list))  # 去重
        exist_urls += href_list  # 加入已存在的链接
        for href in href_list:  # 发请求
            yield feapder.Request(href, callback=self.parser_news)

    def parser_news(self, request, response):
        global num_pages, exist_urls
        if response.encoding.lower() != 'utf-8':
            raise Exception("encoding  error")

        title = response.xpath('//h1[@class="main-title"]/text()').extract_first().strip()
        contents = response.xpath('//div[@id="article"]//p/text()').extract()  # 获取正文的列表
        contents = [unicodedata.normalize('NFKC', i) for i in contents]
        content = "".join(contents).strip()  # 拼接正文

        if len(title) < 5 or len(content) < 50:
            raise Exception("pass this url")

        else:
            hrefs = response.xpath('//a/@href').extract()  # 提取链接
            hrefs = list(set(hrefs))  # 去重
            hrefs = [href for href in hrefs if href.startswith("http") or href.startswith("https")]

            cLock.acquire()

            s = Simhash(get_feature(title + content))

            if not index.get_near_dups(s):
                index.add(str(num_pages), s)

                # 数据入库
                item = SpiderDataItem()
                item.table_name = TABLE_NAME  # 表名
                ans = hashlib.md5(request.url.encode(encoding='UTF-8')).hexdigest()
                item.id = int(ans[8:-8], 16)  # id, 这条数据的唯一标识
                item.title = title
                item.content = content
                item.link = request.url
                item.urls = " ".join(hrefs)

                yield item

            num_pages += 1
            if num_pages == max_pages:
                print('exit')
                os._exit(0)

            unique_urls = list(set(hrefs) - set(exist_urls))  # 提取未爬取过的链接
            exist_urls += unique_urls

            cLock.notify_all()  # 通知wait()
            cLock.release()
            time.sleep(0.1)

            # 未爬取的链接继续爬取
            for unique_url in unique_urls:
                yield feapder.Request(unique_url, callback=self.parser_news)

    def validate(self, request, response):
        if response.status_code != 200:
            raise Exception("response code not 200")  # 抛出异常

    # 下载中间件用于在请求之前，对请求做一些处理，如添加cookie、header等。写法如下：
    def download_midware(self, request):
        request.timeout = (6, 6)
        return request


if __name__ == "__main__":
    delete_values(TABLE_NAME)
    AirSpiderTest(thread_count=8).start()
