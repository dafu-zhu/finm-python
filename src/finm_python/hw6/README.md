# HW6: Design Patterns in Financial Software Architecture

A scaffolding project for implementing key object-oriented design patterns in the context of financial analytics and trading platform simulation.

## Overview

This project provides the structure and interfaces for nine design patterns. **Your task is to implement the core logic** where you see `TODO` comments and `raise NotImplementedError()`.

### Patterns to Implement

**Creational Patterns:**
- Factory: Create instrument instances from raw data
- Singleton: Centralized configuration management
- Builder: Construct complex portfolio structures

**Structural Patterns:**
- Decorator: Add analytics to instruments without modifying base classes
- Adapter: Standardize external data formats
- Composite: Model portfolios as trees (already partially implemented)

**Behavioral Patterns:**
- Strategy: Interchangeable trading strategies
- Observer: Event notification system for signals
- Command: Order execution with undo/redo support

## Project Structure

```
hw6/
├── models.py                # Core models - implement get_type(), get_metrics(), get_value(), etc.
├── patterns/
│   ├── creational.py        # Factory, Singleton, Builder - implement core pattern logic
│   ├── structural.py        # Decorator (analytics), Adapter - implement calculations
│   └── behavioral.py        # Strategy, Observer, Command - implement signal generation
├── data_loader.py           # Data loading utilities (uses your pattern implementations)
├── analytics.py             # Helper functions for analytics
├── engine.py                # Strategy execution engine
├── reporting.py             # Observer implementations for reporting
├── main.py                  # Demo script showing pattern usage
└── tests/
    └── test_patterns.py     # Comprehensive tests to validate your implementations
```

## Getting Started

### 1. Read the Requirements

Check `docs/hw6.md` for the full assignment specification.

### 2. Implement Patterns

Start with the simplest patterns and work your way up:

**Recommended Order:**

1. **Composite Pattern** (`models.py`):
   - `Position.get_value()` - multiply quantity by price
   - `Position.get_positions()` - return self as dict in list
   - `PortfolioGroup.get_value()` - sum child values
   - `PortfolioGroup.get_positions()` - flatten child positions

2. **Factory Pattern** (`patterns/creational.py`):
   - `InstrumentFactory.create_instrument()` - switch on type

3. **Singleton Pattern** (`patterns/creational.py`):
   - `Config.__new__()` - ensure single instance
   - `Config.load()`, `Config.get()`, `Config.set()`

4. **Builder Pattern** (`patterns/creational.py`):
   - `PortfolioBuilder.set_owner()`, `add_position()`, `add_subportfolio()`, `build()`
   - `PortfolioBuilder.from_dict()` - recursive construction

5. **Decorator Pattern** (`patterns/structural.py`):
   - `VolatilityDecorator.calculate_volatility()` - annualized volatility
   - `BetaDecorator.calculate_beta()` - covariance / market variance
   - `DrawdownDecorator.calculate_max_drawdown()` - peak-to-trough decline

6. **Adapter Pattern** (`patterns/structural.py`):
   - `YahooFinanceAdapter.get_data()` - parse JSON format
   - `BloombergXMLAdapter.get_data()` - parse XML format

7. **Strategy Pattern** (`patterns/behavioral.py`):
   - `MeanReversionStrategy.generate_signals()` - deviation from MA
   - `BreakoutStrategy.generate_signals()` - break above/below range

8. **Observer Pattern** (`patterns/behavioral.py`):
   - `SignalPublisher.attach()`, `detach()`, `notify()`
   - `LoggerObserver.update()` - log signals
   - `AlertObserver.update()` - check threshold

9. **Command Pattern** (`patterns/behavioral.py`):
   - `ExecuteOrderCommand.execute()`, `undo()`
   - `CancelOrderCommand.execute()`, `undo()`
   - `CommandInvoker.execute()`, `undo()`, `redo()`

### 3. Run Tests

As you implement each pattern, run the corresponding tests:

```bash
# Run all tests (most will fail initially)
pytest src/finm_python/hw6/tests/ -v

# Run specific pattern tests
pytest -k TestFactoryPattern -v
pytest -k TestSingletonPattern -v
pytest -k TestBuilderPattern -v
pytest -k TestDecoratorPattern -v
pytest -k TestAdapterPattern -v
pytest -k TestCompositePattern -v
pytest -k TestStrategyPattern -v
pytest -k TestObserverPattern -v
pytest -k TestCommandPattern -v
```

### 4. Demo Your Implementation

Once you've implemented the patterns, uncomment the demo functions in `main.py`:

```bash
python -m finm_python.hw6.main
```

## Implementation Tips

### Finding TODOs

Search for `TODO` comments in the code to find what needs to be implemented:

```bash
grep -r "TODO" src/finm_python/hw6/
```

### Example: Factory Pattern

```python
# In patterns/creational.py
@staticmethod
def create_instrument(data: dict) -> Instrument:
    # TODO: Implement factory logic
    # 1. Extract type from data
    instrument_type = data.get("type", "").lower()
    symbol = data["symbol"]
    price = float(data["price"])

    # 2. Create appropriate instance based on type
    if instrument_type == "stock":
        return Stock(symbol, price, data.get("sector", ""), data.get("issuer", ""))
    elif instrument_type == "bond":
        return Bond(symbol, price, ...)
    # etc.
```

### Example: Decorator Pattern

```python
# In patterns/structural.py
def calculate_volatility(self) -> float:
    if len(self._historical_returns) < 2:
        return 0.0

    mean = sum(self._historical_returns) / len(self._historical_returns)
    variance = sum((r - mean) ** 2 for r in self._historical_returns) / (len(self._historical_returns) - 1)
    daily_vol = variance ** 0.5
    annualized_vol = daily_vol * (252 ** 0.5)
    return annualized_vol
```

## Data Files

Sample data files are provided in `scripts/hw6/`:

- `config.json` - System configuration
- `instruments.csv` - Instrument definitions
- `portfolio_structure.json` - Portfolio hierarchy
- `strategy_params.json` - Trading strategy parameters
- `external_data_yahoo.json` - Yahoo Finance format
- `external_data_bloomberg.xml` - Bloomberg XML format
- `market_data.csv` - Historical OHLCV data

## Deliverables

1. **Completed Implementation** - All TODO sections filled in
2. **Passing Tests** - All unit tests should pass
3. **Design Report** - Fill in `design_report.md` with your analysis
4. **Working Demo** - `main.py` should run without errors

## Testing Your Work

Run the full test suite to validate your implementations:

```bash
# All tests
pytest src/finm_python/hw6/tests/ -v

# With coverage
pytest src/finm_python/hw6/tests/ --cov=src/finm_python/hw6
```

All 45+ tests should pass when your implementation is complete.

## Dependencies

- Python 3.11+
- pytest (for testing)
- Standard library only (no external packages required)

## Common Issues

1. **NotImplementedError** - You haven't completed that TODO section yet
2. **Import errors** - Make sure you're running from the project root
3. **Test failures** - Read the test carefully to understand expected behavior
4. **Type errors** - Check method signatures match expected interfaces

## Need Help?

- Review the pattern docstrings for implementation hints
- Check the test cases to see expected behavior
- Look at `main.py` for usage examples
- Consult the design patterns documentation in your course materials

---

Created for FINM Python Programming Course - Assignment 6
