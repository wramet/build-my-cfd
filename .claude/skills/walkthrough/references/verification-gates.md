# Walkthrough Verification Gates

Detailed instructions for the 6 mandatory verification gates in walkthrough generation.

## Gate 1: File Structure

**When:** After reading the input file

**Verify:**
- [ ] Input file exists in `daily_learning/Phase_XX_YourPhase/`
- [ ] File has valid H2 section headers
- [ ] Contains required sections (Theory, Code, Implementation)

**On failure:** Stop workflow and exit with code 1

**Common issues:**
- File path incorrect
- File doesn't have proper section structure
- File is empty or corrupted

---

## Gate 2: Ground Truth Extraction

**When:** After extracting facts from source code

**Verify:**
- [ ] Minimum 5 facts extracted from source code
- [ ] Valid JSON output format
- [ ] No extraction errors reported

**Check command:**
```bash
python3 .claude/scripts/extract_facts.py --mode hierarchy
```

**On failure:** Stop workflow and exit with code 1

**Common issues:**
- OpenFOAM source code not accessible
- Extraction script errors
- Insufficient facts extracted

---

## Gate 3: Theory Equations

**When:** After analyzing theory section

**Verify:**
- [ ] Equations match ground truth exactly
- [ ] LaTeX syntax is valid (no nested delimiters)
- [ ] All equations have file:line references
- [ ] Proper vector notation: `\mathbf{U}` not `\bfU`

**Check command:**
```bash
# Check for nested LaTeX
! grep -q '\$\$.*\$[^$]' file.md && echo "✅" || echo "❌"
```

**On failure:** Stop workflow and exit with code 1

**Common issues:**
- Equation operators wrong (|r| vs r)
- Nested LaTeX delimiters
- Invalid vector commands

---

## Gate 4: Code Structure

**When:** After analyzing code section

**Verify:**
- [ ] Code structure aligns with ground truth
- [ ] No hallucinated classes or methods
- [ ] Class hierarchies match source code
- [ ] File paths and line numbers are correct

**Check:**
- Compare class hierarchy with extracted facts
- Verify all referenced classes exist
- Check method signatures match source

**On failure:** Stop workflow and exit with code 1

**Common issues:**
- Hallucinated class names
- Missing intermediate inheritance levels
- Wrong method signatures

---

## Gate 5: Implementation

**When:** After analyzing implementation section

**Verify:**
- [ ] Implementation consistent with theory
- [ ] All references verified
- [ ] Code examples are syntactically correct
- [ ] Step-by-step logic flows correctly

**Check:**
- Theory equations match implementation
- All code snippets compile
- Implementation steps are logical

**On failure:** Stop workflow and exit with code 1

**Common issues:**
- Theory doesn't match implementation
- Code syntax errors
- Missing implementation steps

---

## Gate 6: Final Coherence

**When:** Before generating final output

**Verify:**
- [ ] Overall consistency across all sections
- [ ] All ⭐ markers present and correct
- [ ] No contradictions between sections
- [ ] All verification markers used properly

**Check:**
- Review all sections for consistency
- Verify all ⭐ markers have ground truth
- Check for ⚠️ markers that should be ⭐

**On failure:** Stop workflow and exit with code 1

**Common issues:**
- Inconsistent information between sections
- Missing verification markers
- Unverified claims that should be verified

---

## Verification Markers

Use these markers in walkthrough output:

- **⭐** = Verified from ground truth
- **⚠️** = Unverified (documentation source)
- **❌** = Incorrect/Don't

## Strict Enforcement

**The workflow STOPS on ANY failure with non-zero exit code.**

This ensures technical accuracy is maintained throughout walkthrough generation.

## Troubleshooting

### "Gate 1 Failed: Invalid file structure"
- Ensure input file exists in correct location
- Check file has proper H2 section headers

### "Gate 2 Failed: Insufficient ground truth"
- Run `extract_facts.py` directly to debug
- Check OpenFOAM source code is accessible

### "Gate 3 Failed: Equation mismatch"
- Compare LaTeX equations with ground truth
- Check for nested delimiters (`$$` inside `$`)

### "Gate 4 Failed: Code structure mismatch"
- Verify class hierarchy matches extracted facts
- Check for hallucinated references

### "Gate 5 Failed: Implementation inconsistent"
- Verify implementation matches theory
- Check code examples for syntax errors

### "Gate 6 Failed: Coherence check failed"
- Review all sections for consistency
- Verify all ⭐ markers have ground truth
