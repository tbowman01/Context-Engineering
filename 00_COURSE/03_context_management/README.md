# Module 03: Context Management

![Module Status](https://img.shields.io/badge/Status-85%25%20Complete-yellow)
![Tools](https://img.shields.io/badge/Tools-3%2F3%20✓-success)
![Architectures](https://img.shields.io/badge/Architectures-2%2F2%20✓-success)
![Labs](https://img.shields.io/badge/Labs-0%2F3%20Pending-orange)

## Overview

Context management is the systematic approach to handling, organizing, and optimizing context windows for large language models. This module covers the critical tools and architectures needed for effective context engineering.

## Module Contents

### Tools (100% Complete)

Production-ready tools for context management and optimization:

1. **memory_profiler.py** ✅
   - Comprehensive memory tracking for context systems
   - RSS/VMS memory monitoring
   - Memory leak detection
   - Baseline comparison and profiling
   - Visualization with matplotlib
   - **Lines:** 600+

2. **compression_analyzer.py** ✅
   - Multi-algorithm compression analysis
   - Supports gzip, bz2, lzma, zlib
   - Compression ratio and speed benchmarking
   - Semantic preservation scoring
   - Method recommendation engine
   - **Lines:** 550+

3. **performance_monitor.py** ✅
   - Real-time performance tracking
   - Latency and throughput measurement
   - Statistical analysis (mean, median, P95, P99)
   - Anomaly detection
   - Threshold violation checking
   - Time-series visualization
   - **Lines:** 600+

**Total Tools:** ~1,750 lines of production code

### Architectures (100% Complete)

Advanced architectural patterns for context engineering:

1. **hierarchical_memory.py** ✅
   - Multi-level memory system
   - Working Memory (7-item capacity, Miller's Law)
   - Episodic Memory (events with temporal context)
   - Semantic Memory (structured facts and knowledge)
   - Procedural Memory (step-by-step procedures)
   - Automatic relevance scoring
   - Context retrieval across memory levels
   - **Lines:** 700+

2. **adaptive_compression.py** ✅
   - Intelligent compression strategy selection
   - 6 compression strategies (whitespace, abbreviation, deduplication, summarization, semantic, pruning)
   - 5 compression levels (none to maximum)
   - Quality estimation and constraint satisfaction
   - Iterative compression
   - Adaptive learning from results
   - **Lines:** 950+

**Total Architectures:** ~1,650 lines of production code

### Labs (Pending)

Interactive notebooks for hands-on learning:

- [ ] **memory_management_lab.ipynb** - Convert from .py
- [ ] **compression_lab.ipynb** - New lab needed
- [ ] **optimization_lab.ipynb** - New lab needed

## Key Concepts

### Memory Management

Understanding how to manage context across multiple interactions:

- **Working Memory:** Immediate, active context (limited capacity)
- **Episodic Memory:** Specific events and conversations
- **Semantic Memory:** Persistent knowledge and facts
- **Procedural Memory:** How-to knowledge and workflows

### Compression Strategies

Techniques for reducing context size while preserving meaning:

- **Lossless:** Whitespace removal, abbreviations
- **Semantic Preservation:** Careful rephrasing and deduplication
- **Lossy:** Summarization, pruning, aggressive compression
- **Adaptive:** Dynamic strategy selection based on constraints

### Performance Optimization

Monitoring and optimizing context operations:

- **Latency Tracking:** Measure operation speed
- **Throughput Analysis:** Tokens processed per second
- **Anomaly Detection:** Identify performance outliers
- **Threshold Management:** Define and enforce SLAs

## Usage Examples

### Memory Profiling

```python
from tools.memory_profiler import MemoryProfiler

with MemoryProfiler() as profiler:
    profiler.record("start")

    # Your context-heavy operation
    context = build_large_context()

    profiler.record("after_build")

    # Check for leaks
    if profiler.detect_memory_leak():
        print("Warning: Memory leak detected!")

    profiler.plot_memory_usage()
```

### Hierarchical Memory

```python
from architectures.hierarchical_memory import HierarchicalMemory

memory = HierarchicalMemory(working_capacity=7)

# Add to working memory
memory.add_to_working("User asked about Python", importance=0.8)

# Consolidate to long-term
memory.consolidate_to_episodic()

# Add facts
memory.add_fact("python_features", "Decorators modify functions", 0.9)

# Retrieve context for query
context = memory.get_context_for_query("How do decorators work?")
```

### Adaptive Compression

```python
from architectures.adaptive_compression import (
    AdaptiveCompressor,
    CompressionConstraints
)

compressor = AdaptiveCompressor()

# Define constraints
constraints = CompressionConstraints(
    max_length=500,
    min_quality=0.8,
    allow_lossy=True
)

# Compress
compressed, metrics = compressor.compress(text, constraints)
print(f"Ratio: {metrics.compression_ratio:.2%}")
print(f"Quality: {metrics.quality_score:.2f}")
```

### Performance Monitoring

```python
from tools.performance_monitor import PerformanceMonitor

monitor = PerformanceMonitor()

# Method 1: Context manager
with monitor.measure("context_assembly", tokens=500):
    result = assemble_context(components)

# Get statistics
stats = monitor.get_statistics("context_assembly")
print(f"P95 latency: {stats['p95_ms']:.2f}ms")

# Check for anomalies
anomalies = monitor.detect_anomalies("context_assembly")
if anomalies:
    print(f"Found {len(anomalies)} performance anomalies")
```

## Module Progress

| Component | Files | Status | Lines | Tests |
|-----------|-------|--------|-------|-------|
| Tools | 3 | ✅ Complete | 1,750+ | Pending |
| Architectures | 2 | ✅ Complete | 1,650+ | Pending |
| Labs | 0/3 | ⏳ Pending | - | - |
| **Total** | **5** | **85%** | **3,400+** | **0%** |

## Integration with Examples

These Module 03 components are used in:

- **30_examples/01_simple_rag_assistant** - Context assembly and optimization
- **30_examples/02_memory_chatbot** (planned) - Hierarchical memory usage

## Prerequisites

- Python 3.10+
- psutil (for memory profiling)
- matplotlib (for visualization)
- Standard library modules (json, dataclasses, statistics)

## Installation

```bash
# Install core dependencies
pip install psutil matplotlib

# Or use project requirements
pip install -r requirements.txt
```

## Testing

```bash
# Run tool examples
python 00_COURSE/03_context_management/tools/memory_profiler.py
python 00_COURSE/03_context_management/tools/compression_analyzer.py
python 00_COURSE/03_context_management/tools/performance_monitor.py

# Run architecture examples
python 00_COURSE/03_context_management/architectures/hierarchical_memory.py
python 00_COURSE/03_context_management/architectures/adaptive_compression.py
```

## Next Steps

1. **Complete Labs** - Convert existing .py labs to Jupyter notebooks
2. **Add Tests** - Create unit tests for tools and architectures
3. **Documentation** - Add API documentation and tutorials
4. **Integration** - Build more examples using these components

## Related Modules

- **Module 01:** Mathematical Foundations (theory behind optimization)
- **Module 02:** Core Architectures (RAG, memory, tools, agents)
- **Module 04:** RAG Systems (practical application of context management)
- **Module 05:** Memory Systems (advanced memory architectures)

## Resources

- [Context Engineering Research Papers](../../10_research/)
- [Example Implementations](../../30_examples/)
- [Development Roadmap](../../DEVELOPMENT_GAP_ANALYSIS.md)

---

**Last Updated:** 2025-11-12
**Module Lead:** Context Engineering Contributors
**Status:** Production Ready (Tools & Architectures)
