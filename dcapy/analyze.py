"""
Decision Curve Analysis

Author: Matthew Black
"""

import pandas as pd
import numpy as np
from validate import dca_input_validation


class DecisionCurveAnalysis:
    """
    """
    #boundaries for threshold probabilities
    threshold_boundaries = [0.01, 0.99, 0.01]

    def __init__(self, data, outcome, predictors):
        if not isinstance(data, pd.DataFrame):
            raise TypeError("data must be a pandas DataFrame")
        self.data = data
        self.outcome = outcome
        self.predictors = predictors
        #initialize results to NoneType
        self.net_benefit = self.interventions_avoided = None

    def run(self):
        """Performs the decision curve analysis

        Returns:
        --------
        A tuple (net_benefit, interventions_avoided) of pandas DataFrames
        """
        self.net_benefit, self.interventions_avoided = analyze(data, outcome,
                                                               predictors)
        return self.net_benefit, self.interventions_avoided


def dca(data, outcome, predictors,
        thresh_lb=0.01, thresh_ub=0.99, thresh_step=0.01, 
        probability=None, harm=None, intervention_per=100):
    """Performs decision curve analysis on the input data set

    Parameters:
    -----------
    data : the data set to analyze (must be a pandas DataFrame)
    outcome : the column of the data frame to use as the outcome
    predictors : the column(s) that will be used to predict the outcome
    thresh_lb : lower bound for threshold probabilities (defaults to 0.01)
    thresh_ub : upper bound for threshold probabilities (defaults to 0.99)
    thresh_step : step size for the set of threshold probabilities [x_start:x_stop]
    probability :
    harm :
    intervention_per : 
    smooth : 

    Returns:
    --------
    A tuple (net_benefit, interventions_avoided) of pandas DataFrames
    net_benefit : 
    interventions_avoided : 
    """
    #perform input validation
    data, predictors, probability, harm = dca_input_validation(
        data, outcome, predictors, thresh_lb, thresh_ub, thresh_step, probability,
        harm, intervention_per)
    
    if isinstance(predictors, str):
        #need to convert to a list
        predictors = [predictors]

    ##CALCULATE NET BENEFIT
    num_observations = len(data[outcome])
    event_rate = mean(data[outcome])

    #create DataFrames for holding results
    net_benefit = pd.Series(frange(thresh_lb, thresh_ub+thresh_step, thresh_step), name="threshold")
    interventions_avoided = pd.DataFrame(net_benefit)
    net_benefit_all = event_rate - (1-event_rate)*net_benefit/(1-net_benefit)
    net_benefit_all.name = 'all'
    net_benefit = pd.concat([net_benefit, net_benefit_all], axis=1)
    net_benefit['none'] = 0

    for i in range(0, len(predictors)):  #for each predictor
        net_benefit[predictors[i]] = 0.00  #initialize new column of net_benefits 
        for j in range(0, len(net_benefit['threshold'])):  #for each observation
            true_positives, false_positives = calc_tf_positives(data,
                                                                outcome,
                                                                predictors[i],
                                                                net_benefit['threshold'],
                                                                j)
            #calculate net benefit
            net_benefit_value = true_positives/num_observations - false_positives/num_observations \
                * (net_benefit['threshold'][j]/(1-net_benefit['threshold'][j])) - harm[i]
            net_benefit.set_value(j, predictors[i], net_benefit_value)
        #calculate interventions_avoided
        interventions_avoided[predictors[i]] = (net_benefit[predictors[i]] - net_benefit['all']) * \
            intervention_per/(interventions_avoided['threshold']/(1-interventions_avoided['threshold']))

    #TODO: implement smoothing with loess function

    return net_benefit, interventions_avoided


def calc_tf_positives(data, outcome, predictor, net_benefit_threshold, j):
    """Calculate the number of true/false positives for the given parameters

    Parameters:
    ----------
    data : A pandas DataFrame containing the data set to analyze
    outcome : the column of the data frame to use as the outcome
    predictor : the column to use as the predictor for this calculation
    net_benefit_threshold : the threshold column of the net_benefit data frame
    j : the index in the net_benefit data frame to use

    Returns:
    --------
    A tuple (true_positives, false_positives) for the input parameters
    """
    true_positives = false_positives = 0
    #create a filter mask
    filter_mask = data[predictor] >= net_benefit_threshold[j]
    filter_mask_sum = filter_mask.sum()
    if filter_mask_sum == 0:
        pass
    else:
        #get all outcomes where the filter_mask is 'True'
        filtered_outcomes = map(lambda x,y: x if y == True else np.nan,
                                data[outcome],filter_mask)
        filtered_outcomes = [outcome for outcome in filtered_outcomes
                             if outcome is not np.nan]  #drop all NaN values
        true_positives = mean(filtered_outcomes)*filter_mask_sum
        false_positives = (1-mean(filtered_outcomes))*filter_mask_sum

    return true_positives, false_positives


def frange(start, stop, step):
    """Generator that can create ranges of floats

    See: http://stackoverflow.com/questions/7267226/range-for-floats
    """
    while start < stop:
        yield start
        start += step


def mean(iterable):
    """Calculates the mean of the given iterable
    """
    return sum(iterable)/len(iterable)


if __name__ == "__main__":
    import sys

    sys.exit(0)