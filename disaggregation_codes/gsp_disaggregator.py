#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
In this I implement Bochao's GSP disaggregation method
Created on Thu Feb  1 15:42:41 2018

@author: haroonr
"""
from __future__ import division
import warnings
warnings.filterwarnings("ignore")
import pandas as pd
import sys

sys.path.append('/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/disaggregation_codes/')
import accuracy_metrics_disagg as acmat
import matplotlib.pyplot as plt
import gsp_support as gsp
import AD_support as ads
from copy import deepcopy
import standardize_column_names

#%%
dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/REFIT_selected/"
home = "House20.csv"
df = pd.read_csv(dir+home,index_col="Time")
df.index = pd.to_datetime(df.index)
df_sub = deepcopy(df[:])
#% Resampling data
#TODO : TUNE ME
resample = True
data_sampling_time = 1 #in minutes
data_sampling_type = "minutes" # or seconds
if resample: 
  df_samp = df_sub.resample('1T',label='right',closed='right').mean()
  df_samp.drop('Issues',axis=1,inplace=True)
  standardize_column_names.rename_appliances(home,df_samp) # this renames columns
  #df_samp.rename(columns={'Aggregate':'use'},inplace=True) # renaming agg column
  print("*****RESAMPling DONE********")
  if home == "House16.csv":
      df_samp = df_samp[df_samp.index!= '2014-03-08'] # after resamping this day gets created 
else:
  df_samp = deepcopy(df_sub)
  df_samp.drop('Issues',axis=1,inplace=True)
  standardize_column_names.rename_appliances(home,df_samp) # this renames columns  

energy = df_samp.sum(axis=0)
high_energy_apps = energy.nlargest(7).keys() # CONTROL : selects few appliances
df_selected = df_samp[high_energy_apps]
#%
#TODO : TUNE ME
denoised = False
if denoised:
    # chaning aggregate column
    iams = high_energy_apps.difference(['use'])
    df_selected['use'] = df_selected[iams].sum(axis=1)
    print('**********DENOISED DATA*************8')
train_dset,test_dset = ads.get_selected_home_data(home,df_selected)
#%%
main = train_dset['use']
main_val = main.values
main_ind = main.index
#%%
data_vec =  main_val
delta_p = [round(data_vec[i+1] - data_vec[i],2) for i in range(0,len(data_vec)-1)]
sigma = 40;
ri = 0.1;
T_Positive = 40;
T_Negative = -40;
event =  [i for i in range(0, len(delta_p)) if (delta_p[i] > T_Positive or delta_p[i] < T_Negative) ]
clusters = gsp.refined_clustering_block(event, delta_p, sigma, ri)
finalclusters, pairs = gsp.pair_clusters_appliance_wise(clusters, data_vec, delta_p)
#%%
alpha = 0.6
beta = 0.4
appliance_pairs = gsp.feature_matching_module(pairs, delta_p, finalclusters, alpha, beta)
power_series = gsp.generate_appliance_powerseries(appliance_pairs,delta_p)
power_timeseries = gsp.create_appliance_timeseries_signature(power_series,main_ind)
gsp_result = pd.concat(power_timeseries,axis=1)
mapped_names = gsp.map_appliance_names(train_dset,gsp_result)
gsp_result.rename(columns=mapped_names,inplace=True)
gsp_result.plot(subplots=True)
#%%
fig,axes = plt.subplots(nrows=9,ncols=2,sharex=False,sharey=False,figsize=(12,15))
app =0
for ax in range(len(power_series)//2):
    axes[ax,0].plot(power_series[app].timestamp,power_series[app].power)
    app+=1
    axes[ax,1].plot(power_series[app].timestamp,power_series[app].power)
    app+=1
#fig.savefig("gsp.png")
#%% create mat files

fig,axes = plt.subplots(nrows=9,ncols=2,sharex=False,sharey=False,figsize=(12,15))
app =0
for ax in range(len(power_timeseries)//2):
    axes[ax,0].plot(power_timeseries[app])
    app+=1
    axes[ax,1].plot(power_timeseries[app])
    app+=1



