# FOR sshmss results, run this in python 3 and for remaining run it in python 2. This is due to the difference of pickle versions
#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
It reads disaggregation results and the ground truth first and then runs anomaly detection algorithm
Created on Fri Feb  9 09:27:42 2018

@author: haroonr
"""
#%%
''' Running instructions:
    1. For each home, first obtain results with FHMM, next CO and immediately with submetered, that is last cell of this file. Remember sumbetered data should be executed immediately after CO, becaue in denoised case, I forgot to add 'aggregate' column to decoded_results. 
    2. Read TODO lines carefully before running the code. These define parameter settings
    3. LBM can be Run too whenever you need'''

#%%
import pickle
import sys
sys.path.append('/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/disaggregation_codes/')
import AD_support as ads
import pipeline_support as ps
#%% 
file_location = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/Intermediary_results/"
#TODO : TUNE ME
log_report = False # this logs final reports, log only if you are sure of algorithm
ad_logging = True # this logs intemediary ad results 
if log_report:
    #TODO : TUNE ME
  logging_file = file_location+"noisy_resultfile.csv" # denoisy_resultfile.csv
  resultfile = open(logging_file,'a')
else:
  logging_file = ""

#TODO : TUNE  US [we are 5]
home = "House10.pkl" # options are: 10,20,18,16,1
disagg_approach = "sshmms" # options are co,fhmm, lbm,sshmms,gsp

NoOfContexts = 4
alpha = 2
num_std = 2
myapp = ads.get_selected_home_appliance(home)


#TODO : TUNE ME % path for reading pickle files
method = "noisy/"+ disagg_approach+ "/selected/" # noisy or denoised
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
#%% RUN THIS CELL ONLY WHEN DUMPING SUMBETERED RESULTS
test_data =  actual_power[myapp]
disagg_approach = "submetered" # options are co,fhmm, lbm,sshmms,gsp

#%%
#test_data =   decoded_power[myapp][:'2014-10-24'] # house10
data_sampling_time = 1 #in minutes
data_sampling_type = "minutes" # or seconds

#ps.compute_AD_and_disagg_status(logging_file,log_report,train_data,data_sampling_type,data_sampling_time, NoOfContexts,myapp,test_data,data_dic,disagg_approach,home,file_location,alpha,num_std)
# if we want to log intermediary anomaly detection results.
if ad_logging:
    #TODO: check me
    ad_logging_file = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/Intermediary_results/AD_noisy/ad_confusion_metrics.csv"
ps.dump_AD_result(ad_logging_file, train_data,data_sampling_type,data_sampling_time, NoOfContexts,myapp,test_data,data_dic,disagg_approach,home,file_location,alpha,num_std)

#%% for SUBMETERED DATA CASE 
#actual_signature =   actual_power[myapp]
disagg_approach = "SUBMETERED"
ps.compute_AD_status_only(logging_file,train_data,data_sampling_type,data_sampling_time, NoOfContexts,myapp,actual_power[myapp],data_dic,disagg_approach,home,file_location,alpha,num_std,actual_power)



#%%
