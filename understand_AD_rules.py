#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
In this file, I understand how two (energy per cycle and number of cycles) AD rules affect overall Anomaly detection. Question is should we consider only Energy or cycle frequecy for anomaly detecion. Current knowlege using 
both of these results in high false positives. With this I think all TP were fagged by chance.

Experiment result: Results show that using only energy decreases FP but increase FN. 
conclusion: Plot all actual anomalies and count no of long and frequent anomalies
Created on Thu Mar 22 14:15:03 2018

@author: haroonr
"""
import pickle
import sys
sys.path.append('/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/disaggregation_codes/')
import AD_support as ads
import re
import accuracy_metrics_disagg as acmat
import pandas as pd
import standardize_column_names as scn


#%% 
file_location = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/Intermediary_results/"
#TODO : TUNE ME
log_report = False # this logs final reports, log only if you are sure of algorithm
ad_logging = False # this logs intermediary AD results 
if log_report:
    #TODO : TUNE ME
  logging_file = file_location + "noisy_resultfile.csv" # denoisy_resultfile.csv
  resultfile = open(logging_file,'a')
else:
  logging_file = " "

#TODO : TUNE  US [we are 5]
home = "House10.pkl" # options are: 10, 20, 18, 16, 1
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
#%%
data_sampling_time = 1 #in minutes
data_sampling_type = "minutes" # or seconds
if log_report:
  resultfile = open(logging_file,'a')
  resultfile.write('*********************NEW HOME*****************\n')    
train_results = ads.AD_refit_training(train_data,data_sampling_type,data_sampling_time, NoOfContexts,myapp)
test_results  = ads.AD_refit_testing(test_data,data_sampling_type,data_sampling_time, NoOfContexts,myapp)            
#%
if myapp == 'ElectricHeater':
    res_df = ads.anomaly_detection_algorithm_ElectricHeater(test_results,train_results,alpha,num_std)
else:
    res_df = ads.anomaly_detection_algorithm(test_results,train_results,alpha,num_std)

result_sub = res_df[res_df.anomtype == "long"]
print ("ONLY SELECTING LONG ANOMALIES, DROPPING FREQUENT ONES")



#%
# Compute disaggregation accuracies
norm_error = acmat.accuracy_metric_norm_error(data_dic)
if log_report:
  resultfile.write('Following two disaggagregation metrics of {} approach \n'.format(disagg_approach))
  resultfile.write(str(norm_error))
  resultfile.write('\n')
else:
  print('ANE is:\n')
  print(norm_error)
confus_mat = acmat.call_confusion_metrics_on_disagg(data_dic['actual_power'],data_dic['decoded_power'],power_threshold=10)
confus_mat = pd.DataFrame.from_dict(confus_mat)
if log_report:
  resultfile.write(str(confus_mat))
  resultfile.write('\n')
else:
  print('Confusion matrix accuracies are:\n')
  print(confus_mat)
#%
# Compute anomaly detection accuracies
#house_no = 1
house_no =  int(re.findall('\d+',home)[0])
home = home.split('.')[0]+'.csv'
appliance = scn.reverse_lookup(home,myapp) # find actual name of appliance in anomaly database
assert len(appliance) > 1
day_start = test_data.first_valid_index()
day_end = test_data.last_valid_index()
gt,ob = ads.tidy_gt_and_ob(house_no,appliance,day_start,day_end,result_sub)
#confusion_matrix(gt.day.values,ob.day.values)
precision,recall, fscore = ads.compute_AD_confusion_metrics(gt,ob)
#print(precision,recall, fscore)  
if log_report:
  resultfile.write("Anomaly detection accuracies at; context {}, alpha {}, std {} on {} data \n".format(NoOfContexts,alpha,num_std,disagg_approach))
  resultfile.write('Precision, reall and f_score are: {}, {}, {} \n'.format(precision,recall, fscore))
  resultfile.close()
else:
  print("Anomaly detection accuracies at; context {}, alpha {}, std {} on {} data \n".format(NoOfContexts,alpha,num_std,disagg_approach))
  print('Precision, reall and f_score are: {}, {}, {} \n'.format(precision,recall, fscore))
