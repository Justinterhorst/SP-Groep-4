#verander visitor_id1's naar jou variabele voor visitorid


import psycopg2
import re


con = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password=" "
)
cur = con.cursor()

visitor_id1 = '5a394487a825610001bb7348'


def check_aankoopgeschiedenis(visitor_id1):
    '''
    Checkt of gebruiker aankoopgeschiedenis heeft om op basis hiervan een recommendation te doen. Heeft gebruiker geen
    visitor id of geen aankopen, toon recommendation 1. Zo wel, toon recommendation 4
    '''
    cur.execute("SELECT buids FROM profiles WHERE profile_id like %s;", [visitor_id1])
    x = cur.fetchone()
    x = str(x)
    x = x[3:]
    x = x[:-4]

    if x == '': #geen matchende buid in sessions
        print('hier moet recomendation 1 komen')
        #roep recomendation 1 aan !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        return

    y = x.split(',')
    for i in y:
        recommend_items(check_producten(i))


def check_producten(buid):
    '''
    Haal producten op, zet product id's in lijst
    '''
    cur.execute("SELECT order_products FROM sessions WHERE buid like %s;", [buid])
    product_id = cur.fetchall()
    product_id = str(product_id)
    product_id_list = re.findall(r'\d+', product_id)
    if not product_id_list: #geen producten gekocht
        print('hier moet recomendation komen')
        #roep recomendation 1 aan!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        return

    else:
        return define_gender_pref(product_id_list), define_category(product_id_list), define_price_range(product_id_list)



def define_gender_pref(product_id_list):
    '''
    Haal product id's op, zet product genders in lijst. Vervolgens wordt er gekeken welk gender het meest voorkomt, deze
    wordt gereturned. Is er een draw? dan wordt er 1 item gereturned.
    '''
    gender_list = []
    for i in product_id_list:
        cur.execute("SELECT gender FROM products WHERE product_id like %s;", [str(i)])
        gender = cur.fetchall()
        a = str(gender)
        if 'None' in a:
            continue
        first = "[('"
        last = "',)]"

        try:
            start = a.index(first) + len(first)
            end = a.index(last, start)
            gender_str = ((a[start:end]))
            gender_list.append(gender_str)

        except ValueError:
            return print('error')

    if not gender_list:
        return None

    return max(gender_list, key=gender_list.count)



def define_category(product_id_list):
    '''
    Haal product id's op, zet product category's in lijst. Vervolgens wordt er gekeken welke categeory het meest
    voorkomt, deze wordt gereturned. Is er een draw? dan wordt er 1 item gereturned. Is category Null, skip dit item
    '''
    category_list = []
    for i in product_id_list:
        cur.execute("SELECT category FROM products WHERE product_id like %s;", [str(i)])
        category = cur.fetchall()
        a = str(category)
        if 'None' in a:
            continue
        first = "[('"
        last = "',)]"

        try:
            start = a.index(first) + len(first)
            end = a.index(last, start)
            gender_str = (a[start:end])
            category_list.append(gender_str)

        except ValueError:
            return print('error')

    if not category_list:
        return None

    return max(category_list, key=category_list.count)




def define_price_range(product_id_list):
    """
    Haal prijzen van eerder gekochten producten op uit database, maak er een lijst met floats van. Reken daarna
    het gemiddelde uit. Hiermee kunnen we een price range bepalen voor het te recommenden product.
    """
    prijs_lijst = []
    count = 0

    for i in product_id_list:
        cur.execute("SELECT price FROM products WHERE product_id like %s;", [str(i)])
        prijs = cur.fetchall()
        a = str(prijs)
        first = "[(Decimal('"
        last = "'),)]"

        try:
            start = a.index(first) + len(first)
            end = a.index(last, start)
            gender_str = (a[start:end])
            prijs_lijst.append(gender_str)

        except ValueError:
            return print('error')

    prijs_lijst = [float(i) for i in prijs_lijst]

    for i in prijs_lijst:
        count += i

    prijs_range_1_min = round(count / (len(prijs_lijst) * 0.8), 2)
    prijs_range_1_max = round(count / (len(prijs_lijst) * 1.2), 2)

    return prijs_range_1_min, prijs_range_1_max


def recommend_items(a):
    """
    Toon lijst van 4 recommendations wanneer mogelijk. Is category en gender None, toon recommendation 1. Is lijst met gerecommende producten kleiner dan 2, toon ook recomendation 1
    """
    gegevens = list(a)

    gender = (gegevens[0])
    category = (gegevens[1])
    prijsranges = (gegevens[2])

    index_prijs_max = 0
    index_prijs_min = 1
    prijs_max = prijsranges[index_prijs_max]
    prijs_min = prijsranges[index_prijs_min]


    # Haal producten op uit database
    if gender is None and category is None:
        print('recomendation 1') #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


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

    recommendations = cur.fetchall()

    #Zet matchende product id's in net format in lijst
    recommendations_string = str(recommendations)
    recommendation_list = re.findall(r'\d+', recommendations_string)
    if len(recommendation_list) <= 2:
        print('recomendation 1 functie')
        # toon recomendation 1 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    print(recommendation_list[:4])




check_aankoopgeschiedenis(visitor_id1)

