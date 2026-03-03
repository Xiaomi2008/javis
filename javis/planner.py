"""Task planning and decomposition for Javis Agent."""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum, auto
import json


class TaskStatus(Enum):
    PENDING = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()
    BLOCKED = auto()


@dataclass
class Task:
    """A single task in a plan."""
    
    id: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = field(default_factory=list)
    result: Any = None
    error: Optional[str] = None
    tool: Optional[str] = None  # Tool to use
    args: Dict[str, Any] = field(default_factory=dict)  # Tool arguments
    
    @property
    def is_ready(self) -> bool:
        """Check if task is ready to execute (all deps completed)."""
        return self.status == TaskStatus.PENDING and all(
            self.status == TaskStatus.COMPLETED for _ in self.dependencies
        )
    
    @property
    def is_complete(self) -> bool:
        """Check if task is complete."""
        return self.status == TaskStatus.COMPLETED
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "description": self.description,
            "status": self.status.name,
            "dependencies": self.dependencies,
            "result": str(self.result)[:200] if self.result else None,
            "error": self.error,
            "tool": self.tool,
            "args": self.args,
        }


@dataclass
class Plan:
    """A plan consisting of multiple tasks."""
    
    goal: str
    tasks: List[Task] = field(default_factory=list)
    context: str = ""
    
    def add_task(self, task: Task) -> None:
        """Add a task to the plan."""
        self.tasks.append(task)
    
    def get_next_task(self) -> Optional[Task]:
        """Get the next ready task."""
        for task in self.tasks:
            if task.status == TaskStatus.PENDING and self._deps_satisfied(task):
                return task
        return None
    
    def _deps_satisfied(self, task: Task) -> bool:
        """Check if all dependencies are satisfied."""
        for dep_id in task.dependencies:
            dep = self.get_task(dep_id)
            if not dep or dep.status != TaskStatus.COMPLETED:
                return False
        return True
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    @property
    def is_complete(self) -> bool:
        """Check if all tasks are complete."""
        return all(t.is_complete for t in self.tasks) or len(self.tasks) == 0
    
    @property
    def progress(self) -> Dict[str, int]:
        """Get task status counts."""
        counts = {s.name: 0 for s in TaskStatus}
        for task in self.tasks:
            counts[task.status.name] += 1
        return counts
    
    def summary(self) -> str:
        """Get human-readable summary."""
        lines = [f"📋 Plan: {self.goal}"]
        lines.append(f"   Progress: {self.progress}")
        for task in self.tasks:
            icon = {
                TaskStatus.PENDING: "⏳",
                TaskStatus.IN_PROGRESS: "🔄",
                TaskStatus.COMPLETED: "✅",
                TaskStatus.FAILED: "❌",
                TaskStatus.BLOCKED: "🚫",
            }[task.status]
            deps = f" (depends on: {', '.join(task.dependencies)})" if task.dependencies else ""
            lines.append(f"   {icon} {task.id}: {task.description}{deps}")
        return "\n".join(lines)


class SimplePlanner:
    """Simple rule-based planner."""
    
    def create_plan(self, goal: str, context: str = "") -> Plan:
        """
        Create a plan from a goal.
        
        This is a simple implementation that parses common patterns.
        A more sophisticated version would use an LLM.
        """
        import re
        
        plan = Plan(goal=goal, context=context)
        
        # Simple pattern matching for common tasks
        goal_lower = goal.lower()
        
        # Check for URLs first (before other patterns)
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, goal)
        if urls:
            plan.add_task(Task(
                id="1",
                description=f"Fetch URL: {urls[0]}",
                tool="web_fetch",
                args={"url": urls[0]}
            ))
            plan.add_task(Task(
                id="2",
                description="Analyze content",
                dependencies=["1"],
            ))
            return plan
        
        # Web research pattern
        if any(w in goal_lower for w in ["search", "find", "research", "look up"]):
            # Extract what to search for
            query = goal
            for prefix in ["search for", "find", "research", "look up"]:
                if prefix in goal_lower:
                    query = goal_lower.split(prefix, 1)[-1].strip()
                    break
            
            plan.add_task(Task(
                id="1",
                description=f"Search web for: {query}",
                tool="web_search",
                args={"query": query}
            ))
            plan.add_task(Task(
                id="2",
                description="Fetch top result",
                dependencies=["1"],
                tool="web_fetch",
                args={}  # Will fill in from result
            ))
            plan.add_task(Task(
                id="3",
                description="Summarize findings",
                dependencies=["2"],
            ))
        
        # File analysis pattern
        elif any(w in goal_lower for w in ["analyze", "read", "check file"]):
            # Try to find filepath
            words = goal.split()
            filepath = None
            for i, word in enumerate(words):
                if '.' in word and len(word) > 2:
                    filepath = word.strip(".,!?")
                    break
            
            if filepath:
                plan.add_task(Task(
                    id="1",
                    description=f"Read file: {filepath}",
                    tool="read_file",
                    args={"path": filepath}
                ))
                plan.add_task(Task(
                    id="2",
                    description="Analyze content",
                    dependencies=["1"],
                ))
        
        # Shell command pattern
        elif any(w in goal_lower for w in ["run", "execute", "command", "list files", "show directory"]):
            # Try to infer command
            cmd = None
            if "list files" in goal_lower or "show" in goal_lower and "directory" in goal_lower:
                cmd = "ls -la"
            elif "current directory" in goal_lower or "pwd" in goal_lower:
                cmd = "pwd"
            
            if cmd:
                plan.add_task(Task(
                    id="1",
                    description=f"Execute: {cmd}",
                    tool="exec",
                    args={"command": cmd}
                ))
        
        # Generic single-task plan
        else:
            plan.add_task(Task(
                id="1",
                description=goal,
            ))
        
        return plan
    
    def replan(self, plan: Plan, feedback: str) -> Plan:
        """
        Adjust plan based on feedback.
        
        Args:
            plan: Current plan
            feedback: Reason for replanning
        
        Returns:
            Updated plan
        """
        # Simple implementation - could use LLM for sophisticated replanning
        plan.add_task(Task(
            id=f"replan_{len(plan.tasks)}",
            description=f"Replan: {feedback}",
            dependencies=[t.id for t in plan.tasks if not t.is_complete],
        ))
        return plan


class StepPlanner:
    """Planner that works step-by-step with user/agent."""
    
    def next_step(self, goal: str, previous_actions: List[Dict], 
                  context: str = "") -> Dict:
        """
        Determine next step based on history.
        
        Returns dict with:
        - thought: reasoning about what to do
        - action: tool to use or "done"
        - action_input: arguments for tool
        - observation: expected outcome
        """
        # This would typically use an LLM
        # Simple rule-based version:
        
        if not previous_actions:
            # First step
            return {
                "thought": f"I need to accomplish: {goal}",
                "action": "think",
                "action_input": {"about": goal},
                "observation": "Will plan approach",
            }
        
        last_action = previous_actions[-1]
        
        # Check if done
        if len(previous_actions) > 5:  # Arbitrary limit
            return {
                "thought": "Task appears complete based on action history",
                "action": "done",
                "action_input": {},
                "observation": "Task complete",
            }
        
        # Continue based on last action
        return {
            "thought": "Continuing with next logical step",
            "action": "think",
            "action_input": {"about": "next steps"},
            "observation": "Planning continuation",
        }
