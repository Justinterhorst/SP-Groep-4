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
        if len(set(data)) < 5:
            aantal = len(set(data))
        elif len(set(data)) >= 5:
            aantal = 5

        lijst = []
        for i in range(0, aantal):
            meestvoorkomende = max(set(data), key=data.count)
            data = [x for x in data if x != meestvoorkomende]
            lijst.append(meestvoorkomende)
        if not lijst:
            lijst = None
        return lijst


def subcategory():
    cur.execute("select sub_category from products where sub_category is not null")
    subcategories = list(set(cur.fetchall()))

    cur.execute("select viewed_before from visitors where viewed_before is not null")
    viewed_before = cur.fetchall()

    cur.execute("select order_products from sessions where has_sale is true and order_products is not null")
    order_products = cur.fetchall()


    count = 0
    for x in subcategories:
        bekekenproducten = []
        for y in viewed_before:
            if "," in y[0][1:len(y[0])-1:]:
                for z in y[0][1:len(y[0])-1:].split(","):
                    cur.execute("select sub_category from products where product_id = '{}'".format(z))
                    subcategory = cur.fetchone()
                    if subcategory is None:
                        continue
                    elif subcategory[0] == x[0]:
                        bekekenproducten.append(z)
            else:
                cur.execute("select sub_category from products where product_id = '{}'".format(y[0][1:len(y[0])-1:]))
                subcategory = cur.fetchone()
                if subcategory[0] == x[0]:
                    bekekenproducten.append(y[0][1:len(y[0])-1:])
        if not bekekenproducten:
            bekekenproducten = None

        meestbekeken = betere_recommendation(bekekenproducten)

        gekochteproducten = []
        for y in order_products:
            if "," in y[0][9:len(y[0]) - 3:]:
                for z in y[0][0:len(y[0]) - 1:].split(","):
                    cur.execute("select sub_category from products where product_id = '{}'".format(z[9:len(z) - 2:]))
                    subcategory = cur.fetchone()
                    if subcategory[0] == x[0]:
                        gekochteproducten.append(z[9:len(z) - 2:])
            else:
                cur.execute("select sub_category from products where product_id = '{}'".format(y[0][9:len(y[0]) - 3:]))
                subcategory = cur.fetchone()
                if subcategory[0] == x[0]:
                    gekochteproducten.append(y[0][9:len(y) - 4:])
        if not gekochteproducten:
            gekochteproducten = None

        meestgekocht = betere_recommendation(gekochteproducten)

        cur.execute("insert into subcategory (subcategory, bekekenproducten, gekochteproducten, meestbekeken, meestgekocht) values (%s, %s, %s, %s, %s)",
                    (x[0], bekekenproducten, gekochteproducten, meestbekeken, meestgekocht))

        count += 1
        print("{} / {}   ({:.1f}%)".format(count, 54, count * 100 / 54))


subcategory()

con.commit()
cur.close()
con.close()