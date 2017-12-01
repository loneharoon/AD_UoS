#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This includes all support function which are called from other scripts of the project
Created on Wed Nov 22 12:02:44 2017

@author: haroonr
"""
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

def plot_facet_plots(df_local):
  
  """ this function creates a facet plot with 7 columns
  Used to plot power consumtpion of appliances"""
  h =  sns.FacetGrid(df_local,col='day',col_wrap=7,size=2.5,sharey=False)
  h = (h.map_dataframe(plt.plot,'timestamp','power')
      .set_axis_labels("Timestamp","Power(W)")
      .fig.subplots_adjust(wspace=.2,hspace=.5))
  return h
  
def plot_facet_plots_years(df_local,savedir):
  
  """ this function creates a facet plot with 7 columns
  Used to plot appliance frequency usage"""
  sns.set(style="whitegrid")
  h =  sns.FacetGrid(df_local,col='month',col_wrap=4,size=2.5,sharex=False,sharey=False)
  (h.map_dataframe(plt.bar,'hour','Frequency')
      .set_axis_labels("Day_hour","Frequency")
      .fig.subplots_adjust(wspace=.2,hspace=.5))
  h.set(xticks = [0,6,12,18])
  h.set(yticks = np.arange(0,31,5))
  h.savefig(savedir)
  h.clear()
  #return h
  
def plot_temperature_plots(df_local):
  """ this function creates a facet plot with 7 columns
  Used to plot appliance frequency usage"""
  sns.set(style="whitegrid")
  sns.set(context="paper")
  h =  sns.FacetGrid(df_local,col='date',col_wrap=7,size=2.5,sharex=False,sharey=False)
  h = (h.map_dataframe(plt.plot,'time','TemperatureC')
      .set_axis_labels("Time (minutes)","Temeperature(c)")
      .fig.subplots_adjust(wspace=.2,hspace=.5))
  return h
