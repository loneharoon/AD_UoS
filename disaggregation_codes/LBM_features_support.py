#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 12:12:11 2017

@author: haroonr
"""
#%% 
import pandas as pd
import numpy as np
from copy import copy
from hmmlearn import hmm
np.random.seed(42)
#%%
dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/Dataport/mix_homes/default/injected_anomalies/"
fl = "115.csv"
df = pd.read_csv(dir+fl,index_col="localminute")
df.index = pd.to_datetime(df.index)
#%%
df.drop('use',axis=1,inplace=True)
train_df = copy(df[:'2014-06-20'])
for i in train_df.columms:
  data = train_df.i
  data = data.values
  data = [[j] for j in data]
  hmm_par = find_hmm_parameters(data)
  means = hmm_par.means_ 
  startprob = hmm_par.startprob_
  transprob =hmm_par.transmat_
  lbm_cyclepar =  find_cycle_parameters(data)
  
  
  
  
  
  
  
def find_hmm_parameters(seq):
  model = hmm.GaussianHMM(n_components=2)
  model.fit(seq)
  return(model)
  
def find_cycle_parameters(seq):
sampling_time = 2*60 # 2 minutes
#  = 0CALCULATE NUMBER OF CYCLES 
cycles=[]
duration=[]
energy=[]
for day in freezer_daywise:
 # print(type(day))
  data = day[1] # day[1] is item and day[0] is key
  count = 0
  ontime = 0
  energycount = 0
  for i in range(1,data.shape[0]): 
    if data[i] > 10 and data[i-1] < 2:
      count = count +1
      ontime = ontime + 1
      energycount =  energycount + data[i]
    elif data[i] > 10 and data[i-1] > 10: # in same ON state
      ontime = ontime + 1
      energycount = energycount + data[i]
  cycles.append(count)
  duration.append(ontime)
  energy.append(energycount)

cycles_unique = np.unique(cycles)
df  = pd.DataFrame({'cycles':cycles,'duration':duration})
appliance_duration = df.groupby(cycles)['duration'].mean()
energy_appliance =  df.groupby(cycles)['energy'].mean()
  