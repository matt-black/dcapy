"""
Decision Curve Analysis

Tests for the DecisionCurveAnalysis class

Author: Matthew Black
"""

import unittest
from dcapy import DecisionCurveAnalysis
from dcapy.algo import dca
from test import load_r_results, load_default_data

class UnivCancerFamHistTest(unittest.TestCase):
    """Test whether the class properly implements the raw algorithm
    """

    data = load_default_data()
    outcome = 'cancer'
    predictors = 'famhistory'
    probs = [True]
    harms = [0]

    def setUp(self):
        self.dca = DecisionCurveAnalysis('dca', data=self.data, outcome=self.outcome,
                                         predictors=self.predictors)
        self.dca.run()
        self.p_nb, self.p_ia = dca(self.data, self.outcome, [self.predictors],
                                   probabilities=self.probs, harms=self.harms)

    def test_compare_net_benefit(self):
        cls_nb = self.dca.results['net benefit']
        for i in range(1,99):
            try:
                self.assertEqual(self.p_nb['famhistory'][i], 
                                       cls_nb['famhistory'][i])
            except AssertionError as e:
                msg_string = 'i: {0} || cls_nb: {1} | p_nb: {2}'.format(i, cls_nb['famhistory'][i],
                                                                self.p_nb['famhistory'][j])
                e.args += (msg_string)
                raise

    def test_compare_interv_avoid(self):
        cls_ia = self.dca.results['interventions avoided']
        for i in range(1,99):
            try:
                self.assertEqual(self.p_ia['famhistory'][i], 
                                       cls_ia['famhistory'][i])
            except AssertionError as e:
                msg_string = 'i: {0} || cls_ia: {1} | p_ia: {2}'.format(i, cls_ia['famhistory'][i],
                                                                      self.p_ia['famhistory'][j])
                e.args += (msg_string)
                raise

if __name__ == '__main__':
    unittest.main()
