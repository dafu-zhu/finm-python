"""
Test suite for data_loader.py with focus on space complexity analysis.

Tests:
1. Functional correctness
2. Memory profiling with tracemalloc
3. Memory profiling with memory_profiler
4. Space complexity verification
5. Memory scaling analysis

Run from project root:
    pytest src/trading_system/hw3/tests/test_data_loader.py -v -s
    pytest src/trading_system/hw3/tests/test_data_loader.py -v -s -m slow
"""

import pytest
import tracemalloc
from pathlib import Path
from datetime import datetime
import csv
import tempfile
import sys
from typing import List

# Import from hw3
from trading_system.hw3.src.data_loader import data_ingestor
from trading_system.hw3.src.models import MarketDataPoint


class TestDataLoaderCorrectness:
    """Test functional correctness of data loading."""

    @pytest.fixture
    def sample_csv(self):
        """Create a temporary CSV file for testing."""
        content = """timestamp,symbol,price
2025-01-01 09:30:00,AAPL,150.25
2025-01-01 09:30:01,AAPL,150.30
2025-01-01 09:30:02,GOOGL,2800.50
2025-01-01 09:30:03,MSFT,380.75
2025-01-01 09:30:04,AAPL,150.35"""

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write(content)
            temp_path = Path(f.name)

        yield temp_path

        # Cleanup
        temp_path.unlink()

    def test_load_valid_csv(self, sample_csv):
        """Test loading a valid CSV file."""
        data = data_ingestor(sample_csv)

        assert len(data) == 5
        assert all(isinstance(point, MarketDataPoint) for point in data)
        assert data[0].symbol == 'AAPL'
        assert data[0].price == 150.25

    def test_frozen_dataclass(self, sample_csv):
        """Test that MarketDataPoint is immutable (frozen)."""
        data = data_ingestor(sample_csv)

        with pytest.raises(AttributeError):
            data[0].price = 999.99  # Should raise error for frozen dataclass

    def test_timestamp_parsing(self, sample_csv):
        """Test correct timestamp parsing."""
        data = data_ingestor(sample_csv)

        assert isinstance(data[0].timestamp, datetime)
        assert data[0].timestamp == datetime(2025, 1, 1, 9, 30, 0)

    def test_empty_csv(self):
        """Test handling of empty CSV (only headers)."""
        content = "timestamp,symbol,price\n"

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            data = data_ingestor(temp_path)
            assert len(data) == 0
        finally:
            temp_path.unlink()

    def test_invalid_timestamp(self):
        """Test handling of invalid timestamp format."""
        content = """timestamp,symbol,price
invalid-timestamp,AAPL,150.25"""

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValueError):
                data_ingestor(temp_path)
        finally:
            temp_path.unlink()


class TestSpaceComplexityTracemalloc:
    """Test space complexity using tracemalloc (built-in, no dependencies)."""

    @pytest.fixture
    def generate_csv(self):
        """Factory to generate CSV files of different sizes."""
        def _generate(n_records: int) -> Path:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
                f.write("timestamp,symbol,price\n")
                for i in range(n_records):
                    # Use modulo for seconds to keep timestamps valid
                    sec = i % 60
                    min_offset = (i // 60) % 60
                    f.write(f"2025-01-01 09:{min_offset:02d}:{sec:02d},AAPL,{150 + i*0.01:.2f}\n")
                return Path(f.name)
        return _generate

    def test_memory_linear_scaling(self, generate_csv):
        """
        Test that memory usage scales linearly with input size - O(n).

        Space Complexity Analysis:
        - Each MarketDataPoint stores:
          * timestamp: datetime object (~48 bytes)
          * symbol: str (~50 bytes for short symbols like "AAPL")
          * price: float (~24 bytes)
          * object overhead: ~16 bytes
        - Total per record: ~150-200 bytes
        - For n records: O(n) space
        """
        sizes = [100, 1000, 10000]
        memory_usage = []

        for size in sizes:
            csv_path = generate_csv(size)

            try:
                # Start memory tracking
                tracemalloc.start()

                # Take snapshot before loading
                snapshot_before = tracemalloc.take_snapshot()

                # Load data
                data = data_ingestor(csv_path)

                # Take snapshot after loading
                snapshot_after = tracemalloc.take_snapshot()

                # Calculate memory difference
                top_stats = snapshot_after.compare_to(snapshot_before, 'lineno')

                # Get current and peak memory
                current, peak = tracemalloc.get_traced_memory()

                tracemalloc.stop()

                memory_usage.append({
                    'size': size,
                    'current_mb': current / (1024 * 1024),
                    'peak_mb': peak / (1024 * 1024),
                    'bytes_per_record': peak / size if size > 0 else 0
                })

                # Verify data loaded correctly
                assert len(data) == size

            finally:
                csv_path.unlink()

        # Print results
        print("\n" + "="*70)
        print("SPACE COMPLEXITY ANALYSIS (tracemalloc)")
        print("="*70)
        for usage in memory_usage:
            print(f"Records: {usage['size']:>6,} | "
                  f"Peak Memory: {usage['peak_mb']:>7.2f} MB | "
                  f"Bytes/Record: {usage['bytes_per_record']:>6.0f}")

        # Verify linear scaling: ratio of memory should be close to ratio of sizes
        if len(memory_usage) >= 2:
            ratio_size = memory_usage[1]['size'] / memory_usage[0]['size']
            ratio_memory = memory_usage[1]['peak_mb'] / memory_usage[0]['peak_mb']

            print(f"\nScaling Analysis:")
            print(f"Size ratio (1000/100): {ratio_size:.1f}x")
            print(f"Memory ratio: {ratio_memory:.1f}x")
            print(f"Expected: ~{ratio_size:.1f}x (linear scaling)")

            # Allow 50% deviation due to overhead, but should be roughly linear
            assert 0.5 * ratio_size <= ratio_memory <= 1.5 * ratio_size, \
                f"Memory scaling is not linear! Expected ~{ratio_size}x, got {ratio_memory:.2f}x"

    def test_memory_per_record_estimate(self, generate_csv):
        """
        Estimate memory per MarketDataPoint record.

        Expected breakdown:
        - datetime object: ~48 bytes
        - str (symbol): ~49 bytes (base) + len(symbol)
        - float (price): ~24 bytes
        - object overhead: ~16 bytes
        - Total: ~137-200 bytes per record
        """
        size = 10000
        csv_path = generate_csv(size)

        try:
            tracemalloc.start()

            # Measure memory before
            baseline_current, baseline_peak = tracemalloc.get_traced_memory()

            # Load data
            data = data_ingestor(csv_path)

            # Measure memory after
            after_current, after_peak = tracemalloc.get_traced_memory()

            tracemalloc.stop()

            # Calculate memory per record
            memory_used = after_peak - baseline_peak
            bytes_per_record = memory_used / size

            print("\n" + "="*70)
            print("MEMORY PER RECORD ANALYSIS")
            print("="*70)
            print(f"Total records: {size:,}")
            print(f"Total memory used: {memory_used / (1024*1024):.2f} MB")
            print(f"Memory per record: {bytes_per_record:.0f} bytes")
            print(f"\nExpected components:")
            print(f"  - datetime object: ~48 bytes")
            print(f"  - str (symbol): ~50 bytes")
            print(f"  - float (price): ~24 bytes")
            print(f"  - object overhead: ~16 bytes")
            print(f"  - Total expected: ~138-200 bytes")

            # Verify reasonable memory usage (100-500 bytes per record)
            # Allowing wider range for Python overhead
            assert 100 <= bytes_per_record <= 500, \
                f"Unexpected memory per record: {bytes_per_record:.0f} bytes"

        finally:
            csv_path.unlink()

    def test_memory_snapshot_analysis(self, generate_csv):
        """
        Detailed memory allocation analysis using snapshots.

        Shows top memory allocations and their locations.
        """
        size = 5000
        csv_path = generate_csv(size)

        try:
            tracemalloc.start()
            snapshot_before = tracemalloc.take_snapshot()

            # Load data
            data = data_ingestor(csv_path)

            snapshot_after = tracemalloc.take_snapshot()
            tracemalloc.stop()

            # Get top memory allocations
            top_stats = snapshot_after.compare_to(snapshot_before, 'lineno')

            print("\n" + "="*70)
            print("TOP 10 MEMORY ALLOCATIONS")
            print("="*70)

            for stat in top_stats[:10]:
                print(f"{stat}")

            # Verify we loaded the data
            assert len(data) == size

        finally:
            csv_path.unlink()


class TestSpaceComplexityMemoryProfiler:
    """Test space complexity using memory_profiler (requires: pip install memory_profiler)."""

    @pytest.fixture
    def generate_csv(self):
        """Factory to generate CSV files of different sizes."""
        def _generate(n_records: int) -> Path:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
                f.write("timestamp,symbol,price\n")
                for i in range(n_records):
                    sec = i % 60
                    min_offset = (i // 60) % 60
                    f.write(f"2025-01-01 09:{min_offset:02d}:{sec:02d},AAPL,{150 + i*0.01:.2f}\n")
                return Path(f.name)
        return _generate

    def test_memory_profiler_basic(self, generate_csv):
        """
        Test memory usage with memory_profiler.

        Note: memory_profiler provides line-by-line memory analysis
        but requires the @profile decorator for detailed output.
        Here we use it programmatically.
        """
        try:
            from memory_profiler import memory_usage
        except ImportError:
            pytest.skip("memory_profiler not installed. Install with: pip install memory_profiler")

        size = 10000
        csv_path = generate_csv(size)

        try:
            # Measure memory usage of the function
            mem_usage = memory_usage((data_ingestor, (csv_path,)), interval=0.01)

            baseline = mem_usage[0]
            peak = max(mem_usage)
            memory_increase = peak - baseline

            print("\n" + "="*70)
            print("MEMORY PROFILER ANALYSIS")
            print("="*70)
            print(f"Records: {size:,}")
            print(f"Baseline memory: {baseline:.2f} MB")
            print(f"Peak memory: {peak:.2f} MB")
            print(f"Memory increase: {memory_increase:.2f} MB")
            print(f"Memory per record: {(memory_increase * 1024 * 1024) / size:.0f} bytes")

            # Verify reasonable memory usage
            assert memory_increase > 0, "Memory usage should increase"

        finally:
            csv_path.unlink()

    def test_memory_scaling_comparison(self, generate_csv):
        """
        Compare memory usage across different dataset sizes.

        Verifies O(n) space complexity by checking that memory
        scales linearly with input size.
        """
        try:
            from memory_profiler import memory_usage
        except ImportError:
            pytest.skip("memory_profiler not installed")

        sizes = [1000, 5000, 10000]
        results = []

        for size in sizes:
            csv_path = generate_csv(size)

            try:
                # Measure memory
                mem_usage = memory_usage((data_ingestor, (csv_path,)), interval=0.01)

                baseline = mem_usage[0]
                peak = max(mem_usage)
                increase = peak - baseline

                results.append({
                    'size': size,
                    'baseline_mb': baseline,
                    'peak_mb': peak,
                    'increase_mb': increase,
                    'bytes_per_record': (increase * 1024 * 1024) / size if increase > 0 else 0
                })

            finally:
                csv_path.unlink()

        # Print results
        print("\n" + "="*70)
        print("MEMORY SCALING ANALYSIS (memory_profiler)")
        print("="*70)
        print(f"{'Records':<10} | {'Baseline (MB)':<15} | {'Peak (MB)':<12} | "
              f"{'Increase (MB)':<15} | {'Bytes/Record':<12}")
        print("-" * 70)

        for result in results:
            print(f"{result['size']:<10,} | "
                  f"{result['baseline_mb']:<15.2f} | "
                  f"{result['peak_mb']:<12.2f} | "
                  f"{result['increase_mb']:<15.2f} | "
                  f"{result['bytes_per_record']:<12.0f}")

        # Verify linear scaling
        if len(results) >= 2 and results[0]['increase_mb'] > 0:
            ratio_size = results[1]['size'] / results[0]['size']
            ratio_memory = results[1]['increase_mb'] / results[0]['increase_mb']

            print(f"\nScaling factor:")
            print(f"Size: {ratio_size:.2f}x")
            print(f"Memory: {ratio_memory:.2f}x")
            print(f"Expected: ~{ratio_size:.2f}x (linear O(n))")

            # Allow 50% deviation
            assert 0.5 * ratio_size <= ratio_memory <= 1.5 * ratio_size


class TestSpaceComplexityLarge:
    """Test with larger datasets to verify O(n) complexity."""

    @pytest.fixture
    def generate_large_csv(self):
        """Generate large CSV files for stress testing."""
        def _generate(n_records: int) -> Path:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
                f.write("timestamp,symbol,price\n")

                # Write in chunks to avoid memory issues during generation
                chunk_size = 10000
                for chunk_start in range(0, n_records, chunk_size):
                    chunk_end = min(chunk_start + chunk_size, n_records)
                    lines = []
                    for i in range(chunk_start, chunk_end):
                        # Create valid timestamps
                        hours = 9 + (i // 3600) % 7  # 9am to 4pm
                        minutes = (i // 60) % 60
                        seconds = i % 60
                        lines.append(f"2025-01-01 {hours:02d}:{minutes:02d}:{seconds:02d},AAPL,{150 + i*0.01:.2f}\n")
                    f.write(''.join(lines))

                return Path(f.name)
        return _generate

    @pytest.mark.slow
    def test_large_dataset_memory(self, generate_large_csv):
        """
        Test memory usage with large dataset (100k records).

        Assignment requirement: Should use <100MB for 100k ticks.

        Expected: ~15-25 MB for 100k records
        (100k records * ~200 bytes/record ≈ 20 MB)
        """
        size = 100000
        csv_path = generate_large_csv(size)

        try:
            tracemalloc.start()

            # Load data
            data = data_ingestor(csv_path)

            # Measure memory
            current, peak = tracemalloc.get_traced_memory()

            tracemalloc.stop()

            peak_mb = peak / (1024 * 1024)
            bytes_per_record = peak / size

            print("\n" + "="*70)
            print("LARGE DATASET TEST (100K records)")
            print("="*70)
            print(f"Records loaded: {len(data):,}")
            print(f"Peak memory: {peak_mb:.2f} MB")
            print(f"Bytes per record: {bytes_per_record:.0f}")
            print(f"\nAssignment requirement: <100 MB {'✓' if peak_mb < 100 else '❌'}")

            # Verify requirements
            assert len(data) == size
            assert peak_mb < 100, f"Memory usage {peak_mb:.2f} MB exceeds 100 MB limit!"

        finally:
            csv_path.unlink()

    @pytest.mark.slow
    def test_complexity_verification(self, generate_large_csv):
        """
        Mathematically verify O(n) space complexity.

        If space complexity is O(n), then:
        Memory(2n) ≈ 2 * Memory(n)
        """
        sizes = [10000, 20000, 40000]
        memory_measurements = []

        for size in sizes:
            csv_path = generate_large_csv(size)

            try:
                tracemalloc.start()
                data = data_ingestor(csv_path)
                current, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()

                memory_measurements.append({
                    'size': size,
                    'peak_bytes': peak,
                    'peak_mb': peak / (1024 * 1024)
                })

                assert len(data) == size

            finally:
                csv_path.unlink()

        print("\n" + "="*70)
        print("O(n) COMPLEXITY VERIFICATION")
        print("="*70)

        for i, measurement in enumerate(memory_measurements):
            print(f"Size: {measurement['size']:>6,} records | "
                  f"Memory: {measurement['peak_mb']:>7.2f} MB")

        # Check ratios
        print("\nScaling Verification:")
        for i in range(1, len(memory_measurements)):
            size_ratio = memory_measurements[i]['size'] / memory_measurements[i-1]['size']
            memory_ratio = memory_measurements[i]['peak_bytes'] / memory_measurements[i-1]['peak_bytes']

            print(f"Size {memory_measurements[i-1]['size']:,} → {memory_measurements[i]['size']:,}: "
                  f"Ratio = {size_ratio:.2f}x")
            print(f"Memory ratio: {memory_ratio:.2f}x")
            print(f"Deviation: {abs(memory_ratio - size_ratio) / size_ratio * 100:.1f}%")

            # Verify linear scaling (within 50% tolerance)
            assert 0.5 * size_ratio <= memory_ratio <= 1.5 * size_ratio, \
                f"Space complexity is not O(n)! Expected ratio ~{size_ratio}, got {memory_ratio:.2f}"

        print("\n✓ Space complexity verified as O(n)")


class TestMemoryOptimization:
    """Test potential memory optimizations."""

    def test_dataclass_memory_footprint(self):
        """
        Measure actual memory footprint of MarketDataPoint.
        """
        import sys

        timestamp = datetime(2025, 1, 1, 9, 30, 0)
        point = MarketDataPoint(timestamp, "AAPL", 150.25)

        # Get size (note: this doesn't include referenced objects)
        size = sys.getsizeof(point)

        # Get sizes of components
        timestamp_size = sys.getsizeof(timestamp)
        symbol_size = sys.getsizeof("AAPL")
        price_size = sys.getsizeof(150.25)

        total_estimated = timestamp_size + symbol_size + price_size

        print("\n" + "="*70)
        print("DATACLASS MEMORY FOOTPRINT")
        print("="*70)
        print(f"MarketDataPoint object: {size} bytes")
        print(f"\nComponent sizes:")
        print(f"  - datetime: {timestamp_size} bytes")
        print(f"  - str ('AAPL'): {symbol_size} bytes")
        print(f"  - float: {price_size} bytes")
        print(f"  - Total components: {total_estimated} bytes")
        print(f"  - Object overhead: ~{size - total_estimated if size > total_estimated else 0} bytes")


if __name__ == "__main__":
    # Run with:
    # cd to project root, then:
    # pytest src/trading_system/hw3/tests/test_data_loader.py -v -s
    #
    # For detailed output:
    # pytest src/trading_system/hw3/tests/test_data_loader.py -v -s --tb=short
    #
    # For slow tests (100K records):
    # pytest src/trading_system/hw3/tests/test_data_loader.py -v -s -m slow
    pytest.main([__file__, "-v", "-s"])