"""
Tests for Simple RAG Assistant
===============================

Basic unit tests for RAG components.

Author: Context Engineering Contributors
License: MIT
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.document_loader import DocumentLoader, Document
from src.vector_store import VectorStore, SearchResult
from src.context_assembler import ContextAssembler, AssemblyStrategy
from src.rag_assistant import RAGAssistant
from src.utils import (
    count_tokens,
    chunk_text,
    clean_text,
    similarity_score
)


class TestUtils:
    """Test utility functions."""

    def test_token_counting(self):
        """Test token counting."""
        text = "Hello, world!"
        tokens = count_tokens(text)
        assert tokens > 0
        assert isinstance(tokens, int)

    def test_chunking(self):
        """Test text chunking."""
        text = "This is a test. " * 50  # 200 chars
        chunks = chunk_text(text, chunk_size=100, chunk_overlap=20)

        assert len(chunks) >= 2
        assert all(isinstance(chunk, str) for chunk in chunks)
        assert all(len(chunk) <= 120 for chunk in chunks)  # Allow for overlap

    def test_clean_text(self):
        """Test text cleaning."""
        text = "  Hello   World!  \n\n  "
        cleaned = clean_text(text)
        assert cleaned == "Hello World!"

    def test_similarity(self):
        """Test similarity scoring."""
        text1 = "machine learning"
        text2 = "machine learning"
        text3 = "quantum physics"

        # Identical texts should have high similarity
        score1 = similarity_score(text1, text2)
        assert score1 > 0.9

        # Different texts should have low similarity
        score2 = similarity_score(text1, text3)
        assert score2 < 0.5


class TestDocumentLoader:
    """Test document loading."""

    def test_load_text(self):
        """Test loading from text string."""
        loader = DocumentLoader(chunk_size=100, chunk_overlap=20)

        text = "Context engineering is important. " * 10
        documents = loader.load_text(text)

        assert len(documents) > 0
        assert all(isinstance(doc, Document) for doc in documents)
        assert all(doc.token_count > 0 for doc in documents)

    def test_document_metadata(self):
        """Test document metadata."""
        loader = DocumentLoader()

        text = "Test document"
        metadata = {'source': 'test', 'author': 'tester'}
        documents = loader.load_text(text, metadata=metadata)

        assert len(documents) > 0
        doc = documents[0]
        assert doc.metadata['source'] == 'test'
        assert doc.metadata['author'] == 'tester'

    def test_chunking_parameters(self):
        """Test different chunking parameters."""
        text = "Word " * 100  # 500 chars

        loader1 = DocumentLoader(chunk_size=50)
        docs1 = loader1.load_text(text)

        loader2 = DocumentLoader(chunk_size=100)
        docs2 = loader2.load_text(text)

        # Smaller chunks should create more documents
        assert len(docs1) > len(docs2)


class TestVectorStore:
    """Test vector store functionality."""

    def test_add_documents(self):
        """Test adding documents to store."""
        store = VectorStore()
        loader = DocumentLoader()

        text = "Context engineering is the art of optimization."
        documents = loader.load_text(text)

        store.add_documents(documents)

        assert len(store) == len(documents)

    def test_search(self):
        """Test document search."""
        store = VectorStore()
        loader = DocumentLoader(chunk_size=100)

        # Add sample documents
        texts = [
            "Context engineering is important for LLMs.",
            "RAG systems retrieve and generate responses.",
            "Vector stores enable similarity search."
        ]

        for text in texts:
            docs = loader.load_text(text)
            store.add_documents(docs)

        # Search
        results = store.search("context engineering", top_k=2)

        assert len(results) <= 2
        assert all(isinstance(r, SearchResult) for r in results)
        assert all(0 <= r.score <= 1 for r in results)

        # Results should be sorted by score
        if len(results) > 1:
            assert results[0].score >= results[1].score

    def test_empty_search(self):
        """Test search with no documents."""
        store = VectorStore()
        results = store.search("test query", top_k=5)
        assert len(results) == 0

    def test_statistics(self):
        """Test store statistics."""
        store = VectorStore()
        loader = DocumentLoader()

        text = "Test document " * 20
        docs = loader.load_text(text)
        store.add_documents(docs)

        stats = store.get_statistics()

        assert stats['total_documents'] == len(docs)
        assert stats['total_tokens'] > 0
        assert stats['average_tokens_per_doc'] > 0


class TestContextAssembler:
    """Test context assembly."""

    def test_linear_assembly(self):
        """Test linear assembly strategy."""
        assembler = ContextAssembler(
            max_tokens=500,
            strategy=AssemblyStrategy.LINEAR
        )

        # Create mock search results
        loader = DocumentLoader()
        docs = loader.load_text("Context engineering is important.")

        from src.vector_store import SearchResult
        results = [
            SearchResult(doc, score=0.9, rank=1)
            for doc in docs
        ]

        query = "What is context engineering?"
        assembled = assembler.assemble(query, results)

        assert assembled.total_tokens > 0
        assert assembled.total_tokens <= 500
        assert assembled.documents_used > 0
        assert query in assembled.context_text

    def test_weighted_assembly(self):
        """Test weighted assembly strategy."""
        assembler = ContextAssembler(
            max_tokens=500,
            strategy=AssemblyStrategy.WEIGHTED
        )

        loader = DocumentLoader()
        docs = loader.load_text("Test content " * 20)

        from src.vector_store import SearchResult
        results = [
            SearchResult(doc, score=0.8, rank=1)
            for doc in docs
        ]

        query = "Test query?"
        assembled = assembler.assemble(query, results)

        assert assembled.strategy_used == "linear"  # Weighted uses linear internally
        assert assembled.total_tokens > 0


class TestRAGAssistant:
    """Test complete RAG assistant."""

    def test_initialization(self):
        """Test assistant initialization."""
        assistant = RAGAssistant()
        assert assistant.query_count == 0
        assert len(assistant.conversation_history) == 0

    def test_load_text(self):
        """Test loading text into assistant."""
        assistant = RAGAssistant(chunk_size=100)

        text = "Context engineering is a systematic approach to optimizing context windows."
        count = assistant.load_text(text)

        assert count > 0

        stats = assistant.get_statistics()
        assert stats['document_count'] == count

    def test_query(self):
        """Test querying the assistant."""
        assistant = RAGAssistant()

        # Load knowledge
        text = """
        Context engineering is the art of optimizing context windows.
        It involves systematic approaches to context design and optimization.
        RAG systems use context engineering principles.
        """
        assistant.load_text(text)

        # Query
        response = assistant.query("What is context engineering?")

        assert response.answer is not None
        assert len(response.answer) > 0
        assert response.metadata['total_time_ms'] > 0
        assert response.metadata['query_count'] == 1

    def test_empty_query(self):
        """Test query with no documents loaded."""
        assistant = RAGAssistant()

        response = assistant.query("Test query?")

        # Should return response indicating no information
        assert "don't have enough information" in response.answer.lower()

    def test_statistics(self):
        """Test assistant statistics."""
        assistant = RAGAssistant()

        text = "Test document content."
        assistant.load_text(text)
        assistant.query("Test query?")

        stats = assistant.get_statistics()

        assert stats['total_queries'] == 1
        assert stats['document_count'] > 0
        assert stats['average_query_time_ms'] > 0

    def test_conversation_history(self):
        """Test conversation history tracking."""
        assistant = RAGAssistant()

        text = "Context engineering is important."
        assistant.load_text(text)

        # First query with history enabled
        response1 = assistant.query(
            "What is context engineering?",
            use_conversation_history=True
        )

        assert len(assistant.conversation_history) == 2  # Query + response

        # Second query
        response2 = assistant.query(
            "Tell me more.",
            use_conversation_history=True
        )

        assert len(assistant.conversation_history) == 4  # 2 exchanges

        # Clear history
        assistant.clear_conversation()
        assert len(assistant.conversation_history) == 0


def run_tests():
    """Run all tests."""
    print("Running RAG Assistant Tests")
    print("=" * 60)

    test_classes = [
        TestUtils,
        TestDocumentLoader,
        TestVectorStore,
        TestContextAssembler,
        TestRAGAssistant
    ]

    total_tests = 0
    passed_tests = 0

    for test_class in test_classes:
        print(f"\n{test_class.__name__}:")
        print("-" * 60)

        test_instance = test_class()
        test_methods = [
            method for method in dir(test_instance)
            if method.startswith('test_')
        ]

        for method_name in test_methods:
            total_tests += 1
            try:
                method = getattr(test_instance, method_name)
                method()
                print(f"  ✓ {method_name}")
                passed_tests += 1
            except Exception as e:
                print(f"  ✗ {method_name}: {e}")

    print("\n" + "=" * 60)
    print(f"Results: {passed_tests}/{total_tests} tests passed")

    return passed_tests == total_tests


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
