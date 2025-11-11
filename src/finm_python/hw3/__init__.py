__version__ = '0.1.0'
__author__ = 'Dafu'

from .src.models import MarketDataPoint, Strategy
from .src.strategies import (
    NaiveMovingAverageStrategy,
    WindowedMovingAverageStrategy,
    VectorizedMovingAverageStrategy,
    CachedMovingAverageStrategy,
    StreamingMovingAverageStrategy,
    HybridOptimizedStrategy
)
from .src.profiler import run_comprehensive_benchmark
from .src.reporting import generate_complexity_report, generate_plots


__all__ = [
    "MarketDataPoint",
    "Strategy",
    "NaiveMovingAverageStrategy",
    "WindowedMovingAverageStrategy",
    "VectorizedMovingAverageStrategy",
    "CachedMovingAverageStrategy",
    "StreamingMovingAverageStrategy",
    "HybridOptimizedStrategy",
    "generate_complexity_report",
    "generate_plots"
]