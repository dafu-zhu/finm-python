from pathlib import Path
from shlex import quote
from typing import Dict, List
import polars as pl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

from finm_python.hw1 import StrategyState


def value_tbl(time: list, value: list) -> pl.LazyFrame:
    tb = pl.LazyFrame({'time': time, 'value': value})
    tb = tb.with_columns(
        pl.col('time').cast(pl.Datetime), pl.col('value').cast(pl.Float64))
    return tb


def total_return(value: list) -> float:
    return value[-1] / value[0] - 1


def period_returns(time: list, value: list) -> pl.LazyFrame:
    tb = value_tbl(time, value)
    tb = tb.with_columns(
        pl.col('value').pct_change().alias('returns')
    ).drop_nulls()
    return tb


def calc_sharpe(value: list, risk_free: float = 0) -> float:
    s = pl.Series('value', value)
    pct_chg = s.pct_change().drop_nulls()
    excess_ret = pct_chg.mean() - risk_free
    volatility = pct_chg.std()
    return excess_ret / volatility


def calc_max_dd(time: list, value: list) -> dict:  # @save
    """
    Calculate maximum drawdown for an asset
    :param time
    :param value: portfolio's value

    Returns
    -------
    Dict:
        - max_drawdown: amount
        - peak: day that reaches peak of the max drawdown
        - bottom: day that reaches bottom of the max drawdown
        - recover: day recover, if no, then "nan"
        - duration: time length to recover, if no, then "nan"
        - drawdown (pl.LazyFrame): drawdown time series
    """
    # create new df, calculate cumulative return, peak, bottom
    tb = period_returns(time, value)
    tb = tb.with_columns(
        (pl.col('returns') + 1).cum_prod().alias('cum_return')
    ).with_columns(
        pl.col("cum_return").cum_max().alias("peak")
    ).with_columns(
        (pl.col("cum_return") / pl.col("peak") - 1).alias("drawdown")
    )

    # filter the period where max drawdown is realized
    dd_period = tb.filter(
        pl.col("drawdown").eq(pl.col("drawdown").min())
    ).collect()
    max_dd = dd_period["drawdown"][0]
    peak_value = dd_period["peak"]
    bottom_day = dd_period['time'][0]

    peak_day = tb.filter(
        (pl.col("cum_return").eq(peak_value)) &
        (pl.col('time').le(bottom_day))
    ).collect()['time'][-1]  # Take the last occurrence before bottom

    recover_df = tb.filter(
        pl.col("cum_return").ge(peak_value)
        & (pl.col('time').gt(bottom_day))
    ).collect()
    if recover_df.height > 0:
        recover_day = recover_df[0]['time'][0]
        duration = recover_day - peak_day
    else:
        recover_day = None
        duration = None

    result = {
        "max_drawdown": max_dd,
        "peak": peak_day,
        "bottom": bottom_day,
        "recover": recover_day,
        "duration": duration,
        "drawdown": tb.select(pl.col(['time', "drawdown"]))
    }
    return result


def plot_portfolio_value(report: dict, output_path: Path, time_period: str = 'short'):
    """
    Plot portfolio value over time showing the equity curve.

    :param report: Dictionary containing 'prd_return' LazyFrame with columns ['time', 'value']
    :param output_path: Path to save the plot
    :param time_period: 'short' (intraday/days), 'medium' (weeks/months), or 'long' (years)
    """
    # Collect the data
    df = report['prd_return'].collect()

    # Normalize to start at 1.0
    initial_value = df['value'][0]
    normalized_values = df['value'] / initial_value

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot equity curve
    ax.plot(df['time'], normalized_values, linewidth=1.5, color='#2E86AB', label='Portfolio Value')

    # Add horizontal line at 1.0
    ax.axhline(y=1.0, color='gray', linestyle='--', linewidth=1, alpha=0.5)

    # Format
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('Portfolio Value (Normalized)', fontsize=12)
    ax.set_title(f'Portfolio Value Over Time - {report["name"]}', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()

    # Format x-axis based on time period
    if time_period == 'short':
        # Intraday or few days - show time with seconds or hours
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    elif time_period == 'medium':
        # Weeks to months - show date and optionally time
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(df) // 10)))
    elif time_period == 'long':
        # Years - show year or year-month
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_minor_locator(mdates.MonthLocator(interval=6))

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_drawdown(report: dict, output_path: Path, time_period: str = 'short'):
    """
    Plot drawdown over time with annotations for peak, bottom, and recovery.

    Args:
        report: Dictionary containing 'max_dd' with drawdown LazyFrame and key events
        output_path: Path to save the plot
        time_period: 'short' (intraday/days), 'medium' (weeks/months), or 'long' (years)
    """
    # Collect the data
    df = report['max_dd']['drawdown'].collect()

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot drawdown curve (negative values)
    ax.fill_between(df['time'], 0, df['drawdown'] * 100,
                    alpha=0.3, color='#A23B72', label='Drawdown')
    ax.plot(df['time'], df['drawdown'] * 100,
            linewidth=1.5, color='#A23B72')

    # Format
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('Drawdown (%)', fontsize=12)
    ax.set_title(f'Drawdown Analysis - {report["name"]}', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left')

    # Format x-axis based on time period
    if time_period == 'short':
        # Intraday or few days - show time with seconds or hours
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    elif time_period == 'medium':
        # Weeks to months - show date and optionally time
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(df) // 10)))
    elif time_period == 'long':
        # Years - show year or year-month
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_minor_locator(mdates.MonthLocator(interval=6))

    plt.xticks(rotation=45, ha='right')

    # Set y-axis limits to ensure 0 is at top
    y_min = df['drawdown'].min() * 100
    ax.set_ylim(y_min * 1.1, 0)  # Add 10% padding at bottom

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_multi_strategy_pnl(
        names: List[str],
        states: Dict[str, StrategyState],
        output_path: Path,
        time_period: str = 'short'
):
    """
    Plot all strategies' portfolio values on one chart for comparison.

    Args:
        names: List of strategy names
        states: Dictionary mapping strategy names to StrategyState objects
        output_path: Path to save the plot
        time_period: 'short' (intraday/days), 'medium' (weeks/months), or 'long' (years)
    """
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 7))

    # Color palette for different strategies
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E',
              '#BC4B51', '#5E60CE', '#F72585', '#4361EE', '#06FFA5']

    # Plot each strategy
    for idx, name in enumerate(names):
        time, value = zip(*states[name].history)
        df = pl.DataFrame({'time': time, 'value': value})

        # Normalize to start at 1.0
        initial_value = df['value'][0]
        normalized_values = df['value'] / initial_value

        color = colors[idx % len(colors)]
        ax.plot(df['time'], normalized_values, linewidth=2,
                color=color, label=name, alpha=0.8)

    # Add horizontal line at 1.0
    ax.axhline(y=1.0, color='gray', linestyle='--', linewidth=1, alpha=0.5)

    # Format
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('Portfolio Value (Normalized)', fontsize=12)
    ax.set_title('Multi-Strategy Performance Comparison', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best', fontsize=10)

    # Format x-axis based on time period
    if time_period == 'short':
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    elif time_period == 'medium':
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        # Calculate appropriate interval based on data length
        sample_time, _ = zip(*states[names[0]].history)
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(sample_time) // 10)))
    elif time_period == 'long':
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_minor_locator(mdates.MonthLocator(interval=6))

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def generate_comparison_report(
        names: List[str],
        states: Dict[str, StrategyState],
        img_dir: Path,
        doc_dir: Path,
        time_period: str = 'short'
):
    """
    Generate a comprehensive comparison report for all strategies.

    Args:
        names: List of strategy names to compare
        states: Dictionary mapping strategy names to StrategyState objects
        img_dir: Directory to save images
        doc_dir: Directory to save the markdown report
        time_period: Time period format for charts
    """
    # Calculate metrics for all strategies
    all_reports = {}
    for name in names:
        time, value = zip(*states[name].history)
        max_dd = calc_max_dd(time, value)
        all_reports[name] = {
            'name': name,
            'ttl_return': total_return(value),
            'sharpe': calc_sharpe(value),
            'max_dd': max_dd,
            'prd_return': period_returns(time, value),
            'final_value': value[-1],
            'initial_value': value[0]
        }

    # Generate multi-strategy comparison plot
    comparison_path = img_dir / 'comparison_all_strategies.png'
    plot_multi_strategy_pnl(names, states, output_path=comparison_path, time_period=time_period)
    print(f"Comparison plot saved to: {comparison_path}")

    # Generate markdown comparison report
    md_path = doc_dir / 'strategy_comparison.md'
    write_comparison_report(all_reports, comparison_path, md_path)
    print(f"Comparison report saved to: {md_path}")


def write_comparison_report(all_reports: Dict[str, dict], comparison_path: Path, output_path: Path):
    """
    Write a markdown comparison report for all strategies.

    Args:
        all_reports: Dictionary mapping strategy names to their report dictionaries
        comparison_path: Path to the comparison chart image
        output_path: Path to save the markdown report
    """
    # Adjust path for relative reference from doc directory
    comparison_md = quote(comparison_path.as_posix())

    lines = [
        "# Strategy Comparison Report",
        "",
        "## Overview",
        "",
        f"This report compares the performance of **{len(all_reports)}** trading strategies "
        f"across key metrics including total return, risk-adjusted performance, and drawdown characteristics.",
        "",
        "## Performance Comparison Chart",
        "",
        f"![Multi-Strategy Comparison](../{comparison_md})",
        "",
        "The chart above shows normalized portfolio values (starting at 1.0) for all strategies, "
        "allowing direct visual comparison of relative performance.",
        "",
        "## Summary Metrics",
        "",
        "| Strategy | Total Return | Sharpe Ratio | Max Drawdown | Recovery Status |",
        "|----------|--------------|--------------|--------------|-----------------|"
    ]

    # Sort strategies by total return (descending)
    sorted_strategies = sorted(all_reports.items(),
                               key=lambda x: x[1]['ttl_return'],
                               reverse=True)

    # Add each strategy's metrics
    for name, report in sorted_strategies:
        ttl_return_pct = report['ttl_return'] * 100
        sharpe = report['sharpe']
        max_dd_pct = report['max_dd']['max_drawdown'] * 100
        recovery = '✅ Recovered' if report['max_dd']['recover'] is not None else '❌ Not Recovered'

        lines.append(f"| **{name}** | {ttl_return_pct:+.2f}% | {sharpe:.4f} | {max_dd_pct:.2f}% | {recovery} |")

    lines.extend(["", "## Detailed Analysis", ""])

    # Best and worst performers
    best_strategy = sorted_strategies[0]
    worst_strategy = sorted_strategies[-1]

    lines.extend([
        "### Best Performer",
        "",
        f"**{best_strategy[0]}** achieved the highest total return of "
        f"**{best_strategy[1]['ttl_return'] * 100:+.2f}%** with a Sharpe ratio of "
        f"**{best_strategy[1]['sharpe']:.4f}**.",
        ""
    ])

    if len(sorted_strategies) > 1:
        lines.extend([
            "### Worst Performer",
            "",
            f"**{worst_strategy[0]}** had the lowest total return of "
            f"**{worst_strategy[1]['ttl_return'] * 100:+.2f}%** with a Sharpe ratio of "
            f"**{worst_strategy[1]['sharpe']:.4f}**.",
            ""
        ])

    # Risk-adjusted performance ranking
    sorted_by_sharpe = sorted(all_reports.items(),
                              key=lambda x: x[1]['sharpe'],
                              reverse=True)

    lines.extend([
        "### Risk-Adjusted Performance (Sharpe Ratio Ranking)",
        "",
        "| Rank | Strategy | Sharpe Ratio | Interpretation |",
        "|------|----------|--------------|----------------|"
    ])

    for rank, (name, report) in enumerate(sorted_by_sharpe, 1):
        sharpe = report['sharpe']
        if sharpe > 2:
            interpretation = "Excellent"
        elif sharpe > 1:
            interpretation = "Very Good"
        elif sharpe > 0.5:
            interpretation = "Good"
        elif sharpe > 0:
            interpretation = "Adequate"
        else:
            interpretation = "Poor"

        lines.append(f"| {rank} | **{name}** | {sharpe:.4f} | {interpretation} |")

    # Drawdown analysis
    lines.extend([
        "",
        "### Drawdown Comparison",
        "",
        "| Strategy | Max Drawdown | Peak Date | Bottom Date | Recovery Duration |",
        "|----------|--------------|-----------|-------------|-------------------|"
    ])

    sorted_by_dd = sorted(all_reports.items(),
                          key=lambda x: x[1]['max_dd']['max_drawdown'])

    for name, report in sorted_by_dd:
        max_dd_pct = report['max_dd']['max_drawdown'] * 100
        peak = report['max_dd']['peak'].strftime('%Y-%m-%d %H:%M')
        bottom = report['max_dd']['bottom'].strftime('%Y-%m-%d %H:%M')
        duration = str(report['max_dd']['duration']) if report['max_dd']['duration'] else 'N/A'

        lines.append(f"| **{name}** | {max_dd_pct:.2f}% | {peak} | {bottom} | {duration} |")

    # Statistical summary
    lines.extend([
        "",
        "## Statistical Summary",
        "",
        "### Return Statistics",
        "",
    ])

    returns = [r['ttl_return'] * 100 for r in all_reports.values()]
    avg_return = sum(returns) / len(returns)
    max_return = max(returns)
    min_return = min(returns)

    lines.extend([
        "| Metric | Value |",
        "|--------|-------|",
        f"| Average Return | {avg_return:.2f}% |",
        f"| Best Return | {max_return:+.2f}% |",
        f"| Worst Return | {min_return:+.2f}% |",
        f"| Return Spread | {max_return - min_return:.2f}% |",
        ""
    ])

    # Sharpe ratio statistics
    sharpes = [r['sharpe'] for r in all_reports.values()]
    avg_sharpe = sum(sharpes) / len(sharpes)

    lines.extend([
        "### Risk-Adjusted Return Statistics",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Average Sharpe Ratio | {avg_sharpe:.4f} |",
        f"| Best Sharpe Ratio | {max(sharpes):.4f} |",
        f"| Worst Sharpe Ratio | {min(sharpes):.4f} |",
        ""
    ])

    # Recovery analysis
    recovered_count = sum(1 for r in all_reports.values() if r['max_dd']['recover'] is not None)
    recovery_rate = (recovered_count / len(all_reports)) * 100

    lines.extend([
        "### Recovery Analysis",
        "",
        f"**{recovered_count}** out of **{len(all_reports)}** strategies ({recovery_rate:.1f}%) "
        f"recovered from their maximum drawdown during the backtesting period.",
        ""
    ])

    # Recommendations
    lines.extend([
        "## Recommendations",
        "",
    ])

    if best_strategy[1]['sharpe'] > 1 and best_strategy[1]['max_dd']['recover'] is not None:
        lines.append(
            f"- **{best_strategy[0]}** shows the most promising combination of returns and risk management, "
            f"with strong recovery characteristics."
        )

    strategies_with_poor_sharpe = [name for name, r in all_reports.items() if r['sharpe'] < 0]
    if strategies_with_poor_sharpe:
        lines.append(
            f"- The following strategies have negative Sharpe ratios and should be reconsidered: "
            f"{', '.join(f'**{s}**' for s in strategies_with_poor_sharpe)}"
        )

    unrecovered = [name for name, r in all_reports.items() if r['max_dd']['recover'] is None]
    if unrecovered:
        lines.append(
            f"- These strategies have not recovered from their maximum drawdown: "
            f"{', '.join(f'**{s}**' for s in unrecovered)}. Consider risk mitigation measures."
        )

    lines.extend([
        "",
        "## Conclusion",
        "",
        f"This analysis compared {len(all_reports)} trading strategies across multiple performance dimensions. "
        f"Investors should consider their risk tolerance, investment horizon, and diversification needs "
        f"when selecting strategies for deployment. The best-performing strategy in terms of raw returns "
        f"may not always offer the best risk-adjusted returns.",
        "",
        f"*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
    ])

    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def generate_report(
        names: List[str],
        states: Dict[str, StrategyState],
        img_dir: Path,
        doc_dir: Path,
        time_period: str = 'short'
):
    for name in names:
        time, value = zip(*states[name].history)
        max_dd = calc_max_dd(time, value)
        report = {
            'name': name,
            'ttl_return': total_return(value),
            'prd_return': period_returns(time, value),
            'sharpe': calc_sharpe(value),
            'max_dd': max_dd
        }

        pnl_path = img_dir / f'pnl_{name}.png'
        drawdown_path = img_dir / f'drawdown_{name}.png'

        # Generate plots
        plot_portfolio_value(report, output_path=pnl_path, time_period=time_period)
        plot_drawdown(report, output_path=drawdown_path, time_period=time_period)
        print(f"Plots saved to: {pnl_path}, {drawdown_path}")

        # Generate a Markdown report
        md_path = doc_dir / f'performance_{name}.md'
        write_markdown_report(report, pnl_path, drawdown_path, md_path)
        print(f"Report saved to: {md_path}")

    # Generate comprehensive comparison report if multiple strategies
    if len(names) > 1:
        print(f"\nGenerating comprehensive comparison report for {len(names)} strategies...")
        generate_comparison_report(names, states, img_dir, doc_dir, time_period)
        print("Comprehensive comparison report complete!")
    else:
        print("\nSkipping comparison report (only one strategy provided)")


def write_markdown_report(report: dict, pnl_path: Path, drawdown_path: Path, output_path: Path):
    """
    Write a Markdown performance report.

    :param report: Dict
    :param pnl_path: relative path of pnl_*.png file
    :param pnl_path: relative path of drawdown_*.png file
    :param output_path: absolute path to save the Markdown report
    :param drawdown_path:
    """
    # Change base directory into doc
    pnl_md = quote(pnl_path.as_posix())
    drawdown_md = quote(drawdown_path.as_posix())

    # Extract metrics
    name = report['name']
    ttl_return = report['ttl_return']
    sharpe = report['sharpe']
    max_dd_info = report['max_dd']

    # Format metrics
    ttl_return_pct = ttl_return * 100
    max_dd_pct = max_dd_info['max_drawdown'] * 100

    # Build markdown content line by line
    lines = [f"# Performance Report: {name}", "", "## Executive Summary", "", "| Metric | Value |",
             "|--------|-------|", f"| **Total Return** | {ttl_return_pct:+.2f}% |",
             f"| **Sharpe Ratio** | {sharpe:.4f} |", f"| **Maximum Drawdown** | {max_dd_pct:.2f}% |"]

    # Header
    recovery_status = 'Recovered' if max_dd_info['recover'] is not None else '❌ No Recovery'
    lines.append(f"| **Recovery Status** | {recovery_status} |")
    lines.append("")

    # Performance Analysis
    lines.append("## Performance Analysis")
    lines.append("")
    lines.append("### Overall Performance")
    lines.append("")

    # Add narrative based on performance
    if ttl_return >= 0:
        lines.append(
            f"The **{name}** strategy generated a positive return of **{ttl_return_pct:.2f}%** over the backtesting period. ")
    else:
        lines.append(
            f"The **{name}** strategy resulted in a loss of **{ttl_return_pct:.2f}%** over the backtesting period. ")

    # Sharpe ratio interpretation
    if sharpe > 1:
        lines.append(f"The Sharpe ratio of **{sharpe:.4f}** indicates strong risk-adjusted performance. ")
    elif sharpe > 0:
        lines.append(f"The Sharpe ratio of **{sharpe:.4f}** indicates modest risk-adjusted performance. ")
    else:
        lines.append(
            f"The negative Sharpe ratio of **{sharpe:.4f}** indicates poor risk-adjusted performance, with returns not compensating for the risk taken. ")

    lines.append("")
    lines.append("### Portfolio Value Over Time")
    lines.append("")
    lines.append(f"![Portfolio Value](../{pnl_md})")
    lines.append("")
    lines.append("The equity curve above shows the evolution of portfolio value throughout the backtesting period.")
    lines.append("")

    # Drawdown analysis
    lines.append("## Drawdown Analysis")
    lines.append("")
    lines.append(f"![Drawdown Analysis](../{drawdown_md})")
    lines.append("")

    lines.append("### Maximum Drawdown Details")
    lines.append("")
    lines.append("| Event | Timestamp | Value |")
    lines.append("|-------|-----------|-------|")
    lines.append(f"| **Peak** | {max_dd_info['peak'].strftime('%Y-%m-%d %H:%M:%S')} | 0.00% |")
    lines.append(f"| **Bottom** | {max_dd_info['bottom'].strftime('%Y-%m-%d %H:%M:%S')} | {max_dd_pct:.2f}% |")

    if max_dd_info['recover'] is not None:
        lines.append(f"| **Recovery** | {max_dd_info['recover'].strftime('%Y-%m-%d %H:%M:%S')} | 0.00% |")
        lines.append(f"| **Duration** | - | {max_dd_info['duration']} periods |")
        lines.append("")

        lines.append(f"The strategy experienced a maximum drawdown of **{max_dd_pct:.2f}%**, ")
        lines.append(f"reaching its lowest point at {max_dd_info['bottom'].strftime('%H:%M:%S')}. ")
        lines.append(f"The portfolio successfully recovered after **{max_dd_info['duration']} periods**, ")
        lines.append(f"returning to its previous peak at {max_dd_info['recover'].strftime('%H:%M:%S')}.")
        lines.append("")
    else:
        lines.append(f"| **Recovery** | - | ❌ Not Recovered |")
        lines.append(f"| **Duration** | - | N/A |")
        lines.append("")

        lines.append(f"⚠️ **Warning**: The strategy experienced a maximum drawdown of **{max_dd_pct:.2f}%** ")
        lines.append(f"and **has not recovered** by the end of the backtesting period. ")
        lines.append(f"The drawdown began at {max_dd_info['peak'].strftime('%H:%M:%S')} ")
        lines.append(f"and reached its lowest point at {max_dd_info['bottom'].strftime('%H:%M:%S')}.")
        lines.append("")

    # Key statistics summary
    prd_return_df = report['prd_return'].collect()

    lines.append("## Key Statistics")
    lines.append("")
    lines.append("| Statistic | Value |")
    lines.append("|-----------|-------|")
    lines.append(f"| Number of Periods | {len(prd_return_df)} |")
    lines.append(f"| Starting Value | ${prd_return_df['value'][0]:,.2f} |")
    lines.append(f"| Ending Value | ${prd_return_df['value'][-1]:,.2f} |")
    lines.append(f"| Total Return | {ttl_return_pct:+.2f}% |")
    lines.append(f"| Sharpe Ratio | {sharpe:.4f} |")
    lines.append(f"| Maximum Drawdown | {max_dd_pct:.2f}% |")
    lines.append("")

    # Conclusion
    lines.append("## Conclusion")
    lines.append("")

    if ttl_return >= 0 and sharpe > 0 and (max_dd_info['recover'] is not None or abs(max_dd_pct) < 10):
        lines.append(
            f"The **{name}** strategy demonstrates positive performance with acceptable risk characteristics. ")
    elif ttl_return < 0 or sharpe < 0:
        lines.append(
            f"The **{name}** strategy shows concerning performance metrics that warrant further investigation. ")
    else:
        lines.append(f"The **{name}** strategy shows mixed results. ")

    lines.append(
        "Traders should consider these metrics in the context of their risk tolerance and investment objectives before deployment.")
    lines.append("")

    lines.append(f"*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))