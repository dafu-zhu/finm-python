"""
Event Logger

This module implements a structured event logging system for the trading system.
Events are logged with timestamps and can be saved to JSON for replay and analysis.

The logger captures important system events like:
- Order creation
- Order state changes
- Risk check results
- Order fills
- Order rejections

All events are stored in memory and can be saved to a JSON file.
"""

from datetime import datetime
from typing import Any, Dict, List
import json
from pathlib import Path


class Logger:
    """
    Singleton logger for recording trading system events.

    The logger maintains an in-memory list of events, each with a timestamp,
    event type, and associated data. Events can be saved to a JSON file for
    persistence and later analysis.

    Attributes:
        events (List[Dict]): List of logged events
        log_file (Path): Path to the JSON file for saving events
    """

    _instance = None

    def __new__(cls, path: str = "events.json"):
        """
        Implement singleton pattern to ensure only one logger instance exists.

        Args:
            path (str): Path to the log file (default: "events.json")

        Returns:
            Logger: The singleton logger instance

        TODO: Implement singleton pattern:
        1. Check if cls._instance is None
        2. If None, create new instance using super().__new__(cls)
        3. Return cls._instance
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, path: str = "events.json"):
        """
        Initialize the logger (called only once due to singleton pattern).

        Args:
            path (str): Path to the JSON file for saving events

        TODO: Implement initialization:
        1. Only initialize if not already initialized (check for hasattr)
        2. Initialize events as an empty list
        3. Store log_file as a Path object
        4. If the log file exists, optionally load previous events
        """
        pass

    def log(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Log an event with timestamp and data.

        Creates an event record with:
        - timestamp: ISO format datetime string
        - event_type: Category of event (e.g., "OrderCreated", "OrderFilled")
        - data: Dictionary containing event-specific information

        Args:
            event_type (str): Type of event being logged
            data (Dict[str, Any]): Event data (can contain any JSON-serializable values)

        TODO: Implement the following:
        1. Create a dictionary with:
           - 'timestamp': current time in ISO format (datetime.now().isoformat())
           - 'event_type': the event_type parameter
           - 'data': the data parameter
        2. Append this dictionary to self.events
        3. Print the log entry to console for real-time monitoring
           Format: "[LOG] {event_type} = {data}"
        """
        pass

    def save(self, path: str = None) -> None:
        """
        Save all logged events to a JSON file.

        Args:
            path (str): Optional path to save to (uses self.log_file if None)

        TODO: Implement the following:
        1. Determine the file path (use parameter or self.log_file)
        2. Open the file in write mode
        3. Use json.dump() to write self.events to the file
        4. Use indent=2 for readable formatting
        5. Print a message indicating how many events were saved
        """
        pass

    def load(self, path: str = None) -> List[Dict]:
        """
        Load events from a JSON file.

        Args:
            path (str): Optional path to load from (uses self.log_file if None)

        Returns:
            List[Dict]: List of loaded events

        TODO: Implement the following:
        1. Determine the file path
        2. Check if file exists
        3. If exists, load JSON and return the events
        4. If not exists, return empty list
        5. Handle JSON decode errors gracefully
        """
        pass

    def get_events_by_type(self, event_type: str) -> List[Dict]:
        """
        Filter events by type.

        Args:
            event_type (str): The event type to filter for

        Returns:
            List[Dict]: All events matching the specified type

        TODO: Filter self.events and return only those with matching event_type
        """
        pass

    def get_events_for_symbol(self, symbol: str) -> List[Dict]:
        """
        Get all events related to a specific symbol.

        Args:
            symbol (str): The trading symbol to filter for

        Returns:
            List[Dict]: All events where data contains the symbol

        TODO: Filter events where the 'data' dictionary contains 'symbol' key
        TODO: Return events where data['symbol'] matches the parameter
        """
        pass

    def clear(self) -> None:
        """
        Clear all logged events from memory.

        TODO: Clear the events list
        TODO: Print a message indicating events were cleared
        """
        pass

    def get_event_count(self) -> int:
        """
        Get the total number of logged events.

        Returns:
            int: Number of events in the log

        TODO: Return the length of self.events
        """
        pass

    def print_summary(self) -> None:
        """
        Print a summary of logged events by type.

        TODO: Create a count of events by type
        TODO: Print the summary in a readable format
        Example output:
            Event Summary:
            - OrderCreated: 5
            - OrderFilled: 3
            - OrderRejected: 1
            Total: 9 events
        """
        pass

    def replay_events(self) -> None:
        """
        Replay all logged events by printing them in order.

        Useful for debugging and understanding the sequence of system events.

        TODO: Iterate through all events
        TODO: Print each event with timestamp and data in a readable format
        """
        pass

    def __str__(self) -> str:
        """
        String representation of the logger.

        Returns:
            str: Summary of logger state

        TODO: Return a string showing:
        1. Number of events logged
        2. Path to log file
        3. Event types present
        """
        pass


def main():
    """
    Example usage and testing of the Logger.

    TODO: Create test scenarios:
    1. Create logger instance and log several events
    2. Save events to file
    3. Clear and reload events
    4. Filter events by type
    5. Print summary
    """
    print("Testing Logger")
    print("-" * 50)

    # TODO: Get logger instance
    # logger = Logger("test_events.json")

    # TODO: Log some sample events
    # logger.log("OrderCreated", {"symbol": "AAPL", "qty": 100, "side": "1"})
    # logger.log("OrderAcked", {"symbol": "AAPL", "order_id": "1"})
    # logger.log("OrderFilled", {"symbol": "AAPL", "qty": 100, "price": 150.00})

    # TODO: Print summary

    # TODO: Save to file

    # TODO: Test filtering by type

    # TODO: Test clearing and reloading

    pass


if __name__ == "__main__":
    main()
