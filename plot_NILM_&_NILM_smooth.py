#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
In this I plot submetered, NILM and NILM smoothened version day wise for each NILM techn separ. It shows how smoothening effects NILM version
Created on Thu Mar 29 09:13:38 2018

@author: haroonr
"""

import pickle
import sys
sys.path.append('/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/disaggregation_codes/')
import AD_support as ads
import pandas as pd
import pipeline_support as ps
import matplotlib.pyplot as plt
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
NILM_smooth_version = True # if you want to read NILM smoothened dataset
home = "House10.pkl" # options are: 10, 20, 18, 16, 1
disagg_approach = "sshmms" # options are co,fhmm, lbm,sshmms,gsp
num_std_smooth = 0

NoOfContexts = 4
alpha = 2
num_std = 2
myapp = ads.get_selected_home_appliance(home)


#TODO : TUNE ME % path for reading pickle files
method_nilm = "noisy/" + disagg_approach + "/selected/" # noisy or denoised
filename =  file_location + method_nilm + home
results_nilm = open(filename, 'rb')
if sys.version_info > (3, 0):
  data_dic_nilm = pickle.load(results_nilm, encoding = 'latin1')
else:
  data_dic_nilm = pickle.load(results_nilm)
results_nilm.close()


method_nilm_smooth = 'nilm_smoothened/'+ disagg_approach + '/' + 'std' + str(num_std_smooth) + "/"
filename =  file_location + method_nilm_smooth + home
results_nilm_smooth = open(filename, 'rb')
if sys.version_info > (3, 0):
  data_dic_nilm_smooth = pickle.load(results_nilm_smooth, encoding = 'latin1')
else:
  data_dic_nilm_smooth = pickle.load(results_nilm_smooth)
results_nilm_smooth.close()

  
train_data_ns  =  data_dic_nilm_smooth['train_power'] 
test_data_ns   =  data_dic_nilm_smooth['decoded_power']
actual_data_ns =  data_dic_nilm_smooth['actual_power']

train_power =   data_dic_nilm['train_power']
decoded_power = data_dic_nilm['decoded_power']
actual_power  = data_dic_nilm['actual_power']
if disagg_approach == "lbm":
    data_dic_nilm['decoded_power'] = data_dic_nilm['decoded_power'].drop(['inferred mains'],axis=1)
train_data_n =  train_power[myapp]
test_data_n =   decoded_power[myapp]
#%% This cell is used to save a range of plots
days = np.unique(test_data_n.index.date)
days = [str(i) for i in days]
for i in days:
  gt = actual_data_ns[i]
  nilm = test_data_n[i]
  nilm_smooth =  test_data_ns[i]
  cat = pd.concat([gt, nilm, nilm_smooth],axis = 1)
  cat.columns = ['submetered', 'NILM', 'NILM_smooth']
  ax = cat.plot(subplots = True, figsize = (12,4))
  fig = ax[0].get_figure()
  savedir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/Intermediary_results/NILM_nilm_smooth_plots/"
  savedir = savedir + home.split('.')[0] + "/" + disagg_approach + "/"
  fig.savefig(savedir + i + ".png", bbox_inches='tight')
  plt.close()  
#%% This cell saves only one plot at a time
#i = '2014-05-21 : 2014-05-21 05:59:59'
gt = actual_data_ns['2014-05-21' : '2014-05-21 05:59:59']
nilm = test_data_n['2014-05-21' : '2014-05-21 05:59:59']
nilm_smooth =  test_data_ns['2014-05-21' : '2014-05-21 05:59:59']
cat = pd.concat([gt, nilm, nilm_smooth],axis = 1)
cat.columns = ['Submetered', 'NILM', 'NILM_Processed']
ax = cat.plot(subplots = True, figsize = (8,4))
fig = ax[0].get_figure()
plt.xlabel('Timestamp')
plt.ylabel('Power (W)')
savedir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/Intermediary_results/paper_plots/"

fig.savefig(savedir + home.split('.')[0] + disagg_approach + ".pdf", bbox_inches='tight')
plt.close()  
