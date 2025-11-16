# HW7: Parallel Computing for Financial Data Processing

## Overview

This module implements parallel computing techniques for processing large-scale financial time-series data. It compares different approaches including:
- **Data Libraries**: pandas vs polars
- **Parallel Execution**: Threading vs Multiprocessing
- **Portfolio Analysis**: Sequential vs Parallel aggregation

## Learning Objectives

By completing this assignment, you will:
- Understand the difference between threading and multiprocessing in Python
- Apply parallelism to accelerate financial computations
- Benchmark pandas vs polars for time-series analytics
- Use profiling tools to measure CPU usage, memory consumption, and execution time
- Identify bottlenecks and optimize data pipelines for concurrency
- Aggregate portfolio metrics using parallel processing and recursive logic

## Module Structure

```
hw7/
├── __init__.py              # Package initialization
├── data_loader.py           # Data ingestion (pandas & polars)
├── metrics.py               # Rolling analytics computation
├── parallel.py              # Threading & multiprocessing implementations
├── portfolio.py             # Portfolio aggregation with recursion
├── reporting.py             # Performance reporting & visualization
├── main.py                  # Main orchestration script
├── README.md                # This file
├── performance_report.md    # Your performance analysis report (generated)
├── output/                  # Generated outputs
│   ├── plots/              # Visualization images
│   └── reports/            # JSON and markdown reports
└── tests/                   # Unit tests
    ├── __init__.py
    ├── test_data_loader.py
    ├── test_metrics.py
    ├── test_parallel.py
    └── test_portfolio.py
```

## Installation

### Prerequisites

Add the following dependencies to your `pyproject.toml`:

```toml
[project.dependencies]
# Existing dependencies...
polars = ">=0.20.0"
psutil = ">=5.9.0"
matplotlib = ">=3.7.0"
```

Install with:
```bash
uv sync
```

Or using pip:
```bash
pip install polars psutil matplotlib
```

## Usage

### Running the Complete Pipeline

```bash
python -m finm_python.hw7.main
```

This will:
1. Load market data using pandas and polars
2. Compute rolling metrics for each symbol
3. Compare threading vs multiprocessing performance
4. Aggregate portfolio metrics recursively
5. Generate performance reports and visualizations

### Running Individual Modules

```python
# Data Loading
from finm_python.hw7 import data_loader

pandas_df = data_loader.load_with_pandas("path/to/market_data.csv")
polars_df = data_loader.load_with_polars("path/to/market_data.csv")
benchmarks = data_loader.benchmark_ingestion("path/to/market_data.csv")

# Rolling Metrics
from finm_python.hw7 import metrics

df_with_metrics = metrics.compute_rolling_metrics_pandas(symbol_df)

# Parallel Processing
from finm_python.hw7 import parallel

results, time = parallel.process_symbols_threading(symbol_data_list, compute_func)

# Portfolio Aggregation
from finm_python.hw7 import portfolio

portfolio_struct = portfolio.load_portfolio_structure("path/to/portfolio.json")
aggregated = portfolio.aggregate_portfolio_metrics(portfolio_struct, market_df)
```

### Running Tests

```bash
# Run all HW7 tests
pytest src/finm_python/hw7/tests/ -v

# Run specific test file
pytest src/finm_python/hw7/tests/test_data_loader.py -v

# Run with coverage
pytest src/finm_python/hw7/tests/ --cov=finm_python.hw7
```

## Data Files

### Input Data

1. **Market Data**: `src/finm_python/hw3/data/raw/market_data.csv`
   - Columns: `timestamp`, `symbol`, `price`
   - Contains tick data for AAPL, MSFT, SPY

2. **Portfolio Structure**: `src/finm_python/scripts/hw7/portfolio_structure.json`
   - Hierarchical portfolio with positions and sub-portfolios
   - Each position has `symbol` and `quantity`

### Output Files

After running the pipeline:
- `output/performance_comparison.png` - Bar charts comparing approaches
- `output/rolling_metrics_AAPL.png` - Visualization of rolling metrics
- `output/aggregated_portfolio.json` - Portfolio with computed metrics
- `performance_report.md` - Comprehensive analysis report

## Key Concepts

### Python GIL (Global Interpreter Lock)

The GIL prevents multiple threads from executing Python bytecode simultaneously. This means:
- **Threading** is good for I/O-bound tasks but limited for CPU-bound work
- **Multiprocessing** bypasses the GIL for true parallelism but has higher overhead

### When to Use Each Approach

| Scenario | Recommended Approach |
|----------|---------------------|
| File I/O operations | Threading |
| Network requests | Threading |
| CPU-intensive calculations | Multiprocessing |
| Small datasets | Sequential |
| Large datasets | Multiprocessing |

### pandas vs polars

| Feature | pandas | polars |
|---------|--------|--------|
| Memory usage | Higher | Lower |
| Performance | Slower | Faster |
| Syntax | More verbose | Expressive |
| Ecosystem | Mature | Growing |
| Learning curve | Familiar | New syntax |

## Implementation Guide

### Step 1: Data Ingestion
Start with `data_loader.py`. Implement the functions to:
- Load CSV files with both pandas and polars
- Parse timestamps correctly
- Benchmark loading performance

### Step 2: Rolling Metrics
In `metrics.py`, implement:
- 20-period moving average
- Rolling standard deviation
- Rolling Sharpe ratio (rf=0)

### Step 3: Parallel Processing
In `parallel.py`, implement:
- Sequential baseline
- ThreadPoolExecutor approach
- ProcessPoolExecutor approach
- Performance comparison

### Step 4: Portfolio Aggregation
In `portfolio.py`, implement:
- Position metrics (value, volatility, drawdown)
- Recursive aggregation for sub-portfolios
- JSON serialization

### Step 5: Reporting
In `reporting.py`, implement:
- Performance summary generation
- Comparison table creation
- Visualizations
- Analysis narrative

## Expected Output

Your `performance_report.md` should include:
- Executive summary of findings
- Detailed comparison tables
- Visualizations (embedded images)
- Analysis of when to use each approach
- Recommendations based on your benchmarks

## Grading Criteria

- **Data Ingestion (15%)**: Correct loading with both libraries
- **Rolling Metrics (20%)**: Accurate calculations and benchmarking
- **Parallel Processing (25%)**: Working threading and multiprocessing
- **Portfolio Aggregation (20%)**: Correct recursive aggregation
- **Performance Reporting (10%)**: Clear analysis and visualizations
- **Code Quality (10%)**: Clean, documented, tested code

## Troubleshooting

### Multiprocessing Issues
- Ensure functions are defined at module level (not nested)
- Use `if __name__ == "__main__":` guard in main scripts
- Check that data is serializable (picklable)

### Memory Issues
- Use polars for large datasets
- Process data in chunks
- Monitor with `psutil`

### Import Errors
```bash
# Ensure all dependencies are installed
uv sync
# or
pip install -r requirements.txt
```

## Resources

- [Python concurrent.futures documentation](https://docs.python.org/3/library/concurrent.futures.html)
- [polars User Guide](https://pola-rs.github.io/polars/py-polars/html/index.html)
- [Understanding the GIL](https://realpython.com/python-gil/)
- [psutil documentation](https://psutil.readthedocs.io/)

## Questions?

If you have questions:
1. Review the docstrings in each module
2. Check the test files for expected behavior
3. Consult the resources above
4. Reach out to your TAs (Jenn: jcolli5158, Hunter: hyoung3)
