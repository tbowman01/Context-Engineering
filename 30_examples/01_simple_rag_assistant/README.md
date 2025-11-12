# Simple RAG Assistant Example
## Context Engineering in Action

This example demonstrates a complete **Retrieval-Augmented Generation (RAG)** system built with context engineering principles.

---

## Overview

This RAG assistant shows how to:
- Build a vector store from documents
- Retrieve relevant context for queries
- Assemble optimal context windows
- Generate responses using LLMs
- Monitor performance and memory usage

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   RAG ASSISTANT                         │
└─────────────────────────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
     ┌────▼────┐     ┌────▼────┐    ┌────▼────┐
     │ Document│     │ Vector  │    │ Context │
     │ Loader  │────▶│  Store  │◀───│Assembly │
     └─────────┘     └─────────┘    └────┬────┘
                          │               │
                     ┌────▼────┐     ┌────▼────┐
                     │Retriever│────▶│   LLM   │
                     └─────────┘     └─────────┘
```

## Features

✅ **Document Processing** - Load and chunk documents
✅ **Vector Storage** - Efficient similarity search
✅ **Context Assembly** - Optimized context windows
✅ **LLM Integration** - OpenAI/Anthropic support
✅ **Performance Monitoring** - Real-time metrics
✅ **Memory Profiling** - Memory usage tracking

---

## Installation

### Prerequisites

- Python 3.10+
- OpenAI API key (or Anthropic)

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
export OPENAI_API_KEY="your-key-here"

# Or use .env file
echo "OPENAI_API_KEY=your-key-here" > .env
```

---

## Quick Start

### 1. Run with Sample Data

```bash
# Run the example
python main.py

# Or with custom documents
python main.py --docs data/your_documents.txt
```

### 2. Interactive Mode

```python
from src.rag_assistant import RAGAssistant

# Create assistant
assistant = RAGAssistant()

# Load documents
assistant.load_documents("data/sample_docs.txt")

# Ask questions
response = assistant.query("What is context engineering?")
print(response)
```

### 3. With Performance Monitoring

```python
from src.rag_assistant import RAGAssistant
from performance_monitor import PerformanceMonitor

monitor = PerformanceMonitor()
assistant = RAGAssistant(monitor=monitor)

# Use assistant
response = assistant.query("Your question here")

# Check performance
monitor.print_summary()
```

---

## Project Structure

```
01_simple_rag_assistant/
├── README.md              # This file
├── main.py               # Entry point
├── requirements.txt      # Dependencies
├── config.yaml           # Configuration
├── src/
│   ├── __init__.py
│   ├── rag_assistant.py  # Main RAG class
│   ├── document_loader.py # Document processing
│   ├── vector_store.py   # Vector storage
│   ├── context_assembler.py # Context assembly
│   └── utils.py          # Utilities
├── data/
│   └── sample_docs.txt   # Sample documents
├── outputs/
│   └── .gitkeep         # Output directory
└── tests/
    └── test_rag.py      # Unit tests
```

---

## Usage Examples

### Example 1: Basic Question Answering

```python
from src.rag_assistant import RAGAssistant

# Initialize
assistant = RAGAssistant()

# Load knowledge base
assistant.load_documents("data/python_docs.txt")

# Ask question
response = assistant.query(
    "How do I create a list comprehension in Python?"
)

print(response)
```

**Output:**
```
A list comprehension in Python is created using the syntax:
[expression for item in iterable if condition]

For example:
squares = [x**2 for x in range(10)]

This creates a list of squares from 0 to 81.
```

### Example 2: With Context Optimization

```python
# Enable context optimization
assistant = RAGAssistant(
    max_context_tokens=500,
    optimize_context=True
)

# Query with optimization
response = assistant.query(
    "Explain Python decorators",
    num_results=5,  # Retrieve top 5 relevant chunks
    rerank=True     # Re-rank by relevance
)
```

### Example 3: Multi-Query Conversation

```python
# Enable conversation memory
assistant = RAGAssistant(memory_enabled=True)

# Query 1
assistant.query("What is a Python decorator?")

# Query 2 (uses conversation context)
assistant.query("Can you show me an example?")

# Query 3 (continues conversation)
assistant.query("How do I add arguments to it?")
```

---

## Configuration

Edit `config.yaml` to customize:

```yaml
# Vector Store Settings
vector_store:
  type: "chroma"  # or "faiss"
  embedding_model: "text-embedding-ada-002"
  chunk_size: 500
  chunk_overlap: 50

# Context Assembly
context:
  max_tokens: 2000
  strategy: "weighted"  # linear, weighted, hierarchical
  prioritize_recent: true

# LLM Settings
llm:
  provider: "openai"  # or "anthropic"
  model: "gpt-3.5-turbo"
  temperature: 0.7
  max_tokens: 500

# Performance
performance:
  enable_monitoring: true
  enable_memory_profiling: false
  log_queries: true
```

---

## Advanced Features

### 1. Custom Document Loaders

```python
from src.document_loader import DocumentLoader

# PDF loader
loader = DocumentLoader(file_type="pdf")
docs = loader.load("document.pdf")

# Web scraper
loader = DocumentLoader(file_type="web")
docs = loader.load("https://example.com")
```

### 2. Custom Context Assembly

```python
from src.context_assembler import ContextAssembler

assembler = ContextAssembler(
    max_tokens=1000,
    strategy="hierarchical"
)

# Assemble with custom logic
context = assembler.assemble(
    retrieved_docs=docs,
    query=query,
    conversation_history=history
)
```

### 3. Performance Optimization

```python
# Enable caching
assistant = RAGAssistant(enable_cache=True)

# Batch processing
responses = assistant.batch_query([
    "Question 1?",
    "Question 2?",
    "Question 3?"
])

# Async operations
import asyncio

async def main():
    responses = await assistant.query_async([
        "Question 1?",
        "Question 2?"
    ])

asyncio.run(main())
```

---

## Performance Metrics

When running with monitoring enabled, you'll see:

```
PERFORMANCE MONITORING SUMMARY
============================================================
Operation: document_retrieval
  Count: 10
  Mean: 45.23ms
  Median: 42.10ms
  P95: 67.34ms

Operation: context_assembly
  Count: 10
  Mean: 12.45ms
  Median: 11.20ms

Operation: llm_generation
  Count: 10
  Mean: 1234.56ms
  Median: 1198.23ms
  Tokens/sec: 45.2
============================================================
```

---

## Testing

Run the test suite:

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src

# Run specific test
pytest tests/test_rag.py::test_document_loading
```

---

## Troubleshooting

### Issue: "No API key found"

**Solution:**
```bash
export OPENAI_API_KEY="your-key-here"
```

### Issue: "Vector store initialization failed"

**Solution:**
```bash
# Install ChromaDB
pip install chromadb

# Or use FAISS
pip install faiss-cpu
```

### Issue: "Memory error with large documents"

**Solution:**
```python
# Reduce chunk size in config.yaml
chunk_size: 200  # Instead of 500

# Or enable streaming
assistant = RAGAssistant(stream_mode=True)
```

---

## Performance Tips

1. **Optimize Chunk Size**
   - Smaller chunks: More precise but more retrieval calls
   - Larger chunks: Better context but slower

2. **Use Caching**
   - Cache embeddings for frequently accessed documents
   - Cache LLM responses for common queries

3. **Batch Processing**
   - Process multiple queries together
   - Reduces API calls

4. **Monitor Resource Usage**
   ```python
   from memory_profiler import MemoryProfiler

   with MemoryProfiler() as profiler:
       assistant.load_documents("large_doc.txt")
       profiler.print_report()
   ```

---

## Next Steps

After completing this example:

1. **Try Module 04** - Advanced RAG patterns
2. **Add Memory** - Integrate hierarchical memory (Module 05)
3. **Add Tools** - Tool-integrated reasoning (Module 06)
4. **Scale Up** - Multi-agent systems (Module 07)

---

## Resources

- [RAG Paper](https://arxiv.org/abs/2005.11401)
- [Context Engineering Survey](https://arxiv.org/pdf/2507.13334)
- [LangChain RAG Tutorial](https://python.langchain.com/docs/use_cases/question_answering/)

---

## License

MIT License - See main repository LICENSE file

---

## Contributing

Found a bug or want to improve this example?

1. Fork the repository
2. Create your feature branch
3. Submit a pull request

---

**Built with Context Engineering principles** 🚀
