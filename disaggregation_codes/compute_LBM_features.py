#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
In this file, I see how to compute features of LBM disaggregation model.
This is my dummy code for an appliance. Please use other py files as final files
Created on Tue Dec 19 19:09:12 2017

@author: haroonr
"""
#%% 
import pandas as pd
import numpy as np
from copy import copy
import matplotlib.pyplot as plt
#%%
dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/CLEAN_REFIT_081116/House1.csv"
df =  pd.read_csv(dir,index_col="Time")
df.index = pd.to_datetime(df.index)
df_2min = df.resample('2T',label="right").mean()

freezer_1 = copy(df.Freezer_1)
freezer_1_sub =  freezer_1['2013']
freezer_daywise = pd.groupby(freezer_1_sub,by=freezer_1_sub.index.date)
#%% CALCULATE NUMBER OF CYCLES 
cycles = []
for day in freezer_daywise:
 # print(type(day))
  data = day[1] # day[1] is item and day[0] is key
  count = 0
  for i in range(1,data.shape[0]): 
    if data[i] > 10 and data[i-1] < 2:
      count = count +1
  cycles.append(count)
cycles_unique = np.unique(cycles)
#%% CALCULATE NUMBER OF SAMPLES
from collections import Counter
samples = Counter(cycles)

#%% Calculate number of cycles probabilites
from collections import OrderedDict
samples_ordered = OrderedDict(sorted(samples.items()))
frequency = list(samples_ordered.values())
frequency_sum = np.sum(frequency)
cyclesProb = [i/frequency_sum for i in frequency]
#%% calculate duration and energy of applaince usage
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
#%% Compute SAC parameter 
sac_energy=[]
sac_duration=[]
sampling_freq =  2*60 # 2 minutes
for day in freezer_daywise:
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
sac = np.average(sac_energy)
induced_sac_density  =   [np.mean(sac_energy),np.std(sac_energy)] 
induced_sac_duration =   [np.mean(sac_duration),np.std(sac_duration)] 
  
  