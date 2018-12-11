#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File used extensively for answering AppliedEnergy Queries
Created on Tue Dec 11 17:14:50 2018

@author: haroonr
"""



def AD_refit_training(train_data, data_sampling_type, data_sampling_time, NoOfContexts, appliance):
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
    if appliance =="ElectricHeater":
        print("AD module for ElectricHeater called")
        for k,v in contexts_daywise.items():
            print("Contexts are {}".format(k))
            contexts_stats[k] = create_training_stats_ElectricHeater(v,sampling_type=data_sampling_type,sampling_rate=data_sampling_time)
    else:
        print("AD module for {} called".format(appliance))
        for k,v in contexts_daywise.items():
            print("Contexts are {}".format(k))
            contexts_stats[k] = create_training_stats(v,sampling_type=data_sampling_type,sampling_rate=data_sampling_time) 
    return contexts_stats