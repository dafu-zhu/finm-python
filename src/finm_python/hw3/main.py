"""
Main orchestration script for the assignment.

Workflow:
1. Load data for different input sizes
2. Initialize strategies
3. Run profiling benchmarks
4. Generate visualizations
5. Create complexity_report.md
"""
from finm_python.hw3 import (
    run_comprehensive_benchmark,
    generate_plots,
    generate_complexity_report
)
from pathlib import Path


# Create output directories
OUTPUT_DIR = Path("./output")
PLOTS_DIR = OUTPUT_DIR / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def main():
    """Main execution."""
    print("Starting Optimization Challenge...\n")

    # Run benchmarks
    results = run_comprehensive_benchmark()

    # Generate visualizations
    print("\n\nGenerating visualizations...")
    plot_filename = generate_plots(results, plot_dir=PLOTS_DIR)

    # Generate report
    print("Generating markdown report...")
    report_path = generate_complexity_report(results, plot_filename, output_dir=OUTPUT_DIR)

    print(f"\n{'='*80}")
    print("OPTIMIZATION CHALLENGE COMPLETE")
    print(f"{'='*80}")
    print(f"\nReport: {report_path}")
    print(f"Plots: {PLOTS_DIR}")

    # Print summary
    print("\n Summary:")
    naive_time = results['data']['Naive']['times'][-1]
    for strategy in results['strategies'][1:]:
        time = results['data'][strategy]['times'][-1]
        if time and naive_time:
            speedup = naive_time / time
            print(f"  {strategy:12} - {speedup:5.1f}x faster than Naive")


if __name__ == "__main__":
    main()