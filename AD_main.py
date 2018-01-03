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
samp_val =  samp.values
samp_val = samp_val.reshape(-1,1)
kobj = perform_clustering(samp_val,clusters=2)
#FIXME:
samp['cluster'] = kobj.labels_
#%% obtain cycle stats

temp1 = [(k,sum(1 for i in g)) for k,g in groupby(kobj.labels_)]
temp1 = pd.DataFrame(temp1,columns=['cluster','cluster_length'])
temp1['duration'] = temp1['cluster_length'] * data_sampling_time