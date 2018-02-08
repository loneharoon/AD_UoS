#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This file only computes disagregation error using LBM technique for only dataport. Please
use another file for homes with seconds data
Created on Sun Dec 24 14:52:10 2017

@author: haroonr
"""

#%%
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
np.random.seed(42)
import pickle,sys
sys.path.append('/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/disaggregation_codes/')
from latent_Bayesian_melding import LatentBayesianMelding
#execfile("/Volumes/MacintoshHD2/Users/haroonr/Dropbox/nilmtk_work/nilmtk_pycharm/localize_appliance_support.py")
#dissagg_result_save= "/Volumes/MacintoshHD2/Users/haroonr/Dropbox/nilmtk_work/inter_results/disagg_outputs/"
#%% Read one home at a time
dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/Dataport/mix_homes/default3/"
savedir = "/Volumes/MacintoshHD2/Users/haroonr/Dropbox/nilmtk_work/inter_results/lbm_disaggregation_puredata/"
savedir_error = "/Volumes/MacintoshHD2/Users/haroonr/Dropbox/nilmtk_work/disagg_results/"

hos = "3538.csv"  #3538
pklobject = "3538.pkl"
model_path = "/Volumes/MacintoshHD2/Users/haroonr/Dropbox/nilmtk_work/inter_results/lbm_population_models/"
population_parameters = model_path + pklobject
df = pd.read_csv(dir + hos, index_col='localminute')  
df.index = pd.to_datetime(df.index)
df = df["2014-06-01":"2014-08-29 23:59:59"]
res = df.sum(axis=0)
#high_energy_apps = res.nlargest(6).keys() # CONTROL : selects few appliances
high_energy_apps = ['use','air1','furnace1','refrigerator1','microwave1','kitchenapp2']#3538.csv
df_new = df[high_energy_apps]
del df_new['use']# drop stale aggregate column
df_new['use'] = df_new.sum(axis=1).values # create new aggregate column
#%%
meterdata = df_new.truncate(before="2014-07-02", after="2014-08-29 23:59:59")
#meterdata = df_new.truncate(before="2014-07-01", after="2014-07-10 23:59:59")
#%%
# experiments show that we should provide day level chunks intead of allday once. and changing sample_seconds does not affect accuracy
#lbm_result = lbm_decoder(meterdata, population_parameters, main_meter = "use", filetype = "pkl")
main_meter = 'use'
filetype = 'pkl'
mains = meterdata[main_meter]
meterlist = meterdata.columns.tolist()
meterlist.remove(main_meter)
lbm = LatentBayesianMelding()
#meterlist=["refrigerator1",'bedroom1']
individual_model = lbm.import_model(meterlist, population_parameters,filetype)
mains_group = mains.groupby(mains.index.date)
res = []
for key,val in mains_group:
    print(key)
    results = lbm.disaggregate_chunk(val)
    infApplianceReading = results['inferred appliance energy']
    res.append(infApplianceReading)
infApplianceReading = pd.concat(res)
infApplianceReading.to_csv(dissagg_result_save+"lbm/" + hos) # save diss_data for furthe processing
#%%
#infApplianceReading.to_csv(savedir+"115.csv")
#%% TEMPORARY CELL
gt = meterdata[meterlist]
lbm_result = {'actaul_power':gt,'decoded_power':infApplianceReading}
norm_lbm = accuracy_metric_norm_error(lbm_result)
print (norm_lbm)


#%%
gt = meterdata[meterlist] # drops aggregate column internally
lbm_rmse = compute_rmse(gt,infApplianceReading)
lbm_rmse = pd.DataFrame.from_dict(lbm_rmse)
lbm_rmse.to_csv(savedir_error+"lbm_rmse_"+hos)

#prepare DS as according to metric input
aggregate = sum(meterdata['use'])
lbm_result = {'actaul_power':gt,'decoded_power':infApplianceReading}
lbm_kotler = diss_accu_metric_kotler_1(lbm_result,aggregate)
norm_lbm = accuracy_metric_norm_error(lbm_result)
norm_lbm.to_csv(savedir_error + "lbm_norm_rmse"+hos)

res_frame = pd.DataFrame(data={'algo':['lbm_acc'],'accuracy':[lbm_kotler]})
res_frame = res_frame.round(2)
res_frame.to_csv(savedir_error+"lbm_accuracy_kolter_"+hos,index=False)
