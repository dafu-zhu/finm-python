"""
Main Trading System Integration

This module integrates all components of the mini trading system:
- FIX Message Parser: Parses incoming FIX messages
- Order Lifecycle: Manages order state transitions
- Risk Engine: Validates orders against limits
- Event Logger: Records all system events

The flow is: FIX Message → Parser → Order → Risk Check → Logger

Example flow:
1. Receive raw FIX message
2. Parse into structured dictionary
3. Create Order object from parsed data
4. Check order against risk limits
5. If passed, acknowledge and fill
6. If failed, reject
7. Log all events
8. Save log to file
"""

from typing import List, Dict, Any
from .fix_parser import FixParser
from .order import Order, OrderState
from .risk_engine import RiskEngine
from .logger import Logger


class TradingSystem:
    """
    Main trading system that orchestrates all components.

    Attributes:
        parser (FixParser): FIX message parser
        risk_engine (RiskEngine): Risk management engine
        logger (Logger): Event logger
        orders (Dict[str, Order]): Dictionary of all orders by order_id
    """

    def __init__(
        self,
        max_order_size: int = 1000,
        max_position: int = 2000,
        log_file: str = "events.json"
    ):
        """
        Initialize the trading system with all components.

        Args:
            max_order_size (int): Maximum order size for risk engine
            max_position (int): Maximum position for risk engine
            log_file (str): Path to event log file

        TODO: Initialize the following:
        1. Create FixParser instance
        2. Create RiskEngine with specified limits
        3. Create Logger with specified log file
        4. Initialize orders dictionary
        """
        pass

    def process_fix_message(self, fix_message: str) -> Order:
        """
        Process a raw FIX message through the entire system.

        This is the main entry point for incoming messages. It:
        1. Parses the FIX message
        2. Creates an Order object
        3. Logs order creation
        4. Runs risk checks
        5. Transitions order state based on risk check result
        6. Logs the outcome

        Args:
            fix_message (str): Raw FIX protocol message

        Returns:
            Order: The created order object

        TODO: Implement the complete flow:
        1. Parse the FIX message using self.parser.parse()
        2. Extract relevant fields (symbol, qty, side, price if available)
        3. Create Order object
        4. Log "OrderCreated" event with parsed message data
        5. Try to run risk check:
           a. If passes: transition to ACKED, log "OrderAcked"
           b. If fails: catch ValueError, transition to REJECTED, log "OrderRejected"
        6. Store order in self.orders dictionary
        7. Return the order
        """
        pass

    def fill_order(self, order_id: str, qty: int = None) -> bool:
        """
        Fill an order (simulate execution).

        Args:
            order_id (str): ID of the order to fill
            qty (int): Quantity to fill (None = fill entire order)

        Returns:
            bool: True if fill was successful

        TODO: Implement the following:
        1. Look up order in self.orders
        2. If not found, return False
        3. Determine fill quantity (use qty parameter or order.qty)
        4. Call order.fill(qty)
        5. Update risk engine position
        6. Log "OrderFilled" event with details
        7. Return True
        8. Handle any exceptions and return False if they occur
        """
        pass

    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order.

        Args:
            order_id (str): ID of the order to cancel

        Returns:
            bool: True if cancellation was successful

        TODO: Implement the following:
        1. Look up order in self.orders
        2. If not found, return False
        3. Attempt to cancel the order
        4. If successful, log "OrderCanceled" event
        5. Return the result
        """
        pass

    def get_order(self, order_id: str) -> Order:
        """
        Retrieve an order by ID.

        Args:
            order_id (str): The order ID to look up

        Returns:
            Order: The order object, or None if not found

        TODO: Return order from self.orders dictionary, or None if not found
        """
        pass

    def get_all_orders(self) -> List[Order]:
        """
        Get all orders in the system.

        Returns:
            List[Order]: List of all order objects

        TODO: Return list of all orders from self.orders.values()
        """
        pass

    def get_orders_by_state(self, state: OrderState) -> List[Order]:
        """
        Filter orders by their current state.

        Args:
            state (OrderState): The state to filter by

        Returns:
            List[Order]: All orders in the specified state

        TODO: Filter orders and return those with matching state
        """
        pass

    def print_status(self) -> None:
        """
        Print current system status.

        TODO: Print the following:
        1. Number of orders by state
        2. Current positions from risk engine
        3. Number of logged events
        """
        pass

    def shutdown(self) -> None:
        """
        Gracefully shutdown the system.

        TODO: Implement the following:
        1. Print final status
        2. Save logger events to file
        3. Print summary of logged events
        """
        pass


def process_single_message_example():
    """
    Example from the homework: Process a single FIX message.

    This demonstrates the basic flow with one message.
    """
    print("Single Message Example")
    print("=" * 60)

    # TODO: Initialize components
    # fix = FixParser()
    # risk = RiskEngine()
    # log = Logger()

    # TODO: Process the example message from homework
    # raw = "8=FIX.4.2|35=D|55=AAPL|54=1|38=500|40=2|10=128"

    # TODO: Parse message
    # msg = fix.parse(raw)

    # TODO: Create order
    # order = Order(msg["55"], int(msg["38"]), msg["54"])
    # log.log("OrderCreated", msg)

    # TODO: Risk check and state transitions
    # try:
    #     risk.check(order)
    #     order.transition(OrderState.ACKED)
    #     risk.update_position(order)
    #     order.transition(OrderState.FILLED)
    #     log.log("OrderFilled", {"symbol": order.symbol, "qty": order.qty})
    # except ValueError as e:
    #     order.transition(OrderState.REJECTED)
    #     log.log("OrderRejected", {"reason": str(e)})

    # TODO: Save log
    # log.save()

    pass


def process_multiple_messages_example():
    """
    Example: Process multiple FIX messages using TradingSystem class.

    This demonstrates handling multiple orders with different outcomes.
    """
    print("\nMultiple Messages Example")
    print("=" * 60)

    # Sample FIX messages
    messages = [
        "8=FIX.4.2|35=D|55=AAPL|54=1|38=500|40=2|44=150.00|10=128",
        "8=FIX.4.2|35=D|55=GOOGL|54=1|38=300|40=2|44=2800.00|10=129",
        "8=FIX.4.2|35=D|55=AAPL|54=2|38=200|40=2|44=151.00|10=130",
        "8=FIX.4.2|35=D|55=MSFT|54=1|38=1500|40=2|44=380.00|10=131",  # Should fail: too large
        "8=FIX.4.2|35=D|55=AAPL|54=1|38=800|40=2|44=149.00|10=132",  # Should fail: position limit
    ]

    # TODO: Create TradingSystem instance
    # system = TradingSystem(max_order_size=1000, max_position=2000)

    # TODO: Process each message
    # for i, msg in enumerate(messages, 1):
    #     print(f"\nProcessing message {i}...")
    #     order = system.process_fix_message(msg)
    #     print(f"Order {order.order_id}: {order.symbol} {order.qty} - State: {order.state.name}")

    # TODO: Simulate fills for acknowledged orders
    # for order in system.get_orders_by_state(OrderState.ACKED):
    #     system.fill_order(order.order_id)

    # TODO: Print final status
    # system.print_status()

    # TODO: Shutdown and save
    # system.shutdown()

    pass


def interactive_demo():
    """
    Interactive demo allowing user to send FIX messages.

    TODO: Create an interactive loop where user can:
    1. Enter FIX messages
    2. View current orders
    3. Fill orders
    4. Cancel orders
    5. View positions
    6. Exit and save
    """
    print("\nInteractive Trading System Demo")
    print("=" * 60)
    print("Commands:")
    print("  send <fix_message>  - Send a FIX message")
    print("  fill <order_id>     - Fill an order")
    print("  cancel <order_id>   - Cancel an order")
    print("  status              - Show system status")
    print("  quit                - Exit and save")
    print()

    # TODO: Implement interactive loop
    pass


def main():
    """
    Main entry point - run various examples.

    TODO: Uncomment and run the examples you want to test:
    1. Single message example
    2. Multiple messages example
    3. Interactive demo
    """
    print("Mini Trading System")
    print("=" * 60)
    print()

    # Run examples
    # process_single_message_example()
    # process_multiple_messages_example()
    # interactive_demo()

    print("\nTODO: Implement the examples above!")
    print("Uncomment the function calls in main() to test each component.")


if __name__ == "__main__":
    main()
