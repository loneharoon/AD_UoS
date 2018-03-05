#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  1 08:54:19 2018

@author: haroonr
"""

import sys, json
from statistics import mean
from time import time
from datetime import datetime
#from libDataLoaders import dataset_loader
#from libFolding import Folding
sys.path.append('/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/python_3_codes/')
from libPMF import EmpiricalPMF
from libSSHMM import SuperStateHMM, frange
from libAccuracy import Accuracy
ε = 0.00021
from copy import deepcopy
import pandas as pd
sys.path.append('/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/disaggregation_codes/')
import AD_support as ads
import makonin_support as mks
#%%

dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/REFIT_selected/"

home = "House1.csv"
df = pd.read_csv(dir+home,index_col="Time")
df.index = pd.to_datetime(df.index)
df_sub = deepcopy(df[:])
resample = True
data_sampling_time = 1 #in minutes
data_sampling_type = "minutes" # or seconds
if resample: 
  df_samp = df_sub.resample('1T',label='right',closed='right').mean()
  df_samp.drop('Issues',axis=1,inplace=True)
  #standardize_column_names.rename_appliances(home,df_samp) # this renames columns
  #df_samp.rename(columns={'Aggregate':'use'},inplace=True) # renaming agg column
  print("*****RESAMPling DONE********")
  if home == "House16.csv":
      df_samp = df_samp[df_samp.index!= '2014-03-08'] # after resamping this day gets created 
else:
  df_samp = deepcopy(df_sub)
  df_samp.drop('Issues',axis=1,inplace=True)
  #standardize_column_names.rename_appliances(home,df_samp) # this renames columns  

energy = df_samp.sum(axis=0)
high_energy_apps = energy.nlargest(7).keys() # CONTROL : selects few appliances
df_selected = df_samp[high_energy_apps]
#TODO : TUNE ME
denoised = False
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
ids.remove('Aggregate')

train_times = []
max_states = 4 # makonin set 4
precision = 1 # makonin set 10
#TODO: FIX ME
max_obs = 23970 # don;t know it fully ## maximum of aggregate values
max_obs = float(max_obs)
max_states = int(max_states)

#%%
sshmms = mks.create_train_model(train_dset,ids,max_states,max_obs,precision)

#%%  start testing
#modeldb = "/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/sshmm_results/interresults"
#mdoe
#test_id, modeldb, precision, measure, denoised, limit, algo_name = 'haroon', modeldb,1, 'P','noisy',86400,'SparseViterbi'
#fp = open(modeldb, 'r')
#jdata = json.load(fp)
#fp.close()
##%
#folds = len(jdata)
#
##print('\tModel set for %d-fold cross-validation.' % folds)
#print('\tLoading JSON data into SSHMM objects...')
#sshmms = []
#for data in jdata:
#    sshmm = SuperStateHMM()
#    sshmm._fromdict(data)
#    sshmms.append(sshmm)
#del jdata
#labels = sshmms[0].labels
#print('\tModel lables are: ', labels)
#%%
print()
#folds=1
#test_id, modeldb, precision, measure, denoised, limit, algo_name = 'haroon', '',1, 'P','noisy',86400,'SparseViterbi'


labels = sshmms[0].labels
precision = 1
algo_name = 'SparseViterbi'
limit ="all"
print('Testing %s algorithm load disagg...' % algo_name)
disagg_algo = getattr(__import__('algo_' + algo_name, fromlist=['disagg_algo']), 'disagg_algo')
gt_dat,pred_dat = mks.perform_testing(test_dset,sshmms,labels,disagg_algo,limit)
gt_data  =  pd.DataFrame.from_records(gt_dat)
pred_dat = pd.DataFrame.from_records(pred_dat)
pred_dat.columns = labels
pred_dat['ElectricHeater'].plot()
#%%

