#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This differs from plot_REFIT.py becuase here I repeat the same procedure for all
houses. It automates all file reading and saving results appropriately.
Created on Wed Nov 22 11:30:37 2017

@author: haroonr
"""

#%%
#%matplotlib inline
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import os
#%%
#dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/dataset_10mins/"
dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/dataset_default/"
savedir_home = "/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/plots/"
exec(open("/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/support_functions.py").read)
home = "House1.csv"
df = pd.read_csv(dir+home,index_col="localminute")
df.index = pd.to_datetime(df.index)
#%%
# this plots data of each appliance separtely in row fashion manner
req_folder = savedir_home + home.split(".")[0] + "/"
if not os.path.exists(req_folder):
  os.makedirs(req_folder)
df = df/1000
df.plot(subplots=True,figsize=(12,10))
plt.savefig(req_folder+"all_meters.pdf")
#plt.close()
#%%
meters = df.columns
for i in range(0,meters.size):
  meter_name = meters[i]
  temp = df[meter_name]
  temp = temp.to_frame()
  temp['day'] = temp.index.date
  temp['timestamp'] = temp.index.hour * 60 + temp.index.minute
  temp  =  temp.rename(columns={meter_name : 'power'})
  grouped_1 = temp.groupby([temp.index.year,temp.index.month])
  pdf_file_name = req_folder + meter_name + ".pdf"
  with PdfPages(pdf_file_name) as pdf:
    for i, group in grouped_1:
      plt.figure()
      ob = plot_facet_plots(group)
      pdf.savefig(ob)
