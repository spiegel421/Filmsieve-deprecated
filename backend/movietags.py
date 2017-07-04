import mysql.connector
from mysql.connector import errorcode

DB_NAME = 'movietags'

TABLES = {}
TABLES['user_movie_tag'] = (
  "CREATE TABLE movie_tags( "
  "user varchar(20) NOT NULL, "
  "movie varchar(100) NOT NULL, "
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

def update_movie_tags(user, movie, tag):
  cnx = mysql.connector.connect(user='root', password='Reverie42', buffered=True)
  cursor = cnx.cursor()
  cnx.database = DB_NAME
  
  check_exists = ("SELECT EXISTS(SELECT 1 FROM "
                  "movie_tags WHERE user = %s "
                  "AND movie = %s AND tag = %s); ")
  
  add_movie_tag = ("INSERT INTO movie_tags "
             "(user, movie, tag) "
             "VALUES (%s, %s, %s); ")
  
  data = (user, movie, tag)
  
  cursor.execute(check_exists, data)
  for item in cursor:
    exists = item[0]
  if exists == 0:
    cursor.execute(add_movie_tag, data)
  
  cnx.commit()
  cursor.close()
  cnx.close()
  
def read_movie_tags():
  cnx = mysql.connector.connect(user='root', password='Reverie42', buffered=True)
  cursor = cnx.cursor()
  cnx.database = DB_NAME
  
  movie_tag_dict = {}
  
  cursor.execute("SELECT * FROM movie_tags; ")
  for item in cursor:
    if item[1] in movie_tag_dict:
      if item[2] in movie_tag_dict[item[1]]:
        movie_tag_dict[item[1]][item[2]] += 1
      else:
        movie_tag_dict[item[1]][item[2]] = 1
    else:
      movie_tag_dict[item[1]] = {}
      movie_tag_dict[item[1]][item[2]] = 1
  
  cnx.commit()
  cursor.close()
  cnx.close()
  
  return movie_tag_dict
