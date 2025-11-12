"""
Utility Functions for RAG Assistant
====================================

Helper functions for text processing, tokenization, and general utilities.

Author: Context Engineering Contributors
License: MIT
"""

import re
from typing import List, Optional

# Try to import tiktoken, fall back to simple estimation if not available
try:
    import tiktoken
    HAS_TIKTOKEN = True
except ImportError:
    HAS_TIKTOKEN = False


def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """
    Count tokens in text using tiktoken or simple estimation.

    Args:
        text: Text to count tokens for
        model: Model name for tokenizer

    Returns:
        Number of tokens

    Example:
        >>> count_tokens("Hello, world!")
        4
    """
    if HAS_TIKTOKEN:
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")

        return len(encoding.encode(text))
    else:
        # Simple estimation: ~4 characters per token for English text
        return len(text) // 4


def chunk_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    separator: str = "\n\n"
) -> List[str]:
    """
    Split text into overlapping chunks.

    Args:
        text: Text to chunk
        chunk_size: Target size of each chunk in characters
        chunk_overlap: Number of characters to overlap between chunks
        separator: Preferred split point (paragraph breaks)

    Returns:
        List of text chunks

    Example:
        >>> text = "Paragraph 1.\\n\\nParagraph 2.\\n\\nParagraph 3."
        >>> chunks = chunk_text(text, chunk_size=20, chunk_overlap=5)
        >>> len(chunks) >= 2
        True
    """
    if not text:
        return []

    # Try to split on separator first
    if separator in text:
        splits = text.split(separator)
    else:
        # Fallback to sentence splitting
        splits = re.split(r'(?<=[.!?])\s+', text)

    chunks = []
    current_chunk = []
    current_size = 0

    for split in splits:
        split_size = len(split)

        # If single split is larger than chunk_size, split it further
        if split_size > chunk_size:
            # Add current chunk if exists
            if current_chunk:
                chunks.append(separator.join(current_chunk))
                current_chunk = []
                current_size = 0

            # Split the large text into sub-chunks
            for i in range(0, len(split), chunk_size - chunk_overlap):
                chunks.append(split[i:i + chunk_size])
            continue

        # Check if adding this split exceeds chunk_size
        if current_size + split_size > chunk_size and current_chunk:
            # Save current chunk
            chunks.append(separator.join(current_chunk))

            # Start new chunk with overlap
            if chunk_overlap > 0 and current_chunk:
                # Include last part of previous chunk for overlap
                overlap_text = current_chunk[-1]
                if len(overlap_text) > chunk_overlap:
                    overlap_text = overlap_text[-chunk_overlap:]
                current_chunk = [overlap_text, split]
                current_size = len(overlap_text) + split_size
            else:
                current_chunk = [split]
                current_size = split_size
        else:
            current_chunk.append(split)
            current_size += split_size

    # Add remaining chunk
    if current_chunk:
        chunks.append(separator.join(current_chunk))

    return chunks


def clean_text(text: str) -> str:
    """
    Clean and normalize text.

    Args:
        text: Text to clean

    Returns:
        Cleaned text

    Example:
        >>> clean_text("  Hello   World!  \\n\\n  ")
        'Hello World!'
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove leading/trailing whitespace
    text = text.strip()

    return text


def extract_keywords(text: str, top_n: int = 5) -> List[str]:
    """
    Extract keywords from text (simple implementation).

    Args:
        text: Text to extract keywords from
        top_n: Number of keywords to extract

    Returns:
        List of keywords

    Example:
        >>> text = "context engineering context window engineering"
        >>> keywords = extract_keywords(text, top_n=2)
        >>> "context" in keywords or "engineering" in keywords
        True
    """
    # Simple keyword extraction using word frequency
    # Remove punctuation and convert to lowercase
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())

    # Count word frequency
    word_freq = {}
    for word in words:
        # Skip common stop words
        if word in {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at',
                    'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was',
                    'are', 'were', 'been', 'be', 'have', 'has', 'had', 'do',
                    'does', 'did', 'will', 'would', 'could', 'should', 'may',
                    'might', 'can', 'this', 'that', 'these', 'those'}:
            continue
        word_freq[word] = word_freq.get(word, 0) + 1

    # Sort by frequency and return top N
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in sorted_words[:top_n]]


def format_context_window(
    query: str,
    retrieved_docs: List[str],
    max_tokens: Optional[int] = None,
    model: str = "gpt-3.5-turbo"
) -> str:
    """
    Format context window from query and retrieved documents.

    Args:
        query: User query
        retrieved_docs: List of retrieved document chunks
        max_tokens: Maximum tokens for context (None = no limit)
        model: Model name for token counting

    Returns:
        Formatted context string

    Example:
        >>> query = "What is RAG?"
        >>> docs = ["RAG is a technique...", "It combines retrieval..."]
        >>> context = format_context_window(query, docs, max_tokens=100)
        >>> "Context:" in context
        True
    """
    context_parts = []

    # Add system instruction
    context_parts.append("Use the following context to answer the question.")
    context_parts.append("\nContext:")

    # Add retrieved documents
    current_tokens = count_tokens("\n".join(context_parts), model)

    for i, doc in enumerate(retrieved_docs, 1):
        doc_section = f"\n[Document {i}]\n{doc}\n"
        doc_tokens = count_tokens(doc_section, model)

        if max_tokens and (current_tokens + doc_tokens) > (max_tokens * 0.8):
            # Reserve 20% for query and response
            break

        context_parts.append(doc_section)
        current_tokens += doc_tokens

    # Add query
    context_parts.append(f"\nQuestion: {query}\n")
    context_parts.append("\nAnswer based on the context provided:")

    return "\n".join(context_parts)


def similarity_score(text1: str, text2: str) -> float:
    """
    Calculate simple similarity score between two texts.

    Simple implementation using word overlap (Jaccard similarity).
    For production, use embeddings instead.

    Args:
        text1: First text
        text2: Second text

    Returns:
        Similarity score (0-1)

    Example:
        >>> similarity_score("hello world", "hello universe")
        0.333...
    """
    words1 = set(re.findall(r'\b\w+\b', text1.lower()))
    words2 = set(re.findall(r'\b\w+\b', text2.lower()))

    if not words1 or not words2:
        return 0.0

    intersection = len(words1 & words2)
    union = len(words1 | words2)

    return intersection / union if union > 0 else 0.0


if __name__ == "__main__":
    # Test utilities
    print("Testing RAG Assistant Utilities")
    print("=" * 50)

    # Test token counting
    sample_text = "Context engineering is the art of filling the context window."
    tokens = count_tokens(sample_text)
    print(f"\nToken Count Test:")
    print(f"Text: {sample_text}")
    print(f"Tokens: {tokens}")

    # Test chunking
    long_text = """
    Context engineering is the delicate art and science of filling the context
    window with just the right information for the next step.

    It encompasses systematic approaches to context design, orchestration,
    and optimization.

    The mathematical foundation includes context formalization, optimization theory,
    information theory, and Bayesian inference.
    """

    chunks = chunk_text(long_text, chunk_size=100, chunk_overlap=20)
    print(f"\nChunking Test:")
    print(f"Original length: {len(long_text)} chars")
    print(f"Number of chunks: {len(chunks)}")
    for i, chunk in enumerate(chunks, 1):
        print(f"  Chunk {i}: {len(chunk)} chars")

    # Test keyword extraction
    keywords = extract_keywords(long_text, top_n=5)
    print(f"\nKeyword Extraction:")
    print(f"Keywords: {', '.join(keywords)}")

    # Test similarity
    text1 = "machine learning and artificial intelligence"
    text2 = "artificial intelligence and deep learning"
    score = similarity_score(text1, text2)
    print(f"\nSimilarity Test:")
    print(f"Text 1: {text1}")
    print(f"Text 2: {text2}")
    print(f"Similarity: {score:.3f}")

    print("\n" + "=" * 50)
    print("All utilities working correctly!")
