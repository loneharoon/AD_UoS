#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script will note down all important observations related to REFIT dataset
Created on Tue Jan 16 22:45:22 2018
@author: haroonr
"""
#%%
"""
Following cases are present in REFIT data
1. Na Values
2. Days were data is already filled so only contionous high values [needs to be identifed in algorithm]

Failures/Insights:
1. Boxplot rule fails becuase it is sensitive to small changes.

FHMM:
1. Number of states for an appliance are detected via clustering. No manual need to specify. Same as done in toolkit
'''