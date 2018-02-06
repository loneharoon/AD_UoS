#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
In this I implement Bochao's GSP disaggregation method
Created on Thu Feb  1 15:42:41 2018

@author: haroonr
"""
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import sys, statistics
from scipy.stats import norm
sys.path.append('/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/disaggregation_codes/')
import accuracy_metrics_disagg as acmat
import matplotlib.pyplot as plt
#%%
#import scipy.io
#fpath = "/Volumes/MacintoshHD2/Users/haroonr/Documents/MATLAB/main.mat"
#fl = scipy.io.loadmat(fpath)
#data_file = fl['main'].flatten().tolist()  
reddhome= "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/Redd_dataset/house3/"
main = pd.read_csv(reddhome+"main_meters.csv",index_col="Index")
main = main[0:10000]
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
      clus = gspclustering_event2(event,delta_p,sigmas[k]);
      clusters.append(clus)
  jt =  johntable(clusters,Finalcluster,delta_p,ri)
  events_updated = find_new_events(clusters,delta_p,ri)
  events_updated = sorted(events_updated)
  event = events_updated
  Finalcluster = jt
if len(event) > 0:
  Finalcluster.append(event)
#%% Code ClusterTable_3_H6.m


#%%
Ls = 10
L = iam_sub.shape[0]
iam_sub = iam_sub[0:4000]
del_iam = iam_sub.apply(lambda x: [round(x[i+1]-x[i],2) for i in range(0,len(x)-1)],axis=0)
del_iam.keys()
#%%
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
L = len(data_vec)-1
DelP = [round(data_vec[i+1]-data_vec[i],2) for i in range(0,len(data_vec)-1)]
Newcluster_1 = []
Newtable = []
for i in range(0,len(FinalTable)):
  if (FinalTable[i][0]>=2):
    Newcluster_1.append(sorted_cluster[i])
    Newtable.append(FinalTable[i])
Newcluster = Newcluster_1
for i in range(0,len(FinalTable)):
  if(FinalTable[i][0] < 2 ):
    for j in range(len(sorted_cluster[i])):
      count =  []
      for k in range(len(Newcluster)):
        count.append(norm.pdf(DelP[sorted_cluster[i][j]],Newtable[k][1],Newtable[k][2]))
      asv = [h == max(count) for h in count]
      if len(asv) == 1:
        johnIndex = count.index(max(count))
      elif DelP[sorted_cluster[i][j]] > 0:
        tablemeans = [r[1] for r in Newtable]
        tempelem = [r for r in tablemeans if r < DelP[sorted_cluster[i][j]]][0]
        johnIndex = tablemeans.index(tempelem)
      else:
        tablemeans = [r[1] for r in Newtable]
        tempelem = [r for r in tablemeans if r > DelP[sorted_cluster[i][j]]].pop()
        johnIndex = tablemeans.index(tempelem)
      Newcluster[johnIndex].append(sorted_cluster[i][j])
    
  
#%% pairing module code
tic;
L = length(meter)-1;
% set L as a easier number
DelP(1:L) = meter(2:L+1) - meter(1:L);

[FinalTable,Clusters_2] = ClusterTable_3_H6(FinalCluster,DelP);
NewCluster_1 = [];
NewTable = [];
for i = 1:size(FinalTable,1)
    if FinalTable(i,1)>=5
        NewCluster_1(size(NewCluster_1,1)+1,1:FinalTable(i,1)) = Clusters_2(i,find(Clusters_2(i,:)>0));
        NewTable(size(NewTable,1)+1,:) = FinalTable(i,:);
    end
end
NewCluster = NewCluster_1;
for i = 1:size(FinalTable,1)
    if FinalTable(i,1)<5
        for j = 1:FinalTable(i,1)
            Count = zeros(1,size(NewCluster,1));
            for k = 1: size(NewCluster,1)
                Count(k) = normpdf(DelP(Clusters_2(i,j)),NewTable(k,2),NewTable(k,3));
            end
            asv = find(Count == max(Count));
            if length(asv) == 1
                JohnIndex = asv;
            else
                if  DelP(Clusters_2(i,j)) >0
                    JohnIndex = find(NewTable(:,2) < DelP(Clusters_2(i,j)),1,'first');
                else
                    JohnIndex = find(NewTable(:,2) > DelP(Clusters_2(i,j)),1,'last');
                end
            end
            NewCluster(JohnIndex(1),length(find(NewCluster(JohnIndex(1),:)>0))+1) = Clusters_2(i,j);
        end
    end
end
[NT,NC] = ClusterTable_3_H6(NewCluster,DelP);
toc;
#%%
