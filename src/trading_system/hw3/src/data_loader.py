"""
CSV data ingestion and parsing module.

Functions:
- load_market_data(filepath: Path) -> List[MarketDataPoint]
- generate_synthetic_data(n_ticks: int, filepath: Path) -> None
- validate_csv_format(filepath: Path) -> bool

Complexity Analysis:
- Loading: O(n) time, O(n) space
"""

from datetime import datetime
from typing import List
from pathlib import Path
import csv
from trading_system.hw3.src.models import MarketDataPoint


def data_ingestor(filepath: Path) -> List[MarketDataPoint]:
    with open(filepath, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        data_points = []
        for row in reader:
            data_point = MarketDataPoint(
                timestamp = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S'),
                symbol = str(row['symbol']),
                price = float(row['price'])
            )
            data_points.append(data_point)
        return data_points

if __name__ == "__main__":
    path = Path('../data/raw/market_data.csv')
    loader = data_ingestor(path)
    print(loader)