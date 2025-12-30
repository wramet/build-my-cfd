# Boundary Conditions

## Learning Objectives

**What You Will Learn:**
- Mathematical and physical classifications of boundary conditions
- Correct pressure-velocity coupling rules in OpenFOAM
- Wall function selection based on y+ values
- Turbulence specification at inlets
- Common BC pitfalls and how to avoid them

**Why This Matters:**
Boundary conditions are the **second most critical** factor after mesh quality. Incorrect BCs cause simulation divergence or non-physical results. Understanding U-p coupling and proper wall function selection ensures solver stability and accurate solutions.

---

## Mathematical Foundations

### Classification by Type

| Type | Name | Mathematical Meaning | OpenFOAM |
|------|------|---------------------|----------|
| **Dirichlet** | Fixed Value | Specifies value: φ = φ₀ | `fixedValue` |
| **Neumann** | Fixed Gradient | Specifies derivative: ∂φ/∂n = g | `zeroGradient`, `fixedGradient` |
| **Mixed** | Robin | Linear combination: aφ + b(∂φ/∂n) = c | `mixed` |

> **Physical Interpretation:** Dirichlet = "what happens here", Neumann = "what flows across here"

### Physical Classification

| Type | Meaning | Velocity | Pressure |
|------|---------|----------|----------|
| **Inlet** | Fluid enters domain | `fixedValue` | `zeroGradient` |
| **Outlet** | Fluid leaves domain | `zeroGradient` | `fixedValue` |
| **Wall** | Solid boundary | `noSlip` (= 0) | `zeroGradient` |
| **Symmetry** | Mirror plane | `symmetry` | `symmetry` |
| **Periodic** | Repeating flow | `cyclic` | `cyclic` |

---

## OpenFOAM File Structure

Boundary conditions are defined in files within the `0/` directory:

```cpp
// File: 0/U
dimensions      [0 1 -1 0 0 0 0];   // m/s
internalField   uniform (0 0 0);    // Initial value

boundaryField
{
    inlet
    {
        type    fixedValue;
        value   uniform (10 0 0);   // 10 m/s in x-direction
    }
    
    outlet
    {
        type    zeroGradient;       // Let develop naturally
    }
    
    walls
    {
        type    noSlip;             // Velocity = 0 at wall
    }
    
    symmetryPlane
    {
        type    symmetry;
    }
}
```

---

## Pressure-Velocity Coupling Rules

### Fundamental Rule

| Location | Velocity | Pressure | Rationale |
|----------|----------|----------|-----------|
| Inlet | `fixedValue` | `zeroGradient` | Specify U, let p develop |
| Outlet | `zeroGradient` | `fixedValue` | Let U develop, specify p |
| Wall | `noSlip` | `zeroGradient` | U=0, no flux through wall |

> **⚠️ CRITICAL:** Never specify BOTH U and p as `fixedValue` on the same boundary → solver instability

### BC Compatibility Matrix

| Patch Type | U can be fixedValue? | p can be fixedValue? | Notes |
|------------|---------------------|---------------------|-------|
| Inlet | ✅ Yes | ❌ No | Over-specification if both fixed |
| Outlet | ❌ No | ✅ Yes | Over-specification if both fixed |
| Wall | ✅ Yes (noSlip) | ❌ No | Only U specified, p gradient |
| Symmetry | ❌ No | ❌ No | Both use symmetry type |
| Cyclic | ❌ No | ❌ No | Both use cyclic type |

---

## Inlet Boundary Conditions

### Velocity Inlet

```cpp
inlet
{
    type    fixedValue;
    value   uniform (10 0 0);   // Direct specification
}
```

### Pressure Inlet (Compressible Flows)

```cpp
inlet
{
    type    totalPressure;
    p0      uniform 101325;     // Total pressure [Pa]
}
```

### Turbulence Specification

<details>
<summary><b>📐 Quick Reference: Turbulence Calculations</b></summary>

**Step 1: Define Flow Parameters**
- Mean velocity: $U = 10$ m/s
- Turbulence intensity: $I = 5\%$ (0.05)
- Hydraulic diameter: $D = 0.1$ m
- Kinematic viscosity: $\nu = 1.5 \times 10^{-5}$ m²/s (air)

**Step 2: Calculate k (Turbulent Kinetic Energy)**

$$k = \frac{3}{2} (I \cdot U)^2$$

$$k = 1.5 \times (0.05 \times 10)^2 = 0.375 \text{ m}^2/\text{s}^2$$

**Step 3: Calculate ε (Dissipation Rate)**

$$\varepsilon = C_\mu^{3/4} \frac{k^{3/2}}{\ell}$$

Where:
- $C_\mu = 0.09$ (empirical constant)
- $\ell = 0.07 \times D$ (length scale for pipe flow)
- $\ell = 0.007$ m

$$\varepsilon = 0.09^{0.75} \times \frac{0.375^{1.5}}{0.007} \approx 5.38 \text{ m}^2/\text{s}^3$$

**Step 4: Calculate ω (Specific Dissipation Rate)**

$$\omega = \frac{\sqrt{k}}{C_\mu^{0.25} \cdot \ell} = \frac{\sqrt{0.375}}{0.09^{0.25} \times 0.007} \approx 119.5 \text{ s}^{-1}$$

**Summary Formulas:**
- **k:** $k = 1.5 \times (I \cdot U)^2$
- **ε:** $\varepsilon = C_\mu^{0.75} \cdot k^{1.5} / \ell$ where $\ell = 0.07 D$
- **ω:** $\omega = \sqrt{k} / (C_\mu^{0.25} \cdot \ell)$

</details>

```cpp
// 0/k
inlet
{
    type    fixedValue;
    value   uniform 0.375;      // k = 1.5 * (I * U)^2
}

// 0/epsilon
inlet
{
    type    fixedValue;
    value   uniform 5.38;       // epsilon = Cmu^0.75 * k^1.5 / l
}

// 0/omega (for k-ω model)
inlet
{
    type    fixedValue;
    value   uniform 119.5;      // omega = sqrt(k) / (Cmu^0.25 * l)
}
```

---

## Outlet Boundary Conditions

### Zero Gradient (Most Common)

```cpp
outlet
{
    type    zeroGradient;       // ∂φ/∂n = 0
}
```

### Fixed Pressure Outlet

```cpp
outlet
{
    type    fixedValue;
    value   uniform 0;          // Gauge pressure = 0
}
```

### Backflow Prevention

```cpp
outlet
{
    type        inletOutlet;
    inletValue  uniform (0 0 0);    // Value if flow reverses
    value       uniform (0 0 0);
}
```

---

## Wall Boundary Conditions

### No-Slip Condition (Velocity)

```cpp
walls
{
    type    noSlip;             // u = 0
    // Equivalent to:
    // type    fixedValue;
    // value   uniform (0 0 0);
}
```

### Moving/Rotating Wall

```cpp
rotatingWall
{
    type    rotatingWallVelocity;
    origin  (0 0 0);
    axis    (0 0 1);
    omega   3.14159;            // rad/s
}
```

### Wall Functions for Turbulence

> **⚠️ Wall Function Selection Guide**
> Choice depends entirely on **y+** value of near-wall cells. Calculate y+ first using [04_Dimensionless_Numbers.md](04_Dimensionless_Numbers.md).

```
                    START
                      │
              ┌───────┴────────────────┐
              │ Run simulation & check │
              │ yPlus (postProcess)    │
              └───────┬────────────────┘
                      │
          ┌───────────┴────────────┐
          │                        │
    y+ < 5 (Fine mesh)      30 < y+ < 300 (Coarse mesh)
          │                        │
          ▼                        ▼
  ┌───────────────┐      ┌─────────────────┐
  │ Low-Re Model  │      │ Wall Functions  │
  │ Resolve BL    │      │ Model BL        │
  └───────┬───────┘      └────────┬────────┘
          │                       │
  nutkLowReWallFunction     nutkWallFunction
  kqRWallFunction           epsilonWallFunction
                          omegaWallFunction
          │                       │
          └───────────┬───────────┘
                      │
                      ▼
              SOLVE SIMULATION
```

### Wall Function Selection Table

| Turbulence Model | y+ Range | Wall Function BCs |
|------------------|----------|-------------------|
| **k-ε standard** | 30-300 | `nutkWallFunction`, `epsilonWallFunction` |
| **k-ω SST** | < 5 (recommended) | `nutkWallFunction`, `omegaWallFunction` |
| **Spalart-Allmaras** | < 5 | `nutUSpaldingWallFunction` |

```cpp
// 0/nut - Wall function for k-ε
walls
{
    type    nutkWallFunction;
    value   uniform 0;
}

// 0/k
walls
{
    type    kqRWallFunction;
    value   uniform 0;
}

// 0/epsilon
walls
{
    type    epsilonWallFunction;
    value   uniform 0;
}
```

> **💡 Note:** k-ω SST automatically switches between low-Re and wall function treatment based on y+.

---

## Thermal Boundary Conditions

### Fixed Temperature

```cpp
// 0/T
hotWall
{
    type    fixedValue;
    value   uniform 400;        // 400 K
}
```

### Adiabatic (No Heat Flux)

```cpp
insulated
{
    type    zeroGradient;       // ∂T/∂n = 0
}
```

### Fixed Heat Flux

```cpp
heatedWall
{
    type    fixedGradient;
    gradient uniform 1000;      // W/m²
}
```

### Convection to Environment

```cpp
externalWall
{
    type    externalWallHeatFluxTemperature;
    mode    coefficient;
    h       uniform 10;         // W/(m²·K)
    Ta      uniform 300;        // Ambient temperature [K]
}
```

---

## Special Boundary Conditions

### Symmetry Plane

```cpp
symmetryPlane
{
    type    symmetry;
    // No additional parameters needed
}
```

### Periodic/Cyclic

```cpp
periodic1
{
    type    cyclic;
    // Paired with periodic2 defined in constant/polyMesh/boundary
}
```

### Time-Varying Inlet

```cpp
inlet
{
    type            uniformFixedValue;
    uniformValue    table
    (
        (0   (0 0 0))
        (1   (5 0 0))
        (2   (10 0 0))
    );
}
```

---

## Common Pitfalls

### 1. Over-Specification

**Problem:** Setting both velocity and pressure to `fixedValue` on same boundary

```cpp
// ❌ WRONG - Over-specified
inlet
{
    // In 0/U
    type    fixedValue;
    value   uniform (10 0 0);
}
// AND in 0/p
inlet
{
    type    fixedValue;        // CONFLICT!
    value   uniform 0;
}
```

**Solution:** Follow U-p coupling rules

```cpp
// ✅ CORRECT
// In 0/U
inlet
{
    type    fixedValue;
    value   uniform (10 0 0);
}
// In 0/p
inlet
{
    type    zeroGradient;      // Let pressure develop
}
```

### 2. Incorrect Wall Function Selection

**Problem:** Using wall functions with y+ < 5

```cpp
// ❌ WRONG if y+ < 5
walls
{
    type    nutkWallFunction;  // Requires y+ 30-300
}
```

**Solution:** Check y+ first, then select appropriate BC

```cpp
// ✅ CORRECT for y+ < 5
walls
{
    type    fixedValue;        // Low-Re treatment
    value   uniform 0;
}

// ✅ CORRECT for y+ 30-300
walls
{
    type    nutkWallFunction;
    value   uniform 0;
}
```

### 3. Backflow Instability

**Problem:** `zeroGradient` allows unphysical values during backflow

```cpp
// ❌ PROBLEMATIC with recirculation
outlet
{
    type    zeroGradient;      // Unstable if backflow occurs
}
```

**Solution:** Use `inletOutlet` with sensible inletValue

```cpp
// ✅ CORRECT for potential backflow
outlet
{
    type        inletOutlet;
    inletValue  uniform (0 0 0);    // Applied if flow reverses
    value       uniform (0 0 0);
}
```

### 4. Missing Turbulence Inlet Values

**Problem:** Default k = ε = 0 causes laminar assumption

```cpp
// ❌ WRONG - Causes effective laminar flow
inlet
{
    type    fixedValue;
    value   uniform 0;        // k = 0 → no turbulence
}
```

**Solution:** Calculate and specify proper turbulence values (see section above)

---

## Complete Working Example

### Directory Structure: `0/`

```
0/
├── U
├── p
├── T
├── k
├── epsilon
├── nut
└── omega
```

### File Contents

```cpp
// 0/U
dimensions      [0 1 -1 0 0 0 0];
internalField   uniform (0 0 0);

boundaryField
{
    inlet
    {
        type        fixedValue;
        value       uniform (10 0 0);
    }
    
    outlet
    {
        type        inletOutlet;
        inletValue  uniform (0 0 0);
        value       uniform (0 0 0);
    }
    
    walls
    {
        type        noSlip;
    }
    
    symmetryPlane
    {
        type        symmetry;
    }
}

// 0/p
dimensions      [0 2 -2 0 0 0 0];
internalField   uniform 0;

boundaryField
{
    inlet
    {
        type        zeroGradient;
    }
    
    outlet
    {
        type        fixedValue;
        value       uniform 0;
    }
    
    walls
    {
        type        zeroGradient;
    }
    
    symmetryPlane
    {
        type        symmetry;
    }
}

// 0/T (if heat transfer)
dimensions      [0 0 0 1 0 0 0];
internalField   uniform 300;

boundaryField
{
    inlet
    {
        type        fixedValue;
        value       uniform 300;
    }
    
    outlet
    {
        type        zeroGradient;
    }
    
    walls
    {
        type        fixedValue;
        value       uniform 350;
    }
    
    symmetryPlane
    {
        type        symmetry;
    }
}

// 0/k
dimensions      [0 2 -2 0 0 0 0];
internalField   uniform 0.375;

boundaryField
{
    inlet
    {
        type        fixedValue;
        value       uniform 0.375;
    }
    
    outlet
    {
        type        zeroGradient;
    }
    
    walls
    {
        type        kqRWallFunction;
        value       uniform 0;
    }
    
    symmetryPlane
    {
        type        symmetry;
    }
}

// 0/epsilon
dimensions      [0 2 -3 0 0 0 0];
internalField   uniform 5.38;

boundaryField
{
    inlet
    {
        type        fixedValue;
        value       uniform 5.38;
    }
    
    outlet
    {
        type        zeroGradient;
    }
    
    walls
    {
        type        epsilonWallFunction;
        value       uniform 0;
    }
    
    symmetryPlane
    {
        type        symmetry;
    }
}

// 0/nut
dimensions      [0 2 -1 0 0 0 0];
internalField   uniform 0;

boundaryField
{
    inlet
    {
        type        calculated;
        value       uniform 0;
    }
    
    outlet
    {
        type        calculated;
        value       uniform 0;
    }
    
    walls
    {
        type        nutkWallFunction;
        value       uniform 0;
    }
    
    symmetryPlane
    {
        type        symmetry;
    }
}
```

---

## Quick Reference Summary

| Field | Inlet | Outlet | Wall | Symmetry |
|-------|-------|--------|------|----------|
| `U` | `fixedValue` | `inletOutlet` | `noSlip` | `symmetry` |
| `p` | `zeroGradient` | `fixedValue` | `zeroGradient` | `symmetry` |
| `T` | `fixedValue` | `zeroGradient` | `fixedValue`/`zeroGradient` | `symmetry` |
| `k` | `fixedValue` | `zeroGradient` | `kqRWallFunction` | `symmetry` |
| `epsilon` | `fixedValue` | `zeroGradient` | `epsilonWallFunction` | `symmetry` |
| `nut` | `calculated` | `calculated` | `nutkWallFunction` | `symmetry` |

---

## Concept Check

<details>
<summary><b>1. Why use zeroGradient for velocity at outlet?</b></summary>

We don't know the outlet velocity in advance - it should develop naturally from solving the governing equations. Neumann condition (∂u/∂n = 0) allows this by assuming the flow is fully developed.
</details>

<details>
<summary><b>2. When should inletOutlet be used instead of zeroGradient?</b></summary>

When backflow is possible at the outlet (e.g., flow recirculation after an obstacle). `inletOutlet` applies a specified value during reverse flow, preventing numerical instability from unphysical values entering the domain.
</details>

<details>
<summary><b>3. What is the physical meaning of the noSlip BC?</b></summary>

Fluid sticks to the wall (no relative motion). Fluid velocity at the wall equals wall velocity (normally 0 for stationary walls). This is a consequence of fluid viscosity in real fluids.
</details>

<details>
<summary><b>4. Why can't both U and p be fixedValue on the same boundary?</b></summary>

This over-constrains the problem. The pressure-velocity coupling in the Navier-Stokes equations means specifying both creates a mathematical conflict - the solver cannot satisfy both conditions simultaneously, leading to instability or divergence.
</details>

---

## Key Takeaways

✓ **U-p coupling is critical:** Fixed U → zero-gradient p, and vice versa  
✓ **Wall functions require proper y+:** Check mesh resolution first  
✓ **Specify turbulence at inlets:** Calculate k, ε, ω from flow parameters  
✓ **Prevent backflow issues:** Use `inletOutlet` with appropriate inletValue  
✓ **Avoid over-specification:** Never fix both U and p on same patch  
✓ **Verify y+ after solving:** Adjust BCs if outside required range

---

## Related Documents

- **Previous:** [05_OpenFOAM_Implementation.md](05_OpenFOAM_Implementation.md) — OpenFOAM file structure and solver selection
- **Next:** [07_Initial_Conditions.md](07_Initial_Conditions.md) — Initial field specification
- **Related:** [04_Dimensionless_Numbers.md](04_Dimensionless_Numbers.md) — y+ calculation and mesh design
- **Related:** [03_Equation_of_State.md](03_Equation_of_State.md) — Temperature units and thermodynamic properties