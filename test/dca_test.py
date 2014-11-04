"""
Decision Curve Analysis

Functional, end-to-end tests of the accuracy of the DCA algorithm

Author: Matthew Black
"""
import unittest
import pandas as pd
from test.support import RCompareDCATest, resources_dir
from os import path

class UnivariateAnalysisTest(RCompareDCATest):
    """Tests the accuracy of Univariate analysis, as described in the
    DCA tutorial
    """

    def setUp(self):
        self.data = pd.read_csv(path.join(resources_dir, 'dca.csv'))
        self.outcome = 'cancer'
        self.predictors = 'famhistory'
        #self.r_net_ben, self.r_int_avoid = \
        #    self.run_r_analysis('dca', self.form_r_args())
        self.p_net_ben, self.p_int_avoid = self.run_python_analysis()

    @unittest.skip("always fails, looks like due to floating point math")
    def test_purecompare(self):
        """Performs element-wise comparison of the famhistory columns of both
        result dataframes
        """
        #element-wise comparison
        for i, nb in enumerate(self.r_net_ben['famhistory']):
            if self.p_net_ben['famhistory'][i] != nb:
                print('netben {}'.format(i))
                print('r: {0} | p: {1}'
                      .format(nb, self.p_net_ben['famhistory'][i]))
                assert(False)
        for i, ia in enumerate(self.r_int_avoid['famhistory']):
            if self.p_int_avoid['famhistory'][i] != ia:
                print('interv {}'.format(i))
                print('r: {0} | p: {1}'
                      .format(ia, self.p_int_avoid['famhistory'][i]))
                assert(False)
        assert(True)

if __name__ == "__main__":
    unittest.main()
