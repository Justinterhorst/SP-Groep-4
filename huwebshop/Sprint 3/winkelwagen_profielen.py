import psycopg2
import random
import ast
from collections import Counter

def winkelwagen_inhoud():
    cur.execute("select product_id from products")
    product_id = cur.fetchall()
    product_id_lst = []
    for pid in product_id:
        product_id_lst.append(pid[0])

    inhoud = []
    aantal_winkelwagen = random.randint(1, 10)
    for x in range(aantal_winkelwagen):
        product_index = random.randint(1, 33979)
        inhoud.append(product_id_lst[product_index])
    return inhoud

def percentage(winkelwagen):
    cur.execute("select order_products, buid from sessions where order_products is not null")
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
        # buid = buid.strip('{}')
        cur_buid = '%' + buid + '%'
        cur.execute("select profile_id from profiles where buids like %s", (cur_buid,))
        profile_id = cur.fetchall()
        if profile_id != []:
            profile_id = profile_id[0]
            profile_id = profile_id[0]
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

def producten_opvragen(profile_multiplier, winkelwagen):
    profile_multiplier_keys = list(profile_multiplier.keys())
    profile_multiplier_keys.reverse()

    producten_lst = []
    index = -1
    while len(profile_multiplier_keys) > index + 1:
        index += 1
        cur.execute("select buids from profiles where profile_id = %s", (profile_multiplier_keys[index],))
        buids = cur.fetchall()
        buids = buids[0]
        buids = buids[0]
        buids = buids.strip('{}')
        buids_lst = buids.split(',')

        for buid in buids_lst:
            cur_buid = '%' + buid + '%'
            cur.execute("select order_products from sessions where buid like %s and order_products is not null", (cur_buid,))
            order_products = cur.fetchall()
            for product_lst in order_products:
                product_lst = product_lst[0]
                product_lst = ast.literal_eval(product_lst)
                for product_id in product_lst:
                    producten_lst.append(product_id['id'])
            if len(producten_lst) > 5:
                break

    for product in producten_lst:
        if product in winkelwagen:
            producten_lst.remove(product)
    producten_lst = list(dict.fromkeys(producten_lst))

    producten_dct = {}
    for product_ in producten_lst:
        cur.execute("select price from products where product_id = %s", (product_,))
        price = cur.fetchall()
        price = price[0]
        price = price[0]
        producten_dct[product_] = price
    sorted_producten_dct = dict(sorted(producten_dct.items(), key=lambda item: item[1]))
    price_sorted_product_lst = list(sorted_producten_dct.keys())
    return price_sorted_product_lst


if __name__ == '__main__':
    con = psycopg2.connect(
        host="localhost",
        database="huwebshop",
        user="Niels",
        password="niels"
    )

    cur = con.cursor()

    winkelwagen = winkelwagen_inhoud()
    profile_multiplier = percentage(winkelwagen)
    opgevraagde_producten = producten_opvragen(profile_multiplier, winkelwagen)
    print(opgevraagde_producten)

    # con.commit()
    cur.close()
    con.close()