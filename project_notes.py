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
1. Run project_main.py first to get disaggregation results from different disagg techniques. This saves disagg results as pickle files. Makonin's SSHMM runs in python 3 only so run makonin_main.py placed in python_3_codes to get disagg results
2. open pipeline_main.py. This calls disagg results first and then runs AD logic. Remember in this script you can run in between anomaly detection too as pickle files. Also, remember this script all pickle files except sshmss result because sshmss results werer obtained in python 3 and it seems that python3 and 2 have differenet pickle versions
...................................................
Following cases are present in REFIT data
1. Na Values
2. Days were data is already filled so only contionous high values [needs to be identifed in algorithm]

Failures/Insights:
1. Boxplot rule fails becuase it is sensitive to small changes.

FHMM:
1. Number of states for an appliance are detected via clustering. No manual need to specify. Same as done in toolkit

I found that GSP fails for denoised data. It often detects less number of appliances than actual number present. As a result it becomes difficult to compute accuracies.
    
SSHMMS: It is the only algorithm which needs to run in python 3. Remaining run in python 2. 
The code is present in python_3_codes folder. Run makonin_main.py first

Sensitivity analysis:
1. For anomaly detection algorithm, I do grid search in file 'grid_search_parameters.py'  
    
'''
'''
############################HOme Notes#####################
1. Home 10
training: month 4
testing: moths 5, 6
target_appliance:Chest_freezer
Issues: NONE

2. Home 20
training: month 5
testing: moths 6, 7,8
target_appliance:Freezer
Issues: NONE

3. Home 18
training: month 7
testing: moths 8, 9,10
target_appliance:frige freezer
Issues: NONE

4. Home 16
training: month 3
testing: moths 4, 5,6
target_appliance: Frige_Freezer_1
Issues: Day 3 March is removed since it contains anomaly

5. Home 1
training: month 12 of 2014
testing: months 1,2 and 3 of 2015
target_appliance:ElectricHeater
Issues: NONE
# NOTES AFTER COMING TO IIITD
1. Plot showing the effect of smoothing on NILM data is plotted using plot_NILM_NILM_smooth.py



'''