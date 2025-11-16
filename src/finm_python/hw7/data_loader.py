"""
Data Loader Module for HW7: Parallel Computing

This module handles loading market data using both pandas and polars libraries,
allowing for performance comparison between the two approaches.

Learning Objectives:
- Understand data ingestion patterns in pandas vs polars
- Measure and compare memory usage and load times
- Parse time-series data into appropriate data structures

TODO: Implement the functions below to complete the data loading functionality.
"""

import time
from pathlib import Path
from typing import Any, Dict, Tuple

# TODO: Import pandas
# import pandas as pd

# TODO: Import polars
# import polars as pl


def load_with_pandas(file_path: str) -> Any:
    """
    Load market data CSV using pandas.

    The CSV file has columns: timestamp, symbol, price

    Args:
        file_path: Path to the CSV file containing market data

    Returns:
        pandas.DataFrame: DataFrame with parsed timestamp as index

    Expected Implementation:
        1. Read CSV file using pd.read_csv()
        2. Parse 'timestamp' column as datetime
        3. Set timestamp as index (optional but recommended)
        4. Return the DataFrame

    Example:
        >>> df = load_with_pandas("path/to/market_data.csv")
        >>> df.head()
                            symbol   price
        timestamp
        2025-10-01 09:30:00   AAPL  169.89
        2025-10-01 09:30:00   MSFT  320.22
    """
    # TODO: Implement pandas data loading
    # Hint: Use pd.read_csv() with parse_dates parameter
    raise NotImplementedError("Implement pandas data loading")


def load_with_polars(file_path: str) -> Any:
    """
    Load market data CSV using polars.

    The CSV file has columns: timestamp, symbol, price

    Args:
        file_path: Path to the CSV file containing market data

    Returns:
        polars.DataFrame: DataFrame with parsed timestamp column

    Expected Implementation:
        1. Read CSV file using pl.read_csv()
        2. Parse 'timestamp' column as datetime
        3. Return the DataFrame

    Example:
        >>> df = load_with_polars("path/to/market_data.csv")
        >>> df.head()
        shape: (5, 3)
        ┌─────────────────────┬────────┬────────┐
        │ timestamp           ┆ symbol ┆ price  │
        │ ---                 ┆ ---    ┆ ---    │
        │ datetime[μs]        ┆ str    ┆ f64    │
        └─────────────────────┴────────┴────────┘
    """
    # TODO: Implement polars data loading
    # Hint: Use pl.read_csv() and cast timestamp column
    raise NotImplementedError("Implement polars data loading")


def benchmark_ingestion(file_path: str) -> Dict[str, Dict[str, float]]:
    """
    Benchmark data ingestion performance for pandas vs polars.

    Measures:
    - Load time (seconds)
    - Memory usage (bytes)

    Args:
        file_path: Path to the CSV file

    Returns:
        Dictionary with performance metrics for each library:
        {
            "pandas": {"load_time": float, "memory_bytes": float},
            "polars": {"load_time": float, "memory_bytes": float}
        }

    Expected Implementation:
        1. Time the load_with_pandas() function
        2. Measure memory usage of resulting DataFrame
        3. Time the load_with_polars() function
        4. Measure memory usage of resulting DataFrame
        5. Return comparison dictionary

    Hints:
        - Use time.perf_counter() for timing
        - For pandas memory: df.memory_usage(deep=True).sum()
        - For polars memory: df.estimated_size()
    """
    # TODO: Implement benchmarking logic
    # Hint: Use time.perf_counter() for accurate timing
    raise NotImplementedError("Implement ingestion benchmarking")


def get_symbols(df: Any) -> list:
    """
    Extract unique symbols from the DataFrame.

    Works with both pandas and polars DataFrames.

    Args:
        df: DataFrame (pandas or polars)

    Returns:
        List of unique symbol strings

    Expected Implementation:
        1. Detect if df is pandas or polars DataFrame
        2. Extract unique values from 'symbol' column
        3. Return as Python list
    """
    # TODO: Implement symbol extraction
    # Hint: Check type using isinstance() or hasattr()
    raise NotImplementedError("Implement symbol extraction")


def filter_by_symbol(df: Any, symbol: str) -> Any:
    """
    Filter DataFrame for a specific symbol.

    Works with both pandas and polars DataFrames.

    Args:
        df: DataFrame (pandas or polars)
        symbol: Stock symbol to filter (e.g., "AAPL")

    Returns:
        Filtered DataFrame containing only rows for the specified symbol

    Expected Implementation:
        1. Detect DataFrame type
        2. Apply appropriate filtering syntax
        3. Return filtered DataFrame

    Note:
        - Pandas: df[df['symbol'] == symbol]
        - Polars: df.filter(pl.col('symbol') == symbol)
    """
    # TODO: Implement symbol filtering
    raise NotImplementedError("Implement symbol filtering")
