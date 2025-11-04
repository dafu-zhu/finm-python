# Developer Guide

A comprehensive guide for developers looking to extend, customize, or contribute to the Trading Backtesting System.

## Table of Contents

- [Getting Started](#getting-started)
- [Creating Custom Strategies](#creating-custom-strategies)
- [Extending the Data Model](#extending-the-data-model)
- [Adding New Metrics](#adding-new-metrics)
- [Custom Visualizations](#custom-visualizations)
- [Testing](#testing)
- [Best Practices](#best-practices)
- [Common Patterns](#common-patterns)
- [Troubleshooting](#troubleshooting)

---

## Getting Started

### Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd trading-backtest

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt --break-system-packages

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy --break-system-packages
```

### Project Structure

```
src/pyquant/hw1/
├── models.py           # Core data structures
├── strategies.py       # Strategy implementations
├── engine.py           # Backtesting engine
├── reporting.py        # Analytics and reporting
├── data_loader.py      # Data ingestion
└── main.py            # Application entry point

tests/
├── test_models.py
├── test_strategies.py
├── test_engine.py
└── test_reporting.py

docs/
├── README.md
├── API_REFERENCE.md
└── DEVELOPER_GUIDE.md
```

### Running the System

```bash
# Run backtest
python -m src.pyquant.hw1.main

# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/
```

---

## Creating Custom Strategies

### Basic Strategy Template

```python
from strategies import Strategy
from data_loader import MarketDataPoint
from models import ConfigError

class MyCustomStrategy(Strategy):
    """
    Brief description of your strategy.
    
    Trading Logic:
    - Describe when to buy
    - Describe when to sell
    - Describe when to hold
    """
    
    def __init__(self, ticks: List[MarketDataPoint], params: dict):
        """
        Initialize strategy with parameters.
        
        Required params:
        - param1 (type): Description
        - param2 (type): Description
        """
        # Validate parameters
        try:
            self._param1 = params['param1']
            self._param2 = params['param2']
        except KeyError as e:
            raise ConfigError(f"Missing parameter: {e}") from e
        
        # Type checking
        if not isinstance(self._param1, expected_type):
            raise TypeError(f"param1 must be {expected_type}")
        
        # Value validation
        if self._param1 <= 0:
            raise ValueError("param1 must be positive")
        
        # Initialize state
        self._ticks = ticks
        self._indicator_buffer = []
    
    def __repr__(self) -> str:
        """Return unique strategy identifier."""
        return f"MyCustomStrategy_{self._param1}_{self._param2}"
    
    def generate_signals(self, tick: MarketDataPoint) -> list:
        """
        Generate trading signal based on current market data.
        
        Args:
            tick: Current market data point
            
        Returns:
            Signal list: [action, symbol, quantity, price]
            - action: 'Buy', 'Sell', or 'Hold'
            - symbol: str
            - quantity: int (fixed at 100)
            - price: float
        """
        symbol = tick.symbol
        price = tick.price
        
        # Update indicators
        self._update_indicators(price)
        
        # Generate signal logic
        if self._should_buy():
            return ['Buy', symbol, 100, price]
        elif self._should_sell():
            return ['Sell', symbol, 100, price]
        else:
            return ['Hold', symbol, 100, price]
    
    def _update_indicators(self, price: float) -> None:
        """Update internal indicators (helper method)."""
        # Implementation
        pass
    
    def _should_buy(self) -> bool:
        """Determine if buy conditions are met."""
        # Implementation
        return False
    
    def _should_sell(self) -> bool:
        """Determine if sell conditions are met."""
        # Implementation
        return False
```

### Example: RSI Strategy

```python
from collections import deque

class RSIStrategy(Strategy):
    """
    Relative Strength Index strategy.
    
    Trading Logic:
    - Buy when RSI < oversold_threshold (e.g., 30)
    - Sell when RSI > overbought_threshold (e.g., 70)
    """
    
    def __init__(self, ticks: List[MarketDataPoint], params: dict):
        try:
            self._period = params['period']
            self._oversold = params['oversold_threshold']
            self._overbought = params['overbought_threshold']
        except KeyError as e:
            raise ConfigError(f"Missing parameter: {e}") from e
        
        # Validation
        if not isinstance(self._period, int) or self._period < 2:
            raise ValueError("Period must be integer >= 2")
        
        if not (0 < self._oversold < self._overbought < 100):
            raise ValueError("Thresholds must satisfy: 0 < oversold < overbought < 100")
        
        self._ticks = ticks
        self._prices = deque(maxlen=self._period + 1)
        self._rsi_history = []
    
    def __repr__(self) -> str:
        return f"RSI_{self._period}_{self._oversold}_{self._overbought}"
    
    def generate_signals(self, tick: MarketDataPoint) -> list:
        symbol = tick.symbol
        price = tick.price
        
        # Update price buffer
        self._prices.append(price)
        
        # Need at least period+1 prices to calculate RSI
        if len(self._prices) < self._period + 1:
            return ['Hold', symbol, 100, price]
        
        # Calculate RSI
        rsi = self._calculate_rsi()
        self._rsi_history.append(rsi)
        
        # Generate signals
        if rsi < self._oversold:
            return ['Buy', symbol, 100, price]
        elif rsi > self._overbought:
            return ['Sell', symbol, 100, price]
        else:
            return ['Hold', symbol, 100, price]
    
    def _calculate_rsi(self) -> float:
        """Calculate RSI from price changes."""
        prices = list(self._prices)
        changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        gains = [max(0, change) for change in changes]
        losses = [abs(min(0, change)) for change in changes]
        
        avg_gain = sum(gains[-self._period:]) / self._period
        avg_loss = sum(losses[-self._period:]) / self._period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
```

### Strategy Testing

```python
# test_custom_strategy.py
import pytest
from datetime import datetime
from strategies import RSIStrategy
from data_loader import MarketDataPoint
from models import ConfigError

def test_rsi_initialization():
    """Test RSI strategy initialization."""
    ticks = []  # Empty for initialization test
    params = {
        'period': 14,
        'oversold_threshold': 30,
        'overbought_threshold': 70
    }
    
    strategy = RSIStrategy(ticks, params)
    assert strategy._period == 14
    assert strategy._oversold == 30

def test_rsi_missing_params():
    """Test that missing parameters raise ConfigError."""
    with pytest.raises(ConfigError):
        RSIStrategy([], {'period': 14})  # Missing thresholds

def test_rsi_signal_generation():
    """Test signal generation logic."""
    # Create mock data
    ticks = [
        MarketDataPoint(datetime.now(), 'AAPL', 100 + i)
        for i in range(20)
    ]
    
    params = {
        'period': 14,
        'oversold_threshold': 30,
        'overbought_threshold': 70
    }
    
    strategy = RSIStrategy(ticks, params)
    
    # Test signal format
    tick = MarketDataPoint(datetime.now(), 'AAPL', 150.0)
    signal = strategy.generate_signals(tick)
    
    assert len(signal) == 4
    assert signal[0] in ['Buy', 'Sell', 'Hold']
    assert signal[1] == 'AAPL'
    assert signal[2] == 100
    assert signal[3] == 150.0
```

---

## Extending the Data Model

### Adding Order Types

Currently, the system only supports market orders. To add limit orders:

```python
# models.py
from enum import Enum

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

@dataclass
class Order:
    symbol: str
    quantity: int
    price: float
    status: str
    order_type: OrderType = OrderType.MARKET
    limit_price: float = None  # For limit orders
    stop_price: float = None   # For stop orders
    
    def __post_init__(self):
        if self.price <= 0:
            raise OrderError(f"Invalid price: {self.price}")
        
        # Validate limit order
        if self.order_type == OrderType.LIMIT:
            if self.limit_price is None or self.limit_price <= 0:
                raise OrderError("Limit orders require valid limit_price")
        
        # Validate stop order
        if self.order_type in [OrderType.STOP, OrderType.STOP_LIMIT]:
            if self.stop_price is None or self.stop_price <= 0:
                raise OrderError("Stop orders require valid stop_price")
```

### Adding Position Tracking

To track position entry time and P&L:

```python
@dataclass
class Position:
    symbol: str
    quantity: int = 0
    avg_price: float = 0.0
    entry_time: datetime = None
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    
    def calculate_unrealized_pnl(self, current_price: float) -> float:
        """Calculate unrealized P&L."""
        if self.quantity == 0:
            return 0.0
        self.unrealized_pnl = (current_price - self.avg_price) * self.quantity
        return self.unrealized_pnl
    
    def realize_pnl(self, quantity: int, exit_price: float) -> float:
        """Calculate realized P&L for a closed position."""
        pnl = (exit_price - self.avg_price) * quantity
        self.realized_pnl += pnl
        return pnl
```

---

## Adding New Metrics

### Creating Custom Metrics

```python
# reporting.py

def calc_sortino_ratio(value: list, risk_free: float = 0, target_return: float = 0) -> float:
    """
    Calculate Sortino ratio (downside deviation version of Sharpe).
    
    Args:
        value: Portfolio values over time
        risk_free: Risk-free rate
        target_return: Minimum acceptable return
        
    Returns:
        Sortino ratio
    """
    s = pl.Series('value', value)
    returns = s.pct_change().drop_nulls()
    
    # Calculate excess return
    excess_return = returns.mean() - risk_free
    
    # Calculate downside deviation
    downside_returns = returns.filter(returns < target_return)
    if len(downside_returns) == 0:
        return float('inf')
    
    downside_deviation = downside_returns.std()
    
    return excess_return / downside_deviation if downside_deviation > 0 else float('inf')


def calc_win_rate(orders: List[Order], positions: Dict[str, Position]) -> dict:
    """
    Calculate win rate and related statistics.
    
    Args:
        orders: List of executed orders
        positions: Final positions
        
    Returns:
        Dictionary with win rate metrics
    """
    trades = []
    
    # Pair buy and sell orders to identify completed trades
    for symbol in set(order.symbol for order in orders):
        symbol_orders = [o for o in orders if o.symbol == symbol]
        
        # Implementation of trade pairing logic
        # ...
    
    if not trades:
        return {'win_rate': 0, 'avg_win': 0, 'avg_loss': 0}
    
    wins = [t for t in trades if t > 0]
    losses = [t for t in trades if t < 0]
    
    return {
        'win_rate': len(wins) / len(trades) if trades else 0,
        'avg_win': sum(wins) / len(wins) if wins else 0,
        'avg_loss': sum(losses) / len(losses) if losses else 0,
        'profit_factor': abs(sum(wins) / sum(losses)) if losses and sum(losses) != 0 else float('inf')
    }


def calc_calmar_ratio(value: list, time: list) -> float:
    """
    Calculate Calmar ratio (annualized return / max drawdown).
    
    Args:
        value: Portfolio values
        time: Timestamps
        
    Returns:
        Calmar ratio
    """
    total_ret = total_return(value)
    max_dd_info = calc_max_dd(time, value)
    max_dd = abs(max_dd_info['max_drawdown'])
    
    if max_dd == 0:
        return float('inf')
    
    # Annualize return (assumes daily data)
    days = (time[-1] - time[0]).days
    annualized_return = (1 + total_ret) ** (365 / days) - 1 if days > 0 else 0
    
    return annualized_return / max_dd
```

### Integrating New Metrics into Reports

```python
# reporting.py - update generate_report function

def generate_report(names, states, img_dir: Path, doc_dir: Path):
    for name in names:
        time, value = zip(*states[name].history)
        max_dd = calc_max_dd(time, value)
        
        # Calculate all metrics
        report = {
            'name': name,
            'ttl_return': total_return(value),
            'prd_return': period_returns(time, value),
            'sharpe': calc_sharpe(value),
            'sortino': calc_sortino_ratio(value),  # New metric
            'calmar': calc_calmar_ratio(value, time),  # New metric
            'max_dd': max_dd,
            'win_rate': calc_win_rate(states[name].orders, states[name].portfolio.positions)  # New metric
        }
        
        # Generate visualizations and reports
        # ...
```

---

## Custom Visualizations

### Creating New Charts

```python
# reporting.py

def plot_rolling_sharpe(report: dict, output_path: Path, window: int = 20):
    """
    Plot rolling Sharpe ratio over time.
    
    Args:
        report: Dictionary with 'prd_return' LazyFrame
        output_path: Path to save plot
        window: Rolling window size
    """
    df = report['prd_return'].collect()
    
    # Calculate rolling Sharpe
    rolling_sharpe = []
    for i in range(window, len(df)):
        window_values = df['value'][i-window:i].to_list()
        sharpe = calc_sharpe(window_values)
        rolling_sharpe.append(sharpe)
    
    # Create plot
    fig, ax = plt.subplots(figsize=(12, 6))
    
    times = df['time'][window:]
    ax.plot(times, rolling_sharpe, linewidth=1.5, color='#2E86AB')
    
    # Formatting
    ax.axhline(y=0, color='gray', linestyle='--', linewidth=1)
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel(f'Rolling Sharpe Ratio ({window} period)', fontsize=12)
    ax.set_title(f'Rolling Sharpe Ratio - {report["name"]}', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_returns_distribution(report: dict, output_path: Path):
    """
    Plot histogram of returns distribution.
    
    Args:
        report: Dictionary with 'prd_return' LazyFrame
        output_path: Path to save plot
    """
    df = report['prd_return'].collect()
    returns = df['returns'] * 100  # Convert to percentage
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Histogram
    ax.hist(returns, bins=50, alpha=0.7, color='#2E86AB', edgecolor='black')
    
    # Add vertical line at mean
    mean_return = returns.mean()
    ax.axvline(x=mean_return, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_return:.2f}%')
    
    # Formatting
    ax.set_xlabel('Returns (%)', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title(f'Returns Distribution - {report["name"]}', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
```

---

## Testing

### Test Structure

```python
# tests/test_models.py

import pytest
from datetime import datetime
from models import Order, Position, Portfolio, OrderError

class TestOrder:
    """Test Order class functionality."""
    
    def test_valid_order(self):
        """Test creating a valid order."""
        order = Order('AAPL', 100, 150.0, 'pending')
        assert order.symbol == 'AAPL'
        assert order.quantity == 100
    
    def test_negative_price_raises_error(self):
        """Test that negative price raises OrderError."""
        with pytest.raises(OrderError):
            Order('AAPL', 100, -150.0, 'pending')
    
    def test_zero_price_raises_error(self):
        """Test that zero price raises OrderError."""
        with pytest.raises(OrderError):
            Order('AAPL', 100, 0.0, 'pending')


class TestPortfolio:
    """Test Portfolio class functionality."""
    
    @pytest.fixture
    def portfolio(self):
        """Create a test portfolio."""
        return Portfolio(100000, ['AAPL', 'GOOGL'])
    
    def test_initialization(self, portfolio):
        """Test portfolio initialization."""
        assert portfolio.cash == 100000
        assert 'AAPL' in portfolio.positions
        assert portfolio.positions['AAPL'].quantity == 0
    
    def test_buy_updates_position(self, portfolio):
        """Test buying updates position correctly."""
        portfolio.update_position('AAPL', 100, 150.0)
        
        assert portfolio.positions['AAPL'].quantity == 100
        assert portfolio.positions['AAPL'].avg_price == 150.0
        assert portfolio.cash == 85000  # 100000 - (100 * 150)
    
    def test_multiple_buys_average_price(self, portfolio):
        """Test that multiple buys calculate correct average."""
        portfolio.update_position('AAPL', 100, 150.0)
        portfolio.update_position('AAPL', 50, 160.0)
        
        expected_avg = (100 * 150 + 50 * 160) / 150
        assert portfolio.positions['AAPL'].quantity == 150
        assert abs(portfolio.positions['AAPL'].avg_price - expected_avg) < 0.01
    
    def test_sell_maintains_average_price(self, portfolio):
        """Test that selling maintains the average price."""
        portfolio.update_position('AAPL', 100, 150.0)
        initial_avg = portfolio.positions['AAPL'].avg_price
        
        portfolio.update_position('AAPL', -50, 160.0)
        
        assert portfolio.positions['AAPL'].quantity == 50
        assert portfolio.positions['AAPL'].avg_price == initial_avg
    
    def test_get_value(self, portfolio):
        """Test portfolio valuation."""
        portfolio.update_position('AAPL', 100, 150.0)
        portfolio.update_position('GOOGL', 10, 2800.0)
        
        prices = {'AAPL': 160.0, 'GOOGL': 2900.0}
        value = portfolio.get_value(prices)
        
        # Cash: 100000 - 15000 - 28000 = 57000
        # AAPL: 100 * 160 = 16000
        # GOOGL: 10 * 2900 = 29000
        # Total: 102000
        assert value == 102000
```

### Integration Tests

```python
# tests/test_integration.py

def test_full_backtest():
    """Test complete backtesting workflow."""
    # Create mock data
    ticks = create_mock_data(days=30)
    
    # Create strategy
    strategy = MACDStrategy(
        ticks=ticks,
        params={'short_period': 5, 'long_period': 10}
    )
    
    # Run backtest
    engine = ExecutionEngine(ticks, [strategy], 100000)
    states = engine.run()
    
    # Verify results
    assert len(states) == 1
    state = list(states.values())[0]
    
    # Should have executed some orders
    assert len(state.orders) > 0
    
    # Portfolio value should be tracked
    assert len(state.history) == len(ticks)
    
    # Final value should be reasonable
    final_value = state.history[-1][1]
    assert 50000 < final_value < 200000  # Within reasonable range
```

---

## Best Practices

### Code Style

1. **Follow PEP 8**: Use consistent naming and formatting
2. **Type Hints**: Always use type hints for function signatures
3. **Docstrings**: Document all public methods
4. **Comments**: Explain complex logic, not obvious code

### Error Handling

```python
# Good: Specific exceptions with context
try:
    order = create_order(signal)
except OrderError as e:
    logger.error(f"Order validation failed for {signal}: {e}")
    state.order_errors.append(f"{timestamp}: {e}")
    return None

# Bad: Generic exceptions
try:
    order = create_order(signal)
except Exception as e:
    print("Error:", e)
```

### Performance

```python
# Good: Use deque for sliding windows
from collections import deque
prices = deque(maxlen=window_size)

# Bad: Use list with manual size management
prices = []
if len(prices) > window_size:
    prices = prices[-window_size:]
```

### Configuration

```python
# Good: Validate configuration early
def validate_config(config: dict) -> None:
    required_keys = ['init_cash', 'strategies']
    for key in required_keys:
        if key not in config:
            raise ConfigError(f"Missing required key: {key}")
    
    if config['init_cash'] <= 0:
        raise ConfigError("init_cash must be positive")

# Bad: Fail late with unclear errors
cash = config['init_cash']  # KeyError if missing
portfolio = Portfolio(cash, symbols)  # Fails later if cash invalid
```

---

## Common Patterns

### Pattern 1: Indicator Calculation with Buffer

```python
def __init__(self, ticks, params):
    self._window = params['window']
    self._prices = deque(maxlen=self._window)
    self._indicator = []

def generate_signals(self, tick):
    self._prices.append(tick.price)
    
    if len(self._prices) < self._window:
        return ['Hold', tick.symbol, 100, tick.price]
    
    indicator_value = self._calculate_indicator()
    self._indicator.append(indicator_value)
    
    # Use indicator for signal
```

### Pattern 2: Multi-Condition Signals

```python
def generate_signals(self, tick):
    conditions = {
        'trend_up': self._short_ma > self._long_ma,
        'oversold': self._rsi < 30,
        'volume_spike': self._volume > self._avg_volume * 1.5
    }
    
    # Buy if multiple conditions met
    if conditions['trend_up'] and conditions['oversold']:
        return ['Buy', tick.symbol, 100, tick.price]
    
    # Strong sell if trend reversed with high volume
    elif not conditions['trend_up'] and conditions['volume_spike']:
        return ['Sell', tick.symbol, 100, tick.price]
    
    return ['Hold', tick.symbol, 100, tick.price]
```

### Pattern 3: Position Sizing

```python
def calculate_position_size(self, portfolio, price, risk_per_trade=0.02):
    """
    Calculate position size based on risk management.
    
    Args:
        portfolio: Current portfolio state
        price: Current price
        risk_per_trade: Maximum risk as fraction of portfolio
        
    Returns:
        Number of shares to trade
    """
    total_value = portfolio.get_value(current_prices)
    risk_amount = total_value * risk_per_trade
    
    # Simple position sizing: risk amount / price
    shares = int(risk_amount / price)
    
    # Ensure we can afford it
    max_affordable = int(portfolio.cash / price)
    
    return min(shares, max_affordable)
```

---

## Troubleshooting

### Common Issues

#### Issue: "OrderError: Not enough cash to buy"

**Cause**: Strategy attempting to buy more than available cash

**Solutions**:
1. Increase initial cash
2. Implement position sizing in strategy
3. Add cash management logic

```python
# In strategy:
def generate_signals(self, tick):
    # Check available cash before buying
    max_shares = int(self.available_cash / tick.price)
    if max_shares < 100:
        return ['Hold', tick.symbol, 100, tick.price]
    # ... rest of logic
```

#### Issue: "IndexError: list index out of range"

**Cause**: Accessing indicator buffer before it's populated

**Solution**: Add warmup period check

```python
def generate_signals(self, tick):
    self._prices.append(tick.price)
    
    # Need minimum data points
    if len(self._prices) < self._min_periods:
        return ['Hold', tick.symbol, 100, tick.price]
    
    # Now safe to calculate indicators
```

#### Issue: Portfolio value becomes negative

**Cause**: No cash validation before trades

**Solution**: Add validation in engine

```python
def create_order(self, name, signal):
    # ... existing code ...
    
    # Ensure cash doesn't go negative
    if qty > 0 and portfolio.cash < qty * price:
        raise OrderError(f"Insufficient cash: need {qty*price}, have {portfolio.cash}")
```

---

## Contributing

### Submission Checklist

- [ ] Code follows PEP 8 style guide
- [ ] All new functions have docstrings
- [ ] Type hints added for function signatures
- [ ] Unit tests written for new features
- [ ] Integration tests pass
- [ ] Documentation updated
- [ ] No breaking changes to existing API

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing performed

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Code reviewed
```