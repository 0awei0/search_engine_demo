# 搜索引擎小demo

## 简介

爬取新浪新闻，并进行分词，倒排，计算tfidf，pagerank等操作，实现一个简单的搜索引擎。

## 环境要求

1. mysql, Redis（请在对应文件修改你的连接）
2. python库要求：相关依赖已经保存到requirements.txt中，直接运行命令`pip install -r requirements.txt`安装依赖即可。

## 复现说明

1. 直接运行`spiders`文件夹下的`main.py`文件，记得在`create_db.py`中修改你的mysql连接信息，否则数据无法正常入库。
2. 直接运行`pre_process`文件夹下的`main.py`文件，对采集到的数据进行预处理，包括分词，计算tfidf等操作，生成的文件会保存到`cache`文件夹下。
3. 直接运行根目录下的`app.py`文件。

