# Assignment 7: Parallel Computing for Financial Data Processing

**Due:** Sun Nov 2, 2025 11:59pm

**100 Points Possible**

## Overview

Design and implement a Python module that processes large-scale financial time-series data using parallel computing techniques. You will explore the tradeoffs between threading and multiprocessing, benchmark pandas vs polars for performance, and apply concurrency to accelerate analytics such as rolling metrics, signal generation, and portfolio aggregation.

This assignment emphasizes computational efficiency, parallel architecture, and performance profiling in the context of finance.

## Learning Objectives

- Understand the difference between threading and multiprocessing in Python
- Apply parallelism to accelerate financial computations
- Benchmark pandas vs polars for time-series analytics
- Use profiling tools to measure CPU usage, memory consumption, and execution time
- Identify bottlenecks and optimize data pipelines for concurrency
- Aggregate portfolio metrics using parallel processing and recursive logic



## Task Specifications

### 1. Data Ingestion

**Input:** [`market_data-1.csv`](../src/trading_system/hw3/data/raw/market_data.csv)

**Expectations:**

- Load the data using both **pandas** and **polars**
- Parse into a time-indexed DataFrame with columns: `timestamp`, `symbol`, `price`
- Demonstrate equivalent parsing logic in both libraries
- Compare ingestion time and memory usage using profiling tools



### 2. Rolling Analytics

**Task:** Compute rolling metrics per symbol:

- 20-period moving average
- 20-period rolling standard deviation
- Rolling Sharpe ratio (assume risk-free rate = 0)

**Expectations:**

- Implement using both pandas and polars
- Time each computation and compare performance
- Visualize results for one symbol (e.g., AAPL) using matplotlib or plotly
- Discuss syntax differences and performance tradeoffs



### 3. Threading vs Multiprocessing

**Task:** Implement two parallel approaches to compute rolling metrics across symbols:

- **Threading** using `concurrent.futures.ThreadPoolExecutor`
- **Multiprocessing** using `concurrent.futures.ProcessPoolExecutor`

**Expectations:**

- Create a function that computes metrics for a single symbol
- Use threading and multiprocessing to run this function across all symbols
- Compare:
  - Total execution time
  - CPU utilization
  - Memory usage
- Discuss GIL limitations and when multiprocessing is preferred



### 4. Portfolio Aggregation

**Input:** [`portfolio_structure-1.json`](../src/finm_python/scripts/hw7/portfolio_structure-1.json)

**Task:** For each position, compute:

- `value = quantity × latest price`
- `volatility = rolling standard deviation of returns`
- `drawdown = maximum peak-to-trough loss`

**Expectations:**

- Implement a function that computes metrics for a single position
- Use multiprocessing to compute metrics for all positions in parallel
- Recursively aggregate metrics for sub-portfolios:
  - `total_value = sum of all position values`
  - `aggregate_volatility = weighted average volatility`
  - `max_drawdown = worst drawdown across all positions and sub-portfolios`
- Implement a sequential version for comparison
- Output a structured JSON-like object representing the full portfolio hierarchy with computed metrics

**Example output:**

```json
{
  "name": "Main Portfolio",
  "total_value": 32000.00,
  "aggregate_volatility": 0.015,
  "max_drawdown": -0.12,
  "positions": [
    {
      "symbol": "AAPL",
      "value": 17235.00,
      "volatility": 0.012,
      "drawdown": -0.10
    },
    {
      "symbol": "MSFT",
      "value": 16405.00,
      "volatility": 0.018,
      "drawdown": -0.14
    }
  ],
  "sub_portfolios": [
    {
      "name": "Index Holdings",
      "total_value": 8610.00,
      "aggregate_volatility": 0.010,
      "max_drawdown": -0.08,
      "positions": [
        {
          "symbol": "SPY",
          "value": 8610.00,
          "volatility": 0.010,
          "drawdown": -0.08
        }
      ]
    }
  ]
}
```



### 5. Performance Comparison: pandas vs polars

**Task:** Create a summary table comparing:

- Ingestion time
- Rolling metric computation time
- Memory usage
- Parallel execution speed

**Expectations:**

- Use profiling tools like `timeit`, `memory_profiler`, and `psutil`
- Discuss tradeoffs in syntax, ecosystem, and scalability
- Include visualizations (e.g., bar charts) comparing performance
- Narrative explaining when each library is preferable



## 🧪 Unit Tests

- Validate correctness of rolling metrics
- Confirm threading and multiprocessing produce consistent results
- Test pandas vs polars outputs for equivalence
- Ensure portfolio aggregation matches expected totals



## 📦 Deliverables

👉 **Please share your GitHub with your TAs:**

- Jenn: jcolli5158
- Hunter: hyoung3

| File | Description |
|------|-------------|
| `data_loader.py` | Loads market data using pandas and polars |
| `metrics.py` | Rolling analytics functions |
| `parallel.py` | Threading and multiprocessing implementations |
| `portfolio.py` | Aggregates portfolio metrics |
| `reporting.py` | Performance summary and visualizations |
| `main.py` | Orchestrates ingestion, computation, and reporting |
| `tests/` | Unit tests or notebook-based validation |
| `performance_report.md` | Summary of benchmarks and tradeoffs |
| `README.md` | Setup instructions and module descriptions |