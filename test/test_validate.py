"""
Decision Curve Analysis

Tests for validation functions that are not covered by doctests

Author: Matthew Black
"""

import unittest
from test import load_default_data
from dcapy.validate import outcome_validate, DCAError


class TestOutcomeValidate(unittest.TestCase):
    
    def setUp(self):
        """Loads the dataset for each test
        """
        self.data = load_default_data()

    def test_not_in_data(self):
        """Tests that an outcome that isn't a column in the data
        set raises a DCAError
        """
        with self.assertRaises(DCAError):
            outcome = outcome_validate(self.data, 'not_an_outcome')

    def test_value_outbounds(self):
        """Tests that a value not in range 0-1 raises ValueError
        """
        outcome = 'cancer'
        self.data.set_value(10, outcome, 2)
        with self.assertRaises(ValueError):
            outcome = outcome_validate(self.data, 'cancer')

    def test_default_ok(self):
        """Tests that a known-good dataset passes
        """
        outcome = outcome_validate(self.data, 'cancer')
        self.assertEqual(outcome, 'cancer')


if __name__ == '__main__':
    unittest.main()
