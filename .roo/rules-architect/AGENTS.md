# Project Architecture Rules (Non-Obvious Only)

## System Architecture Overview
- **Dual-track project**: Content generation + CFD engine development
- **Content pipeline**: DeepSeek API → English draft → Thai translation → QC → Final
- **CFD engine**: OpenFOAM-based phase-change evaporator solver
- **6-phase structure**: Follows `roadmap.md` with clear milestones

## Critical Architectural Decisions
1. **Expansion Term Integration**: Must be in pressure equation, not as separate source
2. **VOF with Phase Change**: Interface tracking with mass transfer
3. **Bilingual Content**: Technical terms in English, explanations in Thai
4. **MODULE Structure**: Refactored content separate from daily learning
5. **Phase Progression**: Strict adherence to `roadmap.md` 6-phase structure

## Content Generation Architecture
- **Generator**: `scripts/generate_day_v3.py` with DeepSeek API
- **QC System**: `.agent/workflows/qc-modular.md` for section-by-section processing
- **Workflow Automation**: `.agent/workflows/` for repeatable processes
- **Batch Processing**: `scripts/batch_generate_phase1_remaining.sh`

## CFD Engine Architecture
- **Core Data Structures**: `volScalarField`, `volVectorField`, `fvMatrix`
- **Solver Algorithm**: PISO with expansion term correction
- **Phase Change Model**: Lee Model for mass transfer
- **Interface Tracking**: VOF method with compression term
- **Expansion Term**: Critical for solver stability (Day 11, 34, 61)

## Phase Architecture
- **Phase 1 (Foundation)**: Theory and governing equations
- **Phase 2 (Geometry/Mesh)**: Tube mesh generator
- **Phase 3 (Solver Core)**: Field classes, operators, SIMPLE, turbulence
- **Phase 4 (VOF+Phase Change)**: Two-phase flow with expansion term
- **Phase 5 (Pre/Post)**: Case setup and visualization
- **Phase 6 (Integration)**: Final validation

## Constraints and Trade-offs
- **Content length**: Varies by topic, not fixed at 2500 lines
- **Technical accuracy**: Must match OpenFOAM API exactly
- **Language balance**: Technical terms remain English for precision
- **Performance**: CFD solver must handle large density ratios (R410A: ~22:1)
- **QC workflow**: Use `.agent/workflows/qc-modular.md` (others outdated)
