# Code Architecture: multiphaseEulerFoam

สถาปัตยกรรมของ solver สำหรับการไหลหลายเฟส

---

## Class Hierarchy Overview

```
phaseSystem
├── phases_ (PtrListDictionary<phaseModel>)
│   ├── water: phaseModel
│   │   ├── alpha_ (volScalarField)
│   │   ├── U_ (volVectorField)
│   │   ├── rho_ (volScalarField)
│   │   ├── thermo_ (autoPtr<basicThermo>)
│   │   └── turbulence_ (autoPtr<...>)
│   └── air: phaseModel
│       └── ...
├── dragModels_ (HashTable<dragModel>)
├── liftModels_ (HashTable<liftModel>)
├── virtualMassModels_ (HashTable<...>)
└── heatTransferModels_ (HashTable<...>)
```

---

## Core Classes

### 1. phaseModel

เก็บข้อมูลของแต่ละเฟส:

```cpp
class phaseModel
{
protected:
    volScalarField alpha_;  // Volume fraction
    volVectorField U_;      // Velocity
    volScalarField rho_;    // Density
    
    autoPtr<basicThermo> thermo_;
    autoPtr<turbulenceModel> turbulence_;
    
public:
    const volScalarField& alpha() const { return alpha_; }
    volVectorField& U() { return U_; }
    
    virtual void correct() = 0;  // Update properties
};
```

**Case file mapping:**
- `alpha_` ← `0/alpha.water`
- `U_` ← `0/U.water`

---

### 2. phaseSystem

จัดการทุกเฟสและ interphase models:

```cpp
class phaseSystem
{
protected:
    PtrListDictionary<phaseModel> phases_;
    
    // Interphase models (key = phasePairKey)
    HashTable<autoPtr<dragModel>> dragModels_;
    HashTable<autoPtr<liftModel>> liftModels_;
    HashTable<autoPtr<virtualMassModel>> vmModels_;
    
public:
    const PtrListDictionary<phaseModel>& phases() const;
    
    tmp<volVectorField> interfacialMomentumTransfer(
        const phaseModel& phase
    ) const;
    
    virtual void correct();
};
```

**Case file mapping:**
- `phases_` ← `constant/phaseProperties`
- `dragModels_` ← `constant/phaseProperties` → `drag { ... }`

---

### 3. dragModel (Strategy Pattern)

```cpp
class dragModel
{
protected:
    const phasePair& pair_;
    
public:
    virtual tmp<volScalarField> K(
        const volScalarField& alpha1,
        const volScalarField& alpha2
    ) const = 0;
    
    // Factory method
    static autoPtr<dragModel> New(
        const dictionary& dict,
        const phasePair& pair
    );
};

// Example: Schiller-Naumann implementation
class SchillerNaumannDrag : public dragModel
{
public:
    virtual tmp<volScalarField> K(...) const
    {
        // CD = 24/Re * (1 + 0.15*Re^0.687)
        return dragCoefficient;
    }
};
```

---

## Solution Algorithm (PIMPLE)

```
while (pimple.loop())
{
    1. #include "UEqns.H"    // Solve momentum
    2. #include "pEqn.H"     // Pressure-velocity coupling
    3. #include "EEqns.H"    // Energy (if enabled)
}
```

### Momentum Equation

$$\frac{\partial (\alpha_k \rho_k \mathbf{u}_k)}{\partial t} + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k \mathbf{u}_k) = -\alpha_k \nabla p + \nabla \cdot \boldsymbol{\tau}_k + \alpha_k \rho_k \mathbf{g} + \mathbf{M}_k$$

```cpp
// UEqns.H
fvVectorMatrix UEqn
(
    fvm::ddt(alpha, rho, U)       // ∂(αρU)/∂t
  + fvm::div(alphaPhi, rho, U)    // ∇·(αρUU)
  ==
    - alpha*fvc::grad(p)          // -α∇p
  + fvc::div(alpha*R)             // ∇·τ
  + alpha*rho*g                   // Body force
  + interfacialMomentumTransfer() // Drag, Lift, VM
);
```

### Interphase Momentum Transfer

$$\mathbf{M}_k = \sum_{l} (\mathbf{F}^D_{kl} + \mathbf{F}^L_{kl} + \mathbf{F}^{VM}_{kl})$$

---

## Memory Management

### Smart Pointers

| Type | Use | Example |
|------|-----|---------|
| `autoPtr<T>` | Unique ownership | `autoPtr<dragModel> ptr(new Schiller(...))` |
| `tmp<T>` | Temporary with ref count | `tmp<volScalarField> tK = drag.K()` |

### Lazy Allocation

```cpp
const GeometricField& field()
{
    if (!fieldPtr_)
    {
        fieldPtr_.reset(new GeometricField(...));
    }
    return fieldPtr_();
}
```

---

## fvm vs fvc

| Operator | fvm (Implicit) | fvc (Explicit) |
|----------|----------------|----------------|
| `ddt` | Adds to matrix | Evaluates directly |
| `div` | Adds to matrix | Evaluates directly |
| `grad` | — | Evaluates directly |
| `laplacian` | Adds to matrix | Evaluates directly |

**Rule:** Use `fvm` for unknown (solved) terms, `fvc` for known terms.

---

## Under-Relaxation

$$\phi^{new} = \phi^{old} + \lambda(\phi^{calc} - \phi^{old})$$

| Field | λ | Notes |
|-------|---|-------|
| alpha | 0.7-0.9 | Medium-high |
| U | 0.6-0.8 | Medium |
| p | 0.2-0.5 | Low |

**Case file:** `system/fvSolution` → `relaxationFactors`

---

## Concept Check

<details>
<summary><b>1. phaseSystem ทำหน้าที่อะไร?</b></summary>

เป็นตัวกลางจัดการทุกเฟสและ interphase models (drag, lift, etc.) ทำให้ solver ไม่ต้องจัดการรายละเอียดของแต่ละ pair
</details>

<details>
<summary><b>2. fvm กับ fvc ต่างกันอย่างไร?</b></summary>

- **fvm**: สร้าง matrix coefficients สำหรับ implicit solve (unknown → solved)
- **fvc**: คำนวณค่า explicit จาก field ที่รู้แล้ว (known → calculated)
</details>

<details>
<summary><b>3. ทำไม dragModel ใช้ virtual function?</b></summary>

เพื่อ **runtime polymorphism** — solver เรียก `K()` ผ่าน base class แต่ได้ implementation ที่ถูกต้องตาม type ที่ระบุใน dictionary
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [01_Solver_Overview.md](01_Solver_Overview.md)
- **บทถัดไป:** [03_Boundary_Conditions.md](03_Boundary_Conditions.md)