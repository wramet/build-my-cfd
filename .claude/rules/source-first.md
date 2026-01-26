# Source-First Rule

🔒 **Core Principle:** Ground Truth from source code > AI analysis > Internal training

## What This Means

When creating or modifying CFD learning content:

1. **Extract facts FIRST** from actual OpenFOAM source code
2. **Verify ALL technical claims** before including them
3. **Mark verified content** with ⭐ emoji
4. **Label unverified content** clearly with ⚠️

## Mandatory Requirements

### For Technical Claims

**Class Hierarchies:**
- ✅ Required: Extract from actual `.H` files
- ✅ Required: Verify with `extract_facts.py`
- ✅ Required: Mark verified with ⭐
- ❌ Forbidden: Rely on AI memory or external documentation

**Mathematical Formulas:**
- ✅ Required: Extract from actual implementation files
- ✅ Required: Verify operator accuracy (especially `|r|` vs `r`)
- ✅ Required: Include source file reference
- ❌ Forbidden: Use formulas from documentation without verification

**Code Snippets:**
- ✅ Required: Test in actual OpenFOAM environment
- ✅ Required: Verify syntax and correctness
- ✅ Required: Include file path and line numbers
- ❌ Forbidden: Generate code without verification

### For Content Creation

**Before using AI:**
1. Extract ground truth from source code
2. Structure into JSON format
3. Load as constraints in AI prompt

**After AI generates:**
1. Verify output against ground truth
2. Check for hallucinations
3. Only use verified content

## When Source-First Applies

**Must use for:**
- Class hierarchies and inheritance
- Mathematical formulas and equations
- API signatures and method names
- Code examples and snippets
- Implementation details

**Optional for:**
- General explanations
- High-level concepts
- Non-technical content
- Opinions and commentary

## Verification Markers

Use these markers in your content:

```markdown
### ⭐ Verified Fact
> Content verified from [specific source file]

### ⚠️ Unverified Claim
> Content from documentation, needs source verification

### ❌ Incorrect
> Common misconception - here's the correct version
```

## Enforcement

This rule is enforced by:

1. **Hooks:** Pre-edit verification checks
2. **Agents:** `verifier` agent validates content
3. **Scripts:** `verify_*.py` tools check accuracy
4. **Workflow:** Source-First built into all commands

## Consequences

**If this rule is violated:**
- Content may contain technical errors
- Hallucinations can propagate to learners
- Trust in documentation is lost

**If this rule is followed:**
- Content is technically accurate
- Learners can trust the material
- Errors are caught before publication

## Examples

### ✅ Good: Following Source-First

```markdown
### ⭐ upwind Class Hierarchy

> Verified from `openfoam_temp/src/finiteVolume/.../upwind.H:42`

The `upwind` class inherits through **two** levels:

```mermaid
upwind<Type> --> limitedSurfaceInterpolationScheme<Type>
limitedSurfaceInterpolationScheme<Type> --> surfaceInterpolationScheme<Type>
```

This is verified from the actual source code.
```

### ❌ Bad: Not Following Source-First

```markdown
### upwind Class Hierarchy

The `upwind` class inherits from `surfaceInterpolationScheme`:

```mermaid
upwind --> surfaceInterpolationScheme
```

[No verification, missing intermediate class]
```

## Quick Reference

**Extract:** `python3 .claude/scripts/extract_facts.py --mode hierarchy`
**Verify:** `python3 .claude/scripts/verify_skeleton.py`
**Mark:** Use ⭐ for verified, ⚠️ for unverified

---

**See also:** `cfd-standards.md`, `verification-gates.md`
