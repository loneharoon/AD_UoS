#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is the main file frow where entire project starts. It will do disagg an AD too
Created on Wed Feb  7 09:00:08 2018

@author: haroonr
"""

import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import sys
sys.path.append('/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/disaggregation_codes/')
import accuracy_metrics_disagg as acmat
import localize_fhmm,co
import matplotlib.pyplot as plt
#from standardize_column_names import rename_appliances
#%%
dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/CLEAN_REFIT_081116/"
home = "House10.csv"
df = pd.read_csv(dir+home,index_col="Time")
df.index = pd.to_datetime(df.index)
#df_sub = df["2014-03-01":'2014-04-30']
df_sub = df["2014-04-01":] # since before march their are calibration issues
#%% Resampling data
print("*****RESAMPLING********")
df_samp = df_sub.resample('1T',label='right',closed='right').mean()
data_sampling_time = 1 #in minutes
data_sampling_type = "minutes" # or seconds
df_samp.drop('Issues',axis=1,inplace=True)
rename_appliances(home,df_samp) # this renames columns
#df_samp.rename(columns={'Aggregate':'use'},inplace=True) # renaming agg column
#%%
energy = df_samp.sum(axis=0)
high_energy_apps = energy.nlargest(7).keys() # CONTROL : selects few appliances
df_selected = df_samp[high_energy_apps]
#%%
train_dset = df_selected['2014-04-01':'2014-04-30']
train_dset.dropna(inplace=True)
#test_dset = df_samp['2014-04-01':'2014-04-04']
test_dset = df_selected['2014-04-01']
#test_dset.dropna(inplace=True)
#%%
fhmm_result  =  localize_fhmm.fhmm_decoding(train_dset,test_dset) # dissagreation
#co_result = co.co_decoding(train_dset,test_dset)
#fhmm_result = co_result