#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  1 08:54:19 2018
It works in python 3 only
@author: haroonr
"""

import sys,pickle
sys.path.append('/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/python_3_codes/')
from copy import deepcopy
import pandas as pd
sys.path.append('/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/disaggregation_codes/')
import AD_support as ads
import makonin_support as mks
import standardize_column_names as scn
import numpy as np
#%%

dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/REFIT_selected/"

home = "House18.csv"
df = pd.read_csv(dir+home,index_col="Time")
df.index = pd.to_datetime(df.index)
df_sub = deepcopy(df[:])
#TODO : TUNE ME
resample = True
data_sampling_time = 1 #in minutes
data_sampling_type = "minutes" # or seconds
if resample: 
  df_samp = df_sub.resample('1T',label='right',closed='right').mean()
  df_samp.drop('Issues',axis=1,inplace=True)
  scn.rename_appliances(home,df_samp) # this renames columns
  df_samp.rename(columns={'Aggregate':'use'},inplace=True) # renaming agg column
  print("*****RESAMPling DONE********")
  if home == "House16.csv":
      df_samp = df_samp[df_samp.index!= '2014-03-08'] # after resamping this day gets created 
else:
  df_samp = deepcopy(df_sub)
  df_samp.drop('Issues',axis=1,inplace=True)
  scn.rename_appliances(home,df_samp) # this renames columns  
  df_samp.rename(columns={'Aggregate':'use'},inplace=True)

energy = df_samp.sum(axis=0)
high_energy_apps = energy.nlargest(7).keys() # CONTROL : selects few appliances
df_selected = df_samp[high_energy_apps]
#TODO : TUNE ME
denoised = True
if denoised:
    # chaning aggregate column
    iams = high_energy_apps.difference(['use'])
    df_selected['use'] = df_selected[iams].sum(axis=1)
    print('**********DENOISED DATA*************8')
train_dset,test_dset = ads.get_selected_home_data(home,df_selected)
#train_dset = train_dset[:86400]
#test_dset = test_dset[:86400]
#%%
ids = train_dset.columns.values.tolist()
ids.remove('use')

train_times = []
max_states = 4 # makonin set 4
precision = 1 
# this defines max aggregate power value as confirmed by Makonin
max_obs = np.ceil(max(df_selected['use'].values)) + 1
max_obs = float(max_obs)
max_states = int(max_states)
#%
sshmms = mks.create_train_model(train_dset,ids,max_states,max_obs,precision)

#%%
labels = sshmms[0].labels
precision = 1
algo_name = 'SparseViterbi'
limit ="all"
print('Testing %s algorithm load disagg...' % algo_name)
disagg_algo = getattr(__import__('algo_' + algo_name, fromlist=['disagg_algo']), 'disagg_algo')
sshmms_result = mks.perform_testing(test_dset,sshmms,labels,disagg_algo,limit)
sshmms_result['train_power'] = train_dset # required during anomaly detection logic
#%
save_dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/Intermediary_results/"
#TODO : TUNE ME
filename = save_dir+"denoised/sshmms/selected/"+ home.split('.')[0]+'.pkl'
handle = open(filename,'wb')
#https://docs.python.org/2/library/pickle.html
pickle.dump(sshmms_result,handle)
handle.close()
print('I am done')
#%%

