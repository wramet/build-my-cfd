---
name: source-first
description: Extract and verify technical facts from source code using Source-First methodology
---

# Source-First Methodology

Extract and verify technical facts from source code before using AI to generate or explain content.

## Core Principle

🔒 **Ground Truth from source code > AI analysis > Internal training**

## When to Use

Use Source-First when creating content that requires technical accuracy:

- ✅ Class hierarchies and inheritance structures
- ✅ Mathematical formulas and equations
- ✅ API signatures and method names
- ✅ Code examples and implementation details
- ✅ Technical documentation and references

Optional for:
- ❌ General conceptual explanations
- ❌ High-level overviews
- ❌ Non-technical commentary

## The Workflow

### 1. Extract Facts First

Before asking AI to explain or generate content, extract ground truth from actual source code:

```
Extract class hierarchy from: openfoam_temp/src/finiteVolume
Extract formulas from actual .H and .C files
Verify operator accuracy (|r| vs r matters!)
```

### 2. Structure and Verify

Structure extracted facts into JSON format and verify:
- Output files exist and are non-empty
- JSON structure is valid
- No extraction errors

### 3. Constrain AI with Ground Truth

Provide AI with explicit ground truth as constraints:

```
**🔒 CRITICAL CONSTRAINTS - YOU MUST FOLLOW:**
[verified_facts.json content]

**Rules:**
- Use ONLY class hierarchy from constraints above
- Use ONLY formulas from constraints above
- If something doesn't exist → Use 'TODO: VERIFY'
```

### 4. Verify Outputs

After AI generates content, verify against ground truth:
- Class hierarchy matches source
- Formulas match implementation
- No hallucinated classes or methods

## Verification Markers

Use these markers in generated content:

```markdown
### ⭐ Verified Fact
> Content verified from actual source code at file:line

### ⚠️ Unverified Claim
> Content from documentation, needs source verification

### ❌ Incorrect
> Common misconception - here's the correct version
```

## Common Pitfalls

### Assuming AI Knows

**Wrong:** "Ask GLM-4.7 what the upwind class hierarchy is"

**Right:** "Extract hierarchy from source code, then ask GLM to explain it"

### Verifying After Creation

**Wrong:** "Generate content, then verify"

**Right:** "Extract ground truth, verify skeleton, THEN expand content"

### Ignoring Verification Failures

**Wrong:** "Close enough, proceed anyway"

**Right:** "Stop, fix, re-verify before proceeding"

## Available Tools

- `extract_facts.py` - Extract class hierarchies and formulas from source
- `verify_skeleton.py` - Verify AI-generated skeleton against ground truth
- `verify_content.py` - Verify final content against ground truth

## See Also

- [Verification Gates](references/verification-gates.md) - Detailed gate instructions
- [CFD Content Standards](../../rules/cfd-standards.md) - Formatting and syntax rules
