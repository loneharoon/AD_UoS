#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
In this I see whether I can tune SSHMM output for anomaly detection.
Created on Tue Mar 27 10:16:41 2018
@author: haroonr
"""


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
actual_data = actual_power[myapp]
#%%
temp = test_data['2014-05-11'].to_frame()
status = [0 if i < 5 else 1 for i in temp.values]
temp['status'] = status
temp_groups = temp.groupby('status')
tgt_gp = temp_groups.get_group(1)
temp_dup = deepcopy(temp)
temp_dup.columns = ['power','status']

#%%
threshold_minutes = 10 # minutes
for i in range(tgt_gp.shape[0]):
  j = i + 1
  if j >= tgt_gp.shape[0]:
    print ('Loop limit reached\n')
    break
  start_ind = tgt_gp.index[i]
  #while True:
  next_ind = tgt_gp.index[j]
  delta = next_ind - start_ind
  delta_minutes = (delta.seconds / 60)
  print(delta_minutes)
  if delta_minutes <= 1:
    pass
  elif delta_minutes < threshold_minutes:
    # interpolate me at minutes rate
    print('interp')
    temp_dup = interpolate_dataframe(start_ind, next_ind, temp_dup)
  else:
    pass
      
    
      
#%%
def  interpolate_dataframe(start_ob, end_ob, temp_dup):
       ind = pd.date_range(start = start_ob, end = end_ob, freq = 'T')
       temp_df =  pd.DataFrame(index = ind)
       k = pd.concat([temp_dup.loc[str(start_ob)], temp_dup.loc[str(end_ob)]],axis = 1).T
       k = k.combine_first(temp_df)
       k['power'].interpolate(method = 'linear',inplace = True)
       temp_dup.loc[k.index.intersection(temp_dup.index)] = k
       return temp_dup
       
      
    
#%%

      
      