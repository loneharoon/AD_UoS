#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script contains all obselete codes. All of them work but given some conditions I no longer used such codes
Created on Tue Jan 16 15:00:39 2018

@author: haroonr
"""
#%% AD logic starts
# this is the logic for flagging anomalies. It is entirely based standard deviations approach. I found this approach results in fasle postive so I shunned it.
# test_stats - contains stats computed on test day
#contexts_stats - contains stats computed from training data   
          import logging
import logging.handlers
LOG_FILENAME = '/Volumes/MacintoshHD2/Users/haroonr/Downloads/REFIT_log/logfile_REFIT.out'
my_logger = logging.getLogger('MyLogger')
my_logger.setLevel(logging.INFO)
# Add the log message handler to the logger
handler = logging.handlers.RotatingFileHandler(
              LOG_FILENAME, maxBytes=9000000, backupCount=0)
my_logger.addHandler(handler)

result = []
num_std = 2.5
dummy_no = 2
for day,data in test_stats.items():
  for contxt,contxt_stats in data.items():
    #be clear - word contexts_stats represents training data and word contxt represents test day stats
    train_results = contexts_stats[contxt] # all relevant train stats
    test_results  = contxt_stats
    temp_res = {}
    temp_res['timestamp'] = datetime.strptime(day,'%Y-%m-%d')
    temp_res['context'] = contxt
    temp_res['status'] = 0
    temp_res['anomtype'] = ' '
    if (test_results['ON_duration']['mean'] >  train_results['ON_duration']['mean'] + num_std* train_results['ON_duration']['std']) and (test_results['OFF_duration']['mean'] >  train_results['OFF_duration']['mean'] + num_std* train_results['OFF_duration']['std']):
       temp_res['status'] = 0
       my_logger.info(day + ":" + contxt + "is not elongated anomaly as off time was also longer")
    elif test_results['ON_duration']['mean'] > dummy_no * train_results['ON_duration']['mean'] + num_std* train_results['ON_duration']['std']:
       temp_res['status'] = 1
       temp_res['anomtype'] = "long"
       my_logger.info(day + ":"+ contxt + ", elongated anomaly" + ", train_stats duration, " + str(train_results['ON_duration']['mean']) + ":"+str(train_results['ON_duration']['std']) + "; test_stats duration, " + str(test_results['ON_duration']['mean']) )
    elif test_results['ON_cycles']['mean'] >  dummy_no * train_results['ON_cycles']['mean'] + num_std* train_results['ON_cycles']['std']:
       temp_res['status'] = 1
       temp_res['anomtype'] = "frequent"
       my_logger.info(day + ":"+contxt +  ", frequent anomaly" + ", train_stats frequency, " + str(train_results['ON_cycles']['mean']) + ":"+str(train_results['ON_cycles']['std']) + "; test_stats frequency, " + str(test_results['ON_cycles']['mean']) )
    result.append(temp_res)
res_df = pd.DataFrame.from_dict(result)
res_df = res_df.sort_values('timestamp')
res_df[res_df.status==1]
res_df[res_df.status==1].shape[0]
