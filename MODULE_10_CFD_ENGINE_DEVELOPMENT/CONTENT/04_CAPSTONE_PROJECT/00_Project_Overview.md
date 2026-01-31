# Phase 0: Project Overview (R410A Evaporator Focus)

---

## Learning Objectives

By the end of this capstone project, you will be able to:

- Design and implement a complete OpenFOAM solver for **R410A evaporator simulation**
- Apply the Finite Volume Method to solve **two-phase flow with phase change**
- Develop **custom boundary conditions** for tube heat transfer and evaporation
- Integrate **VOF method** and **phase change models** for liquid-vapor interfaces
- Optimize solver performance for **conjugate heat transfer** in evaporator tubes
- Validate numerical results against **experimental evaporator data**
- Follow professional software development practices (version control, testing, documentation)

---

## 3W Overview

### What?
Build a complete **R410A evaporator solver** (`myEvaporatorFoam`) starting from a 1D tube heat transfer and progressively adding complexity: two-phase VOF modeling, phase change implementation, custom tube wall heat transfer, parallel execution, and performance optimization for evaporator tubes.

### Why?
This project bridges theory and practice by requiring you to:
- **Apply all concepts** from Modules 1-9 to a **real R410A evaporator** engineering problem
- **Experience the full development lifecycle**: design → implement → test → optimize → document for multiphase flow
- **Solve real engineering challenges** in refrigeration systems: phase change, tube flow, and conjugate heat transfer
- **Build a portfolio piece** demonstrating expertise in **industrial-scale CFD simulation** for HVAC applications

### How?
Through five progressive phases, each building on the previous:

```mermaid
flowchart LR
    P1[Phase 1: 1D Tube Heat] --> P2[Phase 2: Evap BC]
    P2 --> P3[Phase 3: Two-Phase VOF]
    P3 --> P4[Phase 4: Phase Change]
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
<summary>📊 Phase Summary Table (R410A Evaporator Focus)</summary>

| Phase | Goal | Skills Acquired | Difficulty | Est. Time |
|:---:|:---|:---|:---:|:---:|
| **1** | 1D tube heat transfer | Basic FVM, tube geometry, heat transfer | ⭐⭐ | 4-6 hrs |
| **2** | Evaporation boundary conditions | Wall heat flux, tube BCs, evaporation modeling | ⭐⭐⭐ | 4-6 hrs |
| **3** | Two-phase VOF implementation | Interface tracking, multiphase coupling | ⭐⭐⭐⭐ | 6-8 hrs |
| **4** | Phase change models | Schnerr-Sauer, Lee evaporation models | ⭐⭐⭐⭐ | 6-8 hrs |
| **5** | Conjugate heat transfer optimization | Solid-fluid coupling, parallel scaling | ⭐⭐⭐⭐ | 4-6 hrs |
| **Total** | **R410A evaporator solver** | **Multiphase development lifecycle** | - | **24-34 hrs** |

</details>

---

## Prerequisites Checklist

Ensure you have completed these requirements before starting:

### Module Completion
- [ ] **Module 1-3**: OpenFOAM fundamentals, basic solver usage, C++ foundations
- [ ] **Module 4**: Boundary conditions and field manipulation
- [ ] **Module 5**: Advanced solver programming techniques
- [ ] **Module 6**: **Multiphase/coupled physics understanding** (critical for two-phase)
- [ ] **Module 7**: Utilities, automation, and visualization tools
- [ ] **Module 8**: Testing, verification, and validation methodologies
- [ ] **Module 9**: Template programming, design patterns, memory management
- [ ] **Module 10**: Custom solver development for multiphase flows

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
mkdir -p myEvaporatorFoam
cd myEvaporatorFoam
```

### 2. Initialize from Template

```bash
# Copy multiphaseInterFoam as starting point (for VOF)
cp -r $FOAM_SOLVERS/multiphase/multiphaseInterFoam/* .

# Rename main file
mv multiphaseInterFoam.C myEvaporatorFoam.C
```

### 3. Configure Build System

**Create `Make/files`:**
```bash
cat > Make/files << 'EOF'
myEvaporatorFoam.C

EXE = $(FOAM_USER_APPBIN)/myEvaporatorFoam
EOF
```

**Create `Make/options`:**
```bash
cat > Make/options << 'EOF'
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude \
    -I$(LIB_SRC)/meshTools/lnInclude \
    -I$(LIB_SRC)/transportModels \
    -I$(LIB_SRC)/multiphase/lnInclude \
    -I$(LIB_SRC)/thermophysicalModels/lnInclude \
    -I$(LIB_SRC)/turbulenceModels

EXE_LIBS = \
    -lfiniteVolume \
    -lmeshTools \
    -lmultiphaseEuler \
    -lcompressibleMultiphaseMomentum \
    -lthermophysicalModels \
    -lturbulenceModels
EOF
```

### 4. Test Compilation

```bash
# Clean and compile
wclean
wmake

# Expected output:
# wmake LnInclude myEvaporatorFoam
# wmake linux64GccDPOpt myEvaporatorFoam
# Source files
#     myEvaporatorFoam.C
# ...
# ln: ../../lib/linux64GccDPOpt/libmyEvaporatorFoam.so
# ln: ../../lib/linux64GccDPOpt/libmyEvaporatorFoam.so
#    created symbolic link from ../../lib/linux64GccDPOpt/libmyEvaporatorFoam.so to
#    ./libmyEvaporatorFoam.so
```

---

## Final Project Structure (R410A Evaporator)

```
myEvaporatorFoam/
├── Make/
│   ├── files                      # Source file list
│   └── options                    # Compilation flags
├── myEvaporatorFoam.C             # Main solver (all phases)
├── createFields.H                 # Field creation helper (R410A properties)
├── myTubeWallBC/                  # Custom tube wall BC (Phase 2)
│   ├── myTubeWallFvPatchVectorField.H
│   ├── myTubeWallFvPatchVectorField.C
│   └── Make/
│       ├── files
│       └── options
├── tutorials/
│   ├── 1D_tube/                   # Phase 1: Basic tube heat transfer
│   │   ├── 0/
│   │   ├── constant/
│   │   └── system/
│   ├── evaporator_test/           # Phase 2: Evaporation BC testing
│   ├── two_phase_tube/            # Phase 3: VOF interface tracking
│   ├── phase_change_tube/         # Phase 4: Evaporation modeling
│   └── evaporator_validation/    # Phase 5: Conjugate heat transfer
├── R410A_properties/              # Property tables and models
│   ├── transportProperties         # R410A thermophysical properties
│   ├── phaseChangeModels          # Schnerr-Sauer, Lee models
│   └── saturationTables          # Saturation property data
└── README.md                      # Project documentation
```

---

## Phase-Specific Objectives

### Phase 1: 1D Tube Heat Transfer 🔥

**Governing Equation:**
$$\rho c_p \frac{\partial T}{\partial t} = \frac{1}{r}\frac{\partial}{\partial r}\left(k r \frac{\partial T}{\partial r}\right)$$

**Deliverables:**
- ✅ Working `myEvaporatorFoam` solver for 1D cylindrical heat conduction
- ✅ Analytical solution comparison for tube wall heat transfer (error < 1%)
- ✅ Grid convergence study for cylindrical coordinates
- ✅ Test case with tube geometry and wall heat flux boundary conditions

**Success Criteria:**
- Solver compiles with multiphase libraries
- Results match cylindrical heat conduction analytical solution
- Code includes proper cylindrical coordinate discretization

---

### Phase 2: Evaporation Boundary Conditions 🌡️

**Governing Equation:**
$$q''_{wall} = h_{tp}(T_{wall} - T_{sat}) \quad \text{(Two-phase heat transfer)}$$

**Deliverables:**
- ✅ `myTubeWallFvPatchVectorField` class implementation for tube walls
- ✅ R410A saturation temperature property lookup
- ✅ Test case demonstrating evaporation BC behavior
- ✅ Comparison with empirical heat transfer correlations

**Success Criteria:**
- BC loads correctly with multiphase solver
- Two-phase heat transfer coefficient properly implemented
- Wall temperature matches expected evaporation behavior

---

### Phase 3: Two-Phase VOF Implementation 💨

**Governing Equation:**
$$\frac{\partial \alpha}{\partial t} + \nabla \cdot (\mathbf{U} \alpha) = 0$$

**Deliverables:**
- ✅ VOF interface tracking implementation
- ✅ R410A liquid-vapor interface capturing
- ✅ Tube geometry with proper boundary conditions
- ✅ Validation against analytical bubble rise velocity

**Success Criteria:**
- VOF equation converges for tube flow
- Interface sharpness maintained (no numerical diffusion)
- Mass conservation error < 0.1%

---

### Phase 4: Phase Change Modeling 🔥

**Implementation:**
Schnerr-Sauer cavitation model:
$$\dot{m} = \rho_l \rho_v \frac{\alpha_v (1-\alpha_l)}{\rho_l} \sqrt{\frac{2}{3} \frac{|p_v - p|}{\rho_l}}$$

**Deliverables:**
- ✅ Schnerr-Sauer phase change model implementation
- ✅ R410A vapor pressure model
- ✅ Mass transfer source terms in VOF equation
- ✅ Evaporation rate validation against data

**Success Criteria:**
- Phase change model converges with VOF
- Evaporation rate matches experimental data within 15%
- Interface behavior matches expected evaporator flow patterns

---

### Phase 5: Conjugate Heat Transfer Optimization 🔥🌡️

**Implementation:**
Coupled solid-fluid heat transfer:
$$-k_s \nabla T_s \cdot \mathbf{n} = k_f \nabla T_f \cdot \mathbf{n} \quad \text{at interface}$$

**Deliverables:**
- ✅ Conjugate heat transfer between tube wall and refrigerant
- ✅ R410A property tables integration
- ✅ Parallel scaling for large evaporator meshes
- ✅ Validation against experimental evaporator performance

**Success Criteria:**
- Conjugate heat transfer converges
- Heat transfer coefficient within 10% of experimental data
- Achieve 2x speedup with parallelization
- Quality distribution matches evaporator measurements

---

## Evaluation Criteria

<details>
<summary>📋 Grading Rubric</summary>

| Criterion | Weight | Assessment Criteria |
|:---:|:---:|:---|
| **Correctness** | 35% | - Solver produces physically correct two-phase results<br>- Validated against evaporator experimental data<br>- Proper mass/energy conservation<br>- Accurate interface tracking |
| **R410A Physics** | 20% | - Proper phase change modeling<br>- Correct thermodynamic properties<br>- Accurate heat transfer coefficients<br>- Realistic evaporator flow patterns |
| **Code Quality** | 20% | - Follows OpenFOAM coding standards<br>- Clear comments and documentation<br>- Proper multiphase memory management<br>- Error handling for VOF convergence |
| **Documentation** | 15% | - README with evaporator setup instructions<br>- R410A property documentation<br>- Validation results against experimental data<br>- Known limitations for industrial use |
| **Performance** | 10% | - Meets optimization targets for evaporator cases<br>- Efficient VOF implementation<br>- Proper parallel scaling for large meshes<br>- Profiling data provided |

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
- Review **Module 10, Section 1 (Code Anatomy)** for detailed multiphase solver walkthroughs
- Consult **Module 1-3, Section 5 (Two-Phase Flow)** for R410A properties
- Reference **Module 6, Section 2 (VOF Method)** for interface tracking implementation
- Use **Module 8, Section 3 (Evaporator Validation)** for experimental data comparison

---

## Key Takeaways

After completing this capstone project, you will have:

✅ **R410A Evaporator Expertise**: Built a complete solver for industrial refrigeration systems with proper two-phase physics

✅ **Multiphase FVM Mastery**: Applied finite volume discretization to VOF, phase change, and conjugate heat transfer

✅ **Industrial-Grade Practices**: Used version control, documented R410A properties, validated against experimental data, and optimized for performance

✅ **Advanced Customization Skills**: Developed tube wall boundary conditions, integrated phase change models, and extended OpenFOAM for evaporator applications

✅ **Scalable Computing Expertise**: Implemented parallel computing for large evaporator meshes and analyzed scaling behavior

✅ **Portfolio-Ready Project**: A complete, validated R410A evaporator solver demonstrating expertise in industrial CFD simulation

✅ **HVAC Industry Application**: Skills directly applicable to heat exchanger design, refrigeration systems, and thermal engineering

✅ **Multiphase Physics Foundation**: Deep understanding of VOF, phase change, and two-phase heat transfer transferable to other applications

---

## Next Steps

Ready to begin? Start with **[Phase 1: 1D Tube Heat Transfer](01_Phase1_1D_Heat_Equation.md)**

> **Pro Tip:** Create a git repository before starting Phase 1 to track your R410A evaporator development and enable experimentation without fear of breaking working code.
> ```bash
> git init
> git add .
> git commit -m "Initial R410A evaporator solver setup"
> ```
>
> **Important:** First, download R410A property data from NIST Chemistry WebBook for accurate phase change modeling.