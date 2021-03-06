# INSTALL DEPENDENCIES WITH THIS COMMAND
# pip install -r requirements.txt
# RUN THIS COMMAND TO RUN SERVER:
# python main.py and go to http://localhost:5000/
import json
import os
import urllib

import flask

from . import db, rec

app = flask.Flask(__name__)
app.config['JSON_AS_ASCII'] = False


@app.route('/stop')
def stop():
    return '<h1>Stop hacking our site</h1><a href="/">Обратно на сайт</a>'


@app.route('/get_goods/<int:n_page>')
def get_goods(n_page):
    if flask.request.is_xhr:
        names, prices, categories, image, ids = [[] for i in range(5)]
        goods = db.get_page_goods(n_page)
        for g in goods:
            names.append(g["name"])
            prices.append(g["price"])
            ids.append(g["pk"])
            image.append(g["image"])
            categories.append('')
        return flask.jsonify(
            list(zip(names, prices, categories, image, ids)),
        )
    else:
        return flask.redirect('/stop')


@app.route('/')
def index():
    names, prices, categories, image, ids = [
        [] for i in range(5)]  # Инициализация списков
    goods = db.get_page_goods(1)  # первая страница товаров
    for g in goods:
        names.append(g["name"])
        prices.append(g["price"])
        ids.append(g["pk"])
        image.append(g["image"])
        categories.append('')
    info = zip(names, prices, categories, image, ids)  # склейка в один список
    return flask.render_template(
        'index.html', info=info
    )


@app.route('/cart')
def cart():
    cart_ids, ns = [], []  # Инициализация списков
    cookie = flask.request.cookies.get('cart', '')
    if cookie:
        cookie = urllib.parse.unquote(cookie)
        cookie = json.loads(cookie)
    for (pk, n) in cookie:
        cart_ids.append(pk)
        ns.append(n)
    r_names, r_prices, r_categories, r_image, r_ids = [[] for i in range(5)]
    recommendations = rec.get_recs_from_db(cart_ids, ns)
    for g in recommendations:
        r_names.append(g["name"])
        r_prices.append(g["price"])
        r_ids.append(g["pk"])
        r_image.append(g["image"])
        r_categories.append('')
    rec_info = zip(r_names, r_prices, r_categories, r_image, r_ids)
    names, prices, categories, image, ids = [[] for i in range(5)]
    goods = db.get_goods_by_ids(cart_ids)
    for g in goods:
        names.append(g["name"])
        prices.append(g["price"])
        ids.append(g["pk"])
        image.append(g["image"])
        categories.append('')
    info = zip(names, prices, categories, image, ids)
    return flask.render_template(
        'cart.html', info=info, rec_info=rec_info
    )


@app.route('/search/<string:request>')
def search(request):
    names, prices, categories, image, ids = [[] for i in range(5)]
    items = db.find_items(request)
    isEmpty = False
    for g in items:
        names.append(g["name"])
        prices.append(g["price"])
        ids.append(g["pk"])
        image.append(g["image"])
        categories.append('')
    if len(items) == 0:
        isEmpty = True
    info = zip(names, prices, categories, image, ids)
    return flask.render_template(
        'search.html', info=info, request=request, isEmpty=isEmpty
    )


@app.route('/static/images/products/<string:name>')
def get_image(name):
    fullpath = 'web/static/images/products/' + name
    filepath = 'static/images/products/' + name
    if os.path.isfile(fullpath):
        return flask.send_file(filepath)
    else:
        default = 'static/images/products/default.png'
        return flask.send_file(default)
