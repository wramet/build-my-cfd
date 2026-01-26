# Project Debug Rules (Non-Obvious Only)

## Content Generation Debugging
- Check for unclosed code blocks with `grep -c '^```'` - must be even number
- LaTeX validation: search for `\vec{}` (wrong) vs `\mathbf{}` (correct)
- Use `.agent/workflows/qc-modular.md` for section-by-section debugging
- Chinese character detection: use `python3 scripts/find_chinese.py`

## CFD Engine Debugging
- **Critical**: Missing expansion term causes immediate solver divergence
- Check `volScalarField::addExpansionSource()` implementation
- Verify mass/energy conservation in integration tests
- Monitor Courant number (Co) - should stay below 0.5 for stability
- Expansion term appears in: Day 11 (Theory), Day 34 (Pressure with source), Day 61 (Implementation)

## Common Failure Modes
1. **QC failures**: Usually from unclosed code blocks or wrong LaTeX notation
2. **API failures**: DEEPSEEK_API_KEY not set or expired
3. **Content truncation**: Use modular QC workflow for large files
4. **Solver divergence**: Missing expansion term or incorrect boundary conditions

## Debug Workflows
- Use `.agent/workflows/qc-modular.md` for quality control process (others outdated)
- Check `batch_en_log.txt` for batch generation errors
- Run `python3 check_qc.py` for common markdown issues
- Use `scripts/debug_code_blocks.py` for code block analysis

## Phase-Specific Debugging
- **Phase 1-2**: Focus on theory and mesh generation
- **Phase 3**: Check SIMPLE algorithm and turbulence implementation
- **Phase 4**: Critical - expansion term and VOF phase change
- **Phase 5-6**: Integration and validation issues
