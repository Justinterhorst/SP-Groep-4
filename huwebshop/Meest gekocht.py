import psycopg2

con = psycopg2.connect(
    host="localhost",
    database="huwebshop",
    user="postgres",
    password=" "
)
cur = con.cursor()


def meestgekocht():
    cur.execute("select product_id from products")
    products = cur.fetchall()

    cur.execute("select order_products from sessions where order_products is not null")
    order_products = cur.fetchall()

    count = 0
    for x in products:
        samengekocht = []
        for y in order_products:
            producten = []
            if "'" in y[0][9:len(y[0])-3:]:
                for z in y[0][0:len(y[0])-1:].split(','):
                    producten.append(z[9:len(z)-2:])
            if x[0] in producten:
                for z in producten:
                    if z != id:
                        samengekocht.append(z)

        if len(set(samengekocht)) >= 4:
            meestgekocht = []
            for i in range(0, 4):
                meestvoorkomende = max(set(samengekocht), key=samengekocht.count)
                samengekocht = [x for x in samengekocht if x != meestvoorkomende]
                meestgekocht.append(meestvoorkomende)
        elif len(set(samengekocht)) < 4:
            meestgekocht = None

        cur.execute("insert into samengekocht (product_id, samengekocht) values (%s, %s)",
                    (x[0], meestgekocht))

        count += 1
        print("{} / {}   ({:.1f}%)".format(count, 33979, count * 100 / 33979))


meestgekocht()

con.commit()
cur.close()
con.close()