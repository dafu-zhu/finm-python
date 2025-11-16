"""
Core financial models and data structures.

Contains:
- Instrument base class and concrete implementations (Stock, Bond, ETF)
- MarketDataPoint for standardized market data
- Portfolio component hierarchy for Composite pattern
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


# ============================================================================
# Market Data
# ============================================================================

@dataclass
class MarketDataPoint:
    """Standardized market data point used throughout the system."""
    symbol: str
    price: float
    timestamp: datetime
    volume: Optional[int] = None
    metadata: dict = field(default_factory=dict)


# ============================================================================
# Instrument Base Class and Implementations
# ============================================================================

class Instrument(ABC):
    """Abstract base class for financial instruments."""

    def __init__(self, symbol: str, price: float):
        self.symbol = symbol
        self.price = price

    @abstractmethod
    def get_type(self) -> str:
        """Return the instrument type."""
        pass

    def get_metrics(self) -> dict:
        """
        Return metrics for this instrument.
        Base implementation returns basic info.
        Can be extended by decorators.
        """
        return {
            "symbol": self.symbol,
            "price": self.price,
            "type": self.get_type()
        }

    def __repr__(self) -> str:
        return f"{self.get_type()}({self.symbol}, price={self.price})"


class Stock(Instrument):
    """Stock instrument."""

    def __init__(self, symbol: str, price: float, sector: str = "", issuer: str = ""):
        super().__init__(symbol, price)
        self.sector = sector
        self.issuer = issuer

    def get_type(self) -> str:
        return "Stock"

    def get_metrics(self) -> dict:
        metrics = super().get_metrics()
        metrics["sector"] = self.sector
        metrics["issuer"] = self.issuer
        return metrics


class Bond(Instrument):
    """Bond instrument."""

    def __init__(self, symbol: str, price: float, issuer: str = "",
                 maturity: Optional[str] = None, coupon: float = 0.0):
        super().__init__(symbol, price)
        self.issuer = issuer
        self.maturity = maturity
        self.coupon = coupon

    def get_type(self) -> str:
        return "Bond"

    def get_metrics(self) -> dict:
        metrics = super().get_metrics()
        metrics["issuer"] = self.issuer
        metrics["maturity"] = self.maturity
        metrics["coupon"] = self.coupon
        return metrics


class ETF(Instrument):
    """Exchange-Traded Fund instrument."""

    def __init__(self, symbol: str, price: float, sector: str = "",
                 issuer: str = "", expense_ratio: float = 0.0):
        super().__init__(symbol, price)
        self.sector = sector
        self.issuer = issuer
        self.expense_ratio = expense_ratio

    def get_type(self) -> str:
        return "ETF"

    def get_metrics(self) -> dict:
        metrics = super().get_metrics()
        metrics["sector"] = self.sector
        metrics["issuer"] = self.issuer
        metrics["expense_ratio"] = self.expense_ratio
        return metrics


# ============================================================================
# Portfolio Components (Composite Pattern)
# ============================================================================

class PortfolioComponent(ABC):
    """Abstract component for Composite pattern."""

    @abstractmethod
    def get_value(self) -> float:
        """Calculate and return total value."""
        pass

    @abstractmethod
    def get_positions(self) -> list[dict]:
        """Return list of position information."""
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass


class Position(PortfolioComponent):
    """Leaf node: single position in the portfolio tree."""

    def __init__(self, symbol: str, quantity: int, price: float):
        self.symbol = symbol
        self.quantity = quantity
        self.price = price

    def get_value(self) -> float:
        """Return position value (quantity * price)."""
        return self.quantity * self.price

    def get_positions(self) -> list[dict]:
        """Return this position as a single-item list."""
        return [{
            "symbol": self.symbol,
            "quantity": self.quantity,
            "price": self.price,
            "value": self.get_value()
        }]

    def __repr__(self) -> str:
        return f"Position({self.symbol}, qty={self.quantity}, price={self.price})"


class PortfolioGroup(PortfolioComponent):
    """Composite node: group of positions and/or sub-portfolios."""

    def __init__(self, name: str):
        self.name = name
        self.components: list[PortfolioComponent] = []

    def add(self, component: PortfolioComponent) -> None:
        """Add a child component."""
        self.components.append(component)

    def remove(self, component: PortfolioComponent) -> None:
        """Remove a child component."""
        self.components.remove(component)

    def get_value(self) -> float:
        """Recursively calculate total value of all components."""
        return sum(component.get_value() for component in self.components)

    def get_positions(self) -> list[dict]:
        """Recursively collect all positions from child components."""
        positions = []
        for component in self.components:
            positions.extend(component.get_positions())
        return positions

    def __repr__(self) -> str:
        return f"PortfolioGroup({self.name}, components={len(self.components)})"


# ============================================================================
# Portfolio (with metadata)
# ============================================================================

@dataclass
class Portfolio:
    """
    Complete portfolio with ownership and metadata.
    Uses PortfolioGroup internally for composite structure.
    """
    name: str
    owner: str
    root: PortfolioGroup

    def get_value(self) -> float:
        """Get total portfolio value."""
        return self.root.get_value()

    def get_positions(self) -> list[dict]:
        """Get all positions in portfolio."""
        return self.root.get_positions()

    def __repr__(self) -> str:
        return f"Portfolio(name={self.name}, owner={self.owner}, value={self.get_value():.2f})"
