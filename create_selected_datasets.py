#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
In this script, I subset various homes data for disagg purposes. I keep months for which there are many more anomalies
Created on Tue Feb 13 10:45:20 2018

@author: haroonr
"""
import pandas as pd
#%%
direc = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/CLEAN_REFIT_081116/"
savedir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/REFIT_selected/"
home = "House10.csv"
df = pd.read_csv(direc+home,index_col="Time")
df.index = pd.to_datetime(df.index)
print ('**careful in changing name while calling next function**')
res = subset_House10(df)
res.to_csv(savedir+home)


#%%
def subset_House10(df):  
    df1 = df['2014-04':'2014-06']
    df2 = df['2014-12']
    df_result = pd.concat([df1,df2],axis=2)
    return df_result
    
def subset_House20(df):  
    dfx = df['2014-05':'2014-08']
    return dfx
