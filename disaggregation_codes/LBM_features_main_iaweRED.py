#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
In this file I Compute LBM features of all appliances for a home (iawe and redd) and save in a pickle file. This is replica of LBM_features_main.py for 1 second data
Created on Fri Dec 29 19:49:46 2017

@author: haroonr
"""
#%% 
import pandas as pd
import numpy as np
from copy import copy
from hmmlearn import hmm
np.random.seed(42)
import json,pickle
from collections import Counter,OrderedDict
exec(open("/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/disaggregation_codes/LBM_features_support.py").read())
#%%
dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/Dataport/mix_homes/default/injected_anomalies/"
home =  "redd_home_6.csv" #"meter_2.csv"# 
#%%
df = pd.read_csv(dir+home,index_col="localminute")
df.index = pd.to_datetime(df.index)
#%% SPEICIFIC TO iawe and redd home
res = df.sum(axis=0)
# since the aggregate has no impact on the population parameters of different applainces so I create a train file or pickle for all appliances

#high_energy_apps = ['use','air1','refrigerator1','laptop','tv','water_filter'] # for aiwe
#high_energy_apps = ['use','air1','refrigerator1','electric_heat','stove','bathroom_gfi'] # for redd_home
#df_new = df[high_energy_apps]
df_new = df
del df_new['use']# dont need for building population models
#train_df = df_new.truncate(before="2013-07-13", after="2013-08-03 23:59:59") # for iawe
train_df = df_new.truncate(before="2011-05-24", after="2011-06-12 23:59:59") # for redd [all data given since less training data, lets see how it works]
train_df = train_df.dropna() # drops rows containing na values
#%%
sampling_time =  1 # let's not care here. Set after some visual inference
lbm_app_features = {}
appliances = train_df.columns
print(appliances)
state_2_appliances = ['air1','furnace1','refrigerator1'] # for these we create 2 states in HMM otherwise 
#%%
#appliances = ['air1','refrigerator1']
for i in appliances:
  # the data structure is implemented in sync with LBM model
  app_features = {} 
  data = copy(train_df[i])
  data = data.values
  data = [[j] for j in data]
  print('current appliance is: {}'.format(i))
  if i in state_2_appliances:
    n_components = 2
  else:
    n_components = 3
  hmm_par = find_hmm_parameters(data,n_components)
  app_features['means'] = hmm_par.means_.tolist() 
  app_features['startprob'] = hmm_par.startprob_.reshape(-1,1).tolist()
  app_features['transprob'] = hmm_par.transmat_.tolist()
  data_daywise =  pd.groupby(train_df[i],by=train_df[i].index.date)
  lbm_cyclepar =  find_cycle_parameters(data_daywise,sampling_time)
  app_features['numberOfCyclesStats'] = lbm_cyclepar
  lbm_sacpar = find_sac_parameters(data_daywise,sampling_time)
  app_features.update(lbm_sacpar) # merging dictionaries
  lbm_app_features[i] = app_features
#%% save as pickle format
save_dir = "/Volumes/MacintoshHD2/Users/haroonr/Dropbox/nilmtk_work/inter_results/lbm_population_models/"
savename = save_dir +  home.split('.')[0] + '.pkl'
save_obj(lbm_app_features, savename)
   
#%% OR Save dictionary in a json file
json_save_dir = "/Volumes/MacintoshHD2/Users/haroonr/Dropbox/nilmtk_work/inter_results/lbm_population_models/"
savename = json_save_dir +  home.split('.')[0] + '.json'
with open(savename,'w') as fp:
  json.dump(subdict,fp,indent = 4)