# Runtime & Space Complexity in Financial Signal Processing

Due: Sun Oct 12, 2025

## Overview

Design and implement a Python module that ingests market data from a CSV file and applies multiple trading strategies with varying runtime and space complexities. You will analyze, compare, and optimize the performance of these strategies using profiling tools and theoretical Big-O analysis. The goal is to understand how algorithmic design choices affect both execution time and memory usage in financial systems.

This assignment emphasizes computational efficiency, profiling, and performance visualization—critical skills for building scalable trading infrastructure.

## Learning Objectives

- Implement trading strategies with different time and space complexities
- Analyze and annotate Python code using Big-O notation
- Use profiling tools (timeit, cProfile, line_profiler, memory_profiler) to measure runtime and memory usage
- Visualize performance scaling across input sizes
- Apply optimization techniques to reduce runtime and memory bottlenecks

## Task Specifications

### 1. Data Ingestion & Immutable Types

- Read `market_data.csv` (columns: `timestamp`, `symbol`, `price`) using the built-in `csv` module
- Define a frozen dataclass `MarketDataPoint` with attributes:
  - `@dataclass(frozen=True)`

```python
class MarketDataPoint:
    timestamp: datetime
    symbol: str
    price: float
```

- Parse each row into a `MarketDataPoint` and collect them in a list
- Analyze space complexity of storing the full dataset in memory

### 2. Strategy Interface & Implementations

Create an abstract base class:

```python
class Strategy(ABC):
    @abstractmethod
    def generate_signals(self, tick: MarketDataPoint) -> list:
        pass
```

Implement two strategies:

- **NaiveMovingAverageStrategy:** For each tick, recompute the average price from scratch (Time: O(n), Space: O(n))
- **WindowedMovingAverageStrategy:** Maintain a fixed-size buffer and update the average incrementally (Time: O(1), Space: O(k), where k is window size)

### 3. Complexity Annotation

- Annotate each strategy with theoretical time and space complexity
- Include comments in code explaining why each operation has its complexity
- Compare memory usage of full-history vs windowed approaches

### 4. Profiling & Benchmarking

Use timeit, cProfile, and memory_profiler to measure runtime and memory usage for each strategy on:

- 1,000 ticks
- 10,000 ticks
- 100,000 ticks

Record total execution time and peak memory usage.

Use matplotlib or seaborn to plot:

- Runtime vs input size
- Memory usage vs input size

### 5. Optimization Challenge

Refactor NaiveMovingAverageStrategy to reduce both time and space complexity.

Optionally explore:

- `collections.deque` for efficient sliding windows
- NumPy for vectorized operations
- `functools.lru_cache` for memoization
- Generator-based streaming to reduce memory footprint

### 6. Reporting

Generate `complexity_report.md` with:

- Tables of runtime and memory metrics
- Complexity annotations
- Plots of scaling behavior
- Narrative comparing strategies and optimization impact

## Unit Tests

- Validate correctness of both strategies
- Confirm that optimized strategy runs under 1 second and uses <100MB memory for 100k ticks
- Test that profiling output includes expected hotspots and memory peaks

## Deliverables

Upload to GitHub with the following structure:

👉 **Please share your GitHub with your TAs:**

- Jenn: jcolli5158
- Hunter: hyoung3

| File | Description |
|------|-------------|
| `data_loader.py` | CSV parsing and dataclass creation |
| `models.py` | MarketDataPoint, Strategy base class |
| `strategies.py` | Naive and optimized strategy implementations |
| `profiler.py` | Runtime and memory measurement |
| `reporting.py` | Markdown and plot generation |
| `main.py` | Orchestrates ingestion, strategy execution, profiling |
| `tests/` | Unit tests or notebook-based validation |
| `complexity_report.md` | Summary of findings |
| `README.md` | Setup instructions and module descriptions |

## Checklist

- [x] Data Ingestion & Immutable Types (0)
- [x] Strategy Interface & Implementations (1h)
- [x] Complexity Annotation (0)
- [x] Profiling & Benchmarking (1h)
- [x] Optimization Challenge
- [x] Reporting (0.5h)

## Things learned

- timeit
- cProfile, pstats, io.StringIO
- tracemalloc