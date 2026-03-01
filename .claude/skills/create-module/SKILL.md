---
name: create-module
description: Create and revise MODULE content with Source-First verification for custom CFD engine implementation
---

# Module Creation Workflow

Transform MODULE content from general OpenFOAM usage to custom CFD engine implementation for R410A refrigerant evaporator simulation.

## Core Process

When creating or revising MODULE content, follow this workflow:

1. **Load Module Config** - Read existing MODULE structure
2. **Extract Ground Truth** - Use extract_facts.py from OpenFOAM source
3. **Verify Ground Truth** - Ensure extraction succeeded
4. **Generate/Revise Content** - Create implementation-focused content
5. **Verify Math** - DeepSeek R1 checks derivations
6. **Verify Code** - DeepSeek Chat V3 checks C++ syntax
7. **Apply Verification Gates** - All 9 gates must pass
8. **Generate Final Content** - Output verified content
9. **Save to Module** - Write to MODULE directory

## Model Assignment

| Stage | Primary Model | Purpose |
|-------|---------------|---------|
| Ground Truth | `extract_facts.py` | Extract from OpenFOAM source |
| Math Derivations | DeepSeek R1 | Verify expansion term, TVD conditions |
| Code Implementation | DeepSeek Chat V3 | Verify C++ syntax and practices |
| Content Generation | GLM-4.7 | Generate draft content |
| Final Verification | DeepSeek R1 + V3 | Double-check all claims |

## Verification Gates

### Gates 1-6: Standard (from source-first skill)
- File structure, ground truth, equations, code, implementation, coherence

### Gate 7: Two-Phase Physics
- Void fraction bounded [0,1]
- Density ratio handled correctly (ρ_v/ρ_l ≈ 1/30 for R410A)
- Surface tension included
- Interface compression present

### Gate 8: Expansion Term
- Derivation mathematically sound
- Sign convention correct (ṁ positive for evaporation)
- Implemented in pressure equation
- Density ratio terms correct

### Gate 9: Property Integration
- CoolProp API correct
- R410A properties accurate
- Table interpolation valid
- Temperature ranges appropriate

## Module Revision Strategy

### Phase 1: Create New Days (Priority)

**Day 11: Expansion Term** (CRITICAL)
- Mathematical derivation
- Implementation in pressure equation
- Lee evaporation model

**Day 10: Two-Phase Flow**
- VOF method theory
- Void fraction and quality
- Large density ratio handling

**Day 12: Refrigerant Properties**
- CoolProp integration
- R410A property tables
- Temperature-dependent properties

### Phase 2: Revise Existing Days

| Day | Current Focus | New Focus | Key Changes |
|-----|--------------|-----------|-------------|
| 01 | General N-S | R410A evaporator N-S | Add source terms |
| 02 | Cartesian FVM | Cylindrical FVM | Radial/axial discretization |
| 03 | Generic schemes | Tube-specific schemes | Near-wall treatment |
| 04 | Time stepping | VOF-stable time stepping | CFL for two-phase |
| 05 | General mesh | Cylindrical O-grid | Tube mesh generation |
| 06 | Generic BCs | Evaporator BCs | Heat flux, saturation |
| 07 | Sparse matrices | LDU for cylindrical | Matrix optimization |
| 08 | Iterative solvers | Two-phase solvers | Convergence criteria |
| 09 | SIMPLE/PISO | PISO with expansion | Modified pressure eq |

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
