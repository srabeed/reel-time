import os 
import time 

from flask import Flask, request, render_template
import mysql.connector
from mysql.connector import errorcode

app = Flask(__name__)

def get_db_creds():
    # db = "reel_time_db"
    # username = "myadmin"
    # password = "Reeltime!"
    # hostname = "reel-time-db.chr9q1gt6nxw.us-east-1.rds.amazonaws.com"
    db = os.environ.get("DB", None) or os.environ.get("database", None)
    username = os.environ.get("USER", None) or os.environ.get("username", None)
    password = os.environ.get("PASSWORD", None) or os.environ.get("password", None)
    hostname = os.environ.get("HOST", None) or os.environ.get("dbhost", None)
    port = 3306
    return db, username, password, hostname, port

def create_table():
    # Check if table exists or not. Create and populate it only if it does not exist.
    db, username, password, hostname, port = get_db_creds()
    table_ddl = 'CREATE TABLE fishes(area varchar(100), location varchar(100), species varchar(100), amount INT UNSIGNED NOT NULL, PRIMARY KEY (species))'

    cnx = ''
    try:
        cnx = mysql.connector.connect(user=username, password=password,
                                      host=hostname, port=port,
                                      database=db)
    except Exception as exp:
        print(exp)
        import MySQLdb
        cnx = MySQLdb.connect(unix_socket=hostname, user=username, passwd=password, port=port, db=db)

    cur = cnx.cursor()

    try:
        cur.execute(table_ddl)
        cnx.commit()
    except mysql.connector.Error as err:

        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)

class Water:
    def __init__(self, name, lat, lng):
        self.name = name
        self.lat = lat
        self.lng = lng

waters = (
    Water('Grapevine Lake',        32.9954785, -97.156763),
    Water('Lewisville Lake',       33.1636987, -97.0695049),
    Water('Joe Pool Lake',         32.5916823, -97.0961563),
    Water('Lake Ray Hubbard',      32.9027607, -96.66767),
    Water('Cedar Creek Reservoir', 32.2969884, -96.2492798)
    Water('Lake Houston',        30.0002148,-95.2473016),
    Water('Sheldon Lake',       29.8672648,-95.193382),
    Water('Buffalo Bayou',         29.7394345,-95.4612953),
    Water('Clear Lake',      29.5838715,-95.1430026),
    Water('Spring Creek', 30.0939521,-95.6261575)
    Water('Colorado River',        30.6424196,-101.0677113),
    Water('Lady Bird Lake',       30.2689918,-97.7683175),
    Water('Lake Austin',         30.3436219,-97.9221555),
    Water('Shoal Creek',      30.3438809,-97.9221556),
    Water('Barton Creek', 30.2823514,-97.8841912),
    Water('Mueller Lake', 30.2967752,-97.708041)
)

waters_by_name = {water.name: water for water in waters}

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/log")
def log_catch():
    return render_template("log.html")

@app.route('/log_catch', methods=['POST'])
def add_to_db():
    print("Received request.")
    # Error checking for empty fields 
    area = request.form.get('area')
    if not (area):
        return render_template('log.html', message="Please select an area.")

    location = request.form.get('location')
    if not (location):
        return render_template('log.html', message="Please select a location.")

    species = request.form.get('species')
    if not (species):
        return render_template('log.html', message="Please select a species.")

    curr_amount = request.form.get('amount')
    if (not curr_amount or curr_amount == '0'):
        return render_template('log.html', message="Please enter a non-zero amount.")

    other = request.form.get('other_species')
    if(species == 'Other' and other != None and other != ""):
        species = request.form.get('other_species')
    elif (species != 'Other' and other != ''):
        return render_template('log.html', message="Please enter a valid species.")
        

    # print "Args:"
    # print area, "."
    # print area == 'empty'
    # print location, "."
    # print species, "."
    # print curr_amount, "."
    # print other, "."

    db, username, password, hostname, port = get_db_creds()

    create_table()

    cnx = ''
    try:
        cnx = mysql.connector.connect(user=username, password=password,
                                      host=hostname, port=port,
                                      database=db)
    except Exception as exp:
        print(exp)
        import MySQLdb
        cnx = MySQLdb.connect(unix_socket=hostname, user=username, passwd=password, db=db, port=port)

    cur = cnx.cursor()
    cur0 = cnx.cursor(buffered=True)
    sql = ("SELECT * FROM fishes WHERE species = '%s'" % (species) )
    cur0.execute(sql)
    if(cur0.rowcount > 0):
        sql = ("UPDATE fishes SET amount = amount + curr_amount WHERE location = '%s' AND species = '%s'" % (location, species))
    else:
        sql = ("INSERT INTO fishes (area, location, species, amount) VALUES (%s, %s, %s, %s)")
        val = (area, location, species, curr_amount)
    try:
        cur.execute(sql, val)
        cnx.commit()
        return render_template('log.html', message="Catch successfully logged!")
    except Exception as exp:
        return render_template('log.html', message="Catch could not be logged." + str(exp))

@app.route('/lookup')
def lookup():
    return render_template("lookup.html")

@app.route('/lookup_search', methods=['GET'])
def lookup_search():
    print("Received request.")

    area = request.args.get('area')
    location = request.args.get('location')

    db, username, password, hostname, port = get_db_creds()
    
    cnx = ''
    try:
        cnx = mysql.connector.connect(user=username, password=password,
                                      host=hostname, port=port,
                                      database=db)
    except Exception as exp:
        print(exp)
        import MySQLdb
        cnx = mysql.connector.connect(user=username, password=password,
                                      host=hostname, port=port,
                                      database=db)
    results = []
    cur = cnx.cursor() 
    sql = ("SELECT * FROM fishes WHERE area = '%s' AND location = '%s'" % (area, location))
    cur.execute(sql)
    for row in cur:
        species = str(row[2])
        amount = (row[3])
        pop = ""
        if(amount < 3):
            pop = "Population - POOR"
        elif(amount < 7):
            pop = "Population - FAIR"
        elif(amount < 11):
            pop = "Population - GOOD"
        else:
            pop = "Population - EXCELLENT"
        res = species + ": " + pop
        results.append(res)

    cnx.commit()
    if len(results) == 0:
        return render_template('lookup.html', message ="No fish in location")
    return render_template('lookup.html', results = results)

@app.route('/search')
def search():
    return render_template("search.html")

@app.route('/search_species', methods=['GET'])
def search_species():
    print("Received request.")

    area = request.args.get('area')
    species = request.args.get('species')

    db, username, password, hostname, port = get_db_creds()
    
    cnx = ''
    try:
        cnx = mysql.connector.connect(user=username, password=password,
                                      host=hostname, port=port,
                                      database=db)
    except Exception as exp:
        print(exp)
        import MySQLdb
        cnx = mysql.connector.connect(user=username, password=password,
                                      host=hostname, port=port,
                                      database=db)
    cur = cnx.cursor() 
    sql = ("SELECT * FROM fishes WHERE area = '%s' AND species = '%s'" % (area, species))
    cur.execute(sql)
    largest_amount = 0
    loc = ""
    for row in cur:
        amount = (row[3])
        if(amount > largest_amount):
            amount = largest_amount
            loc = row[1]

    cnx.commit()
    if (loc == ""):
        return render_template('search.html', message ="Species not in location")
    return render_template('search.html', results = loc)


if __name__ == "__main__":
    app.run(host = "0.0.0.0")
