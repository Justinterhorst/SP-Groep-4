import psycopg2


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


def subcategory(con):
    cur = con.cursor()
    
    cur.execute("select sub_category from products where sub_category is not null")
    subcategories = list(set(cur.fetchall()))

    cur.execute("select viewed_before from profiles where viewed_before is not null")
    viewed_before = []
    for y in cur.fetchall():
        if "," in y[0][1:len(y[0]) - 1:]:
            for z in y[0][1:len(y[0]) - 1:].split(","):
                viewed_before.append(z)
        else:
            viewed_before.append(y[0][1:len(y[0]) - 1:])

    cur.execute("select data from lijsten")
    order_products = (cur.fetchone()[0].strip('{}')).split(',')

    for x in subcategories:
        count = 0
        bekekenproducten = []
        for y in viewed_before:
            cur.execute("select subcategory from products where product_id = '{}'".format(y))
            subcategory = cur.fetchone()
            if subcategory is not None and subcategory[0] == x:
                bekekenproducten.append(y)
            count += 1
            print("{} / 1464507".format(count))
        if not bekekenproducten:
            bekekenproducten = None

        meestbekeken = betere_recommendation(bekekenproducten)

        count = 0
        gekochteproducten = []
        for y in order_products:
            cur.execute("select subcategory from products where product_id = '{}'".format(y))
            subcategory = cur.fetchone()
            if subcategory is not None and subcategory[0] == x:
                gekochteproducten.append(y)
            count += 1
            print("{} / 658960".format(count))
        if not gekochteproducten:
            gekochteproducten = None

        meestgekocht = betere_recommendation(gekochteproducten)

        cur.execute("insert into subcategory (subcategory, bekekenproducten, gekochteproducten, meestbekeken, meestgekocht) values (%s, %s, %s, %s, %s)",
                    (x[0], bekekenproducten, gekochteproducten, meestbekeken, meestgekocht))
        con.commit()
    cur.close()
    con.close()


subcategory(psycopg2.connect(
    host="localhost",
    database="huwebshop",
    user="postgres",
    password=" "
))
