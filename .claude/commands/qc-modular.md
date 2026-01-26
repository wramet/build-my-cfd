---
description: Section-by-section QC and Translation workflow for large daily_learning files
---

# /qc-modular

Modular Quality Control and Translation workflow for large markdown files (1000+ lines). Splits files into manageable sections and processes each independently.

## Usage

```
/qc-modular --file=daily_learning/drafts/day03_draft_english.md
```

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--file` | Yes | Path to target markdown file |
| `--sections-dir` | No | Custom temp directory (default: `daily_learning/temp_qc/`) |

## Prerequisites

- Target file must be a daily_learning markdown file
- File must use `##` headers to delineate sections

## Workflow Steps

### Step 1: Inventory Sections

```bash
grep -n "^## " "$TARGET_FILE" | head -20
```

This shows all top-level section headers with line numbers.

### Step 2: Split File into Temp Sections

Create temporary section files in `daily_learning/temp_qc/`:

```bash
mkdir -p daily_learning/temp_qc
csplit -f "daily_learning/temp_qc/section_" -b "%02d.md" "$TARGET_FILE" '/^## /' '{*}'
```

### Step 3: Iterate QC on Each Section

For each `section_XX.md` file:

#### 3.1 View Section Content

```
Read section_XX.md
```

#### 3.2 Run Syntax Checks

Check for common errors:

```bash
# Nested LaTeX ($ inside $$ or vice versa)
grep -n '\$\$.*\$[^$]' section_XX.md

# Unclosed code blocks (odd count of ```)
grep -c '```' section_XX.md

# Unescaped underscores in prose
grep -n '[^$`]_[a-zA-Z]' section_XX.md

# Mermaid syntax issues
grep -n 'classDiagram' -A 20 section_XX.md | grep '<'
```

#### 3.3 Apply Fixes

Use Edit or Write tool to fix identified issues.

#### 3.4 Translate to Engineering Thai (if needed)

**Guidelines:**
- Preserve all code blocks unchanged
- Preserve LaTeX expressions unchanged
- Use bilingual headers: `## Section Title (หัวข้อภาษาไทย)`
- Keep technical terms in English

**Common technical terms to keep in English:**
- Finite Volume, Mesh, Flux, Gradient, Divergence
- Owner-Neighbor, Face, Cell, Boundary Condition
- Gauss, Upwind, Linear, Limited, TVD

### Step 4: Merge Sections Back

```bash
cat daily_learning/temp_qc/section_*.md > "$TARGET_FILE"
rm -r daily_learning/temp_qc
```

### Step 5: Final Validation Pass

Run comprehensive validation:

```bash
# Check code block balance
awk '/```/{count++} END{print "Code blocks:", count, (count%2==0 ? "OK" : "UNBALANCED")}' "$TARGET_FILE"

# Check for nested LaTeX
grep -c '\$\$.*\$[^$]' "$TARGET_FILE"

# Check for truncated content
grep -n '\*\*$' "$TARGET_FILE"
grep -n '^\d\. \*\*$' "$TARGET_FILE"
```

## QC Checklist

Use `qc-agent` to verify:

- [ ] Frontmatter is correct
- [ ] Headers are bilingual format
- [ ] TOC uses Wiki-links
- [ ] LaTeX syntax is valid
- [ ] Mermaid diagrams render correctly
- [ ] Code blocks are balanced
- [ ] No truncated content
- [ ] Technical accuracy verified (use ground truth)

## Output Files

| File | Description |
|------|-------------|
| `daily_learning/temp_qc/section_XX.md` | Individual section files |
| `daily_learning/Phase_XX/.../YYYY-MM-DD.md` | Final Thai translated file |

## Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| Nested LaTeX (`$$...$...$$`) | Use single `$` for inline, `$$` for block |
| Unclosed code block | Add missing ` ``` ` |
| Underscore italics | Escape with `\_` or use code formatting |
| Truncated bold text | Complete the bold section |

## Example Session

```
User: /qc-modular --file=daily_learning/drafts/day03_draft_english.md

AI Actions:
1. Inventories sections → Found 8 sections
2. Splits file into section_00.md to section_07.md
3. For each section:
   - Reads section
   - Runs syntax checks
   - Applies fixes
   - Translates to Engineering Thai
4. Merges sections back
5. Runs final validation
6. Reports: "✅ QC complete for day03_draft_english.md"
```

## Next Steps

After QC:
- Translation complete → Ready for final review
- If issues found → Run `/qc-modular` again after fixes

---

**See also:** `/create-day`, `/walkthrough`
