#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
In this I understand how median filtering affect disaggregation (ONLY CO AND FHMM FROM THIS MODULE) process. Intermediary results are saved in separte directory. Please use gsp and sshmm scripts to get median filtered outputs for those too
Created on Wed May  9 17:28:02 2018

@author: haroonr
"""

import numpy as np
import scipy as sp
from scipy import signal # it is necessary
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import sys,pickle,time
sys.path.append('/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/disaggregation_codes/')
import accuracy_metrics_disagg as acmat
import localize_fhmm, co, standardize_column_names
import matplotlib.pyplot as plt
from copy import deepcopy
import AD_support as ads
from standardize_column_names import rename_appliances
import latent_Bayesian_melding as LBM
#%%
dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/REFIT_selected/"
home = "House16.csv"
df = pd.read_csv(dir + home, index_col = "Time")
df.index = pd.to_datetime(df.index)
df_sub = deepcopy(df[:])
#% Resampling data
#TODO : Toggle switch and set sampling rate correctly
resample = True
data_sampling_time = 1 #in minutes
data_sampling_type = "minutes" # or seconds
if resample: 
  df_samp = df_sub.resample('1T', label = 'right', closed = 'right').mean()
  df_samp.drop('Issues', axis = 1, inplace = True)
  standardize_column_names.rename_appliances(home, df_samp) # this renames columns
  #df_samp.rename(columns={'Aggregate':'use'},inplace=True) # renaming agg column
  print("*****RESAMPling DONE********")
  if home == "House16.csv":
      df_samp = df_samp[df_samp.index!= '2014-03-08'] # after resamping this day gets created 
else:
  df_samp = deepcopy(df_sub)
  df_samp.drop('Issues', axis = 1, inplace = True)
  standardize_column_names.rename_appliances(home, df_samp) # this renames columns  

energy = df_samp.sum(axis = 0)
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

#%% Apply filtering
filtered = deepcopy(df_selected)
filtered_agg = sp.signal.medfilt(filtered['use'], kernel_size = 5)
filtered['use'] = filtered_agg
print ("Applied median filter")
#plt.subplot(2,1,1)
#train_dset['2014-04-01']['use'].plot()
#plt.subplot(2,1,2)
#filtered['2014-04-01']['use'].plot()
#%
train_dset, test_dset = ads.get_selected_home_data(home, filtered)
#%% RUN fHMM
save_dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/Intermediary_results/"
#TODO : TUNE ME
filename = save_dir + "noisy_median_filtered/fhmm/windowsize5/" + home.split('.')[0] + '.pkl'
fhmm_result  =  localize_fhmm.fhmm_decoding(train_dset, test_dset) # dissagreation
fhmm_result['actual_power']['use'] = test_dset['use']
fhmm_result['train_power'] = train_dset
handle = open(filename,'wb')
pickle.dump(fhmm_result, handle, protocol = 2)
handle.close()  
#%% RUN CO
save_dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/Intermediary_results/"
#TODO : TUNE ME
filename = save_dir + "noisy_median_filtered/co/windowsize5/" + home.split('.')[0] + '.pkl'
co_result = co.co_decoding(train_dset, test_dset)
co_result['actual_power']['use'] = test_dset['use'] # appending aggregate column for later use
co_result['train_power'] = train_dset
handle = open(filename, 'wb')
pickle.dump(co_result, handle, protocol = 2)
handle.close()