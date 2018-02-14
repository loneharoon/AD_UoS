#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
In this I implement Bochao's GSP disaggregation method
Created on Thu Feb  1 15:42:41 2018

@author: haroonr
"""
from __future__ import division
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import sys
from scipy.stats import norm
sys.path.append('/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/disaggregation_codes/')
import accuracy_metrics_disagg as acmat
import matplotlib.pyplot as plt
import gsp_support as gsp
from collections import OrderedDict
#%%
#import scipy.io
#fpath = "/Volumes/MacintoshHD2/Users/haroonr/Documents/MATLAB/main.mat"
#fl = scipy.io.loadmat(fpath)
#data_file = fl['main'].flatten().tolist()  
reddhome= "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/Redd_dataset/house3/"
main = pd.read_csv(reddhome+"main_meters.csv",index_col="Index")
main = main[0:30000]
main['aggregate'] = main.apply(sum,axis=1)
main['timestamp'] = pd.to_datetime(main.index).astype(np.int64) //10**9
iam = pd.read_csv(reddhome+"sub_meters.csv",index_col="Index")
keep = ['refrigerator','disposal','dishwaser','kitchen_outlets', 'kitchen_outlets.1','lighting','microwave']
iam_sub = iam[keep]
iam_sub['timestamp'] = pd.to_datetime(iam_sub.index).astype(np.int64) //10**9
#main['aggregate'] = main.apply(sum,axis=1)

#%%
#dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/CLEAN_REFIT_081116/"
#home = "House1.csv"
#df = pd.read_csv(dir+home,index_col="Time")
#df.index = pd.to_datetime(df.index)
#df_sub = df["2014-03-01":'2014-04-30'] # since before march their are calibration issues
##%% Resampling data
#print("*****RESAMPLING********")
#df_samp = df_sub.resample('1T',label='right',closed='right').mean()
#data_sampling_time = 1 #in minutes
#data_sampling_type = "minutes" # or seconds
#df_samp.drop('Issues',axis=1,inplace=True)
#df_samp.rename(columns={'Aggregate':'use'},inplace=True) # renaming agg column
#%%
#data_vec = df_samp['use'].values.tolist()
#data_vec = data_file[19:10000]
data_vec =  main['aggregate'].values.tolist()
delta_p = [round(data_vec[i+1]-data_vec[i],2) for i in range(0,len(data_vec)-1)]
#T = 80;
sigma = 15;
ri = 0.05;
#events = [i for i in range(0, len(delta_p)) if(delta_p[i] > T or delta_p[i] < -T)]
T_Positive = 40;
T_Negative = -40;
event =  [i for i in range(0, len(delta_p)) if (delta_p[i] > T_Positive or delta_p[i] < T_Negative) ]
sigmas = [sigma,sigma/2,sigma/4,sigma/8,sigma/14,sigma/32,sigma/64]
Finalcluster = []
#%%
for k in range(0,len(sigmas)):
  clusters = []
  print('k val is {}'.format(k))
  for i in range(2000): ## change limit
    if i==0:
      event = sorted(list(set(event)-set(clusters))) 
    else:
      event = sorted(list(set(event)-set(clusters[(i-1)])) )
    if not len(event):
      print('event list got empty')
      print('i got empty at value {}'.format(i))
      break
    else:
      clus = gsp.gspclustering_event2(event,delta_p,sigmas[k]);
      clusters.append(clus)
  jt =  gsp.johntable(clusters,Finalcluster,delta_p,ri)
  events_updated = gsp.find_new_events(clusters,delta_p,ri)
  events_updated = sorted(events_updated)
  event = events_updated
  Finalcluster = jt
if len(event) > 0:
  Finalcluster.append(event)
#%% Code ClusterTable_3_H6.m


#%%   iam related data
Ls = 10
L = iam_sub.shape[0]
iam_sub = iam_sub[0:4000]
del_iam = iam_sub.apply(lambda x: [round(x[i+1]-x[i],2) for i in range(0,len(x)-1)],axis=0)
del_iam.keys()
#%% reducing number of clusters
time = main['timestamp'].values.tolist()
time_main= iam_sub['timestamp'].values.tolist()
Table_1 =  np.zeros((len(Finalcluster),5))
winsize = 20
for i in range(len(Finalcluster)):
  Table_1[i,0] = len(Finalcluster[i])
  Table_1[i,1] = np.mean([delta_p[j] for j in Finalcluster[i]])
  Table_1[i,2] = np.std([delta_p[j] for j in Finalcluster[i]],ddof=1)
  Table_1[i,3] =  abs(Table_1[i,3]/ Table_1[i,2])
  #for j in range(len(Finalcluster[i])):
   # judgestart =  

#time < time_main[Finalcluster[i][j] + Ls-1] -winsize
sort_means = np.argsort(Table_1[:,1]).tolist() # returns positions of sorted array
sort_means.reverse() # gives decreasing order
sorted_cluster =[]
FinalTable = []
for i in range(len(sort_means)):
  sorted_cluster.append(Finalcluster[sort_means[i]])
  FinalTable.append(Table_1[sort_means[i]].tolist())
#%% 
#L = len(data_vec)-1
DelP = [round(data_vec[i+1]-data_vec[i],2) for i in range(0,len(data_vec)-1)]
Newcluster_1 = []
Newtable = []
for i in range(0,len(FinalTable)):
  if (FinalTable[i][0]>=5):
    Newcluster_1.append(sorted_cluster[i])
    Newtable.append(FinalTable[i])
Newcluster = Newcluster_1
#%%
for i in range(0,len(FinalTable)):
  if(FinalTable[i][0] < 5 ):
    for j in range(len(sorted_cluster[i])):
      count =  []
      for k in range(len(Newcluster)):
        count.append(norm.pdf(DelP[sorted_cluster[i][j]],Newtable[k][1],Newtable[k][2]))
      asv = [h == max(count) for h in count]
      if sum(asv) == 1:
        johnIndex = count.index(max(count))
      elif DelP[sorted_cluster[i][j]] > 0:
        print("case1",i,j)
        tablemeans = [r[1] for r in Newtable]
        tempelem = [r for r in tablemeans if r < DelP[sorted_cluster[i][j]]][0]
        johnIndex = tablemeans.index(tempelem)
      else:
        print("case else",i,j)
        tablemeans = [r[1] for r in Newtable]
        tempelem = [r for r in tablemeans if r > DelP[sorted_cluster[i][j]]].pop()
        johnIndex = tablemeans.index(tempelem)
      Newcluster[johnIndex].append(sorted_cluster[i][j])
#%%
# Use Newtable and Newclusters for pairing 
clus_means = [i[1] for i in Newtable]
pairs = []

# TODO: handle case for pending clusters which do not cluster  and sometimes more than one positive cluster might will pair with same neg. cluster
for i in range(len(clus_means)):
  if clus_means[i] > 0: # postive edge
    neg_edges = [ (clus_means[i] + clus_means[j],j) for j in range(i+1,len(clus_means)) if clus_means[j] < 0] # find all neg edges and their location in tuple form
    edge_mag = [j[0] for j in neg_edges] # list only edge mags
    match_loc = neg_edges[edge_mag.index(min(edge_mag))][1]
    pairs.append((i,match_loc))
#%% Now
appliance_pairs = feature_matching_module(pairs,DelP)
power_series = generate_appliance_powerseries(appliance_pairs)

#%%


#%% create mat files
import scipy.io
iam_sub.keys()
spath = "/Volumes/MacintoshHD2/Users/haroonr/Documents/MATLAB/"
scipy.io.savemat(spath+"refrigerator",mdict={'refrigerator':iam_sub['refrigerator'].values.tolist()})
scipy.io.savemat(spath+"disposal",mdict={'disposal':iam_sub['disposal'].values.tolist()})
scipy.io.savemat(spath+"dishwaser",mdict={'dishwaser':iam_sub['dishwaser'].values.tolist()})
scipy.io.savemat(spath+"kitchen_outlets",mdict={'kitchen_outlets':iam_sub['kitchen_outlets'].values.tolist()})

scipy.io.savemat(spath+"microwave",mdict={'microwave':iam_sub['microwave'].values.tolist()})
scipy.io.savemat(spath+"lighting",mdict={'lighting':iam_sub['lighting'].values.tolist()})
scipy.io.savemat(spath+"kitchen_outlets.1",mdict={'kitchen_outlets.1':iam_sub['kitchen_outlets.1'].values.tolist()})

scipy.io.savemat(spath+"time",mdict={'time':iam_sub['timestamp'].values.tolist()})
scipy.io.savemat(spath+"time_main",mdict={'time_main':time_main})

