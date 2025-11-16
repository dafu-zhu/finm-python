"""
Strategy execution engine.

Manages strategy lifecycle, signal generation, and event dispatch.
"""

import json
from pathlib import Path
from typing import Any, Optional

from .models import MarketDataPoint
from .patterns.behavioral import (
    Strategy,
    MeanReversionStrategy,
    BreakoutStrategy,
    SignalPublisher,
    Observer
)
from .patterns.creational import Config


class StrategyEngine:
    """
    Main engine for strategy execution and signal dispatch.

    Coordinates strategy selection, market data processing,
    and signal notification.
    """

    def __init__(self):
        """Initialize the engine."""
        self._strategies: dict[str, Strategy] = {}
        self._active_strategy: Optional[Strategy] = None
        self._publisher = SignalPublisher()
        self._signal_history: list[dict] = []

    def register_strategy(self, name: str, strategy: Strategy) -> None:
        """
        Register a strategy with the engine.

        Args:
            name: Strategy name/identifier.
            strategy: Strategy instance.
        """
        self._strategies[name] = strategy

    def set_active_strategy(self, name: str) -> None:
        """
        Set the active strategy for signal generation.

        Args:
            name: Name of registered strategy.

        Raises:
            KeyError: If strategy not registered.
        """
        if name not in self._strategies:
            raise KeyError(f"Strategy '{name}' not registered")
        self._active_strategy = self._strategies[name]

    def get_active_strategy(self) -> Optional[Strategy]:
        """Get the currently active strategy."""
        return self._active_strategy

    def attach_observer(self, observer: Observer) -> None:
        """
        Attach an observer for signal notifications.

        Args:
            observer: Observer to attach.
        """
        self._publisher.attach(observer)

    def detach_observer(self, observer: Observer) -> None:
        """
        Detach an observer.

        Args:
            observer: Observer to detach.
        """
        self._publisher.detach(observer)

    def process_tick(self, tick: MarketDataPoint) -> list[dict]:
        """
        Process a market data tick through active strategy.

        Args:
            tick: Market data point.

        Returns:
            List of generated signals.

        Raises:
            ValueError: If no active strategy set.
        """
        if self._active_strategy is None:
            raise ValueError("No active strategy set")

        # Generate signals
        signals = self._active_strategy.generate_signals(tick)

        # Store and notify
        for signal in signals:
            self._signal_history.append(signal)
            self._publisher.notify(signal)

        return signals

    def get_signal_history(self) -> list[dict]:
        """Get all generated signals."""
        return self._signal_history.copy()

    def clear_signal_history(self) -> None:
        """Clear signal history."""
        self._signal_history.clear()

    def reset(self) -> None:
        """Reset engine state including active strategy."""
        if self._active_strategy:
            self._active_strategy.reset()
        self.clear_signal_history()

    @classmethod
    def from_config(cls, config_path: str | Path,
                    strategy_params_path: str | Path) -> "StrategyEngine":
        """
        Create engine from configuration files.

        Args:
            config_path: Path to main config JSON.
            strategy_params_path: Path to strategy parameters JSON.

        Returns:
            Configured StrategyEngine instance.
        """
        # Load configuration
        config = Config.get_instance()
        config.load(config_path)

        # Load strategy parameters
        with open(strategy_params_path, "r") as f:
            strategy_params = json.load(f)

        # Create engine
        engine = cls()

        # Register strategies with parameters
        if "MeanReversionStrategy" in strategy_params:
            params = strategy_params["MeanReversionStrategy"]
            engine.register_strategy(
                "MeanReversionStrategy",
                MeanReversionStrategy(
                    lookback_window=params.get("lookback_window", 20),
                    threshold=params.get("threshold", 0.02)
                )
            )

        if "BreakoutStrategy" in strategy_params:
            params = strategy_params["BreakoutStrategy"]
            engine.register_strategy(
                "BreakoutStrategy",
                BreakoutStrategy(
                    lookback_window=params.get("lookback_window", 15),
                    threshold=params.get("threshold", 0.03)
                )
            )

        # Set default strategy from config
        default_strategy = config.get("default_strategy")
        if default_strategy and default_strategy in engine._strategies:
            engine.set_active_strategy(default_strategy)

        return engine


def create_strategy(name: str, params: dict) -> Strategy:
    """
    Factory function for creating strategy instances.

    Args:
        name: Strategy type name.
        params: Strategy parameters.

    Returns:
        Strategy instance.

    Raises:
        ValueError: If strategy type unknown.
    """
    if name == "MeanReversionStrategy":
        return MeanReversionStrategy(
            lookback_window=params.get("lookback_window", 20),
            threshold=params.get("threshold", 0.02)
        )
    elif name == "BreakoutStrategy":
        return BreakoutStrategy(
            lookback_window=params.get("lookback_window", 15),
            threshold=params.get("threshold", 0.03)
        )
    else:
        raise ValueError(f"Unknown strategy type: {name}")
