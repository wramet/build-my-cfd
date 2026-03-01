---
name: walkthrough
description: Generate interactive walkthrough content for daily CFD learning materials with Source-First verification
---

# Interactive Walkthrough Generation

Generate step-by-step interactive tutoring for daily learning content with strict Source-First verification.

## Core Process

When generating a walkthrough for daily learning content:

1. **Read Daily Content** - Load content from `daily_learning/Phase_XX_YourPhase/XX.md`
2. **Extract Ground Truth** - Mine OpenFOAM source code for verified facts
3. **Analyze Sections** - Process Theory, Code, and Implementation sections
4. **Verify Against Ground Truth** - Ensure technical accuracy at each step
5. **Generate Output** - Create walkthrough with verification markers

## Model Assignment

| Stage | Primary Model | Backup |
|-------|---------------|--------|
| Ground Truth | `extract_facts.py` | N/A |
| Theory/Math | DeepSeek R1 | GLM-4.7 |
| Code Structure | DeepSeek Chat V3 | DeepSeek R1 |
| Final Synthesis | GLM-4.7 | DeepSeek Chat V3 |

## Output Location

Walkthroughs are saved to:
```
daily_learning/walkthroughs/day_XX_walkthrough.md
```

## Verification Gates

The walkthrough workflow includes 6 mandatory verification gates:

1. **File Structure** - Input file exists with valid sections
2. **Ground Truth Extraction** - Minimum 5 facts extracted
3. **Theory Equations** - Equations match ground truth
4. **Code Structure** - Code aligns with ground truth
5. **Implementation** - Consistent with theory
6. **Final Coherence** - Overall consistency check

**STRICT:** Workflow STOPS on ANY failure with non-zero exit code.

## Verification Markers

Use these markers in generated walkthroughs:

- **⭐** = Verified from ground truth
- **⚠️** = Unverified (documentation source)
- **❌** = Incorrect/Don't

## Example Output Structure

```markdown
# Day XX Walkthrough
**Generated**: [Timestamp]
**Verification Status**: ✅ All 6 gates passed

## Ground Truth Extraction
⭐ [N] facts extracted from OpenFOAM source code

## Theory Section Walkthrough
⭐ [Explanation with verified facts]

## Code Section Analysis
⭐ [Analysis matching source code]

## Implementation Guidance
[Step-by-step guidance]

## Verification Summary
| Gate | Status | Details |
|------|--------|---------|
```

## Integration

This skill integrates with:

- `extract_facts.py` - Ground truth extraction
- `deepseek_content.py` - Model routing for DeepSeek R1/Chat V3
- Verification scripts in `.claude/scripts/`

## See Also

- [Detailed gate instructions](references/verification-gates.md)
- [Source-First methodology](../source-first/SKILL.md)
- [CFD content standards](../../rules/cfd-standards.md)
