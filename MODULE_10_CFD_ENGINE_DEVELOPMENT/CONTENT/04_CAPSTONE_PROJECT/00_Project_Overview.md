# Capstone Project — Build Your Own Solver

สร้าง Heat Transfer Solver ตั้งแต่ศูนย์

---

## Project Goal

> **สร้าง Incompressible Heat Transfer Solver ที่ทำงานได้จริง**
>
> ตั้งแต่ 1D Heat Equation ไปจนถึง Parallel Turbulent Flow

---

## Why This Project?

1. **Hands-on experience:** ไม่ใช่แค่อ่าน — ต้องเขียนเอง!
2. **Full cycle:** Design → Implement → Test → Optimize
3. **Real challenges:** เจอปัญหาเหมือนนักพัฒนาจริง
4. **Portfolio:** ผลงานที่แสดงความสามารถได้

---

## Project Phases

```mermaid
flowchart LR
    P1[Phase 1: 1D Heat] --> P2[Phase 2: Custom BC]
    P2 --> P3[Phase 3: Turbulence]
    P3 --> P4[Phase 4: Parallel]
    P4 --> P5[Phase 5: Optimize]
```

| Phase | Goal | Skills |
|:---|:---|:---|
| **1** | Working 1D solver | Basic FVM, fvMatrix |
| **2** | Custom BC | BC development |
| **3** | Add k-ε | Turbulence modeling |
| **4** | MPI parallel | Domain decomposition |
| **5** | 2x speedup | Profiling, optimization |

---

## Prerequisites

- [x] Module 01-09 completed
- [x] Code Anatomy section read
- [x] OpenFOAM dev environment set up
- [x] Basic C++ proficiency

---

## Development Environment

```bash
# Check OpenFOAM environment
echo $WM_PROJECT_DIR

# Create project directory
mkdir -p $FOAM_RUN/myHeatFoam
cd $FOAM_RUN/myHeatFoam

# Copy template
cp -r $FOAM_SOLVERS/basic/laplacianFoam/* .
mv laplacianFoam.C myHeatFoam.C
```

---

## Project Structure (Final)

```
myHeatFoam/
├── Make/
│   ├── files
│   └── options
├── myHeatFoam.C                    # Main solver
├── createFields.H                  # Field creation
├── myConvectiveBC/                 # Custom BC (Phase 2)
│   ├── myConvectiveFvPatchScalarField.H
│   └── myConvectiveFvPatchScalarField.C
└── tutorials/
    ├── 1D_diffusion/               # Phase 1 test case
    ├── convective_cooling/         # Phase 2 test case
    ├── turbulent_channel/          # Phase 3 test case
    └── parallel_channel/           # Phase 4 test case
```

---

## Phases Overview

### Phase 1: 1D Heat Equation

$$\frac{\partial T}{\partial t} = \alpha \nabla^2 T$$

**Deliverables:**
- Working solver
- Comparison with analytical solution
- Grid convergence study

---

### Phase 2: Custom Boundary Condition

$$q'' = h(T - T_\infty)$$ (Convective BC)

**Deliverables:**
- `myConvectiveFvPatchScalarField` class
- Compiled as library
- Test case validation

---

### Phase 3: Add Turbulence

$$\frac{\partial T}{\partial t} + \nabla \cdot (\mathbf{U} T) = \nabla \cdot \left(\frac{\nu_t}{Pr_t} + \alpha\right) \nabla T$$

**Deliverables:**
- Integrated k-ε model
- Turbulent heat transfer case
- Nusselt number validation

---

### Phase 4: Parallelize

**Deliverables:**
- Parallel decomposition
- Scaling test (1, 2, 4, 8 CPUs)
- Efficiency analysis

---

### Phase 5: Optimize

**Goal:** 2x speedup over baseline

**Deliverables:**
- Profiling results
- Optimized settings
- Before/after comparison

---

## Evaluation Criteria

| Criterion | Weight |
|:---|:---:|
| **Correctness** | 40% |
| **Code Quality** | 20% |
| **Documentation** | 20% |
| **Performance** | 20% |

---

## Getting Started

```bash
# Clone starter template
cd $FOAM_RUN
mkdir myHeatFoam && cd myHeatFoam

# Create Make/files
cat > Make/files << 'EOF'
myHeatFoam.C
EXE = $(FOAM_USER_APPBIN)/myHeatFoam
EOF

# Create Make/options
cat > Make/options << 'EOF'
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude \
    -I$(LIB_SRC)/meshTools/lnInclude

EXE_LIBS = \
    -lfiniteVolume \
    -lmeshTools
EOF
```

---

## Timeline Suggestion

| Phase | Estimated Time |
|:---|:---:|
| Phase 1 | 4-6 hours |
| Phase 2 | 4-6 hours |
| Phase 3 | 6-8 hours |
| Phase 4 | 4-6 hours |
| Phase 5 | 4-6 hours |
| **Total** | **22-32 hours** |

---

## Support Resources

- OpenFOAM Wiki: `openfoamwiki.net`
- Source code: `$FOAM_SRC`
- Example solvers: `$FOAM_SOLVERS`
- This module's Code Anatomy section

---

## ถัดไป

เริ่มต้นที่ [Phase 1: 1D Heat Equation](01_Phase1_1D_Heat_Equation.md)
