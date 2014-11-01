"""
Functional tests for the dcapy module

Author: Matthew Black 
"""
import unittest
import pandas as pd
import dcapy

class UnivariateAnalysisTest(unittest.TestCase):
    """Test to check the accuracy and functionality of univariate analysis by
    running the same simulation as performed in the dca tutorial 
    """
    def setUp(self):
        self.data = generate_df()
        self.outcome = "cancer"
        self.predictors = "famhistory"

    def test_run_analysis(self):
        net_ben, int_avd = dcapy.dca(self.data, self.outcome, self.predictors)
        #TODO: finish comparing this result with rpy2
        

def generate_df():
    """Create a "dummy" dataframe for use within a test
    Loads data from dca.csv in this file's directory
    """
    from os import path
    csv_path = path.join(path.dirname(path.realpath(__file__)),
                         "dca.csv")
    
    return pd.read_csv(csv_path)
    

if __name__ == "__main__":
    unittest.main()