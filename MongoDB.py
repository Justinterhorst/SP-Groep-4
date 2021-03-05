from pymongo import MongoClient

mongodb_host = 'localhost'
mongodb_port = '27017'

client = MongoClient(mongodb_host +':'+ mongodb_port)
db = client['huwebshop']

# products = db.products
# data = products.find({})

#14342 correcte data
# y = 0
# for x in data:
#     try:
#         id = x['_id']
#         brand = x['brand']
#         category = x['category']
#         color = x['color']
#         description = x['description']
#         flavor = x['flavor']
#         gender = x['gender']
#         herhaalaankopen = x['herhaalaankopen']
#         name = x['name']
#         price = x['price']['selling_price'] / 100
#         discount = x['properties']['discount']
#         doelgroep = x['properties']['doelgroep']
#         sub_category = x['sub_category']
#         sub_sub_category = x['sub_sub_category']
#
#         y += 1
#     except:
#         continue
# print(y)

# sessions = db.sessions
# data = sessions.find({})
#
# for i in range(0, 100):
#     x = data[i]
#     try:
#         id = x['_id']
#         session_start = x['session_start']
#         session_end = x['session_end']
#         has_sale = x['has_sale']
#         order_products = x['order']['products']
#
#         print("{} en {}".format(has_sale, order_products))
#     except:
#         continue

visitors = db.visitors
data = visitors.find({})

y = 0
for i in range(0, 50000):
    x = data[i]
    try:
        id = x['_id']
        viewed_before = x['recommendations']['viewed_before']
        similars = x['recommendations']['similars']
        previously_recommended = x['previously_recommended']

        y += 1
        print(id)
        print(y)
    except:
        continue
print(y)