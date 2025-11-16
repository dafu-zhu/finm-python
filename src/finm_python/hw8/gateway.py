"""
Gateway Module - Data and News Feed Server

The Gateway acts as the source of truth for market data in the trading system.
It runs two TCP servers that broadcast:
1. Price stream: Random-walk prices for multiple symbols
2. News sentiment: Market sentiment values (0-100)

Key Concepts:
- TCP server socket programming
- Non-blocking I/O and select()
- Message framing with delimiters
- Random walk price generation
- Multi-client connection handling

Learning Objectives:
- Understand TCP server socket lifecycle
- Implement message serialization and framing
- Handle multiple client connections
- Generate realistic market data streams

Architecture:
    Gateway (this module)
        |
        |-- Price Server (port 5001) --> OrderBook
        |
        |-- News Server (port 5002) --> Strategy

Usage:
    python -m finm_python.hw8.gateway

TODO: Implement the Gateway server with price and news streams.
"""

import socket
import time
import random
import threading
from typing import List, Dict, Optional
import logging

from .shared_memory_utils import (
    MESSAGE_DELIMITER,
    DEFAULT_PORT_GATEWAY_PRICE,
    DEFAULT_PORT_GATEWAY_NEWS,
    create_price_message,
    create_sentiment_message,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("Gateway")


class PriceGenerator:
    """
    Generates random-walk prices for multiple symbols.

    Simulates realistic market price movements using a random walk model
    where each price change is a small random percentage of the current price.

    Attributes:
        symbols (List[str]): List of trading symbols
        prices (Dict[str, float]): Current prices for each symbol
        volatility (float): Price movement volatility factor

    Example:
        gen = PriceGenerator(["AAPL", "MSFT"], {"AAPL": 150.0, "MSFT": 300.0})
        new_prices = gen.generate_tick()
        # Returns: {"AAPL": 150.23, "MSFT": 299.87}
    """

    def __init__(self, symbols: List[str], initial_prices: Dict[str, float],
                 volatility: float = 0.001):
        """
        Initialize the price generator.

        Args:
            symbols: List of symbol names to generate prices for
            initial_prices: Starting prices for each symbol
            volatility: Standard deviation of price changes (default 0.1%)

        Implementation Steps:
            1. Store symbols and initial prices
            2. Set volatility parameter
            3. Initialize current prices from initial_prices
        """
        # TODO: Implement initialization
        # self.symbols = symbols
        # self.prices = initial_prices.copy()
        # self.volatility = volatility
        raise NotImplementedError("Implement PriceGenerator initialization")

    def generate_tick(self) -> Dict[str, float]:
        """
        Generate the next price tick for all symbols.

        Uses random walk: new_price = old_price * (1 + random_change)
        where random_change ~ Normal(0, volatility)

        Returns:
            Dictionary of {symbol: new_price} for all symbols

        Implementation Steps:
            1. For each symbol:
               - Generate random change from normal distribution
               - Apply change to current price
               - Ensure price stays positive
            2. Return dictionary of new prices

        Hints:
            - Use random.gauss(0, self.volatility) for change
            - new_price = current_price * (1 + change)
            - Use max(new_price, 0.01) to ensure positive
        """
        # TODO: Implement tick generation
        # for symbol in self.symbols:
        #     change = random.gauss(0, self.volatility)
        #     self.prices[symbol] = max(self.prices[symbol] * (1 + change), 0.01)
        # return self.prices.copy()
        raise NotImplementedError("Implement generate_tick method")


class SentimentGenerator:
    """
    Generates random market sentiment values.

    Simulates news sentiment that varies over time, with occasional
    large moves representing significant news events.

    Attributes:
        current_sentiment (int): Current sentiment value (0-100)
    """

    def __init__(self, initial_sentiment: int = 50):
        """
        Initialize sentiment generator.

        Args:
            initial_sentiment: Starting sentiment (default 50 = neutral)
        """
        # TODO: Implement initialization
        # self.current_sentiment = initial_sentiment
        raise NotImplementedError("Implement SentimentGenerator initialization")

    def generate_sentiment(self) -> int:
        """
        Generate new sentiment value.

        Sentiment changes gradually with occasional large jumps.
        Most of the time: small random walk
        Occasionally (10% chance): large jump for "news events"

        Returns:
            Integer sentiment value between 0 and 100

        Implementation Steps:
            1. With 10% probability, make a large jump (-20 to +20)
            2. Otherwise, make small adjustment (-5 to +5)
            3. Clamp result to [0, 100] range
            4. Update and return current_sentiment

        Hints:
            - Use random.random() < 0.1 for probability check
            - Use random.randint() for integer changes
            - Use max(0, min(100, value)) for clamping
        """
        # TODO: Implement sentiment generation
        # if random.random() < 0.1:
        #     change = random.randint(-20, 20)
        # else:
        #     change = random.randint(-5, 5)
        # self.current_sentiment = max(0, min(100, self.current_sentiment + change))
        # return self.current_sentiment
        raise NotImplementedError("Implement generate_sentiment method")


class PriceServer:
    """
    TCP server that broadcasts price updates to connected clients.

    Listens for incoming connections and continuously sends price updates
    to all connected clients using the message protocol.

    Attributes:
        host (str): Server host address
        port (int): Server port number
        price_generator (PriceGenerator): Price data source
        running (bool): Server running state
        clients (List[socket.socket]): Connected client sockets
    """

    def __init__(self, host: str = "localhost",
                 port: int = DEFAULT_PORT_GATEWAY_PRICE,
                 symbols: List[str] = None,
                 initial_prices: Dict[str, float] = None,
                 tick_interval: float = 0.1):
        """
        Initialize the price server.

        Args:
            host: Server bind address
            port: Server bind port
            symbols: List of symbols to stream
            initial_prices: Starting prices for symbols
            tick_interval: Seconds between price updates

        Implementation Steps:
            1. Store host, port, tick_interval
            2. Initialize default symbols if None
            3. Initialize default prices if None
            4. Create PriceGenerator
            5. Initialize empty clients list
            6. Set running = False
        """
        # TODO: Implement initialization
        # self.host = host
        # self.port = port
        # self.tick_interval = tick_interval
        #
        # if symbols is None:
        #     symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]
        # if initial_prices is None:
        #     initial_prices = {
        #         "AAPL": 175.0, "MSFT": 330.0, "GOOGL": 140.0,
        #         "AMZN": 145.0, "META": 350.0
        #     }
        #
        # self.price_generator = PriceGenerator(symbols, initial_prices)
        # self.clients = []
        # self.running = False
        # self.server_socket = None
        raise NotImplementedError("Implement PriceServer initialization")

    def start(self) -> None:
        """
        Start the price server and begin accepting connections.

        Creates a TCP server socket, binds to host:port, and starts
        listening for connections in a separate thread while broadcasting
        prices to connected clients.

        Implementation Steps:
            1. Create TCP socket (socket.AF_INET, socket.SOCK_STREAM)
            2. Set socket options (SO_REUSEADDR)
            3. Bind to (host, port)
            4. Start listening (backlog of 5)
            5. Set running = True
            6. Start accept thread for new connections
            7. Start broadcast loop for price updates

        Hints:
            - socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            - Use threading.Thread for accept loop
            - Main loop broadcasts prices at tick_interval
        """
        # TODO: Implement server start
        # self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.server_socket.bind((self.host, self.port))
        # self.server_socket.listen(5)
        # self.running = True
        #
        # logger.info(f"Price server started on {self.host}:{self.port}")
        #
        # # Start accepting connections in background
        # accept_thread = threading.Thread(target=self._accept_connections)
        # accept_thread.daemon = True
        # accept_thread.start()
        #
        # # Main broadcast loop
        # self._broadcast_loop()
        raise NotImplementedError("Implement server start method")

    def _accept_connections(self) -> None:
        """
        Accept new client connections in a loop.

        Runs in a separate thread, continuously accepting new connections
        and adding them to the clients list.

        Implementation Steps:
            1. While running:
               - Accept new connection
               - Add client socket to clients list
               - Log the connection
            2. Handle exceptions gracefully
        """
        # TODO: Implement connection acceptance
        # while self.running:
        #     try:
        #         client_socket, address = self.server_socket.accept()
        #         self.clients.append(client_socket)
        #         logger.info(f"Price client connected from {address}")
        #     except Exception as e:
        #         if self.running:
        #             logger.error(f"Error accepting connection: {e}")
        raise NotImplementedError("Implement connection acceptance")

    def _broadcast_loop(self) -> None:
        """
        Main loop that broadcasts price updates to all clients.

        Continuously generates new prices and sends them to all connected
        clients, removing disconnected clients.

        Implementation Steps:
            1. While running:
               - Generate new price tick
               - Create message for each symbol
               - Send to all clients
               - Remove disconnected clients
               - Sleep for tick_interval
        """
        # TODO: Implement broadcast loop
        # while self.running:
        #     prices = self.price_generator.generate_tick()
        #
        #     # Build message with all prices
        #     message = b""
        #     for symbol, price in prices.items():
        #         message += create_price_message(symbol, price)
        #
        #     # Send to all clients
        #     disconnected = []
        #     for client in self.clients:
        #         try:
        #             client.sendall(message)
        #         except Exception:
        #             disconnected.append(client)
        #
        #     # Remove disconnected clients
        #     for client in disconnected:
        #         self.clients.remove(client)
        #         client.close()
        #
        #     time.sleep(self.tick_interval)
        raise NotImplementedError("Implement broadcast loop")

    def stop(self) -> None:
        """
        Stop the price server and close all connections.

        Implementation Steps:
            1. Set running = False
            2. Close all client connections
            3. Close server socket
        """
        # TODO: Implement server stop
        # self.running = False
        # for client in self.clients:
        #     client.close()
        # if self.server_socket:
        #     self.server_socket.close()
        # logger.info("Price server stopped")
        raise NotImplementedError("Implement server stop method")


class NewsServer:
    """
    TCP server that broadcasts news sentiment updates.

    Similar to PriceServer but sends sentiment values instead of prices.
    Sentiment updates are less frequent than price updates.

    Attributes:
        host (str): Server host address
        port (int): Server port number
        sentiment_generator (SentimentGenerator): Sentiment data source
        running (bool): Server running state
        clients (List[socket.socket]): Connected client sockets
    """

    def __init__(self, host: str = "localhost",
                 port: int = DEFAULT_PORT_GATEWAY_NEWS,
                 update_interval: float = 1.0):
        """
        Initialize the news server.

        Args:
            host: Server bind address
            port: Server bind port
            update_interval: Seconds between sentiment updates

        Implementation Steps:
            1. Store host, port, update_interval
            2. Create SentimentGenerator
            3. Initialize empty clients list
            4. Set running = False
        """
        # TODO: Implement initialization
        # self.host = host
        # self.port = port
        # self.update_interval = update_interval
        # self.sentiment_generator = SentimentGenerator()
        # self.clients = []
        # self.running = False
        # self.server_socket = None
        raise NotImplementedError("Implement NewsServer initialization")

    def start(self) -> None:
        """
        Start the news server.

        Similar to PriceServer.start() but for sentiment data.

        Implementation Steps:
            1. Create and configure TCP socket
            2. Bind and listen
            3. Start accept thread
            4. Start broadcast loop for sentiment
        """
        # TODO: Implement server start
        raise NotImplementedError("Implement news server start")

    def _accept_connections(self) -> None:
        """Accept new client connections."""
        # TODO: Implement connection acceptance
        raise NotImplementedError("Implement connection acceptance")

    def _broadcast_loop(self) -> None:
        """
        Main loop that broadcasts sentiment updates.

        Implementation Steps:
            1. While running:
               - Generate new sentiment
               - Create sentiment message
               - Send to all clients
               - Remove disconnected clients
               - Sleep for update_interval
        """
        # TODO: Implement broadcast loop
        raise NotImplementedError("Implement sentiment broadcast loop")

    def stop(self) -> None:
        """Stop the news server."""
        # TODO: Implement server stop
        raise NotImplementedError("Implement server stop")


def run_gateway(price_port: int = DEFAULT_PORT_GATEWAY_PRICE,
                news_port: int = DEFAULT_PORT_GATEWAY_NEWS,
                duration: Optional[float] = None) -> None:
    """
    Main entry point to run the Gateway servers.

    Starts both price and news servers in separate threads.

    Args:
        price_port: Port for price server
        news_port: Port for news server
        duration: Optional duration to run (None = run forever)

    Implementation Steps:
        1. Create PriceServer and NewsServer instances
        2. Start each server in a separate thread
        3. If duration specified, sleep then stop servers
        4. Otherwise, run until interrupted

    Usage:
        # Run indefinitely
        run_gateway()

        # Run for 60 seconds
        run_gateway(duration=60.0)
    """
    # TODO: Implement gateway runner
    # logger.info("Starting Gateway servers...")
    #
    # price_server = PriceServer(port=price_port)
    # news_server = NewsServer(port=news_port)
    #
    # # Start servers in threads
    # price_thread = threading.Thread(target=price_server.start)
    # news_thread = threading.Thread(target=news_server.start)
    #
    # price_thread.daemon = True
    # news_thread.daemon = True
    #
    # price_thread.start()
    # news_thread.start()
    #
    # try:
    #     if duration:
    #         time.sleep(duration)
    #     else:
    #         while True:
    #             time.sleep(1)
    # except KeyboardInterrupt:
    #     logger.info("Shutting down Gateway...")
    # finally:
    #     price_server.stop()
    #     news_server.stop()

    raise NotImplementedError("Implement gateway runner")


if __name__ == "__main__":
    run_gateway()
