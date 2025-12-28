# HPC and Cloud - Overview

ภาพรวม HPC และ Cloud Computing

---

## Overview

> **HPC** = Run large CFD on clusters

---

## 1. Key Concepts

| Concept | Description |
|---------|-------------|
| Parallel | Multiple processors |
| MPI | Message passing |
| Cluster | Many nodes |
| Cloud | Remote resources |

---

## 2. Parallel Run

```bash
# Decompose
decomposePar

# Run
mpirun -np 16 simpleFoam -parallel

# Reconstruct
reconstructPar
```

---

## 3. HPC Job Script

```bash
#!/bin/bash
#SBATCH -n 64
#SBATCH -t 24:00:00

source /path/to/openfoam/etc/bashrc
mpirun simpleFoam -parallel
```

---

## 4. Module Contents

| File | Topic |
|------|-------|
| 01_Decomposition | Split mesh |
| 02_Monitoring | Track progress |
| 03_Optimization | Speed up |
| 04_HPC | Clusters |

---

## Quick Reference

| Task | Command |
|------|---------|
| Split | decomposePar |
| Run | mpirun -np N |
| Merge | reconstructPar |

---

## 🧠 Concept Check

<details>
<summary><b>1. MPI คืออะไร?</b></summary>

**Message Passing Interface** — communication between processors
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **Decomposition:** [01_Domain_Decomposition.md](01_Domain_Decomposition.md)