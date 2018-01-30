#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
In this script, I use all disaggregatin metrics to understand which will makes more sense to understand the 
disaggregation performance
Experiment:
    1. Get disagg data
    2. Find results for accuracy metrics using NILM and submetered data
    3. Plot both NILM and submeterd data to understand in better way
Created on Mon Jan 29 12:07:37 2018
@author: haroonr
"""
#%%
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import sys
sys.path.append('/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/disaggregation_codes/')
import accuracy_metrics_disagg as acmat
import localize_fhmm,co
import matplotlib.pyplot as plt
#%%
dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/CLEAN_REFIT_081116/"
home = "House1.csv"
df = pd.read_csv(dir+home,index_col="Time")
df.index = pd.to_datetime(df.index)
df_sub = df["2014-03-01":'2014-04-30'] # since before march their are calibration issues

#%% Resampling data
print("*****RESAMPLING********")
df_samp = df_sub.resample('1T',label='right',closed='right').mean()
data_sampling_time = 1 #in minutes
data_sampling_type = "minutes" # or seconds
df_samp.drop('Issues',axis=1,inplace=True)
df_samp.rename(columns={'Aggregate':'use'},inplace=True) # renaming agg column
#%%
#res = df.sum(axis=0)
#high_energy_apps = res.nlargest(6).keys() # CONTROL : selects few appliances
#df_new = df[high_energy_apps]
#del df_new['use']# drop stale aggregate column
#df_new['use'] = df_new.sum(axis=1) # create new aggregate column
#%%
res = df_samp.sum(axis=0)
high_energy_apps = res.nlargest(7).keys() # CONTROL : selects few appliances
df_samp = df_samp[high_energy_apps]
#del df_new['use']# drop stale aggregate column
#df_new['use'] = df_new.sum(axis=1) # create new aggregate column


#%%
train_dset = df_samp['2014-03-11':'2014-03-29']
train_dset.dropna(inplace=True)
#test_dset = df_samp['2014-04-01':'2014-04-04']
test_dset = df_samp['2014-04-01']
test_dset.dropna(inplace=True)
#%%
fhmm_result  =  localize_fhmm.fhmm_decoding(train_dset,test_dset) # dissagreation
#co_result = co.co_decoding(train_dset,test_dset)
#fhmm_result = co_result
#%%
fhmm_rmse = acmat.compute_rmse(fhmm_result['actaul_power'],fhmm_result['decoded_power'])
print(fhmm_rmse)
aggregate = sum(test_dset['use'])
fhmm_kolter2 = acmat.diss_accu_metric_kolter_exact(fhmm_result,aggregate)
print(fhmm_kolter2)
norm_fhmm = acmat.accuracy_metric_norm_error(fhmm_result)
print(norm_fhmm)
kolter_appliance = acmat.diss_accu_metric_kolter_appliance_wise(fhmm_result)
print(kolter_appliance)
mae = acmat.compute_mae(fhmm_result['actaul_power'],fhmm_result['decoded_power'])
print(mae)
confus_mat = acmat.call_confusion_metrics_on_disagg(fhmm_result['actaul_power'],fhmm_result['decoded_power'],power_threshold=10)
pd.DataFrame.from_dict(confus_mat)
acmat.compute_EEFI_AEFI_metrics(fhmm_result['actaul_power'],fhmm_result['decoded_power'])

#%%
gt= fhmm_result['actaul_power']
pred= fhmm_result['decoded_power']
#%% DATA PLOTTING
count= 0
fig,axes = plt.subplots(pred.columns.shape[0]*2,1,sharex=True,figsize=(16,10))
for app in pred.columns:
    gt1    = gt[app]
    pred1  = pred[app]
    gt1.plot(ax=axes[count],color="blue",legend=app)
    count = count+1
    pred1.plot(ax=axes[count],color="black")
    count = count+1
plt.show()
#%%
acmat.call_confusion_metrics_on_disagg(fhmm_result['actaul_power'],fhmm_result['decoded_power'])