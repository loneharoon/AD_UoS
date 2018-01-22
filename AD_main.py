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
from datetime import datetime
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
train_data =  df_samp[myapp]['2014-03-07']
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
#test_data =  df_samp[myapp]['2014-04-08':'2014-08-30']
test_data =  df_samp[myapp]['2014-08-01']
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

LOG_FILENAME = '/Volumes/MacintoshHD2/Users/haroonr/Downloads/REFIT_log/logfile_REFIT.csv'
with open(LOG_FILENAME,'a') as mylogger:

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
      temp_res['anomtype']  = ' '
      # sum(np.logical_or(x < low,x>up))
      #duratation logic
      lower_ON_duration_outlier  = sum( test_results['ON_duration'] < train_results['ON_duration']['lowerwisker'] )
      higher_ON_duration_outlier = sum(test_results['ON_duration'] > train_results['ON_duration']['upperwisker']  )
      ON_duration_outlier = lower_ON_duration_outlier + higher_ON_duration_outlier
        
      lower_OFF_duration_outlier = sum(test_results['OFF_duration'] < train_results['OFF_duration']['lowerwisker'] )
      higher_OFF_duration_outlier = sum(test_results['OFF_duration'] > train_results['OFF_duration']['upperwisker'] )
      OFF_duration_outlier = lower_OFF_duration_outlier + higher_OFF_duration_outlier
      #energy logic
      lower_ON_energy_outlier  = sum( test_results['ON_energy'] < train_results['ON_energy']['lowerwisker'] )
      higher_ON_energy_outlier = sum(test_results['ON_energy'] > train_results['ON_energy']['upperwisker']  )
      ON_energy_outlier = lower_ON_energy_outlier + higher_ON_energy_outlier
        
      lower_OFF_energy_outlier = sum(test_results['OFF_energy'] < train_results['OFF_energy']['lowerwisker'] )
      higher_OFF_energy_outlier = sum(test_results['OFF_energy'] > train_results['OFF_energy']['upperwisker'] )
      OFF_energy_outlier = lower_OFF_energy_outlier + higher_OFF_energy_outlier
      #cycles logic
      lower_ON_cycles  =   test_results['ON_cycles'] < train_results['ON_cycles']['lowerwisker'] 
      higher_ON_cycles =   test_results['ON_cycles'] > train_results['ON_cycles']['upperwisker']  
      #ON_cycles_outlier = lower_ON_cycles + higher_ON_cycles
      #lower ON cycles will include OFF cases
      ON_cycles_outlier =  higher_ON_cycles
      
      lower_OFF_cycles  =   test_results['OFF_cycles'] < train_results['OFF_cycles']['lowerwisker']  
      higher_OFF_cycles =   test_results['OFF_cycles'] > train_results['OFF_cycles']['upperwisker'] 
      OFF_cycles_outlier = lower_OFF_cycles + higher_OFF_cycles
          #logging on duration basis
      if lower_ON_duration_outlier:
        mylogger.write(day+":"+contxt+":"+" lower_ON_duration_outlier_count: "+ str(lower_ON_duration_outlier)+ " lower_wisker: "+ str(train_results['ON_duration']['lowerwisker']) + ", test_Case : " + str(test_results['ON_duration'])+"\n")
      if higher_ON_duration_outlier:
        mylogger.write(day+":"+contxt+":"+" higher_ON_duration_outlier_count: "+ str(higher_ON_duration_outlier)+ " upper_wisker: "+ str(train_results['ON_duration']['upperwisker']) + ", test_Case : " + str(test_results['ON_duration'])+"\n")
      if lower_OFF_duration_outlier:
        mylogger.write(day+":"+contxt+":"+" lower_OFF_duration_outlier_count: "+ str(lower_OFF_duration_outlier)+ " lower_wisker: "+ str(train_results['OFF_duration']['lowerwisker']) + ", test_Case : " + str(test_results['OFF_duration'])+"\n")
      if higher_OFF_duration_outlier:
        mylogger.write(day+":"+contxt+":"+" higher_OFF_duration_outlier_count: "+ str(higher_OFF_duration_outlier)+ " upper_wisker: "+ str(train_results['OFF_duration']['upperwisker']) + ", test_Case : " + str(test_results['OFF_duration'])+"\n")
  
          #logging on energy basis
      if lower_ON_energy_outlier:
        mylogger.write(day+":"+contxt+":"+" lower_ON_energy_outlier_count: "+ str(lower_ON_energy_outlier)+ " lower_wisker: "+ str(train_results['ON_energy']['lowerwisker']) + ", test_Case : " + str(test_results['ON_energy'])+"\n")
      if higher_ON_energy_outlier:
        mylogger.write(day+":"+contxt+":"+" higher_ON_energy_outlier_count: "+ str(higher_ON_energy_outlier)+ " upper_wisker: "+ str(train_results['ON_energy']['upperwisker']) + ", test_Case : " + str(test_results['ON_energy'])+"\n")
      if lower_OFF_energy_outlier:
        mylogger.write(day+":"+contxt+":"+" lower_OFF_energy_outlier_count: "+ str(lower_OFF_energy_outlier)+ " lower_wisker: "+ str(train_results['OFF_energy']['lowerwisker']) + ", test_Case : " + str(test_results['OFF_energy'])+"\n")
      if higher_OFF_energy_outlier:
        mylogger.write(day+":"+contxt+":"+" higher_OFF_energy_outlier_count: "+ str(higher_OFF_energy_outlier)+ " upper_wisker: "+ str(train_results['OFF_energy']['upperwisker']) + ", test_Case : " + str(test_results['OFF_duration'])+"\n")
  
#      if lower_ON_cycles:
#        mylogger.write(day+":"+contxt+":"+" lower_ON_cycles_count: "+ str(lower_ON_cycles)+ " lower_wisker: "+ str(train_results['ON_cycles']['lowerwisker']) + ", test_Case : " + str(test_results['ON_cycles'])+"\n")
      if higher_ON_cycles:
        mylogger.write(day+":"+contxt+":"+" higher_ON_cyclesr_count: "+ str(higher_ON_cycles)+ " upper_wisker: "+ str(train_results['ON_cycles']['upperwisker']) + ", test_Case : " + str(test_results['ON_cycles'])+"\n")
#      if lower_OFF_cycles:
#        mylogger.write(day+":"+contxt+":"+" lower_OFF_cycles_count: "+ str(lower_OFF_cycles)+ " lower_wisker: "+ str(train_results['OFF_cycles']['lowerwisker']) + ", test_Case : " + str(test_results['OFF_cycles'])+"\n")
#      if higher_OFF_cycles:
#        mylogger.write(day+":"+contxt+":"+" higher_OFF_cycles_count: "+ str(higher_OFF_cycles)+ " upper_wisker: "+ str(train_results['OFF_cycles']['upperwisker']) + ", test_Case : " + str(test_results['OFF_cycles'])+"\n")  
      
      if ON_duration_outlier and OFF_duration_outlier:
        temp_res['status'] = 0
        print ("non anomalous on {} with context {}".format(day,contxt))
      elif ON_duration_outlier:
        temp_res['status'] = 1
        temp_res['anomtype'] = 'elongated_duration'
        print ("Elongated duration anomaly on {} with context {}".format(day,contxt))
      elif ON_cycles_outlier:
        temp_res['status'] = 1
        temp_res['anomtype'] = 'frequent'
        print ("Frequent anomaly on {} with context {}".format(day,contxt))
      result.append(temp_res)
      # energy logic starts now
      if ON_energy_outlier:
        temp_res['status'] = 1
        temp_res['anomtype'] = 'elongated_energy'
        print ("Elongated energy anomaly on {} with context {}".format(day,contxt))
        result.append(temp_res)
res_df = pd.DataFrame.from_dict(result)
res_df = res_df.sort_values('timestamp')
res_df[res_df.status==1].shape[0]      
res_df[res_df.status==1]    
    
#%%

#sum(test_stats['2014-04-01']['day_1_gp']['ON_cycles'] < contexts_stats['day_1_gp']['ON_cycles']['lowerwisker'])
