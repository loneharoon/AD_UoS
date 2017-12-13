#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This scipt process raw REFIT data. It does followig:
  1. Merges two raw files of each home
  2. Re names columns and saves this file in sep. folder
  3. It downsamples to 10 minutes data and saves this sep folder
  4. Creates/saves Facet plots for each appliace in sep folder
The last block of the code takes clean data as input and does following
  1. Drops unix column
  2. Renames columns with appliance names
  3. saves file
  
Created on Wed Dec  6 11:14:56 2017

@author: haroonr
"""

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import os,re,glob

#%%
raw_dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/REFIT_RAW_081116/"
new_raw_dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/REFIT_RAW/"
new_raw_dir_10min = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/REFIT_RAW_10min/"
exec(open("/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/REFIT_column_names.py").read())
exec(open("/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/support_functions.py").read())
plot_folder = "/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/plot_raw/"
all_homes = os.listdir(raw_dir)
#%%
part1 = 'RAW_House_17_Part1.csv'
part2 = 'RAW_House_17_Part2.csv'
df1 = pd.read_csv(raw_dir+part1,index_col="Time")
df2 = pd.read_csv(raw_dir+part2,index_col="Time")
#%%
temp = pd.concat([df1,df2],axis=0) # concatenating dfs
temp.drop('Unix',axis=1,inplace=True)
house_no = [int(f) for f in re.findall('\d+', part1)][0] # extract house number
house_appliances =  home_app[house_no][1:] # extract appliances list
temp.columns = house_appliances # name columns
temp.to_csv(new_raw_dir+part1.split('_')[2]+".csv")
#% create/save downsampled version 
temp.index= pd.to_datetime(temp.index)
temp_sub = temp.resample('10T',label='right').mean()
temp_sub.to_csv(new_raw_dir_10min+part1.split('_')[2]+".csv")
#% plot each of raw meters
#meters= temp_sub.columns
#req_folder = plot_folder + part1.split("_")[1] + "/"
#if not os.path.exists(req_folder):
#  os.makedirs(req_folder)
#for i in range(0,meters.size): # dropping issue column from plotting
#  meter_name = meters[i]
#  temp2 = temp_sub[meter_name]
#  temp2 = temp2.to_frame()
#  temp2['day'] = temp2.index.date
#  #CHECK IF DATA IS AT SECONDS OR AT MINUTES LEVEL
#  #temp['timestamp'] = temp.index.hour * 60 + temp.index.minute +  temp.index.second/60 
#  temp2['timestamp'] = temp2.index.hour * 60 + temp2.index.minute
#  temp2  =  temp2.rename(columns={meter_name : 'power'})
#  grouped_1 = temp2.groupby([temp2.index.year,temp2.index.month])
#  pdf_file_name = req_folder + meter_name + ".pdf"
#  with PdfPages(pdf_file_name) as pdf:
#    for i, group in grouped_1:
#      ob = plot_facet_plots(group,color="r")
#      pdf.savefig(ob)

#%% FROM ONWWARDS THIS PLAYS WITH CLEAN DATA ONLY
data_dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/CLEAN_REFIT_081116/"
exec(open("/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/REFIT_column_names.py").read())
home_list = [os.path.basename(x) for x in glob.glob(data_dir+'*.csv')]
print (home_list)
#%%
for i in range(1,len(home_list)):
  home = home_list[i]
  home_df = pd.read_csv(data_dir+home,index_col="Time")
  home_df.drop('Unix',axis=1,inplace=True)
  house_no = [int(f) for f in re.findall('\d+', home)][0] # extract house number
  house_appliances =  home_app[house_no][1:] # extract appliances list
  house_appliances.append('Issues')
  home_df.columns = house_appliances # name columns
  os.remove(data_dir+home)
  home_df.to_csv(data_dir+home)
