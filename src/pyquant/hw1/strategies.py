from abc import ABC, abstractmethod
from typing import List, Tuple
from collections import deque
from src.pyquant.hw1.data_loader import MarketDataPoint, data_ingestor


class Strategy(ABC):
    """
    Blueprint of Strategy classes.
    """
    @abstractmethod
    def generate_signals(self, tick: MarketDataPoint) -> list:
        pass


class MACrossing(Strategy):
    """
    Logic:
    - when short-term MA > long-term MA, buy
    - when short-term MA < long-term MA, sell
    """
    def __init__(
            self,
            ticks: List[MarketDataPoint],
            short_period: int,
            long_period: int
    ):
        if short_period > long_period:
            raise ValueError("Long period should be longer than short period")
        self._ticks = ticks
        self._short_period = short_period
        self._long_period = long_period
        self._short_ma = []
        self._long_ma = []
        self._window = long_period
        self._prices = deque(maxlen=self._window)

    def generate_signals(
            self,
            tick: MarketDataPoint
    ) -> List[str|int|float]:
        symbol = tick.symbol
        price = tick.price
        short_period = self._short_period
        long_period = self._long_period
        prices = self._prices

        # update price buffer
        self._prices.append(price)
        if len(self._prices) > self._window:
            self._prices.popleft()  # O(1) complexity

        # calculate indicators
        short_ma = sum(list(prices)[-short_period:]) / short_period
        long_ma = sum(list(prices)[-long_period:]) / long_period
        self._short_ma.append(short_ma)
        self._long_ma.append(long_ma)

        # generate a signal
        # format: (action, symbol, qty, price)
        if short_ma > long_ma:
            return ['Buy', symbol, 100, price]
        elif short_ma < long_ma:
            return ['Sell', symbol, 100, price]
        else:
            return ['Hold', symbol, 100, price]










