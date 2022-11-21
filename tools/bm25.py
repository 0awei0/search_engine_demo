import jieba
import numpy as np
import logging
import pickle

from numpy import ndarray

jieba.setLogLevel(logging.INFO)


class BM25(object):
    def __init__(self, docs: list, idf_dic: dict):
        self.docs = docs  # tf列表，列表的每一个元素是一个文档的tf词典
        self.doc_num = len(docs)  # 文档数
        self.avgdl = sum([len(doc) + 0.0 for doc in docs]) / self.doc_num  # 所有文档的平均长度
        self.k1 = 1.5
        self.b = 0.75
        self.idf_dic = idf_dic

    # 计算单个词的得分
    def score(self, word: str) -> list:
        score_list = []
        for index, word_count in enumerate(self.docs):
            doc_len = sum(word_count.values())
            # tf词典
            if word in word_count.keys():
                f = (word_count[word] + 0.0) / doc_len
            else:
                f = 0.0
            r_score = (f * (self.k1 + 1)) / (f + self.k1 * (1 - self.b + self.b * doc_len / self.avgdl))
            score_list.append(self.idf_dic[word] * r_score)
        return score_list

    def score_all(self, sequence: list) -> ndarray:
        sum_score = []
        for word in sequence:
            sum_score.append(self.score(word))
        sim = np.sum(sum_score, axis=0)
        sim[sim < 0] = 0
        return sim


def bm25_test():
    with open("../cache/idf_dic.pickle", mode="rb") as f:
        idf = pickle.load(f)
    print(idf['欧洲'])
    docs = [['欧洲', '欧洲人'], ['欧洲', '欧洲但是'], ['欧洲哈哈', '三生三世', "欧洲"]]
    bm = BM25(docs, idf)
    score = bm.score_all(['欧洲'])
    print(score)


if __name__ == '__main__':
    bm25_test()
