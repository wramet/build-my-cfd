---
name: Content Quality Checker
description: |
  Use this skill when: reviewing documentation quality, checking for pedagogical elements, validating OpenFOAM content structure, or running quality assurance on markdown files.
  
  This skill provides a checklist for ensuring documentation meets quality standards including Learning Objectives, Concept Checks, Code Examples, and proper structure.
---

# Content Quality Checker

This skill validates documentation quality for OpenFOAM educational content.

## Quality Checklist

Every content file should include these pedagogical elements:

### Required Elements

| Element | Description | Priority |
|---------|-------------|----------|
| **Learning Objectives** | Clear list of what reader will learn | Critical |
| **Why This Matters** | Real-world relevance, OpenFOAM context | Critical |
| **Code Examples** | Working OpenFOAM code with comments | Critical |
| **Concept Check** | 2-4 Q&A with hidden answers in Thai | High |
| **Key Takeaways** | Summary of main points | High |
| **Related Documents** | Links to related content | Medium |

### Optional Elements

| Element | When to Include |
|---------|-----------------|
| **Mermaid Diagrams** | For workflows, hierarchies, processes |
| **Comparison Tables** | When comparing approaches/methods |
| **Common Pitfalls** | For troubleshooting topics |
| **Quick Reference** | For parameter/command summaries |

## Validation Rules

### Language Requirements

1. **No Chinese characters** - Content must be in Thai or English only
2. **Thai Concept Checks** - Q&A hidden answers should be in Thai
3. **English technical terms** - OpenFOAM keywords, code, equations

### Structure Requirements

1. **No TOC/Checklists** - Avoid redundant table of contents
2. **Consistent headers** - Use proper markdown hierarchy
3. **Code blocks** - Use proper language tags (cpp, python, bash)

### Content Requirements

1. **OpenFOAM Context** - Connect concepts to OpenFOAM implementation
2. **File references** - Show relevant files (constant/, system/, 0/)
3. **Practical examples** - Real solver/case examples

## How to Use

### For Manual Review

Check each file against the checklist above.

### For Automated Review (refactor_batch.py)

The refactor_batch.py script uses this skill to:

1. **Plan Phase**: Generate refactor plan based on quality gaps
2. **Execute Phase**: Apply enhancements using skill guidelines
3. **Verify Phase**: Confirm elements are present

### Quality Scoring

| Score | Description |
|-------|-------------|
| ✅ Excellent | All critical + all high priority elements |
| ✅ Good | All critical elements, most high priority |
| ⚠️ Needs Work | Missing critical elements |
| ❌ Poor | Missing multiple critical elements |

## Integration with refactor_batch.py

When refactor_batch.py processes a folder:

1. Reads all .md files
2. Generates plan using content-quality-checker criteria
3. Executes refactoring to add missing elements
4. Creates .refactor_status.json tracking

**Key prompt triggers**:
- "Check content quality"
- "Validate documentation"
- "Add pedagogical elements"
- "Enhance content structure"
