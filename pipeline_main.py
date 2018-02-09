#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
It reads disaggregation results and the ground truth first and then
runs anomaly detection algorithm
Created on Fri Feb  9 09:27:42 2018

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
#%%
file_location = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/Intermediary_results/"
home = "House10.pkl"
method="co/"

filename= file_location + method + home
results = open(filename, 'rb')
data_dic = pickle.load(results)
#%%
myapp = "Chest_Freezer"
train_power =   data_dic['train_power']
decoded_power = data_dic['decoded_power']
actual_power  = data_dic['actual_power']

train_data =  train_power[myapp]
test_data =   decoded_power[myapp][:'2014-10-24']

data_sampling_time = 1 #in minutes
data_sampling_type = "minutes" # or seconds
#test_data =  df_samp[myapp]['2014-05-01':'2014-05-31'] # home 3
train_results = ads.AD_refit_training(train_data,data_sampling_type,data_sampling_time)
test_results  = ads.AD_refit_testing(test_data,data_sampling_type,data_sampling_time)            
num_std = 2
alpha = 2.5
res_df = ads.anomaly_detection_algorithm(test_results,train_results,alpha,num_std)
result_sub = res_df[res_df.status==1]

#%%
# Compute anomaly detection accuracies
#house_no = 1
house_no =  int(re.findall('\d+',home)[0])
home = home.split('.')[0]+'.csv'
appliance = scn.reverse_lookup(home,myapp) # find actual name of appliance in anomaly database
day_start = test_data.first_valid_index()
day_end = test_data.last_valid_index()
print('both S and NS anomalies selected')
gt,ob = ads.tidy_gt_and_ob(house_no,appliance,day_start,day_end,result_sub)
#confusion_matrix(gt.day.values,ob.day.values)
precision,recall, fscore = ads.compute_AD_confusion_metrics(gt,ob)
print(precision,recall, fscore)  
#%%
# Compute disaggregation accuracies
norm_fhmm = acmat.accuracy_metric_norm_error(data_dic)
print(norm_fhmm)

confus_mat = acmat.call_confusion_metrics_on_disagg(data_dic['actual_power'],data_dic['decoded_power'],power_threshold=10)
pd.DataFrame.from_dict(confus_mat)
