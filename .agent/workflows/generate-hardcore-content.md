---
description: Multi-stage workflow for generating HARDCORE OpenFOAM daily content
---

# Generate HARDCORE Content (4-Stage Pipeline)

This workflow creates high-quality HARDCORE-level daily learning content using Aider with ctags in 4 incremental stages.

## Prerequisites
- `universal-ctags` installed (`brew install universal-ctags`)
- Aider configured with Z.AI (`use-aider-glm`)
- Git repo (for repo-map)

---

## Stage 1: Draft Content (Foundation)

**Goal:** Create initial structure with correct OpenFOAM references using ctags

**Prompt:**
```
Create daily_learning/YYYY-MM-DD.md

Topic: [TOPIC NAME]
Level: HARDCORE

Structure:
1. Theory (brief: equations + purpose)
2. OpenFOAM class hierarchy (reference actual source files from $FOAM_SRC)
3. Code walkthrough (e.g., createFields.H, UEqn.H)
4. Dictionary analysis (fvSchemes/fvSolution)
5. Hands-on tasks (3 tasks: utility + BC + debugging)
6. Concept checks (5 questions with answers)

Requirements:
- Thai explanations, English code comments
- Reference actual source code paths
- 300+ lines minimum
- Include line numbers for source references
```

**Command:**
```bash
// turbo
source ~/.zshrc && use-aider-glm && aider --model anthropic/claude-3-opus-20240229 --yes --map-tokens 4096 --message "Create daily_learning/2026-01-XX.md [INSERT STAGE 1 PROMPT HERE]"
```

**Expected Output:** 300-400 lines, basic structure complete

---

## Stage 2: Expand Details (Deep Dive)

**Goal:** Add implementation details, memory layouts, and source code snippets

**Prompt:**
```
Expand daily_learning/YYYY-MM-DD.md to HARDCORE level:

Add to each section:
1. IOobject analysis (readOption, writeOption, registry)
2. Memory layout diagrams (ASCII art for GeometricField, fvMatrix)
3. Template parameter explanations (Type, PatchField, GeoMesh)
4. Behind-the-scenes code (memory allocation, constructor calls)
5. Algorithm pseudocode (SIMPLE/PISO step-by-step)
6. Performance notes (memory usage, computational complexity)

Target: 500-700 lines
Requirements:
- Add ASCII diagrams
- Show actual C++ template code
- Explain every parameter
```

**Command:**
```bash
// turbo
source ~/.zshrc && use-aider-glm && aider --model anthropic/claude-3-opus-20240229 --yes --file daily_learning/2026-01-XX.md --map-tokens 4096 --message "[INSERT STAGE 2 PROMPT HERE]"
```

**Expected Output:** 500-700 lines with deep implementation details

---

## Stage 3: Add Visualizations (Clarity)

**Goal:** Enhance understanding with diagrams, examples, and annotations

**Prompt:**
```
Enhance daily_learning/YYYY-MM-DD.md with visualizations:

1. Add matrix structure diagrams (show diag/upper/lower for 2x2 mesh)
2. Add data flow diagrams (field creation → assembly → solve → BC update)
3. Add code annotations (inline comments explaining every line)
4. Add comparison tables (upwind vs linear vs limiters)
5. Add memory footprint examples (1M cells = X MB)
6. Add debugging command examples (GDB session walkthrough)
7. Add file structure trees (case directory layout)

Target: 700-1000 lines
Requirements:
- Use ASCII art for diagrams
- Annotate every code block
- Add practical examples
```

**Command:**
```bash
// turbo
source ~/.zshrc && use-aider-glm && aider --model anthropic/claude-3-opus-20240229 --yes --file daily_learning/2026-01-XX.md --map-tokens 4096 --message "[INSERT STAGE 3 PROMPT HERE]"
```

**Expected Output:** 700-1000 lines with rich visualizations

---

## Stage 4: Quality Check & Polish (Final)

**Goal:** Review, add study guides, references, and ensure completeness

**Prompt:**
```
Final polish for daily_learning/YYYY-MM-DD.md:

1. Add comprehensive summary section
2. Add 5-week study plan (weekly goals + practice tasks)
3. Add additional concept checks (bring total to 8-10 questions)
4. Add recommended reading list
5. Add quick reference appendix (common commands, env vars, file locations)
6. Add prerequisite checklist for next day
7. Fix any incomplete sections
8. Ensure all code compiles
9. Verify all source paths are correct

Target: 1000-1500 lines
Requirements:
- Complete all TODOs
- Add study resources
- Professional formatting
```

**Command:**
```bash
// turbo
source ~/.zshrc && use-aider-glm && aider --model anthropic/claude-3-opus-20240229 --yes --file daily_learning/2026-01-XX.md --map-tokens 4096 --message "[INSERT STAGE 4 PROMPT HERE]"
```

**Expected Output:** 1000-1500 lines, publication-ready

---

## Full Pipeline Execution

To run all 4 stages sequentially:

```bash
#!/bin/zsh
# File: generate_day.sh

DATE=$1  # e.g., 2026-01-02
TOPIC=$2 # e.g., "Finite Volume Method"

echo "🚀 Starting 4-stage content generation for Day: $DATE"
echo "📚 Topic: $TOPIC"

# Stage 1: Draft
echo "\n=== Stage 1: Draft Content ==="
source ~/.zshrc && use-aider-glm
aider --model anthropic/claude-3-opus-20240229 --yes --map-tokens 4096 \
  --message "Create daily_learning/$DATE.md. Topic: $TOPIC. [Stage 1 prompt from workflow]"

# Check if file created
if [ ! -f "daily_learning/$DATE.md" ]; then
  echo "❌ Stage 1 failed"
  exit 1
fi

echo "✅ Stage 1 complete ($(wc -l < daily_learning/$DATE.md) lines)"

# Stage 2: Expand
echo "\n=== Stage 2: Expand Details ==="
aider --model anthropic/claude-3-opus-20240229 --yes --file daily_learning/$DATE.md --map-tokens 4096 \
  --message "[Stage 2 prompt from workflow]"

echo "✅ Stage 2 complete ($(wc -l < daily_learning/$DATE.md) lines)"

# Stage 3: Visualize
echo "\n=== Stage 3: Add Visualizations ==="
aider --model anthropic/claude-3-opus-20240229 --yes --file daily_learning/$DATE.md --map-tokens 4096 \
  --message "[Stage 3 prompt from workflow]"

echo "✅ Stage 3 complete ($(wc -l < daily_learning/$DATE.md) lines)"

# Stage 4: Polish
echo "\n=== Stage 4: Quality Check ==="
aider --model anthropic/claude-3-opus-20240229 --yes --file daily_learning/$DATE.md --map-tokens 4096 \
  --message "[Stage 4 prompt from workflow]"

echo "✅ Stage 4 complete ($(wc -l < daily_learning/$DATE.md) lines)"
echo "\n🎉 Content generation complete!"
wc -l daily_learning/$DATE.md
```

**Usage:**
```bash
chmod +x generate_day.sh
./generate_day.sh 2026-01-02 "Finite Volume Method & Discretization"
```

---

## Benefits of Multi-Stage Approach

1. **Incremental Quality:** Each stage builds on previous foundation
2. **Early Detection:** Catch issues in early stages before investing more tokens
3. **Flexible Editing:** Can re-run specific stages if needed
4. **Cost Effective:** Smaller prompts = more focused responses
5. **Ctags Efficiency:** Repo-map cached between stages
6. **Better Context:** Each stage knows what was done before

---

## Troubleshooting

**If Stage X fails:**
```bash
# Re-run just that stage
aider --file daily_learning/YYYY-MM-DD.md --message "[Stage X prompt]"
```

**If content incomplete:**
```bash
# Add manual intervention after Stage 2
aider --file daily_learning/YYYY-MM-DD.md --message "Fix section X: [specific request]"
# Then continue with Stage 3
```

**If quality not HARDCORE enough:**
```bash
# Add extra "deep dive" stage between 2 and 3
aider --file daily_learning/YYYY-MM-DD.md --message "Add source code deep dive for [specific topic]"
```
