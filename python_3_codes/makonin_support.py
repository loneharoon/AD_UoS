#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
It works in python 3 only
This file contains support files of Makononins SparseHMM code
Created on Mon Mar  5 11:56:25 2018

@author: haroonr
"""

import sys
sys.path.append('/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/python_3_codes/')
from libPMF import EmpiricalPMF
from libSSHMM import SuperStateHMM, frange

ε = 0.00021
import pandas as pd



#%%
def create_train_model(train_dset,ids,max_states,max_obs,precision):
  
  sshmms = []
  print('Creating load PMFs and finding load states...')
  print('\tMax partitions per load =', max_states)
  pmfs = []
  for id in ids:
      pmfs.append(EmpiricalPMF(id, max_obs * precision, list(train_dset[id].astype(int))))
      pmfs[-1].quantize(max_states, ε)
  #%
  print()
  print('Creating compressed SSHMM...')
  incro = 1 / precision
  sshmm = SuperStateHMM(pmfs, [i for i in frange(0, max_obs + incro, incro)])
  
  print('\tConverting DataFrame in to obs/hidden lists...')
  #%
  #tempme = deepcopy(train_dset)
  train_dset = train_dset.astype(int)
  #len(train_dset)
  
  obs_id = list(train_dset)[0]
  obs = list(train_dset[obs_id])
  hidden = [i for i in train_dset[ids].to_records(index=False)]
  
  sshmm.build(obs, hidden)
  sshmms.append(sshmm)
  return sshmms
#%%  
def perform_testing(test_dset,sshmms,labels,disagg_algo,limit):
  
  testing = test_dset.astype(int)
  fold = 0
  #tm_start = time()    
  sshmm = sshmms[fold]
  obs_id = list(testing)[0]
  obs = list(testing[obs_id])
  hidden = [i for i in testing[labels].to_records(index=False)]
  
  print()
  print('Begin evaluation testing on observations, compare against ground truth...')
  print()
  #pbar = ''
  #pbar_incro = len(testing) // 20
  #%
  ## code block by haroon:
  #handle = open("dummresults.csv",'a')
  gt = []
  pred = []
  for i in range(1, len(obs)):
          #multi_switches_count += (sum([i != j for (i, j) in list(zip(hidden[i - 1], hidden[i]))]) > 1)
      
          y0 = obs[i - 1]
          y1 = obs[i]
          
          #start = time() 
          #print(y0,y1)
          (p, k, Pt, cdone, ctotal) = disagg_algo(sshmm, [y0, y1])
          #elapsed = (time() - start)
  
          s_est = sshmm.detangle_k(k)
          y_est = sshmm.y_estimate(s_est, breakdown=True)
          
          y_true = hidden[i]
          #s_true = sshmm.obs_to_bins(y_true)
  
          #acc.classification_result(fold, s_est, s_true, sshmm.Km)
          #acc.measurement_result(fold, y_est, y_true)
          gt.append(y_true)
          pred.append(y_est)
          #handle.write(str(fold)+'\t')
          #handle.write(str(y_est)+'\t')
          #handle.write(str(y_true)+'\n')
  
          if limit != 'all' and i >= limit:
              print('\n\n *** LIMIT SET: Only testing %d obs. Testing ends now!' % limit)
              break;
  #handle.close() 
  gt  =  pd.DataFrame.from_records(gt)
  gt.columns = labels
  gt.index = test_dset.index[1:] # becuase we skip first obs in for loop
  gt['use'] = obs[1:] # adding aggregate column for accuracy metrics calculation
  pred = pd.DataFrame.from_records(pred)
  pred.columns = labels   
  pred.index = test_dset.index[1:]  
  data_dic = {}
  data_dic['decoded_power'] = pred
  data_dic['actual_power'] = gt
  return data_dic    
  #test_times.append((time() - tm_start) / 60)
