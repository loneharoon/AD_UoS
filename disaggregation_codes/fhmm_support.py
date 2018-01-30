
# coding: utf-8

# In[ ]:

import json
import numpy as np
from hmmlearn import hmm
import itertools
from copy import deepcopy
import warnings
warnings.filterwarnings("ignore")


# In[ ]:

def compute_pi_fhmm(list_pi):
    result =  list_pi[0]
    for i in range(len(list_pi)-1):
        result = np.kron(result,list_pi[i+1])
    return result

def compute_A_fhmm(list_A):
    '''
    Input: list_pi: List of PI's of individual learnt HMMs
    Output: Combined Pi for the FHMM
    '''
    result=list_A[0]
    for i in range(len(list_A)-1):
        result=np.kron(result,list_A[i+1])
    return result

def compute_means_fhmm(list_means):  
    '''
    Returns [mu, sigma]
    '''
    #list_of_appliances_centroids=[ [appliance[i][0] for i in range(len(appliance))] for appliance in list_B]
    states_combination=list(itertools.product(*list_means))
    #print states_combination
    num_combinations=len(states_combination)
    #print num_combinations
    means_stacked=np.array([sum(x) for x in states_combination])
    means=np.reshape(means_stacked,(num_combinations,1)) 
    cov=np.tile(5*np.identity(1), (num_combinations, 1, 1))
    return [means, cov]

# def create_combined_hmm(n, pi, A, mean, cov):
#     combined_model=hmm.GaussianHMM(n_components=n,covariance_type='full', startprob=pi, transmat=A)
#     combined_model.covars_=cov
#     combined_model.means_=mean
#     return combined_model

def decode_hmm(length_sequence, centroids, appliance_list, states):
    '''
    Decodes the HMM state sequence
    '''
    power_states_dict={}    
    hmm_states={}
    hmm_power={}
    total_num_combinations=1
    for appliance in appliance_list:
        total_num_combinations*=len(centroids[appliance])  

    for appliance in appliance_list:
        hmm_states[appliance]=np.zeros(length_sequence,dtype=np.int)
        hmm_power[appliance]=np.zeros(length_sequence)
        
    for i in range(length_sequence):
        factor=total_num_combinations
        for appliance in appliance_list:
            #assuming integer division (will cause errors in Python 3x)
            factor=factor//len(centroids[appliance])
            
            temp=int(states[i])/factor
            hmm_states[appliance][i]=temp%len(centroids[appliance])
            hmm_power[appliance][i]=centroids[appliance][hmm_states[appliance][i]]
            
    return [hmm_states,hmm_power]


# In[ ]:

def return_sorting_mapping(means):
    means_copy = deepcopy(means)
    # Sorting 
    means_copy = np.sort(means_copy, axis = 0)  
    # Finding mapping
    mapping = {}
    for i, val in enumerate(means_copy):
        assert val==means[np.where(val==means)[0]]
        mapping[i] = np.where(val==means)[0][0]
    return mapping

def sort_startprob(mapping, startprob):
    """ Sort the startprob according to power means; as returned by mapping
    """
    num_elements = len(startprob)
    new_startprob = np.zeros(num_elements)
    for i in xrange(len(startprob)):
        new_startprob[i] = startprob[mapping[i]]
    return new_startprob

def sort_covars(mapping, covars):
    num_elements = len(covars)
    new_covars = np.zeros_like(covars)
    for i in xrange(len(covars)):
        new_covars[i] = covars[mapping[i]]
    return new_covars

def sort_transition_matrix(mapping, A):
    """ Sorts the transition matrix according to power means; as returned by mapping
    """
    num_elements = len(A)
    A_new = np.zeros((num_elements, num_elements))
    for i in range(num_elements):
        for j in range(num_elements):
            A_new[i,j] = A[mapping[i], mapping[j]]   
    return A_new

def sort_learnt_parameters(startprob, means, covars, transmat):
    mapping = return_sorting_mapping(means)
    means_new = np.sort(means, axis = 0)
    startprob_new = sort_startprob(mapping, startprob)
    covars_new = sort_covars(mapping, covars)
    transmat_new = sort_transition_matrix(mapping, transmat)
    assert np.shape(means_new) == np.shape(means)
    assert np.shape(startprob_new) == np.shape(startprob)
    assert np.shape(transmat_new) == np.shape(transmat)
    
    return [startprob_new, means_new, covars_new, transmat_new]

def create_combined_hmm(model):
    from IPython import embed
    #print ("p0")
    list_pi=[model[appliance].startprob_ for appliance in model]
    #print ("p1")
    list_A=[model[appliance].transmat_ for appliance in model]
    list_means=[model[appliance].means_.flatten().tolist() for appliance in model]
    #print ("p2")
    pi_combined=compute_pi_fhmm(list_pi)
    A_combined=compute_A_fhmm(list_A)
    [mean_combined, cov_combined]=compute_means_fhmm(list_means)
    #embed()
    #model_fhmm=create_combined_hmm(len(pi_combined),pi_combined, A_combined, mean_combined, cov_combined)
    combined_model=hmm.GaussianHMM(n_components=len(pi_combined),covariance_type='full')
    combined_model.startprob_=pi_combined
    combined_model.transmat_=A_combined 
    combined_model.covars_=cov_combined
    combined_model.means_=mean_combined
    return combined_model

