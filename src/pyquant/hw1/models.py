from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class Order:
    symbol: str
    quantity: int
    price: float
    status: str     # 'pending', 'filled', 'rejected'

    def __post_init__(self):
        # Handle order error
        if self.price <= 0:
            raise OrderError(f"Invalid price: {self.price}")


@dataclass
class Position:
    symbol: str
    quantity: int = 0
    avg_price: float = 0.0


class Portfolio:
    def __init__(self, init_cash: float, symbols: list):
        self.cash = init_cash
        self.positions: Dict[str, Position] = {
            symbol: Position(symbol) for symbol in symbols
        }

    def update_position(self, symbol: str, qty: int, price: float) -> None:
        position = self.positions[symbol]
        avg_price = position.avg_price

        # Calculate average price
        if qty > 0:
            # buy more shares
            avg_price = (
                position.avg_price * position.quantity + price * qty
            ) / (position.quantity + qty)

        # Update quantity and avg_price
        self.positions[symbol].quantity += qty
        self.positions[symbol].avg_price = avg_price
        self.cash -= qty * price

    def get_value(self, price_dict: Dict[str, float]) -> float:
        val = self.cash
        for symbol in self.positions:
            price = price_dict[symbol]
            val += self.positions[symbol].quantity * price
        return val


class OrderError(Exception):
    pass


class ExecutionError(Exception):
    pass


class ConfigError(Exception):
    pass