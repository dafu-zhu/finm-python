# Interprocess Communication for Trading Systems

## Overview

In this assignment, you will design and implement a simplified multi-process trading system that uses **interprocess communication (IPC)** to connect independent components through real TCP sockets and shared memory.

You'll build a mini trading stack — a **Gateway**, **OrderBook**, **Strategy**, and **OrderManager** — that communicate in real time.

This assignment emphasizes process orchestration, socket programming, serialization, and shared memory synchronization in the context of financial systems.

## Learning Objectives

- Understand how to establish and manage socket connections between processes
- Use multiprocessing and socket to build producer-consumer systems
- Apply `multiprocessing.shared_memory` to share market data efficiently between processes
- Design and implement simple message protocols for structured communication
- Handle serialization, message framing, and synchronization

## Task Specifications

### 1. System Overview

You will implement four cooperating Python processes:

```
[ Gateway ] → [ OrderBook ] → [ Strategy ] → [ OrderManager ]
```

**Gateway**: Streams random tick prices and news sentiment values over sockets.

**OrderBook**: Receives price data and updates a shared memory store.

**Strategy**: Reads shared memory and news, decides whether to buy or sell.

**OrderManager**: Receives orders over a socket and logs executed trades.

All four processes should run concurrently and communicate only through sockets or shared memory — no shared Python objects.

### 2. Gateway (Data & News Feed)

#### Responsibilities

Acts as a server that broadcasts two streams:

1. **Price stream**: A random-walk price feed for multiple symbols. You can build this yourself, or you can use the csv file from the previous homework as the price data you will stream.

2. **News sentiment**: Integers between 0-100, representing market sentiment. Low values represent bad news while high values represent good news. A sentiment of 50 is neutral. You will be the news server yourself that will randomly choose a news sentiment value to stream.

Uses TCP sockets to send data to connected clients (OrderBook and Strategy).

#### Expectations

- Use the socket module
- Send serialized messages delimited by a consistent MESSAGE_DELIMITER (e.g. `b'*'`)
- Example message: `b"AAPL,172.53*MSFT,325.20*"`
- Respect MESSAGE_DELIMITER in all transmissions

### 3. OrderBook (Shared Market State)

#### Responsibilities

- Connects to the Gateway to receive price data
- Maintains the latest prices for all symbols in **shared memory**
- Provides shared memory access to the Strategy process

#### Expectations

- Use `multiprocessing.shared_memory` to store and update a NumPy structured array, or a serialized dictionary of {symbol: price}
- Ensure updates are atomic and synchronized using `multiprocessing.Lock`
- Handle reconnection logic gracefully if the Gateway restarts

### 4. Strategy (Signal Generator)

#### Responsibilities

- Reads the latest prices from shared memory
- Connects to the Gateway's news stream to receive sentiment
- Generates trading signals:
  - **Price-based**: Moving average crossover (short vs long window). If the short moving average is above the long moving average you should generate a buy signal, otherwise a sell signal. The condition for buy or sell is strictly greater than or less than. Don't worry about the case where they are equal.
  - **News-based**: Sentiment > bullish_threshold → Buy signal; Sentiment < bearish_threshold → Sell signal
- Only act when both signals agree - when news signal and price signal are both buy, you buy; if they are both sell, you sell; and if they are different you do nothing
- Sends an Order message to the OrderManager when a trade is decided

#### Expectations

- Use a local rolling buffer for price history
- Manage current position (None, long, short) to avoid duplicate orders
- Serialize orders before sending (e.g., JSON, pickle, or otherwise)
- Respect MESSAGE_DELIMITER in all transmissions

### 5. OrderManager (Trade Execution)

#### Responsibilities

- Acts as a TCP server receiving Order objects from one or more Strategy clients
- Deserialize each order and log the trade

Print human-readable trade confirmations in real time:

```
Received Order 12: BUY 10 AAPL @ 173.20
```

### 6. Shared Memory Interface

Create a helper class for structured memory access:

```python
class SharedPriceBook:
    def __init__(self, symbols, name=None):
        ...

    def update(self, symbol, price):
        ...

    def read(self, symbol):
        ...
```

Use `multiprocessing.shared_memory.SharedMemory` and `np.ndarray` for efficient updates.

### 7. Orchestration (main.py)

Your `main.py` should start each process and manage startup order:

```python
if __name__ == "__main__":
    processes = [
        Process(target=run_gateway),
        Process(target=run_orderbook),
        Process(target=run_strategy),
        Process(target=run_ordermanager)
    ]

    for p in processes: p.start()
    for p in processes: p.join()
```

## Performance & Reliability

### Measure

- Average latency between a new price tick and a trade decision
- Throughput (ticks per second)
- Memory footprint of the shared memory region
- Behavior under dropped connections or missing data

### Unit Tests

Write tests to confirm:

- Connections establish successfully between components
- Messages are serialized/deserialized correctly
- Shared memory updates propagate as expected
- Strategy generates correct buy/sell/neutral signals
- OrderManager receives and logs the correct number of orders

## Deliverables

### GitHub Sharing

Please share your GitHub with your TAs:

- Jenn: jcolli5158
- Hunter: hyoung3

### Files to Include

| File | Description |
|------|-------------|
| `gateway.py` | Streams price & sentiment data via TCP |
| `orderbook.py` | Receives prices and maintains shared memory |
| `strategy.py` | Generates trading signals and sends orders |
| `order_manager.py` | Receives and logs executed trades |
| `shared_memory_utils.py` | Defines shared memory wrapper |
| `main.py` | Launches all processes |
| `tests/` | Unit tests for connectivity and correctness |
| `performance_report.md` | Latency & throughput benchmarks |
| `README.md` | Architecture diagram and run instructions |
| `video.mp4` | Video of the system in action. Show the processes running independently, separate logs, etc. How you do this is up to you, but it should show are the parts in action together. |

You may also include any other files you think are necessary for running the project.

Please document your project well.

---

## Architecture Notes

- **Gateway** is the source of truth for market data
- **OrderBook** caches prices in shared memory for fast access
- **Strategy** consumes shared memory and socket streams
- **OrderManager** is the sink — receives and logs all orders

Use proper error handling, logging, and connection retry logic to ensure reliability under realistic conditions.