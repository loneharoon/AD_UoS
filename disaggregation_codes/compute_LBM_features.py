#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
In this file, I see how to compute features of LBM disaggregation model
Created on Tue Dec 19 19:09:12 2017

@author: haroonr
"""
#%% 
import pandas as pd
import numpy as np
from copy import copy

#%%
dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/CLEAN_REFIT_081116/House1.csv"
df =  pd.read_csv(dir,index_col="Time")
df.index = pd.to_datetime(df.index)
df_2min = df.resample('2T',label="right").mean()

freezer_1 = copy(df.Freezer_1)
freezer_1_sub =  freezer_1['2013']
freezer_daywise = pd.groupby(freezer_1_sub,by=freezer_1_sub.index.date)
cycles = []
for day in freezer_daywise:
 # print(type(day))
  data = day[1] # day[1] is item and day[0] is key
  count = 0
  for i in range(1,data.shape[0]): 
    if data[i] > 10 and data[i-1] < 2:
      count = count +1
  cycles.append(count)
  


  
  