"""Skill/plugin system for Javis."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Type
from importlib import import_module
from pathlib import Path


class Skill(ABC):
    """Base class for Javis skills."""
    
    name: str = ""
    description: str = ""
    version: str = "0.1.0"
    
    def __init__(self, javis: Optional[Any] = None):
        self.javis = javis
    
    def setup(self) -> None:
        """Called when skill is registered. Override to initialize."""
        pass
    
    def teardown(self) -> None:
        """Called when skill is unregistered. Override to cleanup."""
        pass
    
    def get_commands(self) -> Dict[str, Any]:
        """
        Return commands this skill provides.
        
        Returns:
            Dict mapping command names to callable functions
        """
        return {}
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Return capabilities this skill provides.
        
        Returns:
            Dict mapping capability names to descriptions
        """
        return {}
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} '{self.name}' v{self.version}>"


class SkillRegistry:
    """Registry for managing skills."""
    
    def __init__(self):
        self._skills: Dict[str, Skill] = {}
        self._commands: Dict[str, callable] = {}
    
    def register(self, skill: Skill, javis: Optional[Any] = None) -> None:
        """
        Register a skill.
        
        Args:
            skill: Skill instance to register
            javis: Javis instance to attach to skill
        """
        if not skill.name:
            raise ValueError("Skill must have a name")
        
        if skill.name in self._skills:
            raise ValueError(f"Skill '{skill.name}' already registered")
        
        skill.javis = javis
        self._skills[skill.name] = skill
        
        # Setup skill
        skill.setup()
        
        # Register commands
        for cmd_name, cmd_func in skill.get_commands().items():
            full_name = f"{skill.name}.{cmd_name}"
            self._commands[full_name] = cmd_func
    
    def unregister(self, name: str) -> Optional[Skill]:
        """Unregister and return a skill."""
        if name not in self._skills:
            return None
        
        skill = self._skills.pop(name)
        skill.teardown()
        
        # Remove commands
        for cmd_name in list(self._commands.keys()):
            if cmd_name.startswith(f"{name}."):
                del self._commands[cmd_name]
        
        return skill
    
    def get(self, name: str) -> Optional[Skill]:
        """Get a skill by name."""
        return self._skills.get(name)
    
    def list_skills(self) -> List[str]:
        """List all registered skill names."""
        return list(self._skills.keys())
    
    def has_skill(self, name: str) -> bool:
        """Check if skill is registered."""
        return name in self._skills
    
    def __getattr__(self, name: str) -> Skill:
        """Allow accessing skills via registry.skill_name."""
        if name in self._skills:
            return self._skills[name]
        raise AttributeError(f"Skill '{name}' not found")
    
    def execute(self, command: str, *args, **kwargs) -> Any:
        """
        Execute a command by name.
        
        Args:
            command: Full command name (e.g., 'weather.get')
            *args, **kwargs: Arguments to pass to command
        """
        if command not in self._commands:
            raise ValueError(f"Unknown command: {command}")
        
        return self._commands[command](*args, **kwargs)
    
    def load_from_module(self, module_path: str, javis: Optional[Any] = None) -> Skill:
        """
        Load a skill from a module.
        
        Args:
            module_path: Python module path (e.g., 'javis.skills.weather')
            javis: Javis instance to attach
        
        Returns:
            Loaded skill instance
        """
        module = import_module(module_path)
        
        # Look for Skill subclass
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                issubclass(attr, Skill) and 
                attr is not Skill):
                skill = attr()
                self.register(skill, javis)
                return skill
        
        raise ValueError(f"No Skill subclass found in {module_path}")


# === Example Skills ===

class EchoSkill(Skill):
    """A simple echo skill for testing."""
    
    name = "echo"
    description = "Echo messages back"
    
    def echo(self, message: str, times: int = 1) -> str:
        """Echo a message."""
        return (message + " ") * times
    
    def get_commands(self) -> Dict[str, Any]:
        return {
            "echo": self.echo,
        }


class WeatherSkill(Skill):
    """Weather skill using wttr.in - no API key required."""
    
    name = "weather"
    description = "Get weather information for any location"
    
    def __init__(self, javis=None):
        super().__init__(javis)
        self.base_url = "https://wttr.in"
    
    def get_weather(self, location: str, lang: str = "en") -> str:
        """Get weather for a location using wttr.in."""
        import requests
        
        encoded_location = requests.utils.quote(location)
        url = f"{self.base_url}/{encoded_location}"
        params = {"format": 3, "lang": lang}
        headers = {"User-Agent": "Javis-Weather-Skill/1.0"}
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text.strip()
        except Exception as e:
            return f"Weather error: {str(e)}"
    
    def get_detailed(self, location: str, lang: str = "en") -> str:
        """Get detailed weather forecast."""
        import requests
        
        encoded_location = requests.utils.quote(location)
        url = f"{self.base_url}/{encoded_location}"
        params = {"lang": lang}
        headers = {"User-Agent": "Javis-Weather-Skill/1.0"}
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            return f"Weather error: {str(e)}"
    
    def get_commands(self) -> Dict[str, Any]:
        return {
            "get_weather": self.get_weather,
            "get_detailed": self.get_detailed,
        }
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "get_weather": "Get current weather for a location (uses wttr.in, no API key)",
            "get_detailed": "Get detailed weather forecast",
        }


class TimerSkill(Skill):
    """Timer and reminder skill."""
    
    name = "timer"
    description = "Set timers and reminders"
    
    def __init__(self, javis: Any = None):
        super().__init__(javis)
        self._timers: Dict[str, Any] = {}
    
    def set_timer(self, minutes: int, message: str = "Timer complete!") -> str:
        """Set a timer for N minutes."""
        import threading
        
        def alert():
            if self.javis:
                self.javis.remember(f"Timer: {message}", category="alerts")
        
        timer = threading.Timer(minutes * 60, alert)
        timer.daemon = True
        timer.start()
        
        timer_id = f"timer_{len(self._timers)}"
        self._timers[timer_id] = timer
        
        return f"⏱️ Timer set for {minutes} minutes"
    
    def get_commands(self) -> Dict[str, Any]:
        return {
            "set_timer": self.set_timer,
        }
