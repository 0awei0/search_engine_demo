import pickle

from words_hint import Trie


def create_trie():
    print("creating trie")
    with open('../cache/tfidf_df.pickle', mode='rb') as f:
        tfidf = pickle.load(f)
    trie = Trie()
    for value in tfidf['tfidf']:
        trie.build_trie(value)

    with open('../cache/trie.pickle', mode='wb') as f:
        pickle.dump(trie, f)
    print('create trie tree successfully!')


def trie_test():
    with open('../cache/trie.pickle', mode='rb') as f:
        trie = pickle.load(f)
    print(trie.auto_complete('张'))
    print(trie.auto_complete('lin'))
    print(trie.auto_complete('数据'))
    print(trie.auto_complete('c'))


if __name__ == '__main__':
    create_trie()
    trie_test()
