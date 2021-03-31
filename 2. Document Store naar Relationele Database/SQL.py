import psycopg2
from pymongo import MongoClient

mongodb_host = 'localhost'
mongodb_port = '27017'

client = MongoClient(mongodb_host +':'+ mongodb_port)
db = client['huwebshop']

con = psycopg2.connect(
    host="localhost",
    database="huwebshop",
    user="Niels",
    password="niels"
)

cur = con.cursor()

cur.execute('drop table if exists sessions; drop table if exists visitors; drop table if exists products')
cur.execute('create table products(product_id VARCHAR(29) NOT NULL, brand VARCHAR(27) NULL, category VARCHAR(44) NULL, color VARCHAR(14) NULL, description VARCHAR(1001) NULL, gender VARCHAR(16) NULL, herhaalaankopen BOOLEAN NOT NULL, name VARCHAR(89) NOT NULL, price DECIMAL(6, 2) NOT NULL, discount VARCHAR(12) NULL, doelgroep VARCHAR(15) NULL, sub_category VARCHAR(26) NULL, sub_sub_category VARCHAR(34) NULL, PRIMARY KEY(product_id))')
cur.execute('create table visitors(visitor_id VARCHAR(25) NOT NULL, buids VARCHAR(11000) NULL, viewed_before VARCHAR(107) NULL, similars VARCHAR(117) NULL, previously_recommended VARCHAR(4295) NULL, product_id VARCHAR(29) NULL, PRIMARY KEY(visitor_id), FOREIGN KEY(product_id) REFERENCES products(product_id))')
cur.execute('create table sessions(session_id VARCHAR(83) NOT NULL, buid VARCHAR(106) NULL, session_start TIMESTAMP NOT NULL, session_end TIMESTAMP NOT NULL, has_sale BOOLEAN NOT NULL, order_products VARCHAR(795) NULL, product_id VARCHAR(29) NULL, visitor_id VARCHAR(25) NULL, PRIMARY KEY(session_id), FOREIGN KEY(product_id) REFERENCES products(product_id), FOREIGN KEY(visitor_id) REFERENCES visitors(visitor_id))')


def producten_uploaden():
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


def visitors_sessions_uploaden():
    visitors = db.visitors
    visitorsdata = visitors.find({})

    sessions = db.sessions
    sessionsdata = sessions.find({})

    y = 0
    for i in range(0, 100000):
        try:
            x = visitorsdata[i]
            z = sessionsdata[i]

            id = str(x['_id'])
            try:
                buids = x['buids']
            except:
                buids = None
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

            cur.execute("insert into visitors (visitor_id, buids, viewed_before, similars, previously_recommended) values (%s, %s, %s, %s, %s)",
                        (id, buids, viewed_before, similars, previously_recommended))

            id = z['_id']
            buid = z['buid']
            if len(z['buid']) > 1:
                buid = buid[0]
            session_start = z['session_start']
            session_end = z['session_end']
            has_sale = z['has_sale']
            try:
                order_products = str(z['order']['products'])
            except:
                order_products = None

            cur.execute(
                "insert into sessions (session_id, buid, session_start, session_end, has_sale, order_products) values (%s, %s, %s, %s, %s, %s)",
                (id, buid, session_start, session_end, has_sale, order_products))

            y += 1
            print("{} / 100000 ({:.1f}%)".format(y, y * 100 / 100000))
        except Exception as e:
            print(e)
            print(buids)
            print(buid)
            print(z)
            break


producten_uploaden()
visitors_sessions_uploaden()

client.close()



con.commit()
cur.close()
con.close()