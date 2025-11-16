"""
Analytics module using Decorator pattern.

Provides convenience functions for adding analytics capabilities
to instruments without modifying their base classes.
"""

from typing import Optional

from .models import Instrument
from .patterns.structural import (
    VolatilityDecorator,
    BetaDecorator,
    DrawdownDecorator
)


def add_volatility_analysis(
    instrument: Instrument,
    historical_returns: Optional[list[float]] = None
) -> VolatilityDecorator:
    """
    Add volatility calculation capability to an instrument.

    Args:
        instrument: Base instrument.
        historical_returns: List of historical daily returns.

    Returns:
        Decorated instrument with volatility metrics.
    """
    return VolatilityDecorator(instrument, historical_returns)


def add_beta_analysis(
    instrument: Instrument,
    instrument_returns: Optional[list[float]] = None,
    market_returns: Optional[list[float]] = None
) -> BetaDecorator:
    """
    Add beta calculation capability to an instrument.

    Args:
        instrument: Base instrument.
        instrument_returns: Historical returns of instrument.
        market_returns: Historical returns of market benchmark.

    Returns:
        Decorated instrument with beta metrics.
    """
    return BetaDecorator(instrument, instrument_returns, market_returns)


def add_drawdown_analysis(
    instrument: Instrument,
    price_history: Optional[list[float]] = None
) -> DrawdownDecorator:
    """
    Add maximum drawdown calculation to an instrument.

    Args:
        instrument: Base instrument.
        price_history: Historical price series.

    Returns:
        Decorated instrument with drawdown metrics.
    """
    return DrawdownDecorator(instrument, price_history)


def add_full_analytics(
    instrument: Instrument,
    historical_returns: Optional[list[float]] = None,
    market_returns: Optional[list[float]] = None,
    price_history: Optional[list[float]] = None
) -> Instrument:
    """
    Add all analytics decorators to an instrument.

    Stacks volatility, beta, and drawdown decorators.

    Args:
        instrument: Base instrument.
        historical_returns: Historical returns for volatility/beta.
        market_returns: Market benchmark returns for beta.
        price_history: Price history for drawdown.

    Returns:
        Fully decorated instrument.

    Example:
        >>> stock = Stock("AAPL", 172.35, "Technology", "Apple Inc.")
        >>> decorated = add_full_analytics(
        ...     stock,
        ...     historical_returns=[0.01, -0.02, 0.015, ...],
        ...     market_returns=[0.005, -0.01, 0.008, ...],
        ...     price_history=[170.0, 172.0, 168.0, ...]
        ... )
        >>> metrics = decorated.get_metrics()
        >>> # metrics now includes volatility, beta, and max_drawdown
    """
    # Stack decorators
    decorated = VolatilityDecorator(instrument, historical_returns)
    decorated = BetaDecorator(decorated, historical_returns, market_returns)
    decorated = DrawdownDecorator(decorated, price_history)
    return decorated


def calculate_returns(prices: list[float]) -> list[float]:
    """
    Calculate simple returns from price series.

    Args:
        prices: List of historical prices.

    Returns:
        List of simple returns (percentage changes).
    """
    if len(prices) < 2:
        return []

    returns = []
    for i in range(1, len(prices)):
        ret = (prices[i] - prices[i - 1]) / prices[i - 1]
        returns.append(ret)

    return returns


def calculate_log_returns(prices: list[float]) -> list[float]:
    """
    Calculate logarithmic returns from price series.

    Args:
        prices: List of historical prices.

    Returns:
        List of log returns.
    """
    import math

    if len(prices) < 2:
        return []

    returns = []
    for i in range(1, len(prices)):
        if prices[i - 1] > 0 and prices[i] > 0:
            ret = math.log(prices[i] / prices[i - 1])
            returns.append(ret)

    return returns
