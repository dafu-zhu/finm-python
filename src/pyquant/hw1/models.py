from dataclasses import dataclass


@dataclass
class Order:
    symbol: str
    quantity: int
    price: float
    status: str     # 'pending', 'filled', 'rejected'


class OrderError(Exception):
    pass


class ExecutionError(Exception):
    pass