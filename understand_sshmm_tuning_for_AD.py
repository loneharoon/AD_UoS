#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
In this I see whether I can tune SSHMM output for anomaly detection.
Created on Tue Mar 27 10:16:41 2018
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
#TODO : TUNE ME
log_report = False # this logs final reports, log only if you are sure of algorithm
ad_logging = False # this logs intermediary AD results 
if log_report:
    #TODO : TUNE ME
  logging_file = file_location + "noisy_resultfile_onlyenergy_AD_rule.csv" # denoisy_resultfile.csv
  resultfile = open(logging_file,'a')
else:
  logging_file = " "

#TODO : TUNE  US [we are 5]
home = "House16.pkl" # options are: 10, 20, 18, 16, 1
disagg_approach = "sshmms" # options are co,fhmm, lbm,sshmms,gsp

NoOfContexts = 4
alpha = 2
num_std = 2
myapp = ads.get_selected_home_appliance(home)


#TODO : TUNE ME % path for reading pickle files
method = "noisy/" + disagg_approach + "/selected/" # noisy or denoised
#method="lbm/selected_results/"
if log_report:
  resultfile.write('*********************NEW HOME*****************\n')
  resultfile.write("\n Home is {} and appliance is {}\n ".format(home,myapp))
filename= file_location + method + home
results = open(filename, 'rb')
data_dic = pickle.load(results)
results.close()
if log_report:
  resultfile.close()

train_power =   data_dic['train_power']
decoded_power = data_dic['decoded_power']
actual_power  = data_dic['actual_power']
if disagg_approach == "lbm":
    data_dic['decoded_power'] = data_dic['decoded_power'].drop(['inferred mains'],axis=1)
train_data =  train_power[myapp]
test_data =   decoded_power[myapp]
actual_data = actual_power[myapp]
#%% play with training data
data_sampling_time = 1 #in minutes
data_sampling_type = "minutes" # or s
NoOfContexts, appliance = 4 ,'Freezer'
train_results = ads.AD_refit_training(train_data,data_sampling_type,data_sampling_time,NoOfContexts,appliance)
#%%
threshold_minutes = train_results['day_1_gp']['OFF_duration']['mean']
std = train_results['day_1_gp']['OFF_duration']['std']
# number of standard deviations
#%%
threshold_minutes = 10
num_std = 0 # 0, 1, 1.5, 2, .....
#data_series = test_data['2014-06-1']
data_series = test_data['2014-06-1 04:00:00':'2014-06-1 05:00:00']
#data_series = test_data
nilm_smoothened = ps.smoothen_NILM_output(data_series, threshold_minutes, std, num_std)
data_series.plot()
nilm_smoothened.plot()
#%%
ps.compute_AD_and_disagg_status_on_NILM_smoothened_data(logging_file,log_report,train_results, data_sampling_type,data_sampling_time, NoOfContexts,myapp, nilm_smoothened, data_dic, disagg_approach, home, file_location, alpha, num_std)
      
      