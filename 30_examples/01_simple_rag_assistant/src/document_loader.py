"""
Document Loader for RAG Assistant
==================================

Load and process documents from various sources.

Author: Context Engineering Contributors
License: MIT
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
from dataclasses import dataclass
import json

from .utils import chunk_text, clean_text, count_tokens


@dataclass
class Document:
    """
    Represents a document or document chunk.

    Attributes:
        content: Document text content
        metadata: Additional metadata (source, page, etc.)
        token_count: Number of tokens in content
        chunk_id: Unique identifier for this chunk
    """

    content: str
    metadata: Dict[str, Any]
    token_count: int = 0
    chunk_id: Optional[str] = None

    def __post_init__(self):
        """Calculate token count if not provided."""
        if self.token_count == 0:
            self.token_count = count_tokens(self.content)

        if self.chunk_id is None:
            # Generate simple chunk ID
            self.chunk_id = f"doc_{hash(self.content) % 1000000}"


class DocumentLoader:
    """
    Load and process documents from various sources.

    Supports:
    - Plain text files (.txt)
    - JSON files (.json)
    - Markdown files (.md)
    - Direct text input

    Example:
        >>> loader = DocumentLoader(chunk_size=500, chunk_overlap=50)
        >>> documents = loader.load_file("data/sample.txt")
        >>> print(f"Loaded {len(documents)} chunks")
    """

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        clean_whitespace: bool = True
    ):
        """
        Initialize document loader.

        Args:
            chunk_size: Target chunk size in characters
            chunk_overlap: Overlap between chunks in characters
            clean_whitespace: Whether to clean extra whitespace
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.clean_whitespace = clean_whitespace

    def load_file(self, filepath: str) -> List[Document]:
        """
        Load documents from file.

        Args:
            filepath: Path to file

        Returns:
            List of Document objects

        Example:
            >>> loader = DocumentLoader()
            >>> docs = loader.load_file("data/sample.txt")
        """
        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        # Determine file type and load accordingly
        if filepath.suffix == '.txt':
            return self._load_text_file(filepath)
        elif filepath.suffix == '.md':
            return self._load_markdown_file(filepath)
        elif filepath.suffix == '.json':
            return self._load_json_file(filepath)
        else:
            # Try loading as text
            return self._load_text_file(filepath)

    def _load_text_file(self, filepath: Path) -> List[Document]:
        """Load plain text file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()

        if self.clean_whitespace:
            text = clean_text(text)

        # Split into chunks
        chunks = chunk_text(
            text,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )

        # Create Document objects
        documents = []
        for i, chunk in enumerate(chunks):
            doc = Document(
                content=chunk,
                metadata={
                    'source': str(filepath),
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'file_type': 'text'
                }
            )
            documents.append(doc)

        return documents

    def _load_markdown_file(self, filepath: Path) -> List[Document]:
        """Load markdown file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()

        if self.clean_whitespace:
            text = clean_text(text)

        # For markdown, try to split on headers first
        chunks = chunk_text(
            text,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separator='\n## '  # Split on H2 headers
        )

        documents = []
        for i, chunk in enumerate(chunks):
            doc = Document(
                content=chunk,
                metadata={
                    'source': str(filepath),
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'file_type': 'markdown'
                }
            )
            documents.append(doc)

        return documents

    def _load_json_file(self, filepath: Path) -> List[Document]:
        """
        Load JSON file.

        Expected format:
        - List of objects with 'text' or 'content' field
        - Or single object with 'documents' list
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        documents = []

        # Handle different JSON formats
        if isinstance(data, list):
            # List of document objects
            for i, item in enumerate(data):
                content = item.get('text') or item.get('content')
                if content:
                    if self.clean_whitespace:
                        content = clean_text(content)

                    # Chunk if too large
                    if len(content) > self.chunk_size:
                        chunks = chunk_text(
                            content,
                            chunk_size=self.chunk_size,
                            chunk_overlap=self.chunk_overlap
                        )
                        for j, chunk in enumerate(chunks):
                            doc = Document(
                                content=chunk,
                                metadata={
                                    'source': str(filepath),
                                    'document_index': i,
                                    'chunk_index': j,
                                    'file_type': 'json',
                                    **{k: v for k, v in item.items()
                                       if k not in ['text', 'content']}
                                }
                            )
                            documents.append(doc)
                    else:
                        doc = Document(
                            content=content,
                            metadata={
                                'source': str(filepath),
                                'document_index': i,
                                'file_type': 'json',
                                **{k: v for k, v in item.items()
                                   if k not in ['text', 'content']}
                            }
                        )
                        documents.append(doc)

        elif isinstance(data, dict):
            # Single document or nested structure
            if 'documents' in data:
                # Recursively process documents list
                for i, item in enumerate(data['documents']):
                    content = item.get('text') or item.get('content')
                    if content:
                        doc = Document(
                            content=content,
                            metadata={
                                'source': str(filepath),
                                'document_index': i,
                                'file_type': 'json',
                                **{k: v for k, v in item.items()
                                   if k not in ['text', 'content']}
                            }
                        )
                        documents.append(doc)
            else:
                # Single document
                content = data.get('text') or data.get('content')
                if content:
                    doc = Document(
                        content=content,
                        metadata={
                            'source': str(filepath),
                            'file_type': 'json',
                            **{k: v for k, v in data.items()
                               if k not in ['text', 'content']}
                        }
                    )
                    documents.append(doc)

        return documents

    def load_text(self, text: str, metadata: Optional[Dict] = None) -> List[Document]:
        """
        Load from raw text string.

        Args:
            text: Text content
            metadata: Optional metadata dict

        Returns:
            List of Document objects

        Example:
            >>> loader = DocumentLoader()
            >>> text = "Context engineering is..."
            >>> docs = loader.load_text(text, metadata={'source': 'manual'})
        """
        if self.clean_whitespace:
            text = clean_text(text)

        chunks = chunk_text(
            text,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )

        documents = []
        for i, chunk in enumerate(chunks):
            doc = Document(
                content=chunk,
                metadata={
                    'source': 'direct_input',
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    **(metadata or {})
                }
            )
            documents.append(doc)

        return documents

    def load_multiple_files(self, filepaths: List[str]) -> List[Document]:
        """
        Load multiple files.

        Args:
            filepaths: List of file paths

        Returns:
            Combined list of Document objects

        Example:
            >>> loader = DocumentLoader()
            >>> docs = loader.load_multiple_files(['doc1.txt', 'doc2.txt'])
        """
        all_documents = []

        for filepath in filepaths:
            try:
                documents = self.load_file(filepath)
                all_documents.extend(documents)
            except Exception as e:
                print(f"Warning: Failed to load {filepath}: {e}")
                continue

        return all_documents


# ============================================================================
# Example Usage
# ============================================================================

def example_document_loading():
    """Example of loading documents."""
    print("Document Loader Example")
    print("=" * 60)

    # Create loader
    loader = DocumentLoader(chunk_size=200, chunk_overlap=30)

    # Example 1: Load from text
    sample_text = """
    Context engineering is the delicate art and science of filling the context
    window with just the right information for the next step.

    The mathematical foundation includes four key pillars:
    1. Context Formalization: C = A(c₁, c₂, ..., c₆)
    2. Optimization Theory: F* = arg max E[Reward(C)]
    3. Information Theory: I(Context; Query)
    4. Bayesian Inference: P(Strategy|Evidence)

    Practical applications include RAG systems, memory management,
    tool-integrated reasoning, and multi-agent coordination.
    """

    print("\nLoading from text string...")
    documents = loader.load_text(sample_text)

    print(f"Created {len(documents)} document chunks:")
    for i, doc in enumerate(documents, 1):
        print(f"\nChunk {i}:")
        print(f"  Content length: {len(doc.content)} chars")
        print(f"  Token count: {doc.token_count}")
        print(f"  Preview: {doc.content[:80]}...")
        print(f"  Metadata: {doc.metadata}")

    # Example 2: Demonstrate metadata
    print("\n" + "=" * 60)
    print("Document with custom metadata:")
    custom_docs = loader.load_text(
        "This is a custom document.",
        metadata={'author': 'Example', 'importance': 'high'}
    )
    print(f"Metadata: {custom_docs[0].metadata}")

    print("\n" + "=" * 60)
    print("Document loading complete!")


if __name__ == "__main__":
    example_document_loading()
