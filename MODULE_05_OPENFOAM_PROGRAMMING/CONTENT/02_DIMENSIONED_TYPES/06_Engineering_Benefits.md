# Engineering Benefits of Dimensioned Types

ประโยชน์ทางวิศวกรรมของ Dimensioned Types

---

## Overview

> Dimensioned Types = **Safety + Clarity + Maintainability**

---

## 1. Error Prevention

### Problem: Silent Unit Errors

```cpp
// Without dimension checking
scalar nu = 1e-6;     // m²/s or Pa·s? Unclear!
scalar rho = 1000;    // kg/m³ probably
scalar mu = rho * nu; // What if nu was dynamic viscosity?
```

### Solution: Compile-Time Detection

```cpp
dimensionedScalar nu("nu", dimKinematicViscosity, 1e-6);
dimensionedScalar rho("rho", dimDensity, 1000);
dimensionedScalar mu = rho * nu;  // Correct: [M L^-3][L² T^-1] = [M L^-1 T^-1]
```

---

## 2. Self-Documenting Code

### Before

```cpp
scalar val = 1.5e-5;  // What is this?
```

### After

```cpp
dimensionedScalar nu("nu", dimKinematicViscosity, 1.5e-5);
// Clear: kinematic viscosity, 1.5e-5 m²/s
```

---

## 3. Equation Verification

### Navier-Stokes Check

```cpp
// All terms should be [M L^-2 T^-2] = force/volume
fvm::ddt(rho, U)           // [M L^-3][L T^-1]/[T] = [M L^-2 T^-2] ✓
fvm::div(phi, U)           // [M T^-1][L T^-1]/[L³] = [M L^-2 T^-2] ✓
fvc::grad(p)               // [M L^-1 T^-2]/[L] = [M L^-2 T^-2] ✓
fvm::laplacian(mu, U)      // [M L^-1 T^-1][L T^-1]/[L²] = [M L^-2 T^-2] ✓
```

---

## 4. Interface Safety

### API Design

```cpp
// Function signature documents expectations
void setBoundaryCondition(
    const dimensionedScalar& velocity,  // Must be [L T^-1]
    const dimensionedScalar& pressure   // Must be [M L^-1 T^-2]
);

// Caller can't accidentally swap arguments
```

---

## 5. Dimensional Analysis

### Reynolds Number

```cpp
dimensionedScalar Re = rho * U * L / mu;
// [M L^-3][L T^-1][L][M^-1 L T] = [1] = dimless ✓

if (!Re.dimensions().dimensionless())
{
    FatalError << "Re should be dimensionless!";
}
```

---

## 6. Unit Conversion

### Automatic Handling

```cpp
// All internal calculations in SI
// Input/output can be different units with proper conversion
dimensionedScalar T_celsius("T", dimTemperature, 25);
dimensionedScalar T_kelvin = T_celsius + dimensionedScalar("", dimTemperature, 273.15);
```

---

## 7. Debugging Aid

### Error Messages

```
--> FOAM FATAL ERROR:
Inconsistent dimensions for +/-
   Left operand: [1 -1 -2 0 0 0 0]  (pressure)
   Right operand: [0 1 -1 0 0 0 0]  (velocity)
```

---

## 8. Best Practices

| Practice | Benefit |
|----------|---------|
| Always use dimensioned types | Catch errors early |
| Use predefined aliases | Consistent, readable |
| Check Re, Nu are dimless | Verify formulation |
| Don't disable checking | Loses all benefits |

---

## Quick Reference

| Benefit | How |
|---------|-----|
| Prevent errors | Compile/runtime checking |
| Document code | Units in type |
| Verify equations | Dimension match |
| Debug faster | Clear error messages |

---

## Concept Check

<details>
<summary><b>1. ทำไม dimensioned types ดีกว่า comments?</b></summary>

Comments ไม่มี **enforcement** — compiler ตรวจ dimensioned types ได้
</details>

<details>
<summary><b>2. ผลกระทบต่อ performance?</b></summary>

**มีน้อยมาก** — checking ส่วนใหญ่ทำ compile-time, runtime overhead minimal
</details>

<details>
<summary><b>3. ควร disable dimension checking ไหม?</b></summary>

**ไม่ควร** — จะเสียประโยชน์ทั้งหมด, ใช้แค่ตอน debug legacy code
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Pitfalls:** [05_Pitfalls_and_Solutions.md](05_Pitfalls_and_Solutions.md)
