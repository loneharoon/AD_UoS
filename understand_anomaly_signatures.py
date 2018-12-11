#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
In this I plot only anomalous days, homewise. Intent is to check the signatures of all such days
Created on Thu Mar 22 15:23:21 2018

@author: haroonr
"""
import pickle
import sys
sys.path.append('/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/disaggregation_codes/')
import standardize_column_names as scn
import AD_support as ads
import re
import matplotlib.pyplot as plt
import accuracy_metrics_disagg as acmat
#%%
file_location = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/Intermediary_results/noisy/"
#TODO: tune two of us
home = "House10.pkl"
#home_no = home.split('.')[0]
#myapp = "ElectricHeater"# home 1
myapp = "Chest_Freezer"# home 10
#myapp = "Fridge_Freezer_1"# home 16
#myapp = "Fridge_Freezer"# home 18
#myapp = "Freezer"# home 20

technique = "fhmm"
method = technique + "/selected/"
#method="lbm/selected_results/"

filename = file_location + method + home
results = open(filename, 'rb')
data_dic = pickle.load(results)
train_power =   data_dic['train_power']
decoded_power = data_dic['decoded_power']
actual_power  = data_dic['actual_power']

train_data  =  train_power[myapp]
test_data   =  decoded_power[myapp]
actual_data = actual_power[myapp]

#%
house_no =  int(re.findall('\d+',home)[0])
home = home.split('.')[0] + '.csv'
appliance = scn.reverse_lookup(home, myapp) # find actual name of appliance in anomaly database
assert len(appliance) > 1
day_start = actual_data.first_valid_index()
day_end = actual_data.last_valid_index()
#%%
plt.ioff()
gt_days = ads.anomalous_days_from_gt(house_no, appliance, day_start, day_end)
ads.plot_bind_save_all_anomalies(actual_data, gt_days.values, home, myapp)

#%%

#rmse_score = compute_rmse(actual_power, decoded_power)
#(pd_cat.corr().predicted[0],2)
daterange = "2014-06-01" + ":" +"2014-06-05"
gt = actual_power["2014-06-01" : "2014-06-05"]
pred = decoded_power["2014-06-01" : "2014-06-05"]
#compute_rmse(gt, pred)
compute_correlation(gt, pred)
#%%
###
def compute_rmse(gt, pred):
    from sklearn.metrics import mean_squared_error
    rms_error = {}
    for app in pred.columns:
        rms_error[app] =  np.sqrt(mean_squared_error(gt[app],pred[app]))
    return pd.Series(rms_error)
#%%
def compute_correlation(gt, pred):
    corr_coeff = {}
    for app in pred.columns:
        corr_coeff[app] =  ( pd.concat([gt[app], pred[app]], axis = 1).corr()).iloc[0][1]      
    return pd.Series(corr_coeff)