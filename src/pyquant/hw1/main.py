from src.pyquant.hw1.engine import ExecutionEngine
from src.pyquant.hw1.strategies import MACDStrategy, MomentumStrategy
from src.pyquant.hw1.data_loader import data_ingestor
from src.pyquant.utils import *
from src.pyquant.hw1.reporting import *

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
    names = states.keys()

    # Generate report
    for name in names:
        time, value = zip(*states[name].history)
        max_dd = calc_max_dd(time, value)
        report = {
            'name': name,
            'ttl_return': total_return(value),
            'prd_return': period_returns(time, value),
            'sharpe': calc_sharpe(value),
            'max_dd': max_dd
        }
        print(report['name'])
        print(report['ttl_return'])
        print(report['prd_return'].collect())
        print(report['sharpe'])
        print(report['max_dd']['max_drawdown'])
        print(report['max_dd']['peak'])
        print(report['max_dd']['bottom'])
        print(report['max_dd']['recover'])
        print(report['max_dd']['duration'])
        print(report['max_dd']['drawdown'].collect())

    # Now what?
    # 1. Load data
    # 2. Create strategy instances
    # 3. Run backtest
    # 4. Generate report

if __name__ == '__main__':
    main()