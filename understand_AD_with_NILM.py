#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
In this I understand, how different NILM approaches reproduce anomaly signatures
Created on Mon Feb 26 09:06:15 2018

@author: haroonr
"""

#%%
sys.path.append('/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/disaggregation_codes/')
import standardize_column_names as scn
import AD_support as ads
import re,pickle
import accuracy_metrics_disagg as acmat
import matplotlib.pyplot as plt
from copy import deepcopy
import pipeline_support as ps
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style="ticks",color_codes=True)
from matplotlib.backends.backend_pdf import PdfPages
#%%  Here I read NILM data of all aproaches only 
file_location = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/Intermediary_results/"
#TODO : TUNE ME
home = "House18.pkl" # options are: 10,20,18,16,1
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
        result_dic['submetered']  = data_dic['actual_power']
    
#%%
#mydates = ["2015-01-01", "2015-02-01"]
mydates = ads.find_my_anomalous_dates_from_gt(home)
subset_dic = {}
for key,value in result_dic.items():
    temp = value
    data = []
    for day in mydates:
        data.append(temp[day])
    Fdata = pd.concat(data,axis=0)
    subset_dic[key] = Fdata
#%% Select only TARGET APPLAINCE AMONG ALL APPLIANCES and create dataframe
myapp = ads.get_selected_home_appliance(home)
appliance_data = {}
for key,value in subset_dic.items():
    temp = value[myapp]
    appliance_data[key]= temp
res = pd.concat(appliance_data,axis=1)

#%%

#%%
res_grouped= res.groupby(res.index.date)
axis_counter = 0
pdf_file_path= "/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/anomalous_days/"
pdf_file_name= pdf_file_path + home.split('.')[0] + "_" + myapp +".pdf"
with PdfPages(pdf_file_name) as pdfhandle:
    for k,v in res_grouped:
        plt.figure(figsize=(8,4))
        v.plot(subplots=True,title=k)
        #plt.xaxis.set_major_locator(hours)
        #plt.xaxis.set_major_formatter(dfmt)
        plt.xlabel('Time (H)')
        plt.ylabel('Watts')
        pdfhandle.savefig()
        plt.close()
        #axis_counter+=1
#%%
ncols=3
res_grouped= res.groupby(res.index.date)
fig,axes = plt.subplots(nrows = int(np.ceil(len(res_grouped.size())/ncols)), ncols=ncols,figsize=(12,14))
#axes= axes.flatten()
hours = dates.HourLocator(interval=4)
dfmt =  dates.DateFormatter('%H')
axis_counter = 0
for k,v in res_grouped:
    v.plot(subplots=True,ax=axes[axis_counter],title=k)
    axes[axis_counter].xaxis.set_major_locator(hours)
    axes[axis_counter].xaxis.set_major_formatter(dfmt)
    axes[axis_counter].set_xlabel('Time (H)')
    #axes[axis_counter].set_ylabel('Watts')
    axis_counter+=1
#plt.savefig('haro.pdf', format='pdf')  