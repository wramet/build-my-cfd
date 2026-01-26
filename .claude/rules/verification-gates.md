# Verification Gates

Mandatory checkpoints for ensuring technical accuracy throughout content creation.

## What Are Verification Gates?

Verification gates are **mandatory stops** where content must be verified before proceeding to the next stage. If verification fails, you **must stop** and fix issues before continuing.

## The 6 Verification Gates

### Gate 1: Ground Truth Extraction

**When:** After extracting facts from source code

**Verify:**
- [ ] Extraction completed without errors
- [ ] Output files exist and are non-empty
- [ ] JSON structure is valid

**Check command:**
```bash
ls -lh /tmp/ground_truth*.txt /tmp/verified_facts.json
```

**On failure:** Fix extraction, re-run `extract_facts.py`

---

### Gate 2: Skeleton Generation

**When:** After AI generates skeleton

**Verify:**
- [ ] Class hierarchy matches ground truth
- [ ] Formulas match ground truth
- [ ] No hallucinated classes or methods

**Check command:**
```bash
python3 .claude/scripts/verify_skeleton.py \
    --ground-truth /tmp/verified_facts.json \
    --skeleton daily_learning/skeletons/dayXX_skeleton.json \
    --output verification_report.md

# Check for failures
grep -q "❌ VERIFICATION_FAILED" verification_report.md && exit 1
```

**On failure:** Review report, fix skeleton or ground truth, re-verify

---

### Gate 3: Content Generation

**When:** After AI expands skeleton into full content

**Verify:**
- [ ] Mermaid diagrams match verified hierarchy
- [ ] Formulas in LaTeX match verified versions
- [ ] Code snippets are syntactically correct

**Check command:**
```bash
python3 .claude/scripts/verify_content.py \
    --content daily_learning/drafts/dayXX_draft.md \
    --ground-truth /tmp/verified_facts.json \
    --output content_verification.md

# Check for errors
grep -q "❌ TECHNICAL_ERROR" content_verification.md && exit 1
```

**On failure:** Fix technical errors, re-verify before translation

---

### Gate 4: Syntax QC

**When:** After content is generated, before translation

**Verify:**
- [ ] All code blocks are balanced
- [ ] No nested LaTeX
- [ ] Headers follow hierarchy
- [ ] Mermaid syntax is valid

**Check command:**
```bash
# Code blocks
awk '/```/{count++} END{print count, (count%2==0 ? "✅" : "❌")}' file.md

# Nested LaTeX
! grep -q '\$\$.*\$[^$]' file.md && echo "✅" || echo "❌"

# Headers
grep -n '^#' file.md | sort -k1.1n
```

**On failure:** Run `/qc-modular` to fix issues

---

### Gate 5: Translation

**When:** After translating to Engineering Thai

**Verify:**
- [ ] All headers are bilingual
- [ ] Technical terms kept in English
- [ ] Code blocks unchanged
- [ ] LaTeX intact

**Check:**
- Visual inspection of file
- Search for translated technical terms (should find none)

**On failure:** Fix translations manually

---

### Gate 6: Final Validation

**When:** Before publishing content

**Verify:**
- [ ] All previous gates passed
- [ ] File renders correctly in preview
- [ ] All links work
- [ ] No truncated content

**Check command:**
```bash
# Final comprehensive check
python3 .claude/scripts/final_validation.py file.md
```

**On failure:** Fix remaining issues before publishing

---

## Gate Enforcement

### Automated Enforcement

These gates are enforced by:

1. **Hooks:** Pre-edit and post-write checks
2. **Workflow:** Built into `/create-day` command
3. **Agents:** `verifier` agent validates content
4. **Scripts:** Verification tools check accuracy

### Manual Enforcement

Even with automation, you should:

1. **Review reports:** Read verification reports carefully
2. **Check output:** Visual inspection of generated content
3. **Test examples:** Try code examples in OpenFOAM
4. **Cross-reference:** Compare with documentation

## Bypassing Gates

**❌ FORBIDDEN:** Skipping verification gates

**Exception:** Only for non-technical content (general explanations, opinions)

**When bypassing:**
- Mark content clearly: `⚠️ Unverified - Use with caution`
- Document reason for bypass
- Plan to verify later

## Gate Status Indicators

Use these in your workflow:

```markdown
### Gate 1: Ground Truth Extraction
- Status: ✅ PASSED
- Output: /tmp/verified_facts.json
- Timestamp: 2026-01-24 10:30

### Gate 2: Skeleton Verification
- Status: ❌ FAILED
- Issues: 2 mismatches found
- Action: Fixing now...

### Gate 3: Content Verification
- Status: ⏸️ PENDING
- Waiting for: Gate 2 to pass
```

## Best Practices

1. **Stop at failures:** Don't proceed when a gate fails
2. **Document issues:** Note what failed and why
3. **Fix thoroughly:** Don't make quick fixes that introduce new issues
4. **Re-verify:** After fixing, run verification again
5. **Keep reports:** Save verification reports for reference

## Quick Reference

| Gate | Script | Status Check |
|------|--------|--------------|
| Ground Truth | `extract_facts.py` | Output files exist? |
| Skeleton | `verify_skeleton.py` | No ❌ in report? |
| Content | `verify_content.py` | No ❌ in report? |
| Syntax | `qc_syntax_check.py` | All checks pass? |
| Translation | Visual | Headers bilingual? |
| Final | `final_validation.py` | All checks pass? |

---

**See also:** `source-first.md`, `cfd-standards.md`
