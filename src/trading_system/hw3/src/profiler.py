"""
Optimization Challenge Benchmarking Script

Compares all optimization strategies:
1. Naive (baseline)
2. Windowed (deque + running sums)
3. Vectorized (NumPy batch processing)
4. Cached (LRU memoization)
5. Streaming (generator-based)
6. Hybrid (combined optimizations)

Generates comprehensive comparison report.
"""

import timeit
import tracemalloc
from pathlib import Path
from typing import List, Dict
from datetime import datetime, timedelta
import numpy as np

# Import optimized strategies
import sys
sys.path.insert(0, str(Path(__file__).parent))

from trading_system.hw3 import (
MarketDataPoint,
NaiveMovingAverageStrategy,
WindowedMovingAverageStrategy,
VectorizedMovingAverageStrategy,
CachedMovingAverageStrategy,
StreamingMovingAverageStrategy,
HybridOptimizedStrategy,
)


def generate_market_data(n_ticks: int, seed: int = 42) -> List[MarketDataPoint]:
    """Generate synthetic market data."""
    np.random.seed(seed)
    returns = np.random.normal(loc=0.0001, scale=0.02, size=n_ticks)
    prices = 100.0 * np.exp(np.cumsum(returns))
    base_time = datetime(2025, 1, 1, 9, 30, 0)

    result = []
    for i, price in enumerate(prices.tolist()):
        data_point = MarketDataPoint(
            timestamp=base_time + timedelta(seconds=i),
            symbol='AAPL',
            price=price
        )
        result.append(data_point)

    return result


def benchmark_strategy(strategy_class, n_ticks: int, params: dict) -> Dict:
    """Benchmark a single strategy."""
    # Generate data
    data = generate_market_data(n_ticks)

    # Time measurement
    strategy = strategy_class(params)

    start_time = timeit.default_timer()
    for tick in data:
        strategy.generate_signals(tick)
    end_time = timeit.default_timer()

    execution_time = end_time - start_time

    # Memory measurement
    strategy = strategy_class(params)
    tracemalloc.start()

    for tick in data:
        strategy.generate_signals(tick)

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Cache info (if applicable)
    cache_info = None
    if hasattr(strategy, 'get_cache_info'):
        cache_info = strategy.get_cache_info()

    return {
        'time': execution_time,
        'time_per_tick': execution_time / n_ticks * 1e6,  # microseconds
        'memory_current': current / 1024 / 1024,  # MB
        'memory_peak': peak / 1024 / 1024,  # MB
        'cache_info': cache_info
    }


def run_comprehensive_benchmark():

    strategies = [
        ('Naive', NaiveMovingAverageStrategy, 'Baseline O(n)'),
        ('Windowed', WindowedMovingAverageStrategy, 'Deque + Running Sums'),
        ('Vectorized', VectorizedMovingAverageStrategy, 'NumPy Batch Processing'),
        ('Cached', CachedMovingAverageStrategy, 'LRU Memoization'),
        ('Streaming', StreamingMovingAverageStrategy, 'Generator-based'),
        ('Hybrid', HybridOptimizedStrategy, 'Combined Optimizations')
    ]

    tick_sizes = [1_000, 10_000, 100_000]
    params = {'short': 5, 'long': 20}

    results = {
        'strategies': [name for name, _, _ in strategies],
        'descriptions': [desc for _, _, desc in strategies],
        'tick_sizes': tick_sizes,
        'params': params,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'data': {}
    }

    # Initialize result storage
    for name, _, _ in strategies:
        results['data'][name] = {
            'times': [],
            'times_per_tick': [],
            'memory_current': [],
            'memory_peak': [],
            'cache_info': []
        }

    print("=" * 80)
    print("OPTIMIZATION CHALLENGE - COMPREHENSIVE BENCHMARK")
    print("=" * 80)
    print(f"\nTesting {len(strategies)} strategies across {len(tick_sizes)} input sizes")
    print(f"Parameters: short={params['short']}, long={params['long']}\n")

    # Run benchmarks
    for n_ticks in tick_sizes:
        print(f"\n{'='*80}")
        print(f"Benchmarking with {n_ticks:,} ticks")
        print(f"{'='*80}")

        for name, strategy_class, description in strategies:
            print(f"\n  {name} ({description}):")

            try:
                result = benchmark_strategy(strategy_class, n_ticks, params)

                results['data'][name]['times'].append(result['time'])
                results['data'][name]['times_per_tick'].append(result['time_per_tick'])
                results['data'][name]['memory_current'].append(result['memory_current'])
                results['data'][name]['memory_peak'].append(result['memory_peak'])
                results['data'][name]['cache_info'].append(result['cache_info'])

                print(f"    ✓ Time: {result['time']:.4f}s ({result['time_per_tick']:.2f} µs/tick)")
                print(f"    ✓ Memory: {result['memory_peak']:.4f} MB peak")

                if result['cache_info']:
                    print(f"    ✓ Cache: {result['cache_info']}")

            except Exception as e:
                print(f"    ✗ Error: {e}")
                results['data'][name]['times'].append(None)
                results['data'][name]['times_per_tick'].append(None)
                results['data'][name]['memory_current'].append(None)
                results['data'][name]['memory_peak'].append(None)
                results['data'][name]['cache_info'].append(None)

    return results