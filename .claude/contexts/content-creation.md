# Content Creation Mode

You are in **Content Creation Mode** for the CFD learning curriculum.

## Mode Priority

1. **Source-First:** Always verify from OpenFOAM source code
2. **Accuracy:** Correct formulas over completeness
3. **Verification:** Mark verified content with ⭐

## Active Agents

| Agent | Model | Backend | Purpose |
|-------|-------|---------|---------|
| **architect** | glm-4.7 | Z.ai | Planning & structuring |
| **engineer** | deepseek-chat | DeepSeek | Content generation |
| **verifier** | deepseek-reasoner | DeepSeek | Source verification |
| **researcher** | glm-4.7 | Z.ai | Documentation research |
| **translator** | glm-4.7 | Z.ai | English → Thai |
| **qc-agent** | glm-4.7 | Z.ai | Quality control |

## Quality Standards

### Mathematical Content
- All formulas: ⭐ + source file:line
- Complete derivations (not just final results)
- No nested LaTeX delimiters

### Code Examples
- All code blocks balanced with language tags
- File references include line numbers
- Inline comments for key lines

### Structure
- Headers: Bilingual (English/Thai)
- Minimum line counts met
- Mermaid diagrams for hierarchies

## Source-First Principle

🔒 **Ground Truth from source code > AI analysis > Internal training**

When in doubt:
1. Extract from source first
2. Verify against source
3. Mark with ⭐ if verified
4. Mark with ⚠️ if unverified

## Common Tasks

### Create Daily Content
```bash
/create-day 03
```

### Verify Content
```bash
/delegate verifier "Check formulas in Day 03"
```

### Quality Check
```bash
/qc-modular --file=daily_learning/Phase_01_Foundation_Theory/03.md
```

## Error Handling

| Error | Solution |
|-------|----------|
| Formula doesn't match source | Extract from source, verify, mark ⭐ |
| Code block unbalanced | Check for closing ``` |
| Nested LaTeX | Use $$ for display, $ for inline |
| Missing file reference | Run: grep -r "class" openfoam_temp/src |

## Output Standards

- Theory: ≥3000 lines
- OpenFOAM Reference: ≥2000 lines
- Implementation: ≥1500 lines
- Total: ≥7000 lines
