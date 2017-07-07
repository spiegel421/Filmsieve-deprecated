import numpy as np
import pandas as pd
import copy
from keras.layers import Input, Dense
from keras.models import Model
from sklearn import svm

def convert_to_matrix(tag_dict):
  return pd.DataFrame.from_dict(tag_dict, orient='index').fillna(0)
  print 'done'

def convert_to_ppmi(count_matrix):
  sum_tot = count_matrix.values.sum()
  print '1'
  sum_row = count_matrix.values.sum(axis=1)
  print '2'
  sum_col = count_matrix.values.sum(axis=0)
  print '3'
  
  count = 0
  for row in len(count_matrix.index):
    count += 1
    if count % 1000 == 0:
      print count
    for col in len(count_matrix.columns):
      entry = float(count_matrix.values[row][col])
      if entry == 0:
        count_matrix.values[row][col] = 0.0
      else:
        prob_con = entry / sum_tot
        if prob_con == 1.0:
          count_matrix.values[row][col] = 1.0
        else:
          prob_row = entry / sum_row[row]
          prob_col = entry / sum_col[tag]
          ppmi_value = 2 ** (np.log(prob_con / (prob_row * prob_col)) + np.log(prob_con))
          count_matrix.values[row][col] = ppmi_value
          
  return count_matrix

def autoencode(ppmi_matrix):
  original_dim = len(ppmi_matrix.values[0])
  encoding_dim = 20
  
  input = Input(shape=(original_dim,))
  encoded = Dense(encoding_dim, activation='sigmoid')(input)
  decoded = Dense(original_dim, activation='sigmoid')(encoded)
  
  autoencoder = Model(input, decoded)
  encoder = Model(input, encoded)
  encoded_input = Input(shape=(encoding_dim,))
  decoder_layer = autoencoder.layers[-1]
  decoder = Model(encoded_input, decoder_layer(encoded_input))
  
  X = ppmi_matrix.values
  autoencoder.compile(optimizer='sgd', loss='mean_squared_error')
  autoencoder.fit(X, X, validation_split=0.2, 
                  epochs=50, batch_size=10)
  
  encoded_space = pd.DataFrame(encoder.predict(ppmi_matrix.values), index=ppmi_matrix.index)
  return encoded_space

def find_distance_matrix(count_matrix, encoded_space):
  distance_matrix = copy.copy(count_matrix).T
  
  clf = svm.LinearSVC()
  for tag in distance_matrix.index:
    y = copy.copy(distance_matrix.loc[tag])
    y = [1 if i > 0 else 0 for i in y.values]
    clf.fit(encoded_space.values, y)
    distance_matrix.loc[tag] = clf.decision_function(encoded_space.values)
    
  return distance_matrix

def rank_distance_matrix(distance_matrix):
  sorted_by_distance = {}
  for tag in distance_matrix.index:
    sorted_by_distance[tag] = sorted(distance_matrix.columns, 
                                     key=lambda item: distance_matrix.loc[tag][item], 
                                     reverse=True)
    
  ranked_matrix = copy.copy(distance_matrix)
  for tag in distance_matrix.index:
    ranked_matrix.loc[tag] = [sorted_by_distance[tag].index(item) + 1 for item in distance_matrix.columns]
    
  return ranked_matrix

def find_ndcg_values(ppmi_matrix, ranked_matrix):
  ndcg_values = {}
  rankings_dict = ranked_matrix.to_dict(orient='index')
  for tag in ranked_matrix.index:
    dcg = 0.0
    item_rankings = rankings_dict[tag]
    for item in item_rankings:
      dcg += ppmi_matrix.loc[item][tag] / (np.log(item_rankings[item] + 1) / np.log(2))
      
    idcg = 0.0
    sorted_relevancies = sorted(ppmi_matrix.T.loc[tag], reverse=True)
    for i in range(len(sorted_relevancies)):
      idcg += sorted_relevancies[i] / (np.log(i + 2) / np.log(2))
      
    ndcg_values[tag] = dcg / idcg
    
  return ndcg_values

def find_binary_table(ranked_matrix, percentile, ndcg_values, cutoff_ndcg):
  interpretable_tags = []
  for tag in ndcg_values:
    if ndcg_values[tag] >= cutoff_ndcg:
      interpretable_tags.append(tag)
  
  binary_table = []
  num_items = len(ranked_matrix.iloc[0])
  cutoff_rank = (1 - percentile) * num_items
  rankings_dict = ranked_matrix.to_dict(orient='index')
  for tag in interpretable_tags:
    item_rankings = rankings_dict[tag]
    for item in item_rankings:
      if item_rankings[item] <= cutoff_rank:
        i = (item, tag)
        binary_table.append(i)
        
  return [interpretable_tags, binary_table]

def perform_all(tag_dict):
  count_matrix = convert_to_matrix(tag_dict)
  ppmi_matrix = convert_to_ppmi(count_matrix)
  encoded_space = autoencode(ppmi_matrix)
  distance_matrix = find_distance_matrix(count_matrix, encoded_space)
  ranked_matrix = rank_distance_matrix(distance_matrix)
  ndcg_values = find_ndcg_values(ppmi_matrix, ranked_matrix)
  binary_table = find_binary_table(ranked_matrix, 0.90, ndcg_values, 0.30)
  return binary_table
