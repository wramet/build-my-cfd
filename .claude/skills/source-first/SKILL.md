# Source-First Methodology

## Core Principle

🔒 **Ground Truth from source code > AI analysis > Internal training**

## What is Source-First?

Source-First is a methodology for creating technically accurate content by:

1. **Extracting facts FIRST** from actual source code
2. **Constraining AI** to use only verified facts
3. **Verifying outputs** at each stage before proceeding
4. **Marking verified content** with ⭐ for transparency

## Why Source-First?

AI models can **hallucinate** technical details:
- Wrong class hierarchies
- Incorrect mathematical formulas
- Non-existent API methods
- Inaccurate code snippets

Source-First prevents this by anchoring all content in **verified ground truth**.

## The 6-Stage Workflow

### Stage 1: Extract Ground Truth

```bash
# Extract class hierarchy
python3 .claude/scripts/extract_facts.py \
    --mode hierarchy \
    --path "openfoam_temp/src/finiteVolume" \
    --output /tmp/ground_truth.txt

# Extract formulas
python3 .claude/scripts/extract_facts.py \
    --mode formulas \
    --path "openfoam_temp/src/finiteVolume" \
    --output /tmp/formulas.txt
```

### Stage 2: Structure Facts

```bash
python3 .claude/scripts/extract_facts.py \
    --mode structure \
    --input /tmp/ground_truth.txt \
    --output /tmp/verified_facts.json
```

### Stage 3: AI Analyzes WITH Constraints

Provide AI with EXPLICIT ground truth as constraints:

```
**🔒 CRITICAL CONSTRAINTS - YOU MUST FOLLOW:**
[verified_facts.json content]

**Rules:**
- Use ONLY class hierarchy from constraints above
- Use ONLY formulas from constraints above
- If something doesn't exist in constraints → Use 'TODO: VERIFY'
```

### Stage 4: Verify Skeleton

```bash
python3 .claude/scripts/verify_skeleton.py \
    --ground-truth /tmp/verified_facts.json \
    --skeleton output_skeleton.json \
    --output verification_report.md
```

**If verification fails:** Stop and fix before proceeding.

### Stage 5: AI Expands WITH Verification

Expand content with verified skeleton:
- Include verification report in prompt
- Mark verified facts with ⭐
- Label unverified content clearly

### Stage 6: Final Verification

```bash
python3 .claude/scripts/verify_content.py \
    --content final_content.md \
    --ground-truth /tmp/verified_facts.json \
    --output final_verification.md
```

## When to Use Source-First

Use for:
- ✅ Technical documentation
- ✅ API references
- ✅ Code examples
- ✅ Mathematical formulas
- ✅ Class hierarchies
- ✅ Implementation details

Don't need for:
- ❌ General concepts
- ❌ High-level overviews
- ❌ Non-technical content
- ❌ Opinions or commentary

## Verification Markers

Use these markers in content:

```markdown
### ⭐ Verified Fact
> Content verified from actual source code

### ⚠️ Unverified Claim
> Content from documentation, needs verification

### ❌ Incorrect
> Common misconception (corrected)
```

## Common Pitfalls

### Pitfall 1: Assuming AI Knows

**Wrong:** "Ask GLM-4.7 what the upwind class hierarchy is"

**Right:** "Extract hierarchy from source code, then ask GLM to explain it"

### Pitfall 2: Verifying After Creation

**Wrong:** "Generate content, then verify"

**Right:** "Verify skeleton BEFORE expanding content"

### Pitfall 3: Ignoring Verification Failures

**Wrong:** "Close enough, proceed anyway"

**Right:** "Stop, fix, re-verify before proceeding"

## Best Practices

1. **Extract First:** Always extract ground truth before involving AI
2. **Verify Early:** Verify at skeleton stage, not after content is complete
3. **Be Explicit:** Include ground truth as constraints in AI prompts
4. **Mark Verified:** Use ⭐ for verified facts, be transparent about uncertainty
5. **Fail Fast:** Stop workflow immediately when verification fails

## Example: Class Hierarchy

### ❌ Without Source-First

```
User: "Explain the upwind class hierarchy"
AI: "upwind inherits from surfaceInterpolationScheme"
Reality: WRONG - missing intermediate class!
```

### ✅ With Source-First

```
1. Extract: upwind → limitedSurfaceInterpolationScheme → surfaceInterpolationScheme
2. Verify: Check against source code
3. Constrain AI: "Use hierarchy: upwind → limitedSurfaceInterpolationScheme → surfaceInterpolationScheme"
4. Output: Accurate diagram with ⭐ marker
```

## Example: Mathematical Formula

### ❌ Without Source-First

```
AI: "van Leer limiter: φ(r) = (r + 1)/(1 + r)"
Reality: WRONG - denominator should be (1 + |r|)!
```

### ✅ With Source-First

```
1. Extract from source: return (r + mag(r))/(1 + mag(r));
2. Convert: mag(r) → |r|
3. Verify: φ(r) = (r + |r|)/(1 + |r|)
4. Constrain AI: Use exact formula from source
5. Output: ⭐ Verified formula
```

## Tools & Scripts

### extract_facts.py
Extracts ground truth from OpenFOAM source code

Modes:
- `hierarchy`: Extract class inheritance
- `formulas`: Extract mathematical formulas
- `structure`: Parse and structure into JSON

### verify_skeleton.py
Verifies AI-generated skeleton against ground truth

Checks:
- Class hierarchy matches source
- Formulas match implementation
- No hallucinated content

### verify_content.py
Verifies final content against ground truth

Checks:
- Mermaid diagrams are accurate
- Formulas are correct
- Code snippets are valid

## Summary

Source-First = **Extract → Verify → Constrain AI → Expand → Verify Again**

By following this methodology, you ensure:
- ✅ Technical accuracy
- ✅ No hallucinations
- ✅ Traceable facts
- ✅ Transparent uncertainty

---

**Related Skills:** `ground-truth-verification`, `engineering-thai`
