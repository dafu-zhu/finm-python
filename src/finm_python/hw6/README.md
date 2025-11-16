# HW6: Design Patterns in Financial Software Architecture

A modular Python system demonstrating key object-oriented design patterns in the context of financial analytics and trading platform simulation.

## Overview

This project implements a financial analytics and trading system using nine design patterns from three categories:

- **Creational Patterns**: Factory, Singleton, Builder
- **Structural Patterns**: Decorator, Adapter, Composite
- **Behavioral Patterns**: Strategy, Observer, Command

## Project Structure

```
hw6/
├── __init__.py              # Package initialization
├── models.py                # Core financial models (Instrument, Portfolio)
├── data_loader.py           # Adapter-based data ingestion
├── analytics.py             # Decorator-based instrument analytics
├── engine.py                # Strategy execution and signal dispatch
├── reporting.py             # Observer-based logging and reporting
├── main.py                  # Main orchestration and demos
├── patterns/                # Design pattern implementations
│   ├── __init__.py
│   ├── creational.py        # Factory, Singleton, Builder
│   ├── structural.py        # Decorator, Adapter
│   └── behavioral.py        # Strategy, Observer, Command
├── tests/                   # Unit tests
│   ├── __init__.py
│   └── test_patterns.py
└── output/                  # Generated reports
```

## Quick Start

### Installation

Ensure you have Python 3.11+ and the project dependencies installed:

```bash
cd /path/to/finm-python
pip install -e .
```

### Running the Demo

```bash
python -m finm_python.hw6.main
```

This runs demonstrations of all nine design patterns with sample financial data.

### Running Tests

```bash
pytest src/finm_python/hw6/tests/ -v
```

## Module Descriptions

### `models.py`
Core data structures for the financial system:
- `Instrument` (abstract base): Base class for financial instruments
- `Stock`, `Bond`, `ETF`: Concrete instrument implementations
- `MarketDataPoint`: Standardized market data structure
- `PortfolioComponent`: Abstract base for Composite pattern
- `Position`: Leaf node in portfolio tree
- `PortfolioGroup`: Composite node for grouping positions
- `Portfolio`: Complete portfolio with metadata

### `patterns/creational.py`
**Factory Pattern** - `InstrumentFactory`
- Creates Stock, Bond, or ETF instances from raw data dictionaries
- Centralizes object creation logic
- Example: `InstrumentFactory.create_instrument({"type": "Stock", ...})`

**Singleton Pattern** - `Config`
- Centralized configuration management
- Ensures single instance across all modules
- Loads settings from JSON configuration files
- Example: `Config.get_instance().get("log_level")`

**Builder Pattern** - `PortfolioBuilder`
- Fluent interface for constructing complex portfolios
- Supports nested sub-portfolios
- Example:
  ```python
  portfolio = (PortfolioBuilder("Main")
               .set_owner("user")
               .add_position("AAPL", 100, 172.35)
               .build())
  ```

### `patterns/structural.py`
**Decorator Pattern** - Analytics Decorators
- `VolatilityDecorator`: Adds volatility calculation
- `BetaDecorator`: Adds beta coefficient calculation
- `DrawdownDecorator`: Adds maximum drawdown calculation
- Decorators can be stacked without modifying base classes
- Example:
  ```python
  decorated = DrawdownDecorator(
      BetaDecorator(
          VolatilityDecorator(stock)))
  ```

**Adapter Pattern** - Data Source Adapters
- `YahooFinanceAdapter`: Converts Yahoo JSON to `MarketDataPoint`
- `BloombergXMLAdapter`: Converts Bloomberg XML to `MarketDataPoint`
- Standardizes different external data formats

### `patterns/behavioral.py`
**Strategy Pattern** - Trading Strategies
- `Strategy` (abstract): Base interface for all strategies
- `MeanReversionStrategy`: Generates signals based on price deviation from moving average
- `BreakoutStrategy`: Generates signals on price breakouts
- Strategies are interchangeable at runtime

**Observer Pattern** - Signal Notifications
- `SignalPublisher`: Subject that manages observers
- `LoggerObserver`: Logs all signals
- `AlertObserver`: Alerts on high-value trades
- Dynamic registration and notification

**Command Pattern** - Order Execution
- `Command` (abstract): Base command interface
- `ExecuteOrderCommand`: Executes trades
- `CancelOrderCommand`: Cancels orders
- `CommandInvoker`: Manages command history with undo/redo

### `data_loader.py`
Unified data loading using adapters:
- `load_instruments_from_csv()`: Load instruments using Factory
- `load_market_data_from_csv()`: Stream market data points
- `load_yahoo_data()`: Load via Yahoo adapter
- `load_bloomberg_data()`: Load via Bloomberg adapter

### `analytics.py`
Convenience functions for decorator-based analytics:
- `add_volatility_analysis()`: Wrap instrument with volatility metrics
- `add_beta_analysis()`: Wrap instrument with beta metrics
- `add_drawdown_analysis()`: Wrap instrument with drawdown metrics
- `add_full_analytics()`: Stack all analytics decorators
- `calculate_returns()`: Compute simple returns from prices

### `engine.py`
Main strategy execution engine:
- `StrategyEngine`: Coordinates strategy execution, signal generation, and notification
- Manages strategy registration and switching
- Integrates with Observer pattern for signal dispatch
- Supports configuration via JSON files

### `reporting.py`
Observer-based reporting and analytics:
- `LoggerObserver`: File and console logging
- `AlertObserver`: High-value trade alerts
- `StatisticsObserver`: Signal statistics collection
- `ReportGenerator`: Markdown report generation

### `main.py`
Orchestrates the entire system:
- Demonstrates each pattern in isolation
- Shows full system integration
- Loads configuration and data from files
- Generates reports

## Data Files

The system uses data files from `scripts/hw6/`:

- `config.json`: System configuration (log level, paths, default strategy)
- `instruments.csv`: Instrument definitions (symbol, type, price, attributes)
- `portfolio_structure.json`: Portfolio hierarchy definition
- `strategy_params.json`: Trading strategy parameters
- `external_data_yahoo.json`: Sample Yahoo Finance format data
- `external_data_bloomberg.xml`: Sample Bloomberg XML format data
- `market_data.csv`: Historical OHLCV market data

## Example Usage

### Creating Instruments with Factory
```python
from finm_python.hw6.patterns.creational import InstrumentFactory

factory = InstrumentFactory()
stock = factory.create_instrument({
    "symbol": "AAPL",
    "type": "Stock",
    "price": 172.35,
    "sector": "Technology"
})
```

### Building Portfolios
```python
from finm_python.hw6.patterns.creational import PortfolioBuilder

portfolio = (PortfolioBuilder("My Portfolio")
             .set_owner("jdoe")
             .add_position("AAPL", 100, 172.35)
             .add_position("MSFT", 50, 328.10)
             .build())

print(f"Total Value: ${portfolio.get_value():,.2f}")
```

### Adding Analytics with Decorators
```python
from finm_python.hw6.models import Stock
from finm_python.hw6.analytics import add_full_analytics

stock = Stock("AAPL", 172.35, "Technology", "Apple")
decorated = add_full_analytics(
    stock,
    historical_returns=[0.01, -0.02, 0.015],
    market_returns=[0.005, -0.01, 0.008],
    price_history=[170.0, 172.0, 168.0]
)
metrics = decorated.get_metrics()
# metrics includes: volatility, beta, max_drawdown
```

### Running Trading Strategies
```python
from finm_python.hw6.engine import StrategyEngine
from finm_python.hw6.patterns.behavioral import MeanReversionStrategy
from finm_python.hw6.reporting import LoggerObserver

engine = StrategyEngine()
engine.register_strategy("MeanReversion", MeanReversionStrategy())
engine.set_active_strategy("MeanReversion")
engine.attach_observer(LoggerObserver())

# Process market ticks
for tick in market_data:
    signals = engine.process_tick(tick)
```

### Order Execution with Undo/Redo
```python
from finm_python.hw6.patterns.behavioral import (
    Order, ExecuteOrderCommand, CommandInvoker
)

invoker = CommandInvoker()
order = Order("ORD001", "AAPL", "BUY", 100, 172.35)

invoker.execute(ExecuteOrderCommand(order))  # Execute
invoker.undo()  # Revert execution
invoker.redo()  # Re-execute
```

## Testing

Run all tests:
```bash
pytest src/finm_python/hw6/tests/ -v
```

Tests cover:
- Factory creates correct instrument types
- Singleton behavior with shared config
- Builder constructs proper portfolio hierarchies
- Decorator-enhanced analytics output
- Adapter data format conversion
- Composite recursive value calculation
- Strategy signal generation logic
- Observer notification dispatch
- Command execution and undo/redo

## Dependencies

- Python 3.11+
- pytest (for testing)
- Standard library only (no external packages required)

## Author

Created for FINM Python Programming Course - Assignment 6
