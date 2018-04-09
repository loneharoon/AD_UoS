#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IN this I will apply low pass filter on NILM output and see the effect on the signal
Created on Mon Apr  9 11:37:37 2018

@author: haroonr
"""

from scipy import signal
import matplotlib.pyplot as plt
import numpy as np
#%%
data_tm = test_data['2014-06-30']
data = data_tm.values
b, a = signal.butter(50,0.00138, 'low', analog = True)
output = signal.filtfilt(b, a, data)
plt.plot(output)
#%%
actual = actual_data['2014-06-03']
plt.plot(np.fft.fft(actual))