from dataclasses import dataclass
from datetime import datetime
from typing import List
import csv
from pathlib import Path
from finm_python.hw1 import root_dir


@dataclass(frozen=True)
class MarketDataPoint:
    timestamp: datetime
    symbol: str
    price: float


def data_ingestor(filepath: Path) -> List[MarketDataPoint]:
    with open(filepath, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        data_points = []
        for row in reader:
            data_point = MarketDataPoint(
                timestamp = datetime.strptime(row['timestamp'], '%Y-%m-%dT%H:%M:%S.%f'),
                symbol = str(row['symbol']),
                price = float(row['price'])
            )
            data_points.append(data_point)
        return data_points


if __name__ == "__main__":
    root = root_dir()
    csvfile = root / 'data' / 'raw' / 'market_data.csv'
    ingestor = data_ingestor(csvfile)
    print(ingestor)
