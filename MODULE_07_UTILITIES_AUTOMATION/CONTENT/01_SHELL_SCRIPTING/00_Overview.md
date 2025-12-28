# Shell Scripting - Overview

ภาพรวม Shell Scripting

---

## Overview

> **Shell scripts** = Automate OpenFOAM workflows

---

## 1. Allrun Pattern

```bash
#!/bin/bash
cd ${0%/*} || exit 1
. $WM_PROJECT_DIR/bin/tools/RunFunctions

runApplication blockMesh
runApplication simpleFoam
```

---

## 2. Allclean Pattern

```bash
#!/bin/bash
cd ${0%/*} || exit 1

rm -rf 0.[0-9]* [1-9]* log.* postProcessing
cp -r 0.orig 0
```

---

## 3. Module Contents

| File | Topic |
|------|-------|
| 01_Strategy | Planning |
| 02_Framework | Templates |

---

## Quick Reference

| Script | Purpose |
|--------|---------|
| Allrun | Run case |
| Allclean | Clean case |
| Allrun.pre | Pre-process |
| Allrun.post | Post-process |

---

## Concept Check

<details>
<summary><b>1. runApplication ทำอะไร?</b></summary>

**Run with logging** — auto-saves to log.*
</details>

---

## Related Documents

- **Strategy:** [01_Automation_Strategy.md](01_Automation_Strategy.md)