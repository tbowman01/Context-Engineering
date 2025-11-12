#!/usr/bin/env python3
"""
Simple RAG Assistant - Main Entry Point
========================================

Interactive RAG (Retrieval-Augmented Generation) assistant demonstrating
context engineering principles in practice.

Usage:
    python main.py                    # Interactive mode with sample data
    python main.py --docs file.txt    # Load custom documents
    python main.py --help             # Show help

Author: Context Engineering Contributors
License: MIT
"""

import argparse
import sys
from pathlib import Path

from src.rag_assistant import RAGAssistant
from src.context_assembler import AssemblyStrategy


def load_sample_data() -> str:
    """Load sample data if available."""
    sample_file = Path("data/sample_docs.txt")

    if sample_file.exists():
        with open(sample_file, 'r', encoding='utf-8') as f:
            return f.read()

    # Return embedded sample data if file doesn't exist
    return """
    Context Engineering: A Comprehensive Introduction

    What is Context Engineering?

    Context engineering is the delicate art and science of filling the context
    window with just the right information for the next step. It encompasses
    systematic approaches to context design, orchestration, and optimization
    for large language models.

    Unlike simple prompt engineering, which focuses on crafting individual prompts,
    context engineering takes a holistic view of the entire context window as a
    programmable, optimizable resource.

    Mathematical Foundations

    The field rests on four mathematical pillars:

    1. Context Formalization
       Representing context as: C = A(c₁, c₂, ..., c₆)
       Where components include:
       - c₁: Base instructions and system prompts
       - c₂: Retrieved facts and knowledge
       - c₃: Conversation history
       - c₄: Tool call results
       - c₅: Reasoning traces
       - c₆: Meta-context and guidelines

    2. Optimization Theory
       Finding optimal context strategies:
       F* = arg max E[Reward(C)]
       Subject to constraints:
       - Token limits: |C| ≤ max_tokens
       - Latency requirements: T(C) ≤ max_time
       - Cost constraints: Cost(C) ≤ budget

    3. Information Theory
       Measuring context efficiency:
       I(Context; Query) - mutual information between context and query
       H(Context) - entropy of context distribution
       Optimizing information density within token limits

    4. Bayesian Inference
       Updating strategies based on evidence:
       P(Strategy|Evidence) ∝ P(Evidence|Strategy) × P(Strategy)
       Continuously improving context design through feedback

    Practical Applications

    RAG Systems
    Retrieval-Augmented Generation combines vector search with generation:
    - Embed documents in vector space
    - Retrieve relevant chunks for queries
    - Assemble optimal context windows
    - Generate informed responses

    Memory Systems
    Hierarchical memory structures:
    - Working Memory: Limited capacity, fast access (7 items)
    - Episodic Memory: Specific events with temporal context
    - Semantic Memory: Structured facts and knowledge
    - Procedural Memory: Step-by-step processes

    Tool Integration
    Orchestrating tool calls within context:
    - Planning tool sequences
    - Maintaining tool call history
    - Reasoning about tool results
    - Error handling and recovery

    Multi-Agent Systems
    Coordinating multiple agents:
    - Shared context management
    - Inter-agent communication
    - Task decomposition and allocation
    - Collective reasoning and decision making

    Performance Optimization

    Context Compression
    Techniques for reducing token usage:
    - Semantic compression (summarization)
    - Syntactic compression (abbreviation)
    - Lossy vs lossless tradeoffs
    - Adaptive compression strategies

    Caching Strategies
    Improving performance through caching:
    - Prompt caching for repeated contexts
    - Embedding caching for documents
    - Result caching for common queries
    - Hierarchical caching structures

    Monitoring and Metrics
    Tracking system performance:
    - Latency (retrieval, assembly, generation)
    - Token usage and efficiency
    - Context relevance scores
    - Memory usage and leaks
    - Quality metrics (accuracy, coherence)

    Advanced Techniques

    Hierarchical Context Assembly
    Multi-level context organization:
    - Critical context (always included)
    - High-priority context (important)
    - Medium-priority context (useful)
    - Low-priority context (supplementary)

    Dynamic Context Adjustment
    Adapting context based on:
    - Query complexity
    - Available tokens
    - Response requirements
    - Historical performance

    Context Field Theory
    Modeling context as fields:
    - Attraction dynamics between components
    - Resonance patterns in effective contexts
    - Emergent behaviors from interactions
    - Phase transitions in context quality

    Best Practices

    Design Principles
    - Keep critical information early in context
    - Use clear structure and formatting
    - Maintain consistent terminology
    - Include relevant examples
    - Provide necessary background

    Optimization Guidelines
    - Monitor token usage closely
    - Benchmark different strategies
    - A/B test context variations
    - Profile memory and performance
    - Iterate based on feedback

    Common Pitfalls
    - Context overload (too much information)
    - Irrelevant retrieval (poor search quality)
    - Insufficient coverage (missing key facts)
    - Inefficient assembly (wasted tokens)
    - Lack of monitoring (blind optimization)

    Future Directions

    The field of context engineering continues to evolve:
    - Longer context windows (100K+ tokens)
    - Smarter retrieval (semantic search, graph RAG)
    - Adaptive strategies (RL-based optimization)
    - Multi-modal context (text, images, code)
    - Distributed context (across agents/systems)

    Resources for Learning

    Research Papers
    - "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"
    - "Lost in the Middle: How Language Models Use Long Contexts"
    - "In-Context Learning and Induction Heads"

    Tools and Frameworks
    - LangChain: Framework for LLM applications
    - LlamaIndex: Data framework for LLMs
    - ChromaDB: Vector database for embeddings
    - FAISS: Efficient similarity search

    Conclusion

    Context engineering is a critical skill for building effective LLM applications.
    By understanding its mathematical foundations, mastering its practical techniques,
    and following best practices, developers can create systems that make optimal
    use of the precious context window resource.

    The journey from simple prompts to sophisticated context engineering represents
    a maturation of the field, moving from ad-hoc approaches to systematic,
    theoretically-grounded methodologies.
    """


def interactive_mode(assistant: RAGAssistant):
    """Run interactive query loop."""
    print("\n" + "=" * 60)
    print("Interactive RAG Assistant")
    print("=" * 60)
    print("Enter your questions (or 'quit' to exit)")
    print("Commands:")
    print("  stats - Show system statistics")
    print("  clear - Clear conversation history")
    print("  quit  - Exit the assistant")
    print("=" * 60)

    while True:
        try:
            query = input("\nYour question: ").strip()

            if not query:
                continue

            if query.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break

            if query.lower() == 'stats':
                stats = assistant.get_statistics()
                print("\nSystem Statistics:")
                for key, value in stats.items():
                    print(f"  {key}: {value}")
                continue

            if query.lower() == 'clear':
                assistant.clear_conversation()
                continue

            # Process query
            print("\nSearching knowledge base...")
            response = assistant.query(query, include_sources=True)

            print(f"\nAnswer:")
            print(response.answer)

            # Show sources
            if response.sources:
                print(f"\nSources ({len(response.sources)} documents):")
                for i, source in enumerate(response.sources[:3], 1):
                    print(f"\n  [{i}] Relevance: {source.score:.3f}")
                    preview = source.document.content[:120].replace('\n', ' ')
                    print(f"      {preview}...")

            # Show metadata
            print(f"\nQuery Performance:")
            print(f"  Retrieval: {response.metadata['retrieval_time_ms']:.2f}ms")
            print(f"  Assembly: {response.metadata['assembly_time_ms']:.2f}ms")
            print(f"  Total: {response.metadata['total_time_ms']:.2f}ms")
            print(f"  Context tokens: {response.metadata['context_tokens']}")

        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            continue


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Simple RAG Assistant - Context Engineering Example"
    )

    parser.add_argument(
        '--docs',
        type=str,
        help='Path to document file to load'
    )

    parser.add_argument(
        '--chunk-size',
        type=int,
        default=500,
        help='Chunk size for document splitting (default: 500)'
    )

    parser.add_argument(
        '--top-k',
        type=int,
        default=5,
        help='Number of documents to retrieve (default: 5)'
    )

    parser.add_argument(
        '--max-tokens',
        type=int,
        default=2000,
        help='Maximum context tokens (default: 2000)'
    )

    parser.add_argument(
        '--strategy',
        type=str,
        choices=['linear', 'weighted', 'hierarchical', 'sliding'],
        default='weighted',
        help='Context assembly strategy (default: weighted)'
    )

    parser.add_argument(
        '--query',
        type=str,
        help='Single query mode (non-interactive)'
    )

    args = parser.parse_args()

    # Map strategy string to enum
    strategy_map = {
        'linear': AssemblyStrategy.LINEAR,
        'weighted': AssemblyStrategy.WEIGHTED,
        'hierarchical': AssemblyStrategy.HIERARCHICAL,
        'sliding': AssemblyStrategy.SLIDING
    }

    # Create assistant
    print("Initializing RAG Assistant...")
    assistant = RAGAssistant(
        chunk_size=args.chunk_size,
        max_context_tokens=args.max_tokens,
        top_k_results=args.top_k,
        assembly_strategy=strategy_map[args.strategy]
    )

    # Load documents
    if args.docs:
        print(f"Loading documents from: {args.docs}")
        try:
            count = assistant.load_documents(args.docs)
            print(f"Loaded {count} document chunks")
        except Exception as e:
            print(f"Error loading documents: {e}")
            print("Using sample data instead...")
            sample_data = load_sample_data()
            count = assistant.load_text(sample_data,
                                       metadata={'source': 'sample_data'})
            print(f"Loaded {count} chunks from sample data")
    else:
        print("Loading sample data...")
        sample_data = load_sample_data()
        count = assistant.load_text(sample_data,
                                    metadata={'source': 'sample_data'})
        print(f"Loaded {count} chunks from sample data")

    # Single query mode or interactive
    if args.query:
        print(f"\nQuery: {args.query}")
        response = assistant.query(args.query)
        print(f"\nAnswer:")
        print(response.answer)

        if response.sources:
            print(f"\nSources:")
            for i, source in enumerate(response.sources, 1):
                print(f"  [{i}] Score: {source.score:.3f}")
    else:
        interactive_mode(assistant)


if __name__ == "__main__":
    main()
