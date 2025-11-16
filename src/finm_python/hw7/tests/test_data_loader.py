"""
Unit Tests for Data Loader Module

Tests to validate:
- Correct CSV parsing
- Timestamp handling
- Symbol extraction
- Filtering functionality
- Benchmark accuracy

TODO: Implement test cases to verify your data_loader implementation.
"""

import pytest
from pathlib import Path

# TODO: Import your data_loader module
# from finm_python.hw7 import data_loader


class TestPandasLoader:
    """Tests for pandas data loading functionality."""

    def test_load_csv_returns_dataframe(self):
        """Test that load_with_pandas returns a pandas DataFrame."""
        # TODO: Implement test
        # Hint: Use isinstance() to check type
        pytest.skip("Implement this test")

    def test_dataframe_has_correct_columns(self):
        """Test that DataFrame has timestamp, symbol, and price columns."""
        # TODO: Implement test
        pytest.skip("Implement this test")

    def test_timestamp_is_datetime(self):
        """Test that timestamp is properly parsed as datetime."""
        # TODO: Implement test
        pytest.skip("Implement this test")

    def test_symbols_are_strings(self):
        """Test that symbol column contains strings."""
        # TODO: Implement test
        pytest.skip("Implement this test")

    def test_prices_are_numeric(self):
        """Test that price column contains numeric values."""
        # TODO: Implement test
        pytest.skip("Implement this test")


class TestPolarsLoader:
    """Tests for polars data loading functionality."""

    def test_load_csv_returns_dataframe(self):
        """Test that load_with_polars returns a polars DataFrame."""
        # TODO: Implement test
        pytest.skip("Implement this test")

    def test_dataframe_has_correct_columns(self):
        """Test that DataFrame has timestamp, symbol, and price columns."""
        # TODO: Implement test
        pytest.skip("Implement this test")

    def test_timestamp_is_datetime(self):
        """Test that timestamp is properly parsed as datetime."""
        # TODO: Implement test
        pytest.skip("Implement this test")


class TestSymbolOperations:
    """Tests for symbol extraction and filtering."""

    def test_get_symbols_returns_list(self):
        """Test that get_symbols returns a list."""
        # TODO: Implement test
        pytest.skip("Implement this test")

    def test_get_symbols_unique_values(self):
        """Test that get_symbols returns unique values."""
        # TODO: Implement test
        pytest.skip("Implement this test")

    def test_filter_by_symbol_pandas(self):
        """Test filtering pandas DataFrame by symbol."""
        # TODO: Implement test
        pytest.skip("Implement this test")

    def test_filter_by_symbol_polars(self):
        """Test filtering polars DataFrame by symbol."""
        # TODO: Implement test
        pytest.skip("Implement this test")

    def test_filter_returns_only_specified_symbol(self):
        """Test that filtered data contains only the specified symbol."""
        # TODO: Implement test
        pytest.skip("Implement this test")


class TestBenchmarking:
    """Tests for benchmarking functionality."""

    def test_benchmark_returns_dict(self):
        """Test that benchmark_ingestion returns a dictionary."""
        # TODO: Implement test
        pytest.skip("Implement this test")

    def test_benchmark_contains_pandas_metrics(self):
        """Test that benchmark includes pandas metrics."""
        # TODO: Implement test
        pytest.skip("Implement this test")

    def test_benchmark_contains_polars_metrics(self):
        """Test that benchmark includes polars metrics."""
        # TODO: Implement test
        pytest.skip("Implement this test")

    def test_benchmark_times_are_positive(self):
        """Test that benchmark times are positive numbers."""
        # TODO: Implement test
        pytest.skip("Implement this test")
