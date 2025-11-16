"""
Data loading module using Adapter pattern.

Provides unified interface for loading data from various sources:
- CSV files
- JSON files (Yahoo Finance format)
- XML files (Bloomberg format)
"""

import csv
from pathlib import Path
from typing import Iterator

from .models import Instrument, MarketDataPoint
from .patterns.creational import InstrumentFactory
from .patterns.structural import YahooFinanceAdapter, BloombergXMLAdapter


def load_instruments_from_csv(filepath: str | Path) -> list[Instrument]:
    """
    Load instruments from CSV file using Factory pattern.

    Args:
        filepath: Path to CSV file with instrument data.

    Returns:
        List of Instrument instances.
    """
    instruments = []
    factory = InstrumentFactory()

    with open(filepath, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            instrument = factory.create_instrument(row)
            instruments.append(instrument)

    return instruments


def load_market_data_from_csv(filepath: str | Path) -> Iterator[MarketDataPoint]:
    """
    Load market data from CSV file.

    Yields MarketDataPoint objects for each row.

    Args:
        filepath: Path to CSV file with OHLCV data.

    Yields:
        MarketDataPoint instances.
    """
    from datetime import datetime

    with open(filepath, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Assume CSV has: symbol, timestamp, open, high, low, close, volume
            timestamp_str = row.get("timestamp", row.get("date", ""))
            if timestamp_str:
                # Try different timestamp formats
                try:
                    timestamp = datetime.fromisoformat(timestamp_str)
                except ValueError:
                    try:
                        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d")
                    except ValueError:
                        timestamp = datetime.now()
            else:
                timestamp = datetime.now()

            yield MarketDataPoint(
                symbol=row.get("symbol", row.get("ticker", "")),
                price=float(row.get("close", row.get("price", 0))),
                timestamp=timestamp,
                volume=int(row.get("volume", 0)) if row.get("volume") else None,
                metadata={
                    "open": float(row.get("open", 0)) if row.get("open") else None,
                    "high": float(row.get("high", 0)) if row.get("high") else None,
                    "low": float(row.get("low", 0)) if row.get("low") else None,
                }
            )


def load_yahoo_data(filepath: str | Path, symbol: str) -> MarketDataPoint:
    """
    Load market data from Yahoo Finance JSON format.

    Args:
        filepath: Path to JSON file.
        symbol: Symbol to load.

    Returns:
        MarketDataPoint instance.
    """
    adapter = YahooFinanceAdapter(filepath)
    return adapter.get_data(symbol)


def load_bloomberg_data(filepath: str | Path, symbol: str) -> MarketDataPoint:
    """
    Load market data from Bloomberg XML format.

    Args:
        filepath: Path to XML file.
        symbol: Symbol to load.

    Returns:
        MarketDataPoint instance.
    """
    adapter = BloombergXMLAdapter(filepath)
    return adapter.get_data(symbol)


class DataLoader:
    """
    Unified data loader that manages multiple data sources.
    """

    def __init__(self):
        """Initialize data loader."""
        self._instruments: dict[str, Instrument] = {}
        self._adapters: dict[str, any] = {}

    def load_instruments(self, filepath: str | Path) -> None:
        """
        Load instruments from CSV and cache them.

        Args:
            filepath: Path to instruments CSV.
        """
        instruments = load_instruments_from_csv(filepath)
        for inst in instruments:
            self._instruments[inst.symbol] = inst

    def get_instrument(self, symbol: str) -> Instrument | None:
        """
        Get cached instrument by symbol.

        Args:
            symbol: Instrument symbol.

        Returns:
            Instrument instance or None.
        """
        return self._instruments.get(symbol)

    def get_all_instruments(self) -> list[Instrument]:
        """Get all cached instruments."""
        return list(self._instruments.values())

    def register_adapter(self, name: str, adapter: any) -> None:
        """
        Register a data adapter.

        Args:
            name: Adapter name.
            adapter: Adapter instance.
        """
        self._adapters[name] = adapter

    def get_data(self, adapter_name: str, symbol: str) -> MarketDataPoint:
        """
        Get data from named adapter.

        Args:
            adapter_name: Name of registered adapter.
            symbol: Symbol to fetch.

        Returns:
            MarketDataPoint instance.

        Raises:
            KeyError: If adapter not registered.
        """
        if adapter_name not in self._adapters:
            raise KeyError(f"Adapter '{adapter_name}' not registered")
        return self._adapters[adapter_name].get_data(symbol)
