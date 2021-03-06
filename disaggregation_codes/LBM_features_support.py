#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file contains all support functions for computing LBM features
Created on Fri Dec 22 12:12:11 2017

@author: haroonr
"""
from collections import OrderedDict,Counter
import pandas as pd
from hmmlearn import hmm
import pickle
import numpy as np
np.random.seed(42)

def find_hmm_parameters(seq,n_components):
  model = hmm.GaussianHMM(n_components=n_components)
  model.fit(seq)
  return(model)
  
def find_cycle_parameters(app_daywise, sampling_time):
  #sampling_time = 2*60 # 2 minutes
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
  return(cycle_stat)
  
def find_sac_parameters(app_daywise,sampling_time):
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
  return(sac_stat)
  
#class MyJsonEncoder(json.JSONEncoder):
#    #'''This function is required to save json file otherwise default implementation throws errors,https://stackoverflow.com/a/27050186/3317829''''
#    def default(self, obj):
#        if isinstance(obj, np.integer):
#            return int(obj)
#        elif isinstance(obj, np.floating):
#            return float(obj)
#        elif isinstance(obj, np.ndarray):
#            return obj.tolist()
#        else:
#            return super(MyJsonEncoder, self).default(obj)

def save_obj(obj, fname ):
    # function used to save dictionaries in a file in pickle format
    ## fname should end with .pkl
    with open(fname, 'wb') as f:
        pickle.dump(obj, f, protocol= 2)

def load_obj(picklobject):
   #function used to read dictionaries from a pickle format file
    with open(picklobject, 'rb') as f:
        return pickle.load(f)