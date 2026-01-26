---
description: Generate deep, comprehensive daily learning content using multi-agent pipeline (GLM + DeepSeek + Agent) with Ground Truth Verification
---

# /teach-deep Workflow
## Multi-Agent Content Generation Pipeline (with Verification)

> **Goal:** Generate 1,000+ line content with both pedagogical structure AND technical accuracy
>
> **🔒 Critical:** All AI-generated content MUST be verified against actual OpenFOAM source code before use

---

## Model Roles

| Stage | Model | Why |
|-------|-------|-----|
| **Research** | GLM-4.7 (Parallel) | High token capacity, good extraction |
| **Verification** | Python Script | Ground truth extraction from source code |
| **Math/Physics** | DeepSeek R1 (`deepseek-reasoner`) | Reasoning model, step-by-step derivation |
| **Code Analysis** | DeepSeek V3 (`deepseek-chat`) | Coding model, C++ understanding |
| **Synthesis** | DeepSeek V3 (`deepseek-chat`) | Long-form writing |
| **QC + Translation** | Agent (Claude/Gemini) | File access, cross-reference, skill integration |

---

## Prerequisites

```bash
# Verify DeepSeek is configured
llm keys | grep deepseek

# Verify GLM script exists
ls .agent/scripts/ask_glm.py

# Verify verification scripts exist
ls .agent/scripts/verify_*.py

# Install openai package if needed
pip install openai
```

---

## Workflow Steps

### Step 0: Initialize

```bash
# Set variables
export DAY="03"
export TOPIC="Spatial Discretization Schemes"
export PHASE="Phase_01_Foundation_Theory"

# Create drafts directory
mkdir -p daily_learning/drafts
```

---

### Step 0.5: Load Resources & Skeleton

**Critical:** Load the Skeleton JSON first. It is the distinct "Blueprint" for the lesson.

```bash
export SKELETON="daily_learning/skeletons/day${DAY}_skeleton.json"

# Check if skeleton exists
if [ ! -f "$SKELETON" ]; then
    echo "❌ Error: Skeleton file $SKELETON not found!"
    exit 1
fi

echo "✅ Blueprint loaded: $SKELETON"

# Extract Key Info for Research (Classes & headers)
python3 -c "import json, sys; sk=json.load(open('$SKELETON')); print('\n'.join([c['header'] for c in sk.get('openfoam_analysis', [])]))" > /tmp/target_headers.txt

python3 -c "import json, sys; sk=json.load(open('$SKELETON')); print('\n'.join([c['class'] for c in sk.get('openfoam_analysis', [])]))" > /tmp/target_classes.txt

echo "🎯 Targeted Research: $(cat /tmp/target_classes.txt | xargs)"
```

---

### Step 1: Targeted Research (GLM-4.7 + Agent)

Use the Skeleton's target list to find *exact* files, rather than guessing.

```bash
# Agent: Find exact file paths for the headers listed in Skeleton
echo -n > /tmp/found_files.txt
for header in $(cat /tmp/target_headers.txt); do
    find openfoam_temp -name "$(basename $header)" >> /tmp/found_files.txt
done

# GLM Instance A: Analyze Found Headers (Class Hierarchy & Methods)
cat /tmp/found_files.txt | xargs cat | python3 .agent/scripts/ask_glm.py -s "You are an OpenFOAM Expert. Analyze these specific headers defined in our lesson plan. Extract: Class inheritance, Virtual methods, Data members. Output Markdown." > daily_learning/drafts/day${DAY}_research_headers.md &

# GLM Instance B: Implementation Logic (Search based on classes)
echo -n > /tmp/found_impl.txt
for cls in $(cat /tmp/target_classes.txt | sed 's/<.*>//'); do
    grep -r "class $cls" openfoam_temp --include="*.C" -l >> /tmp/found_impl.txt
done

cat /tmp/found_impl.txt | xargs cat | head -c 50000 | python3 .agent/scripts/ask_glm.py -s "Analyze these implementation files. Focus on: How they calculate weights, flux, and limiters. Output logic analysis." > daily_learning/drafts/day${DAY}_research_impl.md &

# GLM Instance C: Context & Connections (From Skeleton)
python3 -c "import json; sk=json.load(open('$SKELETON')); print('Prior: ' + sk['connections']['previous_link'] + '\nNext: ' + sk['connections']['next_preview'])" > /tmp/connections.txt

cat daily_learning/${PHASE}/02.md /tmp/connections.txt | python3 .agent/scripts/ask_glm.py -s "Synthesize the connection between Day $((DAY-1)) and Day ${DAY}. Explain why we need this specific topic now." > daily_learning/drafts/day${DAY}_research_context.md &

wait
echo "✅ Targeted Research Complete"
```

---

### 🔒 Step 1.5: Verify GLM Research Against Actual Source Code (NEW)

**CRITICAL:** Do not proceed if discrepancies are found!

```bash
echo "🔍 Verifying GLM analysis against actual source code..."

# 1.5.1 Extract actual class hierarchy from found headers
> /tmp/actual_hierarchy.txt
for header in $(cat /tmp/found_files.txt); do
    echo "=== $header ===" >> /tmp/actual_hierarchy.txt
    # Extract inheritance: class className : public baseClass
    grep -E "class\s+\w+\s*:\s*public\s+\w+" "$header" >> /tmp/actual_hierarchy.txt
done

# 1.5.2 Run verification script
python3 .agent/scripts/verify_class_hierarchy.py \
    --actual-hierarchy /tmp/actual_hierarchy.txt \
    --claimed-analysis daily_learning/drafts/day${DAY}_research_headers.md \
    --output daily_learning/drafts/day${DAY}_verification_report.md

# 1.5.3 Check for discrepancies
if grep -q "❌ MISMATCH" daily_learning/drafts/day${DAY}_verification_report.md; then
    echo "⚠️  CLASS HIERARCHY DISCREPANCIES FOUND!"
    echo "========================================"
    cat daily_learning/drafts/day${DAY}_verification_report.md
    echo ""
    echo "❌ Halting workflow. Please review discrepancies and:"
    echo "   1. Fix the GLM analysis manually, OR"
    echo "   2. Update the skeleton if it was wrong"
    exit 1
else
    echo "✅ Class hierarchy verification passed"
fi
```

---

### Step 2: Merge Research Notes

```bash
cat daily_learning/drafts/day${DAY}_research_*.md > daily_learning/drafts/day${DAY}_research_notes.md
```

---

### Step 3: Math Derivation (DeepSeek R1 - Source Code Verified)

We force R1 to derive the *specific* equations, then verify against source code.

```bash
# Extract Theory Section from Skeleton to prompt R1
python3 -c "import json; sk=json.load(open('$SKELETON')); print(json.dumps(sk['theory_sections'], indent=2))" > /tmp/theory_reqs.json

cat daily_learning/drafts/day${DAY}_research_notes.md /tmp/theory_reqs.json | \
  llm -m deepseek-reasoner -s "You are a CFD Professor.
Task: Derive the mathematical formulations for Day ${DAY}.
CONSTRAINT: You MUST strictly follow the 'theory_sections' in the provided JSON.
1. Derive EVERY equation listed in the JSON from first principles.
2. Explain EVERY variable listed.
3. Address the specific 'warning' listed.
Output: LaTeX equations with detailed English explanations." > daily_learning/drafts/day${DAY}_math_derivation.md

echo "✅ Math Derivation Complete"
```

---

### 🔒 Step 3.5: Verify Math Formulas Against Source Code (NEW)

**CRITICAL:** Especially important for TVD limiters and stability criteria.

```bash
echo "🔍 Verifying mathematical formulas against source code..."

# 3.5.1 Extract actual formulas from implementation files
> /tmp/actual_formulas.txt
for impl_file in $(cat /tmp/found_impl.txt); do
    echo "=== $impl_file ===" >> /tmp/actual_formulas.txt
    # Extract limiter return statements
    grep -A 2 "return.*r\|return.*phi" "$impl_file" >> /tmp/actual_formulas.txt
done

# 3.5.2 Run formula verification
python3 .agent/scripts/verify_formulas.py \
    --actual-formulas /tmp/actual_formulas.txt \
    --claimed-formulas daily_learning/drafts/day${DAY}_math_derivation.md \
    --output daily_learning/drafts/day${DAY}_formula_verification.md

# 3.5.3 Check for discrepancies
if grep -q "❌ MISMATCH" daily_learning/drafts/day${DAY}_formula_verification.md; then
    echo "⚠️  FORMULA DISCREPANCIES FOUND!"
    echo "==================================="
    cat daily_learning/drafts/day${DAY}_formula_verification.md
    echo ""
    echo "❌ Halting workflow. Please review and fix formulas."
    exit 1
else
    echo "✅ Formula verification passed"
fi
```

---

### Step 4: Code Analysis (DeepSeek V3 - Verified Hierarchy)

```bash
# Extract OpenFOAM Analysis & Implementation Skeleton
python3 -c "import json; sk=json.load(open('$SKELETON')); print(json.dumps({'openfoam_analysis': sk['openfoam_analysis'], 'implementation_skeleton': sk['implementation_skeleton']}, indent=2))" > /tmp/code_reqs.json

# Include verification report in the prompt to ensure correct hierarchy
cat daily_learning/drafts/day${DAY}_verification_report.md daily_learning/drafts/day${DAY}_research_notes.md /tmp/code_reqs.json | \
  llm -m deepseek-chat -s "You are a C++ Expert.
Task: Analyze OpenFOAM code and Design Custom Implementation.
IMPORTANT: Use the VERIFIED class hierarchy from the verification report above.
DO NOT deviate from the actual inheritance relationships found in the source code.
1. Analyze the specific classes listed using ONLY the verified hierarchy.
2. Create Mermaid diagrams matching the ACTUAL inheritance (not the skeleton if they differ).
3. Design the 'SpatialDiscretizer' and 'TVDLimiter' classes as requested.
4. CLEARLY LABEL which classes are OpenFOAM standard vs project-specific custom implementation.
Output: Technical analysis and C++ design patterns." > daily_learning/drafts/day${DAY}_code_analysis.md

echo "✅ Code Analysis (Verified) Complete"
```

---

### 🔒 Step 4.5: Verify Code Analysis Content (NEW)

```bash
echo "🔍 Final verification of code analysis content..."

# Check that custom classes are clearly labeled
if ! grep -q "Project-Specific\|Custom Implementation" daily_learning/drafts/day${DAY}_code_analysis.md; then
    echo "⚠️  WARNING: Custom implementation classes are not clearly labeled!"
    echo "   Please ensure SpatialDiscretizer, TVDLimiter, etc. are marked as project-specific."
fi

# Check that OpenFOAM classes are referenced correctly
if grep -q "upwind.*:.*surfaceInterpolationScheme" daily_learning/drafts/day${DAY}_code_analysis.md; then
    # Check if it's the WRONG direct inheritance (should be via limitedSurfaceInterpolationScheme)
    if ! grep -q "limitedSurfaceInterpolationScheme" daily_learning/drafts/day${DAY}_code_analysis.md; then
        echo "⚠️  WARNING: upwind inheritance may be incorrect (missing limitedSurfaceInterpolationScheme)"
    fi
fi

echo "✅ Code analysis content verification complete"
```

---

### Step 5: Content Synthesis (Chunks based on Verified Research)

#### Chunk 1: Objectives & Theory
```bash
# Extract Objectives
python3 -c "import json; sk=json.load(open('$SKELETON')); print(json.dumps(sk['learning_objectives'], indent=2))" > /tmp/objs.json

# Include verification report to ensure accuracy
cat CONVENTIONS.md /tmp/objs.json daily_learning/drafts/day${DAY}_math_derivation.md daily_learning/drafts/day${DAY}_formula_verification.md | \
  llm -m deepseek-chat -s "Write Part 1 of Day ${DAY}:
1. Learning Objectives: Use the provided JSON objectives strictly.
2. Theory Section: Use the Math Derivation provided.
3. IMPORTANT: All formulas have been verified against source code. Use ONLY the verified formulas.
4. If any formula in the verification report was marked as incorrect, use the corrected version.
Style: Engineering English. Analogies first. LaTeX for math." > daily_learning/drafts/day${DAY}_part1.md
```

#### Chunk 2: Reference & Design
```bash
cat CONVENTIONS.md daily_learning/drafts/day${DAY}_verification_report.md daily_learning/drafts/day${DAY}_code_analysis.md | \
  llm -m deepseek-chat -s "Write Part 2 of Day ${DAY}:
3. OpenFOAM Reference: detailed analysis of source code.
   CRITICAL: Use the VERIFIED class hierarchy. Do NOT use incorrect inheritance.
4. Class Design: Mermaid diagrams and architecture.
   CLEARLY LABEL: OpenFOAM standard classes vs Project-Specific custom classes.
Use the provided Code Analysis notes." > daily_learning/drafts/day${DAY}_part2.md
```

#### Chunk 3: Implementation & Checks
```bash
# Extract Pitfalls & Checks
python3 -c "import json; sk=json.load(open('$SKELETON')); print(json.dumps({'pitfalls': sk['pitfalls'], 'concept_checks': sk['concept_checks']}, indent=2))" > /tmp/checks.json

cat CONVENTIONS.md /tmp/checks.json daily_learning/drafts/day${DAY}_code_analysis.md | \
  llm -m deepseek-chat -s "Write Part 3 of Day ${DAY}:
5. Implementation: Custom C++ implementation.
   IMPORTANT: Clearly state this is PROJECT-SPECIFIC CODE, not OpenFOAM standard.
6. Concept Checks: Use the 'concept_checks' JSON. Create Q&A with hidden solutions.
7. Pitfalls: Use the 'pitfalls' JSON.
Style: Hardcore Engineering." > daily_learning/drafts/day${DAY}_part3.md

# Merge
cat daily_learning/drafts/day${DAY}_part1.md \
    daily_learning/drafts/day${DAY}_part2.md \
    daily_learning/drafts/day${DAY}_part3.md > daily_learning/drafts/day${DAY}_draft_english.md

echo "✅ Content Synthesis (Verified) Complete"
```

---

### Step 6: QC + Translation (Agent-Only)

> ⚠️ **This step is performed by the Agent (Claude/Gemini) directly, NOT via scripts.**

Agent reads: `daily_learning/drafts/day${DAY}_draft_english.md`
Agent writes: `daily_learning/${PHASE}/${DAY}.md`

#### 6.1 Translation Rules (Engineering Thai)

The Agent MUST follow these rules when translating:

1. **Tone:** Professional, Instructional (เหมือนรุ่นพี่สอนรุ่นน้อง)
2. **Technical Terms:** Keep in English. **DO NOT transliterate.**
   - ✅ `การคำนวณ Flux`
   - ❌ `การคำนวณ ฟลักซ์`
3. **Headers:** Bilingual format `## English | ไทย`
4. **LaTeX & Code:** Keep **UNTOUCHED**
5. **Structure:** Preserve Markdown hierarchy

#### 6.2 Technical Accuracy Verification (NEW - Agent Manual Check)

Before finalizing, Agent MUST verify:

- [ ] **Class Hierarchy:** All inheritance relationships match verification report
- [ ] **Formulas:** All mathematical formulas match source code
- [ ] **Labeling:** OpenFOAM standard vs Project-Specific code is clearly distinguished
- [ ] **File References:** All mentioned files exist in `openfoam_temp/`

#### 6.3 QC Checklist

Before finalizing, Agent must verify:

- [ ] All headers are bilingual
- [ ] Technical terms remain in English
- [ ] LaTeX syntax is correct (no nested `$`)
- [ ] Mermaid diagrams render correctly
- [ ] Concept Checks have hidden solutions (`> [!example]- Solution`)

#### 6.4 Workflow Reference

For large files (1000+ lines), use the modular approach:
```
/qc-modular daily_learning/drafts/day${DAY}_draft_english.md
```

This will:
1. Split the file into sections
2. Translate each section
3. Apply QC fixes
4. Merge back into final destination

---

## Output Files

| File | Description |
|------|-------------|
| `day${DAY}_research_headers.md` | GLM Instance A output |
| `day${DAY}_research_impl.md` | GLM Instance B output |
| `day${DAY}_research_context.md` | GLM Instance C output |
| `day${DAY}_research_notes.md` | Merged research |
| `day${DAY}_verification_report.md` | **🔒 Class hierarchy verification** |
| `day${DAY}_formula_verification.md` | **🔒 Formula verification** |
| `day${DAY}_math_derivation.md` | DeepSeek R1 output |
| `day${DAY}_code_analysis.md` | DeepSeek V3 code output |
| `day${DAY}_draft_english.md` | DeepSeek V3 synthesis output |
| `${PHASE}/${DAY}.md` | **Final Thai content** |

---

## 🔒 Verification Scripts Required

The following scripts must be present in `.agent/scripts/`:

1. **`verify_class_hierarchy.py`** - Extracts actual class inheritance from headers and compares with claimed
2. **`verify_formulas.py`** - Extracts actual formulas from .C/.H files and compares with derived

These will be created separately.

---

## Quick Run

// turbo-all
```bash
# Full pipeline for Day 03
export DAY="03" TOPIC="Spatial Discretization Schemes" PHASE="Phase_01_Foundation_Theory"

# Step 1: Research (parallel)
grep -r "surfaceInterpolationScheme" --include="*.H" openfoam_src/ 2>/dev/null | head -200 | python3 .agent/scripts/ask_glm.py -s "Analyze OpenFOAM headers" > daily_learning/drafts/day${DAY}_research.md

# Step 1.5: VERIFY (don't skip!)
python3 .agent/scripts/verify_class_hierarchy.py \
    --actual-hierarchy /tmp/actual_hierarchy.txt \
    --claimed-analysis daily_learning/drafts/day${DAY}_research_headers.md \
    --output daily_learning/drafts/day${DAY}_verification_report.md

# Step 2-5: Sequential (with verification at each step)
cat daily_learning/drafts/day${DAY}_research.md | llm -m deepseek-reasoner -s "Derive math for ${TOPIC}" > daily_learning/drafts/day${DAY}_math.md

python3 .agent/scripts/verify_formulas.py \
    --actual-formulas /tmp/actual_formulas.txt \
    --claimed-formulas daily_learning/drafts/day${DAY}_math.md \
    --output daily_learning/drafts/day${DAY}_formula_verification.md

cat daily_learning/drafts/day${DAY}_*.md CONVENTIONS.md | llm -m deepseek-chat -s "Write comprehensive content" > daily_learning/drafts/day${DAY}_draft.md

echo "✅ Draft ready for Agent QC at: daily_learning/drafts/day${DAY}_draft.md"
```

---

**Last Updated:** 2026-01-24
**Changes:** Added Ground Truth Verification steps (1.5, 3.5, 4.5) to prevent hallucinations
