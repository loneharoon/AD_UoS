#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The initial copy of this code has been taken from https://github.com/guptasoumya/Energy-Disaggregation.
It uses KNN for disaggregation
Created on Thu Dec 14 10:29:39 2017

@author: haroonr
"""
#%%
import numpy as np
import scipy as sp
import sklearn as skit
import pandas as pd
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor
import copy
#%%
ddir = "/Volumes/MacintoshHD2/Users/haroonr/Downloads/House 1-6 data in csv/"
home = 'House{}.csv'.format(1)
df = pd.read_csv(ddir+home)
data = copy.copy(df)
#%%
data = shuffle(data)
x = data.iloc[:,1:3]
y = data.iloc[:,3:]
column_name = []
train_accuarcy = []
test_accuracy = []

for column in y:
  y1 = y[column]
  x_train,x_test,y_train,y_test = train_test_split(x,y1,test_size=0.2,random_state=100)
  print ('samples in training data:',len(x_train))
  print ('samples in testin data:',len(x_test))
  knn = KNeighborsRegressor(n_neighbors=20)
  knn.fit(x_train,y_train)
  train_acc = round(knn.score(x_train,y_train)*100,2)
  test_acc =  round(knn.score(y_train,y_test)*100,2)
  column_name.append(column)
  train_accuracy.append(train_accu)
  test_accuracy.append(test_accu)

acc= pd.DataFrame(list(zip(column_name,train_accuracy,test_accuracy)),columns=['Appliance','train_accuracy','])
  