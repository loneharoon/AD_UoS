#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
In this file I Compute LBM features of all appliances for a home and save in a json file
Created on Fri Dec 22 15:13:33 2017

@author: haroonr
"""

#%% 
import pandas as pd
import numpy as np
from copy import copy
from hmmlearn import hmm
np.random.seed(42)
from collections import Counter,OrderedDict
exec(open("/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/disaggregation_codes/LBM_features_support.py").read())
#%%
dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/Dataport/mix_homes/default/injected_anomalies/"
fl = "115.csv"
df = pd.read_csv(dir+fl,index_col="localminute")
df.index = pd.to_datetime(df.index)
#%%
####
df.drop('use',axis=1,inplace=True)
train_df = copy(df[:'2014-06-20'])
sampling_time =  2*60
lbm_app_features = {}
appliances = train_df.columns
#%%
appliances = ['air1']
for i in appliances:
  # the data structure is implemented in sync with LBM model
  app_features = {} 
  data = copy(train_df[i])
  data = data.values
  data = [[j] for j in data]
  hmm_par = find_hmm_parameters(data)
  app_features['means'] = hmm_par.means_ 
  app_features['startprob'] = hmm_par.startprob_
  app_features['transprob'] =hmm_par.transmat_
  data_daywise =  pd.groupby(train_df[i],by=train_df[i].index.date)
  lbm_cyclepar =  find_cycle_parameters(data_daywise,sampling_time)
  app_features['numberOfCyclesStats'] = lbm_cyclepar
  lbm_sacpar = find_sac_parameters(data_daywise,sampling_time)
  app_features.update(lbm_sacpar) # merging dictionaries
  lbm_app_features[i] = apo_features
#%%