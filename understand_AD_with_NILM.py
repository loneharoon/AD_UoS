#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
In this I understand, how different NILM approaches reproduce anomaly signatures
Created on Mon Feb 26 09:06:15 2018

@author: haroonr
"""

#%%
from __future__ import division
import sys
sys.path.append('/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/disaggregation_codes/')
import AD_support as ads
import pickle
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style="ticks",color_codes=True)
from matplotlib.backends.backend_pdf import PdfPages
#%%  Here I read NILM data of all aproaches only  and submetered data too for a single home
file_location = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/Intermediary_results/"
#TODO : TUNE ME
home = "House1.pkl" # options are: 10,20,18,16,1
approaches = ['co','fhmm','lbm']
result_dic = {}
for approach in approaches:
    #disagg_approach = approach
    method = "noisy/"+ approach+ "/selected/" # noisy or denoised
    filename = file_location + method + home
    results = open(filename, 'rb')
    data_dic = pickle.load(results)
    results.close()
    result_dic[approach] = data_dic['decoded_power']
    if approach == "co": # get submetered data too
        result_dic['submetered']   =  data_dic['actual_power']
    
#%% Keep only those days from read data on which anomaly happened
#mydates = ["2015-01-01", "2015-02-01"]
mydates = ads.find_my_anomalous_dates_from_gt(home) # find anomalous days of a home from gt
subset_dic = {} # subset after retainining only anomalous days
for key,value in result_dic.items():
    temp = value
    data = []
    for day in mydates:
        data.append(temp[day])
    Fdata = pd.concat(data,axis=0)
    subset_dic[key] = Fdata
#% Select only TARGET APPLAINCE AMONG ALL APPLIANCES and create dataframe
myapp = ads.get_selected_home_appliance(home) # find anomal appliance of target home
appliance_data = {} # keep only data of anomalous apliance
for key,value in subset_dic.items():
    temp = value[myapp]
    appliance_data[key]= temp
res = pd.concat(appliance_data,axis=1)
submetered_data = subset_dic['submetered']
submetered_data.rename(columns={'use':'Aggregate'},inplace=True)

#%
res_grouped= res.groupby(res.index.date)
gt_grouped = submetered_data.groupby(submetered_data.index.date)

#%%
res_grouped= res.groupby(res.index.date)
gt_grouped = submetered_data.groupby(submetered_data.index.date)
axis_counter = 0
pdf_file_path= "/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/anomalous_days/"
pdf_file_name= pdf_file_path + home.split('.')[0] + "_" + myapp +".pdf"

with PdfPages(pdf_file_name) as pdfhandle:
    for gp1,gp2 in zip(res_grouped,gt_grouped):
        key = gp1[0] # date
        nilm = gp1[1]
         # https://stackoverflow.com/q/49006699/3317829
        nilm['dummy_1'] = 10 # dummy data to makes dfs of equal number of columns
        nilm['dummy_2'] = 10
        nilm['dummy_3'] = 10
        metered = gp2[1]
        fig, axes = plt.subplots(nrows=7,ncols=2,figsize=(12,6),sharex=True)       
        metered.plot(ax = axes[:,0],subplots=True,title=key)
        nilm.plot(ax = axes[:,1],subplots=True,title=str(key) + "_"+myapp)
        #plt.xaxis.set_major_locator(hours)
        #plt.xaxis.set_major_formatter(dfmt)
        #plt.xlabel('Time (H)')
        #plt.ylabel('Watts')
        pdfhandle.savefig()
        plt.close()
#%%
#%%

       
