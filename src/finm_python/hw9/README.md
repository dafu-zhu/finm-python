# Assignment 9: Mini Trading System

**Due: Tue Nov 18, 2025 11:59pm**

**100 Points Possible**

## Overview

This project implements a mini trading system with four core components that work together to process trading orders. You will build each component incrementally and then integrate them into a complete end-to-end system.

### System Architecture

```
FIX Message → Parser → Order Object → Risk Engine → Event Logger
                                          ↓
                                    Position Updates
```

## Components

### Part 1: FIX Message Parser (`fix_parser.py`)

**Purpose**: Convert raw FIX protocol strings into structured Python dictionaries.

**Key Concepts**: String parsing, dictionaries, validation

**TODO**:
- [ ] Implement `parse()` method to split FIX messages and extract tag-value pairs
- [ ] Implement `validate_required_tags()` to check for required fields
- [ ] Handle missing tags by raising `ValueError` with descriptive messages
- [ ] Implement `get_message_type()` helper method
- [ ] Test with both order and quote messages

**FIX Resources**:
- [FIX Parser Tool](https://fixparser.targetcompid.com/)
- [FIX Message Reference](https://ref.onixs.biz/fix-message.html)

**Common FIX Tags**:
- `8`: BeginString (FIX version)
- `35`: MsgType (D=NewOrderSingle, 8=ExecutionReport)
- `55`: Symbol
- `54`: Side (1=Buy, 2=Sell)
- `38`: OrderQty
- `40`: OrdType (1=Market, 2=Limit)
- `44`: Price
- `10`: CheckSum

### Part 2: Order Lifecycle Simulator (`order.py`)

**Purpose**: Manage order state transitions from creation to completion.

**Key Concepts**: State machines, enums, class design

**State Machine**:
```
NEW ──┬──> ACKED ──┬──> FILLED
      │            │
      └──> REJECTED│
                   └──> CANCELED
```

**TODO**:
- [ ] Implement `Order` class with proper initialization
- [ ] Implement `transition()` method with state validation
- [ ] Define allowed transitions dictionary
- [ ] Implement `fill()` method for partial and full fills
- [ ] Implement `cancel()` method
- [ ] Implement helper methods: `is_terminal_state()`, `get_side_name()`
- [ ] Add `__str__()` and `__repr__()` for debugging

### Part 3: Risk Check Engine (`risk_engine.py`)

**Purpose**: Validate orders against position and size limits before execution.

**Key Concepts**: Validation logic, exceptions, position tracking

**Risk Checks**:
1. **Order Size**: Single order cannot exceed `max_order_size`
2. **Position Limit**: Total position cannot exceed `max_position` (considering direction)

**TODO**:
- [ ] Implement `check()` method to validate both order size and position limits
- [ ] Calculate new position considering buy/sell direction
- [ ] Raise `ValueError` with descriptive messages for violations
- [ ] Implement `update_position()` to track positions per symbol
- [ ] Implement `get_position()` to query current positions
- [ ] Implement `get_available_capacity()` helper
- [ ] Support multiple symbols independently

### Part 4: Event Logger (`logger.py`)

**Purpose**: Record all system events for replay and analysis.

**Key Concepts**: Structured logging, JSON serialization, singleton pattern

**TODO**:
- [ ] Implement singleton pattern in `__new__()` method
- [ ] Implement `log()` method to record events with timestamps
- [ ] Create event dictionaries with `timestamp`, `event_type`, and `data`
- [ ] Implement `save()` to write events to JSON file
- [ ] Implement `load()` to read events from JSON file
- [ ] Implement filtering methods: `get_events_by_type()`, `get_events_for_symbol()`
- [ ] Implement utility methods: `clear()`, `print_summary()`, `replay_events()`

## Integration: `main.py`

**Purpose**: Orchestrate all components into a complete trading system.

### TradingSystem Class

**TODO**:
- [ ] Implement `__init__()` to create all component instances
- [ ] Implement `process_fix_message()` for complete order flow
- [ ] Implement `fill_order()` to execute orders
- [ ] Implement `cancel_order()` for order cancellation
- [ ] Implement query methods: `get_order()`, `get_all_orders()`, `get_orders_by_state()`
- [ ] Implement `print_status()` for system monitoring
- [ ] Implement `shutdown()` to save logs gracefully

### Example Usage

The system should handle orders like this:

```python
system = TradingSystem(max_order_size=1000, max_position=2000)

# Process a FIX message
msg = "8=FIX.4.2|35=D|55=AAPL|54=1|38=500|40=2|44=150.00|10=128"
order = system.process_fix_message(msg)

# Fill the order if it was acknowledged
if order.state == OrderState.ACKED:
    system.fill_order(order.order_id)

# Save all events
system.shutdown()
```

## Testing Requirements

### Unit Tests

Create comprehensive unit tests for each component:

1. **`test_fix_parser.py`**: Test message parsing, validation, edge cases
2. **`test_order.py`**: Test state transitions, fills, cancellations
3. **`test_risk_engine.py`**: Test risk checks, position tracking
4. **`test_logger.py`**: Test logging, persistence, filtering
5. **`test_integration.py`**: Test complete system flows

**TODO**:
- [ ] Write unit tests for all public methods
- [ ] Test both success and failure cases
- [ ] Test edge cases and boundary conditions
- [ ] Achieve high code coverage (aim for >80%)
- [ ] Use pytest fixtures to reduce code duplication
- [ ] Test error handling and exception messages

### Running Tests

```bash
# Run all tests
pytest src/finm_python/hw9/tests/

# Run with coverage
pytest --cov=src/finm_python/hw9 --cov-report=term-missing src/finm_python/hw9/tests/

# Run specific test file
pytest src/finm_python/hw9/tests/test_fix_parser.py

# Run with verbose output
pytest -v src/finm_python/hw9/tests/
```

## Submission Requirements

Submit the following files:

- [ ] `fix_parser.py` - FIX message parser implementation
- [ ] `order.py` - Order lifecycle simulator
- [ ] `risk_engine.py` - Risk check engine
- [ ] `logger.py` - Event logger
- [ ] `main.py` - System integration and examples
- [ ] `tests/test_fix_parser.py` - Parser unit tests
- [ ] `tests/test_order.py` - Order unit tests
- [ ] `tests/test_risk_engine.py` - Risk engine unit tests
- [ ] `tests/test_logger.py` - Logger unit tests
- [ ] `tests/test_integration.py` - Integration tests
- [ ] `coverage_report.md` - Test coverage report and analysis
- [ ] `events.json` - Sample output from running the system

## Getting Started

1. **Start with Part 1** - Get the FIX parser working first
   - Run the `fix_parser.py` main function to test manually
   - Write unit tests as you implement each method

2. **Move to Part 2** - Implement the Order state machine
   - Test each state transition individually
   - Verify invalid transitions are rejected

3. **Implement Part 3** - Build the risk engine
   - Start with order size checks (simpler)
   - Then add position tracking
   - Test with multiple symbols

4. **Add Part 4** - Create the logger
   - Test singleton pattern works correctly
   - Verify JSON serialization
   - Test filtering methods

5. **Integrate in `main.py`** - Bring it all together
   - Start with single message example
   - Expand to multiple messages
   - Add error handling

6. **Write Tests** - Comprehensive test coverage
   - Write tests as you go (don't save for the end!)
   - Aim for >80% coverage
   - Test edge cases and error conditions

## Tips for Success

1. **Read the Scaffolding Comments**: Each TODO comment explains what to implement
2. **Test Incrementally**: Don't write everything before testing
3. **Use Type Hints**: They're already in the scaffolding - they help catch errors
4. **Print for Debugging**: Use print statements to understand flow during development
5. **Study the Examples**: The main() functions show expected usage
6. **Ask Questions**: If requirements are unclear, ask!

## Expected Output Example

```
Mini Trading System
============================================================

Processing message 1...
[LOG] OrderCreated = {'55': 'AAPL', '38': '500', '54': '1', ...}
Order AAPL is now ACKED
Position update: AAPL = 500 shares
Order AAPL is now FILLED
[LOG] OrderFilled = {'symbol': 'AAPL', 'qty': 500}

Processing message 2...
[LOG] OrderCreated = {'55': 'AAPL', '38': '2000', '54': '1', ...}
Risk check failed: Order quantity 2000 exceeds maximum 1000
Order AAPL is now REJECTED
[LOG] OrderRejected = {'reason': 'Order size exceeds limit'}

System Status:
- Orders: 2 total (1 FILLED, 1 REJECTED)
- Positions: AAPL = 500
- Events logged: 4

Saved 4 events to events.json
```

## Grading Rubric

| Component | Points |
|-----------|--------|
| FIX Parser working correctly | 20 |
| Order state machine implementation | 20 |
| Risk engine with proper checks | 20 |
| Event logger with persistence | 20 |
| Integration and main.py | 10 |
| Unit tests with >80% coverage | 10 |
| Code quality and documentation | 10 |
| **Total** | **100** |

## Academic Integrity

This is an individual assignment. You may discuss concepts with classmates, but all code must be your own. Do not share code or copy from others.

Good luck! 🚀
