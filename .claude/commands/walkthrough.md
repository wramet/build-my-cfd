---
description: Interactive walkthrough of daily_learning content with Source-First verification
---

# /walkthrough

Use this command to tutor through `daily_learning/` content step-by-step with **verified facts**.

> **🔒 Source-First Principle:** Ground Truth from source code > AI analysis. Verify at each stage.

## Usage

```
/walkthrough <path-to-file>
```

Examples:
- `/walkthrough daily_learning/Phase_01_Foundation_Theory/01.md`
- `/walkthrough 05.md`
- `/walkthrough 02.md --section="Section 2"` (start from specific section)

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `<file>` | Yes | Path to daily_learning markdown file |
| `--section` | No | Start from specific section |

## Output

Walkthrough files are stored in `daily_learning/walkthroughs/` with naming: `day_XX_walkthrough.md`

## Workflow Steps

### Step 0: Extract Ground Truth (Before Starting)

```bash
# Identify the topic from the daily_learning file
export DAY="XX"  # From filename
export TOPIC="[topic_from_content]"  # e.g., "surfaceInterpolation"

# Extract ground truth
python3 .claude/scripts/extract_facts.py \
    --mode hierarchy \
    --path "openfoam_temp/src/finiteVolume" \
    --output /tmp/walkthrough_gt_hierarchy.txt

python3 .claude/scripts/extract_facts.py \
    --mode formulas \
    --path "openfoam_temp/src/finiteVolume" \
    --output /tmp/walkthrough_gt_formulas.txt

# Structure into JSON
python3 .claude/scripts/extract_facts.py \
    --mode structure \
    --input /tmp/walkthrough_gt_hierarchy.txt \
    --output /tmp/walkthrough_verified_facts.json
```

**Why?** This ensures ALL subsequent AI analysis is constrained by verified facts.

### Step 1: Initialize & Scan

1. Check if the source file exists
2. Read file structure (headers) to build Table of Contents
3. Check if `daily_learning/walkthroughs/day_XX_walkthrough.md` exists:
   - If yes: Read and append
   - If no: Create with frontmatter

### Step 2: Show Overview

Display message:
> "📂 สร้างไฟล์ `daily_learning/walkthroughs/day_XX_walkthrough.md` แล้ว พร้อมเริ่มที่ Section X"
>
> "🔒 Ground Truth extracted from: [source paths]"

### Phase A: Dual-Agent Recon + Verify

**Execute in parallel:**

1. **DeepSeek (Theorist):** Explains math/physics from source text
2. **GLM-4.7 (Scout):** Searches for Class Hierarchy & Namespaces using native Web Search

**Then verify GLM output:**
```bash
python3 .claude/scripts/verify_glm_output.py \
    --glm-output glm_out.md \
    --ground-truth /tmp/walkthrough_verified_facts.json \
    --output /tmp/glm_verification.md
```

**🔒 Verification Gate:**
- If GLM output fails verification → Use ground truth facts instead
- Only show verified content to user

### Phase B: Orchestrator Synthesis + Verify

**Role:** You are the **Orchestrator**. Synthesize inputs from:
1. **deepseek_out.md:** Math/Theory/Logic
2. **glm_out.md (or ground truth):** Real-world Code Structure
3. **Source Material:** Code examples from `daily_learning` file
4. **Ground Truth (from Step 0):** Verified facts ⭐

**🔒 Before writing, verify:**
- Class hierarchy matches ground truth
- Mathematical formulas are correct
- No unverified technical claims

**Write/append to walkthrough file:**

```markdown
## 🎯 [Section Number]: [หัวข้อปัจจุบัน]

**📍 ตำแหน่ง:** Day XX > Section Y > [Current Header]

### 📝 คำอธิบาย (Sythesized from DeepSeek + GLM-4.7 + Source + Ground Truth)

[Explain using "Engineering Thai" style]

### 🔬 Verified Facts (Source-First) ⭐
> **Class Hierarchy:** [Verified from actual source code]
> ```
> [Verified Mermaid diagram]
> ```
>
> **Formulas:** [If applicable, verified formulas]
> `$formula$`

### 💡 Key Insight

> [The most important takeaway]

### 🔗 เชื่อมโยง

[Link to previous concepts if applicable]

---
```

## Teaching Style Guidelines

| Rule | Description |
|------|-------------|
| **🔒 Source of Truth** | **Ground Truth > AI output > Internal training** |
| **Language** | "Engineering Thai" (Technical terms in English, explanation in Thai) |
| **LaTeX** | Use for all math: `$\nabla \cdot U$` |
| **Code** | Use backticks: `volScalarField`, `fvm::ddt()` |
| **Verification** | Mark verified facts with ⭐ emoji. Label unverified content clearly. |

## Notes

- **Step 0 (Extract Ground Truth) is mandatory**
- **Verification is mandatory** - Never use unverified AI output
- **Append mode:** After the first section, new sections append to the same file
- **Source-First Principle:** When conflict between AI output and ground truth → Use ground truth

## Example Session

```
User: /walkthrough 02.md --section="Section 2"

AI Actions:
1. Extracts ground truth from OpenFOAM source
2. Reads 02.md → Identifies Section 2 headers
3. Creates daily_learning/walkthroughs/day_02_walkthrough.md
4. Runs DeepSeek analysis of Section 2.1
5. Runs GLM-4.7 Web Search for code structure
6. Verifies GLM output against ground truth
7. Writes Section 2.1 to walkthrough file
8. Notifies: "✅ เขียน Section 2.1 แล้ว พร้อมไป 2.2 ไหมครับ?"
9. User says "ต่อ"
10. Appends Section 2.2 to same file
11. Repeat until user says "Done"
```

---

**See also:** `/create-day`, `/qc-modular`
