# Coupled Physics Fundamentals

พื้นฐานทางทฤษฎีของ Coupled Physics

---

## 🎯 Learning Objectives

หลังจากอ่านบทนี้ คุณจะสามารถ:
- Understand the mathematical formulation of multi-physics coupling (What)
- Apply coupling algorithms and convergence criteria (How)
- Choose appropriate coupling schemes based on physics characteristics (Why)
- Implement interface boundary conditions for different coupling types (How)

---

## Overview

This file provides the **theoretical foundation** for coupled physics simulations. For a catalog of coupling types and solver selection, see [00_Overview.md](00_Overview.md).

> **Coupled Physics Theory** = Mathematical framework describing how different physics domains interact through shared interfaces

---

## 1. Mathematical Formulation

### 1.1 Governing Equations for Coupled Systems

For a coupled system with domains Ω₁ and Ω₂ sharing interface Γ:

**Domain Ω₁ (e.g., fluid):**
```cpp
// Continuity
∂ρ₁/∂t + ∇·(ρ₁u₁) = 0

// Momentum
∂(ρ₁u₁)/∂t + ∇·(ρ₁u₁⊗u₁) = -∇p₁ + ∇·τ₁ + f₁

// Energy
∂(ρ₁e₁)/∂t + ∇·(ρ₁u₁e₁) = -p₁∇·u₁ + ∇·(k₁∇T₁) + Q₁
```

**Domain Ω₂ (e.g., solid):**
```cpp
// Energy (heat conduction)
∂(ρ₂c₂T₂)/∂t = ∇·(k₂∇T₂) + Q₂

// Or structural equilibrium
∇·σ₂ + f₂ = 0
```

### 1.2 Interface Conditions

At interface Γ, **continuity conditions** must be satisfied:

**CHT Interface (Dirichlet-Neumann):**
```cpp
// Temperature continuity (Dirichlet)
T₁|Γ = T₂|Γ

// Heat flux continuity (Neumann)
-k₁(∂T₁/∂n)|Γ = -k₂(∂T₂/∂n)|Γ
```

**FSI Interface (Kinematic + Dynamic):**
```cpp
// Kinematic (velocity matching)
u₁|Γ = ∂d₂/∂t|Γ  // fluid velocity = solid velocity

// Dynamic (force equilibrium)
σ₁·n₁ + σ₂·n₂ = 0  // fluid stress = solid stress

// Geometric (position)
Γ₁ = Γ₂  // interface positions match
```

---

## 2. Coupling Algorithms

### 2.1 Weak (Explicit) Coupling

**Algorithm:**
```cpp
// Pseudo-code for weak coupling
for (runTime; !runTime.end(); ++runTime)
{
    // Solve each region sequentially
    forAll(fluidRegions, i)
    {
        solveFluidRegion(fluidRegions[i]);
    }
    
    forAll(solidRegions, i)
    {
        solveSolidRegion(solidRegions[i]);
    }
    
    // No iteration between regions
    // Interface data from previous timestep
}
```

**Mathematical Form:**
```
u_f^(n+1) = solve(u_f^n, T_s^n)
T_s^(n+1) = solve(T_f^(n+1), T_s^n)
```

**Stability Criterion:**
```
Δt < Δt_critical ∝ (L/c_s) · (ρ_s/ρ_f)
```
where L = characteristic length, c_s = wave speed in solid

<details>
<summary><b>🔧 When to Use Weak Coupling</b></summary>

**Appropriate when:**
- Density ratio ρ_f/ρ_s << 1 (e.g., gas-structure)
- Thermal timescales are well-separated
- Interaction is weak (one-way dominated)
- Computational cost is critical

**Typical applications:**
- Air-cooled heat sinks
- Buoyancy-driven ventilation
- Low-speed gas-particle flows
</details>

### 2.2 Strong (Implicit) Coupling

**Algorithm:**
```cpp
// Pseudo-code for strong coupling
for (runTime; !runTime.end(); ++runTime)
{
    scalar residual = GREAT;
    
    do
    {
        scalar residualOld = residual;
        
        // Solve all regions
        forAll(fluidRegions, i)
        {
            solveFluidRegion(fluidRegions[i]);
        }
        
        forAll(solidRegions, i)
        {
            solveSolidRegion(solidRegions[i]);
        }
        
        // Check convergence
        residual = max(
            fluidRegion.residual(),
            solidRegion.residual()
        );
        
    } while (residual > convergenceTolerance 
             && residual < 0.9 * residualOld);
}
```

**Mathematical Form:**
```
Solve iteratively until:
||u_f^(k+1) - u_f^k|| < ε
||T_s^(k+1) - T_s^k|| < ε
```

**Convergence Acceleration:**
```cpp
// Under-relaxation for stability
T_interface_new = ω·T_interface_calculated + (1-ω)·T_interface_old

// Typical values
ω = 0.5 - 0.9  // Lower for tighter coupling
```

<details>
<summary><b>🔧 When to Use Strong Coupling</b></summary>

**Appropriate when:**
- Density ratio ρ_f/ρ_s ≈ 1 (e.g., water-structure)
- Two-way interaction is significant
- Stability is critical
- Accuracy requirements are high

**Typical applications:**
- Hydraulic FSI (valves, pistons)
- Blood flow-vessel wall interaction
- High-density particle flows
- Conjugate heat transfer with high heat flux
</details>

### 2.3 Monolithic Coupling (Theoretical)

**Mathematical Form:**
```cpp
// Single matrix system
| A_ff  A_fs | | u_f |   | b_f |
| A_sf  A_ss | | u_s | = | b_s |

// Where off-diagonal blocks couple physics
// A_fs = coupling from solid to fluid
// A_sf = coupling from fluid to solid
```

**Comparison with OpenFOAM's Approach:**

| Approach | Matrix Structure | Solver | OpenFOAM Support |
|----------|-----------------|--------|------------------|
| **Monolithic** | Fully coupled | Direct/Iterative on full matrix | Limited (requires custom coding) |
| **Partitioned** | Block-diagonal | Separate solvers + iteration | Native (chtMultiRegionFoam, etc.) |

OpenFOAM primarily uses **partitioned approach** due to:
- Modular solver architecture
- Flexibility in physics combinations
- Lower memory requirements
- Code reusability

---

## 3. Convergence Criteria

### 3.1 Interface Residuals

```cpp
// Temperature residual at interface
scalar T_residual = max(
    mag(T_fluid.boundaryField()[interfaceID] 
      - T_solid.boundaryField()[interfaceID])
);

// Heat flux residual
scalar q_residual = max(
    mag(q_fluid.boundaryField()[interfaceID] 
      - q_solid.boundaryField()[interfaceID])
) / max(mag(q_solid.boundaryField()[interfaceID]));
```

### 3.2 Typical Tolerances

| Coupling Type | Variable | Tolerance |
|---------------|----------|-----------|
| **Weak** | Any | 10⁻³ to 10⁻⁴ (not critical) |
| **Strong** | Temperature | 10⁻⁴ to 10⁻⁶ |
| **Strong** | Velocity/Force | 10⁻³ to 10⁻⁵ |
| **Strong** | Heat flux | 10⁻³ to 10⁻⁴ |

```cpp
// Example fvSolution settings
coupling
{
    nCorrectors      10;      // Max iterations
    tolerance        1e-6;    // Absolute tolerance
    relTolerance     1e-3;    // Relative tolerance
    relaxation       0.8;     // Under-relaxation factor
}
```

### 3.3 Convergence Monitoring

```cpp
// Log convergence info
if (couplingIter % 10 == 0)
{
    Info<< "Coupling iteration: " << couplingIter << nl
        << "  T_residual: " << T_residual << nl
        << "  q_residual: " << q_residual << nl
        << "  U_residual: " << U_residual << endl;
}
```

---

## 4. Partitioned Implementation in OpenFOAM

### 4.1 Multi-Region Solver Architecture

```cpp
// Typical chtMultiRegionFoam structure
int main(int argc, char *argv[])
{
    // Create time
    Time runTime(Time::controlDictName, args);
    
    // Create meshes for all regions
    const wordList regionNames =
        regionProperties::readRegionNames(args);
    
    PtrList<fvMesh> fluidRegions(regionNames.size());
    PtrList<fvMesh> solidRegions(regionNames.size());
    
    // Create fields for each region
    PtrList<volScalarField> TFluids(regionNames.size());
    PtrList<volVectorField> UFluids(regionNames.size());
    PtrList<volScalarField> pFluids(regionNames.size());
    PtrList<volScalarField> TSolids(regionNames.size());
    
    // Time loop
    while (runTime.loop())
    {
        // Strong coupling outer loop
        for (int couplingIter = 0; couplingIter < nCorr; couplingIter++)
        {
            // Solve fluid regions
            forAll(fluidRegions, i)
            {
                solveFluidRegion(i);
            }
            
            // Solve solid regions
            forAll(solidRegions, i)
            {
                solveSolidRegion(i);
            }
            
            // Check convergence
            if (converged()) break;
        }
        
        runTime.write();
    }
}
```

### 4.2 Interface Data Transfer

```cpp
// Boundary condition coupling
// At fluid region
TFluid.boundaryFieldRef()[interfaceID] = 
    TSolid.boundaryField()[interfaceID];

// Heat flux calculation
qFluid = -kFluid * TFluid.boundaryField()[interfaceID].snGrad();

// At solid region  
qSolid = -kSolid * TSolid.boundaryField()[interfaceID].snGrad();

// Flux balance enforced implicitly
// by the coupled boundary condition
```

### 4.3 Under-Relaxation Strategies

```cpp
// Fixed under-relaxation
T_new = relax * T_calculated + (1 - relax) * T_old;

// Adaptive under-relaxation (Aitken's method)
scalar omega = omega_old;
scalar delta = T_calculated - T_old;
scalar residual = mag(T_new - T_old);

omega = omega_old * (residual_old / residual);
omega = max(0.1, min(0.9, omega));  // Clamp
```

---

## 5. Stability Analysis

### 5.1 Added Mass Effect (FSI)

For fluid-structure interaction with ρ_f ≈ ρ_s:

```cpp
// Stability condition
Δt < 2/ω_n · sqrt(ρ_s/ρ_f - 1)

// where ω_n = natural frequency of structure
```

**Consequences:**
- Weak coupling becomes unstable for ρ_f/ρ_s > 0.1
- Strong coupling required for water-structure systems
- Artificial compressibility can improve stability

### 5.2 Thermal Coupling Stability

```cpp
// Explicit stability limit
Δt < (ρcV/2hA)  // Fourier number constraint

// where:
// h = heat transfer coefficient
// A = interface area
// V = element volume
// c = specific heat
```

---

## 📊 Key Takeaways

1. **Interface conditions** enforce continuity of primary variables and fluxes
2. **Weak coupling** is efficient for loose interactions (ρ_f/ρ_s << 1)
3. **Strong coupling** is required for tight interactions (ρ_f/ρ_s ≈ 1)
4. **Under-relaxation** (ω = 0.5-0.9) stabilizes strong coupling iterations
5. **Convergence criteria** should monitor both variable and flux residuals
6. **OpenFOAM uses partitioned approach** - separate solvers with interface iteration
7. **Monolithic coupling** offers better stability but requires custom implementation

---

## 🧠 Concept Check

<details>
<summary><b>1. เมื่อไหร่ต้องใช้ Strong Coupling แทน Weak Coupling?</b></summary>

**ใช้ Strong Coupling เมื่อ:**

1. **Density ratio ใกล้เคียงกัน:** ρ_f/ρ_s ≈ 1 (เช่น น้ำ-โครงสร้าง)
2. **Two-way interaction รุนแรง:** Fluid ส่งผลต่อ solid มาก และกลับกัน
3. **Added mass effect ชัดเจน:** Fluid mass เปลี่ยน natural frequency ของ structure
4. **Convergence ไม่เสถียร:** Weak coupling แก้ไม่ลู่เข้า

**ตัวอย่าง:**
- ✅ Strong: Blood flow (ρ ≈ 1060 kg/m³) ใน blood vessel (ρ ≈ 1200 kg/m³)
- ✅ Strong: Hydraulic piston ในน้ำมัน
- ❌ Weak: Air flow (ρ ≈ 1.2 kg/m³) ผ่าน steel structure (ρ ≈ 7800 kg/m³)

</details>

<details>
<summary><b>2. Interface Conditions ที่ต้องการสำหรับ CHT?</b></summary>

**CHT Interface ต้องมี 2 continuity conditions:**

```cpp
// 1. Temperature continuity (Dirichlet)
T_fluid|interface = T_solid|interface

// 2. Heat flux continuity (Neumann)
q_fluid = q_solid
-k_fluid · (∂T_fluid/∂n) = -k_solid · (∂T_solid/∂n)
```

**OpenFOAM Implementation:**
```cpp
// Fluid side
type compressible::turbulentTemperatureCoupledBaffleMixed;
Tnbr T;  // Neighbor temperature
kappaMethodName fluidThermo;

// Solid side  
type compressible::turbulentTemperatureCoupledBaffleMixed;
Tnbr T;
kappaMethodName solidThermo;
```

</details>

<details>
<summary><b>3. วิธีตรวจสอบ Convergence ของ Coupled Simulation?</b></summary>

**3 ระดับของ convergence check:**

**1) Field Residuals (ภายในแต่ละ region):**
```cpp
// ใน fvSolution
solvers
{
    T
    {
        solver          GAMG;
        tolerance       1e-6;
        relTol          1e-3;
    }
}
```

**2) Interface Residuals (ระหว่าง regions):**
```cpp
T_residual = max(mag(T_fluid[interface] - T_solid[interface]));
q_residual = max(mag(q_fluid[interface] - q_solid[interface]));
```

**3) Coupling Loop Convergence:**
```cpp
if (T_residual < 1e-6 && q_residual < 1e-4)
{
    break;  // Converged
}
```

**Best Practice:** ตรวจสอบทั้ง 3 ระดับ และ plot convergence history
</details>

<details>
<summary><b>4. Monolithic vs Partitioned Approach — เลือกอย่างไร?</b></summary>

| มิติ | Monolithic | Partitioned (OpenFOAM) |
|------|------------|------------------------|
| **Matrix** | Single coupled matrix | Separate matrices |
| **Solver** | Direct (MUMPS, SuperLU) | Iterative per region |
| **Memory** | สูง (dense coupling) | ต่ำกว่า |
| **Robustness** | ดีกว่า (solves together) | ต้อง iterate |
| **Coding** | ยาก (custom) | ง่าย (modular) |
| **Applications** | งานวิจัย, เฉพาะทาง | งาน engineering ทั่วไป |

**OpenFOAM ใช้ Partitioned:**
- ✅ ยืดหยุ่น — ผสม solver ต่าง physics ได้
- ✅ ใช้ existing solvers ได้เลย
- ✅ Memory efficiency ดีกว่า
- ❌ ต้องเฝ้า convergence ของ coupling loop

</details>

<details>
<summary><b>5. Under-Relaxation คืออะไรและเมื่อไหร่ต้องใช้?</b></summary>

**Under-Relaxation** = ผสมค่าเก่ากับค่าใหม่ เพื่อ stability:

```cpp
φ_new = ω·φ_calculated + (1-ω)·φ_old
```

**เลือกค่า ω (relaxation factor):**

| สถานการณ์ | ω | เหตุผล |
|-----------|--------|-------|
| **Loose coupling** | 0.9 - 1.0 | ลู่เข้าเร็ว |
| **Moderate coupling** | 0.7 - 0.8 | สมดุล speed/stability |
| **Tight coupling** | 0.5 - 0.7 | Stability สำคัญ |
| **Diverging** | ลดลงครึ่งหนึ่ง | กู้คืน stability |

**ตัวอย่างใน fvSolution:**
```cpp
relaxationFactors
{
    fields
    {
        T       0.7;
    }
    equations
    {
        U       0.7;
        p       0.3;
    }
}
```

</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

### บทถัดไป (Recommended Reading Order)
- **ภาพรวม:** [00_Overview.md](00_Overview.md) — Module map & coupling type catalog
- **CHT:** [02_Conjugate_Heat_Transfer.md](02_Conjugate_Heat_Transfer.md) — CHT implementation details
- **FSI:** [03_Fluid_Structure_Interaction.md](03_Fluid_Structure_Interaction.md) — FSI theory & practice
- **Programming:** [04_Registry_and_Multi-Region_Code.md](04_Registry_and_Multi-Region_Code.md) — OpenFOAM multi-region architecture
- **ขั้นสูง:** [05_Advanced_Coupling_Topics.md](05_Advanced_Coupling_Topics.md) — Advanced coupling techniques
- **Validation:** [06_Validation_and_Verification.md](06_Validation_and_Verification.md) — Grid convergence & benchmarks
- **ฝึกปฏิบัติ:** [07_Hands-On_Exercises.md](07_Hands-On_Exercises.md) — Tutorial cases

### Related Modules
- **MODULE_03:** Single-phase flow solvers
- **MODULE_04:** Multiphase fundamentals
- **MODULE_05:** OpenFOAM programming