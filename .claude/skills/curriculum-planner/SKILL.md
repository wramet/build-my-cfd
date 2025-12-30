---
name: Curriculum Planner
description: |
  Use this skill when: designing new learning modules, planning content structure, creating module outlines, or setting learning objectives for educational content.
  
  This skill provides guidance for planning and structuring educational content for CFD/OpenFOAM learning materials.
---

# Curriculum Planner

วางแผนและออกแบบ curriculum สำหรับ educational content

## When to Use

- Creating a new MODULE
- Planning content for a new topic
- Restructuring existing content
- Defining learning objectives

## Curriculum Design Process

### Step 1: Define Learning Goals

Answer these questions:
1. **Who** is the target audience? (beginner/intermediate/advanced)
2. **What** should they know after completing this module?
3. **Why** is this knowledge important?
4. **How** will they apply this knowledge?

### Step 2: Topic Decomposition

Break down the subject into logical units:

```
MODULE_XX_TOPIC_NAME/
├── README.md                    → Module overview
├── CONTENT/
│   ├── 01_SUBTOPIC_A/
│   │   ├── 00_Overview.md      → Subtopic introduction
│   │   ├── 01_Concept_1.md     → First concept
│   │   ├── 02_Concept_2.md     → Second concept
│   │   └── 0N_Summary.md       → Subtopic summary
│   ├── 02_SUBTOPIC_B/
│   └── ...
└── images/                      → Figures, diagrams
```

### Step 3: File Objectives Template

For each file, define:

```yaml
File: 01_Concept_Name.md
Learning Objectives:
  - [Action verb] + [specific knowledge/skill]
  - [Action verb] + [specific knowledge/skill]
Prerequisites:
  - [Previous file or external knowledge]
Time Estimate: XX minutes
Key Concepts:
  - Concept 1
  - Concept 2
OpenFOAM Connection:
  - Relevant files/solvers/utilities
```

### Step 4: Sequencing

Order content by:
1. **Foundational** → Abstract concepts first
2. **Progressive** → Build on previous knowledge
3. **Practical** → Theory before application
4. **Connected** → Link related concepts

## File Content Guidelines

### Required Elements

Every content file MUST have:

| Element | Purpose |
|---------|---------|
| Learning Objectives | Set expectations |
| Why This Matters | Motivation |
| Core Content | Theory/concepts |
| OpenFOAM Context | Implementation |
| Code Examples | Practical application |
| Concept Check | Self-assessment |
| Key Takeaways | Summary |
| Related Documents | Navigation |

### Optional Elements

| Element | When to Include |
|---------|-----------------|
| Mermaid Diagrams | Workflows, hierarchies |
| Comparison Tables | Alternatives/options |
| Common Pitfalls | Complex topics |
| Exercises | Skill-building topics |

## Module Templates

### Template: Conceptual Module

```
XX_CONCEPT_NAME/
├── 00_Overview.md           → What, Why, How
├── 01_Fundamentals.md       → Basic theory
├── 02_Mathematical_Basis.md → Equations
├── 03_OpenFOAM_Impl.md      → Implementation
├── 04_Examples.md           → Worked examples
├── 05_Common_Pitfalls.md    → Troubleshooting
└── 06_Summary_Exercises.md  → Review + practice
```

### Template: Practical Module

```
XX_HOW_TO_TOPIC/
├── 00_Overview.md           → Goal and context
├── 01_Setup.md              → Prerequisites
├── 02_Step_by_Step.md       → Procedure
├── 03_Customization.md      → Extensions
├── 04_Troubleshooting.md    → Common issues
└── 05_Quick_Reference.md    → Cheat sheet
```

### Template: Reference Module

```
XX_REFERENCE_TOPIC/
├── 00_Overview.md           → Usage guide
├── 01_Category_A.md         → First category
├── 02_Category_B.md         → Second category
├── ...
└── 99_Index.md              → Quick lookup
```

## Quality Checklist

Before finalizing curriculum:

- [ ] All files have clear learning objectives
- [ ] Prerequisites are realistic and documented
- [ ] Time estimates are reasonable (15-60 min per file)
- [ ] OpenFOAM connections are explicit
- [ ] Code examples are complete and tested
- [ ] Concept checks have answers
- [ ] Cross-references are accurate
- [ ] No duplicate content across files

## Integration with Refactor Script

When planning content that will be processed by `refactor_batch.py`:

1. Create folder structure first
2. Add 00_Overview.md with objectives
3. Create initial files with placeholders
4. Run refactor script to enhance content
5. Review and iterate

## Example: Planning a New Subtopic

**Task:** Add content about "Adaptive Mesh Refinement (AMR)"

**Step 1: Goals**
- Audience: Intermediate users
- Goal: Set up and use dynamicRefineFvMesh
- Importance: Handle moving interfaces, save computation

**Step 2: Structure**
```
08_ADAPTIVE_MESH_REFINEMENT/
├── 00_Overview.md
├── 01_AMR_Concepts.md
├── 02_dynamicRefineFvMesh.md
├── 03_Refinement_Criteria.md
├── 04_Case_Setup.md
└── 05_Best_Practices.md
```

**Step 3: Objectives per file**
- 00: Explain when AMR is useful
- 01: Describe refinement/coarsening algorithms
- 02: Configure dynamicMeshDict
- 03: Set field-based refinement criteria
- 04: Complete case setup walkthrough
- 05: Optimization and troubleshooting
