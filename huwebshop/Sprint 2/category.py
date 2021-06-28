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


def category(con):
    cur = con.cursor()

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

    cur.execute("select data from lijsten")
    order_products = (cur.fetchone()[0].strip('{}')).split(',')

    for x in categories:
        count = 0
        bekekenproducten = []
        for y in viewed_before:
            cur.execute("select category from products where product_id = '{}'".format(y))
            category = cur.fetchone()
            if category is not None and category[0] == x:
                bekekenproducten.append(y)
            count += 1
            print("{} / 1464507".format(count))
        if not bekekenproducten:
            bekekenproducten = None

        meestbekeken = betere_recommendation(bekekenproducten)

        count = 0
        gekochteproducten = []
        for y in order_products:
            cur.execute("select category from products where product_id = '{}'".format(y))
            category = cur.fetchone()
            if category is not None and category[0] == x:
                gekochteproducten.append(y)
            count += 1
            print("{} / 658960".format(count))
        if not gekochteproducten:
            gekochteproducten = None

        meestgekocht = betere_recommendation(gekochteproducten)

        cur.execute("insert into category (category, bekekenproducten, gekochteproducten, meestbekeken, meestgekocht) values (%s, %s, %s, %s, %s)",
                    (x, bekekenproducten, gekochteproducten, meestbekeken, meestgekocht))
        con.commit()
    cur.close()
    con.close()


category(psycopg2.connect(
    host="localhost",
    database="huwebshop",
    user="postgres",
    password=" "
))
