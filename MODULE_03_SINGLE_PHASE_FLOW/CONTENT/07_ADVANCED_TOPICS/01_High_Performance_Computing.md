# High-Performance Computing

การประมวลผลสมรรถนะสูงสำหรับ OpenFOAM

---

## Overview

OpenFOAM ใช้ **MPI** (Message Passing Interface) สำหรับ parallel computing:

1. **Decompose** — แบ่ง mesh เป็น subdomains
2. **Run** — รันแบบ parallel ด้วย `mpirun`
3. **Reconstruct** — รวมผลลัพธ์กลับมา

---

## 1. Domain Decomposition

### How It Works

```
Serial Mesh → Decompose → Parallel Execution → Reconstruct

    Original Domain
    ┌─────────────────────────────────────┐
    │                                     │
    │         Single Large Mesh           │
    │         (10 million cells)          │
    │                                     │
    └─────────────────────────────────────┘
                   ↓ decomposePar
    ┌─────────┬─────────┬─────────┬─────────┐
    │ Proc 0  │ Proc 1  │ Proc 2  │ Proc 3  │
    │         │         │         │         │
    │  2.5M   │  2.5M   │  2.5M   │  2.5M   │
    │ cells   │ cells   │ cells   │ cells  │
    │         │         │         │         │
    │  Mesh   │  Mesh   │  Mesh   │  Mesh  │
    │  Zone 0 │  Zone 1 │  Zone 2 │  Zone 3 │
    └─────────┴─────────┴─────────┴─────────┘
                   ↓ mpirun -np 4
         [Parallel Solving on 4 Cores]
                   ↓ reconstructPar
    ┌─────────────────────────────────────┐
    │                                     │
    │         Reconstructed Results       │
    │                                     │
    └─────────────────────────────────────┘
```

### Processor Communication

```
    Proc 0        Proc 1        Proc 2        Proc 3
    ┌───────┐    ┌───────┐    ┌───────┐    ┌───────┐
    │       │    │       │    │       │    │       │
    │  ...  │◄──►│  ...  │◄──►│  ...  │◄──►│  ...  │
    │       │    │       │    │       │    │       │
    └───────┘    └───────┘    └───────┘    └───────┘
       │            │            │            │
       └────────────┴────────────┴────────────┘
                    MPI Communication
              (Data exchange at boundaries)
```

### decomposeParDict

```cpp
// system/decomposeParDict
numberOfSubdomains  16;       // จำนวน processors

method              scotch;   // แนะนำสำหรับ load balance ดี
// หรือ: simple, metis, hierarchical, manual

// Optional constraints
constraints
{
    preservePatches
    {
        type    preservePatches;
        patches (inlet outlet);
    }
}
```

### Decomposition Methods

| Method | Load Balance | Use Case |
|--------|-------------|----------|
| `simple` | ต่ำ | Uniform mesh, structured |
| `scotch` | ดี | ทั่วไป (แนะนำ) |
| `metis` | ดี | ทางเลือกจาก scotch |
| `hierarchical` | ปานกลาง | Multi-level |
| `manual` | กำหนดเอง | พิเศษ |

### Commands

```bash
# Decompose
decomposePar

# Check decomposition
decomposePar -debug

# Clean decomposition
rm -rf processor*
```

---

## 2. Parallel Execution

### mpirun

```bash
# Local machine
mpirun -np 16 simpleFoam -parallel > log.simpleFoam &

# Cluster with hostfile
mpirun -np 64 --hostfile hosts simpleFoam -parallel

# Check running
tail -f log.simpleFoam
```

### hostfile Format

```
# hosts file
node1 slots=16
node2 slots=16
node3 slots=16
node4 slots=16
```

---

## 3. Reconstruction

```bash
# Reconstruct all time steps
reconstructPar

# Latest time only (เร็วกว่า)
reconstructPar -latestTime

# Specific time range
reconstructPar -time 0.5:1.0
```

---

## 4. Linear Solvers (Parallel)

### fvSolution Settings

```cpp
// system/fvSolution
solvers
{
    p
    {
        solver          GAMG;              // Multigrid (best for p)
        preconditioner  GAMG;
        tolerance       1e-6;
        relTol          0.01;
        smoother        GaussSeidel;
        nPreSweeps      0;
        nPostSweeps     2;
        cacheAgglomeration on;
    }
    
    U
    {
        solver          PBiCGStab;         // Non-symmetric
        preconditioner  DILU;
        tolerance       1e-5;
        relTol          0.1;
    }
    
    "(k|epsilon|omega)"
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-5;
        relTol          0.1;
    }
}
```

### Solver Selection

| Variable | Solver | Preconditioner |
|----------|--------|----------------|
| Pressure (p) | GAMG | GAMG |
| Velocity (U) | PBiCGStab | DILU |
| Turbulence | smoothSolver | symGaussSeidel |
| Scalars | smoothSolver | DILU/DIC |

---

## 5. Load Balancing

### Check Load Balance

```bash
# Count cells per processor
for proc in processor*; do
    cells=$(grep nCells $proc/constant/polyMesh/owner | head -1 | awk '{print $2}')
    echo "$proc: $cells cells"
done
```

### Imbalance Metric

$$\mathcal{I} = \frac{W_{max} - W_{avg}}{W_{avg}}$$

| $\mathcal{I}$ | Quality |
|---------------|---------|
| < 0.1 | Excellent |
| 0.1 - 0.2 | Good |
| > 0.2 | Needs improvement |

---

## 6. Memory & Performance

### Estimate Memory

```
Memory ≈ (nCells × 50 bytes) × nFields × 2
```

| Cells | Fields | Estimated RAM |
|-------|--------|---------------|
| 1M | 10 | ~1 GB |
| 10M | 10 | ~10 GB |
| 100M | 10 | ~100 GB |

### Optimal Cells per Core

- **RANS:** 50,000 - 200,000 cells/core
- **LES:** 10,000 - 50,000 cells/core
- **DNS:** 1,000 - 10,000 cells/core

---

## 7. Parallel Workflow Summary

```mermaid
flowchart LR
    A[Serial Case] --> B[decomposePar]
    B --> C[mpirun solver -parallel]
    C --> D[reconstructPar]
    D --> E[paraFoam]
```

### Complete Example

```bash
#!/bin/bash
# parallel_run.sh

# Settings
NP=16
SOLVER=simpleFoam

# Pre-processing
blockMesh
checkMesh

# Decompose
decomposePar

# Run parallel
mpirun -np $NP $SOLVER -parallel > log.$SOLVER 2>&1 &

# Monitor
tail -f log.$SOLVER

# Post-processing (after completion)
reconstructPar -latestTime
paraFoam
```

---

## Concept Check

<details>
<summary><b>1. ทำไม scotch ดีกว่า simple สำหรับ mesh ทั่วไป?</b></summary>

`scotch` ใช้ graph-based partitioning ที่พิจารณา mesh connectivity จริง ทำให้ได้ load balance ดีกว่าและ communication ระหว่าง processor น้อยกว่า — `simple` แบ่งทาง geometric ธรรมดาซึ่งอาจทำให้ processor บางตัวมี cells มากกว่าตัวอื่น
</details>

<details>
<summary><b>2. เมื่อไหร่ใช้ GAMG vs PBiCGStab?</b></summary>

- **GAMG:** สำหรับ pressure equation (elliptic, symmetric) — มี optimal O(n) complexity
- **PBiCGStab:** สำหรับ momentum equation (non-symmetric) — ต้องการ less memory
</details>

<details>
<summary><b>3. จะรู้ได้อย่างไรว่าใช้ cores มากเกินไป?</b></summary>

เมื่อ cells per core < 10,000 หรือเมื่อ speedup ไม่เพิ่มเมื่อเพิ่ม cores — communication overhead จะกินเวลาที่ประหยัดได้จาก calculation
</details>

---

## Related Documents

- **บทก่อนหน้า:** [00_Overview.md](00_Overview.md)
- **บทถัดไป:** [02_Advanced_Turbulence.md](02_Advanced_Turbulence.md)