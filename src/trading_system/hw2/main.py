from pathlib import Path

from trading_system.hw2.benchmark_strategy import BenchmarkStrategy
from trading_system.hw2.engine import ExecutionEngine
from trading_system.hw2.position_sizer import FixedShareSizer
from trading_system.hw2.price_loader import PriceLoader
from trading_system.hw1.src.reporting import generate_report
from trading_system.hw2.strategies import MovingAverageStrategy, VolatilityBreakoutStrategy, MACDStrategy, RSIStrategy


def main():
    # Load data
    loader = PriceLoader()
    parquet_path = Path('../../..') / 'data' / 'raw' / 'sp500.parquet'
    loader.load_parquet(path=parquet_path)
    ticks = loader.get_ticks()
    symbols = loader.tickers

    # Configs
    bm_config = {'entry_day': loader.time_range[0]}
    ma_config = {'short_ma': 20, 'long_ma': 50}
    vb_config = {'lookback': 20}
    macd_config = {'fast_period': 12, 'slow_period': 26, 'signal_period': 9}
    rsi_config = {'period': 14, 'oversell_threshold': 30, 'overbuy_threshold': 70}

    # Configure strategy
    strategies = [
        (BenchmarkStrategy(bm_config), FixedShareSizer(100)),
        (MovingAverageStrategy(ma_config), FixedShareSizer(1)),
        (VolatilityBreakoutStrategy(vb_config), FixedShareSizer(1)),
        (MACDStrategy(macd_config), FixedShareSizer(1)),
        (RSIStrategy(rsi_config), FixedShareSizer(1)),
    ]

    # Run execution engine
    init_cash = 1_000_000
    engine = ExecutionEngine(ticks, strategies, symbols, init_cash)
    states = engine.run()
    names = list(states.keys())
    generate_report(names, states, Path('img'), Path('doc'), time_period='long')



if __name__ == '__main__':
    main()