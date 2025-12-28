# Performance Monitoring

การ Monitor Performance

---

## Overview

> **Monitor** parallel simulations for efficiency

---

## 1. Basic Timing

```bash
time mpirun -np 4 simpleFoam -parallel
```

---

## 2. Log Analysis

```bash
# Get execution time
grep 'ExecutionTime' log.simpleFoam | tail -5

# Clock time
grep 'ClockTime' log.simpleFoam | tail -1
```

---

## 3. Residual Monitoring

```bash
# Extract residuals
foamLog log.simpleFoam

# Plot
gnuplot -e "plot 'logs/p_0' w l; pause -1"
```

---

## 4. Load Balance

```bash
# Check per-processor time
for p in processor*/; do
    grep ExecutionTime $p/log.* | tail -1
done
```

---

## 5. Memory

```bash
/usr/bin/time -v mpirun -np 4 solver
# Look for "Maximum resident set size"
```

---

## Quick Reference

| Metric | Check |
|--------|-------|
| Time | grep ExecutionTime |
| Residuals | foamLog |
| Memory | /usr/bin/time -v |

---

## Concept Check

<details>
<summary><b>1. Load balance ดีแค่ไหน?</b></summary>

**< 10% difference** between processors
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)