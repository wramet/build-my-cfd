# Phase 1 Context ("Bible")
## Foundation Theory (Days 01-12)

> **Purpose:** This file defines the shared notation, terminology, and key concepts for Phase 1.
> All daily lessons in this phase MUST reference this file to ensure consistency.

---

## 📐 Notation Standards

### Vector/Scalar Notation (LaTeX)

| Symbol | LaTeX | Description |
|--------|-------|-------------|
| Velocity | `$\mathbf{U}$` | Vector field |
| Velocity components | `$u, v, w$` | Scalar components |
| Pressure | `$p$` | Scalar field |
| Density | `$\rho$` | Scalar |
| Dynamic viscosity | `$\mu$` | Scalar |
| Kinematic viscosity | `$\nu$` | Scalar |
| Temperature | `$T$` | Scalar |
| Volume fraction | `$\alpha$` | 0=gas, 1=liquid |
| Face area vector | `$\mathbf{S}_f$` | Vector |
| Cell volume | `$V_P$` | Scalar |
| Mass flow rate | `$\dot{m}$` | Scalar |

### Math Conventions
- Use `$\mathbf{X}$` for vectors (bold), NOT `$\vec{X}$`
- Use `$\nabla \cdot$` for divergence
- Use `$\nabla$` for gradient
- Partial derivatives: `$\frac{\partial \phi}{\partial t}$`

---

## 🔧 OpenFOAM Class References

### Core Classes (Phase 1)

| Class | Purpose |
|-------|---------|
| `volScalarField` | Cell-centered scalar field. **Note:** In this project, we extend this class to include `addExpansionSource()` (Custom implementation, DO NOT Remove). |
| `volVectorField` | Cell-centered vector field (U) |
| `surfaceScalarField` | Face-centered scalar (phi) |
| `fvMesh` | Finite volume mesh |
| `lduMatrix` | Sparse matrix (LDU format) |
| `fvMatrix<Type>` | Equation matrix |
| `lduAddressing` | Matrix connectivity |

### Operators

| Operator | Purpose |
|----------|---------|
| `fvm::ddt()` | Time derivative (implicit) |
| `fvm::div()` | Divergence/convection (implicit) |
| `fvm::laplacian()` | Diffusion (implicit) |
| `fvc::grad()` | Gradient (explicit) |
| `fvc::div()` | Divergence (explicit) |

---

## ⭐ Hero Concept: Expansion Term

The most critical equation for this project:

$$
\nabla \cdot \mathbf{U} = \dot{m} \left( \frac{1}{\rho_v} - \frac{1}{\rho_l} \right)
$$

Where:
- $\dot{m}$ = mass transfer rate (evaporation)
- $\rho_v$ = vapor density
- $\rho_l$ = liquid density

**Why it matters:** This term accounts for volume expansion during phase change.
Without it, the solver will diverge.

**Mentioned in:** Day 01 (Derivation), Day 11 (Implementation)

---

## 🔄 Completed Days Summary (Context for Next Days)

### Day 01: Governing Equations
- **Physics**: Derived Conservation of Mass, Momentum, Energy for *two-phase mixture*.
- **Key Equation**: $\nabla \cdot \mathbf{U} = \dot{m} \left( \frac{1}{\rho_v} - \frac{1}{\rho_l} \right)$ (Expansion Term).
- **Implmentation**:
    - `volScalarField` extension: `addExpansionSource(const dimensionedScalar& mDot, ...)`
    - **Outcome**: A coupled system of PDEs ready for discretization.

### Day 02: FVM Basics
- **Theory**: Gauss's Divergence Theorem application ($ \int_V \nabla \cdot \phi dV = \sum_f \phi_f \cdot S_f $).
- **Implementation**:
    - `fvMesh`: Implemented basic owner-neighbour addressing.
    - `surfaceScalarField`: Created distinct type for face-fluxes.
    - **Outcome**: Ability to compute net flux for any control volume.

### Day 03: Spatial Discretization
- **Schemes Implemented**:
    - **Upwind (UDS)**: $ \phi_f = \phi_P $ if flux > 0. Stable, Diffusive.
    - **Central (CDS)**: $ \phi_f = 0.5(\phi_P + \phi_N) $. Accurate, Oscillatory (unbounded).
    - **TVD**: Hybrid. $ \phi_f = \phi_P + \frac{1}{2} \psi(r) (\phi_N - \phi_P) $.
- **Classes**:
    - `TVDLimiter`: Base class.
    - `VanLeerLimiter`: Smooth limiter ($ \psi(r) = (r+|r|)/(1+r) $).
    - `SuperBeeLimiter`: Compressive limiter (for VOF).

### Day 04: Temporal Discretization
- **Schemes Implemented**:
    - **Euler Implicit**: First-order, Unconditionally stable.
    - **Crank-Nicolson**: Second-order, marginally stable (requires good IC).
- **Stability**:
    - `CourantNumber` class: Implemented $ Co = \frac{U \Delta t}{\Delta x} $ calculation.

### Day 05: Mesh Topology
- **Data Structures**:
    - **LDU Addressing**: `lowerAddr`, `upperAddr`, `faces`.
    - **CSR Format**: Implemented converter `LduToCsr()` for interface with external linear algebra libraries.
- **Outcome**: Efficient O(N) traversal for matrix assembly.

### Day 06: Boundary Conditions
- **Hierarchy**: `fvPatchField` (Abstract) -> `FixedValue`, `ZeroGradient`, `Mixed`.
- **Special BCs**:
    - `WallFunction`: Implemented standard log-law for k-epsilon.
    - `InletOutlet`: Switches between zeroGradient (outflow) and fixedValue (inflow).

### Day 07: Linear Algebra (LDU)
- **Matrix structure**: `lduMatrix` { `diag`, `lower`, `upper`, `source` }.
- **Assembly**:
    - `fvm::div`: Assembles flux contributions (asymmetric).
    - `fvm::laplacian`: Assembles diffusion contributions (symmetric).
- **Outcome**: A fully assembled linear system $ Ax = b $.

### Day 08: Iterative Solvers
- **Algorithms**:
    - **PCG**: Preconditioned Conjugate Gradient (Symmetric matrices, e.g., Pressure).
    - **PBiCGStab**: Preconditioned Bi-Conjugate Gradient Stabilized (Asymmetric, e.g., U, T).
- **Preconditioners**:
    - `DIC`: Diagonal Incomplete Cholesky (for PCG).
    - `DILU`: Diagonal Incomplete LU (for PBiCGStab).

### Day 09: Pressure-Velocity Coupling
- **Algorithm (PISO)**:
    1. **Predictor**: Solve Momentum (implicit U).
    2. **Loop**:
        - Calc $ H_{by}A $.
        - Solve Pressure Poisson: $ \nabla \cdot ( \frac{1}{A_P} \nabla p ) = \nabla \cdot H_{by}A $.
        - **Corrector**: Correct U and Flux.
- **Rhie-Chow**: Implemented within `fvc::reconstruct` to prevent checkerboarding.

### Day 10: Two-Phase Fundamentals (VOF)
- **Method**: Volume of Fluid (VOF) with MULES.
- **Equation**: $ \frac{\partial \alpha}{\partial t} + \nabla \cdot (U \alpha) + \nabla \cdot (U_r \alpha (1-\alpha)) = 0 $.
- **Classes**:
    - `AlphaEquation`: Solver class with sub-cycling.
    - `InterfaceCompression`: The artificial compression term.

### Day 11: Phase Change Theory
- **Model**: Lee Model (Assumption: Thermodynamic Equilibrium at Interface).
- **Source Terms**:
    - Evaporation ($\alpha_l \rightarrow \alpha_v$): $ \dot{m} = C \alpha_l \rho_l \frac{T - T_{sat}}{T_{sat}} $.
    - Condensation ($\alpha_v \rightarrow \alpha_l$): $ \dot{m} = C \alpha_v \rho_v \frac{T_{sat} - T}{T_{sat}} $.
- **Implementation**: `LinearizedSource` added to `fvMatrix`.

### Day 12: Phase 1 Review & Integration
- **Architecture**: `IntegratedEvaporatorSolver` class.
- **Capabilities**:
    - Solves coupled U, p, T, alpha system.
    - Handles phase change source terms.
    - Stable up to Co = 0.5.

---

## 📚 Phase 1 Topics Overview

| Day | Topic | Key Classes/Concepts | Detailed Description |
|-----|-------|----------------------|----------------------|
| 01 | Governing Equations | Continuity, N-S, Energy | |
| 02 | FVM Basics | Gauss theorem, Control volume | |
| 03 | Spatial Discretization | Upwind, Central, TVD schemes | Finite Volume interpolation, Flux calculation, TVD limiters (vanLeer, superBee), Numerical diffusion vs. Oscillation. |
| 04 | Temporal Discretization | Euler, Crank-Nicolson | Time integration schemes, Courant Number (CFL) stability condition, Implicit vs Explicit time-stepping. |
| 05 | Mesh Topology | `lduAddressing`, `fvMesh` | Unstructured mesh data structures, Owner-Neighbour addressing, CSR/LDU Matrix formats. |
| 06 | Boundary Conditions (BCs) | `FvPatchField`, `FixedValue` | Dirichlet/Neumann conditions, Wall functions, Runtime selection mechanism, Matrix manipulation for BCs. |
| 07 | Linear Algebra (LDU) | `LduMatrixAssembler` | Matrix assembly for unstructured grids, Diagonal dominance, Handling asymmetric matrices. |
| 08 | Iterative Solvers | BiCGStab, PCG | Krylov subspace methods, Preconditioning (DIC, DILU), Convergence criteria, Residual scaling. |
| 09 | Pressure-Velocity Coupling | SIMPLE, PISO | Segregated solvers, Rhie-Chow interpolation, Pressure correction equation, Predictor-Corrector steps. |
| 10 | Two-Phase Fundamentals | VOF, MULES | Volume of Fluid method, Interface capturing, Compression flux term, Boundedness preservation. |
| 11 | Phase Change Theory | Lee Model | Mass transfer model, Linearization of source terms, Interface temperature saturation, Expansion term implementation. |
| 12 | Phase 1 Review | Integrated Evaporator Solver | Synthesis of all concepts into a unified solver architecture, verification strategies, and roadmap for Phase 2. |

---

## 🔗 Cross-References

- **Previous Phase:** None (this is the foundation)
- **Next Phase:** Phase 2 - Geometry & Mesh (Days 13-19)
- **Related Modules:** MODULE_01_CFD_FUNDAMENTALS, MODULE_05_OPENFOAM_PROGRAMMING
