from abc import ABC, abstractmethod
from trading_system.hw2 import Portfolio


class PositionSizer(ABC):
    """Abstract base class for position-sizing logic"""

    @abstractmethod
    def calc_qty(
            self,
            signal: list,  # [action, symbol, qty_hint, price]
            portfolio: Portfolio,
            price: float
    ) -> int:
        """
        Convert a signal into a concrete share quantity.

        Args:
            signal: Raw signal from strategy
            portfolio: Current portfolio state
            price: Current price for the symbol

        Returns:
            Number of shares to trade (positive for buy, negative for sell)
        """
        pass


class FixedShareSizer(PositionSizer):
    """Always trade a fixed number of shares"""

    def __init__(self, shares: int = 1):
        self.shares = shares

    def calc_qty(self, signal, portfolio, price):
        action = signal[0]
        if action == 'Buy':
            return self.shares
        elif action == 'Sell':
            return -self.shares
        return 0


class FixedDollarSizer(PositionSizer):
    """Trade a fixed dollar amount"""

    def __init__(self, dollar_amount: float = 10000):
        self.dollar_amount = dollar_amount

    def calc_qty(self, signal, portfolio, price):
        action = signal[0]
        if action == 'Buy':
            return int(self.dollar_amount / price)
        elif action == 'Sell':
            return -int(self.dollar_amount / price)
        return 0


class PercentPortfolioSizer(PositionSizer):
    """
    Trade a percentage of current portfolio value.
    Useful for dynamic position sizing that adapts to P&L.
    """

    def __init__(self, percent: float = 0.02):
        """
        Args:
            percent: Fraction of portfolio to allocate (e.g., 0.02 = 2%)
        """
        self.percent = percent
        self._cached_portfolio_value = None
        self._cached_prices = None

    def set_portfolio_value(self, value: float):
        """Cache portfolio value to avoid recalculating"""
        self._cached_portfolio_value = value

    def calc_qty(self, signal, portfolio, price):
        action = signal[0]

        if action not in ['Buy', 'Sell']:
            return 0

        # Use cached value if available, otherwise use init cash
        if self._cached_portfolio_value:
            target_value = self._cached_portfolio_value * self.percent
        else:
            target_value = portfolio.init_cash * self.percent

        shares = int(target_value / price)

        return shares if action == 'Buy' else -shares


class EqualWeightSizer(PositionSizer):
    """
    Equal-weight allocation across N symbols.
    Best for benchmark strategies.
    """

    def __init__(self, total_symbols: int):
        """
        Args:
            total_symbols: Total number of symbols in the universe
        """
        self.total_symbols = total_symbols

    def calc_qty(self, signal, portfolio, price):
        action = signal[0]

        if action != 'Buy':
            return 0

        # Equal-weight based on initial capital
        target_value = portfolio.init_cash / self.total_symbols
        shares = int(target_value / price)

        return shares


class VolatilityScaledSizer(PositionSizer):
    """
    Size positions inversely to volatility (risk parity approach).
    Lower volatility = larger position, higher volatility = smaller position.
    """

    def __init__(self, target_risk: float = 0.01, lookback: int = 20):
        """
        Args:
            target_risk: Target risk per position (e.g., 0.01 = 1% risk)
            lookback: Days to calculate volatility
        """
        self.target_risk = target_risk
        self.lookback = lookback
        self._price_history = {}  # symbol -> list of prices

    def update_prices(self, symbol: str, price: float):
        """Update price history for volatility calculation"""
        if symbol not in self._price_history:
            self._price_history[symbol] = []
        self._price_history[symbol].append(price)

        # Keep only recent history
        if len(self._price_history[symbol]) > self.lookback:
            self._price_history[symbol] = self._price_history[symbol][-self.lookback:]

    def calc_qty(self, signal, portfolio, price):
        action, symbol = signal[0], signal[1]

        if action != 'Buy':
            return 0

        # Need enough history
        if symbol not in self._price_history or len(self._price_history[symbol]) < self.lookback:
            return 0

        # Calculate volatility
        prices = self._price_history[symbol]
        returns = [(prices[i] - prices[i - 1]) / prices[i - 1] for i in range(1, len(prices))]
        volatility = (sum(r ** 2 for r in returns) / len(returns)) ** 0.5

        if volatility == 0:
            return 0

        # Size inversely to volatility
        position_value = portfolio.init_cash * self.target_risk / volatility
        shares = int(position_value / price)

        return shares