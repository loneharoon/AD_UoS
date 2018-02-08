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
import standardize_column_names
import AD_support as ads
#%%
dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/CLEAN_REFIT_081116/"
home = "House10.csv"
df = pd.read_csv(dir+home,index_col="Time")
df.index = pd.to_datetime(df.index)
df_sub = df["2014-03":] # since before march their are calibration issues
#%% Resampling data
print("*****RESAMPLING********")
df_samp = df_sub.resample('1T',label='right',closed='right').mean()
data_sampling_time = 1 #in minutes
data_sampling_type = "minutes" # or seconds
standardize_column_names.rename_appliances(home,df_samp)
#%% select particular appliance for anomaly detection
df_samp.columns
myapp = "Fridge_Freezer"
train_data =  df_samp[myapp]['2014-04-01' : '2014-04-30'] # home 3 freezer
test_data =  df_samp[myapp]['2014-05-01':'2014-05-03'] # home 3
train_results = ads.AD_refit_training(train_data,data_sampling_type,data_sampling_time)
test_results  = ads.AD_refit_testing(test_data,data_sampling_type,data_sampling_time)      
  
  
  
  #print("training stats of context {} is done".format(k))


      
#%% Anomaly detection logic
num_std = 2
alpha = 2.5
res_df = ads.anomaly_detection_algorithm(test_results,train_results,alpha,num_std)
 
#%%
# Compute different accuracies
house_no = 1
appliance = "Freezer_1"
gt = read_REFIT_groundtruth()
select_house = gt.House_No==house_no
select_appliance = gt.Appliance==appliance
gt_sub = gt[select_house & select_appliance]
gt_sub
#%%
x= p.timestamp
y= gt_sub['start_time'][0]
z= gt_sub['end_time'][0]
if (x >= y).values[0] & (x <= z).values[0]:
#%% visualise specific data portion
dat = "2014-05-03"
test_data[dat].plot()