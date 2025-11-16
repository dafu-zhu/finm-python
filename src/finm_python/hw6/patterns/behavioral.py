"""
Behavioral Design Patterns

- Strategy: Interchangeable trading strategies
- Observer: Event notification system for signals
- Command: Encapsulated order execution with undo/redo
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional

from ..models import MarketDataPoint


# ============================================================================
# Strategy Pattern
# ============================================================================

class Strategy(ABC):
    """
    Abstract base class for trading strategies.

    Each strategy generates trading signals based on market data.
    """

    @abstractmethod
    def generate_signals(self, tick: MarketDataPoint) -> list[dict]:
        """
        Generate trading signals based on new market data.

        Args:
            tick: New market data point.

        Returns:
            List of signal dictionaries with action and details.
        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset strategy state."""
        pass


class MeanReversionStrategy(Strategy):
    """
    Mean reversion trading strategy.

    Generates buy signals when price is significantly below moving average,
    and sell signals when price is significantly above.
    """

    def __init__(self, lookback_window: int = 20, threshold: float = 0.02):
        """
        Initialize mean reversion strategy.

        Args:
            lookback_window: Number of periods for moving average.
            threshold: Percentage deviation threshold for signals.
        """
        self.lookback_window = lookback_window
        self.threshold = threshold
        self.price_history: list[float] = []
        self.symbol: Optional[str] = None

    def generate_signals(self, tick: MarketDataPoint) -> list[dict]:
        """
        Generate signals based on mean reversion logic.

        Args:
            tick: New market data point.

        Returns:
            List of signals (empty if no action needed).
        """
        signals = []

        # Track symbol
        if self.symbol is None:
            self.symbol = tick.symbol
        elif self.symbol != tick.symbol:
            # New symbol, reset
            self.reset()
            self.symbol = tick.symbol

        # Add current price to history
        self.price_history.append(tick.price)

        # Need enough history for moving average
        if len(self.price_history) < self.lookback_window:
            return signals

        # Calculate moving average
        window = self.price_history[-self.lookback_window:]
        moving_avg = sum(window) / len(window)

        # Calculate deviation
        deviation = (tick.price - moving_avg) / moving_avg

        # Generate signals based on threshold
        if deviation < -self.threshold:
            signals.append({
                "type": "BUY",
                "symbol": tick.symbol,
                "price": tick.price,
                "timestamp": tick.timestamp,
                "reason": f"Price {deviation:.2%} below MA({self.lookback_window})",
                "strategy": "MeanReversion"
            })
        elif deviation > self.threshold:
            signals.append({
                "type": "SELL",
                "symbol": tick.symbol,
                "price": tick.price,
                "timestamp": tick.timestamp,
                "reason": f"Price {deviation:.2%} above MA({self.lookback_window})",
                "strategy": "MeanReversion"
            })

        # Keep history bounded
        if len(self.price_history) > self.lookback_window * 2:
            self.price_history = self.price_history[-self.lookback_window:]

        return signals

    def reset(self) -> None:
        """Reset strategy state."""
        self.price_history = []
        self.symbol = None


class BreakoutStrategy(Strategy):
    """
    Breakout trading strategy.

    Generates signals when price breaks above/below recent high/low levels.
    """

    def __init__(self, lookback_window: int = 15, threshold: float = 0.03):
        """
        Initialize breakout strategy.

        Args:
            lookback_window: Number of periods to establish range.
            threshold: Minimum breakout percentage.
        """
        self.lookback_window = lookback_window
        self.threshold = threshold
        self.price_history: list[float] = []
        self.symbol: Optional[str] = None

    def generate_signals(self, tick: MarketDataPoint) -> list[dict]:
        """
        Generate signals based on breakout logic.

        Args:
            tick: New market data point.

        Returns:
            List of signals (empty if no breakout detected).
        """
        signals = []

        # Track symbol
        if self.symbol is None:
            self.symbol = tick.symbol
        elif self.symbol != tick.symbol:
            self.reset()
            self.symbol = tick.symbol

        # Need history to establish range
        if len(self.price_history) >= self.lookback_window:
            window = self.price_history[-self.lookback_window:]
            high = max(window)
            low = min(window)

            # Check for breakout
            if tick.price > high * (1 + self.threshold):
                signals.append({
                    "type": "BUY",
                    "symbol": tick.symbol,
                    "price": tick.price,
                    "timestamp": tick.timestamp,
                    "reason": f"Breakout above {high:.2f} (threshold {self.threshold:.2%})",
                    "strategy": "Breakout"
                })
            elif tick.price < low * (1 - self.threshold):
                signals.append({
                    "type": "SELL",
                    "symbol": tick.symbol,
                    "price": tick.price,
                    "timestamp": tick.timestamp,
                    "reason": f"Breakdown below {low:.2f} (threshold {self.threshold:.2%})",
                    "strategy": "Breakout"
                })

        # Add to history after check
        self.price_history.append(tick.price)

        # Keep history bounded
        if len(self.price_history) > self.lookback_window * 2:
            self.price_history = self.price_history[-self.lookback_window:]

        return signals

    def reset(self) -> None:
        """Reset strategy state."""
        self.price_history = []
        self.symbol = None


# ============================================================================
# Observer Pattern
# ============================================================================

class Observer(ABC):
    """
    Abstract observer for receiving signal notifications.
    """

    @abstractmethod
    def update(self, signal: dict) -> None:
        """
        Handle signal notification.

        Args:
            signal: Signal dictionary with trade information.
        """
        pass


class LoggerObserver(Observer):
    """
    Observer that logs all signals.
    """

    def __init__(self, log_file: Optional[str] = None):
        """
        Initialize logger observer.

        Args:
            log_file: Optional file path for logging. If None, prints to stdout.
        """
        self.log_file = log_file
        self.logs: list[str] = []

    def update(self, signal: dict) -> None:
        """
        Log the signal.

        Args:
            signal: Signal dictionary.
        """
        timestamp = signal.get("timestamp", datetime.now())
        if isinstance(timestamp, datetime):
            timestamp = timestamp.isoformat()

        log_entry = (
            f"[{timestamp}] SIGNAL: {signal.get('type')} "
            f"{signal.get('symbol')} @ {signal.get('price'):.2f} - "
            f"{signal.get('reason', 'N/A')}"
        )

        self.logs.append(log_entry)

        if self.log_file:
            with open(self.log_file, "a") as f:
                f.write(log_entry + "\n")
        else:
            print(log_entry)


class AlertObserver(Observer):
    """
    Observer that alerts on large trades.
    """

    def __init__(self, price_threshold: float = 1000.0):
        """
        Initialize alert observer.

        Args:
            price_threshold: Price level that triggers alert.
        """
        self.price_threshold = price_threshold
        self.alerts: list[dict] = []

    def update(self, signal: dict) -> None:
        """
        Check signal and generate alert if necessary.

        Args:
            signal: Signal dictionary.
        """
        price = signal.get("price", 0)
        if price >= self.price_threshold:
            alert = {
                "timestamp": signal.get("timestamp", datetime.now()),
                "type": "HIGH_VALUE_TRADE",
                "signal": signal,
                "message": f"High value trade alert: {signal.get('type')} {signal.get('symbol')} @ {price:.2f}"
            }
            self.alerts.append(alert)
            print(f"ALERT: {alert['message']}")


class SignalPublisher:
    """
    Publisher that manages observer subscriptions and notifications.

    Implements the subject/observable part of the Observer pattern.
    """

    def __init__(self):
        """Initialize empty observer list."""
        self._observers: list[Observer] = []

    def attach(self, observer: Observer) -> None:
        """
        Attach an observer.

        Args:
            observer: Observer to add.
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        """
        Detach an observer.

        Args:
            observer: Observer to remove.
        """
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, signal: dict) -> None:
        """
        Notify all observers of a signal.

        Args:
            signal: Signal dictionary to broadcast.
        """
        for observer in self._observers:
            observer.update(signal)


# ============================================================================
# Command Pattern
# ============================================================================

class Command(ABC):
    """
    Abstract command for encapsulating operations.

    Supports execute and undo operations.
    """

    @abstractmethod
    def execute(self) -> Any:
        """Execute the command."""
        pass

    @abstractmethod
    def undo(self) -> Any:
        """Undo the command."""
        pass


class Order:
    """
    Simple order representation for command execution.
    """

    def __init__(self, order_id: str, symbol: str, order_type: str,
                 quantity: int, price: float):
        """
        Initialize order.

        Args:
            order_id: Unique order identifier.
            symbol: Instrument symbol.
            order_type: BUY or SELL.
            quantity: Number of units.
            price: Execution price.
        """
        self.order_id = order_id
        self.symbol = symbol
        self.order_type = order_type
        self.quantity = quantity
        self.price = price
        self.status = "PENDING"
        self.executed_at: Optional[datetime] = None

    def __repr__(self) -> str:
        return (f"Order({self.order_id}, {self.order_type} {self.quantity} "
                f"{self.symbol} @ {self.price}, status={self.status})")


class ExecuteOrderCommand(Command):
    """
    Command to execute a trade order.
    """

    def __init__(self, order: Order):
        """
        Initialize command with order.

        Args:
            order: Order to execute.
        """
        self.order = order
        self._previous_status: Optional[str] = None

    def execute(self) -> Order:
        """
        Execute the order.

        Returns:
            The executed order.
        """
        self._previous_status = self.order.status
        self.order.status = "EXECUTED"
        self.order.executed_at = datetime.now()
        print(f"Executed: {self.order}")
        return self.order

    def undo(self) -> Order:
        """
        Undo the order execution.

        Returns:
            The reverted order.
        """
        if self._previous_status:
            self.order.status = self._previous_status
            self.order.executed_at = None
            print(f"Undone: {self.order}")
        return self.order


class CancelOrderCommand(Command):
    """
    Command to cancel an order.
    """

    def __init__(self, order: Order):
        """
        Initialize command with order.

        Args:
            order: Order to cancel.
        """
        self.order = order
        self._previous_status: Optional[str] = None

    def execute(self) -> Order:
        """
        Cancel the order.

        Returns:
            The cancelled order.
        """
        self._previous_status = self.order.status
        self.order.status = "CANCELLED"
        print(f"Cancelled: {self.order}")
        return self.order

    def undo(self) -> Order:
        """
        Undo the cancellation.

        Returns:
            The restored order.
        """
        if self._previous_status:
            self.order.status = self._previous_status
            print(f"Restore cancelled: {self.order}")
        return self.order


class CommandInvoker:
    """
    Invoker that manages command execution history.

    Supports undo and redo operations.
    """

    def __init__(self):
        """Initialize empty command history."""
        self._history: list[Command] = []
        self._redo_stack: list[Command] = []

    def execute(self, command: Command) -> Any:
        """
        Execute a command and store in history.

        Args:
            command: Command to execute.

        Returns:
            Result of command execution.
        """
        result = command.execute()
        self._history.append(command)
        # Clear redo stack when new command is executed
        self._redo_stack.clear()
        return result

    def undo(self) -> Optional[Any]:
        """
        Undo the last command.

        Returns:
            Result of undo operation, or None if no history.
        """
        if not self._history:
            print("Nothing to undo")
            return None

        command = self._history.pop()
        result = command.undo()
        self._redo_stack.append(command)
        return result

    def redo(self) -> Optional[Any]:
        """
        Redo the last undone command.

        Returns:
            Result of redo operation, or None if no redo available.
        """
        if not self._redo_stack:
            print("Nothing to redo")
            return None

        command = self._redo_stack.pop()
        result = command.execute()
        self._history.append(command)
        return result

    def get_history(self) -> list[Command]:
        """Get command history."""
        return self._history.copy()

    def clear_history(self) -> None:
        """Clear command history and redo stack."""
        self._history.clear()
        self._redo_stack.clear()
