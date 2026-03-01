---
name: create-module
description: Create and revise MODULE content with Source-First verification for C++ learning through OpenFOAM
---

# Module Creation Workflow

Create comprehensive MODULE content for C++ and Software Engineering learning through OpenFOAM case studies.

## Core Process

When creating or revising MODULE content, follow this workflow:

1. **Load Module Config** - Read existing MODULE structure
2. **Extract Ground Truth** - Use extract_facts.py from OpenFOAM source
3. **Verify Ground Truth** - Ensure extraction succeeded
4. **Generate/Revise Content** - Create C++ learning-focused content
5. **Verify Math** - DeepSeek R1 checks algorithm derivations
6. **Verify Code** - DeepSeek Chat V3 checks C++ syntax and patterns
7. **Apply Verification Gates** - All 6 gates must pass
8. **Generate Final Content** - Output verified content
9. **Save to Module** - Write to MODULE directory

## Model Assignment

| Stage | Primary Model | Purpose |
|-------|---------------|---------|
| Ground Truth | `extract_facts.py` | Extract C++ patterns from OpenFOAM source |
| Algorithm Analysis | DeepSeek R1 | Verify algorithm correctness and complexity |
| Code Implementation | DeepSeek Chat V3 | Verify C++ syntax, patterns, and best practices |
| Content Generation | GLM-4.7 | Generate draft content |
| Final Verification | DeepSeek R1 + V3 | Double-check all claims |

## Verification Gates

### Gate 1: File Structure
- MODULE has proper directory layout
- Source files exist and are readable
- Content organized by topics

### Gate 2: Ground Truth
- C++ patterns extracted from actual OpenFOAM source
- Class hierarchies verified
- File paths and line numbers included

### Gate 3: Mathematical Content
- Algorithm derivations complete
- Complexity analysis correct
- Big-O notation accurate

### Gate 4: Code Verification
- C++ syntax correct
- Modern C++ standards followed (C++11/14/17)
- OpenFOAM patterns used correctly

### Gate 5: Implementation Practice
- Mini-implementations provided
- Compilation instructions included
- Testing procedures explained

### Gate 6: Coherence
- Theory matches code examples
- Progressive overload maintained
- Learning objectives met

## Module Content Strategy

### Phase 1: C++ Through OpenFOAM's Eyes (Days 1-14)
Focus on fundamental C++ patterns in OpenFOAM:

**Day 01-03: Smart Pointers & Memory Management**
- autoPtr, tmp, refPtr
- RAII principles
- Memory safety patterns

**Day 04-07: Templates & Generic Programming**
- Template classes in OpenFOAM
- Expression templates
- Compile-time polymorphism

**Day 08-10: Object-Oriented Design**
- Virtual functions and polymorphism
- Abstract base classes
- RTTI and run-time selection

**Day 11-14: Advanced C++ Features**
- Function objects and lambdas
- STL integration
- Move semantics

### Phase 2: Data Structures & Memory (Days 15-28)
Focus on data structures used in OpenFOAM:

**Key Topics:**
- UList, List, PtrList implementations
- Field containers
- Mesh data structures
- Hash tables and dictionaries

### Phase 3: Software Architecture (Days 29-42)
Focus on design patterns and architecture:

**Key Topics:**
- Factory pattern (run-time selection)
- Strategy pattern (discretization schemes)
- Observer pattern (boundary conditions)
- Plugin architecture

### Phase 4: Performance Optimization (Days 43-56)
Focus on profiling and optimization:

**Key Topics:**
- Profiling tools and techniques
- Memory access patterns
- Cache optimization
- Parallel computing basics

### Phase 5: Focused Implementation (Days 57-84)
Comprehensive CFD component implementation:

**Key Topics:**
- Complete solver implementation
- Custom boundary conditions
- Discretization schemes
- Turbulence models

## Markers

- ⭐ = Verified from ground truth
- ⚠️ = Unverified (documentation source)
- ❌ = Incorrect/Don't
- 🔧 = Implementation focus

## Integration

This skill integrates with:

- `extract_facts.py` - Ground truth extraction
- `deepseek_content.py` - Model routing
- `verify_two_phase.py` - Two-phase physics verification
- `verify_expansion_term.py` - Expansion term verification
- `verify_properties.py` - CoolProp integration verification

## Troubleshooting

**Gate 8 Failed: Expansion term incorrect**
- Verify mathematical derivation with DeepSeek R1
- Check sign convention (ṁ positive for evaporation)
- Ensure density ratio terms are correct

**Gate 7 Failed: Two-phase physics error**
- Verify void fraction is bounded [0,1]
- Check density ratio handling
- Ensure surface tension is included

**Ground truth extraction failed**
- Check OpenFOAM source path is correct
- Verify two-phase models exist in source tree
- Run extraction script directly to debug

## See Also

- [Detailed 9-stage workflow](references/workflow.html)
- [Source-First methodology](../source-first/SKILL.md)
- [Verification gates](../../rules/verification-gates.md)
