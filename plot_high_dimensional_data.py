#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
In this script I play with high dimensional data only
Created on Thu Dec  7 17:31:54 2017

@author: haroonr
"""
%matplotlib auto
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style="ticks",color_codes=True)
from matplotlib.backends.backend_pdf import PdfPages
import inspect
#%%
dir_RAW = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/REFIT_RAW/"
home_RAW = "House17.csv"
df_RAW = pd.read_csv(dir_RAW+home_RAW,index_col="Time")
df_RAW.index = pd.to_datetime(df_RAW.index)
#%% ALl appliances single day plot
df_RAW['2014-06-22'].plot(subplots=True)
#%% SELECTED appliances single day plot
df_RAW['2015-04-22'][['Aggregate','Freezer']].plot(subplots=True)
#%% SINGLE appliance single DAY PLOT
daydat_RAW = df_RAW['2014-10-17']['Firdge']
daydat_RAW.plot() 