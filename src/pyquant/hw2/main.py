from pathlib import Path

from pyquant.hw2.benchmark_strategy import BenchmarkStrategy
from pyquant.hw2.engine import ExecutionEngine
from pyquant.hw2.position_sizer import FixedShareSizer
from pyquant.hw2.price_loader import PriceLoader
from pyquant.hw1.reporting import generate_report


def main():
    # Load data
    loader = PriceLoader()
    parquet_path = Path('../../..') / 'data' / 'raw' / 'sp500.parquet'
    loader.load_parquet(path=parquet_path)
    ticks = loader.get_ticks()
    symbols = loader.tickers

    # Benchmark config
    bm_config = {'entry_day': loader.time_range[0]}

    # Configure strategy
    strategies = [
        (BenchmarkStrategy(bm_config), FixedShareSizer(100))
    ]

    # Run execution engine
    init_cash = 1_000_000
    engine = ExecutionEngine(ticks, strategies, symbols, init_cash)
    states = engine.run()
    names = list(states.keys())
    generate_report(names, states, Path('img'), Path('doc'), time_period='long')



if __name__ == '__main__':
    main()