from pathlib import Path
from shlex import quote

import polars as pl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from src.pyquant.utils import root_dir


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


def plot_portfolio_value(report: dict, output_path: Path):
    """
    Plot portfolio value over time showing the equity curve.

    :param: report: Dictionary containing 'prd_return' LazyFrame with columns ['time', 'value']
    :param: output_path: Path to save the plot
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

    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_drawdown(report: dict, output_path: Path):
    """
    Plot drawdown over time with annotations for peak, bottom, and recovery.

    Args:
        report: Dictionary containing 'max_dd' with drawdown LazyFrame and key events
        output_path: Path to save the plot
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

    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.xticks(rotation=45)

    # Set y-axis limits to ensure 0 is at top
    y_min = df['drawdown'].min() * 100
    ax.set_ylim(y_min * 1.1, 0)  # Add 10% padding at bottom

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def generate_report(names, states, img_dir: Path, doc_dir: Path):
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
        plot_portfolio_value(report, output_path=pnl_path)
        plot_drawdown(report, output_path=drawdown_path)
        print(f"Plots saved to: {pnl_path}, {drawdown_path}")

        # Generate a Markdown report
        md_path = doc_dir / f'performance_{name}.md'
        write_markdown_report(report, pnl_path, drawdown_path, md_path)
        print(f"Report saved to: {md_path}")


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
    pnl_path = Path('..') / pnl_path.relative_to('.')
    drawdown_path = Path('..') / drawdown_path.relative_to('.')
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
    lines.append(f"![Portfolio Value]({pnl_md})")
    lines.append("")
    lines.append("The equity curve above shows the evolution of portfolio value throughout the backtesting period.")
    lines.append("")

    # Drawdown analysis
    lines.append("## Drawdown Analysis")
    lines.append("")
    lines.append(f"![Drawdown Analysis]({drawdown_md})")
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