# Project Documentation Rules (Non-Obvious Only)

## Key Documentation Locations
- **Phase 1 Bible**: `daily_learning/phase_1_context.md` - master reference for all Phase 1 concepts
- **Roadmap**: `roadmap.md` - complete 90-day plan with 6 phases and milestones
- **Daily Learning**: `daily_learning/Phase_XX/2026-01-XX.md` - final Thai versions
- **MODULE directories**: Refactored technical content (e.g., `MODULE_03_SINGLE_PHASE_FLOW/`)
- **Workflows**: `.agent/workflows/qc-modular.md` - current QC workflow (others outdated)

## Content Organization
- **Dual-language structure**: English technical terms preserved in Thai content
- **Hero Concept**: Expansion term $\nabla \cdot \mathbf{U} = \dot{m} \left( \frac{1}{\rho_v} - \frac{1}{\rho_l} \right)$ is central to project
- **Phase progression**: Follows 6-phase structure from `roadmap.md`
- **Content length**: Varies by topic, not fixed at 2500 lines

## Learning Path Dependencies
- **Phase 1 (Days 01-12)**: Foundation theory for all phases
- **Phase 2 (Days 13-19)**: Geometry and mesh generation
- **Phase 3 (Days 20-49)**: Solver core with turbulence
- **Phase 4 (Days 50-77)**: VOF + Phase change (critical expansion term)
- **Phase 5 (Days 78-86)**: Pre/post processing
- **Phase 6 (Days 87-90)**: Integration and validation

## Critical Concept References
- **Expansion Term**: Volume change during phase change, must be in pressure equation
- **Appears in**: Day 11 (Theory), Day 34 (Pressure with source), Day 61 (Implementation)
- **VOF Method**: Volume of Fluid for interface tracking
- **Lee Model**: Phase change model using temperature difference
- **PISO Algorithm**: Pressure-Implicit with Splitting of Operators

## Non-Obvious Relationships
- **Content generation ≠ CFD development**: Separate but related workflows
- **MODULE directories** contain deep-dive content, not daily lessons
- **`.agent/workflows/qc-modular.md`** defines the current QC workflow
- **Skeleton files** (JSON) control structure of generated content
- **Phase progression** must follow `roadmap.md` structure
