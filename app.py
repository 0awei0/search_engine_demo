import json
import pickle
import redis

from flask import Flask, render_template, redirect, request, jsonify, url_for
from search import search

# redis(缓存)
db = redis.Redis()

app = Flask(__name__)
# 前缀树(用于搜索提示)
with open('cache/trie.pickle', mode='rb') as f:
    trie = pickle.load(f)


# 返回提示词列表
@app.route('/words_hint', methods=['POST'])
def words_hint():
    global trie

    # 获得前端返回的数据
    data = json.loads(request.form.get('data'))
    if data['data'] == '':
        hint_list = []
    # 获得以data开头的关键词列表
    else:
        hint_list = trie.auto_complete(data['data'])
        hint_list = sorted(hint_list, key=lambda x: len(x), reverse=True)
        # 选长度较长的前8个作为提示词(其实可以改成按搜索频率，更合理)
        hint_list = hint_list[0:8]
    # print('hint_list: ', hint_list)

    return jsonify({'hint_list': hint_list})


# 对query进行搜索
def search_info(query):
    global trie
    if db.exists(query):
        print("cache hit")
    else:
        ans, keywords = search(query)
        cols = ['title', 'summary', 'link']
        result = {
            'keywords': keywords,
            'data': ans[cols]
        }
        # 设置为100秒过期
        db.set(query, pickle.dumps(result), ex=100)
        # 如果搜索成功，加入前缀树。
        trie.insert("".join(keywords))


# 点击提示内容的时候，在这里搜索
@app.route('/render_hint_list', methods=['POST'])
def render_hint_list():
    data = json.loads(request.form.get('data'))
    # print('json: ', data['data'])
    try:
        query = data['data']
        search_info(query)
        return jsonify({'message': 'success'})
    except Exception as e:
        print(e)
        return redirect('/exception')


# 异常界面
@app.route('/exception', methods=['GET'])
def exception_view():
    return render_template('exception.html')


# 用户输入的视图
@app.route('/', methods=['GET', 'POST'])
def search_view():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        query = request.form.get('search_info')

        try:
            search_info(query)
            return redirect(url_for("show_results", query=query))
        except Exception as e:
            print(e)
            return redirect('/exception')

        # 测试时用
        # search_info(query)
        # return redirect(url_for("show_results", query=query))


# 关键词高亮
def highlight_keywords(content, keywords):
    for keyword in keywords:
        content = content.replace(keyword, '<em><font color="red">{}</font></em>'.format(keyword))
    return content


# 渲染搜索结果
@app.route('/results/<string:query>')
def show_results(query):
    # 从缓存中取出搜索结果
    cache_data = pickle.loads(db.get(query))
    ans = cache_data['data']
    keywords = cache_data['keywords']

    ans['summary'] = ans['summary'].apply(lambda x: highlight_keywords(x, keywords))
    ans['title'] = ans['title'].apply(lambda x: highlight_keywords(x, keywords))

    titles = ans['title'].tolist()
    summaries = ans['summary'].tolist()
    links = ans['link'].tolist()

    results = []
    for idx, title in enumerate(titles):
        temp = {
            'title': title,
            'summary': summaries[idx],
            'link': links[idx]
        }
        results.append(temp)

    return render_template("result.html", results=results)


if __name__ == '__main__':
    app.run()
