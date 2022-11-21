import jieba
import re
import feapder


# 数据入库函数
class SpiderDataItem(feapder.Item):
    __unique_key__ = ['url']  # 指定去重的key为url，最后的指纹为url值计算的md5

    def __init__(self, *args, **kwargs):
        super(SpiderDataItem, self).__init__()
        self.id = None
        self.title = None
        self.content = None
        self.link = None
        self.urls = None


stopwords = [line.strip() for line in open('../cache/stopwords.txt', 'r', encoding='utf-8').readlines()]


def get_feature(line):
    seg_list = [i for i in jieba.cut(line.strip().replace(' ', '')) if i not in stopwords]
    seg_list = [re.sub(r'[A-Za-z\d_.!+-=—,$%^，。？、~@#￥…&*《》<>「」{}【】()/]', '', i) for i in seg_list]
    return seg_list
