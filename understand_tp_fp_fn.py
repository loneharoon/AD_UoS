#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
In this I understand the signatures of FP, TP and FN.
Created on Tue Mar 20 09:37:59 2018

@author: haroonr
"""

import pickle
import pandas as pd
import numpy as np
import sys,os
sys.path.append('/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/disaggregation_codes/')
import standardize_column_names as scn
import AD_support as ads
import re
import my_utilities as myutil
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

technique = "fhmm"
method = technique + "/selected/"
#method="lbm/selected_results/"

filename = file_location + method + home
results = open(filename, 'rb')
data_dic = pickle.load(results)
train_power =   data_dic['train_power']
decoded_power = data_dic['decoded_power']
actual_power  = data_dic['actual_power']
#TODO : SETME
train_data =  train_power[myapp]
test_data =   decoded_power[myapp]
actual_data = actual_power[myapp]
#test_data =   decoded_power[myapp][:'2014-10-24'] # house10
#%%
contexts = 4
data_sampling_time = 1 #in minutes
data_sampling_type = "minutes" # or seconds
alpha,num_std = 2, 2
train_results = ads.AD_refit_training(train_data, data_sampling_type, data_sampling_time, contexts, myapp)
test_results  = ads.AD_refit_testing(test_data, data_sampling_type, data_sampling_time, contexts, myapp)     
res_df = ads.anomaly_detection_algorithm(test_results,train_results,alpha,num_std)
result_sub = res_df
house_no =  int(re.findall('\d+',home)[0])
home = home.split('.')[0]+'.csv'
appliance = scn.reverse_lookup(home,myapp) # find actual name of appliance in anomaly database
assert len(appliance) > 1
day_start = test_data.first_valid_index()
day_end = test_data.last_valid_index()
#print('both S and NS anomalies selected')
#%%
gt,ob = ads.tidy_gt_and_ob(house_no,appliance,day_start,day_end,result_sub)
precision,recall, fscore = ads.compute_AD_confusion_metrics(gt,ob)
tp, fp, fn, tp_list, fp_list, fn_list = ads.show_tp_fp_fn_dates(gt,ob)
#%%
plt.ioff()
for i in range(len(fp_list)): 
    fpdate = str(fp_list[i])
    df = pd.concat([actual_data[fpdate],test_data[fpdate]],axis = 1)
    restype = 'fn'
    df.columns = ['submetered',technique]
    ax = df.plot(title = home.split('.')[0] + "-" + myapp + "-" + restype, figsize = (12,3))
    fig = ax.get_figure()
    savedir = "/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/intresting_plots/"
    savedir = savedir + restype + "/"
    fig.savefig(savedir + fpdate + ".pdf", bbox_inches='tight') 
#%%
rootdir = "/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/intresting_plots/fp/"
file_list = [rootdir + i for i in os.listdir(rootdir) if i.endswith(".pdf")]
saveresult = "/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/intresting_plots/fp.pdf"
myutil.create_pdf_from_pdf_list(file_list, saveresult)

