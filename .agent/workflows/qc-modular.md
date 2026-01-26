---
description: Modular QC and Translation workflow for large daily_learning files
---

# /qc-modular - Section-by-Section QC & Translation

This workflow ensures consistent, thorough quality control for large markdown files (1000+ lines) by splitting them into manageable sections and processing each independently.

## Prerequisites
- Target file must be a daily_learning markdown file (e.g., `2026-01-XX.md`)
- File must use `##` headers to delineate sections

## Step 1: Inventory Sections
// turbo
```bash
grep -n "^## " "$TARGET_FILE" | head -20
```
This shows all top-level section headers with line numbers. Note the approximate line counts per section.

## Step 2: Split File into Temp Sections
Create temporary section files in `daily_learning/temp_qc/`:
```bash
mkdir -p daily_learning/temp_qc
csplit -f "daily_learning/temp_qc/section_" -b "%02d.md" "$TARGET_FILE" '/^## /' '{*}'
```

## Step 3: Iterate QC on Each Section
For each `section_XX.md` file:

### 3.1 View Section Content
```
view_file section_XX.md
```

### 3.2 Run Syntax Checks
Check for common errors using grep:
```bash
# Nested LaTeX ($ inside $$ or vice versa)
grep -n '\$\$.*\$[^$]' section_XX.md

# Unclosed code blocks (odd count of ```)
grep -c '```' section_XX.md

# Unescaped underscores in prose (potential italics)
grep -n '[^$`]_[a-zA-Z]' section_XX.md

# Mermaid syntax issues (< > without quotes)
grep -n 'classDiagram' -A 20 section_XX.md | grep '<'
```

### 3.3 Apply Fixes
Use `replace_file_content` or `multi_replace_file_content` to fix identified issues.

### 3.4 Translate to Engineering Thai (if needed)
- Preserve all code blocks unchanged
- Preserve LaTeX expressions unchanged
- Use bilingual headers: `## Section Title (หัวข้อภาษาไทย)`
- Keep technical terms in English

## Step 4: Merge Sections Back
// turbo
```bash
cat daily_learning/temp_qc/section_*.md > "$TARGET_FILE"
rm -r daily_learning/temp_qc
```

## Step 5: Final Validation Pass
Run comprehensive validation across the merged file:
```bash
# Check code block balance
awk '/```/{count++} END{print "Code blocks:", count, (count%2==0 ? "OK" : "UNBALANCED")}' "$TARGET_FILE"

# Check for remaining nested LaTeX
grep -c '\$\$.*\$[^$]' "$TARGET_FILE"

# Check for truncated content (lines ending with incomplete bold/italics)
grep -n '\*\*$' "$TARGET_FILE"
grep -n '^\d\. \*\*$' "$TARGET_FILE"
```

## Step 6: Manual Review Prompt
After all automated checks pass, notify user for final Obsidian rendering review.

---

## Usage Example
```
User: /qc-modular daily_learning/Phase_01_Foundation_Theory/03.md
```

## Notes
- For files with 8+ sections, consider batching 2-3 sections per iteration
- Always verify Mermaid diagrams render correctly in Obsidian after merge
- If truncation is detected, regenerate that section from source skeleton
