"""
Data Loader Module for HW7: Parallel Computing

This module handles loading market data using both pandas and polars libraries,
allowing for performance comparison between the two approaches.

Learning Objectives:
- Understand data ingestion patterns in pandas vs polars
- Measure and compare memory usage and load times
- Parse time-series data into appropriate data structures
"""

import time
import sys
from pathlib import Path
from typing import Any, Dict, Tuple
import pandas as pd
import polars as pl


def load_with_pandas(file_path: str) -> Any:
    pd_df = pd.read_csv(file_path, index_col="timestamp")
    return pd_df


def load_with_polars(file_path: str) -> Any:
    pl_df = pl.read_csv(file_path)
    return pl_df

def benchmark_ingestion(file_path: str) -> Dict[str, Dict[str, float]]:
    """
    Benchmark data ingestion performance for pandas vs polars.

    Args:
        file_path: Path to the CSV file

    Returns:
        Dictionary with performance metrics for each library:
        {
            "pandas": {"load_time": float, "memory_bytes": float},
            "polars": {"load_time": float, "memory_bytes": float}
        }
    """
    def performance(path, func):
        start = time.perf_counter()
        df = func(path)
        end = time.perf_counter()
        size = sys.getsizeof(df)
        return end - start, size

    pd_perf = performance(file_path, load_with_pandas)
    pl_perf = performance(file_path, load_with_polars)

    return {
        "pandas": {"load_time": pd_perf[0], "memory_bytes": pd_perf[1]},
        "polars": {"load_time": pl_perf[0], "memory_bytes": pl_perf[1]}
    }

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
    pass


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


if __name__ == '__main__':
    path = "data/market_data-1.csv"
    res = benchmark_ingestion(path)
    print(res)