"""
Reporting module using Observer pattern.

Provides observer implementations for logging, alerting,
and analytics reporting.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

from .patterns.behavioral import Observer


class LoggerObserver(Observer):
    """
    Observer that logs all signals to file or console.
    """

    def __init__(self, log_file: Optional[str | Path] = None, verbose: bool = True):
        """
        Initialize logger.

        Args:
            log_file: Optional path to log file.
            verbose: If True, also print to console.
        """
        self.log_file = Path(log_file) if log_file else None
        self.verbose = verbose
        self.logs: list[str] = []

        # Create log file if specified
        if self.log_file:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def update(self, signal: dict) -> None:
        """
        Log the signal.

        Args:
            signal: Signal dictionary.
        """
        timestamp = signal.get("timestamp", datetime.now())
        if isinstance(timestamp, datetime):
            timestamp_str = timestamp.isoformat()
        else:
            timestamp_str = str(timestamp)

        log_entry = (
            f"[{timestamp_str}] {signal.get('strategy', 'Unknown')} SIGNAL: "
            f"{signal.get('type')} {signal.get('symbol')} @ {signal.get('price', 0):.2f} | "
            f"Reason: {signal.get('reason', 'N/A')}"
        )

        self.logs.append(log_entry)

        if self.verbose:
            print(log_entry)

        if self.log_file:
            with open(self.log_file, "a") as f:
                f.write(log_entry + "\n")


class AlertObserver(Observer):
    """
    Observer that generates alerts for significant events.
    """

    def __init__(self, price_threshold: float = 500.0, alert_file: Optional[str | Path] = None):
        """
        Initialize alert observer.

        Args:
            price_threshold: Price level that triggers alert.
            alert_file: Optional file to write alerts.
        """
        self.price_threshold = price_threshold
        self.alert_file = Path(alert_file) if alert_file else None
        self.alerts: list[dict] = []

        if self.alert_file:
            self.alert_file.parent.mkdir(parents=True, exist_ok=True)

    def update(self, signal: dict) -> None:
        """
        Check signal and generate alert if necessary.

        Args:
            signal: Signal dictionary.
        """
        price = signal.get("price", 0)
        if price >= self.price_threshold:
            alert = {
                "timestamp": datetime.now().isoformat(),
                "type": "HIGH_VALUE_TRADE",
                "signal_type": signal.get("type"),
                "symbol": signal.get("symbol"),
                "price": price,
                "reason": signal.get("reason"),
                "message": f"HIGH VALUE ALERT: {signal.get('type')} {signal.get('symbol')} @ {price:.2f}"
            }
            self.alerts.append(alert)

            print(f"*** ALERT: {alert['message']} ***")

            if self.alert_file:
                with open(self.alert_file, "a") as f:
                    f.write(f"{alert['timestamp']} - {alert['message']}\n")


class StatisticsObserver(Observer):
    """
    Observer that collects statistics on signals.
    """

    def __init__(self):
        """Initialize statistics counters."""
        self.total_signals = 0
        self.buy_signals = 0
        self.sell_signals = 0
        self.by_symbol: dict[str, int] = {}
        self.by_strategy: dict[str, int] = {}

    def update(self, signal: dict) -> None:
        """
        Update statistics with new signal.

        Args:
            signal: Signal dictionary.
        """
        self.total_signals += 1

        # Count by type
        if signal.get("type") == "BUY":
            self.buy_signals += 1
        elif signal.get("type") == "SELL":
            self.sell_signals += 1

        # Count by symbol
        symbol = signal.get("symbol", "UNKNOWN")
        self.by_symbol[symbol] = self.by_symbol.get(symbol, 0) + 1

        # Count by strategy
        strategy = signal.get("strategy", "UNKNOWN")
        self.by_strategy[strategy] = self.by_strategy.get(strategy, 0) + 1

    def get_summary(self) -> dict:
        """
        Get statistics summary.

        Returns:
            Dictionary with statistics.
        """
        return {
            "total_signals": self.total_signals,
            "buy_signals": self.buy_signals,
            "sell_signals": self.sell_signals,
            "by_symbol": self.by_symbol.copy(),
            "by_strategy": self.by_strategy.copy()
        }

    def reset(self) -> None:
        """Reset all statistics."""
        self.total_signals = 0
        self.buy_signals = 0
        self.sell_signals = 0
        self.by_symbol.clear()
        self.by_strategy.clear()


class ReportGenerator:
    """
    Generates reports from signal and analytics data.
    """

    @staticmethod
    def generate_signal_report(signals: list[dict], output_path: Optional[str | Path] = None) -> str:
        """
        Generate a report summarizing signals.

        Args:
            signals: List of signal dictionaries.
            output_path: Optional path to write report.

        Returns:
            Report as string.
        """
        if not signals:
            report = "# Signal Report\n\nNo signals generated.\n"
        else:
            report_lines = [
                "# Signal Report",
                "",
                f"**Total Signals:** {len(signals)}",
                "",
                "## Signal Details",
                "",
                "| Timestamp | Type | Symbol | Price | Strategy | Reason |",
                "|-----------|------|--------|-------|----------|--------|"
            ]

            for signal in signals:
                timestamp = signal.get("timestamp", "N/A")
                if isinstance(timestamp, datetime):
                    timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                report_lines.append(
                    f"| {timestamp} | {signal.get('type', 'N/A')} | "
                    f"{signal.get('symbol', 'N/A')} | {signal.get('price', 0):.2f} | "
                    f"{signal.get('strategy', 'N/A')} | {signal.get('reason', 'N/A')} |"
                )

            report = "\n".join(report_lines)

        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                f.write(report)

        return report

    @staticmethod
    def generate_portfolio_report(portfolio, output_path: Optional[str | Path] = None) -> str:
        """
        Generate a report for portfolio composition.

        Args:
            portfolio: Portfolio instance.
            output_path: Optional path to write report.

        Returns:
            Report as string.
        """
        positions = portfolio.get_positions()
        total_value = portfolio.get_value()

        report_lines = [
            "# Portfolio Report",
            "",
            f"**Name:** {portfolio.name}",
            f"**Owner:** {portfolio.owner}",
            f"**Total Value:** ${total_value:,.2f}",
            "",
            "## Positions",
            "",
            "| Symbol | Quantity | Price | Value | Weight |",
            "|--------|----------|-------|-------|--------|"
        ]

        for pos in positions:
            value = pos.get("value", 0)
            weight = (value / total_value * 100) if total_value > 0 else 0
            report_lines.append(
                f"| {pos.get('symbol', 'N/A')} | {pos.get('quantity', 0)} | "
                f"${pos.get('price', 0):.2f} | ${value:,.2f} | {weight:.1f}% |"
            )

        report = "\n".join(report_lines)

        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                f.write(report)

        return report
