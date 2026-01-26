# Using the /create-day Skill

## Quick Start

You can now create Day 03 content with a single command:

```bash
cd /Users/woramet/Documents/th_new
/create-day 03
```

That's it! The skill will:

1. ✅ Auto-detect "Spatial Discretization Schemes" as the topic
2. ✅ Extract ground truth from OpenFOAM source code
3. ✅ Create content skeleton with architect agent
4. ✅ Generate 7000+ lines of verified content
5. ✅ Verify output against ground truth

## What Happens Automatically

```
Day 03 Request
    ↓
Auto-detect: "Spatial Discretization Schemes"
    ↓
Extract from: openfoam_temp/src/finiteVolume/interpolation/surfaceInterpolation
    ↓
Ground Truth → /tmp/verified_facts.json
    ↓
Architect Agent (DeepSeek R1) → Skeleton
    ↓
Engineer Agent (DeepSeek V3) → 7000+ lines content
    ↓
Verifier Agent (GLM-4.7) → QC Report
    ↓
Output: daily_learning/Phase_01_Foundation_Theory/03.md
```

## Usage Examples

```bash
# Create Day 03
/create-day 03

# Create Day 15 (Advanced phase - auto-detected)
/create-day 15

# Create Day 28 (Programming phase - auto-detected)
/create-day 28
```

## Skill Files

```
.claude/skills/create-day/
├── SKILL.md              # Main skill file (required)
├── orchestrator.py       # Workflow orchestration script
├── topics.json           # Complete curriculum map
└── skill.yaml            # Additional metadata
```

## Direct Script Alternative

If the skill doesn't trigger, you can run directly:

```bash
python3 .claude/skills/create-day/orchestrator.py --day=03
```

Or use the wrapper script:

```bash
./create-content 03
```

## What Gets Generated

```
daily_learning/
├── Phase_01_Foundation_Theory/
│   └── 03.md                    # Final content (7000+ lines)
├── skeletons/
│   └── day03_skeleton.json      # Content outline
└── drafts/
    └── day03_verification.md    # QC report
```

## Content Standards

- **Theory**: ≥3000 lines with math derivations (⭐ verified)
- **OpenFOAM Reference**: ≥2000 lines with class hierarchies
- **Implementation**: ≥1500 lines with C++ code examples
- **All formulas**: Marked with ⭐ + source file:line
- **Code blocks**: Balanced with language tags
- **Headers**: Bilingual (English/Thai)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Skill not found | Check `.claude/skills/create-day/SKILL.md` exists |
| Topic not detected | Verify `roadmap.md` has Day 03 entry |
| Proxy not running | Orchestrator starts it automatically |
| Content too short | Re-run the skill |

## Next Steps After Generation

```bash
# Review the output
cat daily_learning/Phase_01_Foundation_Theory/03.md

# Run QC check (optional)
/qc-modular --file=daily_learning/Phase_01_Foundation_Theory/03.md
```

---

**Ready to create Day 03? Just run:**

```bash
/create-day 03
```
