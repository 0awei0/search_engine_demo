import numpy as np


class TfIdfVec:
    def __init__(self, keywords: list, tf_idf: any, idf: dict):
        self.keywords = keywords
        self.tf_idf = tf_idf
        self.idf = idf

    def get_query_vector(self) -> list:
        vector = []
        for keyword in self.keywords:
            if keyword in self.idf.keys():
                vector.append(self.idf.get(keyword))
            else:
                vector.append(0)
        return vector

    def cos_sim(self) -> list:
        vectors = []
        for dic in self.tf_idf:
            vector = []
            for keyword in self.keywords:
                if keyword in dic.keys():
                    vector.append(dic.get(keyword))
                else:
                    vector.append(0)
            vectors.append(vector)
        vector = self.get_query_vector()
        sims = get_cos_similar_multi(np.asarray(vector), np.asarray(vectors))
        return sims


def get_cos_similar_multi(v1: np.array, v2: np.array) -> np.array:
    num = np.dot([v1], np.array(v2).T)  # 向量点乘
    denom = np.linalg.norm(v1) * np.linalg.norm(v2, axis=1)  # 求模长的乘积
    res = num / denom
    res[np.isneginf(res)] = 0
    return res[0]


def get_cos_similar(v1: np.array, v2: np.array):
    num = float(np.dot(v1, v2.T))  # 向量点乘
    denom = np.linalg.norm(v1) * np.linalg.norm(v2)  # 求模长的乘积
    return num / denom if denom != 0 else 0


if __name__ == '__main__':
    pass
