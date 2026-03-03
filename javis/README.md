# 🤖 Javis - An AI Assistant Library

Javis is a flexible, extensible AI assistant library that combines autonomous agent capabilities with conversational interaction. Built with Python, it features meta-cognitive planning, tool execution, and persistent memory.

## ✨ Features

- **🧠 Meta-Cognition**: Cursor-style autonomous replanning based on execution feedback
- **🔄 ReAct Pattern**: Interleaved Reasoning → Action → Observation → Reflection
- **💾 Persistent Memory**: Daily logs + long-term memory with search capabilities
- **🛠️ Tool System**: Execute shell commands, web searches, file operations
- **🧩 Plugin Architecture**: Extensible skill system for adding new capabilities
- **💬 Conversational Agent**: Natural chat interface with tool integration
- **⚡ Parallel Execution**: Spawn sub-agents for complex tasks

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/javis.git
cd javis

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Required Dependencies

- `requests` - Web requests and API calls
- `beautifulsoup4` - HTML parsing for web content extraction
- `python-dateutil` - Date parsing utilities
- `pyyaml` - Configuration file handling

## 🚀 Quick Start

### Basic Usage

```python
from javis import Javis

# Initialize
javis = Javis()

# Remember something
javis.remember("User prefers Python over JavaScript", category="preferences")

# Recall later
print(javis.recall("programming preferences"))

# Execute commands
result = javis.exec("ls -la")
print(result.stdout)

# Search the web (requires BRAVE_API_KEY)
results = javis.web_search("Python async patterns")
for r in results:
    print(f"{r.title}: {r.url}")
```

### Autonomous Agent

```python
from javis import JavisAgent

agent = JavisAgent()

# Run on a goal (asks for approval before actions)
session = agent.run("Research Python async patterns", auto_approve=False)

# Get summary
print(agent.get_summary(session.id))

# Export session to JSON
agent.export_session(session.id, "research_session.json")
```

### Advanced Agent with Meta-Cognition

```python
from javis import AdvancedAgent

agent = AdvancedAgent()

# Auto-replans when stuck or errors occur
session = agent.run("Build a simple web scraper", auto_approve=True)
print(f"Completed in {len(session.thoughts)} steps")
```

### Conversational Agent

```python
from javis import ChatAgent

chat = ChatAgent()

# Natural conversation with tool use
response = chat.chat("What files are in the current directory?")
print(response)

# Remember preferences during chat
chat.chat("Remember that I prefer markdown over plain text")
```

## 🏗️ Architecture

```
javis/
├── core.py          # Main Javis class (entry point)
├── agent.py         # Basic autonomous agent with ReAct loop
├── advanced_agent.py# Advanced agent with meta-cognition
├── chat_agent.py    # Conversational agent
├── planner.py       # Task planning and decomposition
├── metacognition.py # Meta-level decision making
├── tools.py         # Tool execution (shell, web, files)
├── skills.py        # Plugin system for extensibility
├── memory.py        # Memory management
├── config.py        # Configuration management
├── __init__.py      # Package exports
├── README.md        # This file
├── requirements.txt # Python dependencies
├── tests/           # Test suite
│   ├── test_core.py
│   ├── test_tools.py
│   └── test_memory.py
└── examples/        # Usage demos
    ├── basic_usage.py
    ├── chat_demo.py
    └── weather_demo.py
```

## 📦 Installation & Import

### Install from PyPI (when published)
```bash
pip install javis
```

### Or use as a local package
```bash
git clone https://github.com/Xiaomi2008/javis.git
cd javis
pip install -e .
```

### Import in your code
```python
from javis import Javis, JavisAgent, AdvancedAgent
# or directly from root files:
from core import Javis
from agent import JavisAgent
```

## 🛠️ Tools & Capabilities

### Built-in Tools

- **Shell Execution**: Run commands safely with timeout and output limits
- **Web Search**: Brave Search API integration (requires API key)
- **Web Fetching**: Extract content from URLs with HTML parsing
- **File Operations**: Read, write, edit files with path validation
- **Memory Management**: Persistent storage with search and categorization

### Skills System

Skills provide specialized capabilities:

```python
from javis.skills import Skill

class MySkill(Skill):
    name = "my_custom_skill"
    description = "Custom functionality"
    
    def my_command(self, arg1, arg2):
        return f"Result with {arg1} and {arg2}"
    
    def get_commands(self):
        return {"my_command": self.my_command}

# Register the skill
javis.register_skill(MySkill())
```

### Built-in Skills

- **Echo**: Test and debug tool calls
- **Weather**: Get weather from wttr.in (no API key required)
- **Timer**: Set timers and reminders

## 🔧 Configuration

Create a `config.yaml` file or set environment variables:

```yaml
# config.yaml
memory_dir: ~/.javis/memory
brave_api_key: "your_brave_api_key"
openai_api_key: "your_openai_api_key"  # Optional
max_exec_output: 50000
exec_timeout: 60
search_count: 10
```

Environment variables:

- `JAVIS_MEMORY_DIR` - Memory storage directory
- `BRAVE_API_KEY` - Brave Search API key
- `OPENAI_API_KEY` - OpenAI API key (for future features)
- `JAVIS_MAX_EXEC_OUTPUT` - Max output characters from commands
- `JAVIS_EXEC_TIMEOUT` - Default command timeout in seconds

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_core.py -v

# With coverage report
pytest --cov=javis tests/
```

## 📝 Memory System

Javis maintains two types of memory:

1. **Daily Logs**: Time-stamped entries in `memory/YYYY-MM-DD.md`
2. **Long-term Memory**: Curated important facts in `MEMORY.md`

Search across all memories:

```python
results = javis.recall("programming preferences")
print(results)
```

## 🚀 Roadmap

- [ ] Vector-based memory search (embeddings)
- [ ] LLM-powered planning (instead of rule-based)
- [ ] More built-in skills (Git, code analysis, etc.)
- [ ] Web UI interface
- [ ] Multi-agent collaboration
- [ ] Docker support for easy deployment

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - feel free to use this for personal or commercial projects.

## 🙏 Acknowledgments

- Inspired by ReAct paper: [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
- Meta-cognition inspired by Cursor IDE's planning approach
- Weather data from wttr.in

---

**Built with ❤️ by the Javis team**
