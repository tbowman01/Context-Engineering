"""
Simple RAG Assistant - Context Engineering Example
===================================================

A complete Retrieval-Augmented Generation system demonstrating
context engineering principles in action.

Author: Context Engineering Contributors
License: MIT
"""

__version__ = "0.1.0"

from .rag_assistant import RAGAssistant
from .document_loader import DocumentLoader
from .vector_store import VectorStore
from .context_assembler import ContextAssembler

__all__ = [
    "RAGAssistant",
    "DocumentLoader",
    "VectorStore",
    "ContextAssembler",
]
