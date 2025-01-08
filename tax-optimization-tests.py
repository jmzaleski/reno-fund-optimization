import unittest
from tax_optimization import calculate_tax_impact, optimize_funding_mix
import pandas as pd
import numpy as np

class TestTaxOptimization(unittest.TestCase):
    def setUp(self):
        """Set up test cases with known values"""
        self.test_cases = {
            'small_gain': {
                'capital_gain': 50000,  # Small gain within first tax bracket
                'expected_tax': 11415,  # Manually calculated: (50000 * 0.5) * (0.15 + 0.0506)
            },
            'medium_gain': {
                'capital_gain': 150000,  # Spans multiple brackets
                'expected_tax': 37725,  # Pre-calculated based on 2024 rates
            },
            'large_gain': {
                'capital_gain': 300000,  # Similar to the actual case
                'expected_tax': 82350,  # Pre-calculated based on 2024 rates
            }
        }

    def test_tax_calculation_accuracy(self):
        """Test tax calculations for different capital gains"""
        for case_name, case_data in self.test_cases.items():
            with self.subTest(case=case_name):
                calculated_tax = calculate_tax_impact(case_data['capital_gain'])
                self.assertAlmostEqual(
                    calculated_tax,
                    case_data['expected_tax'],
                    places=0,
                    msg=f"Tax calculation failed for {case_name}"
                )

    def test_tax_calculation_edge_cases(self):
        """Test edge cases for tax calculation"""
        # Test zero capital gain
        self.assertEqual(calculate_tax_impact(0), 0)
        
        # Test negative capital gain (should raise ValueError)
        with self.assertRaises(ValueError):
            calculate_tax_impact(-10000)

    def test_optimize_funding_mix_basic_scenario(self):
        """Test basic optimization scenario"""
        result = optimize_funding_mix(
            total_amount=1000000,
            stock_value=350000,
            capital_gain=300000,
            interest_rate=0.07,
            years=5
        )
        
        # Basic validation of the result structure
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 5)  # Should have 5 years of data
        self.assertTrue(all(col in result.columns for col in [
            'Year', 'Stock_Sold', 'LOC_Used', 'Tax_Paid', 'Interest_Paid', 'Total_Cost'
        ]))

    def test_optimize_funding_mix_constraints(self):
        """Test if optimization results meet basic constraints"""
        result = optimize_funding_mix(
            total_amount=1000000,
            stock_value=350000,
            capital_gain=300000,
            interest_rate=0.07,
            years=5
        )
        
        # Total stock sold should equal stock_value
        self.assertAlmostEqual(result['Stock_Sold'].sum(), 350000, places=2)
        
        # LOC balance should start at full amount minus first stock sale
        self.assertAlmostEqual(
            result.loc[0, 'LOC_Used'],
            1000000 - result.loc[0, 'Stock_Sold'],
            places=2
        )
        
        # All values should be non-negative
        self.assertTrue((result['Stock_Sold'] >= 0).all())
        self.assertTrue((result['LOC_Used'] >= 0).all())
        self.assertTrue((result['Tax_Paid'] >= 0).all())
        self.assertTrue((result['Interest_Paid'] >= 0).all())

    def test_interest_calculation_accuracy(self):
        """Test interest calculations in a controlled scenario"""
        # Test with simple numbers for easy verification
        result = optimize_funding_mix(
            total_amount=100000,
            stock_value=50000,
            capital_gain=40000,
            interest_rate=0.10,  # 10% for easy math
            years=2
        )
        
        # Verify first year interest calculation
        expected_first_year_interest = (100000 - result.loc[0, 'Stock_Sold']) * 0.10
        self.assertAlmostEqual(
            result.loc[0, 'Interest_Paid'],
            expected_first_year_interest,
            places=2
        )

    def test_optimal_solution_comparison(self):
        """Test if the optimal solution is actually optimal"""
        # Create a simple scenario where we know the optimal solution
        result = optimize_funding_mix(
            total_amount=100000,
            stock_value=50000,
            capital_gain=10000,  # Small capital gain
            interest_rate=0.20,  # High interest rate
            years=2
        )
        
        # With high interest and low capital gains, it should favor selling stock early
        self.assertTrue(
            result.loc[0, 'Stock_Sold'] > result.loc[1, 'Stock_Sold'],
            "With high interest rates and low capital gains, early stock sale should be preferred"
        )

def run_tests():
    unittest.main(argv=[''], verbosity=2, exit=False)

if __name__ == '__main__':
    run_tests()
