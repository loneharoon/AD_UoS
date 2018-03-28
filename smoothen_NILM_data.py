#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
In this file, I take NILM data and smoothen target appliance data only and save in another directory.
There are few redundancies in the file. Ignore those. It works properly
Created on Wed Mar 28 12:36:33 2018

@author: haroonr
"""
from __future__ import division
import pickle
import sys
sys.path.append('/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/disaggregation_codes/')
import AD_support as ads
import pipeline_support as ps
from copy import deepcopy

#%% 
file_location = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/Intermediary_results/"
log_report = False # this logs final reports, log only if you are sure of algorithm
ad_logging = False # this logs intermediary AD results 
if log_report:
  logging_file = file_location +"xxxx.csv" # denoisy_resultfile.csv
  resultfile = open(logging_file,'a')
else:
  logging_file = " "
#TODO : TUNE ME % path for reading pickle files
home = "House20.pkl" # options are: 10, 20, 18, 16, 1
disagg_approach = "co" # options are co,fhmm, lbm,sshmms,gsp


NoOfContexts = 4
alpha = 2
num_std = 2
myapp = ads.get_selected_home_appliance(home)
method = "noisy/" + disagg_approach + "/selected/" # noisy or denoised
#method="lbm/selected_results/"
if log_report:
  resultfile.write('*********************NEW HOME*****************\n')
  resultfile.write("\n Home is {} and appliance is {}\n ".format(home,myapp))
filename= file_location + method + home
results = open(filename, 'rb')
if sys.version_info > (3, 0):
  data_dic = pickle.load(results, encoding = 'latin1')
else:
  data_dic = pickle.load(results)
results.close()
if log_report:
  resultfile.close()

train_power =   data_dic['train_power']
decoded_power = data_dic['decoded_power']
actual_power  = data_dic['actual_power']
if disagg_approach == "lbm":
    data_dic['decoded_power'] = data_dic['decoded_power'].drop(['inferred mains'], axis = 1)
train_data =  train_power[myapp]
test_data =   decoded_power[myapp]
actual_data = actual_power[myapp]
#%play with training data
data_sampling_time = 1 #in minutes
data_sampling_type = "minutes" # or s
if home =="House1.pkl":
  appliance = "ElectricHeater"
else:
  appliance = "Freezer"
NoOfContexts = 4 
train_results = ads.AD_refit_training(train_data, data_sampling_type, data_sampling_time, NoOfContexts, appliance)
#%
#TODO: TUNE ME
num_std = 0 # 0, 1, 1.5, 2, .....
#data_series = test_data[:'2014-04-04']
#data_series = test_data['2014-06-1 04:00:00':'2014-06-1 05:00:00']
#nilm_smoothened = ps.smoothen_NILM_output(data_series, threshold_minutes, std, num_std)
data_series = test_data
nilm_smoothened = ps.divide_smoothen_combine(data_series, NoOfContexts, train_results, num_std)
#%
data_dic2 = {}
data_dic2['train_power'] = train_data
data_dic2['decoded_power'] = nilm_smoothened
data_dic2['actual_power'] = actual_data

save_dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/Intermediary_results/"
filename = save_dir + 'nilm_smoothened/'+ disagg_approach +'/'+'std'+ str(num_std)+"/" + home.split('.')[0] + '.pkl'
handle = open(filename,'wb')
pickle.dump(data_dic2, handle)
handle.close()
#%% read same pickle data

results = open(filename, 'rb')
if sys.version_info > (3, 0):
  data_dicpp = pickle.load(results, encoding = 'latin1')
else:
  data_dicpp = pickle.load(results)
results.close()
