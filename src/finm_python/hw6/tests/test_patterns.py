"""
Unit tests for HW6 Design Patterns.

These tests validate your pattern implementations. As you complete each TODO,
the corresponding tests should pass.

To run specific test classes:
    pytest -k TestFactoryPattern
    pytest -k TestSingletonPattern
    etc.

Tests cover:
- Factory pattern: Correct instrument type creation
- Singleton pattern: Shared config instance
- Builder pattern: Portfolio construction
- Decorator pattern: Analytics output
- Adapter pattern: Data format conversion
- Composite pattern: Recursive value calculation
- Strategy pattern: Signal generation
- Observer pattern: Notification dispatch
- Command pattern: Execute/undo logic
"""

import pytest
import json
import tempfile
from datetime import datetime
from pathlib import Path

# Import all components
from ..models import (
    Stock, Bond, ETF, MarketDataPoint,
    Position, PortfolioGroup, Portfolio
)
from ..patterns.creational import InstrumentFactory, Config, PortfolioBuilder
from ..patterns.structural import (
    VolatilityDecorator, BetaDecorator, DrawdownDecorator,
    YahooFinanceAdapter, BloombergXMLAdapter
)
from ..patterns.behavioral import (
    MeanReversionStrategy, BreakoutStrategy,
    SignalPublisher, LoggerObserver, AlertObserver,
    Order, ExecuteOrderCommand, CancelOrderCommand, CommandInvoker
)
from ..analytics import calculate_returns


# =============================================================================
# Factory Pattern Tests
# =============================================================================

class TestFactoryPattern:
    """Test InstrumentFactory creates correct instrument types."""

    def test_create_stock(self):
        """Factory creates Stock with correct attributes."""
        data = {
            "symbol": "AAPL",
            "type": "Stock",
            "price": 172.35,
            "sector": "Technology",
            "issuer": "Apple Inc."
        }
        instrument = InstrumentFactory.create_instrument(data)

        assert isinstance(instrument, Stock)
        assert instrument.symbol == "AAPL"
        assert instrument.price == 172.35
        assert instrument.sector == "Technology"
        assert instrument.issuer == "Apple Inc."
        assert instrument.get_type() == "Stock"

    def test_create_bond(self):
        """Factory creates Bond with correct attributes."""
        data = {
            "symbol": "US10Y",
            "type": "Bond",
            "price": 100.0,
            "issuer": "US Treasury",
            "maturity": "2035-10-01"
        }
        instrument = InstrumentFactory.create_instrument(data)

        assert isinstance(instrument, Bond)
        assert instrument.symbol == "US10Y"
        assert instrument.price == 100.0
        assert instrument.issuer == "US Treasury"
        assert instrument.maturity == "2035-10-01"
        assert instrument.get_type() == "Bond"

    def test_create_etf(self):
        """Factory creates ETF with correct attributes."""
        data = {
            "symbol": "SPY",
            "type": "ETF",
            "price": 430.50,
            "sector": "Index",
            "issuer": "State Street"
        }
        instrument = InstrumentFactory.create_instrument(data)

        assert isinstance(instrument, ETF)
        assert instrument.symbol == "SPY"
        assert instrument.price == 430.50
        assert instrument.get_type() == "ETF"

    def test_factory_unknown_type(self):
        """Factory raises error for unknown instrument type."""
        data = {"symbol": "XXX", "type": "Unknown", "price": 100.0}
        with pytest.raises(ValueError, match="Unknown instrument type: unknown"):
            InstrumentFactory.create_instrument(data)


# =============================================================================
# Singleton Pattern Tests
# =============================================================================

class TestSingletonPattern:
    """Test Config singleton behavior."""

    def setup_method(self):
        """Reset singleton before each test."""
        Config.reset()

    def test_singleton_same_instance(self):
        """Multiple calls return same instance."""
        config1 = Config.get_instance()
        config2 = Config.get_instance()
        config3 = Config()

        assert config1 is config2
        assert config2 is config3

    def test_shared_state(self):
        """All references share same state."""
        config1 = Config.get_instance()
        config2 = Config.get_instance()

        config1.set("test_key", "test_value")
        assert config2.get("test_key") == "test_value"

    def test_load_from_file(self):
        """Config loads from JSON file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"log_level": "DEBUG", "data_path": "./data/"}, f)
            f.flush()

            config = Config.get_instance()
            config.load(f.name)

            assert config.get("log_level") == "DEBUG"
            assert config.get("data_path") == "./data/"

        Path(f.name).unlink()

    def test_get_default_value(self):
        """Config.get returns default for missing keys."""
        config = Config.get_instance()
        assert config.get("nonexistent", "default") == "default"


# =============================================================================
# Builder Pattern Tests
# =============================================================================

class TestBuilderPattern:
    """Test PortfolioBuilder constructs portfolios correctly."""

    def test_build_simple_portfolio(self):
        """Builder creates portfolio with positions."""
        portfolio = (PortfolioBuilder("Test Portfolio")
                     .set_owner("testuser")
                     .add_position("AAPL", 100, 150.0)
                     .add_position("MSFT", 50, 300.0)
                     .build())

        assert portfolio.name == "Test Portfolio"
        assert portfolio.owner == "testuser"
        assert portfolio.get_value() == 100 * 150.0 + 50 * 300.0
        assert len(portfolio.get_positions()) == 2

    def test_build_nested_portfolio(self):
        """Builder creates portfolio with sub-portfolios."""
        portfolio = (PortfolioBuilder("Main")
                     .set_owner("user1")
                     .add_position("AAPL", 10, 100.0)
                     .add_subportfolio("Sub",
                                       PortfolioBuilder("SubPort")
                                       .add_position("MSFT", 5, 200.0))
                     .build())

        assert portfolio.get_value() == 10 * 100.0 + 5 * 200.0
        assert len(portfolio.get_positions()) == 2

    def test_fluent_interface(self):
        """Builder methods return self for chaining."""
        builder = PortfolioBuilder("Test")
        result = builder.set_owner("user")
        assert result is builder

        result = builder.add_position("A", 1, 100.0)
        assert result is builder

    def test_from_dict(self):
        """Builder creates portfolio from dictionary."""
        data = {
            "name": "JSON Portfolio",
            "owner": "jsonuser",
            "positions": [
                {"symbol": "A", "quantity": 10, "price": 50.0}
            ],
            "sub_portfolios": []
        }
        builder = PortfolioBuilder.from_dict(data)
        portfolio = builder.build()

        assert portfolio.name == "JSON Portfolio"
        assert portfolio.owner == "jsonuser"
        assert portfolio.get_value() == 500.0


# =============================================================================
# Decorator Pattern Tests
# =============================================================================

class TestDecoratorPattern:
    """Test analytics decorators add metrics."""

    def test_volatility_decorator(self):
        """VolatilityDecorator adds volatility metric."""
        stock = Stock("TEST", 100.0, "Tech", "Test Inc")
        returns = [0.01, -0.02, 0.015, -0.01, 0.025]
        decorated = VolatilityDecorator(stock, returns)

        metrics = decorated.get_metrics()
        assert "volatility" in metrics
        assert metrics["volatility"] > 0
        assert metrics["symbol"] == "TEST"

    def test_volatility_empty_returns(self):
        """VolatilityDecorator handles empty returns."""
        stock = Stock("TEST", 100.0, "Tech", "Test Inc")
        decorated = VolatilityDecorator(stock, [])
        assert decorated.calculate_volatility() == 0.0

    def test_beta_decorator(self):
        """BetaDecorator adds beta metric."""
        stock = Stock("TEST", 100.0, "Tech", "Test Inc")
        inst_returns = [0.02, -0.01, 0.03, -0.02, 0.01]
        mkt_returns = [0.01, -0.005, 0.015, -0.01, 0.005]
        decorated = BetaDecorator(stock, inst_returns, mkt_returns)

        metrics = decorated.get_metrics()
        assert "beta" in metrics
        assert isinstance(metrics["beta"], float)

    def test_beta_default_value(self):
        """BetaDecorator returns 1.0 for invalid inputs."""
        stock = Stock("TEST", 100.0, "Tech", "Test Inc")
        decorated = BetaDecorator(stock, [], [])
        assert decorated.calculate_beta() == 1.0

    def test_drawdown_decorator(self):
        """DrawdownDecorator adds max_drawdown metric."""
        stock = Stock("TEST", 100.0, "Tech", "Test Inc")
        prices = [100.0, 110.0, 105.0, 95.0, 100.0]
        decorated = DrawdownDecorator(stock, prices)

        metrics = decorated.get_metrics()
        assert "max_drawdown" in metrics
        assert metrics["max_drawdown"] < 0  # Drawdown is negative

    def test_stacked_decorators(self):
        """Multiple decorators can be stacked."""
        stock = Stock("TEST", 100.0, "Tech", "Test Inc")
        returns = [0.01, -0.02, 0.015]
        prices = [100.0, 102.0, 100.0]

        decorated = DrawdownDecorator(
            BetaDecorator(
                VolatilityDecorator(stock, returns),
                returns, returns
            ),
            prices
        )

        metrics = decorated.get_metrics()
        assert "volatility" in metrics
        assert "beta" in metrics
        assert "max_drawdown" in metrics
        assert decorated.get_type() == "Stock"


# =============================================================================
# Adapter Pattern Tests
# =============================================================================

class TestAdapterPattern:
    """Test data adapters convert formats correctly."""

    def test_yahoo_adapter_single(self):
        """YahooFinanceAdapter converts single JSON object."""
        data = {
            "ticker": "AAPL",
            "last_price": 172.35,
            "timestamp": "2025-10-01T09:30:00Z"
        }
        adapter = YahooFinanceAdapter(data)
        point = adapter.get_data("AAPL")

        assert isinstance(point, MarketDataPoint)
        assert point.symbol == "AAPL"
        assert point.price == 172.35
        assert point.metadata["source"] == "yahoo_finance"

    def test_yahoo_adapter_list(self):
        """YahooFinanceAdapter handles list of tickers."""
        data = [
            {"ticker": "AAPL", "last_price": 172.35, "timestamp": "2025-10-01T09:30:00Z"},
            {"ticker": "MSFT", "last_price": 328.10, "timestamp": "2025-10-01T09:30:00Z"}
        ]
        adapter = YahooFinanceAdapter(data)
        point = adapter.get_data("MSFT")

        assert point.symbol == "MSFT"
        assert point.price == 328.10

    def test_yahoo_adapter_symbol_mismatch(self):
        """YahooFinanceAdapter raises error on symbol mismatch."""
        data = {"ticker": "AAPL", "last_price": 172.35, "timestamp": "2025-10-01T09:30:00Z"}
        adapter = YahooFinanceAdapter(data)
        with pytest.raises(ValueError):
            adapter.get_data("MSFT")

    def test_bloomberg_adapter(self):
        """BloombergXMLAdapter converts XML to MarketDataPoint."""
        import xml.etree.ElementTree as ET
        xml_string = """
        <instrument>
            <symbol>MSFT</symbol>
            <price>328.10</price>
            <timestamp>2025-10-01T09:30:00Z</timestamp>
        </instrument>
        """
        root = ET.fromstring(xml_string)
        adapter = BloombergXMLAdapter(root)
        point = adapter.get_data("MSFT")

        assert isinstance(point, MarketDataPoint)
        assert point.symbol == "MSFT"
        assert point.price == 328.10
        assert point.metadata["source"] == "bloomberg"


# =============================================================================
# Composite Pattern Tests
# =============================================================================

class TestCompositePattern:
    """Test portfolio composite structure."""

    def test_position_value(self):
        """Position calculates correct value."""
        pos = Position("AAPL", 100, 150.0)
        assert pos.get_value() == 15000.0

    def test_position_get_positions(self):
        """Position returns itself as single-item list."""
        pos = Position("AAPL", 100, 150.0)
        positions = pos.get_positions()
        assert len(positions) == 1
        assert positions[0]["symbol"] == "AAPL"
        assert positions[0]["quantity"] == 100

    def test_portfolio_group_recursive_value(self):
        """PortfolioGroup calculates value recursively."""
        root = PortfolioGroup("Root")
        root.add(Position("A", 10, 100.0))  # 1000
        root.add(Position("B", 20, 50.0))   # 1000

        sub = PortfolioGroup("Sub")
        sub.add(Position("C", 5, 200.0))    # 1000
        root.add(sub)

        assert root.get_value() == 3000.0

    def test_get_positions_flattens(self):
        """get_positions returns all positions from hierarchy."""
        root = PortfolioGroup("Root")
        root.add(Position("A", 10, 100.0))

        sub = PortfolioGroup("Sub")
        sub.add(Position("B", 20, 50.0))
        root.add(sub)

        positions = root.get_positions()
        assert len(positions) == 2
        symbols = [p["symbol"] for p in positions]
        assert "A" in symbols
        assert "B" in symbols


# =============================================================================
# Strategy Pattern Tests
# =============================================================================

class TestStrategyPattern:
    """Test trading strategy signal generation."""

    def test_mean_reversion_buy_signal(self):
        """MeanReversionStrategy generates BUY on price below average."""
        strategy = MeanReversionStrategy(lookback_window=3, threshold=0.05)

        ticks = [
            MarketDataPoint("TEST", 100.0, datetime.now()),
            MarketDataPoint("TEST", 100.0, datetime.now()),
            MarketDataPoint("TEST", 100.0, datetime.now()),
            MarketDataPoint("TEST", 90.0, datetime.now()),  # 10% below avg
        ]

        signals = []
        for tick in ticks:
            signals.extend(strategy.generate_signals(tick))

        assert len(signals) == 1
        assert signals[0]["type"] == "BUY"
        assert signals[0]["symbol"] == "TEST"

    def test_mean_reversion_sell_signal(self):
        """MeanReversionStrategy generates SELL on price above average."""
        strategy = MeanReversionStrategy(lookback_window=3, threshold=0.05)

        ticks = [
            MarketDataPoint("TEST", 100.0, datetime.now()),
            MarketDataPoint("TEST", 100.0, datetime.now()),
            MarketDataPoint("TEST", 100.0, datetime.now()),
            MarketDataPoint("TEST", 110.0, datetime.now()),  # 10% above avg
        ]

        signals = []
        for tick in ticks:
            signals.extend(strategy.generate_signals(tick))

        assert len(signals) == 1
        assert signals[0]["type"] == "SELL"

    def test_breakout_strategy_buy(self):
        """BreakoutStrategy generates BUY on upward breakout."""
        strategy = BreakoutStrategy(lookback_window=3, threshold=0.05)

        ticks = [
            MarketDataPoint("TEST", 100.0, datetime.now()),
            MarketDataPoint("TEST", 102.0, datetime.now()),
            MarketDataPoint("TEST", 101.0, datetime.now()),
            MarketDataPoint("TEST", 110.0, datetime.now()),  # Breakout
        ]

        signals = []
        for tick in ticks:
            signals.extend(strategy.generate_signals(tick))

        assert len(signals) >= 1
        assert signals[0]["type"] == "BUY"

    def test_strategy_reset(self):
        """Strategy reset clears internal state."""
        strategy = MeanReversionStrategy()
        strategy.price_history = [100.0, 102.0]
        strategy.symbol = "TEST"
        strategy.reset()

        assert strategy.price_history == []
        assert strategy.symbol is None


# =============================================================================
# Observer Pattern Tests
# =============================================================================

class TestObserverPattern:
    """Test observer notifications."""

    def test_observer_receives_notification(self):
        """Observer receives signal notification."""
        publisher = SignalPublisher()
        logger = LoggerObserver()
        publisher.attach(logger)

        signal = {
            "type": "BUY",
            "symbol": "AAPL",
            "price": 172.35,
            "timestamp": datetime.now(),
            "reason": "test"
        }
        publisher.notify(signal)

        assert len(logger.logs) == 1
        assert "BUY" in logger.logs[0]
        assert "AAPL" in logger.logs[0]

    def test_multiple_observers(self):
        """Multiple observers all receive notification."""
        publisher = SignalPublisher()
        logger1 = LoggerObserver()
        logger2 = LoggerObserver()
        publisher.attach(logger1)
        publisher.attach(logger2)

        signal = {
            "type": "SELL",
            "symbol": "MSFT",
            "price": 328.10,
            "timestamp": datetime.now(),
            "reason": "test"
        }
        publisher.notify(signal)

        assert len(logger1.logs) == 1
        assert len(logger2.logs) == 1

    def test_alert_observer_threshold(self):
        """AlertObserver alerts on high-value trades."""
        alerter = AlertObserver(price_threshold=300.0)

        # Below threshold
        low_signal = {
            "type": "BUY",
            "symbol": "AAPL",
            "price": 172.35,
            "timestamp": datetime.now()
        }
        alerter.update(low_signal)
        assert len(alerter.alerts) == 0

        # Above threshold
        high_signal = {
            "type": "BUY",
            "symbol": "MSFT",
            "price": 328.10,
            "timestamp": datetime.now()
        }
        alerter.update(high_signal)
        assert len(alerter.alerts) == 1

    def test_detach_observer(self):
        """Detached observer stops receiving notifications."""
        publisher = SignalPublisher()
        logger = LoggerObserver()
        publisher.attach(logger)
        publisher.detach(logger)

        signal = {
            "type": "BUY",
            "symbol": "AAPL",
            "price": 172.35,
            "timestamp": datetime.now(),
            "reason": "test"
        }
        publisher.notify(signal)

        assert len(logger.logs) == 0


# =============================================================================
# Command Pattern Tests
# =============================================================================

class TestCommandPattern:
    """Test command execution and undo/redo."""

    def test_execute_order_command(self):
        """ExecuteOrderCommand changes order status."""
        order = Order("ORD001", "AAPL", "BUY", 100, 172.35)
        assert order.status == "PENDING"

        cmd = ExecuteOrderCommand(order)
        cmd.execute()

        assert order.status == "EXECUTED"
        assert order.executed_at is not None

    def test_undo_order_command(self):
        """ExecuteOrderCommand.undo reverts status."""
        order = Order("ORD001", "AAPL", "BUY", 100, 172.35)
        cmd = ExecuteOrderCommand(order)
        cmd.execute()
        cmd.undo()

        assert order.status == "PENDING"
        assert order.executed_at is None

    def test_command_invoker_history(self):
        """CommandInvoker maintains command history."""
        invoker = CommandInvoker()
        order = Order("ORD001", "AAPL", "BUY", 100, 172.35)
        cmd = ExecuteOrderCommand(order)

        invoker.execute(cmd)
        assert len(invoker.get_history()) == 1

    def test_invoker_undo_redo(self):
        """CommandInvoker supports undo and redo."""
        invoker = CommandInvoker()
        order = Order("ORD001", "AAPL", "BUY", 100, 172.35)
        cmd = ExecuteOrderCommand(order)

        invoker.execute(cmd)
        assert order.status == "EXECUTED"

        invoker.undo()
        assert order.status == "PENDING"

        invoker.redo()
        assert order.status == "EXECUTED"

    def test_cancel_order_command(self):
        """CancelOrderCommand cancels and restores orders."""
        order = Order("ORD001", "AAPL", "BUY", 100, 172.35)
        order.status = "EXECUTED"

        cmd = CancelOrderCommand(order)
        cmd.execute()
        assert order.status == "CANCELLED"

        cmd.undo()
        assert order.status == "EXECUTED"

    def test_invoker_clears_redo_on_new_command(self):
        """New command clears redo stack."""
        invoker = CommandInvoker()
        order1 = Order("ORD001", "AAPL", "BUY", 100, 172.35)
        order2 = Order("ORD002", "MSFT", "SELL", 50, 328.10)

        invoker.execute(ExecuteOrderCommand(order1))
        invoker.undo()
        invoker.execute(ExecuteOrderCommand(order2))

        # Redo should do nothing since stack was cleared
        result = invoker.redo()
        assert result is None


# =============================================================================
# Analytics Helper Tests
# =============================================================================

class TestAnalyticsHelpers:
    """Test analytics utility functions."""

    def test_calculate_returns(self):
        """calculate_returns computes correct simple returns."""
        prices = [100.0, 105.0, 102.0]
        returns = calculate_returns(prices)

        assert len(returns) == 2
        assert abs(returns[0] - 0.05) < 1e-10
        assert abs(returns[1] - (-3 / 105)) < 1e-10

    def test_calculate_returns_empty(self):
        """calculate_returns handles edge cases."""
        assert calculate_returns([]) == []
        assert calculate_returns([100.0]) == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
