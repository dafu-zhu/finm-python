"""
Order Lifecycle Simulator

This module implements the order lifecycle management system, which tracks orders
through their various states from creation to completion.

An order goes through a state machine with specific allowed transitions:
- NEW -> ACKED or REJECTED
- ACKED -> FILLED or CANCELED

Invalid transitions are logged and prevented.
"""

from enum import Enum, auto
from typing import Optional
from datetime import datetime


class OrderState(Enum):
    """
    Enumeration of possible order states.

    The order lifecycle follows this state machine:

        NEW ──┬──> ACKED ──┬──> FILLED
              │            │
              └──> REJECTED│
                           └──> CANCELED

    States:
        NEW: Order has been created but not yet acknowledged by the exchange
        ACKED: Order has been acknowledged and is active in the market
        FILLED: Order has been completely executed
        CANCELED: Order was canceled before being filled
        REJECTED: Order was rejected (e.g., failed risk checks)
    """
    NEW = auto()
    ACKED = auto()
    FILLED = auto()
    CANCELED = auto()
    REJECTED = auto()


class Order:
    """
    Represents a trading order with state management.

    Attributes:
        symbol (str): The trading symbol (e.g., 'AAPL', 'GOOGL')
        qty (int): Order quantity (number of shares)
        side (str): Order side ('1' for Buy, '2' for Sell)
        price (Optional[float]): Limit price (None for market orders)
        state (OrderState): Current state of the order
        order_id (str): Unique identifier for the order
        timestamp (datetime): When the order was created
        filled_qty (int): Quantity that has been filled so far
    """

    # Class variable to generate unique order IDs
    _next_order_id = 1

    def __init__(
        self,
        symbol: str,
        qty: int,
        side: str,
        price: Optional[float] = None,
        order_id: Optional[str] = None
    ):
        """
        Initialize a new order.

        Args:
            symbol (str): Trading symbol (e.g., 'AAPL')
            qty (int): Order quantity
            side (str): Order side ('1' for Buy, '2' for Sell)
            price (Optional[float]): Limit price (None for market orders)
            order_id (Optional[str]): Custom order ID (auto-generated if None)

        TODO: Initialize all order attributes:
        1. Set symbol, qty, side, and price from parameters
        2. Set state to OrderState.NEW
        3. Generate or use provided order_id
        4. Set timestamp to current time
        5. Initialize filled_qty to 0
        6. Increment _next_order_id class variable if auto-generating ID
        """
        pass

    def transition(self, new_state: OrderState) -> bool:
        """
        Transition the order to a new state.

        Validates that the transition is allowed based on the state machine rules.
        If the transition is invalid, logs a warning and returns False without
        changing the state.

        Valid transitions:
        - NEW -> ACKED
        - NEW -> REJECTED
        - ACKED -> FILLED
        - ACKED -> CANCELED

        Args:
            new_state (OrderState): The desired new state

        Returns:
            bool: True if transition was successful, False if not allowed

        TODO: Implement the following steps:
        1. Define the allowed transitions dictionary (see docstring above)
        2. Check if current state allows transition to new_state
        3. If allowed:
           - Update self.state to new_state
           - Print a message like "Order {symbol} is now {new_state.name}"
           - Return True
        4. If not allowed:
           - Print a warning message
           - Return False
        """
        pass

    def get_allowed_transitions(self) -> set:
        """
        Get the set of states that the order can transition to from its current state.

        Returns:
            set: Set of OrderState values that are valid transitions from current state

        TODO: Return the allowed transitions for the current state
        TODO: Return an empty set if no transitions are allowed
        """
        pass

    def fill(self, qty: int) -> None:
        """
        Record a partial or full fill of the order.

        Updates the filled quantity and transitions to FILLED state if
        the entire order has been filled.

        Args:
            qty (int): Quantity filled in this execution

        Raises:
            ValueError: If fill quantity exceeds remaining quantity
            ValueError: If order is not in ACKED state

        TODO: Implement the following:
        1. Validate that order is in ACKED state
        2. Validate that filled_qty + qty doesn't exceed total qty
        3. Update filled_qty
        4. If fully filled (filled_qty == qty), transition to FILLED
        5. Print a message indicating the fill
        """
        pass

    def cancel(self) -> bool:
        """
        Attempt to cancel the order.

        Only orders in ACKED state can be canceled.

        Returns:
            bool: True if cancellation was successful, False otherwise

        TODO: Check if order is in ACKED state
        TODO: If yes, transition to CANCELED and return True
        TODO: If no, return False
        """
        pass

    def is_terminal_state(self) -> bool:
        """
        Check if the order is in a terminal state.

        Terminal states are FILLED, CANCELED, or REJECTED - states from which
        no further transitions are possible.

        Returns:
            bool: True if order is in a terminal state, False otherwise

        TODO: Return True if state is FILLED, CANCELED, or REJECTED
        """
        pass

    def get_side_name(self) -> str:
        """
        Get a human-readable name for the order side.

        Returns:
            str: 'Buy' if side is '1', 'Sell' if side is '2', otherwise the raw value

        TODO: Implement a mapping from FIX side codes to readable names
        """
        pass

    def __str__(self) -> str:
        """
        String representation of the order.

        Returns:
            str: Formatted string with order details

        TODO: Return a formatted string like:
        "Order {order_id}: {side_name} {qty} {symbol} @ {price} - State: {state}"
        """
        pass

    def __repr__(self) -> str:
        """
        Developer-friendly representation of the order.

        Returns:
            str: String that could be used to recreate the order

        TODO: Return a string like:
        "Order(symbol='{symbol}', qty={qty}, side='{side}', price={price}, state={state})"
        """
        pass


def main():
    """
    Example usage and testing of the Order class.

    TODO: Create several test scenarios:
    1. Create an order and transition it through valid states
    2. Try an invalid state transition and observe the error
    3. Test partial fills
    4. Test order cancellation
    """
    print("Testing Order Lifecycle")
    print("-" * 50)

    # TODO: Create a new order for AAPL
    # order = Order(symbol='AAPL', qty=100, side='1', price=150.00)

    # TODO: Print the order

    # TODO: Transition through valid states: NEW -> ACKED -> FILLED

    # TODO: Create another order and try an invalid transition
    # Example: NEW -> FILLED (should fail)

    # TODO: Create an order and test cancellation

    pass


if __name__ == "__main__":
    main()
