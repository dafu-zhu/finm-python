# Reporting

## Objective

Compute:
- Total return `float`
- Series of periodic returns `pl.LazyFrame`: with column `['time', 'value']`
- Sharpe ratio `float`
- Maximum drawdown `dict`
  - max_drawdown `float`
  - peak `datetime`: day that reaches peak during the max drawdown
  - bottom `datetime`: day that reaches bottom during the max drawdown
  - recovery `datetime` or `None`: if value recovered from bottom, when it was recovered
  - duration `int` or `None`: if value recovered from bottom, how long it took to recover
  - drawdown `pl.LazyFrame`: with column `['time', 'drawdown']`

