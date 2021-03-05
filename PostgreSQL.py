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

#14342 correcte data
list = []

y = 0
for x in data:
    try:
        id = x['_id']
        brand = x['brand']
        category = x['category']
        color = x['color']
        description = x['description']
        gender = x['gender']
        herhaalaankopen = x['herhaalaankopen']
        name = x['name']
        price = x['price']['selling_price'] / 100
        discount = x['properties']['discount']
        doelgroep = x['properties']['doelgroep']
        sub_category = x['sub_category']
        sub_sub_category = x['sub_sub_category']

        y += 1
        print("{} / 14342 ({}%)".format(y, round(y * 100 / 14342, 1)))
    except:
        continue

    cur.execute("insert into products (product_id, brand, category, color, description, gender, herhaalaankopen, name, price, discount, doelgroep, sub_category, sub_sub_category) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (id, brand, category, color, description, gender, herhaalaankopen, name, price, discount, doelgroep, sub_category, sub_sub_category))

con.commit()
cur.close()
con.close()