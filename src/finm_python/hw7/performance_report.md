# Performance Analysis Report: Parallel Computing for Financial Data

**Author:** [Your Name]
**Date:** [Date]
**Assignment:** HW7 - Parallel Computing

---

## Executive Summary

<!-- TODO: Write a 2-3 sentence summary of your key findings -->
This report presents the results of benchmarking parallel computing approaches for financial data processing. Key findings include...

---

## 1. Data Ingestion: pandas vs polars

### Benchmark Results

<!-- TODO: Fill in with your actual benchmark results -->

| Metric | pandas | polars | Winner | Speedup |
|--------|--------|--------|--------|---------|
| Load Time (s) | | | | |
| Memory Usage (MB) | | | | |

### Analysis

<!-- TODO: Discuss the differences you observed -->

**Key observations:**
-
-
-

**Why does polars perform differently?**
<!-- Hint: Consider memory layout, lazy evaluation, and Rust vs Python -->

---

## 2. Rolling Metrics Computation

### Benchmark Results

| Operation | pandas Time (s) | polars Time (s) | Speedup |
|-----------|----------------|-----------------|---------|
| Moving Average | | | |
| Rolling Std | | | |
| Rolling Sharpe | | | |
| **Total** | | | |

### Visualization

<!-- TODO: Include your rolling metrics plot for AAPL -->
![Rolling Metrics for AAPL](output/plots/rolling_metrics_AAPL.png)

### Syntax Comparison

**pandas approach:**
```python
# TODO: Show your pandas implementation
df['rolling_ma'] = df['price'].rolling(window=20).mean()
```

**polars approach:**
```python
# TODO: Show your polars implementation
df.with_columns(
    pl.col('price').rolling_mean(20).alias('rolling_ma')
)
```

**Discussion:**
<!-- Compare the syntax, readability, and performance -->

---

## 3. Threading vs Multiprocessing

### Performance Comparison

| Approach | Time (s) | Speedup vs Sequential | CPU Usage (%) | Memory (MB) |
|----------|----------|----------------------|---------------|-------------|
| Sequential | | 1.00x | | |
| Threading | | | | |
| Multiprocessing | | | | |

### Visualization

<!-- TODO: Include your parallel processing comparison plot -->
![Parallel Processing Comparison](output/plots/parallel_comparison.png)

### Analysis

#### GIL Limitations

<!-- TODO: Explain what you observed regarding the Global Interpreter Lock -->

The Global Interpreter Lock (GIL) is...

In my experiments, I observed that threading...

Multiprocessing showed... because...

#### When to Use Each Approach

**Threading is preferred when:**
-
-
-

**Multiprocessing is preferred when:**
-
-
-

**Key insight:** <!-- Your main takeaway about parallel processing in Python -->

---

## 4. Portfolio Aggregation

### Results

<!-- TODO: Show your aggregated portfolio output -->

```json
{
  "name": "Main Portfolio",
  "total_value": ,
  "aggregate_volatility": ,
  "max_drawdown": ,
  "positions": [
    // ...
  ],
  "sub_portfolios": [
    // ...
  ]
}
```

### Performance

| Approach | Time (s) | Speedup |
|----------|----------|---------|
| Sequential | | 1.00x |
| Parallel | | |

### Recursive Aggregation Logic

<!-- TODO: Explain your approach to recursive aggregation -->

The recursive aggregation works by:
1.
2.
3.

---

## 5. Overall Performance Summary

### Comprehensive Comparison Table

| Task | pandas/Sequential | polars/Parallel | Best Performer | Improvement |
|------|------------------|-----------------|----------------|-------------|
| Data Ingestion | | | | |
| Rolling Metrics | | | | |
| Symbol Processing | | | | |
| Portfolio Aggregation | | | | |

### Visualizations

<!-- TODO: Include your overall performance comparison chart -->
![Performance Comparison](output/plots/performance_comparison.png)

---

## 6. Recommendations

Based on my analysis, I recommend:

### For Data Ingestion
<!-- When to use pandas vs polars -->

### For Rolling Calculations
<!-- Which library provides better performance -->

### For Parallel Processing
<!-- When to use threading vs multiprocessing -->

### For Production Systems
<!-- Overall architectural recommendations -->

---

## 7. Lessons Learned

<!-- TODO: Reflect on what you learned from this assignment -->

1. **About Python's GIL:**

2. **About DataFrame libraries:**

3. **About parallel computing:**

4. **About performance profiling:**

---

## 8. Future Improvements

If I had more time, I would:

1. <!-- e.g., Test with larger datasets -->
2. <!-- e.g., Implement async/await for I/O operations -->
3. <!-- e.g., Add distributed computing with Dask -->
4. <!-- e.g., Profile memory usage more deeply -->

---

## Appendix

### A. System Specifications

- **OS:**
- **CPU:**
- **RAM:**
- **Python Version:**
- **Key Libraries:** pandas, polars, psutil

### B. Code Repository

All source code is available in:
- `src/finm_python/hw7/`

### C. Raw Benchmark Data

<!-- TODO: Include any additional raw data or logs -->

---

*Report generated on [Date]*
