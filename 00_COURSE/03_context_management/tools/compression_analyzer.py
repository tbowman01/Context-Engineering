"""
Compression Analyzer for Context Engineering
=============================================

Analyzes different compression strategies for context management,
evaluating both size reduction and semantic preservation.

Author: Context Engineering Contributors
License: MIT
"""

import gzip
import bz2
import lzma
import zlib
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import json
from pathlib import Path


@dataclass
class CompressionResult:
    """
    Results from compression analysis.

    Attributes:
        method: Compression method name
        original_size: Original size in bytes
        compressed_size: Compressed size in bytes
        compression_ratio: Ratio of compression (compressed/original)
        space_savings: Percentage of space saved
        compression_time: Time taken to compress (seconds)
        decompression_time: Time taken to decompress (seconds)
        semantic_score: Semantic preservation score (0-1)
    """

    method: str
    original_size: int
    compressed_size: int
    compression_ratio: float
    space_savings: float
    compression_time: float
    decompression_time: float
    semantic_score: float = 1.0

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "method": self.method,
            "original_size_bytes": self.original_size,
            "compressed_size_bytes": self.compressed_size,
            "compression_ratio": round(self.compression_ratio, 3),
            "space_savings_percent": round(self.space_savings, 2),
            "compression_time_ms": round(self.compression_time * 1000, 2),
            "decompression_time_ms": round(self.decompression_time * 1000, 2),
            "semantic_preservation_score": round(self.semantic_score, 3),
        }


class CompressionAnalyzer:
    """
    Analyze and compare different compression strategies for context data.

    Supports multiple compression algorithms and provides detailed analysis
    of compression efficiency, speed, and semantic preservation.

    Example:
        >>> analyzer = CompressionAnalyzer()
        >>> text = "Your long context text here..."
        >>> results = analyzer.compare_methods(text)
        >>> analyzer.print_comparison(results)
    """

    def __init__(self):
        """Initialize compression analyzer."""
        self.supported_methods = [
            "gzip",
            "bz2",
            "lzma",
            "zlib",
            "summary",  # Extractive summarization
            "truncate",  # Simple truncation
        ]

    def compress_gzip(self, text: str, level: int = 9) -> Tuple[bytes, float, float]:
        """
        Compress using gzip.

        Args:
            text: Text to compress
            level: Compression level (1-9, higher = more compression)

        Returns:
            Tuple of (compressed_data, compression_time, decompression_time)
        """
        import time

        data = text.encode("utf-8")

        # Compress
        start = time.time()
        compressed = gzip.compress(data, compresslevel=level)
        compression_time = time.time() - start

        # Decompress (to measure time)
        start = time.time()
        _ = gzip.decompress(compressed)
        decompression_time = time.time() - start

        return compressed, compression_time, decompression_time

    def compress_bz2(self, text: str, level: int = 9) -> Tuple[bytes, float, float]:
        """
        Compress using bz2.

        Args:
            text: Text to compress
            level: Compression level (1-9)

        Returns:
            Tuple of (compressed_data, compression_time, decompression_time)
        """
        import time

        data = text.encode("utf-8")

        # Compress
        start = time.time()
        compressed = bz2.compress(data, compresslevel=level)
        compression_time = time.time() - start

        # Decompress
        start = time.time()
        _ = bz2.decompress(compressed)
        decompression_time = time.time() - start

        return compressed, compression_time, decompression_time

    def compress_lzma(self, text: str) -> Tuple[bytes, float, float]:
        """
        Compress using LZMA (highest compression, slowest).

        Args:
            text: Text to compress

        Returns:
            Tuple of (compressed_data, compression_time, decompression_time)
        """
        import time

        data = text.encode("utf-8")

        # Compress
        start = time.time()
        compressed = lzma.compress(data)
        compression_time = time.time() - start

        # Decompress
        start = time.time()
        _ = lzma.decompress(compressed)
        decompression_time = time.time() - start

        return compressed, compression_time, decompression_time

    def compress_zlib(self, text: str, level: int = 9) -> Tuple[bytes, float, float]:
        """
        Compress using zlib.

        Args:
            text: Text to compress
            level: Compression level (1-9)

        Returns:
            Tuple of (compressed_data, compression_time, decompression_time)
        """
        import time

        data = text.encode("utf-8")

        # Compress
        start = time.time()
        compressed = zlib.compress(data, level=level)
        compression_time = time.time() - start

        # Decompress
        start = time.time()
        _ = zlib.decompress(compressed)
        decompression_time = time.time() - start

        return compressed, compression_time, decompression_time

    def compress_summary(
        self, text: str, ratio: float = 0.3
    ) -> Tuple[str, float, float]:
        """
        Compress using extractive summarization.

        Simple implementation: keep first N% of sentences.

        Args:
            text: Text to compress
            ratio: Fraction of text to keep (0-1)

        Returns:
            Tuple of (compressed_text, compression_time, decompression_time)
        """
        import time

        start = time.time()

        # Split into sentences (simple approach)
        sentences = [s.strip() + "." for s in text.split(".") if s.strip()]

        # Keep first N% of sentences
        keep_count = max(1, int(len(sentences) * ratio))
        summary = " ".join(sentences[:keep_count])

        compression_time = time.time() - start
        decompression_time = 0.0  # No decompression needed

        return summary, compression_time, decompression_time

    def compress_truncate(self, text: str, max_chars: int = 1000) -> Tuple[str, float, float]:
        """
        Compress by simple truncation.

        Args:
            text: Text to compress
            max_chars: Maximum characters to keep

        Returns:
            Tuple of (truncated_text, compression_time, decompression_time)
        """
        import time

        start = time.time()
        truncated = text[:max_chars]
        if len(text) > max_chars:
            truncated += "..."
        compression_time = time.time() - start
        decompression_time = 0.0

        return truncated, compression_time, decompression_time

    def calculate_semantic_score(self, original: str, compressed: str) -> float:
        """
        Calculate semantic preservation score.

        Simple implementation using word overlap. More sophisticated
        implementations could use embeddings.

        Args:
            original: Original text
            compressed: Compressed text

        Returns:
            Score from 0 to 1 (1 = perfect preservation)
        """
        # Extract words
        original_words = set(original.lower().split())
        compressed_words = set(compressed.lower().split())

        if not original_words:
            return 0.0

        # Calculate Jaccard similarity
        intersection = len(original_words & compressed_words)
        union = len(original_words | compressed_words)

        if union == 0:
            return 0.0

        return intersection / union

    def analyze_compression(
        self, text: str, method: str, **kwargs
    ) -> CompressionResult:
        """
        Analyze single compression method.

        Args:
            text: Text to analyze
            method: Compression method name
            **kwargs: Additional parameters for compression method

        Returns:
            CompressionResult object
        """
        original_size = len(text.encode("utf-8"))

        # Apply compression
        if method == "gzip":
            compressed, comp_time, decomp_time = self.compress_gzip(text, **kwargs)
            compressed_size = len(compressed)
            semantic_score = 1.0  # Lossless
        elif method == "bz2":
            compressed, comp_time, decomp_time = self.compress_bz2(text, **kwargs)
            compressed_size = len(compressed)
            semantic_score = 1.0  # Lossless
        elif method == "lzma":
            compressed, comp_time, decomp_time = self.compress_lzma(text)
            compressed_size = len(compressed)
            semantic_score = 1.0  # Lossless
        elif method == "zlib":
            compressed, comp_time, decomp_time = self.compress_zlib(text, **kwargs)
            compressed_size = len(compressed)
            semantic_score = 1.0  # Lossless
        elif method == "summary":
            compressed, comp_time, decomp_time = self.compress_summary(text, **kwargs)
            compressed_size = len(compressed.encode("utf-8"))
            semantic_score = self.calculate_semantic_score(text, compressed)
        elif method == "truncate":
            compressed, comp_time, decomp_time = self.compress_truncate(text, **kwargs)
            compressed_size = len(compressed.encode("utf-8"))
            semantic_score = self.calculate_semantic_score(text, compressed)
        else:
            raise ValueError(f"Unknown compression method: {method}")

        # Calculate metrics
        compression_ratio = compressed_size / original_size if original_size > 0 else 0
        space_savings = (1 - compression_ratio) * 100

        return CompressionResult(
            method=method,
            original_size=original_size,
            compressed_size=compressed_size,
            compression_ratio=compression_ratio,
            space_savings=space_savings,
            compression_time=comp_time,
            decompression_time=decomp_time,
            semantic_score=semantic_score,
        )

    def compare_methods(
        self, text: str, methods: Optional[List[str]] = None
    ) -> Dict[str, CompressionResult]:
        """
        Compare multiple compression methods.

        Args:
            text: Text to compress
            methods: List of methods to compare (None = all)

        Returns:
            Dictionary mapping method names to results

        Example:
            >>> results = analyzer.compare_methods(text)
            >>> best = max(results.values(), key=lambda r: r.space_savings)
            >>> print(f"Best: {best.method} - {best.space_savings:.1f}% savings")
        """
        if methods is None:
            methods = ["gzip", "bz2", "lzma", "zlib"]

        results = {}

        for method in methods:
            try:
                result = self.analyze_compression(text, method)
                results[method] = result
            except Exception as e:
                print(f"Error with method {method}: {e}")

        return results

    def print_comparison(self, results: Dict[str, CompressionResult]) -> None:
        """
        Print formatted comparison table.

        Args:
            results: Dictionary of compression results
        """
        print("\n" + "=" * 80)
        print("COMPRESSION ANALYSIS RESULTS")
        print("=" * 80)

        # Header
        print(
            f"{'Method':<12} {'Original':<12} {'Compressed':<12} {'Ratio':<8} "
            f"{'Savings':<10} {'Time (ms)':<12}"
        )
        print("-" * 80)

        # Sort by compression ratio
        sorted_results = sorted(
            results.items(), key=lambda x: x[1].compression_ratio
        )

        for method, result in sorted_results:
            print(
                f"{method:<12} "
                f"{result.original_size:<12} "
                f"{result.compressed_size:<12} "
                f"{result.compression_ratio:<8.3f} "
                f"{result.space_savings:<10.1f}% "
                f"{result.compression_time*1000:<12.2f}"
            )

        print("=" * 80)

        # Recommendations
        best_ratio = min(results.values(), key=lambda r: r.compression_ratio)
        fastest = min(results.values(), key=lambda r: r.compression_time)

        print("\nRecommendations:")
        print(f"  Best compression: {best_ratio.method} ({best_ratio.space_savings:.1f}% savings)")
        print(f"  Fastest: {fastest.method} ({fastest.compression_time*1000:.2f}ms)")
        print()

    def recommend_method(
        self, text: str, priority: str = "balanced"
    ) -> Tuple[str, CompressionResult]:
        """
        Recommend best compression method based on priorities.

        Args:
            text: Text to analyze
            priority: One of 'speed', 'ratio', 'balanced'

        Returns:
            Tuple of (method_name, result)

        Example:
            >>> method, result = analyzer.recommend_method(text, priority='speed')
            >>> print(f"Recommended: {method}")
        """
        results = self.compare_methods(text)

        if priority == "speed":
            # Fastest compression
            method = min(results.items(), key=lambda x: x[1].compression_time)[0]
        elif priority == "ratio":
            # Best compression ratio
            method = min(results.items(), key=lambda x: x[1].compression_ratio)[0]
        elif priority == "balanced":
            # Balance between speed and ratio
            # Score = (normalized_time + normalized_ratio) / 2
            times = [r.compression_time for r in results.values()]
            ratios = [r.compression_ratio for r in results.values()]

            min_time, max_time = min(times), max(times)
            min_ratio, max_ratio = min(ratios), max(ratios)

            scores = {}
            for name, result in results.items():
                norm_time = (
                    (result.compression_time - min_time) / (max_time - min_time)
                    if max_time != min_time
                    else 0
                )
                norm_ratio = (
                    (result.compression_ratio - min_ratio) / (max_ratio - min_ratio)
                    if max_ratio != min_ratio
                    else 0
                )
                scores[name] = (norm_time + norm_ratio) / 2

            method = min(scores.items(), key=lambda x: x[1])[0]
        else:
            raise ValueError(f"Unknown priority: {priority}")

        return method, results[method]

    def save_report(
        self, results: Dict[str, CompressionResult], filepath: str
    ) -> None:
        """
        Save compression analysis report to JSON.

        Args:
            results: Compression results
            filepath: Path to save report
        """
        report = {
            "summary": {
                "num_methods_tested": len(results),
                "best_compression": min(
                    results.items(), key=lambda x: x[1].compression_ratio
                )[0],
                "fastest_method": min(
                    results.items(), key=lambda x: x[1].compression_time
                )[0],
            },
            "results": {name: result.to_dict() for name, result in results.items()},
        }

        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)

        print(f"Report saved to: {filepath}")


# ============================================================================
# Example Usage
# ============================================================================

def example_compression_analysis():
    """Comprehensive example of compression analysis."""
    print("Compression Analyzer Example")
    print("=" * 80)

    # Sample text (simulating context)
    sample_text = """
    Context engineering is the delicate art and science of filling the context
    window with just the right information for the next step. It encompasses
    systematic approaches to context design, orchestration, and optimization.

    The mathematical foundation includes context formalization (C = A(c₁, c₂, ..., c₆)),
    optimization theory (F* = arg max E[Reward(C)]), information theory
    (I(Context; Query)), and Bayesian inference (P(Strategy|Evidence)).

    Practical applications include retrieval-augmented generation (RAG),
    memory systems, tool-integrated reasoning, and multi-agent coordination.
    Field theory approaches model context as continuous fields with attractors,
    resonance, and emergent behaviors.
    """ * 10  # Repeat for meaningful compression

    print(f"Original text size: {len(sample_text)} characters")
    print(f"Original size: {len(sample_text.encode('utf-8'))} bytes\n")

    # Create analyzer
    analyzer = CompressionAnalyzer()

    # Compare all methods
    print("Comparing compression methods...")
    results = analyzer.compare_methods(sample_text)

    # Print comparison
    analyzer.print_comparison(results)

    # Get recommendations
    print("\nMethod Recommendations by Priority:")
    for priority in ["speed", "ratio", "balanced"]:
        method, result = analyzer.recommend_method(sample_text, priority=priority)
        print(f"  {priority.title()}: {method} ({result.space_savings:.1f}% savings)")

    # Save report
    analyzer.save_report(results, "compression_analysis_report.json")


if __name__ == "__main__":
    print("Context Engineering - Compression Analyzer")
    print("=" * 80)
    print("Analyze and optimize compression strategies for context management")
    print("=" * 80)
    print()

    example_compression_analysis()

    print("\n" + "=" * 80)
    print("Compression analysis complete!")
    print("=" * 80)
