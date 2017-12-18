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

fl = "/Volumes/MacintoshHD2/Users/haroonr/Dropbox/nilmtk_work/appliance_model_induced_density.json"
dt = json.load(open(fl))    
#%%
from copy import deepcopy
dic = deepcopy(dt)

#%%
 for key,value in dic.items():
  dic[key] = {k:v for k,v in dic[key].items() if k not in drop_keys}

#json.dump(dic,fp='/Volumes/MacintoshHD2/Users/haroonr/Dropbox/nilmtk_work/reduced.json')
with open('/Volumes/MacintoshHD2/Users/haroonr/Dropbox/nilmtk_work/reduced.json','w') as outfile:
  json.dump(dic,outfile)