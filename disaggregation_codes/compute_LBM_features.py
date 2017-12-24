#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
In this file, I see how to compute features of LBM disaggregation model for a single appliance.
Please use LBM_features_main.py to compute such featueres at a scale
Created on Tue Dec 19 19:09:12 2017

@author: haroonr
"""
#%% 
import pandas as pd
import numpy as np
from copy import copy
import matplotlib.pyplot as plt
from hmmlearn import hmm
np.random.seed(42)
import json,pickle
from collections import Counter,OrderedDict
#%%
dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/CLEAN_REFIT_081116/House1.csv"
df =  pd.read_csv(dir,index_col="Time")
df.index = pd.to_datetime(df.index)
df_2min = df.resample('2T',label="right").mean()
freezer_1 = copy(df.Freezer_1)
freezer_1_sub =  freezer_1['2013']
#%% HMM modelling
app_features = {}
data = freezer_1_sub .values
data = [[j] for j in data]
model = hmm.GaussianHMM(n_components=2)
model.fit(data)
app_features['means'] = model.means_.tolist() 
app_features['startprob'] = model.startprob_.reshape(-1,1).tolist()
app_features['transprob'] = model.transmat_.tolist()
#%% cycles modelling
sampling_time = 1 # means I am not changing anything
app_daywise = pd.groupby(freezer_1_sub,by=freezer_1_sub.index.date)
cycle_stat = {}
cycles = [] # no  of cycles
duration = [] # no. of cycles duration
energy = [] # no of cycles energy
for day in app_daywise:
  data = day[1] # day[1] is item and day[0] is key
  count = 0
  ontime = 0
  energycount = 0
  for i in range(1,data.shape[0]): 
    if data[i] > 10 and data[i-1] < 2:
      count = count + 1
      ontime = ontime + 1
      energycount =  energycount + data[i]
    elif data[i] > 10 and data[i-1] > 10: # in same ON state
      ontime = ontime + 1
      energycount = energycount + data[i]
  cycles.append(count)
  duration.append(ontime)
  energy.append(energycount)
  
cycles_unique = np.unique(cycles)
df = pd.DataFrame({'cycles':cycles,'duration':duration,'energy':energy})
appliance_duration = df.groupby(cycles)['duration'].mean() * sampling_time
energy_appliance =  df.groupby(cycles)['energy'].mean()
samples = Counter(cycles) 
# calculate cycle probabilites
samples_ordered = OrderedDict(sorted(samples.items()))
frequency = list(samples_ordered.values())
frequency_sum = np.sum(frequency)
cyclesprob = [i/frequency_sum for i in frequency]
cycle_stat['numberOfCycles'] = cycles_unique.tolist()
cycle_stat['numberOfSamples'] = list(dict(samples).values())
cycle_stat['numberOfCyclesProb'] = cyclesprob
cycle_stat['numberOfCyclesEnergy'] = energy_appliance.tolist()
cycle_stat['numberOfCyclesDuration'] = appliance_duration.tolist()

app_features['numberOfCyclesStats'] = cycle_stat
#%% sac modelling
sac_stat = {}
sac_energy=[]
sac_duration=[]
for day in app_daywise:
 # print(type(day))
  data = day[1] # day[1] is item and day[0] is key
  energy = 0
  duration = 0
  for i in range(1,data.shape[0]): 
    if data[i] > 10 and data[i-1] < 2:
      duration = duration + 1
      energy =  energy + data[i]
    elif data[i] > 10 and data[i-1] > 10: # in same ON state
      duration = duration + 1
      energy =  energy + data[i]
  sac_energy.append(energy)
  sac_duration.append(duration)
sac_stat['sac'] = np.average(sac_energy)
sac_stat['induced density of sac'] = [np.mean(sac_energy),np.std(sac_energy)] 
sac_stat['induced density of duration'] = [np.mean(sac_duration)*sampling_time,np.std(sac_duration)*sampling_time] 
sac_stat['sac sample'] = np.reshape(sac_energy, (-1,1)).tolist()
app_features.update(sac_stat)

#%% save temporary somwhere
# IF JSON FAILS SAVE AS PICKLE FORMAT
json_save_dir = "/Volumes/MacintoshHD2/Users/haroonr/Downloads/temp/"
savename = json_save_dir+'freezer.json'
with open(savename,'w') as fp:
  json.dump(app_features,fp,indent = 4)
 # OR
save_obj(app_features,json_save_dir+"temp.pkl")
#%%
def save_obj(obj, fname ):
    ## fname should end with .pkl
    with open(fname, 'wb') as f:
        pickle.dump(obj, f, protocol= 2)

def load_obj(picklobject):
    with open(picklobject, 'rb') as f:
        return pickle.load(f)
