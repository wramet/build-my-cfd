# CLAUDE.md - Project Instructions for Claude Code

This file contains project-specific instructions that Claude Code follows when working in this repository.

---

## 🚫 CRITICAL RULES - DO NOT VIOLATE

### 1. NEVER Delete `.claude` Folder

**The `.claude/` directory is PROTECTED and MUST NOT be deleted, moved, or modified without explicit user permission.**

```
⚠️ FORBIDDEN ACTIONS:
- rm -rf .claude
- git clean (affecting .claude)
- Any command that removes .claude folder
- Any operation that deletes hidden folders starting with .
```

This folder contains:
- Claude Skills definitions
- Learning assistant configurations
- Tutor skill files
- Project-specific AI configurations

### 2. Protected Paths

The following paths are PROTECTED and should not be deleted:

```
.claude/                    # Claude Code skills and configurations
.agent/                     # Agent workflows  
daily_learning/             # Daily learning content
MODULE_01-10/               # Educational content modules
```

---

## 📁 Project Structure

```
/Users/woramet/Documents/th_new/
├── .claude/skills/         # ⚠️ PROTECTED - Claude skills
├── .agent/workflows/       # Agent workflow definitions
├── daily_learning/         # Daily learning content
├── MODULE_01-10/           # Educational modules
└── CLAUDE.md               # This file
```

---

## 🎯 Project Context

This is an **OpenFOAM/CFD educational content** repository containing:
- 10 learning modules (MODULE_01 to MODULE_10)
- Daily learning system for self-paced study
- Claude skills for AI-assisted learning

---

## 🔧 Common Tasks

### Creating Daily Learning Content

1. Check `daily_learning/README.md` for learning path
2. Create content file: `daily_learning/YYYY-MM-DD.md`
3. Copy to iCloud: `/Users/woramet/Library/Mobile Documents/com~apple~CloudDocs/daily/`

### Using Skills

Skills are located at `.claude/skills/` and include:
- `daily-lesson-generator` - Create daily lessons
- `learning-assistant` - Route learning questions
- `content-quality-checker` - QC content
- `tutors/` - Various subject tutors

---

## ⚡ Quick Commands

```bash
# Restore .claude if accidentally deleted
git restore .claude

# Check .claude status
ls -la .claude/skills/

# List all skills
find .claude/skills -name "SKILL.md"
```
