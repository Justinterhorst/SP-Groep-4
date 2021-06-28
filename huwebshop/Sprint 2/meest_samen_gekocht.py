import psycopg2


def meestgekocht(con):
    cur = con.cursor()

    cur.execute("select product_id from products where price > 0")
    products = []
    for x in cur.fetchall():
        products.append(x[0])
    """
    Alle producten in lijst zetten zodat er later gekeken kan worden of een id wel bestaat
    """

    count = -1
    for x in products:
        count += 1
        print(count)

        cur.execute("select order_products from sessions where order_products LIKE '%{}%'".format(x))
        order_products = cur.fetchall()

        samengekocht = []
        for y in order_products:
            if x in y[0] and y[0].count('{') > 1:
                if 'price' in y[0]:
                    for z in y[0].split(','):
                        if z[9:len(z)-1:] in products and z[9:len(z)-1:] != x:
                            samengekocht.append(z[9:len(z)-1:])
                else:
                    for z in y[0][0:len(y[0]) - 1:].split(','):
                        if z[9:len(z)-2:] != x:
                            samengekocht.append(z[9:len(z)-2:])
        """
        Query hierboven haalt alle gekochte producten die het product id bevatten op. Vervolgens worden alle producten
        die samen met het product id gekocht zijn in een lijst gezet.
        """

        if len(set(samengekocht)) >= 4:
            meestgekocht = []
            for i in range(0, 4):
                meestvoorkomende = max(set(samengekocht), key=samengekocht.count)
                samengekocht = [x for x in samengekocht if x != meestvoorkomende]
                meestgekocht.append(meestvoorkomende)
        elif len(set(samengekocht)) != 0:
            meestgekocht = samengekocht
        elif len(set(samengekocht)) == 0:
            meestgekocht = None
        """
        Hier worden de 4 meest voorkomende vastgesteld. Als er meer dan 4 verschillende producten samen met het product
        id gekocht zijn loopt er een for loop 4x. Eerst wordt er gekeken welk product het meeste voorkomt, vervolgens
        wordt die uit de samengekocht lijst verwijderd, en als laatste wordt het meest voorkomende id aan een nieuwe 
        lijst toegevoegd.
        """

        print(x, meestgekocht)

        cur.execute("insert into samengekocht (product_id, samengekocht) values (%s, %s)",
                    (x, meestgekocht))
        con.commit()

    cur.close()
    con.close()


meestgekocht(psycopg2.connect(
    host="localhost",
    database="huwebshop",
    user="postgres",
    password=" "
))
