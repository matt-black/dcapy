"""
Decision Curve Analysis

Unit tests for functions in calc.py

Author: Matthew Black
"""

import unittest
import pandas as pd
from os import path
import dcapy.calc as calc
from test import resources_dir


class CalcTfPositivesTest(unittest.TestCase):
    """Tests the accuracy of the calc_tf_positives() function
    """

    data = pd.read_csv(path.join(resources_dir, "dca.csv"))

    def test_univariate(self):
        """Tests the function for an univariate analysis
        """
        outcome = 'cancer'
        predictor = 'famhistory'
        net_benefit_threshold = pd.Series(data=calc.frange(0.1,0.99,0.1))
        true_pos, false_pos = calc.calc_tf_positives(self.data, outcome,
                                                     predictor, net_benefit_threshold, 0)
        #assersions -- got values from R debugging
        self.assertEqual(true_pos, 24)
        self.assertEqual(false_pos, 91)


class CalcNetBenefitTest(unittest.TestCase):
    """Tests the accuracy of the calculate_net_benefit() function
    """

    def setUp(self):
        pass


if __name__ == "__main__":
    unittest.main()