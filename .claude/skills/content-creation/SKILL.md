---
name: content-creation
description: Generate daily CFD learning content using Source-First methodology with integrated model routing for GLM-4.7 and DeepSeek APIs
---

# Daily Content Creation Workflow

Generate daily CFD learning content (English-only) using Source-First methodology with integrated model routing.

## Core Process

When creating daily CFD learning content, follow this workflow:

1. **Extract Ground Truth** - Use source code to extract verified facts
2. **Create Skeleton** - Generate JSON outline with verified constraints
3. **Generate Blueprint** - Apply progressive overload template
4. **Verify** - Validate with DeepSeek R1
5. **Expand Content** - Generate with DeepSeek Chat V3
6. **Final Verify** - Technical verification with DeepSeek R1

## Model Assignment

| Stage | Model | Purpose |
|-------|-------|---------|
| 1-2 | GLM-4.7 | Ground truth extraction, skeleton creation |
| 2.5 | Python Script | Generate structural blueprint (progressive overload) |
| 3 | DeepSeek R1 | Verify skeleton + blueprint against ground truth |
| 4 | DeepSeek Chat V3 | Expand to full English content |
| 5 | DeepSeek R1 | Final technical verification |
| 6 | Python Script | Syntax QC |

## Content Requirements

| Section | Minimum | Details |
|---------|---------|---------|
| Theory | ≥500 lines | Equations + explanations + derivations |
| Code Analysis | 3-5 snippets | Must include file paths and line numbers |
| Implementation | ≥300 lines C++ | Step-by-step breakdown |
| Exercises | 4-6 questions | With detailed solutions |

## Progressive Overload Templates

| Template | Focus | Best For |
|----------|--------|----------|
| **Engine-Builder** | Code-heavy | Matrix Assembly, Solver Core |
| **Scientist** | Physics-heavy | Phase Change, VOF, Turbulence |
| **Mathematician** | Theory-heavy | Discretization, Stability |
| **Integration Engineer** | Hybrid | Expansion Term, Tabulation |

## Critical Markdown Requirements

### LaTeX Math
- Use `$$equation$$` for display math (NOT `\[` `\]`)
- Use `$equation$` for inline math (NOT `\(` `\)`)
- Use `\mathbf{U}` for vectors (NOT `\bfU` or `\bf{U}`)

### Code Blocks
- Every code block MUST have language tag: ` ```cpp `, ` ```python `, ` ```mermaid `
- Code blocks MUST be balanced (even number of ` ``` `)
- C++ braces must be balanced

### Mermaid Diagrams
- Use ONLY standard spaces (U+0020), never non-breaking spaces (U+00A0)
- Wrap node text with special characters in quotes: `["text|()"]`
- Wrap edge labels with special characters in quotes: `-->|"label·φ"|`

## English-Only Policy

- ✅ All content in English
- ✅ No Thai translation required
- ✅ Headers in English only
- ✅ Technical terms in English

## See Also

- [Detailed workflow stages](references/workflow.md)
- [DeepSeek API integration](references/deepseek-api.md)
- [Source-First methodology](../source-first/SKILL.md)
- [CFD content standards](../../rules/cfd-standards.md)
