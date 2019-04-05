# here will be database settings
# all dbs are here: https://drive.google.com/drive/folders/1cCOzefvsFQZ6fI9r4LVAG8BYJ-VGDU4A
import sqlite3
import random
import re

goods_on_one_page = 20
conn = sqlite3.connect("web/products.db", check_same_thread=False)
conn_images = sqlite3.connect("web/urls.db", check_same_thread=False)
conn_clusters = sqlite3.connect("web/cluster.db", check_same_thread=False)
conn_gg = sqlite3.connect("web/good-generic.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("SELECT count(*) FROM clean_goods;")
n_of_goods = cursor.fetchone()[0]


class Good(object):

    def __init__(self, query):
        self.image = '../static/images/products/default.png'
        cursor_images = conn_images.cursor()
        cursor_images.execute("SELECT url FROM data WHERE product_id = '" + str(query[0]) + "';")
        image = cursor_images.fetchone()

        if image:
            self.image = image[0]

        self.generic = query[-1]
        self.pk = query[0]
        self.mnn = query[11]
        name = query[1].split(" ")[:3]
        name = query[1].split(" капли")[0]
        name = name.split(" аэр")[0]
        name = name.split(" драже")[0]
        name = name.split(" сироп")[0]
        name = name.split(" г/х")[0]
        name = name.split(" фл")[0]
        name = name.split(" пор")[0]
        name = name.split(" лиоф")[0]
        name = name.split(" гель")[0]
        name = name.split(" г/хл")[0]
        name = name.split(" сусп")[0]
        name = name.split(" мазь")[0]
        name = name.split(" крем")[0]
        name = name.split(" средство")[0]
        name = name.split(" спрей")[0]
        name = name.split(" норм")[0]
        name = name.split(" капс")[0]
        name = name.split(" быстрорастворимый")[0]
        name = name.split(" конц")[0]
        name = name.split(" р-р д/местн")[0]
        name = name.split(" р-р д/наружн")[0]
        name = name.split(" р-р")[0]
        name = name.split(" д/дет")[0]
        name = name.split(" таб")[0]
        name = name.split(" ")[:3]
        self.name = ' '.join(name)
        self.price = random.randint(57, 1031)
    
    def __eq__(self, other):
        return self.pk == other.pk


def LD(s,t):
    s = ' ' + s
    t = ' ' + t
    d = {}
    S = len(s)
    T = len(t)
    for i in range(S):
        d[i, 0] = i
    for j in range (T):
        d[0, j] = j
    for j in range(1,T):
        for i in range(1,S):
            if s[i] == t[j]:
                d[i, j] = d[i-1, j-1]
            else:
                d[i, j] = min(d[i-1, j], d[i, j-1], d[i-1, j-1]) + 1
    return d[S-1, T-1]


def find_items(request):
    cursor = conn.cursor()
    fixed_request = str(request)[0].upper() + str(request)[1:len(str(request))].lower()
    fixed_request = re.sub(r'[^(0-9)^ ^(a-z)^(а-я)^(А-Я)^\-]', '', fixed_request)
    if not fixed_request:
        return []

    query = "SELECT * FROM 'clean_goods' WHERE Наименование LIKE '%" + fixed_request + "%' LIMIT 20;"
    

    queryResult = cursor.execute(query)
    clean_goods = queryResult.fetchall()

    all_results = []
    all_results += clean_goods

    if len(all_results) == 0:
        for i in range(min(10, len(request))):
            query = "SELECT * FROM 'clean_goods' WHERE Наименование LIKE '%" + str(fixed_request[0:i]) + "%" + str(fixed_request[(i + 1):len(fixed_request)]) + "%' LIMIT 20;"
            queryResult = cursor.execute(query)
            clean_goods = queryResult.fetchall()
            all_results += clean_goods

    goods = []
    all_results_with_LD = []


    for query in all_results:
        g = Good(query)
        all_results_with_LD.append((query, LD(' '.join(g.name.split()[:3]), ' '.join(fixed_request.split()[:3]))))

    all_results_with_LD = sorted(all_results_with_LD, key=lambda x: x[1])

    for query in all_results_with_LD[:20]:
        g = Good(query[0])
        goods.append(g)
    return goods


def get_page_goods(n_page):
    # we must get [n_page * 20 : (n_page + 1) * 20]
    cursor = conn.cursor()
    n_page -= 1
    offset = (n_page + 1) * goods_on_one_page
    cursor.execute(
        "SELECT * FROM clean_goods LIMIT {} OFFSET {};".format(
            goods_on_one_page, offset
        ))
    goods = []
    queries = cursor.fetchall()
    for query in queries:
        g = Good(query)
        goods.append(g)
    return goods


def get_goods_by_ids(ids_list: list) -> list:
    cursor = conn.cursor()
    goods = []
    for i in ids_list:
        sql = "SELECT * FROM clean_goods WHERE id='{}';".format(i)
        cursor.execute(sql)
        query = cursor.fetchone()
        g = Good(query)
        goods.append(g)
    return goods


def get_generics_clusters(generics) -> list:
    cluster_cursor = conn_clusters.cursor()
    clusters = []
    sql = "SELECT cluster FROM 'generic_cluster' WHERE generic='{}'"
    for generic in generics:
        cluster_cursor.execute(sql.format(generic))
        clusters.append(cluster_cursor.fetchone())
    return [int(c[0]) if c else c for c in clusters]  # WE DON'T RETURN CLUSTER IF THERE IS NO


def searching_popular_good_by_generic(gen):
    cursor_gg = conn_gg.cursor()
    sql = "SELECT good, count(generic) as cnt from good_generic where generic = '"+gen+"' group by good order by cnt DESC limit 5"
    smth = [i[0] for i in sorted(cursor_gg.execute(sql).fetchall(), key=lambda x:x[1]*random.random()/302366)]
    cursor = conn.cursor()
    sql = "SELECT * FROM 'clean_goods' WHERE [Код товара]={};".format(smth[0])
    cursor.execute(sql)
    temp = cursor.fetchone()
    return Good(temp)


def get_random_recs(n):
    cursor = conn.cursor()
    goods = []
    sql = "SELECT * FROM clean_goods ORDER BY RANDOM() LIMIT {};".format(n)
    cursor.execute(sql)
    queryies = cursor.fetchall()
    for query in queryies:
        goods.append(Good(query))
    return goods