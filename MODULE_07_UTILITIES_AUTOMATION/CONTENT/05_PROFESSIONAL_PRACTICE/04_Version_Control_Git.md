# Version Control with Git

การใช้ Git สำหรับ Version Control

---

## Overview

> **Git** = Track changes, collaborate

---

## 1. Initialize

```bash
cd project
git init
git add .
git commit -m "Initial commit"
```

---

## 2. .gitignore

```
# OpenFOAM specific
[0-9]*
!0/
processor*/
postProcessing/
log.*
*.foam
```

---

## 3. Basic Workflow

```bash
# Create branch
git checkout -b feature/new-bc

# Make changes, commit
git add -A
git commit -m "Add new BC"

# Merge back
git checkout main
git merge feature/new-bc
```

---

## 4. Remote

```bash
git remote add origin git@github.com:user/project.git
git push -u origin main
```

---

## 5. Tags

```bash
# Mark validated state
git tag -a v1.0 -m "Validated against NASA data"
git push --tags
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Initialize | git init |
| Stage | git add |
| Commit | git commit |
| Push | git push |
| Tag | git tag |

---

## Concept Check

<details>
<summary><b>1. .gitignore ใส่อะไร?</b></summary>

**Generated files** — results, logs, processor dirs
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)