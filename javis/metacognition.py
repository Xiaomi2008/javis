"""Meta-cognition for autonomous replanning - LLM-powered intelligent planning."""

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
    reflection: str = ""   # My analysis (LLM-generated reasoning)
    decision: str = ""       # What I decided
    confidence: float = 0.0  # How confident I am (0-1)
    llm_analysis: Optional[str] = None  # Raw LLM output for transparency


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


class LLMMetacognitiveAnalyzer:
    """
    LLM-powered metacognitive analyzer for intelligent replanning decisions.
    
    Instead of hardcoded rules, this uses an actual language model to analyze
    execution context and determine the best course of action.
    """
    
    def __init__(self, agent_session):
        """
        Initialize with access to the agent's session/model.
        
        Args:
            agent_session: The Javis agent session with model calling capability
        """
        self.agent = agent_session
        self.analysis_count = 0
    
    def analyze(self, state: ExecutionState, 
                plan: Any,
                last_action: str,
                last_result: Any) -> Optional[str]:
        """
        Use LLM to analyze execution context and determine if replanning is needed.
        
        Args:
            state: Current execution state
            plan: Current plan
            last_action: Last action taken
            last_result: Result of last action
        
        Returns:
            ReplanReason string if replanning needed, None otherwise
            Or LLM's custom analysis in natural language
        """
        self.analysis_count += 1
        
        # Build context for the LLM
        context = self._build_analysis_context(state, plan, last_action, last_result)
        
        # Create prompt for metacognitive reasoning
        prompt = self._create_metacognition_prompt(context)
        
        try:
            # Call the agent's model to analyze the situation
            analysis_response = self.agent.call_model(
                system_message=self._get_system_prompt(),
                user_message=prompt,
                temperature=0.3  # Low temp for consistent reasoning
            )
            
            # Parse LLM response to extract decision and reasoning
            return self._parse_llm_analysis(analysis_response, state)
            
        except Exception as e:
            # Fallback to rule-based if LLM fails
            print(f"LLM metacognition failed: {e}, falling back to rules")
            return None
    
    def _build_analysis_context(self, state: ExecutionState, 
                                plan: Any,
                                last_action: str,
                                last_result: Any) -> Dict[str, Any]:
        """Build comprehensive context for LLM analysis."""
        return {
            "goal": getattr(plan, 'goal', 'Unknown goal'),
            "step_count": state.step_count,
            "success_rate": f"{state.success_rate:.1%}",
            "failed_steps": state.failed_steps,
            "recent_errors": state.errors[-3:] if state.errors else [],
            "blockers": state.blockers[-2:] if state.blockers else [],
            "last_action": last_action[:200],  # Truncate for context window
            "last_result_summary": str(last_result)[:500] if last_result else "None",
            "is_struggling": state.is_struggling,
        }
    
    def _create_metacognition_prompt(self, context: Dict[str, Any]) -> str:
        """Create a prompt for the LLM to analyze execution and decide on replanning."""
        return f"""You are an intelligent planning assistant analyzing agent execution.

EXECUTION CONTEXT:
- Goal: {context['goal']}
- Current Step: {context['step_count']}
- Success Rate: {context['success_rate']}
- Failed Steps: {context['failed_steps']}
- Recent Errors: {context['recent_errors'] or 'None'}
- Blockers: {context['blockers'] or 'None'}

LAST ACTION & RESULT:
- Action: {context['last_action']}
- Result: {context['last_result_summary']}

IS THE AGENT STRUGGLING? {context['is_struggling']}

ANALYSIS TASKS:
1. Should the agent replan right now? (yes/no)
2. If yes, what type of problem is this? Choose one:
   - BLOCKED: Dependencies failed blocking progress
   - ERROR: Tool execution failed
   - WRONG_APPROACH: Strategy isn't working
   - INEFFICIENT: Better path exists
   - COMPLEX: Problem harder than expected
   - CONTINUE: Keep going, no replanning needed

3. Provide specific reasoning for your decision (2-4 sentences)

Respond in this EXACT format:
DECISION: [BLOCKED|ERROR|WRONG_APPROACH|INEFFICIENT|COMPLEX|CONTINUE]
REASONING: [Your explanation here]"""
    
    def _get_system_prompt(self) -> str:
        """System prompt for the LLM metacognitive analyzer."""
        return """You are an expert planning and execution analysis AI. Your job is to analyze agent execution context and determine whether replanning is needed, and if so, what type of problem exists.

Be analytical but practical. Consider:
- Is the agent making progress toward its goal?
- Are errors recoverable or indicative of fundamental problems?
- Would a different approach be more efficient?
- Is the problem complexity being underestimated?

Your analysis should be concise and actionable."""
    
    def _parse_llm_analysis(self, response: str, state: ExecutionState) -> Optional[str]:
        """Parse LLM response to extract decision and reasoning."""
        try:
            # Extract DECISION line
            decision_match = re.search(r'DECISION:\s*(\w+)', response, re.IGNORECASE)
            if not decision_match:
                return None
            
            decision = decision_match.group(1).upper()
            
            # Map to ReplanReason enum or CONTINUE
            valid_reasons = ['BLOCKED', 'ERROR', 'WRONG_APPROACH', 'INEFFICIENT', 'COMPLEX']
            if decision in valid_reasons:
                return decision
            
            # If CONTINUE, no replanning needed
            if decision == 'CONTINUE':
                return None
            
            # Fallback to ERROR for unknown decisions
            print(f"Unknown LLM decision: {decision}, treating as ERROR")
            return ReplanReason.ERROR.value
            
        except Exception as e:
            print(f"Failed to parse LLM analysis: {e}")
            return None


class MetacognitiveMonitor:
    """
    Monitors execution and decides when to replan using LLM intelligence.
    
    Combines LLM-powered analysis with rule-based fallback for reliability.
    """
    
    def __init__(self, agent_session=None):
        self.history: List[MetaThought] = []
        self.agent_session = agent_session
        
        # Initialize LLM analyzer if we have access to the agent
        self.llm_analyzer = None
        if agent_session:
            try:
                self.llm_analyzer = LLMMetacognitiveAnalyzer(agent_session)
            except Exception as e:
                print(f"Could not initialize LLM metacognition: {e}")
        
        # Rule-based fallback (still used for quick checks and when LLM unavailable)
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
        Decide if replanning is needed using LLM analysis with rule fallback.
        
        Priority order:
        1. Try LLLM-powered analysis (preferred for intelligent decisions)
        2. Fall back to rule-based checks if LLM unavailable or fails
        
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
        
        # Try LLM analysis first (if available)
        if self.llm_analyzer:
            llm_decision = self.llm_analyzer.analyze(state, plan, last_action, last_result)
            if llm_decision and llm_decision != 'CONTINUE':
                reason = ReplanReason(llm_decision.lower())
                # Log the LLM-powered decision
                self._record_thought(
                    observation=state.summary,
                    reflection=f"LLM analysis detected {reason.value}",
                    decision=f"Recommend replanning: {reason.value}"
                )
                return reason
        
        # Fallback to rule-based checks if no LLM or LLM says CONTINUE
        for rule in self.rules:
            reason = rule(state, plan, last_action, last_result)
            if reason:
                # Log the decision (rule-based fallback)
                self._record_thought(
                    observation=state.summary,
                    reflection=f"Rule detected condition for {reason.value}",
                    decision=f"Recommend replanning: {reason.value}"
                )
                return reason
        
        return None
    
    def _check_for_errors(self, state: ExecutionState, 
                          plan: Any, 
                          action: str,
                          result: Any) -> Optional[ReplanReason]:
        """Quick rule-based error detection (fallback)."""
        if result is None:
            state.failed_steps += 1
            return ReplanReason.ERROR
        
        if isinstance(result, str) and any(x in result.lower() for x in ["error", "failed", "exception"]):
            state.failed_steps += 1
            state.errors.append(result[:100])
            
            if len(state.errors) > 2:
                return ReplanReason.BLOCKED
            return ReplanReason.ERROR
        
        state.successful_steps += 1
        return None
    
    def _check_for_blockers(self, state: ExecutionState,
                            plan: Any,
                            action: str,
                            result: Any) -> Optional[ReplanReason]:
        """Quick rule-based blocker detection (fallback)."""
        if hasattr(plan, 'tasks'):
            pending = sum(1 for t in plan.tasks if t.status.name == 'PENDING')
            failed = sum(1 for t in plan.tasks if t.status.name == 'FAILED')
            
            if failed > 0 and pending > 0:
                state.blockers.append(f"{failed} failed tasks blocking {pending} pending")
                return ReplanReason.BLOCKED
            
            if state.step_count > 10 and pending == 0:
                return ReplanReason.COMPLEX
        
        return None
    
    def _check_for_inefficiency(self, state: ExecutionState,
                                plan: Any,
                                action: str,
                                result: Any) -> Optional[ReplanReason]:
        """Quick rule-based efficiency check (fallback)."""
        if state.failed_steps > 3:
            return ReplanReason.INEFFICIENT
        
        return None
    
    def _check_for_complexity(self, state: ExecutionState,
                              plan: Any,
                              action: str,
                              result: Any) -> Optional[ReplanReason]:
        """Quick rule-based complexity check (fallback)."""
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
        llm_usage = sum(1 for t in self.history if "llm" in t.reflection.lower())
        
        if error_count > 3:
            insights.append(f"{error_count} replans due to errors - execution prone to failures")
        
        if blocker_count > 2:
            insights.append(f"{blocker_count} replans due to blockers - plan had dependency issues")
        
        insights.append(f"Total metacognitive checks: {len(self.history)}")
        insights.append(f"LLM-powered decisions: {llm_usage}")
        
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
    Planner that adapts based on LLM-powered metacognitive feedback.
    
    Extends SimplePlanner with intelligent learning from execution.
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
            reason: Why we're replanning (from LLM analysis or rules)
            state: Current execution state
        
        Returns:
            New plan adapted to the situation
        """
        # Learn from pattern
        pattern_key = f"{session.goal[:50]}-{reason.value}"
        self.execution_patterns[pattern_key] = self.execution_patterns.get(pattern_key, 0) + 1
        
        # Adjust strategy based on reason (now informed by LLM analysis)
        if reason == ReplanReason.ERROR:
            new_plan = self._create_safer_plan(session)
        elif reason == ReplanReason.BLOCKED:
            new_plan = self._create_alternative_plan(session)
        elif reason == ReplanReason.INEFFICIENT:
            new_plan = self._create_simplified_plan(session)
        elif reason == ReplanReason.COMPLEX:
            new_plan = self._create_subagent_plan(session)
        elif reason == ReplanReason.WRONG_APPROACH:
            # LLM detected wrong approach - try completely different strategy
            new_plan = self._create_alternative_strategy(session)
        else:
            new_plan = self.base_planner.replan(session.plan, reason.value)
        
        session.replan_count = getattr(session, 'replan_count', 0) + 1
        
        return new_plan
    
    def _create_safer_plan(self, session: Any) -> Any:
        """Create a plan with more verification steps."""
        base_plan = self.base_planner.create_plan(session.goal)
        return base_plan
    
    def _create_alternative_plan(self, session: Any) -> Any:
        """Create plan avoiding current blockers."""
        return self.base_planner.create_plan(session.goal + " (alternative approach)")
    
    def _create_simplified_plan(self, session: Any) -> Any:
        """Create a more direct plan."""
        return self.base_planner.create_plan(session.goal + " (simplified)")
    
    def _create_subagent_plan(self, session: Any) -> Any:
        """Break into sub-agent tasks for complex problems."""
        return self.base_planner.create_plan(session.goal + " (with sub-agents)")
    
    def _create_alternative_strategy(self, session: Any) -> Any:
        """Create plan with completely different approach (LLM detected wrong strategy)."""
        return self.base_planner.create_plan(session.goal + " (different strategy)")


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
        recall_results = self.javis.recall(current_thought[:50])
        context["memories"] = recall_results[:500]
        
        # 2. Current session context
        if hasattr(plan, 'tasks'):
            active_tasks = [t for t in plan.tasks 
                          if t.status.name in ['IN_PROGRESS', 'PENDING']]
            context["active_tasks"] = active_tasks[:max_items]
        
        return context
