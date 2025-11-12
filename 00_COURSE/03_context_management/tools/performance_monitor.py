"""
Performance Monitor for Context Engineering Systems
====================================================

Real-time performance monitoring and analysis for context operations,
including latency, throughput, token efficiency, and quality metrics.

Author: Context Engineering Contributors
License: MIT
"""

import time
import statistics
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any, Tuple
from collections import deque
import json
from pathlib import Path
import matplotlib.pyplot as plt
from datetime import datetime


@dataclass
class PerformanceMetrics:
    """
    Performance metrics for a single operation.

    Attributes:
        operation_name: Name of the operation
        timestamp: When the operation occurred
        duration_ms: How long it took (milliseconds)
        tokens_processed: Number of tokens processed
        tokens_per_second: Processing throughput
        memory_delta_mb: Memory change during operation
        quality_score: Optional quality metric (0-1)
        metadata: Additional custom metrics
    """

    operation_name: str
    timestamp: float
    duration_ms: float
    tokens_processed: int = 0
    tokens_per_second: float = 0.0
    memory_delta_mb: float = 0.0
    quality_score: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Calculate derived metrics."""
        if self.tokens_processed > 0 and self.duration_ms > 0:
            self.tokens_per_second = (self.tokens_processed / self.duration_ms) * 1000

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "operation_name": self.operation_name,
            "timestamp": self.timestamp,
            "duration_ms": round(self.duration_ms, 2),
            "tokens_processed": self.tokens_processed,
            "tokens_per_second": round(self.tokens_per_second, 2),
            "memory_delta_mb": round(self.memory_delta_mb, 2),
            "quality_score": round(self.quality_score, 3) if self.quality_score else None,
            "metadata": self.metadata,
        }


class PerformanceMonitor:
    """
    Real-time performance monitoring for context engineering systems.

    Tracks latency, throughput, resource usage, and quality metrics
    across different operations. Provides statistical analysis,
    visualization, and anomaly detection.

    Example:
        >>> monitor = PerformanceMonitor()
        >>> with monitor.measure("context_assembly"):
        ...     assemble_context(components)
        >>> monitor.print_summary()
    """

    def __init__(
        self,
        window_size: int = 100,
        track_memory: bool = False,
        auto_save: bool = False,
    ):
        """
        Initialize performance monitor.

        Args:
            window_size: Number of recent metrics to keep in memory
            track_memory: Whether to track memory usage (slower)
            auto_save: Automatically save metrics to file
        """
        self.metrics: List[PerformanceMetrics] = []
        self.window_size = window_size
        self.track_memory = track_memory
        self.auto_save = auto_save

        # Rolling window for recent metrics
        self.recent_metrics: deque = deque(maxlen=window_size)

        # Operation-specific statistics
        self.operation_stats: Dict[str, List[float]] = {}

        # Memory tracking (if enabled)
        if track_memory:
            import psutil

            self.process = psutil.Process()
        else:
            self.process = None

        # Thresholds for anomaly detection
        self.latency_thresholds: Dict[str, float] = {}
        self.quality_thresholds: Dict[str, float] = {}

    def measure(self, operation_name: str, tokens: int = 0, **metadata):
        """
        Context manager for measuring operation performance.

        Args:
            operation_name: Name of the operation
            tokens: Number of tokens processed
            **metadata: Additional metadata to track

        Returns:
            Context manager for measurement

        Example:
            >>> with monitor.measure("llm_call", tokens=100):
            ...     response = llm.generate(prompt)
        """
        return PerformanceMeasurement(
            self, operation_name, tokens, metadata
        )

    def record(
        self,
        operation_name: str,
        duration_ms: float,
        tokens: int = 0,
        quality_score: Optional[float] = None,
        **metadata,
    ) -> PerformanceMetrics:
        """
        Manually record a performance metric.

        Args:
            operation_name: Name of the operation
            duration_ms: Duration in milliseconds
            tokens: Number of tokens processed
            quality_score: Optional quality score (0-1)
            **metadata: Additional custom metrics

        Returns:
            The recorded PerformanceMetrics object
        """
        metric = PerformanceMetrics(
            operation_name=operation_name,
            timestamp=time.time(),
            duration_ms=duration_ms,
            tokens_processed=tokens,
            quality_score=quality_score,
            metadata=metadata,
        )

        # Add to collections
        self.metrics.append(metric)
        self.recent_metrics.append(metric)

        # Update operation statistics
        if operation_name not in self.operation_stats:
            self.operation_stats[operation_name] = []
        self.operation_stats[operation_name].append(duration_ms)

        # Auto-save if enabled
        if self.auto_save:
            self._auto_save_metrics()

        return metric

    def _auto_save_metrics(self):
        """Automatically save metrics to file."""
        if len(self.metrics) % 10 == 0:  # Save every 10 metrics
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_metrics_{timestamp}.json"
            self.save_metrics(filename)

    def get_statistics(self, operation_name: Optional[str] = None) -> Dict:
        """
        Get statistical summary of performance metrics.

        Args:
            operation_name: Optional filter by operation name

        Returns:
            Dictionary of statistics

        Example:
            >>> stats = monitor.get_statistics("llm_call")
            >>> print(f"Average: {stats['mean_ms']:.2f}ms")
        """
        # Filter metrics
        if operation_name:
            durations = self.operation_stats.get(operation_name, [])
            if not durations:
                return {"error": f"No data for operation: {operation_name}"}
        else:
            durations = [m.duration_ms for m in self.metrics]

        if not durations:
            return {"error": "No metrics recorded"}

        # Calculate statistics
        stats = {
            "count": len(durations),
            "mean_ms": statistics.mean(durations),
            "median_ms": statistics.median(durations),
            "min_ms": min(durations),
            "max_ms": max(durations),
            "total_time_ms": sum(durations),
        }

        # Add standard deviation if enough data
        if len(durations) >= 2:
            stats["stdev_ms"] = statistics.stdev(durations)
            stats["variance_ms"] = statistics.variance(durations)

        # Add percentiles
        if len(durations) >= 4:
            sorted_durations = sorted(durations)
            stats["p50_ms"] = statistics.median(sorted_durations)
            stats["p95_ms"] = sorted_durations[int(len(sorted_durations) * 0.95)]
            stats["p99_ms"] = sorted_durations[int(len(sorted_durations) * 0.99)]

        return stats

    def get_throughput_stats(self, operation_name: Optional[str] = None) -> Dict:
        """
        Get throughput statistics (tokens per second).

        Args:
            operation_name: Optional filter by operation name

        Returns:
            Dictionary of throughput statistics
        """
        # Filter metrics with tokens
        if operation_name:
            metrics = [m for m in self.metrics if m.operation_name == operation_name]
        else:
            metrics = self.metrics

        token_metrics = [m for m in metrics if m.tokens_processed > 0]

        if not token_metrics:
            return {"error": "No token processing metrics available"}

        throughputs = [m.tokens_per_second for m in token_metrics]

        return {
            "count": len(throughputs),
            "mean_tokens_per_sec": statistics.mean(throughputs),
            "median_tokens_per_sec": statistics.median(throughputs),
            "min_tokens_per_sec": min(throughputs),
            "max_tokens_per_sec": max(throughputs),
            "total_tokens": sum(m.tokens_processed for m in token_metrics),
        }

    def detect_anomalies(
        self, operation_name: str, threshold_multiplier: float = 3.0
    ) -> List[PerformanceMetrics]:
        """
        Detect performance anomalies using statistical methods.

        Uses standard deviation to identify outliers.

        Args:
            operation_name: Operation to analyze
            threshold_multiplier: Number of std devs for anomaly threshold

        Returns:
            List of anomalous metrics

        Example:
            >>> anomalies = monitor.detect_anomalies("llm_call", threshold=2.5)
            >>> if anomalies:
            ...     print(f"Found {len(anomalies)} anomalies!")
        """
        stats = self.get_statistics(operation_name)

        if "error" in stats or "stdev_ms" not in stats:
            return []

        mean = stats["mean_ms"]
        stdev = stats["stdev_ms"]
        threshold = mean + (threshold_multiplier * stdev)

        # Find anomalies
        anomalies = [
            m
            for m in self.metrics
            if m.operation_name == operation_name and m.duration_ms > threshold
        ]

        return anomalies

    def set_latency_threshold(self, operation_name: str, threshold_ms: float):
        """
        Set latency threshold for monitoring.

        Args:
            operation_name: Operation to monitor
            threshold_ms: Maximum acceptable latency in milliseconds
        """
        self.latency_thresholds[operation_name] = threshold_ms

    def set_quality_threshold(self, operation_name: str, threshold: float):
        """
        Set quality threshold for monitoring.

        Args:
            operation_name: Operation to monitor
            threshold: Minimum acceptable quality (0-1)
        """
        self.quality_thresholds[operation_name] = threshold

    def check_thresholds(self) -> List[Dict]:
        """
        Check if recent metrics violate thresholds.

        Returns:
            List of threshold violations

        Example:
            >>> violations = monitor.check_thresholds()
            >>> for v in violations:
            ...     print(f"⚠️  {v['message']}")
        """
        violations = []

        for metric in self.recent_metrics:
            # Check latency threshold
            if metric.operation_name in self.latency_thresholds:
                threshold = self.latency_thresholds[metric.operation_name]
                if metric.duration_ms > threshold:
                    violations.append(
                        {
                            "type": "latency",
                            "operation": metric.operation_name,
                            "value": metric.duration_ms,
                            "threshold": threshold,
                            "message": f"Latency violation: {metric.operation_name} "
                            f"took {metric.duration_ms:.2f}ms "
                            f"(threshold: {threshold:.2f}ms)",
                        }
                    )

            # Check quality threshold
            if (
                metric.quality_score is not None
                and metric.operation_name in self.quality_thresholds
            ):
                threshold = self.quality_thresholds[metric.operation_name]
                if metric.quality_score < threshold:
                    violations.append(
                        {
                            "type": "quality",
                            "operation": metric.operation_name,
                            "value": metric.quality_score,
                            "threshold": threshold,
                            "message": f"Quality violation: {metric.operation_name} "
                            f"quality {metric.quality_score:.3f} "
                            f"below threshold {threshold:.3f}",
                        }
                    )

        return violations

    def print_summary(self, operation_name: Optional[str] = None):
        """
        Print formatted performance summary.

        Args:
            operation_name: Optional filter by operation name
        """
        print("\n" + "=" * 70)
        print("PERFORMANCE MONITORING SUMMARY")
        print("=" * 70)

        if operation_name:
            print(f"\nOperation: {operation_name}")
            stats = self.get_statistics(operation_name)
        else:
            print("\nAll Operations")
            stats = self.get_statistics()

        if "error" in stats:
            print(f"Error: {stats['error']}")
            return

        print(f"\nLatency Statistics:")
        print(f"  Count: {stats['count']}")
        print(f"  Mean: {stats['mean_ms']:.2f}ms")
        print(f"  Median: {stats['median_ms']:.2f}ms")
        print(f"  Min: {stats['min_ms']:.2f}ms")
        print(f"  Max: {stats['max_ms']:.2f}ms")

        if "stdev_ms" in stats:
            print(f"  Std Dev: {stats['stdev_ms']:.2f}ms")

        if "p95_ms" in stats:
            print(f"  P95: {stats['p95_ms']:.2f}ms")
            print(f"  P99: {stats['p99_ms']:.2f}ms")

        # Throughput stats
        throughput = self.get_throughput_stats(operation_name)
        if "error" not in throughput:
            print(f"\nThroughput Statistics:")
            print(f"  Total Tokens: {throughput['total_tokens']:,}")
            print(f"  Mean: {throughput['mean_tokens_per_sec']:.2f} tokens/sec")
            print(
                f"  Median: {throughput['median_tokens_per_sec']:.2f} tokens/sec"
            )

        # Check for violations
        violations = self.check_thresholds()
        if violations:
            print(f"\n⚠️  Threshold Violations: {len(violations)}")
            for v in violations[:5]:  # Show first 5
                print(f"  • {v['message']}")

        print("=" * 70)

    def plot_metrics(
        self,
        operation_name: Optional[str] = None,
        save_path: Optional[str] = None,
        show: bool = True,
    ):
        """
        Plot performance metrics over time.

        Args:
            operation_name: Optional filter by operation name
            save_path: Optional path to save plot
            show: Whether to display the plot
        """
        # Filter metrics
        if operation_name:
            metrics = [m for m in self.metrics if m.operation_name == operation_name]
        else:
            metrics = self.metrics

        if not metrics:
            print("No metrics to plot")
            return

        # Prepare data
        times = [m.timestamp - metrics[0].timestamp for m in metrics]
        durations = [m.duration_ms for m in metrics]
        throughputs = [
            m.tokens_per_second if m.tokens_per_second > 0 else None for m in metrics
        ]

        # Create figure with subplots
        fig, axes = plt.subplots(2, 1, figsize=(12, 8))

        # Plot 1: Latency over time
        axes[0].plot(times, durations, "b-", alpha=0.6, label="Latency")
        axes[0].axhline(
            y=statistics.mean(durations), color="r", linestyle="--", label="Mean"
        )
        axes[0].set_xlabel("Time (seconds)")
        axes[0].set_ylabel("Latency (ms)")
        axes[0].set_title(
            f"Latency Over Time{f': {operation_name}' if operation_name else ''}"
        )
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)

        # Plot 2: Throughput over time (if available)
        valid_throughputs = [t for t in throughputs if t is not None and t > 0]
        if valid_throughputs:
            axes[1].plot(
                [times[i] for i, t in enumerate(throughputs) if t],
                valid_throughputs,
                "g-",
                alpha=0.6,
            )
            axes[1].set_xlabel("Time (seconds)")
            axes[1].set_ylabel("Throughput (tokens/sec)")
            axes[1].set_title("Throughput Over Time")
            axes[1].grid(True, alpha=0.3)
        else:
            axes[1].text(
                0.5,
                0.5,
                "No throughput data available",
                ha="center",
                va="center",
                transform=axes[1].transAxes,
            )

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Plot saved to: {save_path}")

        if show:
            plt.show()
        else:
            plt.close()

    def plot_comparison(
        self, operation_names: List[str], save_path: Optional[str] = None
    ):
        """
        Plot comparison of multiple operations.

        Args:
            operation_names: List of operations to compare
            save_path: Optional path to save plot
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Collect statistics for each operation
        means = []
        medians = []
        p95s = []

        for op_name in operation_names:
            stats = self.get_statistics(op_name)
            if "error" not in stats:
                means.append(stats["mean_ms"])
                medians.append(stats["median_ms"])
                p95s.append(stats.get("p95_ms", stats["max_ms"]))

        if not means:
            print("No data to plot")
            return

        # Plot 1: Bar chart of latencies
        x = range(len(operation_names))
        width = 0.25

        ax1.bar([i - width for i in x], means, width, label="Mean", alpha=0.8)
        ax1.bar(x, medians, width, label="Median", alpha=0.8)
        ax1.bar([i + width for i in x], p95s, width, label="P95", alpha=0.8)

        ax1.set_xlabel("Operation")
        ax1.set_ylabel("Latency (ms)")
        ax1.set_title("Operation Latency Comparison")
        ax1.set_xticks(x)
        ax1.set_xticklabels(operation_names, rotation=45, ha="right")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot 2: Throughput comparison
        throughputs = []
        for op_name in operation_names:
            tp_stats = self.get_throughput_stats(op_name)
            if "error" not in tp_stats:
                throughputs.append(tp_stats["mean_tokens_per_sec"])
            else:
                throughputs.append(0)

        if sum(throughputs) > 0:
            ax2.bar(operation_names, throughputs, alpha=0.8, color="green")
            ax2.set_xlabel("Operation")
            ax2.set_ylabel("Throughput (tokens/sec)")
            ax2.set_title("Operation Throughput Comparison")
            ax2.tick_params(axis="x", rotation=45)
            ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Comparison plot saved to: {save_path}")

        plt.show()

    def save_metrics(self, filepath: str):
        """
        Save metrics to JSON file.

        Args:
            filepath: Path to save metrics
        """
        data = {
            "summary": {
                "total_operations": len(self.metrics),
                "unique_operations": len(self.operation_stats),
                "timestamp": datetime.now().isoformat(),
            },
            "statistics": {
                op_name: self.get_statistics(op_name)
                for op_name in self.operation_stats.keys()
            },
            "metrics": [m.to_dict() for m in self.metrics],
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        print(f"Metrics saved to: {filepath}")

    def reset(self):
        """Reset all metrics and statistics."""
        self.metrics.clear()
        self.recent_metrics.clear()
        self.operation_stats.clear()
        print("Monitor reset complete")


class PerformanceMeasurement:
    """Context manager for measuring operation performance."""

    def __init__(
        self, monitor: PerformanceMonitor, operation_name: str, tokens: int, metadata: Dict
    ):
        self.monitor = monitor
        self.operation_name = operation_name
        self.tokens = tokens
        self.metadata = metadata
        self.start_time = None
        self.start_memory = None

    def __enter__(self):
        """Start measurement."""
        self.start_time = time.time()

        if self.monitor.track_memory and self.monitor.process:
            mem_info = self.monitor.process.memory_info()
            self.start_memory = mem_info.rss / 1024 / 1024  # MB

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End measurement and record."""
        duration_ms = (time.time() - self.start_time) * 1000

        memory_delta = 0.0
        if self.start_memory and self.monitor.process:
            mem_info = self.monitor.process.memory_info()
            current_memory = mem_info.rss / 1024 / 1024
            memory_delta = current_memory - self.start_memory

        self.monitor.record(
            operation_name=self.operation_name,
            duration_ms=duration_ms,
            tokens=self.tokens,
            **self.metadata,
        )


# ============================================================================
# Example Usage
# ============================================================================

def example_performance_monitoring():
    """Comprehensive example of performance monitoring."""
    print("Performance Monitor Example")
    print("=" * 70)

    # Create monitor
    monitor = PerformanceMonitor(window_size=50)

    # Set thresholds
    monitor.set_latency_threshold("context_assembly", 100.0)  # 100ms max
    monitor.set_quality_threshold("context_assembly", 0.8)  # 80% min quality

    # Simulate operations
    print("\nSimulating context engineering operations...")

    for i in range(20):
        # Simulate context assembly
        with monitor.measure("context_assembly", tokens=500):
            time.sleep(0.02 + (i * 0.002))  # Gradually increasing latency

        # Simulate LLM call
        with monitor.measure("llm_call", tokens=1000):
            time.sleep(0.05 + (i * 0.001))

        # Simulate retrieval
        with monitor.measure("vector_search", tokens=0):
            time.sleep(0.01)

    # Print summary
    monitor.print_summary()

    # Print operation-specific stats
    print("\n" + "=" * 70)
    print("Operation-Specific Statistics")
    print("=" * 70)

    for op_name in ["context_assembly", "llm_call", "vector_search"]:
        print(f"\n{op_name}:")
        stats = monitor.get_statistics(op_name)
        print(f"  Mean: {stats['mean_ms']:.2f}ms")
        print(f"  P95: {stats.get('p95_ms', 0):.2f}ms")

    # Detect anomalies
    print("\n" + "=" * 70)
    print("Anomaly Detection")
    print("=" * 70)

    for op_name in ["context_assembly", "llm_call"]:
        anomalies = monitor.detect_anomalies(op_name, threshold_multiplier=2.0)
        if anomalies:
            print(f"\n{op_name}: {len(anomalies)} anomalies detected")
            for a in anomalies[:3]:
                print(f"  • {a.duration_ms:.2f}ms")

    # Plot metrics
    monitor.plot_metrics("context_assembly", save_path="performance_plot.png", show=False)
    monitor.plot_comparison(
        ["context_assembly", "llm_call", "vector_search"],
        save_path="performance_comparison.png",
    )

    # Save metrics
    monitor.save_metrics("performance_metrics.json")


if __name__ == "__main__":
    print("Context Engineering - Performance Monitor")
    print("=" * 70)
    print("Real-time performance monitoring and analysis")
    print("=" * 70)
    print()

    example_performance_monitoring()

    print("\n" + "=" * 70)
    print("Performance monitoring complete!")
    print("Check performance_metrics.json and generated plots for details.")
    print("=" * 70)
