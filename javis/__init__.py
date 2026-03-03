"""Javis - An AI assistant library with meta-cognition."""

from core import Javis, MemoryManager, MemoryEntry, ExecResult, SearchResult
from tools import ToolExecutor, FileTools, WebTools, WebContent
from skills import Skill, SkillRegistry
from config import Config
from agent import JavisAgent, AgentSession, AgentThought
from chat_agent import ChatAgent, ChatMessage
from advanced_agent import AdvancedAgent, ReActAgent
from metacognition import MetacognitiveMonitor, ExecutionState, ReplanReason

__version__ = "0.1.0"
__all__ = [
    # Core classes
    "Javis",
    "MemoryManager",
    "MemoryEntry",
    
    # Agent classes
    "JavisAgent",
    "AdvancedAgent",
    "ReActAgent",
    "AgentSession",
    "AgentThought",
    "ChatAgent",
    "ChatMessage",
    
    # Meta-cognition
    "MetacognitiveMonitor",
    "ExecutionState",
    "ReplanReason",
    
    # Tools and results
    "ToolExecutor",
    "FileTools",
    "WebTools",
    "ExecResult",
    "SearchResult",
    "WebContent",
    
    # Skills
    "Skill",
    "SkillRegistry",
    
    # Configuration
    "Config",
]
