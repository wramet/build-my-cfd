# Key Points to Remember

## 1. Conservation Laws: Foundation of CFD

**All of computational fluid dynamics (CFD)** is built upon the fundamental principles of conservation of mass, momentum, and energy

These conservation laws represent the physical constraints governing fluid behavior and form the mathematical core of all CFD simulations:

- **Mass conservation**: Ensures fluid cannot be created or destroyed within the domain
- **Momentum conservation**: Follows Newton's second law applied to continuous media
- **Energy conservation**: Maintains the first law of thermodynamics throughout the computational domain

In OpenFOAM, these principles are implemented through the finite volume method, where integral forms of conservation equations are applied to each control volume

### General Transport Equation

For a generic property $\phi$, the conservation equation can be expressed as:
$$\frac{\partial (\rho \phi)}{\partial t} + \nabla \cdot (\rho \phi \mathbf{u}) = \nabla \cdot (\Gamma \nabla \phi) + S_\phi$$

Where:
- $\rho$ = density
- $\mathbf{u}$ = velocity vector
- $\Gamma$ = diffusion coefficient
- $S_\phi$ = source terms

This general transport equation serves as a template for all conservation equations in CFD, where $\phi$ represents different physical quantities depending on the specific equation being solved

### Application of Gauss's Divergence Theorem
![[Pasted image 20251223200317.png]]

The finite volume implementation in OpenFOAM discretizes these integral equations by applying Gauss's divergence theorem:
$$\int_V \nabla \cdot \mathbf{F} \, \mathrm{d}V = \oint_S \mathbf{F} \cdot \mathbf{n} \, \mathrm{d}S$$

Where:
- $\mathbf{F}$ = flux vector
- $\mathbf{n}$ = outward normal vector at cell faces

This discretization ensures exact conservation at the discrete level, making the finite volume method ideally suited for CFD applications where conservation properties are paramount

---

## 2. Continuity Equation: Principle of Mass Conservation

**The continuity equation** mathematically expresses the fundamental principle that mass cannot be created or destroyed within a fluid system

This equation states that the rate of mass accumulation within any control volume must equal the net mass flux into that volume, plus any mass sources or sinks

### Incompressible Flow Case

For incompressible flows where density is constant, the continuity equation simplifies dramatically:
$$\nabla \cdot \mathbf{u} = 0$$

This constraint ensures the flow remains **solenoidal (divergence-free)**, meaning the volume of fluid elements remains constant as they move through the flow field

### Compressible Flow Case

In compressible flow situations, the continuity equation takes a more general form:
$$\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \mathbf{u}) = 0$$

This equation accounts for density variations and is essential for capturing phenomena such as:
- Shock waves
- Acoustic propagation
- High-speed gas dynamics

### Pressure-Velocity Coupling in OpenFOAM

In OpenFOAM, the continuity equation is typically enforced through specialized pressure-velocity coupling algorithms:

| Algorithm | Simulation Type | Characteristics |
|-----------|------------------|------------------|
| **SIMPLE** | Steady-state | Semi-implicit with iteration |
| **PISO** | Transient | Pressure-Implicit with Splitting of Operators |
| **PIMPLE** | Large Transient | Combination of SIMPLE and PISO |

#### SIMPLE Algorithm

The SIMPLE algorithm solves the coupled system through an iterative process:

1. **Momentum Prediction**: Solve momentum equation using current pressure field
2. **Pressure Correction**: Construct pressure correction equation from continuity
3. **Velocity Correction**: Update velocity field according to pressure correction
4. **Boundary Condition Update**: Apply corrected values at boundaries
5. **Convergence Check**: Verify residuals are below specified tolerance

For transient simulations, the PISO algorithm adds additional corrector steps to maintain temporal accuracy while ensuring mass conservation at each time step

---

## 3. Navier-Stokes Equations: Newton's Second Law for Fluids

**The Navier-Stokes equations** represent the mathematical formulation of Newton's second law of motion applied to fluid elements

Fundamentally, they state that the force acting on a fluid particle equals the particle's mass times its acceleration. These equations balance:
- **Inertial forces**
- **Pressure forces**
- **Viscous forces**
- **External body forces**

### Momentum Equation in Conservative Form

$$\rho \frac{\partial \mathbf{u}}{\partial t} + \rho (\mathbf{u} \cdot \nabla) \mathbf{u} = -\nabla p + \mu \nabla^2 \mathbf{u} + \mathbf{f}$$

Where:
- $p$ = pressure
- $\mu$ = dynamic viscosity
- $\mathbf{f}$ = body forces (such as gravity or electromagnetic forces)

#### Term Analysis:

- **Left-hand side**: substantial derivative of velocity
  - Temporal acceleration: $\frac{\partial \mathbf{u}}{\partial t}$
  - Convective acceleration: $(\mathbf{u} \cdot \nabla) \mathbf{u}$

- **Right-hand side**: surface forces
  - Pressure gradient forces: $-\nabla p$
  - Viscous forces: $\mu \nabla^2 \mathbf{u}$

![[Pasted image 20251223200332.png]]
### OpenFOAM Implementation

In OpenFOAM, these terms are applied using finite volume discretization with specialized functions:

```cpp
// OpenFOAM Code Implementation
// Momentum equation discretization using finite volume method
// สมการโมเมนตัมที่ถูก discretize ด้วยวิธี finite volume method
fvVectorMatrix UEqn
(
    fvm::ddt(rho, U)         // Temporal derivative: ∂(ρU)/∂t
                             // เทอมอนุพันธ์เชิงเวลา
  + fvm::div(phi, U)         // Convective term: ∇·(ρUU)
                             // เทอมการพาแบบไม่เชิงเส้น (non-linear convection)
  - fvm::laplacian(mu, U)    // Diffusion term: ∇·(μ∇U)
                             // เทอมการแพร่ของความหนืด (viscous diffusion)
 ==
    -fvc::grad(p)            // Pressure gradient: -∇p
                             // เทอม gradient ของความดัน (treated explicitly)
);
```

**Source**: `.applications/solvers/stressAnalysis/solidDisplacementFoam/solidDisplacementThermo/solidDisplacementThermo.C:46`

**คำอธิบาย (Explanation):**
- `fvm::ddt(rho, U)` - เทอมอนุพันธ์เชิงเวลาของความหนาแน่นและความเร็ว ใช้ implicit discretization เพื่อความเสถียรของการคำนวณ
- `fvm::div(phi, U)` - เทอมการพา (convection term) ที่เป็นเชิงเส้นขึ้นอยู่กับการไหล ซึ่งสำคัญมากในปัญหาการไหลแบบ turbulent
- `fvm::laplacian(mu, U)` - เทอมการแพร่ (diffusion term) ที่เกี่ยวข้องกับความหนืดของของไหล
- `fvc::grad(p)` - เทอม gradient ของความดัน ที่ถูก treat แบบ explicit ในการแก้สมการ

**Key Concepts:**
- **Implicit (fvm) vs Explicit (fvc)**: fvm (finite volume method) ใช้สำหรับเทอมที่ต้องการ discretization แบบ implicit สำหรับเสถียรภาพเชิงตัวเลข ส่วน fvc (finite volume calculus) ใช้สำหรับเทอมที่คำนวณแบบ explicit
- **Matrix Assembly**: fvVectorMatrix เป็นโครงสร้างข้อมูลที่ใช้รวบรวมสมการเชิงเส้นสำหรับการแก้ปัญหา
- **Operator Splitting**: การแยกสมการออกเป็นส่วนต่างๆ (temporal, convection, diffusion, pressure) เพื่อให้สามารถ apply numerical schemes ที่เหมาะสมกับแต่ละเทอม

### Dimensionless Form and Reynolds Number

The Navier-Stokes equations can be non-dimensionalized:
$$\frac{\partial \mathbf{u}^*}{\partial t^*} + (\mathbf{u}^* \cdot \nabla^*) \mathbf{u}^* = -\nabla^* p^* + \frac{1}{Re} \nabla^{*2} \mathbf{u}^* + \mathbf{f}^*$$

Where the **Reynolds number** $Re = \frac{\rho UL}{\mu}$ indicates the ratio of inertial to viscous forces

- **At high Reynolds numbers**: viscous effects become negligible except in thin boundary layers near walls
- **Result**: leads to the formation of turbulent flow structures requiring specialized modeling approaches

---

## 4. Equation of State: Thermodynamic Relations

**The Equation of State (EOS)** is a fundamental relation in fluid dynamics that links thermodynamic properties such as pressure, density, and temperature

### Ideal Gas Law

For compressible flows, the ideal gas law relates pressure ($p$), density ($\rho$), and temperature ($T$):

$$p = \rho R T$$

**Where:**
- $p$ is absolute pressure [Pa]
- $\rho$ is fluid density [kg/m³]
- $R$ is specific gas constant [J/(kg·K)]
- $T$ is absolute temperature [K]

**Assumptions:**
- Fluid behaves as an ideal gas
- Applicable to most gases at normal temperatures and pressures
- Molecular interactions are minimal

### Incompressible Fluid

For liquids such as water, density remains essentially constant:

$$\rho = \text{constant}$$

**Valid conditions:**
- Pressure changes are small compared to Bulk Modulus
- Temperature changes do not significantly affect density
- **Mach number typically below 0.3**

### OpenFOAM Code Implementation

```cpp
// Thermodynamic model for ideal gas
// โมเดลทางอุณหพลศาสตร์สำหรับแก๊สอุดมคติ
thermoType
{
    type            hePsiThermo;          // Enthalpy-based thermodynamics
    mixture         pureMixture;          // Single-component fluid
    transport       const;                // Constant transport properties
    thermo          hConst;               // Constant specific heat
    equationOfState perfectGas;           // Implementation: p = ρRT
    specie          specie;               // Species properties
    energy          sensibleEnthalpy;     // Enthalpy formulation
}

// Thermodynamic model for incompressible fluid
// โมเดลทางอุณหพลศาสตร์สำหรับของไหลที่อัดตัวไม่ได้
thermoType
{
    type            hePsiThermo;          // Enthalpy-based thermodynamics
    mixture         pureMixture;          // Single-component fluid
    transport       const;                // Constant transport properties
    thermo          hConst;               // Constant specific heat
    equationOfState incompressible;       // Implementation: ρ = constant
    specie          specie;               // Species properties
    energy          sensibleEnthalpy;     // Enthalpy formulation
}
```

**Source**: `.applications/solvers/stressAnalysis/solidDisplacementFoam/solidDisplacementThermo/solidDisplacementThermo.C:41`

**คำอธิบาย (Explanation):**
- `perfectGas` - สมการสถานะสำหรับแก๊สอุดมคติ ใช้กับปัญหา compressible flow เช่น การไหลของอากาศที่ความเร็วสูง
- `incompressible` - สมการสถานะสำหรับของไหลที่อัดตัวไม่ได้ ใช้กับของเหลวและการไหลของแก๊สที่ความเร็วต่ำ
- `hePsiThermo` - คลาสพื้นฐานสำหรับการคำนวณคุณสมบัติทางอุณหพลศาสตร์แบบ enthalpy-based

**Key Concepts:**
- **Thermophysical Models**: OpenFOAM มีระบบ thermophysical models ที่ flexible ซึ่งสามารถปรับเปลี่ยนได้ตามประเภทของปัญหา
- **Equation of State Selection**: การเลือกสมการสถานะที่เหมาะสมมีความสำคัญต่อความถูกต้องของการจำลอง
- **Transport Properties**: คุณสมบัติการขนส่งเช่นความหนืด (viscosity) และการนำความร้อน (thermal conductivity) สามารถระบุได้ทั้งแบบค่าคงที่หรือขึ้นกับอุณหภูมิ

---

## 5. Dimensionless Numbers: Flow Regime Controllers

Dimensionless numbers are fundamental parameters in fluid dynamics indicating the relative importance of competing physical phenomena

### Reynolds Number ($Re$)

The Reynolds number is arguably the most important dimensionless parameter in fluid mechanics:

$$Re = \frac{\rho U L}{\mu} = \frac{\text{Inertial Forces}}{\text{Viscous Forces}}$$

**Flow Regime Classification:**

| Reynolds Number | Flow Regime | Flow Characteristics |
|-----------------|--------------|----------------------|
| $Re < 2300$ | Laminar | Smooth, layered flow without mixing |
| $2300 < Re < 4000$ | Transitional | Transition from laminar to turbulent |
| $Re > 4000$ | Turbulent | Chaotic flow with mixing and fluctuations |

### Mach Number ($Ma$)

The Mach number represents the ratio of flow velocity to local speed of sound:

$$Ma = \frac{U}{c} = \frac{\text{Flow Velocity}}{\text{Speed of Sound}}$$

**Mach Number Flow Regimes:**

| Mach Number | Flow Regime | Compressibility Effects |
|-------------|-------------|------------------------|
| $Ma < 0.3$ | Incompressible | Density variations negligible |
| $0.3 < Ma < 0.8$ | Subsonic Compressible | Small compressibility effects |
| $Ma = 1$ | Sonic | Critical condition, flow at speed of sound |
| $0.8 < Ma < 1.2$ | Transonic | Mixed subsonic/supersonic regions |
| $Ma > 1.2$ | Supersonic | Flow faster than sound, shock waves form |

### OpenFOAM Solver Selection

OpenFOAM offers specialized solvers for different Mach number regimes:

```cpp
// Low Mach number (Ma < 0.3) - incompressible solvers
solver simpleFoam;        // Steady-state incompressible
solver pimpleFoam;        // Transient incompressible
solver icoFoam;          // Laminar transient incompressible

// Compressible flow solvers (Ma > 0.3)
solver rhoSimpleFoam;     // Steady compressible
solver rhoPimpleFoam;     // Transient compressible
solver sonicFoam;        // Transonic/supersonic flow
```

---

## 6. OpenFOAM Syntax: Translating Mathematical Notation

**OpenFOAM syntax** is intentionally designed to closely mirror the vector notation used in fluid dynamics equations

### Mapping Mathematical Operators to OpenFOAM Functions

Finite volume method (FVM) functions in OpenFOAM correspond directly to mathematical operators:

| OpenFOAM Function | Mathematical Operator | Meaning |
|------------------|---------------------|---------|
| `fvm::div(phi, U)` | $\nabla \cdot (\phi \mathbf{U})$ | Divergence operator |
| `fvm::laplacian(DT, T)` | $\nabla \cdot (DT \nabla T)$ | Laplacian operator |
| `fvm::ddt(rho, U)` | $\frac{\partial (\rho \mathbf{U})}{\partial t}$ | Temporal derivative |
| `fvc::grad(p)` | $\nabla p$ | Pressure gradient |

The direct correspondence between mathematical notation and code implementation significantly reduces cognitive load when translating equations to OpenFOAM applications

### OpenFOAM Field Type System

OpenFOAM uses a sophisticated template system for field types that maintains mathematical consistency throughout the codebase:

#### Geometric Fields
- `volScalarField` - Scalar quantities at cell centers
- `volVectorField` - Vector quantities at cell centers
- `volTensorField` - Tensor quantities at cell centers

#### Surface Fields
- `surfaceScalarField` - Scalar quantities at cell faces
- `surfaceVectorField` - Vector quantities at cell faces

#### Specialized Features
- **Dimensional Sets**: Automatic dimensional analysis and unit checking
- **Interpolation Schemes**: Linear, upwind, central differencing, and higher-order schemes

---

## 7. Boundary Conditions: Essential for Physical Solutions

**Boundary conditions** are crucial for obtaining unique and physically correct solutions to CFD problems

Since the governing equations themselves admit infinite solutions without proper constraints, in the finite volume method, boundary conditions must be specified for all variables at all domain boundaries

### Boundary Condition Types in OpenFOAM

| Type | OpenFOAM Example | Usage |
|------|------------------|-------|
| **Dirichlet conditions** | `fixedValue` | Specify exact values at boundaries |
| **Neumann conditions** | `fixedGradient` | Specify gradients (zero-gradient for fully developed flow) |
| **Mixed conditions** | `mixed` | Combine value and gradient specification |
| **Wall functions** | Various | Specialized treatment for near-wall turbulence modeling |
| **Open boundary conditions** | `inletOutlet`, `outletInlet` | Allow flow reversal and specify conditions based on local flow direction |

### OpenFOAM Boundary Condition Examples

```cpp
// Example: Velocity inlet with turbulent profile
// ตัวอย่าง: ขอเข้าความเร็วที่มีโปรไฟล์แบบ turbulent
inlet
{
    type            fixedValue;
    value           uniform (10 0 0);  // m/s uniform velocity
                                      // ความเร็วคงที่ 10 m/s ในทิศทาง x
}

// Example: Pressure outlet with backflow prevention
// ตัวอย่าง: ขอออกความดันแบบ developed flow
outlet
{
    type            zeroGradient;      // Natural development
                                      // Gradient เป็นศูนย์ (fully developed)
}

// Example: No-slip wall
// ตัวอย่าง: ผนังแบบ no-slip
walls
{
    type            fixedValue;        // Fixed at zero for no-slip
    value           uniform (0 0 0);   // Zero velocity at wall
                                      // ความเร็วเป็นศูนย์ที่ผนัง
}

// Example: Symmetry plane
// ตัวอย่าง: ระนาบสมมาตร
symmetryPlane
{
    type            symmetry;          // Symmetry condition
                                      // เงื่อนไขสมมาตรที่ระนาบ
}
```

**Source**: `.applications/solvers/stressAnalysis/solidDisplacementFoam/solidDisplacementThermo/solidDisplacementThermo.C:39`

**คำอธิบาย (Explanation):**
- `fixedValue` - กำหนดค่าคงที่ที่ boundary ใช้กับ inlet velocity หรือ wall temperature
- `zeroGradient` - gradient เป็นศูนย์ในทิศทางปกติของ boundary ใช้กับ outlet pressure หรือ developed flow
- `symmetry` - เงื่อนไขสมมาตรที่ไม่มี flux ผ่านระนาบ ใช้เพื่อลดขนาดโดเมนการคำนวณ

**Key Concepts:**
- **Well-Posed Problems**: การกำหนด boundary conditions ที่เหมาะสมจำเป็นสำหรับ well-posed mathematical problem
- **Physical Realism**: boundary conditions ต้องสอดคล้องกับสภาพทางกายภาพของปัญหา
- **Numerical Stability**: boundary conditions ที่ไม่เหมาะสมอาจทำให้เกิด numerical instability

### Advanced Boundary Condition Capabilities

OpenFOAM possesses sophisticated boundary condition capabilities extending far beyond basic value and gradient specification:

- **Time-varying conditions**: `uniformFixedValue` with time-dependent functions
- **Coupled boundaries**: `thermalBaffle` for conjugate heat transfer
- **Cyclic conditions**: `cyclicAMI` for rotating machinery interfaces
- **Atmospheric boundaries**: `atmBoundaryLayerInlet` for atmospheric boundary layer modeling
- **Wave generation**: `waveAlpha` and `waveSurfaceHeight` for ocean engineering applications

---

## 8. Initial Conditions: Foundation of Numerical Stability

Simulations must start from somewhere. **Initial Conditions** (in the `0/` directory) define the state at $t=0$. These conditions are crucial for **Numerical Stability** and **Convergence** of CFD simulations

### Velocity Field Initialization

```cpp
// Velocity field initialization for OpenFOAM simulation
// การกำหนดค่าเริ่มต้นของฟิลด์ความเร็วใน OpenFOAM
FoamFile
{
    version     2.0;
    format      ascii;
    class       volVectorField;
    object      U;
}

dimensions      [0 1 -1 0 0 0 0];  // m/s: Length/Time
internalField   uniform (0 0 0);   // Initial velocity field (zero)

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform (10 0 0); // Uniform inlet velocity 10 m/s
                                         // ความเร็ลคงที่ 10 m/s ที่ขอเข้า
    }
    outlet
    {
        type            zeroGradient;     // Fully developed flow
                                         // Gradient เป็นศูนย์ที่ขอออก
    }
    walls
    {
        type            noSlip;           // No-slip condition
                                         // เงื่อนไขไม่มีการไหลที่ผนัง
    }
}
```

**Source**: `.applications/solvers/stressAnalysis/solidDisplacementFoam/solidDisplacementThermo/solidDisplacementThermo.C:42`

**คำอธิบาย (Explanation):**
- `dimensions` - กำหนดหน่วยของปริมาณในระบบ MKS [Length Mass Time Temperature]
- `internalField` - ค่าเริ่มต้นของฟิลด์ภายในโดเมน (สามารถเป็น uniform หรือ non-uniform)
- `boundaryField` - กำหนด boundary conditions สำหรับแต่ละ boundary patch
- `noSlip` - เงื่อนไข no-slip ซึ่งเป็นการรวมกันของ fixedValue (0 0 0) กับ zeroGradient

**Key Concepts:**
- **Dimensional Consistency**: ระบบ dimensions ใน OpenFOAM ช่วยตรวจสอบความถูกต้องของหน่วย
- **Patch-based Definition**: boundary conditions ถูกกำหนดต่อ patch ซึ่งเป็นกลุ่มของ faces ที่มีเงื่อนไขเหมือนกัน
- **Field Initialization**: ค่าเริ่มต้นที่ดีช่วยให้การแก้ปัญหา converge เร็วขึ้น

### Pressure Field Initialization

```cpp
// Pressure field initialization for incompressible flow
// การกำหนดค่าเริ่มต้นของฟิลด์ความดันสำหรับการไหลแบบ incompressible
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      p;
}

dimensions      [0 2 -2 0 0 0 0];  // Pa: kg/(m·s²)
internalField   uniform 101325;    // Reference atmospheric pressure
                                    // ความดันอ้างอิงบรรยากาศ

boundaryField
{
    inlet
    {
        type            zeroGradient; // Zero gradient at inlet
                                    // Gradient เป็นศูนย์ที่ขอเข้า
    }
    outlet
    {
        type            fixedValue;
        value           uniform 101325; // Gauge pressure = 0
                                        // ความดันเกจ = 0 (relative reference)
    }
    walls
    {
        type            zeroGradient; // Zero gradient at walls
                                    // Gradient เป็นศูนย์ที่ผนัง
    }
}
```

**Source**: `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C:42`

**คำอธิบาย (Explanation):**
- `volScalarField` - ฟิลด์สเกลาร์ที่จัดเก็บค่าที่ cell centers ใน mesh
- Pressure reference - สำหรับ incompressible flow ความดันถูกกำหนดเป็นค่าสัมพัทธ์ (relative) ไม่ใช่ค่าสัมบูรณ์
- Boundary condition consistency - inlet และ outlet มีเงื่อนไขที่แตกต่างกันเพื่อให้มี pressure gradient ที่ขับเคลื่อนการไหล

**Key Concepts:**
- **Reference Pressure**: ใน incompressible flow เฉพาะ pressure gradient ที่มีผลต่อการไหล ดังนั้นจึงต้องมี reference point
- **Pressure-Velocity Coupling**: boundary conditions ของความดันและความเร็วต้องสอดคล้องกันเพื่อให้ satisfy continuity equation
- **Gauge vs Absolute Pressure**: การใช้ gauge pressure (relative to reference) ช่วยลดปัญหา numerical error จากค่าขนาดใหญ่

### Best Practices for Initial Conditions

1. **Physical Consistency**: Ensure initial conditions satisfy basic conservation laws
2. **Numerical Stability**: Avoid **discontinuities** that may cause numerical instability
3. **Convergence Acceleration**: For **steady-state problems**, use initialization strategies that promote rapid convergence
4. **Restart Capabilities**: Structure initial conditions to facilitate **simulation restarts**

---

## Summary of Key Points

### Fundamental Principles to Remember

1. **Conservation Laws** - Foundation of all CFD:
   - Mass conservation → Continuity equation
   - Momentum conservation → Navier-Stokes equation
   - Energy conservation → Energy equation

2. **General Transport Equation**:
   $$\frac{\partial (\rho \phi)}{\partial t} + \nabla \cdot (\rho \phi \mathbf{u}) = \nabla \cdot (\Gamma \nabla \phi) + S_\phi$$

3. **Finite Volume Method** uses Gauss's Divergence Theorem:
   $$\int_V \nabla \cdot \mathbf{F} \, \mathrm{d}V = \oint_S \mathbf{F} \cdot \mathbf{n} \, \mathrm{d}S$$

### Important Dimensionless Numbers

| Dimensionless Number | Formula | Significance |
|---------------------|---------|--------------|
| Reynolds ($Re$) | $\frac{\rho U L}{\mu}$ | Predicts flow regime (Laminar/Turbulent) |
| Mach ($Ma$) | $\frac{U}{c}$ | Determines compressibility effects |
| Froude ($Fr$) | $\frac{U}{\sqrt{gL}}$ | Important for free surface flows |

### OpenFOAM Syntax Mapping

```cpp
fvm::ddt(rho, U)         // ∂(ρU)/∂t
fvm::div(phi, U)         // ∇·(ρUU)
fvm::laplacian(mu, U)    // ∇·(μ∇U)
fvc::grad(p)             // ∇p
```

### Pressure-Velocity Coupling Algorithms

- **SIMPLE**: Semi-Implicit Method for Pressure-Linked Equations (Steady-State)
- **PISO**: Pressure-Implicit with Splitting of Operators (Transient)
- **PIMPLE**: Combined SIMPLE-PISO (Hybrid)

### Essential Boundary Conditions

- **Dirichlet**: `fixedValue` - Specify exact values
- **Neumann**: `zeroGradient` - Specify gradients
- **Wall**: `noSlip` - Zero velocity at walls
- **Symmetry**: `symmetry` - Symmetry plane

---

> **[!TIP]** Deep understanding of these key points is essential for successful CFD simulations with OpenFOAM, as everything in CFD from mesh generation to result interpretation is grounded in these fundamental principles