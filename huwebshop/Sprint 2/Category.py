import psycopg2

con = psycopg2.connect(
    host="localhost",
    database="huwebshop",
    user="postgres",
    password=" "
)
cur = con.cursor()


def betere_recommendation(data):
    if data is None:
        return None
    else:
        if len(set(data)) >= 4:
            lijst = []
            for i in range(0, 4):
                meestvoorkomende = max(set(data), key=data.count)
                data = [x for x in data if x != meestvoorkomende]
                lijst.append(meestvoorkomende)
        elif len(set(data)) != 0:
            lijst = list(set(data))
        elif len(set(data)) == 0:
            lijst = None
        return lijst


def category():
    cur.execute("select product_id from products where category is not null")
    products = []
    for x in cur.fetchall():
        products.append(x[0])

    cur.execute("select category from products where category is not null")
    categories = []
    for x in set(cur.fetchall()):
        if "{" in x[0]:
            continue
        else:
            categories.append(x[0])

    cur.execute("select viewed_before from profiles where viewed_before is not null")
    viewed_before = []
    for y in cur.fetchall():
        if "," in y[0][1:len(y[0])-1:]:
            for z in y[0][1:len(y[0])-1:].split(","):
                viewed_before.append(z)
        else:
            viewed_before.append(y[0][1:len(y[0])-1:])

    cur.execute("select order_products from sessions where order_products is not null")
    order_products = []
    count = 0
    for y in cur.fetchall():
        if 'price' in y[0]:
            for z in y[0].split(','):
                if z[9:len(z)-1:] in products:
                    order_products.append(z[9:len(z)-1:])
        elif ',' in y[0][9:len(y[0])-3:]:
            for z in y[0][0:len(y[0])-1:].split(','):
                order_products.append(z[9:len(z)-2:])
        else:
            order_products.append(y[0][9:len(y)-4:])
        count += 1
        print("{}/185113".format(count))

    for x in categories:
        bekekenproducten = []
        for y in viewed_before:
            if "," in y[0][1:len(y[0])-1:]:
                for z in y[0][1:len(y[0])-1:].split(","):
                    cur.execute("select category from products where product_id = '{}'".format(z))
                    category = cur.fetchone()
                    if category is None:
                        continue
                    elif category[0] == x:
                        bekekenproducten.append(z)
            else:
                cur.execute("select category from products where product_id = '{}'".format(y[0][1:len(y[0])-1:]))
                category = cur.fetchone()
                if category[0] == x:
                    bekekenproducten.append(y[0][1:len(y[0])-1:])
        if not bekekenproducten:
            bekekenproducten = None

        meestbekeken = betere_recommendation(bekekenproducten)

        gekochteproducten = []
        for y in order_products:
            if 'price' in y[0]:
                for z in y[0].split(','):
                    try:
                        cur.execute("select category from products where product_id = '{}'".format(z[9:len(z)-1:]))
                        category = cur.fetchone()
                        if category is not None and category[0] == x:
                            gekochteproducten.append(z[9:len(z)-1:])
                    except:
                        continue
            elif "," in y[0][9:len(y[0])-3:]:
                for z in y[0][0:len(y[0])-1:].split(","):
                    cur.execute("select category from products where product_id = '{}'".format(z[9:len(z)-2:]))
                    category = cur.fetchone()
                    if category is not None and category[0] == x:
                        gekochteproducten.append(z[9:len(z)-2:])
            else:
                cur.execute("select category from products where product_id = '{}'".format(y[0][9:len(y[0])-3:]))
                category = cur.fetchone()
                if category is not None and category[0] == x:
                    gekochteproducten.append(y[0][9:len(y)-4:])
        if not gekochteproducten:
            gekochteproducten = None

        meestgekocht = betere_recommendation(gekochteproducten)

        cur.execute("insert into category (category, bekekenproducten, gekochteproducten, meestbekeken, meestgekocht) values (%s, %s, %s, %s, %s)",
                    (x, bekekenproducten, gekochteproducten, meestbekeken, meestgekocht))
        con.commit()
    cur.close()
    con.close()


category()