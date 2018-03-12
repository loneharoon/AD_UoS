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
import AD_support as ads
from collections import OrderedDict
from copy import deepcopy
from collections import defaultdict
import standardize_column_names

#%%
dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/REFIT_selected/"
home = "House20.csv"
df = pd.read_csv(dir+home,index_col="Time")
df.index = pd.to_datetime(df.index)
df_sub = deepcopy(df[:])
#% Resampling data
#TODO : TUNE ME
resample = True
data_sampling_time = 1 #in minutes
data_sampling_type = "minutes" # or seconds
if resample: 
  df_samp = df_sub.resample('1T',label='right',closed='right').mean()
  df_samp.drop('Issues',axis=1,inplace=True)
  standardize_column_names.rename_appliances(home,df_samp) # this renames columns
  #df_samp.rename(columns={'Aggregate':'use'},inplace=True) # renaming agg column
  print("*****RESAMPling DONE********")
  if home == "House16.csv":
      df_samp = df_samp[df_samp.index!= '2014-03-08'] # after resamping this day gets created 
else:
  df_samp = deepcopy(df_sub)
  df_samp.drop('Issues',axis=1,inplace=True)
  standardize_column_names.rename_appliances(home,df_samp) # this renames columns  

energy = df_samp.sum(axis=0)
high_energy_apps = energy.nlargest(7).keys() # CONTROL : selects few appliances
df_selected = df_samp[high_energy_apps]
#%
#TODO : TUNE ME
denoised = False
if denoised:
    # chaning aggregate column
    iams = high_energy_apps.difference(['use'])
    df_selected['use'] = df_selected[iams].sum(axis=1)
    print('**********DENOISED DATA*************8')
train_dset,test_dset = ads.get_selected_home_data(home,df_selected)
#%% READING REFIT HOME 10 SELECTED [used only during comparison for Matlab results]
#readdir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/REFIT_selected/"
#home = "gsp_refit_home10.csv"
#df = pd.read_csv(readdir+home,index_col="Time")
#df.index = pd.to_datetime(df.index)
#main =  df['Aggregate'].values.tolist() # len= 426732
#main = main[0:15000] # 3 days data
#%%
main = train_dset['use']
main_val = main.values
main_ind = main.index
#%%
data_vec =  main_val
delta_p = [round(data_vec[i+1]-data_vec[i],2) for i in range(0,len(data_vec)-1)]
sigma = 40;
ri = 0.1;
T_Positive = 40;
T_Negative = -40;
event =  [i for i in range(0, len(delta_p)) if (delta_p[i] > T_Positive or delta_p[i] < T_Negative) ]
Finalcluster = gsp.refined_clustering_block(event, delta_p, sigma, ri)
#%% Here i count number of members of each cluster, their mean and standard deviation and store such stats in Table_1. Next, I sort 'Finalcluster' according to cluster means in decreasing order. 
Table_1 =  np.zeros((len(Finalcluster),4))
for i in range(len(Finalcluster)):
  Table_1[i,0] = len(Finalcluster[i])
  Table_1[i,1] = np.mean([delta_p[j] for j in Finalcluster[i]])
  Table_1[i,2] = np.std([delta_p[j] for j in Finalcluster[i]],ddof=1)
  Table_1[i,3] =  abs(Table_1[i,2]/ Table_1[i,1])
#% sorting module
sort_means = np.argsort(Table_1[:,1]).tolist() # returns positions of sorted array
sort_means.reverse() # gives decreasing order
sorted_cluster =[]
FinalTable = []
for i in range(len(sort_means)):
  sorted_cluster.append(Finalcluster[sort_means[i]])
  FinalTable.append(Table_1[sort_means[i]].tolist())
#%% 
# Here I reduce number of clusters. I keep clusters with more than or equal 'instancelimit' members as such and in next cell I merge cluster with less than 5 members to clusters with more than 'instancelimit' members 
DelP = [round(data_vec[i+1]-data_vec[i],2) for i in range(0,len(data_vec)-1)]
Newcluster_1 = []
Newtable = []
intancelimit = 20
for i in range(0,len(FinalTable)):
  if (FinalTable[i][0] >= intancelimit):
    Newcluster_1.append(sorted_cluster[i])
    Newtable.append(FinalTable[i])
Newcluster = Newcluster_1
#% merge cluster with less than intancelimit members to clusters with more than 5 members 
for i in range(0,len(FinalTable)):
  if(FinalTable[i][0] < intancelimit ):
    for j in range(len(sorted_cluster[i])):
      count =  []
      for k in range(len(Newcluster)):
        count.append(norm.pdf(DelP[sorted_cluster[i][j]],Newtable[k][1],Newtable[k][2]))
      asv = [h == max(count) for h in count]
      if sum(asv) == 1:
        johnIndex = count.index(max(count))
      elif DelP[sorted_cluster[i][j]] > 0:
        #print("case1",i,j)
        tablemeans = [r[1] for r in Newtable]
        tempelem = [r for r in tablemeans if r < DelP[sorted_cluster[i][j]]][0]
        johnIndex = tablemeans.index(tempelem)
      else:
        #print("case else",i,j)
        tablemeans = [r[1] for r in Newtable]
        tempelem = [r for r in tablemeans if r > DelP[sorted_cluster[i][j]]].pop()
        johnIndex = tablemeans.index(tempelem)
      Newcluster[johnIndex].append(sorted_cluster[i][j])
# updating table means in new table
Table_2 =  np.zeros((len(Newcluster),4))
for i in range(len(Newcluster)):
  Table_2[i,0] = len(Newcluster[i])
  Table_2[i,1] = np.mean([delta_p[j] for j in Newcluster[i]])
  Table_2[i,2] = np.std([delta_p[j] for j in Newcluster[i]],ddof=1)
  Table_2[i,3] =  abs(Table_2[i,2]/ Table_2[i,1])
Newtable = Table_2
#%% Ideally, number of positive clusters should be equal to negative clusters. if one type is more than the other then we merge extra clusters until we get equal number of postive and negative clusters
pos_clusters = neg_clusters = 0
for i in range(Newtable.shape[0]):
    if Newtable[i][1] > 0:
        pos_clusters += 1
    else:
        neg_clusters += 1
Newcluster_cp = deepcopy(Newcluster)
# merge until we get equal number of postive and negative clusters
while pos_clusters != neg_clusters:
    index_cluster = Newcluster_cp
    power_cluster = []
    for i in index_cluster:
        list_member = []
        for j in i:
            list_member.append(delta_p[j])
        power_cluster.append(list_member)
        
    clustermeans = [np.mean(i) for i in power_cluster]
    postive_cluster_chunk= []
    negative_cluster_chunk = []
    postive_cluster_means= []
    negative_cluster_means = []
    pos_clusters = neg_clusters = 0
    for j in range(len(clustermeans)):
       if clustermeans[j] > 0:
            pos_clusters += 1
            postive_cluster_chunk.append(index_cluster[j])
            postive_cluster_means.append(clustermeans[j])    
       else:
            neg_clusters += 1
            negative_cluster_chunk.append(index_cluster[j])
            negative_cluster_means.append(clustermeans[j])
            
    if pos_clusters > neg_clusters:
         print ('call positive')
         postive_cluster_chunk = gsp.find_closest_pair(postive_cluster_means, postive_cluster_chunk)
    elif neg_clusters > pos_clusters:
         print ('call negative')
         negative_cluster_chunk = gsp.find_closest_pair(negative_cluster_means, negative_cluster_chunk)
    else:
        pass
    Newcluster_cp = postive_cluster_chunk + negative_cluster_chunk        

#%%
# Use Newcluster_cp for pairing. Basically here we combine one postive cluster with one negative cluster, which corresponds to ON and OFF instances of the same appliance
clus_means = []
for i in Newcluster_cp:
    list_member = []
    for j in i:
        list_member.append(delta_p[j])
    clus_means.append(np.mean(list_member))    
pairs = []
for i in range(len(clus_means)):
  if clus_means[i] > 0: # postive edge
    neg_edges = [ (abs(clus_means[i] + clus_means[j]),j) for j in range(i+1,len(clus_means)) if clus_means[j] < 0] # find all neg edges and their location in tuple form
    edge_mag = [j[0] for j in neg_edges] # 0 corresponds to list magnitude in the tuple
    match_loc = neg_edges[edge_mag.index(min(edge_mag))][1]
    pairs.append((i,match_loc))
#%%
# while looking at pairs, we find that there are cases where more than one positive edge has piaired with more than one negative edge. To solve this issue, we fill process again this pairing process. step 1: save this in default dic by negative edge wise step 2: see with which positive edge matches the negative edge matches the most
pairs_temp = deepcopy(pairs)
dic_def = defaultdict(list)
for value,key in pairs:
    dic_def[key].append(value)
#%
updated_pairs= []
for neg_edge in dic_def.keys():
    #neg_edge= 35
    pos_edges = dic_def[neg_edge]
    if len(pos_edges) >1:
        candidates = [abs(clus_means[edge]+ clus_means[neg_edge]) for edge in pos_edges]
        good_pos_edge =  [el_pos for el_pos in range(len(candidates)) if candidates[el_pos] == min(candidates)][0]
        good_pair = (pos_edges[good_pos_edge],neg_edge)
    else:
        good_pair = (pos_edges[0],neg_edge)
    updated_pairs.append(good_pair)
alpha = 0.6
beta = 0.4
appliance_pairs = gsp.feature_matching_module(updated_pairs,DelP, Newcluster_cp,alpha,beta)
#%
power_series = gsp.generate_appliance_powerseries(appliance_pairs,DelP)
power_timeseries = gsp.create_appliance_timeseries_signature(power_series,main_ind)
gsp_result = pd.concat(power_timeseries,axis=1)
mapped_names = gsp.map_appliance_names(train_dset,gsp_result)
gsp_result.rename(columns=mapped_names,inplace=True)
gsp_result.plot(subplots=True)
#%%
fig,axes = plt.subplots(nrows=9,ncols=2,sharex=False,sharey=False,figsize=(12,15))
app =0
for ax in range(len(power_series)//2):
    axes[ax,0].plot(power_series[app].timestamp,power_series[app].power)
    app+=1
    axes[ax,1].plot(power_series[app].timestamp,power_series[app].power)
    app+=1
#fig.savefig("gsp.png")
#%% create mat files

fig,axes = plt.subplots(nrows=9,ncols=2,sharex=False,sharey=False,figsize=(12,15))
app =0
for ax in range(len(power_timeseries)//2):
    axes[ax,0].plot(power_timeseries[app])
    app+=1
    axes[ax,1].plot(power_timeseries[app])
    app+=1

#%%
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
#%%   iam related data
#Ls = 10
#L = iam_sub.shape[0]
#iam_sub = iam_sub[0:4000]
#del_iam = iam_sub.apply(lambda x: [round(x[i+1]-x[i],2) for i in range(0,len(x)-1)],axis=0)
#del_iam.keys()
