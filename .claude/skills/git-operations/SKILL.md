---
name: git-operations
description: Git best practices and conventional commit enforcement for CFD project
---

# Git Operations

Follow conventional commit format for all changes to the CFD codebase.

## Commit Types

| Type | Purpose | Example |
|------|---------|---------|
| `feat` | New CFD model or solver feature | `feat: add mixing length turbulence model` |
| `fix` | Bug fix in code or math formula | `fix: correct expansion term sign` |
| `docs` | Documentation or daily learning content | `docs: update Day 04 with van Leer limiter` |
| `style` | Formatting checks | `style: fix bilingual header format` |
| `refactor` | Code restructuring without behavior change | `refactor: extract fvMatrix common methods` |

## Commit Message Rules

- Subject line: **< 50 characters**
- Use imperative mood: "Add" not "Added", "Fix" not "Fixed"
- Reference files/lines when relevant: `@upwind.H:42`

**Example:**
```
fix(upwind): correct limiter formula for r < 0

The limiter was returning 0 for all negative r values,
but should return 0 only when r < 0.

Ref: vanLeer.H:67-69
```
