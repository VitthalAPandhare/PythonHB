from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
import sqlite3
import os.path
import datetime

VAR_DB_NAME = "servers.db"
VAR_TABLE_COLLECTION_NAME = "server100"
VAR_COLUMN_NAME = "webAddress"
VAR_TABLE_PASSED_NAME = "passed"
VAR_COLUMN_DATE = "dateColumn"


def generate_table(webSite="http://register.start.bg", myImportedList=[]):
    Create_Tables(webSite)

    connection = sqlite3.connect(VAR_DB_NAME)
    cursor = connection.cursor()

    myHeaders = {}
    ua1 = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
    myHeaders["User-Agent"] = ua1

    r = requests.get(webSite, headers=myHeaders)

    mySoup = BeautifulSoup(r.text)
    myList = []
    myImprovedList = []

    for link in mySoup.find_all('a'):
        if (link.get('href') is not None
                and len(link.get('href')) > 8  # I love magic!
                and link.get('href')[:1] != "/"
                and "javascript" not in link.get('href')):

            myList.append(link.get('href'))

    for line in myList:
        ok = True
        if (line[:12] == "link.php?id="):
            line = webSite + "/" + line
        try:
            r = requests.head(line, headers=myHeaders, timeout=3)

            if (r.status_code != 200):
                line = r.headers["location"]

            line = urlparse(line)
            line = line.netloc

        except Exception:
            ok = False

        # Magic makes me feel good!
        if line not in myImprovedList and len(line) > 6 and ok and line not in myImportedList:
            myImprovedList.append(line)

    for line in myImprovedList:
        ok = True
        try:

            if (line[:4] != "http"):
                line = "http://" + line

            print("Writing {}".format(line))

            r = requests.head(line, headers=myHeaders, timeout=3)

            headers1 = str(r.headers)

            serverType = r.headers["server"]

            if (r.status_code == 200):
                serverSite = line
            else:
                serverSite = r.headers["location"]

        except Exception:
            ok = False

        if ok:
            sqlText = """INSERT INTO ? (webAddress,serverType,headers, accessedFrom)
                     VALUES (?, ?,?,?,?);"""
            cursor.execute(
                sqlText, (VAR_TABLE_COLLECTION_NAME, serverSite, serverType, headers1, webSite))
            connection.commit()

    cursor.close()
    connection.close()


def Create_Tables(website):
    nowIsTime = datetime.datetime.now()

    connection = sqlite3.connect(VAR_DB_NAME)
    cursor = connection.cursor()

    create_users_table = """CREATE TABLE IF NOT EXISTS
                        {} (id INTEGER PRIMARY KEY, {} TEXT, serverType TEXT, headers TEXT, accessedFrom TEXT);
                        """.format(VAR_TABLE_COLLECTION_NAME, VAR_COLUMN_NAME)

    create_visited_table = """CREATE TABLE IF NOT EXISTS
                        {} (id INTEGER PRIMARY KEY, {} TEXT, {} DATE);
                        """.format(VAR_TABLE_PASSED_NAME, VAR_COLUMN_NAME, VAR_COLUMN_DATE)

    add_website = """INSERT INTO {} ({},{}) VALUES ({},{});""".format(
        VAR_TABLE_PASSED_NAME, VAR_COLUMN_NAME, website, VAR_COLUMN_DATE, nowIsTime)

    print(add_website)
    cursor.execute(create_users_table)
    cursor.execute(create_visited_table)
    cursor.execute(add_website)

    connection.commit()

    cursor.close()
    connection.close()


def Read_Table(db_name, table_name, column_name):

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, db_name)
    connection = sqlite3.connect(db_path)
    myList = []
    cursor = connection.cursor()
    sql = """SELECT {} FROM {};"""
    cursor.execute(sql.format(column_name, table_name))

    for row in cursor:
        myList.append(row[0])

    return myList


def Delete_Tables():
    connection = sqlite3.connect("servers.db")
    cursor = connection.cursor()

    delete_server100 = """DELETE FROM server100;"""
    delete_passed = """DELETE FROM passed;"""

    cursor.execute(delete_server100)
    cursor.execute(delete_passed)

    connection.commit()


def Lets_Crawl():

    myReadList = Read_Table(
        VAR_DB_NAME, VAR_TABLE_COLLECTION_NAME, VAR_COLUMN_NAME)

    myCrawledList = Read_Table(
        VAR_DB_NAME, VAR_TABLE_PASSED_NAME, VAR_COLUMN_NAME)

    siteToCrawl = myReadList.pop(0)
    while siteToCrawl in myCrawledList:
        siteToCrawl = myReadList.pop(0)

    generate_table(siteToCrawl, myReadList)

    print("End of crawling.")


def Start(times):

    generate_table()
    for x in range(1, times):
        Lets_Crawl()
        x += 1

Start(10)
