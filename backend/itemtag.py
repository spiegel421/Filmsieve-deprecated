import mysql.connector
from mysql.connector import errorcode

DB_NAME = 'itemtag'

TABLES = {}
TABLES['item_tags'] = (
  "CREATE TABLE item_tags( "
  "item varchar(100) NOT NULL, "
  "tag varchar(20) NOT NULL ); ")

TABLES['tags'] = (
  "CREATE TABLE tags( "
  "tag varchar(20) NOT NULL ); ")

cnx = mysql.connector.connect(user='root', password='Reverie42')
cursor = cnx.cursor()

def create_database(cursor):
  try:
    cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
  except mysql.connector.Error as err:
     print "Failed creating database: {}".format(err)
     exit(1)

try:
    cnx.database = DB_NAME  
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        create_database(cursor)
        cnx.database = DB_NAME
    else:
        print err
        exit(1)

for name, ddl in TABLES.iteritems():
    try:
        print "Creating table {}: ".format(name)
        cursor.execute(ddl)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print "already exists."
        else:
            print err.msg
    else:
        print "OK"

cnx.commit()
cursor.close()
cnx.close()

def read_binary_table(interpretable_tags, binary_table):
  cnx = mysql.connector.connect(user='root', password='Reverie42', buffered=True)
  cursor = cnx.cursor()
  cnx.database = DB_NAME
  
  for tag in interpretable_tags:
    add_tag = ("INSERT INTO tags "
              "(tag) "
              "VALUES (%s); ")
    
    data = (tag)
    
    cursor.execute(add_tag, data)
  
  for i in binary_table:
    item = i[0]
    tag = i[1]
    add_item_tag = ("INSERT INTO item_tags "
             "(item, tag) "
             "VALUES (%s, %s); ")
  
    data = (item, tag)
  
    cursor.execute(add_item_tag, data)
  
  cnx.commit()
  cursor.close()
  cnx.close()
