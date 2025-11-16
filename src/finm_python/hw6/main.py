#!/usr/bin/env python3
"""
Main orchestration module for HW6: Design Patterns in Financial Software.

This module demonstrates the integration of multiple design patterns:
- Factory: Creating instruments
- Singleton: Configuration management
- Builder: Portfolio construction
- Decorator: Analytics enhancement
- Adapter: Data source integration
- Composite: Portfolio hierarchy
- Strategy: Trading signal generation
- Observer: Event notification
- Command: Order execution with undo/redo

Usage:
    python -m finm_python.hw6.main
"""

import json
from pathlib import Path

# Import all pattern implementations
from .models import Stock, Bond, ETF, MarketDataPoint, Position, PortfolioGroup
from .patterns.creational import InstrumentFactory, Config, PortfolioBuilder
from .patterns.structural import (
    VolatilityDecorator,
    BetaDecorator,
    DrawdownDecorator,
    YahooFinanceAdapter,
    BloombergXMLAdapter
)
from .patterns.behavioral import (
    MeanReversionStrategy,
    BreakoutStrategy,
    SignalPublisher,
    ExecuteOrderCommand,
    CancelOrderCommand,
    CommandInvoker,
    Order
)
from .data_loader import load_instruments_from_csv, load_market_data_from_csv
from .engine import StrategyEngine
from .reporting import LoggerObserver, AlertObserver, StatisticsObserver, ReportGenerator
from .analytics import add_full_analytics, calculate_returns


def get_data_path() -> Path:
    """Get the path to data files."""
    # Check for scripts/hw6 directory
    base_path = Path(__file__).parent.parent.parent.parent / "scripts" / "hw6"
    if base_path.exists():
        return base_path
    # Fallback to current directory
    return Path(".")


def demo_factory_pattern():
    """Demonstrate Factory Pattern: Creating instruments from raw data."""
    print("\n" + "=" * 60)
    print("FACTORY PATTERN: Creating Instruments")
    print("=" * 60)

    data_path = get_data_path()
    instruments_file = data_path / "instruments.csv"

    if instruments_file.exists():
        instruments = load_instruments_from_csv(instruments_file)
        for inst in instruments:
            print(f"Created: {inst}")
            print(f"  Metrics: {inst.get_metrics()}")
    else:
        # Demo with hardcoded data
        factory = InstrumentFactory()
        sample_data = [
            {"symbol": "AAPL", "type": "Stock", "price": 172.35, "sector": "Technology", "issuer": "Apple Inc."},
            {"symbol": "US10Y", "type": "Bond", "price": 100.0, "issuer": "US Treasury", "maturity": "2035-10-01"},
            {"symbol": "SPY", "type": "ETF", "price": 430.50, "sector": "Index", "issuer": "State Street"}
        ]
        for data in sample_data:
            inst = factory.create_instrument(data)
            print(f"Created: {inst}")
            print(f"  Metrics: {inst.get_metrics()}")


def demo_singleton_pattern():
    """Demonstrate Singleton Pattern: Centralized configuration."""
    print("\n" + "=" * 60)
    print("SINGLETON PATTERN: Centralized Configuration")
    print("=" * 60)

    # Reset singleton for demo
    Config.reset()

    data_path = get_data_path()
    config_file = data_path / "config.json"

    config1 = Config.get_instance()
    config2 = Config.get_instance()

    print(f"config1 is config2: {config1 is config2}")

    if config_file.exists():
        config1.load(config_file)
    else:
        config1.set("log_level", "INFO")
        config1.set("data_path", "./data/")
        config1.set("default_strategy", "MeanReversionStrategy")

    print(f"Config via config1: {config1.get_all()}")
    print(f"Config via config2: {config2.get_all()}")
    print(f"Same instance confirmed: {config1.get_all() == config2.get_all()}")


def demo_builder_pattern():
    """Demonstrate Builder Pattern: Complex portfolio construction."""
    print("\n" + "=" * 60)
    print("BUILDER PATTERN: Portfolio Construction")
    print("=" * 60)

    data_path = get_data_path()
    portfolio_file = data_path / "portfolio_structure.json"

    if portfolio_file.exists():
        with open(portfolio_file, "r") as f:
            portfolio_data = json.load(f)
        builder = PortfolioBuilder.from_dict(portfolio_data)
    else:
        # Build manually
        builder = (PortfolioBuilder("Main Portfolio")
                   .set_owner("jdoe")
                   .add_position("AAPL", 100, 172.35)
                   .add_position("MSFT", 50, 328.10)
                   .add_subportfolio("ETF Holdings",
                                     PortfolioBuilder("ETFs")
                                     .add_position("SPY", 20, 430.50)))

    portfolio = builder.build()

    print(f"Built: {portfolio}")
    print(f"Positions: {portfolio.get_positions()}")
    print(f"Total Value: ${portfolio.get_value():,.2f}")

    # Generate portfolio report
    report = ReportGenerator.generate_portfolio_report(portfolio)
    print("\n" + report)


def demo_decorator_pattern():
    """Demonstrate Decorator Pattern: Adding analytics to instruments."""
    print("\n" + "=" * 60)
    print("DECORATOR PATTERN: Instrument Analytics")
    print("=" * 60)

    # Create base instrument
    stock = Stock("AAPL", 172.35, "Technology", "Apple Inc.")
    print(f"Base instrument: {stock}")
    print(f"Base metrics: {stock.get_metrics()}")

    # Sample data for calculations
    price_history = [170.0, 172.0, 168.0, 175.0, 173.0, 172.35]
    historical_returns = calculate_returns(price_history)
    market_returns = [0.005, -0.01, 0.02, -0.005, 0.003]  # Sample market returns

    # Stack decorators
    print("\nStacking decorators:")
    decorated = VolatilityDecorator(stock, historical_returns)
    print(f"After VolatilityDecorator: {decorated.get_metrics()}")

    decorated = BetaDecorator(decorated, historical_returns, market_returns)
    print(f"After BetaDecorator: {decorated.get_metrics()}")

    decorated = DrawdownDecorator(decorated, price_history)
    print(f"After DrawdownDecorator: {decorated.get_metrics()}")

    print(f"\nFinal decorated instrument type: {decorated.get_type()}")


def demo_adapter_pattern():
    """Demonstrate Adapter Pattern: External data integration."""
    print("\n" + "=" * 60)
    print("ADAPTER PATTERN: External Data Integration")
    print("=" * 60)

    data_path = get_data_path()
    yahoo_file = data_path / "external_data_yahoo.json"
    bloomberg_file = data_path / "external_data_bloomberg.xml"

    if yahoo_file.exists():
        yahoo_adapter = YahooFinanceAdapter(yahoo_file)
        yahoo_data = yahoo_adapter.get_data("AAPL")
        print(f"Yahoo Finance Data: {yahoo_data}")
    else:
        print("Yahoo data file not found, using sample data")
        yahoo_adapter = YahooFinanceAdapter({
            "ticker": "AAPL",
            "last_price": 172.35,
            "timestamp": "2025-10-01T09:30:00Z"
        })
        print(f"Yahoo Finance Data: {yahoo_adapter.get_data('AAPL')}")

    if bloomberg_file.exists():
        bloomberg_adapter = BloombergXMLAdapter(bloomberg_file)
        bloomberg_data = bloomberg_adapter.get_data("MSFT")
        print(f"Bloomberg XML Data: {bloomberg_data}")
    else:
        print("Bloomberg data file not found")


def demo_composite_pattern():
    """Demonstrate Composite Pattern: Portfolio hierarchy."""
    print("\n" + "=" * 60)
    print("COMPOSITE PATTERN: Portfolio Hierarchy")
    print("=" * 60)

    # Build a hierarchical portfolio
    main_portfolio = PortfolioGroup("Main Portfolio")

    # Add direct positions
    main_portfolio.add(Position("AAPL", 100, 172.35))
    main_portfolio.add(Position("MSFT", 50, 328.10))

    # Add a sub-portfolio
    tech_subportfolio = PortfolioGroup("Tech Holdings")
    tech_subportfolio.add(Position("GOOGL", 25, 141.50))
    tech_subportfolio.add(Position("META", 30, 345.20))

    main_portfolio.add(tech_subportfolio)

    # Add another sub-portfolio
    etf_subportfolio = PortfolioGroup("ETF Holdings")
    etf_subportfolio.add(Position("SPY", 20, 430.50))
    etf_subportfolio.add(Position("QQQ", 15, 380.25))

    main_portfolio.add(etf_subportfolio)

    print(f"Main Portfolio: {main_portfolio}")
    print(f"Total Value (recursive): ${main_portfolio.get_value():,.2f}")
    print(f"All Positions (flattened): {main_portfolio.get_positions()}")


def demo_strategy_pattern():
    """Demonstrate Strategy Pattern: Interchangeable trading strategies."""
    print("\n" + "=" * 60)
    print("STRATEGY PATTERN: Trading Strategies")
    print("=" * 60)

    data_path = get_data_path()
    strategy_params_file = data_path / "strategy_params.json"

    if strategy_params_file.exists():
        with open(strategy_params_file, "r") as f:
            params = json.load(f)
    else:
        params = {
            "MeanReversionStrategy": {"lookback_window": 20, "threshold": 0.02},
            "BreakoutStrategy": {"lookback_window": 15, "threshold": 0.03}
        }

    # Create strategies
    mean_rev = MeanReversionStrategy(**params["MeanReversionStrategy"])
    breakout = BreakoutStrategy(**params["BreakoutStrategy"])

    # Sample market data ticks
    from datetime import datetime
    ticks = [
        MarketDataPoint("AAPL", 170.0, datetime(2025, 10, 1, 9, 30)),
        MarketDataPoint("AAPL", 172.0, datetime(2025, 10, 1, 9, 31)),
        MarketDataPoint("AAPL", 168.0, datetime(2025, 10, 1, 9, 32)),
        MarketDataPoint("AAPL", 175.0, datetime(2025, 10, 1, 9, 33)),
        MarketDataPoint("AAPL", 180.0, datetime(2025, 10, 1, 9, 34)),  # Breakout
        MarketDataPoint("AAPL", 160.0, datetime(2025, 10, 1, 9, 35)),  # Mean reversion
    ]

    print("Testing Mean Reversion Strategy:")
    for tick in ticks:
        signals = mean_rev.generate_signals(tick)
        if signals:
            print(f"  Tick {tick.price}: {signals}")

    mean_rev.reset()
    breakout.reset()

    print("\nTesting Breakout Strategy:")
    for tick in ticks:
        signals = breakout.generate_signals(tick)
        if signals:
            print(f"  Tick {tick.price}: {signals}")


def demo_observer_pattern():
    """Demonstrate Observer Pattern: Signal notifications."""
    print("\n" + "=" * 60)
    print("OBSERVER PATTERN: Signal Notifications")
    print("=" * 60)

    # Create publisher and observers
    publisher = SignalPublisher()
    logger = LoggerObserver(verbose=False)
    stats = StatisticsObserver()
    alerter = AlertObserver(price_threshold=200.0)

    # Attach observers
    publisher.attach(logger)
    publisher.attach(stats)
    publisher.attach(alerter)

    print("Attached observers: LoggerObserver, StatisticsObserver, AlertObserver")

    # Generate sample signals
    from datetime import datetime
    signals = [
        {"type": "BUY", "symbol": "AAPL", "price": 172.35, "timestamp": datetime.now(), "reason": "Test signal 1", "strategy": "MeanReversion"},
        {"type": "SELL", "symbol": "MSFT", "price": 328.10, "timestamp": datetime.now(), "reason": "Test signal 2", "strategy": "Breakout"},
        {"type": "BUY", "symbol": "SPY", "price": 430.50, "timestamp": datetime.now(), "reason": "Test signal 3", "strategy": "MeanReversion"},
    ]

    print("\nNotifying observers:")
    for signal in signals:
        publisher.notify(signal)

    print(f"\nLogger recorded {len(logger.logs)} signals")
    for log in logger.logs:
        print(f"  {log}")

    print(f"\nAlerts generated: {len(alerter.alerts)}")
    for alert in alerter.alerts:
        print(f"  {alert['message']}")

    print(f"\nStatistics summary: {stats.get_summary()}")


def demo_command_pattern():
    """Demonstrate Command Pattern: Order execution with undo/redo."""
    print("\n" + "=" * 60)
    print("COMMAND PATTERN: Order Execution with Undo/Redo")
    print("=" * 60)

    # Create command invoker
    invoker = CommandInvoker()

    # Create orders
    order1 = Order("ORD001", "AAPL", "BUY", 100, 172.35)
    order2 = Order("ORD002", "MSFT", "SELL", 50, 328.10)

    print(f"Created orders:")
    print(f"  {order1}")
    print(f"  {order2}")

    # Execute orders
    print("\nExecuting orders:")
    cmd1 = ExecuteOrderCommand(order1)
    cmd2 = ExecuteOrderCommand(order2)

    invoker.execute(cmd1)
    invoker.execute(cmd2)

    print(f"\nOrder states after execution:")
    print(f"  {order1}")
    print(f"  {order2}")

    # Undo last order
    print("\nUndoing last order:")
    invoker.undo()
    print(f"  {order2}")

    # Redo
    print("\nRedoing undone order:")
    invoker.redo()
    print(f"  {order2}")

    # Show history
    print(f"\nCommand history: {len(invoker.get_history())} commands")


def demo_full_integration():
    """Demonstrate full system integration."""
    print("\n" + "=" * 60)
    print("FULL INTEGRATION: Strategy Engine Demo")
    print("=" * 60)

    # Create engine
    engine = StrategyEngine()

    # Register strategies
    engine.register_strategy("MeanReversion", MeanReversionStrategy(lookback_window=5, threshold=0.02))
    engine.register_strategy("Breakout", BreakoutStrategy(lookback_window=5, threshold=0.03))
    engine.set_active_strategy("MeanReversion")

    # Attach observers
    logger = LoggerObserver(verbose=False)
    stats = StatisticsObserver()
    engine.attach_observer(logger)
    engine.attach_observer(stats)

    print("Engine configured with MeanReversion strategy")
    print("Attached LoggerObserver and StatisticsObserver")

    # Process ticks
    from datetime import datetime, timedelta
    base_time = datetime(2025, 10, 1, 9, 30)
    prices = [100.0, 102.0, 98.0, 105.0, 95.0, 110.0, 85.0]  # Volatile prices

    print("\nProcessing market ticks:")
    for i, price in enumerate(prices):
        tick = MarketDataPoint("TEST", price, base_time + timedelta(minutes=i))
        signals = engine.process_tick(tick)
        if signals:
            print(f"  Tick {i + 1} (${price:.2f}): {len(signals)} signal(s) generated")

    # Report
    print(f"\nSignal History: {len(engine.get_signal_history())} total signals")
    print(f"Statistics: {stats.get_summary()}")

    # Generate report
    report = ReportGenerator.generate_signal_report(engine.get_signal_history())
    print(f"\nGenerated Signal Report:\n{report}")


def main():
    """Main entry point - run all pattern demonstrations."""
    print("=" * 60)
    print("HW6: Design Patterns in Financial Software Architecture")
    print("=" * 60)

    # Run all demonstrations
    demo_factory_pattern()
    demo_singleton_pattern()
    demo_builder_pattern()
    demo_decorator_pattern()
    demo_adapter_pattern()
    demo_composite_pattern()
    demo_strategy_pattern()
    demo_observer_pattern()
    demo_command_pattern()
    demo_full_integration()

    print("\n" + "=" * 60)
    print("All pattern demonstrations completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
