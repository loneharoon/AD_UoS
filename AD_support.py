#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This contains different function defintions for anomaly detection on REFIT
Created on Tue Jan  2 08:54:04 2018

@author: haroonr
"""

def perform_clustering(samp):
  #TODO: this has not been completed yet
  # http://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html#sklearn.cluster.KMeans
  kmeans = KMeans(n_clusters=2, random_state=0).fit(samp)
  #kmeans.labels_
  #kmeans.cluster_centers_
  return (kmeans)



def find_cycle_parameters(app_daywise,sampling_time):
  #sampling_time = 2*60 # 2 minutes
  cycle_stat = {}
  cycles = [] # no  of cycles
  duration = [] # no. of cycles duration
  energy = [] # no of cycles energy
      if data[i] > 10 and data[i-1] < 2:
        count = count + 1
        ontime = ontime + 1
        energycount =  energycount + data[i]
  for day in app_daywise:
    data = day[1] # day[1] is item and day[0] is key
    count = 0
    ontime = 0
    energycount = 0
    for i in range(1,data.shape[0]): 
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