from typing import List
from src.pyquant.hw1.data_loader import MarketDataPoint
from src.pyquant.hw1.strategies import MACrossing, Strategy
from src.pyquant.hw1.models import OrderError, Order, ExecutionError


def create_order(signal: list) -> Order:
    try:
        action, symbol, qty, price = signal
        # Handle order error
        if qty < 0:
            raise OrderError(f"Invalid quantity: {qty}")
        if price <= 0:
            raise OrderError(f"Invalid price: {qty}")

        # Translate action to a numeric direction
        if action == 'Buy':
            direction = 1
        elif action == 'Sell':
            direction = -1
        else:
            direction = 0
        qty *= direction
    except (TypeError, ValueError) as e:
        raise OrderError(f"Malformed signal: {signal}") from e

    return Order(symbol, qty, price, 'pending')


def execute_order(portfolio: dict, order: Order) -> dict:
    symbol = order.symbol
    qty = order.quantity
    price = order.price
    position = portfolio.get(symbol, {'quantity': 0, 'avg_price': 0.0})

    # Avoid negative positions
    if position['quantity'] < qty:
        raise ExecutionError(
            f"Insufficient shares to sell: have {position['quantity']}, trying to sell {qty}")

    try:
        if qty > 0:
            avg_price = (
                position['avg_price'] * position['quantity'] + price * qty
            ) / (position['quantity'] + qty)
        else:
            # If sell or hold, remain avg_price unchanged
            # avg_price indicates the entry cost, not the current market price
            avg_price = position['avg_price']

        portfolio[symbol]['quantity'] = qty
        portfolio[symbol]['avg_price'] = avg_price
    except (TypeError, ValueError) as e:
        raise ExecutionError from e

    return portfolio


class Engine:
    def __init__(
            self,
            ticks: List[MarketDataPoint],
            strategies: List[Strategy]
    ) -> None:
        self._portfolios = dict()
        self._ticks = ticks.sort(key=lambda tick: tick.timestamp)
        self._symbols = [tick.symbol for tick in ticks]
        self._strategies = strategies

        # Initialize portfolio dictionary
        # eg. {'MACrossing': {'AAPL': {'quantity': 0, 'avg_price': 0.0}}}
        for strategy in strategies:
            name = strategy.__class__.__name__
            self._portfolios[name] = dict()
            for symbol in self._symbols:
                self._portfolios[name][symbol] = {
                    'quantity': 0, 'avg_price': 0.0
                }

    def run(self) -> dict:
        """
        Iterate through the list of MarketDataPoint objects in timestamp order.

        For each tick:
        - Invoke each strategy to generate signals
        - Instantiate and validate Order objects
        - Execute orders by updating the portfolio dictionary
        """
        # Iterate in timestamp order
        for tick in self._ticks:
            for strategy in self._strategies:
                name = strategy.__class__.__name__
                portfolio = self._portfolios[name]
                signal = strategy.generate_signals(tick)

                # Create and Execute order
                order = create_order(signal)
                self._portfolios[name] = execute_order(portfolio, order)

        return self._portfolios