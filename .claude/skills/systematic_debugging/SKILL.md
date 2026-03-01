---
name: systematic_debugging
description: The Iron Law of Debugging - find root causes before applying fixes
---

# Systematic Debugging

## Overview
Random fixes waste time and create new bugs. Quick patches mask underlying issues.
**Core principle:** ALWAYS find root cause before attempting fixes. Symptom fixes are failure.

## The Iron Law
```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

## When to Use
Use for ANY technical issue: test failures, bugs in production, unexpected behavior.
**ESPECIALLY when:**
- Under time pressure
- "Just one quick fix" seems obvious
- You've already tried multiple fixes

## The Four Phases
You MUST complete each phase before proceeding to the next.

### Phase 1: Root Cause Investigation
**BEFORE attempting ANY fix:**
1. **Read Error Messages Carefully**: Don't skip. Read stack traces completely.
2. **Reproduce Consistently**: Can you trigger it reliably? If not, gather more data.
3. **Check Recent Changes**: Git diff, recent commits, environmental differences.
4. **Trace Data Flow**: Where does bad value originate? Trace backward.

### Phase 2: Pattern Analysis
1. **Find Working Examples**: What works that's similar to what's broken?
2. **Identify Differences**: List every difference between working and broken.
3. **Understand Dependencies**: What assumptions does it make?

### Phase 3: Hypothesis and Testing
1. **Form Single Hypothesis**: "I think X is the root cause because Y".
2. **Test Minimally**: Make the SMALLEST possible change to test it.
3. **Verify Before Continuing**: Did it work? If not, form NEW hypothesis.

### Phase 4: Implementation
1. **Create Failing Test Case**: Simplest possible reproduction.
2. **Implement Single Fix**: Address root cause. ONE change at a time.
3. **Verify Fix**: Test passes now? Issue resolved?
