# Verification Fundamentals - Overview

ภาพรวมการตรวจสอบความถูกต้อง (Verification)

> **Verification** = Are we solving the equations correctly?

---

## Learning Objectives (วัตถุประสงค์การเรียนรู้)

After completing this module, you should be able to:

| Objective | Description |
|:---|:---|
| **Distinguish** | Difference between Verification and Validation |
| **Apply** | Code verification (MMS) and Solution verification (GCI) |
| **Analyze** | Convergence behavior and conservation properties |
| **Evaluate** | OpenFOAM solver accuracy using systematic methods |

---

## 1. V&V Definitions

| Concept | Question | OpenFOAM Files |
|:---|:---|:---|
| **Verification** | Solving equations **right**? | `system/fvSchemes`, `system/fvSolution` |
| **Validation** | Solving the **right** equations? | `0/`, `constant/`, benchmarks |

---

## 2. Verification Types

| Type | Check | Method |
|:---|:---|:---|
| **Code** | Implementation correct? | MMS, Analytical Solutions |
| **Solution** | Solver converges? | Residuals, Grid Convergence |
| **Calculation** | Results consistent? | Conservation Checks, Mass Balance |

---

## 3. Key Methods

| Method | Purpose | Complexity |
|:---|:---|:---|
| **MMS** | Manufactured solutions | High (code modification) |
| **Grid Convergence** | Order of accuracy | Medium (3+ meshes) |
| **Conservation** | Flux balance | Low (routine check) |

---

## 4. Module Contents

| File | Topic | Lines |
|:---|:---|:---:|
| **01_Introduction** | Basics | ~130 |
| **02a_MMS** | Method of Manufactured Solutions | ~220 |
| **02b_Richardson_GCI** | Richardson Extrapolation & GCI | ~195 |
| **03_Architecture** | OpenFOAM Architecture | ~140 |

---

## Quick Reference

| Check | How | Command |
|:---|:---|:---|
| Residuals | Log analysis | `grep 'Solving for' log` |
| Conservation | Flux balance | `grep 'sum local' log` |
| Order | Grid refinement | Run 3 meshes → plot |
| Implementation | MMS | Custom solver code |

---

## Concept Check

<details>
<summary><b>1. Verification คืออะไร?</b></summary>

**Check code solves equations correctly** (แก้สมการถูกไหม?)
</details>

<details>
<summary><b>2. MMS คืออะไร?</b></summary>

**Method of Manufactured Solutions** — create known answer, verify solver finds it
</details>

<details>
<summary><b>3. Grid convergence ทดสอบอะไร?</b></summary>

**Order of accuracy** — error vs mesh size (ความผิดพลาด vs ขนาดเมช)
</details>

---

## Key Takeaways (สรุปสิ่งสำคัญ)

| Concept | Key Point |
|:---|:---|
| **V vs V** | Verification = solving equations right; Validation = solving right equations |
| **Three Types** | Code (implementation), Solution (convergence), Calculation (conservation) |
| **MMS** | Most rigorous code verification method using manufactured analytical solutions |
| **GCI** | Quantifies numerical uncertainty from grid convergence studies |
| **OpenFOAM** | Check residuals in logs, conservation in `sum local`, implement MMS in custom solvers |

---

## Related Documents

- **Introduction:** [01_Introduction.md](01_Introduction.md)
- **MMS:** [02a_Method_of_Manufactured_Solutions_MMS.md](02a_Method_of_Manufactured_Solutions_MMS.md)
- **Richardson & GCI:** [02b_Richardson_Extrapolation_GCI.md](02b_Richardson_Extrapolation_GCI.md)
- **Architecture:** [03_OpenFOAM_Architecture.md](03_OpenFOAM_Architecture.md)