#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inludes all supporting functions for gsp disaggregation
Created on Fri Feb  2 12:09:27 2018

@author: haroonr
"""
import numpy as np

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
