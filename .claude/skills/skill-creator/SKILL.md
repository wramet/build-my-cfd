---
name: Skill Creator
description: |
  Use this skill when: creating new Claude Code skills, updating existing skills, or needing guidance on skill best practices.
  
  This skill provides guidance for creating effective skills that integrate with the project's refactor_batch.py workflow.
---

# Skill Creator

This skill provides guidance for creating effective skills for Claude Code.

## Skill Structure

Every skill consists of a required SKILL.md file and optional bundled resources:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter metadata (required)
│   │   ├── name: (required)
│   │   └── description: (required)
│   └── Markdown instructions (required)
└── Bundled Resources (optional)
    ├── scripts/          - Executable code (Python/Bash/etc.)
    ├── references/       - Documentation for context
    └── assets/           - Files used in output (templates, icons)
```

## SKILL.md Format

### Frontmatter (YAML)

```yaml
---
name: Skill Name
description: |
  Use this skill when: [trigger conditions]
  
  [What the skill does and provides]
---
```

**Critical**: The description field is how Claude determines when to use the skill. Be clear and comprehensive.

### Body (Markdown)

Instructions and guidance for using the skill. Only loaded AFTER the skill triggers.

## Core Principles

### Concise is Key

- Keep SKILL.md lean and focused
- Move detailed reference material to references/ files
- Avoid duplicating information between SKILL.md and reference files

### What NOT to Include

- README.md
- INSTALLATION_GUIDE.md
- CHANGELOG.md
- User-facing documentation
- Process documentation

## Skill Creation Process

### Step 1: Understand Use Cases

Ask clarifying questions:
- "What functionality should this skill support?"
- "Can you give examples of how this skill would be used?"
- "What would a user say that should trigger this skill?"

### Step 2: Plan Reusable Resources

Analyze each use case to identify:
- **Scripts**: Code that gets rewritten repeatedly
- **References**: Documentation Claude should reference while working
- **Assets**: Files used in output (templates, images)

### Step 3: Create the Skill

1. Create directory: `.claude/skills/<skill-name>/`
2. Create SKILL.md with YAML frontmatter
3. Add optional resources to scripts/, references/, assets/

### Step 4: Test and Iterate

1. Test the skill with representative examples
2. Verify the description triggers appropriately
3. Refine instructions based on results

## Integration with refactor_batch.py

Skills in this project are designed to work with the refactor_batch.py workflow:

1. **content-quality-checker**: Validates documentation quality
2. **mermaid-diagram-generator**: Creates Mermaid diagrams for concepts
3. **skill-creator**: This skill for creating new skills

When creating new skills, ensure they:
- Have clear trigger descriptions in frontmatter
- Provide actionable instructions in the body
- Integrate with the existing refactor workflow
