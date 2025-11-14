import random
from typing import Dict, List, Iterable, Tuple
import polars as pl
import logging

from finm_python.hw1.src.data_loader import MarketDataPoint
from finm_python.hw1.src.strategies import Strategy, StrategyState
from finm_python.hw1.src.models import (Order, OrderError, ExecutionError)
from finm_python.hw2 import Portfolio, Position
from finm_python.hw2 import PositionSizer

logging.basicConfig(
    level=logging.INFO,
    filename='./engine.log',
    filemode='w',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)



class ExecutionEngine:
    """
    Backtesting engine that processes market data day-by-day.

    Key improvements:
    - Accepts generators/iterables for memory efficiency
    - Single-pass consumption of tick data
    - Batches ticks by trading day
    - Maintains price cache across days
    - One portfolio valuation per day
    """

    def __init__(
            self,
            ticks: Iterable[MarketDataPoint],
            strategies: List[Tuple[Strategy, PositionSizer]],
            symbols: List[str],
            init_cash: float,
            allow_short: bool = False
    ) -> None:
        """
        Initialize the execution engine.

        Args:
            ticks: Iterable of market data (can be generator for memory efficiency)
            strategies: List of trading strategies
            symbols: list of symbols from price loader
            init_cash: Initial cash per strategy
            allow_short: Whether to allow short selling
        """
        self._ticks: Iterable[MarketDataPoint] = ticks
        self._symbols: List[str] = symbols
        self._strategies: List[Tuple[Strategy, PositionSizer]] = strategies
        self._allow_short: bool = allow_short

        # Price cache - carries forward last known prices
        self._last_known_prices: Dict[str, float] = {symbol: 0.0 for symbol in self._symbols}

        # Initialize strategy states
        self._states: Dict[str, StrategyState] = {}
        for strategy, sizer in strategies:
            name = strategy.__repr__()

            state = StrategyState(
                strategy=strategy,
                portfolio=Portfolio(init_cash),
                orders=[],
                order_errors=[],
                execution_errors=[],
                history=[]
            )

            self._states[name] = state

    def run(self):
        # Tracker
        prev_time = None

        for tick in self._ticks:
            # Track current prices across all ticks
            self._last_known_prices[tick.symbol] = tick.price
            current_time = tick.timestamp

            # Check for date change BEFORE processing strategies
            if prev_time is not None and prev_time.date() != current_time.date():
                if prev_time.month != current_time.month:
                    logging.info(f"Processing {prev_time.date()}")

                # Record portfolio value for ALL strategies for the completed day
                for strategy, sizer in self._strategies:
                    name = strategy.__repr__()
                    state = self._states[name]
                    value = state.portfolio.get_value(self._last_known_prices)
                    state.history.append((prev_time.date(), round(value, 2)))

                # Update tracker
                prev_time = current_time

            if prev_time is None:
                prev_time = current_time
                logging.info(f"Processing {prev_time.date()}")

            for strategy, sizer in self._strategies:
                signal = strategy.generate_signals(tick)
                if not signal:
                    continue

                action, symbol, qty, price = signal

                if action == 'Hold':
                    continue

                name = strategy.__repr__()
                state = self._states[name]

                # Create and Execute order
                quantity = sizer.calc_qty(signal, state.portfolio, tick.price)
                new_signal = [action, symbol, quantity, price]

                try:
                    order = self._create_order(name, new_signal)
                except OrderError as e:
                    state.order_errors.append(f"{tick.timestamp}: {e}")
                    continue

                try:
                    self._execute_order(name, order)
                    order.status = 'success'
                except ExecutionError as e:
                    order.status = 'failed'
                    state.execution_errors.append(f"{tick.timestamp}: {e}")

                state.orders.append(order)

        return self._states

    def _calc_portfolio_value(self, state):
        value = state.portfolio.cash
        positions = state.portfolio.positions
        for symbol in positions:
            price = self._last_known_prices[symbol]
            value += positions[symbol].quantity * price
        return value

    def _create_order(self, name: str, signal: list) -> Order:
        try:
            action, symbol, qty, price = signal
        except ValueError as e:
            raise OrderError(f"Malformed signal: expected 4 elements, got {len(signal)}") from e

        portfolio = self._states[name].portfolio
        position = portfolio.positions.get(symbol, Position(symbol))

        # Avoid negative positions
        if not self._allow_short and position.quantity < abs(qty) and qty < 0:
            raise OrderError(f"Not enough shares to sell: "
                             f"expected sell {abs(qty)}, got {position.quantity}")
        # Cash limitation
        if portfolio.cash < qty * price:
            raise OrderError(f"Not enough cash to buy: "
                             f"need {qty * price:.2f}, got {portfolio.cash:.2f}")

        return Order(symbol, qty, price, 'pending')

    def _execute_order(self, name: str, order: Order) -> None:

        # After validation passes, simulate random failures
        if random.random() < 0.01:  # 1% failure rate
            raise ExecutionError(f"Market rejected order: {order}")

        self._states[name].portfolio.update_position(
            symbol = order.symbol,
            qty = order.quantity,
            price = order.price
        )


if __name__ == "__main__":
    data = pl.read_parquet('../../../data/raw/sp500.parquet')
    print(data.tail())
    # engine = ExecutionEngine()
