#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
IN this file I search optimal set of parameters for anomaly detection.
Most of the code taken from pipeline_main.py(). ONly loops added
Created on Mon Feb 19 16:27:09 2018

@author: haroonr
"""

import pickle
import pandas as pd
import numpy as np
import sys
sys.path.append('/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/disaggregation_codes/')
import standardize_column_names as scn
import AD_support as ads
import re
from copy import deepcopy
import accuracy_metrics_disagg as acmat
import matplotlib.pyplot as plt
#%%
file_location = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/Intermediary_results/noisy/"
#TODO: tune two of us
home = "House10.pkl"
home_no = home.split('.')[0]
#myapp = "ElectricHeater"# home 1
myapp = "Chest_Freezer"# home 10
#myapp = "Fridge_Freezer_1"# home 16
#myapp = "Fridge_Freezer"# home 18
#myapp = "Freezer"# home 20

method="co/selected/"
#method="lbm/selected_results/"

filename = file_location + method + home
results = open(filename, 'rb')
data_dic = pickle.load(results)
train_power =   data_dic['train_power']
decoded_power = data_dic['decoded_power']
actual_power  = data_dic['actual_power']
#TODO : SETME
train_data =  train_power[myapp]
test_data =   actual_power[myapp]
#test_data =   decoded_power[myapp][:'2014-10-24'] # house10
#%% GRID SEARCH
contexts = [1, 2, 3, 4, 6, 8]
alphas = [1,1.5,2,2.5,3,3.5]
sigmas = [1,1.5,2,2.5,3,3.5]
data_sampling_time = 1 #in minutes
data_sampling_type = "minutes" # or seconds

logfile = '/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/AD_gridsearch_results.csv'
fp = open(logfile,'a')
#fp.write('\n Home is {} \n'.format(home))
#fp.write('columns are: NoOfContexts, alpha, sigma, precision, recall, fscore \n')
#fp.write('********************************\n')
for i in contexts:
    train_results = ads.AD_refit_training(train_data, data_sampling_type, data_sampling_time, i, myapp)
    test_results  = ads.AD_refit_testing(test_data, data_sampling_type, data_sampling_time, i, myapp)            
    for alpha in alphas:
        #alpha = alpha
        for sigma in sigmas:
            num_std = sigma
            if myapp == 'ElectricHeater':
                res_df = ads.anomaly_detection_algorithm_ElectricHeater(test_results,train_results,alpha,num_std)
            else:
                res_df = ads.anomaly_detection_algorithm(test_results,train_results,alpha,num_std)
            #res_df = ads.anomaly_detection_algorithm(test_results,train_results,alpha,num_std)
            result_sub = res_df
            
            house_no =  int(re.findall('\d+',home)[0])
            home = home.split('.')[0]+'.csv'
            appliance = scn.reverse_lookup(home,myapp) # find actual name of appliance in anomaly database
            assert len(appliance) > 1
            day_start = test_data.first_valid_index()
            day_end = test_data.last_valid_index()
            #print('both S and NS anomalies selected')
            gt,ob = ads.tidy_gt_and_ob(house_no,appliance,day_start,day_end,result_sub)
            precision,recall, fscore = ads.compute_AD_confusion_metrics(gt,ob)
            fp.write('{},\t{},\t{},\t{},\t{},\t{},\t{},\t{}\n'.format(home_no,myapp,i,alpha,sigma,precision,recall, fscore))
            #fp.write('\n')
            #print(alpha,sigma,i,precision,recall, fscore)
    #fp.write('*********************************\n')
#fp.write('****************END*****************\n')
fp.close()
#%%
temp_test = deepcopy(test_data)
train_data = train_data['2014-12-14']

#%% WITHOUT GRID SEARCH .. NORMAL CASE
appliance= "ElectricHeater" # only in case of home 1 required,
context= 4
alpha = 2
sigma = 2
data_sampling_time = 1 #in minutes
data_sampling_type = "minutes" # or seconds
train_results = ads.AD_refit_training(train_data,data_sampling_type,data_sampling_time, context,appliance)
test_results  = ads.AD_refit_testing(test_data,data_sampling_type,data_sampling_time,context,appliance)        

#res_df = ads.anomaly_detection_algorithm(test_results,train_results,alpha,num_std)
res_df = ads.anomaly_detection_algorithm_ElectricHeater(test_results,train_results,alpha,num_std)

result_sub = res_df
house_no =  int(re.findall('\d+',home)[0])
home = home.split('.')[0]+'.csv'
appliance = scn.reverse_lookup(home,myapp) # find actual name of appliance in anomaly database
assert len(appliance)>1
day_start = test_data.first_valid_index()
day_end = test_data.last_valid_index()
#print('both S and NS anomalies selected')
gt,ob = ads.tidy_gt_and_ob(house_no,appliance,day_start,day_end,result_sub)
precision,recall, fscore = ads.compute_AD_confusion_metrics(gt,ob)
print(context,alpha,sigma,precision,recall, fscore)

#%%
test_data['2014-07-05'].plot()
dt = test_data['2014-07-04': '2014-07-04 05:59:59']
#%%
test_results['2014-10-02']['next8_gp']['ON_energy']
test_results['2014-10-02']['day_1_gp']['ON_energy']
test_results['2014-10-02']['day_2_gp']['ON_energy']
#%%
test_temporary = df_selected['2015-01']['Chest_Freezer']