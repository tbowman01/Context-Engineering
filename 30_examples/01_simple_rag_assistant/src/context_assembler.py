"""
Context Assembler for RAG Assistant
====================================

Intelligently assemble context windows from retrieved documents.
Implements context engineering principles for optimal context construction.

Author: Context Engineering Contributors
License: MIT
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

from .document_loader import Document
from .vector_store import SearchResult
from .utils import count_tokens, format_context_window


class AssemblyStrategy(Enum):
    """Context assembly strategies."""
    LINEAR = "linear"  # Simple concatenation
    WEIGHTED = "weighted"  # Weight by relevance scores
    HIERARCHICAL = "hierarchical"  # Organize by importance levels
    SLIDING = "sliding"  # Prioritize recent context


@dataclass
class AssembledContext:
    """
    Result of context assembly.

    Attributes:
        context_text: Final assembled context string
        total_tokens: Token count of assembled context
        documents_used: Number of documents included
        documents_truncated: Number of documents that were truncated
        strategy_used: Assembly strategy applied
        metadata: Additional assembly metadata
    """

    context_text: str
    total_tokens: int
    documents_used: int
    documents_truncated: int
    strategy_used: str
    metadata: Dict[str, Any]


class ContextAssembler:
    """
    Assemble optimal context windows from retrieved documents.

    Implements various strategies for context construction:
    - Linear: Simple concatenation by relevance
    - Weighted: Priority-based selection with scoring
    - Hierarchical: Multi-level organization
    - Sliding: Time-aware context with recency bias

    Example:
        >>> assembler = ContextAssembler(max_tokens=1000)
        >>> context = assembler.assemble(query, search_results)
        >>> print(f"Assembled {context.documents_used} docs")
        >>> print(f"Total tokens: {context.total_tokens}")
    """

    def __init__(
        self,
        max_tokens: int = 2000,
        strategy: AssemblyStrategy = AssemblyStrategy.WEIGHTED,
        reserve_tokens_for_response: int = 500,
        model: str = "gpt-3.5-turbo"
    ):
        """
        Initialize context assembler.

        Args:
            max_tokens: Maximum tokens for assembled context
            strategy: Assembly strategy to use
            reserve_tokens_for_response: Tokens to reserve for response
            model: Model name for token counting
        """
        self.max_tokens = max_tokens
        self.strategy = strategy
        self.reserve_tokens = reserve_tokens_for_response
        self.model = model

        # Calculate available tokens for context
        self.available_tokens = max_tokens - reserve_tokens_for_response

    def assemble(
        self,
        query: str,
        search_results: List[SearchResult],
        conversation_history: Optional[List[Dict]] = None,
        additional_context: Optional[str] = None
    ) -> AssembledContext:
        """
        Assemble context from search results and other sources.

        Args:
            query: User query
            search_results: Retrieved documents with scores
            conversation_history: Optional conversation history
            additional_context: Optional additional context to include

        Returns:
            AssembledContext object

        Example:
            >>> results = vector_store.search(query, top_k=5)
            >>> context = assembler.assemble(query, results)
        """
        # Select strategy
        if self.strategy == AssemblyStrategy.LINEAR:
            return self._assemble_linear(query, search_results, additional_context)
        elif self.strategy == AssemblyStrategy.WEIGHTED:
            return self._assemble_weighted(
                query, search_results, conversation_history, additional_context
            )
        elif self.strategy == AssemblyStrategy.HIERARCHICAL:
            return self._assemble_hierarchical(
                query, search_results, conversation_history, additional_context
            )
        elif self.strategy == AssemblyStrategy.SLIDING:
            return self._assemble_sliding(
                query, search_results, conversation_history, additional_context
            )
        else:
            return self._assemble_linear(query, search_results, additional_context)

    def _assemble_linear(
        self,
        query: str,
        search_results: List[SearchResult],
        additional_context: Optional[str] = None
    ) -> AssembledContext:
        """
        Linear assembly: Simple concatenation by relevance.

        Most relevant documents first, add until token limit.
        """
        context_parts = []
        total_tokens = 0
        docs_used = 0
        docs_truncated = 0

        # Add instruction
        instruction = "Use the following context to answer the question.\n\nContext:\n"
        context_parts.append(instruction)
        total_tokens += count_tokens(instruction, self.model)

        # Add additional context if provided
        if additional_context:
            additional_text = f"\n[Additional Context]\n{additional_context}\n"
            additional_tokens = count_tokens(additional_text, self.model)

            if total_tokens + additional_tokens < self.available_tokens:
                context_parts.append(additional_text)
                total_tokens += additional_tokens

        # Add documents in order of relevance
        for i, result in enumerate(search_results, 1):
            doc = result.document
            doc_text = f"\n[Document {i}] (Relevance: {result.score:.3f})\n{doc.content}\n"
            doc_tokens = count_tokens(doc_text, self.model)

            if total_tokens + doc_tokens <= self.available_tokens:
                # Add full document
                context_parts.append(doc_text)
                total_tokens += doc_tokens
                docs_used += 1
            else:
                # Try to fit truncated version
                remaining_tokens = self.available_tokens - total_tokens
                if remaining_tokens > 50:  # Only if meaningful space left
                    # Estimate characters that fit
                    chars_per_token = len(doc.content) / doc.token_count
                    max_chars = int(remaining_tokens * chars_per_token * 0.9)

                    if max_chars > 100:
                        truncated_content = doc.content[:max_chars] + "..."
                        truncated_text = (
                            f"\n[Document {i}] (Relevance: {result.score:.3f}, Truncated)\n"
                            f"{truncated_content}\n"
                        )
                        context_parts.append(truncated_text)
                        total_tokens += count_tokens(truncated_text, self.model)
                        docs_used += 1
                        docs_truncated += 1

                break  # No more space

        # Add query
        query_text = f"\nQuestion: {query}\n\nAnswer based on the context provided:"
        context_parts.append(query_text)
        total_tokens += count_tokens(query_text, self.model)

        return AssembledContext(
            context_text="\n".join(context_parts),
            total_tokens=total_tokens,
            documents_used=docs_used,
            documents_truncated=docs_truncated,
            strategy_used="linear",
            metadata={
                'total_results': len(search_results),
                'available_tokens': self.available_tokens
            }
        )

    def _assemble_weighted(
        self,
        query: str,
        search_results: List[SearchResult],
        conversation_history: Optional[List[Dict]] = None,
        additional_context: Optional[str] = None
    ) -> AssembledContext:
        """
        Weighted assembly: Priority-based selection.

        Adjusts document priority based on:
        - Relevance score (40%)
        - Recency if in conversation (30%)
        - Token efficiency (30%)
        """
        # Calculate composite scores
        scored_results = []

        for result in search_results:
            doc = result.document
            tokens = doc.token_count

            # Base score from relevance
            relevance_score = result.score * 0.4

            # Token efficiency (prefer information-dense documents)
            chars_per_token = len(doc.content) / tokens if tokens > 0 else 0
            efficiency_score = min(chars_per_token / 5.0, 1.0) * 0.3

            # Recency score (if metadata available)
            recency_score = 0.0
            if 'timestamp' in doc.metadata:
                # Implement recency scoring based on timestamp
                recency_score = 0.3  # Placeholder

            composite_score = relevance_score + efficiency_score + recency_score

            scored_results.append((result, composite_score))

        # Sort by composite score
        scored_results.sort(key=lambda x: x[1], reverse=True)

        # Use linear assembly with reordered results
        reordered_results = [result for result, _ in scored_results]
        return self._assemble_linear(query, reordered_results, additional_context)

    def _assemble_hierarchical(
        self,
        query: str,
        search_results: List[SearchResult],
        conversation_history: Optional[List[Dict]] = None,
        additional_context: Optional[str] = None
    ) -> AssembledContext:
        """
        Hierarchical assembly: Multi-level organization.

        Organizes context into levels:
        1. High relevance (score > 0.7)
        2. Medium relevance (0.4 - 0.7)
        3. Low relevance (< 0.4)
        """
        # Categorize by relevance
        high_relevance = [r for r in search_results if r.score > 0.7]
        medium_relevance = [r for r in search_results if 0.4 <= r.score <= 0.7]
        low_relevance = [r for r in search_results if r.score < 0.4]

        context_parts = []
        total_tokens = 0
        docs_used = 0
        docs_truncated = 0

        # Instruction
        instruction = (
            "Use the following hierarchically organized context to answer the question.\n\n"
        )
        context_parts.append(instruction)
        total_tokens += count_tokens(instruction, self.model)

        # Process each level
        for level_name, level_results in [
            ("High Priority", high_relevance),
            ("Medium Priority", medium_relevance),
            ("Low Priority", low_relevance)
        ]:
            if not level_results:
                continue

            level_header = f"\n[{level_name} Context]\n"
            level_tokens = count_tokens(level_header, self.model)

            if total_tokens + level_tokens >= self.available_tokens:
                break

            context_parts.append(level_header)
            total_tokens += level_tokens

            # Add documents from this level
            for result in level_results:
                doc = result.document
                doc_text = f"\n{doc.content}\n"
                doc_tokens = count_tokens(doc_text, self.model)

                if total_tokens + doc_tokens <= self.available_tokens:
                    context_parts.append(doc_text)
                    total_tokens += doc_tokens
                    docs_used += 1
                else:
                    break

        # Add query
        query_text = f"\nQuestion: {query}\n\nAnswer:"
        context_parts.append(query_text)
        total_tokens += count_tokens(query_text, self.model)

        return AssembledContext(
            context_text="\n".join(context_parts),
            total_tokens=total_tokens,
            documents_used=docs_used,
            documents_truncated=docs_truncated,
            strategy_used="hierarchical",
            metadata={
                'high_relevance_count': len(high_relevance),
                'medium_relevance_count': len(medium_relevance),
                'low_relevance_count': len(low_relevance)
            }
        )

    def _assemble_sliding(
        self,
        query: str,
        search_results: List[SearchResult],
        conversation_history: Optional[List[Dict]] = None,
        additional_context: Optional[str] = None
    ) -> AssembledContext:
        """
        Sliding window assembly: Prioritize recent context.

        Useful for conversational systems where recent messages are more relevant.
        """
        # If conversation history provided, prioritize it
        context_parts = []
        total_tokens = 0
        docs_used = 0

        instruction = "Context:\n"
        context_parts.append(instruction)
        total_tokens += count_tokens(instruction, self.model)

        # Add recent conversation history first
        if conversation_history:
            history_text = "\n[Recent Conversation]\n"
            for msg in conversation_history[-3:]:  # Last 3 messages
                history_text += f"{msg.get('role', 'user')}: {msg.get('content', '')}\n"

            history_tokens = count_tokens(history_text, self.model)
            if total_tokens + history_tokens <= self.available_tokens:
                context_parts.append(history_text)
                total_tokens += history_tokens

        # Add retrieved documents
        for result in search_results:
            doc = result.document
            doc_text = f"\n{doc.content}\n"
            doc_tokens = count_tokens(doc_text, self.model)

            if total_tokens + doc_tokens <= self.available_tokens:
                context_parts.append(doc_text)
                total_tokens += doc_tokens
                docs_used += 1
            else:
                break

        # Add query
        query_text = f"\nQuestion: {query}\n\nAnswer:"
        context_parts.append(query_text)
        total_tokens += count_tokens(query_text, self.model)

        return AssembledContext(
            context_text="\n".join(context_parts),
            total_tokens=total_tokens,
            documents_used=docs_used,
            documents_truncated=0,
            strategy_used="sliding",
            metadata={
                'conversation_included': conversation_history is not None
            }
        )


# ============================================================================
# Example Usage
# ============================================================================

def example_context_assembly():
    """Example of context assembly."""
    print("Context Assembler Example")
    print("=" * 60)

    # Create mock search results
    from .document_loader import Document, DocumentLoader
    from .vector_store import SearchResult

    loader = DocumentLoader()

    # Sample documents
    doc_texts = [
        "Context engineering is the art of optimizing the context window for LLMs.",
        "RAG systems retrieve relevant documents and generate responses based on them.",
        "Vector databases enable efficient similarity search over embeddings.",
        "The context window is limited, so careful engineering is required.",
        "Information theory helps us measure the efficiency of context usage."
    ]

    documents = [loader.load_text(text)[0] for text in doc_texts]

    # Create mock search results with scores
    search_results = [
        SearchResult(doc, score, rank)
        for rank, (doc, score) in enumerate(
            zip(documents, [0.9, 0.7, 0.5, 0.8, 0.6]), 1
        )
    ]

    query = "How does context engineering work?"

    # Test different strategies
    strategies = [
        AssemblyStrategy.LINEAR,
        AssemblyStrategy.WEIGHTED,
        AssemblyStrategy.HIERARCHICAL
    ]

    for strategy in strategies:
        print(f"\n{'='*60}")
        print(f"Strategy: {strategy.value.upper()}")
        print("-" * 60)

        assembler = ContextAssembler(
            max_tokens=500,
            strategy=strategy
        )

        result = assembler.assemble(query, search_results)

        print(f"Documents used: {result.documents_used}/{len(search_results)}")
        print(f"Total tokens: {result.total_tokens}")
        print(f"Documents truncated: {result.documents_truncated}")
        print(f"Metadata: {result.metadata}")
        print(f"\nContext preview:")
        print(result.context_text[:300] + "...")

    print("\n" + "=" * 60)
    print("Context assembly example complete!")


if __name__ == "__main__":
    example_context_assembly()
