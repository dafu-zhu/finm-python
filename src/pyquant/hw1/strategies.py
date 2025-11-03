from abc import ABC, abstractmethod
from typing import List, Tuple
from dataclasses import dataclass
from datetime import datetime
from collections import deque
from src.pyquant.hw1.data_loader import MarketDataPoint, data_ingestor
from src.pyquant.hw1.models import ConfigError, Portfolio, Order


class Strategy(ABC):
    """
    Blueprint of Strategy classes.
    """
    @abstractmethod
    def generate_signals(self, tick: MarketDataPoint) -> list:
        pass


@dataclass
class StrategyState:
    strategy: Strategy
    portfolio: Portfolio
    orders: List[Order]
    order_errors: List[str]
    execution_errors: List[str]
    history: List[Tuple[datetime, float]]


class MACDStrategy(Strategy):
    """
    MACD Crossing Strategy
    Logic:
    - when short-term MA > long-term MA, buy
    - when short-term MA < long-term MA, sell
    """
    def __init__(
            self,
            ticks: List[MarketDataPoint],
            params: dict
    ):
        try:
            short_period = params['short_period']
            long_period = params['long_period']
        except KeyError as e:
            raise ConfigError("Missing parameter") from e

        if not isinstance(short_period, int) and isinstance(long_period, int):
            raise TypeError("Periods should be integers")

        if short_period > long_period:
            raise ValueError("Long period should be longer than short period")

        self._ticks = ticks
        self._short_period = short_period
        self._long_period = long_period
        self._short_ma = []
        self._long_ma = []
        self._window = long_period
        self._prices = deque(maxlen=self._window)

    def __repr__(self):
        return f"MACD(short={self._short_period}, long={self._long_period})"

    def generate_signals(self, tick: MarketDataPoint) -> list:
        symbol = tick.symbol
        price = tick.price
        short_period = self._short_period
        long_period = self._long_period

        # prices excluding today (avoid future data)
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
            return ['Buy', symbol, 10, price]
        elif short_ma < long_ma:
            return ['Sell', symbol, 10, price]
        else:
            return ['Hold', symbol, 10, price]


class MomentumStrategy(Strategy):
    """
    Rate of Change Momentum Strategy
    Logic: Calculate price rate of change for the past, if > 2% buy, < 2% sell
    If today is the 32nd trade day, then the past 20 days count from the 12th to 31st day
    """
    def __init__(
            self,
            ticks: List[MarketDataPoint],
            params: dict
    ):
        self._ticks = ticks

        try:
            self._lookback = params['lookback']
            self._buy_threshold = params['buy_threshold']
            self._sell_threshold = params['sell_threshold']
        except KeyError as e:
            raise ConfigError("Missing parameter") from e

        if not isinstance(self._lookback, int):
            raise TypeError("Lookback should be integer")

        if not all(isinstance(var, float) for var in [self._buy_threshold, self._sell_threshold]):
            raise TypeError("Thresholds should be float")

        self._roc = []
        self._prices = deque(maxlen=self._lookback)

    def __repr__(self):
        return (f"Momentum(lookback={self._lookback}, "
                f"buy_threshold={self._buy_threshold}, "
                f"sell_threshold={self._sell_threshold})")

    def generate_signals(self, tick: MarketDataPoint) -> list:
        symbol = tick.symbol
        price = tick.price
        prices = self._prices

        # update prices buffer
        self._prices.append(price)
        if len(self._prices) > self._lookback:
            self._prices.popleft()

        # calculate indicators
        if prices[0] == 0:
            raise ZeroDivisionError('Invalid price data')
        roc = prices[-1] / prices[0] - 1
        self._roc.append(roc)

        if roc > self._buy_threshold:
            return ['Buy', symbol, 10, price]
        elif roc < self._sell_threshold:
            return ['Sell', symbol, 10, price]
        else:
            return ['Hold', symbol, 10, price]






