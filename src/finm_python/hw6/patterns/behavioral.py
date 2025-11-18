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
        # TODO: Implement mean reversion signal generation
        # 1. Track symbol - if new symbol, reset state
        # 2. Add current price to price_history
        # 3. Return empty list if not enough history (< lookback_window)
        # 4. Calculate moving average of last lookback_window prices
        # 5. Calculate deviation: (current_price - ma) / ma
        # 6. Generate signals:
        #    - If deviation < -threshold: BUY signal
        #    - If deviation > threshold: SELL signal
        # 7. Keep history bounded (max 2 * lookback_window)
        # 8. Return list of signal dicts with keys:
        #    type, symbol, price, timestamp, reason, strategy
        raise NotImplementedError("TODO: Implement generate_signals for MeanReversionStrategy")

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
        # TODO: Implement breakout signal generation
        # 1. Track symbol - if new symbol, reset state
        # 2. If enough history (>= lookback_window):
        #    a. Find high and low of last lookback_window prices
        #    b. Check for breakout:
        #       - If price > high * (1 + threshold): BUY signal
        #       - If price < low * (1 - threshold): SELL signal
        # 3. Add current price to history AFTER checking for breakout
        # 4. Keep history bounded
        # 5. Return list of signal dicts
        raise NotImplementedError("TODO: Implement generate_signals for BreakoutStrategy")

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
        # TODO: Implement signal logging
        # 1. Extract timestamp from signal (default to datetime.now())
        # 2. Format log entry string with timestamp, signal type, symbol, price, reason
        # 3. Append to self.logs
        # 4. If log_file is set, write to file; otherwise print to stdout
        raise NotImplementedError("TODO: Implement LoggerObserver.update")


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
        # Extract price from signal
        price = signal.get('price', 0.0)

        # Check if price meets threshold
        if price >= self.price_threshold:
            # Create alert dict
            alert = {
                'timestamp': signal.get('timestamp', datetime.now()),
                'type': 'ALERT',
                'signal': signal,
                'message': f"High-value trade alert: {signal.get('type', 'TRADE')} "
                          f"{signal.get('symbol', 'N/A')} @ ${price:.2f}"
            }

            # Append to alerts list
            self.alerts.append(alert)

            # Print alert message
            print(alert['message'])


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
        # Add observer to list if not already present
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        """
        Detach an observer.

        Args:
            observer: Observer to remove.
        """
        # Remove observer from list if present
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, signal: dict) -> None:
        """
        Notify all observers of a signal.

        Args:
            signal: Signal dictionary to broadcast.
        """
        # Call update() on each observer
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
        # TODO: Implement order execution
        # 1. Save current status to _previous_status
        # 2. Set order.status to "EXECUTED"
        # 3. Set order.executed_at to current datetime
        # 4. Print execution message
        # 5. Return the order
        raise NotImplementedError("TODO: Implement ExecuteOrderCommand.execute")

    def undo(self) -> Order:
        """
        Undo the order execution.

        Returns:
            The reverted order.
        """
        # TODO: Implement undo
        # 1. If _previous_status exists, restore it
        # 2. Clear executed_at
        # 3. Print undo message
        # 4. Return the order
        raise NotImplementedError("TODO: Implement ExecuteOrderCommand.undo")


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
        # TODO: Implement order cancellation
        # 1. Save current status
        # 2. Set status to "CANCELLED"
        # 3. Print cancellation message
        # 4. Return the order
        raise NotImplementedError("TODO: Implement CancelOrderCommand.execute")

    def undo(self) -> Order:
        """
        Undo the cancellation.

        Returns:
            The restored order.
        """
        # TODO: Implement undo of cancellation
        # 1. Restore previous status if available
        # 2. Print restoration message
        # 3. Return the order
        raise NotImplementedError("TODO: Implement CancelOrderCommand.undo")


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
        # TODO: Implement execute with history tracking
        # 1. Call command.execute()
        # 2. Append command to history
        # 3. Clear redo stack (new command invalidates redo)
        # 4. Return result
        raise NotImplementedError("TODO: Implement CommandInvoker.execute")

    def undo(self) -> Optional[Any]:
        """
        Undo the last command.

        Returns:
            Result of undo operation, or None if no history.
        """
        # TODO: Implement undo
        # 1. If history is empty, print message and return None
        # 2. Pop command from history
        # 3. Call command.undo()
        # 4. Push command to redo stack
        # 5. Return result
        raise NotImplementedError("TODO: Implement CommandInvoker.undo")

    def redo(self) -> Optional[Any]:
        """
        Redo the last undone command.

        Returns:
            Result of redo operation, or None if no redo available.
        """
        # TODO: Implement redo
        # 1. If redo stack is empty, print message and return None
        # 2. Pop command from redo stack
        # 3. Call command.execute()
        # 4. Append command to history
        # 5. Return result
        raise NotImplementedError("TODO: Implement CommandInvoker.redo")

    def get_history(self) -> list[Command]:
        """Get command history."""
        return self._history.copy()

    def clear_history(self) -> None:
        """Clear command history and redo stack."""
        self._history.clear()
        self._redo_stack.clear()
