#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This contains different function defintions for anomaly detection on REFIT
Created on Tue Jan  2 08:54:04 2018

@author: haroonr
"""
#%%
import pandas as pd
from sklearn.cluster import KMeans
import numpy as np
from itertools import groupby
from collections import OrderedDict,Counter
from AD_support import *
#%%
def perform_clustering(samp,clusters):
  #TODO: this has not been completed yet
  # http://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html#sklearn.cluster.KMeans
  kmeans = KMeans(n_clusters=clusters, random_state=0).fit(samp)
  #kmeans.labels_
  #kmeans.cluster_centers_
  return (kmeans)
###
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
#%%
###
def compute_boxplot_stats(boxdata):
  ''' Here i compute all stats of boxplot and return them as dictionary'''
  boxdict = OrderedDict()
  nmedian =  np.median(boxdata)
  istquat =  np.percentile(boxdata,0)
  thirdquat =  np.percentile(boxdata,100)
  iqr = thirdquat - istquat
  boxdict['nmedian'] = nmedian
  boxdict['lowerwisker'] =  nmedian - 1.5 * iqr 
  boxdict['upperwisker'] =  nmedian + 1.5 * iqr
  return (boxdict)
#%%
###
def create_training_stats(traindata,sampling_type,sampling_rate):
  """ this method computes cycle frequences and durations from the training data
  Input: pandas series of power data in the python groupby object
  Output: Stats computed in form of dictionary """
  dic = OrderedDict()
  for k, v in traindata:
    #print(k)
    samp = v.to_frame()
    # handle nans in data
    nan_obs = int(samp.isnull().sum())
    #rule: if more than 50% are nan then I drop that day from calculcations othewise I drop nan readings only
    if nan_obs:  
      if nan_obs >= 0.50*samp.shape[0]:
        print("More than 50percent obs missing hence drop day {} ".format(k))
        #continue
      elif nan_obs < 0.50*samp.shape[0]:
        print("dropping  {} nan observations for day {}".format(nan_obs,k))
        samp.dropna(inplace=True)
    samp.columns = ['power']
    samp_val =  samp.values
    samp_val = samp_val.reshape(-1,1)
    #FIXME: you can play with clustering options
    kobj = perform_clustering(samp_val,clusters=2)
    samp['cluster'] = kobj.labels_
    samp = re_organize_clusterlabels(samp)
    tempval = [(k,sum(1 for i in g)) for k,g in groupby(samp.cluster.values)]
    tempval = pd.DataFrame(tempval,columns=['cluster','samples'])
    #%energy computation logic for eacy cycle
    samp['state_no']  = np.repeat(range(tempval.shape[0]),tempval['samples'])
    samp_groups = samp.groupby(samp.state_no)
    energy_state= [np.sum(v.power) for k,v in samp_groups]
    if sampling_type =='minutes':
      energy_state = np.multiply(energy_state, (sampling_rate/60.))
    elif sampling_type == 'seconds':
      energy_state = np.multiply(energy_state, (sampling_rate/3600.)) 
    tempval['energy_state'] =  np.round(energy_state,2)
   #% energy logic ends
    off_cycles =list(tempval[tempval.cluster==0].samples)
    on_cycles =list(tempval[tempval.cluster==1].samples)
    off_energy =list(tempval[tempval.cluster==0].energy_state)
    on_energy =list(tempval[tempval.cluster==1].energy_state)
    temp_dic = {}
    temp_dic["on"] = on_cycles
    temp_dic["off"] = off_cycles
    temp_dic["on_energy"] = on_energy
    temp_dic["off_energy"] = off_energy
    cycle_stat = Counter(tempval.cluster)
    temp_dic.update(cycle_stat)
    dic[str(k)] = temp_dic
    #% Merge  OFF and ON states of different days into singe lists 
  ON_duration = []
  OFF_duration = []
  ON_energy = []
  OFF_energy = []
  ON_cycles = []
  OFF_cycles = []
  for k,v in dic.items():
    ON_duration.append(v['on'])
    OFF_duration.append(v['off'])
    ON_energy.append(v['on_energy'])
    OFF_energy.append(v['off_energy'])
    ON_cycles.append(v[1])
    OFF_cycles.append(v[0])
  ON_duration  =  [ item for sublist in ON_duration for item in sublist]
  OFF_duration = [ item for sublist in OFF_duration for item in sublist]
  ON_energy  =  [ item for sublist in ON_energy for item in sublist]
  OFF_energy = [ item for sublist in OFF_energy for item in sublist]
   #%
  summ_dic = {}
  #for boxplot logic  
  summ_dic['ON_duration'] = {'mean':round(np.mean(ON_duration),3), 'std':round(np.std(ON_duration),3)}
  summ_dic['ON_duration'].update(compute_boxplot_stats(ON_duration))
  summ_dic['OFF_duration'] = {'mean':round(np.mean(OFF_duration),3), 'std':round(np.std(OFF_duration),3)}
  summ_dic['OFF_duration'].update(compute_boxplot_stats(OFF_duration))
  summ_dic['ON_energy'] = {'mean':round(np.mean(ON_energy),3), 'std':round(np.std(ON_energy),3)}
  summ_dic['ON_energy'].update(compute_boxplot_stats(ON_energy))
  summ_dic['OFF_energy'] = {'mean':round(np.mean(OFF_energy),3), 'std':round(np.std(OFF_energy),3)}
  summ_dic['OFF_energy'].update(compute_boxplot_stats(OFF_energy))
  summ_dic['ON_cycles'] = {'mean':round(np.mean(ON_cycles),0), 'std':round(np.std(ON_cycles),3)}
  summ_dic['ON_cycles'].update(compute_boxplot_stats(ON_cycles))
  summ_dic['OFF_cycles'] = {'mean':round(np.mean(OFF_cycles),0), 'std':round(np.std(OFF_cycles),3)}
  summ_dic['OFF_cycles'].update(compute_boxplot_stats(OFF_cycles))
  #for debugging purpose
  print(compute_boxplot_stats(ON_duration))
  print(compute_boxplot_stats(OFF_duration))
  print(compute_boxplot_stats(ON_cycles))
  return (summ_dic)

#%%
def create_testing_stats_with_boxplot(testdata,k,sampling_type,sampling_rate):
  """  """
  temp_dic = {}
  #for k, v in testdata:
    #print(k)
  samp = testdata.to_frame()
  # handle nans in data
  nan_obs = int(samp.isnull().sum())
  #rule: if more than 50% are nan then I drop that day from calculcations othewise I drop nan readings only
  if nan_obs:  
    if nan_obs >= 0.50*samp.shape[0]:
      print("More than 50percent obs missing hence dropping context {} ".format(k))
      return (False)
    elif nan_obs < 0.50*samp.shape[0]:
      print("dropping  {} nan observations for total of {} in context {}".format(nan_obs, samp.shape[0], k))
      samp.dropna(inplace=True)
  samp.columns = ['power']
  samp_val =  samp.values
  samp_val = samp_val.reshape(-1,1)
  #FIXME: you can play with clustering options
  if np.std(samp_val) <= 1:# contains observations with same values, basically forward filled values
    print("Dropping context {} from analysis as it contains same readings".format(k))
    return (False)
  kobj = perform_clustering(samp_val,clusters=2)
  samp['cluster'] = kobj.labels_
  samp = re_organize_clusterlabels(samp)
  tempval = [(k,sum(1 for i in g)) for k,g in groupby(samp.cluster.values)]
  tempval = pd.DataFrame(tempval,columns=['cluster','samples'])
  #%energy computation logic for eacy cycle
  samp['state_no']  = np.repeat(range(tempval.shape[0]),tempval['samples'])
  samp_groups = samp.groupby(samp.state_no)
  temp_energy_state= [np.sum(v.power) for k,v in samp_groups]
  if sampling_type =='minutes':
    temp_energy_state = np.multiply(temp_energy_state, (sampling_rate/60.)) # energy formula
  elif sampling_type == 'seconds':
    temp_energy_state = np.multiply(temp_energy_state, (sampling_rate/3600.)) # energy formula
  tempval['energy_state'] =  np.round(temp_energy_state,2)

 #% energy logic ends
  off_cycles =list(tempval[tempval.cluster==0].samples)
  on_cycles =list(tempval[tempval.cluster==1].samples)
  off_energy =list(tempval[tempval.cluster==0].energy_state)
  print(off_energy)
  on_energy =list(tempval[tempval.cluster==1].energy_state)
  print(on_energy)
  temp_dic["on_energy"] = on_energy
  temp_dic["off_energy"] = off_energy
  temp_dic["on"] = on_cycles
  temp_dic["off"] = off_cycles
  cycle_stat = Counter(tempval.cluster)
  temp_dic.update(cycle_stat)
  summ_dic = OrderedDict()
  summ_dic['ON_duration'] = temp_dic["on"]
  summ_dic['OFF_duration'] = temp_dic["off"]
  summ_dic['ON_energy'] = temp_dic["on_energy"]
  summ_dic['OFF_energy'] = temp_dic["off_energy"]
  summ_dic['ON_cycles'] = temp_dic[1]
  summ_dic['OFF_cycles'] = temp_dic[0]
  return (summ_dic)
#%%
###
def create_testing_stats(testdata,k):
  """ this method computes cycle frequences and durations for the test day data
  Input: pandas series of power data
  Output: Stats computed in form of dictionary """
  temp_dic = {}
  #for k, v in testdata:
    #print(k)
  samp = testdata.to_frame()
  # handle nans in data
  nan_obs = int(samp.isnull().sum())
  #rule: if more than 50% are nan then I drop that day from calculcations othewise I drop nan readings only
  if nan_obs:  
    if nan_obs >= 0.50*samp.shape[0]:
      print("More than 50percent obs missing hence dropping context {} ".format(k))
      return
    elif nan_obs < 0.50*samp.shape[0]:
      print("dropping  {} nan observations for context {}".format(nan_obs,k))
      samp.dropna(inplace=True)
  samp.columns = ['power']
  samp_val =  samp.values
  samp_val = samp_val.reshape(-1,1)
  #FIXME: you can play with clustering options
  kobj = perform_clustering(samp_val,clusters=2)
  samp['cluster'] = kobj.labels_
  samp = re_organize_clusterlabels(samp)
  tempval = [(k,sum(1 for i in g)) for k,g in groupby(samp.cluster.values)]
  tempval = pd.DataFrame(tempval,columns=['cluster','samples'])
  off_cycles =list(tempval[tempval.cluster==0].samples)
  on_cycles =list(tempval[tempval.cluster==1].samples)
  temp_dic["on"] = on_cycles
  temp_dic["off"] = off_cycles
  cycle_stat = Counter(tempval.cluster)
  temp_dic.update(cycle_stat)

  summ_dic = {}
  summ_dic['ON_duration'] = {'mean':round(np.mean(temp_dic["on"]),3), 'std':round(np.std(temp_dic["on"]),3)}
  summ_dic['OFF_duration'] = {'mean':round(np.mean(temp_dic["off"]),3), 'std':round(np.std(temp_dic["off"]),3)}
  summ_dic['ON_cycles'] = {'mean':round(np.mean(temp_dic[1]),0), 'std':round(np.std(temp_dic[1]),3)}
  summ_dic['OFF_cycles'] = {'mean':round(np.mean(temp_dic[0]),0), 'std':round(np.std(temp_dic[0]),3)}
  return (summ_dic)