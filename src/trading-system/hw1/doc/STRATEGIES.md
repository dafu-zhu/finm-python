# Strategies Guide

Complete guide to trading strategies in the backtesting system, including implementation details, trading logic, and customization.

## Table of Contents

- [Overview](#overview)
- [Strategy Architecture](#strategy-architecture)
- [Built-in Strategies](#built-in-strategies)
  - [MACD Strategy](#macd-strategy)
  - [Momentum Strategy](#momentum-strategy)
- [Strategy Implementation](#strategy-implementation)
- [Advanced Topics](#advanced-topics)
- [Strategy Comparison](#strategy-comparison)
- [Best Practices](#best-practices)

---

## Overview

### What is a Trading Strategy?

A trading strategy is a systematic approach to making buy and sell decisions in financial markets. In this system, strategies analyze market data and generate trading signals based on predefined rules.

### Strategy Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                    Strategy Lifecycle                        │
└─────────────────────────────────────────────────────────────┘
         │
         ├─── 1. Initialization
         │    ├─── Load historical data
         │    ├─── Validate parameters
         │    └─── Initialize indicators
         │
         ├─── 2. Warmup Period
         │    ├─── Accumulate initial data
         │    ├─── Calculate first indicators
         │    └─── Generate "Hold" signals
         │
         ├─── 3. Active Trading
         │    ├─── Receive market tick
         │    ├─── Update indicators
         │    ├─── Evaluate conditions
         │    └─── Generate signal
         │
         └─── 4. Completion
              ├─── Final portfolio value
              ├─── Performance metrics
              └─── Trade history
```

---

## Strategy Architecture

### Base Strategy Class

All strategies inherit from the abstract `Strategy` class:

```python
from abc import ABC, abstractmethod
from data_loader import MarketDataPoint

class Strategy(ABC):
    """Blueprint for all trading strategies."""
    
    @abstractmethod
    def generate_signals(self, tick: MarketDataPoint) -> list:
        """
        Generate trading signal based on current market data.
        
        Args:
            tick: Current market data point with timestamp, symbol, and price
            
        Returns:
            Signal list: [action, symbol, quantity, price]
            - action: 'Buy', 'Sell', or 'Hold'
            - symbol: Ticker symbol (str)
            - quantity: Number of shares (int)
            - price: Order price (float)
        """
        pass
```

### Signal Format

Every strategy must return signals in this exact format:

```python
[action, symbol, quantity, price]
```

**Components**:
- `action` (str): One of `'Buy'`, `'Sell'`, or `'Hold'`
- `symbol` (str): The ticker symbol being traded
- `quantity` (int): Number of shares (currently fixed at 100)
- `price` (float): The current market price

**Examples**:
```python
['Buy', 'AAPL', 100, 150.50]   # Buy 100 shares of AAPL at $150.50
['Sell', 'GOOGL', 100, 2850.0] # Sell 100 shares of GOOGL at $2850
['Hold', 'MSFT', 100, 380.25]  # No action for MSFT
```

### Strategy State

Each strategy maintains internal state through the `StrategyState` dataclass:

```python
@dataclass
class StrategyState:
    strategy: Strategy              # The strategy instance
    portfolio: Portfolio            # Cash and positions
    orders: List[Order]            # All orders created
    order_errors: List[str]        # Validation failures
    execution_errors: List[str]    # Execution failures
    history: List[Tuple[datetime, float]]  # Portfolio value over time
```

---

## Built-in Strategies

### MACD Strategy

#### Overview

The Moving Average Convergence Divergence (MACD) strategy trades based on the crossover of two moving averages. This is a trend-following strategy that works well in trending markets.

#### Mathematical Foundation

**Moving Average Formula**:
```
MA(n) = (P₁ + P₂ + ... + Pₙ) / n
```

Where:
- `MA(n)` = Moving average over n periods
- `Pᵢ` = Price at period i
- `n` = Number of periods

**Trading Signal**:
```
If MA(short) > MA(long) → Buy Signal
If MA(short) < MA(long) → Sell Signal
Otherwise → Hold
```

#### Implementation Details

```python
class MACDStrategy(Strategy):
    def __init__(self, ticks: List[MarketDataPoint], params: dict):
        # Required parameters
        self._short_period = params['short_period']  # e.g., 12
        self._long_period = params['long_period']    # e.g., 26
        
        # State variables
        self._prices = deque(maxlen=self._long_period)
        self._short_ma = []  # Historical short MA values
        self._long_ma = []   # Historical long MA values
```

**Key Features**:
- Uses `deque` with fixed length for memory efficiency
- Maintains history of MA values for analysis
- Implements O(1) price buffer updates

#### Trading Logic Flow

```
For each new market tick:
    │
    ├─── 1. Update Price Buffer
    │    └─── prices.append(current_price)
    │
    ├─── 2. Calculate Moving Averages
    │    ├─── short_ma = mean(prices[-short_period:])
    │    └─── long_ma = mean(prices[-long_period:])
    │
    ├─── 3. Store MA Values
    │    ├─── self._short_ma.append(short_ma)
    │    └─── self._long_ma.append(long_ma)
    │
    └─── 4. Generate Signal
         ├─── If short_ma > long_ma → Buy
         ├─── If short_ma < long_ma → Sell
         └─── Else → Hold
```

#### Parameter Selection

| Period Combination | Trading Style | Signal Frequency | Best For |
|-------------------|---------------|------------------|----------|
| 5 / 10 | Very Aggressive | High | Day trading, volatile stocks |
| 12 / 26 | Standard | Medium | Medium-term trading |
| 26 / 52 | Conservative | Low | Long-term investing |
| 50 / 200 | Very Conservative | Very Low | Position trading |

**Guidelines**:
- **Short Period**: Typically 1/2 to 1/3 of long period
- **Long Period**: Depends on your time horizon
- **Ratio**: Short/Long ratio affects sensitivity

#### Performance Characteristics

**Strengths**:
- ✅ Excellent in strong trending markets
- ✅ Simple to understand and implement
- ✅ Reduces noise through averaging
- ✅ Clear entry and exit signals

**Weaknesses**:
- ❌ Lags market turns (lagging indicator)
- ❌ Poor performance in sideways markets
- ❌ Generates false signals in choppy conditions
- ❌ Late entries and exits

#### Example Usage

```python
from strategies import MACDStrategy
from data_loader import data_ingestor

# Load data
ticks = data_ingestor('market_data.csv')

# Create strategy with standard parameters
macd_standard = MACDStrategy(
    ticks=ticks,
    params={
        'short_period': 12,
        'long_period': 26
    }
)

# Create aggressive variant
macd_aggressive = MACDStrategy(
    ticks=ticks,
    params={
        'short_period': 5,
        'long_period': 10
    }
)
```

#### Real-World Example

Consider a trending stock:

```
Day | Price | Short MA (5) | Long MA (10) | Signal
----|-------|--------------|--------------|--------
1   | 100   | -            | -            | Hold (warmup)
...
5   | 105   | 102.4        | -            | Hold (warmup)
...
10  | 110   | 107.2        | 105.5        | Buy (107.2 > 105.5)
11  | 112   | 108.6        | 106.8        | Buy (continue)
12  | 114   | 110.2        | 108.1        | Buy (continue)
...
20  | 108   | 109.8        | 110.2        | Sell (109.8 < 110.2)
```

---

### Momentum Strategy

#### Overview

The Momentum strategy trades based on the Rate of Change (ROC) of prices. It identifies and capitalizes on price momentum by buying when prices are rising strongly and selling when they're falling.

#### Mathematical Foundation

**Rate of Change Formula**:
```
ROC = (Pₜ / Pₜ₋ₙ) - 1
```

Where:
- `Pₜ` = Current price
- `Pₜ₋ₙ` = Price n periods ago
- `n` = Lookback period

**Trading Signal**:
```
If ROC > buy_threshold → Buy Signal
If ROC < sell_threshold → Sell Signal
Otherwise → Hold
```

#### Implementation Details

```python
class MomentumStrategy(Strategy):
    def __init__(self, ticks: List[MarketDataPoint], params: dict):
        # Required parameters
        self._lookback = params['lookback']              # e.g., 20
        self._buy_threshold = params['buy_threshold']    # e.g., 0.02 (2%)
        self._sell_threshold = params['sell_threshold']  # e.g., -0.02 (-2%)
        
        # State variables
        self._prices = deque(maxlen=self._lookback)
        self._roc = []  # Historical ROC values
```

**Key Features**:
- Direct price comparison (no averaging)
- More responsive than MACD
- Threshold-based signal generation

#### Trading Logic Flow

```
For each new market tick:
    │
    ├─── 1. Update Price Buffer
    │    └─── prices.append(current_price)
    │
    ├─── 2. Calculate ROC
    │    ├─── current_price = prices[-1]
    │    ├─── old_price = prices[0]
    │    └─── roc = (current_price / old_price) - 1
    │
    ├─── 3. Store ROC Value
    │    └─── self._roc.append(roc)
    │
    └─── 4. Generate Signal
         ├─── If roc > buy_threshold → Buy
         ├─── If roc < sell_threshold → Sell
         └─── Else → Hold
```

#### Parameter Selection

**Lookback Period**:

| Lookback | Trading Style | Sensitivity | Best For |
|----------|---------------|-------------|----------|
| 5-10 | Very Short-term | Extremely High | Scalping, day trading |
| 10-20 | Short-term | High | Swing trading |
| 20-30 | Medium-term | Medium | Position trading |
| 50+ | Long-term | Low | Trend following |

**Threshold Selection**:

| Threshold | Signal Frequency | Risk Level | Description |
|-----------|-----------------|------------|-------------|
| ±1% | Very High | High | Many trades, high noise |
| ±2% | High | Medium-High | Active trading |
| ±3% | Medium | Medium | Balanced approach |
| ±5% | Low | Low | Conservative, strong signals |
| ±10% | Very Low | Very Low | Only extreme moves |

#### Performance Characteristics

**Strengths**:
- ✅ Captures strong price movements quickly
- ✅ More responsive than moving averages
- ✅ Works well in volatile markets
- ✅ Customizable through thresholds

**Weaknesses**:
- ❌ Prone to whipsaws in choppy markets
- ❌ Can generate many false signals
- ❌ Requires careful threshold tuning
- ❌ May miss slower trends

#### Example Usage

```python
from strategies import MomentumStrategy

# Conservative momentum strategy
momentum_conservative = MomentumStrategy(
    ticks=ticks,
    params={
        'lookback': 20,
        'buy_threshold': 0.05,   # Buy on 5% rise
        'sell_threshold': -0.05  # Sell on 5% drop
    }
)

# Aggressive momentum strategy
momentum_aggressive = MomentumStrategy(
    ticks=ticks,
    params={
        'lookback': 10,
        'buy_threshold': 0.02,   # Buy on 2% rise
        'sell_threshold': -0.02  # Sell on 2% drop
    }
)
```

#### Real-World Example

Consider a volatile stock:

```
Day | Price | ROC (20-day) | Threshold | Signal
----|-------|--------------|-----------|--------
1   | 100   | -            | ±2%       | Hold (warmup)
...
20  | 105   | 5.0%         | ±2%       | Buy (5% > 2%)
21  | 107   | 7.0%         | ±2%       | Buy (continue)
22  | 104   | 4.0%         | ±2%       | Buy (still above)
23  | 98    | -2.0%        | ±2%       | Hold (within range)
24  | 95    | -5.0%        | ±2%       | Sell (-5% < -2%)
```

---

## Strategy Implementation

### Creating a Custom Strategy

#### Step 1: Define the Strategy Class

```python
from strategies import Strategy
from data_loader import MarketDataPoint
from models import ConfigError
from collections import deque

class BollingerBandsStrategy(Strategy):
    """
    Bollinger Bands strategy implementation.
    
    Trading Logic:
    - Buy when price crosses below lower band (oversold)
    - Sell when price crosses above upper band (overbought)
    """
```

#### Step 2: Implement Constructor

```python
    def __init__(self, ticks: List[MarketDataPoint], params: dict):
        """
        Initialize Bollinger Bands strategy.
        
        Required params:
        - period (int): Moving average period
        - std_dev (float): Number of standard deviations for bands
        """
        # Validate required parameters
        try:
            self._period = params['period']
            self._std_dev = params['std_dev']
        except KeyError as e:
            raise ConfigError(f"Missing required parameter: {e}") from e
        
        # Type validation
        if not isinstance(self._period, int):
            raise TypeError("period must be an integer")
        if not isinstance(self._std_dev, (int, float)):
            raise TypeError("std_dev must be numeric")
        
        # Value validation
        if self._period < 2:
            raise ValueError("period must be at least 2")
        if self._std_dev <= 0:
            raise ValueError("std_dev must be positive")
        
        # Initialize state
        self._ticks = ticks
        self._prices = deque(maxlen=self._period)
        self._upper_band = []
        self._lower_band = []
        self._middle_band = []
```

#### Step 3: Implement String Representation

```python
    def __repr__(self) -> str:
        """Return unique identifier for this strategy."""
        return f"BollingerBands_{self._period}_{self._std_dev}"
```

#### Step 4: Implement Signal Generation

```python
    def generate_signals(self, tick: MarketDataPoint) -> list:
        """
        Generate signals based on Bollinger Bands.
        
        Args:
            tick: Current market data
            
        Returns:
            Signal: [action, symbol, quantity, price]
        """
        symbol = tick.symbol
        price = tick.price
        
        # Update price buffer
        self._prices.append(price)
        
        # Need full period for calculation
        if len(self._prices) < self._period:
            return ['Hold', symbol, 100, price]
        
        # Calculate Bollinger Bands
        middle = sum(self._prices) / self._period
        variance = sum((p - middle) ** 2 for p in self._prices) / self._period
        std_dev = variance ** 0.5
        
        upper = middle + (self._std_dev * std_dev)
        lower = middle - (self._std_dev * std_dev)
        
        # Store band values
        self._upper_band.append(upper)
        self._lower_band.append(lower)
        self._middle_band.append(middle)
        
        # Generate signals
        if price < lower:
            return ['Buy', symbol, 100, price]   # Price below lower band (oversold)
        elif price > upper:
            return ['Sell', symbol, 100, price]  # Price above upper band (overbought)
        else:
            return ['Hold', symbol, 100, price]  # Price within bands
```

#### Step 5: Add Helper Methods (Optional)

```python
    def get_band_width(self) -> float:
        """Calculate current band width (volatility measure)."""
        if not self._upper_band:
            return 0.0
        return self._upper_band[-1] - self._lower_band[-1]
    
    def get_percent_b(self, price: float) -> float:
        """
        Calculate %B indicator.
        Shows where price is relative to the bands.
        
        Returns:
            float: 0-1 scale (0.5 = middle of bands)
        """
        if not self._upper_band:
            return 0.5
        
        upper = self._upper_band[-1]
        lower = self._lower_band[-1]
        
        if upper == lower:
            return 0.5
        
        return (price - lower) / (upper - lower)
```

---

## Advanced Topics

### Multi-Indicator Strategies

Combine multiple indicators for more robust signals:

```python
class ComboStrategy(Strategy):
    """Combines MACD and RSI for signal confirmation."""
    
    def __init__(self, ticks, params):
        self._macd_short = params['macd_short']
        self._macd_long = params['macd_long']
        self._rsi_period = params['rsi_period']
        self._rsi_oversold = params['rsi_oversold']
        self._rsi_overbought = params['rsi_overbought']
        
        # Initialize buffers for both indicators
        self._prices = deque(maxlen=max(self._macd_long, self._rsi_period + 1))
    
    def generate_signals(self, tick):
        symbol, price = tick.symbol, tick.price
        self._prices.append(price)
        
        # Calculate both indicators
        macd_signal = self._calculate_macd()
        rsi_signal = self._calculate_rsi()
        
        # Require confirmation from both
        if macd_signal == 'Buy' and rsi_signal == 'Buy':
            return ['Buy', symbol, 100, price]
        elif macd_signal == 'Sell' and rsi_signal == 'Sell':
            return ['Sell', symbol, 100, price]
        else:
            return ['Hold', symbol, 100, price]
```

### State-Based Strategies

Implement strategies with internal states:

```python
class StatefulStrategy(Strategy):
    """Strategy that maintains trading state."""
    
    def __init__(self, ticks, params):
        self._state = 'NEUTRAL'  # NEUTRAL, LONG, SHORT
        self._entry_price = None
        self._stop_loss_pct = params['stop_loss']
        self._take_profit_pct = params['take_profit']
    
    def generate_signals(self, tick):
        symbol, price = tick.symbol, tick.price
        
        if self._state == 'NEUTRAL':
            # Look for entry
            if self._should_enter_long(price):
                self._state = 'LONG'
                self._entry_price = price
                return ['Buy', symbol, 100, price]
        
        elif self._state == 'LONG':
            # Check exit conditions
            pnl_pct = (price / self._entry_price) - 1
            
            if pnl_pct <= -self._stop_loss_pct:
                # Stop loss hit
                self._state = 'NEUTRAL'
                return ['Sell', symbol, 100, price]
            
            elif pnl_pct >= self._take_profit_pct:
                # Take profit hit
                self._state = 'NEUTRAL'
                return ['Sell', symbol, 100, price]
        
        return ['Hold', symbol, 100, price]
```

### Position Sizing Strategies

Implement dynamic position sizing:

```python
class DynamicPositionStrategy(Strategy):
    """Strategy with variable position sizes."""
    
    def calculate_position_size(self, portfolio_value, price, volatility):
        """
        Kelly Criterion-based position sizing.
        
        Args:
            portfolio_value: Current portfolio value
            price: Stock price
            volatility: Historical volatility
            
        Returns:
            Number of shares to trade
        """
        # Risk 2% of portfolio per trade
        risk_per_trade = 0.02
        risk_amount = portfolio_value * risk_per_trade
        
        # Adjust for volatility
        volatility_adjusted_risk = risk_amount / (1 + volatility)
        
        # Calculate shares
        shares = int(volatility_adjusted_risk / price)
        
        # Ensure minimum and maximum
        shares = max(10, min(shares, 1000))
        
        return shares
```

---

## Strategy Comparison

### Performance Comparison Matrix

| Strategy | Trending Markets | Volatile Markets | Sideways Markets | Responsiveness | Complexity |
|----------|-----------------|------------------|------------------|----------------|------------|
| MACD | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐ | Medium | Low |
| Momentum | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | High | Low |
| Bollinger Bands | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | Medium-High | Medium |
| Multi-Indicator | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | Medium | High |

### When to Use Each Strategy

**MACD Strategy**:
- Strong, sustained trends
- Low-frequency trading
- Clear directional moves
- Lower transaction costs desired

**Momentum Strategy**:
- High volatility environments
- News-driven moves
- Quick profit opportunities
- Active trading acceptable

**Combined Approach**:
Test multiple strategies simultaneously to diversify:

```python
strategies = [
    MACDStrategy(ticks, {'short_period': 12, 'long_period': 26}),
    MomentumStrategy(ticks, {'lookback': 20, 'buy_threshold': 0.02, 'sell_threshold': -0.02}),
    # Add more as needed
]

engine = ExecutionEngine(ticks, strategies, init_cash=100_000)
states = engine.run()

# Compare performance
for name, state in states.items():
    final_value = state.history[-1][1]
    returns = (final_value / 100_000 - 1) * 100
    print(f"{name}: {returns:+.2f}%")
```

---

## Best Practices

### 1. Parameter Validation

Always validate parameters thoroughly:

```python
def __init__(self, ticks, params):
    # Check existence
    required = ['period', 'threshold']
    for param in required:
        if param not in params:
            raise ConfigError(f"Missing required parameter: {param}")
    
    # Check types
    if not isinstance(params['period'], int):
        raise TypeError("period must be integer")
    
    # Check values
    if params['period'] < 1:
        raise ValueError("period must be positive")
```

### 2. Handle Edge Cases

```python
def generate_signals(self, tick):
    # Handle warmup period
    if len(self._prices) < self._min_periods:
        return ['Hold', tick.symbol, 100, tick.price]
    
    # Handle division by zero
    if denominator == 0:
        return ['Hold', tick.symbol, 100, tick.price]
    
    # Normal signal generation
    # ...
```

### 3. Use Efficient Data Structures

```python
# Good: O(1) append and automatic size management
self._prices = deque(maxlen=window)

# Bad: O(n) slicing on every update
self._prices = self._prices[-window:]
```

### 4. Document Your Strategy

```python
class MyStrategy(Strategy):
    """
    Brief one-line description.
    
    Detailed explanation of:
    - Trading logic
    - Indicators used
    - Entry/exit rules
    - Parameter meanings
    - Market conditions where it works best
    
    References:
    - Link to academic paper
    - Link to trading book
    """
```

### 5. Test Thoroughly

```python
def test_strategy():
    # Test parameter validation
    with pytest.raises(ConfigError):
        MyStrategy(ticks, {})  # Missing params
    
    # Test signal format
    strategy = MyStrategy(ticks, valid_params)
    signal = strategy.generate_signals(tick)
    assert len(signal) == 4
    assert signal[0] in ['Buy', 'Sell', 'Hold']
    
    # Test edge cases
    # ...
```

---

## Summary

### Key Takeaways

1. **Strategy Pattern**: All strategies implement `generate_signals()`
2. **Signal Format**: Always return `[action, symbol, quantity, price]`
3. **State Management**: Use instance variables for indicators and buffers
4. **Validation**: Validate parameters early and thoroughly
5. **Efficiency**: Use appropriate data structures (deque for windows)
6. **Documentation**: Document trading logic and parameters clearly

### Next Steps

1. Review the built-in strategies (MACD and Momentum)
2. Understand their strengths and weaknesses
3. Try different parameter combinations
4. Implement your own custom strategy
5. Backtest and compare results

For implementation details, see the **[Developer Guide](DEVELOPER_GUIDE.md)**.

For performance analysis, see **[Reporting & Analytics](REPORTING.md)**.

---

*Happy strategy development!*
