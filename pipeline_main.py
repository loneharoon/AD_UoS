#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
It reads disaggregation results and the ground truth first and then
runs anomaly detection algorithm
Created on Fri Feb  9 09:27:42 2018

@author: haroonr
"""
#%%
''' Running instructions:
    1. For each home, first obtain results with CO, next FHMM and finally with submetered, that is last cell of this file
    2. Read TODO lines break running the code'''

#%%
import pickle
import pandas as pd
import sys
sys.path.append('/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/disaggregation_codes/')
import standardize_column_names as scn
import AD_support as ads
import re
import accuracy_metrics_disagg as acmat
import matplotlib.pyplot as plt
from copy import deepcopy
import pipeline_support as ps
#%% 
file_location = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/Intermediary_results/"
logging_file = file_location+"noisy_resultfile.csv"
resultfile = open(logging_file,'a')

#TODO : TUNE ME
home = "House1.pkl" # options are: 10,20,18,16,1
disagg_approach = "fhmm" # options are co,fhmm, lbm

NoOfContexts = 4
alpha = 2
num_std = 2
myapp = ads.get_selected_home_appliance(home)

resultfile.write('*********************NEW HOME*****************\n')
#TODO : TUNE ME % path for reading pickle files
method="noisy/"+ disagg_approach+ "/selected/"
#method="lbm/selected_results/"

resultfile.write("\n Home is {} and appliance is {}\n ".format(home,myapp))
filename= file_location + method + home
results = open(filename, 'rb')
data_dic = pickle.load(results)
resultfile.close()
#%%
train_power =   data_dic['train_power']
decoded_power = data_dic['decoded_power']
actual_power  = data_dic['actual_power']
# TUNE ME
train_data =  train_power[myapp]
test_data =   decoded_power[myapp]
#test_data =   decoded_power[myapp][:'2014-10-24'] # house10
data_sampling_time = 1 #in minutes
data_sampling_type = "minutes" # or seconds
#%
ps.compute_AD_and_disagg_status(logging_file,train_data,data_sampling_type,data_sampling_time, NoOfContexts,myapp,test_data,data_dic,disagg_approach,home,file_location,alpha,num_std)

#%% for SUBMETERED DATA CASE 
#actual_signature =   actual_power[myapp]
disagg_approach = "SUBMETERED"
ps.compute_AD_status_only(logging_file,train_data,data_sampling_type,data_sampling_time, NoOfContexts,myapp,actual_power[myapp],data_dic,disagg_approach,home,file_location,alpha,num_std,actual_power)

