"""
Rolling Metrics Module for HW7: Parallel Computing

This module computes rolling analytics for financial time-series data,
implementing calculations in both pandas and polars for comparison.

Learning Objectives:
- Compute rolling statistics (moving average, standard deviation)
- Calculate risk-adjusted returns (Sharpe ratio)
- Compare pandas vs polars syntax and performance for rolling operations
"""
import timeit
from typing import Any, Dict
import pandas as pd
import polars as pl

from src.finm_python.hw7 import load_with_pandas, load_with_polars


def compute_rolling_metrics_pandas(df: Any, window: int = 20) -> Any:
    """
    Compute rolling metrics using pandas.

    Args:
        df: pandas DataFrame with 'price' column (single symbol data)
        window: Rolling window size (default: 20)

    Returns:
        pandas.DataFrame: Original DataFrame with additional columns:
            - rolling_ma
            - rolling_std
            - rolling_sharpe
    """
    df = df.copy()

    grouped = df.groupby("symbol")
    df["rolling_ma"] = grouped["price"].transform(
        lambda x: x.rolling(window).mean()
    )
    df["rolling_std"] = grouped["price"].transform(
        lambda x: x.rolling(window).std()
    )
    df["return"] = grouped["price"].transform(lambda x: x.pct_change())
    df["rolling_sharpe"] = grouped["return"].transform(
        lambda x: x.rolling(window).mean() / x.rolling(window).std()
    )

    return df


def compute_rolling_metrics_polars(df: Any, window: int = 20) -> Any:
    """
    Compute rolling metrics using polars.

    Calculates for each row:
    - rolling_ma: 20-period moving average of price
    - rolling_std: 20-period rolling standard deviation of price
    - rolling_sharpe: Rolling Sharpe ratio (returns / volatility, rf=0)

    Args:
        df: polars DataFrame with 'price' column (single symbol data)
        window: Rolling window size (default: 20)

    Returns:
        polars.DataFrame: Original DataFrame with additional columns:
            - rolling_ma
            - rolling_std
            - rolling_sharpe
    """
    df = df.clone()
    df = df.with_columns(
        pl.col("price").rolling_mean(window).over("symbol").alias("rolling_ma"),
        pl.col("price").rolling_std(window).over("symbol").alias("rolling_std"),
        pl.col("price").pct_change().over("symbol").alias("return")
    ).with_columns(
        (pl.col("return").rolling_mean(window).over("symbol") /
        pl.col("return").rolling_std(window).over("symbol")).alias("rolling_sharpe")
    )

    return df


def compute_rolling_symbol(df: Any, symbol: str, window: int = 20) -> Any:
    if isinstance(df, pd.DataFrame):
        symbol_df = df[df["symbol"] == symbol]
        metrics = compute_rolling_metrics_pandas(symbol_df, window=window)
    elif isinstance(df, pl.DataFrame):
        symbol_df = df.filter(pl.col("symbol").eq(symbol))
        metrics = compute_rolling_metrics_polars(symbol_df, window=window)
    else:
        raise TypeError(f"Expected Pandas or Polars dataframe, got {type(df)}")

    return metrics


def benchmark_rolling_metrics(
    pandas_df: Any,
    polars_df: Any,
    window: int = 20
) -> Dict[str, float]:
    """
    Benchmark rolling metric computation for pandas vs polars.

    Args:
        pandas_df: pandas DataFrame with market data
        polars_df: polars DataFrame with market data
        window: Rolling window size

    Returns:
        Dictionary with timing results:
        {
            "pandas_time": float,
            "polars_time": float,
            "speedup_factor": float  # polars relative to pandas
        }
    """
    def timer(df: Any, func, window=window):
        start = timeit.default_timer()
        func(df, window)
        end = timeit.default_timer()
        return start - end

    pd_time = timer(pandas_df, compute_rolling_metrics_pandas)
    pl_time = timer(polars_df, compute_rolling_metrics_polars)

    print(f"Polars speedup {pd_time / pl_time:.2f}x comparing with Pandas")

    return {
        "pandas_time": pd_time,
        "polars_time": pl_time,
        "speedup_factor": pd_time / pl_time
    }



if __name__ == '__main__':
    path = "data/market_data-1.csv"
    pd_df = load_with_pandas(path)
    pl_df = load_with_polars(path)
    symbol = "AAPL"
    res = compute_rolling_symbol(pl_df, symbol)
    print(res)