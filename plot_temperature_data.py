#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
I use this script to plot the temperature data month wise. Each pdf page shows days of a month
Created on Fri Dec  1 15:13:08 2017

@author: haroonr
"""
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
exec(open("/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/support_functions.py").read())
#%%
dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/weather_Midlands_complete.csv"
df  = pd.read_csv(dir,index_col="timestamp")
df.index = pd.to_datetime(df.index)
df['date'] = df.index.date
df["time"] = df.index.hour *60 + df.index.minute
df_groups = pd.groupby(df,[df.index.year,df.index.month])
#%%
savefile="/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/plots/REFITtemperature.pdf"
with PdfPages(savefile) as pdf:
  for key,value in df_groups:
    s = plot_temperature_plots(value)
    pdf.savefig(s)
