#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
In this file, I compute the metrics(RMSE and correlation) on NILM smoothened data
Created on Wed May  9 08:44:57 2018

@author: haroonr
"""
import sys, pickle
import pipeline_support as ps
import AD_support as ads
#%%
file_location = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/Intermediary_results/nilm_smoothened/"
#TODO : TUNE ME
fpath = file_location + 'sshmms/std2/House10.pkl'
home = "House10.pkl" # options are: 10, 20, 18, 16, 1
disagg_approach = "sshmms" # options are co,fhmm, lbm,sshmms,gsp
myapp = ads.get_selected_home_appliance(home)
filename = file_location + disagg_approach + "/" + home
results = open(filename, 'rb')
if sys.version_info > (3, 0):
  data_dic = pickle.load(results, encoding = 'latin1')
else:
  data_dic = pickle.load(results)
results.close()

train_power =   data_dic['train_power']
decoded_power = data_dic['decoded_power']
actual_power  = data_dic['actual_power']
if disagg_approach == "lbm":
    data_dic['decoded_power'] = data_dic['decoded_power'].drop(['inferred mains'],axis=1)
train_data =  train_power[myapp]
test_data =   decoded_power[myapp]
actual_data = actual_power[myapp]
#%%
ps.compute_accuracy_metrics_on_NILM_smoothend_ver(data_actual, nilm_smoothened)
