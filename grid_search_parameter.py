#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
IN this file I search optimal set of parameters.
Most of the code taken from pipeline_main.py(). ONly loops added
Created on Mon Feb 19 16:27:09 2018

@author: haroonr
"""



import pickle
import pandas as pd
import sys
sys.path.append('/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/disaggregation_codes/')
import standardize_column_names as scn
import AD_support as ads
import re
import accuracy_metrics_disagg as acmat
import matplotlib.pyplot as plt
#%%
file_location = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/Intermediary_results/"
home = "House18.pkl"
#myapp = "Chest_Freezer"# home 10
#myapp = "Freezer"# home 10
#myapp = "Fridge_Freezer_1"# home 16
myapp = "Fridge_Freezer"# home 18
#myapp = "ElectricHeater"# home 1
method="co/selected/"
#method="lbm/selected_results/"

filename= file_location + method + home
results = open(filename, 'rb')
data_dic = pickle.load(results)
train_power =   data_dic['train_power']
decoded_power = data_dic['decoded_power']
actual_power  = data_dic['actual_power']
#TODO : SETME
train_data =  train_power[myapp]
test_data =   actual_power[myapp]
#test_data =   decoded_power[myapp][:'2014-10-24'] # house10

contexts = [1,2,3,4,6,8]
alphas = [1,1.5,2,2.5,3]
sigmas = [1,1.5,2,2.5,3,3.5]
data_sampling_time = 1 #in minutes
data_sampling_type = "minutes" # or seconds
#%%
for i in contexts:
    train_results = ads.AD_refit_training(train_data,data_sampling_type,data_sampling_time, NoOfContexts=i)
    test_results  = ads.AD_refit_testing(test_data,data_sampling_type,data_sampling_time, NoOfContexts=i)            
    for alpha in alphas:
        alpha = 1
        for sigma in sigmas:
            num_std = sigma
            res_df = ads.anomaly_detection_algorithm(test_results,train_results,alpha,num_std)
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
            print(alpha,sigma,i,precision,recall, fscore)
            print('\n')

