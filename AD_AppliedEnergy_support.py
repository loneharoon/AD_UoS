#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File used extensively for answering AppliedEnergy Queries
Created on Tue Dec 11 17:14:50 2018

@author: haroonr
"""
#%%
from __future__ import division
import pandas as pd
from sklearn.cluster import KMeans
import numpy as np
from copy import deepcopy
from itertools import groupby
import standardize_column_names as scn
from collections import OrderedDict,Counter
from datetime import datetime,timedelta
import re
import os
import my_utilities as myutil
import  matplotlib.pyplot  as plt
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
def AppliedEnergy_training(train_data, data_sampling_type, data_sampling_time, NoOfContexts, appliance):
    #%create training stats
    """" 1. get data
         2. divide it into different contexts/sets 
         3. divide each into day wise
         4. calculate above stats """
    contexts = create_contexts(train_data, NoOfContexts)      
    
    # create groups within contexts day wise, this will allow us to catch stats at day level otherwise preserving boundaries between different days might become difficult
    contexts_daywise = OrderedDict()
    for k,v in contexts.items():
      contexts_daywise[k] = v.groupby(v.index.date)
     #% Compute stats context wise
    contexts_stats = OrderedDict()
    #%
    print("AD module for {} called".format(appliance))
    for k,v in contexts_daywise.items():
        print("Contexts are {}".format(k))
        contexts_stats[k] = create_training_stats(v,sampling_type=data_sampling_type,sampling_rate=data_sampling_time) 
    return contexts_stats
  
  #%%
def create_contexts(data, NoOfContexts):
    
    if NoOfContexts == 1:
        contexts = OrderedDict()
        contexts['all24_gp'] = data.between_time("00:00","23:59:59")
    elif NoOfContexts == 2:
        contexts = OrderedDict()
        contexts['first12_gp'] = data.between_time("00:00","11:59:59")
        contexts['last12_gp'] = data.between_time("12:00","23:59:59")
    elif  NoOfContexts == 3:
        contexts = OrderedDict()
        contexts['first8_gp'] = data.between_time("00:00","07:59:59")
        contexts['next8_gp'] = data.between_time("08:00","15:59:59")
        contexts['last8_gp'] = data.between_time("16:00","23:59:59")
    elif NoOfContexts == 4:
        contexts = OrderedDict()
        contexts['night_1_gp'] = data.between_time("00:00:00","05:59:59")
        contexts['day_1_gp'] =  data.between_time("06:00:00","11:59:59")
        contexts['day_2_gp'] = data.between_time("12:00:00","17:59:59")
        contexts['night_2_gp'] = data.between_time("18:00:00","23:59:59")
    elif NoOfContexts == 6:
        contexts = OrderedDict()
        contexts['gp_0_4'] =   data.between_time("00:00","03:59:59")
        contexts['gp_4_8'] =   data.between_time("04:00","07:59:59")
        contexts['gp_8_12'] =  data.between_time("08:00","11:59:59")
        contexts['gp_12_16'] = data.between_time("12:00","15:59:59")
        contexts['gp_16_20'] = data.between_time("16:00","19:59:59")
        contexts['gp_20_24'] = data.between_time("20:00","23:59:59")
    elif NoOfContexts == 8:
        contexts = OrderedDict()
        contexts['gp_0_3'] =    data.between_time("00:00","02:59:59")
        contexts['gp_3_6'] =    data.between_time("03:00","05:59:59")
        contexts['gp_6_9'] =    data.between_time("06:00","08:59:59")
        contexts['gp_9_12'] =   data.between_time("09:00","11:59:59")
        contexts['gp_12_15'] =  data.between_time("12:00","14:59:59")
        contexts['gp_15_18'] =  data.between_time("15:00","17:59:59")
        contexts['gp_18_21'] =  data.between_time("18:00","20:59:59")
        contexts['gp_21_24'] =  data.between_time("21:00","23:59:59")
    
    else:
        raise ValueError("Please provide contexts which make sense\n")
    return (contexts)
  
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
    energy_state= [np.sum(v.power)/1000 for k,v in samp_groups] # dividing by 1000 to convert watts to Killowats as in next steps I want to compute KWH instead of WH (watthour)
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
  summ_dic['ON_duration'] = ON_duration
  summ_dic['OFF_duration'] = OFF_duration
  summ_dic['ON_energy'] = ON_energy
  summ_dic['OFF_energy'] = OFF_energy
  summ_dic['ON_cycles'] = ON_cycles
  summ_dic['OFF_cycles'] = OFF_cycles
  
  #for boxplot logic  
#  summ_dic['ON_duration'] = {'mean':round(np.mean(ON_duration),3), 'std':round(np.std(ON_duration),3)}
#  #summ_dic['ON_duration'].update(compute_boxplot_stats(ON_duration))
#  summ_dic['OFF_duration'] = {'mean':round(np.mean(OFF_duration),3), 'std':round(np.std(OFF_duration),3)}
#  #summ_dic['OFF_duration'].update(compute_boxplot_stats(OFF_duration))
#  summ_dic['ON_energy'] = {'mean':round(np.mean(ON_energy),3), 'std':round(np.std(ON_energy),3)}
# # summ_dic['ON_energy'].update(compute_boxplot_stats(ON_energy))
#  summ_dic['OFF_energy'] = {'mean':round(np.mean(OFF_energy),3), 'std':round(np.std(OFF_energy),3)}
#  #summ_dic['OFF_energy'].update(compute_boxplot_stats(OFF_energy))
#  summ_dic['ON_cycles'] = {'mean':round(np.mean(ON_cycles),0), 'std':round(np.std(ON_cycles),3)}
#  #summ_dic['ON_cycles'].update(compute_boxplot_stats(ON_cycles))
#  summ_dic['OFF_cycles'] = {'mean':round(np.mean(OFF_cycles),0), 'std':round(np.std(OFF_cycles),3)}
#  #summ_dic['OFF_cycles'].update(compute_boxplot_stats(OFF_cycles))
#  #for debugging purpose
##  print(compute_boxplot_stats(ON_duration))
#  print(compute_boxplot_stats(OFF_duration))
 # print(compute_boxplot_stats(ON_cycles))
  return (summ_dic)
