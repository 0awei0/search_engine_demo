class TrieNode:
    def __init__(self):
        self.children = {}  # 孩子节点
        self.end = False  # 标志单词是否结束


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def build_trie(self, words):
        """

        :param words: 单词列表
        :return:
        """
        for word in words:  # 逐个插入单词到树中
            self.insert(word)

    def insert(self, word):
        """

        :param word: 要插入树的单词
        :return:
        """
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.end = True

    def search(self, word):
        """

        :param word: 要搜索的单词
        :return:     单词是否在树中
        """
        node = self.root
        for char in word:
            if char in node.children:
                node = node.children[char]
            else:
                return False

        return node.end

    def _walk_trie(self, node, word, word_list):

        if node.children:
            for char in node.children:
                word_new = word + char
                if node.children[char].end:
                    # if node.end:
                    word_list.append(word_new)
                    # word_list.append( word)
                self._walk_trie(node.children[char], word_new, word_list)

    def auto_complete(self, partial_word):
        """

        :param partial_word: 前缀
        :return: 返回以partial_word为前缀的所有字符串的列表
        """
        node = self.root

        word_list = []
        # find the node for last char of word
        for char in partial_word:
            if char in node.children:
                node = node.children[char]
            else:
                # partial_word not found return
                return word_list

        if node.end:
            word_list.append(partial_word)

        #  word_list will be created in this method for suggestions that start with partial_word
        self._walk_trie(node, partial_word, word_list)
        return word_list


def tree_test():
    trie = Trie()
    # 插入词汇
    words = ['马化腾', '马云', '马斯克', '马克思', "列宁"]

    trie.build_trie(words)
    # 判断某个单词是否在树中
    print(trie.search("马斯克"))
    print(trie.search("云"))

    # 返回以马为前缀的所有字符串
    print(trie.auto_complete('马'))


if __name__ == '__main__':
    tree_test()
