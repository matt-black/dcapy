"""
Decision Curve Analysis

Support and helper functions/classes for dcapy testing

Author: Matthew Black
"""
import unittest
import pandas as pd
import pandas.rpy.common as pdcom
import rpy2.robjects as ro
from os import path
from dcapy.algo import dca as py_dca

root_test_dir = path.dirname(path.realpath(__file__))
resources_dir = path.join(root_test_dir, 'resource')


class RCompareTest(unittest.TestCase):
    """Base class for comparing the results of the R function for dca/stdca
    to their Python equivalents
    """

    #COMMON PARAMETERS TO DCA AND STDCA
    thresh_lb = 0.01  #equivalent to xstart
    thresh_ub = 0.99  #equivalent to xstop
    thresh_step = 0.01  #equivalent to xby
    y_min = -0.05
    probability=None
    harm=None
    intervention_per=100
    smooth = False
    loess_span = 0.10

    def form_r_args(self, **kwargs):
        """Form the argument dictionary for the R function
        """
        r_args_dict = self._form_common_r_args(**kwargs)
        return r_args_dict

    def run_r_analysis(self, r_file_name, r_args_dict):
        """Run the analysis for the function in the given r file

        Parameters:
        -----------
        r_file_name : the name of the r file to source (must be in the /resource
        subdirectory of this file's directory), in this case it is also the function
        that will be called within that file
        r_args_dict : a dictionary of arguments to pass to the r function

        Returns:
        --------
        A tuple of pandas DataFrames (net_benefit, interventions_avoided)
        """
        import rpy2.robjects.packages as rpy2p
        #source the r file and make a python func to call it
        with open(path.join(resources_dir, r_file_name+'.r')) as f:
            func_string = ''.join(f.readlines())
        r_file = rpy2p.SignatureTranslatedAnonymousPackage(func_string, "r_file")
        #call the function in the r file
        res_list = r_file.__getattribute__(r_file_name)(**r_args_dict)
        return unpack_r_results_list(res_list)

    def _form_common_r_args(self, thresh_lb=0.01, thresh_ub=0.99, thresh_step=0.01,
                            y_min=-0.05, probability=None, harm=None,
                            intervention_per=100, smooth=False, loess_span=0.10):
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
        r_smooth = ro.r(str(smooth).upper())
        r_loess_span = loess_span
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

    def run_python_analysis(self):
        """Runs the python version of the DCA analysis

        Must be implemented by inheriting classes!
        """
        pass


class RCompareDCATest(RCompareTest):
    """Class for testing the DCA algorithm against the R version
    """

    def form_r_args(self, **kwargs):
        valid_keywords = ['thresh_lb', 'thresh_ub', 'thresh_step',
                          'probability', 'harm', 'intervention_per']
        for kw in kwargs:
            if kw not in valid_keywords:
                raise ValueError("did not specify a valid keyword")
        return super(RCompareDCATest, self).form_r_args(**kwargs)

    def run_python_analysis(self):
        """Sets self.nb and self.ia to the net_benefit and interventions_avoided
        for the dca analysis
        """
        return py_dca(self.data, self.outcome, self.predictors,
                      self.thresh_lb, self.thresh_ub, self.thresh_step,
                      self.probability, self.harm, self.intervention_per)


def unpack_r_results_list(res_list):
    """Unpacks the results list to a tuple (net_benefit, interventions_avoided)
    for comparison with the results of Python

    Parameters:
    -----------
    res_list : a list of results from the R analysis (returned by the R dca function)

    Returns:
    --------
    a length-2 tuple of pandas DataFrames equivalent to those yielded by the
    Python anaylsis
    (net_benefit, interventions_avoided)
    """
    r_nb = pdcom.convert_robj(res_list.rx('net.benefit'))
    r_nb = r_nb['net.benefit']  #unpack dataFrame from dict
    r_ia = pdcom.convert_robj(res_list.rx('interventions.avoided'))
    r_ia = r_ia['interventions.avoided']
    #reindex the df's with their threshold columns
    r_nb.index = r_nb['threshold']
    r_ia.index = r_ia['threshold']
    return r_nb, r_ia


def generate_df():
    """Create a "dummy" dataframe for use within a test
    Loads data from dca.csv in this file's directory
    """
    from os import path
    csv_path = path.join(path.dirname(path.realpath(__file__)),
                         "dca.csv")

    return pd.read_csv(csv_path)
