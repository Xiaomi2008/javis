"""Chat agent demo."""

import sys
sys.path.insert(0, "..")

from javis.chat_agent import ChatAgent


def demo():
    """Demo of chat agent."""
    print("=" * 60)
    print("CHAT AGENT DEMO")
    print("=" * 60)
    
    chat = ChatAgent()
    
    # Demo conversations
    conversations = [
        "Hello!",
        "Create a file called hello.txt with Hello World",
        "What files are in the current directory?",
        "Search for Python asyncio best practices",
        "Remember my timezone is America/Los_Angeles",
        "What do you know about my timezone?",
        "Thank you!",
    ]
    
    for user_msg in conversations:
        print(f"\n👤 User: {user_msg}")
        response = chat.chat(user_msg)
        print(f"🤖 Agent: {response}")
    
    print("\n" + "=" * 60)
    print("Chat complete!")
    
    # Show history
    print("\n📜 Conversation History:")
    for msg in chat.get_history():
        if msg.role == "user":
            print(f"  User: {msg.content}")
        elif msg.role == "assistant":
            print(f"  Agent: {msg.content[:100]}...")


if __name__ == "__main__":
    demo()
