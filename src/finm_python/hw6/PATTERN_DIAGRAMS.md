# Design Pattern Diagrams - HW6

This document provides visual diagrams for all design patterns implemented in the HW6 financial software architecture project.

## Table of Contents
- [Creational Patterns](#creational-patterns)
  - [Factory Pattern](#factory-pattern)
  - [Singleton Pattern](#singleton-pattern)
  - [Builder Pattern](#builder-pattern)
- [Structural Patterns](#structural-patterns)
  - [Decorator Pattern](#decorator-pattern)
  - [Adapter Pattern](#adapter-pattern)
  - [Composite Pattern](#composite-pattern)
- [Behavioral Patterns](#behavioral-patterns)
  - [Strategy Pattern](#strategy-pattern)
  - [Observer Pattern](#observer-pattern)
  - [Command Pattern](#command-pattern)

---

## Creational Patterns

### Factory Pattern

**Purpose:** Create instrument instances from raw data without exposing instantiation logic.

```
┌─────────────────────────────────────────────────────────────┐
│                    InstrumentFactory                        │
├─────────────────────────────────────────────────────────────┤
│ + create_instrument(data: dict) → Instrument                │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ creates
                            ↓
                    ┌──────────────┐
                    │  Instrument  │ (Abstract)
                    ├──────────────┤
                    │ + symbol     │
                    │ + price      │
                    └──────────────┘
                            △
                            │
            ┌───────────────┼───────────────┐
            │               │               │
    ┌───────▼──────┐ ┌──────▼──────┐ ┌─────▼────────┐
    │    Stock     │ │    Bond     │ │     ETF      │
    ├──────────────┤ ├─────────────┤ ├──────────────┤
    │ + sector     │ │ + issuer    │ │ + sector     │
    │ + issuer     │ │ + maturity  │ │ + issuer     │
    │              │ │ + coupon    │ │ + exp_ratio  │
    └──────────────┘ └─────────────┘ └──────────────┘
```

**Example Flow:**
```
Client Code
    │
    │ data = {"type": "Stock", "symbol": "AAPL", ...}
    │
    └──> InstrumentFactory.create_instrument(data)
              │
              │ Check type field
              │
              ├──> "stock" → return Stock(...)
              ├──> "bond"  → return Bond(...)
              └──> "etf"   → return ETF(...)
```

**Key Benefits:**
- Centralized creation logic
- Easy to add new instrument types
- Client code doesn't depend on concrete classes

---

### Singleton Pattern

**Purpose:** Ensure only one Config instance exists throughout the application.

```
┌─────────────────────────────────────────────────────────────┐
│                         Config                              │
├─────────────────────────────────────────────────────────────┤
│ - _instance: Config (class variable)                        │
│ - _initialized: bool                                        │
│ - _data: dict                                               │
├─────────────────────────────────────────────────────────────┤
│ + __new__() → Config                                        │
│ + get_instance() → Config                                   │
│ + load(filepath: str)                                       │
│ + get(key: str, default: Any) → Any                         │
│ + set(key: str, value: Any)                                 │
│ + get_all() → dict                                          │
│ + reset()                                                   │
└─────────────────────────────────────────────────────────────┘
```

**Singleton Pattern Flow:**
```
First Call:                    Second Call:
   │                              │
   │ Config.get_instance()        │ Config.get_instance()
   │                              │
   ├──> _instance is None?        ├──> _instance exists?
   │    YES                       │    YES
   │                              │
   └──> Create new instance       └──> Return existing instance
        Store in _instance             (same object)
        Return instance


Module A              Module B              Module C
   │                     │                     │
   └──> config1 ─────────┼─────> config2 ──────┼──> config3
                         │                     │
                    SAME OBJECT (singleton)
                    All point to _instance
```

**Key Benefits:**
- Global configuration state
- Single source of truth
- No need to pass config objects everywhere

---

### Builder Pattern

**Purpose:** Construct complex portfolio structures with a fluent interface.

```
┌─────────────────────────────────────────────────────────────┐
│                    PortfolioBuilder                         │
├─────────────────────────────────────────────────────────────┤
│ - name: str                                                 │
│ - owner: str                                                │
│ - root: PortfolioGroup                                      │
├─────────────────────────────────────────────────────────────┤
│ + __init__(name: str)                                       │
│ + set_owner(name: str) → PortfolioBuilder                   │
│ + add_position(symbol, qty, price) → PortfolioBuilder       │
│ + add_subportfolio(name, builder) → PortfolioBuilder        │
│ + build() → Portfolio                                       │
│ + from_dict(data: dict) → PortfolioBuilder                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ builds
                            ↓
                    ┌──────────────┐
                    │  Portfolio   │
                    ├──────────────┤
                    │ + name       │
                    │ + owner      │
                    │ + root       │
                    └──────────────┘
```

**Fluent Interface Example:**
```
portfolio = (PortfolioBuilder("Main")
             .set_owner("jdoe")                    ← returns self
             .add_position("AAPL", 100, 172.35)    ← returns self
             .add_position("MSFT", 50, 328.10)     ← returns self
             .add_subportfolio("ETFs",             ← returns self
                 PortfolioBuilder("ETF Group")
                 .add_position("SPY", 20, 430.50))
             .build())                             ← returns Portfolio
```

**Construction Flow:**
```
Step 1: Create Builder         Step 2: Configure           Step 3: Build
    │                              │                           │
PortfolioBuilder("Main")       set_owner("jdoe")            build()
    │                              │                           │
    └─> root = PortfolioGroup  add_position(...)               └─> Portfolio
                                   │                               - name
                                   └─> Position added              - owner
                                   add_subportfolio(...)           - root
                                       │
                                       └─> PortfolioGroup added
```

**Key Benefits:**
- Readable, chainable API
- Supports complex nested structures
- Separates construction from representation

---

## Structural Patterns

### Decorator Pattern

**Purpose:** Add analytics capabilities to instruments without modifying base classes.

```
                     ┌──────────────┐
                     │  Instrument  │ (Abstract)
                     ├──────────────┤
                     │ + symbol     │
                     │ + price      │
                     │ + get_type() │
                     │ + get_metrics() │
                     └──────────────┘
                            △
                            │
            ┌───────────────┼───────────────┐
            │               │               │
    ┌───────┴──────┐        │        ┌──────────────────────┐
    │    Stock     │        │        │ InstrumentDecorator  │
    │    Bond      │        │        ├──────────────────────┤
    │    ETF       │        │        │ - _instrument        │
    └──────────────┘        │        └──────────────────────┘
                            │                   △
                            │                   │
                            └───────────────────┘
                                                │
                    ┌───────────────────────────┼───────────────────────────┐
                    │                           │                           │
        ┌───────────▼──────────┐   ┌───────────▼──────────┐   ┌────────────▼──────────┐
        │ VolatilityDecorator  │   │   BetaDecorator      │   │  DrawdownDecorator    │
        ├──────────────────────┤   ├──────────────────────┤   ├───────────────────────┤
        │ - historical_returns │   │ - instrument_returns │   │ - price_history       │
        │                      │   │ - market_returns     │   │                       │
        ├──────────────────────┤   ├──────────────────────┤   ├───────────────────────┤
        │ + calculate_         │   │ + calculate_beta()   │   │ + calculate_max_      │
        │   volatility()       │   │ + get_metrics()      │   │   drawdown()          │
        │ + get_metrics()      │   │                      │   │ + get_metrics()       │
        └──────────────────────┘   └──────────────────────┘   └───────────────────────┘
```

**Decorator Stacking:**
```
        Original Object              After 1st Decorator         After 2nd Decorator
┌──────────────────────┐      ┌──────────────────────┐    ┌──────────────────────┐
│       Stock          │      │ VolatilityDecorator  │    │   BetaDecorator      │
│  "AAPL" @ $172.35    │ ───> │   wraps Stock        │ ──>│ wraps Volatility     │
│                      │      │   + volatility       │    │   + beta             │
└──────────────────────┘      └──────────────────────┘    └──────────────────────┘
      get_metrics()              get_metrics()                get_metrics()
      {"price": 172.35}          {"price": 172.35,            {"price": 172.35,
                                  "volatility": 0.25}          "volatility": 0.25,
                                                               "beta": 1.05}
```

**Usage Pattern:**
```python
stock = Stock("AAPL", 172.35, "Technology", "Apple Inc.")
# Base metrics: {"symbol": "AAPL", "price": 172.35, "type": "Stock"}

stock = VolatilityDecorator(stock, historical_returns)
# Adds: {"volatility": 0.25}

stock = BetaDecorator(stock, historical_returns, market_returns)
# Adds: {"beta": 1.05}

stock = DrawdownDecorator(stock, price_history)
# Adds: {"max_drawdown": -0.15}
```

**Key Benefits:**
- Add features without modifying original classes
- Flexible combination of capabilities
- Single responsibility for each decorator

---

### Adapter Pattern

**Purpose:** Convert external data formats into standardized MarketDataPoint format.

```
External Data Sources                    Adapters                      Internal Format
┌────────────────────┐            ┌──────────────────┐           ┌──────────────────┐
│  Yahoo Finance     │            │ MarketDataAdapter│           │ MarketDataPoint  │
│  JSON Format       │            │   (Abstract)     │           ├──────────────────┤
│ ┌────────────────┐ │            ├──────────────────┤           │ + symbol         │
│ │ ticker         │ │            │ + get_data()     │           │ + price          │
│ │ last_price     │ │            └──────────────────┘           │ + timestamp      │
│ │ timestamp      │ │                     △                     │ + metadata       │
│ │ volume         │ │                     │                     └──────────────────┘
│ └────────────────┘ │         ┌───────────┴───────────┐                 △
└────────────────────┘         │                       │                 │
         │                     │                       │                 │
         │              ┌──────▼──────────┐   ┌────────▼────────┐        │
         └─────────────>│ YahooFinance    │   │  BloombergXML   │────────┘
                        │    Adapter      │   │    Adapter      │
┌────────────────────┐  ├─────────────────┤   ├─────────────────┤
│   Bloomberg        │  │ - _data (JSON)  │   │ - _root (XML)   │
│   XML Format       │  ├─────────────────┤   ├─────────────────┤
│ ┌────────────────┐ │  │ + get_data()    │   │ + get_data()    │
│ │ <symbol>       │ │  │   → parse JSON  │   │   → parse XML   │
│ │ <price>        │ ├─>│   → convert to  │   │   → convert to  │
│ │ <timestamp>    │ │  │     MarketData  │   │     MarketData  │
│ └────────────────┘ │  └─────────────────┘   └─────────────────┘
└────────────────────┘
```

**Adaptation Flow:**
```
Yahoo JSON                           Adapter Processing                    Result
┌────────────────────┐              ┌───────────────────┐          ┌─────────────────┐
│ {                  │              │ 1. Parse JSON     │          │ MarketDataPoint │
│   "ticker": "AAPL",│  ──────────> │ 2. Extract fields │ ───────> │   symbol="AAPL" │
│   "last_price": 172.35,│          │ 3. Convert types  │          │   price=172.35  │
│   "timestamp": "..." │            │ 4. Create object  │          │   timestamp=... │
│ }                  │              └───────────────────┘          └─────────────────┘
└────────────────────┘

Bloomberg XML                        Adapter Processing                    Result
┌────────────────────┐              ┌───────────────────┐          ┌─────────────────┐
│ <instrument>       │              │ 1. Parse XML      │          │ MarketDataPoint │
│   <symbol>AAPL...  │  ──────────> │ 2. Find elements  │ ───────> │   symbol="AAPL" │
│   <price>172.35... │              │ 3. Extract text   │          │   price=172.35  │
│   <timestamp>...   │              │ 4. Create object  │          │   timestamp=... │
│ </instrument>      │              └───────────────────┘          └─────────────────┘
└────────────────────┘
```

**Key Benefits:**
- Unified internal data format
- Easy to add new data sources
- External format changes don't affect internal code

---

### Composite Pattern

**Purpose:** Model portfolios as trees of individual positions and sub-portfolios.

```
                        ┌──────────────────────┐
                        │ PortfolioComponent   │ (Abstract)
                        ├──────────────────────┤
                        │ + get_value()        │
                        │ + get_positions()    │
                        └──────────────────────┘
                                   △
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
          ┌─────────▼─────────┐         ┌─────────▼─────────┐
          │     Position      │         │  PortfolioGroup   │
          │      (Leaf)       │         │   (Composite)     │
          ├───────────────────┤         ├───────────────────┤
          │ + symbol          │         │ + name            │
          │ + quantity        │         │ + components: []  │
          │ + price           │         │                   │
          ├───────────────────┤         ├───────────────────┤
          │ + get_value()     │         │ + add(component)  │
          │   = qty * price   │         │ + remove(comp)    │
          │                   │         │ + get_value()     │
          │ + get_positions() │         │   = Σ child.value │
          │   = [self]        │         │                   │
          └───────────────────┘         │ + get_positions() │
                                        │   = flatten all   │
                                        └───────────────────┘
```

**Hierarchical Structure Example:**
```
                    ┌─────────────────────────────┐
                    │   Main Portfolio            │
                    │   Total: $45,395.00         │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
          ┌─────────▼─────┐ ┌──────▼──────┐ ┌────▼─────────────┐
          │ Position      │ │ Position    │ │ Tech Holdings    │
          │ AAPL          │ │ MSFT        │ │ (Sub-portfolio)  │
          │ 100 @ $172.35 │ │ 50 @ $328.10│ └────┬─────────────┘
          │ = $17,235     │ │ = $16,405   │      │
          └───────────────┘ └─────────────┘      │
                                           ┌─────┴─────┐
                                           │           │
                                    ┌──────▼──────┐ ┌──▼──────────┐
                                    │ Position    │ │ Position    │
                                    │ GOOGL       │ │ META        │
                                    │ 25 @ $141.50│ │ 30 @ $345.20│
                                    │ = $3,537.50 │ │ = $10,356   │
                                    └─────────────┘ └─────────────┘
```

**Recursive Operations:**
```
get_value() call on Main Portfolio
    │
    ├─> Position(AAPL).get_value()        → 17,235.00
    ├─> Position(MSFT).get_value()        → 16,405.00
    └─> PortfolioGroup(Tech).get_value()
            │
            ├─> Position(GOOGL).get_value() → 3,537.50
            └─> Position(META).get_value()  → 10,356.00
            │
            └─> Sum                         → 13,893.50
    │
    └─> Total Sum                          → 45,395.00
```

**Key Benefits:**
- Uniform treatment of simple and complex structures
- Natural recursive operations
- Easy to build arbitrary hierarchies

---

## Behavioral Patterns

### Strategy Pattern

**Purpose:** Support interchangeable trading algorithms at runtime.

```
                        ┌──────────────────────┐
                        │     Strategy         │ (Abstract)
                        ├──────────────────────┤
                        │ + generate_signals() │
                        │ + reset()            │
                        └──────────────────────┘
                                   △
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
      ┌─────────────▼────────────┐   ┌───────────▼────────────┐
      │ MeanReversionStrategy    │   │  BreakoutStrategy      │
      ├──────────────────────────┤   ├────────────────────────┤
      │ - lookback_window        │   │ - lookback_window      │
      │ - threshold              │   │ - threshold            │
      │ - price_history: []      │   │ - price_history: []    │
      ├──────────────────────────┤   ├────────────────────────┤
      │ + generate_signals()     │   │ + generate_signals()   │
      │   Logic:                 │   │   Logic:               │
      │   - Calculate MA         │   │   - Find high/low      │
      │   - Check deviation      │   │   - Detect breakout    │
      │   - BUY if << MA         │   │   - BUY if > high      │
      │   - SELL if >> MA        │   │   - SELL if < low      │
      │ + reset()                │   │ + reset()              │
      └──────────────────────────┘   └────────────────────────┘
```

**Strategy Selection:**
```
Client Code
    │
    ├─> Choose Strategy at Runtime
    │
    ├─> Option 1: MeanReversionStrategy(lookback=20, threshold=0.02)
    │       │
    │       └─> Signals based on moving average deviation
    │
    └─> Option 2: BreakoutStrategy(lookback=15, threshold=0.03)
            │
            └─> Signals based on range breakouts


Market Data Flow:
    ┌──────────────┐
    │ Market Tick  │
    │ AAPL @ $100  │
    └──────┬───────┘
           │
           ├──────> MeanReversionStrategy ──> BUY (below MA)
           │
           └──────> BreakoutStrategy ──────> No signal (no breakout)
```

**Signal Generation Example:**
```
MeanReversionStrategy (threshold=0.02, window=5)
─────────────────────────────────────────────────
Price History: [100, 102, 98, 105, 95]
Current Price: 95
Moving Average: (100+102+98+105+95)/5 = 100
Deviation: (95-100)/100 = -5%
Result: BUY signal (deviation < -2%)

BreakoutStrategy (threshold=0.03, window=5)
───────────────────────────────────────────
Price History: [100, 102, 98, 105, 95]
Current Price: 110
High: 105, Low: 95
Breakout Check: 110 > 105*(1+0.03) = 108.15
Result: BUY signal (upward breakout)
```

**Key Benefits:**
- Swap algorithms at runtime
- Easy to add new strategies
- Each strategy is independently testable

---

### Observer Pattern

**Purpose:** Decouple signal generation from signal handling through event notifications.

```
                    ┌──────────────────────┐
                    │  SignalPublisher     │ (Subject)
                    ├──────────────────────┤
                    │ - _observers: []     │
                    ├──────────────────────┤
                    │ + attach(observer)   │
                    │ + detach(observer)   │
                    │ + notify(signal)     │
                    └──────────┬───────────┘
                               │ manages
                               │
                    ┌──────────▼───────────┐
                    │     Observer         │ (Abstract)
                    ├──────────────────────┤
                    │ + update(signal)     │
                    └──────────────────────┘
                               △
                               │
                ┌──────────────┼──────────────┐
                │              │              │
    ┌───────────▼────────┐     │     ┌────────▼─────────┐
    │  LoggerObserver    │     │     │  AlertObserver   │
    ├────────────────────┤     │     ├──────────────────┤
    │ - log_file         │     │     │ - price_threshold│
    │ - logs: []         │     │     │ - alerts: []     │
    ├────────────────────┤     │     ├──────────────────┤
    │ + update(signal)   │     │     │ + update(signal) │
    │   → log to file/   │     │     │   → check thresh │
    │     console        │     │     │   → alert if big │
    └────────────────────┘     │     └──────────────────┘
                               │
                    ┌──────────▼────────────┐
                    │  Custom Observer      │
                    │  (easy to add more)   │
                    └───────────────────────┘
```

**Observer Pattern Flow:**
```
1. Setup Phase
   ───────────
   publisher = SignalPublisher()
   logger = LoggerObserver()
   alerter = AlertObserver(threshold=300)

   publisher.attach(logger)
   publisher.attach(alerter)

   ┌──────────────────┐
   │ SignalPublisher  │
   │ _observers:      │
   │   [logger,       │
   │    alerter]      │
   └──────────────────┘


2. Event Phase
   ───────────
   Signal Generated: {"type": "BUY", "symbol": "MSFT", "price": 328.10}

   publisher.notify(signal)
        │
        ├──> logger.update(signal)
        │      └─> Logs: "[2025-10-01] BUY MSFT @ $328.10"
        │
        └──> alerter.update(signal)
               └─> Alerts: "High-value trade alert: BUY MSFT @ $328.10"


3. Notification Flow
   ─────────────────

   Strategy                 Publisher               Observers
      │                         │                       │
      │ generate_signals()      │                       │
      └────────────────────────>│                       │
                                │                       │
                                │ notify(signal)        │
                                ├──────────────────────>│ LoggerObserver
                                │                       │   → log signal
                                │                       │
                                ├──────────────────────>│ AlertObserver
                                │                       │   → check threshold
                                │                       │   → send alert if needed
                                │<───────────────────────
                                │
```

**Key Benefits:**
- Loose coupling between publishers and subscribers
- Multiple observers can react independently
- Easy to add new observers without modifying publisher

---

### Command Pattern

**Purpose:** Encapsulate order execution as objects with undo/redo support.

```
                        ┌──────────────────────┐
                        │      Command         │ (Abstract)
                        ├──────────────────────┤
                        │ + execute()          │
                        │ + undo()             │
                        └──────────────────────┘
                                   △
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
      ┌─────────────▼────────────┐   ┌───────────▼────────────┐
      │ ExecuteOrderCommand      │   │ CancelOrderCommand     │
      ├──────────────────────────┤   ├────────────────────────┤
      │ - order: Order           │   │ - order: Order         │
      │ - _previous_status       │   │ - _previous_status     │
      ├──────────────────────────┤   ├────────────────────────┤
      │ + execute()              │   │ + execute()            │
      │   → status = "EXECUTED"  │   │   → status = "CANCELLED"│
      │   → save timestamp       │   │   → save prev state    │
      │                          │   │                        │
      │ + undo()                 │   │ + undo()               │
      │   → restore prev status  │   │   → restore prev status│
      │   → clear timestamp      │   │                        │
      └──────────────────────────┘   └────────────────────────┘
                    │
                    │ operates on
                    ↓
              ┌──────────┐
              │  Order   │
              ├──────────┤
              │ + order_id│
              │ + symbol │
              │ + type   │
              │ + quantity│
              │ + price  │
              │ + status │
              └──────────┘


                        ┌──────────────────────┐
                        │  CommandInvoker      │
                        ├──────────────────────┤
                        │ - _history: []       │
                        │ - _redo_stack: []    │
                        ├──────────────────────┤
                        │ + execute(command)   │
                        │ + undo()             │
                        │ + redo()             │
                        │ + get_history()      │
                        └──────────────────────┘
```

**Command Execution Flow:**
```
Initial State:
Order(ORD001, BUY 100 AAPL @ $172.35, status=PENDING)


1. Execute Command
   ───────────────
   invoker.execute(ExecuteOrderCommand(order))
        │
        ├──> command.execute()
        │      ├─ Save current status: _previous_status = "PENDING"
        │      ├─ Update order: status = "EXECUTED"
        │      └─ Set timestamp: executed_at = now()
        │
        └──> Add to history: [ExecuteOrderCommand]

   Order(ORD001, BUY 100 AAPL @ $172.35, status=EXECUTED)


2. Undo Command
   ────────────
   invoker.undo()
        │
        ├──> Pop from history: ExecuteOrderCommand
        │
        ├──> command.undo()
        │      ├─ Restore status: status = "PENDING" (from _previous_status)
        │      └─ Clear timestamp: executed_at = None
        │
        └──> Add to redo_stack: [ExecuteOrderCommand]

   Order(ORD001, BUY 100 AAPL @ $172.35, status=PENDING)


3. Redo Command
   ────────────
   invoker.redo()
        │
        ├──> Pop from redo_stack: ExecuteOrderCommand
        │
        ├──> command.execute()
        │      └─ Re-execute (status = "EXECUTED" again)
        │
        └──> Add back to history: [ExecuteOrderCommand]

   Order(ORD001, BUY 100 AAPL @ $172.35, status=EXECUTED)
```

**Command History Management:**
```
History Stack                    Redo Stack
─────────────                    ──────────

Initial:
  []                              []

After execute(cmd1):
  [cmd1]                          []

After execute(cmd2):
  [cmd1, cmd2]                    []

After undo():
  [cmd1]                          [cmd2]

After undo():
  []                              [cmd2, cmd1]

After redo():
  [cmd1]                          [cmd2]

After execute(cmd3):
  [cmd1, cmd3]                    []  ← redo stack cleared!
```

**Key Benefits:**
- Operations as first-class objects
- Built-in undo/redo support
- Audit trail of all operations
- Easy to add new command types

---

## Pattern Interactions

### How Patterns Work Together

```
┌─────────────────────────────────────────────────────────────────┐
│                    Application Architecture                     │
└─────────────────────────────────────────────────────────────────┘

Data Layer              Pattern Layer            Business Logic
──────────             ─────────────            ──────────────

CSV/JSON/XML              ADAPTER                Market Data
   Files          ──>   Standardizes      ──>   Processing
                         Data Formats


Instrument               FACTORY                 Portfolio
  Data            ──>    Creates         ──>     Construction
                        Instruments


Portfolio                BUILDER                 Complex
Structure        ──>    Constructs       ──>    Portfolios
                        Hierarchies


Base                   DECORATOR                Enhanced
Instruments      ──>   Adds Analytics   ──>    Instruments
                       (Vol, Beta, DD)


Configuration           SINGLETON               Global
  Files          ──>   Single Config    ──>    Settings
                        Instance


Portfolio                COMPOSITE              Hierarchical
 Hierarchy        ─>    Tree Structure   ─>    Calculations


Market                  STRATEGY                Trading
  Ticks          ──>   Signal Algos     ──>    Signals
                       (Mean Rev, BO)


Trading                 OBSERVER                Event
Signals          ──>   Notifications    ──>    Handling
                      (Log, Alert)


Order                   COMMAND                 Execution
Requests         ──>   Encapsulates     ──>    with Undo
                      Operations
```

### Example Integration Flow

```
Full Application Flow:
────────────────────

1. Load Configuration
   Config.get_instance().load("config.json")  ← SINGLETON

2. Load Market Data
   YahooFinanceAdapter("data.json")           ← ADAPTER
   → MarketDataPoint objects

3. Create Instruments
   InstrumentFactory.create_instrument(data)  ← FACTORY
   → Stock/Bond/ETF objects

4. Add Analytics
   VolatilityDecorator(                       ← DECORATOR
     BetaDecorator(stock))
   → Enhanced instruments

5. Build Portfolio
   PortfolioBuilder("Main")                   ← BUILDER
     .add_position(...)                       ← COMPOSITE
     .build()
   → Complex portfolio hierarchy

6. Setup Strategy
   strategy = MeanReversionStrategy()         ← STRATEGY
   publisher = SignalPublisher()              ← OBSERVER
   publisher.attach(LoggerObserver())

7. Generate Signals
   for tick in market_data:
     signals = strategy.generate_signals(tick)
     for signal in signals:
       publisher.notify(signal)               ← OBSERVER

8. Execute Orders
   invoker = CommandInvoker()                 ← COMMAND
   order = Order(...)
   invoker.execute(ExecuteOrderCommand(order))
   # Later: invoker.undo() if needed
```

---

## Summary

### Pattern Categories

**Creational Patterns** (Object Creation)
- **Factory**: Centralized instrument creation
- **Singleton**: Single configuration instance
- **Builder**: Step-by-step portfolio construction

**Structural Patterns** (Object Composition)
- **Decorator**: Layered analytics enhancement
- **Adapter**: External data integration
- **Composite**: Hierarchical portfolio modeling

**Behavioral Patterns** (Object Interaction)
- **Strategy**: Interchangeable algorithms
- **Observer**: Event-driven notifications
- **Command**: Encapsulated operations with undo

### When to Use Each Pattern

| Pattern | Use When... |
|---------|-------------|
| **Factory** | You need to create objects based on runtime data/types |
| **Singleton** | You need exactly one instance shared globally |
| **Builder** | You're constructing complex objects step-by-step |
| **Decorator** | You need to add features without modifying classes |
| **Adapter** | You're integrating incompatible interfaces |
| **Composite** | You're modeling tree/hierarchical structures |
| **Strategy** | You need interchangeable algorithms |
| **Observer** | You need event-driven, decoupled notifications |
| **Command** | You need undo/redo or operation history |

---

## Quick Reference

### Class Relationships

```
Inheritance (is-a):      ───▷
Implementation (is-a):   ···▷
Composition (has-a):     ───>
Dependency (uses):       ···>
```

### Common Symbols

```
┌─────┐
│Class│  = Class or Interface
└─────┘

△      = Inheritance/Implementation point

[list] = Collection/Array

(•)    = Method/Operation
```

---

*This diagram guide covers all nine design patterns implemented in HW6. For detailed implementation notes, see `design_report.md`.*
