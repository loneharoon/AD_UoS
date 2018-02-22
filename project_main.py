#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This in one of the main files. It calls different disaggregation approaches and saves the disagg (and gt too) results in a folder. Note it does not contain any AD logic
Created on Wed Feb  7 09:00:08 2018

@author: haroonr
"""
#%%
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import sys,pickle,time
sys.path.append('/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/disaggregation_codes/')
import accuracy_metrics_disagg as acmat
import localize_fhmm,co,standardize_column_names
import matplotlib.pyplot as plt
from copy import deepcopy
import AD_support as ads
from standardize_column_names import rename_appliances
import latent_Bayesian_melding as LBM
#%%
#dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/CLEAN_REFIT_081116/"
dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/REFIT_selected/"
home = "House1.csv"
df = pd.read_csv(dir+home,index_col="Time")
df.index = pd.to_datetime(df.index)
df_sub = deepcopy(df[:])
#% Resampling data
#TODO : TUNE ME
resample = True
data_sampling_time = 1 #in minutes
data_sampling_type = "minutes" # or seconds
if resample: 
  df_samp = df_sub.resample('1T',label='right',closed='right').mean()
  df_samp.drop('Issues',axis=1,inplace=True)
  standardize_column_names.rename_appliances(home,df_samp) # this renames columns
  #df_samp.rename(columns={'Aggregate':'use'},inplace=True) # renaming agg column
  print("*****RESAMPling DONE********")
  if home == "House16.csv":
      df_samp = df_samp[df_samp.index!= '2014-03-08'] # after resamping this day gets created 
else:
  df_samp = deepcopy(df_sub)
  df_samp.drop('Issues',axis=1,inplace=True)
  standardize_column_names.rename_appliances(home,df_samp) # this renames columns  

energy = df_samp.sum(axis=0)
high_energy_apps = energy.nlargest(7).keys() # CONTROL : selects few appliances
df_selected = df_samp[high_energy_apps]
#TODO : TUNE ME
denoised = True
if denoised:
    # chaning aggregate column
    iams = high_energy_apps.difference(['use'])
    df_selected['use'] = df_selected[iams].sum(axis=1)
    print('**********DENOISED DATA*************8')
train_dset,test_dset = ads.get_selected_home_data(home,df_selected)
#%% RUN fHMM
save_dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/Intermediary_results/"
#TODO : TUNE ME
filename = save_dir+"noisy/fhmm/selected/"+ home.split('.')[0]+'.pkl'
fhmm_result  =  localize_fhmm.fhmm_decoding(train_dset,test_dset) # dissagreation
fhmm_result['actual_power']['use'] = test_dset['use']
fhmm_result['train_power'] = train_dset
handle = open(filename,'wb')
#https://docs.python.org/2/library/pickle.html
pickle.dump(fhmm_result,handle)
handle.close()
#%% RUN CO
save_dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/Intermediary_results/"
#TODO : TUNE ME
filename = save_dir+"denoised/co/selected/" + home.split('.')[0]+'.pkl'
co_result = co.co_decoding(train_dset,test_dset)
co_result['actual_power']['use'] = test_dset['use'] # appending aggregate column for later use
co_result['train_power'] = train_dset
handle = open(filename,'wb')
pickle.dump(co_result,handle)
handle.close()
#%% RUN LBM
#TODO : TUNE ME
model_path= "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/Intermediary_results/denoised/lbm/population_models/selected/"
population_parameters = model_path +  home.split('.')[0] +'.pkl'
meterdata= test_dset
main_meter = 'use'
filetype = 'pkl'
lbm_result ={}
mains = meterdata[main_meter]
meterlist = meterdata.columns.tolist()
meterlist.remove(main_meter)
lbm = LBM.LatentBayesianMelding()
#meterlist=["refrigerator1",'bedroom1']
individual_model = lbm.import_model(meterlist, population_parameters,filetype)
mains_group = mains.groupby(mains.index.date)
res = []
start = time.clock()
for key,val in mains_group:
    print(key)
    try:    
        results = lbm.disaggregate_chunk(val)
        infApplianceReading = results['inferred appliance energy']
        res.append(infApplianceReading)
    except:
        print ("** LBM exception on {}**".format(key))
    continue    
print('LBM time taken {}'.format(time.clock()-start))  
infreadings = pd.concat(res)
#%%
infreadings.rename(columns={'mains':'use'},inplace=True)
lbm_result['decoded_power'] = infreadings
lbm_result['actual_power'] = meterdata
lbm_result['train_power'] = train_dset
#%%
#TODO : TUNE ME
save_dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/Intermediary_results/noisy/lbm/selected/"
filename = save_dir+ home.split('.')[0]+'.pkl'
handle = open(filename,'wb')
#https://docs.python.org/2/library/pickle.html
pickle.dump(lbm_result,handle)
handle.close()

#%%
#fhmm_result = co_result
#norm_fhmm = acmat.accuracy_metric_norm_error(fhmm_result)
#print(norm_fhmm)
#%%
gt= fhmm_result['actual_power']
pred= fhmm_result['decoded_power']
#%% DATA PLOTTING
count= 0
fig,axes = plt.subplots(pred.columns.shape[0]*2,1,sharex=True)
for app in pred.columns:
    gt1    = gt[app]
    pred1  = pred[app]
    gt1.plot(ax=axes[count],color="blue",legend=app)
    count = count+1
    pred1.plot(ax=axes[count],color="black")
    count = count+1
plt.show()
#%%
pkl_file = open(filename, 'rb')
data1 = pickle.load(pkl_file)
#pprint.pprint(data1)
#%%
def f(x,a,b):
   a=12
   b=55