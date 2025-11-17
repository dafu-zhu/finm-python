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
        # TODO: Implement factory logic
        # 1. Extract instrument_type from data (convert to lowercase)
        # 2. Extract symbol and price from data
        # 3. Based on instrument_type, create and return appropriate instance:
        #    - "stock": return Stock with symbol, price, sector, issuer
        #    - "bond": return Bond with symbol, price, issuer, maturity, coupon
        #    - "etf": return ETF with symbol, price, sector, issuer, expense_ratio
        # 4. Raise ValueError for unknown types
        raise NotImplementedError("TODO: Implement create_instrument")


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
        # TODO: Implement singleton pattern
        # Check if _instance is None, if so create new instance using super().__new__(cls)
        # Return the singleton instance
        raise NotImplementedError("TODO: Implement __new__ for Singleton")

    def __init__(self):
        """Initialize configuration data (only once)."""
        # TODO: Initialize _data dict only if not already initialized
        # Use Config._initialized flag to track this
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
        # TODO: Load JSON file and store in self._data
        raise NotImplementedError("TODO: Implement load")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.

        Args:
            key: Configuration key.
            default: Default value if key not found.

        Returns:
            Configuration value or default.
        """
        # TODO: Return value from _data dict, or default if not found
        raise NotImplementedError("TODO: Implement get")

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.

        Args:
            key: Configuration key.
            value: Value to set.
        """
        # TODO: Set key-value in _data dict
        raise NotImplementedError("TODO: Implement set")

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
        # TODO: Set owner and return self for chaining
        raise NotImplementedError("TODO: Implement set_owner")

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
        # TODO: Create Position and add to root, return self
        raise NotImplementedError("TODO: Implement add_position")

    def add_subportfolio(self, name: str, builder: "PortfolioBuilder") -> "PortfolioBuilder":
        """
        Add a sub-portfolio.

        Args:
            name: Name of sub-portfolio.
            builder: PortfolioBuilder for the sub-portfolio.

        Returns:
            Self for method chaining.
        """
        # TODO: Create PortfolioGroup from builder and add to root
        # Hint: Create new PortfolioGroup with name, transfer components from builder.root
        raise NotImplementedError("TODO: Implement add_subportfolio")

    def build(self) -> Portfolio:
        """
        Construct the final Portfolio object.

        Returns:
            Completed Portfolio instance.
        """
        # TODO: Return Portfolio with name, owner, and root
        raise NotImplementedError("TODO: Implement build")

    @staticmethod
    def from_dict(data: dict) -> "PortfolioBuilder":
        """
        Create a PortfolioBuilder from dictionary structure.

        Args:
            data: Dictionary with portfolio structure (from JSON).

        Returns:
            Configured PortfolioBuilder.
        """
        # TODO: Recursively build portfolio from dictionary
        # 1. Create builder with name from data
        # 2. Set owner from data
        # 3. Add positions from data["positions"] list
        # 4. Recursively add sub-portfolios from data["sub_portfolios"]
        raise NotImplementedError("TODO: Implement from_dict")
