# MODULE 10: CFD Engine Development

**ระดับ:** Advanced (ต้องผ่าน Module 01-09 ก่อน)

---

## 🎯 เป้าหมาย

> เตรียมความพร้อมให้คุณสามารถ **เขียน CFD Solver ของตัวเอง** ได้

---

## 📚 เนื้อหา

### 01 — Code Anatomy
ผ่าโค้ด OpenFOAM ทีละบรรทัด

| File | Topic |
|:---|:---|
| [icoFoam Walkthrough](CONTENT/01_CODE_ANATOMY/01_icoFoam_Walkthrough.md) | Incompressible NS Solver |
| [simpleFoam Walkthrough](CONTENT/01_CODE_ANATOMY/02_simpleFoam_Walkthrough.md) | Steady-State SIMPLE |
| [kEpsilon Anatomy](CONTENT/01_CODE_ANATOMY/03_kEpsilon_Model_Anatomy.md) | Turbulence Model |
| [fvMatrix Deep Dive](CONTENT/01_CODE_ANATOMY/04_fvMatrix_Deep_Dive.md) | Matrix Assembly |

---

### 02 — Advanced Patterns
Design Patterns ที่ซ่อนอยู่ใน OpenFOAM

| File | Pattern |
|:---|:---|
| [Strategy in fvSchemes](CONTENT/02_ADVANCED_PATTERNS/01_Strategy_in_fvSchemes.md) | Swappable Algorithms |
| [Template Method](CONTENT/02_ADVANCED_PATTERNS/02_Template_Method_Pattern.md) | turbulenceModel::correct() |
| [Singleton MeshObject](CONTENT/02_ADVANCED_PATTERNS/03_Singleton_MeshObject.md) | Caching Mechanism |
| [Visitor Pattern](CONTENT/02_ADVANCED_PATTERNS/04_Visitor_Pattern.md) | Field Operations |
| [CRTP Pattern](CONTENT/02_ADVANCED_PATTERNS/05_CRTP_Pattern.md) | Compile-time Polymorphism |

---

### 03 — Performance Engineering
ทำให้ CFD Code เร็วขึ้น

| File | Topic |
|:---|:---|
| [Profiling Tools](CONTENT/03_PERFORMANCE_ENGINEERING/01_Profiling_Tools.md) | gprof, perf, valgrind |
| [Memory Layout & Cache](CONTENT/03_PERFORMANCE_ENGINEERING/02_Memory_Layout_Cache.md) | Cache-aware Programming |
| [Loop Optimization](CONTENT/03_PERFORMANCE_ENGINEERING/03_Loop_Optimization.md) | Vectorization, SIMD |
| [Parallel Scaling](CONTENT/03_PERFORMANCE_ENGINEERING/04_Parallel_Scaling.md) | MPI Efficiency |

---

### 04 — Capstone Project
สร้าง Heat Transfer Solver ตั้งแต่ศูนย์

| Phase | Outcome |
|:---|:---|
| [Phase 1: 1D Heat](CONTENT/04_CAPSTONE_PROJECT/01_Phase1_1D_Heat_Equation.md) | Basic Solver |
| [Phase 2: Custom BC](CONTENT/04_CAPSTONE_PROJECT/02_Phase2_Custom_BC.md) | Convective BC |
| [Phase 3: Turbulence](CONTENT/04_CAPSTONE_PROJECT/03_Phase3_Turbulence_Model.md) | Add k-ε |
| [Phase 4: Parallel](CONTENT/04_CAPSTONE_PROJECT/04_Phase4_Parallelization.md) | MPI Decomposition |
| [Phase 5: Optimize](CONTENT/04_CAPSTONE_PROJECT/05_Phase5_Optimization.md) | 2x Speedup |

---

### 05 — Beyond OpenFOAM
มองไปข้างหน้า

| File | Topic |
|:---|:---|
| [Alternative Frameworks](CONTENT/05_BEYOND_OPENFOAM/01_Alternative_Architectures.md) | SU2, Nektar++, PyFR |
| [GPU Computing](CONTENT/05_BEYOND_OPENFOAM/02_GPU_Computing.md) | CUDA, OpenCL, Kokkos |
| [Modern C++](CONTENT/05_BEYOND_OPENFOAM/03_Modern_Cpp_for_CFD.md) | C++17/20 Features |

---

## 🚀 Learning Path

```mermaid
flowchart LR
    A[Module 01-09] --> B[Code Anatomy]
    B --> C[Advanced Patterns]
    C --> D[Performance]
    D --> E[Capstone Project]
    E --> F[Beyond OpenFOAM]
    F --> G[Write Your Own Engine!]
```

---

## ⏱️ Estimated Time

| Section | Hours |
|:---|:---:|
| Code Anatomy | 8-10 |
| Advanced Patterns | 6-8 |
| Performance | 6-8 |
| Capstone Project | 15-20 |
| Beyond OpenFOAM | 4-6 |
| **Total** | **40-50** |
