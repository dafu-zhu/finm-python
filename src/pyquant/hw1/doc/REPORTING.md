# Reporting & Analytics

Complete guide to performance metrics, visualization, and report generation in the backtesting system.

## Table of Contents

- [Overview](#overview)
- [Performance Metrics](#performance-metrics)
- [Visualization](#visualization)
- [Report Generation](#report-generation)
- [Advanced Analytics](#advanced-analytics)
- [Custom Metrics](#custom-metrics)
- [Interpretation Guide](#interpretation-guide)

---

## Overview

### Purpose

The reporting module transforms raw backtest results into actionable insights through:

1. **Quantitative Metrics**: Statistical measures of performance and risk
2. **Visual Analytics**: Charts showing portfolio evolution and risk characteristics
3. **Comprehensive Reports**: Markdown documents with metrics, charts, and analysis

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


### Workflow

```
Backtest Results (StrategyState)
         │
         ├─── Extract History: (timestamp, value) pairs
         │
         ├─── Calculate Metrics
         │    ├─── Total Return
         │    ├─── Sharpe Ratio
         │    └─── Maximum Drawdown
         │
         ├─── Generate Visualizations
         │    ├─── Equity Curve
         │    └─── Drawdown Chart
         │
         └─── Create Report
              └─── Markdown with metrics + embedded charts
```

### Technology Stack

- **Data Processing**: Polars (high-performance DataFrame library)
- **Visualization**: Matplotlib with custom styling
- **Reporting**: Markdown format for portability

---

## Performance Metrics

### Total Return

#### Definition

Overall profit or loss over the entire backtesting period, expressed as a percentage.

#### Formula

```
Total Return = (Final Value / Initial Value) - 1
```

#### Implementation

```python
def total_return(value: list) -> float:
    """
    Calculate total return over entire period.
    
    Args:
        value: List of portfolio values over time
        
    Returns:
        Total return as decimal (e.g., 0.15 = 15%)
    """
    return value[-1] / value[0] - 1
```

#### Interpretation

| Return Range | Interpretation | Assessment |
|--------------|---------------|------------|
| > 20% | Excellent | Strong performance |
| 10% - 20% | Good | Above average |
| 0% - 10% | Modest | Acceptable |
| -10% - 0% | Poor | Underperforming |
| < -10% | Very Poor | Significant losses |

**Example**:
```python
values = [1000000, 1050000, 1120000, 1150000]
ret = total_return(values)
# Result: 0.15 (15% return)

print(f"Total Return: {ret * 100:.2f}%")
# Output: Total Return: 15.00%
```

---

### Period Returns

#### Definition

Percentage change from one period to the next, showing tick-by-tick performance.

#### Formula

```
Return(t) = (Value(t) / Value(t-1)) - 1
```

#### Implementation

```python
def period_returns(time: list, value: list) -> pl.LazyFrame:
    """
    Calculate period-by-period returns.
    
    Args:
        time: List of timestamps
        value: List of portfolio values
        
    Returns:
        Polars LazyFrame with columns ['time', 'value', 'returns']
    """
    tb = value_tbl(time, value)
    tb = tb.with_columns(
        pl.col('value').pct_change().alias('returns')
    ).drop_nulls()
    return tb
```

#### Uses

- Input for Sharpe ratio calculation
- Volatility measurement
- Return distribution analysis
- Identifying outlier periods

**Example**:
```python
times = [t1, t2, t3, t4]
values = [100000, 102000, 101000, 103000]

returns_df = period_returns(times, values).collect()

# Results:
# time | value  | returns
# t2   | 102000 | 0.02    (2% gain)
# t3   | 101000 | -0.0098 (-0.98% loss)
# t4   | 103000 | 0.0198  (1.98% gain)
```

---

### Sharpe Ratio

#### Definition

Risk-adjusted return measure that accounts for volatility. Higher values indicate better risk-adjusted performance.

#### Formula

```
Sharpe Ratio = (Mean Return - Risk Free Rate) / Std Dev of Returns
```

#### Implementation

```python
def calc_sharpe(value: list, risk_free: float = 0) -> float:
    """
    Calculate Sharpe ratio for risk-adjusted returns.
    
    Args:
        value: List of portfolio values
        risk_free: Risk-free rate (default: 0)
        
    Returns:
        Sharpe ratio
    """
    s = pl.Series('value', value)
    pct_chg = s.pct_change().drop_nulls()
    
    excess_ret = pct_chg.mean() - risk_free
    volatility = pct_chg.std()
    
    return excess_ret / volatility
```

#### Interpretation

| Sharpe Ratio | Interpretation | Assessment |
|--------------|---------------|------------|
| < 0 | Negative | Losing money |
| 0 - 1 | Below Average | Poor risk-adjusted returns |
| 1 - 2 | Good | Acceptable for most investors |
| 2 - 3 | Very Good | Strong risk-adjusted returns |
| > 3 | Excellent | Exceptional performance |

**Key Insights**:
- Compares return to volatility
- Values > 1 generally considered good
- Strategy with 15% return and high volatility may have lower Sharpe than 10% return with low volatility

**Example**:
```python
values = [100000, 102000, 101000, 103000, 105000]
sharpe = calc_sharpe(values)
# Result: ~1.45

# Interpretation: Good risk-adjusted returns
```

---

### Maximum Drawdown

#### Definition

The largest peak-to-trough decline in portfolio value during the backtesting period. Critical metric for understanding worst-case risk.

#### Formula

```
Drawdown(t) = (Value(t) / Peak Value up to t) - 1
Maximum Drawdown = min(Drawdown(t)) for all t
```

#### Implementation

```python
def calc_max_dd(time: list, value: list) -> dict:
    """
    Calculate maximum drawdown and recovery information.
    
    Args:
        time: List of timestamps
        value: List of portfolio values
        
    Returns:
        Dictionary with:
        - max_drawdown: Maximum drawdown as decimal
        - peak: Timestamp of peak before drawdown
        - bottom: Timestamp of lowest point
        - recover: Timestamp of recovery (None if not recovered)
        - duration: Time to recover (None if not recovered)
        - drawdown: LazyFrame with complete drawdown time series
    """
    # Create dataframe with returns
    tb = period_returns(time, value)
    
    # Calculate cumulative return and running peak
    tb = tb.with_columns(
        (pl.col('returns') + 1).cum_prod().alias('cum_return')
    ).with_columns(
        pl.col("cum_return").cum_max().alias("peak")
    ).with_columns(
        (pl.col("cum_return") / pl.col("peak") - 1).alias("drawdown")
    )
    
    # Find maximum drawdown period
    dd_period = tb.filter(
        pl.col("drawdown").eq(pl.col("drawdown").min())
    ).collect()
    
    max_dd = dd_period["drawdown"][0]
    peak_value = dd_period["peak"]
    bottom_day = dd_period['time'][0]
    
    # Find peak day
    peak_day = tb.filter(
        (pl.col("cum_return").eq(peak_value)) &
        (pl.col('time').le(bottom_day))
    ).collect()['time'][-1]
    
    # Find recovery day
    recover_df = tb.filter(
        pl.col("cum_return").ge(peak_value) &
        (pl.col('time').gt(bottom_day))
    ).collect()
    
    if recover_df.height > 0:
        recover_day = recover_df[0]['time'][0]
        duration = recover_day - peak_day
    else:
        recover_day = None
        duration = None
    
    return {
        "max_drawdown": max_dd,
        "peak": peak_day,
        "bottom": bottom_day,
        "recover": recover_day,
        "duration": duration,
        "drawdown": tb.select(pl.col(['time', "drawdown"]))
    }
```

#### Interpretation

**Drawdown Magnitude**:

| Drawdown | Risk Level | Assessment |
|----------|-----------|------------|
| 0% - 5% | Very Low | Minimal risk |
| 5% - 10% | Low | Acceptable for conservative investors |
| 10% - 20% | Moderate | Typical for balanced strategies |
| 20% - 30% | High | Requires strong risk tolerance |
| > 30% | Very High | Extreme risk |

**Recovery Time**:
- Quick recovery (< 10 periods): Resilient strategy
- Moderate recovery (10-50 periods): Average
- Slow recovery (> 50 periods): Concerning
- No recovery: Strategy may be fundamentally flawed

**Example**:
```python
times = [t1, t2, t3, t4, t5, t6]
values = [100000, 110000, 105000, 95000, 98000, 112000]

dd_info = calc_max_dd(times, values)

print(f"Max Drawdown: {dd_info['max_drawdown']*100:.2f}%")
# Output: Max Drawdown: -13.64%

print(f"Peak: {dd_info['peak']}")
print(f"Bottom: {dd_info['bottom']}")
print(f"Recovered: {dd_info['recover']}")
print(f"Duration: {dd_info['duration']}")
```

---

## Visualization

### Equity Curve (Portfolio Value Chart)

#### Purpose

Visualizes portfolio value evolution over time, showing cumulative performance.

#### Implementation

```python
def plot_portfolio_value(report: dict, output_path: Path):
    """
    Plot portfolio value over time showing the equity curve.
    
    Args:
        report: Dictionary containing 'prd_return' LazyFrame and 'name'
        output_path: Path to save the PNG plot
    """
    # Collect data
    df = report['prd_return'].collect()
    
    # Normalize to start at 1.0 for easier comparison
    initial_value = df['value'][0]
    normalized_values = df['value'] / initial_value
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot equity curve
    ax.plot(df['time'], normalized_values, 
            linewidth=1.5, color='#2E86AB', label='Portfolio Value')
    
    # Add reference line at 1.0 (starting value)
    ax.axhline(y=1.0, color='gray', linestyle='--', 
               linewidth=1, alpha=0.5)
    
    # Formatting
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('Portfolio Value (Normalized)', fontsize=12)
    ax.set_title(f'Portfolio Value Over Time - {report["name"]}', 
                 fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
```

#### Reading the Chart

**Trend Direction**:
- Upward slope: Profitable strategy
- Downward slope: Losing strategy
- Flat: Break-even or inactive

**Smoothness**:
- Smooth curve: Consistent performance
- Jagged curve: High volatility
- Steep changes: Large individual trades

**Key Features**:
```
     ┌─────────────────────────────────────┐
  1.5│                            ╱────────│ Final Value
     │                       ╱────          │
  1.2│                   ╱──                │
     │               ╱──                    │
  1.0│═════════════╱                       │ Starting Value
     │          ╱                           │
  0.8│      ╱──                             │ Drawdown
     │  ╱──                                 │
  0.6└─────────────────────────────────────┘
     Time →
```

---

### Drawdown Chart

#### Purpose

Visualizes the magnitude and duration of portfolio declines from peak values.

#### Implementation

```python
def plot_drawdown(report: dict, output_path: Path):
    """
    Plot drawdown over time with key events annotated.
    
    Args:
        report: Dictionary containing 'max_dd' with drawdown info and 'name'
        output_path: Path to save the PNG plot
    """
    # Collect drawdown data
    df = report['max_dd']['drawdown'].collect()
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot drawdown area (fill between 0 and drawdown)
    ax.fill_between(df['time'], 0, df['drawdown'] * 100,
                    alpha=0.3, color='#A23B72', label='Drawdown')
    
    # Plot drawdown line
    ax.plot(df['time'], df['drawdown'] * 100,
            linewidth=1.5, color='#A23B72')
    
    # Formatting
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('Drawdown (%)', fontsize=12)
    ax.set_title(f'Drawdown Analysis - {report["name"]}', 
                 fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left')
    
    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.xticks(rotation=45)
    
    # Set y-axis (0 at top, negative values below)
    y_min = df['drawdown'].min() * 100
    ax.set_ylim(y_min * 1.1, 0)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
```

#### Reading the Chart

**Depth**:
- Shallow dips: Low risk
- Deep valleys: High risk
- Flat at 0: At peak value

**Width**:
- Narrow dips: Quick recovery
- Wide valleys: Prolonged drawdown
- Multiple dips: Volatile strategy

**Example Chart**:
```
   0%│════════════════════════════════════│ No Drawdown (at peak)
     │    ╲                               │
  -5%│     ╲   ╱                          │ Moderate Drawdown
     │      ╲ ╱                           │
 -10%│       ╳        ╱─────              │ Recovering
     │      ╱ ╲      ╱                    │
 -15%│     ╱   ╲    ╱                     │
     │    ╱     ╲  ╱                      │
 -20%│───────────╲╱───────────────────────│ Maximum Drawdown
     └─────────────────────────────────────
                Time →
```

---

## Report Generation

### Comprehensive Markdown Reports

#### Structure

```markdown
# Performance Report: Strategy Name

## Executive Summary
[Metrics table with key statistics]

## Performance Analysis
[Narrative interpretation of results]

### Portfolio Value Over Time
[Embedded equity curve image]

## Drawdown Analysis
[Embedded drawdown chart]

### Maximum Drawdown Details
[Table with peak, bottom, recovery timestamps]

## Key Statistics
[Complete metrics table]

## Conclusion
[Overall assessment and recommendations]
```

#### Generation Process

```python
def generate_report(names, states, img_dir: Path, doc_dir: Path):
    """
    Generate complete performance reports for all strategies.
    
    Args:
        names: Strategy names (keys from states dict)
        states: Dictionary mapping names to StrategyState objects
        img_dir: Directory to save chart images
        doc_dir: Directory to save markdown reports
    """
    for name in names:
        # Extract history
        time, value = zip(*states[name].history)
        
        # Calculate all metrics
        max_dd = calc_max_dd(time, value)
        report = {
            'name': name,
            'ttl_return': total_return(value),
            'prd_return': period_returns(time, value),
            'sharpe': calc_sharpe(value),
            'max_dd': max_dd
        }
        
        # Generate visualizations
        pnl_path = img_dir / f'pnl_{name}.png'
        drawdown_path = img_dir / f'drawdown_{name}.png'
        
        plot_portfolio_value(report, output_path=pnl_path)
        plot_drawdown(report, output_path=drawdown_path)
        
        print(f"Plots saved to: {pnl_path}, {drawdown_path}")
        
        # Generate markdown report
        md_path = doc_dir / f'performance_{name}.md'
        write_markdown_report(report, pnl_path, drawdown_path, md_path)
        
        print(f"Report saved to: {md_path}")
```

#### Report Sections

**1. Executive Summary**
```markdown
| Metric | Value |
|--------|-------|
| **Total Return** | +15.23% |
| **Sharpe Ratio** | 1.45 |
| **Maximum Drawdown** | -12.45% |
| **Recovery Status** | ✓ Recovered |
```

**2. Performance Analysis**

Narrative interpretation based on metrics:
- Positive/negative return assessment
- Sharpe ratio evaluation
- Risk-adjusted performance commentary

**3. Visual Analytics**

Embedded charts showing:
- Portfolio value evolution
- Drawdown magnitude and duration

**4. Detailed Metrics**

Complete statistics including:
- Number of periods
- Starting and ending values
- Peak and trough values
- Drawdown recovery information

**5. Conclusion**

Overall assessment considering:
- Return magnitude
- Risk metrics
- Recovery capability
- Suitability for different investor profiles

---

## Advanced Analytics

### Additional Metrics You Can Calculate

#### Win Rate

```python
def calculate_win_rate(orders: List[Order]) -> dict:
    """Calculate percentage of profitable trades."""
    # Separate buy and sell orders
    buys = [o for o in orders if o.quantity > 0 and o.status == 'success']
    sells = [o for o in orders if o.quantity < 0 and o.status == 'success']
    
    # Match buys with sells to identify complete trades
    trades = []
    for sell in sells:
        # Find corresponding buy
        for buy in buys:
            if buy.symbol == sell.symbol:
                pnl = (sell.price - buy.price) * abs(sell.quantity)
                trades.append(pnl)
                break
    
    if not trades:
        return {'win_rate': 0, 'avg_win': 0, 'avg_loss': 0}
    
    wins = [t for t in trades if t > 0]
    losses = [t for t in trades if t < 0]
    
    return {
        'win_rate': len(wins) / len(trades) if trades else 0,
        'num_wins': len(wins),
        'num_losses': len(losses),
        'avg_win': sum(wins) / len(wins) if wins else 0,
        'avg_loss': sum(losses) / len(losses) if losses else 0,
        'total_pnl': sum(trades)
    }
```

#### Sortino Ratio

```python
def calc_sortino_ratio(value: list, target_return: float = 0) -> float:
    """
    Calculate Sortino ratio (downside deviation).
    Better than Sharpe for asymmetric returns.
    """
    s = pl.Series('value', value)
    returns = s.pct_change().drop_nulls()
    
    excess_return = returns.mean() - target_return
    
    # Only consider downside volatility
    downside_returns = returns.filter(returns < target_return)
    downside_deviation = downside_returns.std() if len(downside_returns) > 0 else 0
    
    return excess_return / downside_deviation if downside_deviation > 0 else float('inf')
```

#### Calmar Ratio

```python
def calc_calmar_ratio(value: list, time: list) -> float:
    """
    Calculate Calmar ratio (return / max drawdown).
    Higher is better.
    """
    total_ret = total_return(value)
    max_dd_info = calc_max_dd(time, value)
    max_dd = abs(max_dd_info['max_drawdown'])
    
    if max_dd == 0:
        return float('inf')
    
    # Annualize return
    days = (time[-1] - time[0]).days
    annualized_return = (1 + total_ret) ** (365 / days) - 1 if days > 0 else 0
    
    return annualized_return / max_dd
```

---

## Custom Metrics

### Creating Your Own Metrics

Template for custom metric functions:

```python
def calc_custom_metric(time: list, value: list, **kwargs) -> float:
    """
    Calculate custom metric.
    
    Args:
        time: List of timestamps
        value: List of portfolio values
        **kwargs: Additional parameters
        
    Returns:
        Calculated metric value
    """
    # Convert to Polars if needed
    df = pl.DataFrame({'time': time, 'value': value})
    
    # Perform calculations
    # ...
    
    return result
```

### Example: Rolling Volatility

```python
def calc_rolling_volatility(value: list, window: int = 20) -> list:
    """
    Calculate rolling volatility over specified window.
    
    Args:
        value: Portfolio values
        window: Rolling window size
        
    Returns:
        List of rolling volatility values
    """
    s = pl.Series('value', value)
    returns = s.pct_change().drop_nulls()
    
    rolling_vol = []
    for i in range(window, len(returns)):
        window_returns = returns[i-window:i]
        vol = window_returns.std()
        rolling_vol.append(vol)
    
    return rolling_vol
```

### Integrating Custom Metrics

```python
# In generate_report function
report = {
    'name': name,
    'ttl_return': total_return(value),
    'sharpe': calc_sharpe(value),
    'sortino': calc_sortino_ratio(value),  # Add custom metric
    'calmar': calc_calmar_ratio(value, time),  # Add custom metric
    'max_dd': calc_max_dd(time, value),
    'win_rate': calculate_win_rate(states[name].orders)  # Add custom metric
}
```

---

## Interpretation Guide

### Comprehensive Strategy Evaluation

#### Step 1: Returns Analysis

```python
total_ret = report['ttl_return'] * 100

if total_ret > 15:
    print("✓ Excellent returns")
elif total_ret > 8:
    print("✓ Good returns")
elif total_ret > 0:
    print("○ Modest returns")
else:
    print("✗ Negative returns - strategy needs work")
```

#### Step 2: Risk Assessment

```python
sharpe = report['sharpe']
max_dd = abs(report['max_dd']['max_drawdown']) * 100

# Risk-adjusted performance
if sharpe > 1 and max_dd < 15:
    print("✓ Excellent risk-adjusted returns")
elif sharpe > 0.5 and max_dd < 25:
    print("○ Acceptable risk profile")
else:
    print("✗ Poor risk-adjusted returns")
```

#### Step 3: Recovery Analysis

```python
dd_info = report['max_dd']

if dd_info['recover'] is not None:
    duration = dd_info['duration']
    print(f"✓ Portfolio recovered in {duration}")
    
    if duration.days < 30:
        print("  → Quick recovery (resilient)")
    elif duration.days < 90:
        print("  → Moderate recovery time")
    else:
        print("  → Slow recovery (concerning)")
else:
    print("✗ Portfolio never recovered - major red flag")
```

#### Step 4: Overall Rating

```python
def rate_strategy(report: dict) -> str:
    """
    Provide overall rating based on multiple factors.
    
    Returns: 'Excellent', 'Good', 'Fair', 'Poor'
    """
    total_ret = report['ttl_return']
    sharpe = report['sharpe']
    max_dd = abs(report['max_dd']['max_drawdown'])
    recovered = report['max_dd']['recover'] is not None
    
    # Excellent: High returns, good Sharpe, low drawdown, recovered
    if total_ret > 0.15 and sharpe > 1.5 and max_dd < 0.15 and recovered:
        return 'Excellent'
    
    # Good: Positive returns, decent Sharpe, moderate drawdown
    elif total_ret > 0.08 and sharpe > 1.0 and max_dd < 0.25 and recovered:
        return 'Good'
    
    # Fair: Positive returns but concerning risk metrics
    elif total_ret > 0 and sharpe > 0:
        return 'Fair'
    
    # Poor: Negative returns or terrible risk metrics
    else:
        return 'Poor'

rating = rate_strategy(report)
print(f"Overall Strategy Rating: {rating}")
```

---

## Complete Usage Example

```python
from pathlib import Path
from engine import ExecutionEngine
from strategies import MACDStrategy, MomentumStrategy
from data_loader import data_ingestor
from reporting import generate_report, calc_sharpe, calc_max_dd, total_return

# Run backtest
ticks = data_ingestor('market_data.csv')
strategies = [
    MACDStrategy(ticks, {'short_period': 12, 'long_period': 26}),
    MomentumStrategy(ticks, {'lookback': 20, 'buy_threshold': 0.02, 'sell_threshold': -0.02})
]

engine = ExecutionEngine(ticks, strategies, init_cash=1_000_000)
states = engine.run()

# Generate standard reports
generate_report(
    names=states.keys(),
    states=states,
    img_dir=Path('output/images'),
    doc_dir=Path('output/reports')
)

# Additional analysis
for name, state in states.items():
    time, value = zip(*state.history)
    
    print(f"\n{name} Analysis:")
    print("=" * 60)
    
    # Basic metrics
    total_ret = total_return(value) * 100
    sharpe = calc_sharpe(value)
    dd_info = calc_max_dd(time, value)
    max_dd = abs(dd_info['max_drawdown']) * 100
    
    print(f"Total Return: {total_ret:+.2f}%")
    print(f"Sharpe Ratio: {sharpe:.2f}")
    print(f"Max Drawdown: {max_dd:.2f}%")
    
    # Recovery analysis
    if dd_info['recover']:
        print(f"Recovery Time: {dd_info['duration']}")
        print("Status: ✓ Recovered")
    else:
        print("Status: ✗ Never recovered")
    
    # Orders analysis
    successful_orders = sum(1 for o in state.orders if o.status == 'success')
    failed_orders = sum(1 for o in state.orders if o.status == 'failed')
    
    print(f"\nOrder Statistics:")
    print(f"  Successful: {successful_orders}")
    print(f"  Failed: {failed_orders}")
    print(f"  Success Rate: {successful_orders/len(state.orders)*100:.1f}%")
    
    # Final assessment
    rating = rate_strategy({
        'ttl_return': total_ret / 100,
        'sharpe': sharpe,
        'max_dd': dd_info
    })
    print(f"\n{'='*60}")
    print(f"Overall Rating: {rating}")
    print(f"{'='*60}")
```

---

## Summary

### Key Takeaways

1. **Multiple Metrics**: Use total return, Sharpe ratio, and max drawdown together
2. **Visual Analysis**: Charts reveal patterns not visible in numbers alone
3. **Recovery Matters**: Drawdown recovery is as important as magnitude
4. **Context is Key**: Interpret metrics relative to market conditions and goals
5. **Comprehensive Reports**: Generated markdown provides complete documentation

### Best Practices

- Always calculate multiple metrics, never rely on one
- Review both charts and tables
- Compare strategies using same metrics
- Consider risk alongside returns
- Document assumptions and limitations

### Next Steps

- Review generated reports in the `doc/` directory
- Compare multiple strategy configurations
- Create custom metrics for specific needs
- See **[Developer Guide](DEVELOPER_GUIDE.md)** for custom metric implementation

---

*Effective performance analysis requires understanding both the numbers and what they mean in context. Use these tools to make informed decisions about strategy viability.*
