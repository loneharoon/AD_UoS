#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
In this I compute normalized RMSE from the rmse calculated earlier. Read rmse file and then divide each column by the applianc wattage
Created on Mon Mar 26 11:12:08 2018

@author: haroonr
"""
from __future__ import division
 
#%%

rootd = "/Volumes/MacintoshHD2/Users/haroonr/Downloads/rmse.csv"
df = pd.read_csv(rootd,header = None)
df.index = df.iloc[:,0]
df.drop([0], axis = 1 , inplace = True)

# these wattages are in home order and appliance order recoreded on notebook also, home order is 1,10,16,18 and 20
appliance_wattage = [2200,200,83,50,1000,80,
                     1800,140,80,2100,80,100,
                     2200,70,200,84,100,700,
                     2800,100,175,140,130,120,
                     2200,90,2600,85,115,1600]
for i in range(df.shape[1]):
    df.iloc[:,i] =  df.iloc[:,i] / appliance_wattage[i]

df = df.round(2)
df.to_csv("/Volumes/MacintoshHD2/Users/haroonr/Downloads/normalized_rmse.csv" ,sep = '&')
