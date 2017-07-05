from usermovietag import *
from movietag import *
from embed import perform_all

def read_tags(filename):
  reader = open(filename, mode='r')
  line = reader.readline()
  line = reader.readline()
  while line != '':
    datum = line.split(',')
    update_tags(datum[0], datum[1], datum[2])
    line = reader.readline()
  reader.close()

if __name__ == "__main__":
  read_tags('ml-latest/tags.csv')
  binary_table = embed.perform_all(read_into_dict())
  read_binary_table(binary_table[0], binary_table[1])
