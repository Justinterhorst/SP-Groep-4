import psycopg2
import re

def check_aankoopgeschiedenis(con, visitor_id1):
    '''
    Checkt of gebruiker aankoopgeschiedenis heeft om op basis hiervan een recommendation te doen. Heeft gebruiker geen
    visitor id of geen aankopen, toon recommendation 1. Zo wel, toon recommendation 4
    '''
    cur = con.cursor()

    cur.execute("SELECT buids FROM profiles WHERE profile_id like %s;", [visitor_id1])
    x = (str(cur.fetchone())[3:])[:-4]

    if x == '': #geen matchende buid in sessions
        return ['38815', '25960', '32032', '29289']

    y = x.split(',')
    for buid in y:
        recommend_items(cur, list(check_producten(cur, buid)))

def check_producten(cur, buid):
    '''
    Haal producten op, zet product id's in lijst
    '''
    cur.execute("SELECT order_products FROM sessions WHERE buid like %s;", [buid])
    product_id_list = re.findall(r'\d+', str(cur.fetchall()))
    if not product_id_list:  # geen producten gekocht
        return ['38815', '25960', '32032', '29289']
    else:
        return define_gender_pref(cur, product_id_list), define_category(cur, product_id_list), \
                    define_price_range(cur, product_id_list)

def define_gender_pref(cur, product_id_list):
    '''
    Haal product id's op, zet product genders in lijst. Vervolgens wordt er gekeken welk gender het meest voorkomt, deze
    wordt gereturned. Is er een draw? dan wordt er 1 item gereturned.
    '''
    gender_list = []
    for i in product_id_list:
        cur.execute("SELECT gender FROM products WHERE product_id like %s;", [str(i)])
        gender = str(cur.fetchall())

        if 'None' in gender:
            continue
        first = "[('"
        last = "',)]"

        try:
            start = gender.index(first) + len(first)
            end = gender.index(last, start)
            gender_str = ((gender[start:end]))
            gender_list.append(gender_str)

        except ValueError:
            return print('error')

    if not gender_list:
        return None

    return max(gender_list, key=gender_list.count)

def define_category(cur, product_id_list):
    '''
    Haal product id's op, zet product category's in lijst. Vervolgens wordt er gekeken welke categeory het meest
    voorkomt, deze wordt gereturned. Is er een draw? dan wordt er 1 item gereturned. Is category Null, skip dit item
    '''
    category_list = []
    for i in product_id_list:
        cur.execute("SELECT category FROM products WHERE product_id like %s;", [str(i)])
        category = str(cur.fetchall())

        if 'None' in category:
            continue
        first = "[('"
        last = "',)]"

        try:
            start = category.index(first) + len(first)
            end = category.index(last, start)
            gender_str = (category[start:end])
            category_list.append(gender_str)

        except ValueError:
            return print('error')

    if not category_list:
        return None

    return max(category_list, key=category_list.count)

def define_price_range(cur, product_id_list):
    """
    Haal prijzen van eerder gekochten producten op uit database, maak er een lijst met floats van. Reken daarna
    het gemiddelde uit. Hiermee kunnen we een price range bepalen voor het te recommenden product.
    """
    prijs_lijst = []
    count = 0

    for i in product_id_list:
        cur.execute("SELECT price FROM products WHERE product_id like %s;", [str(i)])
        prijs = str(cur.fetchall())

        first = "[(Decimal('"
        last = "'),)]"

        try:
            start = prijs.index(first) + len(first)
            end = prijs.index(last, start)
            gender_str = (prijs[start:end])
            prijs_lijst.append(gender_str)

        except ValueError:
            return print('error')

    prijs_lijst = [float(i) for i in prijs_lijst]

    for i in prijs_lijst:
        count += i

    return round(count / (len(prijs_lijst) * 0.8), 2), round(count / (len(prijs_lijst) * 1.2), 2)

def recommend_items(cur, gegevens):
    """
    Toon lijst van 4 recommendations wanneer mogelijk. Is category en gender None, toon recommendation 1. Is lijst met gerecommende producten kleiner dan 2, toon ook recomendation 1
    """
    gender = gegevens[0]
    category = gegevens[1]
    prijsranges = gegevens[2]

    prijs_max = prijsranges[0]
    prijs_min = prijsranges[1]

    # Haal producten op uit database
    if gender is None and category is None:
        return ['38815', '25960', '32032', '29289']
    elif gender is not None and category is None:
        cur.execute(
            "select product_id from products where gender like '{}' and category is null and price between '{}' and '{}'".format(
                gender, prijs_min, prijs_max))
    elif gender is None and category is not None:
        cur.execute(
            "select product_id from products where gender is null and category like '{}' and price between '{}' and '{}'".format(
                category, prijs_min, prijs_max))
    else:
        cur.execute(
            "select product_id from products where gender like '{}' and category like '{}' and price between '{}' and '{}'".format(
                gender, category, prijs_min, prijs_max))

    # Zet matchende product id's in net format in lijst
    recommendation_list = re.findall(r'\d+', str(cur.fetchall()))[:4]
    if len(recommendation_list) <= 2:
        return ['38815', '25960', '32032', '29289']

    return recommendation_list

check_aankoopgeschiedenis(psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password=" "
), '5a394487a825610001bb7348')
