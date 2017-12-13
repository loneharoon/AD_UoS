#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This differs from plot_REFIT.py becuase here I repeat the same procedure for all
houses. It automates all file reading and saving results appropriately.
CTM: data sampling rate, several lines are directly affected
Created on Wed Nov 22 11:30:37 2017
@author: haroonr
"""

#%%
%matplotlib inline
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import os
plt.ioff()
#%%
direc = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/CLEAN_REFIT_10min/"
#dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/REFIT_RAW/"
savedir_home = "/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/plots/"
exec(open("/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/support_functions.py").read())
#total_homes = sorted(os.listdir(dir))
#%%
#for i in range(14,19):
#home = total_homes[i]
home = "House21.csv"
#df = pd.read_csv(dir+home,index_col="localminute")
df = pd.read_csv(direc+home,index_col="Time")
df.index = pd.to_datetime(df.index)
#df.drop(df.columns[[0]], axis=1, inplace=True) #drop row no. column
# this plof each appliance separtely in row fashion manner
req_folder = savedir_home + home.split(".")[0] + "/"
#req_folder = savedir_home + "Raw_home3" + "/"
if not os.path.exists(req_folder):
  os.makedirs(req_folder)
meters = df.columns
#%%
meters = ["Aggregate", "Fridge-Freezer", "TumbleDryer", "WashingMachine", "Dishwasher", "FoodMixer", "noname", "Vivarium", "PondPump"]
for i in range(0,len(meters)): # dropping issue column from plotting
  meter_name = meters[i]
  temp = df[meter_name]
  temp = temp.to_frame()
  temp['day'] = temp.index.date
  #CHECK IF DATA IS AT SECONDS OR AT MINUTES LEVEL
  #temp['timestamp'] = temp.index.hour * 60 + temp.index.minute +  temp.index.second/60 
  temp['timestamp'] = temp.index.hour * 60 + temp.index.minute
  temp  =  temp.rename(columns={meter_name : 'power'})
  grouped_1 = temp.groupby([temp.index.year,temp.index.month])
  pdf_file_name = req_folder + meter_name + ".pdf"
  with PdfPages(pdf_file_name) as pdf:
    for i, group in grouped_1:
      ob = plot_facet_plots(group)
      pdf.savefig(ob)
