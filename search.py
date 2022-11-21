import pickle
import jieba
import pandas as pd
import warnings

from sklearn.preprocessing import MinMaxScaler
from spiders.create_db import connect
from tools.abstract import Abstract
from tools.bm25 import BM25
from tools.cos_sim import TfIdfVec

warnings.filterwarnings("ignore")

global pr_dic, index_map, idf, tf_df, tfidf_df


def load_cache():
    global pr_dic, index_map, idf, tf_df, tfidf_df

    # PageRank字典，key: url, value: pr值
    with open('cache/pr.pickle', mode='rb') as f:
        pr_dic = pickle.load(f)

    # 倒排索引表，key: word, value: [word出现的所有文档编号]
    with open('cache/index_map.pickle', mode='rb') as f:
        index_map = pickle.load(f)

    # idf字典，key: word, value: word的idf
    with open("cache/idf_dic.pickle", mode="rb") as f:
        idf = pickle.load(f)

    # tf_df pandas.DataFrame, 一列是id， 一列是这个id对应文档的tf(词频)字典
    with open("cache/tf_df.pickle", mode="rb") as f:
        tf_df = pickle.load(f)

    # tfidf_df pandas.DataFrame, 一列是id， 一列是这个id对应文档的tfidf字典
    with open("cache/tfidf_df.pickle", mode="rb") as f:
        tfidf_df = pickle.load(f)

    print("load cache finished")


# 摘要
def get_abstract(x, keywords: list) -> str:
    summary = Abstract(x['content'], window_size=70, keywords=keywords)
    return summary.get_abstract(tfidf_df.loc[tfidf_df['id'] == x['id'], "tfidf"])


# 获得排序后的搜索结果
def get_content(indexes: list, keywords: list, words: list) -> pd.DataFrame:
    global pr_dic
    # 连接mysql
    conn = connect()

    # sql语句
    if len(indexes) > 1:
        file_sql = "select id, title, content, link from sina where id in {index}".format(index=tuple(indexes))
    else:
        file_sql = "select id, title, content, link from sina where id = {index}".format(index=indexes[0])

    # 从mysql读取数据
    all_files = pd.read_sql(file_sql, conn)
    conn.close()
    # 新增一列pr，保存pagerank值
    all_files['pr'] = all_files['link'].apply(lambda x: pr_dic.get(x))
    # 生成摘要
    all_files['summary'] = all_files.apply(lambda x: get_abstract(x, keywords), axis=1)
    # 生成词频列表(用户计算bm25)
    docs = tf_df.loc[tf_df['id'].isin(all_files['id']), "tf"]
    # 对搜索结果排序
    all_files = rank(all_files, docs, keywords, words)
    return all_files[['title', 'summary', 'link']]


def rank(all_files: pd.DataFrame, docs, keywords: list, words: list) -> pd.DataFrame:
    global tfidf_df
    # 计算bm25得分
    bm25 = BM25(docs, idf_dic=idf)
    scores = bm25.score_all(keywords)
    all_files['bm25'] = scores

    # 计算余弦相似度
    tfidf_df = tfidf_df.loc[tfidf_df['id'].isin(all_files['id']), "tfidf"]
    tfidf_vec = TfIdfVec(words, tfidf_df, idf)
    all_files['cos_sim'] = tfidf_vec.cos_sim()

    # 归一化及最终排名
    cols = ['pr', 'bm25', "cos_sim"]
    all_files[cols] = MinMaxScaler().fit_transform(all_files[cols])
    # 按照权重计算最后得分(其实只算个bm25就好了)
    all_files['final_score'] = all_files['pr'] * 0.4 + all_files['bm25'] * 0.5 + all_files['cos_sim'] * 0.1
    all_files = all_files.sort_values(by='final_score', ascending=False)
    return all_files


def search(query):
    load_cache()

    global index_map
    # 得到分词后的列表
    words = list(jieba.cut(query))
    print('search words after cut: ', words)

    # 获得这些词在得到文档字典，key: word, value: [word出现的所有文档编号]
    index_dic = dict()

    for item in words:
        if item in index_map.keys():
            index_dic[item] = index_map[item]  # keyword: indexes

    # 得到在索引库中的词
    keywords = list(index_dic.keys())
    print('key words are:', keywords)

    try:
        # 求并集(效果好一点)
        intersection = set(list(index_dic.values())[0]).union(*list(index_dic.values())[1:])
        # 求交集
        # intersection = set(list(index_dic.values())[0]).intersection(*list(index_dic.values())[1:])
        print('length of intersection: ', len(intersection))
        # 得到搜索结果(info为pandas的DataFrame结构)
        info = get_content(list(intersection), keywords, words)
    except Exception as e:
        print(e)
        raise Exception('未收录该词条')

    return info, keywords


if __name__ == '__main__':
    for i in range(0, 10):
        search('中国')
