"""
RAG Assistant - Main Class
===========================

Complete RAG (Retrieval-Augmented Generation) system integrating
document loading, vector storage, context assembly, and LLM generation.

Author: Context Engineering Contributors
License: MIT
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import os
import time

from .document_loader import DocumentLoader, Document
from .vector_store import VectorStore, SearchResult
from .context_assembler import ContextAssembler, AssemblyStrategy, AssembledContext


@dataclass
class RAGResponse:
    """
    Response from RAG assistant.

    Attributes:
        answer: Generated answer
        context_used: Context that was provided to LLM
        sources: Source documents used
        metadata: Additional metadata (latency, tokens, etc.)
    """

    answer: str
    context_used: AssembledContext
    sources: List[SearchResult]
    metadata: Dict[str, Any]


class RAGAssistant:
    """
    Complete RAG Assistant integrating all components.

    Combines:
    - Document loading and chunking
    - Vector storage and retrieval
    - Context assembly and optimization
    - LLM generation (simulated in this basic version)

    Example:
        >>> assistant = RAGAssistant()
        >>> assistant.load_documents("data/knowledge_base.txt")
        >>> response = assistant.query("What is context engineering?")
        >>> print(response.answer)
    """

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        max_context_tokens: int = 2000,
        top_k_results: int = 5,
        assembly_strategy: AssemblyStrategy = AssemblyStrategy.WEIGHTED,
        model: str = "gpt-3.5-turbo",
        enable_monitoring: bool = True
    ):
        """
        Initialize RAG Assistant.

        Args:
            chunk_size: Size for document chunking
            chunk_overlap: Overlap between chunks
            max_context_tokens: Maximum tokens for context
            top_k_results: Number of documents to retrieve
            assembly_strategy: Strategy for context assembly
            model: LLM model name
            enable_monitoring: Enable performance monitoring
        """
        # Initialize components
        self.document_loader = DocumentLoader(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        self.vector_store = VectorStore()

        self.context_assembler = ContextAssembler(
            max_tokens=max_context_tokens,
            strategy=assembly_strategy,
            model=model
        )

        # Configuration
        self.top_k = top_k_results
        self.model = model
        self.enable_monitoring = enable_monitoring

        # Conversation history
        self.conversation_history: List[Dict] = []

        # Performance metrics
        self.query_count = 0
        self.total_query_time = 0.0

    def load_documents(self, filepath: str) -> int:
        """
        Load documents from file into the system.

        Args:
            filepath: Path to document file

        Returns:
            Number of document chunks loaded

        Example:
            >>> assistant = RAGAssistant()
            >>> count = assistant.load_documents("data/docs.txt")
            >>> print(f"Loaded {count} document chunks")
        """
        # Load documents
        documents = self.document_loader.load_file(filepath)

        # Add to vector store
        self.vector_store.add_documents(documents)

        print(f"Loaded {len(documents)} document chunks from {filepath}")

        return len(documents)

    def load_text(self, text: str, metadata: Optional[Dict] = None) -> int:
        """
        Load text directly into the system.

        Args:
            text: Text content
            metadata: Optional metadata

        Returns:
            Number of chunks created

        Example:
            >>> assistant.load_text("Context engineering is...",
            ...                      metadata={'source': 'manual'})
        """
        documents = self.document_loader.load_text(text, metadata)
        self.vector_store.add_documents(documents)

        print(f"Loaded {len(documents)} chunks from text input")

        return len(documents)

    def load_multiple_files(self, filepaths: List[str]) -> int:
        """
        Load multiple document files.

        Args:
            filepaths: List of file paths

        Returns:
            Total number of chunks loaded
        """
        documents = self.document_loader.load_multiple_files(filepaths)
        self.vector_store.add_documents(documents)

        print(f"Loaded {len(documents)} chunks from {len(filepaths)} files")

        return len(documents)

    def query(
        self,
        question: str,
        top_k: Optional[int] = None,
        include_sources: bool = True,
        use_conversation_history: bool = False
    ) -> RAGResponse:
        """
        Query the RAG system.

        Args:
            question: User question
            top_k: Number of documents to retrieve (None = use default)
            include_sources: Include source documents in response
            use_conversation_history: Use conversation context

        Returns:
            RAGResponse object with answer and metadata

        Example:
            >>> response = assistant.query("What is RAG?")
            >>> print(response.answer)
            >>> print(f"Used {len(response.sources)} sources")
        """
        start_time = time.time()

        # Track query
        self.query_count += 1

        # Retrieve relevant documents
        retrieval_start = time.time()
        top_k = top_k or self.top_k
        search_results = self.vector_store.search(question, top_k=top_k)
        retrieval_time = time.time() - retrieval_start

        if not search_results:
            return RAGResponse(
                answer="I don't have enough information to answer that question.",
                context_used=None,
                sources=[],
                metadata={
                    'retrieval_time_ms': retrieval_time * 1000,
                    'total_time_ms': (time.time() - start_time) * 1000,
                    'documents_found': 0
                }
            )

        # Assemble context
        assembly_start = time.time()
        conversation_context = (
            self.conversation_history if use_conversation_history else None
        )
        assembled_context = self.context_assembler.assemble(
            question,
            search_results,
            conversation_history=conversation_context
        )
        assembly_time = time.time() - assembly_start

        # Generate response (simulated in basic version)
        generation_start = time.time()
        answer = self._generate_response(
            question,
            assembled_context,
            search_results
        )
        generation_time = time.time() - generation_start

        total_time = time.time() - start_time
        self.total_query_time += total_time

        # Create response
        response = RAGResponse(
            answer=answer,
            context_used=assembled_context,
            sources=search_results if include_sources else [],
            metadata={
                'retrieval_time_ms': retrieval_time * 1000,
                'assembly_time_ms': assembly_time * 1000,
                'generation_time_ms': generation_time * 1000,
                'total_time_ms': total_time * 1000,
                'documents_retrieved': len(search_results),
                'documents_used': assembled_context.documents_used,
                'context_tokens': assembled_context.total_tokens,
                'query_count': self.query_count
            }
        )

        # Update conversation history
        if use_conversation_history:
            self.conversation_history.append({
                'role': 'user',
                'content': question
            })
            self.conversation_history.append({
                'role': 'assistant',
                'content': answer
            })

        return response

    def _generate_response(
        self,
        question: str,
        context: AssembledContext,
        sources: List[SearchResult]
    ) -> str:
        """
        Generate response using LLM.

        NOTE: This is a simulated implementation. For production:
        - Use OpenAI API: openai.ChatCompletion.create()
        - Use Anthropic API: anthropic.completions.create()
        - Use local models: llama.cpp, Ollama, etc.

        Args:
            question: User question
            context: Assembled context
            sources: Retrieved source documents

        Returns:
            Generated answer string
        """
        # SIMULATED RESPONSE
        # In production, this would call an actual LLM API

        # For demonstration, create a simple response based on sources
        answer_parts = [
            f"Based on the {len(sources)} relevant documents I found, "
        ]

        # Extract key information from top sources
        if sources:
            top_source = sources[0].document.content
            # Simple extraction: first sentence or two
            sentences = top_source.split('.')[:2]
            extracted_info = '.'.join(sentences) + '.'

            answer_parts.append(extracted_info)
        else:
            answer_parts.append("I don't have enough information to provide a detailed answer.")

        answer_parts.append(
            f"\n\n(Note: This is a simulated response. "
            f"In production, this would use a real LLM like GPT-4 or Claude.)"
        )

        return " ".join(answer_parts)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get system statistics.

        Returns:
            Dictionary with statistics

        Example:
            >>> stats = assistant.get_statistics()
            >>> print(f"Total queries: {stats['total_queries']}")
            >>> print(f"Documents in store: {stats['document_count']}")
        """
        store_stats = self.vector_store.get_statistics()

        avg_query_time = (
            self.total_query_time / self.query_count
            if self.query_count > 0 else 0
        )

        return {
            'total_queries': self.query_count,
            'average_query_time_ms': round(avg_query_time * 1000, 2),
            'document_count': store_stats['total_documents'],
            'total_tokens': store_stats['total_tokens'],
            'unique_sources': store_stats['unique_sources'],
            'conversation_history_length': len(self.conversation_history)
        }

    def clear_conversation(self) -> None:
        """Clear conversation history."""
        self.conversation_history.clear()
        print("Conversation history cleared")

    def save_vector_store(self, filepath: str) -> None:
        """
        Save vector store to file.

        Args:
            filepath: Path to save file
        """
        self.vector_store.save(filepath)

    def load_vector_store(self, filepath: str) -> None:
        """
        Load vector store from file.

        Args:
            filepath: Path to load from
        """
        self.vector_store.load(filepath)

    def __repr__(self) -> str:
        """String representation."""
        stats = self.get_statistics()
        return (
            f"RAGAssistant("
            f"documents={stats['document_count']}, "
            f"queries={stats['total_queries']})"
        )


# ============================================================================
# Example Usage
# ============================================================================

def example_rag_assistant():
    """Comprehensive example of RAG assistant usage."""
    print("RAG Assistant Example")
    print("=" * 60)

    # Create assistant
    assistant = RAGAssistant(
        chunk_size=300,
        max_context_tokens=1000,
        top_k_results=3
    )

    # Load sample knowledge base
    knowledge_base = """
    Context Engineering: The Comprehensive Guide

    Context engineering is the delicate art and science of filling the context
    window with just the right information for the next step. It goes beyond
    simple prompt engineering to encompass systematic approaches to context
    design, orchestration, and optimization.

    The mathematical foundation of context engineering includes four key pillars:

    1. Context Formalization: Representing context as C = A(c₁, c₂, ..., c₆)
       where components include base instructions, retrieved facts, conversation
       history, tool results, reasoning traces, and meta-context.

    2. Optimization Theory: Finding optimal strategies F* = arg max E[Reward(C)]
       that maximize expected outcomes given constraints on context size and
       computational resources.

    3. Information Theory: Measuring context efficiency using mutual information
       I(Context; Query) and optimizing information density within token limits.

    4. Bayesian Inference: Updating context strategies based on evidence using
       P(Strategy|Evidence) to continuously improve context design.

    Practical applications of context engineering include:

    - RAG (Retrieval-Augmented Generation): Combining retrieval systems with
      generation to provide relevant knowledge in context.

    - Memory Systems: Implementing hierarchical memory structures (working,
      episodic, semantic, procedural) for maintaining coherent long-term context.

    - Tool-Integrated Reasoning: Orchestrating tool calls within context to
      enable complex multi-step problem solving.

    - Multi-Agent Coordination: Managing shared context across multiple agents
      for collaborative task completion.

    Field theory approaches model context as continuous fields with attractors,
    resonance patterns, and emergent behaviors arising from component interactions.
    """

    print("Loading knowledge base...")
    doc_count = assistant.load_text(knowledge_base,
                                     metadata={'source': 'comprehensive_guide'})
    print(f"Loaded {doc_count} document chunks\n")

    # Example queries
    queries = [
        "What is context engineering?",
        "What are the mathematical foundations?",
        "What are some practical applications?",
        "How does RAG work?"
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n{'='*60}")
        print(f"Query {i}: {query}")
        print("-" * 60)

        response = assistant.query(query)

        print(f"\nAnswer:")
        print(response.answer)

        print(f"\nMetadata:")
        for key, value in response.metadata.items():
            print(f"  {key}: {value}")

        if response.sources:
            print(f"\nTop Source (Score: {response.sources[0].score:.3f}):")
            print(f"  {response.sources[0].document.content[:150]}...")

    # Print statistics
    print(f"\n{'='*60}")
    print("System Statistics:")
    stats = assistant.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 60)
    print("RAG Assistant example complete!")


if __name__ == "__main__":
    example_rag_assistant()
