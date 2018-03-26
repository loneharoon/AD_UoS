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
from copy import deepcopy
from collections import OrderedDict
#%%
def compute_rmse(gt, pred):
    from sklearn.metrics import mean_squared_error
    rms_error = {}
    for app in gt.columns:
        rms_error[app] =  np.sqrt(mean_squared_error(gt[app],pred[app]))
    return pd.Series(rms_error)

def compute_correlation(gt, pred):
    corr_coeff = {}
    for app in pred.columns:
        corr_coeff[app] =  ( pd.concat([gt[app], pred[app]], axis = 1).corr()).iloc[0][1]      
    return pd.Series(corr_coeff)

def compute_rmse_ver_dict(dis_result):
    from sklearn.metrics import mean_squared_error
    pred = dis_result['decoded_power']
    gt = deepcopy(dis_result['actual_power'])
    try:
        gt = gt.drop(['use'], axis = 1)
    except:
        print("GT does not contain use column\n")
    rms_error = {}
    for app in gt.columns:
        gt_app = gt[app]
        ob_app = pred[app]
        if abs(len(ob_app) - len(gt_app)) == 1:
            #sometimes downsampling  results in extra reading, so remove that entry to make both gt and ob readings equal
            gt_app =  gt_app[:-1]
        rms_error[app] =  np.sqrt(mean_squared_error(gt_app.values, ob_app.values))
    return pd.Series(rms_error)

def compute_correlation_ver_dict(dis_result):
    pred = dis_result['decoded_power']
    gt = deepcopy(dis_result['actual_power'])
    
    try:
        gt = gt.drop(['use'], axis = 1)
        pred = pred.drop(['use'], axis = 1) # in case of LBM results required
    except:
        print("GT does not contain use column\n")
   
    corr_coeff = {}
    for app in pred.columns:
        #print(app)
        gt_app = gt[app]
        pred_app = pred[app]
        if abs(len(pred_app) - len(gt_app)) == 1:
            #sometimes downsampling  results in extra reading, so remove that entry to make both gt and ob readings equal
            gt_app =  gt_app[:-1]
        corr_coeff[app] =  ( pd.concat([gt_app, pred_app], axis = 1).corr()).iloc[0,1]      
    
    return pd.Series(corr_coeff)
def accuracy_metric_norm_error(dis_result):
    '''Metric taken from Nipuns NILMTK paper:Normalised error in assigned power'''
    pred = dis_result['decoded_power']
    gt = deepcopy(dis_result['actual_power'])
    try:
        gt = gt.drop(['use'],axis=1)
    except:
        print("GT does not contain use column\n")
    
    error = {}
    for app in gt.columns:
        gt_app = gt[app]
        ob_app = pred[app]
        if abs(len(ob_app) - len(gt_app)) == 1:
            #sometimes downsampling  results in extra reading, so remove that entry to make both gt and ob readings equal
            gt_app =  gt_app[:-1]
        numerator = np.nansum(abs(ob_app.values - gt_app.values))
        denominator = np.nansum(gt_app) * 1.0
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
    gt = dis_result['actual_power']
    numerator = 0
    for app in gt.columns:
        numerator = numerator + sum(abs(pred[app].values - gt[app].values))
    denominator = aggregate*1.0 # to make it float
    #return (1 - (numerator / denominator))
    return(1-2*(numerator/denominator))

def diss_accu_metric_kolter_exact(dis_result,aggregate):
    pred = dis_result['decoded_power']
    gt = dis_result['actual_power']
    numerator = 0
    for app in gt.columns:
        numerator = numerator + sum(abs(pred[app].values - gt[app].values))
    denominator = aggregate*1.0 # to make it float
    return(1- (numerator/(2*denominator)))
 #%%   
def diss_accu_metric_kolter_appliance_wise(dis_result):
   '''This metric is taken from Makonins paper: Nonintrusive Load Monitoring (NILM) Performance Evaluation A unified approach for accuracy reportin'''
   pred = dis_result['decoded_power']
   gt = dis_result['actual_power']
   accur = OrderedDict()
   for app in gt.columns:
     numerator = sum(abs(pred[app].values - gt[app].values))
     denominator = sum(gt[app].values)
     accur[app] = 1-(numerator/(2*denominator))
   return(pd.Series(accur))


#%%

def diss_accu_metric_kolter_2(dis_result, aggregate):
    # dis_result = co_result
    pred = dis_result['decoded_power']
    gt = dis_result['actual_power']
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
    gt = dis_result['actual_power']
    per_accu = {}
    for app in gt.columns:
        per_error = (abs(pred[app].values - gt[app].values)/ (gt[app] * 1.0)) * 100
        per_accu[app] = np.mean(per_error)
        #
    result = pd.DataFrame.from_dict(per_accu, orient='index')
    return result


#%%%% CONFUSION METRICS
#%%
def call_confusion_metrics_on_disagg(test_dset,predict_df,power_threshold):
    #predict_df = predict_df.drop(['use'],axis=1)
    on_power_threshold = power_threshold
    appliances  = predict_df.columns
    results =  OrderedDict()
    for app in appliances:
        actual = test_dset[app]
        predict = predict_df[app]
        if abs(len(actual) - len(predict)) == 1:
            #sometimes downsampling  results in extra reading, so remove that entry to make both gt and ob readings equal
            actual =  actual[:-1]
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
    try: 
        precision = tp/(tp+fp) 
        recall =  tp/(tp+fn)
        fscore =  2*(precision*recall)/(precision+recall)
    except ValueError:
        print ("Denominator results in error\n")
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
    result_dict = OrderedDict()
    for app in pred.columns:
        aefi = np.sum(gt[app].values)/actual_total
        eefi = np.sum(gt[app].values)/estimated_total
        oneminusdivison  = 1 - (eefi/aefi)
        differencedivion = abs(aefi-eefi)/aefi 
        result_dict[app] = OrderedDict({ 'AEFI' : aefi , 'EEFI' : eefi , 'MinDiv' : oneminusdivison , 'DifDiv' : differencedivion})
    return(pd.DataFrame.from_dict(result_dict))

  #%%
