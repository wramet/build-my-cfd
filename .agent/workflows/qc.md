---
description: Batch quality control workflow for checking daily lessons (Days 01-12+)
---

# /qc - Batch Quality Control

Run a rigorous quality control check on a range of daily lessons. This workflow combines automated syntax checking with intelligent content review.

## Usage

```
/qc [StartDay] [EndDay]
# Example: /qc 1 12
```

---

## Workflow Steps

### Step 0: Automated Sanitation (Run First!)

Before reading the content, run these commands to catch common syntax errors that cause rendering issues.

```bash
# Run the Iron Linter (Checks for LaTeX, Code Blocks, Truncation)
python3 scripts/validate_markdown.py --day [StartDay] [EndDay]
```

**CRITICAL:** If this script fails, **STOP**. Fix the syntax errors first. Do not proceed to semantic audit until the file is structurally valid.

**If any critical syntax issues are found (odd code blocks, bad latex), FIX THEM FIRST before detailed reading.**

### Step 1: Load Standards

Read the master checklist to establish the standard:
- **Source**: `quality_control_checklist.md`
- **Global Context**: Read `daily_learning/phase_1_context.md` to check against the "Big Picture" (Redundancy/Consistency).
- **Key Focus**:
    - **Physics Accuracy**: Equations must be dimensionally consistent.
    - **Obsidian Rendering**: No backticks on math, correct vector notation (`\mathbf`).
    - **Structure**: Proper headers, Wiki-links, and Mermaid diagrams.

### Step 2: Technical Audit & Standardization (DeepSeek Output is Thai)

Since DeepSeek V3 now generates content directly in Thai, this step focuses on **Auditing** and **Polishing**, not translation.

For each day from Start to End (Process **ONE FILE AT A TIME**):
> **WARNING:** Do NOT batch multiple files in the AI prompt. The Context Window will overflow, and reasoning will degrade. Audit one day, finish it, then move to the next.

1.  **Read File**: Read `daily_learning/YYYY-MM-DD.md` (Thai content from DeepSeek).
2.  **Structural Validation**:
    - **Truncation**: Does the file end abruptly mid-sentence or mid-code?
    - **Code Blocks**: Do all blocks have language headers (`cpp`, `cmake`)?
    - **Formatting**: Are headers hierarchical and correct?
3.  **Technical Audit (The "Something Else")**:
    - **Physics Logic**: Verify that DeepSeek didn't hallucinate equations or violate conservation laws.
    - **OpenFOAM Reality**: Check that classes mentioned actually exist in strict OpenFOAM (e.g., `volScalarField` vs hallucinated names).
    - **Engineering Thai Tone**: Check if the Thai is "Natural Engineering" style. If DeepSeek is too formal/academic, adjust to be more practical.
    - **CRITICAL**: Do not summarize. Verify **line-by-line** to ensure no detail is skipped.
4.  **Fix Issues**: Apply edits directly to the file using `replace_file_content`.
5.  **Log Critical Errors**: If a major logic flaw is discovered (e.g., wrong physics), log it in `qc_issues_log.md`.

### Step 3: Final Verification

- Confirm all files in the range are structurally valid.
- Report: "✅ QC Complete for Days X to Y."
- List any files requiring manual attention/regenerating.

---

## Notes

- **Goal**: Perfect rendering (Obsidian) and technical accuracy (OpenFOAM).
- **Automation First**: Always use `Step 0` commands to save time on visual checks.
- **Coverage**: This workflow is designed to cover Phase 1 (Fundamentals) and Phase 2 (Geometry).
