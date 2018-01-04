#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This scritp contains the AD logic for refit HOMES
Created on Tue Jan  2 08:53:47 2018

@author: haroonr
"""

#%%
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import numpy as np
from itertools import groupby
from collections import OrderedDict,Counter
from AD_support import *
#%%
dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/CLEAN_REFIT_081116/"
home = "House1.csv"
df = pd.read_csv(dir+home,index_col="Time")
df.index = pd.to_datetime(df.index)
df_sub = df["2014-03":] # since before march their are calibration issues
#%% Resampling data
print("*****RESAMPLING********")
df_samp = df_sub.resample('1T',label='right',closed='right').mean()
data_sampling_time = 1 #in minutes
#%% select particular appliance for anomaly detection
df_samp.columns
myapp = "Freezer_1"
app_data = df_samp[myapp]
print(app_data.head(1))
print(app_data.tail(1))
#%%perform clustering
samp = app_data['2014-03-07'].to_frame()
samp.columns = ['power']
samp_val =  samp.values
samp_val = samp_val.reshape(-1,1)
#FIXME: you can play with clustering options
kobj = perform_clustering(samp_val,clusters=2)
samp['cluster'] = kobj.labels_
samp = re_organize_clusterlabels(samp)
   
#%% perfom stats on cycles
temp1 = [(k,sum(1 for i in g)) for k,g in groupby(samp.cluster.values)]
temp1 = pd.DataFrame(temp1,columns=['cluster','samples'])
#temp1['duration'] = temp1['cluster_length'] * data_sampling_time
off_cycles =list(temp1[temp1.cluster==0].samples)
on_cycles =list(temp1[temp1.cluster==1].samples)
#%% create training stats
"""" 1. get data
     2. divide it into 4 contexts 
     3. divide each into day wise
     4. calculate above stats """"
myapp = "Freezer_1"
# set training data duration
train_data =  df_samp[myapp]['2014-03']
# divide data according to  4 contexts [defined by times]
contexts = {}
contexts['night_1_gp'] = train_data.between_time("00:00","05:59")
contexts['day_1_gp'] = train_data.between_time("06:00","11:59")
contexts['day_2_gp'] = train_data.between_time("12:00","17:59")
contexts['night_2_gp'] = train_data.between_time("18:00","23:59")
#%%
# create groups within contexts day wise, this will allow us to catch stats at day level otherwise preserving boundaries between different days might become difficult
contexts_daywise = {}
for k,v in contexts.items():
  contexts_daywise[k] = v.groupby(v.index.date)
 #%% Compute stats context wise
contexts_stats = {}
for k,v in contexts_daywise.items():
  contexts_stats[k] = create_training_stats(v)
  print("trainins stats of context {} is done".format(k))
#%% TESTING STAGE STARTS
#prepare test data
test_data =  df_samp[myapp]['2014-04-01']
test_data_daywise = test_data.groupby(test_data.index.date) # daywise grouping
test_contexts_daywise = {} 
for k,v in test_data_daywise:     # context wise division
  #print(str(k))
  test_contexts= {}
  test_contexts['night_1_gp'] = v.between_time("00:00","05:59")
  test_contexts['day_1_gp']   = v.between_time("06:00","11:59")
  test_contexts['day_2_gp']   = v.between_time("12:00","17:59")
  test_contexts['night_2_gp'] = v.between_time("18:00","23:59")
  test_contexts_daywise[str(k)] = test_contexts
#%%
res_dic = {}
for day,data in test_contexts_daywise.items():
  print("testing for day {}".format(day))
  temp = {}
  for context,con_data in data.items():
    temp[context] = create_testing_stats(con_data)
  res_dic[day] = temp
    
    
 #test_result_contextscreate_testing_stats(contexts_stats)
  