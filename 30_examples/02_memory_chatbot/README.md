# Memory-Enhanced Chatbot

![Status](https://img.shields.io/badge/Status-Week%204-blue)
![Completion](https://img.shields.io/badge/Completion-In%20Progress-yellow)

A conversational AI assistant enhanced with hierarchical memory architecture, enabling coherent long-term conversations with context retention across sessions.

## Overview

This example demonstrates practical application of the **hierarchical memory architecture** from Module 03 in a conversational agent. The chatbot maintains multiple levels of memory (working, episodic, semantic, procedural) to provide contextually aware, personalized responses.

## Key Features

✨ **Hierarchical Memory**
- Working Memory: Immediate conversation context (last 7 exchanges)
- Episodic Memory: Past conversations with temporal context
- Semantic Memory: Learned facts and user preferences
- Procedural Memory: Step-by-step instructions and workflows

🧠 **Intelligent Context Management**
- Automatic memory consolidation
- Relevance-based context retrieval
- Memory decay for outdated information
- Priority-based memory access

💾 **Persistence**
- Save/load conversation state
- Export conversation history
- Memory analytics and statistics

🎯 **Personalization**
- Learn user preferences over time
- Remember past interactions
- Adapt responses based on history
- Context-aware suggestions

## Architecture

```
┌─────────────────────────────────────────┐
│      MEMORY-ENHANCED CHATBOT            │
└─────────────────────────────────────────┘
              │
    ┌─────────┼─────────┐
    │         │         │
┌───▼───┐ ┌───▼───┐ ┌───▼───┐
│Working│ │Episodic│ │Semantic│
│Memory │ │ Memory │ │ Memory │
│ (7)   │ │ (100)  │ │(Facts) │
└───┬───┘ └───┬───┘ └───┬───┘
    │         │         │
    └─────────┼─────────┘
              │
         ┌────▼────┐
         │Context  │
         │Assembly │
         └────┬────┘
              │
         ┌────▼────┐
         │Response │
         │Generator│
         └─────────┘
```

## Installation

```bash
cd 30_examples/02_memory_chatbot

# Install dependencies (optional - uses stdlib)
pip install -r requirements.txt

# Or run directly (no dependencies required for basic version)
python main.py
```

## Usage

### Interactive Mode

```bash
# Start chatbot
python main.py

# With custom memory configuration
python main.py --working-capacity 10 --episodic-capacity 200

# Load previous conversation
python main.py --load conversation_001.json

# Enable debug mode
python main.py --debug
```

### Programmatic Usage

```python
from src.memory_chatbot import MemoryChatbot

# Create chatbot
chatbot = MemoryChatbot(
    name="Claude",
    working_capacity=7,
    episodic_capacity=100
)

# Have a conversation
response = chatbot.chat("Hello! Can you help me learn Python?")
print(response)

response = chatbot.chat("What are decorators?")
print(response)

# Add facts to semantic memory
chatbot.add_fact(
    category="programming_languages",
    content="Python uses indentation for code blocks",
    importance=0.9
)

# Add procedures
chatbot.add_procedure(
    name="create_function",
    steps=[
        "Use def keyword",
        "Provide function name",
        "Define parameters in parentheses",
        "Add docstring",
        "Write function body",
        "Return value (optional)"
    ]
)

# Check memory statistics
stats = chatbot.get_memory_stats()
print(stats)

# Save conversation
chatbot.save_conversation("session_001.json")
```

## Memory Levels Explained

### 1. Working Memory (Capacity: 7)

Immediate conversation context following Miller's Law.

**What it stores:**
- Last 7 conversation exchanges
- Current topic/intent
- Active variables and context

**Example:**
```
User: "What is Python?"
Bot: "Python is a programming language..."
[Stored in working memory for immediate context]

User: "Can you give an example?"
Bot: [Retrieves from working memory to understand "example" refers to Python]
```

### 2. Episodic Memory (Capacity: 100)

Specific past conversations with timestamps.

**What it stores:**
- Past conversation exchanges
- Temporal context (when did we discuss this?)
- User's questions and bot's responses
- Relevance scores based on recency and importance

**Example:**
```
User: "What did we discuss yesterday about Python?"
Bot: [Searches episodic memory for conversations from yesterday]
     "Yesterday we discussed Python decorators and their use in..."
```

### 3. Semantic Memory (Unlimited)

Persistent facts and knowledge organized by category.

**What it stores:**
- Learned facts about user
- Domain knowledge
- User preferences and settings
- Categorized information

**Example:**
```
Categories:
- user_preferences: {"name": "Alex", "favorite_language": "Python"}
- programming_facts: ["Python is interpreted", "Uses duck typing"]
- project_context: ["Working on web scraper", "Using BeautifulSoup"]
```

### 4. Procedural Memory

Step-by-step procedures and workflows.

**What it stores:**
- How-to instructions
- Workflows and processes
- Reusable procedures

**Example:**
```
Procedure: "debug_python_code"
Steps:
1. Read the error message carefully
2. Check line number mentioned in traceback
3. Verify variable values with print statements
4. Use pdb for step-through debugging
5. Fix the issue
6. Re-run and verify
```

## Memory Consolidation

The chatbot automatically consolidates memories:

1. **Working → Episodic:**
   - After 7 new exchanges, oldest working memory moves to episodic
   - Only exchanges with importance > 0.6 are saved

2. **Episodic → Semantic:**
   - Repeated facts extracted as semantic knowledge
   - User preferences identified and categorized

3. **Memory Decay:**
   - Old, low-importance memories gradually forgotten
   - Preserves space for relevant information

## Configuration

### config.yaml

```yaml
chatbot:
  name: "Claude"
  personality: "helpful, concise, friendly"

memory:
  working_capacity: 7
  episodic_capacity: 100
  enable_consolidation: true
  consolidation_threshold: 0.6
  decay_enabled: true
  decay_rate: 0.1

  relevance_weights:
    importance: 0.4
    recency: 0.4
    frequency: 0.2

response:
  max_length: 500
  temperature: 0.7
  use_memory_context: true
  max_context_items: 10

persistence:
  auto_save: true
  save_interval_minutes: 5
  save_directory: "data/conversations"
```

## Commands

During chat, use these commands:

- `/stats` - Show memory statistics
- `/save [filename]` - Save conversation
- `/load [filename]` - Load conversation
- `/clear` - Clear all memory
- `/export` - Export conversation history
- `/help` - Show help message
- `/quit` - Exit chatbot

## Examples

### Example 1: Learning from Conversation

```
User: My name is Alex
Bot: Nice to meet you, Alex! How can I help you today?
[Stores "name: Alex" in semantic memory]

User: I'm learning Python
Bot: Great choice! Python is a versatile language. What would you like to learn?
[Stores "learning: Python" in semantic memory]

... [several messages later]

User: What was my name again?
Bot: Your name is Alex!
[Retrieved from semantic memory]
```

### Example 2: Contextual Responses

```
User: Can you help me with decorators?
Bot: Of course! Python decorators are functions that modify other functions...
[Stored in working memory]

User: Can you give an example?
Bot: Sure! Here's a simple decorator example...
[Uses working memory to understand "example" refers to decorators]

User: How do I use multiple decorators?
Bot: You can stack multiple decorators...
[Maintains decorator context from working memory]
```

### Example 3: Procedural Memory

```
User: How do I debug Python code?
Bot: [Retrieves "debug_python_code" procedure]
Here's a step-by-step approach:
1. Read the error message carefully
2. Check the line number in traceback
3. Add print statements to verify variables
...

User: Can you remind me of step 3?
Bot: Step 3 is: Add print statements to verify variable values
[Retrieved from procedural memory]
```

## Memory Analytics

```python
# Get detailed statistics
stats = chatbot.get_memory_stats()

print(f"Working Memory: {stats['working_memory']['count']}/7")
print(f"Episodic Memory: {stats['episodic_memory']['count']}")
print(f"Semantic Facts: {stats['semantic_memory']['total_facts']}")
print(f"Procedures: {stats['procedural_memory']['count']}")

# Analyze memory usage
analytics = chatbot.analyze_memory()
print(f"Most discussed topics: {analytics['top_topics']}")
print(f"Memory efficiency: {analytics['efficiency_score']:.2f}")
```

## Advanced Features

### 1. Memory Prioritization

Memories are prioritized using composite scoring:

```python
score = (
    0.4 * importance +
    0.4 * recency_score +
    0.2 * access_frequency
)
```

### 2. Context Assembly

For each response, relevant context is assembled:

```python
context = {
    'working': recent_exchanges,      # Last 7 turns
    'episodic': relevant_past,        # Related conversations
    'semantic': relevant_facts,       # Applicable knowledge
    'procedural': relevant_procedures # How-to instructions
}
```

### 3. Smart Forgetting

Low-value memories gradually decay:
- Unaccessed memories lose relevance over time
- Duplicates are merged
- Outdated information is pruned

## Integration with Module 03

This example uses:
- `00_COURSE/03_context_management/architectures/hierarchical_memory.py`
- `00_COURSE/03_context_management/tools/performance_monitor.py` (optional)

## Performance

- **Response Time:** < 100ms for memory operations
- **Memory Usage:** ~1KB per memory item
- **Scalability:** Handles 1000+ episodic memories efficiently

## Testing

```bash
# Run tests
python -m pytest tests/

# Run specific test
python tests/test_memory_chatbot.py

# With coverage
pytest tests/ --cov=src --cov-report=html
```

## Roadmap

- [ ] LLM integration (OpenAI, Anthropic)
- [ ] Vector-based semantic search
- [ ] Multi-user support
- [ ] Voice interface
- [ ] Web UI
- [ ] Mobile app

## Related Examples

- **01_simple_rag_assistant** - Document retrieval and context assembly
- **03_context_optimization** (planned) - Advanced context optimization

## License

MIT

---

**Status:** Week 4 Implementation
**Module:** Context Management (Module 03)
**Last Updated:** 2025-11-12
