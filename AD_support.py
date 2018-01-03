#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This contains different function defintions for anomaly detection on REFIT
Created on Tue Jan  2 08:54:04 2018

@author: haroonr
"""

def perform_clustering(samp,clusters):
  #TODO: this has not been completed yet
  # http://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html#sklearn.cluster.KMeans
  kmeans = KMeans(n_clusters=clusters, random_state=0).fit(samp)
  #kmeans.labels_
  #kmeans.cluster_centers_
  return (kmeans)

def re_organize_clusterlabels(samp):
  """this function checks if labels assigned to data are correct. Less consumption should get lower label and higher should get high label. Doing This maintains consistency across different days and datasets and allows comparison
 input: samp pandas dataframe has  columns: power and cluster
 ouput: pandas dataframe """
  dic = {}
  for i in np.unique(samp.cluster):
    dic[i] = samp[samp.cluster==i].power.iloc[0]
  if not sorted(list(dic.values())) == list(dic.values()):
    #if cluster labels are not assigned acc. to usage levels, i.e., less consumption should get lower label and so on
     p = pd.DataFrame(list(dic.items()))
     p.columns = ['old_label','value']
     q = p.sort_values('value')
     q['new_label'] = range(0,q.shape[0])
     r = dict(zip(q.old_label,q.new_label))
     samp['new_cluster'] =  [r[i] for i in samp['cluster'].values]
     samp.cluster = samp.new_cluster
     samp.drop('new_cluster',axis=1,inplace=True)
  return (samp)


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