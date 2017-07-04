import mysql.connector
from mysql.connector import errorcode

DB_NAME = 'rankings'

TABLES = {}
TABLES['movie_tag_ranking'] = (
  "CREATE TABLE movie_tags( "
  "movie varchar(20) NOT NULL, "
  "tag varchar(100) NOT NULL, "
  "ranking varchar(20) NOT NULL ); ")

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

def read_rankings(ranked_matrix):
  cnx = mysql.connector.connect(user='root', password='Reverie42', buffered=True)
  cursor = cnx.cursor()
  cnx.database = DB_NAME
  
  add_ranking = ("INSERT INTO movie_tag_ranking "
             "(movie, tag, ranking) "
             "VALUES (%s, %s, %s); ")
  
  ranking_dict = ranked_matrix.to_dict(orient='dict')
  for movie in ranking_dict:
    for tag in ranking_dict[movie]:
      ranking = ranking_dict[movie][tag]
      data = (movie, tag, ranking)
      cursor.execute(add_ranking, data)
      
  cnx.commit()
  cursor.close()
  cnx.close()
