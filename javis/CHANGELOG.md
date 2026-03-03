# Changelog

## [0.1.0] - 2026-03-01

### Added
- Initial release of Javis library
- **Memory Management**: Daily and long-term memory with Markdown storage
- **Configuration**: YAML and environment variable support
- **File Operations**: Read, write, and edit with line-level precision
- **Shell Execution**: Safe command execution with timeouts
- **Web Tools**: Search (Brave API) and URL fetching
- **Skills System**: Plugin architecture for extensibility
  - Built-in Echo skill
  - Weather skill (wttr.in, no API key)
- **Examples**: Basic usage, custom skills, chatbot, weather demo
- **Tests**: pytest-based test suite

### Features
- Persistent memory in `~/.javis/memory/`
- Session context tracking
- Skill registry with command execution
- Full test coverage for core modules
