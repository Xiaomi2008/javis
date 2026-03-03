"""Conversational agent - chatty agent like me."""

import re
from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime

from core import Javis
from agent import AgentThought


@dataclass
class ChatMessage:
    """A chat message."""
    role: str  # user, assistant, system, tool
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)


class ChatAgent:
    """
    A conversational agent that feels more like a chat partner.
    
    Unlike the task-focused JavisAgent, ChatAgent:
    - Maintains conversation history
    - Decides when to use tools vs just chat
    - Can spawn sub-agents for complex tasks
    - Knows when to be helpful vs when to just listen
    
    Example:
        >>> agent = ChatAgent()
        >>> agent.chat("What files are in this directory?")
        "I'll check for you... you have 5 files..."
    """
    
    def __init__(self, javis: Optional[Javis] = None):
        self.javis = javis or Javis()
        self.messages: List[ChatMessage] = []
        self.tool_patterns = self._build_tool_patterns()
        self._init_personality()
    
    def _init_personality(self) -> None:
        """Initialize personality and system prompt."""
        self.system_prompt = """You are Javis, a helpful AI assistant.

Your traits:
- Warm and conversational, not robotic
- Concise but thorough
- Proactive when needed, but not pushy
- Good at determining what's best handled by tools vs conversation

When to use tools:
- Files: when user mentions paths, asks about code, or references documents
- Shell: when user asks about system state ("what's running?", "disk space")
- Web: when user asks about current info you don't know
- Memory: when user mentions preferences or asks you to remember

Otherwise, just chat naturally."""
        
        self.messages.append(ChatMessage(role="system", content=self.system_prompt))
    
    def _build_tool_patterns(self) -> Dict[str, Any]:
        """Build patterns for detecting when to use tools."""
        return {
            "read_file": {
                "patterns": [
                    r"read (?:the )?file (.+)",
                    r"show (?:me )?(?:the )?content(?:s)? of (.+)",
                    r"what('s| is) in (.+)",
                    r"(?:file|path)[: ]*(.+\.(?:py|txt|md|json|yaml|yml|js|ts|html|css))",
                ],
                "extract": lambda m: m.group(1) if len(m.groups()) == 1 else m.group(2),
            },
            "write_file": {
                "patterns": [
                    r"(?:create|write) (?:a )?file (?:called )?(.+?) with (.+)",
                    r"save (?:this |that )?to (.+)",
                ],
                "extract": lambda m: (m.group(1), m.group(2)),
            },
            "exec": {
                "patterns": [
                    r"(?:run|execute|what('s| is)) (?:(?:the )?command )?[`\"']?(.+?)[`\"']?(?:\?|$)",
                    r"(?:show|list|get) (?:all )?(?:the )?(?:running )?processes",
                    r"(?:disk|storage|space) usage",
                    r"(?:list|show) (?:the )?(?:files|directory)",
                ],
                "extract": lambda m: m.group(2) if len(m.groups()) > 1 else m.group(0),
            },
            "web_search": {
                "patterns": [
                    r"(?:search |google |look up )(?:for )?['\"]?(.+?)['\"]?\??$",
                    r"(?:what|how|why) (?:is|are|does) (.+?)\??",
                    r"(?:find|get) (?:information|info) about (.+)",
                ],
                "extract": lambda m: m.group(1),
            },
            "remember": {
                "patterns": [
                    r"(?:remember|save|store) (?:that )?(.+)",
                    r"(?:don't forget|keep in mind) (?:that )?(.+)",
                ],
                "extract": lambda m: m.group(1),
            },
            "recall": {
                "patterns": [
                    r"(?:what did i say about|recall|remember) (.+)",
                    r"(?:what do you know about|tell me about) (.+)",
                ],
                "extract": lambda m: m.group(1),
            },
        }
    
    def chat(self, message: str, use_tools: bool = True) -> str:
        """
        Chat with the agent.
        
        Args:
            message: User message
            use_tools: Whether to allow tool use
        
        Returns:
            Response text
        """
        # Store user message
        self.messages.append(ChatMessage(role="user", content=message))
        
        # Decide if we use tools
        if use_tools:
            tool_result = self._try_tools(message)
            if tool_result:
                # Tool was used - incorporate result
                response = self._format_tool_response(message, tool_result)
                self.messages.append(ChatMessage(
                    role="assistant", 
                    content=response,
                    metadata=tool_result
                ))
                return response
        
        # Simple response (in real implementation, would use LLM)
        response = self._generate_response(message)
        self.messages.append(ChatMessage(role="assistant", content=response))
        return response
    
    def _try_tools(self, message: str) -> Optional[Dict]:
        """Try to match message to tools."""
        message_lower = message.lower()
        
        # Check each tool
        for tool_name, config in self.tool_patterns.items():
            for pattern in config["patterns"]:
                match = re.search(pattern, message_lower, re.IGNORECASE)
                if match:
                    try:
                        extracted = config["extract"](match)
                        
                        # Execute tool
                        if tool_name == "read_file":
                            content = self.javis.read_file(extracted)
                            return {"tool": tool_name, "result": content[:1000], "args": {"path": extracted}}
                        
                        elif tool_name == "exec":
                            # Safe command list
                            safe_cmds = ["ls", "pwd", "echo", "cat", "head", "tail", "wc", "ps", "df", "du"]
                            cmd = extracted.strip()
                            base_cmd = cmd.split()[0]
                            
                            if base_cmd not in safe_cmds and not any(s in cmd for s in safe_cmds):
                                return {"tool": tool_name, "error": "Command not in safe list", "args": {"command": cmd}}
                            
                            result = self.javis.exec(cmd)
                            return {"tool": tool_name, "result": str(result)[:1000], "args": {"command": cmd}}
                        
                        elif tool_name == "remember":
                            self.javis.remember(extracted, category="user_pref", important=True)
                            return {"tool": tool_name, "result": f"Remembered: {extracted}", "args": {"content": extracted}}
                        
                        elif tool_name == "recall":
                            results = self.javis.recall(extracted)
                            return {"tool": tool_name, "result": results, "args": {"query": extracted}}
                        
                        elif tool_name == "web_search":
                            results = self.javis.web_search(extracted)
                            return {"tool": tool_name, "result": results[:3], "args": {"query": extracted}}
                        
                    except Exception as e:
                        return {"tool": tool_name, "error": str(e), "args": {"extracted": str(extracted)}}
        
        return None
    
    def _format_tool_response(self, message: str, tool_result: Dict) -> str:
        """Format tool result into natural response."""
        tool = tool_result.get("tool")
        result = tool_result.get("result", tool_result.get("error", "No result"))
        error = tool_result.get("error")
        
        if error:
            return f"I tried to help with that, but ran into an issue: {error}"
        
        if tool == "read_file":
            args = tool_result.get("args", {})
            path = args.get("path", "the file")
            content = result if isinstance(result, str) else str(result)
            lines = content.count('\n')
            return f"Here's the content of {path} ({lines} lines):\n\n```\n{content[:500]}\n```"
        
        elif tool == "exec":
            return f"Command result:\n```\n{result}\n```"
        
        elif tool == "web_search":
            if isinstance(result, list):
                lines = ["Here are some results:"]
                for r in result:
                    lines.append(f"• {r.title}: {r.url}")
                return "\n".join(lines)
            return f"Search results:\n{result}"
        
        elif tool == "remember":
            return "✅ Got it, I'll remember that."
        
        elif tool == "recall":
            if "No memories" in str(result):
                return "I don't recall anything about that specifically."
            return f"Here's what I remember:\n{result}"
        
        return str(result)
    
    def _generate_response(self, message: str) -> str:
        """Generate conversational response (simplified)."""
        # This would normally use an LLM
        # For now, rule-based
        
        message_lower = message.lower()
        
        greetings = ["hello", "hi", "hey", "greetings"]
        if any(g in message_lower for g in greetings):
            return "Hey there! 👋 What can I help you with?"
        
        if "thank" in message_lower:
            return "You're welcome! Let me know if you need anything else."
        
        if "how are you" in message_lower:
            return "I'm doing well, thanks for asking! Ready to help out."
        
        if "who are you" in message_lower or "what are you" in message_lower:
            return "I'm Javis - an AI assistant with memory, tools, and a bit of personality. I can help with files, commands, web searches, and just chat."
        
        # Default helpful response
        return "I'm here to help! I can work with files, run commands, search the web, or just chat. What would you like to do?"
    
    def get_history(self, last_n: int = 10) -> List[ChatMessage]:
        """Get chat history."""
        return self.messages[-last_n:]
    
    def clear_history(self) -> None:
        """Clear chat history but keep system prompt."""
        self.messages = [self.messages[0]]  # Keep system
    
    def export_history(self, path: str) -> None:
        """Export chat history to file."""
        lines = []
        for msg in self.messages:
            lines.append(f"[{msg.role}] {msg.timestamp.strftime('%H:%M:%S')}: {msg.content}")
        
        self.javis.write_file(path, "\n\n".join(lines))
