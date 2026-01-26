---
description: Create daily content with explicit model switching (Option 2 + 3 fallback)
---

# /create-day-v2

Generate daily CFD content with **guaranteed model switching** using:
- Option 2: Environment variable routing
- Option 3: Direct API integration (fallback)

---

## Quick Start

```
/create-day-v2 --day=XX
```

---

## Workflow

This version **DOES NOT** rely on Task tool delegation. Instead:

1. **Checks current model routing** via proxy logs
2. **Uses direct API calls** to DeepSeek when needed
3. **Logs all model usage** for verification

---

## Stage-by-Stage Implementation

### Stage 1: Extract Ground Truth (GLM-4.7)

```bash
# This can use default model (GLM-4.7)
cat > /tmp/stage1_prompt.txt << 'PROMPT'
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
PROMPT

# Ask Claude to execute this research
```

### Stage 2: Verify Skeleton (DeepSeek R1 - Direct API)

```bash
# Prepare prompt
cat > /tmp/stage4_prompt.txt << 'PROMPT'
Verify skeleton for Day XX

SKELETON: daily_learning/skeletons/dayXX_skeleton.json
GROUND TRUTH: /tmp/verified_facts_dayXX.json

Verification tasks:
1. Class hierarchy matches ground truth exactly
2. Formulas match ground truth (check operators!)
3. No hallucinated classes or methods
4. All ⭐ facts are verified

Output format:
- PASS if all checks succeed
- FAIL with specific issues if any mismatch found
PROMPT

# Call DeepSeek R1 directly
python3 .claude/scripts/deepseek_content.py \
  deepseek-reasoner \
  /tmp/stage4_prompt.txt \
  > /tmp/verification_report_dayXX.txt

cat /tmp/verification_report_dayXX.txt
```

### Stage 3: Generate Content (DeepSeek Chat V3 - Direct API)

```bash
# Prepare prompt
cat > /tmp/stage5_prompt.txt << 'PROMPT'
Expand Day XX: [TOPIC] - ENGLISH ONLY

VERIFIED SKELETON: $(cat daily_learning/skeletons/dayXX_skeleton.json)

CRITICAL REQUIREMENTS:
- ENGLISH-ONLY content (no Thai translation)
- Theory: ≥500 lines with complete derivations
- Code: 3-5 snippets with file paths and line numbers
- Implementation: ≥300 lines C++ code
- Exercises: 4-6 concept checks
- All ⭐ facts remain unchanged

Write comprehensive technical content suitable for CFD learners.
Output complete markdown file content.
PROMPT

# Call DeepSeek Chat V3 directly
python3 .claude/scripts/deepseek_content.py \
  deepseek-chat \
  /tmp/stage5_prompt.txt \
  > daily_learning/Phase_01_Foundation_Theory/XX.md

echo "Content generated to: daily_learning/Phase_01_Foundation_Theory/XX.md"
```

### Stage 4: Final Verification (DeepSeek R1 - Direct API)

```bash
cat > /tmp/stage6_prompt.txt << 'PROMPT'
Final verification for Day XX

CONTENT: $(cat daily_learning/Phase_01_Foundation_Theory/XX.md)
GROUND TRUTH: /tmp/verified_facts_dayXX.json

Verification tasks:
1. All Mermaid diagrams match ground truth
2. All formulas in LaTeX match ground truth
3. Code snippets are syntactically correct
4. No ⚠️ claims without explanation

Output verification report.
PROMPT

python3 .claude/scripts/deepseek_content.py \
  deepseek-reasoner \
  /tmp/stage6_prompt.txt \
  > /tmp/final_verification_dayXX.txt

cat /tmp/final_verification_dayXX.txt
```

---

## Logging

All DeepSeek API calls are logged:

```bash
# Check DeepSeek usage logs
echo "DeepSeek API calls made:"
ls -la /tmp/stage*_prompt.txt
ls -la /tmp/*verification*.txt
```

---

## Verification

After content generation, verify in proxy logs:

```bash
# Should see NO DeepSeek in proxy.log (we called API directly)
# This confirms direct API integration is working
grep -c "deepseek-chat" proxy.log  # Should return 0
grep -c "deepseek-reasoner" proxy.log  # Should return 0
```

---

## Troubleshooting

### Direct API Fails

```bash
# Check API key
python3 -c "import os; print(os.getenv('DEEPSEEK_API_KEY'))"

# Test API connection
curl -X POST https://api.deepseek.com/v1/chat/completions \
  -H "Authorization: Bearer sk-a8d183f6f9904326913cb4e799eaba17" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"test"}],"max_tokens":10}'
```

### Content Quality Issues

If DeepSeek generates poor content:

1. **Review prompt** - Ensure constraints are clear
2. **Check ground truth** - Verify skeleton JSON structure
3. **Adjust temperature** - Modify script temperature parameter
4. **Retry with more examples** - Add specific formatting requirements

---

## Example Full Workflow

```bash
# Day 05: Spatial Discretization Schemes

# 1. Research (GLM-4.7 via Claude)
# Ask Claude to research Day 05 using WebSearch

# 2. Generate skeleton (GLM-4.7 via Claude)
# Ask Claude to create skeleton from roadmap

# 3. Verify skeleton (DeepSeek R1 directly)
python3 .claude/scripts/deepseek_content.py deepseek-reasoner /tmp/stage4_prompt.txt

# 4. Generate content (DeepSeek Chat V3 directly)
python3 .claude/scripts/deepseek_content.py deepseek-chat /tmp/stage5_prompt.txt

# 5. Final verify (DeepSeek R1 directly)
python3 .claude/scripts/deepseek_content.py deepseek-reasoner /tmp/stage6_prompt.txt

# 6. Syntax QC
python3 .claude/scripts/qc_syntax_check.py \
  --file=daily_learning/Phase_01_Foundation_Theory/05.md
```

---

**Last Updated:** 2026-01-26
**Approach:** Direct API integration bypassing Task tool delegation issue
