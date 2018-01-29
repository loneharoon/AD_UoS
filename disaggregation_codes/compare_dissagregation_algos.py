"""
This file explicitly computes dissaggregation error metrics on minutes level data. Data used is entirely dataport
and approaches tested include CO and FHMM
Created on 

@author: haroonr
"""
#%%
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
#np.random.seed(123)
import sys
sys.path.append('/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/disaggregation_codes/')
import accuracy_metrics_disagg as acmat
#%%
# List all houses in a directory
dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/Dataport/mix_homes/default3/"
#savedir = "/Volumes/MacintoshHD2/Users/haroonr/Dropbox/nilmtk_work/disagg_results/"
execfile("/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/disaggregation_codes/localize_fhmm.py")

#execfile("/Volumes/MacintoshHD2/Users/haroonr/Dropbox/nilmtk_work/plot_functions.py")
execfile("/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/disaggregation_codes/cluster_file.py")
#execfile("/Volumes/MacintoshHD2/Users/haroonr/Dropbox/nilmtk_work/nilmtk_pycharm/utils.py")
execfile("/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/disaggregation_codes/co.py")

#%%
#def run_dissaggreation_algos():
#    #sel_homes = [1169, 130, 1314, 1463, 2075, 2864, 3039, 3538, 936, 2366]# FOUND IN FIRST 200 HOMES
#    sel_homes = [3864,3893,410,434,4514,4641,4703,4864,4874,490,4927] # FOUND BETWEEN 200-300 HOMES
#    houses = map(lambda x: str(x) + ".csv", sel_homes)
#    #houses = [f for f in os.listdir(dir)]
#    for hos in houses:
#        #df = pd.read_csv(dir+houses[0],index_col='localminute') # USE HOUSE (6,115)
hos = '1463.csv'
df = pd.read_csv(dir + hos, index_col='localminute')  # USE HOUSE (6,115)
df.index = pd.to_datetime(df.index)
df = df["2014-06-01":"2014-08-29 23:59:59"]
res = df.sum(axis=0)
high_energy_apps = res.nlargest(6).keys() # CONTROL : selects few appliances
df_new = df[high_energy_apps]
del df_new['use']# drop stale aggregate column
df_new['use'] = df_new.sum(axis=1) # create new aggregate column

train_dset = df_new.truncate(before="2014-06-01", after="2014-06-30 23:59:59")
test_dset = df_new.truncate(before="2014-07-01", after="2014-07-29 23:59:59")
# keep tab on context option - creates day and night divison
  #%%

fhmm_result  =  fhmm_decoding(train_dset,test_dset) # dissagreation
#co_result = co_decoding(train_dset,test_dset)
#plot_actual_vs_decoded(co_result)
#%%

#co_rmse = compute_rmse(co_result['actaul_power'],co_result['decoded_power'])
#%%
#fhmm_rmse = pd.DataFrame.from_dict(fhmm_rmse)
#co_rmse =pd.DataFrame.from_dict(co_rmse)

#fhmm_rmse.to_csv(savedir+"fhmm_rmse_"+hos)
#co_rmse.to_csv(savedir+"co_rmse_"+hos)
#%%
fhmm_rmse = acmat.compute_rmse(fhmm_result['actaul_power'],fhmm_result['decoded_power'])
print(fhmm_rmse)
aggregate = sum(test_dset['use'])
fhmm_kolter = acmat.diss_accu_metric_kolter_1(fhmm_result,aggregate)
print(fhmm_kolter)
fhmm_kolter = acmat.diss_accu_metric_kolter_exact(fhmm_result,aggregate)
print(fhmm_kolter)
#co_kotler = acmat.diss_accu_metric_kotler_1(co_result,aggregate)
#%%

norm_fhmm = acmat.accuracy_metric_norm_error(fhmm_result)
#norm_co = accuracy_metric_norm_error(co_result)
#%%
concat_res = pd.concat([fhmm_rmse,co_rmse,norm_fhmm,norm_co],axis=1)
concat_res.columns = ['fhmm_rmse','co_rmse','fhmm_norm','co_norm']
concat_res = concat_res.round(2)
concat_res.to_csv(savedir+"norm_rmse_"+hos)

res_frame = pd.DataFrame(data={'algo':['fhmm_acc','co_acc'],'accuracy':[fhmm_kotler,co_kotler]})

res_frame = res_frame.round(2)
res_frame.to_csv(savedir+"accuracy_kolter_"+hos,index=False)

# METRICS TAKEN FROM GAMELLO PAPER
#fhmm_accu = compute_dissagg_accuracy(fhmm_result)
#co_accu = compute_dissagg_accuracy(co_result)
#fhmm_accu.to_csv(savedir + "fhmm_gammello_accu" + hos)
#co_accu.to_csv(savedir + "co_gamello_accu" + hos)