# Summary and Exercises

---

## Learning Objectives

By completing these exercises, you will be able to:

- **Synthesize** dimensional analysis concepts into practical applications
- **Apply** dimensional consistency checking to real CFD equations
- **Design** non-dimensional numbers for flow characterization
- **Implement** proper dimensioned quantities in OpenFOAM code
- **Validate** equation dimensional balance before simulation
- **Combine** multiple dimensional concepts in complex scenarios

---

## Summary

### Core Concepts Matrix

| Concept | Mathematical Form | Physical Meaning | OpenFOAM Implementation |
|---------|------------------|------------------|-------------------------|
| **dimensionSet** | `[M^a L^b T^c θ^d I^e J^f N^g]` | 7 fundamental dimensions | `dimensionSet(1, -1, -2, 0, 0, 0, 0)` |
| **dimensionedScalar** | `value + name + dims` | Physical quantity with units | `dimensionedScalar("p", dimPressure, 101325)` |
| **Dimensional Consistency** | `[LHS] = [RHS]` | Operations verify dimensional balance | Automatic compile-time checking |
| **Non-Dimensionalization** | `Π = product of variables^exponents` | Scale removal for generalization | Buckingham Pi theorem application |

### Dimension Arithmetic Summary

| Operation | Dimension Rule | Example |
|-----------|----------------|---------|
| **Addition** | Must have identical dimensions | `velocity + velocity ✓` |
| **Multiplication** | Add exponents | `[L][T⁻¹] × [T] = [L]` |
| **Division** | Subtract exponents | `[L][T⁻¹] / [T⁻²] = [L][T]` |
| **Power** | Multiply exponents | `[L]² = [L²]` |
| **Integration** | Multiply by variable dimension | `∫v dt → [L/T][T] = [L]` |
| **Differentiation** | Divide by variable dimension | `dv/dt → [L/T]/[T] = [L/T²]` |

### Common Non-Dimensional Numbers

| Symbol | Definition | Physical Significance | Typical Use |
|--------|-----------|----------------------|-------------|
| **Re** | `ρUL/μ = UL/ν` | Inertia / Viscous forces | Turbulence transition |
| **Pr** | `ν/α = Cpμ/k` | Momentum / Thermal diffusivity | Heat transfer correlation |
| **Nu** | `hL/k` | Convective / Conductive heat transfer | Nusselt correlations |
| **Eu** | `ΔP/(ρU²)` | Pressure / Inertia forces | Pressure drop analysis |
| **Fr** | `U/√(gL)` | Inertia / Gravitational forces | Free surface flows |

### Why Dimensional Analysis Matters

1. **Physical Verification**: Catch errors in equations before implementation
2. **Code Safety**: Compiler enforces dimensional consistency
3. **Simulation Scaling**: Non-dimensional results generalize across scales
4. **Data Interpretation**: Understand relative importance of terms
5. **Optimization**: Identify dominant physical mechanisms

---

## Key Takeaways

✓ **Dimensional consistency is not optional** - it's enforced by OpenFOAM's type system  
✓ **Non-dimensional numbers reveal physics** - they quantify relative importance of forces  
✓ **Buckingham Pi theorem guides analysis** - systematically reduce parameter space  
✓ **Dimensional checking prevents costly errors** - catch mistakes before simulation  
✓ **Physical intuition validates code** - if dimensions don't match, physics is wrong  
✓ **Scaling requires non-dimensionalization** - essential for comparing across geometries  

---

## Exercises

### Exercise 1: Creating Thermal Properties

Create properly dimensioned thermodynamic properties for a fluid simulation:

```cpp
// Thermal conductivity [W/(m·K)]
dimensionedScalar k
(
    "k",
    dimPower / dimLength / dimTemperature,
    0.6  // Water at 20°C
);

// Specific heat capacity [J/(kg·K)]
dimensionedScalar Cp
(
    "Cp", 
    dimEnergy / dimMass / dimTemperature,
    4180  // Water
);

// Density [kg/m³]
dimensionedScalar rho
(
    "rho",
    dimMass / dimVolume,
    998  // Water at 20°C
);

// Thermal diffusivity α = k/(ρ·Cp)
dimensionedScalar alpha = k / (rho * Cp);
// Dimensions: [W/(m·K)] / ([kg/m³][J/(kg·K)])
//            = [J/(s·m·K)] / [J/(m³·K)]
//            = [m²/s] ✓
```

**Task**: Verify `alpha` has dimensions of kinematic viscosity `[m²/s]`.

---

### Exercise 2: Verifying Energy Equation Dimensional Balance

Validate dimensional consistency in the transient heat conduction equation:

```cpp
// Energy equation: ρCp(∂T/∂t) = k∇²T + Q̇

// Left-hand side: ρCp(∂T/∂t)
// [kg/m³] × [J/(kg·K)] × [K/s]
// = [J/(m³·s)] = [W/m³]  ✓

// Right-hand side: k∇²T
// [W/(m·K)] × [K/m²]
// = [W/m³]  ✓

// Source term: Q̇
// [W/m³]  ✓

fvScalarMatrix TEqn
(
    fvm::ddt(rho * Cp, T)
 ==
    fvm::laplacian(k, T)
  + dimensionedScalar("Q", dimPower/dimVolume, 1e6)
);
```

**Task**: Check what happens if you forget `rho` in the LHS term. Will it compile?

---

### Exercise 3: Non-Dimensional Number Calculations

Calculate key similarity parameters for a water flow:

```cpp
// Flow parameters
dimensionedScalar U("U", dimVelocity, 2.0);      // [m/s]
dimensionedScalar L("L", dimLength, 0.1);         // [m] characteristic length
dimensionedScalar nu("nu", dimKinematicViscosity, 1e-6);  // [m²/s]
dimensionedScalar alpha("alpha", dimArea/dimTime, 1.4e-7); // [m²/s]

// Reynolds number: Re = UL/ν
dimensionedScalar Re = U * L / nu;
assert(Re.dimensions().dimensionless());  // Should be true
// Re = 2.0 × 0.1 / 1e-6 = 200,000 (turbulent)

// Prandtl number: Pr = ν/α
dimensionedScalar Pr = nu / alpha;
assert(Pr.dimensions().dimensionless());  // Should be true
// Pr = 1e-6 / 1.4e-7 ≈ 7.14 (water)

// Peclet number: Pe = Re × Pr = UL/α
dimensionedScalar Pe = U * L / alpha;
assert(Pe.dimensions().dimensionless());
// Pe = 200,000 × 7.14 ≈ 1.4 million
```

**Task**: Calculate the Grashof number `Gr = gβΔTL³/ν²` for natural convection with:
- `g = 9.81 [m/s²]`
- `β = 0.000207 [K⁻¹]` (thermal expansion coefficient)
- `ΔT = 10 [K]`
- `L = 0.5 [m]`

---

### Exercise 4: Implementing Source Terms with Dimensional Checking

Add various physical source terms to the energy equation:

```cpp
// Volumetric heat source [W/m³]
dimensionedScalar Q_volumetric
(
    "Q_vol",
    dimPower / dimVolume,
    1e6  // 1 MW/m³
);

// Surface heat flux [W/m²] - must divide by volume for source term
dimensionedScalar heatFlux
(
    "q_wall",
    dimPower / dimArea,
    5000  // W/m²
);

dimensionedScalar surfaceArea
(
    "A_surface",
    dimArea,
    0.01  // m²
);

// Convert surface flux to volumetric source: Q̇ = qA/V
dimensionedScalar Q_from_flux = heatFlux * surfaceArea / dimensionedScalar("V", dimVolume, 0.001);

// Complete energy equation with sources
fvScalarMatrix TEqn
(
    fvm::ddt(rho * Cp, T)
 ==
    fvm::laplacian(k, T)
  + Q_volumetric
  + Q_from_flux
);
```

**Task**: Verify both source terms have dimensions `[W/m³]`.

---

### 🔥 Challenge Exercise: Combined Heat and Mass Transfer

Design a complete non-dimensional analysis for coupled heat and mass transfer:

```cpp
// Physical parameters
dimensionedScalar U("U", dimVelocity, 1.0);
dimensionedScalar L("L", dimLength, 0.05);
dimensionedScalar nu("nu", dimKinematicViscosity, 1.5e-5);  // Air
dimensionedScalar alpha("alpha", dimArea/dimTime, 2.2e-5);  // Thermal diffusivity
dimensionedScalar D("D", dimArea/dimTime, 2.4e-5);          // Mass diffusivity
dimensionedScalar beta("beta", dimless/dimTemperature, 0.003); // Thermal expansion

// Temperature and concentration differences
dimensionedScalar DeltaT("DeltaT", dimTemperature, 20.0);
dimensionedScalar DeltaC("DeltaC", dimless, 0.01);  // Mass fraction

// Task 1: Calculate all relevant non-dimensional numbers
dimensionedScalar Re = U * L / nu;              // Reynolds
dimensionedScalar Pr = nu / alpha;              // Prandtl
dimensionedScalar Sc = nu / D;                  // Schmidt
dimensionedScalar Le = alpha / D;               // Lewis
// Grashof for thermal: Gr_T = gβΔTL³/ν²
// Grashof for solutal: Gr_C = gβ_CΔCL³/ν²
// Richardson number: Ri = Gr/Re²

// Task 2: Determine which mechanism dominates
// Buoyancy ratio: N = Gr_C / Gr_T
// If N > 1: Solutal buoyancy dominates
// If N < 1: Thermal buoyancy dominates

// Task 3: Propose Nusselt and Sherwood correlations
// Nu = f(Re, Pr, Gr, Ri)
// Sh = f(Re, Sc, Gr, Ri, N)
```

**Deliverables**:
1. Calculate all non-dimensional numbers
2. Determine dominant buoyancy mechanism
3. Explain how you would validate these correlations experimentally

---

## 💡 Project Idea

### Mini-Project: Automated Dimensional Checker

Develop a Python utility to automatically verify dimensional consistency in OpenFOAM boundary conditions:

**Project Goals**:
1. Parse OpenFOAM field files (`0/p`, `0/U`, `0/T`)
2. Extract dimensions from `dimensions` entry
3. Verify consistency with field type:
   - `p`: `[1 -1 -2 0 0 0 0]` (pressure)
   - `U`: `[0 1 -1 0 0 0 0]` (velocity)
   - `T`: `[0 0 0 1 0 0 0]` (temperature)
4. Check boundary condition values have correct dimensions
5. Generate validation report

**Skills Practiced**:
- Dimensional analysis application
- File parsing and regex
- Error detection and reporting
- OpenFOAM file format understanding

**Output Example**:
```
✓ p field dimensions: [1 -1 -2 0 0 0 0] (pressure) - VALID
✗ U boundary value 10.0 has wrong units - expected [m/s], found [m]  
✓ T boundary condition dimensions consistent
```

---

## Quick Reference

### Creating Dimensioned Quantities

| Task | Syntax | Example |
|------|--------|---------|
| **Scalar** | `dimensionedScalar("name", dims, val)` | `dimensionedScalar("p", dimPressure, 101325)` |
| **Compound dims** | `dim1 / dim2 * dim3` | `dimEnergy / (dimMass * dimTemperature)` |
| **From expression** | Result inherits dims | `dimensionedScalar Re = U * L / nu;` |

### Checking and Accessing

| Operation | Code | Returns |
|-----------|------|---------|
| **Check dimensionless** | `.dimensions().dimensionless()` | `bool` |
| **Get value** | `.value()` | `double` |
| **Get name** | `.name()` | `word` |
| **Get dimensions** | `.dimensions()` | `dimensionSet` |

### Dimension Constants

| Constant | Dimensions |
|----------|------------|
| `dimMass` | `[1 0 0 0 0 0 0]` |
| `dimLength` | `[0 1 0 0 0 0 0]` |
| `dimTime` | `[0 0 1 0 0 0 0]` |
| `dimTemperature` | `[0 0 0 1 0 0 0]` |
| `dimPressure` | `[1 -1 -2 0 0 0 0]` |
| `dimVelocity` | `[0 1 -1 0 0 0 0]` |
| `dimEnergy` | `[1 2 -2 0 0 0 0]` |
| `dimless` | `[0 0 0 0 0 0 0]` |

---

## 🧠 Concept Check

<details>
<summary><b>1. What are the dimensions of thermal conductivity k?</b></summary>

**[W/(m·K)]** = `dimPower / dimLength / dimTemperature`  
  = `[M·L²/T³] / [L] / [θ]`  
  = `[M·L/T³·θ]`  

Physical meaning: energy transfer rate per unit length per unit temperature difference.
</details>

<details>
<summary><b>2. What dimensions should a source term in the energy equation have?</b></summary>

**[W/m³]** = `dimPower / dimVolume`  
  = `[M·L²/T³] / [L³]`  
  = `[M/(L·T³)]`  

This represents volumetric heat generation rate (energy per unit time per unit volume).
</details>

<details>
<summary><b>3. Is Reynolds number UL/ν truly dimensionless?</b></summary>

**Yes** — dimension analysis confirms:  
  `[L/T] × [L] / [L²/T]`  
  = `[L²/T] / [L²/T]`  
  = `[0 0 0 0 0 0 0]` ✓  

Reynolds number represents the ratio of inertial to viscous forces, both having same dimensions.
</details>

<details>
<summary><b>4. Why must you include density ρ when discretizing ∂T/∂t?</b></summary>

**Energy density requires mass**:  
  `ρCp(∂T/∂t)` represents volumetric energy rate  
  Without ρ: `[J/(kg·K)] × [K/s] = [J/(kg·s)]` ✗ (per unit mass)  
  With ρ: `[kg/m³] × [J/(kg·K)] × [K/s] = [J/(m³·s)]` ✓ (per unit volume)  

Forgetting ρ is a common error that dimensional checking catches immediately.
</details>

<details>
<summary><b>5. What does Pr = ν/α physically represent?</b></summary>

**Ratio of momentum to thermal diffusivity**:  
  - `Pr >> 1`: Momentum diffuses faster than heat (oils, metals)  
  - `Pr << 1`: Heat diffuses faster than momentum (liquid metals)  
  - `Pr ≈ 1`: Similar rates (air, water)  

Prandtl number determines relative thickness of velocity vs thermal boundary layers.
</details>

---

## 📖 Related Documentation

- **Overview**: [00_Overview.md](00_Overview.md)
- **DimensionSet Theory**: [02_DimensionSet_Advanced.md](02_DimensionSet_Advanced.md)
- **Non-Dimensionalization**: [04_Non_Dimensionalization.md](04_Non_Dimensionalization.md)
- **Advanced Applications**: [05_Advanced_Applications.md](05_Advanced_Applications.md)