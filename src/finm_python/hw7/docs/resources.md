# HW7 Learning Resources: Parallel Computing for Financial Data

## Overview

This document provides curated learning resources to help you understand the key concepts needed for HW7. The assignment focuses on parallel computing, data processing optimization, and portfolio analytics.

---

## Key Topics & Minimal Essentials

### 1. **Python GIL (Global Interpreter Lock)**
**What you need to know:**
- The GIL is a mutex that allows only one thread to execute Python bytecode at a time
- Threading is limited for CPU-bound tasks due to GIL
- Multiprocessing bypasses the GIL by using separate processes
- Python 3.13+ introduces experimental "free-threaded" mode (PEP 703)

**Best Resources:**

📺 **YouTube Videos:**
- Search "Corey Schafer Python Threading" for threading tutorial
- Search "Corey Schafer Python Multiprocessing" for multiprocessing tutorial
- Real Python video courses on GIL (Python 3.12+)

📖 **Articles & Documentation:**
- [Real Python - Understanding the GIL](https://realpython.com/python-gil/) - Comprehensive guide updated Oct 2024
- [Real Python - GIL Video Course](https://realpython.com/courses/understanding-global-interpreter-lock-gil/)
- [Python Land - The Python GIL](https://python.land/python-concurrency/the-python-gil)
- [Analytics Vidhya - Python GIL](https://www.analyticsvidhya.com/blog/2024/02/python-global-interpreter-lock/) - Updated May 2025

---

### 2. **Threading vs Multiprocessing**

**What you need to know:**
- **Threading**: Good for I/O-bound tasks (file reading, network), shared memory, lower overhead
- **Multiprocessing**: True parallelism for CPU-bound tasks, separate memory spaces, higher overhead
- **When to use each:**
  - Threading → I/O operations, network requests
  - Multiprocessing → CPU-intensive calculations, large datasets

**Best Resources:**

📺 **YouTube Videos:**
- **Corey Schafer** - "Python Multiprocessing Tutorial: Run Code in Parallel Using the Multiprocessing Module"
- Search "Corey Schafer Threading" for his threading tutorial

📖 **Articles & Documentation:**
- [Python Official Docs - concurrent.futures](https://docs.python.org/3/library/concurrent.futures.html)
- [Real Python - Python Concurrency](https://realpython.com/python-concurrency/) - Speed up programs with threading/multiprocessing
- [Real Python Video - concurrent.futures vs multiprocessing](https://realpython.com/lessons/concurrentfutures-vs-multiprocessing/)
- [Real Python Video - When to Use Each](https://realpython.com/lessons/when-use-concurrent-futures-or-multiprocessing/)
- [TestDriven.io - Concurrency, Parallelism, and asyncio](https://testdriven.io/blog/concurrency-parallelism-asyncio/)
- [Super Fast Python - ThreadPoolExecutor in Python](https://superfastpython.com/threadpoolexecutor-in-python/)
- [Super Fast Python - ThreadPoolExecutor vs ProcessPoolExecutor](https://superfastpython.com/threadpoolexecutor-vs-processpoolexecutor/)

📝 **Quick Tutorials:**
- [DigitalOcean - ThreadPoolExecutor Tutorial](https://www.digitalocean.com/community/tutorials/how-to-use-threadpoolexecutor-in-python-3)
- [Python Engineer - ThreadPoolExecutor](https://www.python-engineer.com/posts/threadpoolexecutor/)
- [Python Tutorial - ThreadPoolExecutor Examples](https://www.pythontutorial.net/python-concurrency/python-threadpoolexecutor/)

---

### 3. **pandas vs polars**

**What you need to know:**
- **pandas**: Traditional, mature ecosystem, higher memory usage, slower
- **polars**: Modern (written in Rust), 10x+ faster, lower memory, parallel by default, lazy evaluation
- Polars uses expressive syntax: `.with_columns()`, `.rolling_mean()`
- Both support rolling window calculations

**Best Resources:**

📺 **YouTube Videos:**
- [Real Python - Starting With Polars DataFrames (Video)](https://realpython.com/videos/starting-polars-dataframes/)
- Search YouTube for "Polars vs Pandas 2024" for recent comparisons
- Look for videos by Keith Galli or Joram Mutenge on Polars

📖 **Articles & Documentation:**
- [Official Polars Documentation](https://docs.pola.rs/) - Start here!
- [Polars Getting Started Guide](https://docs.pola.rs/user-guide/getting-started/)
- [Real Python - Polars vs Pandas](https://realpython.com/polars-vs-pandas/) - Complete comparison
- [Real Python - Python Polars Tutorial](https://realpython.com/polars-python/)
- [DataCamp - pandas 2.0 vs polars](https://www.datacamp.com/tutorial/high-performance-data-manipulation-in-python-pandas2-vs-polars)
- [Towards Data Science - Polars vs Pandas Speed Comparison](https://towardsdatascience.com/polars-vs-pandas-an-independent-speed-comparison/)
- [Analytics Vidhya - Pandas vs Polars (Aug 2024)](https://www.analyticsvidhya.com/blog/2024/08/pandas-vs-polars/)

**Performance Benchmarks:**
- Polars: 7.79s ± 1.11s to read full file
- Pandas: 1min 27s ± 2.43s (10x slower)

---

### 4. **Rolling Window Calculations & Financial Metrics**

**What you need to know:**
- Rolling window = moving calculations over a fixed period (e.g., 20 days)
- Key metrics:
  - **Moving Average**: `df['price'].rolling(window).mean()`
  - **Rolling Std**: `df['price'].rolling(window).std()`
  - **Sharpe Ratio**: `rolling_mean(returns) / rolling_std(returns)` (assuming rf=0)
- Annualization factor: √252 for daily financial data

**Best Resources:**

📖 **Articles & Tutorials:**
- [Stack Overflow - Rolling Sharpe Ratio](https://stackoverflow.com/questions/49091044/python-rolling-sharpe-ratio-with-pandas-or-numpy)
- [Saturn Cloud - Rolling Sharpe Ratio Guide](https://saturncloud.io/blog/calculating-rolling-sharpe-ratio-with-python-a-guide-using-pandas-and-numpy/)
- [Codearmo - Sharpe, Sortino, Calmar Ratios](https://www.codearmo.com/blog/sharpe-sortino-and-calmar-ratios-python)
- [Towards Data Science - Calculating Sharpe Ratio](https://towardsdatascience.com/calculating-sharpe-ratio-with-python-755dcb346805/)
- [QuantInsti - Volatility & Risk-Adjusted Returns](https://blog.quantinsti.com/volatility-and-measures-of-risk-adjusted-return-based-on-volatility/)
- [Kaggle - Pandas Finance Tutorial: Sharpe Ratios](https://www.kaggle.com/code/jaakkokivisto/pandas-tutorial-for-finance-bigtech-sharpe-ratios)

**Formula Reference:**
```python
# Rolling Sharpe Ratio
returns = df['price'].pct_change()
rolling_sharpe = returns.rolling(window).mean() / returns.rolling(window).std()
# Annualized: rolling_sharpe * sqrt(252)
```

---

### 5. **Recursion & Hierarchical Data Structures**

**What you need to know:**
- Recursion is ideal for tree-like/nested structures (like portfolios with sub-portfolios)
- Key components: base case + recursive case
- Useful for aggregating metrics up the portfolio hierarchy

**Best Resources:**

📖 **Articles & Documentation:**
- [Real Python - Thinking Recursively in Python](https://realpython.com/python-thinking-recursively/)
- [Real Python - Recursion in Python Introduction](https://realpython.com/python-recursion/)
- [DataCamp - Recursion in Python](https://www.datacamp.com/tutorial/recursion-in-python)
- [Composing Programs - Recursive Data Structures](http://www.composingprograms.com/versions/v1/pages/27-recursive-data-structures.html)
- [SICP in Python - Recursive Data Structures](https://wizardforcel.gitbooks.io/sicp-in-python/content/18.html)
- [Codecademy - Recursion Cheatsheet](https://www.codecademy.com/learn/learn-data-structures-and-algorithms-with-python/modules/recursion/cheatsheet)
- [GeeksforGeeks - Recursion in Python](https://www.geeksforgeeks.org/python/recursion-in-python/)

**Key Concept:**
```python
def aggregate_portfolio(portfolio):
    # Base case: direct positions
    if not portfolio.get('sub_portfolios'):
        return sum_position_values(portfolio['positions'])

    # Recursive case: aggregate sub-portfolios
    total = sum_position_values(portfolio['positions'])
    for sub in portfolio['sub_portfolios']:
        total += aggregate_portfolio(sub)  # Recursion!
    return total
```

---

### 6. **Performance Monitoring with psutil**

**What you need to know:**
- psutil monitors CPU usage, memory consumption, process info
- Use for benchmarking parallel vs sequential performance
- Key functions: `psutil.cpu_percent()`, `process.memory_info().rss`

**Best Resources:**

📖 **Documentation & Tutorials:**
- [Official psutil Documentation](https://psutil.readthedocs.io/)
- [GitHub - psutil Repository](https://github.com/giampaolo/psutil)
- [PyPI - psutil Package](https://pypi.org/project/psutil/)
- [AskPython - psutil Module Tutorial](https://www.askpython.com/python-modules/psutil-module)
- [GeeksforGeeks - psutil Module](https://www.geeksforgeeks.org/python/psutil-module-in-python/)
- [CodeRivers - Mastering psutil](https://coderivers.org/blog/psutil-python/)
- [Medium - System Monitoring with psutil](https://umeey.medium.com/system-monitoring-made-easy-with-pythons-psutil-library-4b9add95a443)

**Quick Example:**
```python
import psutil
import time

process = psutil.Process()
start_mem = process.memory_info().rss / (1024 * 1024)  # MB
start_time = time.time()

# ... your code ...

end_time = time.time()
end_mem = process.memory_info().rss / (1024 * 1024)
print(f"Time: {end_time - start_time:.2f}s, Memory: {end_mem - start_mem:.2f}MB")
```

---

## HW7 Assignment Breakdown

### Task 1: Data Ingestion (15%)
- Load CSV with pandas and polars
- Benchmark loading performance
- **Focus**: Understanding I/O operations

### Task 2: Rolling Metrics (20%)
- Compute moving averages, std, Sharpe ratio
- Compare pandas vs polars performance
- **Focus**: Financial calculations + library comparison

### Task 3: Parallel Processing (25%)
- Implement sequential, threading, multiprocessing
- Measure CPU usage and execution time
- **Focus**: Understanding GIL, choosing right approach

### Task 4: Portfolio Aggregation (20%)
- Recursive aggregation of hierarchical portfolios
- Compute value, volatility, drawdown
- Parallel vs sequential comparison
- **Focus**: Recursion + parallel processing

### Task 5: Performance Reporting (10%)
- Generate visualizations and analysis
- Create comprehensive markdown report
- **Focus**: Communication of results

---

## Quick Reference: When to Use What

| Scenario | Best Approach | Why |
|----------|--------------|-----|
| Reading multiple CSV files | Threading | I/O-bound, shared memory |
| Computing rolling metrics | Multiprocessing | CPU-intensive calculations |
| Small datasets (<1000 rows) | Sequential | Overhead not worth it |
| Large datasets (>100k rows) | Multiprocessing + Polars | Speed + memory efficiency |
| Tree traversal | Recursion | Natural fit for hierarchical data |

---

## Recommended Learning Path

### Day 1: Foundations
1. Watch Corey Schafer's threading video (20 min)
2. Read Real Python's GIL article (20 min)
3. Skim polars documentation (15 min)

### Day 2: Parallel Computing
1. Watch Corey Schafer's multiprocessing video (20 min)
2. Read ThreadPoolExecutor tutorial (15 min)
3. Practice: Create simple threading example (30 min)

### Day 3: Data Libraries
1. Read polars vs pandas comparison (20 min)
2. Try polars rolling calculations (30 min)
3. Review pandas `.rolling()` method (15 min)

### Day 4: Advanced Topics
1. Read recursion tutorial (20 min)
2. Review psutil documentation (15 min)
3. Practice: Recursive sum on nested dict (30 min)

### Day 5: Start HW7
- Apply concepts with starter code
- Reference resources as needed

---

## Additional Resources

### Official Documentation
- [Python concurrent.futures](https://docs.python.org/3/library/concurrent.futures.html)
- [Polars User Guide](https://docs.pola.rs/)
- [psutil Documentation](https://psutil.readthedocs.io/)

### Community Resources
- Stack Overflow tags: `python-multiprocessing`, `python-polars`, `concurrent.futures`
- r/Python subreddit for discussions
- Real Python tutorials (consistently high quality)

### Tools & Libraries
- **pandas**: Traditional data analysis (`pip install pandas`)
- **polars**: High-performance data frames (`pip install polars`)
- **psutil**: System monitoring (`pip install psutil`)
- **matplotlib**: Visualization (`pip install matplotlib`)

---

## Tips for Success

1. **Start with the GIL** - Understanding it is crucial for knowing when threading won't help
2. **Benchmark everything** - Don't assume; measure with `time.time()` and `psutil`
3. **Use polars for speed** - It's significantly faster for large datasets
4. **Test recursion on paper first** - Draw the tree structure before coding
5. **Read docstrings** - Each HW7 module has detailed TODO comments
6. **Run tests frequently** - Use `pytest` to verify correctness
7. **Profile before optimizing** - Find bottlenecks with actual data

---

## Questions?

If you have questions:
1. Review the docstrings in each HW7 module
2. Check the test files for expected behavior (`src/finm_python/hw7/tests/`)
3. Consult the resources above
4. Reach out to TAs: Jenn (jcolli5158) or Hunter (hyoung3)

---

**Last Updated**: November 2025
**Assignment**: HW7 - Parallel Computing for Financial Data Processing
