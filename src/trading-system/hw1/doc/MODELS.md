# Models Documentation

## Overview

This module defines the core data models and portfolio management components for a trading system. It provides classes for managing orders, positions, and portfolio state, along with custom exception types for error handling.

## Table of Contents

- [Data Models](#data-models)
  - [Order](#order)
  - [Position](#position)
- [Portfolio Management](#portfolio-management)
  - [Portfolio](#portfolio)
- [Custom Exceptions](#custom-exceptions)
- [Usage Examples](#usage-examples)

---

## Data Models

### Order

A dataclass representing a trading order with validation.

**Attributes:**

- `symbol` (str): The ticker symbol of the security being traded
- `quantity` (int): Number of shares/units in the order
- `price` (float): Price per unit for the order
- `status` (str): Current order status, must be one of:
  - `'pending'` - Order submitted but not yet executed
  - `'filled'` - Order successfully executed
  - `'rejected'` - Order rejected by the system

**Validation:**

The `__post_init__` method automatically validates that the price is positive. If the price is zero or negative, an `OrderError` is raised.

**Example:**

```python
# Valid order
order = Order(symbol="AAPL", quantity=100, price=150.50, status="pending")

# Invalid order - raises OrderError
order = Order(symbol="AAPL", quantity=100, price=-10.0, status="pending")
```

---

### Position

A dataclass representing a position held in a portfolio.

**Attributes:**

- `symbol` (str): The ticker symbol of the security
- `quantity` (int): Number of shares/units held (default: 0)
- `avg_price` (float): Average purchase price per unit (default: 0.0)

**Notes:**

- A quantity of 0 indicates no position
- The average price is used for calculating unrealized P&L
- Negative quantities could represent short positions (implementation dependent)

**Example:**

```python
# Empty position
position = Position(symbol="GOOGL")

# Position with holdings
position = Position(symbol="GOOGL", quantity=50, avg_price=2800.00)
```

---

## Portfolio Management

### Portfolio

A class managing cash balance, positions, and portfolio valuation.

**Constructor:**

```python
Portfolio(init_cash: float, symbols: list)
```

**Parameters:**

- `init_cash`: Starting cash balance for the portfolio
- `symbols`: List of ticker symbols to track in the portfolio

**Attributes:**

- `cash` (float): Current cash balance
- `positions` (Dict[str, Position]): Dictionary mapping symbols to Position objects

**Methods:**

#### update_position

Updates a position after a trade execution.

```python
def update_position(self, symbol: str, qty: int, price: float) -> None
```

**Parameters:**

- `symbol`: Ticker symbol of the traded security
- `qty`: Quantity traded (positive for buys, negative for sells)
- `price`: Execution price per unit

**Behavior:**

- For buy orders (qty > 0): Calculates new average price using weighted average formula
- For sell orders (qty < 0): Maintains the existing average price
- Updates the position quantity
- Adjusts cash balance by deducting `qty × price`

**Formula for Average Price (Buy):**

```
new_avg_price = (old_avg_price × old_quantity + price × qty) / (old_quantity + qty)
```

#### get_value

Calculates the total portfolio value (cash + positions).

```python
def get_value(self, price_dict: Dict[str, float]) -> float
```

**Parameters:**

- `price_dict`: Dictionary mapping symbols to their current market prices

**Returns:**

- Total portfolio value in currency units

**Calculation:**

```
total_value = cash + Σ(position_quantity × current_price)
```

---

## Custom Exceptions

### OrderError

Raised when an order contains invalid parameters (e.g., negative price).

**Usage:**

```python
raise OrderError(f"Invalid price: {price}")
```

### ExecutionError

Exception type for errors occurring during trade execution. Currently defined but not implemented in this module.

### ConfigError

Exception type for configuration-related errors. Currently defined but not implemented in this module.

---

## Usage Examples

### Creating a Portfolio

```python
# Initialize portfolio with $100,000 and track 3 stocks
portfolio = Portfolio(
    init_cash=100000.0,
    symbols=["AAPL", "GOOGL", "MSFT"]
)
```

### Executing a Buy Order

```python
# Buy 100 shares of AAPL at $150
portfolio.update_position(symbol="AAPL", qty=100, price=150.0)

# Cash reduced by: 100 × 150 = $15,000
# New cash balance: $85,000
```

### Executing a Sell Order

```python
# Sell 50 shares of AAPL at $155
portfolio.update_position(symbol="AAPL", qty=-50, price=155.0)

# Cash increased by: 50 × 155 = $7,750
# New cash balance: $92,750
```

### Calculating Portfolio Value

```python
# Current market prices
current_prices = {
    "AAPL": 160.0,
    "GOOGL": 2850.0,
    "MSFT": 380.0
}

total_value = portfolio.get_value(current_prices)
print(f"Total Portfolio Value: ${total_value:,.2f}")
```

### Complete Workflow

```python
# 1. Create portfolio
portfolio = Portfolio(init_cash=50000.0, symbols=["AAPL", "TSLA"])

# 2. Create and validate an order
try:
    order = Order(symbol="AAPL", quantity=100, price=150.0, status="pending")
    print("Order created successfully")
except OrderError as e:
    print(f"Order validation failed: {e}")

# 3. Execute the order
portfolio.update_position(symbol="AAPL", qty=100, price=150.0)

# 4. Check position
aapl_position = portfolio.positions["AAPL"]
print(f"AAPL Position: {aapl_position.quantity} shares at ${aapl_position.avg_price:.2f}")

# 5. Calculate portfolio value
prices = {"AAPL": 155.0, "TSLA": 250.0}
value = portfolio.get_value(prices)
print(f"Portfolio Value: ${value:,.2f}")
```

---

## Important Notes

**Limitations:**

1. **No transaction costs**: The current implementation doesn't account for commissions or fees
2. **No position limits**: No validation for maximum position sizes or leverage
3. **No cash validation**: The system allows cash to go negative (margin trading)
4. **Sell price handling**: When selling, the average price is not adjusted (FIFO/LIFO not specified)

**Potential Improvements:**

- Add transaction cost calculations
- Implement cash balance validation
- Add position size limits
- Support for different accounting methods (FIFO, LIFO, Average Cost)
- Add methods for calculating P&L (realized and unrealized)
- Timestamp tracking for positions and trades
- Support for fractional shares

---

## Dependencies

- `dataclasses`: For `@dataclass` decorator
- `typing`: For type hints (Dict, List, Tuple)

**Python Version:** Requires Python 3.7+ for dataclass support

---

## Thread Safety

This implementation is **not thread-safe**. If used in a multi-threaded environment, external synchronization is required when accessing or modifying portfolio state.

---

## License

Refer to the project's LICENSE file for usage terms and conditions.