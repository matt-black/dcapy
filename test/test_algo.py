"""
Decision Curve Analysis

Functional, end-to-end tests of the accuracy of the DCA algorithm

Author: Matthew Black
"""
import unittest
from dcapy.algo import dca
from test import load_r_results, load_default_data

class UnivCancerFamHistTest(unittest.TestCase):

    data = load_default_data()
    outcome = 'cancer'
    predictors = ['famhistory']
    thresh_lo = 0.01
    thresh_hi = 0.99
    thresh_step = 0.01
    r_nb, r_ia = load_r_results('univ_canc_famhist')

    def setUp(self):
        probs = [True]*len(self.predictors)
        harms = [0]*len(self.predictors)
        self.p_nb, self.p_ia = dca(self.data, self.outcome, self.predictors,
                                   probabilities=probs, harms=harms)

    def test_compare_net_benefit(self):
        """Performs element-wise comparison of the famhistory columns of net benefits dataframes from each analysis
        """
        for i in range(1,99):
            try:
                self.assertAlmostEqual(self.p_nb['famhistory'][i], 
                                       self.r_nb['famhistory'][i], delta=0.0001)
            except AssertionError as e:
                msg_string = 'i: {0} || r_nb: {1} | p_nb: {2}'.format(i, self.r_nb['famhistory'][i],
                                                                      self.p_nb['famhistory'][j])
                e.args += (msg_string)
                raise

    def test_compare_interv_avoided(self):
        """Performs element-wise commparison of the famhistory columns of interventions avoided dataframes from each analysis
        """
        for i in range(1,99):
            try:
                self.assertAlmostEqual(self.p_ia['famhistory'][i], 
                                       self.r_ia['famhistory'][i], delta=0.0001)
            except AssertionError as e:
                msg_string = 'i: {0} || r_ia: {1} | p_ia: {2}'.format(i, self.r_ia['famhistory'][i],
                                                                      self.p_ia['famhistory'][j])
                e.args += (msg_string)
                raise

if __name__ == "__main__":
    unittest.main()