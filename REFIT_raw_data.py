#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script runs on RAW data. Please specify file name and column names correctly.
Created on Mon Dec  4 11:13:11 2017
@author: haroonr
"""
#%%
%matplotlib inline
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import os
raw_dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/REFIT_RAW/"
exec(open("/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/clean_REFIT_Default.py").read())

#%%
ghar = 'RAW_House_3_Part2.csv'
dr = pd.read_csv(raw_dir+ghar,index_col = "Time")
dr.index= pd.to_datetime(dr.index)
dr.drop('Unix', axis=1,inplace=True)
# Name columns while reading column headers from above exec file as
indx = int(ghar.split('_')[2])
names = home_app[indx][1:] # dropping localminute name
dr.columns= names

#%% ALl appliances single day plot
dr['2013-12-06'].plot(subplots=True)
#%% SELECTED appliances single day plot
dr['2013-12-06'][['Aggregate','Freezer']].plot(subplots=True)
#%% SINGLE appliance single DAY PLOT
daydat = dr['2013-12-06']['Freezer']
daydat.plot() 
