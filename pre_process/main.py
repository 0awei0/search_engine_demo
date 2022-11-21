# 导入的这两个文件用于做倒排索引和PageRank，请不要optimize imports
import invert_index
import page_rank

from build_trie import create_trie

if __name__ == '__main__':
    create_trie()
