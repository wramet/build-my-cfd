# Optimization Techniques

เทคนิคการ Optimize Performance

---

## Overview

> **Optimize** parallel CFD for best performance

---

## 1. Decomposition

```cpp
// system/decomposeParDict
method scotch;  // Automatic balancing

// Or manual
method simple;
simpleCoeffs { n (4 2 1); }
```

---

## 2. Load Balancing

```bash
# Check balance
grep 'Execution time' log.* | tail -5

# Target: < 10% difference between processors
```

---

## 3. I/O Optimization

```cpp
// Reduce write frequency
writeControl    runTime;
writeInterval   0.1;

// Compress output
writeCompression compressed;
```

---

## 4. Solver Settings

```cpp
// Use efficient preconditioner
solver  PCG;
preconditioner  DIC;
tolerance       1e-6;
relTol          0.1;
```

---

## 5. Memory

```bash
# Check memory per processor
/usr/bin/time -v mpirun -np 4 solver -parallel
```

---

## Quick Reference

| Optimization | How |
|--------------|-----|
| Decomposition | scotch |
| I/O | Reduce writes |
| Solver | Good preconditioner |
| Memory | Fewer stored fields |

---

## Concept Check

<details>
<summary><b>1. scotch ดีอย่างไร?</b></summary>

**Automatic load balancing** — minimize communication
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)