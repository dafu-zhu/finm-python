from finm_python.hw1.src.data_loader import MarketDataPoint
from finm_python.hw1.src.strategies import Strategy


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