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
        if self.symbol is None:
            self.symbol = tick.symbol
        elif self.symbol != tick.symbol:
            self.reset()
            self.symbol = tick.symbol

        self.price_history.append(tick.price)
        if len(self.price_history) < self.lookback_window:
            return []

        recent_prices = self.price_history[-self.lookback_window:]
        moving_average = sum(recent_prices) / len(recent_prices)
        deviation = (tick.price - moving_average) / moving_average

        signals = []
        if deviation < -self.threshold:  # Price significantly below MA
            signals.append({
                'type': 'BUY',
                'symbol': tick.symbol,
                'price': tick.price,
                'timestamp': tick.timestamp,
                'reason': f'Price {deviation:.2%} below MA',
                'strategy': 'MeanReversion'
            })
        elif deviation > self.threshold:  # Price significantly above MA
            signals.append({
                'type': 'SELL',
                'symbol': tick.symbol,
                'price': tick.price,
                'timestamp': tick.timestamp,
                'reason': f'Price {deviation:.2%} above MA',
                'strategy': 'MeanReversion'
            })

        if len(self.price_history) > 2 * self.lookback_window:
            self.price_history = self.price_history[-self.lookback_window:]

        return signals
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
        if self.symbol is None:
            self.symbol = tick.symbol
        elif self.symbol != tick.symbol:
            self.reset()
            self.symbol = tick.symbol

        signals = []
        if len(self.price_history) >= self.lookback_window:
            last_window = self.price_history[-self.lookback_window:]
            high, low = max(last_window), min(last_window)

            if tick.price > high * (1 + self.threshold):
                signals.append({
                    'type': 'BUY',
                    'symbol': tick.symbol,
                    'price': tick.price,
                    'timestamp': tick.timestamp,
                    'reason': f'Price {self.threshold:.2%} above previous high prices',
                    'strategy': 'Breakout'
                })
            elif tick.price < low * (1 - self.threshold):
                signals.append({
                    'type': 'SELL',
                    'symbol': tick.symbol,
                    'price': tick.price,
                    'timestamp': tick.timestamp,
                    'reason': f'Price {self.threshold:.2%} below previous low prices',
                    'strategy': 'Breakout'
                })

        self.price_history.append(tick.price)

        if len(self.price_history) > 2 * self.lookback_window:
            self.price_history = self.price_history[-self.lookback_window:]

        return signals
        # 1. Track symbol - if new symbol, reset state
        # 2. If enough history (>= lookback_window):
        #    a. Find high and low of last lookback_window prices
        #    b. Check for breakout:
        #       - If price > high * (1 + threshold): BUY signal
        #       - If price < low * (1 - threshold): SELL signal
        # 3. Add current price to history AFTER checking for breakout
        # 4. Keep history bounded
        # 5. Return list of signal dicts

    def reset(self) -> None:
        """Reset strategy state."""
        self.price_history = []
        self.symbol = None

"""
Note: The location of appending new price. Why in MeanReversionStrategy, it happens before generating signal, 
while in BreakoutStrategy, it happens after?

Usually price updates should happens first. But breakout is a bit special. It buy or sell when current price is 
suddenly high or low. If update price first, the signal generation will use updated price history, which would always
generate no signal since the price jump is absorbed
"""


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
        # 1. Extract timestamp from signal (default to datetime.now())
        # 2. Format log entry string with timestamp, signal type, symbol, price, reason
        # 3. Append to self.logs
        # 4. If log_file is set, write to file; otherwise print to stdout
        timestamp = signal.get("timestamp", datetime.now())
        signal_type = signal.get('type', 'UNKNOWN')
        symbol = signal.get('symbol', 'N/A')
        price = signal.get('price', 0.0)
        reason = signal.get('reason', '')

        log_entry = f"[{timestamp}] {signal_type} {symbol} @ ${price:.2f} - {reason}"
        self.logs.append(log_entry)

        if self.log_file:
            # Append to file
            with open(self.log_file, 'a') as f:
                f.write(log_entry + '\n')
        else:
            # Print to console
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
        # 1. Extract price from signal
        # 2. If price >= price_threshold:
        #    a. Create alert dict with timestamp, type, signal, message
        #    b. Append to self.alerts
        #    c. Print alert message
        price = signal.get("price", 0.0)

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
        # Save current status to _previous_status
        self._previous_status = self.order.status

        # Set order.status to "EXECUTED"
        self.order.status = "EXECUTED"

        # Set order.executed_at to current datetime
        self.order.executed_at = datetime.now()

        # Print execution message
        print(f"Executing: {self.order}")

        # Return the order
        return self.order

    def undo(self) -> Order:
        """
        Undo the order execution.

        Returns:
            The reverted order.
        """
        # If _previous_status exists, restore it
        if self._previous_status is not None:
            self.order.status = self._previous_status

        # Clear executed_at
        self.order.executed_at = None

        # Print undo message
        print(f"Undoing execution: {self.order}")

        # Return the order
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
        # Save current status
        self._previous_status = self.order.status

        # Set status to "CANCELLED"
        self.order.status = "CANCELLED"

        # Print cancellation message
        print(f"Cancelling: {self.order}")

        # Return the order
        return self.order

    def undo(self) -> Order:
        """
        Undo the cancellation.

        Returns:
            The restored order.
        """
        # Restore previous status if available
        if self._previous_status is not None:
            self.order.status = self._previous_status

        # Print restoration message
        print(f"Undoing cancellation: {self.order}")

        # Return the order
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
        # Call command.execute()
        result = command.execute()

        # Append command to history
        self._history.append(command)

        # Clear redo stack (new command invalidates redo)
        self._redo_stack.clear()

        # Return result
        return result

    def undo(self) -> Optional[Any]:
        """
        Undo the last command.

        Returns:
            Result of undo operation, or None if no history.
        """
        # If history is empty, print message and return None
        if not self._history:
            print("No commands to undo")
            return None

        # Pop command from history
        command = self._history.pop()

        # Call command.undo()
        result = command.undo()

        # Push command to redo stack
        self._redo_stack.append(command)

        # Return result
        return result

    def redo(self) -> Optional[Any]:
        """
        Redo the last undone command.

        Returns:
            Result of redo operation, or None if no redo available.
        """
        # If redo stack is empty, print message and return None
        if not self._redo_stack:
            print("No commands to redo")
            return None

        # Pop command from redo stack
        command = self._redo_stack.pop()

        # Call command.execute()
        result = command.execute()

        # Append command to history
        self._history.append(command)

        # Return result
        return result

    def get_history(self) -> list[Command]:
        """Get command history."""
        return self._history.copy()

    def clear_history(self) -> None:
        """Clear command history and redo stack."""
        self._history.clear()
        self._redo_stack.clear()
