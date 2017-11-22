#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 14:35:12 2017

@author: haroonr
"""
%matplotlib inline
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style="ticks",color_codes=True)
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import inspect
#%%
dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/dataset_10mins/"
home = "House1.csv"
savedir = "/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStrat/temp_plots/"
df = pd.read_csv(dir+home,index_col="localminute")
#%%
# this plots data of each appliance separtely in row fashion manner
df = df/1000
#df.plot(subplots=True,figsize=(12,10))
#plt.savefig(savedir+"house1.pdf")
#plt.close()
#%%
df.index = pd.to_datetime(df.index)
temp = df['Aggregate']
temp = temp['2014-01-01': '2014-01-30']
temp = temp.to_frame()
temp['day']= temp.index.date
temp['timestamp'] = temp.index.time
#%%
#sns.set(style="ticks",color_codes=True)
#h =  sns.FacetGrid(temp,col='day',col_wrap=7,size=2.5)
#(h.map_dataframe(plt.plot,'timestamp','Aggregate')
#       .set_axis_labels("Timestamp","Power(kW)")
#       .fig.subplots_adjust(wspace=.2,hspace=.5))
#h.savefig("/Volumes/MacintoshHD2/Users/haroonr/Downloads/haroon_temp.pdf")
#%%
temp2 = df['Aggregate']
temp2 = temp2.to_frame()
temp2['day'] = temp2.index.date
temp2['timestamp'] = temp2.index.hour * 60 + temp2.index.minute
# VERIFY COLUMN NAMES
temp2  =  temp2.rename(columns={'Aggregate' : 'power'})
grouped_1 = temp2.groupby([temp2.index.year,temp2.index.month])
#%%
with PdfPages('demo_haroon.pdf') as pdf:
  for i,group in grouped_1:
    plt.figure()
    print(group)
    ob = plot_facet_plots(group)
    pdf.savefig(ob)
    
