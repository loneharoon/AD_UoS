#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 13:28:25 2018

@author: haroonr
"""
import pandas as pd
import os
import my_utilities as myutil
import matplotlib.pyplot as plt
#%%
def plot_bind_save_pdf(actual_data, test_data, fp_list, technique, home, myapp, restype):
    if len(fp_list) < 1:
        return
    
    for i in range(len(fp_list)): 
        fpdate = str(fp_list[i])
        df = pd.concat([actual_data[fpdate],test_data[fpdate]],axis = 1)
        #restype = 'fp'
        df.columns = ['submetered',technique]
        ax = df.plot(title = home.split('.')[0] + "-" + myapp + "-" + restype, figsize = (12,3))
        fig = ax.get_figure()
        savedir = "/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/intresting_plots/"
        savedir = savedir + restype + "/"
        fig.savefig(savedir + fpdate + "-" + myapp + "-" + technique + ".pdf", bbox_inches='tight')
        plt.close()
    #% now combine pdfs
    #rootdir = "/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/intresting_plots/fp/"
    file_list = [savedir + i for i in os.listdir(savedir) if i.endswith(".pdf")]
    saveresult = "/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/intresting_plots/"
    saveresult = saveresult + restype + ".pdf"
    myutil.create_pdf_from_pdf_list(file_list, saveresult)
    for i in file_list: # delete individual files
      os.remove(i)