import networkx as nx
import pandas as pd
import warnings
import pickle
from spiders.create_db import connect

warnings.filterwarnings('ignore')

conn = connect()
table = pd.read_sql("select * from sina limit 500", conn)

digraph = nx.Graph()
links = table['link'].tolist()

for link in links:
    digraph.add_node(link)


def add_edges(x):
    for url in x['urls'].split(' '):
        if url in links:
            digraph.add_edge(x['link'], url)


table.apply(lambda x: add_edges(x), axis=1)
pr_dic = nx.pagerank(digraph)
print(len(pr_dic))

with open('../cache/pr.pickle', mode='wb') as f:
    pickle.dump(pr_dic, f)
