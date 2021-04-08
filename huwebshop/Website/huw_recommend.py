from flask import Flask, request, session, render_template, redirect, url_for, g
from flask_restful import Api, Resource, reqparse
import os
from pymongo import MongoClient
from dotenv import load_dotenv
import psycopg2
import ast
from collections import Counter
import re

con = psycopg2.connect(
    host="localhost",
    database="huwebshop",
    user="postgres",
    password=" "
)
cur = con.cursor()

app = Flask(__name__)
api = Api(app)

# We define these variables to (optionally) connect to an external MongoDB
# instance.
envvals = ["MONGODBUSER","MONGODBPASSWORD","MONGODBSERVER"]
dbstring = 'mongodb+srv://{0}:{1}@{2}/test?retryWrites=true&w=majority'

# Since we are asked to pass a class rather than an instance of the class to the
# add_resource method, we open the connection to the database outside of the 
# Recom class.
load_dotenv()
if os.getenv(envvals[0]) is not None:
    envvals = list(map(lambda x: str(os.getenv(x)), envvals))
    client = MongoClient(dbstring.format(*envvals))
else:
    client = MongoClient()
database = client.huwebshop 

class Recom(Resource):
    """ This class represents the REST API that provides the recommendations for
    the webshop. At the moment, the API simply returns a random set of products
    to recommend."""

    def percentage(self, winkelwagen):
        cur.execute("select order_products, buid from sessions where order_products is not null and buid is not null")
        sessions_lst = cur.fetchall()

        buid_lst = []
        for session in sessions_lst:
            order_products = session[0]
            order_products = ast.literal_eval(order_products)
            for order_product in order_products:
                if order_product['id'] in winkelwagen:
                    buid_lst.append(session[1])
        buid_dct = Counter(buid_lst)

        profile_id_lst = []
        profile_session_dct = {}
        for buid in buid_dct.keys():
            cur.execute("select profile_id from profiles where buids like '%{}%'".format(buid))
            profile_id = cur.fetchall()
            if profile_id != []:
                profile_id = profile_id[0][0]
                profile_id_lst.append(profile_id)

                if profile_id not in profile_session_dct:
                    profile_session_dct[profile_id] = dict()
                profile_session_dct[profile_id][buid] = buid_dct[buid]

        profile_multiplier = {}
        for profile in profile_session_dct.keys():
            profile_multiplier[profile] = len(profile_session_dct[profile])
            for session_ in profile_session_dct[profile].keys():
                profile_multiplier[profile] = profile_multiplier[profile] * profile_session_dct[profile][session_]
        sorted_profile_multiplier = dict(sorted(profile_multiplier.items(), key=lambda item: item[1]))
        return sorted_profile_multiplier

    def producten_opvragen(self, profile_multiplier, winkelwagen):
        profile_multiplier_keys = list(profile_multiplier.keys())
        profile_multiplier_keys.reverse()

        producten_lst = []
        index = -1
        while len(profile_multiplier_keys) > index + 1 and len(producten_lst) < 4:
            index += 1
            cur.execute("select buids from profiles where profile_id = %s", (profile_multiplier_keys[index],))

            for buid in (cur.fetchall()[0][0].strip('{}')).split(','):
                cur.execute(
                    "select order_products from sessions where buid like '%{}%' and order_products is not null".format(
                        buid))
                order_products = cur.fetchall()
                for product_lst in order_products:
                    product_lst = product_lst[0]
                    product_lst = ast.literal_eval(product_lst)
                    for product_id in product_lst:
                        if product_id['id'] not in producten_lst and product_id['id'] not in winkelwagen:
                            producten_lst.append(product_id['id'])
                        if len(producten_lst) >= 4:
                            break
                    if len(producten_lst) >= 4:
                        break
                if len(producten_lst) >= 4:
                    break
        return producten_lst

    def check_aankoopgeschiedenis(self, visitor_id1):
        '''
        Checkt of gebruiker aankoopgeschiedenis heeft om op basis hiervan een recommendation te doen. Heeft gebruiker geen
        visitor id of geen aankopen, toon recommendation 1. Zo wel, toon recommendation 4
        '''
        cur.execute("SELECT buids FROM profiles WHERE profile_id like %s;", [visitor_id1])
        x = (str(cur.fetchone())[3:])[:-4]

        if x == '':  # geen matchende buid in sessions
            return ['38815', '25960', '32032', '29289']

        y = x.split(',')
        for i in y:
            return self.recommend_items(self.check_producten(i))

    def check_producten(self, buid):
        '''
        Haal producten op, zet product id's in lijst
        '''
        cur.execute("SELECT order_products FROM sessions WHERE buid like %s;", [buid])
        product_id_list = re.findall(r'\d+', str(cur.fetchall()))
        if not product_id_list:  # geen producten gekocht
            return ['38815', '25960', '32032', '29289']

        else:
            return self.define_gender_pref(product_id_list), self.define_category(product_id_list), self.define_price_range(
                product_id_list)

    def define_gender_pref(self, product_id_list):
        '''
        Haal product id's op, zet product genders in lijst. Vervolgens wordt er gekeken welk gender het meest voorkomt, deze
        wordt gereturned. Is er een draw? dan wordt er 1 item gereturned.
        '''
        gender_list = []
        for i in product_id_list:
            cur.execute("SELECT gender FROM products WHERE product_id like %s;", [str(i)])
            a = str(cur.fetchall())
            if 'None' in a:
                continue
            first = "[('"
            last = "',)]"

            try:
                start = a.index(first) + len(first)
                end = a.index(last, start)
                gender_str = ((a[start:end]))
                gender_list.append(gender_str)

            except ValueError:
                return print('error')

        if not gender_list:
            return None

        return max(gender_list, key=gender_list.count)

    def define_category(self, product_id_list):
        '''
        Haal product id's op, zet product category's in lijst. Vervolgens wordt er gekeken welke categeory het meest
        voorkomt, deze wordt gereturned. Is er een draw? dan wordt er 1 item gereturned. Is category Null, skip dit item
        '''
        category_list = []
        for i in product_id_list:
            cur.execute("SELECT category FROM products WHERE product_id like %s;", [str(i)])
            b = str(cur.fetchall())
            if 'None' in b:
                continue
            first = "[('"
            last = "',)]"

            try:
                start = b.index(first) + len(first)
                end = b.index(last, start)
                gender_str = (b[start:end])
                category_list.append(gender_str)

            except ValueError:
                return print('error')

        if not category_list:
            return None

        return max(category_list, key=category_list.count)

    def define_price_range(self, product_id_list):
        """
        Haal prijzen van eerder gekochten producten op uit database, maak er een lijst met floats van. Reken daarna
        het gemiddelde uit. Hiermee kunnen we een price range bepalen voor het te recommenden product.
        """
        prijs_lijst = []
        count = 0

        for i in product_id_list:
            cur.execute("SELECT price FROM products WHERE product_id like %s;", [str(i)])
            c = str(cur.fetchall())
            first = "[(Decimal('"
            last = "'),)]"

            try:
                start = c.index(first) + len(first)
                end = c.index(last, start)
                gender_str = (c[start:end])
                prijs_lijst.append(gender_str)

            except ValueError:
                return print('error')

        prijs_lijst = [float(i) for i in prijs_lijst]

        for i in prijs_lijst:
            count += i

        prijs_range_1_min = round(count / (len(prijs_lijst) * 0.8), 2)
        prijs_range_1_max = round(count / (len(prijs_lijst) * 1.2), 2)

        return prijs_range_1_min, prijs_range_1_max

    def recommend_items(self, d):
        """
        Toon lijst van 4 recommendations wanneer mogelijk. Is category en gender None, toon recommendation 1. Is lijst met gerecommende producten kleiner dan 2, toon ook recomendation 1
        """
        gegevens = list(d)

        gender = (gegevens[0])
        category = (gegevens[1])
        prijsranges = (gegevens[2])

        index_prijs_max = 0
        index_prijs_min = 1
        prijs_max = prijsranges[index_prijs_max]
        prijs_min = prijsranges[index_prijs_min]

        # Haal producten op uit database
        if gender is None and category is None:
            return ['38815', '25960', '32032', '29289']
        elif gender is not None and category is None:
            cur.execute(
                "select product_id from products where gender like '{}' and category is null and price between '{}' and '{}'".format(
                    gender, prijs_min, prijs_max))
        elif gender is None and category is not None:
            cur.execute(
                "select product_id from products where gender is null and category like '{}' and price between '{}' and '{}'".format(
                    category, prijs_min, prijs_max))
        else:
            cur.execute(
                "select product_id from products where gender like '{}' and category like '{}' and price between '{}' and '{}'".format(
                    gender, category, prijs_min, prijs_max))

        # Zet matchende product id's in net format in lijst
        recommendation_list = re.findall(r'\d+', str(cur.fetchall()))[:4]
        if len(recommendation_list) <= 2:
            return ['38815', '25960', '32032', '29289']

        return recommendation_list

    def get(self, profileid, count):
        """ This function represents the handler for GET requests coming in
        through the API. It currently returns a random sample of products. """
        count = str(count)
        if '12345' in count:
            count = count.split('12345')
            profile_multiplier = self.percentage(count)
            opgevraagde_producten = self.producten_opvragen(profile_multiplier, count)
            print("Get(try)   Winkelwagen-recommendation: {}".format(opgevraagde_producten))
            return opgevraagde_producten
        elif '12346' in count:
            alfabet = ['a', 'b', 'B', 'c', 'C', 'd', 'D', 'e', 'E', 'f', 'F', 'g', 'G', 'h', 'i', 'I', 'j', 'k',
                       'K', 'l', 'L', 'm', 'M', 'n', 'N', 'o', 'O', 'p', 'P', 'q', 'r', 'R', 's', 'S', 't', 'T',
                       'u', 'v', 'V', 'w', 'W', 'x', 'X', 'y', 'z', 'Z']
            count = count.split('12346')
            id = [count[0], '-']
            for x in count[1:]:
                id.append(alfabet[int(x)])
            print("Get(try)   {}".format("".join(id)))
            cur.execute("select samengekocht from samengekocht where product_id = '{}'".format("".join(id)))
        else:
            count = int(count)
            if count == 1000:
                data = self.check_aankoopgeschiedenis(profileid)
                print("Get(try)   overzichtpagina: {}".format(data))
                return data
            else:
                if count > 68:
                    cur.execute("select samengekocht from samengekocht where product_id = '{}'".format(count))
                if count <= 68:
                    if count > 15:
                        soort = "subcategory"
                        count -= 15
                    elif count <= 15:
                        soort = "category"
                    cur.execute("select {} from {}".format(soort, soort))
                    categories = []
                    for x in cur.fetchall():
                        categories.append(x[0])
                    count = categories[count]
                    cur.execute("select meestgekocht from {} where {} = '{}'".format(soort, soort, count))
                    print("Get(try)   {}: {}".format(soort, count))
        # except:
        #     print("Get(except)")
        #     cur.execute("select samengekocht from samengekocht where product_id = '{}'".format(count))
        data = cur.fetchall()
        data = data[0][0][1:len(data[0][0])-1:].split(",")[:4]
        print("Get   data: {}".format(data))
        return data, 200

# This method binds the Recom class to the REST API, to parse specifically
# requests in the format described below.
api.add_resource(Recom, "/<string:profileid>/<int:count>")
