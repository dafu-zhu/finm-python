"""
Unit Tests for Rolling Metrics Module

Tests to validate:
- Correct rolling calculations
- Pandas vs polars equivalence
- Sharpe ratio calculation
- Edge cases handling

TODO: Implement test cases to verify your metrics implementation.
"""

import pytest
import numpy as np

# TODO: Import your metrics module
# from finm_python.hw7 import metrics


class TestRollingMetricsPandas:
    """Tests for pandas rolling metric calculations."""

    def test_rolling_ma_calculation(self):
        """Test that rolling moving average is calculated correctly."""
        # TODO: Implement test
        # Hint: Create small test dataset, compute manually, compare
        pytest.skip("Implement this test")

    def test_rolling_std_calculation(self):
        """Test that rolling standard deviation is calculated correctly."""
        # TODO: Implement test
        pytest.skip("Implement this test")

    def test_rolling_sharpe_calculation(self):
        """Test that rolling Sharpe ratio is calculated correctly."""
        # TODO: Implement test
        # Hint: Sharpe = mean(returns) / std(returns)
        pytest.skip("Implement this test")

    def test_output_has_all_columns(self):
        """Test that output DataFrame has all expected columns."""
        # TODO: Implement test
        # Expected: rolling_ma, rolling_std, rolling_sharpe
        pytest.skip("Implement this test")

    def test_first_n_rows_are_nan(self):
        """Test that first (window-1) rows have NaN for rolling metrics."""
        # TODO: Implement test
        pytest.skip("Implement this test")


class TestRollingMetricsPolars:
    """Tests for polars rolling metric calculations."""

    def test_rolling_ma_calculation(self):
        """Test that rolling moving average is calculated correctly."""
        # TODO: Implement test
        pytest.skip("Implement this test")

    def test_rolling_std_calculation(self):
        """Test that rolling standard deviation is calculated correctly."""
        # TODO: Implement test
        pytest.skip("Implement this test")

    def test_rolling_sharpe_calculation(self):
        """Test that rolling Sharpe ratio is calculated correctly."""
        # TODO: Implement test
        pytest.skip("Implement this test")

    def test_output_has_all_columns(self):
        """Test that output DataFrame has all expected columns."""
        # TODO: Implement test
        pytest.skip("Implement this test")


class TestPandasPolarsEquivalence:
    """Tests to ensure pandas and polars produce equivalent results."""

    def test_rolling_ma_equivalence(self):
        """Test that pandas and polars produce same MA values."""
        # TODO: Implement test
        # Hint: Use np.allclose() for floating point comparison
        pytest.skip("Implement this test")

    def test_rolling_std_equivalence(self):
        """Test that pandas and polars produce same std values."""
        # TODO: Implement test
        pytest.skip("Implement this test")

    def test_rolling_sharpe_equivalence(self):
        """Test that pandas and polars produce same Sharpe values."""
        # TODO: Implement test
        pytest.skip("Implement this test")


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_window_larger_than_data(self):
        """Test behavior when window is larger than dataset."""
        # TODO: Implement test
        pytest.skip("Implement this test")

    def test_empty_dataframe(self):
        """Test behavior with empty DataFrame."""
        # TODO: Implement test
        pytest.skip("Implement this test")

    def test_single_value_dataframe(self):
        """Test behavior with single value."""
        # TODO: Implement test
        pytest.skip("Implement this test")
