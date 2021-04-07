from flask import Flask, request, session, render_template, redirect, url_for, g
from flask_restful import Api, Resource, reqparse
import os
from pymongo import MongoClient
from dotenv import load_dotenv
import psycopg2

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

    def get(self, profileid, count):
        """ This function represents the handler for GET requests coming in
        through the API. It currently returns a random sample of products. """
        try:
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
                    cur.execute("select meestgekocht from recommendations where product_id = '{}'".format(count))
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
            print(cur.fetchone())
            cur.execute("select meestgekocht from recommendations where product_id = '{}'".format(count))
        data = cur.fetchall()
        data = data[0][0][1:len(data[0][0])-1:].split(",")[:4]
        print("Get   data: {}".format(data))
        return data, 200

# This method binds the Recom class to the REST API, to parse specifically
# requests in the format described below.
api.add_resource(Recom, "/<string:profileid>/<int:count>")