from dcapy.calc import *
from dcapy.validate import DCAError


def dca(data, outcome, predictors,
        thresh_lo=0.01, thresh_hi=0.99, thresh_step=0.01,
        probabilities=None, harms=None, intervention_per=100,
        smooth_results=False, lowess_frac=0.10):
    """Performs decision curve analysis on the input data set

    Parameters
    ----------
    data : pd.DataFrame
        the data set to analyze
    outcome : str
        the column of the data frame to use as the outcome
        this must be coded as a boolean (T/F) or (0/1)
    predictors : str OR list(str)
        the column(s) that will be used to predict the outcome
    thresh_lo : float
        lower bound for threshold probabilities (defaults to 0.01)
    thresh_hi : float
        upper bound for threshold probabilities (defaults to 0.99)
    thresh_step : float
        step size for the set of threshold probabilities [x_start:x_stop]
    probability : bool or list(bool)
        whether the outcome is coded as a probability
        probability must have the same length as the predictors list
    harm : float or list(float)
        the harm associated with each predictor
        harm must have the same length as the predictors list
    intervention_per : int
        interventions per `intervention_per` patients
    smooth_results : bool
        use lowess smoothing to smooth the result data series
    lowess_frac : float
        the fraction of the data used when estimating each endogenous value

    Returns
    -------
    tuple(pd.DataFrame, pd.DataFrame)
        A tuple of length 2 with net_benefit, interventions_avoided
        net_benefit : TODO
        interventions_avoided : TODO
    """
    #calculate useful constants for the net benefit calculation
    num_observations = len(data[outcome])  # number of observations in data set
    event_rate = mean(data[outcome])  # the rate at which the outcome happens

    #create DataFrames for holding results
    net_benefit, interventions_avoided = \
        initialize_result_dataframes(event_rate, thresh_lo, thresh_hi, thresh_step)
    for i, predictor in enumerate(predictors):  # for each predictor
        net_benefit[predictor] = np.nan  # initialize new column of net_benefits

        for j in range(0, len(net_benefit['threshold'])):  # for each threshold value
            #calculate true/false positives
            true_positives, false_positives = \
                calc_tf_positives(data, outcome, predictor,
                                  net_benefit['threshold'], j)

            #calculate net benefit
            net_benefit_value = \
                calculate_net_benefit(j, net_benefit['threshold'], harms[i],
                                      true_positives, false_positives,
                                      num_observations)
            net_benefit.set_value(j, predictor, net_benefit_value)

        #calculate interventions_avoided for the predictor
        interventions_avoided[predictor] = calculate_interventions_avoided(
            predictor, net_benefit, intervention_per,
            interventions_avoided['threshold'])

        #smooth the predictor, if specified
        if smooth_results:
            nb_sm, ia_sm = lowess_smooth_results(predictor, net_benefit, 
                                                 interventions_avoided, lowess_frac)
            #add the smoothed series to the dataframe
            pd.concat([net_benefit, nb_sm], axis=1)
            pd.concat([interventions_avoided, ia_sm], axis=1)

    return net_benefit, interventions_avoided


def stdca(data, outcome, tt_outcome, time_point, predictors,
          thresh_lb=0.01, thresh_ub=0.99, thresh_step=0.01,
          probability=None, harm=None, intervention_per=100,
          smooth_results=False, lowess_frac=0.10, cmp_risk=False):
    """Performs survival-time decision curve analysis on the input data set

    Parameters
    ----------
    data : pd.DataFrame
        the data set to analyze
    outcome : str
        the column of the data frame to use as the outcome
    tt_outcome : str
        the column of the data frame to use as the time to outcome
    time_point : float
        the time point of interest for this analysis
    predictors : str OR list(str)
        the column(s) that will be used to predict the outcome
    thresh_lb : float
        lower bound for threshold probabilities (defaults to 0.01)
    thresh_ub : float
        upper bound for threshold probabilities (defaults to 0.99)
    thresh_step : float
        step size for the set of threshold probabilities [x_start:x_stop]
    probability : bool or list(bool)
        whether the outcome is coded as a probability
        probability must have the same length as the predictors list
    harm : float or list(float)
        the harm associated with each predictor
        harm must have the same length as the predictors list
    intervention_per : int
        interventions per `intervention_per` patients
    smooth_results : bool
        use lowess smoothing to smooth the result data series
    lowess_frac : float
        the fraction of the data used when estimating each endogenous value
    cmp_risk : bool
        use competitive risk 

    Returns
    -------
    tuple(pd.DataFrame, pd.DataFrame)
        A tuple of length 2 with net_benefit, interventions_avoided
        net_benefit : TODO
        interventions_avoided : TODO
    """
    num_observations = len(data[outcome])  # number of observations in data set

    #get probability of event for all subjects
    #TODO: function call here

    #initialize the results dataframes
    net_benefit, interventions_avoided = \
        initialize_result_dataframes(event_rate, thresh_lb, thresh_ub, thresh_step)
    
    for i, predictor in enumerate(predictors):
        net_benefit[predictor] = np.nan  # initialize

        for j in range(0, len(net_benefit['threshold'])):
            p_x = sum(data[predictor]>=net_benefit['threshold'][j])/num_observations
            if p_x == 0:
                #TODO: this should be more specific
                raise DCAError("no observations with risk greater than threshold")
            if cmp_risk:  #TODO: calculate using competing risk
                from statsmodels.sandbox.survival import SurvivalTime
                pass
            else:  #TODO: calculate using Kaplan Meier
                from statsmodels.sandbox.survival2 import KaplanMeier
                pass

            #TODO: calculate net benefit based on calculated risk

        #TODO: calculate interventions avoided
        
        #smooth the predictor, if specified
        if smooth_results:
            nb_sm, ia_sm = lowess_smooth_results(predictor, net_benefit, 
                                                 interventions_avoided, lowess_frac)
            #add the smoothed series to the dataframe
            pd.concat([net_benefit, nb_sm], axis=1)
            pd.concat([interventions_avoided, ia_sm], axis=1)

    return net_benefit, interventions_avoided
