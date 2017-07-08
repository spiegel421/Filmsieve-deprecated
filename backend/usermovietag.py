import mysql.connector
from mysql.connector import errorcode

DB_NAME = 'usermovietag'

TABLES = {}
TABLES['movie_tags'] = (
  "CREATE TABLE movie_tags( "
  "user int(10) NOT NULL, "
  "movie int(10) NOT NULL, "
  "tag varchar(100) NOT NULL ); ")

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

def update_tags(user, movie, tag):
  cnx = mysql.connector.connect(user='root', password='Reverie42', buffered=True)
  cursor = cnx.cursor()
  cnx.database = DB_NAME
  
  add_tag = ("INSERT INTO movie_tags "
             "(user, movie, tag) "
             "VALUES (%s, %s, %s); ")
  
  data = (user, movie, tag)
  if len(tag) > 100:
    return
  
  cursor.execute(add_tag, data)
  
  cnx.commit()
  cursor.close()
  cnx.close()
  
def read_into_dict():
  cnx = mysql.connector.connect(user='root', password='Reverie42', buffered=True)
  cursor = cnx.cursor()
  cnx.database = DB_NAME
  
  tag_dict = {}
  
  cursor.execute("SELECT * FROM movie_tags; ")
  for i in cursor:
    if i[1] in tag_dict:
      if i[2] in tag_dict[i[1]]:
        tag_dict[i[1]][i[2]] += 1
      else:
        tag_dict[i[1]][i[2]] = 1
    else:
      tag_dict[i[1]] = {}
      tag_dict[i[1]][i[2]] = 1
  
  cnx.commit()
  cursor.close()
  cnx.close()
  
  return tag_dict
