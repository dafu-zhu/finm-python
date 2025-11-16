"""
HW8: Interprocess Communication for Trading Systems

This module provides implementations for:
- TCP socket-based communication between processes
- Shared memory management for market data
- Multi-process trading system orchestration
- Message serialization and protocol design
- Real-time trading signal generation

Architecture:
    [ Gateway ] -> [ OrderBook ] -> [ Strategy ] -> [ OrderManager ]

Components:
- Gateway: Streams price and sentiment data via TCP sockets
- OrderBook: Maintains shared memory price store
- Strategy: Generates trading signals from shared memory and news
- OrderManager: Receives and logs executed trades
"""

__version__ = "0.1.0"
