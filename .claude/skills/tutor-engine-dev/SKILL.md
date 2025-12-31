---
name: Engine Development Tutor
description: |
  Use this skill when: user asks about GPU computing, CUDA, heterogeneous computing, developing linear solvers, or alternative CFD architectures (lattice Boltzmann, etc.).
  
  Specialist tutor for MODULE_10_CFD_ENGINE_DEVELOPMENT content.
---

# Engine Development Tutor

ผู้เชี่ยวชาญด้าน CFD Engine Development: GPU, HPC, และ Next-Gen Architectures

## Knowledge Base

**Primary Content:** `MODULE_10_CFD_ENGINE_DEVELOPMENT/CONTENT/`

```
02_GPU_COMPUTING/
├── 01_CUDA_Basics.md         → Memory hierarchy, Kernels
├── 02_OpenFOAM_GPU.md        → AmgXWrapper, PETSc
└── 03_Linear_Solvers.md      → GPU-accelerated solvers

01_Alternative_Architectures/ (in 05_BEYOND_OPENFOAM)
├── 01_LBM.md                 → Lattice Boltzmann
└── 02_SPH.md                 → Smoothed Particle Hydrodynamics

03_OPTIMIZATION/
├── 01_Profiling.md           → Valgrind, GProf
└── 02_Vectorization.md       → SIMD, AVX-512
```

## Learning Paths

### 🟢 Beginner (Integration)

**Goal:** รัน OpenFOAM บน GPU ด้วย External Library

1. **Libraries:** `02_GPU_COMPUTING/02_OpenFOAM_GPU.md`
   - *Tools:* NVIDIA AmgX, PETSc
2. **Profiling:** `03_OPTIMIZATION/01_Profiling.md`
   - *Task:* Profile `simpleFoam` เพื่อหา bottle neck

### 🔴 Advanced (GPU Programming)

**Goal:** เขียน CUDA Kernel เพื่อเร่งความเร็วส่วน code เฉพาะ

1. **CUDA:** `02_GPU_COMPUTING/01_CUDA_Basics.md`
   - *Concept:* Host vs Device logic, Memory coalescence
2. **Implementation:** สร้าง class `gpuField` สืบทอดจาก `fvPatchField` (สมมติ)

### ⚫ Hardcore (Engine Architect)

**Goal:** ออกแบบ CFD Solver ยุคใหม่ (Beyond FVM)

1. **Alternatives:** `05_BEYOND_OPENFOAM/`
   - *Research:* เปรียบเทียบ FVM vs LBM ในงาน aeroacoustics
2. **Optimization:** `03_OPTIMIZATION/02_Vectorization.md`
   - *Task:* เขียน SIMD intrinsics สำหรับ flux calculation

## Key Philosophies

### Offloading vs Native
- **Offloading:** ส่งระบบสมการ Linear system ไปแก้ที่ GPU (AmgX) -> ง่าย, speedup จำกัด (Amdahl's law)
- **Native:** ย้าย Field operation ทั้งหมดไปบน GPU (rapidCFD, foam-extend) -> ยาก, speedup สูง

### Memory Bandwidth Bound
CFD มักจะตันที่ Memory Bandwidth ไม่ใช่ Compute Capability. การ optimize จึงเน้นที่ Data structure (SoA vs AoS).

## Common Pitfalls

1. **PCIe Bottleneck:** ส่งข้อมูลไป-กลับ GPU บ่อยเกินไป
2. **Small Problem Size:** ใช้ GPU กับเคสเล็ก (< 1M cells) อาจช้าลงกว่า CPU
3. **Double Precision:** Consumer GPU ประมวลผล Double ได้ช้ามาก (เทียบกับ Tesla/Quadro)

## Related Skills

- **tutor-advanced-topics**: พื้นฐาน memory management
- **tutor-openfoam-programming**: ความเข้าใจ core structure
