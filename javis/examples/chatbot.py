"""Simple chatbot example using Javis."""

import os
from javis import Javis


class SimpleChatbot:
    """A simple interactive chatbot powered by Javis."""
    
    def __init__(self):
        self.javis = Javis()
        print("🤖 Chatbot initialized!")
        print(f"{self.javis.info()}\n")
    
    def process(self, message: str) -> str:
        """Process user input and return response."""
        # Store in memory
        self.javis.remember(f"User: {message}", category="chat")
        
        # Simple command handling
        if message.startswith("/"):
            return self._handle_command(message)
        
        # Basic responses
        if "hello" in message.lower() or "hi" in message.lower():
            return "Hello! How can I help you today?"
        
        if "time" in message.lower():
            return f"Session uptime: {self.javis.uptime()}"
        
        if "search" in message.lower():
            # Extract search query
            query = message.replace("search", "").strip()
            if query:
                results = self.javis.web_search(query, count=3)
                return "\n".join([f"• {r.title}: {r.url}" for r in results])
            return "What would you like me to search for?"
        
        if "remember" in message.lower():
            content = message.replace("remember", "").strip()
            self.javis.remember(content, important=True)
            return f"📌 Remembered: {content}"
        
        if "recall" in message.lower():
            query = message.replace("recall", "").strip()
            return self.javis.recall(query)
        
        # Default
        return "I'm not sure how to help with that. Try: hello, time, search <query>, remember <text>, recall <query>"
    
    def _handle_command(self, message: str) -> str:
        """Handle special commands."""
        cmd = message[1:].split()[0].lower()
        
        if cmd == "help":
            return """
Available commands:
/hello - Greeting
/time - Show session uptime
/search <query> - Search the web
/remember <text> - Store in memory
/recall <query> - Search memory
/quit - Exit
            """.strip()
        
        if cmd == "quit":
            return "Goodbye! 👋"
        
        return f"Unknown command: /{cmd}. Type /help for available commands."


def main():
    bot = SimpleChatbot()
    
    print("\n💬 Chatbot ready! Type /help for commands, /quit to exit.\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue
            
            response = bot.process(user_input)
            print(f"Bot: {response}\n")
            
            if user_input.startswith("/quit"):
                break
                
        except EOFError:
            break
        except KeyboardInterrupt:
            print("\nGoodbye! 👋")
            break


if __name__ == "__main__":
    main()
