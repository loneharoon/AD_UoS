#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
In this file I Compute LBM features of all appliances for a home and save in a json/pickle file
Created on Fri Dec 22 15:13:33 2017

@author: haroonr
"""

#%% 
import pandas as pd
import numpy as np
from copy import copy,deepcopy
from hmmlearn import hmm
np.random.seed(42)
import pickle,sys
from collections import Counter,OrderedDict
#exec(open("/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/disaggregation_codes/LBM_features_support.py").read())
sys.path.append('/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/disaggregation_codes/')
import LBM_features_support as lbmsupport
import standardize_column_names
#%%
dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/CLEAN_REFIT_081116/"
home = "House10.csv"
df = pd.read_csv(dir+home,index_col="Time")
df.index = pd.to_datetime(df.index)
df_sub = df["2014-04-01":'2014-07-30']
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
df_samp.drop('use',axis=1,inplace=True) # dropping aggregate column
df_samp = df_samp.dropna(axis=0)
#%%
sampling_time =  1 # let's not care here. Set after some visual inference
lbm_app_features = {}
appliances = df_samp.columns
#print(appliances)
#state_2_appliances = ['air1','furnace1','refrigerator1','oven1',] # for these we create 2 states in HMM otherwise  [for REFIT let's set states as 3 for all]
#%%
#appliances = ['air1','refrigerator1']
for i in appliances:
  # the data structure is implemented in sync with LBM model
  app_features = {} 
  data = copy(df_samp[i])
  data = data.values
  data = [[j] for j in data]
  print('current appliance is: {}'.format(i))
#  if i in state_2_appliances:
#    n_components = 2
#  else:
  n_components = 3
  hmm_par = lbmsupport.find_hmm_parameters(data,n_components)
  app_features['means'] = hmm_par.means_.tolist() 
  app_features['startprob'] = hmm_par.startprob_.reshape(-1,1).tolist()
  app_features['transprob'] = hmm_par.transmat_.tolist()
  data_daywise =  pd.groupby(df_samp[i],by=df_samp[i].index.date)
  lbm_cyclepar =  lbmsupport.find_cycle_parameters(data_daywise,sampling_time)
  app_features['numberOfCyclesStats'] = lbm_cyclepar
  lbm_sacpar = lbmsupport.find_sac_parameters(data_daywise,sampling_time)
  app_features.update(lbm_sacpar) # merging dictionaries
  lbm_app_features[i] = app_features
#%% save as pickle format
save_dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/Intermediary_results/lbm/population_models/"
savename = save_dir +  home.split('.')[0] + '.pkl'
lbmsupport.save_obj(lbm_app_features, savename)
   
#%% OR Save dictionary in a json file
json_save_dir = "/Volumes/MacintoshHD2/Users/haroonr/Dropbox/nilmtk_work/inter_results/lbm_population_models/"
savename = json_save_dir +  home.split('.')[0] + '.json'
with open(savename,'w') as fp:
  json.dump(subdict,fp,indent = 4)