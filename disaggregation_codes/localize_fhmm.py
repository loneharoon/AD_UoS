import warnings
warnings.filterwarnings("ignore")
import fhmm_support as fhm
import numpy as np
import pandas as pd
np.random.seed(123)
import matplotlib.pyplot as plt
from collections import OrderedDict
from hmmlearn import hmm
from IPython import embed
import time

def fhmm_decoding(train_dset,test_dset):

    train_agg_meter,train_sub_meters = divide_dataset_in_appliances(train_dset)
    test_agg_meter,test_sub_meters = divide_dataset_in_appliances(test_dset)
    #train model for each applaince
    model = OrderedDict()
    appliances = train_sub_meters.columns
    for appliance in appliances:
    # print appliance;
        model[appliance] =  hmm.GaussianHMM(n_components=3,covariance_type="full")
        temp =  train_sub_meters[appliance].values.reshape(len(train_sub_meters[appliance]),1)
        model[appliance].fit(temp)
    # sort all the parameters and update new models with these 
    new_learnt_models= OrderedDict()
    for appliance in model:
        #print appliance;
        startprob, means, covars, transmat = fhm.sort_learnt_parameters(model[appliance].startprob_, model[appliance].means_, model[appliance].covars_ , model[appliance].transmat_) 
        new_learnt_models[appliance]=hmm.GaussianHMM(startprob.size, "full")
        new_learnt_models[appliance].startprob_ = startprob
        new_learnt_models[appliance].transmat_ = transmat
        new_learnt_models[appliance].means_ = means
        new_learnt_models[appliance].covars_ = covars
    # create aggregate model
    learnt_model_combined = fhm.create_combined_hmm(new_learnt_models)
    temp1 = test_agg_meter.values.reshape(len(test_agg_meter),1)
    print('\nTesting done\n')
    start_time = time.time()
    new_learnt_states = learnt_model_combined.predict(temp1)
    print('time taken %f seconds' %(time.time() - start_time))
    temp_means = OrderedDict()
    for app in model:
        temp_means[app] = new_learnt_models[app].means_
    [decoded_states, decoded_power] = fhm.decode_hmm(len(new_learnt_states), temp_means, [appliance for appliance in model], new_learnt_states)
    # create dataframe of results
    decoded_power = pd.DataFrame(decoded_power)
    decoded_power.index = test_agg_meter.index
    ret_result = {'actaul_power':test_sub_meters,'decoded_power':decoded_power}
    return(ret_result)

def divide_dataset_in_appliances(df):
    agg_meter = df['use']
    meters = df.columns
    #import ipdb;ipdb.set_trace()
    meters = meters.drop('use')
    sub_meters = df[meters]
    return (agg_meter,sub_meters)
