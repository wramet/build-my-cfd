# Performance Introduction

บทนำ Performance Optimization

---

## Overview

> CFD simulations are **memory and compute intensive**

---

## 1. Performance Bottlenecks

| Bottleneck | Cause |
|------------|-------|
| **Memory** | Large allocations |
| **Bandwidth** | Data transfer |
| **CPU** | Computation |
| **I/O** | Disk access |

---

## 2. OpenFOAM Optimizations

### Memory

```cpp
// tmp avoids copies
tmp<volScalarField> result = fvc::grad(p);
```

### Computation

```cpp
// Templates enable inlining
volScalarField y = sqr(x);  // Can be inlined
```

---

## 3. Profiling

```bash
# Profile first
perf record -g solver
perf report

# Then optimize hotspots
```

---

## 4. Common Issues

| Issue | Solution |
|-------|----------|
| Temporary allocations | Use tmp |
| Virtual call overhead | Batch operations |
| Cache misses | Contiguous access |

---

## Quick Reference

| Priority | Action |
|----------|--------|
| 1 | Profile |
| 2 | Reduce allocations |
| 3 | Improve cache usage |
| 4 | Parallelize |

---

## Concept Check

<details>
<summary><b>1. ทำไมต้อง profile ก่อน?</b></summary>

**Find actual bottleneck** — ไม่ใช่ guess
</details>

<details>
<summary><b>2. Memory bandwidth สำคัญไหม?</b></summary>

**มาก** — มักเป็น bottleneck หลักของ CFD
</details>

<details>
<summary><b>3. Virtual functions ช้าไหม?</b></summary>

**ใน tight loops ใช่** — batch operations ช่วยได้
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Expression Templates:** [02_Expression_Templates_Syntax.md](02_Expression_Templates_Syntax.md)