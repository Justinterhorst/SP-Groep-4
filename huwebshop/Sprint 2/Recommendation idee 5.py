import psycopg2

con = psycopg2.connect(
    host="localhost",
    database="huwebshop",
    user="postgres",
    password=" "
)
cur = con.cursor()


def meestBekeken():
    cur.execute("select viewed_before from visitors where viewed_before is not null")
    viewed_before = cur.fetchall()

    cur.execute("select * from products where sub_sub_category is not null")
    products = cur.fetchall()

    count = 0
    for product in products:
        count += 1
        print("{} / {}   ({:.1f}%)".format(count, 13676, count * 100 / 13676))

        bekekenProducten = []
        for x in viewed_before:
            if ',' in (x[0][1:len(x[0]) - 1:]):
                for y in x[0][1:len(x[0]) - 1:].split(','):
                    cur.execute("select sub_sub_category from products where product_id = '{}'".format(y))
                    sub_sub_category = cur.fetchone()
                    if sub_sub_category[0] == product[12]:
                        bekekenProducten.append(y)
            else:
                y = x[0][1:len(x[0]) - 1:]
                cur.execute("select sub_sub_category from products where product_id = '{}'".format(y))
                sub_sub_category = cur.fetchone()
                if sub_sub_category[0] == product[12]:
                    bekekenProducten.append(y)

        if len(set(bekekenProducten)) < 5:
            aantal = len(set(bekekenProducten))
        elif len(set(bekekenProducten)) >= 5:
            aantal = 5

        meestBekekenProducten = []
        for i in range(0, aantal):
            meestVoorkomende = max(set(bekekenProducten), key=bekekenProducten.count)
            bekekenProducten = [x for x in bekekenProducten if x not in meestVoorkomende]
            meestBekekenProducten.append(meestVoorkomende)

        cur.execute("insert into meestbekeken (product_id, meestbekeken_id) values (%s, %s)",
                    (x[0], meestBekekenProducten))


meestBekeken()

con.commit()
cur.close()
con.close()