# /create-day 03 Workflow Visualization

Complete trace of tasks, AI models, and tools for Day 03 content creation.

---

## User Command

```bash
/create-day 03
```

---

## Phase 1: Skill Invocation

```
USER: /create-day 03
    ↓
Claude CLI loads: .claude/skills/create-day/SKILL.md
    ↓
SKILL FRONTMATTER:
  - disable-model-invocation: true  (Only user can invoke)
  - allowed-tools: Bash(python:*), Read, Write
    ↓
Executes: python3 .claude/skills/create-day/orchestrator.py --day=03
```

---

## Phase 2: Orchestrator Starts

```
ORCHESTRATOR.PY (Python Script)
├── Task: Content creation for Day 03
└── Model: Not applicable (script logic)
```

---

## Phase 3: Topic Detection

```
ORCHESTRATOR → Topics Database
    ↓
Loads: .claude/skills/create-day/topics.json
    ↓
Step 3.1: Detect Phase
    ├── Day 03 → Phase_01_Foundation_Theory
    └── Output path: daily_learning/Phase_01_Foundation_Theory/

Step 3.2: Detect Topic
    ├── Day 03 → "Spatial Discretization Schemes"
    └── Target path: openfoam_temp/src/finiteVolume/interpolation/surfaceInterpolation

    ↓
TOOLS USED:
  • Read (reads topics.json)
  • Script variable access
    ↓
AI MODEL: None (direct lookup)
```

---

## Phase 4: Ground Truth Extraction

```
ORCHESTRATOR → Extract Facts Script
    ↓
Command:
  python3 .claude/scripts/extract_facts.py \
    --mode all \
    --path "openfoam_temp/src/finiteVolume/interpolation/surfaceInterpolation" \
    --output /tmp/verified_facts.json
    ↓
TOOLS USED:
  • Bash(python:*) - Runs extraction script
  • Write - Creates output file
    ↓
SCRIPT OUTPUT:
  /tmp/verified_facts.json
    ├── classes[]     (OpenFOAM class hierarchy)
    ├── formulas[]    (Mathematical formulas from source)
    └── files[]       (Source file references)

    ↓
AI MODEL: GLM-4.7 (if script uses AI to parse) ✅ Verified
```

---

## Phase 5: Proxy Start (if needed)

```
ORCHESTRATOR → Proxy Health Check
    ↓
Checks: curl http://localhost:8888/health
    ↓
If not running:
  Command: python3 .ccproxy_alt/start_proxy.py
    ↓
TOOLS USED:
  • Bash - Starts proxy process
    ↓
PROXY CONFIGURATION:
  • Primary (DeepSeek): https://api.deepseek.com
    ├── deepseek-chat → engineer
    └── deepseek-reasoner → verifier
  • Z.ai (GLM-4.7): https://api.z.ai/api/paas/v4
    ├── architect
    ├── researcher
    ├── translator
    └── qc-agent

    ↓
AI MODEL: None (proxy infrastructure)
```

---

## Phase 6: Skeleton Creation

```
ORCHESTRATOR → Create Skeleton
    ↓
Task: Create content outline based on ground truth
    ↓
AGENT INVOKED: architect (GLM-4.7 via Z.ai)
    ↓
PROMPT TO ARCHITECT:
  "Create content skeleton for Day 03: Spatial Discretization Schemes
   Using verified facts from /tmp/verified_facts.json
   Include sections for Theory, OpenFOAM Reference, Implementation"

    ↓
TOOLS AVAILABLE TO ARCHITECT:
  • Read - Read roadmap.md, ground truth
  • Write - Create skeleton file
  • Grep - Search roadmap
  • Bash - Run commands

    ↓
ARCHITECT OUTPUT:
  daily_learning/skeletons/day03_skeleton.json
    ├── day: "03"
    ├── topic: "Spatial Discretization Schemes"
    ├── sections[] (Theory, OpenFOAM, Implementation)
    └── line_targets (3000, 2000, 1500)

    ↓
AI MODEL: GLM-4.7 (architect) → Z.ai Backend ✅
```

---

## Phase 7: Content Generation

```
ORCHESTRATOR → Generate Full Content
    ↓
Task: Generate 7000+ lines of verified content
    ↓
AGENT INVOKED: engineer (deepseek-chat via DeepSeek)
    ↓
PROMPT TO ENGINEER:
  "Generate comprehensive Day 03 content on Spatial Discretization Schemes
   Reference: /tmp/verified_facts.json
   Skeleton: daily_learning/skeletons/day03_skeleton.json
   Requirements:
     - Theory: ≥3000 lines with math derivations
     - OpenFOAM: ≥2000 lines with class hierarchies
     - Implementation: ≥1500 lines with C++ code
     - All formulas marked with ⭐ + source file:line"

    ↓
TOOLS AVAILABLE TO ENGINEER:
  • Read - Read ground truth, skeleton, OpenFOAM source
  • Grep - Search source code
  • Glob - Find relevant files
  • Bash - Run commands, compile code
  • Write - Generate content file
  • WebSearch - Research best practices (if enabled)

    ↓
ENGINEER OUTPUT:
  daily_learning/drafts/day03_draft_english.md
    ├── Introduction (500 lines)
    ├── Mathematical Foundation (3000+ lines)
    ├── OpenFOAM Implementation (2000+ lines)
    ├── Practical Examples (1500+ lines)
    └── ⭐ verified formulas throughout

    ↓
AI MODEL: DeepSeek Chat (engineer) → DeepSeek Backend ✅
```

---

## Phase 8: Verification

```
ORCHESTRATOR → Verify Content
    ↓
Task: Cross-check content against ground truth
    ↓
AGENT INVOKED: verifier (deepseek-reasoner via DeepSeek)
    ↓
PROMPT TO VERIFIER:
  "Verify Day 03 content against /tmp/verified_facts.json
   Check:
   - Class hierarchies match source
   - Formulas match implementation
   - Code snippets are correct
   - File references include line numbers"

    ↓
TOOLS AVAILABLE TO VERIFIER:
  • Read - Read content, ground truth
  • Grep - Search source code for verification
  • Bash - Run verification scripts
  • Write - Create verification report

    ↓
VERIFIER OUTPUT:
  daily_learning/drafts/day03_verification.md
    ├── ✅ Verified: [list of verified items]
    ├── ❌ Incorrect: [list of corrections needed]
    └── ⚠️ Unverified: [items needing source check]

    ↓
AI MODEL: DeepSeek Reasoner (verifier) → DeepSeek Backend ✅
```

---

## Phase 9: Quality Control

```
ORCHESTRATOR → Quality Check
    ↓
Task: Syntax and formatting check
    ↓
AGENT INVOKED: qc-agent (GLM-4.7 via Z.ai)
    ↓
PROMPT TO QC-AGENT:
  "Check Day 03 content for:
   - Code block balance
   - Nested LaTeX
   - Header hierarchy
   - Bilingual headers
   - ⭐ verification markers"

    ↓
TOOLS AVAILABLE TO QC-AGENT:
  • Read - Read content file
  • Bash - Run syntax checks
  • Write - Fix issues found
  • Grep - Search for patterns

    ↓
QC-AGENT OUTPUT:
  Fixes applied or report generated

    ↓
AI MODEL: GLM-4.7 (qc-agent) → Z.ai Backend ✅
```

---

## Phase 10: Final Output

```
ORCHESTRATOR → Complete
    ↓
OUTPUT FILES:
  ├── daily_learning/Phase_01_Foundation_Theory/03.md
  ├── daily_learning/skeletons/day03_skeleton.json
  └── daily_learning/drafts/day03_verification.md

    ↓
USER NOTIFIED:
  ✅ Day 03 content creation complete!
  📄 Output: daily_learning/Phase_01_Foundation_Theory/03.md
```

---

## Summary Table

| Phase | Task | AI Model | Backend | Tools Used |
|-------|------|----------|---------|-------------|
| 1. Skill Load | Load SKILL.md | None | - |
| 2. Orchestrator | Run Python script | None | Bash(python:*) |
| 3. Topic Detect | Lookup in topics.json | None | Read |
| 4. Extract Truth | Parse OpenFOAM source | GLM-4.7* | Bash(python:*), Write |
| 5. Proxy Start | Start proxy if needed | None | Bash |
| 6. Skeleton | Create outline | GLM-4.7 | Read, Write, Grep |
| 7. Generate | Write 7000+ lines | DeepSeek Chat | Read, Grep, Glob, Bash, Write |
| 8. Verify | Cross-check facts | DeepSeek Reasoner | Read, Grep, Bash, Write |
| 9. QC | Check syntax/formatting | GLM-4.7 | Read, Bash, Grep, Write |
| 10. Output | Save final files | None | - |

\* If extract_facts.py uses AI for parsing

---

## Model Distribution

| Model | Usage | Backend | Token Estimation |
|-------|-------|---------|-----------------|
| GLM-4.7 | architect, qc-agent, researcher, translator | Z.ai | ~40k tokens total |
| DeepSeek Chat | engineer | DeepSeek | ~80k tokens (content gen) |
| DeepSeek Reasoner | verifier | DeepSeek | ~20k tokens (verification) |

**Total:** ~140k tokens across all models

---

## Tool Usage Distribution

| Tool | Phases | Usage Count |
|------|--------|-------------|
| **Read** | 3,6,7,8,9 | 15+ times |
| **Write** | 4,7,8,9,10 | 8 times |
| **Bash** | 4,5,7,8,9 | 10+ times |
| **Grep** | 6,7,8,9 | 8+ times |
| **Glob** | 7 | 2-3 times |

---

## Visual Flowchart

```mermaid
graph TD
    A[User: /create-day 03] --> B[Load SKILL.md]
    B --> C[Run orchestrator.py]
    C --> D[Detect Topic<br/>topics.json]
    D --> E[Extract Ground Truth<br/>extract_facts.py]
    E --> F[/tmp/verified_facts.json]
    F --> G{Proxy Running?}
    G -->|No| H[Start Proxy]
    G -->|Yes| I[Create Skeleton]
    H --> I
    I --> J[Architect Agent<br/>GLM-4.7 → Z.ai]
    J --> K[day03_skeleton.json]
    K --> L[Generate Content]
    L --> M[Engineer Agent<br/>DeepSeek Chat → DeepSeek]
    M --> N[day03_draft_english.md<br/>7000+ lines]
    N --> O[Verify Content]
    O --> P[Verifier Agent<br/>DeepSeek Reasoner → DeepSeek]
    P --> Q[day03_verification.md]
    Q --> R[Quality Check]
    R --> S[QC Agent<br/>GLM-4.7 → Z.ai]
    S --> T[Final Output]
    T --> U[✅ Complete!<br/>03.md created]
```

---

## Key Insights

### 1. Multi-Agent Orchestration

Your setup uses **4 different AI models** automatically:
- **GLM-4.7** (via Z.ai) → Planning, QC, research
- **DeepSeek Chat** (via DeepSeek) → Content generation
- **DeepSeek Reasoner** (via DeepSeek) → Verification

### 2. Tool Usage

**Read tool** is the most critical (15+ times):
- Reads ground truth
- Reads OpenFOAM source
- Reads generated content
- Reads verification results

**Write tool** saves 8 key outputs.

### 3. Backend Routing

All routing happens automatically via proxy:
```
Request with model=X → Proxy → Routes to correct backend
```

### 4. Source-First Verification

Every formula, class hierarchy, and code snippet is verified against actual OpenFOAM source code before being included in content.
