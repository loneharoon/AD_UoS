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
train_data= df_samp[myapp]['2014-03']
# divide data according to  4 contexts [defined by times]
night1_data = train_data.between_time("00:00","05:59")
day1_data = train_data.between_time("06:00","11:59")
day2_data = train_data.between_time("12:00","17:59")
night2_data = train_data.between_time("18:00","23:59")
# create groups within contexts day wise, this will allow us to catch stats at day level otherwise preserving boundaries between different days might become difficult
night1_gp = night1_data.groupby(night1_data.index.date)
day1_gp = day1_data.groupby(day1_data.index.date)
day2_gp = day2_data.groupby(day2_data.index.date)
night2_gp = night2_data.groupby(night2_data.index.date)
#%%
dic = {}
for k, v in night1_gp:
  print(k)
  samp = v.to_frame()
  # handle nans in data
  nan_obs = int(samp.isnull().sum())
  #rule: if more than 50% are nan then I drop that day from calculcations othewise I drop nan readings only
  if nan_obs:  
    if nan_obs >= 0.50*samp.shape[0]:
      print("More than 50percent obs missing hence drop day {} ".format(k))
      #continue
    elif nan_obs < 0.50*samp.shape[0]:
      print("dropping  {} nan observations for day {}".format(nan_obs,k))
      samp.dropna(inplace=True)
  samp.columns = ['power']
  samp_val =  samp.values
  samp_val = samp_val.reshape(-1,1)
  #FIXME: you can play with clustering options
  kobj = perform_clustering(samp_val,clusters=2)
  samp['cluster'] = kobj.labels_
  samp = re_organize_clusterlabels(samp)
  tempval = [(k,sum(1 for i in g)) for k,g in groupby(samp.cluster.values)]
  tempval = pd.DataFrame(tempval,columns=['cluster','samples'])
  off_cycles =list(tempval[tempval.cluster==0].samples)
  on_cycles =list(tempval[tempval.cluster==1].samples)
  temp_dic = {}
  temp_dic["on"] = on_cycles
  temp_dic["off"] = off_cycles
  cycle_stat = Counter(tempval.cluster)
  temp_dic.update(cycle_stat)
  dic[str(k)] = temp_dic
  #%% combine all OFF and ON states of different days into two lists
  ON_duration = []
  OFF_duration = []
  ON_cycles = []
  OFF_cycles = []
  for k,v in dic.items():
    ON_duration.append(v['on'])
    OFF_duration.append(v['off'])
    ON_cycles.append(v[1])
    OFF_cycles.append(v[0])
 ON_duration  =  [ item for sublist in ON_duration for item in sublist]
 OFF_duration = [ item for sublist in OFF_duration for item in sublist]
 #%%
summ_dic = {}
summ_dic['ON_duration'] = {'mean':round(np.mean(ON_duration),3), 'std':round(np.std(ON_duration),3)}
summ_dic['OFF_duration'] = {'mean':round(np.mean(OFF_duration),3), 'std':round(np.std(OFF_duration),3)}
summ_dic['ON_cycles'] = {'mean':round(np.mean(ON_cycles),0), 'std':round(np.std(ON_cycles),3)}
summ_dic['OFF_cycles'] = {'mean':round(np.mean(OFF_cycles),0), 'std':round(np.std(OFF_cycles),3)}
 