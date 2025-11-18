"""
Structural Design Patterns

- Decorator: Add analytics to instruments without modifying base classes
- Adapter: Standardize external data formats
- Composite: (Implemented in models.py as PortfolioComponent hierarchy)
"""

import json
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from ..models import Instrument, MarketDataPoint


# ============================================================================
# Decorator Pattern
# ============================================================================

class InstrumentDecorator(Instrument):
    """
    Base decorator for adding functionality to instruments.

    Wraps an instrument and delegates base operations while allowing
    extension of behavior.
    """

    def __init__(self, instrument: Instrument):
        """
        Initialize the decorator with a wrapped instrument.

        Args:
            instrument: The instrument to decorate.
        """
        self._instrument = instrument
        # Delegate basic properties
        super().__init__(instrument.symbol, instrument.price)

    def get_type(self) -> str:
        """Delegate to a wrapped instrument."""
        return self._instrument.get_type()

    def get_metrics(self) -> dict:
        """Get metrics from a wrapped instrument (to be extended by subclasses)."""
        return self._instrument.get_metrics()


class VolatilityDecorator(InstrumentDecorator):
    """
    Decorator that adds volatility calculation to an instrument.

    Computes annualized volatility based on historical returns.
    """

    def __init__(self, instrument: Instrument, historical_returns: Optional[list[float]] = None):
        """
        Initialize volatility decorator.

        Args:
            instrument: The instrument to decorate.
            historical_returns: Optional list of historical returns for calculation.
        """
        super().__init__(instrument)
        self._historical_returns = historical_returns or []

    def calculate_volatility(self) -> float:
        """
        Calculate annualized volatility.

        Returns:
            Annualized volatility (assuming 252 trading days).
        """
        rets = self._historical_returns
        n = len(rets)
        if n < 2:
            return 0.0
        mean_ret = sum(rets) / n
        sample_var = sum([(ret - mean_ret) ** 2 for ret in rets]) / (n - 1)
        daily_vol = sample_var ** 0.5
        annualized_vol = daily_vol * 252 ** 0.5
        return annualized_vol

    def get_metrics(self) -> dict:
        """Add volatility metric to base metrics."""
        metrics = super().get_metrics()
        metrics["volatility"] = self.calculate_volatility()
        return metrics


class BetaDecorator(InstrumentDecorator):
    """
    Decorator that adds beta calculation to an instrument.

    Beta measures systematic risk relative to market benchmark.
    """

    def __init__(self, instrument: Instrument,
                 instrument_returns: Optional[list[float]] = None,
                 market_returns: Optional[list[float]] = None):
        """
        Initialize beta decorator.

        Args:
            instrument: The instrument to decorate.
            instrument_returns: Historical returns of the instrument.
            market_returns: Historical returns of the market benchmark.
        """
        super().__init__(instrument)
        self._instrument_returns = instrument_returns or []
        self._market_returns = market_returns or []

    def calculate_beta(self) -> float:
        """
        Calculate beta coefficient.

        Returns:
            Beta value (covariance / market variance).
        """
        if (not self._instrument_returns or not self._market_returns
                or len(self._instrument_returns) != len(self._market_returns)
                or len(self._instrument_returns) < 2):
            return 1.0

        n = len(self._instrument_returns)
        mean_ins = sum(self._instrument_returns) / n
        mean_mkt = sum(self._market_returns) / n

        cov = sum(
            (self._instrument_returns[i] - mean_ins) * (self._market_returns[i] - mean_mkt)
            for i in range(n)
        ) / (n - 1)

        var = sum(
            (self._market_returns[i] - mean_mkt) ** 2 for i in range(n)
        ) / (n - 1)

        if var == 0:
            return 1.0

        return cov / var

    def get_metrics(self) -> dict:
        """Add beta metric to base metrics."""
        metrics = super().get_metrics()
        metrics["beta"] = self.calculate_beta()
        return metrics


class DrawdownDecorator(InstrumentDecorator):
    """
    Decorator that adds maximum drawdown calculation to an instrument.

    Maximum drawdown measures the largest peak-to-trough decline.
    """

    def __init__(self, instrument: Instrument, price_history: Optional[list[float]] = None):
        """
        Initialize drawdown decorator.

        Args:
            instrument: The instrument to decorate.
            price_history: Historical price series.
        """
        super().__init__(instrument)
        self._price_history = price_history or []

    def calculate_max_drawdown(self) -> float:
        """
        Calculate maximum drawdown.

        Returns:
            Maximum drawdown as a negative percentage.
        """
        n = len(self._price_history)
        if n < 2:
            return 0.0

        peak = self._price_history[0]
        max_dd = 0
        for i, price in enumerate(self._price_history):
            if price > peak:
                peak = price

            drawdown = (price - peak) / peak
            if drawdown < max_dd:
                max_dd = drawdown

        return max_dd

    def get_metrics(self) -> dict:
        """Add maximum drawdown metric to base metrics."""
        metrics = super().get_metrics()
        metrics["max_drawdown"] = self.calculate_max_drawdown()
        return metrics


# ============================================================================
# Adapter Pattern
# ============================================================================

class MarketDataAdapter:
    """
    Abstract adapter for converting external data to MarketDataPoint.
    """

    def get_data(self, symbol: str) -> MarketDataPoint:
        """
        Get standardized market data for a symbol.

        Args:
            symbol: Instrument symbol.

        Returns:
            MarketDataPoint instance.
        """
        raise NotImplementedError("Subclasses must implement get_data")


class YahooFinanceAdapter(MarketDataAdapter):
    """
    Adapter for Yahoo Finance JSON format.

    Converts Yahoo Finance JSON structure to MarketDataPoint.

    Expected JSON format (single or list):
    {
        "ticker": "AAPL",
        "last_price": 172.35,
        "timestamp": "2024-01-15T10:30:00Z",
        "volume": 1000000
    }
    """

    def __init__(self, data_source: str | Path | dict):
        """
        Initialize adapter with data source.

        Args:
            data_source: Path to JSON file or dictionary with data.
        """
        if isinstance(data_source, dict):
            self._data = data_source
        else:
            with open(data_source, "r") as f:
                self._data = json.load(f)

    def get_data(self, symbol: str) -> MarketDataPoint:
        """
        Convert Yahoo Finance data to MarketDataPoint.

        Args:
            symbol: Instrument symbol (for validation).

        Returns:
            MarketDataPoint instance.

        Raises:
            ValueError: If symbol doesn't match data.
        """
        # TODO: Implement Yahoo Finance data conversion
        # 1. Handle both single ticker dict and list of tickers
        #    - If list, find matching ticker
        #    - If dict, verify ticker matches symbol
        # 2. Extract timestamp and convert to datetime
        #    (use datetime.fromisoformat, replace "Z" with "+00:00")
        # 3. Return MarketDataPoint with:
        #    - symbol from "ticker" field
        #    - price from "last_price" field
        #    - timestamp
        #    - volume from "volume" field (optional)
        #    - metadata with source="yahoo_finance"
        raise NotImplementedError("TODO: Implement YahooFinanceAdapter.get_data")


class BloombergXMLAdapter(MarketDataAdapter):
    """
    Adapter for Bloomberg XML format.

    Converts Bloomberg XML structure to MarketDataPoint.

    Expected XML format:
    <instrument>
        <symbol>AAPL</symbol>
        <price>172.35</price>
        <timestamp>2024-01-15T10:30:00Z</timestamp>
    </instrument>

    Or multiple instruments:
    <instruments>
        <instrument>...</instrument>
        <instrument>...</instrument>
    </instruments>
    """

    def __init__(self, data_source: str | Path | ET.Element):
        """
        Initialize adapter with data source.

        Args:
            data_source: Path to XML file or parsed ElementTree.
        """
        if isinstance(data_source, ET.Element):
            self._root = data_source
        else:
            tree = ET.parse(data_source)
            self._root = tree.getroot()

    def get_data(self, symbol: str) -> MarketDataPoint:
        """
        Convert Bloomberg XML data to MarketDataPoint.

        Args:
            symbol: Instrument symbol (for validation).

        Returns:
            MarketDataPoint instance.

        Raises:
            ValueError: If symbol doesn't match data.
        """
        # TODO: Implement Bloomberg XML data conversion
        # 1. Handle both single <instrument> and <instruments> (list) root
        #    - If root is "instruments", find matching <instrument> by <symbol>
        #    - If root is single instrument, verify symbol matches
        # 2. Extract data from XML elements using .find() and .text
        # 3. Convert timestamp string to datetime
        # 4. Return MarketDataPoint with:
        #    - symbol from <symbol> element
        #    - price from <price> element (convert to float)
        #    - timestamp
        #    - volume=None
        #    - metadata with source="bloomberg"
        raise NotImplementedError("TODO: Implement BloombergXMLAdapter.get_data")
