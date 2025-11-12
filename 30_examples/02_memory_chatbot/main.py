#!/usr/bin/env python3
"""
Memory-Enhanced Chatbot - CLI Application
==========================================

Interactive command-line interface for the memory-enhanced chatbot.

Usage:
    python main.py                          # Interactive mode
    python main.py --load session.json      # Load previous session
    python main.py --debug                  # Enable debug output

Author: Context Engineering Contributors
License: MIT
"""

import argparse
import sys
from pathlib import Path

from src.memory_chatbot import MemoryChatbot


def print_welcome(chatbot: MemoryChatbot):
    """Print welcome message."""
    print("=" * 60)
    print(f"  Memory-Enhanced Chatbot - {chatbot.name}")
    print("=" * 60)
    print()
    print("I'm a chatbot with persistent memory. I remember our")
    print("conversations and learn from them!")
    print()
    print("Commands:")
    print("  /help    - Show help message")
    print("  /stats   - Show memory statistics")
    print("  /save    - Save conversation")
    print("  /load    - Load conversation")
    print("  /export  - Export conversation history")
    print("  /clear   - Clear all memory")
    print("  /quit    - Exit chatbot")
    print()
    print("=" * 60)
    print()


def print_help():
    """Print help message."""
    print()
    print("=" * 60)
    print("AVAILABLE COMMANDS")
    print("=" * 60)
    print()
    print("/help               Show this help message")
    print("/stats              Display memory and conversation statistics")
    print("/save [filename]    Save conversation (default: session_YYYYMMDD_HHMMSS.json)")
    print("/load [filename]    Load a saved conversation")
    print("/export [filename]  Export conversation history as text")
    print("/clear              Clear all memory and reset conversation")
    print("/quit or /exit      Exit the chatbot")
    print()
    print("Just type normally to chat!")
    print()
    print("=" * 60)
    print()


def handle_command(command: str, chatbot: MemoryChatbot) -> bool:
    """
    Handle special commands.

    Args:
        command: Command string
        chatbot: Chatbot instance

    Returns:
        True if should continue, False to exit
    """
    parts = command.strip().split()
    cmd = parts[0].lower()

    if cmd in ["/quit", "/exit", "/q"]:
        print()
        print("Goodbye! I'll remember our conversation.")
        return False

    elif cmd == "/help":
        print_help()

    elif cmd == "/stats":
        print()
        chatbot.print_memory_stats()
        print()

    elif cmd == "/save":
        filename = parts[1] if len(parts) > 1 else None
        if not filename:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"session_{timestamp}.json"

        print()
        chatbot.save_conversation(filename)
        print()

    elif cmd == "/load":
        if len(parts) < 2:
            print()
            print("Usage: /load <filename>")
            print()
        else:
            filename = parts[1]
            print()
            try:
                chatbot.load_conversation(filename)
                print()
            except FileNotFoundError:
                print(f"Error: File '{filename}' not found")
                print()
            except Exception as e:
                print(f"Error loading conversation: {e}")
                print()

    elif cmd == "/export":
        filename = parts[1] if len(parts) > 1 else None
        if not filename:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp}.txt"

        print()
        chatbot.export_conversation_history(filename)
        print()

    elif cmd == "/clear":
        print()
        confirm = input("Are you sure you want to clear all memory? (yes/no): ")
        if confirm.lower() in ['yes', 'y']:
            chatbot.clear_memory()
        else:
            print("Clear cancelled.")
        print()

    else:
        print()
        print(f"Unknown command: {cmd}")
        print("Type /help for available commands")
        print()

    return True


def interactive_mode(chatbot: MemoryChatbot, debug: bool = False):
    """
    Run interactive chat loop.

    Args:
        chatbot: Chatbot instance
        debug: Enable debug output
    """
    print_welcome(chatbot)

    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.startswith("/"):
                should_continue = handle_command(user_input, chatbot)
                if not should_continue:
                    break
                continue

            # Regular conversation
            response = chatbot.chat(user_input)
            print(f"{chatbot.name}: {response}")
            print()

            # Debug output
            if debug:
                stats = chatbot.get_memory_stats()
                print(f"[DEBUG] Working memory: {stats['working_memory']['count']}/7")
                print(f"[DEBUG] Episodic memory: {stats['episodic_memory']['count']}")
                print()

        except KeyboardInterrupt:
            print("\n")
            print("Interrupted. Type /quit to exit or continue chatting.")
            print()
        except EOFError:
            print("\n")
            break
        except Exception as e:
            print(f"\nError: {e}")
            if debug:
                import traceback
                traceback.print_exc()
            print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Memory-Enhanced Chatbot with Hierarchical Memory"
    )

    parser.add_argument(
        "--name",
        type=str,
        default="Claude",
        help="Chatbot name (default: Claude)"
    )

    parser.add_argument(
        "--working-capacity",
        type=int,
        default=7,
        help="Working memory capacity (default: 7)"
    )

    parser.add_argument(
        "--episodic-capacity",
        type=int,
        default=100,
        help="Episodic memory capacity (default: 100)"
    )

    parser.add_argument(
        "--personality",
        type=str,
        default="helpful, knowledgeable, friendly",
        help="Chatbot personality traits"
    )

    parser.add_argument(
        "--load",
        type=str,
        help="Load conversation from file"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output"
    )

    args = parser.parse_args()

    # Create chatbot
    print("Initializing memory-enhanced chatbot...")
    chatbot = MemoryChatbot(
        name=args.name,
        working_capacity=args.working_capacity,
        episodic_capacity=args.episodic_capacity,
        personality=args.personality
    )

    # Load conversation if specified
    if args.load:
        try:
            chatbot.load_conversation(args.load)
        except FileNotFoundError:
            print(f"Error: File '{args.load}' not found")
            return 1
        except Exception as e:
            print(f"Error loading conversation: {e}")
            return 1

    # Run interactive mode
    interactive_mode(chatbot, debug=args.debug)

    return 0


if __name__ == "__main__":
    sys.exit(main())
