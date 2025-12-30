# Code and Model Architecture: multiphaseEulerFoam

สถาปัตยกรรมโค้ดและโมเดลของ solver สำหรับการไหลหลายเฟส

---

## Learning Objectives

**What** you will learn:
- Core class hierarchy: phaseModel, phaseSystem, and interphase force models
- Solution algorithm structure and equation discretization
- Interfacial model architecture (drag, lift, virtual mass, turbulent dispersion)
- Memory management strategies (smart pointers, lazy allocation)
- FVM vs FVC operators and under-relaxation fundamentals

**Why** this matters:
- Understanding class hierarchy enables you to customize solver behavior
- Knowing interphase model architecture helps implement new force models
- Mastering fvm/fvc differences is crucial for numerical stability
- Smart pointer knowledge prevents memory leaks in custom code

**How** to apply this:
- Modify existing drag models or implement new ones
- Debug convergence issues by adjusting under-relaxation
- Extend solver functionality with new interphase forces
- Optimize memory usage in large-scale simulations

---

## Part 1: Core Class Architecture

### 1.1 Class Hierarchy Overview

```
phaseSystem
├── phases_ (PtrListDictionary<phaseModel>)
│   ├── water: phaseModel
│   │   ├── alpha_ (volScalarField)      ← 0/alpha.water
│   │   ├── U_ (volVectorField)          ← 0/U.water
│   │   ├── rho_ (volScalarField)        ← thermo
│   │   ├── thermo_ (autoPtr<basicThermo>)  ← thermophysicalProperties
│   │   └── turbulence_ (autoPtr<...>)   ← turbulenceProperties
│   └── air: phaseModel
│       └── ...
├── dragModels_ (HashTable<dragModel>)       ← phaseProperties
├── liftModels_ (HashTable<liftModel>)       ← phaseProperties
├── virtualMassModels_ (HashTable<...>)      ← phaseProperties
└── turbulentDispersionModels_ (HashTable<...>) ← phaseProperties
```

**Key Design Principle:** `phaseSystem` acts as **facade pattern** — solver interacts with system, not individual phases/models directly.

---

### 1.2 phaseModel (Abstract Base)

เก็บ state variables ของแต่ละเฟส:

```cpp
class phaseModel
{
protected:
    // Primary fields
    volScalarField alpha_;           // Volume fraction
    volVectorField U_;               // Velocity
    volScalarField rho_;             // Density
    
    // Physical models (lazy allocation)
    autoPtr<basicThermo> thermo_;
    autoPtr<turbulenceModel> turbulence_;
    
    // Reference to parent system
    const phaseSystem& fluid_;
    
public:
    // Field access
    const volScalarField& alpha() const { return alpha_; }
    volVectorField& U() { return U_; }
    
    // Virtual interface
    virtual void correct() = 0;  // Update properties (rho, mu, etc.)
    virtual tmp<volScalarField> nu() const = 0;  // Kinematic viscosity
    
    // Phase properties
    word name() const;            // "water", "air", etc.
    scalar phaseFraction() const; // α in alphaEqn
};
```

**Case file mapping:**

| Code Member | File Path | Description |
|-------------|-----------|-------------|
| `alpha_` | `0/alpha.water` | Initial volume fraction |
| `U_` | `0/U.water` | Initial velocity |
| `thermo_` | `constant/thermophysicalProperties.water` | ρ, Cp, μ, etc. |
| `turbulence_` | `constant/turbulenceProperties.water` | k-ε, k-ω, etc. |

---

### 1.3 phaseSystem (Facade + Strategy Pattern)

จัดการทุกเฟสและ interphase models:

```cpp
class phaseSystem
{
protected:
    // Phase storage (dictionary indexed)
    PtrListDictionary<phaseModel> phases_;
    
    // Interphase models (key = phasePairKey)
    HashTable<autoPtr<dragModel>> dragModels_;
    HashTable<autoPtr<liftModel>> liftModels_;
    HashTable<autoPtr<virtualMassModel>> vmModels_;
    HashTable<autoPtr<turbulentDispersionModel>> tdModels_;
    
public:
    // Phase access
    const PtrListDictionary<phaseModel>& phases() const
    {
        return phases_;
    }
    
    phaseModel& phase(const word& name);  // Lookup by name
    
    // Interphase force calculation (momentum source)
    tmp<volVectorField> interfacialMomentumTransfer(
        const phaseModel& phase
    ) const;
    
    // Overall update
    virtual void correct();
    
    // Phase pair access (for model lookups)
    const phasePair& phasePairs(
        const word& phase1,
        const word& phase2
    ) const;
};
```

**Case file mapping:**
```
constant/phaseProperties:
phases ( water air );
drag
{
    water_air SchillerNaumann;  // → dragModels_["water_air"]
}
lift
{
    water_air constantCoefficient 0.5;  // → liftModels_["water_air"]
}
```

**Why HashTable?** Phase pairs are unordered — `(water, air)` and `(air, water)` access same model. `phasePairKey` provides symmetric hashing.

---

## Part 2: Solution Structure

### 2.1 Main Algorithm (PIMPLE)

```cpp
while (pimple.loop())
{
    // 1. Update thermo/turbulence properties
    fluid.correct();  // Calls phaseModel::correct() for each phase
    
    // 2. Solve momentum equations
    #include "UEqns.H"
    
    // 3. Pressure-velocity coupling
    #include "pEqn.H"
    
    // 4. Energy (if enabled)
    #include "EEqns.H"
    
    // 5. Volume fraction correction
    #include "alphaEqns.H"
}
```

---

### 2.2 Momentum Equation Discretization

**Mathematical form:**
$$\frac{\partial (\alpha_k \rho_k \mathbf{u}_k)}{\partial t} + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k \mathbf{u}_k) = -\alpha_k \nabla p + \nabla \cdot \boldsymbol{\tau}_k + \alpha_k \rho_k \mathbf{g} + \mathbf{M}_k$$

**Code implementation (UEqns.H):**
```cpp
fvVectorMatrix UEqn
(
    // Implicit terms (contribute to matrix diagonal)
    fvm::ddt(alpha, rho, U)              // ∂(αρU)/∂t
  + fvm::div(alphaPhi, rho, U)           // ∇·(αρUU)
  + fvm::laplacian(nu, U)                // ∇·τ (viscous)
 ==
    // Explicit terms (evaluated from previous iteration)
  - alpha*fvc::grad(p)                   // -α∇p
  + alpha*rho*g                          // Body force
  + interfacialMomentumTransfer()        // M_k (drag, lift, VM, TD)
);

// Under-relaxation
UEqn.relax();

// Solve (if not in PIMPLE corrector loop)
if (pimple.nCorrPIMPLE() == 1)
{
    solve(UEqn == -fvc::grad(p));
}
```

---

### 2.3 Interphase Momentum Transfer

$$\mathbf{M}_k = \sum_{l \neq k} \left( \mathbf{F}^D_{kl} + \mathbf{F}^L_{kl} + \mathbf{F}^{VM}_{kl} + \mathbf{F}^{TD}_{kl} \right)$$

**Implementation:**
```cpp
tmp<volVectorField> phaseSystem::interfacialMomentumTransfer(
    const phaseModel& phase
) const
{
    tmp<volVectorField> tMTransfer
    (
        new volVectorField
        (
            IOobject("MTransfer", runTime.timeName(), mesh),
            mesh,
            dimensionedVector("zero", dimForce, Zero)
        )
    );
    volVectorField& MTransfer = tMTransfer();

    // Sum over all phase pairs involving this phase
    forAll(phases(), i)
    {
        const phaseModel& otherPhase = phases()[i];
        if (&otherPhase == &phase) continue;

        // Get phase pair key
        const phasePairKey key(phase.name(), otherPhase.name());
        
        // Drag: F_D = K_d * (U_other - U_this)
        if (dragModels_.found(key))
        {
            const volScalarField K = dragModels_[key]->K();
            MTransfer += K * (otherPhase.U() - phase.U());
        }

        // Lift: F_L = K_L * (U_other - U_this) × (∇ × U_this)
        if (liftModels_.found(key))
        {
            // Similar pattern...
        }

        // Virtual Mass, Turbulent Dispersion...
    }

    return tMTransfer;
}
```

---

## Part 3: Interfacial Model Architecture

### 3.1 Base Model Pattern (Strategy)

All interphase models follow **Strategy Pattern**:

```cpp
// Base class (interface)
class dragModel
{
protected:
    const phasePair& pair_;           // Reference to phase pair
    const dictionary& dict_;          // Model parameters

public:
    // DeclareRunTimeSelectionTable (factory)
    declareRunTimeSelectionTable
    (
        autoPtr,
        dragModel,
        dictionary,
        (
            const dictionary& dict,
            const phasePair& pair
        ),
        (dict, pair)
    );

    // Virtual interface (MUST implement)
    virtual tmp<volScalarField> K() const = 0;

    // Factory method
    static autoPtr<dragModel> New
    (
        const dictionary& dict,
        const phasePair& pair
    );
};
```

---

### 3.2 Example: Schiller-Naumann Drag

```cpp
class SchillerNaumannDrag : public dragModel
{
public:
    // Constructor (called by factory)
    SchillerNaumannDrag(
        const dictionary& dict,
        const phasePair& pair
    )
    :
        dragModel(dict, pair)
    {}

    // Drag coefficient calculation
    virtual tmp<volScalarField> K() const
    {
        const volScalarField& alpha1 = pair_.phase1().alpha();
        const volScalarField& alpha2 = pair_.phase2().alpha();
        const volVectorField& U1 = pair_.phase1().U();
        const volVectorField& U2 = pair_.phase2().U();

        // Reynolds number: Re = ρ₂|U₁-U₂|d/μ₂
        volScalarField Re
        (
            pair_.phase2().rho()
           *mag(U1 - U2)
           *pair_.dispersedPhase().d()
           /pair_.phase2().nu()
        );

        // Schiller-Naumann correlation
        volScalarField Cd
        (
            max(24.0/Re*(1.0 + 0.15*pow(Re, 0.687)), 0.44)
        );

        // Exchange coefficient K = (3/4) * (α₁α₂/α₂) * (ρ₂/d) * Cd * |U₁-U₂|
        return tmp<volScalarField>
        (
            new volScalarField
            (
                IOobject("K", ...),
                0.75
               *alpha1*alpha2/max(alpha2, scalar(1e-6))
               *pair_.phase2().rho()/pair_.dispersedPhase().d()
               *Cd
               *mag(U1 - U2)
            )
        );
    }

    // Metadata (for runtime selection)
    TypeName("SchillerNaumann");
};
```

---

### 3.3 Model Registration (Factory)

```cpp
// In SchillerNaumannDrag.C
defineTypeNameAndDebug(SchillerNaumannDrag, 0);
addToRunTimeSelectionTable
(
    dragModel,
    SchillerNaumannDrag,
    dictionary
);

// Usage in solver:
autoPtr<dragModel> ptr = dragModel::New(dict, pair);
// Reads "SchillerNaumann" from dict, calls new SchillerNaumannDrag(dict, pair)
```

**Why this pattern?** Adding new drag model requires:
1. Inherit from `dragModel`
2. Implement `K()`
3. Add `addToRunTimeSelectionTable` macro
4. Compile — no solver code modification needed!

---

### 3.4 Model Implementation Table

| Force Model | Base Class | Key Method | Typical Implementation |
|-------------|------------|------------|------------------------|
| Drag | `dragModel` | `K()` | SchillerNaumann, IshiiZuber, etc. |
| Lift | `liftModel` | `K()`, `Ci()` | constantCoefficient, Moraga |
| Virtual Mass | `virtualMassModel` | `Cvm()` | constantCoefficient (typically 0.5) |
| Turbulent Dispersion | `turbulentDispersionModel` | `D()` | constantCoefficient, Burns |

**All follow identical pattern:** Factory creation → virtual `K()` or coefficient method → return field.

---

## Part 4: Implementation Details

### 4.1 Memory Management

#### Smart Pointer Types

| Type | Ownership | Use Case | Example |
|------|-----------|----------|---------|
| `autoPtr<T>` | Unique | Single owner, no copying | `autoPtr<dragModel> ptr(new Schiller(...))` |
| `tmp<T>` | Shared with ref count | Temporary fields (prevents copies) | `tmp<volScalarField> tK = model.K()` |
| `refPtr<T>` | Shared (newer) | Similar to tmp but clearer | Preferred for temporary fields |

#### Lazy Allocation Pattern

```cpp
class phaseModel
{
    autoPtr<basicThermo> thermo_;

public:
    const basicThermo& thermo() const
    {
        if (!thermo_.valid())
        {
            // Allocate only when first accessed
            thermo_.set(basicThermo::New(phaseDict()).ptr());
        }
        return thermo_();
    }
};
```

**Benefit:** If simulation doesn't use heat transfer, `thermo_` never allocated → **save memory**.

---

### 4.2 fvm vs fvc (CRITICAL)

| Operator | fvm (Implicit) | fvc (Explicit) | Usage Rule |
|----------|----------------|----------------|------------|
| `ddt` | Adds matrix coefficients | Evaluates directly | **fvm** for ∂U/∂t, **fvc** for ∂α/∂t |
| `div` | Adds matrix coefficients | Evaluates directly | **fvm** for ∇·(αU), **fvc** for ∇·φ |
| `grad` | **N/A** | Evaluates directly | Always **fvc** |
| `laplacian` | Adds matrix coefficients | Evaluates directly | **fvm** for diffusion, **fvc** for reconstruction |

**Fundamental Rule:**
- **fvm** → Unknown field being solved → adds to matrix diagonal → **stable but expensive**
- **fvc** → Known field from previous iteration → explicit evaluation → **fast but less stable**

**Example:**
```cpp
// Momentum equation (U is unknown)
fvm::ddt(alpha, rho, U)      // Implicit in U
+ fvm::div(alphaPhi, rho, U) // Implicit in U
- fvc::grad(p)               // Explicit (p known from pEqn)

// Alpha equation (α is unknown)
fvm::ddt(alpha)
+ fvm::div(phi, alpha)
- fvc::div(phi)  // Explicit divergence-free correction
```

---

### 4.3 Under-Relaxation

$$\phi^{new} = \phi^{old} + \lambda(\phi^{calc} - \phi^{old})$$

| Field | λ (factor) | Stability Impact | Typical Range |
|-------|-----------|------------------|---------------|
| `alpha` | 0.7-0.9 | Prevents volume fraction overshoot | Medium-high |
| `U` | 0.6-0.8 | Stabilizes momentum coupling | Medium |
| `p` | 0.2-0.5 | Critical for PISO/PIMPLE convergence | Low |
| `k, ε, ω` | 0.5-0.8 | Turbulence equation stability | Medium |

**Case file:** `system/fvSolution`
```
relaxationFactors
{
    fields
    {
        p               0.3;
        rho             0.05;
        alpha.water     0.8;
    }
    equations
    {
        U               0.7;
        "(k|epsilon|omega)" 0.7;
    }
}
```

**Debugging Tip:** If simulation diverges:
1. Reduce `p` relaxation to 0.1-0.2
2. Reduce `U` relaxation to 0.5
3. Increase nOuterCorrectors (PIMPLE) to 3-5
4. Once stable, gradually increase λ for faster convergence

---

## Concept Check

<details>
<summary><b>1. phaseSystem ทำหน้าที่อะไร?</b></summary>

เป็น **facade** ที่รวมการจัดการทุกเฟสและ interphase models (drag, lift, VM, TD) ไว้ในที่เดียว ทำให้ solver เรียก `fluid.interfacialMomentumTransfer()` ได้เลยโดยไม่ต้องจัดการรายละเอียดของแต่ละ phase pair

**Design pattern:** Facade + Strategy
</details>

<details>
<summary><b>2. fvm กับ fvc ต่างกันอย่างไร? เมื่อไหร้ใช้ตัวไหน?</b></summary>

- **fvm (Finite Volume Matrix)**: สร้าง matrix coefficients สำหรับ implicit solve
  - ใช้กับ **field ที่เรากำลัง solve** ใน equation นั้น (เช่น U ใน UEqn)
  - เพิ่มค่าใน diagonal ของ matrix → stable แต่ใช้ memory เยอะ

- **fvc (Finite Volume Calculus)**: คำนวณค่า explicit จาก field ที่รู้แล้ว
  - ใช้กับ field ที่ถูก solve ใน equation อื่น (เช่น p ใน UEqn)
  - คำนวณโดยตรง → เร็วแต่ต้องระวัง stability

**Rule:** Field ที่ solve ใน eqn นั้น → fvm, field จาก iteration ก่อน → fvc
</details>

<details>
<summary><b>3. ทำไม interphase models ใช้ virtual function + factory pattern?</b></summary>

เพื่อ **runtime polymorphism** และ **open/closed principle**:

1. **Solver ไม่ต้องรู้ว่ามี model อะไรบ้าง** — เรียก `dragModel->K()` ผ่าน base class ได้เลย
2. **เพิ่ม model ใหม่ได้โดยไม่แก้ solver** — แค่ inherit, implement K(), และ register กับ runtime table
3. **Dictionary-driven selection** — ผู้ใช้ระบุ model ใน `phaseProperties` ได้โดยไม่ต้อง recompile

**Design patterns:** Strategy + Factory Method
</details>

<details>
<summary><b>4. Lazy allocation ใช้ทำไม?</b></summary>

เพื่อ **ประหยัด memory** ใน large-scale simulation:

- ถ้าไม่ได้เปิด heat transfer → `thermo_` ไม่ถูก allocate
- ถ้าไม่มี turbulence model บางเฟส → `turbulence_` ไม่ถูก allocate
- Allocate เมื่อ `thermo()` ถูกเรียกครั้งแรกเท่านั้น

**Trade-off:** มี overhead ตอนเรียกครั้งแรก (if check + allocation) แต่คุ้มสำหรับ large mesh
</details>

---

## Summary Diagram

```
multiphaseEulerFoam Architecture
├── Core Classes
│   ├── phaseModel → phase state (α, U, ρ, thermo, turbulence)
│   └── phaseSystem → facade for phases + interphase models
│
├── Interphase Models (Strategy Pattern)
│   ├── dragModel → SchillerNaumann, IshiiZuber, ...
│   ├── liftModel → constantCoefficient, Moraga, ...
│   ├── virtualMassModel → Cvm coefficients
│   └── turbulentDispersionModel → D coefficients
│
├── Solution Loop (PIMPLE)
│   ├── 1. fluid.correct() → update properties
│   ├── 2. UEqns.H → momentum (fvm for U, fvc for p)
│   ├── 3. pEqn.H → pressure-velocity coupling
│   ├── 4. EEqns.H → energy (if enabled)
│   └── 5. alphaEqns.H → volume fraction
│
└── Implementation
    ├── Smart Pointers → autoPtr, tmp (memory management)
    ├── fvm/fvc → implicit/explicit discretization
    └── Under-Relaxation → stability control (λ factors)
```

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [01_Solver_Overview.md](01_Solver_Overview.md)
- **บทถัดไป:** [04_Implementation_Details.md](04_Implementation_Details.md)
- **Interphase Forces:** [../04_INTERPHASE_FORCES/00_Overview.md](../04_INTERPHASE_FORCES/00_Overview.md)
- **Solver Configuration:** [../../MODULE_03_SINGLE_PHASE_FLOW/CONTENT/01_INCOMPRESSIBLE_FLOW_SOLVERS/03_Simulation_Control.md](../../MODULE_03_SINGLE_PHASE_FLOW/CONTENT/01_INCOMPRESSIBLE_FLOW_SOLVERS/03_Simulation_Control.md)