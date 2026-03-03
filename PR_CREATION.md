# Pull Request for LLM-Powered Metacognition

## Summary
This PR adds true LLM-powered metacognitive replanning to the Javis agent.

## Changes Made

### 1. Updated `javis/metacognition.py`
- **Added `LLMMetacognitiveAnalyzer` class**: Uses actual language model for intelligent decision making instead of hardcoded rules
- **Enhanced `MetacognitiveMonitor`**: Now combines LLM-powered analysis with rule-based fallback for reliability
- **New prompt system**: Creates structured prompts that ask the LLM to analyze execution context and decide on replanning strategy
- **LLM reasoning extraction**: Parses natural language responses from the model to extract decisions and confidence levels

### 2. Updated `javis/agent.py`
- **Integrated metacognitive monitor**: Agent now initializes and uses the LLM-powered monitor during execution
- **Added monitoring logic**: Agent loop queries the LLM when tasks fail or encounter issues
- **State tracking**: Monitors success rates, error counts, and execution patterns to inform the LLM

## Key Features

### Before (Rule-Based)
```python
# Hardcoded thresholds
if failed_steps > 3:
    return ReplanReason.INEFFICIENT
if success_rate < 0.4:
    return ReplanReason.COMPLEX
```

### After (LLM-Powered)
```python
# LLM analyzes context and decides
analysis = llm_analyzer.analyze(state, plan, action, result)
# Returns intelligent reasoning like:
# "Agent is stuck in retry loop on web search. Try alternative approach with different query strategy."
```

## Benefits

1. **Intelligent Decision Making**: LLM can understand nuanced situations and provide context-aware recommendations
2. **Natural Language Reasoning**: Get explanations of WHY replanning is needed, not just a flag
3. **Adaptive Strategies**: Can suggest custom fixes rather than choosing from predefined plan types
4. **Backward Compatible**: Falls back to rule-based if LLM unavailable or fails

## Testing

To test the new metacognition:
```python
agent = JavisAgent()
session = agent.run("Research Python async patterns")
# Watch for "🧠 Metacognitive decision" messages in output
```

## Files Changed
- `javis/metacognition.py` - Added LLM-powered analyzer (239 lines added)
- `javis/agent.py` - Integrated metacognitive monitor into agent loop

---

**Note**: The PR title and description are ready to use. Just create the pull request on GitHub!
