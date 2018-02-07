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
import localize_fhmm,co,standardize_column_names
import matplotlib.pyplot as plt
from copy import deepcopy
#from standardize_column_names import rename_appliances
#%%
dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/CLEAN_REFIT_081116/"
home = "House10.csv"
df = pd.read_csv(dir+home,index_col="Time")
df.index = pd.to_datetime(df.index)
#df_sub = df["2014-03-01":'2014-04-30']
df_sub = df["2014-04-01":] # since before march their are calibration issues
#%% Resampling data
resample = 'True'
data_sampling_time = 1 #in minutes
data_sampling_type = "minutes" # or seconds
if resample: 
  df_samp = df_sub.resample('1T',label='right',closed='right').mean()
  df_samp.drop('Issues',axis=1,inplace=True)
  standardize_column_names.rename_appliances(home,df_samp) # this renames columns
  #df_samp.rename(columns={'Aggregate':'use'},inplace=True) # renaming agg column
  print("*****RESAMPling DONE********")
else:
  df_samp = deepcopy(df_sub)
  df_samp.drop('Issues',axis=1,inplace=True)
  standardize_column_names.rename_appliances(home,df_samp) # this renames columns  
#%%
energy = df_samp.sum(axis=0)
high_energy_apps = energy.nlargest(7).keys() # CONTROL : selects few appliances
df_selected = df_samp[high_energy_apps]
#%% 
denoised = 'False'
if denoised:
    # chaning aggregate column
    iams = high_energy_apps.difference(['use'])
    df_selected['use'] = df_selected[iams].sum(axis=1)
    print('**********DENOISED DATA*************8')
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
norm_fhmm = acmat.accuracy_metric_norm_error(fhmm_result)
print(norm_fhmm)

#%%
gt= fhmm_result['actual_power']
pred= fhmm_result['decoded_power']
#%% DATA PLOTTING
count= 0
fig,axes = plt.subplots(pred.columns.shape[0]*2,1,sharex=True)
for app in pred.columns:
    gt1    = gt[app]
    pred1  = pred[app]
    gt1.plot(ax=axes[count],color="blue",legend=app)
    count = count+1
    pred1.plot(ax=axes[count],color="black")
    count = count+1
plt.show()