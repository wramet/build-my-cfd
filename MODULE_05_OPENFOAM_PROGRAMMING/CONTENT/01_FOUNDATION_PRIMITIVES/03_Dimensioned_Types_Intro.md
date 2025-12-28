# Dimensioned Types Introduction

บทนำ Dimensioned Types

---

## Overview

> **Dimensioned Types** = Values with physical units attached

```cpp
dimensionedScalar rho("rho", dimDensity, 1000);
// Name: "rho"
// Units: [M L^-3]
// Value: 1000 kg/m³
```

---

## 1. Why Dimensioned Types?

| Benefit | Description |
|---------|-------------|
| **Safety** | Catches unit errors |
| **Clarity** | Units visible in code |
| **Automatic** | Compile + runtime checking |

---

## 2. Core Classes

### dimensionSet

```cpp
// 7 SI dimensions: [M, L, T, Θ, I, N, J]
dimensionSet(1, -3, 0, 0, 0, 0, 0)  // Density [kg/m³]
```

### Common Aliases

| Alias | Value | Unit |
|-------|-------|------|
| `dimless` | `[0 0 0 0 0 0 0]` | - |
| `dimLength` | `[0 1 0 0 0 0 0]` | m |
| `dimTime` | `[0 0 1 0 0 0 0]` | s |
| `dimMass` | `[1 0 0 0 0 0 0]` | kg |
| `dimVelocity` | `[0 1 -1 0 0 0 0]` | m/s |
| `dimPressure` | `[1 -1 -2 0 0 0 0]` | Pa |
| `dimDensity` | `[1 -3 0 0 0 0 0]` | kg/m³ |

---

## 3. dimensionedScalar

```cpp
// Create
dimensionedScalar rho("rho", dimDensity, 1000);
dimensionedScalar nu("nu", dimKinematicViscosity, 1e-6);

// Access
word n = rho.name();           // "rho"
dimensionSet d = rho.dimensions();  // [M L^-3]
scalar v = rho.value();        // 1000
```

---

## 4. dimensionedVector

```cpp
dimensionedVector g
(
    "g",
    dimAcceleration,
    vector(0, 0, -9.81)
);

// Access component
scalar gz = g.value().z();  // -9.81
```

---

## 5. Dimension Checking

### Valid Operations

```cpp
dimensionedScalar rho("rho", dimDensity, 1000);
dimensionedScalar U("U", dimVelocity, 10);

// OK: result is [M L^-1 T^-2] = pressure
dimensionedScalar dynP = 0.5 * rho * sqr(U);
```

### Invalid Operations

```cpp
dimensionedScalar p("p", dimPressure, 1000);
dimensionedScalar U("U", dimVelocity, 10);

// ERROR: Cannot add pressure + velocity
// dimensionedScalar bad = p + U;
```

---

## 6. Reading from Dictionary

```cpp
// In transportProperties:
// rho rho [1 -3 0 0 0 0 0] 1000;

dimensionedScalar rho("rho", dimDensity, transportProperties);
```

---

## 7. Common Patterns

### Characteristic Scales

```cpp
dimensionedScalar L("L", dimLength, 0.1);
dimensionedScalar Uref("Uref", dimVelocity, 1.0);
dimensionedScalar tRef = L / Uref;  // [T]
```

### Reynolds Number

```cpp
dimensionedScalar Re = rho * U * L / mu;
// Re is dimless: [M L^-3][L T^-1][L][M^-1 L T] = [1]
```

---

## Quick Reference

| Method | Description |
|--------|-------------|
| `.name()` | Get name |
| `.value()` | Get scalar value |
| `.dimensions()` | Get dimensionSet |
| `.component(i)` | Vector component |

---

## Concept Check

<details>
<summary><b>1. dimensionSet มีกี่ตัว?</b></summary>

**7 ตัว**: Mass, Length, Time, Temperature, Current, Moles, Luminous Intensity
</details>

<details>
<summary><b>2. ทำไม dimension checking สำคัญ?</b></summary>

**ป้องกัน physics errors** — เช่น บวก pressure กับ velocity
</details>

<details>
<summary><b>3. อ่าน dimensioned value จาก dict อย่างไร?</b></summary>

```cpp
dimensionedScalar rho("rho", dimDensity, dict);
```
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Basic Primitives:** [02_Basic_Primitives.md](02_Basic_Primitives.md)