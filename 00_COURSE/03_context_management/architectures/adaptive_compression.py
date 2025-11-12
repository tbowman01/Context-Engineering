"""
Adaptive Compression Architecture
===================================

Intelligent context compression system that adapts compression strategies
based on content characteristics, token budgets, and quality requirements.

This architecture demonstrates:
- Dynamic compression strategy selection
- Semantic-preserving compression
- Multi-level compression (syntactic, semantic, lossy)
- Adaptive quality-size tradeoffs
- Performance monitoring and optimization

Author: Context Engineering Contributors
License: MIT
"""

from typing import List, Dict, Optional, Tuple, Any, Callable
from dataclasses import dataclass
from enum import Enum
import time
import statistics


class CompressionLevel(Enum):
    """Compression aggressiveness levels."""
    NONE = "none"           # No compression
    LIGHT = "light"         # Minimal compression (whitespace, abbreviations)
    MODERATE = "moderate"   # Moderate compression (summarization, pruning)
    AGGRESSIVE = "aggressive"  # Aggressive compression (lossy, high summarization)
    MAXIMUM = "maximum"     # Maximum compression (extreme summarization)


class CompressionStrategy(Enum):
    """Available compression strategies."""
    WHITESPACE = "whitespace"           # Remove extra whitespace
    ABBREVIATION = "abbreviation"       # Use abbreviations
    DEDUPLICATION = "deduplication"     # Remove duplicate content
    SUMMARIZATION = "summarization"     # Extractive summarization
    SEMANTIC = "semantic"               # Semantic compression
    PRUNING = "pruning"                 # Remove low-value content
    HYBRID = "hybrid"                   # Combine multiple strategies


@dataclass
class CompressionMetrics:
    """Metrics for a compression operation."""

    original_length: int
    compressed_length: int
    compression_ratio: float
    time_ms: float
    strategy: str
    quality_score: float  # 0-1, estimated semantic preservation
    token_reduction: int

    def __post_init__(self):
        """Calculate derived metrics."""
        if self.compression_ratio == 0:
            self.compression_ratio = (
                self.compressed_length / self.original_length
                if self.original_length > 0 else 1.0
            )

        if self.token_reduction == 0:
            self.token_reduction = self.original_length - self.compressed_length


@dataclass
class CompressionConstraints:
    """Constraints for compression operations."""

    max_length: Optional[int] = None          # Maximum output length
    target_length: Optional[int] = None       # Target output length
    min_quality: float = 0.7                  # Minimum quality (0-1)
    max_time_ms: float = 1000.0               # Maximum compression time
    preserve_structure: bool = True           # Preserve document structure
    allow_lossy: bool = False                 # Allow lossy compression


class AdaptiveCompressor:
    """
    Adaptive compression system that selects optimal strategies
    based on content and constraints.

    Features:
    - Multiple compression strategies
    - Dynamic strategy selection
    - Quality monitoring
    - Performance tracking
    - Adaptive learning from results

    Example:
        >>> compressor = AdaptiveCompressor()
        >>>
        >>> constraints = CompressionConstraints(
        ...     target_length=500,
        ...     min_quality=0.8
        ... )
        >>>
        >>> result = compressor.compress(
        ...     text="Long document...",
        ...     constraints=constraints
        ... )
        >>>
        >>> print(f"Compressed: {result.original_length} -> {result.compressed_length}")
        >>> print(f"Quality: {result.quality_score:.2f}")
    """

    def __init__(
        self,
        default_level: CompressionLevel = CompressionLevel.MODERATE,
        enable_learning: bool = True
    ):
        """
        Initialize adaptive compressor.

        Args:
            default_level: Default compression level
            enable_learning: Enable adaptive learning from results
        """
        self.default_level = default_level
        self.enable_learning = enable_learning

        # Performance tracking
        self.metrics_history: List[CompressionMetrics] = []

        # Strategy effectiveness tracking (for learning)
        self.strategy_scores: Dict[str, List[float]] = {}

        # Compression functions registry
        self._strategies: Dict[CompressionStrategy, Callable] = {
            CompressionStrategy.WHITESPACE: self._compress_whitespace,
            CompressionStrategy.ABBREVIATION: self._compress_abbreviations,
            CompressionStrategy.DEDUPLICATION: self._compress_deduplicate,
            CompressionStrategy.SUMMARIZATION: self._compress_summarize,
            CompressionStrategy.SEMANTIC: self._compress_semantic,
            CompressionStrategy.PRUNING: self._compress_prune,
        }

    def compress(
        self,
        text: str,
        constraints: Optional[CompressionConstraints] = None,
        level: Optional[CompressionLevel] = None
    ) -> Tuple[str, CompressionMetrics]:
        """
        Adaptively compress text based on constraints.

        Args:
            text: Text to compress
            constraints: Compression constraints
            level: Compression level (overrides default)

        Returns:
            Tuple of (compressed_text, metrics)

        Example:
            >>> compressor = AdaptiveCompressor()
            >>> compressed, metrics = compressor.compress(
            ...     "This is a very long document that needs compression...",
            ...     constraints=CompressionConstraints(target_length=50)
            ... )
        """
        start_time = time.time()

        # Use defaults if not provided
        constraints = constraints or CompressionConstraints()
        level = level or self.default_level

        original_length = len(text)

        # Select compression strategy based on constraints and content
        strategy = self._select_strategy(text, constraints, level)

        # Apply compression
        compressed = self._apply_strategy(text, strategy, constraints)

        # Calculate metrics
        elapsed_ms = (time.time() - start_time) * 1000
        quality_score = self._estimate_quality(text, compressed, strategy)

        metrics = CompressionMetrics(
            original_length=original_length,
            compressed_length=len(compressed),
            compression_ratio=len(compressed) / original_length,
            time_ms=elapsed_ms,
            strategy=strategy.value,
            quality_score=quality_score,
            token_reduction=0  # Will be calculated in __post_init__
        )

        # Track metrics
        self.metrics_history.append(metrics)

        # Update strategy effectiveness (learning)
        if self.enable_learning:
            self._update_strategy_scores(strategy, quality_score, metrics.compression_ratio)

        return compressed, metrics

    def compress_iterative(
        self,
        text: str,
        constraints: CompressionConstraints,
        max_iterations: int = 5
    ) -> Tuple[str, List[CompressionMetrics]]:
        """
        Iteratively compress until constraints are met.

        Applies progressively more aggressive compression strategies
        until target length or quality constraints are satisfied.

        Args:
            text: Text to compress
            constraints: Compression constraints
            max_iterations: Maximum compression iterations

        Returns:
            Tuple of (final_text, metrics_list)

        Example:
            >>> result, metrics = compressor.compress_iterative(
            ...     long_text,
            ...     CompressionConstraints(max_length=100, min_quality=0.8)
            ... )
        """
        current_text = text
        all_metrics = []

        # Try increasing compression levels
        levels = [
            CompressionLevel.LIGHT,
            CompressionLevel.MODERATE,
            CompressionLevel.AGGRESSIVE,
            CompressionLevel.MAXIMUM
        ]

        for i, level in enumerate(levels):
            if i >= max_iterations:
                break

            # Apply compression
            compressed, metrics = self.compress(current_text, constraints, level)
            all_metrics.append(metrics)

            # Check if constraints are satisfied
            if self._check_constraints(compressed, constraints, metrics):
                return compressed, all_metrics

            current_text = compressed

        return current_text, all_metrics

    def _select_strategy(
        self,
        text: str,
        constraints: CompressionConstraints,
        level: CompressionLevel
    ) -> CompressionStrategy:
        """
        Select optimal compression strategy based on content and constraints.

        Uses heuristics and learned effectiveness scores.
        """
        text_length = len(text)

        # If learning is enabled, use performance history
        if self.enable_learning and self.strategy_scores:
            best_strategy = self._get_best_learned_strategy(constraints)
            if best_strategy:
                return best_strategy

        # Heuristic-based selection
        if level == CompressionLevel.NONE:
            return CompressionStrategy.WHITESPACE

        elif level == CompressionLevel.LIGHT:
            # Light compression: whitespace + abbreviations
            return CompressionStrategy.WHITESPACE

        elif level == CompressionLevel.MODERATE:
            # Moderate: add deduplication
            if text_length > 1000:
                return CompressionStrategy.DEDUPLICATION
            else:
                return CompressionStrategy.ABBREVIATION

        elif level == CompressionLevel.AGGRESSIVE:
            # Aggressive: summarization or semantic
            if constraints.allow_lossy:
                return CompressionStrategy.SUMMARIZATION
            else:
                return CompressionStrategy.SEMANTIC

        else:  # MAXIMUM
            # Maximum: aggressive pruning and summarization
            return CompressionStrategy.PRUNING

    def _apply_strategy(
        self,
        text: str,
        strategy: CompressionStrategy,
        constraints: CompressionConstraints
    ) -> str:
        """Apply selected compression strategy."""

        if strategy == CompressionStrategy.HYBRID:
            # Apply multiple strategies in sequence
            result = text
            result = self._compress_whitespace(result, constraints)
            result = self._compress_abbreviations(result, constraints)
            result = self._compress_deduplicate(result, constraints)
            return result

        # Apply single strategy
        compress_fn = self._strategies.get(strategy)
        if compress_fn:
            return compress_fn(text, constraints)

        return text

    def _compress_whitespace(
        self,
        text: str,
        constraints: CompressionConstraints
    ) -> str:
        """
        Remove extra whitespace.

        - Collapse multiple spaces to single space
        - Remove trailing whitespace
        - Normalize line breaks
        """
        import re

        # Collapse multiple spaces
        text = re.sub(r' +', ' ', text)

        # Collapse multiple newlines (keep structure if required)
        if constraints.preserve_structure:
            text = re.sub(r'\n\n+', '\n\n', text)
        else:
            text = re.sub(r'\n+', '\n', text)

        # Remove trailing whitespace
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)

        return text.strip()

    def _compress_abbreviations(
        self,
        text: str,
        constraints: CompressionConstraints
    ) -> str:
        """
        Apply common abbreviations.

        Replace common words with abbreviations while maintaining readability.
        """
        abbreviations = {
            'and': '&',
            'the': '',  # Remove articles for compression
            'that': '',
            'which': '',
            'is': "'s",
            'are': "'re",
            'would': "'d",
            'will': "'ll",
            'cannot': "can't",
            'should not': "shouldn't",
            'could not': "couldn't",
            'does not': "doesn't",
            'function': 'func',
            'parameter': 'param',
            'variable': 'var',
            'document': 'doc',
            'application': 'app',
            'configuration': 'config',
            'implementation': 'impl',
            'information': 'info',
            'maximum': 'max',
            'minimum': 'min',
            'number': 'num',
            'string': 'str',
            'integer': 'int',
        }

        result = text
        for word, abbrev in abbreviations.items():
            # Only replace whole words
            import re
            pattern = r'\b' + word + r'\b'
            if abbrev:
                result = re.sub(pattern, abbrev, result, flags=re.IGNORECASE)
            else:
                # Remove word but clean up extra spaces
                result = re.sub(pattern, '', result, flags=re.IGNORECASE)
                result = re.sub(r' +', ' ', result)

        return result.strip()

    def _compress_deduplicate(
        self,
        text: str,
        constraints: CompressionConstraints
    ) -> str:
        """
        Remove duplicate or near-duplicate sentences/paragraphs.

        Uses simple similarity to detect duplicates.
        """
        import re

        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        # Deduplicate using seen set
        seen = set()
        unique_sentences = []

        for sentence in sentences:
            # Normalize for comparison
            normalized = sentence.lower().strip()
            normalized = re.sub(r'\s+', ' ', normalized)

            if normalized not in seen:
                seen.add(normalized)
                unique_sentences.append(sentence)

        return '. '.join(unique_sentences) + '.'

    def _compress_summarize(
        self,
        text: str,
        constraints: CompressionConstraints
    ) -> str:
        """
        Extractive summarization.

        Extract most important sentences based on:
        - Position (first sentences are important)
        - Length (skip very short sentences)
        - Keywords presence
        """
        import re

        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return text

        # Calculate target number of sentences
        target_length = constraints.target_length or (len(text) // 2)
        target_sentences = max(1, len(sentences) // 3)  # Keep ~1/3

        # Score sentences
        scored_sentences = []
        for i, sentence in enumerate(sentences):
            score = 0.0

            # Position score (first and last are important)
            if i == 0:
                score += 1.0
            elif i == len(sentences) - 1:
                score += 0.5

            # Length score (prefer medium length)
            length = len(sentence)
            if 20 <= length <= 150:
                score += 0.5

            # Keyword score (contains important words)
            important_words = ['important', 'key', 'critical', 'essential',
                             'must', 'should', 'significant', 'main']
            for word in important_words:
                if word in sentence.lower():
                    score += 0.3

            scored_sentences.append((sentence, score))

        # Sort by score and take top sentences
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        top_sentences = [s for s, _ in scored_sentences[:target_sentences]]

        # Maintain original order
        ordered_sentences = []
        for sentence in sentences:
            if sentence in top_sentences:
                ordered_sentences.append(sentence)

        return '. '.join(ordered_sentences) + '.'

    def _compress_semantic(
        self,
        text: str,
        constraints: CompressionConstraints
    ) -> str:
        """
        Semantic compression.

        Rephrase to use fewer words while preserving meaning.
        This is a simplified version - production would use NLP models.
        """
        # Apply multiple lightweight transformations
        result = text

        # Remove filler phrases
        fillers = [
            'in order to', 'in the event that', 'due to the fact that',
            'at this point in time', 'for the purpose of', 'with regard to',
            'it should be noted that', 'it is important to note that',
        ]

        replacements = {
            'in order to': 'to',
            'in the event that': 'if',
            'due to the fact that': 'because',
            'at this point in time': 'now',
            'for the purpose of': 'to',
            'with regard to': 'about',
            'it should be noted that': '',
            'it is important to note that': '',
        }

        import re
        for phrase, replacement in replacements.items():
            result = re.sub(phrase, replacement, result, flags=re.IGNORECASE)

        # Clean up extra spaces
        result = re.sub(r' +', ' ', result)

        return result.strip()

    def _compress_prune(
        self,
        text: str,
        constraints: CompressionConstraints
    ) -> str:
        """
        Aggressive pruning of low-value content.

        Remove:
        - Examples (unless preserve_structure=True)
        - Redundant explanations
        - Parenthetical content
        - Qualifiers and hedges
        """
        import re

        result = text

        # Remove parenthetical content
        if not constraints.preserve_structure:
            result = re.sub(r'\([^)]*\)', '', result)

        # Remove common hedging phrases
        hedges = [
            'possibly', 'probably', 'maybe', 'perhaps',
            'it seems', 'it appears', 'might be',
            'kind of', 'sort of', 'somewhat'
        ]

        for hedge in hedges:
            result = re.sub(r'\b' + hedge + r'\b', '', result, flags=re.IGNORECASE)

        # Remove example markers
        result = re.sub(r'for example[,:]?', '', result, flags=re.IGNORECASE)
        result = re.sub(r'e\.g\.', '', result, flags=re.IGNORECASE)

        # Clean up
        result = re.sub(r' +', ' ', result)
        result = re.sub(r'\n\n+', '\n\n', result)

        return result.strip()

    def _estimate_quality(
        self,
        original: str,
        compressed: str,
        strategy: CompressionStrategy
    ) -> float:
        """
        Estimate semantic preservation quality.

        Uses simple heuristics. Production version would use
        embeddings or NLP models.

        Returns: Quality score 0-1
        """
        if not original or not compressed:
            return 0.0

        # Base score on compression ratio
        ratio = len(compressed) / len(original)

        # Different strategies have different quality baselines
        strategy_quality = {
            CompressionStrategy.WHITESPACE: 1.0,      # Perfect preservation
            CompressionStrategy.ABBREVIATION: 0.95,   # Minimal loss
            CompressionStrategy.DEDUPLICATION: 0.90,  # Removes redundancy
            CompressionStrategy.SUMMARIZATION: 0.70,  # Moderate loss
            CompressionStrategy.SEMANTIC: 0.85,       # Careful rephrasing
            CompressionStrategy.PRUNING: 0.60,        # Significant loss
        }

        base_quality = strategy_quality.get(strategy, 0.7)

        # Adjust based on compression ratio
        # More aggressive compression = lower quality
        if ratio > 0.8:
            quality_factor = 1.0
        elif ratio > 0.5:
            quality_factor = 0.9
        elif ratio > 0.3:
            quality_factor = 0.7
        else:
            quality_factor = 0.5

        return base_quality * quality_factor

    def _check_constraints(
        self,
        text: str,
        constraints: CompressionConstraints,
        metrics: CompressionMetrics
    ) -> bool:
        """Check if compression satisfies constraints."""

        # Check length constraints
        if constraints.max_length and len(text) > constraints.max_length:
            return False

        if constraints.target_length:
            # Allow 10% tolerance
            tolerance = constraints.target_length * 0.1
            if len(text) > constraints.target_length + tolerance:
                return False

        # Check quality constraint
        if metrics.quality_score < constraints.min_quality:
            return False

        # Check time constraint
        if metrics.time_ms > constraints.max_time_ms:
            return False

        return True

    def _update_strategy_scores(
        self,
        strategy: CompressionStrategy,
        quality: float,
        compression_ratio: float
    ):
        """Update strategy effectiveness scores for learning."""

        # Composite score: balance quality and compression
        effectiveness = (quality * 0.6) + ((1 - compression_ratio) * 0.4)

        if strategy.value not in self.strategy_scores:
            self.strategy_scores[strategy.value] = []

        self.strategy_scores[strategy.value].append(effectiveness)

        # Keep last 100 scores
        if len(self.strategy_scores[strategy.value]) > 100:
            self.strategy_scores[strategy.value] = (
                self.strategy_scores[strategy.value][-100:]
            )

    def _get_best_learned_strategy(
        self,
        constraints: CompressionConstraints
    ) -> Optional[CompressionStrategy]:
        """Get best strategy based on learning history."""

        if not self.strategy_scores:
            return None

        # Calculate average effectiveness for each strategy
        avg_scores = {}
        for strategy_name, scores in self.strategy_scores.items():
            if scores:
                avg_scores[strategy_name] = statistics.mean(scores)

        if not avg_scores:
            return None

        # Return strategy with highest average effectiveness
        best_strategy_name = max(avg_scores, key=avg_scores.get)

        for strategy in CompressionStrategy:
            if strategy.value == best_strategy_name:
                return strategy

        return None

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get compression statistics.

        Returns:
            Dictionary with statistics

        Example:
            >>> stats = compressor.get_statistics()
            >>> print(f"Average compression: {stats['avg_compression_ratio']:.2%}")
            >>> print(f"Average quality: {stats['avg_quality']:.2f}")
        """
        if not self.metrics_history:
            return {
                'total_compressions': 0,
                'avg_compression_ratio': 0.0,
                'avg_quality': 0.0,
                'avg_time_ms': 0.0,
            }

        ratios = [m.compression_ratio for m in self.metrics_history]
        qualities = [m.quality_score for m in self.metrics_history]
        times = [m.time_ms for m in self.metrics_history]

        return {
            'total_compressions': len(self.metrics_history),
            'avg_compression_ratio': statistics.mean(ratios),
            'avg_quality': statistics.mean(qualities),
            'avg_time_ms': statistics.mean(times),
            'best_compression_ratio': min(ratios),
            'best_quality': max(qualities),
        }

    def print_statistics(self):
        """Print compression statistics."""
        stats = self.get_statistics()

        print("=" * 60)
        print("ADAPTIVE COMPRESSION STATISTICS")
        print("=" * 60)
        print(f"Total compressions: {stats['total_compressions']}")
        print(f"Average compression ratio: {stats['avg_compression_ratio']:.2%}")
        print(f"Average quality score: {stats['avg_quality']:.2f}")
        print(f"Average time: {stats['avg_time_ms']:.2f}ms")

        if self.strategy_scores:
            print("\nStrategy Effectiveness:")
            for strategy, scores in self.strategy_scores.items():
                if scores:
                    avg = statistics.mean(scores)
                    print(f"  {strategy}: {avg:.3f}")

        print("=" * 60)


# ============================================================================
# Example Usage
# ============================================================================

def example_adaptive_compression():
    """Comprehensive example of adaptive compression."""
    print("Adaptive Compression Architecture Example")
    print("=" * 60)

    # Sample text to compress
    sample_text = """
    Context engineering is the delicate art and science of filling the context
    window with just the right information for the next step. It is important
    to note that this process goes beyond simple prompt engineering to encompass
    systematic approaches to context design, orchestration, and optimization.

    The mathematical foundation of context engineering includes four key pillars
    that are essential for understanding the field. These pillars are: context
    formalization, optimization theory, information theory, and Bayesian inference.
    It should be noted that each of these pillars contributes significantly to
    the overall framework.

    In order to effectively implement context engineering, practitioners must
    understand how to balance multiple competing objectives. For example, they
    need to consider relevance, completeness, efficiency, and coherence. It is
    perhaps worth noting that these considerations are critical for success.

    Context engineering is important for building effective LLM applications.
    This is because it allows developers to make optimal use of the context
    window resource. The context window is a limited resource that must be
    used wisely. Therefore, every token must earn its place in the context.
    """

    print(f"\nOriginal text length: {len(sample_text)} characters")
    print(f"Original text preview: {sample_text[:200]}...")

    # Create compressor
    compressor = AdaptiveCompressor(enable_learning=True)

    # Example 1: Light compression
    print("\n" + "=" * 60)
    print("Example 1: Light Compression")
    print("-" * 60)

    constraints = CompressionConstraints(
        min_quality=0.95,
        preserve_structure=True
    )

    compressed, metrics = compressor.compress(
        sample_text,
        constraints=constraints,
        level=CompressionLevel.LIGHT
    )

    print(f"Strategy: {metrics.strategy}")
    print(f"Compressed length: {metrics.compressed_length} chars")
    print(f"Compression ratio: {metrics.compression_ratio:.2%}")
    print(f"Quality score: {metrics.quality_score:.2f}")
    print(f"Time: {metrics.time_ms:.2f}ms")
    print(f"\nCompressed preview: {compressed[:200]}...")

    # Example 2: Moderate compression
    print("\n" + "=" * 60)
    print("Example 2: Moderate Compression")
    print("-" * 60)

    constraints = CompressionConstraints(
        target_length=len(sample_text) // 2,
        min_quality=0.8
    )

    compressed, metrics = compressor.compress(
        sample_text,
        constraints=constraints,
        level=CompressionLevel.MODERATE
    )

    print(f"Strategy: {metrics.strategy}")
    print(f"Compressed length: {metrics.compressed_length} chars")
    print(f"Compression ratio: {metrics.compression_ratio:.2%}")
    print(f"Quality score: {metrics.quality_score:.2f}")
    print(f"Time: {metrics.time_ms:.2f}ms")
    print(f"\nCompressed preview: {compressed[:200]}...")

    # Example 3: Aggressive compression
    print("\n" + "=" * 60)
    print("Example 3: Aggressive Compression")
    print("-" * 60)

    constraints = CompressionConstraints(
        max_length=300,
        min_quality=0.7,
        allow_lossy=True
    )

    compressed, metrics = compressor.compress(
        sample_text,
        constraints=constraints,
        level=CompressionLevel.AGGRESSIVE
    )

    print(f"Strategy: {metrics.strategy}")
    print(f"Compressed length: {metrics.compressed_length} chars")
    print(f"Compression ratio: {metrics.compression_ratio:.2%}")
    print(f"Quality score: {metrics.quality_score:.2f}")
    print(f"Time: {metrics.time_ms:.2f}ms")
    print(f"\nCompressed text: {compressed}")

    # Example 4: Iterative compression
    print("\n" + "=" * 60)
    print("Example 4: Iterative Compression")
    print("-" * 60)

    constraints = CompressionConstraints(
        max_length=200,
        min_quality=0.6,
        allow_lossy=True
    )

    compressed, metrics_list = compressor.compress_iterative(
        sample_text,
        constraints=constraints,
        max_iterations=4
    )

    print(f"Iterations: {len(metrics_list)}")
    print(f"Final length: {len(compressed)} chars")
    print(f"\nIteration details:")
    for i, metrics in enumerate(metrics_list, 1):
        print(f"  {i}. {metrics.strategy}: "
              f"{metrics.compressed_length} chars "
              f"(ratio: {metrics.compression_ratio:.2%}, "
              f"quality: {metrics.quality_score:.2f})")

    print(f"\nFinal compressed text: {compressed}")

    # Print overall statistics
    print("\n" + "=" * 60)
    compressor.print_statistics()

    print("\n" + "=" * 60)
    print("Adaptive compression example complete!")


if __name__ == "__main__":
    example_adaptive_compression()
