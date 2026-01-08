# 90-Day CFD Engine Development Roadmap
## Target: Refrigerant Two-Phase Flow with Evaporation in Tube

---

## 🎯 Target Application

> **จำลองการไหลของสารทำความเย็นในท่อ Evaporator:**
> - **Inlet:** Refrigerant เข้ามาเป็นของเหลว (Subcooled liquid)
> - **Tube:** Two-phase flow + Evaporation (พร้อม Volume expansion)
> - **Outlet:** Refrigerant ออกเป็นไอ (Superheated vapor)
> - **Wall BC:** Fixed temperature หรือ Fixed heat flux

---

## Scope

```
┌─────────────────────────────────────────────────────────────┐
│                 EVAPORATOR TUBE SIMULATION                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Inlet ────────────► Tube ────────────► Outlet            │
│   (Liquid R410A)    (Two-phase)      (Vapor R410A)         │
│                                                             │
│   Wall: T_wall = const  OR  q" = const                     │
│                                                             │
│   ✓ Navier-Stokes (Momentum)                               │
│   ✓ Energy equation                                        │
│   ✓ VOF (Two-phase interface tracking)                     │
│   ✓ Phase change (Evaporation + Expansion term) ⭐         │
│   ✓ Simple turbulence (Mixing Length) ⭐                   │
│   ✓ CoolProp + Lookup Table ⭐                             │
│   ✗ Multi-region CHT                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 6 Phases Overview (Revised)

| Phase | วัน | Module | หมายเหตุ |
|-------|-----|--------|----------|
| 1 | 01-12 | **Foundation** | ทฤษฎี FVM, Heat Transfer, Two-Phase |
| 2 | 13-19 | **Geometry & Mesh** | ลดลง - ใช้ Script ง่ายๆ |
| 3 | 20-49 | **Solver Core** | เพิ่ม Turbulence + Pressure Source prep |
| 4 | 50-77 | **VOF + Phase Change** | เพิ่ม Expansion Term + 1D Boiling Test |
| 5 | 78-86 | **Pre/Post Processing** | เพิ่ม Property Tabulation |
| 6 | 87-90 | **Integration** | Final Validation |

---

## Key Milestones

| Milestone | Day | Deliverable |
|-----------|-----|-------------|
| 🏁 M1 | Day 12 | Foundation Theory Complete |
| 🏁 M2 | Day 19 | Tube Mesh Generator |
| 🏁 M3 | Day 49 | Heat Transfer Solver (with Turbulence) |
| 🏁 **M3.5** | Day 65 | **1D Boiling Test Passed** ⭐ (New!) |
| 🏁 M4 | Day 77 | Two-Phase Evaporation Solver |
| 🏁 M5 | Day 86 | Full Pipeline Working |
| 🏁 M6 | Day 90 | Validated Evaporator Tube CFD Engine |

---

# Phase 1: Foundation (Day 01-12)
## ทฤษฎีพื้นฐานสำหรับ Two-Phase Flow CFD

---

### Day 01: Governing Equations
**หัวข้อ:** Conservation Laws for CFD
**เนื้อหา:**
- Continuity equation (with source term for phase change)
- Navier-Stokes equations (Momentum)
- Energy equation (Enthalpy form)
- Vector notation and tensor basics
**ผลลัพธ์:** เข้าใจสมการหลักที่ต้อง Discretize

---

### Day 02: Finite Volume Method Basics
**หัวข้อ:** From PDE to Algebraic Equations
**เนื้อหา:**
- Control volume concept
- Gauss divergence theorem
- Surface integrals vs Volume integrals
- Discretization overview
**ผลลัพธ์:** เข้าใจหลักการ FVM

---

### Day 03: Spatial Discretization Schemes
**หัวข้อ:** Face Value Interpolation
**เนื้อหา:**
- Central differencing
- Upwind schemes (First/Second order)
- TVD/NVD schemes for two-phase
- Scheme selection criteria
**ผลลัพธ์:** เลือก Scheme ที่เหมาะกับ Two-phase ได้

---

### Day 04: Temporal Discretization
**หัวข้อ:** Time Integration Methods
**เนื้อหา:**
- Euler implicit/explicit
- Backward differencing
- CFL number and stability
- Time step selection for VOF
**ผลลัพธ์:** เลือก Time scheme และกำหนด Δt ได้

---

### Day 05: Mesh Topology Concepts
**หัวข้อ:** Computational Mesh Structure
**เนื้อหา:**
- Points, Faces, Cells definitions
- Owner-Neighbor concept
- Cylindrical mesh considerations
- Face area vectors, Cell volumes
**ผลลัพธ์:** เข้าใจโครงสร้าง Mesh สำหรับท่อ

---

### Day 06: Boundary Conditions Theory
**หัวข้อ:** BCs for Tube Flow
**เนื้อหา:**
- Inlet: Fixed velocity, Fixed alpha (liquid)
- Outlet: Zero gradient / Pressure outlet
- Wall: No-slip, Fixed T or Fixed heat flux
- Axis: Symmetry (for 2D axisymmetric)
**ผลลัพธ์:** กำหนด BC สำหรับ Evaporator tube ได้

---

### Day 07: Linear Algebra for CFD
**หัวข้อ:** Sparse Matrix Systems
**เนื้อหา:**
- Sparse matrix formats (LDU)
- Matrix-vector operations
- Preconditioning concepts
- Memory considerations
**ผลลัพธ์:** เข้าใจ Matrix storage ที่ใช้ใน CFD

---

### Day 08: Iterative Solvers Theory
**หัวข้อ:** Solving Linear Systems
**เนื้อหา:**
- Jacobi, Gauss-Seidel methods
- Conjugate Gradient (CG)
- BiCGStab for non-symmetric
- Convergence criteria
**ผลลัพธ์:** เลือก Solver ที่เหมาะกับ Matrix type

---

### Day 09: Pressure-Velocity Coupling
**หัวข้อ:** SIMPLE/PISO Algorithm
**เนื้อหา:**
- The coupling problem
- SIMPLE algorithm steps
- PISO for transient problems
- **Pressure Poisson with Source Term** (prepare for phase change)
**ผลลัพธ์:** เข้าใจ Pressure-Velocity coupling รวม Source term

---

### Day 10: Two-Phase Flow Fundamentals
**หัวข้อ:** Liquid-Vapor Flow in Tubes
**เนื้อหา:**
- Flow regimes (Bubbly, Slug, Annular)
- Void fraction (α) and Quality (x)
- VOF method overview
- **Density ratio และ Volume expansion**
**ผลลัพธ์:** เข้าใจ Two-phase physics รวม Expansion

---

### Day 11: Phase Change Theory
**หัวข้อ:** Evaporation Modeling
**เนื้อหา:**
- Latent heat of vaporization
- Saturation temperature/pressure
- Lee model for mass transfer
- **Expansion term: ∇·U = ṁ(1/ρ_v - 1/ρ_l)** ⭐
**ผลลัพธ์:** เข้าใจ Expansion term ที่สำคัญมาก

---

### Day 12: Phase 1 Review
**หัวข้อ:** Foundation Summary
**เนื้อหา:**
- Review all governing equations
- Two-phase flow summary
- **Expansion term importance**
- Concept check
**ผลลัพธ์:** 🏁 **Milestone 1:** Foundation Complete

---

# Phase 2: Geometry & Mesh (Day 13-19)
## Mesh Generator สำหรับท่อ (Simplified)

---

### Day 13: Tube Geometry & Mesh Data Structure
**หัวข้อ:** Core Mesh Classes
**เนื้อหา:**
- Point, Face, Cell classes
- Cylindrical coordinates
- Mesh container class
- Parameters: D, L, divisions
**ผลลัพธ์:** Mesh class skeleton

---

### Day 14: Structured Mesh for Tube
**หัวข้อ:** O-grid Meshing
**เนื้อหา:**
- Radial divisions (near-wall refinement)
- Axial divisions (uniform/graded)
- Simple 2D option (axisymmetric)
- Face/Cell construction
**ผลลัพธ์:** Generate tube mesh

---

### Day 15: Mesh Geometry Calculations
**หัวข้อ:** Cell/Face Properties
**เนื้อหา:**
- Cell center, volume
- Face center, area vector
- Owner-Neighbor addressing
- Boundary patches
**ผลลัพธ์:** Complete mesh with geometry

---

### Day 16: Mesh Quality & Refinement
**หัวข้อ:** Quality Checks
**เนื้อหา:**
- Non-orthogonality, Skewness
- Aspect ratio
- Near-wall refinement for y+
- Quality report
**ผลลัพธ์:** Mesh quality checker

---

### Day 17: Mesh I/O
**หัวข้อ:** Read/Write Mesh Files
**เนื้อหา:**
- Custom format or OpenFOAM polyMesh
- Writer functions
- Reader functions
- Validation
**ผลลัพธ์:** Mesh I/O complete

---

### Day 18: VTK Mesh Output
**หัวข้อ:** Visualization
**เนื้อหา:**
- VTK Unstructured Grid format
- Write mesh to VTK
- View in ParaView
- Debug visualization
**ผลลัพธ์:** VTK mesh export

---

### Day 19: Phase 2 Integration
**หัวข้อ:** Complete Tube Mesh Generator
**เนื้อหา:**
- Parametric mesh generation
- Quality check pass
- Export to VTK + custom format
- Ready for solver
**ผลลัพธ์:** 🏁 **Milestone 2:** Tube Mesh Generator

---

# Phase 3: Solver Core (Day 20-49)
## Field, Matrix, Operators, SIMPLE, Turbulence

---

### Day 20: Field Class Template
**หัวข้อ:** Generic Field<Type>
**เนื้อหา:**
- Template class design
- Scalar, Vector types
- Memory allocation
- Basic operations (+, -, *, /)
**ผลลัพธ์:** `Field<Type>` template class

---

### Day 21: Dimensioned Field
**หัวข้อ:** Units and Dimensions
**เนื้อหา:**
- Dimension set (M, L, T, K, ...)
- Dimensional checking
- DimensionedField class
- Preventing unit errors
**ผลลัพธ์:** Dimension-aware fields

---

### Day 22: GeometricField
**หัวข้อ:** Internal + Boundary Fields
**เนื้อหา:**
- Internal field storage
- Boundary field storage
- Mesh reference
- `volScalarField`, `volVectorField`
**ผลลัพธ์:** GeometricField classes

---

### Day 23: PatchField & Basic BCs
**หัวข้อ:** Boundary Conditions
**เนื้อหา:**
- PatchField interface
- fixedValue, zeroGradient, fixedGradient
- inletOutlet
- BC coefficient calculation
**ผลลัพธ์:** Essential BCs working

---

### Day 24: Sparse Matrix - LDU Format
**หัวข้อ:** Matrix Storage
**เนื้อหา:**
- lduAddressing class
- Lower, Diagonal, Upper arrays
- Memory layout
- Matrix-vector multiply
**ผลลัพธ์:** `lduMatrix` class

---

### Day 25: fvMatrix Framework
**หัวข้อ:** Equation Matrix Class
**เนื้อหา:**
- fvMatrix<Type> class
- Source term storage
- Boundary coefficient handling
- `solve()` interface
**ผลลัพธ์:** fvMatrix framework

---

### Day 26: Iterative Solvers
**หัวข้อ:** CG and BiCGStab
**เนื้อหา:**
- Jacobi, Gauss-Seidel (basic)
- PCG for pressure
- PBiCGStab for momentum
- Convergence checking
**ผลลัพธ์:** Linear solvers working

---

### Day 27: fvm::ddt Operator
**หัวข้อ:** Time Derivative
**เนื้อหา:**
- Euler scheme
- Old time storage
- Matrix coefficient
- Source term contribution
**ผลลัพธ์:** `fvm::ddt()` operator

---

### Day 28: fvm::div Operator
**หัวข้อ:** Convection Term
**เนื้อหา:**
- Face flux (phi)
- Upwind interpolation
- Matrix coefficient assembly
- Owner/Neighbor contributions
**ผลลัพธ์:** `fvm::div(phi, U)` operator

---

### Day 29: fvm::laplacian Operator
**หัวข้อ:** Diffusion Term
**เนื้อหา:**
- Laplacian discretization
- Face diffusivity
- Non-orthogonal correction (basic)
- Boundary contribution
**ผลลัพธ์:** `fvm::laplacian(Γ, φ)` operator

---

### Day 30: fvc Operators
**หัวข้อ:** Explicit Field Calculations
**เนื้อหา:**
- `fvc::grad()` - Gradient
- `fvc::div()` - Divergence
- Face interpolation
- Gauss theorem application
**ผลลัพธ์:** Explicit operators

---

### Day 31: Flux Calculation
**หัวข้อ:** Face Mass Flux (phi)
**เนื้อหา:**
- Velocity to face: U_f
- phi = ρ * (Sf · U_f)
- Rhie-Chow interpolation
- Flux conservation
**ผลลัพธ์:** phi calculation routine

---

### Day 32: SIMPLE - Momentum Predictor
**หัวข้อ:** Step 1 of SIMPLE
**เนื้อหา:**
- Momentum equation without pressure
- Solve for U*
- Under-relaxation
- Boundary conditions
**ผลลัพธ์:** Momentum predictor

---

### Day 33: SIMPLE - Pressure Equation (Standard)
**หัวข้อ:** Step 2 of SIMPLE
**เนื้อหา:**
- Pressure Poisson equation
- H/A formulation
- Solve for p'
- Pressure BCs
**ผลลัพธ์:** Pressure equation solver

---

### Day 34: SIMPLE - Pressure with Source Term ⭐
**หัวข้อ:** Pressure Equation with Dilatation
**เนื้อหา:**
- **∇·(1/A ∇p') = ∇·U* - S_expansion**
- Source term for phase change
- Implementation in fvMatrix
- Testing with artificial source
**ผลลัพธ์:** Pressure equation ready for phase change

---

### Day 35: SIMPLE - Velocity Correction
**หัวข้อ:** Step 3 of SIMPLE
**เนื้อหา:**
- Correct velocity: U = U* - (1/A)∇p'
- Correct flux: phi
- Under-relaxation
- Convergence check
**ผลลัพธ์:** Complete SIMPLE loop

---

### Day 36: PISO Algorithm
**หัวข้อ:** Transient Solver
**เนื้อหา:**
- PISO vs SIMPLE
- Multiple corrector steps
- Time loop
- **PISO with source term support**
**ผลลัพธ์:** Working PISO solver

---

### Day 37: Energy Equation
**หัวข้อ:** Temperature Solver
**เนื้อหา:**
- Energy equation: ∂(ρh)/∂t + ∇·(ρUh) = ∇·(k∇T)
- Coupling with flow
- Temperature BCs
- Fixed heat flux wall
**ผลลัพธ์:** Energy equation solver

---

### Day 38: Thermophysical Properties
**หัวข้อ:** Temperature-Dependent Properties
**เนื้อหา:**
- ρ(T), μ(T), k(T), Cp(T)
- Property classes
- Single-phase water for testing
- Prepare for two-phase
**ผลลัพธ์:** Property system

---

### Day 39: Heated Pipe Test (Laminar)
**หัวข้อ:** Single-Phase Validation
**เนื้อหา:**
- Heated pipe (laminar)
- Compare with Graetz solution
- Check temperature profile
- Nusselt number
**ผลลัพธ์:** Validated laminar heat transfer

---

### Day 40: Turbulence Theory (Simple)
**หัวข้อ:** RANS Basics
**เนื้อหา:**
- Reynolds averaging
- Turbulent viscosity νt
- Mixing Length model
- Effective viscosity: ν_eff = ν + νt
**ผลลัพธ์:** เข้าใจ Simple turbulence

---

### Day 41: Mixing Length Model ⭐
**หัวข้อ:** Simple Turbulence Implementation
**เนื้อหา:**
- l_m = κy (near wall)
- νt = l_m² |∂U/∂y|
- Wall distance calculation
- Implementation in solver
**ผลลัพธ์:** Mixing Length turbulence working

---

### Day 42: Turbulent Heat Transfer ⭐
**หัวข้อ:** αt (Thermal Diffusivity)
**เนื้อหา:**
- αt = νt / Pr_t
- Effective thermal conductivity
- Turbulent Prandtl number
- Coupling with energy equation
**ผลลัพธ์:** Turbulent heat transfer

---

### Day 43: Heated Pipe Test (Turbulent)
**หัวข้อ:** Turbulent Validation
**เนื้อหา:**
- Heated pipe (turbulent Re)
- Compare with Gnielinski correlation
- Check Nu number
- Compare with laminar
**ผลลัพธ์:** Validated turbulent heat transfer

---

### Day 44: Wall Function (Optional)
**หัวข้อ:** Near-Wall Treatment
**เนื้อหา:**
- y+ calculation
- Log-law for velocity
- Simple wall function
- When to use
**ผลลัพธ์:** Basic wall function (optional)

---

### Day 45-47: Code Cleanup & Testing
**หัวข้อ:** Code Quality (3 days)
**เนื้อหา:**
- Code organization
- Documentation
- Error messages
- Unit tests for each operator
- Debug output fields
**ผลลัพธ์:** Clean, tested codebase

---

### Day 48-49: Phase 3 Integration
**หัวข้อ:** Single-Phase Heat Transfer Solver
**เนื้อหา:**
- Complete solver integration
- PISO + Energy + Turbulence
- Heated tube test case
- Compare with OpenFOAM
**ผลลัพธ์:** 🏁 **Milestone 3:** Heat Transfer Solver (with Turbulence)

---

# Phase 4: VOF + Phase Change (Day 50-77)
## Two-Phase Flow with Evaporation + Expansion Term

---

### Day 50: VOF Method Theory
**หัวข้อ:** Volume of Fluid Basics
**เนื้อหา:**
- Volume fraction α (0=vapor, 1=liquid)
- Interface representation
- Sharp vs Diffuse interface
- Advantages/Disadvantages
**ผลลัพธ์:** เข้าใจ VOF approach

---

### Day 51: Alpha Transport Equation
**หัวข้อ:** Interface Advection
**เนื้อหา:**
- ∂α/∂t + ∇·(Uα) = 0 (no phase change)
- Discretization
- Explicit vs Implicit
- CFL requirement for VOF
**ผลลัพธ์:** Alpha equation framework

---

### Day 52: Interface Sharpening
**หัวข้อ:** Compression Term
**เนื้อหา:**
- Interface compression velocity
- Artificial compression term
- Preventing smearing
- Compression factor
**ผลลัพธ์:** Sharp interface tracking

---

### Day 53: MULES Limiter
**หัวข้อ:** Boundedness
**เนื้อหา:**
- Ensure 0 ≤ α ≤ 1
- Flux limiting
- MULES algorithm
- Sub-cycling option
**ผลลัพธ์:** Bounded alpha solver

---

### Day 54: Two-Phase Properties
**หัวข้อ:** Mixture Properties
**เนื้อหา:**
- ρ = α·ρ_l + (1-α)·ρ_v
- μ = α·μ_l + (1-α)·μ_v (or harmonic)
- k, Cp averaging
- **Large density ratio handling**
**ผลลัพธ์:** Mixture property calculation

---

### Day 55: Two-Phase Momentum
**หัวข้อ:** VOF Momentum Equation
**เนื้อหา:**
- Single momentum with mixture properties
- Gravity effects
- Pressure-velocity coupling
- **Prepare for expansion source**
**ผลลัพธ์:** Two-phase momentum solver

---

### Day 56: Simple VOF Test (No Phase Change)
**หัวข้อ:** Dam Break or Rising Bubble
**เนื้อหา:**
- Simple two-phase test (water-air)
- Verify alpha transport
- Check mass conservation
- Compare with OpenFOAM interFoam
**ผลลัพธ์:** Working VOF solver (no phase change)

---

### Day 57: CoolProp Setup & Integration
**หัวข้อ:** Refrigerant Property Library
**เนื้อหา:**
- Install CoolProp (C++ library)
- Link with CMake/Make
- Basic API: `PropsSI()` function
- Error handling
**ผลลัพธ์:** CoolProp linked and working

---

### Day 58: CoolProp - Liquid & Vapor Properties
**หัวข้อ:** R410A/R32 Properties via CoolProp
**เนื้อหา:**
- Liquid: ρ_l, μ_l, k_l, Cp_l
- Vapor: ρ_v, μ_v, k_v, Cp_v
- Quality (Q=0 liquid, Q=1 vapor)
- Wrapper class for clean API
**ผลลัพธ์:** Refrigerant property wrapper

---

### Day 59: CoolProp - Saturation Properties
**หัวข้อ:** Saturation Curve
**เนื้อหา:**
- T_sat(P), P_sat(T)
- Latent heat: h_fg = h_v - h_l
- Saturation line
- Property at saturation
**ผลลัพธ์:** Complete CoolProp integration

---

### Day 60: Phase Change Model - Lee Model
**หัวข้อ:** Mass Transfer Theory
**เนื้อหา:**
- Lee evaporation model
- ṁ = r_e · α_l · ρ_l · (T - T_sat) / T_sat
- Evaporation coefficient r_e
- Condensation option
**ผลลัพธ์:** Lee model implementation

---

### Day 61: The Expansion Term ⭐ (Critical!)
**หัวข้อ:** Handling Density Change
**เนื้อหา:**
- **∇·U = ṁ (1/ρ_v - 1/ρ_l)** ⭐
- Why this is critical (Pressure divergence)
- Source term in Pressure equation
- Implementation in PISO loop
**ผลลัพธ์:** Expansion term implemented

---

### Day 62: Alpha Equation with Phase Change
**หัวข้อ:** Source in Alpha Equation
**เนื้อหา:**
- ∂α/∂t + ∇·(Uα) = ṁ/ρ_l
- Mass source term
- Boundedness with source
- Mass conservation check
**ผลลัพธ์:** Alpha equation with source

---

### Day 63: Energy Equation with Latent Heat
**หัวข้อ:** Phase Change Energy
**เนื้อหา:**
- Energy source: S_h = ṁ · h_fg
- Heat absorption during evaporation
- Coupling with temperature
- Energy balance check
**ผลลัพธ์:** Energy equation with phase change

---

### Day 64: Spurious Currents ⭐
**หัวข้อ:** VOF Instability
**เนื้อหา:**
- What causes spurious currents
- Interface smoothing
- CSF model issues
- Mitigation strategies
**ผลลัพธ์:** Understand and mitigate spurious currents

---

### Day 65: 1D Boiling Test ⭐ (Milestone 3.5)
**หัวข้อ:** Stefan Problem
**เนื้อหา:**
- 1D evaporation in closed box
- Check pressure rise
- Compare with analytical
- **Verify expansion term works!**
**ผลลัพธ์:** 🏁 **Milestone 3.5:** 1D Boiling Test Passed!

---

### Day 66-67: Phase Change Solver Integration
**หัวข้อ:** Complete Phase Change Solver
**เนื้อหา:**
- Combine: Alpha + Momentum + Pressure + Energy
- PISO loop with expansion
- Convergence monitoring
- Mass/Energy balance check
**ผลลัพธ์:** Integrated phase change solver

---

### Day 68: Property Tabulation ⭐
**หัวข้อ:** Optimizing Property Lookups
**เนื้อหา:**
- Generate lookup table (T vs ρ, μ, k, Cp)
- Bilinear interpolation
- Replace direct CoolProp calls in loop
- **Speed improvement 100-1000x**
**ผลลัพธ์:** Fast property lookup

---

### Day 69: Tube Flow Setup
**หัวข้อ:** Evaporator Tube Case
**เนื้อหา:**
- Tube mesh (from Phase 2)
- Inlet: Subcooled liquid R410A
- Wall: Fixed heat flux
- Outlet: Pressure outlet
**ผลลัพธ์:** Evaporator tube case ready

---

### Day 70: Wall Heat Flux BC
**หัวข้อ:** Fixed Heat Flux Wall
**เนื้อหา:**
- q" = -k(∂T/∂n)
- fixedGradient implementation
- Heat input calculation
- Wall temperature evolution
**ผลลัพธ์:** Heat flux BC working

---

### Day 71-72: First Tube Evaporation Run
**หัวข้อ:** Initial Simulation
**เนื้อหา:**
- Run tube evaporation case
- Monitor void fraction evolution
- Check for divergence
- Debug if needed
**ผลลัพธ์:** Running tube evaporation

---

### Day 73: Results Analysis
**หัวข้อ:** Post-processing
**เนื้อหา:**
- Void fraction along tube
- Wall temperature profile
- Pressure drop
- Flow regime observation
**ผลลัพธ์:** Results extraction routines

---

### Day 74: Validation - HTC Correlations
**หัวข้อ:** Compare with Shah/Chen
**เนื้อหา:**
- Shah correlation for boiling HTC
- Chen correlation
- Compare outlet quality
- Document discrepancies
**ผลลัพธ์:** HTC validation

---

### Day 75: Validation - Pressure Drop
**หัวข้อ:** Two-Phase Pressure Drop
**เนื้อหา:**
- Lockhart-Martinelli correlation
- Friedel correlation
- Compare with simulation
- Error analysis
**ผลลัพธ์:** Pressure drop validation

---

### Day 76: Parameter Sensitivity
**หัวข้อ:** Numerical Parameters
**เนื้อหา:**
- Time step sensitivity
- Mesh sensitivity
- Lee model coefficient effect
- Optimal settings
**ผลลัพธ์:** Recommended settings

---

### Day 77: Phase 4 Integration
**หัวข้อ:** Complete Evaporation Solver
**เนื้อหา:**
- Full solver documentation
- Test case library
- Known limitations
- Performance benchmarks
**ผลลัพธ์:** 🏁 **Milestone 4:** Two-Phase Evaporation Solver

---

# Phase 5: Pre/Post Processing (Day 78-86)
## Case Setup and Visualization

---

### Day 78: Dictionary Parser
**หัวข้อ:** Configuration File System
**เนื้อหา:**
- Simple key-value format
- Nested dictionaries
- Type conversion
- Error handling
**ผลลัพธ์:** Dictionary parser

---

### Day 79: Case Directory Structure
**หัวข้อ:** Organize Simulation Files
**เนื้อหา:**
- mesh/, properties/, settings/, results/
- Initial conditions files
- Boundary condition files
- Solver settings
**ผลลัพธ์:** Case structure handler

---

### Day 80: VTK Field Output
**หัวข้อ:** Export Solution Fields
**เนื้อหา:**
- VTK with T, p, U, alpha
- Time series output
- ParaView animation
- Output frequency control
**ผลลัพธ์:** VTK field writer

---

### Day 81: Probes & Surface Integration
**หัวข้อ:** Data Extraction
**เนื้อหา:**
- Probe points (T, p at locations)
- Inlet/Outlet mass flow rate
- Heat transfer rate Q
- CSV output
**ผลลัพธ์:** Data extraction system

---

### Day 82: Residual Logging
**หัวข้อ:** Convergence Monitoring
**เนื้อหา:**
- Residual history
- Log file format
- Convergence plots
- Auto-stopping criteria
**ผลลัพธ์:** Residual monitoring

---

### Day 83: Debug Field Output
**หัวข้อ:** Debugging Tools
**เนื้อหา:**
- Output intermediate fields
- Cell-by-cell residual visualization
- Source term visualization
- Helps find where divergence starts
**ผลลัพธ์:** Debug output for ParaView

---

### Day 84-85: Run Script & Automation
**หัวข้อ:** Automation
**เนื้อหา:**
- Python wrapper script
- Case preparation
- Batch runs
- Results packaging
**ผลลัพธ์:** Automated run system

---

### Day 86: Phase 5 Integration
**หัวข้อ:** Complete Pipeline
**เนื้อหา:**
- End-to-end test: mesh → solve → visualize
- Troubleshooting guide
- Performance tips
- Ready for final validation
**ผลลัพธ์:** 🏁 **Milestone 5:** Full Pipeline Working

---

# Phase 6: Integration & Final Validation (Day 87-90)
## Complete Evaporator Tube Simulation

---

### Day 87: Production Case Setup
**หัวข้อ:** Final Evaporator Configuration
**เนื้อหา:**
- Optimized mesh
- Realistic R410A conditions
- Proper convergence criteria
- Long run test
**ผลลัพธ์:** Production-ready case

---

### Day 88: Final Validation
**หัวข้อ:** Complete Validation Report
**เนื้อหา:**
- HTC comparison summary
- Pressure drop comparison
- Mass/Energy balance
- Error quantification
**ผลลัพธ์:** Validation report

---

### Day 89: Documentation
**หัวข้อ:** User Guide
**เนื้อหา:**
- Installation instructions
- Case setup guide
- Troubleshooting
- Example cases
**ผลลัพธ์:** Complete documentation

---

### Day 90: Project Completion
**หัวข้อ:** Final Review
**เนื้อหา:**
- Final code review
- Known limitations
- Future improvements (k-ε, CHT, etc.)
- **Success! 🎉**
**ผลลัพธ์:** 🏁 **Milestone 6:** Evaporator Tube CFD Engine Complete!

---

# Summary

## Critical Additions (Based on Expert Review)

| Addition | Day | Why Critical |
|----------|-----|--------------|
| **Expansion Term** | Day 11, 34, 61 | ไม่มี = Solver Diverge |
| **Simple Turbulence** | Day 40-43 | ไม่มี = HTC ผิด |
| **Property Tabulation** | Day 68 | ไม่มี = รันช้ามาก |
| **1D Boiling Test** | Day 65 | Debug ก่อนทำ Tube |
| **Spurious Currents** | Day 64 | VOF instability |

## 7 Milestones (Including 3.5)

| # | Day | Deliverable |
|---|-----|-------------|
| M1 | 12 | Foundation Theory |
| M2 | 19 | Tube Mesh Generator |
| M3 | 49 | Heat Transfer Solver (with Turbulence) |
| **M3.5** | 65 | **1D Boiling Test Passed** ⭐ |
| M4 | 77 | Two-Phase Evaporation Solver |
| M5 | 86 | Full Pipeline |
| M6 | 90 | **Complete Evaporator CFD Engine!** |

---

*Last Updated: 2026-01-03*
*Revised based on expert technical review*
*Target: Refrigerant Two-Phase Flow with Evaporation*
