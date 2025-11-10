# Optimization Challenge - Comprehensive Results

**Generated:** 2025-11-10 10:13:32
**Parameters:** Short=5, Long=20

---

## Strategy Overview

| Strategy | Description | Key Technique |
|----------|-------------|---------------|
| **Naive** | Baseline O(n) | List conversion + np.mean |
| **Windowed** | Deque + Running Sums | Deque + Running sums |
| **Vectorized** | NumPy Batch Processing | NumPy vectorization |
| **Cached** | LRU Memoization | LRU cache memoization |
| **Streaming** | Generator-based | Generator lazy evaluation |
| **Hybrid** | Combined Optimizations | Circular buffers + NumPy |

## Performance Comparison

![Optimization Comparison](plots/optimization_comparison.png)

## cProfile Results

### Naive Strategy

```
         259571 function calls in 0.170 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.004    0.004    0.170    0.170 /Users/zdf/Documents/GitHub/trading-system/src/trading_system/hw3/src/profiler.py:57(run_strategy)
    10000    0.024    0.000    0.166    0.000 /Users/zdf/Documents/GitHub/trading-system/src/trading_system/hw3/src/strategies.py:83(generate_signals)
    19962    0.024    0.000    0.135    0.000 /Users/zdf/Documents/GitHub/trading-system/.venv/lib/python3.13/site-packages/numpy/_core/fromnumeric.py:3735(mean)
    19962    0.036    0.000    0.111    0.000 /Users/zdf/Documents/GitHub/trading-system/.venv/lib/python3.13/site-packages/numpy/_core/_methods.py:117(_mean)
    19962    0.024    0.000    0.024    0.000 {method 'reduce' of 'numpy.ufunc' objects}
    19962    0.020    0.000    0.023    0.000 /Users/zdf/Documents/GitHub/trading-system/.venv/lib/python3.13/site-packages/numpy/_core/_methods.py:75(_count_reduce_items)
    19962    0.017    0.000    0.017    0.000 {built-in method numpy.asanyarray}
    39924    0.005    0.000    0.005    0.000 {built-in method builtins.issubclass}
    19962    0.003    0.000    0.003    0.000 {built-in method builtins.hasattr}
    19964    0.003    0.000    0.003    0.000 {built-in method builtins.isinstance}
    19962    0.002    0.000    0.002    0.000 {built-in method numpy.lib.array_utils.normalize_axis_index}
    19962    0.002    0.000    0.002    0.000 /Users/zdf/Documents/GitHub/trading-system/.venv/lib/python3.13/site-packages/numpy/_core/fromnumeric.py:3730(_mean_dispatcher)
     9981    0.002    0.000    0.002    0.000 /Users/zdf/Documents/GitHub/trading-system/src/trading_system/hw3/src/strategies.py:30(ma_logic)
    10000    0.001    0.000    0.001    0.000 {method 'append' of 'collections.deque' objects}
    10000    0.001    0.000    0.001    0.000 {built-in method builtins.len}
```

### Windowed Strategy

```
         89951 function calls in 0.026 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.002    0.002    0.026    0.026 /Users/zdf/Documents/GitHub/trading-system/src/trading_system/hw3/src/profiler.py:57(run_strategy)
    10000    0.016    0.000    0.024    0.000 /Users/zdf/Documents/GitHub/trading-system/src/trading_system/hw3/src/strategies.py:184(generate_signals)
    49962    0.004    0.000    0.004    0.000 {built-in method builtins.len}
    20000    0.002    0.000    0.002    0.000 {method 'append' of 'collections.deque' objects}
     9981    0.001    0.000    0.001    0.000 /Users/zdf/Documents/GitHub/trading-system/src/trading_system/hw3/src/strategies.py:30(ma_logic)
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
        2    0.000    0.000    0.000    0.000 {built-in method builtins.isinstance}
        2    0.000    0.000    0.000    0.000 <frozen abc>:117(__instancecheck__)
        2    0.000    0.000    0.000    0.000 {built-in method _abc._abc_instancecheck}



```

### Vectorized Strategy

```
         249550 function calls in 0.166 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000    0.166    0.166 /Users/zdf/Documents/GitHub/trading-system/src/trading_system/hw3/src/profiler.py:57(run_strategy)
        1    0.050    0.050    0.166    0.166 /Users/zdf/Documents/GitHub/trading-system/src/trading_system/hw3/src/strategies.py:311(process_batch)
    19962    0.013    0.000    0.109    0.000 /Users/zdf/Documents/GitHub/trading-system/.venv/lib/python3.13/site-packages/numpy/_core/fromnumeric.py:3735(mean)
    19962    0.036    0.000    0.096    0.000 /Users/zdf/Documents/GitHub/trading-system/.venv/lib/python3.13/site-packages/numpy/_core/_methods.py:117(_mean)
    19962    0.024    0.000    0.024    0.000 {method 'reduce' of 'numpy.ufunc' objects}
    19962    0.020    0.000    0.023    0.000 /Users/zdf/Documents/GitHub/trading-system/.venv/lib/python3.13/site-packages/numpy/_core/_methods.py:75(_count_reduce_items)
    39924    0.005    0.000    0.005    0.000 {built-in method builtins.issubclass}
    19962    0.003    0.000    0.003    0.000 {built-in method builtins.hasattr}
    19963    0.003    0.000    0.003    0.000 {built-in method builtins.isinstance}
    19962    0.003    0.000    0.003    0.000 {built-in method builtins.max}
    19962    0.002    0.000    0.002    0.000 {built-in method numpy.lib.array_utils.normalize_axis_index}
    10000    0.002    0.000    0.002    0.000 {method 'append' of 'list' objects}
    19962    0.002    0.000    0.002    0.000 {built-in method numpy.asanyarray}
    19962    0.002    0.000    0.002    0.000 /Users/zdf/Documents/GitHub/trading-system/.venv/lib/python3.13/site-packages/numpy/_core/fromnumeric.py:3730(_mean_dispatcher)
        1    0.000    0.000    0.000    0.000 {built-in method numpy.array}
```

### Cached Strategy

```
         299495 function calls in 0.147 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.003    0.003    0.147    0.147 /Users/zdf/Documents/GitHub/trading-system/src/trading_system/hw3/src/profiler.py:57(run_strategy)
    10000    0.051    0.000    0.144    0.000 /Users/zdf/Documents/GitHub/trading-system/src/trading_system/hw3/src/strategies.py:397(generate_signals)
   199620    0.077    0.000    0.077    0.000 {built-in method builtins.round}
    19962    0.007    0.000    0.013    0.000 /Users/zdf/Documents/GitHub/trading-system/src/trading_system/hw3/src/strategies.py:389(cached_mean)
    19962    0.004    0.000    0.004    0.000 {built-in method builtins.sum}
    29962    0.003    0.000    0.003    0.000 {built-in method builtins.len}
     9981    0.001    0.000    0.001    0.000 /Users/zdf/Documents/GitHub/trading-system/src/trading_system/hw3/src/strategies.py:30(ma_logic)
    10000    0.001    0.000    0.001    0.000 {method 'append' of 'collections.deque' objects}
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
        2    0.000    0.000    0.000    0.000 {built-in method builtins.isinstance}
        2    0.000    0.000    0.000    0.000 <frozen abc>:117(__instancecheck__)
        2    0.000    0.000    0.000    0.000 {built-in method _abc._abc_instancecheck}



```

### Streaming Strategy

```
         99951 function calls in 0.028 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.001    0.001    0.028    0.028 /Users/zdf/Documents/GitHub/trading-system/src/trading_system/hw3/src/profiler.py:57(run_strategy)
    10001    0.003    0.000    0.026    0.000 /Users/zdf/Documents/GitHub/trading-system/src/trading_system/hw3/src/strategies.py:493(stream_signals)
    10000    0.016    0.000    0.024    0.000 /Users/zdf/Documents/GitHub/trading-system/src/trading_system/hw3/src/strategies.py:467(_process_tick)
    49962    0.004    0.000    0.004    0.000 {built-in method builtins.len}
    20000    0.002    0.000    0.002    0.000 {method 'append' of 'collections.deque' objects}
     9981    0.001    0.000    0.001    0.000 /Users/zdf/Documents/GitHub/trading-system/src/trading_system/hw3/src/strategies.py:30(ma_logic)
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
        2    0.000    0.000    0.000    0.000 {built-in method builtins.isinstance}
        1    0.000    0.000    0.000    0.000 <frozen abc>:117(__instancecheck__)
        1    0.000    0.000    0.000    0.000 {built-in method _abc._abc_instancecheck}
        1    0.000    0.000    0.000    0.000 {built-in method builtins.iter}



```

### Hybrid Strategy

```
         19989 function calls in 0.013 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.002    0.002    0.013    0.013 /Users/zdf/Documents/GitHub/trading-system/src/trading_system/hw3/src/profiler.py:57(run_strategy)
    10000    0.010    0.000    0.011    0.000 /Users/zdf/Documents/GitHub/trading-system/src/trading_system/hw3/src/strategies.py:552(generate_signals)
     9981    0.001    0.000    0.001    0.000 /Users/zdf/Documents/GitHub/trading-system/src/trading_system/hw3/src/strategies.py:30(ma_logic)
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
        2    0.000    0.000    0.000    0.000 {built-in method builtins.isinstance}
        2    0.000    0.000    0.000    0.000 <frozen abc>:117(__instancecheck__)
        2    0.000    0.000    0.000    0.000 {built-in method _abc._abc_instancecheck}



```

## Detailed Performance Results

### Execution Time (seconds)

| Strategy | 1,000 ticks | 10,000 ticks | 100,000 ticks |
|----------|-------------|--------------|---------------|
| Naive | 0.0093 | 0.0953 | 0.9209 | 
| Windowed | 0.0006 | 0.0058 | 0.0580 | 
| Vectorized | 0.0067 | 0.0665 | 0.6927 | 
| Cached | 0.0080 | 0.0813 | 0.8801 | 
| Streaming | 0.0006 | 0.0059 | 0.0584 | 
| Hybrid | 0.0009 | 0.0091 | 0.0905 | 

### Time per Tick (microseconds)

| Strategy | 1,000 ticks | 10,000 ticks | 100,000 ticks |
|----------|-------------|--------------|---------------|
| Naive | 9.33 | 9.53 | 9.21 | 
| Windowed | 0.59 | 0.58 | 0.58 | 
| Vectorized | 6.66 | 6.65 | 6.93 | 
| Cached | 8.05 | 8.13 | 8.80 | 
| Streaming | 0.59 | 0.59 | 0.58 | 
| Hybrid | 0.92 | 0.91 | 0.90 | 

### Peak Memory Usage (MB)

| Strategy | 1,000 ticks | 10,000 ticks | 100,000 ticks |
|----------|-------------|--------------|---------------|
| Naive | 0.0023 | 0.0023 | 0.0023 | 
| Windowed | 0.0012 | 0.0012 | 0.0012 | 
| Vectorized | 0.0969 | 0.9936 | 9.9163 | 
| Cached | 0.0556 | 0.0556 | 0.0556 | 
| Streaming | 0.0014 | 0.0014 | 0.0014 | 
| Hybrid | 0.0002 | 0.0002 | 0.0002 | 

## Speedup Analysis (vs Naive)

| Strategy | 1,000 ticks | 10,000 ticks | 100,000 ticks |
|----------|-------------|--------------|---------------|
| Naive | 1.00x | 1.00x | 1.00x |
| Windowed | **15.78x** | **16.47x** | **15.87x** | 
| Vectorized | **1.40x** | **1.43x** | **1.33x** | 
| Cached | **1.16x** | **1.17x** | **1.05x** | 
| Streaming | **15.86x** | **16.16x** | **15.78x** | 
| Hybrid | **10.10x** | **10.43x** | **10.18x** | 

## Performance Rankings (100,000 ticks)

### Fastest Execution
1. **Windowed**: 0.0580s
2. **Streaming**: 0.0584s
3. **Hybrid**: 0.0905s
4. **Vectorized**: 0.6927s
5. **Cached**: 0.8801s
6. **Naive**: 0.9209s

### Most Memory Efficient
1. **Hybrid**: 0.0002 MB
2. **Windowed**: 0.0012 MB
3. **Streaming**: 0.0014 MB
4. **Naive**: 0.0023 MB
5. **Cached**: 0.0556 MB
6. **Vectorized**: 9.9163 MB

## Key Findings

1. **Fastest Strategy**: Windowed achieves 15.9x speedup
2. **Most Memory Efficient**: Hybrid uses only 0.0002 MB
3. **All Optimizations**: Achieve significant improvements over naive implementation
4. **Complexity Verified**: O(1) strategies scale better than O(n) baseline

## Recommendations

### Use Case Guide

- **Real-time Trading (HFT)**: Use **Windowed** or **Hybrid** for O(1) performance
- **Backtesting Large Datasets**: Use **Vectorized** for NumPy acceleration
- **Low-Memory Environments**: Use **Streaming** for minimal footprint
- **Synthetic Data/Testing**: Consider **Cached** for repeated patterns
- **Production Systems**: Use **Hybrid** for best overall performance

## Complexity Summary

| Strategy | Time Complexity | Space Complexity | Notes |
|----------|-----------------|------------------|-------|
| Naive | O(n) | O(n) | Baseline, recalculates everything |
| Windowed | O(1) | O(k) | Optimal for streaming |
| Vectorized | O(n)* | O(n) | NumPy acceleration |
| Cached | O(1)** | O(k+c) | Depends on cache hits |
| Streaming | O(1) | O(k) | Generator-based |
| Hybrid | O(1) | O(k) | Best overall |

*With NumPy C-level optimization  
**O(n) on cache misses

