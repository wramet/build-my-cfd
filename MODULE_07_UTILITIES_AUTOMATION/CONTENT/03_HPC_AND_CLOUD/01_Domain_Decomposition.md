# Domain Decomposition

การแบ่ง Domain สำหรับ Parallel

---

## Overview

> **Decomposition** = Split mesh for parallel computing

---

## 1. Decomposition Methods

| Method | Use |
|--------|-----|
| scotch | Auto-balanced |
| simple | Regular domains |
| hierarchical | Multi-level |

---

## 2. Setup

```cpp
// system/decomposeParDict
numberOfSubdomains 8;
method scotch;
```

---

## 3. Simple Method

```cpp
method simple;
simpleCoeffs
{
    n (4 2 1);  // x y z splits
}
```

---

## 4. Run

```bash
# Decompose
decomposePar -force

# Check
ls -la processor*/constant/

# Run parallel
mpirun -np 8 simpleFoam -parallel
```

---

## 5. Reconstruct

```bash
# All times
reconstructPar

# Latest only
reconstructPar -latestTime
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Split | decomposePar |
| Check | ls processor* |
| Merge | reconstructPar |

---

## Concept Check

<details>
<summary><b>1. scotch ดีอย่างไร?</b></summary>

**Auto-balances** cells across processors
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)