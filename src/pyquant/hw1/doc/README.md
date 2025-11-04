# Trading Backtesting System

A Python-based algorithmic trading backtesting framework for evaluating trading strategies using historical market data.

## Overview

This system provides a complete infrastructure for backtesting trading strategies with realistic order execution, portfolio management, and comprehensive performance reporting. It supports multiple concurrent strategies and generates detailed performance analytics with visualizations.

## Features

- **Strategy Framework**: Abstract base class for implementing custom trading strategies
- **Execution Engine**: Simulates realistic order execution with validation and error handling
- **Portfolio Management**: Tracks positions, cash, and portfolio value over time
- **Built-in Strategies**:
  - MACD (Moving Average Convergence Divergence) crossover strategy
  - Momentum strategy based on rate of change
- **Performance Analytics**:
  - Total return calculation
  - Sharpe ratio
  - Maximum drawdown analysis with recovery tracking
  - Period-by-period returns
- **Visualization**: Automated generation of equity curves and drawdown charts
- **Reporting**: Markdown reports with comprehensive performance metrics

## Project Structure

```
src/pyquant/hw1/
├── models.py           # Core data models (Order, Position, Portfolio)
├── strategies.py       # Strategy implementations and base class
├── engine.py           # Execution engine for running backtests
├── reporting.py        # Performance metrics and report generation
├── data_loader.py      # Market data ingestion (not included)
└── main.py            # Entry point and configuration
```

## Quick Start

### Installation

```bash
# Install required dependencies
pip install polars matplotlib --break-system-packages
```

### Basic Usage

```python
from engine import ExecutionEngine
from strategies import MACDStrategy, MomentumStrategy
from data_loader import data_ingestor

# Load market data
ticks = data_ingestor('market_data.csv')

# Configure strategies
strategies = [
    MACDStrategy(ticks=ticks, params={'short_period': 12, 'long_period': 26}),
    MomentumStrategy(ticks=ticks, params={'lookback': 20, 'buy_threshold': 0.02, 'sell_threshold': -0.02})
]

# Run backtest
engine = ExecutionEngine(ticks, strategies, init_cash=1_000_000)
states = engine.run()

# Generate reports
generate_report(states.keys(), states, img_dir='img', doc_dir='doc')
```

## Documentation

Detailed documentation is available in the following files:

- **[System Architecture](Architecture.md)** - High-level system design and component interactions
- **[Models Documentation](MODELS.md)** - Data models and portfolio management
- **[Strategies Guide](STRATEGIES.md)** - Strategy implementation guide and examples
- **[Execution Engine](ENGINE.md)** - Order execution and backtesting workflow
- **[Reporting & Analytics](REPORTING.md)** - Performance metrics and visualization
- **[API Reference](API_Reference.md)** - Complete API documentation
- **[Developer Guide](Developer_Guide.md)** - How to extend and customize the system

## Key Concepts

### Strategy

A strategy implements trading logic by analyzing market data and generating trading signals. Each strategy must implement the `generate_signals()` method.

### Order

Represents a buy or sell instruction with symbol, quantity, price, and status tracking.

### Portfolio

Manages cash and positions across multiple securities, tracking average prices and current holdings.

### Execution Engine

Orchestrates the backtesting process by:
1. Iterating through market data chronologically
2. Generating signals from each strategy
3. Creating and validating orders
4. Executing orders and updating portfolios
5. Recording portfolio values over time

## Performance Metrics

The system calculates the following metrics:

- **Total Return**: Overall percentage gain/loss
- **Sharpe Ratio**: Risk-adjusted return measure
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Drawdown Recovery**: Time taken to recover from maximum drawdown
- **Period Returns**: Tick-by-tick percentage changes

## Configuration

Configuration is done through dictionaries in `main.py`:

```python
config = {
    'init_cash': 1_000_000,
    'strategies': [
        {
            'type': MACDStrategy,
            'params': {
                'short_period': 12,
                'long_period': 26
            }
        }
    ]
}
```

## Requirements

- Python 3.7+
- polars (data manipulation)
- matplotlib (visualization)
- dataclasses (Python 3.7+)

## Limitations

- **No transaction costs**: Commissions and fees are not included
- **No slippage**: Orders execute at exact signal prices
- **Simplified execution**: 1% random failure rate for realism
- **No position limits**: No maximum position size constraints
- **Cash can go negative**: No margin requirements enforced
- **Fixed quantities**: All signals use 100 share lots

## Future Enhancements

Potential improvements include:

- Transaction cost modeling
- Slippage simulation
- Dynamic position sizing
- Multiple asset class support
- Risk management rules (stop-loss, position limits)
- Walk-forward optimization
- Monte Carlo simulation
- Multi-timeframe analysis

## License

See LICENSE file for details.

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Implement comprehensive error handling
2. Add unit tests for new features
3. Update documentation
4. Follow existing code style
5. Validate strategies on historical data

## Support

For issues, questions, or contributions, please refer to the detailed documentation files or contact the development team.

---

*Last updated: 2025*
