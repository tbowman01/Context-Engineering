"""
Vector Store for RAG Assistant
===============================

Simple vector store implementation for document retrieval.
For production, use ChromaDB, FAISS, or Pinecone.

Author: Context Engineering Contributors
License: MIT
"""

from typing import List, Optional, Dict, Tuple, Any
from dataclasses import dataclass
import json
from pathlib import Path

# Try to import numpy (only needed for embeddings version)
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

from .document_loader import Document
from .utils import similarity_score


@dataclass
class SearchResult:
    """
    Result from vector search.

    Attributes:
        document: Retrieved document
        score: Similarity score (0-1)
        rank: Ranking position (1-based)
    """

    document: Document
    score: float
    rank: int


class VectorStore:
    """
    Simple vector store for document storage and retrieval.

    This is a basic implementation using text similarity. For production:
    - Use ChromaDB, FAISS, or Pinecone for scalability
    - Use proper embeddings (OpenAI, Sentence Transformers)
    - Implement approximate nearest neighbor search

    Example:
        >>> store = VectorStore()
        >>> store.add_documents(documents)
        >>> results = store.search("context engineering", top_k=5)
    """

    def __init__(
        self,
        embedding_model: Optional[str] = None,
        similarity_threshold: float = 0.0
    ):
        """
        Initialize vector store.

        Args:
            embedding_model: Name of embedding model (not used in basic version)
            similarity_threshold: Minimum similarity for results (0-1)
        """
        self.documents: List[Document] = []
        self.embedding_model = embedding_model
        self.similarity_threshold = similarity_threshold
        self._doc_index: Dict[str, Document] = {}

    def add_documents(self, documents: List[Document]) -> None:
        """
        Add documents to the store.

        Args:
            documents: List of Document objects

        Example:
            >>> store = VectorStore()
            >>> store.add_documents([doc1, doc2, doc3])
            >>> print(f"Store size: {len(store)}")
        """
        for doc in documents:
            self.documents.append(doc)
            self._doc_index[doc.chunk_id] = doc

    def add_document(self, document: Document) -> None:
        """
        Add single document to the store.

        Args:
            document: Document object
        """
        self.documents.append(document)
        self._doc_index[document.chunk_id] = document

    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[SearchResult]:
        """
        Search for relevant documents.

        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Optional metadata filters

        Returns:
            List of SearchResult objects sorted by relevance

        Example:
            >>> results = store.search("RAG systems", top_k=3)
            >>> for result in results:
            ...     print(f"Score: {result.score:.3f}")
            ...     print(f"Content: {result.document.content[:100]}")
        """
        if not self.documents:
            return []

        # Calculate similarity scores
        scored_docs = []

        for doc in self.documents:
            # Apply metadata filters if specified
            if filter_metadata:
                if not self._matches_filters(doc.metadata, filter_metadata):
                    continue

            # Calculate similarity score
            score = similarity_score(query, doc.content)

            if score >= self.similarity_threshold:
                scored_docs.append((doc, score))

        # Sort by score (descending)
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        # Create SearchResult objects
        results = []
        for rank, (doc, score) in enumerate(scored_docs[:top_k], 1):
            result = SearchResult(
                document=doc,
                score=score,
                rank=rank
            )
            results.append(result)

        return results

    def _matches_filters(
        self,
        metadata: Dict,
        filters: Dict
    ) -> bool:
        """Check if document metadata matches filters."""
        for key, value in filters.items():
            if key not in metadata or metadata[key] != value:
                return False
        return True

    def get_document_by_id(self, chunk_id: str) -> Optional[Document]:
        """
        Retrieve document by chunk ID.

        Args:
            chunk_id: Document chunk ID

        Returns:
            Document if found, None otherwise
        """
        return self._doc_index.get(chunk_id)

    def get_all_documents(self) -> List[Document]:
        """
        Get all documents in the store.

        Returns:
            List of all documents
        """
        return self.documents.copy()

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get store statistics.

        Returns:
            Dictionary with statistics

        Example:
            >>> stats = store.get_statistics()
            >>> print(f"Total documents: {stats['total_documents']}")
            >>> print(f"Total tokens: {stats['total_tokens']}")
        """
        total_tokens = sum(doc.token_count for doc in self.documents)
        avg_tokens = total_tokens / len(self.documents) if self.documents else 0

        # Count unique sources
        sources = set(doc.metadata.get('source', 'unknown')
                     for doc in self.documents)

        return {
            'total_documents': len(self.documents),
            'total_tokens': total_tokens,
            'average_tokens_per_doc': round(avg_tokens, 2),
            'unique_sources': len(sources),
            'sources': list(sources)
        }

    def clear(self) -> None:
        """Clear all documents from the store."""
        self.documents.clear()
        self._doc_index.clear()

    def save(self, filepath: str) -> None:
        """
        Save store to file.

        Args:
            filepath: Path to save file

        Example:
            >>> store.save("vector_store.json")
        """
        data = {
            'documents': [
                {
                    'content': doc.content,
                    'metadata': doc.metadata,
                    'token_count': doc.token_count,
                    'chunk_id': doc.chunk_id
                }
                for doc in self.documents
            ],
            'config': {
                'embedding_model': self.embedding_model,
                'similarity_threshold': self.similarity_threshold
            }
        }

        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        print(f"Vector store saved to: {filepath}")

    def load(self, filepath: str) -> None:
        """
        Load store from file.

        Args:
            filepath: Path to load from

        Example:
            >>> store = VectorStore()
            >>> store.load("vector_store.json")
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Load configuration
        config = data.get('config', {})
        self.embedding_model = config.get('embedding_model')
        self.similarity_threshold = config.get('similarity_threshold', 0.0)

        # Load documents
        self.clear()
        for doc_data in data['documents']:
            doc = Document(
                content=doc_data['content'],
                metadata=doc_data['metadata'],
                token_count=doc_data['token_count'],
                chunk_id=doc_data['chunk_id']
            )
            self.add_document(doc)

        print(f"Loaded {len(self.documents)} documents from: {filepath}")

    def __len__(self) -> int:
        """Return number of documents in store."""
        return len(self.documents)

    def __repr__(self) -> str:
        """String representation."""
        return (f"VectorStore(documents={len(self.documents)}, "
                f"threshold={self.similarity_threshold})")


if HAS_NUMPY:
    class VectorStoreWithEmbeddings(VectorStore):
        """
        Extended vector store with proper embeddings support.

        NOTE: This requires additional dependencies:
        - sentence-transformers or
        - openai API
        - numpy

        For this basic example, we use the simple VectorStore.
        """

        def __init__(
            self,
            embedding_model: str = "all-MiniLM-L6-v2",
            similarity_threshold: float = 0.0
        ):
            """
            Initialize with embedding model.

            Args:
                embedding_model: Sentence transformer model name
                similarity_threshold: Minimum similarity for results
            """
            super().__init__(embedding_model, similarity_threshold)
            self.embeddings: Dict[str, np.ndarray] = {}

            # NOTE: Actual implementation would initialize embedding model here
            # from sentence_transformers import SentenceTransformer
            # self.model = SentenceTransformer(embedding_model)

        def _embed_text(self, text: str) -> np.ndarray:
            """
            Generate embedding for text.

            NOTE: This is a placeholder. Real implementation would use:
            - Sentence Transformers
            - OpenAI embeddings API
            - Custom embedding model
            """
            # Placeholder: return random vector
            # Real implementation:
            # return self.model.encode(text)
            return np.random.rand(384)  # Typical embedding dimension

        def add_documents(self, documents: List[Document]) -> None:
            """Add documents and compute embeddings."""
            super().add_documents(documents)

            # Compute embeddings for new documents
            # NOTE: In production, batch this operation
            for doc in documents:
                if doc.chunk_id not in self.embeddings:
                    self.embeddings[doc.chunk_id] = self._embed_text(doc.content)

        def search(
            self,
            query: str,
            top_k: int = 5,
            filter_metadata: Optional[Dict] = None
        ) -> List[SearchResult]:
            """
            Search using embedding similarity.

            Uses cosine similarity between query and document embeddings.
            """
            if not self.documents:
                return []

            # Embed query
            query_embedding = self._embed_text(query)

            # Calculate cosine similarities
            scored_docs = []

            for doc in self.documents:
                # Apply metadata filters
                if filter_metadata:
                    if not self._matches_filters(doc.metadata, filter_metadata):
                        continue

                # Get document embedding
                doc_embedding = self.embeddings.get(doc.chunk_id)
                if doc_embedding is None:
                    continue

                # Cosine similarity
                score = self._cosine_similarity(query_embedding, doc_embedding)

                if score >= self.similarity_threshold:
                    scored_docs.append((doc, score))

            # Sort and return top K
            scored_docs.sort(key=lambda x: x[1], reverse=True)

            results = []
            for rank, (doc, score) in enumerate(scored_docs[:top_k], 1):
                result = SearchResult(
                    document=doc,
                    score=score,
                    rank=rank
                )
                results.append(result)

            return results

        def _cosine_similarity(
            self,
            vec1: np.ndarray,
            vec2: np.ndarray
        ) -> float:
            """Calculate cosine similarity between vectors."""
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            return float(dot_product / (norm1 * norm2))


# ============================================================================
# Example Usage
# ============================================================================

def example_vector_store():
    """Example of using vector store."""
    print("Vector Store Example")
    print("=" * 60)

    # Create some sample documents
    from .document_loader import DocumentLoader

    loader = DocumentLoader(chunk_size=150)

    sample_texts = [
        "Context engineering is the art of optimizing the context window.",
        "RAG systems combine retrieval with generation for better responses.",
        "Vector stores enable efficient similarity search over documents.",
        "Embeddings capture semantic meaning of text in vector form.",
        "Information theory helps measure context relevance and efficiency."
    ]

    documents = []
    for text in sample_texts:
        docs = loader.load_text(text)
        documents.extend(docs)

    print(f"Created {len(documents)} documents")

    # Create vector store
    store = VectorStore(similarity_threshold=0.1)
    store.add_documents(documents)

    print(f"Store size: {len(store)}")

    # Get statistics
    stats = store.get_statistics()
    print(f"\nStore Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Perform searches
    queries = [
        "What is context engineering?",
        "How do RAG systems work?",
        "Explain vector search"
    ]

    for query in queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print("-" * 60)

        results = store.search(query, top_k=3)

        if results:
            for result in results:
                print(f"\nRank {result.rank} (Score: {result.score:.3f}):")
                print(f"  {result.document.content[:100]}...")
        else:
            print("  No results found")

    # Save and load
    print(f"\n{'='*60}")
    print("Testing save/load functionality...")

    save_path = "test_vector_store.json"
    store.save(save_path)

    # Create new store and load
    new_store = VectorStore()
    new_store.load(save_path)

    print(f"Loaded store size: {len(new_store)}")

    # Clean up
    import os
    if os.path.exists(save_path):
        os.remove(save_path)
        print(f"Cleaned up test file: {save_path}")

    print("\n" + "=" * 60)
    print("Vector store example complete!")


if __name__ == "__main__":
    example_vector_store()
