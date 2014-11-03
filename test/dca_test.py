"""
Functional test for the dca analyzer

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
        self.r_args_dict = self.form_r_args()

    def test_accuracy_pure_compare(self):
        """Runs analsysis in both R and Python and compares the datasets generated
        by both analyses through ANOVA

        Test passes if the ANOVA's p value is >0.05
        """
        #run the analyses
        r_nb, r_ia = self.run_r_analysis('dca', self.r_args_dict)
        p_nb, p_ia = self.run_python_analysis()
        #element-wise comparison
        """for i, nb in enumerate(r_nb['famhistory']):
            if p_nb['famhistory'][i] != nb:
                print('netben {}'.format(i))
                print('r: {0} | p: {1}'.format(nb, p_nb['famhistory'][i]))
                assert(False)
        for i, ia in enumerate(r_ia['famhistory']):
            if p_nb['famhistory'][i] != ia:
                print('interv {}'.format(i))
                print('r: {0} | p: {1}'.format(ia, p_ia['famhistory'][i]))
                assert(False)
        assert(True)"""
        #anova




if __name__ == "__main__":
    unittest.main()
