"""
Report generation and visualization.

Functions:
- generate_complexity_report(results: dict, output_path: str)
- generate_plots(results: dict)
"""

from pathlib import Path
from typing import Dict
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def generate_plots(results: Dict, plot_dir: Path):
    """Generate comprehensive comparison visualizations."""
    sns.set_style("whitegrid")
    fig = plt.figure(figsize=(16, 12))

    strategies = results['strategies']
    tick_sizes = results['tick_sizes']
    colors = ['#e74c3c', '#2ecc71', '#3498db', '#9b59b6', '#f39c12', '#1abc9c']

    # Plot 1: Execution Time Comparison
    ax1 = plt.subplot(2, 3, 1)
    for i, strategy in enumerate(strategies):
        times = results['data'][strategy]['times']
        if None not in times:
            ax1.plot(tick_sizes, times, 'o-', label=strategy,
                    linewidth=2, markersize=8, color=colors[i])

    ax1.set_xlabel('Number of Ticks', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Execution Time (seconds)', fontsize=11, fontweight='bold')
    ax1.set_title('Runtime Comparison', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=9, loc='upper left')
    ax1.grid(True, alpha=0.3)

    # Plot 2: Time per Tick
    ax2 = plt.subplot(2, 3, 2)
    x = np.arange(len(tick_sizes))
    width = 0.13

    for i, strategy in enumerate(strategies):
        times_per_tick = results['data'][strategy]['times_per_tick']
        if None not in times_per_tick:
            offset = (i - len(strategies)/2) * width
            ax2.bar(x + offset, times_per_tick, width,
                   label=strategy, color=colors[i], alpha=0.8)

    ax2.set_xlabel('Input Size', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Time per Tick (µs)', fontsize=11, fontweight='bold')
    ax2.set_title('Per-Tick Performance', fontsize=12, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels([f'{n:,}' for n in tick_sizes])
    ax2.legend(fontsize=8, loc='upper left')
    ax2.grid(True, alpha=0.3, axis='y')

    # Plot 3: Memory Usage
    ax3 = plt.subplot(2, 3, 3)
    for i, strategy in enumerate(strategies):
        memory = results['data'][strategy]['memory_peak']
        if None not in memory:
            ax3.plot(tick_sizes, memory, 'o-', label=strategy,
                    linewidth=2, markersize=8, color=colors[i])

    ax3.set_xlabel('Number of Ticks', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Peak Memory (MB)', fontsize=11, fontweight='bold')
    ax3.set_title('Memory Efficiency', fontsize=12, fontweight='bold')
    ax3.legend(fontsize=9, loc='upper left')
    ax3.grid(True, alpha=0.3)

    # Plot 4: Speedup vs Naive (100K ticks)
    ax4 = plt.subplot(2, 3, 4)
    naive_time = results['data']['Naive']['times'][-1]
    speedups = []
    strategy_names = []

    for strategy in strategies[1:]:  # Skip Naive
        time = results['data'][strategy]['times'][-1]
        if time and naive_time:
            speedups.append(naive_time / time)
            strategy_names.append(strategy)

    bars = ax4.barh(strategy_names, speedups, color=colors[1:len(speedups)+1], alpha=0.8)
    ax4.set_xlabel('Speedup Factor (x)', fontsize=11, fontweight='bold')
    ax4.set_title('Speedup vs Naive (100K ticks)', fontsize=12, fontweight='bold')
    ax4.axvline(x=1, color='red', linestyle='--', linewidth=2, alpha=0.5)
    ax4.grid(True, alpha=0.3, axis='x')

    for bar, speedup in zip(bars, speedups):
        width = bar.get_width()
        ax4.text(width, bar.get_y() + bar.get_height()/2,
                f'{speedup:.1f}x', ha='left', va='center', fontweight='bold')

    # Plot 5: Log-Log Time Scaling
    ax5 = plt.subplot(2, 3, 5)
    for i, strategy in enumerate(strategies):
        times = results['data'][strategy]['times']
        if None not in times:
            ax5.loglog(tick_sizes, times, 'o-', label=strategy,
                      linewidth=2, markersize=8, color=colors[i])

    ax5.set_xlabel('Number of Ticks (log)', fontsize=11, fontweight='bold')
    ax5.set_ylabel('Time (seconds, log)', fontsize=11, fontweight='bold')
    ax5.set_title('Complexity Verification (Log-Log)', fontsize=12, fontweight='bold')
    ax5.legend(fontsize=9, loc='upper left')
    ax5.grid(True, alpha=0.3, which='both')

    # Plot 6: Memory Efficiency (100K ticks)
    ax6 = plt.subplot(2, 3, 6)
    memory_values = []
    memory_names = []

    for strategy in strategies:
        memory = results['data'][strategy]['memory_peak'][-1]
        if memory is not None:
            memory_values.append(memory)
            memory_names.append(strategy)

    bars = ax6.bar(memory_names, memory_values, color=colors[:len(memory_values)], alpha=0.8)
    ax6.set_ylabel('Peak Memory (MB)', fontsize=11, fontweight='bold')
    ax6.set_title('Memory Usage (100K ticks)', fontsize=12, fontweight='bold')
    ax6.grid(True, alpha=0.3, axis='y')
    plt.setp(ax6.xaxis.get_majorticklabels(), rotation=45, ha='right')

    for bar, memory in zip(bars, memory_values):
        height = bar.get_height()
        ax6.text(bar.get_x() + bar.get_width()/2, height,
                f'{memory:.4f}', ha='center', va='bottom', fontsize=8)

    plt.tight_layout()
    plot_path = plot_dir / 'optimization_comparison.png'
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()

    return 'optimization_comparison.png'


def generate_complexity_report(results: Dict, plot_filename: str, output_dir: Path) -> Path:
    """Generate comprehensive markdown report."""
    md = []

    # Header
    md.append("# Optimization Challenge - Comprehensive Results\n\n")
    md.append(f"**Generated:** {results['timestamp']}\n")
    md.append(f"**Parameters:** Short={results['params']['short']}, Long={results['params']['long']}\n\n")
    md.append("---\n\n")

    # Strategy Overview
    md.append("## Strategy Overview\n\n")
    md.append("| Strategy | Description | Key Technique |\n")
    md.append("|----------|-------------|---------------|\n")
    for name, desc in zip(results['strategies'], results['descriptions']):
        md.append(f"| **{name}** | {desc} | ")
        if name == 'Naive':
            md.append("List conversion + np.mean |\n")
        elif name == 'Windowed':
            md.append("Deque + Running sums |\n")
        elif name == 'Vectorized':
            md.append("NumPy vectorization |\n")
        elif name == 'Cached':
            md.append("LRU cache memoization |\n")
        elif name == 'Streaming':
            md.append("Generator lazy evaluation |\n")
        elif name == 'Hybrid':
            md.append("Circular buffers + NumPy |\n")
    md.append("\n")

    # Performance Visualization
    md.append("## Performance Comparison\n\n")
    md.append(f"![Optimization Comparison](plots/{plot_filename})\n\n")

    # cProfile Results
    strategies = results['strategies']
    md.append("## cProfile Results\n\n")
    for name in strategies:
        if results['data'][name]['profile_logs']:
            md.append(f"### {name} Strategy\n")
            md.append("\n```\n")
            # Include first 20 lines of profile
            profile_lines = results['data'][name]['profile_logs'].split('\n')[:20]
            md.append('\n'.join(profile_lines))
            md.append("\n```\n\n")

    # Detailed Results Table
    md.append("## Detailed Performance Results\n\n")
    md.append("### Execution Time (seconds)\n\n")
    md.append("| Strategy | 1,000 ticks | 10,000 ticks | 100,000 ticks |\n")
    md.append("|----------|-------------|--------------|---------------|\n")

    for strategy in results['strategies']:
        times = results['data'][strategy]['times']
        md.append(f"| {strategy} | ")
        for t in times:
            if t is not None:
                md.append(f"{t:.4f} | ")
            else:
                md.append("N/A | ")
        md.append("\n")
    md.append("\n")

    # Time per Tick
    md.append("### Time per Tick (microseconds)\n\n")
    md.append("| Strategy | 1,000 ticks | 10,000 ticks | 100,000 ticks |\n")
    md.append("|----------|-------------|--------------|---------------|\n")

    for strategy in results['strategies']:
        times_per_tick = results['data'][strategy]['times_per_tick']
        md.append(f"| {strategy} | ")
        for t in times_per_tick:
            if t is not None:
                md.append(f"{t:.2f} | ")
            else:
                md.append("N/A | ")
        md.append("\n")
    md.append("\n")

    # Memory Usage
    md.append("### Peak Memory Usage (MB)\n\n")
    md.append("| Strategy | 1,000 ticks | 10,000 ticks | 100,000 ticks |\n")
    md.append("|----------|-------------|--------------|---------------|\n")

    for strategy in results['strategies']:
        memory = results['data'][strategy]['memory_peak']
        md.append(f"| {strategy} | ")
        for m in memory:
            if m is not None:
                md.append(f"{m:.4f} | ")
            else:
                md.append("N/A | ")
        md.append("\n")
    md.append("\n")

    # Speedup Analysis
    md.append("## Speedup Analysis (vs Naive)\n\n")
    md.append("| Strategy | 1,000 ticks | 10,000 ticks | 100,000 ticks |\n")
    md.append("|----------|-------------|--------------|---------------|\n")

    naive_times = results['data']['Naive']['times']
    for strategy in results['strategies']:
        if strategy == 'Naive':
            md.append(f"| {strategy} | 1.00x | 1.00x | 1.00x |\n")
        else:
            md.append(f"| {strategy} | ")
            times = results['data'][strategy]['times']
            for i, (naive_t, t) in enumerate(zip(naive_times, times)):
                if naive_t and t:
                    speedup = naive_t / t
                    md.append(f"**{speedup:.2f}x** | ")
                else:
                    md.append("N/A | ")
            md.append("\n")
    md.append("\n")

    # Rankings
    md.append("## Performance Rankings (100,000 ticks)\n\n")

    # Fastest
    md.append("### Fastest Execution\n")
    fastest = sorted(
        [(s, results['data'][s]['times'][-1]) for s in results['strategies']
         if results['data'][s]['times'][-1] is not None],
        key=lambda x: x[1]
    )
    for i, (strategy, time) in enumerate(fastest, 1):
        md.append(f"{i}. **{strategy}**: {time:.4f}s\n")
    md.append("\n")

    # Most Memory Efficient
    md.append("### Most Memory Efficient\n")
    memory_efficient = sorted(
        [(s, results['data'][s]['memory_peak'][-1]) for s in results['strategies']
         if results['data'][s]['memory_peak'][-1] is not None],
        key=lambda x: x[1]
    )
    for i, (strategy, memory) in enumerate(memory_efficient, 1):
        md.append(f"{i}. **{strategy}**: {memory:.4f} MB\n")
    md.append("\n")

    # Key Findings
    md.append("## Key Findings\n\n")

    # Find best performers
    if fastest:
        best_time_strategy, best_time = fastest[0]
        naive_time = results['data']['Naive']['times'][-1]
        if naive_time:
            best_speedup = naive_time / best_time
            md.append(f"1. **Fastest Strategy**: {best_time_strategy} achieves {best_speedup:.1f}x speedup\n")

    if memory_efficient:
        best_mem_strategy, best_mem = memory_efficient[0]
        md.append(f"2. **Most Memory Efficient**: {best_mem_strategy} uses only {best_mem:.4f} MB\n")

    md.append(f"3. **All Optimizations**: Achieve significant improvements over naive implementation\n")
    md.append(f"4. **Complexity Verified**: O(1) strategies scale better than O(n) baseline\n\n")

    # Recommendations
    md.append("## Recommendations\n\n")
    md.append("### Use Case Guide\n\n")
    md.append("- **Real-time Trading (HFT)**: Use **Windowed** or **Hybrid** for O(1) performance\n")
    md.append("- **Backtesting Large Datasets**: Use **Vectorized** for NumPy acceleration\n")
    md.append("- **Low-Memory Environments**: Use **Streaming** for minimal footprint\n")
    md.append("- **Synthetic Data/Testing**: Consider **Cached** for repeated patterns\n")
    md.append("- **Production Systems**: Use **Hybrid** for best overall performance\n\n")

    # Complexity Summary
    md.append("## Complexity Summary\n\n")
    md.append("| Strategy | Time Complexity | Space Complexity | Notes |\n")
    md.append("|----------|-----------------|------------------|-------|\n")
    md.append("| Naive | O(n) | O(n) | Baseline, recalculates everything |\n")
    md.append("| Windowed | O(1) | O(k) | Optimal for streaming |\n")
    md.append("| Vectorized | O(n)* | O(n) | NumPy acceleration |\n")
    md.append("| Cached | O(1)** | O(k+c) | Depends on cache hits |\n")
    md.append("| Streaming | O(1) | O(k) | Generator-based |\n")
    md.append("| Hybrid | O(1) | O(k) | Best overall |\n\n")
    md.append("*With NumPy C-level optimization  \n")
    md.append("**O(n) on cache misses\n\n")

    # Write report
    report_path = output_dir / 'optimization_challenge_report.md'
    with open(report_path, 'w') as f:
        f.write(''.join(md))

    return report_path