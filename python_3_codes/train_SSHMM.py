#!/usr/bin/env python3
#
# Make a super-state hidden Markov model for evaluation (train_SSHMM.py)
# Copyright (C) 2013-2015 Stephen Makonin. All Right Reserved.
#

import sys, json
from statistics import mean
from time import time
from datetime import datetime
#from libDataLoaders import dataset_loader
#from libFolding import Folding
sys.path.append('/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/python_3_codes/')
from libPMF import EmpiricalPMF
from libSSHMM import SuperStateHMM, frange
ε = 0.00021
#%%
ε = 0.00021 # 0.00021, magic number, I forget how I calculated this value (maybe 110 / 524544)
#
print()
print('----------------------------------------------------------------------------------------------------------------')
print('Create & Save a SSHMM for Load Disaggregation Testing/Evaluation -- Copyright (C) 2013-2015, by Stephen Makonin.')
print('----------------------------------------------------------------------------------------------------------------')
print()
print('Start Time = ', datetime.now(), '(local time)')
print()

if len(sys.argv) != 9:
    print()
    print('USAGE: %s [modeldb] [dataset] [precision] [max obs] [denoised] [max states] [folds] [ids]' % (sys.argv[0]))
    print()
    print('       [modeldb]    - file name of model (omit file ext).')
    print('       [dataset]    - file name of dataset to use (omit file ext).')
    print('       [precision]  - number; e.g. 10 would convert A to dA.')
    print('       [max obs]    - The max observed value, e.g. 200.1 A.')
    print('       [denoised]   - denoised aggregate reads, else noisy.')
    print('       [max states] - max number of states a each load can have.')
    print('       [folds]      - number usually set to 10, 1 means data same for train/test.')
    print('       [ids]        - e.g. CDE,FGE(,...) -- case sensitive!')
    print()
    exit(1)

print()
print('Parameters:', sys.argv[1:])
(modeldb, dataset, precision, max_obs, denoised, max_states, folds, ids) = sys.argv[1:]
#(modeldb, dataset, precision, max_obs, denoised, max_states, folds, ids) = ['BigO_L02', 'AMPdsR1_1min_A', 10 ,200,' noisy', 4, 1 ,'BME,CDE']
precision = float(precision)
max_obs = float(max_obs)
denoised = denoised == 'denoised'
max_states = int(max_states)
folds = int(folds)
ids = ids.split(',')
datasets_dir = './datasets/%s.csv'
logs_dir = './logs/%s.log'
models_dir = './models/%s.json'
#%%
from copy import deepcopy
import pandas as pd
import sys
sys.path.append('/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/disaggregation_codes/')
import AD_support as ads

dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/REFIT_selected/"

home = "House1.csv"
df = pd.read_csv(dir+home,index_col="Time")
df.index = pd.to_datetime(df.index)
df_sub = deepcopy(df[:])
#% Resampling data
#TODO : TUNE ME
#%%
resample = True
data_sampling_time = 1 #in minutes
data_sampling_type = "minutes" # or seconds
if resample: 
  df_samp = df_sub.resample('1T',label='right',closed='right').mean()
  df_samp.drop('Issues',axis=1,inplace=True)
  #standardize_column_names.rename_appliances(home,df_samp) # this renames columns
  #df_samp.rename(columns={'Aggregate':'use'},inplace=True) # renaming agg column
  print("*****RESAMPling DONE********")
  if home == "House16.csv":
      df_samp = df_samp[df_samp.index!= '2014-03-08'] # after resamping this day gets created 
else:
  df_samp = deepcopy(df_sub)
  df_samp.drop('Issues',axis=1,inplace=True)
  #standardize_column_names.rename_appliances(home,df_samp) # this renames columns  

energy = df_samp.sum(axis=0)
high_energy_apps = energy.nlargest(7).keys() # CONTROL : selects few appliances
df_selected = df_samp[high_energy_apps]
#TODO : TUNE ME
denoised = False
if denoised:
    # chaning aggregate column
    iams = high_energy_apps.difference(['use'])
    df_selected['use'] = df_selected[iams].sum(axis=1)
    print('**********DENOISED DATA*************8')
train_dset,test_dset = ads.get_selected_home_data(home,df_selected)
#%%
ids = train_dset.columns.values.tolist()
ids.remove('Aggregate')
sshmms = []
train_times = []
max_states = 5
precision = 1.0
max_obs = 43200
max_obs = float(max_obs)
denoised = denoised == 'denoised'
max_states = int(max_states)
#%%
print()
print('Creating load PMFs and finding load states...')
print('\tMax partitions per load =', max_states)
pmfs = []
#id = 'Fridge'
#EmpiricalPMF(id, max_obs * precision, list(train_dset[id].astype(int)))

for id in ids:
    pmfs.append(EmpiricalPMF(id, max_obs * precision, list(train_dset[id].astype(int))))
    pmfs[-1].quantize(max_states, ε)
#%%
print()
print('Creating compressed SSHMM...')
incro = 1 / precision
sshmm = SuperStateHMM(pmfs, [i for i in frange(0, max_obs + incro, incro)])

print('\tConverting DataFrame in to obs/hidden lists...')
#%%
train_dset = train_dset.astype(int)
obs_id = list(train_dset)[0]
obs = list(train_dset[obs_id])
hidden = [i for i in train_dset[ids].to_records(index=False)]

sshmm.build(obs, hidden)
sshmms.append(sshmm)



#%%

#%%

savedir = "/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/sshmm_results/interresults"
print()
#fn = models_dir % modeldb
#print('Converting model %s to JSON for storage in %s...' % (modeldb, fn))
fp = open(savedir, 'w')
json.dump(sshmms, fp, default=(lambda o: o._asdict()), sort_keys=True, indent=None, separators=(',', ':'))
fp.close()
#%%
report = []
report.append(['Model DB', modeldb])
report.append(['Run Date', datetime.now()])
report.append(['Dataset', dataset])
report.append(['Precision', precision])
report.append(['Max States', max_states])
report.append(['Denoised?', denoised])
report.append(['Model Noise?', ('UNE' in ids)])
report.append(['Folds', folds.folds])
report.append(['IDs', ' '.join(ids)])
report.append(['Train Time', round(sum(train_times), 2)])
report.append(['Avg Time/Fold', round(sum(train_times) / len(train_times), 2)])
report.append(['Avg Load States', round(sum([mean(sshmm.Km) for sshmm in sshmms]) / len(sshmms), 1)])
report.append(['Sum Load States', round(sum([sum(sshmm.Km) for sshmm in sshmms]) / len(sshmms), 1)])
report.append(['Super-States', round(sum([sshmm.K for sshmm in sshmms]) / len(sshmms), 1)])
report.append(['Loads', sshmms[0].M])
report.append(['Obs', sshmms[0].N])
report.append(['Time Len', folds.data_size])
report.append(['P0 Size', round(sum([sshmm.P0.size() for sshmm in sshmms]) / len(sshmms), 1)])
report.append(['P0 Non-Zero', round(sum([sshmm.P0.nonzero() for sshmm in sshmms]) / len(sshmms), 1)])
report.append(['P0 Sparsity', round(sum([sshmm.P0.sparsity() for sshmm in sshmms]) / len(sshmms), 1)])
report.append(['P0 bytes', round(sum([sshmm.P0.bytes() for sshmm in sshmms]) / len(sshmms), 1)])
report.append(['A Size', round(sum([sshmm.A.size() for sshmm in sshmms]) / len(sshmms), 1)])
report.append(['A Non-Zero', round(sum([sshmm.A.nonzero() for sshmm in sshmms]) / len(sshmms), 1)])
report.append(['A Sparsity', round(sum([sshmm.A.sparsity() for sshmm in sshmms]) / len(sshmms), 1)])
report.append(['A bytes', round(sum([sshmm.A.bytes() for sshmm in sshmms]) / len(sshmms), 1)])
report.append(['B Size', round(sum([sshmm.B.size() for sshmm in sshmms]) / len(sshmms), 1)])
report.append(['B Non-Zero', round(sum([sshmm.B.nonzero() for sshmm in sshmms]) / len(sshmms), 1)])
report.append(['B Sparsity', round(sum([sshmm.B.sparsity() for sshmm in sshmms]) / len(sshmms), 1)])
report.append(['B bytes', round(sum([sshmm.B.bytes() for sshmm in sshmms]) / len(sshmms), 1)])
#%%
print()
print('-------------------------------- CSV REPORTING --------------------------------')
print()
print(','.join([c[0] for c in report]))
print(','.join([str(c[1]) for c in report]))
print()
print('-------------------------------- ------------- --------------------------------')

print()
print('End Time = ', datetime.now(), '(local time)')
print()
print('DONE!!!')
print()
