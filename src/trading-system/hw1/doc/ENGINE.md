# Execution Engine

Complete guide to the execution engine that orchestrates backtesting, order validation, and portfolio management.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Initialization](#initialization)
- [Order Lifecycle](#order-lifecycle)
- [Execution Flow](#execution-flow)
- [Error Handling](#error-handling)
- [State Management](#state-management)
- [Advanced Features](#advanced-features)
- [Performance Considerations](#performance-considerations)

---

## Overview

### What is the Execution Engine?

The `ExecutionEngine` is the core component that orchestrates the entire backtesting simulation. It acts as the central coordinator between market data, strategies, orders, and portfolios.

### Key Responsibilities

1. **Market Data Processing**: Iterates through historical ticks chronologically
2. **Signal Generation**: Invokes strategies to generate trading signals
3. **Order Management**: Creates, validates, and executes orders
4. **Portfolio Tracking**: Maintains positions and cash balances
5. **Performance Recording**: Tracks portfolio value over time
6. **Error Handling**: Manages validation and execution failures gracefully

### Design Philosophy

The engine is designed with these principles:

- **Realism**: Simulates real-world trading conditions including failures
- **Isolation**: Each strategy operates independently with its own portfolio
- **Safety**: Validates all orders before execution
- **Transparency**: Logs all errors for post-analysis
- **Efficiency**: Processes data in single pass with O(n) complexity

---

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      Execution Engine                           │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              Initialization Phase                        │  │
│  │  • Sort market data by timestamp                        │  │
│  │  • Create strategy states                               │  │
│  │  │  └─── For each strategy:                            │  │
│  │  │       ├─── Initialize portfolio                      │  │
│  │  │       ├─── Create empty order list                   │  │
│  │  │       └─── Initialize error logs                     │  │
│  │  • Extract unique symbols                               │  │
│  └─────────────────────────────────────────────────────────┘  │
│                          ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              Execution Loop                              │  │
│  │                                                          │  │
│  │  For each tick in chronological order:                  │  │
│  │    │                                                     │  │
│  │    ├─── Update current prices                           │  │
│  │    │                                                     │  │
│  │    └─── For each strategy:                              │  │
│  │         │                                                │  │
│  │         ├─── 1. Generate Signal                         │  │
│  │         │    └─── strategy.generate_signals(tick)       │  │
│  │         │                                                │  │
│  │         ├─── 2. Create Order                            │  │
│  │         │    ├─── Parse signal                          │  │
│  │         │    ├─── Validate format                       │  │
│  │         │    ├─── Check position limits                 │  │
│  │         │    └─── Check cash availability               │  │
│  │         │    (Log errors if validation fails)           │  │
│  │         │                                                │  │
│  │         ├─── 3. Execute Order                           │  │
│  │         │    ├─── Simulate random failures (1%)         │  │
│  │         │    └─── Update portfolio                      │  │
│  │         │    (Log errors if execution fails)            │  │
│  │         │                                                │  │
│  │         └─── 4. Record State                            │  │
│  │              ├─── Append order to history               │  │
│  │              ├─── Calculate portfolio value             │  │
│  │              └─── Store (timestamp, value) tuple        │  │
│  └─────────────────────────────────────────────────────────┘  │
│                          ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              Return Phase                                │  │
│  │  • Return dictionary of all strategy states             │  │
│  │  • Each state contains:                                 │  │
│  │    ├─── Final portfolio                                 │  │
│  │    ├─── Complete order history                          │  │
│  │    ├─── All error logs                                  │  │
│  │    └─── Portfolio value time series                     │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Class Structure

```python
class ExecutionEngine:
    """
    Orchestrates backtesting simulation.
    
    Attributes:
        _states: Dictionary mapping strategy names to StrategyState
        _ticks: Sorted list of market data points
        _strategies: List of strategy instances
        _symbols: List of unique symbols from data
        _allow_short: Whether short selling is allowed (not implemented)
    """
```

---

## Initialization

### Constructor Signature

```python
def __init__(
    self,
    ticks: List[MarketDataPoint],
    strategies: List[Strategy],
    init_cash: float,
    allow_short: bool = False
) -> None
```

### Initialization Process

#### Step 1: Sort Market Data

```python
# Ensure chronological processing
self._ticks = sorted(ticks, key=lambda tick: tick.timestamp)
```

**Why**: Prevents look-ahead bias by processing data in historical order.

#### Step 2: Extract Symbols

```python
# Get unique symbols for portfolio initialization
self._symbols = list(set(tick.symbol for tick in ticks))
```

**Purpose**: Create positions for all traded securities.

#### Step 3: Create Strategy States

```python
for strategy in strategies:
    name = strategy.__repr__()
    
    state = StrategyState(
        strategy=strategy,
        portfolio=Portfolio(init_cash, self._symbols),
        orders=[],
        order_errors=[],
        execution_errors=[],
        history=[]
    )
    
    self._states[name] = state
```

**Result**: Each strategy gets:
- Independent portfolio with initial cash
- Empty order list
- Empty error logs
- Empty value history

### Initialization Example

```python
from engine import ExecutionEngine
from strategies import MACDStrategy, MomentumStrategy
from data_loader import data_ingestor

# Load data
ticks = data_ingestor('market_data.csv')

# Create strategies
strategies = [
    MACDStrategy(ticks, {'short_period': 12, 'long_period': 26}),
    MomentumStrategy(ticks, {'lookback': 20, 'buy_threshold': 0.02, 'sell_threshold': -0.02})
]

# Initialize engine
engine = ExecutionEngine(
    ticks=ticks,
    strategies=strategies,
    init_cash=1_000_000
)

# At this point:
# - Data is sorted chronologically
# - Each strategy has its own portfolio with $1M
# - All error logs are empty
# - Ready to run backtest
```

---

## Order Lifecycle

### Complete Order Flow

```
Signal Generation → Order Creation → Validation → Execution → Portfolio Update
     │                  │               │            │              │
     │                  │               │            │              │
     ▼                  ▼               ▼            ▼              ▼
['Buy', 'AAPL',    Order object    Checks pass   Random 1%    Position qty++
 100, 150.0]       created          or fail?     success?     Cash reduced
```

### Phase 1: Signal Generation

**Input**: Current market tick
**Process**: Strategy analyzes data and generates signal
**Output**: List `[action, symbol, quantity, price]`

```python
signal = strategy.generate_signals(tick)
# Example: ['Buy', 'AAPL', 100, 150.50]
```

### Phase 2: Order Creation

**Method**: `create_order(name: str, signal: list) -> Order`

#### Step 2.1: Parse Signal

```python
try:
    action, symbol, qty, price = signal
except ValueError as e:
    raise OrderError(f"Malformed signal: expected 4 elements, got {len(signal)}") from e
```

**Validation**: Ensures signal has exactly 4 components.

#### Step 2.2: Convert Action to Direction

```python
if action == 'Buy':
    direction = 1
elif action == 'Sell':
    direction = -1
else:
    direction = 0  # Hold

qty *= direction  # qty now: positive for buy, negative for sell, 0 for hold
```

#### Step 2.3: Position Validation

```python
portfolio = self._states[name].portfolio
position = portfolio.positions.get(symbol, Position(symbol))

# Check: Can we sell this much?
if position.quantity < abs(qty) and qty < 0:
    raise OrderError(
        f"Not enough shares to sell: "
        f"expected sell {abs(qty)}, got {position.quantity}"
    )
```

**Prevents**: Selling more shares than owned (no short selling by default).

#### Step 2.4: Cash Validation

```python
# Check: Do we have enough cash to buy?
if portfolio.cash < qty * price:
    raise OrderError(
        f"Not enough cash to buy: "
        f"need {qty * price:.2f}, got {portfolio.cash:.2f}"
    )
```

**Prevents**: Buying beyond available cash (no margin trading).

#### Step 2.5: Create Order

```python
return Order(symbol, qty, price, 'pending')
```

**Result**: Validated order ready for execution.

### Phase 3: Order Execution

**Method**: `execute_order(name: str, order: Order) -> None`

#### Step 3.1: Simulate Market Conditions

```python
# 1% random execution failure
if random.random() < 0.01:
    raise ExecutionError(f"Market rejected order: {order}")
```

**Purpose**: Simulates real-world order rejections for realism.

#### Step 3.2: Update Portfolio

```python
self._states[name].portfolio.update_position(
    symbol=order.symbol,
    qty=order.quantity,
    price=order.price
)
```

**Effects**:
- Position quantity updated
- Average price recalculated (for buys)
- Cash balance adjusted

### Phase 4: State Recording

```python
# Mark order status
order.status = 'success'  # or 'failed'

# Store order
state.orders.append(order)

# Calculate and record portfolio value
value = state.portfolio.get_value(current_prices)
state.history.append((current_time, round(value)))
```

---

## Execution Flow

### Main Execution Loop

The `run()` method implements the core backtesting logic:

```python
def run(self) -> dict:
    """
    Execute complete backtesting simulation.
    
    Returns:
        Dictionary mapping strategy names to final StrategyState objects
    """
    # Initialize price tracking
    current_prices = {symbol: 0.0 for symbol in self._symbols}
    
    # Main loop: Process each tick chronologically
    for tick in self._ticks:
        # Update market prices
        current_prices[tick.symbol] = tick.price
        current_time = tick.timestamp
        
        # Process each strategy
        for strategy in self._strategies:
            name = strategy.__repr__()
            state = self._states[name]
            
            # 1. Generate signal
            signal = strategy.generate_signals(tick)
            
            # 2. Create and validate order
            try:
                order = self.create_order(name, signal)
            except OrderError as e:
                state.order_errors.append(f"{tick.timestamp}: {e}")
                continue  # Skip to next strategy
            
            # 3. Execute order
            try:
                self.execute_order(name, order)
                order.status = 'success'
            except ExecutionError as e:
                order.status = 'failed'
                state.execution_errors.append(f"{tick.timestamp}: {e}")
            
            # 4. Record state (even if order failed)
            state.orders.append(order)
            value = state.portfolio.get_value(current_prices)
            state.history.append((current_time, round(value)))
    
    return self._states
```

### Execution Timeline

Consider a simple example with 5 ticks:

```
Tick 1 (t=09:30:00, AAPL=150.00)
├─── MACD Strategy
│    ├─── Generate signal: ['Hold', 'AAPL', 100, 150.00]
│    └─── No order created (Hold action)
└─── Momentum Strategy
     ├─── Generate signal: ['Buy', 'AAPL', 100, 150.00]
     ├─── Create order: Order(AAPL, 100, 150.00, 'pending')
     ├─── Execute: SUCCESS
     └─── Portfolio: Cash=$985,000, AAPL=100 shares

Tick 2 (t=09:31:00, AAPL=152.00)
├─── MACD Strategy
│    ├─── Generate signal: ['Buy', 'AAPL', 100, 152.00]
│    ├─── Create order: Order(AAPL, 100, 152.00, 'pending')
│    ├─── Execute: SUCCESS
│    └─── Portfolio: Cash=$984,800, AAPL=100 shares
└─── Momentum Strategy
     └─── Continue holding...

Tick 3 (t=09:32:00, AAPL=151.00)
├─── MACD Strategy
│    └─── Continue holding...
└─── Momentum Strategy
     ├─── Generate signal: ['Sell', 'AAPL', 100, 151.00]
     ├─── Create order: Order(AAPL, -100, 151.00, 'pending')
     ├─── Execute: FAILED (1% random rejection)
     └─── Order status: 'failed'
```

---

## Error Handling

### Error Categories

The engine handles three categories of errors:

#### 1. Order Errors (Validation Failures)

**Causes**:
- Malformed signal (wrong number of elements)
- Insufficient shares for sell order
- Insufficient cash for buy order

**Handling**:
```python
try:
    order = self.create_order(name, signal)
except OrderError as e:
    state.order_errors.append(f"{tick.timestamp}: {e}")
    continue  # Skip this order, continue with next strategy
```

**Impact**: Order not created, backtest continues

#### 2. Execution Errors (Market Rejections)

**Causes**:
- Random 1% execution failure (simulated)
- Future: Could add slippage, partial fills, etc.

**Handling**:
```python
try:
    self.execute_order(name, order)
    order.status = 'success'
except ExecutionError as e:
    order.status = 'failed'
    state.execution_errors.append(f"{tick.timestamp}: {e}")
```

**Impact**: Order marked as failed, portfolio unchanged, backtest continues

#### 3. Fatal Errors (System Failures)

**Causes**:
- Invalid configuration
- Missing data
- Type errors

**Handling**: These propagate up and halt execution

### Error Logging

All errors are logged with timestamps for post-analysis:

```python
# Access error logs after backtest
states = engine.run()

for name, state in states.items():
    print(f"\n{name} Errors:")
    print(f"Order Errors: {len(state.order_errors)}")
    for error in state.order_errors:
        print(f"  {error}")
    
    print(f"Execution Errors: {len(state.execution_errors)}")
    for error in state.execution_errors:
        print(f"  {error}")
```

### Error Analysis Example

```python
# After running backtest
states = engine.run()
state = states['MACD_12_26']

# Analyze order errors
print("Order Validation Failures:")
for error in state.order_errors:
    print(error)

# Example output:
# 2024-01-15 10:30:00: Not enough cash to buy: need 15250.00, got 5000.00
# 2024-01-15 14:20:00: Not enough shares to sell: expected sell 100, got 50

# Analyze execution errors
print("\nExecution Failures:")
for error in state.execution_errors:
    print(error)

# Example output:
# 2024-01-15 11:45:00: Market rejected order: Order(AAPL, 100, 150.5, 'pending')
```

---

## State Management

### Strategy State Components

Each `StrategyState` maintains complete information about a strategy's execution:

```python
@dataclass
class StrategyState:
    strategy: Strategy              # The strategy instance
    portfolio: Portfolio            # Current cash and positions
    orders: List[Order]            # All orders (successful and failed)
    order_errors: List[str]        # Validation error messages
    execution_errors: List[str]    # Execution error messages
    history: List[Tuple[datetime, float]]  # (timestamp, portfolio_value)
```

### Accessing State Information

#### Portfolio Information

```python
state = states['MACD_12_26']

# Current cash
print(f"Cash: ${state.portfolio.cash:,.2f}")

# Positions
for symbol, position in state.portfolio.positions.items():
    if position.quantity > 0:
        print(f"{symbol}: {position.quantity} shares @ ${position.avg_price:.2f}")
```

#### Order History

```python
# All orders
total_orders = len(state.orders)
successful_orders = sum(1 for o in state.orders if o.status == 'success')
failed_orders = sum(1 for o in state.orders if o.status == 'failed')

print(f"Total orders: {total_orders}")
print(f"Successful: {successful_orders}")
print(f"Failed: {failed_orders}")

# Orders by type
buy_orders = [o for o in state.orders if o.quantity > 0]
sell_orders = [o for o in state.orders if o.quantity < 0]
```

#### Performance History

```python
# Portfolio value over time
times, values = zip(*state.history)

initial_value = values[0]
final_value = values[-1]
peak_value = max(values)
trough_value = min(values)

print(f"Initial: ${initial_value:,.2f}")
print(f"Final: ${final_value:,.2f}")
print(f"Peak: ${peak_value:,.2f}")
print(f"Trough: ${trough_value:,.2f}")

# Return calculation
total_return = (final_value / initial_value - 1) * 100
print(f"Total Return: {total_return:+.2f}%")
```

### State Persistence

While the engine doesn't automatically save states, you can persist them:

```python
import pickle
import json

# Save with pickle (preserves all Python objects)
with open('backtest_state.pkl', 'wb') as f:
    pickle.dump(states, f)

# Load saved state
with open('backtest_state.pkl', 'rb') as f:
    loaded_states = pickle.load(f)

# Or export to JSON (requires conversion)
state_dict = {
    name: {
        'orders': len(state.orders),
        'order_errors': len(state.order_errors),
        'execution_errors': len(state.execution_errors),
        'history': state.history,
        'final_cash': state.portfolio.cash
    }
    for name, state in states.items()
}

with open('backtest_summary.json', 'w') as f:
    json.dump(state_dict, f, indent=2, default=str)
```

---

## Advanced Features

### Multi-Strategy Execution

The engine naturally supports multiple concurrent strategies:

```python
# Create multiple strategies with different parameters
strategies = [
    MACDStrategy(ticks, {'short_period': 5, 'long_period': 10}),
    MACDStrategy(ticks, {'short_period': 12, 'long_period': 26}),
    MACDStrategy(ticks, {'short_period': 26, 'long_period': 52}),
    MomentumStrategy(ticks, {'lookback': 10, 'buy_threshold': 0.02, 'sell_threshold': -0.02}),
    MomentumStrategy(ticks, {'lookback': 20, 'buy_threshold': 0.03, 'sell_threshold': -0.03}),
]

# Each operates independently
engine = ExecutionEngine(ticks, strategies, init_cash=100_000)
states = engine.run()

# Compare performance
results = []
for name, state in states.items():
    final_value = state.history[-1][1]
    returns = (final_value / 100_000 - 1) * 100
    results.append((name, returns))

# Sort by performance
results.sort(key=lambda x: x[1], reverse=True)

print("Performance Ranking:")
for i, (name, returns) in enumerate(results, 1):
    print(f"{i}. {name}: {returns:+.2f}%")
```

### Price Tracking

The engine maintains current prices for all symbols:

```python
# Internal implementation
current_prices = {symbol: 0.0 for symbol in self._symbols}

for tick in self._ticks:
    # Update price for this symbol
    current_prices[tick.symbol] = tick.price
    
    # Now all strategies can get portfolio value with current prices
    value = portfolio.get_value(current_prices)
```

This ensures accurate portfolio valuation even when ticks for different symbols arrive at different times.

### Custom Execution Logic

You can extend the engine for custom behavior:

```python
class CustomExecutionEngine(ExecutionEngine):
    """Extended engine with transaction costs."""
    
    def execute_order(self, name: str, order: Order) -> None:
        # Call parent implementation
        super().execute_order(name, order)
        
        # Deduct transaction costs (0.1% of trade value)
        commission = abs(order.quantity * order.price) * 0.001
        self._states[name].portfolio.cash -= commission
```

---

## Performance Considerations

### Time Complexity

**Overall**: O(n × s) where:
- n = number of ticks
- s = number of strategies

**Per Tick Operations**:
- Signal generation: O(1) amortized (for most strategies)
- Order creation: O(1)
- Order execution: O(1)
- Portfolio valuation: O(m) where m = number of symbols

### Space Complexity

**Memory Usage**: O(n × s) for storing complete history

**Breakdown**:
- Order list: O(n × s) in worst case (order every tick, every strategy)
- History: O(n × s) (value recorded per tick per strategy)
- Error logs: O(e) where e = number of errors

### Optimization Tips

#### 1. Limit History Storage

For very long backtests, consider sampling history:

```python
# Record value every N ticks instead of every tick
if tick_count % sampling_interval == 0:
    state.history.append((current_time, value))
```

#### 2. Batch Processing

For production systems, consider batching strategies:

```python
# Process strategies in parallel (requires threading/multiprocessing)
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [
        executor.submit(process_strategy, strategy, tick)
        for strategy in strategies
    ]
```

#### 3. Efficient Data Structures

The engine already uses efficient structures:
- Dictionary lookups: O(1)
- List appends: O(1) amortized
- Sorted ticks: One-time O(n log n) cost

### Memory Management

For large-scale backtests:

```python
# Clear unnecessary data after processing
for state in states.values():
    # Keep only essential data
    state.strategy._prices.clear()  # Clear indicator buffers
    state.strategy._short_ma.clear()
    state.strategy._long_ma.clear()
```

---

## Complete Usage Example

```python
from engine import ExecutionEngine
from strategies import MACDStrategy, MomentumStrategy
from data_loader import data_ingestor
from reporting import generate_report
from pathlib import Path

# 1. Load data
print("Loading market data...")
ticks = data_ingestor('market_data.csv')
print(f"Loaded {len(ticks)} ticks")

# 2. Create strategies
print("Initializing strategies...")
strategies = [
    MACDStrategy(
        ticks=ticks,
        params={'short_period': 12, 'long_period': 26}
    ),
    MomentumStrategy(
        ticks=ticks,
        params={'lookback': 20, 'buy_threshold': 0.02, 'sell_threshold': -0.02}
    )
]

# 3. Initialize engine
print("Creating execution engine...")
engine = ExecutionEngine(
    ticks=ticks,
    strategies=strategies,
    init_cash=1_000_000
)

# 4. Run backtest
print("Running backtest...")
states = engine.run()

# 5. Analyze results
print("\n" + "="*60)
print("BACKTEST RESULTS")
print("="*60)

for name, state in states.items():
    print(f"\nStrategy: {name}")
    print("-" * 60)
    
    # Orders
    total_orders = len(state.orders)
    successful = sum(1 for o in state.orders if o.status == 'success')
    failed = sum(1 for o in state.orders if o.status == 'failed')
    
    print(f"Orders: {total_orders} total ({successful} successful, {failed} failed)")
    print(f"Order errors: {len(state.order_errors)}")
    print(f"Execution errors: {len(state.execution_errors)}")
    
    # Performance
    if state.history:
        initial = state.history[0][1]
        final = state.history[-1][1]
        returns = (final / initial - 1) * 100
        
        print(f"Initial value: ${initial:,.2f}")
        print(f"Final value: ${final:,.2f}")
        print(f"Return: {returns:+.2f}%")
    
    # Positions
    print(f"Final cash: ${state.portfolio.cash:,.2f}")
    print("Positions:")
    for symbol, pos in state.portfolio.positions.items():
        if pos.quantity > 0:
            print(f"  {symbol}: {pos.quantity} shares @ ${pos.avg_price:.2f}")

# 6. Generate reports
print("\nGenerating reports...")
generate_report(
    names=states.keys(),
    states=states,
    img_dir=Path('output/images'),
    doc_dir=Path('output/reports')
)

print("Done! Check the output directory for reports.")
```

---

## Summary

### Key Points

1. **Chronological Processing**: All data processed in timestamp order
2. **Independent Strategies**: Each strategy has isolated state and portfolio
3. **Robust Error Handling**: Validation and execution failures logged but don't stop backtest
4. **Complete State Tracking**: All orders, errors, and values recorded
5. **Realistic Simulation**: Includes random execution failures

### Best Practices

- Validate your data is sorted before passing to engine
- Check error logs after backtest to identify issues
- Monitor both successful and failed orders
- Use multiple strategies to compare approaches
- Analyze complete history for performance insights

### Next Steps

- Review **[Strategies Guide](STRATEGIES.md)** for strategy implementation
- See **[Reporting & Analytics](REPORTING.md)** for performance analysis
- Check **[API Reference](API_REFERENCE.md)** for detailed method documentation

---

*The execution engine is the heart of the backtesting system. Understanding its operation is key to effective strategy development and testing.*
