"""Meta-cognition for autonomous replanning - Cursor-style interleaving."""

import re
from typing import List, Dict, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ReplanReason(Enum):
    """Reasons for autonomous replanning."""
    BLOCKED = "blocked"  # Dependencies failed
    ERROR = "error"      # Tool execution failed
    WRONG_APPROACH = "wrong_approach"  # Plan isn't working
    NEW_INFO = "new_info"  # Learned something that changes plan
    INEFFICIENT = "inefficient"  # Better path discovered
    COMPLEX = "complex"  # Problem harder than expected


@dataclass
class MetaThought:
    """A meta-level thought about planning/reasoning."""
    timestamp: datetime = field(default_factory=datetime.now)
    observation: str = ""  # What I observed
    reflection: str = ""   # My analysis
    decision: str = ""       # What I decided
    confidence: float = 0.0  # How confident I am (0-1)


@dataclass
class ExecutionState:
    """Captures current execution state for metacognition."""
    step_count: int = 0
    successful_steps: int = 0
    failed_steps: int = 0
    last_result: Any = None
    errors: List[str] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)
    context_changes: List[str] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        total = self.successful_steps + self.failed_steps
        return self.successful_steps / total if total > 0 else 1.0
    
    @property
    def is_struggling(self) -> bool:
        """Check if having difficulty."""
        return self.failed_steps > 2 or self.success_rate < 0.5
    
    @property
    def summary(self) -> str:
        """Human-readable state summary."""
        return (
            f"Step {self.step_count}: "
            f"{self.successful_steps} successful, "
            f"{self.failed_steps} failed, "
            f"{len(self.errors)} errors, "
            f"{len(self.blockers)} blockers"
        )


class MetacognitiveMonitor:
    """
    Monitors execution and decides when to replan.
    
    Like Cursor's orchestrator, but with intelligence about
    WHEN planning is needed vs just executing.
    """
    
    def __init__(self):
        self.history: List[MetaThought] = []
        self.rules: List[Callable] = [
            self._check_for_errors,
            self._check_for_blockers,
            self._check_for_inefficiency,
            self._check_for_complexity,
        ]
    
    def should_replan(self, state: ExecutionState, 
                      plan: Any, 
                      last_action: str,
                      last_result: Any) -> Optional[ReplanReason]:
        """
        Autonomously decide if replanning is needed.
        
        Args:
            state: Current execution state
            plan: Current plan
            last_action: Last action taken
            last_result: Result of last action
        
        Returns:
            ReplanReason if replanning needed, None otherwise
        """
        # Update state
        state.last_result = last_result
        
        # Run all monitoring rules
        for rule in self.rules:
            reason = rule(state, plan, last_action, last_result)
            if reason:
                # Log the decision
                self._record_thought(
                    observation=state.summary,
                    reflection=f"Detected condition for {reason.value}",
                    decision=f"Recommend replanning: {reason.value}"
                )
                return reason
        
        return None
    
    def _check_for_errors(self, state: ExecutionState, 
                          plan: Any, 
                          action: str,
                          result: Any) -> Optional[ReplanReason]:
        """Check if recent action failed."""
        if result is None:
            state.failed_steps += 1
            return ReplanReason.ERROR
        
        # Check if result indicates error
        if isinstance(result, str) and any(x in result.lower() for x in ["error", "failed", "exception"]):
            state.failed_steps += 1
            state.errors.append(result[:100])
            
            # Multiple errors = blocked
            if len(state.errors) > 2:
                return ReplanReason.BLOCKED
            return ReplanReason.ERROR
        
        state.successful_steps += 1
        return None
    
    def _check_for_blockers(self, state: ExecutionState,
                            plan: Any,
                            action: str,
                            result: Any) -> Optional[ReplanReason]:
        """Check if dependencies blocking progress."""
        # Check plan health
        if hasattr(plan, 'tasks'):
            pending = sum(1 for t in plan.tasks if t.status.name == 'PENDING')
            failed = sum(1 for t in plan.tasks if t.status.name == 'FAILED')
            
            if failed > 0 and pending > 0:
                # Some tasks failed but others pending - blocked
                state.blockers.append(f"{failed} failed tasks blocking {pending} pending")
                return ReplanReason.BLOCKED
            
            # Stuck on same task for many iterations
            if state.step_count > 10 and pending == 0:
                return ReplanReason.COMPLEX
        
        return None
    
    def _check_for_inefficiency(self, state: ExecutionState,
                                plan: Any,
                                action: str,
                                result: Any) -> Optional[ReplanReason]:
        """Check if there's a better approach."""
        # Too many retries on same type of action
        if state.failed_steps > 3:
            return ReplanReason.INEFFICIENT
        
        return None
    
    def _check_for_complexity(self, state: ExecutionState,
                              plan: Any,
                              action: str,
                              result: Any) -> Optional[ReplanReason]:
        """Check if problem is more complex than initial plan."""
        # Many steps taken but low success rate
        if state.step_count > 5 and state.success_rate < 0.4:
            return ReplanReason.COMPLEX
        
        return None
    
    def _record_thought(self, observation: str, 
                        reflection: str, 
                        decision: str) -> None:
        """Record a metacognitive thought."""
        thought = MetaThought(
            observation=observation,
            reflection=reflection,
            decision=decision
        )
        self.history.append(thought)
    
    def get_insights(self) -> List[str]:
        """Get insights from meta-cognitive history."""
        insights = []
        
        if not self.history:
            return ["No metacognitive history yet"]
        
        # Analyze patterns
        error_count = sum(1 for t in self.history if "error" in t.decision.lower())
        blocker_count = sum(1 for t in self.history if "block" in t.reflection.lower())
        
        if error_count > 3:
            insights.append(f"{error_count} replans due to errors - execution prone to failures")
        
        if blocker_count > 2:
            insights.append(f"{blocker_count} replans due to blockers - plan had dependency issues")
        
        insights.append(f"Total metacognitive checks: {len(self.history)}")
        
        return insights


class PlanValidator:
    """Validates if a plan is still viable."""
    
    @staticmethod
    def validate(plan: Any, context: Dict) -> Dict[str, Any]:
        """
        Validate if current plan still makes sense given context.
        
        Returns dict with:
        - is_valid: bool
        - issues: List[str]
        - recommendations: List[str]
        """
        result = {
            "is_valid": True,
            "issues": [],
            "recommendations": []
        }
        
        if not hasattr(plan, 'tasks'):
            return result
        
        # Check for stale conditions
        initial_assumptions = getattr(plan, 'context', '')
        current_state = context.get('current_state', '')
        
        if initial_assumptions and current_state:
            # Simple check: did key assumptions change?
            # (In real implementation, this would be more sophisticated)
            pass
        
        # Check task dependencies
        for task in plan.tasks:
            if hasattr(task, 'dependencies'):
                for dep_id in task.dependencies:
                    dep_task = plan.get_task(dep_id)
                    if dep_task and dep_task.status.name == 'FAILED':
                        result["is_valid"] = False
                        result["issues"].append(f"Dependency {dep_id} failed")
        
        return result


class AdaptivePlanner:
    """
    Planner that adapts based on execution feedback.
    
    Extends SimplePlanner with learning from execution.
    """
    
    def __init__(self, base_planner):
        self.base_planner = base_planner
        self.execution_patterns: Dict[str, int] = {}
    
    def replan(self, session: Any, 
               reason: ReplanReason,
               state: ExecutionState) -> Any:
        """
        Create a new plan based on execution feedback.
        
        Args:
            session: Current agent session
            reason: Why we're replanning
            state: Current execution state
        
        Returns:
            New plan
        """
        # Learn from pattern
        pattern_key = f"{session.goal[:50]}-{reason.value}"
        self.execution_patterns[pattern_key] = self.execution_patterns.get(pattern_key, 0) + 1
        
        # Adjust strategy based on reason
        if reason == ReplanReason.ERROR:
            # Be more careful: add verification steps
            new_plan = self._create_safer_plan(session)
        elif reason == ReplanReason.BLOCKED:
            # Remove failed dependencies
            new_plan = self._create_alternative_plan(session)
        elif reason == ReplanReason.INEFFICIENT:
            # Simplify approach
            new_plan = self._create_simplified_plan(session)
        elif reason == ReplanReason.COMPLEX:
            # Break into sub-agents
            new_plan = self._create_subagent_plan(session)
        else:
            # Standard replan
            new_plan = self.base_planner.replan(session.plan, reason.value)
        
        # Record that we adapted
        session.replan_count = getattr(session, 'replan_count', 0) + 1
        
        return new_plan
    
    def _create_safer_plan(self, session: Any) -> Any:
        """Create a plan with more verification steps."""
        # Add intermediate checkpoints
        base_plan = self.base_planner.create_plan(session.goal)
        # (In real implementation, would add verify steps)
        return base_plan
    
    def _create_alternative_plan(self, session: Any) -> Any:
        """Create plan avoiding current blockers."""
        # Remove or work around failed tasks
        return self.base_planner.create_plan(session.goal + " (alternative approach)")
    
    def _create_simplified_plan(self, session: Any) -> Any:
        """Create a more direct plan."""
        return self.base_planner.create_plan(session.goal + " (simplified)")
    
    def _create_subagent_plan(self, session: Any) -> Any:
        """Break into sub-agent tasks."""
        # Would spawn specialized sub-agents
        return self.base_planner.create_plan(session.goal + " (with sub-agents)")


class ContextAwareRetriever:
    """
    Retrieves relevant context before each decision.
    
    Like Cursor's context retrieval system, but per-step.
    """
    
    def __init__(self, javis: Any):
        self.javis = javis
    
    def retrieve(self, current_thought: str, 
                 plan: Any,
                 max_items: int = 5) -> Dict[str, Any]:
        """
        Retrieve relevant context for current decision point.
        
        Args:
            current_thought: What the agent is currently thinking
            plan: Current plan
            max_items: Max context items to retrieve
        
        Returns:
            Relevant context
        """
        context = {}
        
        # 1. Relevant memories
        # Search for similar past experiences
        recall_results = self.javis.recall(current_thought[:50])
        context["memories"] = recall_results[:500]
        
        # 2. Current session context
        if hasattr(plan, 'tasks'):
            active_tasks = [t for t in plan.tasks 
                          if t.status.name in ['IN_PROGRESS', 'PENDING']]
            context["active_tasks"] = active_tasks[:max_items]
        
        # 3. Current execution state
        # (Would include recent tool outputs, errors, etc.)
        
        return context
