# API Reference

Complete reference documentation for all classes, methods, and functions in the Trading Backtesting System.

## Table of Contents

- [models.py](#modelspy)
- [strategies.py](#strategiespy)
- [engine.py](#enginepy)
- [reporting.py](#reportingpy)
- [main.py](#mainpy)

---

## models.py

### Order

**Description**: Dataclass representing a trading order.

```python
@dataclass
class Order:
    symbol: str
    quantity: int
    price: float
    status: str
```

**Attributes**:

| Attribute | Type | Description |
|-----------|------|-------------|
| `symbol` | str | Ticker symbol of the security |
| `quantity` | int | Number of shares (positive for buy, negative for sell) |
| `price` | float | Price per share |
| `status` | str | Order status: 'pending', 'filled', 'rejected', 'success', 'failed' |

**Methods**:

#### `__post_init__()`

Automatically called after initialization to validate the order.

**Raises**:
- `OrderError`: If price is less than or equal to zero

**Example**:
```python
# Valid order
order = Order('AAPL', 100, 150.50, 'pending')

# Invalid - raises OrderError
order = Order('AAPL', 100, -10.0, 'pending')
```

---

### Position

**Description**: Dataclass representing a position in a security.

```python
@dataclass
class Position:
    symbol: str
    quantity: int = 0
    avg_price: float = 0.0
```

**Attributes**:

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `symbol` | str | (required) | Ticker symbol |
| `quantity` | int | 0 | Number of shares held |
| `avg_price` | float | 0.0 | Average cost per share |

**Example**:
```python
# Empty position
pos = Position('AAPL')

# Position with holdings
pos = Position('AAPL', quantity=100, avg_price=150.0)
```

---

### Portfolio

**Description**: Manages cash balance and positions across multiple securities.

```python
class Portfolio:
    def __init__(self, init_cash: float, symbols: list)
```

**Constructor Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `init_cash` | float | Initial cash balance |
| `symbols` | list | List of ticker symbols to track |

**Attributes**:

| Attribute | Type | Description |
|-----------|------|-------------|
| `cash` | float | Current cash balance |
| `positions` | Dict[str, Position] | Dictionary mapping symbols to Position objects |

#### Methods

##### `update_position(symbol: str, qty: int, price: float) -> None`

Updates a position after a trade execution.

**Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | str | Ticker symbol |
| `qty` | int | Quantity traded (positive=buy, negative=sell) |
| `price` | float | Execution price per share |

**Behavior**:
- For buys (qty > 0): Calculates weighted average price
- For sells (qty < 0): Maintains existing average price
- Updates position quantity
- Adjusts cash balance

**Formula**:
```
new_avg_price = (old_avg_price × old_qty + price × qty) / (old_qty + qty)
cash_change = -qty × price
```

**Example**:
```python
portfolio = Portfolio(100000, ['AAPL'])
portfolio.update_position('AAPL', 100, 150.0)  # Buy 100 @ $150
# Cash: 100000 - 15000 = 85000
# Position: 100 shares @ $150 avg
```

##### `get_value(price_dict: Dict[str, float]) -> float`

Calculates total portfolio value.

**Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `price_dict` | Dict[str, float] | Current market prices for all symbols |

**Returns**: `float` - Total portfolio value (cash + positions)

**Formula**:
```
value = cash + Σ(position_qty × current_price)
```

**Example**:
```python
prices = {'AAPL': 160.0, 'GOOGL': 2850.0}
value = portfolio.get_value(prices)
```

---

### Exceptions

#### OrderError

```python
class OrderError(Exception):
    pass
```

Raised when order validation fails (invalid parameters, insufficient cash, insufficient shares).

#### ExecutionError

```python
class ExecutionError(Exception):
    pass
```

Raised when order execution fails (market rejection, system errors).

#### ConfigError

```python
class ConfigError(Exception):
    pass
```

Raised when strategy configuration is invalid (missing parameters, wrong types).

---

## strategies.py

### Strategy (Abstract Base Class)

**Description**: Blueprint for all trading strategies.

```python
class Strategy(ABC):
    @abstractmethod
    def generate_signals(self, tick: MarketDataPoint) -> list:
        pass
```

#### Methods

##### `generate_signals(tick: MarketDataPoint) -> list` (abstract)

Generates a trading signal based on current market data.

**Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `tick` | MarketDataPoint | Current market data point |

**Returns**: `list` - Signal in format `[action, symbol, quantity, price]`

**Signal Format**:
- `action`: str - 'Buy', 'Sell', or 'Hold'
- `symbol`: str - Ticker symbol
- `quantity`: int - Number of shares
- `price`: float - Order price

**Must be implemented by all concrete strategies.**

---

### StrategyState

**Description**: Dataclass holding the complete state of a strategy during backtesting.

```python
@dataclass
class StrategyState:
    strategy: Strategy
    portfolio: Portfolio
    orders: List[Order]
    order_errors: List[str]
    execution_errors: List[str]
    history: List[Tuple[datetime, float]]
```

**Attributes**:

| Attribute | Type | Description |
|-----------|------|-------------|
| `strategy` | Strategy | The strategy instance |
| `portfolio` | Portfolio | Strategy's portfolio |
| `orders` | List[Order] | All orders created |
| `order_errors` | List[str] | Order validation errors |
| `execution_errors` | List[str] | Execution failures |
| `history` | List[Tuple[datetime, float]] | Time-series of portfolio values |

---

### MACDStrategy

**Description**: Moving Average Convergence Divergence crossover strategy.

```python
class MACDStrategy(Strategy):
    def __init__(self, ticks: List[MarketDataPoint], params: dict)
```

**Constructor Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `ticks` | List[MarketDataPoint] | Historical market data |
| `params` | dict | Strategy parameters |

**Required Parameters** (in `params` dict):

| Key | Type | Description |
|-----|------|-------------|
| `short_period` | int | Short-term moving average period |
| `long_period` | int | Long-term moving average period |

**Raises**:
- `ConfigError`: Missing parameters
- `TypeError`: Non-integer periods
- `ValueError`: Short period >= long period

**Trading Logic**:
- When short MA > long MA → Buy signal
- When short MA < long MA → Sell signal
- Otherwise → Hold

**Internal Attributes**:

| Attribute | Type | Description |
|-----------|------|-------------|
| `_short_period` | int | Short MA window |
| `_long_period` | int | Long MA window |
| `_prices` | deque | Rolling price window |
| `_short_ma` | list | Historical short MA values |
| `_long_ma` | list | Historical long MA values |

**Methods**:

##### `__repr__() -> str`

Returns string representation of strategy.

**Returns**: `str` - Format: `"MACD_{short}_{long}"`

##### `generate_signals(tick: MarketDataPoint) -> list`

Generates trading signals based on MA crossover.

**Parameters**:
- `tick`: Current market data point

**Returns**: Signal list `[action, symbol, 100, price]`

**Example**:
```python
strategy = MACDStrategy(
    ticks=market_data,
    params={'short_period': 12, 'long_period': 26}
)
signal = strategy.generate_signals(tick)
# Example output: ['Buy', 'AAPL', 100, 150.50]
```

---

### MomentumStrategy

**Description**: Rate of change momentum strategy.

```python
class MomentumStrategy(Strategy):
    def __init__(self, ticks: List[MarketDataPoint], params: dict)
```

**Constructor Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `ticks` | List[MarketDataPoint] | Historical market data |
| `params` | dict | Strategy parameters |

**Required Parameters** (in `params` dict):

| Key | Type | Description |
|-----|------|-------------|
| `lookback` | int | Lookback period for ROC calculation |
| `buy_threshold` | float | ROC threshold to trigger buy (e.g., 0.02 for 2%) |
| `sell_threshold` | float | ROC threshold to trigger sell (e.g., -0.02 for -2%) |

**Raises**:
- `ConfigError`: Missing parameters
- `TypeError`: Invalid parameter types
- `ZeroDivisionError`: Invalid price data (zero price)

**Trading Logic**:
- Calculate ROC = (current_price / price_N_days_ago) - 1
- If ROC > buy_threshold → Buy signal
- If ROC < sell_threshold → Sell signal
- Otherwise → Hold

**Internal Attributes**:

| Attribute | Type | Description |
|-----------|------|-------------|
| `_lookback` | int | Lookback period |
| `_buy_threshold` | float | Buy trigger threshold |
| `_sell_threshold` | float | Sell trigger threshold |
| `_prices` | deque | Rolling price window |
| `_roc` | list | Historical ROC values |

**Methods**:

##### `__repr__() -> str`

Returns string representation.

**Returns**: `str` - Format: `"Momentum_{lookback}_{buy_threshold}_{sell_threshold}"`

##### `generate_signals(tick: MarketDataPoint) -> list`

Generates signals based on price momentum.

**Parameters**:
- `tick`: Current market data point

**Returns**: Signal list `[action, symbol, 100, price]`

**Example**:
```python
strategy = MomentumStrategy(
    ticks=market_data,
    params={
        'lookback': 20,
        'buy_threshold': 0.02,
        'sell_threshold': -0.02
    }
)
signal = strategy.generate_signals(tick)
```

---

## engine.py

### ExecutionEngine

**Description**: Orchestrates backtesting by processing market data, generating signals, and executing orders.

```python
class ExecutionEngine:
    def __init__(
        self,
        ticks: List[MarketDataPoint],
        strategies: List[Strategy],
        init_cash: float,
        allow_short: bool = False
    ) -> None
```

**Constructor Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ticks` | List[MarketDataPoint] | (required) | Market data time series |
| `strategies` | List[Strategy] | (required) | List of strategies to backtest |
| `init_cash` | float | (required) | Initial cash for each strategy |
| `allow_short` | bool | False | Whether to allow short selling (not implemented) |

**Internal Attributes**:

| Attribute | Type | Description |
|-----------|------|-------------|
| `_states` | Dict[str, StrategyState] | Strategy states by name |
| `_ticks` | List[MarketDataPoint] | Sorted market data |
| `_strategies` | List[Strategy] | Strategy instances |
| `_symbols` | list | Unique symbols from data |

**Methods**:

##### `create_order(name: str, signal: list) -> Order`

Creates and validates an order from a strategy signal.

**Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | str | Strategy name |
| `signal` | list | Signal in format `[action, symbol, qty, price]` |

**Returns**: `Order` - Validated order object

**Raises**:
- `OrderError`: If signal format invalid, insufficient shares for sell, or insufficient cash for buy

**Validation Checks**:
1. Signal has exactly 4 elements
2. Action is 'Buy', 'Sell', or 'Hold'
3. For sells: Position quantity >= sell quantity
4. For buys: Cash >= purchase cost

**Example**:
```python
signal = ['Buy', 'AAPL', 100, 150.0]
order = engine.create_order('MACD_12_26', signal)
```

##### `execute_order(name: str, order: Order) -> None`

Executes a validated order by updating the portfolio.

**Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | str | Strategy name |
| `order` | Order | Order to execute |

**Raises**:
- `ExecutionError`: Random 1% execution failure simulation

**Side Effects**:
- Updates portfolio position
- Updates portfolio cash

**Example**:
```python
engine.execute_order('MACD_12_26', order)
```

##### `run() -> dict`

Executes the complete backtesting simulation.

**Returns**: `Dict[str, StrategyState]` - Final states for all strategies

**Process**:
1. Initialize price tracking
2. Iterate through ticks in chronological order
3. For each tick and strategy:
   - Generate signal
   - Create order (log errors if validation fails)
   - Execute order (log errors if execution fails)
   - Record portfolio value
4. Return all strategy states

**Example**:
```python
engine = ExecutionEngine(ticks, strategies, 1_000_000)
states = engine.run()

# Access results
for name, state in states.items():
    print(f"{name}: {len(state.orders)} orders")
    print(f"Final value: {state.history[-1][1]}")
```

---

## reporting.py

### Data Processing Functions

##### `value_tbl(time: list, value: list) -> pl.LazyFrame`

Creates a Polars LazyFrame from time and value lists.

**Parameters**:
- `time`: List of timestamps
- `value`: List of portfolio values

**Returns**: `pl.LazyFrame` with columns ['time', 'value']

##### `period_returns(time: list, value: list) -> pl.LazyFrame`

Calculates period-by-period percentage returns.

**Parameters**:
- `time`: List of timestamps
- `value`: List of portfolio values

**Returns**: `pl.LazyFrame` with columns ['time', 'value', 'returns']

---

### Metrics Functions

##### `total_return(value: list) -> float`

Calculates total return over the entire period.

**Parameters**:
- `value`: List of portfolio values

**Returns**: `float` - Total return as decimal (e.g., 0.15 = 15%)

**Formula**: `(final_value / initial_value) - 1`

**Example**:
```python
values = [1000, 1050, 1100, 1080]
ret = total_return(values)  # 0.08 (8%)
```

##### `calc_sharpe(value: list, risk_free: float = 0) -> float`

Calculates Sharpe ratio for risk-adjusted returns.

**Parameters**:
- `value`: List of portfolio values
- `risk_free`: Risk-free rate (default: 0)

**Returns**: `float` - Sharpe ratio

**Formula**: `(mean_return - risk_free) / std_dev_returns`

**Example**:
```python
sharpe = calc_sharpe(values, risk_free=0.0)
```

##### `calc_max_dd(time: list, value: list) -> dict`

Calculates maximum drawdown and related metrics.

**Parameters**:
- `time`: List of timestamps
- `value`: List of portfolio values

**Returns**: `dict` with keys:

| Key | Type | Description |
|-----|------|-------------|
| `max_drawdown` | float | Maximum drawdown as decimal |
| `peak` | datetime | Timestamp of peak before drawdown |
| `bottom` | datetime | Timestamp of lowest point |
| `recover` | datetime or None | Recovery timestamp (None if not recovered) |
| `duration` | timedelta or None | Time to recover (None if not recovered) |
| `drawdown` | pl.LazyFrame | Complete drawdown time series |

**Example**:
```python
dd_info = calc_max_dd(times, values)
print(f"Max DD: {dd_info['max_drawdown']*100:.2f}%")
print(f"Recovery: {dd_info['recover']}")
```

---

### Visualization Functions

##### `plot_portfolio_value(report: dict, output_path: Path)`

Generates equity curve plot.

**Parameters**:
- `report`: Dictionary containing 'prd_return' LazyFrame and 'name'
- `output_path`: Path to save PNG file

**Output**: PNG file with normalized portfolio value over time

##### `plot_drawdown(report: dict, output_path: Path)`

Generates drawdown plot.

**Parameters**:
- `report`: Dictionary containing 'max_dd' info and 'name'
- `output_path`: Path to save PNG file

**Output**: PNG file with drawdown percentage over time

---

### Report Generation

##### `generate_report(names, states, img_dir: Path, doc_dir: Path)`

Generates complete performance reports for all strategies.

**Parameters**:
- `names`: Strategy names (keys from states dict)
- `states`: Dictionary of StrategyState objects
- `img_dir`: Directory to save charts
- `doc_dir`: Directory to save markdown reports

**Generates**:
- `{img_dir}/pnl_{name}.png` - Equity curve
- `{img_dir}/drawdown_{name}.png` - Drawdown chart
- `{doc_dir}/performance_{name}.md` - Markdown report

##### `write_markdown_report(report: dict, pnl_path: Path, drawdown_path: Path, output_path: Path)`

Writes a detailed markdown performance report.

**Parameters**:
- `report`: Metrics dictionary
- `pnl_path`: Path to equity curve image
- `drawdown_path`: Path to drawdown image
- `output_path`: Path to save markdown file

**Report Sections**:
1. Executive Summary (metrics table)
2. Performance Analysis (narrative)
3. Portfolio Value Chart
4. Drawdown Analysis
5. Key Statistics
6. Conclusion

---

## main.py

### main()

**Description**: Entry point for running backtests.

**Configuration Structure**:
```python
config = {
    'init_cash': float,  # Initial cash per strategy
    'strategies': [
        {
            'type': Strategy class,  # Class reference
            'params': dict  # Strategy parameters
        }
    ]
}
```

**Workflow**:
1. Load configuration
2. Load market data from CSV
3. Instantiate strategies
4. Create execution engine
5. Run backtest
6. Generate reports

**Example**:
```python
if __name__ == '__main__':
    main()
```

---

## Type Definitions

### MarketDataPoint

(Defined in `data_loader.py`, not shown)

```python
@dataclass
class MarketDataPoint:
    timestamp: datetime
    symbol: str
    price: float
```

---

## Constants and Defaults

| Constant | Value | Description |
|----------|-------|-------------|
| Execution failure rate | 1% | Random order rejection probability |
| Default order quantity | 100 | Fixed lot size for all orders |
| Risk-free rate | 0 | Default for Sharpe ratio calculation |

---

*For usage examples and tutorials, see the Developer Guide.*
