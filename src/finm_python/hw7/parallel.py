"""
Parallel Processing Module for HW7: Parallel Computing

This module implements threading and multiprocessing approaches for
parallel computation of financial metrics across multiple symbols.

Learning Objectives:
- Understand Python's Global Interpreter Lock (GIL) and its impact
- Implement concurrent execution using ThreadPoolExecutor
- Implement parallel execution using ProcessPoolExecutor
- Compare performance characteristics of threading vs multiprocessing
- Learn when to use each approach for different workloads

Key Concepts:
- Threading: Concurrent execution, shared memory, limited by GIL for CPU-bound tasks
- Multiprocessing: True parallelism, separate memory spaces, overhead for data transfer
"""

import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from typing import Any, Callable, Dict, List, Tuple
import pandas as pd
import polars as pl

from src.finm_python.hw7 import (
load_with_pandas,
load_with_polars,
compute_rolling_metrics_pandas,
compute_rolling_metrics_polars,
compute_rolling_symbol
)


def process_symbols_sequential(
    df: Any,
    symbol_list: List[str],
    processing_func: Callable,
    **kwargs
) -> Tuple[List[Any], float]:
    """
    Process symbols sequentially (baseline for comparison).

    Args:
        df: Dataframe loaded from data source
        symbol_list: List of strings, one per symbol
        processing_func: Function to apply to each symbol's data
        **kwargs: Additional arguments for processing_func

    Returns:
        Tuple of:
            - List of results from processing each symbol
            - Total execution time (seconds)
    """
    res_list = []
    start = time.perf_counter()
    for symbol in symbol_list:
        res = processing_func(df, symbol)
        res_list.append(res)
    end = time.perf_counter()

    return res_list, end - start


def process_symbols_threading(
    df: Any,
    symbol_list: List[str],
    processing_func: Callable,
    max_workers: int = 1,
    **kwargs
) -> Tuple[List[Dict], float]:

    start = time.perf_counter()
    res_list = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(processing_func, df, symbol, **kwargs)
            for symbol in symbol_list
        ]

        for f in as_completed(futures):
            res_list.append(f.result())
    end = time.perf_counter()

    return res_list, end - start

def _process_single_symbol_data(args_tuple):
    """
    Helper function for multiprocessing: unpack arguments and process symbol data.

    This function takes pre-filtered data to minimize serialization overhead.

    Args:
        args_tuple: Tuple of (symbol_data, symbol, processing_func, kwargs_dict)

    Returns:
        Result from processing_func
    """
    symbol_data, symbol, processing_func, kwargs = args_tuple
    return processing_func(symbol_data, symbol, **kwargs)


def process_symbols_multiprocessing(
    df: Any,
    symbol_list: List[str],
    processing_func: Callable,
    max_workers: int = 1,
    **kwargs
) -> Tuple[List[Dict], float]:

    start = time.perf_counter()
    res_list = []

    # Pre-filter data by symbol to minimize serialization overhead
    # Only send each worker the data it needs, not the entire dataframe
    symbol_data_map = {}
    if isinstance(df, pd.DataFrame):
        for symbol in symbol_list:
            symbol_data_map[symbol] = df[df["symbol"] == symbol].copy()
    elif isinstance(df, pl.DataFrame):
        for symbol in symbol_list:
            symbol_data_map[symbol] = df.filter(pl.col("symbol") == symbol)
    else:
        # Fallback: use original behavior if unknown dataframe type
        symbol_data_map = {symbol: df for symbol in symbol_list}

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(_process_single_symbol_data, (symbol_data_map[symbol], symbol, processing_func, kwargs))
            for symbol in symbol_list
        ]

        for f in as_completed(futures):
            res_list.append(f.result())
    end = time.perf_counter()

    return res_list, end - start


def compare_parallel_approaches(
    df: Any,
    symbol_list: List[str],
    processing_func: Callable,
    max_workers: int = 1,
    **kwargs
) -> Dict[str, Dict[str, Any]]:
    """
    Compare sequential, threading, and multiprocessing performance.

    Returns:
        Dictionary with performance comparison:
        {
            "sequential": {
                "time": float,
                "results": List[Dict]
            },
            "threading": {
                "time": float,
                "results": List[Dict],
                "speedup": float  # relative to sequential
            },
            "multiprocessing": {
                "time": float,
                "results": List[Dict],
                "speedup": float  # relative to sequential
            }
        }

    Expected Implementation:
        1. Run sequential processing
        2. Run threading-based processing
        3. Run multiprocessing-based processing
        4. Calculate speedup factors
        5. Verify results consistency across approaches
        6. Return comparison dictionary
    """
    seq_res, seq_time = process_symbols_sequential(df, symbol_list, processing_func)
    thr_res, thr_time = process_symbols_threading(df, symbol_list, processing_func, max_workers)
    mpr_res, mpr_time = process_symbols_multiprocessing(df, symbol_list, processing_func, max_workers)
    return {
        "sequential": {
            "time": seq_time,
            "results": seq_res
        },
        "threading": {
            "time": thr_time,
            "results": thr_res,
            "speedup": seq_time / thr_time  # relative to sequential
        },
        "multiprocessing": {
            "time": mpr_time,
            "results": mpr_res,
            "speedup": seq_time / mpr_time  # relative to sequential
        }
    }


def measure_resource_usage(func: Callable, *args, **kwargs) -> Dict[str, float]:
    """
    Measure CPU and memory usage during function execution.

    Args:
        func: Function to execute and monitor
        *args: Positional arguments for func
        **kwargs: Keyword arguments for func

    Returns:
        Dictionary with resource metrics:
        {
            "execution_time": float,
            "cpu_percent": float,
            "memory_mb": float,
            "result": Any  # function return value
        }

    Expected Implementation:
        1. Get initial memory and CPU state
        2. Execute function
        3. Measure final memory and CPU usage
        4. Return metrics dictionary

    Hints:
        - Use psutil.Process() for process monitoring
        - Use psutil.cpu_percent() for CPU usage
        - Memory: process.memory_info().rss / (1024 * 1024) for MB
    """
    # TODO: Implement resource usage monitoring
    # Hint: Use psutil library for CPU and memory monitoring
    raise NotImplementedError("Implement resource usage measurement")


def get_optimal_worker_count() -> int:
    """
    Determine optimal number of workers for parallel processing.

    Returns:
        Recommended number of workers based on system resources

    Expected Implementation:
        1. Get available CPU count
        2. Consider memory constraints
        3. Return optimal worker count (typically CPU count - 1 or CPU count)

    Hint:
        - Use os.cpu_count() or multiprocessing.cpu_count()
    """
    # TODO: Implement optimal worker count determination
    raise NotImplementedError("Implement optimal worker count determination")


if __name__ == '__main__':
    path = "data/market_data-1.csv"
    pd_df = load_with_pandas(path)
    pl_df = load_with_polars(path)
    symbols = ["AAPL", "MSFT", "SPY"]
    res = compare_parallel_approaches(pd_df, symbols, compute_rolling_symbol)
    print(res)