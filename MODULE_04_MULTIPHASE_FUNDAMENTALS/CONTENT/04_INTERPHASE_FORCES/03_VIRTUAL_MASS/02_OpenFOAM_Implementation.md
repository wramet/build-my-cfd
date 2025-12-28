# Virtual Mass - OpenFOAM Implementation

การนำ Virtual Mass ไปใช้ใน OpenFOAM

---

## Overview

> **Virtual Mass** = แรงต้านเนื่องจากต้องเคลื่อนย้าย fluid รอบ bubble/particle เมื่อเร่ง

```mermaid
flowchart LR
    A[Bubble Accelerates] --> B[Displaces Surrounding Fluid]
    B --> C[Adds Inertia]
    C --> D[Virtual Mass Force]
```

---

## 1. Virtual Mass Equation

$$\mathbf{F}_{VM} = C_{VM} \rho_c \alpha_d \left(\frac{D\mathbf{u}_c}{Dt} - \frac{D\mathbf{u}_d}{Dt}\right)$$

| Symbol | Meaning | Unit |
|--------|---------|------|
| $C_{VM}$ | Virtual mass coefficient | - |
| $\rho_c$ | Continuous phase density | kg/m³ |
| $\alpha_d$ | Dispersed phase fraction | - |
| $D/Dt$ | Material derivative | m/s² |

---

## 2. Physical Interpretation

### Why "Virtual"?

- เมื่อ bubble เร่ง ต้องเคลื่อนย้าย liquid รอบๆ
- Effective mass = $m_{bubble} + C_{VM} \cdot m_{displaced}$
- สำหรับ sphere: $C_{VM} = 0.5$ → effective mass = 1.5× actual mass

### When Important

| Condition | Include VM? |
|-----------|-------------|
| ρ_d << ρ_c (gas-liquid) | **Yes** |
| ρ_d ≈ ρ_c (liquid-liquid) | Usually no |
| ρ_d >> ρ_c (solid-gas) | No |
| Transient/oscillating flow | **Yes** |

---

## 3. OpenFOAM Configuration

### phaseProperties

```cpp
virtualMass
{
    (air in water)
    {
        type    constantCoefficient;
        Cvm     0.5;
    }
}
```

### Available Models

| Model | Keyword | $C_{VM}$ |
|-------|---------|----------|
| Constant | `constantCoefficient` | User-specified |
| Lamb | `Lamb` | Shape-dependent |

---

## 4. Implementation Details

### Class Structure

```cpp
class virtualMassModel
{
public:
    virtual tmp<volScalarField> Cvm() const = 0;
    virtual tmp<volVectorField> F() const;
    virtual tmp<volScalarField> K() const;
};
```

### Force Calculation

```cpp
tmp<volVectorField> virtualMassModel::F() const
{
    const volVectorField& Uc = pair_.continuous().U();
    const volVectorField& Ud = pair_.dispersed().U();

    return Cvm()*pair_.continuous().rho()
        *(
            fvc::ddt(Uc) + (Uc & fvc::grad(Uc))
          - fvc::ddt(Ud) - (Ud & fvc::grad(Ud))
        );
}
```

---

## 5. Numerical Treatment

### Implicit vs Explicit

| Treatment | Stability | Use When |
|-----------|-----------|----------|
| Implicit (`fvm::ddt`) | Better | Strong acceleration |
| Semi-implicit | Good | General |
| Explicit | Faster | Weak effect |

### Contribution to Matrix

```cpp
// Adds to momentum equation
UEqn += Cvm*rhoc*
(
    fvm::ddt(Ud)
  - fvc::ddt(Uc)
  - (Uc & fvc::grad(Uc))
  + (Ud & fvc::grad(Ud))
);
```

---

## 6. Stability Considerations

### Under-Relaxation

```cpp
// system/fvSolution
relaxationFactors
{
    equations
    {
        "U.*"   0.7;
    }
}
```

### Time Step Limit

- VM adds **stiffness** to system
- May require smaller time step for transient simulations

---

## 7. Coefficient Values

| Shape | $C_{VM}$ |
|-------|----------|
| Sphere | 0.5 |
| Ellipsoid (prolate) | < 0.5 |
| Ellipsoid (oblate) | > 0.5 |
| Bubble swarm | 0.5 + f(α) |

### Concentration Correction

$$C_{VM}^{eff} = C_{VM} \cdot (1 + 2.78\alpha_d)$$

---

## 8. Verification

### Simple Test: Oscillating Bubble

```cpp
// Expected behavior
// Period = 2π√(m_eff / k)
// m_eff = m_bubble + Cvm * m_displaced
```

### Check Force Field

```cpp
functions
{
    vmForce
    {
        type    volFieldValue;
        fields  (virtualMassForce);
        operation   max;
        writeControl timeStep;
    }
}
```

---

## Quick Reference

| Question | Answer |
|----------|--------|
| When to use? | Gas-liquid, transient flow |
| Default $C_{VM}$? | 0.5 (sphere) |
| OpenFOAM keyword? | `virtualMass` in phaseProperties |
| Stability issue? | Use implicit, lower relaxation |

---

## Concept Check

<details>
<summary><b>1. ทำไม gas bubble ต้องใช้ virtual mass?</b></summary>

เพราะ **gas มี density ต่ำมาก** แต่ต้อง **displace liquid** รอบๆ เมื่อเคลื่อนที่ → effective inertia มาจาก liquid ที่ถูกเคลื่อนย้าย
</details>

<details>
<summary><b>2. ทำไม solid-gas ไม่ต้องใช้?</b></summary>

เพราะ **solid มี density สูง** กว่า gas มาก → inertia ของ solid dominate แล้ว, mass ของ displaced gas negligible
</details>

<details>
<summary><b>3. $C_{VM} = 0.5$ มาจากไหน?</b></summary>

จาก **potential flow theory** รอบ sphere — volume of fluid "trapped" กับ sphere = 0.5 × sphere volume
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Fundamental Concepts:** [01_Fundamental_Concepts.md](01_Fundamental_Concepts.md)
- **Drag Overview:** [../01_DRAG/00_Overview.md](../01_DRAG/00_Overview.md)