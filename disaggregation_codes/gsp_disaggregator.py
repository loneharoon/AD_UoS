#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
In this I implement Bochao's GSP disaggregation method
Created on Thu Feb  1 15:42:41 2018

@author: haroonr
"""
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import sys
sys.path.append('/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/disaggregation_codes/')
import accuracy_metrics_disagg as acmat
import matplotlib.pyplot as plt
#%%
dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/CLEAN_REFIT_081116/"
home = "House1.csv"
df = pd.read_csv(dir+home,index_col="Time")
df.index = pd.to_datetime(df.index)
df_sub = df["2014-03-01":'2014-04-30'] # since before march their are calibration issues
#%% Resampling data
print("*****RESAMPLING********")
df_samp = df_sub.resample('1T',label='right',closed='right').mean()
data_sampling_time = 1 #in minutes
data_sampling_type = "minutes" # or seconds
df_samp.drop('Issues',axis=1,inplace=True)
df_samp.rename(columns={'Aggregate':'use'},inplace=True) # renaming agg column
#%%
data_vec = df_samp['use'].values.tolist()
delta_p = [round(data_vec[i+1]-data_vec[i],2) for i in range(0,len(data_vec)-1)]
T = 80;
sigma = 15;
ri = 0.05;
events = [i for i in range(0, len(delta_p)) if(delta_p[i] > T or delta_p[i] < -T)]
T_Positive = 40;
T_Negative = -40;
event =  [i for i in range(0, len(delta_p)) if delta_p[i] > T_Positive or delta_p[i] < T_Negative ]
clusters = []

pp = list(set(event)-set(clusters)) 
#TODO pending wrong
#%%
# inputs event, delta_p,sigma
gspclustering(event,delta_p,sigma)
  #%%

#%%
