"""Memory management for Javis."""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass, field, asdict
from dateutil import parser as date_parser


@dataclass
class MemoryEntry:
    """A single memory entry."""
    
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    category: str = "general"
    tags: List[str] = field(default_factory=list)
    source: str = "user"  # user, system, tool, etc.
    important: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "category": self.category,
            "tags": self.tags,
            "source": self.source,
            "important": self.important,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryEntry":
        """Create from dictionary."""
        return cls(
            content=data["content"],
            timestamp=date_parser.parse(data["timestamp"]),
            category=data.get("category", "general"),
            tags=data.get("tags", []),
            source=data.get("source", "user"),
            important=data.get("important", False),
        )


class MemoryManager:
    """Manages persistent memory storage."""
    
    def __init__(self, memory_dir: Path):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.daily_dir = self.memory_dir / "daily"
        self.daily_dir.mkdir(parents=True, exist_ok=True)
    
    @property
    def long_term_path(self) -> Path:
        """Path to long-term memory file."""
        return self.memory_dir / "MEMORY.md"
    
    def _get_daily_path(self, date: Optional[datetime] = None) -> Path:
        """Get path for daily memory file."""
        if date is None:
            date = datetime.now()
        return self.daily_dir / f"{date.strftime('%Y-%m-%d')}.md"
    
    # === Long-term Memory ===
    
    def read_long_term(self) -> str:
        """Read long-term memory (MEMORY.md)."""
        if not self.long_term_path.exists():
            return "# Memory\n\n"
        return self.long_term_path.read_text()
    
    def write_long_term(self, content: str) -> None:
        """Write to long-term memory."""
        self.long_term_path.write_text(content)
    
    def append_long_term(self, entry: str, section: Optional[str] = None) -> None:
        """Append entry to long-term memory."""
        content = self.read_long_term()
        
        if section:
            # Find section and insert there
            section_pattern = rf"(## {re.escape(section)}.*?(?:\n## |\Z))"
            match = re.search(section_pattern, content, re.DOTALL)
            if match:
                insert_pos = match.start() + len(match.group(1).rstrip())
                content = content[:insert_pos] + f"\n\n{entry}" + content[insert_pos:]
            else:
                # Section doesn't exist, append to end
                content += f"\n\n## {section}\n\n{entry}"
        else:
            # Append to end
            content += f"\n\n{entry}"
        
        self.write_long_term(content)
    
    # === Daily Memory ===
    
    def read_daily(self, date: Optional[datetime] = None) -> str:
        """Read daily memory file."""
        path = self._get_daily_path(date)
        if not path.exists():
            return f"# {path.stem}\n\n"
        return path.read_text()
    
    def write_daily(self, content: str, date: Optional[datetime] = None) -> None:
        """Write to daily memory."""
        path = self._get_daily_path(date)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    
    def append_daily(self, entry: str, date: Optional[datetime] = None) -> None:
        """Append entry to daily memory."""
        content = self.read_daily(date)
        content += entry + "\n"
        self.write_daily(content, date)
    
    # === Entry Management ===
    
    def store_entry(self, entry: MemoryEntry, long_term: bool = False) -> None:
        """Store a memory entry."""
        if long_term or entry.important:
            # Format for markdown
            entry_text = f"- [{entry.timestamp.strftime('%Y-%m-%d %H:%M')}] {entry.content}"
            if entry.tags:
                entry_text += f" ({', '.join(entry.tags)})"
            self.append_long_term(entry_text, section=entry.category.capitalize())
        else:
            # Store in daily
            entry_text = f"- [{entry.timestamp.strftime('%H:%M')}] [{entry.category}] {entry.content}"
            self.append_daily(entry_text, entry.timestamp)
    
    def remember(self, content: str, category: str = "general", 
                 tags: Optional[List[str]] = None, 
                 important: bool = False) -> MemoryEntry:
        """Create and store a memory."""
        entry = MemoryEntry(
            content=content,
            category=category,
            tags=tags or [],
            important=important,
        )
        self.store_entry(entry, long_term=important)
        return entry
    
    # === Search ===
    
    def search(self, query: str, days: Optional[int] = None) -> List[Tuple[str, MemoryEntry]]:
        """Search memory for relevant entries (simple substring search)."""
        results = []
        query_lower = query.lower()
        
        # Search daily files
        if days is not None:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            current = start_date
            while current <= end_date:
                text = self.read_daily(current)
                for line in text.split("\n"):
                    if query_lower in line.lower() and line.strip():
                        # Try to parse as entry
                        try:
                            entry = MemoryEntry(
                                content=line,
                                timestamp=current,
                            )
                            results.append((str(self._get_daily_path(current)), entry))
                        except:
                            pass
                current += timedelta(days=1)
        else:
            # Search all daily files
            if self.daily_dir.exists():
                for path in sorted(self.daily_dir.glob("*.md")):
                    text = path.read_text()
                    for line in text.split("\n"):
                        if query_lower in line.lower() and line.strip():
                            try:
                                entry = MemoryEntry(content=line)
                                results.append((str(path), entry))
                            except:
                                pass
        
        # Search long-term memory
        long_term = self.read_long_term()
        for line in long_term.split("\n"):
            if query_lower in line.lower() and line.strip():
                try:
                    entry = MemoryEntry(content=line, important=True)
                    results.append((str(self.long_term_path), entry))
                except:
                    pass
        
        return results
    
    # === Session Management ===
    
    def get_recent_context(self, days: int = 2) -> str:
        """Get recent memory context for a session."""
        parts = []
        
        # Long-term memory
        long_term = self.read_long_term()
        if len(long_term) > 100:  # Has actual content
            parts.append("## Long-term Memory\n" + long_term[:2000])
        
        # Recent daily memories
        for i in range(days, -1, -1):
            date = datetime.now() - timedelta(days=i)
            daily = self.read_daily(date)
            if daily.strip() != f"# {date.strftime('%Y-%m-%d')}":
                parts.append(f"## {date.strftime('%Y-%m-%d')}\n" + daily[-2000:])
        
        return "\n\n".join(parts)
