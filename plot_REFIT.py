#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is a simpler version of plot_REFIT_ALL.py. It allows to plot data of single 
home and is bit interactive
Created on Tue Nov 21 14:35:12 2017

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
dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/CLEAN_REFIT_081116/"
home = "House21.csv"
#savedir = "/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStrat/temp_plots/"
df = pd.read_csv(dir+home,index_col="Time")
df.index = pd.to_datetime(df.index)
#%% ALl appliances single day plot
df['2014-03-27'].plot(subplots=True)
#%% SELECTED appliances single day plot
df['2014-06-13'][['Aggregate','Fridge-Freezer']].plot(subplots=True)
#%% SINGLE appliance single DAY PLOT
daydat = df['2015-02-13']['Fridge-Freezer']
daydat.plot() 

#%% prepare data for facet plotting
temp2 = df['Freezer_1']
temp2 = temp2.to_frame()
temp2['day'] = temp2.index.date
temp2['timestamp'] = temp2.index.hour * 60 + temp2.index.minute
# VERIFY COLUMN NAMES
temp2  =  temp2.rename(columns={'Freezer_1' : 'power'})
grouped_1 = temp2.groupby([temp2.index.year,temp2.index.month])
#%%
with PdfPages('demo_haroon.pdf') as pdf:
  for i,group in grouped_1:
    plt.figure()
    print(group)
    ob = plot_facet_plots(group)
    pdf.savefig(ob)
#%% UNDERSTAND LOW DIMENSIONAL DATA ALSO
low_dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/CLEAN_REFIT_10min/"
low_home = "House1.csv"
#savedir = "/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStrat/temp_plots/"
lowdf = pd.read_csv(low_dir+low_home,index_col="Time")
lowdf.index = pd.to_datetime(lowdf.index)
#%% ALl appliances single day plot
lowdf['2014-03-26'].plot(subplots=True)
#%% SELECTED appliances single day plot
lowdf['2014-07-07'][['Aggregate','Freezer_1']].plot(subplots=True)
#%% SINGLE appliance single DAY PLOT
daydatlow = lowdf['2014-07-07']['Freezer_1']
daydatlow.plot() 