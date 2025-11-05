# Strategy Comparison Report

## Overview

This report compares the performance of **2** trading strategies across key metrics including total return, risk-adjusted performance, and drawdown characteristics.

## Performance Comparison Chart

![Multi-Strategy Comparison](../img/comparison_all_strategies.png)

The chart above shows normalized portfolio values (starting at 1.0) for all strategies, allowing direct visual comparison of relative performance.

## Summary Metrics

| Strategy | Total Return | Sharpe Ratio | Max Drawdown | Recovery Status |
|----------|--------------|--------------|--------------|-----------------|
| **Momentum_20_0.0_-0.0** | -29.47% | -0.0049 | -52.54% | ❌ Not Recovered |
| **MACD_12_26** | -47.03% | -0.0112 | -63.25% | ❌ Not Recovered |

## Detailed Analysis

### Best Performer

**Momentum_20_0.0_-0.0** achieved the highest total return of **-29.47%** with a Sharpe ratio of **-0.0049**.

### Worst Performer

**MACD_12_26** had the lowest total return of **-47.03%** with a Sharpe ratio of **-0.0112**.

### Risk-Adjusted Performance (Sharpe Ratio Ranking)

| Rank | Strategy | Sharpe Ratio | Interpretation |
|------|----------|--------------|----------------|
| 1 | **Momentum_20_0.0_-0.0** | -0.0049 | Poor |
| 2 | **MACD_12_26** | -0.0112 | Poor |

### Drawdown Comparison

| Strategy | Max Drawdown | Peak Date | Bottom Date | Recovery Duration |
|----------|--------------|-----------|-------------|-------------------|
| **MACD_12_26** | -63.25% | 2025-11-03 18:26 | 2025-11-03 18:26 | N/A |
| **Momentum_20_0.0_-0.0** | -52.54% | 2025-11-03 18:26 | 2025-11-03 18:26 | N/A |

## Statistical Summary

### Return Statistics

| Metric | Value |
|--------|-------|
| Average Return | -38.25% |
| Best Return | -29.47% |
| Worst Return | -47.03% |
| Return Spread | 17.56% |

### Risk-Adjusted Return Statistics

| Metric | Value |
|--------|-------|
| Average Sharpe Ratio | -0.0080 |
| Best Sharpe Ratio | -0.0049 |
| Worst Sharpe Ratio | -0.0112 |

### Recovery Analysis

**0** out of **2** strategies (0.0%) recovered from their maximum drawdown during the backtesting period.

## Recommendations

- The following strategies have negative Sharpe ratios and should be reconsidered: **MACD_12_26**, **Momentum_20_0.0_-0.0**
- These strategies have not recovered from their maximum drawdown: **MACD_12_26**, **Momentum_20_0.0_-0.0**. Consider risk mitigation measures.

## Conclusion

This analysis compared 2 trading strategies across multiple performance dimensions. Investors should consider their risk tolerance, investment horizon, and diversification needs when selecting strategies for deployment. The best-performing strategy in terms of raw returns may not always offer the best risk-adjusted returns.

*Report generated on 2025-11-05 11:32:45*