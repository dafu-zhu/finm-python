"""
Main Orchestration Module for HW8: Interprocess Communication Trading System

This module orchestrates all four components of the trading system:
- Gateway: Streams price and news data
- OrderBook: Maintains shared memory price store
- Strategy: Generates trading signals
- OrderManager: Receives and logs trades

Learning Objectives:
- Understand process lifecycle management
- Coordinate startup order dependencies
- Handle inter-process communication setup
- Manage shared resources across processes

Architecture:
    [ Gateway ] --> [ OrderBook ] --> [ Strategy ] --> [ OrderManager ]
         |              |                  |
    (prices/news)  (shared mem)       (signals)         (trade log)

Usage:
    python -m finm_python.hw8.main

TODO: Implement the orchestration to start and coordinate all processes.
"""

import time
import logging
from multiprocessing import Process, Queue, Lock
from typing import Optional, Dict, List

# TODO: Import the component modules
# from .gateway import run_gateway
# from .orderbook import run_orderbook
# from .strategy import run_strategy
# from .order_manager import run_order_manager
# from .shared_memory_utils import DEFAULT_PORT_GATEWAY_PRICE, DEFAULT_PORT_GATEWAY_NEWS, DEFAULT_PORT_ORDER_MANAGER

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("Main")


def create_gateway_process(price_port: int, news_port: int,
                           duration: Optional[float] = None) -> Process:
    """
    Create the Gateway process.

    Args:
        price_port: Port for price stream server
        news_port: Port for news stream server
        duration: Optional duration to run

    Returns:
        Process object (not started)

    Implementation Steps:
        1. Create Process with target=run_gateway
        2. Pass appropriate arguments
        3. Return the process

    Hints:
        - Use Process(target=func, args=(...))
        - Don't start the process here, just create it
    """
    # TODO: Implement gateway process creation
    # from .gateway import run_gateway
    # return Process(
    #     target=run_gateway,
    #     args=(price_port, news_port, duration),
    #     name="Gateway"
    # )
    raise NotImplementedError("Implement create_gateway_process")


def create_orderbook_process(symbols: List[str],
                             gateway_host: str,
                             gateway_port: int,
                             shared_memory_queue: Queue,
                             lock: Lock,
                             duration: Optional[float] = None) -> Process:
    """
    Create the OrderBook process.

    The OrderBook creates shared memory and communicates the name
    back to the main process via a Queue.

    Args:
        symbols: List of symbols to track
        gateway_host: Gateway server address
        gateway_port: Gateway price port
        shared_memory_queue: Queue to send shared memory name
        lock: Shared lock for memory synchronization
        duration: Optional duration to run

    Returns:
        Process object (not started)

    Implementation Steps:
        1. Define wrapper function that:
           - Creates OrderBook
           - Sends shared memory name via queue
           - Runs the OrderBook
        2. Create Process with wrapper as target
        3. Return the process
    """
    # TODO: Implement orderbook process creation
    # from .orderbook import OrderBook
    #
    # def orderbook_wrapper():
    #     orderbook = OrderBook(
    #         symbols=symbols,
    #         gateway_host=gateway_host,
    #         gateway_port=gateway_port,
    #         lock=lock
    #     )
    #     # Send shared memory name back to main process
    #     shared_memory_queue.put(orderbook.shared_memory_name)
    #     orderbook.run(duration=duration)
    #     orderbook.cleanup()
    #
    # return Process(target=orderbook_wrapper, name="OrderBook")
    raise NotImplementedError("Implement create_orderbook_process")


def create_strategy_process(symbol: str,
                            symbols: List[str],
                            shared_memory_name: str,
                            news_host: str,
                            news_port: int,
                            order_manager_host: str,
                            order_manager_port: int,
                            lock: Lock,
                            duration: Optional[float] = None) -> Process:
    """
    Create the Strategy process.

    Args:
        symbol: Symbol to trade
        symbols: All symbols in shared memory
        shared_memory_name: Name of shared memory block
        news_host: Gateway news server address
        news_port: Gateway news port
        order_manager_host: OrderManager server address
        order_manager_port: OrderManager port
        lock: Shared lock for memory synchronization
        duration: Optional duration to run

    Returns:
        Process object (not started)

    Implementation Steps:
        1. Create Process with target=run_strategy
        2. Pass all necessary arguments
        3. Return the process
    """
    # TODO: Implement strategy process creation
    # from .strategy import Strategy
    #
    # def strategy_wrapper():
    #     strategy = Strategy(
    #         symbol=symbol,
    #         symbols=symbols,
    #         shared_memory_name=shared_memory_name,
    #         news_host=news_host,
    #         news_port=news_port,
    #         order_manager_host=order_manager_host,
    #         order_manager_port=order_manager_port,
    #         lock=lock
    #     )
    #     strategy.run(duration=duration)
    #
    # return Process(target=strategy_wrapper, name=f"Strategy-{symbol}")
    raise NotImplementedError("Implement create_strategy_process")


def create_order_manager_process(host: str, port: int,
                                 duration: Optional[float] = None) -> Process:
    """
    Create the OrderManager process.

    Args:
        host: Server bind address
        port: Server bind port
        duration: Optional duration to run

    Returns:
        Process object (not started)

    Implementation Steps:
        1. Create Process with target=run_order_manager
        2. Pass appropriate arguments
        3. Return the process
    """
    # TODO: Implement order manager process creation
    # from .order_manager import run_order_manager
    # return Process(
    #     target=run_order_manager,
    #     args=(host, port, duration),
    #     name="OrderManager"
    # )
    raise NotImplementedError("Implement create_order_manager_process")


def measure_startup_latency(start_time: float) -> float:
    """
    Measure time since start for latency tracking.

    Args:
        start_time: Time when measurement started

    Returns:
        Elapsed time in seconds
    """
    # TODO: Implement latency measurement
    # return time.time() - start_time
    raise NotImplementedError("Implement measure_startup_latency")


def wait_for_process_ready(process: Process, timeout: float = 5.0) -> bool:
    """
    Wait for a process to be ready (started and running).

    Args:
        process: Process to wait for
        timeout: Maximum time to wait

    Returns:
        True if process is running, False if timeout

    Implementation Steps:
        1. Record start time
        2. Loop until timeout:
           - Check if process is alive
           - If alive, return True
           - Small sleep to avoid busy wait
        3. Return False if timeout reached
    """
    # TODO: Implement wait for ready
    # start = time.time()
    # while time.time() - start < timeout:
    #     if process.is_alive():
    #         return True
    #     time.sleep(0.1)
    # return False
    raise NotImplementedError("Implement wait_for_process_ready")


def run_trading_system(duration: float = 60.0,
                       symbols: List[str] = None,
                       trade_symbol: str = "AAPL") -> Dict:
    """
    Main orchestration function to run the complete trading system.

    Starts all four processes in the correct order, manages shared
    resources, and collects performance metrics.

    Args:
        duration: Total time to run the system (seconds)
        symbols: List of symbols to track
        trade_symbol: Specific symbol for Strategy to trade

    Returns:
        Dictionary with system metrics:
        {
            "startup_time": float,
            "total_runtime": float,
            "processes_started": int,
            "shared_memory_name": str
        }

    Process Startup Order (Dependencies):
        1. OrderManager - must be ready to receive orders
        2. Gateway - must be ready to send data
        3. OrderBook - connects to Gateway, creates shared memory
        4. Strategy - connects to OrderBook (shared mem) and Gateway (news)

    Implementation Steps:
        1. Set default symbols if None
        2. Create shared resources (Queue for shm name, Lock for sync)
        3. Create all process objects
        4. Start processes in dependency order:
           a. Start OrderManager, wait for ready
           b. Start Gateway, wait for ready
           c. Start OrderBook, wait for ready
           d. Get shared memory name from queue
           e. Start Strategy
        5. Wait for all processes to complete
        6. Clean up resources
        7. Return metrics

    Hints:
        - Use Queue.get(timeout=10) to get shared memory name
        - Add small delays between startups for stability
        - Use process.join() to wait for completion
        - Wrap in try/finally for cleanup
    """
    # TODO: Implement main orchestration
    # logger.info("=" * 50)
    # logger.info("Starting Interprocess Trading System")
    # logger.info("=" * 50)
    #
    # if symbols is None:
    #     symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]
    #
    # start_time = time.time()
    #
    # # Shared resources
    # shared_memory_queue = Queue()
    # shared_lock = Lock()
    #
    # # Create processes
    # order_manager_process = create_order_manager_process(
    #     "localhost", DEFAULT_PORT_ORDER_MANAGER, duration
    # )
    # gateway_process = create_gateway_process(
    #     DEFAULT_PORT_GATEWAY_PRICE, DEFAULT_PORT_GATEWAY_NEWS, duration
    # )
    # orderbook_process = create_orderbook_process(
    #     symbols, "localhost", DEFAULT_PORT_GATEWAY_PRICE,
    #     shared_memory_queue, shared_lock, duration
    # )
    #
    # processes = []
    #
    # try:
    #     # 1. Start OrderManager first (it's the sink)
    #     logger.info("Starting OrderManager...")
    #     order_manager_process.start()
    #     processes.append(order_manager_process)
    #     time.sleep(0.5)  # Give time to bind port
    #
    #     # 2. Start Gateway (data source)
    #     logger.info("Starting Gateway...")
    #     gateway_process.start()
    #     processes.append(gateway_process)
    #     time.sleep(0.5)
    #
    #     # 3. Start OrderBook (connects to Gateway)
    #     logger.info("Starting OrderBook...")
    #     orderbook_process.start()
    #     processes.append(orderbook_process)
    #
    #     # 4. Get shared memory name from OrderBook
    #     logger.info("Waiting for shared memory setup...")
    #     shared_memory_name = shared_memory_queue.get(timeout=10)
    #     logger.info(f"Shared memory created: {shared_memory_name}")
    #
    #     # 5. Start Strategy
    #     strategy_process = create_strategy_process(
    #         trade_symbol, symbols, shared_memory_name,
    #         "localhost", DEFAULT_PORT_GATEWAY_NEWS,
    #         "localhost", DEFAULT_PORT_ORDER_MANAGER,
    #         shared_lock, duration
    #     )
    #     logger.info(f"Starting Strategy for {trade_symbol}...")
    #     strategy_process.start()
    #     processes.append(strategy_process)
    #
    #     startup_time = measure_startup_latency(start_time)
    #     logger.info(f"All processes started in {startup_time:.2f}s")
    #
    #     # Wait for all processes to complete
    #     logger.info(f"System running for {duration} seconds...")
    #     for p in processes:
    #         p.join()
    #
    #     total_runtime = time.time() - start_time
    #
    #     logger.info("=" * 50)
    #     logger.info("Trading System Completed")
    #     logger.info("=" * 50)
    #
    #     return {
    #         "startup_time": startup_time,
    #         "total_runtime": total_runtime,
    #         "processes_started": len(processes),
    #         "shared_memory_name": shared_memory_name
    #     }
    #
    # except Exception as e:
    #     logger.error(f"Error during orchestration: {e}")
    #     raise
    # finally:
    #     # Cleanup: terminate any still-running processes
    #     for p in processes:
    #         if p.is_alive():
    #             p.terminate()
    #             p.join()

    raise NotImplementedError("Implement run_trading_system")


def main():
    """
    Main entry point for the trading system.

    Runs the complete system for a default duration with default configuration.

    Expected Implementation:
        1. Set configuration parameters
        2. Call run_trading_system
        3. Print final metrics
        4. Handle any errors gracefully
    """
    print("=" * 60)
    print("HW8: Interprocess Communication for Trading Systems")
    print("=" * 60)

    # TODO: Implement main entry point
    #
    # Configuration
    # duration = 30.0  # Run for 30 seconds
    # symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]
    # trade_symbol = "AAPL"
    #
    # try:
    #     metrics = run_trading_system(
    #         duration=duration,
    #         symbols=symbols,
    #         trade_symbol=trade_symbol
    #     )
    #
    #     print("\n" + "=" * 60)
    #     print("System Metrics:")
    #     print(f"  Startup Time: {metrics['startup_time']:.2f} seconds")
    #     print(f"  Total Runtime: {metrics['total_runtime']:.2f} seconds")
    #     print(f"  Processes Started: {metrics['processes_started']}")
    #     print(f"  Shared Memory: {metrics['shared_memory_name']}")
    #     print("=" * 60)
    #
    # except KeyboardInterrupt:
    #     print("\nSystem interrupted by user")
    # except Exception as e:
    #     print(f"\nError running system: {e}")
    #     raise

    raise NotImplementedError("Implement main orchestration")


if __name__ == "__main__":
    main()
