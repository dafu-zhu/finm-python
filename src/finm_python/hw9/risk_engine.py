"""
Risk Check Engine

This module implements a risk management system that validates orders against
position limits and order size limits before they are sent to the market.

The risk engine tracks positions across multiple symbols and enforces:
- Maximum order size per order
- Maximum position per symbol (considering buy/sell directions)

Risk checks are performed before an order is acknowledged, and positions are
updated after fills.
"""

from typing import Dict, Optional
from .order import Order


class RiskEngine:
    """
    Risk management engine for validating and tracking trading orders.

    The engine maintains position tracking for multiple symbols and enforces
    risk limits to prevent excessive exposure.

    Attributes:
        max_order_size (int): Maximum quantity allowed in a single order
        max_position (int): Maximum absolute position allowed per symbol
        positions (Dict[str, int]): Current position for each symbol
                                   (positive for long, negative for short)
    """

    def __init__(self, max_order_size: int = 1000, max_position: int = 2000):
        """
        Initialize the risk engine with limit parameters.

        Args:
            max_order_size (int): Maximum quantity per order (default: 1000)
            max_position (int): Maximum absolute position per symbol (default: 2000)

        TODO: Initialize the following:
        1. Store max_order_size and max_position
        2. Initialize positions as an empty dictionary
        """
        pass

    def check(self, order: Order) -> bool:
        """
        Validate an order against risk limits.

        Performs the following checks:
        1. Order size doesn't exceed max_order_size
        2. Resulting position won't exceed max_position (considering direction)

        Args:
            order (Order): The order to validate

        Returns:
            bool: True if order passes all risk checks

        Raises:
            ValueError: If order violates max_order_size limit
            ValueError: If order would cause position to exceed max_position

        TODO: Implement the following steps:
        1. Check if order.qty > max_order_size
           - If yes, raise ValueError with descriptive message
        2. Calculate what the position would be after this order
           - Get current position for the symbol (default to 0)
           - Add or subtract order qty based on side ('1' = buy adds, '2' = sell subtracts)
        3. Check if absolute value of new position exceeds max_position
           - If yes, raise ValueError with descriptive message
        4. If all checks pass, return True

        Example:
            Current position in AAPL: 1500 long
            New buy order for 600 shares
            New position would be: 2100 (exceeds limit of 2000)
            -> Raise ValueError
        """
        pass

    def update_position(self, order: Order) -> None:
        """
        Update position tracking after an order is filled.

        Should only be called for filled orders. Updates the position for
        the order's symbol based on the filled quantity and direction.

        Args:
            order (Order): The filled order

        TODO: Implement the following:
        1. Get current position for order.symbol (default to 0 if not tracked)
        2. Determine the quantity to add/subtract based on:
           - side='1' (Buy): add to position
           - side='2' (Sell): subtract from position
        3. Update positions dictionary
        4. Print a message showing new position
           Example: "Position update: AAPL = 1500 shares"
        """
        pass

    def get_position(self, symbol: str) -> int:
        """
        Get the current position for a symbol.

        Args:
            symbol (str): The trading symbol

        Returns:
            int: Current position (positive for long, negative for short, 0 if no position)

        TODO: Return the position for the symbol, or 0 if not in dictionary
        """
        pass

    def get_available_capacity(self, symbol: str, side: str) -> int:
        """
        Calculate how many shares can be traded in the given direction
        without exceeding position limits.

        Args:
            symbol (str): The trading symbol
            side (str): Order side ('1' for Buy, '2' for Sell)

        Returns:
            int: Maximum quantity that can be traded, or 0 if at limit

        TODO: Implement the following:
        1. Get current position
        2. If buying (side='1'):
           - Return max_position - current_position
        3. If selling (side='2'):
           - Return max_position + current_position (since selling reduces position)
        4. Return 0 if already at or beyond limit

        Example:
            Current position: 1500 long
            Max position: 2000
            Buy capacity: 500 (can buy up to 500 more)
            Sell capacity: 3500 (can sell 1500 to flatten + 2000 more to go short)
        """
        pass

    def reset_positions(self) -> None:
        """
        Reset all position tracking.

        Useful for testing or end-of-day position flattening.

        TODO: Clear the positions dictionary
        TODO: Print a message indicating positions have been reset
        """
        pass

    def get_all_positions(self) -> Dict[str, int]:
        """
        Get a copy of all current positions.

        Returns:
            Dict[str, int]: Dictionary mapping symbols to their positions

        TODO: Return a copy of the positions dictionary
        """
        pass

    def check_position_limit_breach(self, symbol: str) -> bool:
        """
        Check if a symbol's position is currently breaching the limit.

        This is a diagnostic method to detect if positions have somehow
        exceeded limits (e.g., due to fast market moves or system errors).

        Args:
            symbol (str): The trading symbol to check

        Returns:
            bool: True if position exceeds limit, False otherwise

        TODO: Get position for symbol and check if abs(position) > max_position
        """
        pass

    def __str__(self) -> str:
        """
        String representation of the risk engine state.

        Returns:
            str: Summary of risk engine configuration and current positions

        TODO: Return a formatted string showing:
        1. Risk limits (max_order_size, max_position)
        2. Current positions for all symbols
        """
        pass


def main():
    """
    Example usage and testing of the RiskEngine.

    TODO: Create test scenarios:
    1. Create a risk engine with specific limits
    2. Create orders that pass risk checks
    3. Create orders that violate order size limits
    4. Create orders that would violate position limits
    5. Update positions and verify tracking
    """
    from .order import Order, OrderState

    print("Testing Risk Engine")
    print("-" * 50)

    # TODO: Create a RiskEngine with max_order_size=500, max_position=1000
    # risk = RiskEngine(max_order_size=500, max_position=1000)

    # TODO: Create a valid order and check it
    # order1 = Order(symbol='AAPL', qty=300, side='1', price=150.00)

    # TODO: Try to check the order and handle any ValueError

    # TODO: If check passes, update position

    # TODO: Create an order that violates order size limit
    # order2 = Order(symbol='AAPL', qty=600, side='1', price=150.00)

    # TODO: Create an order that would violate position limit
    # (After order1, position is 300. An order for 800 more would exceed 1000)

    # TODO: Test selling to reduce position

    # TODO: Print all positions

    pass


if __name__ == "__main__":
    main()
