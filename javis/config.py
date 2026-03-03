"""Configuration management for Javis."""

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field, asdict


@dataclass
class Config:
    """Javis configuration."""
    
    # Memory settings
    memory_dir: Path = field(default_factory=lambda: Path.home() / ".javis" / "memory")
    
    # API Keys
    brave_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    
    # Tool settings
    max_exec_output: int = 50000  # Max characters from exec
    exec_timeout: int = 60  # Default timeout for commands
    
    # Web settings
    search_count: int = 10
    
    # Browser settings
    browser_headless: bool = True
    browser_timeout: int = 30
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        return cls(
            memory_dir=Path(os.getenv("JAVIS_MEMORY_DIR", str(Path.home() / ".javis" / "memory"))),
            brave_api_key=os.getenv("BRAVE_API_KEY"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            max_exec_output=int(os.getenv("JAVIS_MAX_EXEC_OUTPUT", "50000")),
            exec_timeout=int(os.getenv("JAVIS_EXEC_TIMEOUT", "60")),
            search_count=int(os.getenv("JAVIS_SEARCH_COUNT", "10")),
        )
    
    @classmethod
    def from_file(cls, path: Path) -> "Config":
        """Load configuration from a YAML file."""
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        
        # Convert path strings to Path objects
        if "memory_dir" in data and isinstance(data["memory_dir"], str):
            data["memory_dir"] = Path(data["memory_dir"]).expanduser()
        
        return cls(**data)
    
    @classmethod
    def load(cls) -> "Config":
        """Load configuration from default locations."""
        # Try env first, then file
        config = cls.from_env()
        
        # Look for config file in standard locations
        config_paths = [
            Path.cwd() / "config.yaml",
            Path.cwd() / ".javis" / "config.yaml",
            Path.home() / ".javis" / "config.yaml",
            Path("/etc/javis/config.yaml"),
        ]
        
        for path in config_paths:
            if path.exists():
                file_config = cls.from_file(path)
                # Merge, preferring env vars
                for key, value in asdict(file_config).items():
                    if getattr(config, key) is None or (isinstance(getattr(config, key), (int, Path)) and key not in os.environ):
                        setattr(config, key, value)
                break
        
        return config
    
    def save(self, path: Optional[Path] = None) -> None:
        """Save configuration to a YAML file."""
        if path is None:
            path = Path.home() / ".javis" / "config.yaml"
        
        path.parent.mkdir(parents=True, exist_ok=True)
        
        data = asdict(self)
        # Convert Path to string for serialization
        data["memory_dir"] = str(data["memory_dir"])
        
        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False)
