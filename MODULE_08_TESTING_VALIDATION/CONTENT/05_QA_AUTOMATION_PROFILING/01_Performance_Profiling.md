# Performance Profiling

การ Profile ประสิทธิภาพ

---

## Overview

> **Profiling** = Find where time is spent

---

## 1. Basic Timing

```bash
# Wall clock time
time simpleFoam > log

# OpenFOAM profiling
system/controlDict:
profiling yes;
```

---

## 2. Function Profiling

```cpp
// In controlDict
profiling
{
    active  true;
    cpuInfo true;
    memInfo true;
    sysInfo true;
}
```

---

## 3. Linux Tools

### perf

```bash
# Record
perf record -g simpleFoam

# Report
perf report

# Top functions
perf top
```

### gprof

```bash
# Compile with -pg
wmake CFLAGS=-pg

# Run
./simpleFoam

# Analyze
gprof simpleFoam gmon.out > profile.txt
```

---

## 4. Memory Profiling

```bash
# Peak memory
/usr/bin/time -v simpleFoam

# Detailed
valgrind --tool=massif simpleFoam
ms_print massif.out.* | less
```

---

## 5. Parallel Profiling

```bash
# MPI profiling
mpirun -np 4 simpleFoam -parallel

# Check load balance
grep 'Time = ' log.simpleFoam | tail -20
```

---

## 6. Common Bottlenecks

| Bottleneck | Solution |
|------------|----------|
| Linear solver | Better preconditioner |
| I/O | Reduce write frequency |
| Memory | Reduce stored fields |
| Load imbalance | Better decomposition |

---

## Quick Reference

| Tool | Use |
|------|-----|
| `time` | Wall clock |
| `perf` | CPU profiling |
| `valgrind` | Memory |
| `profiling` | OpenFOAM internal |

---

## Concept Check

<details>
<summary><b>1. ทำไมต้อง profile?</b></summary>

**Find actual bottleneck** — ไม่ใช่ guess
</details>

<details>
<summary><b>2. Linear solver มักช้าไหม?</b></summary>

**ใช่** — often 60-90% of runtime
</details>

<details>
<summary><b>3. Load imbalance คืออะไร?</b></summary>

**Processors wait** — บางตัวทำงานมากกว่า
</details>

---

## Related Documents

- **ภาพรวม:** [../05_QA_AUTOMATION_PROFILING/00_Overview.md](../05_QA_AUTOMATION_PROFILING/00_Overview.md)
- **Regression:** [02_Regression_Testing.md](02_Regression_Testing.md)