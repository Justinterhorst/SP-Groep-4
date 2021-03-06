import psycopg2


def meestgekocht(con):
    cur = con.cursor()

    cur.execute("select product_id from products where discount is not null")
    discounts = []
    for x in cur.fetchall():
        discounts.append(x[0])
    """
    Alle discounts in een lijst zetten zodat er later gekeken kan worden of een id discount heeft
    """

    cur.execute("select order_products from sessions where order_products is not null")
    order_products = cur.fetchall()

    products = []
    count = 0
    for y in order_products:
        if 'price' in y[0]:
            for z in y[0].split(','):
                if z[9:len(z)-1:] in discounts:
                    products.append(z[9:len(z)-1:])
        else:
            if ',' in y[0]:
                for z in y[0][0:len(y[0]) - 1:].split(','):
                    if z[9:len(z)-2:] in discounts:
                        products.append(z[9:len(z)-2:])
            else:
                if len(y[0][9:len(y[0])-3:]) > 0:
                    if y[0][9:len(y[0])-3:] in discounts:
                        products.append(y[0][9:len(y[0])-3:])
        count += 1
        print("{}/185113".format(count))
    """
    Query hierboven haalt alle gekochte producten op. De loop gaat elk gekochte product langs om na te gaan of het een
    discount heeft. Zo ja, wordt het (met wat modificatie om de data goed te kunnen gebruiken) in een lijst gezet. 
    """

    meestgekocht = []
    for i in range(0, 4):
        meestvoorkomende = max(set(products), key=products.count)
        products = [x for x in products if x != meestvoorkomende]
        meestgekocht.append(meestvoorkomende)
    """
    Hier worden de 4 meest voorkomende vastgesteld. Eerst wordt er gekeken welk product het meeste voorkomt, vervolgens
    wordt die uit de samengekocht lijst verwijderd, en als laatste wordt het meest voorkomende id aan een nieuwe lijst 
    toegevoegd.
    """

    print(meestgekocht)

    cur.close()
    con.close()


meestgekocht(psycopg2.connect(
    host="localhost",
    database="huwebshop",
    user="postgres",
    password=" "
))
