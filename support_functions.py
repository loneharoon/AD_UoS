#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This includes all support function which are called from other scripts of the project
Created on Wed Nov 22 12:02:44 2017

@author: haroonr
"""
import seaborn as sns
sns.set(style="ticks",color_codes=True)
import matplotlib.pyplot as plt

def plot_facet_plots(df_local):
  
  """ this function creates a facet plot with 7 columns"""
  h =  sns.FacetGrid(df_local,col='day',col_wrap=7,size=2.5)
  h = (h.map_dataframe(plt.plot,'timestamp','power')
      .set_axis_labels("Timestamp","Power(kW)")
      .fig.subplots_adjust(wspace=.2,hspace=.5))
  return h
  