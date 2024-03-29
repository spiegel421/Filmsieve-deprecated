from usermovietag import *
from movietag import *
import os
from embed import perform_all

def read_tags(filename):
  reader = open(filename, mode='r')
  line = reader.readline()
  line = reader.readline()
  count = 0
  while line != '':
    datum = line.split(',')
    update_tags(datum[0], datum[1], datum[2])
    line = reader.readline()
    count += 1
    if count % 1000 == 0:
      print count
  reader.close()

if __name__ == "__main__":
  read_tags(os.path.expanduser('~/filmsieve/backend/ml-latest-small/tags.csv'))
  binary_table = perform_all(read_into_dict())
  read_binary_table(binary_table[0], binary_table[1])
