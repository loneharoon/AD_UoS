#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Experiment: Here I try to create a NILM metric which will summarise NILM performance for AD algorithm
steps : 1. genertate two series
        2. use various existing measures to measure similarity
Created on Fri Mar 23 09:50:27 2018

@author: haroonr
"""


from __future__ import division
from copy import deepcopy
import pandas as pd
import numpy as np
import sys
sys.path.append('/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/disaggregation_codes/')

#import accuracy_metrics_disagg as acmat
#import matplotlib.pyplot as plt
#%%
def generate_pandasseries(timestart, hours, upper_mag = 10, frequency = 1, dutycycle = 0.5, sampling_type = 'minutes'):
    """ """
    from scipy import signal
    import random as rnd
    if sampling_type == "seconds":   
        t = np.linspace(0, hours, 60*60*hours, endpoint = False)# generate time sequence
        sig = signal.square(2 * np.pi *frequency* t, duty = dutycycle)
        sig2 = [round(rnd.gauss(upper_mag,1), 2) if a==1 else 0 for a in sig]
        ind = pd.date_range(timestart, periods = len(sig2), freq = 'S')
    elif sampling_type == "minutes":
        t = np.linspace(0, hours, 60*hours, endpoint = False)# generate time sequence
        sig = signal.square(2 * np.pi *frequency* t, duty = dutycycle)
        sig2 = [round(rnd.gauss(upper_mag,1),2) if a == 1 else 0 for a in sig]
        ind = pd.date_range(timestart, periods = len(sig2), freq = 'T')
    pdseries = pd.Series(data = sig2, index = ind)
    return(pdseries)

#%% case 1: exactly same
df1 = generate_pandasseries(timestart = '2011-06-01 0:00:00', hours = 6,  upper_mag = 1000, frequency = 2., dutycycle = 0.5, sampling_type = 'minutes')
df2 = generate_pandasseries(timestart = '2011-06-01 0:00:00', hours = 6,  upper_mag = 900, frequency = 3., dutycycle = 0.5, sampling_type = 'minutes')
pd_cat = pd.concat([df1, df2], axis = 1)
pd_cat.columns = ['actual', 'predicted' ]
gt = df1.to_frame()
pred = df2.to_frame()
rmse_score = acmat.compute_rmse(gt, pred)
#print(round(pd_cat.corr()[0][1],2))
pd_cat.plot(title = 'RMSE:' + str(round(rmse_score.values[0],1)) + 'Cor.:' + str(round(pd_cat.corr()[0][1],2) ))
#%% case 2: 50 percent same
df1 = generate_pandasseries(timestart = '2011-06-01 0:00:00', hours = 24,  upper_mag = 1000, frequency = 2., dutycycle = 0.5, sampling_type = 'minutes')
df21 = generate_pandasseries(timestart = '2011-06-01 0:00:00', hours = 12,  upper_mag = 1000, frequency = 2., dutycycle = 0.5, sampling_type = 'minutes')
df22 = generate_pandasseries(timestart = '2011-06-01 12:00:00', hours = 12,  upper_mag = 500, frequency = 2., dutycycle = 0.5, sampling_type = 'minutes')
df2 = pd.concat([df21, df22], axis = 0)
pd_cat = pd.concat([df1, df2], axis = 1)
pd_cat.columns = ['actual', 'predicted' ]
print(pd_cat.corr())
pd_cat.plot()
#%%
gt = df1.to_frame()
pred = df2.to_frame()
rmse_score = acmat.compute_rmse(gt, pred)
print(rmse_score)
