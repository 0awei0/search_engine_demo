import re


class Abstract:
    def __init__(self, doc: str, window_size: int = 100, keywords: list = None):
        """

        :param doc:            待摘要的文本
        :param window_size:    滑动窗口大小
        :param keywords:       关键词(检索词分词后的列表)
        """
        self.doc = doc
        self.window_size = window_size
        self.windows = []
        self.keywords = keywords
        self.abstract = ''

    def get_index(self, substr: str) -> list:
        """

        :param substr: 待匹配的子串
        :return:       子串出现的所有位置
        """
        index = [substr.start() for substr in re.finditer(substr, self.doc)]

        return index

    # 得到所有的滑动窗口
    def get_window(self) -> None:

        for keyword in self.keywords:
            indexes = self.get_index(keyword)
            for index in indexes:
                self.windows.append(self.doc[index:index + self.window_size])
        # print('windows: ', self.windows)

    def get_abstract(self, tfidf_word: dict) -> str:
        """

        :param tfidf_word: 这篇文章的tfidf字典
        :return:           权值最大的摘要
        """
        self.get_window()
        score = dict.fromkeys(self.windows, 0)

        for window in score.keys():
            for keyword in self.keywords:
                if keyword in window and keyword in tfidf_word.keys():
                    score[window] += tfidf_word[keyword]
        self.abstract = max(score.items(), key=lambda x: x[1])[0]
        return self.abstract


if __name__ == '__main__':
    pass
    # with open('自动摘要.TXT', encoding='utf-8') as f:
    #     text = f.read()
    # sizes = [25, 30, 35]
    #
    # for size in sizes:
    #     abstract = Abstract(doc=text, keywords=['搜索引擎', '数学'], window_size=size)
    #
    #     tfidf = TfIdf([text])
    #     tfidf.tfidf()
    #     abstract.get_abstract(tfidf.tfidf_word[0])
    #     print('window_size: {}, abstract: {}'.format(size, abstract.abstract))
