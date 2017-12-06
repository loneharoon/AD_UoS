#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script reads the high frequency dataset, Downsamples it, and renames columns
Created on Tue Dec  5 20:58:02 2017
@author: haroonr
"""
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import os,re

#%%

dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/CLEAN_REFIT_081116/"
new_dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/CLEAN_REFIT_10min/"
exec(open("/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/clean_REFIT_Default.py").read())
all_homes = os.listdir(dir)
#%% Read, Index and drop "Unix" timestamp
for i in all_homes:
  house = i
  df = pd.read_csv(dir+house,index_col="Time")
  df.index = pd.to_datetime(df.index)
  df.drop('Unix',inplace=True,axis=1)
  # Downsampling to 10 mins
  df_sample= df.resample('10T',label='right').mean()
  # column renaming
  house_no = [int(f) for f in re.findall('\d+',house)][0]
  app_names = home_app[house_no][1:]
  app_names.append('issue')
  df_sample.columns = app_names
  df_sample.to_csv(new_dir+house.split('_')[1])