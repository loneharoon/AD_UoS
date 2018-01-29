#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
In this script, I use all disaggregatin metrics to understand which will makes more sense to understand the 
disaggregation performance
Experiment:
    1. Get disagg data
    2. Find results for accuracy metrics using NILM and submetered data
    3. Plot both NILM and submeterd data to understand in better way
Created on Mon Jan 29 12:07:37 2018
@author: haroonr
"""

import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import sys
sys.path.append('/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/disaggregation_codes/')
import accuracy_metrics_disagg as acmat
import localize_fhmm,co
#%%
dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/Dataport/mix_homes/default3/"
#execfile("/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/disaggregation_codes/localize_fhmm.py")
#execfile("/Volumes/MacintoshHD2/Users/haroonr/Dropbox/nilmtk_work/plot_functions.py")
#execfile("/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/disaggregation_codes/cluster_file.py")
#execfile("/Volumes/MacintoshHD2/Users/haroonr/Dropbox/nilmtk_work/nilmtk_pycharm/utils.py")
#execfile("/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/disaggregation_codes/co.py")

hos = '1463.csv'
df = pd.read_csv(dir + hos, index_col='localminute')  # USE HOUSE (6,115)
df.index = pd.to_datetime(df.index)
df = df["2014-06-01":"2014-08-29 23:59:59"]
res = df.sum(axis=0)
high_energy_apps = res.nlargest(6).keys() # CONTROL : selects few appliances
df_new = df[high_energy_apps]
del df_new['use']# drop stale aggregate column
df_new['use'] = df_new.sum(axis=1) # create new aggregate column

train_dset = df_new.truncate(before="2014-06-01", after="2014-06-30 23:59:59")
test_dset = df_new.truncate(before="2014-07-01", after="2014-07-10 23:59:59")
#%%
fhmm_result  =  localize_fhmm.fhmm_decoding(train_dset,test_dset) # dissagreation
#co_result = co.co_decoding(train_dset,test_dset)

#%%
fhmm_rmse = acmat.compute_rmse(fhmm_result['actaul_power'],fhmm_result['decoded_power'])
print(fhmm_rmse)
aggregate = sum(test_dset['use'])
fhmm_kolter = acmat.diss_accu_metric_kolter_1(fhmm_result,aggregate)
print(fhmm_kolter)
fhmm_kolter = acmat.diss_accu_metric_kolter_exact(fhmm_result,aggregate)
print(fhmm_kolter)
norm_fhmm = acmat.accuracy_metric_norm_error(fhmm_result)
mae = acmat.compute_mae(fhmm_result['actaul_power'],fhmm_result['decoded_power'])
print(mae)
confusion_mat = call_confusion_metrics_on_disagg(fhmm_result['actaul_power'],fhmm_result['decoded_power'])
pd.DataFrame.from_dict(confusion_mat)
