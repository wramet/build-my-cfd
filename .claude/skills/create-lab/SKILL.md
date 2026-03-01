---
name: create-lab
description: Generate hands-on lab exercises for CFD + C++ learning with spaced repetition
---

# Lab Creation Workflow

Generate hands-on coding exercises for spaced repetition learning with dual-track coverage:
- **CFD Track** - Implement CFD concepts using OpenFOAM
- **C++ Track** - Learn modern C++ using OpenFOAM as teaching examples

## Core Process

When creating lab exercises, follow this 5-stage workflow:

1. **Auto-Detect Lab Type** - Analyze day's content to determine CFD vs C++ focus
2. **Extract Ground Truth** - Use GLM-4.7 to extract from source code
3. **Generate Lab Skeleton** - Create structure with verified facts
4. **Verify Skeleton** - DeepSeek R1 validates technical accuracy
5. **Generate Full Lab** - DeepSeek Chat V3 expands to complete exercise
6. **Syntax QC** - Python script validates output format

## Lab Type Detection

**Auto-detection factors:**
- **CFD indicators:** Equations, discretization schemes, OpenFOAM-specific terms
- **C++ indicators:** Classes, templates, inheritance, operator overloading
- **Content balance:** Mathematical content vs code content
- **New concepts:** First-time introduction of C++ features

**Detection output example:**
```
Primary Type:   CFD
Confidence:     69%
Scores:
  CFD:          84%
  C++:          15%
CFD Topic:      Governing Equations
C++ Concept:   inheritance → cpp_04_inheritance
```

**When both types are recommended:**
If content balances CFD theory and C++ concepts, create both labs for comprehensive coverage.

## Model Assignment

| Stage | Model | Purpose |
|-------|-------|---------|
| Auto-Detection | Python script | Content analysis |
| Ground Truth | GLM-4.7 | Extract from source |
| Skeleton | GLM-4.7 | Structure with verified facts |
| Verify | DeepSeek R1 | Validate technical accuracy |
| Generate | DeepSeek Chat V3 | Expand to complete exercise |
| QC | Python script | Validate syntax |

## Lab Types

| Type | Focus | Example Topics |
|------|--------|----------------|
| **CFD** | Implement CFD concepts | Governing equations, discretization, boundary conditions |
| **C++** | Learn modern C++ | Classes, templates, smart pointers, move semantics |
| **Mixed** | Both tracks balanced | FVM operator implementation |

## Output

Labs are saved as:
```
labs/XX_lab.md
```

Format includes:
- Objective and prerequisites
- Step-by-step instructions
- Code snippets with file references
- Expected outputs
- Extension exercises

## Integration

- `detect_lab_type.py` - Content analysis for type detection
- `extract_facts.py` - Ground truth extraction
- `deepseek_content.py` - Model routing
- Spaced repetition system for review scheduling

## See Also

- [Implementation methodology](references/implementation.md)
- [Source-First methodology](../source-first/SKILL.md)
- [CFD content standards](../../rules/cfd-standards.md)
