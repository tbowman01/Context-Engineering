"""
Memory-Enhanced Chatbot - Main Class
=====================================

Conversational agent with hierarchical memory for context retention
and personalized responses.

Author: Context Engineering Contributors
License: MIT
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import time

# Add Module 03 to path
module_path = Path(__file__).parent.parent.parent.parent / "00_COURSE" / "03_context_management" / "architectures"
sys.path.insert(0, str(module_path))

from hierarchical_memory import HierarchicalMemory, MemoryItem


@dataclass
class ChatMessage:
    """A single chat message."""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: float
    importance: float = 0.5

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ConversationStats:
    """Statistics about the conversation."""
    total_messages: int
    user_messages: int
    assistant_messages: int
    session_duration_seconds: float
    memory_usage: Dict[str, int]


class MemoryChatbot:
    """
    Memory-enhanced conversational chatbot.

    Integrates hierarchical memory architecture for:
    - Context retention across conversations
    - Learning user preferences
    - Personalized responses
    - Long-term memory persistence

    Example:
        >>> chatbot = MemoryChatbot(name="Claude")
        >>> response = chatbot.chat("Hello! What's your name?")
        >>> print(response)
        >>>
        >>> # Save conversation
        >>> chatbot.save_conversation("session.json")
    """

    def __init__(
        self,
        name: str = "Assistant",
        working_capacity: int = 7,
        episodic_capacity: int = 100,
        personality: str = "helpful, concise, friendly",
        enable_learning: bool = True
    ):
        """
        Initialize memory-enhanced chatbot.

        Args:
            name: Chatbot name
            working_capacity: Working memory capacity (Miller's Law: 7±2)
            episodic_capacity: Episodic memory capacity
            personality: Chatbot personality traits
            enable_learning: Enable learning from conversations
        """
        self.name = name
        self.personality = personality
        self.enable_learning = enable_learning

        # Initialize hierarchical memory
        self.memory = HierarchicalMemory(
            working_capacity=working_capacity,
            episodic_capacity=episodic_capacity
        )

        # Conversation tracking
        self.messages: List[ChatMessage] = []
        self.session_start = time.time()
        self.message_count = 0

        # User profile (learned from conversation)
        self.user_profile: Dict[str, Any] = {}

        # Initialize with bot personality in semantic memory
        self._initialize_personality()

    def _initialize_personality(self):
        """Initialize bot personality in semantic memory."""
        self.memory.add_fact(
            category="bot_personality",
            content=f"I am {self.name}, an AI assistant. My traits: {self.personality}",
            importance=1.0
        )

        # Add some default procedures
        self.memory.add_procedure(
            name="greeting",
            steps=[
                "Acknowledge the user warmly",
                "Ask how you can help",
                "Be friendly and approachable"
            ]
        )

    def chat(
        self,
        user_message: str,
        importance: Optional[float] = None
    ) -> str:
        """
        Process user message and generate response.

        Args:
            user_message: User's input message
            importance: Importance score (0-1), auto-calculated if None

        Returns:
            Bot's response string

        Example:
            >>> response = chatbot.chat("What is Python?")
            >>> print(response)
        """
        # Calculate importance if not provided
        if importance is None:
            importance = self._calculate_importance(user_message)

        # Create message
        user_msg = ChatMessage(
            role="user",
            content=user_message,
            timestamp=time.time(),
            importance=importance
        )

        # Add to working memory
        self.memory.add_to_working(user_message, importance=importance)

        # Extract and learn from message
        if self.enable_learning:
            self._learn_from_message(user_message)

        # Generate response
        response = self._generate_response(user_message)

        # Create assistant message
        assistant_msg = ChatMessage(
            role="assistant",
            content=response,
            timestamp=time.time(),
            importance=importance
        )

        # Add to working memory
        self.memory.add_to_working(response, importance=importance)

        # Store messages
        self.messages.append(user_msg)
        self.messages.append(assistant_msg)
        self.message_count += 2

        # Consolidate to episodic memory if working memory is full
        if len(self.memory.working.items) >= self.memory.working.capacity:
            self.memory.consolidate_to_episodic()

        return response

    def _calculate_importance(self, message: str) -> float:
        """
        Calculate message importance.

        Uses heuristics:
        - Questions are more important
        - Personal information is more important
        - Commands/requests are important
        """
        importance = 0.5  # Base importance

        # Questions are important
        if "?" in message:
            importance += 0.2

        # Personal information keywords
        personal_keywords = ["my name", "i am", "i'm", "my", "me"]
        if any(keyword in message.lower() for keyword in personal_keywords):
            importance += 0.3

        # Command/request keywords
        command_keywords = ["please", "can you", "could you", "help", "show"]
        if any(keyword in message.lower() for keyword in command_keywords):
            importance += 0.1

        return min(importance, 1.0)

    def _learn_from_message(self, message: str):
        """
        Learn facts and preferences from user message.

        Extracts:
        - User name
        - Preferences
        - Topics of interest
        """
        message_lower = message.lower()

        # Extract name
        if "my name is" in message_lower or "i am" in message_lower:
            # Simple name extraction
            parts = message_lower.replace("my name is", "").replace("i am", "").split()
            if parts:
                name = parts[0].strip(".,!?").title()
                self.user_profile["name"] = name
                self.memory.add_fact(
                    category="user_info",
                    content=f"User's name is {name}",
                    importance=0.9
                )

        # Extract interests/learning topics
        learning_keywords = ["learning", "studying", "interested in", "want to learn"]
        for keyword in learning_keywords:
            if keyword in message_lower:
                # Extract topic after keyword
                idx = message_lower.find(keyword)
                after = message[idx + len(keyword):].strip()
                if after:
                    topic = after.split()[0] if after.split() else ""
                    if topic:
                        self.memory.add_fact(
                            category="user_interests",
                            content=f"User is {keyword} {topic}",
                            importance=0.7
                        )

    def _generate_response(self, user_message: str) -> str:
        """
        Generate response based on message and memory context.

        This is a simulated response generator. In production, this would
        call an LLM API (OpenAI, Anthropic, etc.) with assembled context.

        Args:
            user_message: User's message

        Returns:
            Generated response
        """
        # Get relevant context from all memory levels
        context = self.memory.get_context_for_query(
            user_message,
            max_items=10
        )

        # Simulate response generation based on context
        # In production: response = llm.generate(prompt=prompt_with_context)

        response = self._simulate_response(user_message, context)

        return response

    def _simulate_response(
        self,
        message: str,
        context: Dict[str, List]
    ) -> str:
        """
        Simulate response generation.

        In production, replace this with actual LLM API call.
        """
        message_lower = message.lower()

        # Greeting
        if any(word in message_lower for word in ["hello", "hi", "hey"]):
            user_name = self.user_profile.get("name", "")
            if user_name:
                return f"Hello {user_name}! How can I help you today?"
            return f"Hello! I'm {self.name}. How can I assist you today?"

        # Name query
        if "your name" in message_lower or "who are you" in message_lower:
            return f"I'm {self.name}, an AI assistant with persistent memory. I remember our conversations and learn from them!"

        # What's my name
        if "my name" in message_lower and "?" in message:
            user_name = self.user_profile.get("name")
            if user_name:
                return f"Your name is {user_name}!"
            return "I don't know your name yet. Would you like to tell me?"

        # Memory/remember queries
        if "remember" in message_lower or "recall" in message_lower:
            if context['episodic']:
                return f"Yes, I remember! We discussed: {context['episodic'][0].content[:100]}..."
            return "I don't have specific memories matching that query yet."

        # Help/how to questions
        if ("how" in message_lower or "what" in message_lower) and "?" in message:
            # Check for relevant procedures
            if context.get('procedural'):
                proc = context['procedural'][0]
                steps = proc.content[:3] if isinstance(proc.content, list) else []
                if steps:
                    return f"Here's how: {', '.join(steps)}"

            # Check semantic memory for relevant facts
            if context.get('semantic'):
                fact = context['semantic'][0]
                return f"Based on what I know: {fact.content}"

            return "That's a great question! I'd be happy to help you explore that topic."

        # Learning acknowledgment
        if "learning" in message_lower or "studying" in message_lower:
            return "That's wonderful! I can help you learn. What specific topics would you like to explore?"

        # Thanks
        if "thank" in message_lower:
            return "You're welcome! Let me know if you need anything else."

        # Goodbye
        if any(word in message_lower for word in ["bye", "goodbye", "see you"]):
            return "Goodbye! I'll remember our conversation for next time."

        # Default response
        return "I understand. Could you tell me more about that?"

    def add_fact(
        self,
        category: str,
        content: str,
        importance: float = 0.7
    ):
        """
        Add a fact to semantic memory.

        Args:
            category: Fact category
            content: Fact content
            importance: Importance score (0-1)

        Example:
            >>> chatbot.add_fact(
            ...     category="programming",
            ...     content="Python uses indentation for blocks",
            ...     importance=0.9
            ... )
        """
        self.memory.add_fact(category, content, importance)

    def add_procedure(
        self,
        name: str,
        steps: List[str],
        importance: float = 0.7
    ):
        """
        Add a procedure to procedural memory.

        Args:
            name: Procedure name
            steps: List of steps
            importance: Importance score (0-1)

        Example:
            >>> chatbot.add_procedure(
            ...     name="make_coffee",
            ...     steps=["Boil water", "Add coffee", "Pour water", "Wait 4 min"]
            ... )
        """
        self.memory.add_procedure(name, steps, importance)

    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get detailed memory statistics.

        Returns:
            Dictionary with memory statistics

        Example:
            >>> stats = chatbot.get_memory_stats()
            >>> print(f"Working memory: {stats['working_memory']['count']}/7")
        """
        return {
            "working_memory": {
                "count": len(self.memory.working.items),
                "capacity": self.memory.working.capacity,
                "utilization": len(self.memory.working.items) / self.memory.working.capacity
            },
            "episodic_memory": {
                "count": len(self.memory.episodic.episodes),
                "capacity": getattr(self.memory.episodic, 'capacity', 'unlimited')
            },
            "semantic_memory": {
                "categories": len(self.memory.semantic.facts),
                "total_facts": sum(len(facts) for facts in self.memory.semantic.facts.values())
            },
            "procedural_memory": {
                "count": len(self.memory.procedural.procedures)
            },
            "conversation": {
                "total_messages": self.message_count,
                "user_messages": sum(1 for m in self.messages if m.role == "user"),
                "assistant_messages": sum(1 for m in self.messages if m.role == "assistant"),
                "session_duration_minutes": (time.time() - self.session_start) / 60
            },
            "user_profile": self.user_profile
        }

    def print_memory_stats(self):
        """Print memory statistics in readable format."""
        stats = self.get_memory_stats()

        print("=" * 60)
        print("MEMORY-ENHANCED CHATBOT STATISTICS")
        print("=" * 60)

        print(f"\nWorking Memory:")
        print(f"  Items: {stats['working_memory']['count']}/{stats['working_memory']['capacity']}")
        print(f"  Utilization: {stats['working_memory']['utilization']:.1%}")

        print(f"\nEpisodic Memory:")
        print(f"  Episodes: {stats['episodic_memory']['count']}/{stats['episodic_memory']['capacity']}")

        print(f"\nSemantic Memory:")
        print(f"  Categories: {stats['semantic_memory']['categories']}")
        print(f"  Total Facts: {stats['semantic_memory']['total_facts']}")

        print(f"\nProcedural Memory:")
        print(f"  Procedures: {stats['procedural_memory']['count']}")

        print(f"\nConversation:")
        print(f"  Total Messages: {stats['conversation']['total_messages']}")
        print(f"  User Messages: {stats['conversation']['user_messages']}")
        print(f"  Assistant Messages: {stats['conversation']['assistant_messages']}")
        print(f"  Duration: {stats['conversation']['session_duration_minutes']:.1f} minutes")

        if stats['user_profile']:
            print(f"\nUser Profile:")
            for key, value in stats['user_profile'].items():
                print(f"  {key}: {value}")

        print("=" * 60)

    def save_conversation(
        self,
        filepath: str,
        include_memory: bool = True
    ):
        """
        Save conversation and memory state to file.

        Args:
            filepath: Path to save file
            include_memory: Include full memory state

        Example:
            >>> chatbot.save_conversation("session_001.json")
        """
        data = {
            "metadata": {
                "chatbot_name": self.name,
                "session_start": datetime.fromtimestamp(self.session_start).isoformat(),
                "session_duration_seconds": time.time() - self.session_start,
                "message_count": self.message_count,
                "saved_at": datetime.now().isoformat()
            },
            "messages": [msg.to_dict() for msg in self.messages],
            "user_profile": self.user_profile,
        }

        if include_memory:
            # Save memory state
            data["memory"] = {
                "working": [
                    {"content": item.content, "importance": item.importance}
                    for item in self.memory.working.items
                ],
                "episodic_count": len(self.memory.episodic.episodes),
                "semantic_categories": list(self.memory.semantic.facts.keys()),
                "procedures": list(self.memory.procedural.procedures.keys())
            }

        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        print(f"Conversation saved to: {filepath}")

    def load_conversation(self, filepath: str):
        """
        Load conversation from file.

        Args:
            filepath: Path to conversation file

        Example:
            >>> chatbot.load_conversation("session_001.json")
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Load messages
        self.messages = [
            ChatMessage(**msg) for msg in data.get("messages", [])
        ]

        # Load user profile
        self.user_profile = data.get("user_profile", {})

        # Update message count
        self.message_count = len(self.messages)

        print(f"Loaded conversation from: {filepath}")
        print(f"Messages: {self.message_count}")
        if self.user_profile:
            print(f"User profile: {self.user_profile}")

    def export_conversation_history(self, filepath: str):
        """
        Export conversation history in readable format.

        Args:
            filepath: Path to export file

        Example:
            >>> chatbot.export_conversation_history("conversation.txt")
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Conversation with {self.name}\n")
            f.write(f"Started: {datetime.fromtimestamp(self.session_start).isoformat()}\n")
            f.write("=" * 60 + "\n\n")

            for msg in self.messages:
                timestamp = datetime.fromtimestamp(msg.timestamp).strftime("%H:%M:%S")
                role = "User" if msg.role == "user" else self.name
                f.write(f"[{timestamp}] {role}: {msg.content}\n\n")

            f.write("=" * 60 + "\n")
            f.write(f"Total messages: {len(self.messages)}\n")

        print(f"Conversation history exported to: {filepath}")

    def clear_memory(self):
        """Clear all memory and reset conversation."""
        self.memory = HierarchicalMemory(
            working_capacity=self.memory.working.capacity,
            episodic_capacity=self.memory.episodic.capacity
        )
        self.messages.clear()
        self.user_profile.clear()
        self.message_count = 0
        self.session_start = time.time()
        self._initialize_personality()
        print("All memory cleared and conversation reset.")

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"MemoryChatbot(name='{self.name}', "
            f"messages={self.message_count}, "
            f"working_memory={len(self.memory.working.items)}/7)"
        )


# ============================================================================
# Example Usage
# ============================================================================

def example_memory_chatbot():
    """Example of using memory-enhanced chatbot."""
    print("Memory-Enhanced Chatbot Example")
    print("=" * 60)

    # Create chatbot
    chatbot = MemoryChatbot(
        name="Claude",
        personality="helpful, knowledgeable, friendly"
    )

    print(f"Chatbot created: {chatbot}\n")

    # Simulate conversation
    conversations = [
        ("Hello! What's your name?", "Greeting"),
        ("My name is Alex", "Introducing self"),
        ("I'm learning Python programming", "Sharing interest"),
        ("Can you help me with decorators?", "Asking for help"),
        ("What's my name?", "Testing memory"),
    ]

    for i, (message, description) in enumerate(conversations, 1):
        print(f"\n{'='*60}")
        print(f"Exchange {i}: {description}")
        print("-" * 60)
        print(f"User: {message}")

        response = chatbot.chat(message)
        print(f"{chatbot.name}: {response}")

    # Show statistics
    print(f"\n{'='*60}")
    chatbot.print_memory_stats()

    # Add some facts
    print(f"\n{'='*60}")
    print("Adding facts to semantic memory...")
    chatbot.add_fact(
        category="python",
        content="Decorators are functions that modify other functions",
        importance=0.9
    )

    # Add procedure
    print("Adding procedure to procedural memory...")
    chatbot.add_procedure(
        name="create_decorator",
        steps=[
            "Define outer function that takes a function as input",
            "Define inner wrapper function",
            "Call original function inside wrapper",
            "Return wrapper function",
            "Use @decorator syntax to apply"
        ],
        importance=0.8
    )

    # Save conversation
    print(f"\n{'='*60}")
    print("Saving conversation...")
    chatbot.save_conversation("example_session.json")

    # Export history
    print("Exporting conversation history...")
    chatbot.export_conversation_history("example_conversation.txt")

    print(f"\n{'='*60}")
    print("Memory chatbot example complete!")


if __name__ == "__main__":
    example_memory_chatbot()
