#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 13:49:08 2018

@author: haroonr
"""
from __future__ import division
import pickle
import pandas as pd
import sys
sys.path.append('/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/disaggregation_codes/')
import standardize_column_names as scn
import AD_support as ads
import re
import accuracy_metrics_disagg as acmat
from copy import deepcopy
from collections import OrderedDict

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
    #result_sub = res_df
    # Compute disaggregation accuracies
    norm_error = acmat.accuracy_metric_norm_error(data_dic)
    order = format_results_in_appliance_order(home)
    norm_error = norm_error.reindex(order)
    # compute rmse too
    rmse = acmat.compute_rmse_ver_dict(data_dic)
    rmse = rmse.reindex(order)
    cor_coeff = acmat.compute_correlation_ver_dict(data_dic)
    cor_coeff = cor_coeff.reindex(order)
    confus_mat = acmat.call_confusion_metrics_on_disagg(data_dic['actual_power'],data_dic['decoded_power'],power_threshold=10)
    confus_mat = pd.DataFrame.from_dict(confus_mat)
    confus_mat = confus_mat.reindex(order, axis = 1)
    
    if log_report:
      resultfile.write('Following four disaggagregation metrics of {} approach \n'.format(disagg_approach))
      resultfile.write("\n ANE is:\n")
      resultfile.write(str(norm_error))
      resultfile.write("\n RMSE is:\n")
      resultfile.write(str(rmse))
      resultfile.write("\n CORRELATION COEFFICIENT is:\n")
      resultfile.write(str(cor_coeff))
      resultfile.write("\n CONFUSION MAT is:\n")
      resultfile.write(str(confus_mat))
      resultfile.write('\n')
      resultfile.close()
    else:
      print('Appliance normalization error are \n')
      print(norm_error)
      print('RMSE is:\n')
      print(rmse)
      print('correlation values are:\n')
      print(cor_coeff) 
      print('Confusion matrix accuracies are:\n')
      print(confus_mat)
    #%%
    # Compute anomaly detection accuracies
    try:     
        result_sub = res_df[res_df.anomtype == "long"]
        print ("KEEPING LONG ANOMALIES, DROPPING FREQUENT ONES")
    except:
        result_sub = pd.DataFrame()
        print("No long anomaly found in this case\n")
    house_no =  int(re.findall('\d+',home)[0])
    home = home.split('.')[0]+'.csv'
    appliance = scn.reverse_lookup(home,myapp) # find actual name of appliance in anomaly database
    assert len(appliance) > 1
    day_start = test_data.first_valid_index()
    day_end = test_data.last_valid_index()
    gt, ob = ads.tidy_gt_and_ob(house_no, appliance, day_start, day_end, result_sub)
    #confusion_matrix(gt.day.values,ob.day.values)
    precision,recall, fscore = ads.compute_AD_confusion_metrics(gt, ob)
    #print(precision,recall, fscore)  
    if log_report:
      resultfile = open(logging_file,'a')
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
    assert len(appliance) > 1
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
#%%    
def dump_AD_result(logging_file, train_data,data_sampling_type,data_sampling_time, NoOfContexts,myapp,test_data,data_dic,disagg_approach,home,file_location,alpha,num_std):
    
    train_results = ads.AD_refit_training(train_data,data_sampling_type,data_sampling_time, NoOfContexts,myapp)
    test_results  = ads.AD_refit_testing(test_data,data_sampling_type,data_sampling_time, NoOfContexts,myapp)            
    if myapp == 'ElectricHeater':
        res_df = ads.anomaly_detection_algorithm_ElectricHeater(test_results,train_results,alpha,num_std)
    else:
        res_df = ads.anomaly_detection_algorithm(test_results,train_results,alpha,num_std)
    #result_sub = res_df[res_df.status==1]
    result_sub = res_df
    
    house_no =  int(re.findall('\d+',home)[0])
    home = home.split('.')[0]+'.csv'
    appliance = scn.reverse_lookup(home,myapp) # find actual name of appliance in anomaly database
    assert len(appliance) > 1
    day_start = test_data.first_valid_index()
    day_end = test_data.last_valid_index()
    gt,ob = ads.tidy_gt_and_ob(house_no, appliance, day_start ,day_end, result_sub)
    #confusion_matrix(gt.day.values,ob.day.values)
    #precision,recall, fscore = ads.compute_AD_confusion_metrics(gt,ob)
    result_dic ={}
    result_dic['gt'] = gt
    result_dic['ob'] = ob
    savefile = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/Intermediary_results/AD_noisy/"
    handle = open(savefile + disagg_approach + "/" +  home.split('.')[0]+'.pkl','wb')
    pickle.dump(result_dic,handle)
    handle.close()
    
    resultfile = open(logging_file,'a')
    tp, fp, fn =  ads.compute_tp_fp_fn(gt,ob)
    resultfile.write('\n{},{},{},{},{},{}'.format(home.split('.')[0], myapp, disagg_approach, tp, fp, fn))
    resultfile.close()    
#%%
    
def format_results_in_appliance_order(home):
     ''' this function returns applainces in intended order'''
     if home  == "House20.pkl":
         order = ['Dishwasher', 'TV', 'Kettle', 'Fridge', 'Freezer', 'TumbleDryer']
     elif home == "House10.pkl": 
         order = ['Dishwasher', 'TV', 'toaster', 'WashingMachine', 'Chest_Freezer', 'blender'] 
     elif home == "House18.pkl":
         order = ['Dishwasher', 'TV', 'Freezer_garage', 'Computer', 'Fridge_Freezer', 'Fridge_garage']
     elif home == "House16.pkl":    
         order = ['Dishwasher', 'Computer', 'TV', 'Fridge_Freezer_2', 'Fridge_Freezer_1', 'Dehumidifier']
     elif home == "House1.pkl":    
         order = ['Dishwasher', 'WashingMachine', 'Fridge', 'Freezer_1', 'ElectricHeater', 'Freezer_2']
     else :
         raise ValueError ("Supply correct home details")
     return order
#%%
def  interpolate_dataframe(start_ob, end_ob, temp_dup):
   ''' This function creates a new dataframe from temp_dup by using only two observation from it sepecified by parameters start_ob and end_ob. Remaining in between observations are filled by interpolation '''
   ind = pd.date_range(start = start_ob, end = end_ob, freq = 'T')
   temp_df =  pd.DataFrame(index = ind)
   k = pd.concat([temp_dup.loc[str(start_ob)], temp_dup.loc[str(end_ob)]],axis = 1).T
   k = k.combine_first(temp_df)
   k['power'].interpolate(method = 'linear',inplace = True)
   temp_dup.loc[k.index.intersection(temp_dup.index)] = k
   return temp_dup
#%%
def smoothen_NILM_output(data_series, threshold_minutes, std, num_std):    
  '''this function taken NILM output and removes small OFF durations by using threshold_minutes''' 

  threshold_minutes = threshold_minutes - num_std * std
  temp = data_series.to_frame()
  # less than 10, I consider as OFF, this can be done with clustering too
  status = [0 if i < 10 else 1 for i in temp.values]
  temp['status'] = status
  temp_groups = temp.groupby('status')
  try:   
    tgt_gp = temp_groups.get_group(1)
  except: # when all entries with status 0
    temp_dup = deepcopy(temp)
    temp_dup.columns = ['power','status']
    return temp_dup['power']
  temp_dup = deepcopy(temp)
  temp_dup.columns = ['power','status']
  #temp_dup['power'].plot()
  #%
  for i in range(tgt_gp.shape[0]):
    j = i + 1
    if j >= tgt_gp.shape[0]:
      #print ('Loop limit reached\n')
      break
    start_ind = tgt_gp.index[i]
    next_ind = tgt_gp.index[j]
    delta = next_ind - start_ind
    delta_minutes = (delta.seconds / 60)
    #print (delta_minutes)
    if delta_minutes <= 1:
      pass
    elif delta_minutes < threshold_minutes:
      # interpolate me at minutes rate
      temp_dup = interpolate_dataframe(start_ind, next_ind, temp_dup)
    else:
      pass
  # temp_dup['power'].plot() 
  return temp_dup['power']
#%%
def compute_AD_and_disagg_status_on_NILM_smoothened_data(logging_file,log_report, train_results, data_sampling_type,data_sampling_time, NoOfContexts,myapp,test_data,data_dic,disagg_approach,home,file_location,alpha,num_std):
    ''' this is replica of compute_AD_and_disagg_status. It differs in few parameters. It is used in one of specific cases when NILM smoothened data is used '''
    if log_report:
      resultfile = open(logging_file,'a')
      resultfile.write('*********************NEW HOME*****************\n')    
    #train_results = ads.AD_refit_training(train_data,data_sampling_type,data_sampling_time, NoOfContexts,myapp)
    test_results  = ads.AD_refit_testing(test_data,data_sampling_type,data_sampling_time, NoOfContexts,myapp)            
    #%
    if myapp == 'ElectricHeater':
        res_df = ads.anomaly_detection_algorithm_ElectricHeater(test_results,train_results,alpha,num_std)
    else:
        res_df = ads.anomaly_detection_algorithm(test_results,train_results,alpha,num_std)
    #result_sub = res_df[res_df.status==1]
    #result_sub = res_df
    # Compute disaggregation accuracies
    norm_error = acmat.accuracy_metric_norm_error(data_dic)
    order = format_results_in_appliance_order(home)
    norm_error = norm_error.reindex(order)
    # compute rmse too
    rmse = acmat.compute_rmse_ver_dict(data_dic)
    rmse = rmse.reindex(order)
    cor_coeff = acmat.compute_correlation_ver_dict(data_dic)
    cor_coeff = cor_coeff.reindex(order)
    confus_mat = acmat.call_confusion_metrics_on_disagg(data_dic['actual_power'],data_dic['decoded_power'],power_threshold=10)
    confus_mat = pd.DataFrame.from_dict(confus_mat)
    confus_mat = confus_mat.reindex(order, axis = 1)
    
    if log_report:
      resultfile.write('Following four disaggagregation metrics of {} approach \n'.format(disagg_approach))
      resultfile.write("\n ANE is:\n")
      resultfile.write(str(norm_error))
      resultfile.write("\n RMSE is:\n")
      resultfile.write(str(rmse))
      resultfile.write("\n CORRELATION COEFFICIENT is:\n")
      resultfile.write(str(cor_coeff))
      resultfile.write("\n CONFUSION MAT is:\n")
      resultfile.write(str(confus_mat))
      resultfile.write('\n')
      resultfile.close()
    else:
      print('Appliance normalization error are \n')
      print(norm_error)
      print('RMSE is:\n')
      print(rmse)
      print('correlation values are:\n')
      print(cor_coeff) 
      print('Confusion matrix accuracies are:\n')
      print(confus_mat)
    #%
    # Compute anomaly detection accuracies
    try:     
        result_sub = res_df[res_df.anomtype == "long"]
        print ("KEEPING LONG ANOMALIES, DROPPING FREQUENT ONES")
    except:
        result_sub = pd.DataFrame()
        print("No long anomaly found in this case\n")
    house_no =  int(re.findall('\d+',home)[0])
    home = home.split('.')[0]+'.csv'
    appliance = scn.reverse_lookup(home,myapp) # find actual name of appliance in anomaly database
    assert len(appliance) > 1
    day_start = test_data.first_valid_index()
    day_end = test_data.last_valid_index()
    gt, ob = ads.tidy_gt_and_ob(house_no, appliance, day_start, day_end, result_sub)
    #confusion_matrix(gt.day.values,ob.day.values)
    precision,recall, fscore = ads.compute_AD_confusion_metrics(gt, ob)
    #print(precision,recall, fscore)  
    if log_report:
      resultfile = open(logging_file,'a')
      resultfile.write("Anomaly detection accuracies at; context {}, alpha {}, std {} on {} data \n".format(NoOfContexts,alpha,num_std,disagg_approach))
      resultfile.write('Precision, reall and f_score are: {}, {}, {} \n'.format(precision,recall, fscore))
      resultfile.close()
    else:
      print("Anomaly detection accuracies at; context {}, alpha {}, std {} on {} data \n".format(NoOfContexts,alpha,num_std,disagg_approach))
      print('Precision, reall and f_score are: {}, {}, {} \n'.format(precision,recall, fscore))
#%%

def divide_smoothen_combine(data_series, NoOfContexts, train_results, num_std):
  ''' this function takes NILM data as input and then smoothens that data. Note down smoothening is done context wise so context specific thresholds are used''' 
  contexts = ads.create_contexts(data_series, NoOfContexts)      
  contexts_daywise = OrderedDict()
  for k, v in contexts.items():
    gp = v.groupby(v.index.date) 
    # get context specific stats
    off_mean_duration = train_results[k]['OFF_duration']['mean']
    off_std_duration = train_results[k]['OFF_duration']['std']
    threshold_minutes = off_mean_duration
    std = off_std_duration 
    smoothened_daywise = OrderedDict()
    for day_k, day_v in gp:
      #print(day_k)
      smoothened_daywise[day_k] = smoothen_NILM_output(day_v, threshold_minutes, std, num_std)
   # Now merge all daywise results
    contexts_daywise[k] = pd.concat([v for k,v in smoothened_daywise.items()], axis = 0) 
  smoothened_series = pd.concat([v for k,v in contexts_daywise.items()], axis = 0)  
  sorted_series =  smoothened_series.sort_index()
  return sorted_series
    
    
    
