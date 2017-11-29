#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
I use this script to get the appliance frequency usage over the month and then subplots/facets of different
months over the years. I can use the same logic to get rose_plots
Created on Fri Nov 24 13:47:03 2017
@author: haroonr
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
#%%
dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/dataset_10mins/"
home = "House21.csv"
savedir = "/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStrat/temp_plots/"
exec(open("/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/support_functions.py").read())
df = pd.read_csv(dir+home,index_col="localminute")
df.drop(df.columns[[0]], axis=1, inplace=True) #drop row no. column
df.index = pd.to_datetime(df.index)
appliances = df.columns
appliances = appliances[1:appliances.size] # dropping agg column

for app in appliances:
  #appliance = 'Computer'
  appliance = app
  savedir = "/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/plots/"
  pdf_file_name = os.path.join(savedir, home.split(".")[0], "Fr_" + appliance + ".pdf")
  #temp = df['2014-1-1':'2014-12-30'][appliance]
  temp = df[appliance]
  temp = temp.to_frame()
  comb_month_res =  []
  month_gp =  temp.groupby([temp.index.year,temp.index.month])
  for ind, month_data in month_gp:
    temp_gp = month_data.groupby(month_data.index.day)
    threshold_watts = 25
    day_list = []
    for i, group in temp_gp:
      hour_gp = group.groupby(group.index.hour)
      hour_dict = {}
      for j,group2 in hour_gp:
        val =  1 if any(group2.values > threshold_watts) else 0
        hour_dict[group2.index.hour[0]] = val
      day_list.append(hour_dict)
    month_res =  pd.DataFrame.from_dict(day_list).T
    usage_frequency = month_res.sum(axis=1)
    usage_frequency = usage_frequency.to_frame()
    time_col = str(month_data.index.year[1]) + "-" + str(month_data.index.month[1])
    usage_frequency["month"] = [time_col] * usage_frequency.shape[0]
    usage_frequency["hour"] = usage_frequency.index
    usage_frequency.rename(columns={0:'Frequency'},inplace= True)
    comb_month_res.append(usage_frequency)
  result = pd.concat(comb_month_res)
  #result.rename(columns={0:'Frequency'},inplace= True)
  plot_facet_plots_years(result,pdf_file_name) 
