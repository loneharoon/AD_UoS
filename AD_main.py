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
#%% create training stats
"""" 1. get data
     2. divide it into 4 contexts 
     3. divide each into day wise
     4. calculate above stats """
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
test_stats = {}
for day,data in test_contexts_daywise.items():
  print("testing for day {}".format(day))
  temp = {}
  for context,con_data in data.items():
    temp[context] = create_testing_stats(con_data)
  test_stats[day] = temp
#%% AD logic starts now
# test_stats - contains stats computed on test day
#contexts_stats - contains stats computed from training data    
    result = []
for day,data in test_stats.items():
  for contxt,contxt_stats in data.items():
    print(contxt_stats)
    # be clear - word contexts_stats represents training data and word contxt represents test day stats
    train_results = contexts_stats[contxt] # all relevant train stats
    test_results  = contxt_stats
    temp_res = {}
    temp_res['timestamp'] = day
    temp_res['context'] = contxt
    temp_res['status'] = 0
    temp_res['anomtype'] = ' '
    if (test_results['ON_duration']['mean'] >=  train_results['ON_duration']['mean'] + 1.0* train_results['ON_duration']['std']) and (test_results['OFF_duration']['mean'] >=  train_results['OFF_duration']['mean'] + 1.0* train_results['OFF_duration']['std']):
       temp_res['status'] = 0
    elif test_results['ON_duration']['mean'] >=  train_results['ON_duration']['mean'] + 1.0* train_results['ON_duration']['std']:
       temp_res['status'] = 1
       temp_res['anomtype'] = "long"
    elif test_results['ON_cycles']['mean'] >=  train_results['ON_cycles']['mean'] + 1.0* train_results['ON_cycles']['std']:
       temp_res['status'] = 1
       temp_res['anomtype'] = "frequent"
    result.append(temp_res)
    
      
    
    
    
    
  
  