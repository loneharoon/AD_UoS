#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This file contains all metrics related to energy disaggregation
Created on Fri Jan 26 10:23:37 2018

@author: haroonr
"""
from __future__ import division
import numpy as np
import pandas as pd
from collections import OrderedDict
#%%
def compute_rmse(gt,pred):
    from sklearn.metrics import mean_squared_error
    rms_error = {}
    for app in gt.columns:
        rms_error[app] =  np.sqrt(mean_squared_error(gt[app],pred[app]))
    return pd.Series(rms_error)

def accuracy_metric_norm_error(dis_result):
    '''Metric taken from Nipuns NILMTK paper:Normalised error in assigned power'''
    pred = dis_result['decoded_power']
    gt = dis_result['actaul_power']
    error = {}
    for app in gt.columns:
        numerator = np.nansum(abs(pred[app].values - gt[app].values))
        denominator = np.nansum(gt[app]) * 1.0
        error[app] = np.divide(numerator,denominator)
    result = pd.DataFrame.from_dict(error, orient='index')
    return result

#%%
def compute_mae(gt,pred):
    ''' compute mean absolute error'''
    from sklearn.metrics import mean_absolute_error
    mae_error = {}
    for app in pred.columns:
        mae_error[app] =  mean_absolute_error(gt[app],pred[app])
    return pd.Series(mae_error)
    
#%%
def diss_accu_metric_kolter_1(dis_result,aggregate):
    pred = dis_result['decoded_power']
    gt = dis_result['actaul_power']
    error = []
    numerator = 0
    for app in gt.columns:
        numerator = numerator + sum(abs(pred[app].values - gt[app].values))
    denominator = aggregate*1.0 # to make it float
    #return (1 - (numerator / denominator))
    return(1-2*(numerator/denominator))

def diss_accu_metric_kolter_exact(dis_result,aggregate):
    pred = dis_result['decoded_power']
    gt = dis_result['actaul_power']
    error = []
    numerator = 0
    for app in gt.columns:
        numerator = numerator + sum(abs(pred[app].values - gt[app].values))
    denominator = aggregate*1.0 # to make it float
    return(1- (numerator/(2*denominator)))



def diss_accu_metric_kolter_2(dis_result, aggregate):
    # dis_result = co_result
    pred = dis_result['decoded_power']
    gt = dis_result['actaul_power']
    error = []
    numerator = 0
    for app in gt.columns:
        numerator = sum(abs(pred[app].values - gt[app].values))
        denominator = aggregate * 1.0  # to make it float
        print (1 - 2*(numerator / denominator))
    #return (1 - (numerator / denominator))

def accuracy_metric_gemello(dis_result):
    '''This per appliance accuracy metric is used in Gamello. Paper mentions that it is based on works 1,7 mentioned in gamello paper'''
    ### this fails when there are 0 values in the denominator
    pred = dis_result['decoded_power']
    gt = dis_result['actaul_power']
    per_accu = {}
    for app in gt.columns:
        per_error = (abs(pred[app].values - gt[app].values)/ (gt[app] * 1.0)) * 100
        per_accu[app] = np.mean(per_error)
        #
    result = pd.DataFrame.from_dict(per_accu, orient='index')
    return result


#%%%% CONFUSION METRICS
#%%
def call_confusion_metrics_on_disagg(test_dset,predict_df):
    #test_dset = fhmm_result['actaul_power']['air1']
    #predict_df = fhmm_result['decoded_power']['air1']  
    #actual = test_dset >= on_power_threshold
    #predict = predict_df >= on_power_threshold
    #compute_confusion_metrics(when_on_actual,when_on_predict) 
    on_power_threshold = 50
    appliances  = predict_df.columns
    results =  OrderedDict()
    for app in appliances:
        actual = test_dset[app]
        predict = predict_df[app]
        when_on_actual = actual >= on_power_threshold
        when_on_predict = predict >= on_power_threshold
        results[app] = compute_confusion_metrics(when_on_actual,when_on_predict) 
    return(results)
#%%
def compute_confusion_metrics(actual,predict):
    res = OrderedDict()
    tp = np.sum(np.logical_and(predict.values == True,
                actual.values == True))
    fp = np.sum(np.logical_and(predict.values == True,
                actual.values == False))
    fn = np.sum(np.logical_and(predict.values == False,
                actual.values == True))
    tn = np.sum(np.logical_and(predict.values == False,
                actual.values == False))
    precision = tp/(tp+fp) 
    recall =  tp/(tp+fn)
    fscore =  2*(precision*recall)/(precision+recall)
    res['precision'] = precision 
    res['recall'] = recall
    res['f_score'] = fscore
    res['accuracy'] =  (tp + tn)/(tp + tn+ fp + fn)
    return (res)
#%%
def compute_EEFI_AEFI_metrics(gt,pred):
    ''' compute eefi(estimated energy  fraction index), aefi (actual energy fraction index) or metric (fraction of toal energy asssigned correctly  of NILMTK paper)'''
    estimated_total = np.sum(pred.apply(np.sum,axis=0))
    actual_total = np.sum(gt.apply(np.sum,axis=0))
    result_dict = {}
    for app in pred.columns:
        aefi = np.sum(gt[app].values)/actual_total
        eefi = np.sum(gt[app].values)/estimated_total
        result_dict[app] = { 'AEFI' : aefi , 'EEFI' : eefi }
    return(pd.DataFrame.from_dict(result_dict))

    
    