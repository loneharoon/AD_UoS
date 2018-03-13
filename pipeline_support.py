#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 13:49:08 2018

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
from copy import deepcopy

#%%
def compute_AD_and_disagg_status(logging_file,log_report, train_data,data_sampling_type,data_sampling_time, NoOfContexts,myapp,test_data,data_dic,disagg_approach,home,file_location,alpha,num_std):
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
    #result_sub = res_df[res_df.status==1]
    result_sub = res_df
    
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
    assert len(appliance)>1
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
    
    
def compute_AD_status_only(logging_file,train_data,data_sampling_type,data_sampling_time, NoOfContexts,myapp,test_data,data_dic,disagg_approach,home,file_location,alpha,num_std,actual_signature):
    
    train_results = ads.AD_refit_training(train_data,data_sampling_type,data_sampling_time, NoOfContexts,myapp)
    test_results  = ads.AD_refit_testing(test_data,data_sampling_type,data_sampling_time, NoOfContexts,myapp)            
    if myapp == 'ElectricHeater':
        res_df = ads.anomaly_detection_algorithm_ElectricHeater(test_results,train_results,alpha,num_std)
    else:
        res_df = ads.anomaly_detection_algorithm(test_results,train_results,alpha,num_std)
    #result_sub = res_df[res_df.status==1]
    result_sub = res_df
    
    resultfile = open(logging_file,'a')
    resultfile.write('*********************NEW HOME*****************\n') 
    resultfile.write("\n Home is {} and appliance is {}\n ".format(home,myapp))
    house_no =  int(re.findall('\d+',home)[0])
    home = home.split('.')[0]+'.csv'
    appliance = scn.reverse_lookup(home,myapp) # find actual name of appliance in anomaly database
    assert len(appliance)>1
    day_start = test_data.first_valid_index()
    day_end = test_data.last_valid_index()
    gt,ob = ads.tidy_gt_and_ob(house_no,appliance,day_start,day_end,result_sub)
    #confusion_matrix(gt.day.values,ob.day.values)
    precision,recall, fscore = ads.compute_AD_confusion_metrics(gt,ob)
    #print(precision,recall, fscore)  
    resultfile.write("Anomaly detection accuracies at; context {}, alpha {}, std {} on {} data \n".format(NoOfContexts,alpha,num_std,disagg_approach))
    resultfile.write('Precision, reall and f_score are: {}, {}, {} \n'.format(precision,recall, fscore))
    #resultfile.close()
    
    #%
    noise_content = ads.compute_noise_percentage(actual_signature)
    resultfile.write('Noise percentage in the disagg data was: {}\n'.format(noise_content))
    #%
    resultfile.close()