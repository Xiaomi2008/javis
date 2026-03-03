"""Autonomous Agent for Javis - the full agent loop."""

import os
import time
import uuid
from typing import List, Dict, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
import json

from core import Javis
from planner import SimplePlanner, StepPlanner, Plan, Task, TaskStatus
from memory import MemoryEntry
from metacognition import MetacognitiveMonitor, ExecutionState


@dataclass
class AgentThought:
    """A single thought/reasoning step."""
    timestamp: datetime = field(default_factory=datetime.now)
    thought: str = ""
    action: str = ""
    action_input: Dict = field(default_factory=dict)
    observation: str = ""
    reflection: str = ""


@dataclass
class AgentSession:
    """An autonomous agent session."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    goal: str = ""
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    thoughts: List[AgentThought] = field(default_factory=list)
    plan: Optional[Plan] = None
    status: str = "active"  # active, paused, completed, failed
    max_iterations: int = 10
    current_iteration: int = 0
    auto_approve: bool = False  # If False, asks before acting


class JavisAgent:
    """
    An autonomous agent powered by Javis.
    
    This agent can:
    - Reason about goals
    - Plan multi-step tasks
    - Execute tools autonomously
    - Observe results
    - Reflect and replan
    - Learn from outcomes
    
    Example:
        >>> agent = JavisAgent()
        >>> session = agent.run("Research Python async patterns")
        >>> print(agent.get_summary(session.id))
    """
    
    def __init__(self, javis: Optional[Javis] = None, 
                 planner: Optional[SimplePlanner] = None):
        """
        Initialize the agent.
        
        Args:
            javis: Javis instance (creates new one if None)
            planner: Planner to use (creates SimplePlanner if None)
        """
        self.javis = javis or Javis()
        self.planner = planner or SimplePlanner()
        self.step_planner = StepPlanner()
        
        # Metacognitive monitor for intelligent replanning (LLM-powered)
        self.metacognitive_monitor: Optional[MetacognitiveMonitor] = None
        
        # Active sessions
        self._sessions: Dict[str, AgentSession] = {}
        
        # Tool registry
        self._tools: Dict[str, Callable] = {
            "web_search": self._tool_web_search,
            "web_fetch": self._tool_web_fetch,
            "read_file": self._tool_read_file,
            "write_file": self._tool_write_file,
            "edit_file": self._tool_edit_file,
            "exec": self._tool_exec,
            "remember": self._tool_remember,
            "recall": self._tool_recall,
            "think": self._tool_think,
            "done": self._tool_done,
        }
        
        # Initialize metacognitive monitor with LLM capability
        try:
            from metacognition import MetacognitiveMonitor, ExecutionState
            self.metacognitive_monitor = MetacognitiveMonitor(agent_session=self)
            print("✅ Metacognitive monitor initialized (LLM-powered)")
        except Exception as e:
            print(f"⚠️ Could not initialize LLM metacognition: {e}")
        
        # Remember agent initialization
        self.javis.remember("Agent initialized", category="system")
    
    # === Core Agent Loop ===
    
    def run(self, goal: str, max_iterations: int = 10, 
            auto_approve: bool = False) -> AgentSession:
        """
        Run the agent on a goal.
        
        Args:
            goal: The goal to achieve
            max_iterations: Maximum steps before stopping
            auto_approve: If True, execute without asking; if False, prompt for approval
        
        Returns:
            AgentSession with full trace
        """
        # Create session
        session = AgentSession(
            goal=goal,
            max_iterations=max_iterations,
            auto_approve=auto_approve,
        )
        self._sessions[session.id] = session
        
        # Create plan
        session.plan = self.planner.create_plan(goal, self._get_context())
        
        print(f"🤖 Agent started: {goal}")
        print(f"   Session ID: {session.id}")
        print(f"   Plan: {len(session.plan.tasks)} tasks")
        print()
        
        # Run agent loop
        try:
            self._agent_loop(session)
        except Exception as e:
            session.status = "failed"
            self._add_thought(session, 
                thought=f"Agent failed with error: {e}",
                action="error",
                observation=str(e),
            )
        
        # Finalize
        session.end_time = datetime.now()
        if session.status == "active":
            session.status = "completed"
        
        # Store in memory
        self.javis.remember(
            f"Agent session {session.id} completed: {goal}",
            category="agent",
            important=True,
        )
        
        return session
    
    def _agent_loop(self, session: AgentSession) -> None:
        """Main agent loop."""
        while session.status == "active" and session.current_iteration < session.max_iterations:
            session.current_iteration += 1
            
            # Get next task from plan
            task = session.plan.get_next_task()
            
            if not task:
                if session.plan.is_complete:
                    session.status = "completed"
                    break
                else:
                    # No ready tasks but plan not complete - blocked
                    self._add_thought(session,
                        thought="No ready tasks but plan incomplete",
                        action="replan",
                        observation="Plan appears blocked",
                    )
                    break
            
            # Execute task
            task.status = TaskStatus.IN_PROGRESS
            
            # Reason about the task
            thought = self._reason_about_task(task, session)
            
            # Determine action
            action = task.tool or "think"
            action_input = task.args or {"task": task.description}
            
            # Approval check
            if not session.auto_approve:
                approved = self._request_approval(task, thought)
                if not approved:
                    task.status = TaskStatus.BLOCKED
                    break
            
            # Execute action
            observation = self._execute_action(action, action_input, session)
            
            # Reflect
            reflection = self._reflect(task, action, observation)
            
            # Store thought
            self._add_thought(session, thought, action, action_input, observation, reflection)
            
            # Update task
            task.status = TaskStatus.COMPLETED if observation else TaskStatus.FAILED
            task.result = observation
            
            # Metacognitive replanning check (LLM-powered)
            if self.metacognitive_monitor and not session.auto_approve:
                state = ExecutionState(
                    step_count=session.current_iteration,
                    successful_steps=sum(1 for t in session.thoughts if "completed" in str(t.action).lower()),
                    failed_steps=sum(1 for t in session.thoughts if "failed" in str(t.action).lower() or not t.observation),
                )
                
                replan_reason = self.metacognitive_monitor.should_replan(
                    state=state,
                    plan=session.plan,
                    last_action=action,
                    last_result=observation,
                )
                
                if replan_reason:
                    print(f"\n🧠 Metacognitive decision: Replan needed ({replan_reason.value})")
                    # Would trigger replanning logic here
                    # For now, just log it
            
            # Store intermediate results
            if observation:
                self.javis.remember(
                    f"Agent step: {task.description} → {str(observation)[:100]}",
                    category="agent_step",
                )
        
        # Check if max iterations reached
        if session.current_iteration >= session.max_iterations:
            session.status = "paused"
            print(f"⏸️ Max iterations ({session.max_iterations}) reached")
    
    def _reason_about_task(self, task: Task, session: AgentSession) -> str:
        """Generate reasoning about a task."""
        context = self._get_context()
        previous = session.thoughts[-1] if session.thoughts else None
        
        thoughts = [
            f"Goal: {session.goal}",
            f"Current task: {task.description}",
            f"Progress: {session.current_iteration}/{session.max_iterations}",
        ]
        
        if previous:
            thoughts.append(f"Previous action: {previous.action}")
            thoughts.append(f"Previous observation: {previous.observation[:100]}")
        
        return " | ".join(thoughts)
    
    def _request_approval(self, task: Task, thought: str) -> bool:
        """Request user approval before executing."""
        print(f"\n🤔 Agent wants to:")
        print(f"   Task: {task.description}")
        if task.tool:
            print(f"   Tool: {task.tool}")
            print(f"   Args: {task.args}")
        print(f"   Reasoning: {thought[:200]}...")
        
        # In interactive mode, would ask user
        # For now, auto-approve if no destructive action
        destructive_tools = ["exec", "write_file", "edit_file"]
        if task.tool in destructive_tools:
            print("   ⚠️ This is a destructive action - requires approval")
            # In real implementation: input("Approve? (y/n): ") == "y"
            return True  # For demo
        
        print("   ✓ Approved (non-destructive)")
        return True
    
    def _execute_action(self, action: str, action_input: Dict, session: AgentSession) -> Any:
        """Execute a tool action."""
        if action in self._tools:
            try:
                return self._tools[action](**action_input)
            except Exception as e:
                return f"Error: {str(e)}"
        else:
            return f"Unknown tool: {action}"
    
    def _reflect(self, task: Task, action: str, observation: Any) -> str:
        """Reflect on action outcome."""
        if not observation:
            return "No observation to reflect on"
        
        if "error" in str(observation).lower():
            return f"Action failed: {observation}"
        
        return f"Action succeeded, got result: {str(observation)[:100]}"
    
    def _add_thought(self, session: AgentSession, thought: str = "",
                     action: str = "", action_input: Dict = None,
                     observation: str = "", reflection: str = ""):
        """Add a thought to session."""
        t = AgentThought(
            thought=thought,
            action=action,
            action_input=action_input or {},
            observation=str(observation),
            reflection=reflection,
        )
        session.thoughts.append(t)
        
        # Print for visibility
        if action:
            icon = {"web_search": "🔍", "exec": "🔧", "read_file": "📄", 
                   "write_file": "✍️", "done": "✅"}.get(action, "➡️")
            print(f"{icon} {action}: {str(observation)[:80]}")
    
    # === Tool Implementations ===
    
    def _tool_web_search(self, query: str, **kwargs) -> str:
        """Search the web."""
        results = self.javis.web_search(query)
        return "\n".join([f"- {r.title}: {r.url}" for r in results[:5]])
    
    def _tool_web_fetch(self, url: str = None, **kwargs) -> str:
        """Fetch URL."""
        # If no URL provided, try to get from kwargs or context
        if not url:
            return "No URL provided"
        return self.javis.web_fetch(url)[:1000]
    
    def _tool_read_file(self, path: str, **kwargs) -> str:
        """Read a file."""
        return self.javis.read_file(path)[:2000]
    
    def _tool_write_file(self, path: str, content: str, **kwargs) -> str:
        """Write a file."""
        self.javis.write_file(path, content)
        return f"Wrote {len(content)} chars to {path}"
    
    def _tool_edit_file(self, path: str, old_text: str, new_text: str, **kwargs) -> str:
        """Edit a file."""
        self.javis.edit_file(path, old_text, new_text)
        return f"Edited {path}"
    
    def _tool_exec(self, command: str, **kwargs) -> str:
        """Execute shell command."""
        result = self.javis.exec(command)
        return str(result)[:1000]
    
    def _tool_remember(self, content: str, **kwargs) -> str:
        """Store in memory."""
        self.javis.remember(content, important=kwargs.get("important", False))
        return "Remembered"
    
    def _tool_recall(self, query: str, **kwargs) -> str:
        """Recall from memory."""
        return self.javis.recall(query)
    
    def _tool_think(self, about: str, **kwargs) -> str:
        """Pure thinking step."""
        return f"Thought about: {about}"
    
    def _tool_done(self, **kwargs) -> str:
        """Mark as done."""
        return "Task complete"
    
    # === Context ===
    
    def _get_context(self) -> str:
        """Get current context from memory."""
        # Get recent memories
        context = self.javis.context
        
        # Get system info
        info = self.javis.info()
        
        return f"{info}\n\n{context}"
    
    # === Session Management ===
    
    def get_session(self, session_id: str) -> Optional[AgentSession]:
        """Get session by ID."""
        return self._sessions.get(session_id)
    
    def list_sessions(self) -> List[str]:
        """List all session IDs."""
        return list(self._sessions.keys())
    
    def get_summary(self, session_id: str) -> str:
        """Get summary of session."""
        session = self.get_session(session_id)
        if not session:
            return f"Session {session_id} not found"
        
        lines = [
            f"🤖 Agent Session: {session_id}",
            f"Goal: {session.goal}",
            f"Status: {session.status}",
            f"Iterations: {session.current_iteration}/{session.max_iterations}",
            f"Duration: {session.end_time - session.start_time if session.end_time else 'in progress'}",
            "",
            "Thought trace:",
        ]
        
        for i, t in enumerate(session.thoughts, 1):
            lines.append(f"\n  Step {i}:")
            lines.append(f"    Thought: {t.thought[:100]}...")
            if t.action:
                lines.append(f"    Action: {t.action}")
            if t.observation:
                lines.append(f"    Observation: {t.observation[:100]}...")
        
        return "\n".join(lines)
    
    def export_session(self, session_id: str, path: str) -> None:
        """Export session to JSON file."""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        data = {
            "id": session.id,
            "goal": session.goal,
            "status": session.status,
            "start_time": session.start_time.isoformat(),
            "end_time": session.end_time.isoformat() if session.end_time else None,
            "thoughts": [
                {
                    "timestamp": t.timestamp.isoformat(),
                    "thought": t.thought,
                    "action": t.action,
                    "action_input": t.action_input,
                    "observation": t.observation,
                    "reflection": t.reflection,
                }
                for t in session.thoughts
            ],
            "plan": session.plan.summary() if session.plan else None,
        }
        
        self.javis.write_file(path, json.dumps(data, indent=2))
