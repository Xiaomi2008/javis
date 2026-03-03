"""Core Javis class - the main interface."""

import os
from typing import Optional, List, Dict, Any, Union
from pathlib import Path
import datetime

from config import Config
from memory import MemoryManager, MemoryEntry
from tools import ToolExecutor, WebTools, FileTools, ExecResult, SearchResult
from skills import SkillRegistry, Skill


class Javis:
    """
    Javis - An AI assistant library.
    
    This is the main entry point for using Javis capabilities.
    
    Example:
        >>> javis = Javis()
        >>> javis.remember("User's name is Alice")
        >>> result = javis.exec("ls -la")
        >>> print(result.stdout)
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize Javis.
        
        Args:
            config: Configuration object (loads from files/env if not provided)
        """
        self.config = config or Config.load()
        
        # Initialize core systems
        self._memory = MemoryManager(self.config.memory_dir)
        self._tools = ToolExecutor(
            max_output=self.config.max_exec_output,
            default_timeout=self.config.exec_timeout,
        )
        self._web = WebTools(
            brave_api_key=self.config.brave_api_key,
            search_count=self.config.search_count,
        )
        self._files = FileTools()
        self._skills = SkillRegistry()
        
        # Session info
        self._session_start = datetime.datetime.now()
        self._context = ""
        
        # Load built-in skills
        self._load_builtin_skills()
        
        # Load context
        self._load_context()
    
    def _load_builtin_skills(self) -> None:
        """Load built-in skills."""
        from skills import EchoSkill, WeatherSkill
        self._skills.register(EchoSkill(), self)
        self._skills.register(WeatherSkill(), self)
    
    def _load_context(self) -> None:
        """Load recent memory context."""
        self._context = self._memory.get_recent_context(days=2)
    
    # === Memory Operations ===
    
    def remember(self, content: str, category: str = "general",
                 tags: Optional[List[str]] = None,
                 important: bool = False) -> MemoryEntry:
        """
        Store a memory.
        
        Args:
            content: What to remember
            category: Category for organization (e.g., 'identity', 'tasks')
            tags: List of tags
            important: If True, stores in long-term MEMORY.md
        
        Returns:
            MemoryEntry object
        """
        return self._memory.remember(content, category, tags, important)
    
    def recall(self, query: str, days: Optional[int] = None) -> str:
        """
        Search memory for relevant entries.
        
        Args:
            query: Search query
            days: Limit to last N days (None = all time)
        
        Returns:
            Formatted string with search results
        """
        results = self._memory.search(query, days)
        
        if not results:
            return f"No memories found for '{query}'"
        
        lines = [f"Found {len(results)} relevant memories:"]
        for source, entry in results[:10]:  # Limit to 10
            lines.append(f"- [{entry.category}] {entry.content}")
        
        return "\n".join(lines)
    
    def get_memory(self, date: Optional[datetime.datetime] = None) -> str:
        """
        Get daily memory for a specific date.
        
        Args:
            date: Date to fetch (default: today)
        
        Returns:
            Memory content as string
        """
        return self._memory.read_daily(date)
    
    # === File Operations ===
    
    def read_file(self, path: str, offset: int = 0, limit: Optional[int] = None) -> str:
        """
        Read file contents.
        
        Args:
            path: File path (relative or absolute)
            offset: Line number to start from (1-indexed)
            limit: Maximum lines to read
        
        Returns:
            File contents
        """
        return self._files.read(path, offset, limit)
    
    def write_file(self, path: str, content: str) -> None:
        """
        Write content to file (creates directories if needed).
        
        Args:
            path: File path
            content: Content to write
        """
        self._files.write(path, content)
    
    def edit_file(self, path: str, old_text: str, new_text: str) -> None:
        """
        Edit file by replacing exact text.
        
        Args:
            path: File path
            old_text: Exact text to find (must match exactly)
            new_text: Replacement text
        """
        self._files.edit(path, old_text, new_text)
    
    def file_exists(self, path: str) -> bool:
        """Check if file exists."""
        return self._files.exists(path)
    
    def list_files(self, path: str, pattern: str = "*") -> List[str]:
        """List files in directory matching pattern."""
        return self._files.list_dir(path, pattern)
    
    # === Shell Operations ===
    
    def exec(self, command: str, cwd: Optional[str] = None,
             env: Optional[Dict[str, str]] = None,
             timeout: Optional[int] = None) -> ExecResult:
        """
        Execute a shell command.
        
        Args:
            command: Shell command
            cwd: Working directory
            env: Environment variables
            timeout: Timeout in seconds
        
        Returns:
            ExecResult with stdout, stderr, and return code
        """
        return self._tools.exec(command, cwd, env, timeout)
    
    def run_async(self, command: str, cwd: Optional[str] = None) -> int:
        """
        Run a command asynchronously (returns PID).
        
        Args:
            command: Shell command
            cwd: Working directory
        
        Returns:
            Process ID
        """
        return self._tools.run_background(command, cwd)
    
    # === Web Operations ===
    
    def web_search(self, query: str, count: Optional[int] = None) -> List[SearchResult]:
        """
        Search the web.
        
        Args:
            query: Search query
            count: Number of results
        
        Returns:
            List of SearchResult objects
        """
        return self._web.search(query, count)
    
    def web_fetch(self, url: str, max_chars: int = 10000) -> str:
        """
        Fetch content from URL.
        
        Args:
            url: URL to fetch
            max_chars: Maximum characters to return
        
        Returns:
            Extracted content as markdown/text
        """
        content = self._web.fetch(url, max_chars=max_chars)
        return f"# {content.title}\n\n{content.content}"
    
    # === Skill Operations ===
    
    def register_skill(self, skill: Skill) -> None:
        """Register a skill."""
        self._skills.register(skill, self)
    
    def unregister_skill(self, name: str) -> Optional[Skill]:
        """Unregister a skill."""
        return self._skills.unregister(name)
    
    @property
    def skills(self) -> SkillRegistry:
        """Access skill registry."""
        return self._skills
    
    def list_skills(self) -> List[str]:
        """List all registered skills."""
        return self._skills.list_skills()
    
    # === Session Management ===
    
    @property
    def context(self) -> str:
        """Get current session context from memory."""
        return self._context
    
    def refresh_context(self) -> None:
        """Refresh context from memory."""
        self._load_context()
    
    def uptime(self) -> str:
        """Get session uptime."""
        elapsed = datetime.datetime.now() - self._session_start
        hours, remainder = divmod(elapsed.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{elapsed.days}d {hours}h {minutes}m {seconds}s"
    
    # === Utility ===
    
    def info(self) -> str:
        """Get system information."""
        lines = [
            f"Javis v0.1.0",
            f"Session started: {self._session_start.isoformat()}",
            f"Uptime: {self.uptime()}",
            f"Memory directory: {self.config.memory_dir}",
            f"Skills loaded: {', '.join(self.list_skills())}",
        ]
        return "\n".join(lines)
    
    # === Context Manager ===
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        # Could add cleanup here
        pass
