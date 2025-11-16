# HW8: Interprocess Communication for Trading Systems

## Overview

This project implements a multi-process trading system that uses **interprocess communication (IPC)** to connect independent components through TCP sockets and shared memory. The system simulates a real-time trading stack with four cooperating processes.

## Architecture

```
┌─────────────┐     TCP Sockets      ┌─────────────┐
│   Gateway   │ ──────────────────►  │  OrderBook  │
│ (Data Feed) │                      │ (Price Cache)│
└─────────────┘                      └──────┬──────┘
       │                                    │
       │ TCP (News)                  Shared Memory
       │                                    │
       ▼                                    ▼
┌─────────────┐                      ┌─────────────┐
│  Strategy   │ ◄─────────────────── │ Price Data  │
│  (Signals)  │                      │   (NumPy)   │
└──────┬──────┘                      └─────────────┘
       │
       │ TCP (Orders)
       ▼
┌─────────────┐
│OrderManager │
│ (Trade Log) │
└─────────────┘
```

## Components

### 1. Gateway (`gateway.py`)
**Role**: Data source for the entire system

- Streams random-walk prices for multiple symbols
- Broadcasts news sentiment values (0-100)
- Uses TCP sockets to serve multiple clients
- Acts as the "market data feed"

**Key Features**:
- `PriceGenerator`: Random walk price simulation
- `SentimentGenerator`: Market sentiment simulation
- `PriceServer`: TCP server for price data
- `NewsServer`: TCP server for sentiment data

### 2. OrderBook (`orderbook.py`)
**Role**: Market state manager

- Connects to Gateway's price stream
- Maintains latest prices in shared memory
- Provides low-latency price access to Strategy
- Handles network reconnection

**Key Features**:
- `MessageBuffer`: TCP message framing
- `OrderBook`: Shared memory price store
- Atomic price updates with locking

### 3. Strategy (`strategy.py`)
**Role**: Signal generator and decision maker

- Reads prices from shared memory
- Receives sentiment from Gateway
- Implements dual-signal strategy:
  - **Technical**: Moving average crossover
  - **Fundamental**: News sentiment analysis
- Sends orders when both signals agree

**Key Features**:
- `PriceHistory`: Rolling window for MA calculation
- `SignalGenerator`: Signal generation logic
- `Strategy`: Position management and order execution

### 4. OrderManager (`order_manager.py`)
**Role**: Trade execution and logging

- TCP server receiving orders from Strategy
- Logs all executed trades with timestamps
- Provides trade summary statistics
- Handles multiple Strategy clients

**Key Features**:
- `TradeLog`: Thread-safe trade recording
- `ClientHandler`: Per-client message processing
- `OrderManager`: Multi-client TCP server

## Communication Protocol

### Message Format

All messages use `MESSAGE_DELIMITER = b'*'` as separator.

**Price Message**:
```
SYMBOL,PRICE*
Example: b"AAPL,172.53*"
```

**Sentiment Message**:
```
SENTIMENT*
Example: b"75*"
```

**Order Message** (JSON):
```json
{"id": 1, "action": "BUY", "quantity": 10, "symbol": "AAPL", "price": 150.25}*
```

### Shared Memory Structure

Uses NumPy structured array:
- One float64 per symbol
- Indexed by symbol position
- Protected by multiprocessing Lock

## Installation

```bash
# Install dependencies
pip install numpy

# Or using uv
uv sync
```

## Usage

### Run Complete System

```bash
python -m finm_python.hw8.main
```

### Run Individual Components (for debugging)

```bash
# Terminal 1: Start OrderManager
python -m finm_python.hw8.order_manager

# Terminal 2: Start Gateway
python -m finm_python.hw8.gateway

# Terminal 3: Start OrderBook
python -m finm_python.hw8.orderbook

# Terminal 4: Start Strategy (requires shared memory name)
python -m finm_python.hw8.strategy
```

### Run Tests

```bash
pytest src/finm_python/hw8/tests/ -v
```

## Configuration

Default ports (configurable in `shared_memory_utils.py`):
- Gateway Price Server: 5001
- Gateway News Server: 5002
- OrderManager: 5003

Trading parameters (in `strategy.py`):
- Short MA Window: 5
- Long MA Window: 20
- Bullish Threshold: 60
- Bearish Threshold: 40

## Trading Strategy Details

### Signal Generation

1. **Price Signal** (Moving Average Crossover):
   - BUY: Short MA > Long MA (uptrend)
   - SELL: Short MA < Long MA (downtrend)
   - NEUTRAL: Insufficient data

2. **Sentiment Signal**:
   - BUY: Sentiment > 60 (bullish news)
   - SELL: Sentiment < 40 (bearish news)
   - NEUTRAL: 40 ≤ Sentiment ≤ 60

3. **Combined Signal**:
   - Execute BUY only if both signals are BUY
   - Execute SELL only if both signals are SELL
   - Do nothing if signals disagree

### Position Management

- Tracks current position: None, long, or short
- Avoids duplicate orders (won't buy if already long)
- Allows position reversal (can sell if long)

## File Structure

```
hw8/
├── __init__.py               # Package initialization
├── shared_memory_utils.py    # Shared memory and message utilities
├── gateway.py                # Data feed server
├── orderbook.py              # Shared memory price manager
├── strategy.py               # Signal generation and orders
├── order_manager.py          # Trade execution logging
├── main.py                   # Process orchestration
├── README.md                 # This file
├── performance_report.md     # Performance benchmarks (TODO)
└── tests/
    ├── __init__.py
    ├── test_shared_memory.py    # Shared memory tests
    ├── test_connectivity.py     # Socket communication tests
    ├── test_strategy.py         # Signal generation tests
    └── test_order_manager.py    # Trade logging tests
```

## Learning Objectives

By completing this assignment, you will learn:

1. **Socket Programming**: TCP server/client architecture, connection management
2. **Shared Memory**: Inter-process data sharing without copying
3. **Message Protocols**: Serialization, framing, and parsing
4. **Process Orchestration**: Coordinating multiple processes with dependencies
5. **Synchronization**: Thread-safe operations with locks
6. **Trading Systems**: Basic algorithmic trading concepts

## Performance Considerations

- **Latency**: Time from price update to trade decision
- **Throughput**: Ticks processed per second
- **Memory**: Shared memory footprint
- **Reliability**: Reconnection handling, error recovery

## Error Handling

The system should handle:
- Network disconnections with retry logic
- Invalid messages gracefully
- Process startup order dependencies
- Resource cleanup on shutdown

## TODO for Students

1. Implement all `NotImplementedError` sections
2. Add proper error handling and logging
3. Write comprehensive tests
4. Measure and document performance
5. Record system demonstration video
6. Handle edge cases and failure scenarios

## Resources

- Python `socket` module documentation
- Python `multiprocessing.shared_memory` documentation
- NumPy structured arrays
- TCP/IP networking fundamentals
- Trading system architecture patterns

## Submission Requirements

- [ ] All code files implemented
- [ ] Tests passing
- [ ] Performance report completed
- [ ] README with architecture diagram
- [ ] Video demonstration
- [ ] GitHub shared with TAs (jcolli5158, hyoung3)

---

**Good luck with your implementation!**
