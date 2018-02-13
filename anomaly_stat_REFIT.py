#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file performs different stats on the anomalies collected from REFTI dataset
Created on Mon Dec 18 11:40:59 2017

@author: haroonr
"""
#%%
import numpy as np
import pandas as pd
from copy import deepcopy
from collections import Counter
#%%
loc = "/Volumes/MacintoshHD2/users/haroonr/Dropbox/UniOfStra/AD/"
fl = "anomaly_explanation.csv"
df = pd.read_csv(loc+fl)
#%%
# mapping for different appliance present in the sheet
re_map = {'ChestFreezer':'Freezer','Freezer_1':'Freezer','Freezer_2':'Freezer',
          'Freezer_garage': 'Freezer','Freezer_1':'Freezer','Fridge-Freezer_1':'Fridge-Freezer'\
          ,'Fridge-Freezer_2':'Fridge-Freezer','FridgeFreezer':'Fridge-Freezer','Firdge':'Fridge'\
          ,'Fridge_garag':'Fridge'}


def remap_appliances_ifrequired(df,re_map):
  ''' this renames appliance if it is named with some other name'''
  frame = df.copy()
  updated = []
  for i in frame.Appliance:
    if i in re_map:
      updated.append(re_map[i])
    else:
      updated.append(i)
  frame.Appliance = updated
  return(frame)
  
dfx = remap_appliances_ifrequired(df,re_map)
Counter(dfx.Appliance) # prints all anomalies
Counter(dfx[dfx.Status=='S'].Appliance) # prints only sure anomalies
 #%% Find home where specifid_appliance's anomaly occured more
 tg_appliance = "ElectricHeater"
 Counter(dfx[(dfx.Appliance == tg_appliance) & (dfx.Status=='S')].House_No )
 
OR
 
dfx[(dfx.Appliance == tg_appliance) & (dfx.Status=='S')].groupby('House_No').size()
dfx[(dfx.Appliance == tg_appliance) & (dfx.Status=='S')].groupby('House_No').size().sum()
 #%%
 #find dates of specific appliance anomalies
 
 app ="Freezer"
 home = 1
 dfx[(dfx.House_No ==home) &(dfx.Appliance == app) & (dfx.Status=='S') ]
 #%% FIRE QUERIES ON ORIGINAL DATAFRAME. WHOSE APPLAINCE NAMES ARE NOT MAPPED
 app ="ElectricHeater"
 home = 1
 df[(df.House_No ==home) &(df.Appliance == app) & (df.Status=='S') ]
