# Verification Fundamentals - Overview

ภาพรวม Verification

---

## Overview

> **Verification** = Are we solving the equations correctly?

---

## 1. V&V Definitions

| Term | Question |
|------|----------|
| **Verification** | Solving equations right? |
| **Validation** | Solving right equations? |

---

## 2. Verification Types

| Type | Check |
|------|-------|
| **Code** | Implementation |
| **Solution** | Convergence |
| **Calculation** | Consistency |

---

## 3. Key Methods

| Method | Purpose |
|--------|---------|
| MMS | Manufactured solutions |
| Grid convergence | Order of accuracy |
| Conservation | Flux balance |

---

## 4. Module Contents

| File | Topic |
|------|-------|
| 01_Introduction | Basics |
| 03_Architecture | Testing structure |

---

## 5. Quick Checks

```bash
# Convergence
grep 'Solving for' log | tail -20

# Conservation
grep 'sum local' log

# Mesh quality
checkMesh
```

---

## Quick Reference

| Check | How |
|-------|-----|
| Residuals | Log analysis |
| Conservation | Flux balance |
| Order | Grid refinement |
| Implementation | MMS |

---

## Concept Check

<details>
<summary><b>1. Verification คืออะไร?</b></summary>

**Check code solves equations correctly**
</details>

<details>
<summary><b>2. MMS คืออะไร?</b></summary>

**Method of Manufactured Solutions** — create known answer
</details>

<details>
<summary><b>3. Grid convergence ทดสอบอะไร?</b></summary>

**Order of accuracy** — error vs mesh size
</details>

---

## Related Documents

- **Introduction:** [01_Introduction.md](01_Introduction.md)
- **Architecture:** [03_OpenFOAM_Architecture.md](03_OpenFOAM_Architecture.md)