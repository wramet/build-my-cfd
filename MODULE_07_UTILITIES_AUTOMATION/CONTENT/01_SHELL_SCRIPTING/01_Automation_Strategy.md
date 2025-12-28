# Automation Strategy

กลยุทธ์การ Automate

---

## Overview

> **Strategy** สำหรับ effective automation

---

## 1. Principles

| Principle | Description |
|-----------|-------------|
| Reproducible | Same results every time |
| Documented | Know what it does |
| Error handling | Handle failures |
| Modular | Reusable parts |

---

## 2. Workflow Phases

```mermaid
flowchart LR
    A[Pre] --> B[Solve]
    B --> C[Post]
    C --> D[Analyze]
```

---

## 3. Script Structure

```bash
#!/bin/bash
# Phase 1: Pre-processing
./Allrun.pre

# Phase 2: Solve
./Allrun.solve

# Phase 3: Post-processing
./Allrun.post
```

---

## 4. Allrun.pre

```bash
#!/bin/bash
blockMesh
setFields
decomposePar
```

---

## Quick Reference

| Phase | Scripts |
|-------|---------|
| Pre | Mesh, initialize |
| Solve | Run solver |
| Post | Process, plot |

---

## Concept Check

<details>
<summary><b>1. ทำไมแยก phases?</b></summary>

**Debug easily**, rerun specific phase
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)