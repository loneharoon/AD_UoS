#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file contains all support functions for computing LBM features
Created on Fri Dec 22 12:12:11 2017

@author: haroonr
"""

def find_hmm_parameters(seq):
  model = hmm.GaussianHMM(n_components=2)
  model.fit(seq)
  return(model)
  
def find_cycle_parameters(app_daywise,sampling_time):
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
  df = pd.DataFrame({'cycles':cycles,'duration':duration})
  appliance_duration = df.groupby(cycles)['duration'].mean() * sampling_time
  energy_appliance =  df.groupby(cycles)['energy'].mean()
  samples = Counter(cycles) 
  # calculate cycle probabilites
  samples_ordered = OrderedDict(sorted(samples.items()))
  frequency = list(samples_ordered.values())
  frequency_sum = np.sum(frequency)
  cyclesprob = [i/frequency_sum for i in frequency]
  cycle_stat['numberOfCycles'] = cycles_unique
  cycle_stat['numberOfSamples'] = samples
  cycle_stat['numberOfCyclesProb'] = cyclesprob
  cycle_stat['numberOfCyclesEnergy'] = energy_appliance
  cycle_stat['numberOfCyclesDuration'] = appliance_duration
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
  return(sac_stat)
  