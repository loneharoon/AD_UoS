#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Experiment to generate synthetic data and under working of Anomaly detection algo
Created on Mon Feb 19 09:15:53 2018

@author: haroonr
"""
from __future__ import division
from copy import deepcopy
import pandas as pd
import numpy as np
import sys
sys.path.append('/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/disaggregation_codes/')
import AD_support as ads

import accuracy_metrics_disagg as acmat
import matplotlib.pyplot as plt

#%%
df = generate_pandasseries(timestart = '2011-06-01 0:00:00', hours = 24*8,  upper_mag   = 1000, frequency = 2., dutycycle = 0.5,sampling_type='minutes')
train_data = df[:'2011-06-03']
test_data = df['2011-06-04':]
#df.plot()
#%%
anom_signature = {
        0: generate_pandasseries(timestart = '2011-06-04 07:00:00', hours = 3,  upper_mag   = 1000, frequency = 2., dutycycle = 0.9,sampling_type='minutes'),  
        1: generate_pandasseries(timestart = '2011-06-05 07:00:00', hours = 4,  upper_mag   = 1000, frequency = 2., dutycycle = 0.9,sampling_type='minutes'),
        2: generate_pandasseries(timestart = '2011-06-07 07:00:00', hours = 5,  upper_mag   = 1000, frequency = 2., dutycycle = 0.9,sampling_type='minutes'),
        3: generate_pandasseries(timestart = '2011-06-08 07:00:00', hours = 6,  upper_mag   = 1000, frequency = 2., dutycycle = 0.9,sampling_type='minutes')
                  }
#%% # insert anomaly
for key,item in anom_signature.items():
   test_data = insert_anomaly_in_pandaseries(test_data,item)
#%%
 train_data['2011-06-01 06:00':'2011-06-01 12:00'].plot()
 test_data['2011-06-04 06:00':'2011-06-04 12:00'].plot()
#%%
#pp = test_data['2011-06-04 07:00':'2011-06-04 10:00']
pp = test_data['2011-06-04']
results  = ads.AD_refit_testing(pp,data_sampling_type,data_sampling_time)
#pp.plot()
results['2011-06-04']['day_1_gp']['ON_energy']
#%%
data_sampling_time = 1 #in minutes
data_sampling_type = "minutes" # or seconds
#test_data =  df_samp[myapp]['2014-05-01':'2014-05-31'] # home 3
train_results = ads.AD_refit_training(train_data,data_sampling_type,data_sampling_time, NoOfContexts=8)
#%%
test_results  = ads.AD_refit_testing(test_data, data_sampling_type,data_sampling_time,NoOfContexts=8)            
train_results['day_1_gp']['ON_energy']
print('\n')
test_results['2011-06-04']['day_1_gp']['ON_energy']
test_results['2011-06-05']['day_1_gp']['ON_energy']
#%%
alpha = 1
num_std = 2
res_df = ads.anomaly_detection_algorithm(test_results,train_results,alpha,num_std)
#result_sub = res_df[res_df.status==1]
print(res_df)
#%%
def generate_pandasseries(timestart,hours, upper_mag=10, frequency = 1, dutycycle = 0.5, sampling_type = 'minutes'):
    """ """
    from scipy import signal
    import random as rnd
    if sampling_type =="seconds":   
        t = np.linspace(0, hours, 60*60*hours, endpoint=False)# generate time sequence
        sig = signal.square(2 * np.pi *frequency* t,duty=dutycycle)
        sig2 = [round(rnd.gauss(upper_mag,1),2) if a==1 else 0 for a in sig]
        ind = pd.date_range(timestart, periods=len(sig2),freq='S')
    elif sampling_type == "minutes":
        t = np.linspace(0, hours, 60*hours, endpoint=False)# generate time sequence
        sig = signal.square(2 * np.pi *frequency* t,duty=dutycycle)
        sig2 = [round(rnd.gauss(upper_mag,1),2) if a==1 else 0 for a in sig]
        ind = pd.date_range(timestart, periods=len(sig2),freq='T')
    pdseries = pd.Series(data=sig2,index=ind)
    return(pdseries)
#%%
def insert_anomaly_in_pandaseries(test_dset,anomaly):
    data = deepcopy(test_dset)
    for key,value in anomaly.iteritems():
        #print(value.values)
        data[key] = value
    return data