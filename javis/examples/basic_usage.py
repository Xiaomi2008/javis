"""Basic usage examples for Javis.

Run with: python -m examples.basic_usage
or: PYTHONPATH=. python examples/basic_usage.py
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import Javis


def main():
    # Initialize Javis
    javis = Javis()
    
    print("=" * 50)
    print("JAVIS DEMO")
    print("=" * 50)
    
    # System info
    print("\n📊 System Info")
    print(javis.info())
    
    # Memory operations
    print("\n🧠 Memory Operations")
    javis.remember("User asked about Python best practices", category="session")
    javis.remember("Timezone is America/Los_Angeles", category="identity", tags=["preferences"], important=True)
    
    recalled = javis.recall("Python")
    print(recalled)
    
    # File operations
    print("\n📁 File Operations")
    javis.write_file("demo.txt", "Hello from Javis!")
    content = javis.read_file("demo.txt")
    print(f"Read file: {content}")
    
    # Shell execution
    print("\n🔧 Shell Execution")
    result = javis.exec("echo 'Hello World' && pwd")
    print(f"Command output:\n{result}")
    
    # Skill usage
    print("\n🎯 Built-in Skills")
    echo_result = javis.skills.echo.echo("Hello", times=3)
    print(f"Echo: {echo_result}")
    
    print("\n" + "=" * 50)
    print("Demo complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()
