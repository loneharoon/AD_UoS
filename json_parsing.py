#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
In this file, I parse json files[read, write and keep note of important json functions]
Created on Mon Dec 18 11:31:42 2017

@author: haroonr
"""

#%%
import json   
from pprint import pprint
import numpy as np

fl = "/Volumes/MacintoshHD2/Users/haroonr/Dropbox/nilmtk_work/appliance_model_induced_density.json"
dt = json.load(open(fl))    
#%%
from copy import deepcopy
dic = deepcopy(dt)

#%% IN this block, I removed  SAC parameters as defined in drop_keys. Seems I have deleted drop_keys dictionary
 for key,value in dic.items():
  dic[key] = {k:v for k,v in dic[key].items() if k not in drop_keys}

#with open('/Volumes/MacintoshHD2/Users/haroonr/Dropbox/nilmtk_work/reduced.json','w') as outfile:
#  json.dump(dic,outfile)
  
  #%%
  np.mean(dic['kettle']['numberOfCyclesStats']['numberOfCyclesEnergy'])
  #%%
   dict_keys(['dvd', 'faxprinter', 'tvsettopbox', 'chestfreezer', 'microwave', 'hob', 'Unknownkitchen', 'tvcrt', 'foodmixer', 'hottub', 'kettle', 'oven', 'skybox', 'Unknown', 'extractorhood', 'ps', 'shower', 'wii', 'coffeemaker', 'fridgefreezer', 'grill', 'tumbledryer', 'xbox', 'massagebed', 'settopbox', 'dishwasher', 'fridge', 'washingdryingmachine', 'breadmaker', 'tv', 'fryer', 'dvdrecorder', 'foodsteamer', 'hifi', 'uprightfreezer', 'heater', 'audiovisualsite', 'toaster', 'washingmachine', 'centralheating', 'Slowcooker', 'ovencooker', 'waterheater', 'cooker', 'winecooler'])