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
  elif home == "House20.csv":
      df_samp.rename(columns={'Aggregate':'use', 'Fridge':'Fridge','Freezer':'Freezer', 'Kettle':'Kettle',
         'WashingMachine':'WashingMachine', 'Dishwasher':'Dishwasher', 'TelevisionSite':'TV', 'Microwave':'Microwave', 'TumbleDryer':'TumbleDryer','ComputerSite':'ComputerSite'},inplace=True) 
  elif home == "House18.csv":
     df_samp.rename(columns={'Aggregate':'use', 'Fridge-Freezer':'Fridge_Freezer','Fridge_garag':'Fridge_garage',
                          'Freezer_garage':'Freezer_garage','WashingMachin':'WashingMachine', 'Dishwasher':'Dishwasher', 'TelevisionSite':'TV','Microwave':'Microwave','WasherDryer_garage':'WasherDryer','DesktopComputer':'Computer'},inplace=True) 
  elif home == "House16.csv": 
      df_samp.rename(columns={'Aggregate':'use', 'Fridge-Freezer_1':'Fridge_Freezer_1', 'Fridge-Freezer_2':'Fridge_Freezer_2','ElectricHeater_1':'ElectricHeater_1', 'ElectricHeater_2':'ElectricHeater_2', 'WashingMachine':'WashingMachine',
       'Dishwasher':'Dishwasher', 'ComputerSite':'Computer', 'TelevisionSite':'TV', 'Dehumidifier':'Dehumidifier'},inplace=True)
  elif home == "House1.csv": 
     df_samp.rename(columns={'Aggregate':'use', 'Fridge':'Fridge', 'Freezer_1':'Freezer_1', 'Freezer_2':'Freezer_2', 'WasherDryer':'WasherDryer',
       'WashingMachine':'WashingMachine', 'Dishwasher':'Dishwasher', 'Computer':'Computer', 'TelevisionSite':'TV','ElectricHeater':'ElectricHeater'},inplace=True)
  else:
    raise ValueError('Provide mapping of column names for this home')
    
    
    
    

    
def reverse_lookup(home,dictvalue):
    ''' using this function I use assigned appliance name to find the actual name of the appliance'''
    if home == "House10.csv":
        appliance_names = {'Aggregate':'use', 'Magimix_Blender':'blender', 'Toaster':'toaster', 'ChestFreezer':'Chest_Freezer', 'Fridge-Freezer':'Fridge_Freezer',
         'WashingMachine':'WashingMachine', 'Dishwasher':'Dishwasher', 'TelevisionSite':'TV', 'Microwave':'Microwave', 'Mix':'Mixer'}
        return [key for key,value in appliance_names.items() if value==dictvalue ][0]
    elif home == "House20.csv":
        appliance_names = {'Aggregate':'use', 'Fridge':'Fridge','Freezer':'Freezer', 'Kettle':'Kettle',
         'WashingMachine':'WashingMachine', 'Dishwasher':'Dishwasher', 'TelevisionSite':'TV', 'Microwave':'Microwave', 'TumbleDryer':'TumbleDryer','ComputerSite':'ComputerSite'}
        return [key for key,value in appliance_names.items() if value==dictvalue ][0]
    elif home == "House18.csv":
        appliance_names = {'Aggregate':'use', 'Fridge-Freezer':'Fridge_Freezer','Fridge_garag':'Fridge_garage',
                          'Freezer_garage':'Freezer_garage','WashingMachin':'WashingMachine', 'Dishwasher':'Dishwasher', 'TelevisionSite':'TV','Microwave':'Microwave','WasherDryer_garage':'WasherDryer','DesktopComputer':'Computer'}
    elif home == "House16.csv":
        appliance_names = {'Aggregate':'use', 'Fridge-Freezer_1':'Fridge_Freezer_1', 'Fridge-Freezer_2':'Fridge_Freezer_2','ElectricHeater_1':'ElectricHeater_1', 'ElectricHeater_2':'ElectricHeater_2', 'WashingMachine':'WashingMachine',
       'Dishwasher':'Dishwasher', 'ComputerSite':'Computer', 'TelevisionSite':'TV', 'Dehumidifier':'Dehumidifier'}
    elif home == "House1.csv":
         appliance_names = {'Aggregate':'use', 'Fridge':'Fridge', 'Freezer_1':'Freezer_1', 'Freezer_2':'Freezer_2', 'WasherDryer':'WasherDryer',
       'WashingMachine':'WashingMachine', 'Dishwasher':'Dishwasher', 'Computer':'Computer', 'TelevisionSite':'TV','ElectricHeater':'ElectricHeater'}
        
        
    