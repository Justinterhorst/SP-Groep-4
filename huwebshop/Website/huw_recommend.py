from flask import Flask, request, session, render_template, redirect, url_for, g
from flask_restful import Api, Resource, reqparse
import os
from pymongo import MongoClient
from dotenv import load_dotenv
import psycopg2
import random
import ast
from collections import Counter

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

    def get(self, profileid, count):
        """ This function represents the handler for GET requests coming in
        through the API. It currently returns a random sample of products. """
        try:
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
                    cur.execute("select buids from profiles where profile_id = '{}'".format(profileid))
                    buids = cur.fetchone()[0]
                    if buids is not None:
                        for x in buids[1:len(buids)-1:].split(','):
                            cur.execute("select order_products from sessions where buid LIKE '%{}%' and order_products is not null".format(x))
                            data = cur.fetchone()
                            aankopen = True if (data is not None) else False
                            if aankopen is True:
                                break
                    else:
                        aankopen = False
                    if aankopen is False:
                        return ['38815', '25960', '32032', '29289'], 200
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
        except:
            print("Get(except)")
            cur.execute("select samengekocht from samengekocht where product_id = '{}'".format(count))
        data = cur.fetchall()
        data = data[0][0][1:len(data[0][0])-1:].split(",")[:4]
        print("Get   data: {}".format(data))
        return data, 200

# This method binds the Recom class to the REST API, to parse specifically
# requests in the format described below.
api.add_resource(Recom, "/<string:profileid>/<int:count>")
