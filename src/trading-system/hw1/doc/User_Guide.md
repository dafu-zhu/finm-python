# User Guide

A comprehensive guide for using the Trading Backtesting System to test and evaluate trading strategies.

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Running Backtests](#running-backtests)
- [Understanding Reports](#understanding-reports)
- [Strategy Selection](#strategy-selection)
- [Performance Metrics](#performance-metrics)
- [Tips and Best Practices](#tips-and-best-practices)
- [FAQ](#faq)

---

## Introduction

The Trading Backtesting System allows you to test trading strategies using historical market data. By simulating trades based on your strategy rules, you can evaluate performance before risking real capital.

### What This System Does

- **Simulates Trading**: Executes buy and sell orders based on strategy signals
- **Manages Portfolio**: Tracks cash, positions, and overall value
- **Calculates Metrics**: Computes return, risk, and drawdown statistics
- **Generates Reports**: Creates visual charts and detailed performance reports

### What You Need

- Historical market data in CSV format
- Python 3.7 or higher
- Basic understanding of trading concepts

---

## Installation

### Step 1: Install Python

Download and install Python from [python.org](https://python.org) (version 3.12 or higher).

Verify installation:
```bash
python --version
```

### Step 2: Install Dependencies

```bash
uv sync
```

### Step 3: Download the System

```bash
# Clone or download the repository
git clone <repository-url>
```

---

## Quick Start

### Basic Example

Create a file called `my_backtest.py`:

```python
from src.pyquant.hw1.engine import ExecutionEngine
from src.pyquant.hw1.strategies import MACDStrategy
from src.pyquant.hw1.data_loader import data_ingestor
from src.pyquant.hw1.reporting import generate_report
from pathlib import Path

# 1. Load your market data
ticks = data_ingestor('market_data.csv')

# 2. Create a strategy
strategy = MACDStrategy(
    ticks=ticks,
    params={
        'short_period': 12,
        'long_period': 26
    }
)

# 3. Run the backtest
engine = ExecutionEngine(
    ticks=ticks,
    strategies=[strategy],
    init_cash=100_000  # Start with $100,000
)

states = engine.run()

# 4. Generate reports
generate_report(
    names=states.keys(),
    states=states,
    img_dir=Path('img'),
    doc_dir=Path('doc')
)

print("Backtest complete! Check the 'doc' folder for reports.")
```

Run it:
```bash
python my_backtest.py
```

---

## Configuration

### Data Format

Your CSV file should have these columns:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| timestamp | datetime | Date and time | 2024-01-15 09:30:00 |
| symbol | string | Ticker symbol | AAPL |
| price | float | Stock price | 150.50 |

Example CSV:
```csv
timestamp,symbol,price
2024-01-15 09:30:00,AAPL,150.25
2024-01-15 09:30:00,GOOGL,2850.00
2024-01-15 09:31:00,AAPL,150.50
2024-01-15 09:31:00,GOOGL,2855.00
```

### Strategy Configuration

Each strategy requires specific parameters. Here are the available strategies:

#### MACD Strategy

Trades based on moving average crossovers.

```python
MACDStrategy(
    ticks=ticks,
    params={
        'short_period': 12,   # Short MA window (days/ticks)
        'long_period': 26     # Long MA window (days/ticks)
    }
)
```

**Trading Rules**:
- **Buy**: When short MA crosses above long MA
- **Sell**: When short MA crosses below long MA

**Parameter Guidelines**:
- `short_period` should be less than `long_period`
- Common values: 12/26, 5/20, 10/30
- Smaller values = more signals, more sensitive
- Larger values = fewer signals, more stable

#### Momentum Strategy

Trades based on rate of change.

```python
MomentumStrategy(
    ticks=ticks,
    params={
        'lookback': 20,           # Period to calculate momentum
        'buy_threshold': 0.02,    # Buy if ROC > 2%
        'sell_threshold': -0.02   # Sell if ROC < -2%
    }
)
```

**Trading Rules**:
- **Buy**: When price momentum exceeds buy threshold
- **Sell**: When price momentum falls below sell threshold

**Parameter Guidelines**:
- `lookback`: 10-30 typical
- `buy_threshold`: 0.01 to 0.05 (1% to 5%)
- `sell_threshold`: -0.01 to -0.05 (-1% to -5%)
- Wider thresholds = fewer but stronger signals

### Multiple Strategies

Test multiple strategies simultaneously:

```python
strategies = [
    MACDStrategy(ticks=ticks, params={'short_period': 12, 'long_period': 26}),
    MACDStrategy(ticks=ticks, params={'short_period': 5, 'long_period': 20}),
    MomentumStrategy(ticks=ticks, params={
        'lookback': 20, 
        'buy_threshold': 0.02, 
        'sell_threshold': -0.02
    })
]

engine = ExecutionEngine(ticks=ticks, strategies=strategies, init_cash=100_000)
states = engine.run()
```

Each strategy operates independently with its own portfolio.

---

## Running Backtests

### Complete Workflow

```python
# 1. Load data
ticks = data_ingestor('your_data.csv')
print(f"Loaded {len(ticks)} data points")

# 2. Create strategies
strategies = [
    MACDStrategy(ticks=ticks, params={'short_period': 12, 'long_period': 26})
]

# 3. Set up engine
engine = ExecutionEngine(
    ticks=ticks,
    strategies=strategies,
    init_cash=100_000
)

# 4. Run backtest
print("Running backtest...")
states = engine.run()

# 5. Generate reports
from pathlib import Path
generate_report(
    names=states.keys(),
    states=states,
    img_dir=Path('output/images'),
    doc_dir=Path('output/reports')
)

# 6. View results
for name, state in states.items():
    print(f"\n{name}:")
    print(f"  Orders executed: {len(state.orders)}")
    print(f"  Order errors: {len(state.order_errors)}")
    print(f"  Execution errors: {len(state.execution_errors)}")
    
    if state.history:
        initial_value = state.history[0][1]
        final_value = state.history[-1][1]
        return_pct = (final_value / initial_value - 1) * 100
        print(f"  Return: {return_pct:+.2f}%")
```

### Understanding Console Output

During execution, you'll see:

```
Running backtest...
Plots saved to: output/images/pnl_MACD_12_26.png, output/images/drawdown_MACD_12_26.png
Report saved to: output/reports/performance_MACD_12_26.md

MACD_12_26:
  Orders executed: 45
  Order errors: 2
  Execution errors: 1
  Return: +12.35%
```

**What the numbers mean**:
- **Orders executed**: Total buy/sell orders placed
- **Order errors**: Orders rejected (insufficient cash/shares)
- **Execution errors**: Orders that failed to execute (1% random failure)
- **Return**: Total profit/loss as percentage

---

## Understanding Reports

### Report Files

After running a backtest, you'll find these files:

```
root/
├── img/
│   ├── pnl_MACD_12_26.png          # Equity curve
│   └── drawdown_MACD_12_26.png     # Drawdown chart
└── doc/
    └── performance_MACD_12_26.md   # Detailed report
```

### Equity Curve

The equity curve shows your portfolio value over time.

**What to look for**:
- **Upward trend**: Strategy is profitable
- **Smooth curve**: Consistent performance
- **Steep drops**: Large losses or drawdowns
- **Flat periods**: No trading or sideways movement

### Drawdown Chart

Shows peak-to-trough declines in portfolio value.

**Key points**:
- **Depth**: How far did the portfolio fall from peak?
- **Duration**: How long did it take to recover?
- **Frequency**: How often do drawdowns occur?

**Interpretation**:
- **Shallow drawdowns (<10%)**: Low risk
- **Moderate drawdowns (10-20%)**: Medium risk
- **Deep drawdowns (>20%)**: High risk

### Performance Metrics

#### Total Return

```
Total Return: +15.23%
```

The overall profit or loss over the entire period.

**Interpretation**:
- Positive: Strategy made money
- Negative: Strategy lost money
- Compare to buy-and-hold benchmark

#### Sharpe Ratio

```
Sharpe Ratio: 1.45
```

Measures risk-adjusted return. Higher is better.

**Interpretation**:
- **< 0**: Losing money
- **0 to 1**: Poor to acceptable
- **1 to 2**: Good
- **> 2**: Excellent

**Formula**: (Average Return - Risk Free Rate) / Standard Deviation

#### Maximum Drawdown

```
Maximum Drawdown: -12.45%
Peak: 2024-01-15 10:30:00
Bottom: 2024-01-18 14:20:00
Recovery: 2024-01-22 11:15:00
```

Largest peak-to-trough decline.

**Interpretation**:
- Shows worst-case loss during the period
- Important for risk management
- Consider if you could tolerate this loss

---

## Strategy Selection

### Choosing the Right Strategy

#### Market Conditions

Different strategies perform better in different markets:

| Market Type | Best Strategy | Why |
|-------------|---------------|-----|
| Trending | MACD | Captures sustained moves |
| Volatile | Momentum | Profits from sharp movements |
| Sideways | Neither | Both generate false signals |

#### Time Horizon

| Horizon | Parameter Adjustment |
|---------|---------------------|
| Short-term | Smaller periods (5/10) |
| Medium-term | Standard periods (12/26) |
| Long-term | Larger periods (50/200) |

### Parameter Tuning

#### MACD Parameters

**Conservative** (fewer signals):
```python
params={'short_period': 26, 'long_period': 52}
```

**Standard** (balanced):
```python
params={'short_period': 12, 'long_period': 26}
```

**Aggressive** (more signals):
```python
params={'short_period': 5, 'long_period': 10}
```

#### Momentum Parameters

**Conservative**:
```python
params={
    'lookback': 30,
    'buy_threshold': 0.05,   # 5%
    'sell_threshold': -0.05
}
```

**Aggressive**:
```python
params={
    'lookback': 10,
    'buy_threshold': 0.01,   # 1%
    'sell_threshold': -0.01
}
```

### Testing Multiple Configurations

Compare different parameter sets:

```python
# Test various MACD configurations
configs = [
    {'short_period': 5, 'long_period': 10},
    {'short_period': 12, 'long_period': 26},
    {'short_period': 26, 'long_period': 52}
]

strategies = [
    MACDStrategy(ticks=ticks, params=config)
    for config in configs
]

engine = ExecutionEngine(ticks=ticks, strategies=strategies, init_cash=100_000)
states = engine.run()

# Compare results
for name, state in states.items():
    final_value = state.history[-1][1]
    return_pct = (final_value / 100_000 - 1) * 100
    print(f"{name}: {return_pct:+.2f}%")
```

---

## Performance Metrics

### Complete Metrics Glossary

Compute:
- Total return `float`
- Series of periodic returns `pl.LazyFrame`: with column `['time', 'value']`
- Sharpe ratio `float`
- Maximum drawdown `dict`
  - max_drawdown `float`
  - peak `datetime`: day that reaches peak during the max drawdown
  - bottom `datetime`: day that reaches bottom during the max drawdown
  - recovery `datetime` or `None`: if value recovered from bottom, when it was recovered
  - duration `int` or `None`: if value recovered from bottom, how long it took to recover
  - drawdown `pl.LazyFrame`: with column `['time', 'drawdown']`

#### Returns Metrics

**Total Return**
- Overall gain/loss over entire period
- Formula: (Final Value / Initial Value) - 1

**Period Returns**
- Tick-by-tick percentage changes
- Used to calculate other metrics

#### Risk Metrics

**Sharpe Ratio**
- Risk-adjusted return measure
- Accounts for volatility
- Higher is better (>1 is good)

**Maximum Drawdown**
- Largest peak-to-trough decline
- Shows worst possible loss
- Important for risk tolerance

**Drawdown Duration**
- Time from peak to recovery
- Longer = more painful
- Some strategies never recover

#### Trading Metrics

**Number of Orders**
- Total trades executed
- More isn't always better

**Order Errors**
- Failed validations
- Indicates strategy issues

**Execution Errors**
- Failed executions (1% random)
- Simulates market reality

---

## Tips and Best Practices

### Before Running Backtests

1. **Clean Your Data**
   - Remove gaps and errors
   - Ensure timestamps are sequential
   - Check for outliers

2. **Choose Appropriate Timeframe**
   - Need enough data for strategy warmup
   - MACD with period 26 needs >26 data points
   - More data = more reliable results

3. **Set Realistic Capital**
   - Start with $10,000 - $1,000,000
   - Must be enough to execute trades
   - Consider transaction costs in reality

### During Backtests

1. **Monitor Errors**
   - High error count suggests strategy problems
   - Adjust parameters if many orders rejected

2. **Test Multiple Strategies**
   - Compare different approaches
   - Diversification reduces risk

3. **Vary Parameters**
   - Don't rely on single configuration
   - Test sensitivity to changes

### After Backtests

1. **Don't Overfit**
   - Excellent backtest results may not repeat
   - Market conditions change
   - Past performance ≠ future results

2. **Consider Transaction Costs**
   - Backtest assumes zero costs
   - Real trading has commissions and slippage
   - Frequent trading reduces actual returns

3. **Validate Assumptions**
   - 1% execution failure rate is arbitrary
   - Real markets may be more/less reliable
   - Test with different assumptions

### Common Pitfalls

❌ **Over-optimizing**: Tuning parameters until results look perfect
✅ **Better**: Test on different time periods

❌ **Ignoring risk**: Focusing only on returns
✅ **Better**: Consider Sharpe ratio and drawdowns

❌ **Trading too frequently**: Generating excessive orders
✅ **Better**: Use wider thresholds or longer periods

❌ **Not testing edge cases**: Only testing in ideal conditions
✅ **Better**: Test in different market environments

---

## FAQ

### General Questions

**Q: What initial capital should I use?**

A: Start with $100,000 for testing. This provides enough capital for multiple trades while being realistic for many retail traders. Adjust based on your actual intended investment.

**Q: How much historical data do I need?**

A: Minimum: 100 data points. Recommended: 500+ for reliable results. More data provides better statistical significance.

**Q: Can I use multiple stocks?**

A: Yes! The system supports multiple symbols in the same CSV file. Each strategy will trade all symbols.

### Strategy Questions

**Q: Which strategy is best?**

A: It depends on market conditions. MACD works well in trending markets, Momentum in volatile markets. Test both!

**Q: How do I know if my parameters are good?**

A: Compare multiple configurations. Good parameters show:
- Positive returns
- Sharpe ratio > 1
- Maximum drawdown < 20%

**Q: Can I create my own strategy?**

A: Yes! See the Developer Guide for instructions on implementing custom strategies.

### Technical Questions

**Q: Why do I get "Not enough cash" errors?**

A: Strategy is trying to buy more than available cash. Solutions:
- Increase initial capital
- Reduce position sizes
- Modify strategy to check cash before buying

**Q: What does the 1% execution failure mean?**

A: Simulates real market conditions where orders sometimes fail. This is intentional for realism.

**Q: Why are my results different each run?**

A: The 1% random execution failure creates slight variations. Results should be similar, not identical.

**Q: How do I export results to Excel?**

A: Currently not supported. Reports are in Markdown format. You can convert metrics manually or export the history data.

### Performance Questions

**Q: What's a good Sharpe ratio?**

A: 
- < 0: Losing strategy
- 0-1: Acceptable
- 1-2: Good
- \> 2: Excellent

**Q: Is 50% drawdown too much?**

A: Yes, for most traders. Consider strategies with <20% drawdown for better risk management.

**Q: Why did my strategy lose money?**

A: Common reasons:
- Poor market conditions for that strategy type
- Parameters not suited to the data
- Transaction costs (not modeled) would eat returns
- Over-optimization on different data

---

## Next Steps

### Learning More

1. **Read the Architecture Guide**: Understand how the system works
2. **Explore API Reference**: Learn all available functions
3. **Study Developer Guide**: Create custom strategies

### Improving Your Strategy

1. **Backtest Different Periods**: Test on various market conditions
2. **Add Risk Management**: Implement stop-losses
3. **Combine Strategies**: Use multiple indicators
4. **Validate Out-of-Sample**: Test on unseen data

### Getting Help

- Check the FAQ section
- Review error messages carefully
- Consult API Reference for function details
- Read example code in the repository

---

*Happy backtesting! Remember: past performance does not guarantee future results.*
