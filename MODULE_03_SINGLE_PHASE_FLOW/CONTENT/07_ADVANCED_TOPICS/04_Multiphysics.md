# Multiphysics Coupling

การเชื่อมโยงหลายฟิสิกส์ใน OpenFOAM

---

**⏱️ Estimated Reading Time:** 25-30 minutes

**📋 Learning Objectives**

By the end of this document, you will be able to:
- Identify and select appropriate coupling strategies (weak, strong, monolithic) for different multiphysics problems
- Configure Conjugate Heat Transfer (CHT) simulations using `chtMultiRegionFoam`
- Set up Fluid-Structure Interaction (FSI) problems with proper interface conditions
- Implement reacting flow simulations with chemistry models
- Structure multi-region cases in OpenFOAM with proper boundary conditions
- Apply acceleration techniques (Aitken relaxation) for partitioned coupling
- Troubleshoot common convergence issues in multiphysics simulations

**🔗 Prerequisites**
- **Required:** Familiarity with single-physics solvers ([01_Incompressible_Flow_Solvers](01_InCOMPRESSIBLE_FLOW_SOLVERS/01_Introduction.md))
- **Required:** Understanding of boundary conditions ([03_BOUNDARY_CONDITIONS](../../MODULE_01_CFD_FUNDAMENTALS/CONTENT/03_BOUNDARY_CONDITIONS/00_Overview.md))
- **Required:** Heat transfer fundamentals ([01_Energy_Equation_Fundamentals](01_Energy_Equation_Fundamentals.md))
- **Recommended:** Turbulence modeling basics ([01_Turbulence_Fundamentals](03_TURBULENCE_MODELING/01_Turbulence_Fundamentals.md))

---

## Overview

Multiphysics coupling involves solving multiple physical phenomena simultaneously, where each physics affects the others. OpenFOAM provides several approaches for coupling different physics:

| Coupling Type | Physics Involved | Primary Solver | Complexity |
|---------------|------------------|----------------|------------|
| **FSI** | Fluid dynamics + Structural mechanics | `pimpleFoam` + `solidDisplacementFoam` | High |
| **CHT** | Fluid flow + Heat transfer (fluid + solid) | `chtMultiRegionFoam` | Medium |
| **Reacting** | Flow + Chemical reactions | `reactingFoam`, `rhoReactingFoam` | Medium-High |

---

## 1. Fluid-Structure Interaction (FSI)

### What is FSI?

**Fluid-Structure Interaction** analyzes problems where fluid forces cause structural deformation, and this deformation alters the fluid flow. Common applications include:
- Blood flow in arteries (vessel deformation affects flow)
- Aircraft wing flutter (aeroelasticity)
- Wind turbine blades (flexible structures)
- Heart valve mechanics

### Interface Conditions

FSI requires matching conditions at the fluid-solid interface:

**Kinematic Condition (velocity continuity):**
$$\mathbf{u}_f = \frac{\partial \mathbf{d}_s}{\partial t}$$

The fluid velocity at the interface equals the solid velocity (time derivative of displacement).

**Dynamic Condition (force equilibrium):**
$$\boldsymbol{\sigma}_f \cdot \mathbf{n} = \boldsymbol{\sigma}_s \cdot \mathbf{n}$$

Stresses must balance across the interface—fluid forces applied to solid equal solid reaction forces.

### Why Choose Different Coupling Strategies?

```
┌─────────────────────────────────────────────────────────────────────┐
│                        WEAK COUPLING                                 │
│                        (One-way or loose)                            │
│                                                                     │
│  Fluid Domain                Solid Domain                           │
│  ┌─────────────┐            ┌─────────────┐                        │
│  │  Solve      │───────────►│  Solve      │  Single pass per    │
│  │  Fluid Eq.  │            │  Solid Eq.  │  time step           │
│  └─────────────┘            └─────────────┘                        │
│         ▲                         │                                │
│         │                         ▼                                │
│    Load data              No iteration                           │
│    (from previous)         (may be unstable)                      │
│                                                                     │
│    ✓ Simple  ✗ May diverge  ✗ Lower accuracy                      │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                        STRONG COUPLING                                │
│                        (Two-way with iteration)                      │
│                                                                     │
│  Fluid Domain                Solid Domain                           │
│  ┌─────────────┐            ┌─────────────┐                        │
│  │  Solve      │◄───────────│  Solve      │                        │
│  │  Fluid Eq.  │            │  Solid Eq.  │                        │
│  └─────────────┘            └─────────────┘                        │
│         ▲                         │                                │
│         │                         ▼                                │
│    Transfer data           Exchange data                          │
│    (loads, disp)           at interface                           │
│         │                         │                                │
│         └───────► ◄───────────────┘                                │
│                   Iterate                                         │
│         │                                                         │
│         ▼                                                         │
│    Converged?  ──No──►  Repeat                                   │
│         │                                                         │
│        Yes                                                        │
│         │                                                         │
│         ▼                                                         │
│    Next time step                                                 │
│                                                                     │
│    ✓ Stable  ✓ Higher accuracy  ✗ More expensive                  │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                        MONOLITHIC COUPLING                           │
│                        (Single matrix system)                       │
│                                                                     │
│           ┌───────────────────────────────────┐                    │
│           │                                   │                    │
│           │   [A_ff   A_fs] [U_f]   = [R_f]   │                    │
│           │   [A_sf   A_ss] [U_s]     [R_s]   │                    │
│           │                                   │                    │
│           │   Single coupled matrix solve     │                    │
│           │                                   │                    │
│           └───────────────────────────────────┘                    │
│                                                                     │
│    ✓ Most stable  ✓ Exact coupling  ✗ Very complex  ✗ Memory     │
└─────────────────────────────────────────────────────────────────────┘
```

**When to use each:**

| Approach | Use When | Avoid When |
|----------|----------|------------|
| **Weak** | Structure is very stiff (negligible deformation) | Light structures, flutter analysis |
| **Strong** | Moderate coupling, need stability | Extreme stiffness mismatch |
| **Monolithic** | Severe coupling, instability issues | Large-scale problems (memory) |

### Step-by-Step FSI Setup in OpenFOAM

**Step 1: Define regions in `constant/regionProperties`**
```cpp
regions
(
    fluid
    solid
);
```

**Step 2: Set up fluid region (standard pressure-velocity solver)**
```cpp
// 0/fluid/p
boundaryField
{
    fluid_to_solid
    {
        type            regionCoupledWall;
    }
}

// 0/fluid/U
boundaryField
{
    fluid_to_solid
    {
        type            regionCoupledWall;
    }
}
```

**Step 3: Configure solid region (finite displacement solver)**
```cpp
// 0/solid/D (displacement)
boundaryField
{
    solid_to_fluid
    {
        type            regionCoupledWall;
    }
}

// constant/solid/mechanicalProperties
// For linear elastic:
rho             rho [1 -3 0 0 0 0 0]  7850;
mu              mu [1 -1 -2 0 0 0 0]  7.69e10;
lambda          lambda [1 -1 -2 0 0 0 0]  1.15e11;
```

**Step 4: Configure coupling in `system/controlDict`**
```cpp
functions
{
    fsiInterface
    {
        type            regionCouplings;
        libs            ("libsampling.so");
        regions         (fluid solid);
    }
}
```

**Step 5: Run with appropriate solver**
```bash
# For partitioned approach (most common):
solver=pimpleFoam-fluid solidDisplacementFoam-solid

# Or use external coupling (preCICE for complex FSI)
```

---

## 2. Conjugate Heat Transfer (CHT)

### What is CHT?

**Conjugate Heat Transfer** simulates simultaneous heat transfer in fluid and solid domains. Unlike adiabatic walls (no heat transfer), CHT accounts for:
- Convective heat transfer in the fluid
- Conductive heat transfer in the solid
- Energy balance at the interface

**Applications:** Heat exchangers, electronics cooling, engine cooling, building thermal analysis

### Why Use CHT?

| Approach | When to Use | Limitations |
|----------|-------------|-------------|
| **Fixed temperature BC** | Known wall temperature | Doesn't capture solid conduction |
| **Fixed heat flux BC** | Known heat input | Doesn't capture temperature-dependent properties |
| **CHT** | Solid and fluid interact | More computationally expensive |

### Interface Conditions

At the fluid-solid interface, two conditions must be satisfied:

**1. Temperature continuity:**
$$T_{fluid} = T_{solid}$$

**2. Heat flux continuity:**
$$-k_f \frac{\partial T_f}{\partial n} = -k_s \frac{\partial T_s}{\partial n}$$

The heat leaving the fluid equals the heat entering the solid (energy conservation).

### How to Set Up CHT in OpenFOAM

**Step 1: Case Structure**
```
case/
├── 0/
│   ├── fluid/
│   │   ├── p, U, T, k, omega, alphat
│   └── solid/
│       └── T
├── constant/
│   ├── regionProperties
│   ├── fluid/
│   │   ├── thermophysicalProperties
│   │   └── turbulenceProperties
│   └── solid/
│       └── thermophysicalProperties
└── system/
    ├── fluid/
    │   ├── controlDict
    │   ├── fvSchemes
    │   └── fvSolution
    └── solid/
        ├── controlDict
        ├── fvSchemes
        └── fvSolution
```

**Step 2: Define regions**
```cpp
// constant/regionProperties
regions
(
    fluid
    solid
);
```

**Step 3: Fluid thermophysical properties**
```cpp
// constant/fluid/thermophysicalProperties
thermoType
{
    type            heRhoThermo;
    mixture         pureMixture;
    transport       const;
    thermo          hConst;
    equationOfState perfectGas;
    energy          sensibleEnthalpy;
}

mixture
{
    specie
    {
        molWeight       28.96;
    }
    thermodynamics
    {
        Cp              1007;
        Hf              0;
    }
    transport
    {
        mu              1.8e-05;
        Pr              0.7;
    }
}
```

**Step 4: Solid thermophysical properties**
```cpp
// constant/solid/thermophysicalProperties
thermoType
{
    type            heSolidThermo;
    mixture         pureMixture;
    transport       const;
    thermo          hConst;
    equationOfState rhoConst;
    energy          sensibleEnthalpy;
}

mixture
{
    specie
    {
        molWeight       1;
    }
    thermodynamics
    {
        Cp              450;
        Hf              0;
    }
    transport
    {
        kappa           45;  // Thermal conductivity [W/m/K]
    }
}
```

**Step 5: Interface boundary conditions**
```cpp
// 0/fluid/T at interface
boundaryField
{
    fluid_to_solid
    {
        type            compressible::turbulentTemperatureCoupledBaffleMixed;
        Tnbr            T;
        kappaMethod     fluidThermo;  // Use fluid conductivity
        value           uniform 300;   // Initial guess
    }
}

// 0/solid/T at interface
boundaryField
{
    solid_to_fluid
    {
        type            compressible::turbulentTemperatureCoupledBaffleMixed;
        Tnbr            T;
        kappaMethod     solidThermo;  // Use solid conductivity
        value           uniform 300;   // Initial guess
    }
}
```

**Step 6: Run the solver**
```bash
chtMultiRegionFoam
```

### CHT Best Practices

1. **Mesh quality:** Ensure good mesh quality at the interface (non-orthogonality < 70°)
2. **Time step:** Use smaller time steps than pure fluid cases due to thermal coupling
3. **Initialization:** Initialize temperatures reasonably to accelerate convergence
4. **Under-relaxation:** For challenging cases, use under-relaxation on temperature

---

## 3. Reacting Flows

### What are Reacting Flows?

**Reacting flows** involve chemical reactions that release or absorb heat, changing fluid properties (density, viscosity). The interaction between flow, chemistry, and heat transfer creates complex behavior.

**Applications:** Combustion engines, gas turbines, industrial furnaces, fire modeling

### Governing Equations

**Species Transport:**
$$\frac{\partial (\rho Y_i)}{\partial t} + \nabla \cdot (\rho Y_i \mathbf{u}) = -\nabla \cdot \mathbf{J}_i + R_i$$

Where:
- \(Y_i\) = mass fraction of species i
- \(\mathbf{J}_i\) = diffusion flux
- \(R_i\) = reaction rate (source/sink)

**Arrhenius Reaction Rate:**
$$k = A T^\beta \exp\left(-\frac{E_a}{RT}\right)$$

Where:
- \(A\) = pre-exponential factor
- \(\beta\) = temperature exponent
- \(E_a\) = activation energy

### How to Configure Reacting Flows

**Step 1: Select solver**
- `reactingFoam`: Low Mach number combustion
- `rhoReactingFoam`: Compressible reacting flows
- `rhoReactingBuoyantFoam`: Buoyancy-affected combustion

**Step 2: Define species**
```cpp
// constant/thermophysicalProperties
thermoType
{
    type            hePsiThermo;
    mixture         multiComponentMixture;
    transport       sutherland;
    thermo          janaf;
    energy          sensibleEnthalpy;
}

species
(
    O2
    N2
    H2O
    CO2
    fuel
);
```

**Step 3: Define reactions**
```cpp
// constant/reactions
reactions
{
    methane-combustion
    {
        type            irreversible;
        reaction        "CH4 + 2 O2 => CO2 + 2 H2O";
        
        A               1.8e8;
        beta            0;
        Ta              4680;  // Activation temperature [K]
    }
}
```

**Step 4: Chemistry properties**
```cpp
// constant/chemistryProperties
chemistryType
{
    solver          ode;
}

chemistry
{
    chemistryModel  EulerImplicit;
    
    initialChemicalTimeStep  1e-07;
}
```

**Step 5: Species boundary conditions**
```cpp
// 0/fuel
boundaryField
{
    inlet
    {
        type            fixedMean;
        meanValue       uniform 1.0;
    }
    
    outlet
    {
        type            inletOutlet;
        inletValue      uniform 0;
        value           uniform 0;
    }
}
```

---

## 4. Coupling Techniques and Acceleration

### Aitken Relaxation

**Why use it?** Partitioned coupling (weak/strong) can oscillate or diverge. Aitken relaxation automatically adjusts relaxation factor to accelerate convergence.

**How it works:**
$$\omega^{n+1} = \omega^n \frac{\langle \mathbf{r}^{n-1} - \mathbf{r}^n, \mathbf{r}^n \rangle}{\|\mathbf{r}^{n-1} - \mathbf{r}^n\|^2}$$

Where \(\mathbf{r}\) is the residual (discrepancy between iterations).

**Implementation:**
```cpp
// system/fvSolution (fluid)
SOLVERS
{
    D
    {
        solver          GAMG;
        tolerance       1e-06;
        relTol          0.01;
    }
}

relaxationFactors
{
    fields
    {
        D               0.3;  // Start with conservative value
    }
}
```

### Data Transfer Methods

| Method | Conservation | Accuracy | Computational Cost | When to Use |
|--------|--------------|----------|-------------------|-------------|
| **Nearest neighbor** | Poor | Low | Very low | Quick testing, non-critical |
| **Linear interpolation** | Moderate | Good | Low | Most CHT cases |
| **RBF/Morphing** | Good | Very Good | Medium | FSI with large deformation |
| **Mortar method** | Exact | Best | High | Critical applications |

---

## 5. Applications and Solver Selection Guide

| Application | Physics | Recommended Solver | Key Considerations |
|-------------|---------|-------------------|-------------------|
| **Heat exchanger** | CHT | `chtMultiRegionFoam` | Solid conductivity critical |
| **Electronics cooling** | CHT | `chtMultiRegionFoam` | Thin solid layers need refinement |
| **Flexible propeller** | FSI | `pimpleFoam` + structural | Strong coupling needed |
| **Blood flow** | FSI | External (preCICE) | Large deformation |
| **Combustor** | Reacting | `rhoReactingFoam` | Turbulence-chemistry interaction |
| **Fire modeling** | Reacting + Buoyancy | `rhoReactingBuoyantFoam` | Radiation important |
| **Wind turbine blade** | FSI | External (preCICE) | Aeroelastic effects |
| **Building thermal comfort** | CHT | `chtMultiRegionFoam` | Transient boundary conditions |

---

## 6. Multi-Region Case Structure

Complete multi-region case structure (example for CHT):

```
case/
├── 0/
│   ├── fluid/
│   │   ├── p           // Pressure
│   │   ├── U           // Velocity
│   │   ├── T           // Temperature
│   │   ├── k           // Turbulence kinetic energy
│   │   ├── omega       // Specific dissipation rate
│   │   └── alphat      // Thermal diffusivity
│   └── solid/
│       └── T           // Temperature only
│
├── constant/
│   ├── regionProperties        // Define regions
│   ├── fluid/
│   │   ├── polyMesh/
│   │   │   └── points, faces, owner, neighbour, boundary
│   │   └── thermophysicalProperties
│   └── solid/
│       ├── polyMesh/
│       │   └── points, faces, owner, neighbour, boundary
│       └── thermophysicalProperties
│
└── system/
    ├── fluid/
    │   ├── controlDict
    │   ├── fvSchemes
    │   └── fvSolution
    └── solid/
        ├── controlDict
        ├── fvSchemes
        └── fvSolution
```

**Key differences from single-region cases:**
1. Each region has its own `0/`, `constant/`, and `system/` subdirectories
2. `regionProperties` file lists all regions
3. Interface boundaries defined in BOTH regions
4. Each region can have different time steps, solvers, schemes

---

## 7. Troubleshooting Common Issues

### FSI-Specific Issues

| Symptom | Cause | Solution |
|---------|-------|----------|
| **Diverging displacements** | Weak coupling on flexible structure | Switch to strong coupling with more iterations |
| **Oscillating interface loads** | Insufficient under-relaxation | Reduce relaxation factor on displacement |
| **"No matching mapping" error** | Non-conforming interface mesh | Remesh with consistent interface or use interpolation |

### CHT-Specific Issues

| Symptom | Cause | Solution |
|---------|-------|----------|
| **Temperature jump at interface** | Inconsistent kappaMethod | Ensure one side uses `fluidThermo`, other uses `solidThermo` |
| **Very slow convergence** | Large thermal diffusivity ratio | Reduce time step, use implicit Euler |
| **Unphysical temperatures** | Wrong boundary condition type | Use `turbulentTemperatureCoupledBaffleMixed` at interfaces |

### Reacting Flow Issues

| Symptom | Cause | Solution |
|---------|-------|----------|
| **Blow-up (extreme temperatures)** | Time step too large for chemistry | Reduce `initialChemicalTimeStep` |
| **No reaction occurring** | Wrong reaction mechanism or temperature | Check activation energy, verify temperature range |
| **Species non-physical (>1 or <0)** | Insufficient transport time resolution | Refine mesh near reaction zone |

### General Multiphysics Tips

1. **Start simple:** Test each physics independently before coupling
2. **Initialize carefully:** Use physically reasonable initial conditions
3. **Monitor residuals:** Track convergence of all fields in all regions
4. **Use debug output:** Enable additional output for interface quantities
5. **Verify interface:** Check that interface patches have consistent face orientations

---

## 📚 Practical Exercises

### Exercise 1: Basic CHT Setup (30 minutes)

**Task:** Set up a conjugate heat transfer case for flow over a heated plate

**Steps:**
1. Create two regions: `fluid` (air) and `solid` (aluminum)
2. Set fluid inlet velocity to 1 m/s, inlet temperature to 300 K
3. Apply constant heat flux to bottom of solid (1000 W/m²)
4. Configure appropriate interface BCs
5. Run `chtMultiRegionFoam` for 1 second
6. Plot temperature profile through fluid-solid interface

**Expected outcome:** Temperature drop across solid due to convection to fluid

### Exercise 2: FSI Validation (45 minutes)

**Task:** Validate FSI setup using benchmark problem (Turek-Hron FSI3)

**Steps:**
1. Download benchmark geometry (flexible flag in channel)
2. Set up fluid region with `pimpleFoam`
3. Set up solid region with linear elastic material
4. Configure strong coupling with Aitken relaxation
5. Monitor tip displacement over time
6. Compare with reference values (max displacement ~10 mm)

**Expected outcome:** Stable periodic oscillation of flag tip

### Exercise 3: Multi-region Reacting Flow (60 minutes)

**Task:** Simulate methane-air combustion in a simple chamber

**Steps:**
1. Create 3 regions: fuel inlet, oxidizer inlet, combustion chamber
2. Configure CH4 + 2O2 → CO2 + 2H2O reaction
3. Set appropriate turbulence model (k-omega SST)
4. Apply ignition source (high temperature region)
5. Monitor flame propagation and species concentrations
6. Analyze heat release rate

**Expected outcome:** Stable flame with correct species distribution

---

## 🎯 Key Takeaways

- **Coupling strategy matters:** Weak coupling for one-way problems, strong for moderate coupling, monolithic for severe coupling
- **Interface conditions are critical:** Ensure continuity of primary variables (velocity, temperature) and fluxes (stress, heat flux)
- **CHT is relatively straightforward:** `chtMultiRegionFoam` handles most engineering heat transfer problems well
- **FSI is challenging:** Most practical FSI in OpenFOAM uses partitioned approach with external coupling (preCICE) for complex cases
- **Structure matters:** Multi-region cases require careful organization of directories and consistent boundary naming
- **Convergence monitoring:** Always monitor convergence in ALL regions, not just one
- **Start simple and verify:** Test each physics independently, then gradually add coupling complexity
- **Troubleshoot systematically:** Isolate whether issue is in fluid, solid, chemistry, or the coupling between them

---

## Concept Check

<details>
<summary><b>1. One-way vs Two-way FSI ต่างกันอย่างไร?</b></summary>

- **One-way (Weak coupling):** Fluid affects structure แต่ structure ไม่ affect fluid กลับ (เช่น ลมปะทะป้ายแข็ง)—ใช้ได้เมื่อโครงสร้างแข็งมาก
- **Two-way (Strong coupling):** ทั้งสองฝั่งมีผลต่อกัน (เช่น ใบพัดที่โค้งงอ) — ต้อง iterate จน convergence แต่ละ time step
</details>

<details>
<summary><b>2. CHT interface conditions มีอะไรบ้าง?</b></summary>

1. **Temperature continuity:** \(T_f = T_s\) — อุณหภูมิที่ interface เท่ากัน
2. **Heat flux continuity:** \(q_f = q_s\) — พลังงานที่ออกจาก fluid = พลังงานที่เข้า solid (conservation of energy)

ใน OpenFOAM: ใช้ `turbulentTemperatureCoupledBaffleMixed` BC โดยระบุ `kappaMethod` ให้แต่ละฝั่งใช้ conductivity ของตัวเอง
</details>

<details>
<summary><b>3. Partitioned vs Monolithic coupling ต่างกันอย่างไร?</b></summary>

- **Partitioned:** แยก solver (เช่น OpenFOAM + CalculiX) ส่งข้อมูลหากันผ่าน interface — ง่ายต่อการ implement ใช้ solver ที่มีอยู่ แต่อาจไม่เสถียรถ้า coupling แรงมาก
- **Monolithic:** รวมทุกสมการใน matrix เดียว \( \begin{bmatrix} A_{ff} & A_{fs} \\ A_{sf} & A_{ss} \end{bmatrix} \begin{bmatrix} U_f \\ U_s \end{bmatrix} = \begin{bmatrix} R_f \\ R_s \end{bmatrix} \) — เสถียรที่สุดแต่ซับซ้อนมาก ใช้ memory สูง
</details>

<details>
<summary><b>4. เมื่อไหร่ควรใช้ Aitken relaxation?</b></summary>

ใช้เมื่อ:
- Partitioned coupling และมีการ oscillate หรือ diverge
- Interface residuals ลู่เข้าช้า
- ไม่รู้ค่า optimal relaxation factor

Aitken ปรับ relaxation factor \(\omega\) อัตโนมัติจากประวัติ residual:
\[ \omega^{n+1} = \omega^n \frac{\langle \mathbf{r}^{n-1} - \mathbf{r}^n, \mathbf{r}^n \rangle}{\|\mathbf{r}^{n-1} - \mathbf{r}^n\|^2} \]
</details>

<details>
<summary><b>5. CHT case ที่มีหลาย solid regions จัดโครงสร้างไง?</b></summary>

```
constant/
├── regionProperties
regions (fluid solid1 solid2);

0/
├── fluid/
│   └── p, U, T, k, omega
├── solid1/
│   └── T
└── solid2/
    └── T
```

แต่ละ region มี thermophysicalProperties เป็นของตัวเอง และ interface ระหว่าง solid1-solid2 ก็ใช้ `turbulentTemperatureCoupledBaffleMixed` เหมือนกัน
</details>

---

## Related Documents

- **Prerequisites:** [01_Energy_Equation_Fundamentals](01_Energy_Equation_Fundamentals.md)
- **Advanced numerics:** [01_High_Performance_Computing](01_High_Performance_Computing.md) (for parallel multiphysics)
- **Turbulence:** [01_Turbulence_Fundamentals](03_TURBULENCE_MODELING/01_Turbulence_Fundamentals.md)
- **Overview:** [00_Overview](00_Overview.md)