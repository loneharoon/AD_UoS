#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inludes all supporting functions for gsp disaggregation
Created on Fri Feb  2 12:09:27 2018

@author: haroonr
"""

from __future__ import division 
import numpy as np
import pandas as pd
from collections import OrderedDict
#%%
def gspclustering_event2(event,delta_p,sigma):
  winL = 1000
  Smstar = np.zeros((len(event),1))
  #for k in range(0,len(event),winL):
  for k in range(0,int(np.floor(len(event)/winL))):
    r = []
    print('k val is {}'.format(k))
    event_1 =  event[k*winL:((k+1)*winL)]
    # followed as such from the MATLAB code
    r.append(delta_p[event[0]])
    [r.append(delta_p[event_1[i]]) for i in range(0,len(event_1))]
    templen = winL + 1
    Sm = np.zeros((templen,1))
    Sm[0] = 1;

    Am = np.zeros((templen,templen))
    for i in range(0,templen):
      for j in range(0,templen):
         #print(i,j)
         #print('\n')
         Am[i,j] = np.exp(-((r[i]-r[j])/sigma)**2);
         #Gaussian kernel weighting function
    Dm = np.zeros((templen,templen));
    # create diagonal matrix
    for i in range(templen):
      Dm[i,i] = np.sum(Am[:,i]);
    Lm = Dm - Am;
    Smstar[k*winL:(k+1)*winL] = np.matmul(np.linalg.pinv(Lm[1:templen,1:templen]), ((-Sm[0].T) * Lm[0,1:templen]).reshape(-1,1));
  # for remaining elements of the event list
  if (len(event)%winL > 1):
    r = []
    event_1 =  event[int(np.floor(len(event)/winL))*winL:]
    newlen = len(event_1) + 1
    r.append(delta_p[event[0]])
    [r.append(delta_p[event_1[i]]) for i in range(0,len(event_1))]
    Sm = np.zeros((newlen,1))
    Sm[0] = 1;
    Am = np.zeros((newlen,newlen))
    for i in range(newlen):
      for j in range(newlen):
         #print(i,j)
         #print('\n')
         Am[i,j] = np.exp(-((r[i]-r[j])/sigma)**2);
         #Gaussian kernel weighting function
    Dm = np.zeros((newlen,newlen));
    for i in range(newlen):
      Dm[i,i] = np.sum(Am[:,i]);
    Lm = Dm - Am;
    Smstar_temp = np.matmul(np.linalg.pinv(Lm[1:newlen,1:newlen]), ((-Sm[0].T) * Lm[0,1:newlen]).reshape(-1,1));
    Smstar[(int(np.floor(len(event)/winL))*winL):len(event)] = Smstar_temp
  cluster = [event[i] for i in range(len(Smstar)) if (Smstar[i] > 0.98)]
  return cluster
#%%

def johntable(clusters,precluster,delta_p,ri):
  import math
  for h in range(0,len(clusters)):  
    stds = np.std([delta_p[i] for i in clusters[h]],ddof=1)
    if(math.isnan(stds)):
      stds = 0
    means = np.mean([delta_p[i] for i in clusters[h]])
    if abs(stds/means) <= ri :
      precluster.append([i for i in clusters[h]])
  return precluster

#%%
def find_new_events(clusters,delta_p,ri):
  ''' This differs from johntable function in line containing divison statemen'''
  import math
  newevents = []
  for h in range(0,len(clusters)):  
    stds = np.std([delta_p[i] for i in clusters[h]],ddof=1)
    if(math.isnan(stds)):
      stds = 0
    means = np.mean([delta_p[i] for i in clusters[h]])
    if abs(stds/means) > ri :
      newevents.append([i for i in clusters[h]])
  newevents = [subitem for item in newevents for subitem in item]
  return newevents

#%%
def feature_matching_module(pairs,DelP,Newcluster):
    alpha = 0.7
    beta = 0.3
    appliance_pairs = OrderedDict()
    for i in range(len(pairs)):
      pos_cluster = sorted(Newcluster[pairs[i][0]])
      neg_cluster = sorted(Newcluster[pairs[i][1]])
      flag = 0
      state_pairs = []
      for j in range(len(pos_cluster)):
         if j==len(pos_cluster)-1:  # last postive element
             flag = 1 
             start_pos = pos_cluster[j]
         if flag:
             neg_set = [h for h in neg_cluster if (h > start_pos)]
         else:
             start_pos = pos_cluster[j]
             next_pos = pos_cluster[j+1]
             if (next_pos - start_pos) == 1:  #shows both are consecutive to one another, so skip
                 continue
             neg_set = [h for h in neg_cluster if (h > start_pos and h< next_pos)]
         if len(neg_set)==1:
             #pair the postive and neg edges
             pair= (start_pos,neg_set[0])
             state_pairs.append(pair)
         elif len(neg_set)==0: # no negative edge found
             print("No negativ edge found for postive edge: {}".format(start_pos))
             continue
         else:
            #print ("implement it")
             #print (j)
             # TODO : MAKE SURE IT IS DELP ONLY AND NOT ACTUAL CONSUMPTION
             phi_m = [DelP[h]+DelP[start_pos] for h in neg_set]
             phi_t = [(h-start_pos) for h in neg_set]
             newlen= len(neg_set)
             Am = np.zeros((newlen,newlen))
             At = np.zeros((newlen,newlen))
             sigma = 1 # cofirmed with Bochao
             for k in range(newlen):
                 for p in range(newlen):
                     Am[k,p] = np.exp(-((phi_m[k]-phi_m[p])/sigma)**2);
             for k in range(newlen):
                 for p in range(newlen):
                     At[k,p] = np.exp(-((phi_t[k]-phi_t[p])/sigma)**2);
             Dm = np.zeros((newlen,newlen));
             for z in range(newlen):
                 Dm[z,z] = np.sum(Am[:,z]);
             Lm = Dm - Am;
             Sm = np.zeros((newlen,1))
             Sm[0] = np.average(phi_m)
             Smstar = np.matmul(np.linalg.pinv(Lm[0:newlen,0:newlen]), ((-Sm[0].T) * Lm[0,0:newlen]).reshape(-1,1))
             Dt = np.zeros((newlen,newlen));
             for z in range(newlen):
                 Dt[z,z] = np.sum(At[:,z]);
             Lt = Dt - At;
             St = np.zeros((newlen,1))
             St[0] = np.median(phi_t)
             Ststar = np.matmul(np.linalg.pinv(Lt[0:newlen,0:newlen]), ((-St[0].T) * Lt[0,0:newlen]).reshape(-1,1))
             result_vec = []
             for f in range(Smstar.shape[0]):
                 temp=alpha * Smstar[f][0] + beta  * Ststar[f][0]
                 result_vec.append(temp)
             best_pos = [a for a in range(len(result_vec)) if (result_vec[a] == min(result_vec))][0]
             pair = (start_pos,neg_set[best_pos])
             state_pairs.append(pair)
      appliance_pairs[i] = state_pairs
      return appliance_pairs
#%%
def generate_appliance_powerseries(appliance_pairs,DelP):
    ''' generates full power series of appliances'''
    for i in range(len(appliance_pairs)):
        events = appliance_pairs[i]
        appliance_signature = OrderedDict()
        timeseq= []
        powerseq  = []
        for event in events:
            start= event[0]
            end = event[1]
            duration = end - start
            instance = []
            instance.append([DelP[start]])
            temp= np.repeat(np.nan,duration-1).tolist()
            instance.append(temp)
            instance.append([abs(DelP[end])])
            final = [j for sub in instance for j in sub]
            timeval = range(start,end+1,1)
            #print (event)
            powerval = interpolate_values(final) if sum(np.isnan(final)) else final
            timeseq.append(timeval)
            powerseq.append(powerval)
        powerseq =  [j for sub in powerseq for j in sub]
        timeseq =  [j for sub in timeseq for j in sub]
        appliance_signature[i] = pd.DataFrame({'timestamp':timeseq,'power':powerseq})
    return appliance_signature
    
#%%
def interpolate_values(A):
    ''' fills values between pairs of events'''
    if type(A) ==list :
        A= np.array(A)
    ok = -np.isnan(A)
    xp = ok.nonzero()[0]
    fp = A[-np.isnan(A)]
    x  = np.isnan(A).nonzero()[0]
    A[np.isnan(A)] = np.interp(x, xp, fp)
    A = [round(i) for i in A]
    return A