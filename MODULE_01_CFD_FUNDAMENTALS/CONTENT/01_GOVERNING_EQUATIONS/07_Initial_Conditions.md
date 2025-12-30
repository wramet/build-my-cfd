# Initial Conditions

**Learning Objectives:**
- ✅ Understand the structure and purpose of OpenFOAM's `0/` directory files
- ✅ Distinguish between internalField (initial conditions) and boundaryField (boundary conditions)
- ✅ Apply appropriate IC strategies for steady-state vs transient simulations
- ✅ Set realistic turbulence fields to avoid solver divergence
- ✅ Use utilities (setFields, mapFields, potentialFoam) effectively

---

## What Are Initial Conditions?

Initial Conditions (ICs) define the **state of all fields at time $t=0$**

### Why ICs Matter

| Simulation Type | IC Impact | Consequence of Poor ICs |
|----------------|-----------|------------------------|
| **Transient** | Critical — ICs represent physical reality at $t=0$ | Incorrect solution evolution |
| **Steady-state** | Moderate — affects convergence speed | Slow convergence or divergence |
| **Turbulent** | High — must be physically realistic | Division by zero, solver crash |

> 💡 **Key Principle:** ICs provide the starting point for the solution. While boundary conditions drive the solution, ICs determine **how fast** you reach it and **whether** you reach it stably.

---

## File Structure

Every file in `0/` directory follows this structure:

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       volVectorField;    // or volScalarField
    object      U;
}

dimensions      [0 1 -1 0 0 0 0];  // Units: m/s
internalField   uniform (0 0 0);   // ← INITIAL CONDITION

boundaryField
{
    inlet   { type fixedValue; value uniform (10 0 0); }
    outlet  { type zeroGradient; }
    walls   { type noSlip; }
}
```

| Component | Purpose | Update During Simulation |
|-----------|---------|-------------------------|
| `dimensions` | Field units: `[mass length time temperature moles current]` | Never |
| `internalField` | **Initial Condition** — value at $t=0$ throughout domain | Yes (solves for this) |
| `boundaryField` | **Boundary Conditions** — values at domain boundaries | Yes (enforced each timestep) |

---

## Initial Field Types

### 1. Uniform (Single Value Everywhere)

```cpp
internalField   uniform (0 0 0);       // Vector field
internalField   uniform 0;             // Scalar field
```

**Use cases:**
- Starting from rest
- Initial guess for steady-state
- Homogeneous fields

### 2. Non-Uniform (Spatially Varying)

#### Method A: `setFields` Utility (Recommended)

```bash
setFields -dict system/setFieldsDict
```

```cpp
// system/setFieldsDict
locations  (any);
field       U;
defaultValues uniform (0 0 0);

// Parabolic profile in pipe
fieldValues
{
    box (0 -0.05 -0.05) (1 0.05 0.05);
    expression "vector(2 * (1 - sqr(pos().y()/0.05)), 0, 0)";
}
```

#### Method B: `#codeStream` (Advanced)

> ⚠️ **Advanced Topic — Optional Reading**
> 
> `#codeStream` uses dynamic compilation:
> - Requires `wmake` and compiler in the execution environment
> - Adds overhead on first run (compilation time)
> - May have security restrictions on cluster systems
> - **Better alternatives:** `setFields`, `funkySetFields`, or `mapFields`

**When to consider `#codeStream`:**
- ✅ Complex ICs beyond utility capabilities
- ✅ Strong C++ and OpenFOAM API knowledge
- ❌ Avoid on production clusters with security policies
- ❌ Avoid if simpler methods suffice

```cpp
// Parabolic velocity profile using codeStream
internalField   #codeStream
{
    code
    #{
        const vectorField& C = mesh().C();
        vectorField& U = *this;
        scalar R = 0.05;              // Pipe radius
        scalar Umax = 2.0;            // Max velocity

        forAll(C, i)
        {
            scalar r = sqrt(sqr(C[i].y()) + sqr(C[i].z()));
            scalar u = Umax * (1.0 - sqr(r/R));
            U[i] = vector(u, 0, 0);
        }
    #};
};
```

### 3. From Previous Solution (`mapFields`)

```bash
# Copy from coarse mesh to fine mesh
mapFields ../coarseMesh -sourceTime latestTime

# Use steady-state result as transient IC
mapFields ../steadyStateCase -sourceTime 1000
```

---

## IC Strategy Decision Matrix

### For Steady-State Simulations

| Strategy | When to Use | Advantages | Disadvantages |
|----------|-------------|------------|---------------|
| **Zero initial fields** | Simple cases, first runs | Simple to set up | Slow convergence, may stagnate |
| **Potential flow** | External aerodynamics, streamlined flows | Fast convergence, physically realistic | Requires `potentialFoam` setup |
| **Coarse mesh solution** | Complex geometries, high Re | Fastest convergence, good guess | Requires preprocessing case |
| **Similar previous case** | Parametric studies | Reuse existing solution | Must ensure geometric similarity |

**Decision Flow:**
```
Is there a similar solved case?
├─ Yes → mapFields from it (FASTEST)
└─ No → Is flow attached/streamlined?
    ├─ Yes → potentialFoam (FAST)
    └─ No → Zero fields (SIMPLE)
```

### For Transient Simulations

| Strategy | When to Use | Critical Requirements |
|----------|-------------|----------------------|
| **Physical $t=0$ state** | All transient simulations | Must match experimental/real conditions |
| **Steady-state precursor** | Starting from developed flow | Run steady-state first, then map |
| **Restart** | Continuing long simulations | Use `mapFields` from latest time |

**Transient IC Checklist:**
- [ ] Fields match physical conditions at $t=0$
- [ ] Divergence-free velocity field (∇·**u** = 0)
- [ ] Consistent pressure-velocity coupling
- [ ] Turbulence fields non-zero and realistic
- [ ] Phase fields correctly defined (for multiphase)

---

## Field-by-Field Setup

### Velocity Field (`0/U`)

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       volVectorField;
    object      U;
}

dimensions      [0 1 -1 0 0 0 0];  // m/s
```

**Recommended ICs:**

| Case Type | internalField | Rationale |
|-----------|---------------|-----------|
| Steady-state pipe | `uniform (1 0 0)` | Inlet direction guess |
| Steady-state complex | `uniform (0 0 0)` | Start from rest |
| Transient | Realistic profile | Use `setFields` for profile |

### Pressure Field (`0/p`)

#### Incompressible Flow

```cpp
dimensions      [0 2 -2 0 0 0 0];  // m²/s² (kinematic pressure)
internalField   uniform 0;         // Gauge pressure = 0
```

#### Compressible Flow

```cpp
dimensions      [1 -1 -2 0 0 0 0]; // Pa (absolute pressure)
internalField   uniform 101325;    // 1 atm in Pascals
```

| Flow Type | Dimensions | Typical Value | Reference |
|-----------|------------|---------------|-----------|
| Incompressible | `[0 2 -2 0 0 0 0]` | 0 (gauge) | 04_Dimensionless_Numbers.md |
| Compressible | `[1 -1 -2 0 0 0 0]` | 101325 Pa | 03_Equation_of_State.md |

### Temperature Field (`0/T`)

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      T;
}

dimensions      [0 0 0 1 0 0 0];   // Kelvin
internalField   uniform 300;       // 300 K (room temperature)
```

### Turbulence Fields

> ⚠️ **CRITICAL:** Never set k, ε, or ω to exactly zero → causes division by zero

#### Turbulent Kinetic Energy (`0/k`)

$$k = \frac{3}{2}(I \cdot U)^2$$

```cpp
dimensions      [0 2 -2 0 0 0 0];  // m²/s²
internalField   uniform 0.375;     // k = 1.5 × (0.05 × 10)²
```

#### Dissipation Rate (`0/epsilon`)

$$\epsilon = C_\mu^{0.75} \cdot k^{1.5} / l$$

where $l = 0.07 L$ (characteristic length)

```cpp
dimensions      [0 2 -3 0 0 0 0];  // m²/s³
internalField   uniform 14.855;
```

#### Specific Dissipation Rate (`0/omega`)

$$\omega = k^{0.5} / (C_\mu^{0.25} \cdot l)$$

```cpp
dimensions      [0 0 -1 0 0 0 0];  // 1/s
internalField   uniform 440;
```

**Quick Reference Values (I = 5%, U = 10 m/s, L = 1 m):**

| Model | k | ε | ω |
|-------|---|---|---|
| k-ε | 0.375 | 14.855 | — |
| k-ω | 0.375 | — | 440 |

🔗 **See:** [04_Dimensionless_Numbers.md](04_Dimensionless_Numbers.md) for detailed calculations

### Phase Fraction (`0/alpha.water`)

For VOF multiphase simulations:

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      alpha.water;
}

dimensions      [0 0 0 0 0 0 0];   // Dimensionless
internalField   uniform 0;         // Start with air only

boundaryField
{
    inlet { type fixedValue; value uniform 1; }  // Water inlet
    // ... other boundaries
}
```

| α Value | Physical Meaning |
|---------|------------------|
| 0 | No water phase (air only) |
| 1 | Full water phase |
| 0 < α < 1 | Interface region |

**Use `setFields` to initialize patches:**

```bash
setFields -dict system/setFieldsDict
```

```cpp
// Create initial water patch
locations  (any);
field       alpha.water;
defaultValues uniform 0;

fieldValues
{
    // Box region containing water
    box (0 0 0) (1 0.5 1);
    value uniform 1;
}
```

---

## Utility Comparison Table

| Utility | Purpose | Input | Output | Best For |
|---------|---------|-------|--------|----------|
| **setFields** | Set field values in regions | `system/setFieldsDict` | Modified `0/` files | Geometric regions, expressions |
| **mapFields** | Map between meshes | Source case | Interpolated fields | Mesh refinement, case reuse |
| **potentialFoam** | Generate potential flow | `0/` IC | New `0/` files | Fast IC for external flows |
| **funkySetFields** | Complex expressions | Expression syntax | Custom fields | Advanced users only |

### setFields vs mapFields: When to Use Which

| Scenario | Recommended Tool | Why |
|----------|------------------|-----|
| Create initial water patch | `setFields` | Direct geometric control |
| Refine mesh from previous solution | `mapFields` | Preserves solution structure |
| Start transient from steady-state | `mapFields` | Exact field transfer |
| Parabolic velocity profile | `setFields` | Expression-based |
| Different mesh topology | `mapFields` | Handles interpolation |

---

## When ICs Cause Divergence: Troubleshooting

### Symptom: Immediate Solver Crash

**Diagnostic Checklist:**

| Error Message | Likely Cause | Fix |
|---------------|--------------|-----|
| `division by zero` | k, ε, or ω = 0 | Set positive values (≥1e-10) |
| `negative sqrt` | Negative turbulence values | Ensure k ≥ 0 |
| `maximum iterations exceeded` | Poor IC quality | Use better IC strategy |
| `nan in solution` | Non-physical ICs | Verify dimensional consistency |

### Symptom: Slow/Stalled Convergence

**Issue:** ICs far from final solution

**Solutions (in order of preference):**
1. **Use `mapFields`** from similar solved case (fastest)
2. **Generate potential flow** with `potentialFoam` (external flows)
3. **Run with under-relaxation** — adjust `fvSolution`
4. **Use gradual approach** — start with low Re, increase

### Symptom: Oscillating Residuals

**Issue:** ICs inconsistent with boundary conditions

**Example:** Inlet U = 10 m/s, but IC U = 100 m/s

**Fix:** Ensure ICs are **order-of-magnitude consistent** with BCs

---

## Common Pitfalls

| Pitfall | Consequence | Prevention |
|---------|-------------|------------|
| **k = ε = ω = 0** | Solver crash (÷0) | Always use positive values |
| **Wrong pressure units** | Incompressible uses Pa | Check `[0 2 -2...]` vs `[1 -1 -2...]` |
| **Non-divergence-free U** | Pressure-velocity decoupling | Use `potentialFoam` for transient ICs |
| **Ignoring IC for transient** | Unphysical solution | Match experimental $t=0$ conditions |
| **α not in [0,1]** | VOF solver errors | Clamp values or check initialization |

---

## IC Checklist

### For Steady-State Simulations

- [ ] Velocity: `uniform (0 0 0)` or estimate
- [ ] Pressure: `uniform 0` (incompressible) or `uniform 101325` (compressible)
- [ ] Turbulence: k > 0, ε > 0, ω > 0 (use I = 1-5%)
- [ ] Temperature: `uniform 300` (if applicable)
- [ ] Verify dimensions match field type
- [ ] Consider using `mapFields` or `potentialFoam` for faster convergence

### For Transient Simulations

- [ ] All steady-state items above
- [ ] **Velocity profile** matches physical $t=0$ state
- [ ] **Divergence-free** velocity field (∇·**u** ≈ 0)
- [ ] **Pressure consistent** with velocity field
- [ ] **Turbulence fields** realistic (not arbitrary)
- [ ] **Phase fields** correctly initialized (multiphase)
- [ ] **Time-step size** appropriate for ICs
- [ ] Verify ICs against experimental data (if available)

---

## Concept Check

<details>
<summary><b>Q1: Why does setting k = ε = 0 crash the solver?</b></summary>

The turbulent viscosity formula $\nu_t = C_\mu k^2/\epsilon$ involves division by ε. When ε = 0, this creates a division-by-zero error. Similarly, many turbulence model equations contain $\sqrt{k}$ or $k^{-1}$ terms. Always use small positive values (e.g., 1e-10) as a minimum.
</details>

<details>
<summary><b>Q2: What's the difference between internalField and boundaryField?</b></summary>

`internalField` specifies values at $t=0$ throughout the domain — it's the **initial condition** that the solver will evolve. `boundaryField` specifies values at domain boundaries — these are **boundary conditions** enforced at every timestep. The solver solves for the internal field; the boundary field is prescribed.
</details>

<details>
<summary><b>Q3: When should I use mapFields vs setFields?</b></summary>

- **Use `mapFields`** when transferring a complete solution from one mesh to another (e.g., mesh refinement study, using steady-state as transient IC)
- **Use `setFields`** when creating initial field distributions within the same mesh (e.g., water patch, velocity profile)
</details>

<details>
<summary><b>Q4: How do I choose ICs for a transient simulation starting from rest?</b></summary>

For "starting from rest":
- Velocity: `uniform (0 0 0)`
- Pressure: `uniform 0` (gauge)
- Turbulence: Use small values (k ≈ 1e-4, ε ≈ 1e-5) representing residual turbulence
- Verify BCs allow flow to enter (e.g., inlet with `fixedValue`)

This represents a physically realistic "fluid at rest" condition that the solver can evolve from as flow begins entering through boundaries.
</details>

---

## Key Takeaways

✅ **ICs drive convergence speed** — better ICs = faster solution  
✅ **Zero turbulence crashes solvers** — always use positive k, ε, ω  
✅ **Steady-state: zero fields are acceptable** — transient requires physical accuracy  
✅ **Match pressure dimensions to flow type** — kinematic vs absolute  
✅ **Use utilities for complex ICs** — `setFields` > `codeStream`  
✅ **Transient ICs must be divergence-free** — use `potentialFoam` or mapFields  

---

## Related Documents

### Previous Topics
- **[06_Boundary_Conditions.md](06_Boundary_Conditions.md)** — Boundary condition specification and types
- **[04_Dimensionless_Numbers.md](04_Dimensionless_Numbers.md)** — Turbulence quantity calculations from I and Re
- **[03_Equation_of_State.md](03_Equation_of_State.md)** — Pressure and temperature relationships

### Next Topics
- **[08_Key_Points_to_Remember.md](08_Key_Points_to_Remember.md)** — Module summary and quick reference
- **[05_OpenFOAM_Implementation.md](05_OpenFOAM_Implementation.md)** — Solver selection and configuration

### Cross-References
- **Turbulence ICs** ↔ 04_Dimensionless_Numbers.md (Re, I calculations)
- **Pressure fields** ↔ 03_Equation_of_State.md (compressible vs incompressible)
- **Utility usage** ↔ 05_OpenFOAM_Implementation.md (solver workflow)
- **Phase fractions** ↔ 02_Conservation_Laws.md (VOF method)