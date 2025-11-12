# Quick Start - Context Engineering in 30 Minutes

> **"Context engineering is the delicate art and science of filling the context window with just the right information for the next step."** — Andrej Karpathy

Welcome! This guide will get you started with Context Engineering in just 30 minutes.

---

## Table of Contents

1. [What is Context Engineering?](#what-is-context-engineering)
2. [Installation](#installation)
3. [Your First Context Engineering Example](#your-first-example)
4. [Core Concepts](#core-concepts)
5. [Next Steps](#next-steps)

---

## What is Context Engineering?

Context Engineering goes **beyond prompt engineering**. While prompts are what you say to the model, context engineering is about **everything else the model sees**:

```
Traditional Prompt Engineering:
┌────────────────────┐
│ "Write a poem"     │  ← Just the instruction
└────────────────────┘

Context Engineering:
┌─────────────────────────────────────────┐
│ System Instructions                      │  ← c₁
│ External Knowledge                       │  ← c₂
│ Available Tools                          │  ← c₃
│ Memory/History                           │  ← c₄
│ Current State                            │  ← c₅
│ User Query: "Write a poem"               │  ← c₆
└─────────────────────────────────────────┘

Mathematical Form: C = A(c₁, c₂, c₃, c₄, c₅, c₆)
```

---

## Installation

### Prerequisites

- **Python 3.10+**
- Basic understanding of LLMs
- Jupyter Lab or VS Code (recommended)

### Step 1: Clone the Repository

```bash
git clone https://github.com/davidkimai/Context-Engineering.git
cd Context-Engineering
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Or install the package in development mode
pip install -e .
```

### Step 4: Set Up API Keys (Optional)

Create a `.env` file in the project root:

```bash
# .env
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
```

**Note:** Most examples work without API keys for learning purposes.

---

## Your First Example

Let's start with a simple context engineering demonstration using the mathematical foundations.

### Example 1: Context Assembly

Create a file `my_first_context.py` or run in Jupyter:

```python
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class ContextComponent:
    """A single piece of context."""
    component_type: str
    content: str
    relevance_score: float  # 0.0 to 1.0
    token_count: int

# Define context components
components = [
    ContextComponent(
        component_type="instructions",
        content="You are a helpful AI assistant specializing in Python programming.",
        relevance_score=0.9,
        token_count=20
    ),
    ContextComponent(
        component_type="knowledge",
        content="Python uses indentation for code blocks. Functions are defined with 'def'.",
        relevance_score=0.8,
        token_count=30
    ),
    ContextComponent(
        component_type="memory",
        content="User previously asked about list comprehensions.",
        relevance_score=0.7,
        token_count=15
    ),
    ContextComponent(
        component_type="query",
        content="How do I create a dictionary comprehension in Python?",
        relevance_score=1.0,
        token_count=20
    )
]

# Assemble context (simple concatenation)
def assemble_context_simple(components: List[ContextComponent], max_tokens: int = 100):
    """Simple context assembly function."""
    result = []
    total_tokens = 0

    # Sort by relevance
    sorted_components = sorted(components, key=lambda c: c.relevance_score, reverse=True)

    for component in sorted_components:
        if total_tokens + component.token_count <= max_tokens:
            result.append(f"[{component.component_type.upper()}]")
            result.append(component.content)
            result.append("")  # Blank line
            total_tokens += component.token_count

    return "\n".join(result), total_tokens

# Run assembly
assembled_context, tokens_used = assemble_context_simple(components, max_tokens=100)

print("=" * 60)
print("ASSEMBLED CONTEXT")
print("=" * 60)
print(assembled_context)
print("=" * 60)
print(f"Tokens used: {tokens_used} / 100")
print(f"Efficiency: {tokens_used/100:.1%}")
```

**Expected Output:**
```
============================================================
ASSEMBLED CONTEXT
============================================================
[QUERY]
How do I create a dictionary comprehension in Python?

[INSTRUCTIONS]
You are a helpful AI assistant specializing in Python programming.

[KNOWLEDGE]
Python uses indentation for code blocks. Functions are defined with 'def'.

[MEMORY]
User previously asked about list comprehensions.

============================================================
Tokens used: 85 / 100
Efficiency: 85.0%
```

### Example 2: Using the Mathematical Foundations Lab

The repository includes a comprehensive lab demonstrating all four mathematical pillars:

```bash
# Navigate to the mathematical foundations
cd 00_COURSE/00_mathematical_foundations/exercises

# Run the interactive lab
python math_foundations_lab.py
```

This will demonstrate:
1. **Context Formalization**: C = A(c₁, c₂, ..., c₆)
2. **Optimization Theory**: Finding optimal assembly strategies
3. **Information Theory**: Measuring relevance and redundancy
4. **Bayesian Inference**: Learning from feedback

---

## Core Concepts

### The Biological Metaphor

Context Engineering follows a progression from simple to complex:

```
Level 1: ATOMS          →  Single prompts
Level 2: MOLECULES      →  Few-shot learning
Level 3: CELLS          →  Memory + state
Level 4: ORGANS         →  Multi-agent systems
Level 5: NEURAL         →  Cognitive tools
Level 6: FIELDS         →  Persistent context fields
```

### The Four Mathematical Pillars

1. **Context Formalization**
   ```
   C = A(c₁, c₂, c₃, c₄, c₅, c₆)
   ```
   Systematic assembly of context components

2. **Optimization Theory**
   ```
   F* = arg max E[Reward(C)]
   ```
   Finding the best assembly function

3. **Information Theory**
   ```
   I(Context; Query)
   ```
   Maximizing relevance, minimizing redundancy

4. **Bayesian Inference**
   ```
   P(Strategy|Evidence)
   ```
   Learning from feedback

### Key Components

- **c₁: Instructions** - System prompts, role definitions
- **c₂: Knowledge** - External information, facts, data
- **c₃: Tools** - Available functions, APIs, capabilities
- **c₄: Memory** - Conversation history, learned patterns
- **c₅: State** - Current situation, user context
- **c₆: Query** - Immediate user request

---

## Next Steps

### Learning Path

```
┌─────────────────┐     ┌──────────────────┐     ┌────────────────┐
│ 1. Foundations  │────▶│ 2. Retrieval &   │────▶│ 3. Processing  │
│                 │     │    Generation    │     │                │
│ Module 00       │     │ Module 01        │     │ Module 02      │
└─────────────────┘     └──────────────────┘     └────────────────┘
         │                                                │
         ▼                                                ▼
┌─────────────────┐     ┌──────────────────┐     ┌────────────────┐
│ 4. RAG Systems  │────▶│ 5. Memory        │────▶│ 6. Tools       │
│                 │     │                  │     │                │
│ Module 04       │     │ Module 05        │     │ Module 06      │
└─────────────────┘     └──────────────────┘     └────────────────┘
```

### 1. Complete Module 00: Mathematical Foundations

**Time:** 2-3 hours

Start with the mathematical foundations to understand the theory:

```bash
# Read the theory
cat 00_COURSE/00_mathematical_foundations/README.md

# Work through the lab
cd 00_COURSE/00_mathematical_foundations/exercises
python math_foundations_lab.py
```

**What you'll learn:**
- How to mathematically formalize context
- Optimization techniques for context assembly
- Information-theoretic analysis
- Bayesian learning for adaptive strategies

### 2. Explore Module 01: Context Retrieval & Generation

**Time:** 2-3 hours

Learn about prompt engineering and knowledge retrieval:

```bash
# Navigate to Module 01
cd 00_COURSE/01_context_retrieval_generation

# Read the overview
cat README.md

# Try the labs
cd labs
python prompt_engineering_lab.py
python knowledge_retrieval_lab.py
python dynamic_assembly_lab.py
```

### 3. Study the Examples

**Time:** 1-2 hours

Learn from practical implementations:

```bash
# Explore the examples directory
cd 30_examples

# Start with the toy chatbot
cd 00_toy_chatbot
cat README.md
```

### 4. Build Your Own Context Engineering System

**Time:** 4-8 hours

Apply what you've learned:

1. **Choose a domain** (e.g., code assistant, research helper, tutor)
2. **Define your context components** (instructions, knowledge, tools, etc.)
3. **Implement assembly function** (using templates from `20_templates/`)
4. **Add optimization** (using techniques from Module 00)
5. **Iterate and improve** (using evaluation from Module 09)

### 5. Explore Advanced Topics

Once you're comfortable with the basics:

- **Module 04:** RAG Systems
- **Module 05:** Memory Systems
- **Module 06:** Tool-Integrated Reasoning
- **Module 07:** Multi-Agent Systems
- **Module 08:** Field Theory Integration

---

## Additional Resources

### Documentation

- **Full Course:** [`00_COURSE/README.md`](00_COURSE/README.md)
- **Templates:** [`20_templates/`](20_templates/)
- **Reference:** [`40_reference/`](40_reference/)
- **Contributing:** [`.github/CONTRIBUTING.md`](.github/CONTRIBUTING.md)

### Research Papers

Key papers integrated into this course:

1. [Context Engineering Survey](https://arxiv.org/pdf/2507.13334) - 1400+ research papers analyzed
2. [MEM1](https://arxiv.org/pdf/2506.15841) - Memory-reasoning synergy
3. [Cognitive Tools](https://www.arxiv.org/pdf/2506.12115) - IBM Zurich
4. [Emergent Symbols](https://openreview.net/forum?id=y1SnRPDWx4) - ICML Princeton

### Community

- **Discord:** [Join the conversation](https://discord.gg/JeFENHNNNQ)
- **GitHub Discussions:** Share ideas and ask questions
- **Issues:** Report bugs or request features

---

## Troubleshooting

### Common Issues

**Issue 1: Import Errors**
```python
ModuleNotFoundError: No module named 'numpy'
```
**Solution:**
```bash
pip install -r requirements.txt
```

**Issue 2: API Key Errors**
```python
openai.error.AuthenticationError
```
**Solution:**
- Most examples work without API keys for learning
- For API examples, set up `.env` file with your keys
- Use mock/local models for practice

**Issue 3: Memory Issues with Large Examples**
```python
MemoryError
```
**Solution:**
- Start with smaller token limits
- Use the memory profiler from Module 03
- Run on a machine with more RAM

---

## Quick Reference Card

### Context Assembly Pattern
```python
# 1. Define components
components = [ContextComponent(...), ...]

# 2. Assemble context
assembled = assemble_context(components, max_tokens=N)

# 3. Send to LLM
response = llm.generate(assembled)

# 4. Learn from feedback
update_strategy(feedback_score)
```

### Component Template
```python
ContextComponent(
    component_type="<type>",      # instructions, knowledge, tools, memory, state, query
    content="<content>",           # The actual text
    relevance_score=0.X,           # 0.0 to 1.0
    token_count=N,                 # Token count
    quality_metrics={...}          # Optional metadata
)
```

### Evaluation Pattern
```python
# 1. Define metric
def evaluate_context(context, query, response):
    return quality_score

# 2. Run evaluation
score = evaluate_context(assembled, query, response)

# 3. Optimize
if score < threshold:
    optimize_assembly_strategy()
```

---

## What's Next?

You've completed the quick start! Here's what to do next:

✅ **Completed:** Basic understanding of context engineering
✅ **Completed:** First working example
✅ **Completed:** Installation and setup

📚 **Next:** Choose your learning path:
- **Theoretical:** Deep dive into Module 00
- **Practical:** Build examples from scratch
- **Advanced:** Explore RAG, Memory, Multi-Agent systems

🚀 **Ready to build something amazing?** Start with Module 01 and work your way up!

---

## Get Help

- **Questions?** Open a [GitHub Discussion](https://github.com/davidkimai/Context-Engineering/discussions)
- **Found a bug?** Create an [Issue](https://github.com/davidkimai/Context-Engineering/issues)
- **Want to contribute?** Check [CONTRIBUTING.md](.github/CONTRIBUTING.md)

---

**Welcome to the future of LLM interaction. Happy context engineering!** 🎉
