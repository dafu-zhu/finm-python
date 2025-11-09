from dataclasses import dataclass
from datetime import datetime
from typing import List
from pathlib import Path
import csv


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
                timestamp = datetime.strptime(row['timestamp'], '%Y-%m-%dT%H:%M:%S'),
                symbol = str(row['symbol']),
                price = float(row['price'])
            )
            data_points.append(data_point)
        return data_points

if __name__ == "__main__":
    filepath = Path.cwd().parents[3]
    print(filepath)