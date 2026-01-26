---
description: Create daily learning content (English-only) using Source-First approach with Direct API integration for DeepSeek models
---

# /create-day

Generate daily CFD learning content (**English-only**) with Source-First methodology and **Direct API integration**.

## Important: Model Switching Issue

The `Task` tool in Claude Code has a **Lazy Delegation** issue - it loads agent personas but doesn't actually switch API models.

**Solution:** This skill now uses **direct API calls** to DeepSeek when needed, bypassing the Task tool limitation.

---

## Usage

```
/create-day --day=XX
```

Where `XX` is the day number (01-12).

---

## Workflow Overview

This skill executes a complete 6-stage pipeline:

| Stage | Model | API Method | Purpose |
|-------|--------|-------------|---------|
| 1 | GLM-4.7 | Main Agent | Ground truth extraction (WebSearch + Source) |
| 2 | GLM-4.7 | Main Agent | Create CFD curriculum skeleton |
| 3 | DeepSeek R1 | **Direct API** | Verify skeleton against ground truth |
| 4 | DeepSeek Chat V3 | **Direct API** | Expand to full English content |
| 5 | DeepSeek R1 | **Direct API** | Final technical verification |
| 6 | - | Python Script | Syntax QC |

---

## Quick Start

```
/create-day --day=05
```

This provides step-by-step instructions for each stage.

---

## Stage-by-Stage Instructions

### Stage 1: Extract Ground Truth (GLM-4.7 via Main Agent)

**Purpose:** Extract verified facts from OpenFOAM source code AND find latest documentation

**Prompt to Claude:**
```
Research Day XX: [TOPIC]

Tasks:
1. Use WebSearch to find latest OpenFOAM documentation
2. Extract class hierarchy from source code in openfoam_temp/src/finiteVolume
3. Extract mathematical formulas with operators (|r| vs r)
4. Mark all facts with ⭐ (verified) or ⚠️ (from docs)

Output: /tmp/verified_facts_dayXX.json (JSON format)

Use this JSON structure:
{
  "class_hierarchy": {},
  "formulas": {},
  "documentation": []
}
```

**Output:** `/tmp/verified_facts_dayXX.json` ⭐

---

### Stage 2: Generate Skeleton (GLM-4.7 via Main Agent)

**Purpose:** Create CFD curriculum structure from roadmap + ground truth (**English-only**)

**Prompt to Claude:**
```
Plan Day XX: [TOPIC]

GROUND TRUTH: /tmp/verified_facts_dayXX.json

Create ENGLISH-ONLY skeleton with:
- English headers only (no Thai translation)
- Roadmap-aligned structure (read roadmap.md)
- CFD standards compliance
- All verified facts marked with ⭐

Output: daily_learning/skeletons/dayXX_skeleton.json
```

**Output:** `skeletons/dayXX_skeleton.json`

---

### Stage 3: Verify Skeleton (DeepSeek R1 - Direct API)

**Script:**
```bash
# Prepare prompt
cat > /tmp/stage3_prompt.txt << 'PROMPT'
Verify skeleton for Day XX

SKELETON: $(cat daily_learning/skeletons/dayXX_skeleton.json)
GROUND TRUTH: $(cat /tmp/verified_facts_dayXX.json)

Verification tasks:
1. Class hierarchy matches ground truth exactly
2. Formulas match ground truth (check operators!)
3. No hallucinated classes or methods
4. All ⭐ facts are verified

Output format:
- PASS if all checks succeed
- FAIL with specific issues if any mismatch found

Be thorough and specific about any issues found.
PROMPT

# Call DeepSeek R1 directly
python3 .claude/scripts/deepseek_content.py \
  deepseek-reasoner \
  /tmp/stage3_prompt.txt \
  > /tmp/verification_report_dayXX.txt

cat /tmp/verification_report_dayXX.txt
```

**Output:** `/tmp/verification_report_dayXX.txt`

---

### Stage 4: Generate Content (DeepSeek Chat V3 - Direct API)

**Script:**
```bash
# Prepare prompt
cat > /tmp/stage4_prompt.txt << 'PROMPT'
Expand Day XX: [TOPIC] - ENGLISH ONLY

SKELETON: $(cat daily_learning/skeletons/dayXX_skeleton.json)

CRITICAL REQUIREMENTS:
- ENGLISH-ONLY content (no Thai translation)
- Theory: ≥500 lines with complete derivations
- Code: 3-5 snippets with file paths and line numbers
- Implementation: ≥300 lines C++ code
- Exercises: 4-6 concept checks
- All ⭐ facts remain unchanged

Write comprehensive technical content suitable for CFD learners.

Format:
- Use $$ for display math equations
- Use $ for inline math
- Include proper Mermaid diagrams
- All code blocks must have language tags
- Headers in English only

Output complete markdown file content.
PROMPT

# Call DeepSeek Chat V3 directly
python3 .claude/scripts/deepseek_content.py \
  deepseek-chat \
  /tmp/stage4_prompt.txt \
  > daily_learning/Phase_01_Foundation_Theory/XX.md

echo "Content generated to: daily_learning/Phase_01_Foundation_Theory/XX.md"
```

**Output:** `Phase_01_Foundation_Theory/XX.md`

---

### Stage 5: Final Verification (DeepSeek R1 - Direct API)

**Script:**
```bash
cat > /tmp/stage5_prompt.txt << 'PROMPT'
Final verification for Day XX

CONTENT: $(cat daily_learning/Phase_01_Foundation_Theory/XX.md)
GROUND TRUTH: $(cat /tmp/verified_facts_dayXX.json)

Verification tasks:
1. All Mermaid diagrams match ground truth
2. All formulas in LaTeX match ground truth (check operators!)
3. Code snippets are syntactically correct
4. No ⚠️ claims without explanation

Output verification report with specific issues if any found.
PROMPT

python3 .claude/scripts/deepseek_content.py \
  deepseek-reasoner \
  /tmp/stage5_prompt.txt \
  > /tmp/final_verification_dayXX.txt

cat /tmp/final_verification_dayXX.txt
```

**Output:** `/tmp/final_verification_dayXX.txt`

---

### Stage 6: Syntax QC (Python Script)

**Script:**
```bash
python3 .claude/scripts/qc_syntax_check.py \
  --file=daily_learning/Phase_01_Foundation_Theory/XX.md

# Check exit code
if [ $? -eq 0 ]; then
  echo "✅ Syntax QC PASSED"
else
  echo "❌ Syntax QC FAILED - Fix issues before publishing"
fi
```

**Output:** QC report + pass/fail status

---

## Content Requirements

| Section | Minimum | Details |
|---------|---------|---------|
| Theory | ≥500 lines | Equations + explanations + derivations |
| Code Analysis | 3-5 snippets | Must include file paths and line numbers |
| Implementation | ≥300 lines C++ | Step-by-step breakdown |
| Exercises | 4-6 questions | With detailed solutions |

---

## Verification

### Verify Direct API is Working

After running any DeepSeek stage:

```bash
# Check proxy logs - should show NO DeepSeek (we bypass proxy)
grep -c "deepseek-chat" proxy.log  # Should return 0
grep -c "deepseek-reasoner" proxy.log  # Should return 0

# Check direct API calls were made
ls -la /tmp/stage*_prompt.txt
ls -la /tmp/*verification*.txt
```

### Expected Behavior

```
Stage 1-2: Main Agent (GLM-4.7) → Uses proxy
Stage 3-5: DeepSeek API Direct → BYPASSES proxy
```

---

## Troubleshooting

### Direct API Fails

```bash
# Test API connection
curl -X POST https://api.deepseek.com/v1/chat/completions \
  -H "Authorization: Bearer sk-a8d183f6f9904326913cb4e799eaba17" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"test"}],"max_tokens":10}'

# Check if requests is installed
python3 -c "import requests; print('requests available')"

# Check API key in script
grep DEEPSEEK_API_KEY .claude/scripts/deepseek_content.py
```

### Content Quality Issues

If DeepSeek generates poor content:

1. **Review prompt** - Ensure constraints are clear
2. **Check ground truth** - Verify skeleton JSON structure
3. **Adjust temperature** - Modify script (default 0.7)
4. **Retry with more examples** - Add specific formatting requirements

### JSON Validation

```bash
# Validate ground truth structure
python3 -c "import json; json.load(open('/tmp/verified_facts_dayXX.json'))"

# Validate skeleton structure
python3 -c "import json; json.load(open('daily_learning/skeletons/dayXX_skeleton.json'))"
```

---

## Full Example Workflow

```bash
# Day 05: Spatial Discretization Schemes

# 1. Research (ask Claude with prompt from Stage 1)
# 2. Create skeleton (ask Claude with prompt from Stage 2)

# 3. Verify skeleton (DeepSeek R1 directly)
python3 .claude/scripts/deepseek_content.py deepseek-reasoner /tmp/stage3_prompt.txt

# 4. Generate content (DeepSeek Chat V3 directly)
python3 .claude/scripts/deepseek_content.py deepseek-chat /tmp/stage4_prompt.txt

# 5. Final verify (DeepSeek R1 directly)
python3 .claude/scripts/deepseek_content.py deepseek-reasoner /tmp/stage5_prompt.txt

# 6. Syntax QC
python3 .claude/scripts/qc_syntax_check.py \
  --file=daily_learning/Phase_01_Foundation_Theory/05.md
```

---

## Key Principles

### Source-First Rule

```
Ground Truth from Source > Documentation > AI Analysis
```

### Model Assignment

| Task | Model | Method | Why? |
|------|--------|---------|-------|
| Ground Truth | GLM-4.7 | Main Agent + WebSearch |
| Skeleton | GLM-4.7 | Main Agent knows roadmap |
| Verify | DeepSeek R1 | **Direct API** - reasoning |
| Content | DeepSeek Chat V3 | **Direct API** - math+physics |
| Final Verify | DeepSeek R1 | **Direct API** - thorough check |

### English-Only Content

- ✅ All content in English
- ✅ No Thai translation required
- ✅ Headers in English only
- ✅ Technical terms in English

---

## Output Files

| Stage | Model | File | Description |
|-------|--------|------|-------------|
| 1 | GLM-4.7 | `/tmp/verified_facts_dayXX.json` | Ground truth ⭐ |
| 2 | GLM-4.7 | `skeletons/dayXX_skeleton.json` | CFD curriculum skeleton |
| 3 | DeepSeek R1 | `/tmp/verification_report_dayXX.txt` | Skeleton verification |
| 4 | DeepSeek Chat V3 | `Phase_01_Foundation_Theory/XX.md` | English content |
| 5 | DeepSeek R1 | `/tmp/final_verification_dayXX.txt` | Final verification |
| 6 | - | QC report | Syntax validation |

---

## Architecture Diagram

```mermaid
flowchart TD
    Start([/create-day --day=XX]) --> R1[Stage 1: Research<br/>GLM-4.7<br/>Main Agent]
    R1 --> F[verified_facts_dayXX.json ⭐]
    F --> R2[Stage 2: Skeleton<br/>GLM-4.7<br/>Main Agent]
    R2 --> S[skeletons/dayXX_skeleton.json]
    S --> V1[Stage 3: Verify<br/>DeepSeek R1<br/>Direct API]
    V1 -->|Pass ✅| D[Stage 4: Content<br/>DeepSeek Chat V3<br/>Direct API]
    V1 -->|Fail ❌| R2
    D --> C[Phase_01/XX.md]
    C --> V2[Stage 5: Final Verify<br/>DeepSeek R1<br/>Direct API]
    V2 --> QC[Stage 6: Syntax QC<br/>Python Script]
    QC --> Done([✅ Complete])

    style R1 fill:#e1f5e1,stroke:#4caf50
    style R2 fill:#e1f5e1,stroke:#4caf50
    style V1 fill:#f8d7da,stroke:#dc3545
    style V2 fill:#f8d7da,stroke:#dc3545
    style D fill:#e0e0e0,stroke:#6c757d
    style QC fill:#fff3cd,stroke:#ffc107
    style Done fill:#d4edda,stroke:#28a745
```

---

**Last Updated:** 2026-01-26
**Approach:** Direct API integration for DeepSeek models (bypasses Task tool Lazy Delegation)
