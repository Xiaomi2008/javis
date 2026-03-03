"""Demo of Javis Agent - autonomous mode."""

import sys
sys.path.insert(0, "..")

from javis import JavisAgent


def demo_basic():
    """Basic agent demo."""
    print("=" * 60)
    print("JAVIS AGENT DEMO")
    print("=" * 60)
    
    # Create agent
    agent = JavisAgent()
    
    # Set a goal
    goal = "Research Python async patterns"
    
    print(f"\n🎯 Goal: {goal}")
    print("\nStarting autonomous execution...\n")
    
    # Run agent (simplified - non-destructive tools auto-approved)
    session = agent.run(goal, max_iterations=5, auto_approve=True)
    
    # Show results
    print("\n" + "=" * 60)
    print("AGENT COMPLETE")
    print("=" * 60)
    print(f"\nSession ID: {session.id}")
    print(f"Status: {session.status}")
    print(f"Steps: {session.current_iteration}")
    print(f"\nThought trace:")
    
    for i, thought in enumerate(session.thoughts, 1):
        print(f"\n  Step {i}:")
        if thought.thought:
            print(f"    💭 {thought.thought[:100]}...")
        if thought.action:
            print(f"    🛠️  Action: {thought.action}")
        if thought.observation:
            print(f"    👁️  Observation: {thought.observation[:100]}...")
    
    # Cleanup
    import shutil
    from pathlib import Path
    memory_path = Path.home() / ".javis"
    if memory_path.exists():
        shutil.rmtree(memory_path)
        print(f"\n🗑️  Cleaned up demo memory at {memory_path}")


def demo_chat_mode():
    """Interactive chat with agent."""
    print("\n" + "=" * 60)
    print("CHAT MODE (type 'exit' to quit)")
    print("=" * 60)
    
    agent = JavisAgent()
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("👋 Goodbye!")
            break
        
        if not user_input:
            continue
        
        # Determine if this is a direct command or needs agent
        if user_input.startswith("/"):
            # Direct tool command
            cmd = user_input[1:].split()[0]
            if cmd == "help":
                print("""
Commands:
  /search <query>    - Web search
  /exec <command>    - Execute shell command
  /remember <text>   - Store in memory
  /recall <query>    - Search memory
  /status            - Show agent status
  /run <goal>        - Run agent on goal
  exit               - Quit
                "")
            elif cmd == "status":
                print(f"Agent ready. Sessions: {agent.list_sessions()}")
            else:
                print("Unknown command. Type /help")
        else:
            # Treat as goal
            print(f"\n🤖 Agent: I'll help you: '{user_input}'")
            session = agent.run(user_input, max_iterations=3, auto_approve=True)
            
            print(f"\n✅ Task complete in {session.current_iteration} steps")
            print(f"   Summary: {session.thoughts[-1].observation if session.thoughts else 'No result'}")


def demo_multi_step():
    """Demo multi-step autonomous task."""
    print("\n" + "=" * 60)
    print("MULTI-STEP TASK")
    print("=" * 60)
    
    agent = JavisAgent()
    
    # Create a file
    agent.javis.write_file("/tmp/demo_data.txt", "Sample data for processing")
    
    # Multi-step goal
    goal = "Read /tmp/demo_data.txt, analyze its content, and create a summary"
    
    print(f"\n🎯 Goal: {goal}")
    
    session = agent.run(goal, max_iterations=5)
    
    print("\n📊 Session Summary:")
    print(agent.get_summary(session.id))
    
    # Export
    agent.export_session(session.id, "/tmp/agent_session.json")
    print(f"\n📁 Session exported to /tmp/agent_session.json")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "chat":
            demo_chat_mode()
        elif sys.argv[1] == "multi":
            demo_multi_step()
        else:
            demo_basic()
    else:
        demo_basic()
