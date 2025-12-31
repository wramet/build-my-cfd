# Phase 0: Project Overview

---

## Learning Objectives

By the end of this capstone project, you will be able to:

- Design and implement a complete OpenFOAM solver from scratch
- Apply the Finite Volume Method to solve heat transfer problems
- Develop custom boundary conditions and integrate turbulence models
- Optimize solver performance through profiling and parallelization
- Validate numerical results against analytical solutions
- Follow professional software development practices (version control, testing, documentation)

---

## 3W Overview

### What?
Build a complete incompressible heat transfer solver (`myHeatFoam`) starting from a 1D heat equation and progressively adding complexity: custom boundary conditions, turbulence modeling, parallel execution, and performance optimization.

### Why?
This project bridges theory and practice by requiring you to:
- **Apply all concepts** from Modules 1-9 in a unified, realistic implementation
- **Experience the full development lifecycle**: design → implement → test → optimize → document
- **Solve real engineering challenges** encountered by OpenFOAM developers daily
- **Build a portfolio piece** demonstrating your OpenFOAM proficiency to employers or collaborators

### How?
Through five progressive phases, each building on the previous:

```mermaid
flowchart LR
    P1[Phase 1: 1D Heat] --> P2[Phase 2: Custom BC]
    P2 --> P3[Phase 3: Turbulence]
    P3 --> P4[Phase 4: Parallel]
    P4 --> P5[Phase 5: Optimize]
    
    style P1 fill:#e1f5e1
    style P2 fill:#fff4e1
    style P3 fill:#ffe1f5
    style P4 fill:#e1f5ff
    style P5 fill:#f5e1e1
```

---

## Project Phases Overview

<details>
<summary>📊 Phase Summary Table</summary>

| Phase | Goal | Skills Acquired | Difficulty | Est. Time |
|:---:|:---|:---|:---:|:---:|
| **1** | Working 1D solver | Basic FVM, fvMatrix, time-stepping | ⭐⭐ | 4-6 hrs |
| **2** | Custom BC implementation | BC development, virtual functions | ⭐⭐⭐ | 4-6 hrs |
| **3** | Add k-ε turbulence | Turbulence modeling, coupled physics | ⭐⭐⭐⭐ | 6-8 hrs |
| **4** | MPI parallel execution | Domain decomposition, scaling | ⭐⭐⭐ | 4-6 hrs |
| **5** | 2x speedup optimization | Profiling, compiler optimizations | ⭐⭐⭐⭐ | 4-6 hrs |
| **Total** | **Complete solver** | **Full development lifecycle** | - | **22-32 hrs** |

</details>

---

## Prerequisites Checklist

Ensure you have completed these requirements before starting:

### Module Completion
- [ ] **Module 1-3**: OpenFOAM fundamentals, basic solver usage, C++ foundations
- [ ] **Module 4**: Boundary conditions and field manipulation
- [ ] **Module 5**: Advanced solver programming techniques
- [ ] **Module 6**: Multiphase/coupled physics understanding
- [ ] **Module 7**: Utilities, automation, and visualization tools
- [ ] **Module 8**: Testing, verification, and validation methodologies
- [ ] **Module 9**: Template programming, design patterns, memory management

### Technical Skills
- [ ] **Code Anatomy**: Read and understood solver walkthroughs (Module 10)
- [ ] **C++ Proficiency**: Comfortable with classes, inheritance, templates, pointers
- [ ] **OpenFOAM Environment**: `$WM_PROJECT_DIR` accessible and sourced
- [ ] **Development Tools**: Text editor, compiler, git (optional but recommended)

### Environment Setup
```bash
# Verify your OpenFOAM installation
echo $WM_PROJECT_DIR
# Expected output: /opt/openfoam/OpenFOAM-vXXX or similar

# Check compiler availability
which wclean
which wmake
# Both should return valid paths
```

---

## Development Environment Setup

### 1. Create Project Directory

```bash
# Navigate to your run directory
cd $FOAM_RUN

# Create project folder
mkdir -p myHeatFoam
cd myHeatFoam
```

### 2. Initialize from Template

```bash
# Copy laplacianFoam as starting point
cp -r $FOAM_SOLVERS/basic/laplacianFoam/* .

# Rename main file
mv laplacianFoam.C myHeatFoam.C
```

### 3. Configure Build System

**Create `Make/files`:**
```bash
cat > Make/files << 'EOF'
myHeatFoam.C

EXE = $(FOAM_USER_APPBIN)/myHeatFoam
EOF
```

**Create `Make/options`:**
```bash
cat > Make/options << 'EOF'
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude \
    -I$(LIB_SRC)/meshTools/lnInclude \
    -I$(LIB_SRC)/transportModels \
    -I$(LIB_SRC)/turbulenceModels

EXE_LIBS = \
    -lfiniteVolume \
    -lmeshTools
EOF
```

### 4. Test Compilation

```bash
# Clean and compile
wclean
wmake

# Expected output:
# wmake LnInclude myHeatFoam
# wmake linux64GccDPOpt myHeatFoam
# Source files
#     myHeatFoam.C
# ...
# ln: ../../lib/linux64GccDPOpt/libmyHeatFoam.so
# ln: ../../lib/linux64GccDPOpt/libmyHeatFoam.so
#    created symbolic link from ../../lib/linux64GccDPOpt/libmyHeatFoam.so to
#    ./libmyHeatFoam.so
```

---

## Final Project Structure

```
myHeatFoam/
├── Make/
│   ├── files                      # Source file list
│   └── options                    # Compilation flags
├── myHeatFoam.C                   # Main solver (all phases)
├── createFields.H                 # Field creation helper
├── myConvectiveBC/                # Custom BC (Phase 2)
│   ├── myConvectiveFvPatchScalarField.H
│   ├── myConvectiveFvPatchScalarField.C
│   └── Make/
│       ├── files
│       └── options
├── tutorials/
│   ├── 1D_diffusion/              # Phase 1: Basic verification
│   │   ├── 0/
│   │   ├── constant/
│   │   └── system/
│   ├── convective_cooling/        # Phase 2: BC testing
│   ├── turbulent_channel/         # Phase 3: Turbulence validation
│   └── parallel_channel/          # Phase 4-5: Scaling & optimization
└── README.md                      # Project documentation
```

---

## Phase-Specific Objectives

### Phase 1: 1D Heat Equation 🔥

**Governing Equation:**
$$\frac{\partial T}{\partial t} = \alpha \nabla^2 T$$

**Deliverables:**
- ✅ Working `myHeatFoam` solver for 1D conduction
- ✅ Analytical solution comparison (error < 1%)
- ✅ Grid convergence study (GCI calculation)
- ✅ Test case with proper boundary/initial conditions

**Success Criteria:**
- Solver compiles without errors
- Results match analytical solution within expected tolerance
- Code includes clear comments explaining FVM discretization

---

### Phase 2: Custom Boundary Condition 🌡️

**Governing Equation:**
$$q'' = h(T - T_\infty) \quad \text{(Convective cooling)}$$

**Deliverables:**
- ✅ `myConvectiveFvPatchScalarField` class implementation
- ✅ Compiled as shared library
- ✅ Test case demonstrating convective BC behavior
- ✅ Comparison with fixed temperature BC

**Success Criteria:**
- BC loads correctly at runtime
- Robin boundary condition properly implemented
- Heat flux matches expected values

---

### Phase 3: Add Turbulence 💨

**Governing Equation:**
$$\frac{\partial T}{\partial t} + \nabla \cdot (\mathbf{U} T) = \nabla \cdot \left(\frac{\nu_t}{Pr_t} + \alpha\right) \nabla T$$

**Deliverables:**
- ✅ Integrated k-ε turbulence model
- ✅ Turbulent channel flow test case
- ✅ Nusselt number calculation and validation
- �y Comparison with empirical correlations

**Success Criteria:**
- Turbulence model converges
- Nu number matches literature within 10%
- Proper near-wall treatment (y+ considerations)

---

### Phase 4: Parallelize 🖥️

**Implementation:**
```bash
decomposePar
mpirun -np 4 myHeatFoam -parallel
reconstructPar
```

**Deliverables:**
- ✅ Proper domain decomposition setup
- ✅ Scaling test (1, 2, 4, 8 CPUs)
- ✅ Speedup and efficiency analysis
- ✅ Load balancing verification

**Success Criteria:**
- Parallel runs produce identical results to serial
- Speedup > 1.5x on 4 cores
- Efficiency > 60% at 8 cores

---

### Phase 5: Optimize ⚡

**Goal:** 2x speedup over baseline

**Techniques:**
- Compiler optimizations (`-O3`, `-march=native`)
- Linear solver tuning (GAMG vs. PCG)
- Matrix assembly optimization
- Memory allocation reduction

**Deliverables:**
- ✅ Profiling results (`perf`, `valgrind`)
- ✅ Optimized solver settings
- ✅ Before/after performance comparison
- ✅ Final documentation

**Success Criteria:**
- Achieved 2x speedup or better
- No loss in solution accuracy
- Clear documentation of optimizations

---

## Evaluation Criteria

<details>
<summary>📋 Grading Rubric</summary>

| Criterion | Weight | Assessment Criteria |
|:---:|:---:|:---|
| **Correctness** | 40% | - Solver produces physically correct results<br>- Validated against analytical/empirical data<br>- Proper convergence behavior |
| **Code Quality** | 20% | - Follows OpenFOAM coding standards<br>- Clear comments and documentation<br>- Proper memory management<br>- Error handling |
| **Documentation** | 20% | - README with setup instructions<br>- Inline code comments<br>- Validation results documented<br>- Known limitations listed |
| **Performance** | 20% | - Meets optimization targets<br>- Efficient implementation<br>- Proper parallel scaling<br>- Profiling data provided |

</details>

---

## Troubleshooting

### Compilation Issues

**Problem:** `error: fvScalarMatrix was not declared`
```bash
# Solution: Verify Make/options includes finiteVolume
grep finiteVolume Make/options
# Should see: -lfiniteVolume
```

**Problem:** Undefined reference to turbulence models
```bash
# Solution: Add turbulence libraries to Make/options
EXE_LIBS += -lturbulenceModels -lincompressibleTurbulenceModels
```

### Runtime Issues

**Problem:** Segmentation fault on startup
```bash
# Debug with gdb
gdb --args myHeatFoam
(gdb) run
(gdb) backtrace  # Check crash location
```

**Problem:** BC not recognized
```bash
# Verify library path in controlDict
libs ("libmyConvectiveBC.so");
```

---

## Support Resources

### Official Documentation
- **OpenFOAM User Guide:** `$FOAM_DOC/Guides/UserGuide.pdf`
- **Programmer's Guide:** `$FOAM_DOC/Guides/ProgrammersGuide.pdf`
- **Doxygen API:** https://www.openfoam.com/documentation/api-guide

### Code References
- **Source Code:** `$FOAM_SRC` (all OpenFOAM classes)
- **Example Solvers:** `$FOAM_SOLVERS` (reference implementations)
- **Tutorials:** `$FOAM_TUTORIALS` (case setup examples)

### Community
- **OpenFOAM Forum:** https://discourse.openfoam.com
- **CFD Online:** https://www.cfd-online.com/Forums/openfoam
- **Wiki:** https://openfoamwiki.net

### Module References
- Review **Module 10, Section 1 (Code Anatomy)** for detailed solver walkthroughs
- Consult **Module 9, Section 7 (Practical Project)** for additional implementation guidance

---

## Key Takeaways

After completing this capstone project, you will have:

✅ **End-to-End Development Experience**: Designed, implemented, tested, and optimized a complete OpenFOAM solver from scratch

✅ **Deep Understanding of FVM**: Applied finite volume discretization to real heat transfer problems with hands-on implementation

✅ **Professional Development Practices**: Used version control, wrote documentation, performed validation, and optimized performance

✅ **Customization Skills**: Developed custom boundary conditions, integrated turbulence models, and extended OpenFOAM functionality

✅ **Parallel Computing Expertise**: Implemented domain decomposition and analyzed scaling behavior on multi-core systems

✅ **Portfolio-Ready Project**: A complete, validated solver with documentation demonstrating your OpenFOAM proficiency

✅ **Problem-Solving Mindset**: Encountered and resolved real debugging, compilation, and numerical challenges faced by CFD developers

✅ **Foundation for Advanced Work**: Skills transferable to developing custom multiphase, reacting, or specialized physics solvers

---

## Next Steps

Ready to begin? Start with **[Phase 1: 1D Heat Equation](01_Phase1_1D_Heat_Equation.md)**

> **Pro Tip:** Create a git repository before starting Phase 1 to track your progress and enable experimentation without fear of breaking working code.
> ```bash
> git init
> git add .
> git commit -m "Initial project setup from template"
> ```