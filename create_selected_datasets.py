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
print ('**Be careful while changing name of next calling function**')
res = subset_House10(df)
res.to_csv(savedir+home)


#%%
def subset_House10(df):  
    df1 = df['2014-04':'2014-06']
    #df2 = df['2014-12']
    #df_result = pd.concat([df1,df2],axis=0)
    return df1
    #return df_result
    
def subset_House20(df):  
    dfx = df['2014-05':'2014-08']
    return dfx

def subset_House16(df):  
    #dfx = df['2014-03':'2014-06']
    df1 = df['2014-03-01':'2014-03-07']# dropping day 8
    df2 = df['2014-03-09':'2014-06']
    df_result = pd.concat([df1,df2],axis=0)
    return df_result
def subset_House18(df):  
    dfx = df['2014-07':'2014-10']
    return dfx
def subset_House1(df):  
    df1 = df['2014-12']
    df2 = df['2015-01':'2015-03']
    df_result = pd.concat([df1,df2],axis=0)
    return df_result
#%%
    

