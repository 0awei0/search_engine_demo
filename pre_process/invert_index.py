import warnings
import pandas as pd
import jieba
import re
import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from gensim.summarization.bm25 import BM25
from tqdm import tqdm
from spiders.create_db import connect

warnings.filterwarnings('ignore')

conn = connect()
table = pd.read_sql("select * from sina limit 500", conn)

jieba.load_userdict('../cache/user_dict.txt')
stopwords = [line.strip() for line in open('../cache/stopwords.txt', 'r', encoding='utf-8').readlines()]
tqdm.pandas(desc="分词")

eng_pattern = re.compile("[A-Za-z]+", re.I)
clean_pattern = re.compile(r'[A-Za-z\d_.!+-=—,$%^，。？、~@#￥…&*《》<>「」{}【】()/]', re.I)


def cut_sentence(sentence):
    # 将英文分词
    eng_words = re.findall(eng_pattern, sentence)
    eng_words = [word for word in eng_words if not word.isdigit()]
    english_words = list(set(eng_words))
    # 中文分词
    chinese_sentence = re.sub(clean_pattern, '', sentence).replace(' ', '')
    chinese_words = jieba.cut_for_search(chinese_sentence)
    chinese_words = list(set(chinese_words))
    all_words = english_words + chinese_words
    return [word for word in all_words if word not in stopwords and 1 < len(word) <= 20 and not word.isdigit()]


# 分词
table['all_words'] = table['content'].progress_apply(lambda x: cut_sentence(x))

# 获得所有词的idf
bm25 = BM25(table['all_words'])
with open("../cache/idf_dic.pickle", mode="wb") as f:
    pickle.dump(bm25.idf, f)

# 获得所有词的tf
tmp = pd.DataFrame()
tmp['id'] = table['id']
tmp['tf'] = bm25.doc_freqs
with open("../cache/tf_df.pickle", mode="wb") as f:
    pickle.dump(tmp, f)

# 获得tfidf
tqdm.pandas(desc="tfidf")
table['docs'] = table['all_words'].progress_apply(lambda x: " ".join(x))
docs = table['docs'].tolist()
vectorizer = TfidfVectorizer()
vectorizer.fit(docs)
matrix = vectorizer.transform(docs).toarray()
name = vectorizer.get_feature_names_out()

tfidf_list = []


def get_tfidf():
    for i in tqdm(range(0, matrix.shape[0]), desc="生成tfidf df"):
        t = pd.Series(matrix[i, :], name)
        t = t[t != 0]
        # 选择100个tfidf值最大的词作为这篇文档的关键词
        t = t.nlargest(100)
        tfidf_list.append(t.to_dict())
        del t


get_tfidf()
table['tfidf'] = tfidf_list
with open("../cache/tfidf_df.pickle", mode="wb") as f:
    pickle.dump(table[['id', 'tfidf']], f)

table['keywords'] = [''] * len(table)
idx = 0

with open('../cache/tfidf_df.pickle', mode='rb') as f:
    tfidf_df = pickle.load(f)

for value in tfidf_df['tfidf']:
    table._set_value(idx, 'keywords', list(value.keys()))
    idx += 1

all_files = table.explode("keywords")
data_change = all_files.groupby('keywords').groups

index_map = dict()

for item in data_change:
    index_map[item] = table.loc[data_change[item], "id"].tolist()

with open('../cache/index_map.pickle', mode='wb') as f:
    pickle.dump(index_map, f)
