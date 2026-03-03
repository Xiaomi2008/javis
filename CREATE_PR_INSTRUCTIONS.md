# How to Create This Pull Request Manually

## Quick Steps

1. Go to https://github.com/Xiaomi2008/javis
2. Click **"Pull requests"** tab → **"New pull request"** button
3. **Base**: `master` | **Compare**: `master` (same branch)
4. Fill in the details below

## PR Details

### Title
```
feat: Add LLM-powered metacognitive replanning to Javis agent
```

### Description
Copy and paste this entire block:

---

This PR adds true LLM-powered metacognition to the Javis agent. The `MetacognitiveMonitor` now uses an actual language model for intelligent decision making instead of hardcoded rules, with a fallback system for reliability.

## Changes Made

### 1. Updated `javis/metacognition.py`
- **Added `LLMMetacognitiveAnalyzer` class**: Uses actual language model for intelligent decision making instead of hardcoded rules
- **Enhanced `MetacognitiveMonitor`**: Now combines LLM-powered analysis with rule-based fallback for reliability
- **New prompt system**: Creates structured prompts that ask the LLM to analyze execution context and decide on replanning strategy

### 2. Updated `javis/agent.py`
- **Integrated metacognitive monitor**: Agent now initializes and uses the LLM-powered monitor during execution
- **Added monitoring logic**: Agent loop queries the LLM when tasks fail or encounter issues

## Key Features

### Before (Rule-Based)
```python
if failed_steps > 3:
    return ReplanReason.INEFFICIENT
```

### After (LLM-Powered)
The agent now queries an actual language model which can provide reasoning like:
> "Agent is stuck in retry loop on web search. Try alternative approach with different query strategy."

## Benefits

1. **Intelligent Decision Making**: LLM understands nuanced situations and provides context-aware recommendations
2. **Natural Language Reasoning**: Get explanations of WHY replanning is needed, not just a flag
3. **Adaptive Strategies**: Can suggest custom fixes rather than choosing from predefined plan types
4. **Backward Compatible**: Falls back to rules if LLM unavailable or fails

## Files Changed
- `javis/metacognition.py` - Added LLM-powered analyzer (239 lines added)
- `javis/agent.py` - Integrated metacognitive monitor into agent loop

---

## After Creating the PR

Once you've created it, I can help with:
- Reviewing the changes
- Adding reviewers
- Setting up CI checks
- Any other follow-up tasks

Let me know when it's done! 🎉
