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
from datetime import datetime,timedelta
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
data_sampling_type = "minutes" # or seconds
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
#train_data =  df_samp[myapp]['2014-03-07']
train_data =  df_samp[myapp]['2014-03']
# divide data according to  4 contexts [defined by times]
contexts = OrderedDict()
contexts['night_1_gp'] = train_data.between_time("00:00","05:59")
contexts['day_1_gp'] = train_data.between_time("06:00","11:59")
contexts['day_2_gp'] = train_data.between_time("12:00","17:59")
contexts['night_2_gp'] = train_data.between_time("18:00","23:59")
#%
# create groups within contexts day wise, this will allow us to catch stats at day level otherwise preserving boundaries between different days might become difficult
contexts_daywise = OrderedDict()
for k,v in contexts.items():
  contexts_daywise[k] = v.groupby(v.index.date)
 #% Compute stats context wise
contexts_stats = OrderedDict()
#%%
print
for k,v in contexts_daywise.items():
  print("CONTEXT IS {}".format(k))
  contexts_stats[k] = create_training_stats(v,sampling_type=data_sampling_type,sampling_rate=data_sampling_time) 
  
  #print("training stats of context {} is done".format(k))
#%% TESTING STAGE STARTS
#prepare test data
test_data =  df_samp[myapp]['2014-04-08':'2014-08-30']
#test_data =  df_samp[myapp]['2014-08-01']
test_data_daywise = test_data.groupby(test_data.index.date) # daywise grouping
test_contexts_daywise = OrderedDict()
for k,v in test_data_daywise:     # context wise division
  #print(str(k))
  test_contexts= OrderedDict()
  test_contexts['night_1_gp'] = v.between_time("00:00","05:59")
  test_contexts['day_1_gp']   = v.between_time("06:00","11:59")
  test_contexts['day_2_gp']   = v.between_time("12:00","17:59")
  test_contexts['night_2_gp'] = v.between_time("18:00","23:59")
  test_contexts_daywise[str(k)] = test_contexts
#%
test_stats = OrderedDict()
for day,data in test_contexts_daywise.items():
  print("testing for day {}".format(day))
  temp = OrderedDict()
  for context,con_data in data.items():
    #temp[context] = create_testing_stats(con_data,context)
    res = create_testing_stats_with_boxplot(con_data,context,sampling_type=data_sampling_type,sampling_rate=data_sampling_time)
    if res!= False:
      temp[context] = res
    else:
      continue   
  test_stats[day] = temp

      
#%% Anomaly detection logic
num_std = 2.5
dummy_no = 2.5
LOG_FILENAME = '/Volumes/MacintoshHD2/Users/haroonr/Downloads/REFIT_log/logfile_REFIT.csv'
with ope(LOG_FILENAME,'a') as mylogger:

  mylogger.write("\n*****NEW ITERATION at time {}*************\n".format(datetime.now()))
  result = [] 
  for day,data in test_stats.items():
    for contxt,contxt_stats in data.items():
      #be clear - word contexts_stats represents training data and word contxt represents test day stats
      train_results = contexts_stats[contxt] # all relevant train stats
      test_results  = contxt_stats
      temp_res = {}
      temp_res['timestamp'] = datetime.strptime(day,'%Y-%m-%d')
      temp_res['context']   = contxt
      temp_res['status']    = 0
      temp_res['anomtype']  = np.float("Nan")
      # rule 3 of unum
#      if np.mean(test_results['ON_energy'] >  train_results['ON_energy']['mean'] + num_std* train_results['ON_energy']['std']) and (np.mean(test_results['OFF_energy']) >  train_results['OFF_energy']['mean'] + num_std* train_results['OFF_energy']['std']):
#        temp_res['status'] = 0
#        mylogger.write(day + ":" + contxt + "is not elongated anomaly as off time was also longer \n")
#      # rule 1 of unum
      if np.mean(test_results['ON_energy']) > dummy_no * train_results['ON_energy']['mean'] + num_std* train_results['ON_energy']['std']:
        temp_res['status'] = 1
        temp_res['anomtype'] = "long"
        mylogger.write(day + ":"+ contxt + ", elongated anomaly" + ", train_stats duration, " + str(train_results['ON_energy']['mean']) + ":"+str(train_results['ON_energy']['std']) + "; test_stats energy, " + str(np.mean(test_results['ON_energy'])) + "\n" )
            # rule 2 of unum
      elif np.mean(test_results['ON_cycles']) >  dummy_no * train_results['ON_cycles']['mean'] + num_std* train_results['ON_cycles']['std']:
        temp_res['status'] = 1
        temp_res['anomtype'] = "frequent"
        mylogger.write(day + ":"+contxt +  ", frequent anomaly" + ", train_stats frequency, " + str(train_results['ON_cycles']['mean']) + ":"+str(train_results['ON_cycles']['std']) + "; test_stats frequency, " + str(np.mean(test_results['ON_cycles'])) + "\n"  )
      result.append(temp_res)
res_df = pd.DataFrame.from_dict(result)
res_df = res_df.sort_values('timestamp')
res_df[res_df.status==1].shape[0]
res_df[res_df.status==1]
p = res_df[res_df.status==1]
#%% rectify timestamps by including appropriate context information
updated_timestamp = []
for i in range(0,res_df['context'].shape[0]):
  context = res_df['context'][i]
  timestamp = res_df['timestamp'][i]
  if context == 'night_1_gp':
    timestamp =  timestamp + timedelta(hours=3)
  elif context == 'day_1_gp':
    timestamp =  timestamp + timedelta(hours=9)
  elif context == 'day_2_gp':
    timestamp =  timestamp + timedelta(hours=15)
  elif context == 'night_2_gp':
    timestamp =  timestamp + timedelta(hours=21)
  updated_timestamp.append(timestamp)
res_df['updated_timestamp'] =  updated_timestamp   

#%%
# Compute different accuracies
house_no = 1
appliance = "Freezer_1"
gt = read_REFIT_groundtruth()
select_house = gt.House_No==house_no
select_appliance = gt.Appliance==appliance
gt_sub = gt[select_house & select_appliance]
#%%
x= p.timestamp
y= gt_sub['start_time'][0]
z= gt_sub['end_time'][0]
if (x >= y).values[0] & (x <= z).values[0]: