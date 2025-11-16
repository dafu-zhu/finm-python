"""
Creational Design Patterns

- Factory: Create instrument instances from raw data
- Singleton: Centralized configuration management
- Builder: Construct complex portfolio structures
"""

import json
from pathlib import Path
from typing import Any, Optional

from ..models import (
    Instrument, Stock, Bond, ETF,
    Portfolio, PortfolioGroup, Position
)


# ============================================================================
# Factory Pattern
# ============================================================================

class InstrumentFactory:
    """
    Factory for creating Instrument instances from raw data.

    Usage:
        factory = InstrumentFactory()
        stock = factory.create_instrument({
            "symbol": "AAPL",
            "type": "Stock",
            "price": 172.35,
            "sector": "Technology"
        })
    """

    @staticmethod
    def create_instrument(data: dict) -> Instrument:
        """
        Create an instrument instance based on the type field in data.

        Args:
            data: Dictionary containing instrument attributes.
                  Must include 'symbol', 'type', and 'price'.

        Returns:
            Appropriate Instrument subclass instance.

        Raises:
            ValueError: If instrument type is unknown.
        """
        instrument_type = data.get("type", "").lower()
        symbol = data["symbol"]
        price = float(data["price"])

        if instrument_type == "stock":
            return Stock(
                symbol=symbol,
                price=price,
                sector=data.get("sector", ""),
                issuer=data.get("issuer", "")
            )
        elif instrument_type == "bond":
            return Bond(
                symbol=symbol,
                price=price,
                issuer=data.get("issuer", ""),
                maturity=data.get("maturity"),
                coupon=float(data.get("coupon", 0.0))
            )
        elif instrument_type == "etf":
            return ETF(
                symbol=symbol,
                price=price,
                sector=data.get("sector", ""),
                issuer=data.get("issuer", ""),
                expense_ratio=float(data.get("expense_ratio", 0.0))
            )
        else:
            raise ValueError(f"Unknown instrument type: {instrument_type}")


# ============================================================================
# Singleton Pattern
# ============================================================================

class Config:
    """
    Singleton configuration manager.

    Ensures all modules access the same configuration instance.

    Usage:
        config = Config.get_instance()
        config.load("config.json")
        log_level = config.get("log_level")
    """

    _instance: Optional["Config"] = None
    _initialized: bool = False

    def __new__(cls) -> "Config":
        """Ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize configuration data (only once)."""
        if not Config._initialized:
            self._data: dict = {}
            Config._initialized = True

    @classmethod
    def get_instance(cls) -> "Config":
        """Get the singleton instance."""
        return cls()

    def load(self, filepath: str | Path) -> None:
        """
        Load configuration from JSON file.

        Args:
            filepath: Path to JSON configuration file.
        """
        with open(filepath, "r") as f:
            self._data = json.load(f)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.

        Args:
            key: Configuration key.
            default: Default value if key not found.

        Returns:
            Configuration value or default.
        """
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.

        Args:
            key: Configuration key.
            value: Value to set.
        """
        self._data[key] = value

    def get_all(self) -> dict:
        """Get all configuration data."""
        return self._data.copy()

    @classmethod
    def reset(cls) -> None:
        """Reset singleton (mainly for testing)."""
        cls._instance = None
        cls._initialized = False


# ============================================================================
# Builder Pattern
# ============================================================================

class PortfolioBuilder:
    """
    Builder for constructing complex Portfolio objects.

    Supports fluent interface for adding positions and sub-portfolios.

    Usage:
        portfolio = (PortfolioBuilder("Main Portfolio")
                    .set_owner("jdoe")
                    .add_position("AAPL", 100, 172.35)
                    .add_position("MSFT", 50, 328.10)
                    .add_subportfolio("ETF Holdings",
                        PortfolioBuilder("ETFs")
                        .add_position("SPY", 20, 430.50))
                    .build())
    """

    def __init__(self, name: str):
        """
        Initialize builder with portfolio name.

        Args:
            name: Name of the portfolio.
        """
        self.name = name
        self.owner: str = ""
        self.root = PortfolioGroup(name)

    def set_owner(self, name: str) -> "PortfolioBuilder":
        """
        Set portfolio owner.

        Args:
            name: Owner name.

        Returns:
            Self for method chaining.
        """
        self.owner = name
        return self

    def add_position(self, symbol: str, quantity: int, price: float) -> "PortfolioBuilder":
        """
        Add a position to the portfolio.

        Args:
            symbol: Instrument symbol.
            quantity: Number of units.
            price: Price per unit.

        Returns:
            Self for method chaining.
        """
        position = Position(symbol, quantity, price)
        self.root.add(position)
        return self

    def add_subportfolio(self, name: str, builder: "PortfolioBuilder") -> "PortfolioBuilder":
        """
        Add a sub-portfolio.

        Args:
            name: Name of sub-portfolio.
            builder: PortfolioBuilder for the sub-portfolio.

        Returns:
            Self for method chaining.
        """
        # Create a PortfolioGroup from the builder
        subgroup = PortfolioGroup(name)
        # Transfer all components from the builder's root
        for component in builder.root.components:
            subgroup.add(component)
        self.root.add(subgroup)
        return self

    def build(self) -> Portfolio:
        """
        Construct the final Portfolio object.

        Returns:
            Completed Portfolio instance.
        """
        return Portfolio(
            name=self.name,
            owner=self.owner,
            root=self.root
        )

    @staticmethod
    def from_dict(data: dict) -> "PortfolioBuilder":
        """
        Create a PortfolioBuilder from dictionary structure.

        Args:
            data: Dictionary with portfolio structure (from JSON).

        Returns:
            Configured PortfolioBuilder.
        """
        builder = PortfolioBuilder(data.get("name", "Portfolio"))
        builder.set_owner(data.get("owner", ""))

        # Add positions
        for pos_data in data.get("positions", []):
            builder.add_position(
                pos_data["symbol"],
                pos_data["quantity"],
                pos_data["price"]
            )

        # Add sub-portfolios recursively
        for sub_data in data.get("sub_portfolios", []):
            sub_builder = PortfolioBuilder.from_dict(sub_data)
            builder.add_subportfolio(sub_data["name"], sub_builder)

        return builder
