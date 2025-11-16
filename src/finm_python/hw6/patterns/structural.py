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
        Initialize decorator with wrapped instrument.

        Args:
            instrument: The instrument to decorate.
        """
        self._instrument = instrument
        # Delegate basic properties
        super().__init__(instrument.symbol, instrument.price)

    def get_type(self) -> str:
        """Delegate to wrapped instrument."""
        return self._instrument.get_type()

    def get_metrics(self) -> dict:
        """Get metrics from wrapped instrument (to be extended by subclasses)."""
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
        if not self._historical_returns or len(self._historical_returns) < 2:
            return 0.0

        mean = sum(self._historical_returns) / len(self._historical_returns)
        variance = sum((r - mean) ** 2 for r in self._historical_returns) / (len(self._historical_returns) - 1)
        daily_vol = variance ** 0.5
        annualized_vol = daily_vol * (252 ** 0.5)
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
            return 1.0  # Default beta

        n = len(self._instrument_returns)
        mean_inst = sum(self._instrument_returns) / n
        mean_mkt = sum(self._market_returns) / n

        covariance = sum(
            (self._instrument_returns[i] - mean_inst) * (self._market_returns[i] - mean_mkt)
            for i in range(n)
        ) / (n - 1)

        market_variance = sum(
            (self._market_returns[i] - mean_mkt) ** 2
            for i in range(n)
        ) / (n - 1)

        if market_variance == 0:
            return 1.0

        return covariance / market_variance

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
        if not self._price_history or len(self._price_history) < 2:
            return 0.0

        peak = self._price_history[0]
        max_drawdown = 0.0

        for price in self._price_history:
            if price > peak:
                peak = price
            drawdown = (price - peak) / peak
            if drawdown < max_drawdown:
                max_drawdown = drawdown

        return max_drawdown

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
        # Handle both single ticker and list of tickers
        if isinstance(self._data, list):
            # Find matching ticker in list
            data_item = next((d for d in self._data if d.get("ticker") == symbol), None)
            if not data_item:
                raise ValueError(f"Symbol {symbol} not found in Yahoo data")
        else:
            data_item = self._data
            if data_item.get("ticker") != symbol:
                raise ValueError(f"Symbol mismatch: expected {symbol}, got {data_item.get('ticker')}")

        timestamp = datetime.fromisoformat(data_item["timestamp"].replace("Z", "+00:00"))

        return MarketDataPoint(
            symbol=data_item["ticker"],
            price=float(data_item["last_price"]),
            timestamp=timestamp,
            volume=data_item.get("volume"),
            metadata={"source": "yahoo_finance"}
        )


class BloombergXMLAdapter(MarketDataAdapter):
    """
    Adapter for Bloomberg XML format.

    Converts Bloomberg XML structure to MarketDataPoint.
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
        # Handle both single instrument and list
        if self._root.tag == "instruments":
            # Find matching instrument
            instrument_elem = None
            for inst in self._root.findall("instrument"):
                if inst.find("symbol").text == symbol:
                    instrument_elem = inst
                    break
            if not instrument_elem:
                raise ValueError(f"Symbol {symbol} not found in Bloomberg data")
        else:
            instrument_elem = self._root
            xml_symbol = instrument_elem.find("symbol").text
            if xml_symbol != symbol:
                raise ValueError(f"Symbol mismatch: expected {symbol}, got {xml_symbol}")

        timestamp_str = instrument_elem.find("timestamp").text
        timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))

        return MarketDataPoint(
            symbol=instrument_elem.find("symbol").text,
            price=float(instrument_elem.find("price").text),
            timestamp=timestamp,
            volume=None,
            metadata={"source": "bloomberg"}
        )
