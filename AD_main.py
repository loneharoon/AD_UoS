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
import standardize_column_names as scn
import AD_support as ads
import re
from __future__ import division
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
scn.rename_appliances(home,df_samp)
#%% select particular appliance for anomaly detection
df_samp.columns
myapp = "Chest_Freezer"
train_data =  df_samp[myapp]['2014-04-01' : '2014-04-30'] # home 3 freezer
#test_data =  df_samp[myapp]['2014-05-01':'2014-05-03'] # home 3
test_data =  df_samp[myapp]['2014-05-01':'2014-05-31'] # home 3
train_results = ads.AD_refit_training(train_data,data_sampling_type,data_sampling_time)
test_results  = ads.AD_refit_testing(test_data,data_sampling_type,data_sampling_time)            
#%% Anomaly detection logic
num_std = 2
alpha = 2.5
res_df = ads.anomaly_detection_algorithm(test_results,train_results,alpha,num_std)
result_sub = res_df[res_df.status==1]

#%%
# Compute different accuracies
#house_no = 1
house_no =  int(re.findall('\d+',home)[0])
appliance = scn.reverse_lookup(home,myapp) # find actual name of appliance in anomaly database
day_start = test_data.first_valid_index()
day_end = test_data.last_valid_index()
print('both S and NS anomalies selected')
gt,ob = ads.tidy_gt_and_ob(house_no,appliance,day_start,day_end,result_sub)
#confusion_matrix(gt.day.values,ob.day.values)
precision,recall, fscore = ads.compute_confusion_metrics(gt,ob)
print(precision,recall, fscore)  
    
#%%

#%% visualise specific data portion
dat = "2014-05-03"
test_data[dat].plot()