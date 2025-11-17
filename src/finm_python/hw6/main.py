#!/usr/bin/env python3
"""
Main orchestration module for HW6: Design Patterns in Financial Software.

This module demonstrates how to use the design patterns once implemented.

IMPORTANT: This code will not run until you implement the TODO sections
in the pattern modules. Each demo function shows how the patterns should
be used once completed.

Usage:
    python -m finm_python.hw6.main

Patterns demonstrated:
- Factory: Creating instruments
- Singleton: Configuration management
- Builder: Portfolio construction
- Decorator: Analytics enhancement
- Adapter: Data source integration
- Composite: Portfolio hierarchy
- Strategy: Trading signal generation
- Observer: Event notification
- Command: Order execution with undo/redo
"""

import json
from pathlib import Path
from datetime import datetime, timedelta

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
    LoggerObserver,
    AlertObserver,
    ExecuteOrderCommand,
    CommandInvoker,
    Order
)
from .data_loader import load_instruments_from_csv
from .analytics import calculate_returns


def get_data_path() -> Path:
    """Get the path to data files."""
    base_path = Path(__file__).parent.parent / "scripts" / "hw6"
    if base_path.exists():
        return base_path
    return Path(".")


def demo_factory_pattern():
    """
    Demonstrate Factory Pattern: Creating instruments from raw data.

    The Factory Pattern centralizes object creation logic, allowing
    you to create different instrument types based on input data.
    """
    print("\n" + "=" * 60)
    print("FACTORY PATTERN: Creating Instruments")
    print("=" * 60)

    # Example usage of Factory pattern
    sample_data = [
        {
            "symbol": "AAPL",
            "type": "Stock",
            "price": 172.35,
            "sector": "Technology",
            "issuer": "Apple Inc."
        },
        {
            "symbol": "US10Y",
            "type": "Bond",
            "price": 100.0,
            "issuer": "US Treasury",
            "maturity": "2035-10-01",
            "coupon": 0.045
        },
        {
            "symbol": "SPY",
            "type": "ETF",
            "price": 430.50,
            "sector": "Index",
            "issuer": "State Street",
            "expense_ratio": 0.0009
        }
    ]

    print("Creating instruments using Factory pattern:")
    for data in sample_data:
        # TODO: Once you implement InstrumentFactory.create_instrument(),
        # this will create the appropriate instrument type
        inst = InstrumentFactory.create_instrument(data)
        print(f"  Created: {inst}")
        print(f"  Metrics: {inst.get_metrics()}\n")


def demo_singleton_pattern():
    """
    Demonstrate Singleton Pattern: Centralized configuration.

    The Singleton Pattern ensures only one instance of Config exists,
    so all parts of the application share the same settings.
    """
    print("\n" + "=" * 60)
    print("SINGLETON PATTERN: Centralized Configuration")
    print("=" * 60)

    # Reset for demo
    Config.reset()

    # Get instance - should always return the same object
    config1 = Config.get_instance()
    config2 = Config.get_instance()

    print(f"config1 is config2: {config1 is config2}")

    # Set some configuration
    config1.set("log_level", "INFO")
    config1.set("default_strategy", "MeanReversionStrategy")

    # Access via different reference - should see same values
    print(f"Config via config1: {config1.get_all()}")
    print(f"Config via config2: {config2.get_all()}")
    print(f"Log level from config2: {config2.get('log_level')}")


def demo_builder_pattern():
    """
    Demonstrate Builder Pattern: Complex portfolio construction.

    The Builder Pattern allows step-by-step construction of complex
    objects with a fluent interface.
    """
    print("\n" + "=" * 60)
    print("BUILDER PATTERN: Portfolio Construction")
    print("=" * 60)

    # Build a portfolio with fluent interface
    portfolio = (PortfolioBuilder("Main Portfolio")
                 .set_owner("jdoe")
                 .add_position("AAPL", 100, 172.35)
                 .add_position("MSFT", 50, 328.10)
                 .add_subportfolio("ETF Holdings",
                                   PortfolioBuilder("ETFs")
                                   .add_position("SPY", 20, 430.50)
                                   .add_position("QQQ", 15, 380.25))
                 .build())

    print(f"Built: {portfolio}")
    print(f"Total Value: ${portfolio.get_value():,.2f}")
    print(f"All Positions: {portfolio.get_positions()}")


def demo_decorator_pattern():
    """
    Demonstrate Decorator Pattern: Adding analytics to instruments.

    Decorators add functionality without modifying the base class.
    You can stack multiple decorators to add multiple capabilities.
    """
    print("\n" + "=" * 60)
    print("DECORATOR PATTERN: Instrument Analytics")
    print("=" * 60)

    # Create base instrument
    stock = Stock("AAPL", 172.35, "Technology", "Apple Inc.")
    print(f"Base instrument: {stock}")
    print(f"Base metrics: {stock.get_metrics()}")

    # Sample data for analytics
    price_history = [170.0, 172.0, 168.0, 175.0, 173.0, 172.35]
    historical_returns = calculate_returns(price_history)
    market_returns = [0.005, -0.01, 0.02, -0.005, 0.003]

    # Stack decorators one by one
    print("\nStacking decorators:")

    decorated = VolatilityDecorator(stock, historical_returns)
    print(f"After VolatilityDecorator: {decorated.get_metrics()}")

    decorated = BetaDecorator(decorated, historical_returns, market_returns)
    print(f"After BetaDecorator: {decorated.get_metrics()}")

    decorated = DrawdownDecorator(decorated, price_history)
    print(f"After DrawdownDecorator: {decorated.get_metrics()}")

    print(f"\nFinal decorated type: {decorated.get_type()}")


def demo_adapter_pattern():
    """
    Demonstrate Adapter Pattern: External data integration.

    Adapters convert external data formats into our standardized
    MarketDataPoint format.
    """
    print("\n" + "=" * 60)
    print("ADAPTER PATTERN: External Data Integration")
    print("=" * 60)

    # Yahoo Finance JSON format
    yahoo_data = {
        "ticker": "AAPL",
        "last_price": 172.35,
        "timestamp": "2025-10-01T09:30:00Z",
        "volume": 1000000
    }

    yahoo_adapter = YahooFinanceAdapter(yahoo_data)
    market_point = yahoo_adapter.get_data("AAPL")
    print(f"Yahoo Finance Data: {market_point}")
    print(f"  Symbol: {market_point.symbol}")
    print(f"  Price: {market_point.price}")
    print(f"  Timestamp: {market_point.timestamp}")
    print(f"  Metadata: {market_point.metadata}")


def demo_composite_pattern():
    """
    Demonstrate Composite Pattern: Portfolio hierarchy.

    The Composite Pattern allows treating individual positions and
    groups of positions uniformly, enabling recursive calculations.
    """
    print("\n" + "=" * 60)
    print("COMPOSITE PATTERN: Portfolio Hierarchy")
    print("=" * 60)

    # Build hierarchical portfolio
    main_portfolio = PortfolioGroup("Main Portfolio")

    # Add individual positions (leaf nodes)
    main_portfolio.add(Position("AAPL", 100, 172.35))
    main_portfolio.add(Position("MSFT", 50, 328.10))

    # Add sub-portfolio (composite node)
    tech_subportfolio = PortfolioGroup("Tech Holdings")
    tech_subportfolio.add(Position("GOOGL", 25, 141.50))
    tech_subportfolio.add(Position("META", 30, 345.20))
    main_portfolio.add(tech_subportfolio)

    print(f"Portfolio: {main_portfolio}")
    print(f"Total Value (recursive): ${main_portfolio.get_value():,.2f}")
    print(f"All Positions (flattened): {main_portfolio.get_positions()}")


def demo_strategy_pattern():
    """
    Demonstrate Strategy Pattern: Interchangeable trading strategies.

    The Strategy Pattern allows swapping algorithms at runtime.
    Each strategy implements the same interface but different logic.
    """
    print("\n" + "=" * 60)
    print("STRATEGY PATTERN: Trading Strategies")
    print("=" * 60)

    # Create strategies with different parameters
    mean_rev = MeanReversionStrategy(lookback_window=5, threshold=0.02)
    breakout = BreakoutStrategy(lookback_window=5, threshold=0.03)

    # Sample market ticks
    ticks = [
        MarketDataPoint("AAPL", 100.0, datetime(2025, 10, 1, 9, 30)),
        MarketDataPoint("AAPL", 102.0, datetime(2025, 10, 1, 9, 31)),
        MarketDataPoint("AAPL", 98.0, datetime(2025, 10, 1, 9, 32)),
        MarketDataPoint("AAPL", 105.0, datetime(2025, 10, 1, 9, 33)),
        MarketDataPoint("AAPL", 95.0, datetime(2025, 10, 1, 9, 34)),
        MarketDataPoint("AAPL", 110.0, datetime(2025, 10, 1, 9, 35)),
    ]

    print("Mean Reversion Strategy signals:")
    for tick in ticks:
        signals = mean_rev.generate_signals(tick)
        if signals:
            print(f"  ${tick.price:.2f}: {signals[0]['type']} - {signals[0]['reason']}")

    print("\nBreakout Strategy signals:")
    breakout.reset()
    for tick in ticks:
        signals = breakout.generate_signals(tick)
        if signals:
            print(f"  ${tick.price:.2f}: {signals[0]['type']} - {signals[0]['reason']}")


def demo_observer_pattern():
    """
    Demonstrate Observer Pattern: Signal notifications.

    The Observer Pattern decouples signal generation from signal handling.
    Multiple observers can react to the same signals independently.
    """
    print("\n" + "=" * 60)
    print("OBSERVER PATTERN: Signal Notifications")
    print("=" * 60)

    # Create publisher (subject)
    publisher = SignalPublisher()

    # Create observers
    logger = LoggerObserver()
    alerter = AlertObserver(price_threshold=300.0)

    # Attach observers
    publisher.attach(logger)
    publisher.attach(alerter)

    print("Attached: LoggerObserver, AlertObserver (threshold=$300)")

    # Generate signals
    signals = [
        {
            "type": "BUY",
            "symbol": "AAPL",
            "price": 172.35,
            "timestamp": datetime.now(),
            "reason": "Below moving average"
        },
        {
            "type": "SELL",
            "symbol": "MSFT",
            "price": 328.10,
            "timestamp": datetime.now(),
            "reason": "Above moving average"
        },
    ]

    print("\nNotifying observers:")
    for signal in signals:
        publisher.notify(signal)

    print(f"\nLogger recorded {len(logger.logs)} signals")
    print(f"Alerter generated {len(alerter.alerts)} alerts")


def demo_command_pattern():
    """
    Demonstrate Command Pattern: Order execution with undo/redo.

    The Command Pattern encapsulates operations as objects,
    enabling undo/redo functionality.
    """
    print("\n" + "=" * 60)
    print("COMMAND PATTERN: Order Execution with Undo/Redo")
    print("=" * 60)

    # Create invoker (manages command history)
    invoker = CommandInvoker()

    # Create orders
    order1 = Order("ORD001", "AAPL", "BUY", 100, 172.35)
    order2 = Order("ORD002", "MSFT", "SELL", 50, 328.10)

    print(f"Initial orders:")
    print(f"  {order1}")
    print(f"  {order2}")

    # Execute orders through invoker
    print("\nExecuting orders:")
    invoker.execute(ExecuteOrderCommand(order1))
    invoker.execute(ExecuteOrderCommand(order2))

    # Undo last
    print("\nUndo last order:")
    invoker.undo()
    print(f"  Order2 status: {order2.status}")

    # Redo
    print("\nRedo undone order:")
    invoker.redo()
    print(f"  Order2 status: {order2.status}")

    print(f"\nCommand history size: {len(invoker.get_history())}")


def main():
    """
    Main entry point - run all pattern demonstrations.

    NOTE: This will raise NotImplementedError until you implement
    the TODO sections in each pattern module.
    """
    print("=" * 60)
    print("HW6: Design Patterns in Financial Software Architecture")
    print("=" * 60)
    print("\nNOTE: Complete the TODO implementations before running demos.")
    print("Each demo will fail with NotImplementedError until implemented.\n")

    try:
        # Uncomment demos as you implement them
        demo_factory_pattern()
        # demo_singleton_pattern()
        # demo_builder_pattern()
        # demo_decorator_pattern()
        # demo_adapter_pattern()
        # demo_composite_pattern()
        # demo_strategy_pattern()
        # demo_observer_pattern()
        # demo_command_pattern()

    except NotImplementedError as e:
        print(f"\n*** Implementation needed: {e} ***")
        print("Complete the TODO section and try again.")

    print("\n" + "=" * 60)
    print("Demo complete! Implement remaining patterns to see all features.")
    print("=" * 60)


if __name__ == "__main__":
    main()
