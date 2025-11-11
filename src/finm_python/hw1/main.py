from finm_python.hw1 import ExecutionEngine
from finm_python.hw1 import MACDStrategy, MomentumStrategy
from finm_python.hw1 import data_ingestor
from finm_python.hw1 import generate_report
from finm_python.hw1 import root_dir

from pathlib import Path

def main():
    # Configuration
    config = {
        'init_cash': 1_000_000,
        'strategies': [
            {
                'type': MACDStrategy,  # Direct class reference, not string!
                'params': {
                    'short_period': 12,
                    'long_period': 26
                }
            }, {
                'type': MomentumStrategy,
                'params': {
                    'lookback': 20,
                    'buy_threshold': 0.0,
                    'sell_threshold': -0.0
                }
            }
        ]
    }

    # Load data
    root = root_dir()
    csvfile = root / 'data' / 'raw' / 'market_data.csv'
    ticks = data_ingestor(csvfile)

    # Create strategy instances
    strategies = []
    for strat_config in config['strategies']:
        strat_object = strat_config['type']
        params = strat_config['params']
        strategy = strat_object(ticks=ticks, params=params)
        strategies.append(strategy)

    # Run execution engine
    init_cash = config['init_cash']
    engine = ExecutionEngine(ticks, strategies, init_cash)
    states = engine.run()
    names = list(states.keys())

    # Generate report
    img_dir = Path() / 'img'
    doc_dir = Path() / 'doc'
    generate_report(names, states, img_dir, doc_dir)

if __name__ == '__main__':
    main()