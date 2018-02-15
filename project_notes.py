#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script will note down all important observations related to REFIT dataset
Created on Tue Jan 16 22:45:22 2018
@author: haroonr
"""
#%%
"""
..........................................................................
................................PROJECT RUNNING...........................
..........................................................................
1. Run project_main.py first to get disaggregation results from different disagg techniques. This saves disagg results
2. open pipeline_main.py. This calls disagg results first and then runs AD logic.


Following cases are present in REFIT data
1. Na Values
2. Days were data is already filled so only contionous high values [needs to be identifed in algorithm]

Failures/Insights:
1. Boxplot rule fails becuase it is sensitive to small changes.

FHMM:
1. Number of states for an appliance are detected via clustering. No manual need to specify. Same as done in toolkit

CO:
    
    
'''
'''
############################HOme Notes#####################
1. Home 10
training: month 4
testing: moths 5, 6,12
target_appliance:chest freezer
Issues: NONE

2. Home 20
training: month 5
testing: moths 6, 7,8
target_appliance:freezer
Issues: NONE

3. Home 18
training: month 7
testing: moths 8, 9,10
target_appliance:frige freezer
Issues: NONE

4. Home 16
training: month 2
testing: moths 4, 5,6
target_appliance:frige freezer
Issues: Day 3 March is removed since it contains anomaly

5. Home 1
training: month 12 of 2014
testing: moths 1,2 and 3 of 2015
target_appliance:ElectricHeater
Issues: NONE
    

'''