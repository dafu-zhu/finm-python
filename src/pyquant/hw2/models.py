from dataclasses import dataclass
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Dict


@dataclass
class Position:
    symbol: str
    quantity: int = 0
    avg_price: float = 0.0


class Portfolio:
    """Portfolio with lazy position creation and price tracking"""

    def __init__(self, init_cash: float):
        self.cash = init_cash
        self.init_cash = init_cash
        self.positions: Dict[str, Position] = {}  # Lazy creation

    def update_position(self, symbol: str, qty: int, price: float) -> None:
        """Update the position for a symbol, creating it lazily if needed"""
        # Lazy position creation
        if symbol not in self.positions:
            self.positions[symbol] = Position(symbol)

        position = self.positions[symbol]

        # Calculate new average price for buys
        if qty > 0:
            total_cost = position.avg_price * position.quantity + price * qty
            new_quantity = position.quantity + qty
            position.avg_price = total_cost / new_quantity if new_quantity > 0 else 0.0

        # Update quantity and cash
        position.quantity += qty    # Object Position is mutable
        self.cash -= qty * price

    def get_value(self, price_dict: Dict[str, float]) -> float:
        """Calculate total portfolio value given current prices"""
        total_value = self.cash

        for symbol, position in self.positions.items():
            if position.quantity > 0:
                price = price_dict.get(symbol, 0.0)
                total_value += position.quantity * price

        return total_value

    def get_position_quantity(self, symbol: str) -> int:
        """Get quantity for a symbol (0 if the position doesn't exist)"""
        return self.positions.get(symbol, Position(symbol)).quantity


@dataclass
class Signal:
    timestamp: datetime
    symbol: str
    action: str     # 'Buy', 'Sell', 'Hold'
    signal_strength: float = 1.0   # Optional: how strong is the signal?
    metadata: dict = None   # strategy specific data