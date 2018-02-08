#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Since LBM was not working accurately on days data at once. So, I ran the code daywise and stored results. In this script, I will read those day wise results, combine them into one continous pandas dataframe and calculate accuracy results.
Created on Thu Jan  4 21:36:30 2018

@author: haroonr
"""
#%%
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
np.random.seed(42)
import os
import matplotlib.pyplot as plt
#%% this cell is execlusively for iawe dataset
import os
dir_path = "/Volumes/MacintoshHD2/Users/haroonr/Dropbox/nilmtk_work/inter_results/lbm_disaggregation_puredata/meter2_daywise/"
#dir_path = "/Volumes/MacintoshHD2/Users/haroonr/Downloads/meter2_three_iterations/"
fls = os.listdir(dir_path)
df = []
for i in range(0,len(fls)):
    df.append(pd.read_csv(dir_path+fls[i],index_col="localminute"))
    
infApplianceReading =  pd.concat(df,axis=0)

#%% this cell is execlusively for REDD DATASET
import os
dir_path = "/Volumes/MacintoshHD2/Users/haroonr/Dropbox/nilmtk_work/inter_results/lbm_disaggregation_puredata/redd_home6_daywise/"
fls = os.listdir(dir_path)
df = []
for i in range(0,len(fls)): # number 0 is some hidden file
    df.append(pd.read_csv(dir_path+fls[i],index_col="localminute"))
    
infApplianceReading =  pd.concat(df,axis=0)
infApplianceReading.index = pd.to_datetime(infApplianceReading.index)

#%%