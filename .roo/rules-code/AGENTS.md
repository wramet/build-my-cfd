# Project Coding Rules (Non-Obvious Only)

## Content Generation Rules
- Always use `scripts/generate_day_v3.py` with DeepSeek API for content generation
- Content length varies by topic (not fixed at 2500 lines)
- Technical terms must remain in English in Thai translations (e.g., "discretize", "flux", "gradient")
- LaTeX equations must use `\mathbf{}` NOT `\vec{}` for vectors (QC will fail otherwise)
- Use `.agent/workflows/qc-modular.md` for quality control (other workflows are outdated)

## CFD Engine Development Rules
- The expansion term $\nabla \cdot \mathbf{U} = \dot{m} \left( \frac{1}{\rho_v} - \frac{1}{\rho_l} \right)$ MUST be implemented in `volScalarField::addExpansionSource()`
- Without the expansion term in pressure equation, solver will diverge immediately
- Reference `daily_learning/phase_1_context.md` as the "Bible" for Phase 1 concepts
- Follow `roadmap.md` for phase progression across all 6 phases
- All C++ code must follow OpenFOAM naming conventions and include unit tests

## File Structure Conventions
- Daily learning files: `daily_learning/Phase_XX/2026-01-XX.md`
- Draft files: `daily_learning/drafts/dayXX_deepseek_english.md`
- Skeleton files: `daily_learning/skeletons/dayXX_skeleton.json`
- MODULE directories contain refactored technical content, not raw drafts

## Quality Control Requirements
- Code blocks must have even number of ``` markers (QC checks this)
- Headers must use bilingual format: `## Section N: English Title (ชื่อภาษาไทย)`
- Use `.agent/workflows/qc-modular.md` for section-by-section processing
- Check for Chinese characters with `python3 scripts/find_chinese.py`

## Critical Dependencies
- DEEPSEEK_API_KEY environment variable required for content generation
- OpenFOAM development environment required for CFD engine code
- Boost.Test for unit testing C++ code
- CoolProp for refrigerant properties (Phase 4+)
