# HPC Integration

การ Integrate กับ HPC

---

## Overview

> Run OpenFOAM on **computing clusters**

---

## 1. Job Scheduler

| Scheduler | Command |
|-----------|---------|
| SLURM | sbatch |
| PBS | qsub |
| SGE | qsub |

---

## 2. SLURM Script

```bash
#!/bin/bash
#SBATCH --job-name=cfd
#SBATCH --nodes=2
#SBATCH --ntasks=64
#SBATCH --time=24:00:00

module load openfoam
mpirun simpleFoam -parallel
```

---

## 3. PBS Script

```bash
#!/bin/bash
#PBS -N cfd
#PBS -l select=2:ncpus=32
#PBS -l walltime=24:00:00

cd $PBS_O_WORKDIR
mpirun simpleFoam -parallel
```

---

## 4. Workflow

```bash
# 1. Prepare locally
decomposePar

# 2. Transfer
rsync -avz case/ cluster:project/

# 3. Submit
ssh cluster "cd project && sbatch run.sh"

# 4. Monitor
ssh cluster "squeue -u $USER"
```

---

## Quick Reference

| Scheduler | Submit | Check |
|-----------|--------|-------|
| SLURM | sbatch | squeue |
| PBS | qsub | qstat |

---

## Concept Check

<details>
<summary><b>1. Job scheduler ทำอะไร?</b></summary>

**Queue and manage** jobs on cluster
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)