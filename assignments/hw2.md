# Multi-Signal Strategy Simulation on S&P 500

Due: Sat Oct 4, 2025

**Duration:** ~6 hours

**Module:** Signal Engineering, Execution Modeling & Backtesting

**Objective:** Design, implement, and evaluate multiple technical indicators across a large equity universe using object-oriented Python, with attention to execution speed and capital constraints.

## Task Overview

You will build a modular trading simulator that:

- Downloads daily adjusted close prices for all S&P 500 tickers (2005–2025)
- Simulates three strategies:
  - **Benchmark Strategy** (static long)
  - **Four technical indicator strategies**
- Tracks trades, holdings, cash, and total portfolio value
- Starts with **\$1,000,000** in cash
- Considers **execution speed** (measure performance using timer functions)

## Part 1: Data Acquisition (1 hour)

### Task

- Use `yfinance` to download daily adjusted close prices for all S&P 500 tickers (use the list of S&P 500 tickers from today; do not go back point-in-time, as some tickers won't match historical data)
- **Time range:** January 1, 2005 to January 1, 2025
- Store data locally (one file per ticker) — use parquet for efficiency, but CSV also works
- Implement a `PriceLoader` class to manage access

### Hints

- Respect API limits with batching (yfinance API has rate limits; batch requests to avoid hitting the limit)
- Drop tickers with sparse or missing data
- Use any libraries you prefer

## Part 2: Benchmark Strategy (0.5 hour)

### Strategy

- Buy X shares of each ticker on the first day (read addendum 1 at the end of this statement)
- No further trades
- Track portfolio value over time

### Constraints

- Initial cash: **\$1,000,000**
- If insufficient cash, skip purchase
- No shorting, no leverage

## Part 3: Technical Indicator Strategies (3 hours)

Implement four strategies, each in its own `.py` file, inheriting from a common `Strategy` base class.

| Strategy Name | Signal Logic | Category |
|---------------|--------------|----------|
| `MovingAverageStrategy` | Buy if 20-day MA > 50-day MA | Price average |
| `VolatilityBreakoutStrategy` | Buy if daily return > rolling 20-day std dev | Volatility |
| `MACDStrategy` | Buy if MACD line crosses above signal line | Price + momentum |
| `RSIStrategy` | Buy if RSI < 30 (oversold) | Oscillator |

### Constraints

- No short positions
- Only 1 share per buy signal
- Act on previous day's signal
- Initial cash: **\$1,000,000**
- Track holdings, cash, and total assets

## Part 4: Result Presentation (1.5 hours)

### Notebook: `StrategyComparison.ipynb`

#### Tasks

- Load results from all strategies
- Plot:
  - Signal overlay on price chart
  - Holdings over time
  - Cash balance
  - Total portfolio value
- Compare cumulative P&L across strategies
- Reflect on signal behavior, execution constraints, and performance

#### Required Charts

- 📈 Signal overlay with buy markers
- 📊 Holdings, cash, and total assets over time
- 📉 Cumulative P&L comparison

## Submission Checklist

- [ ] `PriceLoader.py`
- [ ] `BenchmarkStrategy.py`
- [ ] Four strategy `.py` files
- [ ] `StrategyComparison.ipynb`
- [ ] All plots and final summary

## Bonus Challenges (Optional)

- Add transaction costs
- Compute Sharpe ratio, drawdown

## Addendum 1: Execution Guidelines

When you choose X shares to place an order, try not to impact the market. If you prefer using a fixed amount, that also works.

### 1. Participation Rate

**Definition:** Your volume as a percentage of total market volume for the asset on that day.

**Rule:**

- Stay below **10% of ADV** for low-impact execution
- **1–5%** is considered safe for stealth trading
- Above **15–20%** risks noticeable price impact and slippage

### 2. Dollar Volume Threshold

**For large-cap stocks like AAPL or MSFT:**

- You can often trade **millions of dollars per day** without impact

**For small/mid-cap stocks:**

- Even **\$100K–\$500K** can move the market if liquidity is thin

**No further trades**

**Track portfolio value over time**