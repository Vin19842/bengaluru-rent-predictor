"""Regression checks for year selection and property filters."""

from pathlib import Path
import unittest

import pandas as pd

from src.comparables import select_comparables
from src.forecast import BASE_YEAR, FORECAST_YEARS, forecast_rent

ROOT = Path(__file__).resolve().parents[1]


class ForecastTests(unittest.TestCase):
    def test_year_selector_includes_2029(self):
        self.assertEqual(FORECAST_YEARS, (2026, 2027, 2028, 2029))

    def test_base_year_returns_observed_rent(self):
        self.assertEqual(forecast_rent(25_000, 10.38, BASE_YEAR), 25_000)

    def test_2029_is_three_compound_years(self):
        expected = 25_000 * (1 + 10.38 / 100) ** 3
        self.assertAlmostEqual(forecast_rent(25_000, 10.38, 2029), expected)

    def test_forecasts_increase_with_year_at_positive_rate(self):
        values = [forecast_rent(25_000, 2.22, year) for year in FORECAST_YEARS]
        self.assertEqual(values, sorted(values))

    def test_rejects_year_outside_dashboard_range(self):
        with self.assertRaises(ValueError):
            forecast_rent(25_000, 4.0, 2030)


class ComparableFilterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.listings = pd.read_csv(ROOT / "data/market/koramangala-asking-listings-2026-10.csv")

    def test_1400_sqft_carpet_filter_matches_expected_sample(self):
        matches = select_comparables(
            self.listings,
            bhk=2,
            area_sqft=1400,
            area_basis="carpet",
            size_tolerance_pct=25,
        )
        self.assertEqual(len(matches), 4)
        self.assertEqual(matches["rent_inr"].median(), 60_000)

    def test_area_basis_filter_changes_matches(self):
        carpet = select_comparables(self.listings, bhk=2, area_sqft=1400, area_basis="carpet", size_tolerance_pct=25)
        super_area = select_comparables(self.listings, bhk=2, area_sqft=1400, area_basis="super", size_tolerance_pct=25)
        self.assertNotEqual(set(carpet["record_id"]), set(super_area["record_id"]))

    def test_mixed_area_filter_can_include_multiple_measurements(self):
        matches = select_comparables(self.listings, bhk=2, area_sqft=1400, area_basis="unknown / mixed", size_tolerance_pct=25)
        self.assertGreater(matches["area_basis"].nunique(), 1)


if __name__ == "__main__":
    unittest.main()

