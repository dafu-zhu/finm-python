from src.trading_system.hw1.data_loader import MarketDataPoint
from src.trading_system.hw1.strategies import Strategy, StrategyState
from collections import deque
from datetime import datetime, timedelta

from collections import deque
from datetime import datetime, timedelta


class MovingAverageStrategy(Strategy):
    def __init__(self, params: dict = None):
        self.params = params if params else {}
        self._short_ma = self.params.get('short_ma', 20)
        self._long_ma = self.params.get('long_ma', 50)
        self._price_history = deque(maxlen=self._long_ma)

    def generate_signals(self, tick: MarketDataPoint) -> list:
        self._price_history.append(tick.price)

        if len(self._price_history) < self._long_ma:
            return []

        short_ma = sum(list(self._price_history)[-self._short_ma:]) / self._short_ma
        long_ma = sum(self._price_history) / self._long_ma

        if short_ma > long_ma:
            return ['Buy', tick.symbol, 100, tick.price]
        elif short_ma < long_ma:
            return ['Sell', tick.symbol, 100, tick.price]
        else:
            return ['Hold', tick.symbol, 100, tick.price]

    def __repr__(self):
        return f"MovingAverageStrategy_{self._short_ma}_{self._long_ma}"


class VolatilityBreakoutStrategy(Strategy):
    def __init__(self, params: dict = None):
        self.params = params if params else {}
        self._lookback = self.params.get('lookback', 20)
        self._price_history = deque(maxlen=self._lookback + 1)

    def generate_signals(self, tick: MarketDataPoint) -> list:
        self._price_history.append(tick.price)

        if len(self._price_history) < self._lookback + 1:
            return []

        # Calculate daily returns
        prices = list(self._price_history)
        returns = [(prices[i] - prices[i - 1]) / prices[i - 1]
                   for i in range(1, len(prices))]

        # Current return
        current_return = returns[-1]

        # Rolling standard deviation (excluding current)
        historical_returns = returns[:-1]
        mean_return = sum(historical_returns) / len(historical_returns)
        variance = sum((r - mean_return) ** 2
                       for r in historical_returns) / len(historical_returns)
        std_dev = variance ** 0.5

        if current_return > std_dev:
            return ['Buy', tick.symbol, 100, tick.price]
        elif current_return < -std_dev:
            return ['Sell', tick.symbol, 100, tick.price]
        else:
            return ['Hold', tick.symbol, 100, tick.price]

    def __repr__(self):
        return f"VolatilityBreakoutStrategy_{self._lookback}"


class MACDStrategy(Strategy):
    def __init__(self, params: dict = None):
        self.params = params if params else {}
        self._fast_period = self.params.get('fast_period', 12)
        self._slow_period = self.params.get('slow_period', 26)
        self._signal_period = self.params.get('signal_period', 9)
        self._price_history = deque(maxlen=self._slow_period + self._signal_period)
        self._macd_history = deque(maxlen=self._signal_period)
        self._prev_macd = None
        self._prev_signal = None

    @staticmethod
    def _calculate_ema(prices, period):
        """Calculate Exponential Moving Average"""
        multiplier = 2 / (period + 1)
        ema = sum(prices[:period]) / period  # Initial SMA

        for price in prices[period:]:
            ema = (price - ema) * multiplier + ema

        return ema

    def generate_signals(self, tick: MarketDataPoint) -> list:
        self._price_history.append(tick.price)

        if len(self._price_history) < self._slow_period:
            return []

        prices = list(self._price_history)

        # Calculate MACD line
        fast_ema = self._calculate_ema(prices, self._fast_period)
        slow_ema = self._calculate_ema(prices, self._slow_period)
        macd_line = fast_ema - slow_ema

        self._macd_history.append(macd_line)

        if len(self._macd_history) < self._signal_period:
            return []

        # Calculate signal line (EMA of MACD)
        signal_line = sum(self._macd_history) / len(self._macd_history)

        # Check for crossover
        signal = []
        if self._prev_macd is not None and self._prev_signal is not None:
            if self._prev_macd <= self._prev_signal and macd_line > signal_line:
                signal = ['Buy', tick.symbol, 100, tick.price]
            elif self._prev_macd >= self._prev_signal and macd_line < signal_line:
                signal = ['Sell', tick.symbol, 100, tick.price]
            else:
                signal = ['Hold', tick.symbol, 100, tick.price]

        self._prev_macd = macd_line
        self._prev_signal = signal_line

        return signal

    def __repr__(self):
        return (f"MACDStrategy_{self._fast_period}_"
                f"{self._slow_period}_{self._signal_period}")


class RSIStrategy(Strategy):
    def __init__(self, params: dict = None):
        self.params = params if params else {}
        self._period = self.params.get('period', 14)
        self._oversell_threshold = self.params.get('oversell_threshold', 30)
        self._overbuy_threshold = self.params.get('overbuy_threshold', 70)
        if self._oversell_threshold >= self._overbuy_threshold:
            raise ValueError("Oversell threshold must be less than overbuy threshold")
        self._price_history = deque(maxlen=self._period + 1)

    def generate_signals(self, tick: MarketDataPoint) -> list:
        self._price_history.append(tick.price)

        if len(self._price_history) < self._period + 1:
            return []

        prices = list(self._price_history)

        # Calculate price changes
        gains = []
        losses = []

        for i in range(1, len(prices)):
            change = prices[i] - prices[i - 1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))

        # Calculate average gain and loss
        avg_gain = sum(gains) / self._period
        avg_loss = sum(losses) / self._period

        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

        if rsi < self._oversell_threshold:
            return ['Buy', tick.symbol, 100, tick.price]
        elif rsi > self._overbuy_threshold:
            return ['Sell', tick.symbol, 100, tick.price]
        else:
            return ['Hold', tick.symbol, 100, tick.price]

    def __repr__(self):
        return (f"RSIStrategy_{self._period}_"
                f"{self._oversell_threshold}_{self._overbuy_threshold}")