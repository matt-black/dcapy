"""
Decision Curve Analysis

Functional, end-to-end tests of the accuracy of the DCA algorithm

Author: Matthew Black
"""
import unittest
from dcapy.algo import dca
from test.r_analysis import load_r_results, load_default_data


class UnivCancerFamHistTest(unittest.TestCase):

    data = load_default_data()
    outcome = 'cancer'
    predictors = 'famhistory'
    r_nb, r_ia = load_r_results('univ_canc_famhist')

    def setUp(self):
        self.p_nb, self.p_ia = dca(self.data, self.outcome, self.predictors)

    def test_purecompare(self):
        """Performs element-wise comparison of the famhistory columns of both
        result dataframes
        """
        #element-wise comparison
        for i, nb in enumerate(self.r_nb['famhistory']):
            p_ind = (i+1)/100
            try:
                self.assertAlmostEqual(self.p_nb['famhistory'][p_ind], nb, delta=0.0001)
            except AssertionError as e:
                msg_string = 'i: {0} || r_nb: {1} | p_nb: {2}'.format(i, nb, self.p_nb['famhistory'][i])
                e.args += (msg_string)
                raise

        for i, ia in enumerate(self.r_ia['famhistory']):
            p_ind = (1+i)/100
            self.assertAlmostEqual(self.p_ia['famhistory'][p_ind], ia, delta=0.0001,
                                   msg='r: {0} | p: {1}'.format(ia, self.p_ia['famhistory'][i]))


if __name__ == "__main__":
    unittest.main()
