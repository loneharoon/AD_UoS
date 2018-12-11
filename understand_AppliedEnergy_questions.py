#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
In this file, I try to answer the queries raised by Applied Energy reviewers empirically. 
The question raised was, "I understand that you have adopted a rule based approach in order to provide a greater explanation power to your algorithm, but I would nevertheless like to see a generic measure such as the total energy consumed by an appliance over a typical day (obtained by some statistical measure) and the energy consumed during a faulty (anomalous) condition. Would this very simple indicator return the same output of UNUM?"

Approach: find the energy consumption of anomalous days in both normal,elongated and frequent anomaly case day wise.
Also, compute energy per cycle wise.

Note: For applied energy paper, I have done earlier experiments in nilmtk_pycharm folder, but this time I am doing it in the directory used for UOS project.

Created on Tue Dec 11 16:41:37 2018

@author: haroonr
"""
import standardize_column_names as scn
import AD_support as ads
import re
import numpy as np
import pandas as pd
#%%
#path2=  "/Volumes/DATA_DSK/Datasets_Macbook/Dataport/mix_homes/default/injected_anomalies/"

#%%
#dir = "/Volumes/DATA_DSK/Datasets_Macbook/REFITT/CLEAN_REFIT_081116/"
#dir = "/Volumes/DATA_DSK/Datasets_Macbook/Dataport/mix_homes/default/injected_anomalies/"
dir =  "/Volumes/DATA_DSK/Datasets_Macbook/Dataport/mix_homes/default/injected_anomalies/"
home = "3538.csv"
df = pd.read_csv(dir+home,index_col="localminute")
df.index = pd.to_datetime(df.index)
#df_sub = df["2014-03":] # since before march their are calibration issues
#%% Resampling data
train_dset = df_new.truncate(before="2014-06-01", after="2014-06-30 23:59:59")
test_dset = df_new.truncate(before="2014-07-01", after="2014-08-30 23:59:59")

print("*****RESAMPLING********")
df_samp = df_sub.resample('1T',label = 'right', closed ='right').mean()
data_sampling_time = 1 #in minutes
data_sampling_type = "minutes" # or seconds
scn.rename_appliances(home, df_samp)
#%% select particular appliance for anomaly detection
df_samp.columns
myapp = "Chest_Freezer"
train_data =  df_samp[myapp]['2014-04-01' : '2014-04-30'] # home 3 freezer
#test_data =  df_samp[myapp]['2014-05-01':'2014-05-03'] # home 3
test_data =  df_samp[myapp]['2014-05-01':'2014-05-31'] # home 3
train_results = ads.AD_refit_training(train_data,data_sampling_type,data_sampling_time)
test_results  = ads.AD_refit_testing(test_data,data_sampling_type,data_sampling_time)
