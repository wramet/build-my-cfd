---
description: Quality Control + Thai Localization workflow
---

# /qc - Quality Control + Localization

## Overview

```
English Draft → Syntax QC → Thai Localization → 4D Evaluation → Final
```

---

## Usage

```bash
/qc [Day]
# Example: /qc 2
```

---

## Phase 1: Syntax Check

### Step 1.1: Code Block Validation
```bash
# Must be even number
count=$(grep -c '^```' drafts/day${N}_en.md)
echo "Code blocks:1$count"
[[1$((count % 2)) -eq 0 ]] && echo "✅ OK" || echo "❌ UNCLOSED"
```

### Step 1.2: LaTeX Validation
```bash
# No \vec{}, use \mathbf{}
grep -n '\\vec{' drafts/day${N}_en.md && echo "❌ Fix: use \\mathbf"

# Check1$$ pairs
grep -c '^\$\$' drafts/day${N}_en.md  # Should be even
```

### Step 1.3: Line Count
```bash
lines=$(wc -l < drafts/day${N}_en.md)
echo "Lines:1$lines (target: ≥2500)"
```

---

## Phase 2: Thai Localization

### Thai Engineering Editor Persona

```markdown
ROLE: Thai Engineering Editor (บรรณาธิการวิศวกรรม)

RULE 1: Keep Technical Terms in English (ทับศัพท์)
✅ CORRECT:
- "เราจะ discretize สมการ"
- "flux ผ่าน face นี้"
- "mesh มี non-orthogonality สูง"

❌ WRONG:
- "เราจะทำให้ไม่ต่อเนื่องซึ่งสมการ"
- "การไหลผ่านพื้นผิวนี้"

Common terms to keep in English:
discretize, flux, gradient, divergence, mesh, cell, face, 
scheme, solver, matrix, vector, field, boundary, patch,
convection, diffusion, advection, interpolation

RULE 2: Formal Academic Thai Tone
✅ "พิจารณาสมการ Navier-Stokes"
❌ "มาดูกันว่าสมการนี้ทำงานยังไง"

RULE 3: Preserve Exactly (Do NOT modify)
- All LaTeX:1$\nabla \cdot \mathbf{U}$
- All code blocks: ```cpp ... ```
- All Mermaid diagrams
- File names and paths
- Variable names in equations

RULE 4: Bilingual Headers
Format: ## Section N: English Title (ชื่อภาษาไทย)
Example: ## Section 1: Theory (ทฤษฎี)
```

### Localization Process

```bash
# Section by section translation
for section in s1 s2 s3 s4 s5; do
  # Use Gemini/Claude as Thai Editor
  cat drafts/day${N}_${section}.md | \
    # Agent applies Thai Engineering Editor rules
    > drafts/day${N}_${section}_th.md
done

# Merge translated sections
cat drafts/day${N}_s*_th.md > drafts/day${N}_th.md
```

---

## Phase 3: 4D Evaluation

### Dimension 1: Technical Integrity (25%)
- [ ] No hallucinated class/function names
- [ ] Math-to-code consistency
- [ ] Correct OpenFOAM API usage
- **Critical Days**: Expansion term correct?

### Dimension 2: Pedagogical Quality (25%)
- [ ] Logical flow (Theory → Code → Test)
- [ ] All sections complete
- [ ] ≥2500 lines
- [ ] No truncation

### Dimension 3: Linguistic Tone (25%)
- [ ] Technical terms in English
- [ ] Academic Thai (not colloquial)
- [ ] No machine translation artifacts

### Dimension 4: Formatting (25%)
- [ ] Code blocks closed (even count)
- [ ] LaTeX renders correctly
- [ ] Mermaid diagrams valid
- [ ] Headers properly formatted

### Scoring
```
Score = (D1 + D2 + D3 + D4) / 4

≥80%: ✅ Pass - Move to final
60-79%: ⚠️ Revise specific sections
<60%: ❌ Regenerate
```

---

## Phase 4: Final Output

```bash
# Copy to final location
cp drafts/day${N}_th.md \
   daily_learning/Phase_01_Foundation_Theory/2026-01-${DD}.md

# Cleanup drafts
rm -f drafts/day${N}_s*.md
```

---

## Quick Reference: Common Fixes

| Issue | Check | Fix |
|-------|-------|-----|
| Unclosed code block | `grep -c '^```'` odd | Find and close |
| Wrong vector notation | `grep '\\vec'` | Replace with `\mathbf` |
| Google Translate Thai | Manual review | Rewrite with tech terms |
| Truncated content | `wc -l` < 2500 | Regenerate section |
| Hallucinated class | Check OpenFOAM source | Correct name |
