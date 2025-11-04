# System Architecture

## Overview

The Trading Backtesting System follows a modular architecture with clear separation of concerns. The system is designed around five core components that work together to simulate realistic trading scenarios.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Main Entry Point                        │
│                          (main.py)                              │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ├─── Load Configuration
                            ├─── Load Market Data
                            └─── Initialize Components
                                        │
        ┌───────────────────────────────┼───────────────────────────┐
        │                               │                           │
┌───────▼────────┐           ┌──────────▼──────────┐     ┌─────────▼────────┐
│  Data Loader   │           │  Strategy Factory   │     │ Execution Engine │
│                │           │                     │     │                  │
│ - CSV Parsing  │           │ - MACD Strategy     │     │ - Order Creation │
│ - Data Points  │           │ - Momentum Strategy │     │ - Validation     │
│                │           │ - Strategy State    │     │ - Execution      │
└───────┬────────┘           └──────────┬──────────┘     │ - Portfolio Mgmt │
        │                               │                └─────────┬────────┘
        │                               │                          │
        │                    ┌──────────▼──────────┐               │
        └───────────────────►│   Models Layer      │◄──────────────┘
                             │                     │
                             │ - Order             │
                             │ - Position          │
                             │ - Portfolio         │
                             │ - Exceptions        │
                             └──────────┬──────────┘
                                        │
                             ┌──────────▼──────────┐
                             │  Reporting Module   │
                             │                     │
                             │ - Metrics Calc      │
                             │ - Visualization     │
                             │ - Report Generation │
                             └─────────────────────┘
```

## Component Descriptions

### 1. Data Layer (`data_loader.py`)

**Responsibility**: Ingesting and parsing market data

**Key Features**:
- Reads CSV files containing market data
- Creates `MarketDataPoint` objects with timestamp, symbol, and price
- Provides clean interface for data access

**Data Flow**:
```
CSV File → data_ingestor() → List[MarketDataPoint]
```

### 2. Models Layer (`models.py`)

**Responsibility**: Core data structures and business logic

**Components**:

#### Order
- Represents trading instructions
- Validates price is positive
- Tracks execution status

#### Position
- Represents holdings in a single security
- Tracks quantity and average price
- Immutable after creation (modified through Portfolio)

#### Portfolio
- Manages cash and all positions
- Updates positions on trades
- Calculates portfolio value
- Enforces business rules

#### Custom Exceptions
- `OrderError`: Invalid order parameters
- `ExecutionError`: Trade execution failures
- `ConfigError`: Configuration issues

### 3. Strategy Layer (`strategies.py`)

**Responsibility**: Trading logic and signal generation

**Architecture**:

```
┌─────────────────────────────────────┐
│      Strategy (ABC)                 │
│                                     │
│  + generate_signals()               │
└──────────────┬──────────────────────┘
               │
               ├─────────────────┬───────────────┐
               │                 │               │
    ┌──────────▼─────────┐  ┌───▼────────────┐   │
    │  MACD Strategy     │  │ Momentum       │   │
    │                    │  │ Strategy       │   │
    │ - Short MA         │  │                │   │
    │ - Long MA          │  │ - Lookback     │   │
    │ - Crossover Logic  │  │ - Thresholds   │   │
    └────────────────────┘  │ - ROC Calc     │   │
                            └────────────────┘   │
                                                 │
                                    ┌────────────▼────────┐
                                    │  StrategyState      │
                                    │                     │
                                    │ - Strategy Instance │
                                    │ - Portfolio         │
                                    │ - Orders History    │
                                    │ - Errors            │
                                    │ - Value History     │
                                    └─────────────────────┘
```

**Strategy Pattern**:
- Abstract base class defines contract
- Concrete strategies implement specific algorithms
- Each strategy maintains its own state and indicators
- Strategies are independent and can run concurrently

**Signal Format**:
```python
[action, symbol, quantity, price]
# Example: ['Buy', 'AAPL', 100, 150.50]
```

### 4. Execution Engine (`engine.py`)

**Responsibility**: Orchestrating the backtesting simulation

**Workflow**:

```
Initialize
    │
    ├─── Sort ticks by timestamp
    ├─── Create strategy states
    ├─── Initialize portfolios
    └─── Extract unique symbols
         │
         ▼
    For each tick:
         │
         ├─── Update current prices
         │
         ├─── For each strategy:
         │    │
         │    ├─── Generate signal
         │    │
         │    ├─── Create order
         │    │    ├─── Validate signal format
         │    │    ├─── Check position limits
         │    │    └─── Check cash availability
         │    │
         │    ├─── Execute order
         │    │    ├─── Simulate random failures (1%)
         │    │    └─── Update portfolio
         │    │
         │    └─── Record portfolio value
         │
         ▼
    Return states
```

**Error Handling Strategy**:
- **Order Errors**: Logged, execution skipped, backtest continues
- **Execution Errors**: Logged, order marked as failed, backtest continues
- **Fatal Errors**: Propagate up, halt execution

**Key Design Decisions**:

1. **Chronological Processing**: Ensures no look-ahead bias
2. **Independent Strategies**: Each strategy has its own portfolio and state
3. **Error Isolation**: Failures in one strategy don't affect others
4. **Price Tracking**: Maintains current prices for portfolio valuation

### 5. Reporting Layer (`reporting.py`)

**Responsibility**: Performance analysis and visualization

**Module Structure**:

```
Reporting Module
    │
    ├─── Metrics Calculation
    │    ├─── total_return()
    │    ├─── period_returns()
    │    ├─── calc_sharpe()
    │    └─── calc_max_dd()
    │
    ├─── Visualization
    │    ├─── plot_portfolio_value()
    │    └─── plot_drawdown()
    │
    └─── Report Generation
         ├─── write_markdown_report()
         └─── generate_report()
```

**Analytics Pipeline**:

```
Raw History Data
      │
      ├─── value_tbl() → Polars LazyFrame
      │
      ├─── period_returns() → % changes
      │
      ├─── Metrics Calculation
      │    ├─── Total Return
      │    ├─── Sharpe Ratio
      │    └─── Max Drawdown
      │
      ├─── Visualization
      │    ├─── Equity Curve (PNG)
      │    └─── Drawdown Chart (PNG)
      │
      └─── Report Assembly
           └─── Markdown Report
```

## Data Flow

### Complete Backtesting Flow

```
1. Configuration
   config.yaml → main.py

2. Data Loading
   CSV → data_ingestor() → List[MarketDataPoint]

3. Strategy Initialization
   MarketDataPoint[] → Strategy.__init__()
   
4. Execution Loop
   For tick in ticks:
       tick → Strategy.generate_signals() → signal
       signal → Engine.create_order() → Order
       Order → Engine.execute_order() → Portfolio.update_position()
       Portfolio → Portfolio.get_value() → portfolio_value
       (timestamp, portfolio_value) → history

5. Analysis
   history → Reporting Module → Metrics + Charts + Report

6. Output
   ├─── img/pnl_*.png
   ├─── img/drawdown_*.png
   └─── doc/performance_*.md
```

## State Management

### Strategy State

Each strategy maintains:
- **Strategy Instance**: The algorithm itself
- **Portfolio**: Cash and positions
- **Orders**: Complete order history
- **Errors**: Order validation and execution errors
- **History**: Time-series of portfolio values

### Portfolio State

Portfolios track:
- **Cash**: Current available cash
- **Positions**: Dictionary of Position objects by symbol
- **Implicitly derived**: Total portfolio value

### Execution State

The engine maintains:
- **Current Prices**: Latest price for each symbol
- **Strategy States**: Dictionary mapping strategy names to states
- **Tick Position**: Current position in time-series

## Concurrency Model

Currently **single-threaded**:
- Strategies execute sequentially for each tick
- No race conditions
- Deterministic results

**Future Enhancement**: Parallel strategy execution with proper synchronization

## Error Handling Architecture

```
┌─────────────────────────────────────┐
│         Application Layer           │
│            (main.py)                │
└─────────────┬───────────────────────┘
              │
              │ ConfigError (fatal)
              │
┌─────────────▼───────────────────────┐
│       Execution Engine              │
│         (engine.py)                 │
└─────────────┬───────────────────────┘
              │
              ├─── OrderError (logged, continue)
              └─── ExecutionError (logged, continue)
              │
┌─────────────▼───────────────────────┐
│         Models Layer                │
│         (models.py)                 │
└─────────────────────────────────────┘
```

**Error Philosophy**:
- **Fail gracefully**: Don't stop backtest for single order failures
- **Log everything**: Track all errors for post-analysis
- **Validate early**: Catch errors before execution
- **Fail fast**: Configuration errors halt immediately

## Design Patterns

### 1. Strategy Pattern
- Defines family of algorithms (trading strategies)
- Makes them interchangeable
- Encapsulates strategy-specific logic

### 2. Template Method
- `Strategy.generate_signals()` as abstract method
- Concrete implementations provide specific logic

### 3. Data Transfer Object
- `Order`, `Position`, `MarketDataPoint` as simple data carriers
- Immutable data structures where appropriate

### 4. Facade Pattern
- `ExecutionEngine` provides simple interface to complex subsystem
- Hides complexity of order validation, execution, and portfolio management

### 5. Repository Pattern
- `Portfolio` manages collection of positions
- Provides clean interface for position updates and queries

## Extensibility Points

### Adding New Strategies

```python
class CustomStrategy(Strategy):
    def __init__(self, ticks, params):
        # Initialize indicators
        pass
    
    def generate_signals(self, tick):
        # Implement logic
        return [action, symbol, quantity, price]
```

### Adding New Metrics

```python
def calc_custom_metric(time, value):
    # Implement calculation
    return metric_value
```

### Adding New Order Types

Currently supports market orders only. To add limit orders:

1. Extend `Order` dataclass with `order_type` field
2. Modify `ExecutionEngine.execute_order()` logic
3. Add order book simulation (if needed)

## Performance Considerations

### Memory Usage
- **Efficient data structures**: Uses `deque` for sliding windows
- **Lazy evaluation**: Polars LazyFrames defer computation
- **Minimal copying**: Updates in-place where possible

### Time Complexity
- **Tick processing**: O(n) where n = number of ticks
- **Strategy signals**: Depends on strategy (typically O(1) per tick)
- **Portfolio updates**: O(1) per trade
- **Valuation**: O(s) where s = number of symbols

### Optimization Opportunities
- Vectorize indicator calculations
- Parallel strategy execution
- Incremental metric calculations
- Caching frequently accessed data

## Dependencies

```
polars          → Data manipulation
matplotlib      → Visualization
dataclasses     → Data structures
collections     → deque for efficient queues
typing          → Type hints
abc             → Abstract base classes
datetime        → Timestamp handling
pathlib         → Path operations
random          → Execution simulation
```

## Testing Strategy

Recommended test coverage:

1. **Unit Tests**:
   - Model validation
   - Strategy signal generation
   - Portfolio calculations
   - Metric computations

2. **Integration Tests**:
   - Full backtest execution
   - Multi-strategy scenarios
   - Error handling paths

3. **Validation Tests**:
   - Known outcome scenarios
   - Edge cases (zero cash, empty portfolio)
   - Stress tests (many orders, extreme prices)

---

*This architecture is designed for clarity, extensibility, and realistic simulation of trading scenarios.*
