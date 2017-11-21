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
import numpy as np

#%%
dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/dataset_10mins/"
home = "House1.csv"
savedir = "/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStrat/temp_plots/"
df = pd.read_csv(dir+home,index_col="localminute")
#%%
# this plots data of each appliance separtely in row fashion manner
df = df/1000
df.plot(subplots=True,figsize=(12,10))
#plt.savefig(savedir+"house1.pdf",bbox_inches="tight")
plt.savefig(savedir+"house1.pdf")
plt.close()
#%%
df.index = pd.to_datetime(df.index)
temp = df['Aggregate']
temp = temp['2014-01-01': '2014-01-30']
temp = temp.to_frame()
temp['day']= temp.index.date
temp['timestamp'] = temp.index.time
#%%
sns.set(style="ticks",color_codes=True)
h =  sns.FacetGrid(temp,col='day',col_wrap=7,size=2.5)
(h.map_dataframe(plt.plot,'timestamp','Aggregate')
.set_axis_labels("Timestamp","Power(kW)")
.fig.subplots_adjust(wspace=.2,hspace=.5))
#h.savefig("/Volumes/MacintoshHD2/Users/haroonr/Downloads/haroon_temp.pdf")
#%%
temp2 = df['Aggregate']['2013']
temp2 = temp2.to_frame()
temp2['date'] = temp2.index.date
grouped_1 = temp2.groupby(temp2.index.month)