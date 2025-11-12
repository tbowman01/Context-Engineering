"""
Memory Profiler for Context Engineering Systems
================================================

This module provides comprehensive memory profiling tools for analyzing
and optimizing memory usage in context engineering applications.

Author: Context Engineering Contributors
License: MIT
"""

import psutil
import time
import sys
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable, Any
from pathlib import Path
import matplotlib.pyplot as plt
import json


@dataclass
class MemorySnapshot:
    """
    Single point-in-time memory measurement.

    Attributes:
        timestamp: Unix timestamp of measurement
        label: Optional label for this snapshot
        rss_mb: Resident Set Size in megabytes (actual physical memory)
        vms_mb: Virtual Memory Size in megabytes
        percent: Percentage of total system RAM used by process
        available_mb: Available system memory in megabytes
        python_objects: Number of Python objects (if available)
    """

    timestamp: float
    label: str = ""
    rss_mb: float = 0.0
    vms_mb: float = 0.0
    percent: float = 0.0
    available_mb: float = 0.0
    python_objects: int = 0

    def __post_init__(self):
        """Calculate relative timestamp."""
        self.relative_time: float = 0.0

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp,
            "relative_time": self.relative_time,
            "label": self.label,
            "rss_mb": round(self.rss_mb, 2),
            "vms_mb": round(self.vms_mb, 2),
            "percent": round(self.percent, 2),
            "available_mb": round(self.available_mb, 2),
            "python_objects": self.python_objects,
        }


class MemoryProfiler:
    """
    Memory profiler for context engineering systems.

    This profiler tracks memory usage over time, identifies memory leaks,
    and provides visualization and reporting capabilities.

    Example:
        >>> profiler = MemoryProfiler()
        >>> profiler.start()
        >>> # ... do some work
        >>> profiler.record("After loading data")
        >>> # ... do more work
        >>> profiler.record("After processing")
        >>> report = profiler.generate_report()
        >>> profiler.plot_memory_usage()
    """

    def __init__(self, track_python_objects: bool = True):
        """
        Initialize memory profiler.

        Args:
            track_python_objects: Whether to track Python object count
                (slightly slower but more informative)
        """
        self.snapshots: List[MemorySnapshot] = []
        self.process = psutil.Process()
        self.baseline: Optional[MemorySnapshot] = None
        self.track_python_objects = track_python_objects
        self._is_running = False

    def start(self) -> "MemoryProfiler":
        """
        Start profiling session.

        Returns:
            Self for method chaining

        Example:
            >>> profiler = MemoryProfiler().start()
        """
        self.snapshots = []
        self.baseline = self._take_snapshot(label="Baseline")
        self._is_running = True

        print(f"Memory Profiler Started")
        print(f"Baseline: {self.baseline.rss_mb:.1f} MB")
        print("-" * 50)

        return self

    def _take_snapshot(self, label: str = "") -> MemorySnapshot:
        """
        Take current memory snapshot.

        Args:
            label: Optional label for this snapshot

        Returns:
            MemorySnapshot object
        """
        # Get process memory info
        mem_info = self.process.memory_info()
        mem_percent = self.process.memory_percent()

        # Get system memory info
        virtual_mem = psutil.virtual_memory()

        # Count Python objects (optional, slightly expensive)
        python_objects = 0
        if self.track_python_objects:
            try:
                import gc

                python_objects = len(gc.get_objects())
            except Exception:
                pass

        snapshot = MemorySnapshot(
            timestamp=time.time(),
            label=label,
            rss_mb=mem_info.rss / 1024 / 1024,
            vms_mb=mem_info.vms / 1024 / 1024,
            percent=mem_percent,
            available_mb=virtual_mem.available / 1024 / 1024,
            python_objects=python_objects,
        )

        # Calculate relative time from baseline
        if self.baseline:
            snapshot.relative_time = snapshot.timestamp - self.baseline.timestamp

        return snapshot

    def record(self, label: Optional[str] = None) -> MemorySnapshot:
        """
        Record current memory state.

        Args:
            label: Optional label for this measurement

        Returns:
            The recorded snapshot

        Example:
            >>> profiler.record("After loading 1M records")
        """
        if not self._is_running:
            print("Warning: Profiler not started. Call start() first.")
            return None

        snapshot = self._take_snapshot(label=label or f"Snapshot {len(self.snapshots)}")
        self.snapshots.append(snapshot)

        # Print summary
        delta = snapshot.rss_mb - self.baseline.rss_mb if self.baseline else 0
        print(
            f"[{snapshot.label}] "
            f"Memory: {snapshot.rss_mb:.1f} MB "
            f"({snapshot.percent:.1f}% of total) "
            f"[Δ {delta:+.1f} MB]"
        )

        return snapshot

    def stop(self) -> Dict:
        """
        Stop profiling and return summary report.

        Returns:
            Summary dictionary
        """
        if not self._is_running:
            print("Warning: Profiler not running")
            return {}

        self._is_running = False
        print("-" * 50)
        print("Memory Profiler Stopped")

        return self.generate_report()

    def get_peak_memory(self) -> float:
        """
        Get peak memory usage in MB.

        Returns:
            Peak RSS memory in megabytes
        """
        if not self.snapshots:
            return 0.0
        return max(s.rss_mb for s in self.snapshots)

    def get_memory_delta(self) -> float:
        """
        Get memory change since baseline.

        Returns:
            Memory delta in megabytes (positive = increase)
        """
        if not self.baseline or not self.snapshots:
            return 0.0
        current = self.snapshots[-1]
        return current.rss_mb - self.baseline.rss_mb

    def detect_memory_leak(self, threshold_mb: float = 10.0) -> bool:
        """
        Detect potential memory leak.

        A simple heuristic: if memory consistently increases across
        multiple measurements, flag as potential leak.

        Args:
            threshold_mb: Minimum increase to consider as leak

        Returns:
            True if potential memory leak detected
        """
        if len(self.snapshots) < 3:
            return False

        # Check if memory is consistently increasing
        increases = 0
        for i in range(1, len(self.snapshots)):
            if self.snapshots[i].rss_mb > self.snapshots[i - 1].rss_mb:
                increases += 1

        # If memory increased in >80% of measurements and total increase > threshold
        leak_ratio = increases / (len(self.snapshots) - 1)
        total_increase = self.get_memory_delta()

        return leak_ratio > 0.8 and total_increase > threshold_mb

    def plot_memory_usage(
        self, save_path: Optional[str] = None, show: bool = True
    ) -> None:
        """
        Plot memory usage over time.

        Args:
            save_path: Optional path to save the plot
            show: Whether to display the plot

        Example:
            >>> profiler.plot_memory_usage("memory_usage.png")
        """
        if not self.snapshots:
            print("No snapshots to plot. Call record() first.")
            return

        # Prepare data
        times = [s.relative_time for s in self.snapshots]
        rss_values = [s.rss_mb for s in self.snapshots]
        vms_values = [s.vms_mb for s in self.snapshots]
        labels = [s.label for s in self.snapshots]

        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

        # Plot 1: RSS Memory Usage
        ax1.plot(times, rss_values, "b-", linewidth=2, label="RSS (Physical)")
        ax1.plot(times, vms_values, "r--", linewidth=1, label="VMS (Virtual)", alpha=0.6)

        # Mark snapshots with labels
        for i, (t, rss, label) in enumerate(zip(times, rss_values, labels)):
            if label and label != f"Snapshot {i}":
                ax1.plot(t, rss, "go", markersize=8)
                ax1.annotate(
                    label,
                    xy=(t, rss),
                    xytext=(10, 10),
                    textcoords="offset points",
                    fontsize=8,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.5),
                )

        ax1.set_xlabel("Time (seconds)")
        ax1.set_ylabel("Memory (MB)")
        ax1.set_title("Memory Usage Over Time")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot 2: Memory Delta from Baseline
        deltas = [s.rss_mb - self.baseline.rss_mb for s in self.snapshots]

        ax2.fill_between(times, 0, deltas, alpha=0.3, color="blue")
        ax2.plot(times, deltas, "b-", linewidth=2)
        ax2.axhline(y=0, color="r", linestyle="--", alpha=0.5)

        ax2.set_xlabel("Time (seconds)")
        ax2.set_ylabel("Memory Change (MB)")
        ax2.set_title("Memory Change from Baseline")
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Plot saved to: {save_path}")

        if show:
            plt.show()
        else:
            plt.close()

    def generate_report(self) -> Dict:
        """
        Generate comprehensive memory report.

        Returns:
            Dictionary containing memory statistics and analysis

        Example:
            >>> report = profiler.generate_report()
            >>> print(f"Peak memory: {report['peak_memory_mb']} MB")
        """
        if not self.snapshots:
            return {"error": "No data collected"}

        # Calculate statistics
        rss_values = [s.rss_mb for s in self.snapshots]
        peak_memory = max(rss_values)
        min_memory = min(rss_values)
        avg_memory = sum(rss_values) / len(rss_values)

        duration = (
            self.snapshots[-1].timestamp - self.baseline.timestamp
            if self.baseline
            else 0
        )

        # Memory leak detection
        potential_leak = self.detect_memory_leak()

        report = {
            "summary": {
                "duration_seconds": round(duration, 2),
                "num_snapshots": len(self.snapshots),
                "baseline_memory_mb": round(self.baseline.rss_mb, 2)
                if self.baseline
                else 0,
            },
            "memory_stats": {
                "peak_memory_mb": round(peak_memory, 2),
                "min_memory_mb": round(min_memory, 2),
                "avg_memory_mb": round(avg_memory, 2),
                "final_memory_mb": round(self.snapshots[-1].rss_mb, 2),
                "memory_delta_mb": round(self.get_memory_delta(), 2),
            },
            "analysis": {
                "potential_memory_leak": potential_leak,
                "memory_growth_rate_mb_per_sec": round(
                    self.get_memory_delta() / duration if duration > 0 else 0, 3
                ),
            },
            "snapshots": [s.to_dict() for s in self.snapshots],
        }

        return report

    def print_report(self) -> None:
        """Print formatted memory report to console."""
        report = self.generate_report()

        if "error" in report:
            print(f"Error: {report['error']}")
            return

        print("\n" + "=" * 60)
        print("MEMORY PROFILING REPORT")
        print("=" * 60)

        print("\nSummary:")
        for key, value in report["summary"].items():
            print(f"  {key}: {value}")

        print("\nMemory Statistics:")
        for key, value in report["memory_stats"].items():
            print(f"  {key}: {value} MB" if "mb" in key.lower() else f"  {key}: {value}")

        print("\nAnalysis:")
        for key, value in report["analysis"].items():
            print(f"  {key}: {value}")

        if report["analysis"]["potential_memory_leak"]:
            print("\n⚠️  WARNING: Potential memory leak detected!")
            print("   Consider investigating memory retention issues.")

        print("=" * 60)

    def save_report(self, filepath: str) -> None:
        """
        Save memory report to JSON file.

        Args:
            filepath: Path to save the report
        """
        report = self.generate_report()

        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)

        print(f"Report saved to: {filepath}")

    def profile_function(
        self, func: Callable, *args, label: Optional[str] = None, **kwargs
    ) -> Any:
        """
        Profile a function's memory usage.

        Args:
            func: Function to profile
            *args: Arguments to pass to function
            label: Optional label for this profiling
            **kwargs: Keyword arguments to pass to function

        Returns:
            Function result

        Example:
            >>> def load_data():
            ...     return [i for i in range(1000000)]
            >>> data = profiler.profile_function(load_data, label="Load Data")
        """
        label = label or func.__name__

        self.record(f"Before {label}")
        result = func(*args, **kwargs)
        self.record(f"After {label}")

        return result

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()


# ============================================================================
# Example Usage & Testing
# ============================================================================

def example_memory_profiling():
    """
    Comprehensive example demonstrating memory profiling.
    """
    print("Memory Profiler Example")
    print("=" * 60)

    # Create profiler and start
    profiler = MemoryProfiler(track_python_objects=True)
    profiler.start()

    # Simulate context engineering operations
    print("\nSimulating context operations...")

    # Operation 1: Load large context
    profiler.record("Baseline")

    large_context = ["Sample text"] * 100000
    profiler.record("After creating large context (100K items)")

    # Operation 2: Process context
    processed = [s.upper() for s in large_context]
    profiler.record("After processing (uppercasing)")

    # Operation 3: Create embeddings (simulated)
    embeddings = [[0.1] * 768 for _ in range(10000)]
    profiler.record("After creating embeddings (10K vectors)")

    # Operation 4: Cleanup
    del large_context
    import gc

    gc.collect()
    profiler.record("After garbage collection")

    # Generate and print report
    report = profiler.stop()
    profiler.print_report()

    # Save report
    profiler.save_report("memory_profile_report.json")

    # Plot visualization
    profiler.plot_memory_usage("memory_usage.png", show=False)


def example_context_manager():
    """Example using context manager syntax."""
    print("\nContext Manager Example")
    print("=" * 60)

    with MemoryProfiler() as profiler:
        profiler.record("Start")

        # Do some work
        data = list(range(1000000))
        profiler.record("Created list of 1M integers")

        # Do more work
        squared = [x**2 for x in data]
        profiler.record("Squared all values")

    # Report is automatically generated on exit


if __name__ == "__main__":
    print("Context Engineering - Memory Profiler")
    print("=" * 60)
    print("This tool helps profile and optimize memory usage in")
    print("context engineering systems.")
    print("=" * 60)
    print()

    # Run examples
    example_memory_profiling()
    print("\n" + "=" * 60 + "\n")
    example_context_manager()

    print("\n" + "=" * 60)
    print("Memory profiling complete!")
    print("Check memory_profile_report.json and memory_usage.png for details.")
    print("=" * 60)
