"""
Decision Curve Analysis

Useful test utilities

Author: Matthew Black
"""
import pandas as pd
from os import path

#useful directories
root_test_dir = path.dirname(path.realpath(__file__))
resources_dir = path.join(root_test_dir, 'resource')
r_results_dir = path.join(resources_dir, 'r_results')

def load_default_data():
    """Create a new dataframe from dca.csv in the resource directory

    Returns
    -------
    pd.DataFrame
        a dataframe of the data
    """
    csv_path = path.join(resources_dir, 'dca.csv')
    return pd.read_csv(csv_path)


def load_r_results(analysis_name):
    """Loads the net_benefit and interventions_avoided results for an R analysis

    Parameters
    ----------
    analysis_name : str
        the name to give to the analysis (this will be the name used by the folder
        created where the output csv's are saved)

    Returns
    -------
    tuple(pd.DataFrame, pd.DataFrame)
        `net benefit` and `interventions avoided` dataframes
    """
    analysis_dir = path.join(r_results_dir, analysis_name)
    r_nb = pd.read_csv(path.join(analysis_dir, 'net_benefit.csv'))
    r_ia = pd.read_csv(path.join(analysis_dir, 'interventions_avoided.csv'))
    return r_nb, r_ia