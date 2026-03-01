# Content Creation Workflow Details

Detailed step-by-step instructions for the 6-stage content creation workflow.

## Stage 1: Extract Ground Truth

**Purpose:** Research and extract verified facts from source code

**Tasks:**
1. Use WebSearch to find latest OpenFOAM documentation
2. Extract class hierarchy from source code in `openfoam_temp/src/finiteVolume`
3. Extract mathematical formulas with operators (|r| vs r)
4. Mark all facts with ⭐ (verified) or ⚠️ (from docs)

**Output:** `/tmp/verified_facts_dayXX.json`

**JSON Structure:**
```json
{
  "class_hierarchy": {},
  "formulas": {},
  "documentation": []
}
```

**Model:** GLM-4.7 (via Claude Main Agent)

---

## Stage 2: Generate Skeleton

**Purpose:** Create structured outline with verified facts

**Requirements:**
- English headers only (no Thai translation)
- Roadmap-aligned structure (read roadmap.md)
- CFD standards compliance
- All verified facts marked with ⭐

**Output:** `daily_learning/skeletons/dayXX_skeleton.json`

**Model:** GLM-4.7 (via Claude Main Agent)

---

## Stage 2.5: Generate Structural Blueprint

**Purpose:** Create progressive-overload learning structure from template library

**Script:** `python3 .claude/scripts/generate_blueprint.py <day> "<topic>"`

**What It Does:**
1. Reads skeleton.json + verified_facts.json
2. Determines template type based on topic characteristics
3. Generates blueprint.json with progressive overload structure
4. Auto-approves (no manual review needed)

**Template Types:**

| Template | Focus | Best For | Structure |
|----------|--------|----------|-----------|
| **Engine-Builder** | Code-heavy | Matrix Assembly, Solver Core | Concept (20%) → Architecture (30%) → Implementation (40%) → Testing (10%) |
| **Scientist** | Physics-heavy | Phase Change, VOF, Turbulence | Theory (25%) → Physics Explained (40%) → Implementation (25%) → Validation (10%) |
| **Mathematician** | Theory-heavy | Discretization, Stability | Theory (30%) → Physical Challenge (20%) → Architecture (35%) → QA (15%) |
| **Integration Engineer** | Hybrid | Expansion Term, Tabulation, Boiling Test | Theory+Physics (25%) → Strategy (30%) → Validation (25%) → Debug (20%) |

**Output:** `blueprints/dayXX_blueprint.json`

---

## Stage 3: Verify Skeleton

**Purpose:** Validate skeleton and blueprint against ground truth

**Verification Tasks:**
1. Class hierarchy matches ground truth exactly
2. Formulas match ground truth (check operators!)
3. No hallucinated classes or methods
4. All ⭐ facts are verified

**Output Format:**
- PASS if all checks succeed
- FAIL with specific issues if any mismatch found

**Model:** DeepSeek R1 (Direct API)

**Output:** `/tmp/verification_report_dayXX.txt`

**On Failure:** Fix issues before proceeding to Stage 4

---

## Stage 4: Generate Content

**Purpose:** Expand skeleton into full English content

**Critical Requirements:**
- **ENGLISH-ONLY** content (no Thai translation)
- Follow **EXACT structure** defined in blueprint.json
- **Progressive Overload:** Start simple, ramp to complex, consolidate
- **Concept First, Code Second:** Show diagrams before code
- **Quarantine Boilerplate:** Move headers/constructors to appendix

**Content Standards:**
- Theory: ≥500 lines with complete derivations
- Code: 3-5 snippets with file paths and line numbers
- Implementation: ≥300 lines C++ code
- Exercises: 4-6 concept checks
- All ⭐ facts remain unchanged

**Model:** DeepSeek Chat V3 (Direct API)

**Output:** `Phase_01_Foundation_Theory/XX.md`

---

## Stage 4a: Content Quality Verification

**Purpose:** Verify generated content meets quality standards (≥80% of benchmark)

**Usage:**
```bash
/verify-content-quality --day=${DAY} --file=Phase_01_Foundation_Theory/XX.md
```

**Quality Metrics:**
- Line count: ≥1900 target, ≥1500 minimum
- Theory: Complete derivations, multiple approaches
- Code: File paths + line numbers + line-by-line
- HERO CONCEPT: Full derivation + R410A
- Exercises: ≥6 with detailed solutions
- Diagrams: ≥3 Mermaid, valid syntax

**Regeneration Loop:**
If quality score < 80%:
1. Analyze gaps from QC report
2. Update prompt with gap-specific requirements
3. Regenerate content (max 3 attempts)
4. Re-verify until pass or max attempts reached

**Output:** Quality score (0-100%), pass/fail status, gap analysis

---

## Stage 5: Final Verification

**Purpose:** Final technical verification before publishing

**Verification Tasks:**
1. All Mermaid diagrams match ground truth
2. All formulas in LaTeX match ground truth (check operators!)
3. Code snippets are syntactically correct
4. No ⚠️ claims without explanation
5. Structure follows blueprint progressive overload
6. Boilerplate code quarantined to appendix
7. **MANDATORY:** Appendix section present with exact title
8. Appendix contains complete, compilable code

**Model:** DeepSeek R1 (Direct API)

**Output:** `/tmp/final_verification_dayXX.txt`

---

## Stage 6: Syntax QC

**Purpose:** Validate syntax before publishing

**Script:** `python3 .claude/scripts/qc_syntax_check.py --file=daily_learning/Phase_01_Foundation_Theory/XX.md`

**Checks:**
- All code blocks are balanced
- No nested LaTeX delimiters
- Headers follow hierarchy
- Mermaid syntax is valid

**Output:** QC report + pass/fail status

---

## Stage 6.5: AI-Powered Mermaid Validation

**Purpose:** Validate and fix Mermaid diagram syntax issues using AI

**Script:** `python3 .claude/scripts/mermaid_ai_validator.py --file=daily_learning/Phase_01_Foundation_Theory/XX.md --fix`

**What It Does:**
1. **Fast Path Validation:** Regex patterns for common errors
2. **AI Agent Analysis:** Delegates complex errors to mermaid-validator agent
3. **Auto-Fix:** Applies minimal syntax-only changes

**Common Fixes:**
- Pipe `|` in node text → wrap in quotes: `["text|with|pipes"]`
- Special chars in edge labels → wrap in quotes: `-->|"label·φ"|`
- Flowchart nodes with special chars → wrap in quotes: `["text()"]`
- Non-breaking spaces → replace with standard spaces

**Output:** Fixed markdown file + detailed report
