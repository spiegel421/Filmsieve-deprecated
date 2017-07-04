from movietags import *

def read_movietags(filename):
  reader = open(filename, mode='r')
  line = reader.readline()
  while line != '':
    datum = line.split(',')
    update_movie_tags(datum[0], datum[1], datum[2])
    line = reader.readline()
  reader.close()
