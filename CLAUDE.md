# C++ & Software Engineering Through OpenFOAM

## Project Goal

Learn **intermediate-to-advanced C++ and software engineering** through OpenFOAM case studies and real-world patterns.

**Target:** Master C++ by studying production code (84 sessions, 5 phases)

---

## Key Files to Reference

| File | Purpose |
|------|---------|
| [roadmap.md](roadmap.md) | **Master learning plan** - 84 sessions, 5 phases |
| [.claude/rules/source-first.md](.claude/rules/source-first.md) | Ground truth extraction methodology |
| [.claude/rules/cfd-standards.md](.claude/rules/cfd-standards.md) | LaTeX, Mermaid, Code standards |
| [.claude/rules/verification-gates.md](.claude/rules/verification-gates.md) | 6 mandatory verification checkpoints |

---

## Project Architecture

```
th_new/
├── roadmap.md                           # Master plan (READ THIS FIRST)
├── CLAUDE.md                            # This file
├── daily_learning/                      # Daily content (Sessions 01-84)
│   ├── Phase_01_CppThroughOpenFOAM/     # C++ patterns in OpenFOAM (01-14)
│   ├── Phase_02_DataStructuresMemory/   # Data structures & memory (15-28)
│   ├── Phase_03_SoftwareArchitecture/   # Architecture patterns (29-42)
│   ├── Phase_04_PerformanceOptimization/ # Profiling & optimization (43-56)
│   ├── Phase_05_FocusedCFDComponent/     # Focused CFD component (57-84)
│   ├── blueprints/                      # Content blueprints
│   ├── walkthroughs/                    # Interactive walkthroughs
│   └── skeletons/                       # Content skeletons
├── .claude/
│   ├── agents/                          # 10 specialized agents
│   │   ├── architect, engineer, researcher
│   │   ├── verifier, qc-agent, translator
│   │   └── deepseek-* (DeepSeek variants)
│   ├── skills/                          # Reusable workflows
│   │   ├── content-creation/            # Daily content generation
│   │   ├── walkthrough/                 # Interactive walkthroughs
│   │   ├── qa/                          # Q&A capture
│   │   ├── create-module/               # Module creation
│   │   ├── source-first/                # Source-first methodology
│   │   ├── cpp_pro/                     # C++ coding (OpenFOAM-aware)
│   │   ├── mermaid_expert/              # Diagram generation
│   │   ├── scientific_skills/           # Scientific computing
│   │   ├── systematic_debugging/        # Iron Law debugging
│   │   ├── integration/                 # Agent/hook bridges
│   │   └── orchestrator/                # Skill execution engine
│   ├── scripts/                         # Verification & utility scripts
│   ├── rules/                           # CFD standards & methodology
│   ├── hooks/                          # Automation triggers
│   ├── mcp/                            # DeepSeek MCP server
│   ├── config/                         # Performance & agent config
│   ├── tasks/                          # Curriculum task tracking (17 tasks)
│   ├── test_cases/                     # Mermaid diagram tests
│   ├── utils/                          # Smart file loading
│   ├── contexts/                       # Mode-specific contexts
│   └── templates/                      # Content templates
└── MODULE_*/                           # Reference modules (01-10)
```

---

## Available Skills

### Content Creation
- **`/create-day`** - Generate daily content with Source-First workflow
- **`/walkthrough`** - Interactive walkthrough with verification
- **`/create-module`** - Create/update MODULE content

### Quality & Verification
- **`/qa`** - Q&A capture for walkthroughs
- **`source-first`** - Ground truth extraction workflow

### Technical Expertise
- **`cpp_pro`** - C++ coding (OpenFOAM-aware)
- **`mermaid_expert`** - Diagram generation
- **`scientific_skills`** - Scientific computing & LaTeX
- **`systematic_debugging`** - 4-phase debugging process

---

## AI Model Strategy

| Task | Model | Why |
|------|-------|-----|
| Main orchestrator | GLM-4.7 | Native tools, Web Search, Top-Tier coding |
| Complex reasoning | DeepSeek R1 | Math derivations, analysis |
| Coding | DeepSeek V3 | Fast code generation |
| Verification | DeepSeek R1 | Statistical testing (3x for confidence) |

### MCP Integration

**DeepSeek MCP Server** (`.claude/mcp/deepseek_mcp_server.py`):
- Direct API integration to DeepSeek
- Response caching (100MB cache, /tmp/prompt_cache)
- Context overflow handling

Configuration in `.mcp.json`:
```json
{
  "mcpServers": {
    "deepseek": {
      "command": "python3",
      "args": [".claude/mcp/deepseek_mcp_server.py"],
      "env": {
        "DEEPSEEK_API_KEY": "...",
        "PROMPT_CACHE_ENABLED": "true",
        "CACHE_SIZE_MB": "100",
        "CACHE_DIR": "/tmp/prompt_cache"
      }
    }
  }
}
```

---

## Curriculum Task Management

Track progress with the built-in task manager:

```bash
# List all tasks
python3 .claude/scripts/task_manager.py list

# Show pending tasks
python3 .claude/scripts/task_manager.py pending

# Execute a task interactively
.claude/scripts/execute_task.sh TASK_001
```

**17 tasks** across 7 layers for curriculum refactoring and content generation.

---

## Content Standards

### Language Preference
**Default:** English only (per user request)

Headers can be bilingual, but content should be English.

### Technical Accuracy
- ⭐ = Verified from source code
- ⚠️ = Unverified claim
- ❌ = Incorrect/Don't

### Code Standards
- All code blocks must have language tags
- All code blocks must be balanced
- No nested LaTeX delimiters
- File references must include paths and line numbers

---

## Verification Tools

```bash
# Ground truth extraction
.claude/scripts/extract_facts.py --mode hierarchy

# Verification
.claude/scripts/verify_skeleton.py
.claude/scripts/verify_content.py
.claude/scripts/qc_syntax_check.py --file <file.md>
```

---

## Smart Loading Utilities

For large OpenFOAM files, use smart loading:

```bash
# RAG-style chunked reading
python3 .claude/utils/smart_reader.py <file>

# Enhanced content loading
python3 .claude/utils/content_loader.py <file>
```

---

## Quick Start for New Sessions

1. Read [roadmap.md](roadmap.md) to understand current day
2. Check [daily_learning/](daily_learning/) for existing content
3. Use `/create-day` to generate new content with Source-First workflow
4. Track progress with `python3 .claude/scripts/task_manager.py pending`

---

## Performance Optimization

Completed optimizations (documented in `.claude/PERFORMANCE_OPTIMIZATION_COMPLETE.md`):
- ✅ 46% faster parallel execution
- ✅ 80% cache hit rate
- ✅ Agent enhancements with Constitutional AI

---

*Last Updated: 2026-03-01*
*Project Phase: C++ & Software Engineering Learning*
