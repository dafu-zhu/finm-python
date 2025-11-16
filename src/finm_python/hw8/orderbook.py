"""
OrderBook Module - Shared Market State Manager

The OrderBook receives price data from the Gateway and maintains the latest
prices in shared memory, making them available to the Strategy process.

Key Concepts:
- TCP client socket programming
- Message parsing and buffering
- Shared memory updates with synchronization
- Reconnection logic for fault tolerance

Learning Objectives:
- Understand TCP client socket lifecycle
- Implement message buffering and parsing
- Update shared memory atomically
- Handle network failures gracefully

Architecture:
    Gateway --> OrderBook (this module) --> Shared Memory --> Strategy

Usage:
    python -m finm_python.hw8.orderbook

TODO: Implement the OrderBook that receives prices and updates shared memory.
"""

import socket
import time
import logging
from typing import List, Optional
from multiprocessing import Lock

from .shared_memory_utils import (
    MESSAGE_DELIMITER,
    DEFAULT_PORT_GATEWAY_PRICE,
    DEFAULT_BUFFER_SIZE,
    SharedPriceBook,
    parse_price_message,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("OrderBook")


class MessageBuffer:
    """
    Buffer for handling partial TCP messages.

    TCP is a stream protocol, so messages may arrive in chunks.
    This buffer accumulates data until complete messages (delimited
    by MESSAGE_DELIMITER) are available.

    Attributes:
        buffer (bytes): Accumulated data
        delimiter (bytes): Message delimiter

    Example:
        buf = MessageBuffer()
        buf.add_data(b"AAPL,150.25*MS")
        messages = buf.get_complete_messages()
        # Returns: [b"AAPL,150.25"]
        # Buffer still contains: b"MS"

        buf.add_data(b"FT,300.50*")
        messages = buf.get_complete_messages()
        # Returns: [b"MSFT,300.50"]
    """

    def __init__(self):
        """Initialize an empty message buffer."""
        # TODO: Implement initialization
        # self.buffer = b""
        # self.delimiter = MESSAGE_DELIMITER
        raise NotImplementedError("Implement MessageBuffer initialization")

    def add_data(self, data: bytes) -> None:
        """
        Add received data to the buffer.

        Args:
            data: Raw bytes received from socket

        Implementation Steps:
            1. Append data to internal buffer
        """
        # TODO: Implement data addition
        # self.buffer += data
        raise NotImplementedError("Implement add_data method")

    def get_complete_messages(self) -> List[bytes]:
        """
        Extract all complete messages from the buffer.

        A complete message is one that ends with MESSAGE_DELIMITER.
        Returns messages without the delimiter.
        Leaves any partial message in the buffer.

        Returns:
            List of complete message bytes (without delimiters)

        Implementation Steps:
            1. Split buffer on delimiter
            2. Complete messages are all parts except the last
            3. The last part is incomplete (stays in buffer)
            4. Return list of complete messages

        Hints:
            - Use bytes.split(delimiter)
            - If buffer ends with delimiter, last element will be empty
            - Keep incomplete part for next call
        """
        # TODO: Implement message extraction
        # parts = self.buffer.split(self.delimiter)
        # # All except last are complete
        # complete = parts[:-1]
        # # Last part is incomplete
        # self.buffer = parts[-1]
        # return complete
        raise NotImplementedError("Implement get_complete_messages method")


class OrderBook:
    """
    Receives price updates from Gateway and updates shared memory.

    Connects to the Gateway's price stream, parses incoming price messages,
    and updates the SharedPriceBook so the Strategy can read current prices.

    Attributes:
        symbols (List[str]): List of symbols being tracked
        price_book (SharedPriceBook): Shared memory price storage
        gateway_host (str): Gateway server address
        gateway_port (int): Gateway server port
        running (bool): Process running state
    """

    def __init__(self, symbols: List[str],
                 shared_memory_name: Optional[str] = None,
                 gateway_host: str = "localhost",
                 gateway_port: int = DEFAULT_PORT_GATEWAY_PRICE,
                 lock: Optional[Lock] = None):
        """
        Initialize the OrderBook.

        Args:
            symbols: List of symbols to track
            shared_memory_name: Optional name of existing shared memory.
                               If None, creates new shared memory.
            gateway_host: Gateway server address
            gateway_port: Gateway server port
            lock: Optional lock for shared memory synchronization

        Implementation Steps:
            1. Store symbols and connection parameters
            2. Create or attach to SharedPriceBook
            3. Initialize connection state variables
            4. Set running = False

        Hints:
            - If shared_memory_name is None, you're creating the memory
            - If it's provided, you're attaching to existing memory
        """
        # TODO: Implement initialization
        # self.symbols = symbols
        # self.gateway_host = gateway_host
        # self.gateway_port = gateway_port
        #
        # self.price_book = SharedPriceBook(
        #     symbols=symbols,
        #     name=shared_memory_name,
        #     lock=lock
        # )
        #
        # self.socket = None
        # self.running = False
        # self.message_buffer = MessageBuffer()
        raise NotImplementedError("Implement OrderBook initialization")

    @property
    def shared_memory_name(self) -> str:
        """Get the name of the shared memory block."""
        # TODO: Return the shared memory name
        # return self.price_book.name
        raise NotImplementedError("Implement shared_memory_name property")

    def connect_to_gateway(self) -> bool:
        """
        Establish connection to the Gateway price server.

        Returns:
            True if connection successful, False otherwise

        Implementation Steps:
            1. Create TCP client socket
            2. Connect to gateway_host:gateway_port
            3. Return True on success
            4. Log and return False on failure
        """
        # TODO: Implement connection establishment
        # try:
        #     self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #     self.socket.connect((self.gateway_host, self.gateway_port))
        #     logger.info(f"Connected to Gateway at {self.gateway_host}:{self.gateway_port}")
        #     return True
        # except Exception as e:
        #     logger.error(f"Failed to connect to Gateway: {e}")
        #     return False
        raise NotImplementedError("Implement connect_to_gateway method")

    def receive_and_update(self) -> int:
        """
        Receive price data and update shared memory.

        Receives data from socket, parses messages, and updates the
        shared memory price book.

        Returns:
            Number of price updates processed

        Implementation Steps:
            1. Receive data from socket (non-blocking with timeout)
            2. Add to message buffer
            3. Get complete messages
            4. Parse each message and update price book
            5. Return count of updates

        Hints:
            - Use socket.settimeout(1.0) for non-blocking
            - Handle socket.timeout exception
            - parse_price_message returns (symbol, price)
        """
        # TODO: Implement receive and update
        # try:
        #     self.socket.settimeout(1.0)
        #     data = self.socket.recv(DEFAULT_BUFFER_SIZE)
        #
        #     if not data:
        #         logger.warning("Gateway closed connection")
        #         return -1
        #
        #     self.message_buffer.add_data(data)
        #     messages = self.message_buffer.get_complete_messages()
        #
        #     update_count = 0
        #     for msg in messages:
        #         if msg:
        #             symbol, price = parse_price_message(msg)
        #             if symbol in self.symbols:
        #                 self.price_book.update(symbol, price)
        #                 update_count += 1
        #                 logger.debug(f"Updated {symbol}: {price:.2f}")
        #
        #     return update_count
        #
        # except socket.timeout:
        #     return 0
        # except Exception as e:
        #     logger.error(f"Error receiving data: {e}")
        #     return -1
        raise NotImplementedError("Implement receive_and_update method")

    def run(self, duration: Optional[float] = None,
            reconnect_attempts: int = 3,
            reconnect_delay: float = 2.0) -> None:
        """
        Main loop for the OrderBook process.

        Connects to Gateway and continuously receives and processes
        price updates, with reconnection logic for fault tolerance.

        Args:
            duration: Optional duration to run (None = run forever)
            reconnect_attempts: Number of reconnection attempts on failure
            reconnect_delay: Seconds to wait between reconnection attempts

        Implementation Steps:
            1. Set running = True
            2. Connect to gateway (with retries)
            3. Main loop:
               - Receive and update prices
               - Handle disconnection with reconnect
               - Check for duration timeout
            4. Clean up on exit

        Hints:
            - Track start time for duration check
            - Use reconnect logic when receive_and_update returns -1
            - Log statistics periodically
        """
        # TODO: Implement main run loop
        # self.running = True
        # start_time = time.time()
        # total_updates = 0
        #
        # # Initial connection
        # attempts = 0
        # while attempts < reconnect_attempts and self.running:
        #     if self.connect_to_gateway():
        #         break
        #     attempts += 1
        #     time.sleep(reconnect_delay)
        # else:
        #     logger.error("Failed to connect to Gateway")
        #     return
        #
        # logger.info("OrderBook running...")
        #
        # try:
        #     while self.running:
        #         # Check duration
        #         if duration and (time.time() - start_time) >= duration:
        #             break
        #
        #         # Receive and update
        #         count = self.receive_and_update()
        #
        #         if count == -1:
        #             # Connection lost, try to reconnect
        #             logger.warning("Connection lost, attempting reconnect...")
        #             # ... reconnection logic
        #         elif count > 0:
        #             total_updates += count
        #
        # except KeyboardInterrupt:
        #     logger.info("OrderBook interrupted")
        # finally:
        #     self.stop()
        #     logger.info(f"OrderBook processed {total_updates} updates")

        raise NotImplementedError("Implement run method")

    def stop(self) -> None:
        """
        Stop the OrderBook process.

        Implementation Steps:
            1. Set running = False
            2. Close socket connection
            3. Close shared memory (but don't unlink)
        """
        # TODO: Implement stop
        # self.running = False
        # if self.socket:
        #     self.socket.close()
        # self.price_book.close()
        # logger.info("OrderBook stopped")
        raise NotImplementedError("Implement stop method")

    def cleanup(self) -> None:
        """
        Clean up shared memory resources.

        Call this only from the process that created the shared memory,
        after all other processes have stopped.
        """
        # TODO: Implement cleanup
        # self.price_book.unlink()
        # logger.info("Shared memory cleaned up")
        raise NotImplementedError("Implement cleanup method")


def run_orderbook(symbols: List[str] = None,
                  gateway_host: str = "localhost",
                  gateway_port: int = DEFAULT_PORT_GATEWAY_PRICE,
                  duration: Optional[float] = None) -> str:
    """
    Main entry point to run the OrderBook process.

    Args:
        symbols: List of symbols to track (default: common tech stocks)
        gateway_host: Gateway server address
        gateway_port: Gateway server port
        duration: Optional duration to run

    Returns:
        Name of the shared memory block (for Strategy to connect)

    Usage:
        # Run and get shared memory name
        shm_name = run_orderbook(symbols=["AAPL", "MSFT"], duration=60.0)
        print(f"Shared memory: {shm_name}")
    """
    # TODO: Implement orderbook runner
    # if symbols is None:
    #     symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]
    #
    # logger.info(f"Starting OrderBook for symbols: {symbols}")
    #
    # orderbook = OrderBook(
    #     symbols=symbols,
    #     gateway_host=gateway_host,
    #     gateway_port=gateway_port
    # )
    #
    # shm_name = orderbook.shared_memory_name
    # logger.info(f"Shared memory name: {shm_name}")
    #
    # try:
    #     orderbook.run(duration=duration)
    # finally:
    #     orderbook.cleanup()
    #
    # return shm_name

    raise NotImplementedError("Implement orderbook runner")


if __name__ == "__main__":
    run_orderbook()
