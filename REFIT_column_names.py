#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script is used to works on default REFIT dataset and formats it for further processing
Created on Wed Nov 22 14:10:59 2017

@author: haroonr
"""

import os
import re
home_app= {
1 : ["localminute","Aggregate", "Fridge", "Freezer_1", "Freezer_2", "WasherDryer",
"WashingMachine", "Dishwasher", "Computer", "TelevisionSite", "ElectricHeater"],
2 : ["localminute","Aggregate", "Fridge-Freezer", "WashingMachine", "Dishwasher", "TelevisionSite",
"Microwave", "Toaster", "Hi-Fi", "Kettle", "OverheadFan"],
3 : ["localminute","Aggregate", "Toaster", "Fridge-Freezer", "Freezer", "TumbleDryer",  
"Dishwasher", "WashingMachine", "TelevisionSite", "Microwave", "Kettle"],
4 : ["localminute","Aggregate", "Fridge", "Freezer", "Fridge-Freezer", "WashingMachine_1",
"WashingMachine_2", "DesktopComputer", "TelevisionSite", "Microwave", "Kettle"],
5 : ["localminute","Aggregate","Fridge-Freezer", "TumbleDryer", "WashingMachine", "Dishwasher",
"DesktopComputer", "TelevisionSite", "Microwave", "Kettle", "Toaster"],
6 : ["localminute","Aggregate", "Freezer", "WashingMachine", "Dishwasher", "MJYComputer",
"TV_Satellite", "Microwave", "Kettle", "Toaster", "PGM_Computer"],
7 : ["localminute","Aggregate", "Fridge", "Freezer_1", "Freezer_2", "TumbleDryer",
"WashingMachine", "Dishwasher", "TelevisionSite", "Toaster", "Kettle"],
8 : ["localminute","Aggregate", "Fridge", "Freezer", "WasherDryer", "WashingMachine",
"Toaster", "Computer", "TelevisionSite", "Microwave", "Kettle"],
9 : ["localminute","Aggregate", "Fridge-Freezer", "WasherDryer", "WashingMachine", "Dishwasher",
"TelevisionSite", "Microwave", "Kettle", "Hi-Fi", "ElectricHeater"],
10 : ["localminute","Aggregate", "Magimix_Blender", "Toaster", "ChestFreezer", "Fridge-Freezer",
"WashingMachine", "Dishwasher", "TelevisionSite", "Microwave", "Mix"],
11 : ["localminute","Aggregate", "Firdge", "Fridge-Freezer", "WashingMachine", "Dishwasher",
"ComputerSite", "Microwave", "Kettle", "Router", "Hi-Fi"],
12 : ["localminute","Aggregate", "Fridge-Freezer", "noname1","noname2", "ComputerSite",
"Microwave", "Kettle", "Toaster", "Television", "noname3"],
13 : ["localminute","Aggregate", "TelevisionSite", "Freezer", "WashingMachine", "Dishwasher",
"noname", "NetworkSite", "Microwave", "Microwave", "Kettle"],
15 : ["localminute","Aggregate", "Fridge-Freezer", "TumbleDryer", "WashingMachine", "Dishwasher",
"ComputerSite", "TelevisionSite", "Microwave", "Hi-Fi", "Toaster"],
16 : ["localminute","Aggregate", "Fridge-Freezer_1", "Fridge-Freezer_2", "ElectricHeater_1",
"ElectricHeater_2", "WashingMachine", "Dishwasher", "ComputerSite",
"TelevisionSite", "Dehumidifier"],
17 : ["localminute","Aggregate", "Freezer", "Fridge-Freezer", "TumbleDryer", "WashingMachine",
"ComputerSite", "TelevisionSite", "Microwave", "Kettle", "TVSite"],
18 : ["localminute","Aggregate", "Fridge_garag", "Freezer_garage", "Fridge-Freezer",
"WasherDryer_garage", "WashingMachin", "Dishwasher", "DesktopComputer",
"TelevisionSite", "Microwave"],
19 : ["localminute","Aggregate", "FridgeFreezer", "WashingMachine", "TelevisionSite", "Microwave", 
  "Kettle", "Toaster", "Bread-maker","GamesConsole", "Hi-Fi"],
20 : ["localminute","Aggregate", "Fridge", "Freezer", "TumbleDryer", "WashingMachine", "Dishwasher", 
 "ComputerSite", "TelevisionSite", "Microwave", "Kettle"],
21 : ["localminute","Aggregate", "Fridge-Freezer", "TumbleDryer", "WashingMachine", "Dishwasher", 
 "FoodMixer", "Television", "noname", "Vivarium", "PondPump"]
}
#%% Temporary disabled  because I use the same script and get house column names on the the fly

#read_dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/dataset_default/"
#save_dir = "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/dataset/"
#fls = os.listdir(read_dir)
#
#for i in range(0,len(fls)):
#  home = fls[i]
#  df = pd.read_csv(read_dir+home)
#  df.columns = home_app[int(re.search(r'\d+', home).group(0))]
#  #df.columns = home_app[i+1]
#  df['localminute'] = pd.to_datetime(df['localminute'],unit="s")
#  df.to_csv(save_dir+home)
  