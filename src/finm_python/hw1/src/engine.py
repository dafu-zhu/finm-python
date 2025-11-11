import random
from typing import List, Dict
from finm_python.hw1 import MarketDataPoint
from finm_python.hw1.src.strategies import Strategy, StrategyState
from finm_python.hw1.src.models import OrderError, Order, ExecutionError, Portfolio, Position


class ExecutionEngine:
    def __init__(
            self,
            ticks: List[MarketDataPoint],
            strategies: List[Strategy],
            init_cash: float,
            allow_short: bool = False
    ) -> None:
        self._states: Dict[str, StrategyState] = {}
        self._ticks: List[MarketDataPoint] = sorted(ticks, key=lambda tick: tick.timestamp)
        self._strategies: List[Strategy] = strategies
        self._allow_short: bool = allow_short
        self._symbols = list(set(tick.symbol for tick in ticks))    # get unique symbols

        # Initialize portfolio dictionary
        # eg. {'MACrossingStrategy': {'AAPL': {'quantity': 0, 'avg_price': 0.0}}}
        for strategy in strategies:
            name = strategy.__repr__()

            # Create a strategy state
            state = StrategyState(
                strategy = strategy,
                portfolio = Portfolio(init_cash, self._symbols),
                orders = [],
                order_errors = [],
                execution_errors = [],
                history = []
            )

            self._states[name] = state

    def create_order(self, name: str,  signal: list) -> Order:
        try:
            action, symbol, qty, price = signal
        except ValueError as e:
            raise OrderError(f"Malformed signal: expected 4 elements, got {len(signal)}") from e

        # Translate action to a numeric direction
        if action == 'Buy':
            direction = 1
        elif action == 'Sell':
            direction = -1
        else:
            direction = 0
        qty *= direction

        portfolio = self._states[name].portfolio
        position = portfolio.positions.get(symbol, Position(symbol))

        # Avoid negative positions
        if position.quantity < abs(qty) and qty < 0:
            raise OrderError(f"Not enough shares to sell: "
                             f"expected sell {abs(qty)}, got {position.quantity}")
        # Cash limitation
        if portfolio.cash < qty * price:
            raise OrderError(f"Not enough cash to buy: "
                             f"need {qty * price:.2f}, got {portfolio.cash:.2f}")

        return Order(symbol, qty, price, 'pending')

    def execute_order(self, name: str, order: Order) -> None:

        # After validation passes, simulate random failures
        if random.random() < 0.01:  # 1% failure rate
            raise ExecutionError(f"Market rejected order: {order}")

        self._states[name].portfolio.update_position(
            symbol = order.symbol,
            qty = order.quantity,
            price = order.price
        )

    def run(self) -> dict:
        """
        Iterate through the list of MarketDataPoint objects in timestamp order.

        For each tick:
        - Invoke each strategy to generate signals
        - Instantiate and validate Order objects
        - Execute orders by updating the portfolio dictionary
        """
        # Track current prices across all ticks
        current_prices = {symbol: 0.0 for symbol in self._symbols}

        # Iterate in timestamp order
        for tick in self._ticks:
            current_prices[tick.symbol] = tick.price
            current_time = tick.timestamp

            for strategy in self._strategies:
                name = strategy.__repr__()
                signal = strategy.generate_signals(tick)
                state = self._states[name]

                # Create and Execute order
                try:
                    order = self.create_order(name, signal)
                except OrderError as e:
                    state.order_errors.append(f"{tick.timestamp}: {e}")
                    continue

                try:
                    self.execute_order(name, order)
                    order.status = 'success'
                except ExecutionError as e:
                    order.status = 'failed'
                    state.execution_errors.append(f"{tick.timestamp}: {e}")

                state.orders.append(order)
                value = state.portfolio.get_value(current_prices)
                state.history.append((current_time, round(value)))

        return self._states