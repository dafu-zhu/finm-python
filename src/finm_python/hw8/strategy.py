"""
Strategy Module - Signal Generator

The Strategy reads market data from shared memory and news sentiment from
the Gateway, then generates trading signals and sends orders to the OrderManager.

Key Concepts:
- Reading from shared memory
- TCP client socket programming
- Moving average crossover strategy
- Sentiment-based trading signals
- Position management

Learning Objectives:
- Implement trading signal generation logic
- Combine multiple data sources for decisions
- Manage trading positions to avoid duplicate orders
- Use rolling windows for technical analysis

Architecture:
    Shared Memory (prices) --> Strategy (this module) --> OrderManager
    Gateway (news) ----------^

Trading Logic:
    1. Price Signal: Short MA > Long MA = BUY, Short MA < Long MA = SELL
    2. News Signal: Sentiment > bullish_threshold = BUY,
                   Sentiment < bearish_threshold = SELL
    3. Execute only when BOTH signals agree

Usage:
    python -m finm_python.hw8.strategy

TODO: Implement the Strategy with signal generation and order sending.
"""

import socket
import time
import logging
from collections import deque
from typing import List, Dict, Optional, Literal
from multiprocessing import Lock

from .shared_memory_utils import (
    MESSAGE_DELIMITER,
    DEFAULT_PORT_GATEWAY_NEWS,
    DEFAULT_PORT_ORDER_MANAGER,
    DEFAULT_BUFFER_SIZE,
    SharedPriceBook,
    parse_sentiment_message,
    create_order_message,
)
from .orderbook import MessageBuffer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("Strategy")

# Type aliases for positions and signals
Position = Literal["long", "short", None]
Signal = Literal["BUY", "SELL", "NEUTRAL"]


class PriceHistory:
    """
    Maintains rolling price history for moving average calculations.

    Uses a fixed-size deque to efficiently store recent prices and
    calculate moving averages.

    Attributes:
        max_size (int): Maximum number of prices to store
        prices (deque): Rolling window of prices

    Example:
        history = PriceHistory(max_size=20)
        for price in [100, 101, 102, 103, 104]:
            history.add_price(price)

        short_ma = history.moving_average(3)   # Average of last 3
        long_ma = history.moving_average(5)    # Average of last 5
    """

    def __init__(self, max_size: int = 100):
        """
        Initialize price history.

        Args:
            max_size: Maximum number of prices to keep

        Implementation Steps:
            1. Create deque with maxlen=max_size
        """
        # TODO: Implement initialization
        # self.prices = deque(maxlen=max_size)
        # self.max_size = max_size
        raise NotImplementedError("Implement PriceHistory initialization")

    def add_price(self, price: float) -> None:
        """
        Add a new price to the history.

        Args:
            price: New price value

        Implementation Steps:
            1. Append price to deque (oldest automatically removed)
        """
        # TODO: Implement price addition
        # self.prices.append(price)
        raise NotImplementedError("Implement add_price method")

    def moving_average(self, window: int) -> Optional[float]:
        """
        Calculate moving average over the specified window.

        Args:
            window: Number of recent prices to average

        Returns:
            Average of last 'window' prices, or None if insufficient data

        Implementation Steps:
            1. Check if enough prices available
            2. If not, return None
            3. Otherwise, calculate mean of last 'window' prices
        """
        # TODO: Implement moving average
        # if len(self.prices) < window:
        #     return None
        # recent = list(self.prices)[-window:]
        # return sum(recent) / len(recent)
        raise NotImplementedError("Implement moving_average method")

    def __len__(self) -> int:
        """Return number of prices in history."""
        # TODO: Return length
        # return len(self.prices)
        raise NotImplementedError("Implement __len__ method")


class SignalGenerator:
    """
    Generates trading signals based on price and sentiment data.

    Combines technical (moving average crossover) and fundamental
    (sentiment) analysis to generate buy/sell signals.

    Attributes:
        short_window (int): Short-term moving average window
        long_window (int): Long-term moving average window
        bullish_threshold (int): Sentiment above this = bullish
        bearish_threshold (int): Sentiment below this = bearish
    """

    def __init__(self, short_window: int = 5, long_window: int = 20,
                 bullish_threshold: int = 60, bearish_threshold: int = 40):
        """
        Initialize signal generator.

        Args:
            short_window: Window for short-term MA
            long_window: Window for long-term MA
            bullish_threshold: Sentiment above this triggers BUY
            bearish_threshold: Sentiment below this triggers SELL

        Implementation Steps:
            1. Store all parameters
            2. Validate short_window < long_window
        """
        # TODO: Implement initialization
        # if short_window >= long_window:
        #     raise ValueError("short_window must be less than long_window")
        #
        # self.short_window = short_window
        # self.long_window = long_window
        # self.bullish_threshold = bullish_threshold
        # self.bearish_threshold = bearish_threshold
        raise NotImplementedError("Implement SignalGenerator initialization")

    def price_signal(self, price_history: PriceHistory) -> Signal:
        """
        Generate signal based on moving average crossover.

        Args:
            price_history: Historical price data

        Returns:
            "BUY" if short MA > long MA
            "SELL" if short MA < long MA
            "NEUTRAL" if insufficient data

        Implementation Steps:
            1. Calculate short-term MA
            2. Calculate long-term MA
            3. If either is None, return "NEUTRAL"
            4. Compare and return appropriate signal
        """
        # TODO: Implement price signal
        # short_ma = price_history.moving_average(self.short_window)
        # long_ma = price_history.moving_average(self.long_window)
        #
        # if short_ma is None or long_ma is None:
        #     return "NEUTRAL"
        #
        # if short_ma > long_ma:
        #     return "BUY"
        # elif short_ma < long_ma:
        #     return "SELL"
        # else:
        #     return "NEUTRAL"
        raise NotImplementedError("Implement price_signal method")

    def sentiment_signal(self, sentiment: int) -> Signal:
        """
        Generate signal based on news sentiment.

        Args:
            sentiment: Current sentiment value (0-100)

        Returns:
            "BUY" if sentiment > bullish_threshold
            "SELL" if sentiment < bearish_threshold
            "NEUTRAL" otherwise

        Implementation Steps:
            1. Compare sentiment to thresholds
            2. Return appropriate signal
        """
        # TODO: Implement sentiment signal
        # if sentiment > self.bullish_threshold:
        #     return "BUY"
        # elif sentiment < self.bearish_threshold:
        #     return "SELL"
        # else:
        #     return "NEUTRAL"
        raise NotImplementedError("Implement sentiment_signal method")

    def combined_signal(self, price_signal: Signal,
                        sentiment_signal: Signal) -> Signal:
        """
        Combine price and sentiment signals.

        Only generates a trade signal when both agree.

        Args:
            price_signal: Signal from price analysis
            sentiment_signal: Signal from sentiment analysis

        Returns:
            "BUY" if both are BUY
            "SELL" if both are SELL
            "NEUTRAL" otherwise

        Implementation Steps:
            1. Check if both signals match
            2. Return combined signal
        """
        # TODO: Implement combined signal
        # if price_signal == "BUY" and sentiment_signal == "BUY":
        #     return "BUY"
        # elif price_signal == "SELL" and sentiment_signal == "SELL":
        #     return "SELL"
        # else:
        #     return "NEUTRAL"
        raise NotImplementedError("Implement combined_signal method")


class Strategy:
    """
    Main strategy class that coordinates signal generation and order execution.

    Reads prices from shared memory, receives news from Gateway,
    generates signals, and sends orders to OrderManager.

    Attributes:
        symbol (str): Symbol being traded
        price_book (SharedPriceBook): Shared memory price access
        signal_generator (SignalGenerator): Signal generation logic
        price_history (PriceHistory): Rolling price window
        current_position (Position): Current market position
        order_id (int): Counter for order IDs
    """

    def __init__(self, symbol: str, symbols: List[str],
                 shared_memory_name: str,
                 news_host: str = "localhost",
                 news_port: int = DEFAULT_PORT_GATEWAY_NEWS,
                 order_manager_host: str = "localhost",
                 order_manager_port: int = DEFAULT_PORT_ORDER_MANAGER,
                 lock: Optional[Lock] = None,
                 short_window: int = 5,
                 long_window: int = 20,
                 order_quantity: int = 10):
        """
        Initialize the Strategy.

        Args:
            symbol: Symbol to trade (e.g., "AAPL")
            symbols: All symbols in shared memory
            shared_memory_name: Name of shared memory block
            news_host: Gateway news server address
            news_port: Gateway news server port
            order_manager_host: OrderManager server address
            order_manager_port: OrderManager server port
            lock: Shared memory lock
            short_window: Short MA window
            long_window: Long MA window
            order_quantity: Number of shares per order

        Implementation Steps:
            1. Store all connection parameters
            2. Create SharedPriceBook (attach to existing)
            3. Create SignalGenerator
            4. Create PriceHistory with max_size >= long_window
            5. Initialize position to None
            6. Initialize order_id counter
            7. Set running = False
        """
        # TODO: Implement initialization
        # self.symbol = symbol
        # self.order_quantity = order_quantity
        #
        # # Connect to shared memory
        # self.price_book = SharedPriceBook(
        #     symbols=symbols,
        #     name=shared_memory_name,
        #     lock=lock
        # )
        #
        # # Initialize signal generator and history
        # self.signal_generator = SignalGenerator(
        #     short_window=short_window,
        #     long_window=long_window
        # )
        # self.price_history = PriceHistory(max_size=long_window * 2)
        #
        # # Connection parameters
        # self.news_host = news_host
        # self.news_port = news_port
        # self.order_manager_host = order_manager_host
        # self.order_manager_port = order_manager_port
        #
        # # State
        # self.current_position: Position = None
        # self.order_id = 0
        # self.running = False
        #
        # # Sockets
        # self.news_socket = None
        # self.order_socket = None
        # self.message_buffer = MessageBuffer()
        #
        # # Current sentiment
        # self.current_sentiment = 50  # Start neutral

        raise NotImplementedError("Implement Strategy initialization")

    def connect_to_news(self) -> bool:
        """
        Connect to Gateway news stream.

        Returns:
            True if connection successful, False otherwise

        Implementation Steps:
            1. Create TCP socket
            2. Connect to news_host:news_port
            3. Set timeout for non-blocking reads
            4. Return success status
        """
        # TODO: Implement news connection
        # try:
        #     self.news_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #     self.news_socket.connect((self.news_host, self.news_port))
        #     self.news_socket.settimeout(0.1)
        #     logger.info(f"Connected to news stream at {self.news_host}:{self.news_port}")
        #     return True
        # except Exception as e:
        #     logger.error(f"Failed to connect to news: {e}")
        #     return False
        raise NotImplementedError("Implement connect_to_news method")

    def connect_to_order_manager(self) -> bool:
        """
        Connect to OrderManager server.

        Returns:
            True if connection successful, False otherwise

        Implementation Steps:
            1. Create TCP socket
            2. Connect to order_manager_host:order_manager_port
            3. Return success status
        """
        # TODO: Implement order manager connection
        # try:
        #     self.order_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #     self.order_socket.connect((self.order_manager_host, self.order_manager_port))
        #     logger.info(f"Connected to OrderManager at {self.order_manager_host}:{self.order_manager_port}")
        #     return True
        # except Exception as e:
        #     logger.error(f"Failed to connect to OrderManager: {e}")
        #     return False
        raise NotImplementedError("Implement connect_to_order_manager method")

    def receive_sentiment(self) -> None:
        """
        Receive and process sentiment updates from Gateway.

        Non-blocking: returns immediately if no data available.

        Implementation Steps:
            1. Try to receive data (with timeout)
            2. Add to message buffer
            3. Parse complete messages
            4. Update current_sentiment
        """
        # TODO: Implement sentiment reception
        # try:
        #     data = self.news_socket.recv(DEFAULT_BUFFER_SIZE)
        #     if data:
        #         self.message_buffer.add_data(data)
        #         messages = self.message_buffer.get_complete_messages()
        #         for msg in messages:
        #             if msg:
        #                 self.current_sentiment = parse_sentiment_message(msg)
        #                 logger.debug(f"Sentiment updated: {self.current_sentiment}")
        # except socket.timeout:
        #     pass
        # except Exception as e:
        #     logger.error(f"Error receiving sentiment: {e}")
        raise NotImplementedError("Implement receive_sentiment method")

    def read_price(self) -> float:
        """
        Read current price from shared memory.

        Returns:
            Current price for self.symbol

        Implementation Steps:
            1. Read from price_book
            2. Return the price
        """
        # TODO: Implement price reading
        # return self.price_book.read(self.symbol)
        raise NotImplementedError("Implement read_price method")

    def generate_signal(self) -> Signal:
        """
        Generate trading signal based on current data.

        Returns:
            Combined signal from price and sentiment analysis

        Implementation Steps:
            1. Read current price and add to history
            2. Generate price signal
            3. Generate sentiment signal
            4. Return combined signal
        """
        # TODO: Implement signal generation
        # price = self.read_price()
        # self.price_history.add_price(price)
        #
        # price_sig = self.signal_generator.price_signal(self.price_history)
        # sentiment_sig = self.signal_generator.sentiment_signal(self.current_sentiment)
        #
        # combined = self.signal_generator.combined_signal(price_sig, sentiment_sig)
        #
        # logger.debug(f"Price: {price:.2f}, Sentiment: {self.current_sentiment}, "
        #              f"Price Signal: {price_sig}, Sentiment Signal: {sentiment_sig}, "
        #              f"Combined: {combined}")
        #
        # return combined
        raise NotImplementedError("Implement generate_signal method")

    def should_execute_order(self, signal: Signal) -> bool:
        """
        Determine if order should be executed based on signal and position.

        Avoids duplicate orders (e.g., don't buy if already long).

        Args:
            signal: Trading signal

        Returns:
            True if order should be executed, False otherwise

        Implementation Steps:
            1. If signal is NEUTRAL, return False
            2. If signal is BUY and position is not long, return True
            3. If signal is SELL and position is not short, return True
            4. Otherwise return False (avoid duplicate)

        Examples:
            - Signal=BUY, Position=None -> Execute (enter long)
            - Signal=BUY, Position=long -> Don't execute (already long)
            - Signal=SELL, Position=long -> Execute (close long, enter short)
        """
        # TODO: Implement execution check
        # if signal == "NEUTRAL":
        #     return False
        # if signal == "BUY" and self.current_position != "long":
        #     return True
        # if signal == "SELL" and self.current_position != "short":
        #     return True
        # return False
        raise NotImplementedError("Implement should_execute_order method")

    def send_order(self, action: str, price: float) -> bool:
        """
        Send order to OrderManager.

        Args:
            action: "BUY" or "SELL"
            price: Execution price

        Returns:
            True if order sent successfully, False otherwise

        Implementation Steps:
            1. Increment order_id
            2. Create order message
            3. Send to order_socket
            4. Update current_position
            5. Log the order

        Hints:
            - Use create_order_message() helper
            - Update position: BUY -> "long", SELL -> "short"
        """
        # TODO: Implement order sending
        # self.order_id += 1
        #
        # message = create_order_message(
        #     self.order_id,
        #     action,
        #     self.order_quantity,
        #     self.symbol,
        #     price
        # )
        #
        # try:
        #     self.order_socket.sendall(message)
        #
        #     # Update position
        #     if action == "BUY":
        #         self.current_position = "long"
        #     else:
        #         self.current_position = "short"
        #
        #     logger.info(f"Sent Order {self.order_id}: {action} {self.order_quantity} "
        #                 f"{self.symbol} @ {price:.2f}")
        #     return True
        #
        # except Exception as e:
        #     logger.error(f"Failed to send order: {e}")
        #     return False
        raise NotImplementedError("Implement send_order method")

    def run(self, duration: Optional[float] = None,
            tick_interval: float = 0.1) -> None:
        """
        Main loop for the Strategy process.

        Args:
            duration: Optional duration to run (None = run forever)
            tick_interval: Seconds between strategy evaluations

        Implementation Steps:
            1. Set running = True
            2. Connect to news and order manager
            3. Main loop:
               - Receive sentiment updates
               - Generate signal
               - Check if should execute
               - Send order if needed
               - Sleep for tick_interval
            4. Check duration timeout
            5. Clean up on exit
        """
        # TODO: Implement main run loop
        # self.running = True
        # start_time = time.time()
        #
        # # Connect to services
        # if not self.connect_to_news():
        #     logger.error("Could not connect to news stream")
        #     return
        #
        # if not self.connect_to_order_manager():
        #     logger.error("Could not connect to OrderManager")
        #     return
        #
        # logger.info(f"Strategy running for {self.symbol}...")
        #
        # try:
        #     while self.running:
        #         # Check duration
        #         if duration and (time.time() - start_time) >= duration:
        #             break
        #
        #         # Update sentiment
        #         self.receive_sentiment()
        #
        #         # Generate signal
        #         signal = self.generate_signal()
        #
        #         # Execute if appropriate
        #         if self.should_execute_order(signal):
        #             price = self.read_price()
        #             self.send_order(signal, price)
        #
        #         time.sleep(tick_interval)
        #
        # except KeyboardInterrupt:
        #     logger.info("Strategy interrupted")
        # finally:
        #     self.stop()

        raise NotImplementedError("Implement run method")

    def stop(self) -> None:
        """
        Stop the Strategy process.

        Implementation Steps:
            1. Set running = False
            2. Close all socket connections
            3. Close shared memory access
        """
        # TODO: Implement stop
        # self.running = False
        # if self.news_socket:
        #     self.news_socket.close()
        # if self.order_socket:
        #     self.order_socket.close()
        # self.price_book.close()
        # logger.info(f"Strategy stopped. Total orders: {self.order_id}")
        raise NotImplementedError("Implement stop method")


def run_strategy(symbol: str = "AAPL",
                 symbols: List[str] = None,
                 shared_memory_name: str = None,
                 duration: Optional[float] = None) -> int:
    """
    Main entry point to run the Strategy process.

    Args:
        symbol: Symbol to trade
        symbols: All symbols in shared memory
        shared_memory_name: Name of shared memory block
        duration: Optional duration to run

    Returns:
        Total number of orders sent

    Usage:
        # Run for 60 seconds
        orders = run_strategy("AAPL", ["AAPL", "MSFT"],
                             "shm_prices", duration=60.0)
        print(f"Generated {orders} orders")
    """
    # TODO: Implement strategy runner
    # if symbols is None:
    #     symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]
    #
    # if shared_memory_name is None:
    #     raise ValueError("shared_memory_name is required")
    #
    # logger.info(f"Starting Strategy for {symbol}")
    #
    # strategy = Strategy(
    #     symbol=symbol,
    #     symbols=symbols,
    #     shared_memory_name=shared_memory_name
    # )
    #
    # strategy.run(duration=duration)
    #
    # return strategy.order_id

    raise NotImplementedError("Implement strategy runner")


if __name__ == "__main__":
    # This requires shared memory to be created by OrderBook first
    print("Strategy requires shared memory name from OrderBook")
    print("Run via main.py orchestration instead")
