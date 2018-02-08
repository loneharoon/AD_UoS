#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file standardizes colum names
Created on Wed Feb  7 09:42:34 2018

@author: haroonr
"""
def rename_appliances(home,df_samp):
  
  if home == "House10.csv":
    df_samp.rename(columns={'Aggregate':'use', 'Magimix_Blender':'blender', 'Toaster':'toaster', 'ChestFreezer':'Chest_Freezer', 'Fridge-Freezer':'Fridge_Freezer',
         'WashingMachine':'WashingMachine', 'Dishwasher':'Dishwasher', 'TelevisionSite':'TV', 'Microwave':'Microwave', 'Mix':'Mixer'},inplace=True)
  else:
    raise ValueError('Provide mapping of column names for this home')
    
def reverse_lookup(home,dictvalue):
    ''' using this function I use assigned appliance name to find the actual name of the appliance'''
    if home == "House10.csv":
        appliance_names = {'Aggregate':'use', 'Magimix_Blender':'blender', 'Toaster':'toaster', 'ChestFreezer':'Chest_Freezer', 'Fridge-Freezer':'Fridge_Freezer',
         'WashingMachine':'WashingMachine', 'Dishwasher':'Dishwasher', 'TelevisionSite':'TV', 'Microwave':'Microwave', 'Mix':'Mixer'}
        return [key for key,value in appliance_names.items() if value==dictvalue ][0]
    