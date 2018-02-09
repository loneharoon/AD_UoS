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
from copy import deepcopy
from itertools import groupby
from collections import OrderedDict,Counter
from datetime import datetime,timedelta
from __future__ import division
#%%
def read_REFIT_groundtruth():
  
  ''' This function reads and formats REFIT's groundtruth file
  return: intelligible pandas dataframe'''
  gt_file = "/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/anomaly_explanation.csv"
  gt_df  = pd.read_csv(gt_file)
  df_temp =  [(i.split(';')[0],i.split(';')[1]) for i in gt_df.Time_Duration.values]
  df_temp =  pd.DataFrame(df_temp)
  df_temp.columns = ["start_time","end_time"]
  
  start_times = [pd.to_datetime(val.replace('"','')) if val.rfind('"')>=0 else pd.to_datetime(val.replace('“','')) for val in df_temp['start_time']]
  end_times = [pd.to_datetime(val.replace('"','')) if val.rfind('"')>=0 else pd.to_datetime(val.replace('”','')) for val in df_temp['end_time']]
  gt_df['start_time'] = start_times
  gt_df['end_time'] = end_times
  return(gt_df)

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
#  print(compute_boxplot_stats(ON_duration))
#  print(compute_boxplot_stats(OFF_duration))
 # print(compute_boxplot_stats(ON_cycles))
  return (summ_dic)

#%%
def  create_testing_stats_with_boxplot(testdata,k,sampling_type,sampling_rate):
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
  if np.std(samp_val) <= 0.2:# contains observations with same values, basically forward filled values
    print("Dropping context {} from analysis as it contains same readings".format(k))
    return (False)
  elif np.std(samp_val) <= 5: # when applaince reamins ON for full context genuinely
    print("Only one state in context {} found".format(k))
    if samp_val[2] > 10:
      temp_lab = [1]* (samp_val.shape[0]-1)
      temp_lab.append(0)
      samp['cluster'] = temp_lab
    else:# when applaince reamins OFF for full context genuinely
      temp_lab = [0]* (samp_val.shape[0]-1)
      temp_lab.append(1)
      samp['cluster'] = temp_lab
  else: # normal case, on and off states of appliance
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
  #print(off_energy)
  on_energy =list(tempval[tempval.cluster==1].energy_state)
  #print(on_energy)
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
#%% Anomaly detection logic
def anomaly_detection_algorithm(test_stats,contexts_stats,alpha,num_std):
  ''' this function defines the anomaly detection logic '''
  LOG_FILENAME = '/Volumes/MacintoshHD2/Users/haroonr/Downloads/REFIT_log/logfile_REFIT.csv'
  with open(LOG_FILENAME,'a') as mylogger:
  
    mylogger.write("\n*****NEW ITERATION at time {}*************\n".format(datetime.now()))
    result = [] 
    for day,data in test_stats.items():
      for contxt,contxt_stats in data.items():
        #be clear - word contexts_stats represents training data and word contxt represents test day stats
        train_results = contexts_stats[contxt] # all relevant train stats
        test_results  = contxt_stats
        temp_res = {}
        temp_res['timestamp'] = datetime.strptime(day,'%Y-%m-%d')
        temp_res['context']   = contxt # denotes part of the day
        temp_res['status']    = 0 # is anomaly
        temp_res['anomtype']  = np.float("Nan") # anomaly type
        # rule 3 of unum
  #      if np.mean(test_results['ON_energy'] >  train_results['ON_energy']['mean'] + num_std* train_results['ON_energy']['std']) and (np.mean(test_results['OFF_energy']) >  train_results['OFF_energy']['mean'] + num_std* train_results['OFF_energy']['std']):
  #        temp_res['status'] = 0
  #        mylogger.write(day + ":" + contxt + "is not elongated anomaly as off time was also longer \n")
  #      # rule 1 of unum
        if np.mean(test_results['ON_energy']) > alpha * train_results['ON_energy']['mean'] + num_std* train_results['ON_energy']['std']:
          temp_res['status'] = 1
          temp_res['anomtype'] = "long"
          mylogger.write(day + ":"+ contxt + ", elongated anomaly" + ", train_stats duration, " + str(train_results['ON_energy']['mean']) + ":"+str(train_results['ON_energy']['std']) + "; test_stats energy, " + str(np.mean(test_results['ON_energy'])) + "\n" )
              # rule 2 of unum
        elif np.mean(test_results['ON_cycles']) >  alpha * train_results['ON_cycles']['mean'] + num_std* train_results['ON_cycles']['std']:
          temp_res['status'] = 1
          temp_res['anomtype'] = "frequent"
          mylogger.write(day + ":"+contxt +  ", frequent anomaly" + ", train_stats frequency, " + str(train_results['ON_cycles']['mean']) + ":"+str(train_results['ON_cycles']['std']) + "; test_stats frequency, " + str(np.mean(test_results['ON_cycles'])) + "\n"  )
        result.append(temp_res)
  res_df = pd.DataFrame.from_dict(result)
  #% rectify timestamps by including appropriate context information
  updated_timestamp = []
  for i in range(0,res_df['context'].shape[0]):
      context = res_df['context'][i]
      timestamp = res_df['timestamp'][i]
      if context == 'night_1_gp':
        timestamp =  timestamp + timedelta(hours=3)
      elif context == 'day_1_gp':
        timestamp =  timestamp + timedelta(hours=9)
      elif context == 'day_2_gp':
        timestamp =  timestamp + timedelta(hours=15)
      elif context == 'night_2_gp':
        timestamp =  timestamp + timedelta(hours=21)
      updated_timestamp.append(timestamp)
  res_df['updated_timestamp'] =  updated_timestamp  
  return(res_df) # returns only anomaly packets
  

#%%
def AD_refit_training(train_data,data_sampling_type,data_sampling_time):
    
    #%create training stats
    """" 1. get data
         2. divide it into 4 contexts 
         3. divide each into day wise
         4. calculate above stats """
    # set training data duration
    #train_data =  df_samp[myapp]['2014-03-07']
    #train_data =  df_samp[myapp]['2014-03']
    
    # divide data according to  4 contexts [defined by times]
    contexts = OrderedDict()
    contexts['night_1_gp'] = train_data.between_time("00:00","05:59")
    contexts['day_1_gp'] = train_data.between_time("06:00","11:59")
    contexts['day_2_gp'] = train_data.between_time("12:00","17:59")
    contexts['night_2_gp'] = train_data.between_time("18:00","23:59")
    #%
    # create groups within contexts day wise, this will allow us to catch stats at day level otherwise preserving boundaries between different days might become difficult
    contexts_daywise = OrderedDict()
    for k,v in contexts.items():
      contexts_daywise[k] = v.groupby(v.index.date)
     #% Compute stats context wise
    contexts_stats = OrderedDict()
    #%
    for k,v in contexts_daywise.items():
      print("CONTEXT IS {}".format(k))
      contexts_stats[k] = create_training_stats(v,sampling_type=data_sampling_type,sampling_rate=data_sampling_time) 
    return contexts_stats
#%%
def AD_refit_testing(test_data,data_sampling_type,data_sampling_time):
    
    test_data_daywise = test_data.groupby(test_data.index.date) # daywise grouping
    test_contexts_daywise = OrderedDict()
    for k,v in test_data_daywise:     # context wise division
      #print(str(k))
      test_contexts= OrderedDict()
      test_contexts['night_1_gp'] = v.between_time("00:00","05:59")
      test_contexts['day_1_gp']   = v.between_time("06:00","11:59")
      test_contexts['day_2_gp']   = v.between_time("12:00","17:59")
      test_contexts['night_2_gp'] = v.between_time("18:00","23:59")
      test_contexts_daywise[str(k)] = test_contexts
    #%
    test_stats = OrderedDict()
    for day,data in test_contexts_daywise.items():
      print("testing for day {}".format(day))
      temp = OrderedDict()
      for context,con_data in data.items():
        #temp[context] = create_testing_stats(con_data,context)
        res = create_testing_stats_with_boxplot(con_data,context,sampling_type=data_sampling_type,sampling_rate=data_sampling_time)
        if res!= False:
          temp[context] = res
        else:
          continue   
      test_stats[day] = temp
    return test_stats
#%%
def tidy_gt_and_ob(house_no,appliance,day_start,day_end,result_sub):
    '''In this I re_format gt and observed results for calculating end results '''
    gt = read_REFIT_groundtruth()
    select_house = gt.House_No==house_no
    select_appliance = gt.Appliance==appliance
    gt_sub = gt[select_house & select_appliance]
    gt_appliance = deepcopy (gt_sub[(gt_sub.start_time >= day_start) & (gt_sub.end_time <= day_end)])
    columns = gt_appliance.columns.values.tolist()
    columns.append('day')
    gt_df = pd.DataFrame(columns= columns)
    for i in range(len(gt_appliance)):
        start = gt_appliance.start_time.iloc[i].date()
        end = gt_appliance.end_time.iloc[i].date()
        temp = gt_appliance.iloc[i]
         # if anomaly continued on more than one day then duplicate rows for th e range
        #days = pd.date_range(start,end) # this creates timestamp object, so dump it 
        total_days = (end - start).days + 1
        days = [start + datetime.timedelta(days=x) for x in range(0, total_days)]
        temp2 = pd.DataFrame([temp]*total_days)
        temp2['day'] = days
        gt_df = gt_df.append(temp2) 
        
    #% # Now format observed results properly
    result_appliance = deepcopy(result_sub)
    # convert timestamp to dates
    result_appliance['day']= result_appliance.updated_timestamp.apply(lambda x: x.date()).tolist()
    # remove duplicated entries
    result_appliance = result_appliance[~result_appliance.duplicated('day')]
    return gt_df,result_appliance  
#%%
def compute_confusion_metrics(gt,ob):
    gt_day = gt.day.values
    ob_day = ob.day.values
    tp=fp=fn = 0
    for i in ob_day:
        if i in gt_day:
            tp = tp + 1
        else:
            fp = fp + 1 
    for j in gt_day:
        if j not in ob_day:
            fn = fn + 1      
    precision = tp/(tp + fp)
    recall = tp/(tp + fn)
    fscore= 2*(precision * recall)/(precision+recall)
    return round(precision,2), round(recall,2),round(fscore,2)  