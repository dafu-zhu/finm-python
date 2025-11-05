from typing import List

from pyquant.hw1.data_loader import MarketDataPoint
from src.pyquant.hw1.strategies import Strategy, StrategyState


class BenchmarkStrategy(Strategy):
    def __init__(self, params: dict = None):
        self.params = params if params else {}

    def generate_signals(self, tick: MarketDataPoint) -> list:
        entry_day = self.params['entry_day']
        if tick.timestamp == entry_day:
            return ['Buy', tick.symbol, 100, tick.price]
        else:
            return ['Hold', tick.symbol, 100, tick.price]

    def __repr__(self):
        return "BenchmarkStrategy"