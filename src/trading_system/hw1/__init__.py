__version__ = "0.1.0"
__author__ = "Dafu"

from .src.utils import root_dir
from .src.data_loader import MarketDataPoint, data_ingestor
from .src.models import Order, OrderError, ConfigError, Portfolio
from .src.strategies import (
    StrategyState,
    MACDStrategy,
    MomentumStrategy,
)
from .src.engine import ExecutionEngine
from .src.reporting import generate_report

__all__ = [
    "root_dir",
    "MarketDataPoint",
    "data_ingestor",
    "Order",
    "OrderError",
    "ConfigError",
    "Portfolio",
    "StrategyState",
    "MACDStrategy",
    "MomentumStrategy",
    "ExecutionEngine",
    "generate_report"
]