import psycopg2
from pymongo import MongoClient

mongodb_host = 'localhost'
mongodb_port = '27017'

client = MongoClient(mongodb_host +':'+ mongodb_port)
db = client['huwebshop']

con = psycopg2.connect(
    host="localhost",
    database="MongoDB",
    user="postgres",
    password=" "
)
cur = con.cursor()

products = db.products
data = products.find({})

#33979 / 34004 producten correct
#uploaden duurt ong 15 sec
y = 0
for x in data:
    id = x['_id']
    try:
        name = x['name']
    except:
        continue
    brand = x['brand']
    category = x['category']
    color = x['color']
    description = x['description']
    gender = x['gender']
    try:
        herhaalaankopen = x['herhaalaankopen']
    except:
        herhaalaankopen = False
    price = x['price']['selling_price'] / 100
    try:
        discount = x['properties']['discount']
    except:
        discount = None
    try:
        doelgroep = x['properties']['doelgroep']
    except:
        doelgroep = None
    try:
        sub_category = x['sub_category']
    except:
        sub_category = None
    try:
        sub_sub_category = x['sub_sub_category']
    except:
        sub_sub_category = None

    y += 1
    print("{} / 33979 ({}%)".format(y, round(y * 100 / 33979, 1)))

    cur.execute("insert into products (product_id, brand, category, color, description, gender, herhaalaankopen, name, price, discount, doelgroep, sub_category, sub_sub_category) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (id, brand, category, color, description, gender, herhaalaankopen, name, price, discount, doelgroep, sub_category, sub_sub_category))

visitors = db.visitors
data = visitors.find({})

#uploaden van 20000 duurt ong 70 sec
y = 0
for i in range(0, 20000):
    x = data[i]

    id = str(x['_id'])
    try:
        viewed_before = x['recommendations']['viewed_before']
        if not viewed_before:
            viewed_before = None
    except:
        viewed_before = None
    try:
        similars = x['recommendations']['similars']
        if not similars:
            similars = None
    except:
        similars = None
    try:
        previously_recommended = x['previously_recommended']
        if not previously_recommended:
            previously_recommended = None
    except:
        previously_recommended = None

    y += 1
    print("{} / 20000 ({}%)".format(y, round(y * 100 / 20000), 1))

    cur.execute("insert into visitors (visitor_id, viewed_before, similars, previously_recommended) values (%s, %s, %s, %s)",
                (id, viewed_before, similars, previously_recommended))

sessions = db.sessions
data = sessions.find({})

#uploaden van 20000 duurt ong 85 sec
y = 0
for i in range(0, 20000):
    x = data[i]

    id = x['_id']
    session_start = x['session_start']
    session_end = x['session_end']
    has_sale = x['has_sale']
    try:
        order_products = str(x['order']['products'])
    except:
        order_products = None

    y += 1
    print("{} / 20000 ({}%)".format(y, round(y * 100 / 20000), 1))

    cur.execute("insert into sessions (session_id, session_start, session_end, has_sale, order_products) values (%s, %s, %s, %s, %s)",
                (id, session_start, session_end, has_sale, order_products))

con.commit()
cur.close()
con.close()
