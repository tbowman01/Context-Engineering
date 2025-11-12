"""
Hierarchical Memory Architecture for Context Engineering
=========================================================

Multi-level memory system inspired by human memory: short-term (working),
episodic (events), semantic (facts), and procedural (skills).

Author: Context Engineering Contributors
License: MIT
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from collections import deque
import time
import json
from pathlib import Path


@dataclass
class MemoryItem:
    """
    Single memory item with metadata.

    Attributes:
        content: The actual content (text, data, etc.)
        timestamp: When it was created
        access_count: Number of times accessed
        last_access: Last access timestamp
        importance: Importance score (0-1)
        memory_type: Type of memory (working, episodic, semantic, procedural)
        metadata: Additional custom data
    """

    content: Any
    timestamp: float = field(default_factory=time.time)
    access_count: int = 0
    last_access: float = field(default_factory=time.time)
    importance: float = 0.5
    memory_type: str = "working"
    metadata: Dict = field(default_factory=dict)

    def access(self):
        """Record an access to this memory item."""
        self.access_count += 1
        self.last_access = time.time()

    def get_recency_score(self) -> float:
        """
        Calculate recency score (higher = more recent).

        Returns:
            Score from 0-1 based on time since last access
        """
        current_time = time.time()
        time_since_access = current_time - self.last_access

        # Decay function: score decreases exponentially with time
        # Half-life of 1 hour (3600 seconds)
        half_life = 3600
        decay_rate = 0.693 / half_life  # ln(2) / half_life

        recency_score = 2 ** (-decay_rate * time_since_access)
        return recency_score

    def get_relevance_score(self) -> float:
        """
        Calculate overall relevance score combining importance, recency, and access frequency.

        Returns:
            Composite relevance score (0-1)
        """
        # Weight the different factors
        importance_weight = 0.4
        recency_weight = 0.4
        frequency_weight = 0.2

        # Normalize access count (assume max of 100 accesses)
        frequency_score = min(self.access_count / 100.0, 1.0)

        relevance = (
            importance_weight * self.importance
            + recency_weight * self.get_recency_score()
            + frequency_weight * frequency_score
        )

        return relevance

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "content": str(self.content),
            "timestamp": self.timestamp,
            "access_count": self.access_count,
            "last_access": self.last_access,
            "importance": self.importance,
            "memory_type": self.memory_type,
            "metadata": self.metadata,
        }


class WorkingMemory:
    """
    Working memory (short-term): Limited capacity, fast access.

    Analogous to human working memory - holds immediate context
    needed for current task. Limited to recent items.
    """

    def __init__(self, capacity: int = 7):
        """
        Initialize working memory.

        Args:
            capacity: Maximum number of items (default 7, Miller's Law)
        """
        self.capacity = capacity
        self.items: deque = deque(maxlen=capacity)

    def add(self, content: Any, importance: float = 0.5, **metadata):
        """
        Add item to working memory.

        Args:
            content: Content to store
            importance: Importance score
            **metadata: Additional metadata
        """
        item = MemoryItem(
            content=content,
            importance=importance,
            memory_type="working",
            metadata=metadata,
        )
        self.items.append(item)

    def get_all(self) -> List[MemoryItem]:
        """Get all items in working memory."""
        return list(self.items)

    def get_recent(self, n: int = 3) -> List[MemoryItem]:
        """
        Get N most recent items.

        Args:
            n: Number of items to retrieve

        Returns:
            List of recent memory items
        """
        return list(self.items)[-n:]

    def clear(self):
        """Clear working memory."""
        self.items.clear()

    def __len__(self):
        return len(self.items)


class EpisodicMemory:
    """
    Episodic memory: Stores specific events and experiences.

    Remembers "what happened when" - autobiographical memory
    of specific events with temporal context.
    """

    def __init__(self, max_episodes: int = 100):
        """
        Initialize episodic memory.

        Args:
            max_episodes: Maximum number of episodes to retain
        """
        self.max_episodes = max_episodes
        self.episodes: List[MemoryItem] = []

    def add_episode(self, content: Any, importance: float = 0.5, **metadata):
        """
        Add new episode to episodic memory.

        Args:
            content: Episode content
            importance: Importance score
            **metadata: Additional metadata (e.g., context, participants)
        """
        episode = MemoryItem(
            content=content,
            importance=importance,
            memory_type="episodic",
            metadata=metadata,
        )
        self.episodes.append(episode)

        # Prune if exceeding capacity
        if len(self.episodes) > self.max_episodes:
            self._prune_episodes()

    def _prune_episodes(self):
        """Prune least relevant episodes to maintain capacity."""
        # Sort by relevance score (ascending)
        self.episodes.sort(key=lambda e: e.get_relevance_score())

        # Keep only the most relevant episodes
        keep_count = int(self.max_episodes * 0.9)  # Keep 90%
        self.episodes = self.episodes[-keep_count:]

    def retrieve_recent(self, n: int = 5) -> List[MemoryItem]:
        """
        Retrieve N most recent episodes.

        Args:
            n: Number of episodes to retrieve

        Returns:
            List of recent episodes
        """
        return self.episodes[-n:]

    def retrieve_by_relevance(self, n: int = 5) -> List[MemoryItem]:
        """
        Retrieve N most relevant episodes.

        Args:
            n: Number of episodes to retrieve

        Returns:
            List of most relevant episodes
        """
        # Sort by relevance score (descending)
        sorted_episodes = sorted(
            self.episodes, key=lambda e: e.get_relevance_score(), reverse=True
        )
        return sorted_episodes[:n]

    def search(self, query: str, n: int = 5) -> List[MemoryItem]:
        """
        Search episodes by content similarity.

        Simple implementation using substring matching.
        Production systems would use embeddings.

        Args:
            query: Search query
            n: Number of results to return

        Returns:
            List of matching episodes
        """
        query_lower = query.lower()

        # Score episodes by query overlap
        scored_episodes = []
        for episode in self.episodes:
            content_str = str(episode.content).lower()
            if query_lower in content_str:
                # Simple scoring: count word overlap
                query_words = set(query_lower.split())
                content_words = set(content_str.split())
                overlap = len(query_words & content_words)
                scored_episodes.append((episode, overlap))

        # Sort by score and return top N
        scored_episodes.sort(key=lambda x: x[1], reverse=True)
        return [ep for ep, score in scored_episodes[:n]]

    def __len__(self):
        return len(self.episodes)


class SemanticMemory:
    """
    Semantic memory: Stores facts and general knowledge.

    Knowledge that is not tied to specific events - facts, concepts,
    meanings. Organized by topic/category.
    """

    def __init__(self):
        """Initialize semantic memory."""
        self.facts: Dict[str, List[MemoryItem]] = {}

    def add_fact(
        self, category: str, content: Any, importance: float = 0.5, **metadata
    ):
        """
        Add fact to semantic memory.

        Args:
            category: Category/topic for this fact
            content: Fact content
            importance: Importance score
            **metadata: Additional metadata
        """
        fact = MemoryItem(
            content=content,
            importance=importance,
            memory_type="semantic",
            metadata={"category": category, **metadata},
        )

        if category not in self.facts:
            self.facts[category] = []

        self.facts[category].append(fact)

    def get_by_category(self, category: str) -> List[MemoryItem]:
        """
        Retrieve all facts in a category.

        Args:
            category: Category to retrieve

        Returns:
            List of facts in that category
        """
        return self.facts.get(category, [])

    def get_all_categories(self) -> List[str]:
        """Get list of all categories."""
        return list(self.facts.keys())

    def search_facts(self, query: str, n: int = 5) -> List[MemoryItem]:
        """
        Search facts across all categories.

        Args:
            query: Search query
            n: Number of results

        Returns:
            List of matching facts
        """
        query_lower = query.lower()
        all_facts = []

        for category, facts in self.facts.items():
            all_facts.extend(facts)

        # Simple matching
        matches = []
        for fact in all_facts:
            content_str = str(fact.content).lower()
            if query_lower in content_str:
                matches.append(fact)

        # Sort by relevance and return top N
        matches.sort(key=lambda f: f.get_relevance_score(), reverse=True)
        return matches[:n]

    def __len__(self):
        return sum(len(facts) for facts in self.facts.values())


class ProceduralMemory:
    """
    Procedural memory: Stores skills and procedures.

    "How to" knowledge - procedures, skills, habits.
    Represented as sequences of steps or patterns.
    """

    def __init__(self):
        """Initialize procedural memory."""
        self.procedures: Dict[str, MemoryItem] = {}

    def add_procedure(
        self, name: str, steps: List[str], importance: float = 0.5, **metadata
    ):
        """
        Add procedure to memory.

        Args:
            name: Procedure name
            steps: List of steps in the procedure
            importance: Importance score
            **metadata: Additional metadata
        """
        procedure = MemoryItem(
            content=steps,
            importance=importance,
            memory_type="procedural",
            metadata={"name": name, **metadata},
        )

        self.procedures[name] = procedure

    def get_procedure(self, name: str) -> Optional[MemoryItem]:
        """
        Retrieve procedure by name.

        Args:
            name: Procedure name

        Returns:
            Procedure memory item or None
        """
        return self.procedures.get(name)

    def get_all_procedures(self) -> List[str]:
        """Get list of all procedure names."""
        return list(self.procedures.keys())

    def execute_procedure(self, name: str) -> Optional[List[str]]:
        """
        Retrieve procedure steps (simulating execution).

        Args:
            name: Procedure name

        Returns:
            List of steps or None if not found
        """
        procedure = self.get_procedure(name)
        if procedure:
            procedure.access()  # Record access
            return procedure.content
        return None

    def __len__(self):
        return len(self.procedures)


class HierarchicalMemory:
    """
    Complete hierarchical memory system integrating all memory types.

    Manages information flow between different memory levels:
    - Working memory (immediate context)
    - Episodic memory (events)
    - Semantic memory (facts)
    - Procedural memory (skills)

    Example:
        >>> memory = HierarchicalMemory()
        >>> memory.add_to_working("User asked about Python")
        >>> memory.consolidate_to_episodic()
        >>> memory.add_fact("programming", "Python uses indentation")
        >>> context = memory.get_context_for_query("How do I code in Python?")
    """

    def __init__(
        self,
        working_capacity: int = 7,
        episodic_capacity: int = 100,
    ):
        """
        Initialize hierarchical memory system.

        Args:
            working_capacity: Working memory capacity
            episodic_capacity: Episodic memory capacity
        """
        self.working = WorkingMemory(capacity=working_capacity)
        self.episodic = EpisodicMemory(max_episodes=episodic_capacity)
        self.semantic = SemanticMemory()
        self.procedural = ProceduralMemory()

    def add_to_working(self, content: Any, importance: float = 0.5, **metadata):
        """
        Add item to working memory.

        Args:
            content: Content to add
            importance: Importance score
            **metadata: Additional metadata
        """
        self.working.add(content, importance, **metadata)

    def consolidate_to_episodic(self):
        """
        Consolidate working memory to episodic memory.

        Simulates memory consolidation - transferring important
        items from short-term to long-term memory.
        """
        for item in self.working.get_all():
            # Only consolidate important items
            if item.importance > 0.6:
                self.episodic.add_episode(
                    content=item.content,
                    importance=item.importance,
                    **item.metadata,
                )

    def add_fact(self, category: str, content: Any, importance: float = 0.5, **metadata):
        """Add fact to semantic memory."""
        self.semantic.add_fact(category, content, importance, **metadata)

    def add_procedure(self, name: str, steps: List[str], importance: float = 0.5):
        """Add procedure to procedural memory."""
        self.procedural.add_procedure(name, steps, importance)

    def get_context_for_query(
        self,
        query: str,
        max_items: int = 10,
    ) -> Dict[str, List[Any]]:
        """
        Retrieve relevant context from all memory levels for a query.

        Args:
            query: Query to get context for
            max_items: Maximum items to retrieve from each memory type

        Returns:
            Dictionary with context from each memory level

        Example:
            >>> context = memory.get_context_for_query("Tell me about Python")
            >>> print(context['semantic'])  # Relevant facts
            >>> print(context['episodic'])  # Relevant past conversations
        """
        context = {
            "working": [item.content for item in self.working.get_recent(3)],
            "episodic": [
                item.content for item in self.episodic.search(query, max_items // 2)
            ],
            "semantic": [
                item.content for item in self.semantic.search_facts(query, max_items // 2)
            ],
            "procedural": [],
        }

        # Add relevant procedures if query contains "how to"
        if "how to" in query.lower() or "how do" in query.lower():
            all_procedures = self.procedural.get_all_procedures()
            for proc_name in all_procedures:
                if any(word in query.lower() for word in proc_name.lower().split()):
                    proc = self.procedural.get_procedure(proc_name)
                    if proc:
                        context["procedural"].append(
                            {"name": proc_name, "steps": proc.content}
                        )

        return context

    def get_statistics(self) -> Dict:
        """Get statistics about memory usage."""
        return {
            "working_memory": {
                "count": len(self.working),
                "capacity": self.working.capacity,
                "utilization": len(self.working) / self.working.capacity,
            },
            "episodic_memory": {
                "count": len(self.episodic),
                "capacity": self.episodic.max_episodes,
            },
            "semantic_memory": {
                "count": len(self.semantic),
                "categories": len(self.semantic.get_all_categories()),
            },
            "procedural_memory": {
                "count": len(self.procedural),
            },
        }

    def print_statistics(self):
        """Print formatted memory statistics."""
        stats = self.get_statistics()

        print("\n" + "=" * 60)
        print("HIERARCHICAL MEMORY STATISTICS")
        print("=" * 60)

        print("\nWorking Memory:")
        print(f"  Items: {stats['working_memory']['count']}/{stats['working_memory']['capacity']}")
        print(f"  Utilization: {stats['working_memory']['utilization']:.1%}")

        print("\nEpisodic Memory:")
        print(f"  Episodes: {stats['episodic_memory']['count']}")

        print("\nSemantic Memory:")
        print(f"  Facts: {stats['semantic_memory']['count']}")
        print(f"  Categories: {stats['semantic_memory']['categories']}")

        print("\nProcedural Memory:")
        print(f"  Procedures: {stats['procedural_memory']['count']}")

        print("=" * 60)

    def save_to_file(self, filepath: str):
        """
        Save memory state to JSON file.

        Args:
            filepath: Path to save file
        """
        data = {
            "timestamp": time.time(),
            "statistics": self.get_statistics(),
            "working_memory": [item.to_dict() for item in self.working.get_all()],
            "episodic_memory": [item.to_dict() for item in self.episodic.episodes],
            "semantic_memory": {
                category: [item.to_dict() for item in items]
                for category, items in self.semantic.facts.items()
            },
            "procedural_memory": {
                name: item.to_dict()
                for name, item in self.procedural.procedures.items()
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        print(f"Memory saved to: {filepath}")

    def clear_all(self):
        """Clear all memory levels."""
        self.working.clear()
        self.episodic.episodes.clear()
        self.semantic.facts.clear()
        self.procedural.procedures.clear()


# ============================================================================
# Example Usage
# ============================================================================

def example_hierarchical_memory():
    """Comprehensive example of hierarchical memory system."""
    print("Hierarchical Memory System Example")
    print("=" * 60)

    # Create memory system
    memory = HierarchicalMemory(working_capacity=5, episodic_capacity=20)

    # Simulate a conversation about Python programming
    print("\nSimulating conversation about Python...")

    # Working memory: Immediate context
    memory.add_to_working(
        "User asked: How do I start learning Python?", importance=0.8
    )
    memory.add_to_working("Discussing Python basics", importance=0.7)
    memory.add_to_working("User mentioned they know JavaScript", importance=0.9)

    # Consolidate to episodic
    memory.consolidate_to_episodic()

    # Add semantic facts
    memory.add_fact(
        "programming",
        "Python is a high-level, interpreted programming language",
        importance=0.9,
    )
    memory.add_fact(
        "programming",
        "Python uses indentation to define code blocks",
        importance=0.8,
    )
    memory.add_fact(
        "python_basics", "Variables in Python don't need type declarations", importance=0.7
    )

    # Add procedures
    memory.add_procedure(
        "setup_python_environment",
        [
            "Install Python from python.org",
            "Set up a virtual environment",
            "Install pip packages",
            "Choose an IDE (VSCode, PyCharm, etc.)",
        ],
        importance=0.9,
    )

    # Print statistics
    memory.print_statistics()

    # Retrieve context for a query
    print("\n" + "=" * 60)
    print("CONTEXT RETRIEVAL")
    print("=" * 60)

    query = "How do I set up Python on my computer?"
    context = memory.get_context_for_query(query, max_items=5)

    print(f"\nQuery: {query}")
    print("\nRetrieved Context:")

    for memory_type, items in context.items():
        if items:
            print(f"\n{memory_type.upper()}:")
            for item in items:
                print(f"  • {item}")

    # Save memory state
    memory.save_to_file("memory_state.json")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    print("Context Engineering - Hierarchical Memory Architecture")
    print("=" * 60)
    print("Multi-level memory system for context management")
    print("=" * 60)
    print()

    example_hierarchical_memory()

    print("\nHierarchical memory demonstration complete!")
    print("=" * 60)
