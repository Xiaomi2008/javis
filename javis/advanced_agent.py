"""Advanced Agent with Cursor-style meta-cognition and interleaved planning."""

import threading
from typing import List, Dict, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
import concurrent.futures

from core import Javis
from agent import JavisAgent, AgentThought, AgentSession
from planner import SimplePlanner, Plan, Task, TaskStatus
from metacognition import (
    MetacognitiveMonitor, AdaptivePlanner, ContextAwareRetriever,
    ExecutionState, ReplanReason, PlanValidator
)


@dataclass
class ParallelAgent:
    """A sub-agent that can work in parallel."""
    name: str
    role: str
    agent: JavisAgent
    assigned_tasks: List[str] = field(default_factory=list)
    results: List[Any] = field(default_factory=list)
    status: str = "idle"  # idle, running, completed, failed


class AdvancedAgent(JavisAgent):
    """
    Advanced agent with Cursor-style meta-cognition.
    
    Key features:
    1. ReAct pattern: interleaves Reason → Action → Observation
    2. Meta-cognition: autonomously decides when to replan
    3. Context-aware: retrieves fresh context per step
    4. Parallel agents: can spawn sub-agents for complex tasks
    5. Plan validation: validates plan health each iteration
    
    Example:
        >>> agent = AdvancedAgent()
        >>> session = agent.run("Build a complex system")
        >>> # Agent automatically replans if needed
    """
    
    def __init__(self, javis: Optional[Javis] = None,
                 planner: Optional[SimplePlanner] = None,
                 enable_parallel: bool = True):
        """
        Initialize advanced agent.
        
        Args:
            javis: Javis instance
            planner: Planner to use
            enable_parallel: Allow parallel sub-agents
        """
        super().__init__(javis, planner)
        
        # Meta-cognition components
        self.monitor = MetacognitiveMonitor()
        self.adaptive_planner = AdaptivePlanner(self.planner)
        self.context_retriever = ContextAwareRetriever(self.javis)
        self.plan_validator = PlanValidator()
        
        # Execution state tracking
        self.state = ExecutionState()
        
        # Parallel execution
        self.enable_parallel = enable_parallel
        self.sub_agents: Dict[str, ParallelAgent] = {}
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)
        
        # Role-based mode (like Cursor's roles)
        self.current_role = "general"
        self.roles = {
            "planner": "Focus on architecture and planning",
            "implementer": "Focus on code implementation",
            "debugger": "Focus on finding and fixing issues",
            "general": "General purpose action",
        }
        
        print("🧠 AdvancedAgent initialized with meta-cognition")
    
    def run(self, goal: str, max_iterations: int = 20,
            auto_approve: bool = True) -> AgentSession:
        """
        Run agent with Cursor-style interleaved planning.
        
        Args:
            goal: Goal to achieve
            max_iterations: Max steps
            auto_approve: Auto-approve actions
        
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
        
        # Reset execution state
        self.state = ExecutionState()
        
        print(f"🤖 AdvancedAgent run: {goal}")
        print(f"   Max iterations: {max_iterations}")
        print(f"   Meta-cognition: ENABLED")
        print()
        
        # START WITH PLANNING PHASE
        print("📋 Phase 1: Planning...")
        session.plan = self._initial_plan(session)
        print(f"   Created plan with {len(session.plan.tasks)} tasks\n")
        
        # INTERLEAVED EXECUTION PHASE
        print("🔄 Phase 2: Interleaved Execution...")
        try:
            while (session.status == "active" and 
                   session.current_iteration < session.max_iterations):
                
                session.current_iteration += 1
                self.state.step_count = session.current_iteration
                
                print(f"\n--- Step {session.current_iteration} ---")
                
                # 1. REINFORCE (Check if replanning is needed)
                if self._should_replan(session):
                    print("   🔄 Meta-cognition: Replanning needed")
                    session.plan = self._replan(session)
                    print(f"   New plan has {len(session.plan.tasks)} tasks")
                
                # 2. RETRIEVE (Get fresh context)
                context = self._retrieve_context(session)
                
                # 3. REASON (Think about what to do)
                thought = self._react_reason(session, context)
                
                # 4. ACT (Execute action)
                observation = self._react_act(thought, session)
                
                # 5. REFLECT (Process result)
                reflection = self._react_reflect(session, thought, observation)
                
                # Record the ReAct cycle
                self._add_thought(session, 
                    thought=f"{thought.get('thought', '')}",
                    action=thought.get('action', ''),
                    action_input=thought.get('action_input', {}),
                    observation=str(observation),
                    reflection=reflection
                )
                
                # Update state
                self._update_state(observation)
                
                # Check for parallel agent opportunity
                if self.enable_parallel and self._should_spawn_parallel(session):
                    self._spawn_parallel_subagent(session)
                
                # Check if done
                if session.plan.is_complete or self._is_goal_achieved(session):
                    session.status = "completed"
                    break
                    
        except Exception as e:
            session.status = "failed"
            self._add_thought(session,
                thought=f"Agent failed: {e}",
                action="error",
                observation=str(e)
            )
        
        # Finalize
        session.end_time = datetime.now()
        
        print(f"\n✅ Session {session.status}: {session.current_iteration} iterations")
        self._print_metacognition_summary()
        
        return session
    
    # === ReAct Pattern Implementation ===
    
    def _react_reason(self, session: AgentSession, 
                      context: Dict) -> Dict[str, Any]:
        """
        REASON step: Think about what to do next.
        
        Returns dict with:
        - thought: reasoning string
        - action: tool to use or "done"
        - action_input: arguments for tool
        """
        # Get next task or decide next action
        task = session.plan.get_next_task()
        
        if not task:
            return {
                "thought": "No more tasks - goal achieved",
                "action": "done",
                "action_input": {}
            }
        
        # Reason about current situation
        reasoning_parts = [
            f"Current goal: {session.goal}",
            f"Working on task: {task.description}",
            f"Step {session.current_iteration}",
            f"Progress: {session.current_iteration}/{session.max_iterations}",
        ]
        
        # Consider context
        if context.get("memories"):
            reasoning_parts.append(f"Context: {context['memories'][:100]}...")
        
        # Decide tool
        if task.tool:
            action = task.tool
            action_input = task.args or {}
        else:
            # Infer from task description
            action, action_input = self._infer_tool_from_description(task.description)
        
        return {
            "thought": " | ".join(reasoning_parts),
            "action": action,
            "action_input": action_input
        }
    
    def _react_act(self, thought: Dict, session: AgentSession) -> Any:
        """
        ACT step: Execute the chosen action.
        """
        action = thought.get("action", 'think')
        action_input = thought.get("action_input", {})
        
        # Approval check
        if not session.auto_approve:
            approved = self._request_approval(thought, session)
            if not approved:
                return "User declined this action"
        
        # Execute
        if action in self._tools:
            try:
                result = self._tools[action](**action_input)
                print(f"   ✅ {action}: {str(result)[:60]}...")
                return result
            except Exception as e:
                print(f"   ❌ {action}: Error - {e}")
                return f"Error: {e}"
        else:
            return f"Unknown action: {action}"
    
    def _react_reflect(self, session: AgentSession,
                       thought: Dict,
                       observation: Any) -> str:
        """
        REFLECT step: Process the observation.
        """
        reflection_parts = []
        
        # Check success
        if "Error" in str(observation):
            reflection_parts.append(f"Action failed: {observation}")
        else:
            reflection_parts.append(f"Action succeeded: {observation}")
        
        # Update task status
        task = session.plan.get_next_task()
        if task:
            task.status = TaskStatus.COMPLETED if "Error" not in str(observation) else TaskStatus.FAILED
            task.result = observation
        
        # Progress assessment
        if session.plan.is_complete:
            reflection_parts.append("Plan complete!")
        
        return " | ".join(reflection_parts)
    
    # === Meta-Cognition ===
    
    def _should_replan(self, session: AgentSession) -> bool:
        """
        Autonomously decide if replanning is needed.
        """
        # Get last action result
        last_thought = session.thoughts[-1] if session.thoughts else None
        last_result = last_thought.observation if last_thought else None
        last_action = last_thought.action if last_thought else ""
        
        # Check with monitor
        reason = self.monitor.should_replan(
            self.state, session.plan, last_action, last_result
        )
        
        return reason is not None
    
    def _replan(self, session: AgentSession) -> Plan:
        """Replan based on execution state."""
        # Find replan reason
        last_thought = session.thoughts[-1] if session.thoughts else None
        last_result = last_thought.observation if last_thought else None
        last_action = last_thought.action if last_thought else ""
        
        reason = self.monitor.should_replan(
            self.state, session.plan, last_action, last_result
        )
        
        if not reason:
            reason = ReplanReason.NEW_INFO
        
        print(f"   Replanning due to: {reason.value}")
        
        # Use adaptive planner
        return self.adaptive_planner.replan(session, reason, self.state)
    
    def _retrieve_context(self, session: AgentSession) -> Dict:
        """Retrieve fresh context for current decision."""
        context = {}
        
        # Get recent memories relevant to current task
        task = session.plan.get_next_task()
        if task:
            context["memories"] = self.javis.recall(task.description[:50])
        
        # Get session context
        context["plan_progress"] = session.plan.progress
        
        # Get execution state
        context["state"] = self.state.summary
        
        return context
    
    # === Planning ===
    
    def _initial_plan(self, session: AgentSession) -> Plan:
        """Create initial plan."""
        return self.planner.create_plan(
            session.goal,
            self.javis.context
        )
    
    def _infer_tool_from_description(self, description: str) -> tuple:
        """Infer appropriate tool from task description."""
        import re
        
        desc_lower = description.lower()
        
        # Check for URLs first (before file detection)
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, description)
        if urls:
            return "web_fetch", {"url": urls[0]}
        
        if any(w in desc_lower for w in ["search", "find", "look up", "google"]):
            return "web_search", {"query": description}
        elif any(w in desc_lower for w in ["read", "show", "get content", "file"]):
            # Try to extract filepath (but not URLs)
            path = description.split()[-1]
            if not path.startswith(('http://', 'https://')):
                return "read_file", {"path": path}
            else:
                return "web_fetch", {"url": path}
        elif any(w in desc_lower for w in ["run", "execute", "command"]):
            cmd = description.replace("run", "").replace("execute", "").strip()
            return "exec", {"command": cmd}
        else:
            return "think", {"about": description}
    
    # === Parallel Sub-Agents ===
    
    def _should_spawn_parallel(self, session: AgentSession) -> bool:
        """Check if should spawn parallel sub-agent."""
        if not self.enable_parallel:
            return False
        
        # Spawn if task is complex and not too many sub-agents
        if (self.state.failed_steps > 2 and 
            len(self.sub_agents) < 3):
            return True
        
        return False
    
    def _spawn_parallel_subagent(self, session: AgentSession) -> None:
        """Spawn a specialized sub-agent in parallel."""
        # Create sub-agent with specific role
        role = self._choose_role_for_task(session)
        
        sub_agent = JavisAgent()
        parallel_agent = ParallelAgent(
            name=f"subagent_{len(self.sub_agents)}",
            role=role,
            agent=sub_agent
        )
        
        self.sub_agents[parallel_agent.name] = parallel_agent
        
        print(f"   🔄 Spawned parallel {role} sub-agent")
        
        # Run in background
        future = self.executor.submit(
            parallel_agent.agent.run,
            f"{role} subtask for: {session.goal}"
        )
    
    def _choose_role_for_task(self, session: AgentSession) -> str:
        """Choose appropriate role based on current needs."""
        if self.state.failed_steps > 0:
            return "debugger"
        elif session.current_iteration < 5:
            return "planner"
        else:
            return "implementer"
    
    # === Utility ===
    
    def _choose_role(self) -> str:
        """Choose appropriate role for current step."""
        if self.state.failed_steps > 2:
            return "debugger"
        elif self.state.step_count < 3:
            return "planner"
        else:
            return "implementer"
    
    def _update_state(self, observation: Any) -> None:
        """Update execution state with observation."""
        # This is handled by monitor, but we can add more tracking here
        pass
    
    def _is_goal_achieved(self, session: AgentSession) -> bool:
        """Check if goal has been achieved."""
        # Simple heuristic: if enough successful steps and plan complete
        return (session.plan.is_complete and 
                self.state.successful_steps > len(session.plan.tasks) * 0.5)
    
    def _print_metacognition_summary(self) -> None:
        """Print summary of meta-cognitive activity."""
        print("\n🧠 Meta-Cognition Summary:")
        for insight in self.monitor.get_insights():
            print(f"   • {insight}")
        
        if self.sub_agents:
            print(f"\n   Parallel sub-agents spawned: {len(self.sub_agents)}")


class ReActAgent(AdvancedAgent):
    """
    Pure ReAct agent - interleaves Reasoning, Acting, Reflecting.
    
    Simplified version focusing only on ReAct pattern.
    """
    
    def run(self, goal: str, **kwargs) -> AgentSession:
        """Run with pure ReAct loop."""
        print(f"🔄 ReAct Agent: {goal}")
        
        session = super().run(goal, **kwargs)
        
        print(f"\n   ReAct cycles: {len(session.thoughts)}")
        return session
