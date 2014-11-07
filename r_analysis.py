#!/usr/bin/env python
"""
Decision Curve Analysis

Provides a command line tool for running producing results from
Dr. Vicker's original R script.

Author: Matthew Black
"""

import pandas as pd
import pandas.rpy.common as pdcom
import rpy2.robjects as ro
from test import resources_dir, root_test_dir, r_results_dir, load_default_data, load_r_results
from os import path


class RAnalysis:

    #COMMON PARAMETERS
    thresh_lb = 0.01  # equivalent to xstart
    thresh_ub = 0.99  # equivalent to xstop
    thresh_step = 0.01  # equivalent to xby
    y_min = -0.05
    probability = None
    harm = None
    intervention_per = 100
    smooth_results = False  #equivalent to smooth
    lowess_frac = 0.10  # equivalent to loess_span

    def __init__(self, outcome, predictors, r_func,**kwargs):
        self.r_func = r_func
        self.data = load_default_data()
        self.outcome = outcome
        self.predictors = predictors
        self.r_file = path.join(resources_dir, r_func+'.r')
        self.r_args = self.form_r_args(**kwargs)

    def form_r_args(self, **kwargs):
        """Forms the argument dict to pass to the dca function in R
        """
        r_args_dict = self._form_common_r_args(**kwargs)
        return r_args_dict

    def _form_common_r_args(self, thresh_lb=0.01, thresh_ub=0.99, thresh_step=0.01,
                            y_min=-0.05, probability=None, harm=None,
                            intervention_per=100, smooth_results=False,
                            lowess_frac=0.10):
        """Performs input validation and converts any Python objects to R objects
        for use when calling into the R function

        Returns
        -------
        A dictionary of keyword-value arguments to pass to the R function
        """
        #data setup and validation
        r_data = pdcom.convert_to_r_dataframe(self.data)
        r_predictors = self.predictors if isinstance(self.predictors, str) \
                            else ro.vectors.StrVector(self.predictors)
        #ensure all variables are properly set and make special r values for
        #use in calling the r function
        r_x_start = thresh_lb
        r_x_stop = thresh_ub
        r_x_by = thresh_step
        r_y_min = y_min
        r_probability = ro.r('NULL') if probability is None \
                        else probability
        r_harm = ro.r('NULL') if harm is None else harm
        r_intervention_per = intervention_per
        r_smooth = ro.r(str(smooth_results).upper())
        r_loess_span = lowess_frac
        r_args_dict = {
            'data' : r_data,
            'outcome' : self.outcome,
            'predictors' : r_predictors,
            'xstart' : r_x_start,
            'xstop' : r_x_stop,
            'xby' : r_x_by,
            'ymin' : r_y_min,
            'probability' : r_probability,
            'harm' : r_harm,
            'graph' : ro.r('FALSE'),
            'intervention' : ro.r('FALSE'),
            'interventionper' : r_intervention_per,
            'smooth' : r_smooth,
            'loess.span' : r_loess_span
        }
        return r_args_dict

    def run(self, rargs=None):
        """Run the analysis

        Returns
        -------
        tuple(pd.DataFrame, pd.DataFrame)
           (net_benefit, interventions_avoided) in the same format/indexing as
           the Python implementation
        """
        import rpy2.robjects.packages as rpy2p
        #if user doesn't specify args, just use the ones for this class
        if rargs is None:
            rargs = self.r_args
        #source the r file
        with open(self.r_file) as f:
            func_string = ''.join(f.readlines())
        r_file = rpy2p.SignatureTranslatedAnonymousPackage(func_string, "r_file")
        #call the function in the r file
        res_list = r_file.__getattribute__(self.r_func)(**rargs)
        return unpack_r_results_list(res_list)

    def export_to_file(self, analysis_name, net_benefit, interventions_avoided):
        """Exports the results of the analysis to 2 csv files in a
        /results directory of this file
        """
        import os
        #ensure path exists, make folder if necessary
        analysis_dir = path.join(r_results_dir, analysis_name)
        if not path.isdir(analysis_dir):
            os.mkdir(analysis_dir)
        #export
        net_benefit.to_csv(path.join(analysis_dir, 'net_benefit.csv'))
        interventions_avoided.to_csv(path.join(analysis_dir,
                                               'interventions_avoided.csv'))


class RAnalysisDCA(RAnalysis):

    def __init__(self, outcome, predictors, r_func='dca', **kwargs):
        super(RAnalysisDCA, self).__init__(outcome, predictors, r_func, **kwargs)

    def form_r_args(self, **kwargs):
        #argument validation
        valid_keywords = ['thresh_lb', 'thresh_ub', 'thresh_step',
                          'probability', 'harm', 'intervention_per',
                          'smooth_results', 'lowess_frac']
        for kw in kwargs:
            if kw not in valid_keywords:
                error_string = "keyword arg, {}, didn't match a DCA arg".format(kw)
                raise ValueError(error_string)  # TODO: make this more helpful!
                
        return super(RAnalysisDCA, self).form_r_args(**kwargs)


class RAnalysisSTDCA(RAnalysis):
    def __init__(self, outcome, predictors, r_func='stdca', **kwargs):
        super(RAnalysisSTDCA, self).__init__(outcome, predictors, r_func, **kwargs)

    def form_r_args(self, **kwargs):
        r_args_dict = {}  # initialize dictionary of arguments
        #argument validation
        must_use_keywords = ['tt_outcome', 'time_point']
        valid_keywords = ['thresh_lb', 'thresh_ub', 'thresh_step',
                          'probability', 'harm', 'intervention_per',
                          'smooth_results', 'lowess_frac', 'cmp_risk']
        for kw in kwargs:
            if kw in must_use_keywords:
                must_use_keywords.pop(kw)
                r_args_dict[kw] = kwargs.pop(kw)
            if kw not in valid_keywords:
                error_string = "keyword arg, {}, didn't match a STDCA arg".format(kw)
                raise ValueError(error_string)  # TODO: make this more helpful!
        #make sure all must use keywords were specified
        if len(must_use_keywords) > 0:
            raise ValueError("did not use all mandatory keyword args")

        from collections import Counter
        r_args_super = Counter(super().form_r_args(**kwargs))

        return dict(r_args_super + Counter(r_args_dict))


def unpack_r_results_list(res_list):
    """Unpacks the results list to a tuple (net_benefit, interventions_avoided)
    for comparison with the results of Python

    Transforms the results of the R analysis into the pandas DataFrame format and
    indexing returned by the Python algorithm

    Parameters
    ----------
    res_list : rpy2.robject
       a list of results from an R analysis (returned by the R dca function)

    Returns
    -------
    tuple(pd.DataFrame, pd.DataFrame)
        (net_benefit, interventions_avoided) -- same result as Python analysis
    """
    r_nb = pdcom.convert_robj(res_list.rx('net.benefit'))
    r_nb = r_nb['net.benefit']  #unpack dataFrame from dict
    r_ia = pdcom.convert_robj(res_list.rx('interventions.avoided'))
    r_ia = r_ia['interventions.avoided']
    return r_nb, r_ia


if __name__ == "__main__":
    """Call this from the command line and generate data
    """
    import sys
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('name', type=str, help='the name to give this analysis')
    #main conditional is the analysis type
    parser.add_argument('analysis', type=str, choices=['dca','stdca'],
                        help='the type of analysis to run')
    subparsers = parser.add_subparsers(dest='subanalysis')

    #common arguments for dca and stdca
    parser.add_argument('-o', '--outcome', type=str,
                            help='the outcome for the analysis')
    parser.add_argument('-p', '--predictors', type=str, nargs='+',
                            help='the predictors for the analysis')
    parser.add_argument('-b', '--bounds', type=float, nargs='+',
                            default=[0.01, 0.99, 0.01], help='bounds for the analysis specified as lower upper step')
    parser.add_argument('-pr', '--probability', type=str, nargs='+',
                            default=None, help='probability values for predictors')
    parser.add_argument('-ha', '--harm', type=str, nargs='+',
                            default=None, help='harm values for predictors')
    parser.add_argument('--smooth', type=float, default=-1,
                            help='smooth the results using the specified value as lowess_frac')

    #subparser for additional args if analysis is type 'stdca'
    parser_stdca = subparsers.add_parser('stdca')
    parser_stdca.add_argument('-tt', '--ttoutcome', type=str,
                              help='the time to outcome column')
    parser_stdca.add_argument('-tp', '--timepoint', type=float,
                              help='the time point to use')
    parser_stdca.add_argument('-r', '--cmprisk', type=bool,
                              help='use competitive risk')

    args = parser.parse_args()
    #convert args 'smooth' value to appropriate vals for analysis
    if args.smooth < 0:
        #apply defaults
        smooth_bool = False
        smooth_frac = 0.10
    else:
        smooth_bool = True
        smooth_frac = args.smooth
    if args.subanalysis == 'stdca':
        #perform stdca
        analysis = RAnalysisSTDCA(outcome=args.outcome, predictors=args.predictors,
                                  tt_outcome=args.ttoutcome, time_point=args.timepoint,
                                  thresh_lb=args.bounds[0], thresh_ub=args.bounds[1],
                                  thresh_step=args.bounds[2], probability=args.probability,
                                  harm=args.harm, smooth_results=smooth_bool,
                                  lowess_frac=smooth_frac, cmp_risk=args.cmprisk)
    else:
        #perform dca
        analysis = RAnalysisDCA(outcome=args.outcome, predictors=args.predictors,
                                thresh_lb=args.bounds[0], thresh_ub=args.bounds[1],
                                thresh_step=args.bounds[2], probability=args.probability,
                                harm=args.harm, smooth_results=smooth_bool,
                                lowess_frac=smooth_frac)
    nb, ia = analysis.run()
    analysis.export_to_file(args.name, nb, ia)
    sys.exit(0)