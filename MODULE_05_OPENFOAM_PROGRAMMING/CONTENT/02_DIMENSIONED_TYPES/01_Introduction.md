# Dimensioned Types - Introduction

บทนำ Dimensioned Types ใน OpenFOAM — Values with Physical Units

> **ทำไมต้องเรียนบทนี้?**
> - เข้าใจวิธีสร้าง dimensioned values
> - รู้วิธีอ่านจาก dictionary
> - ป้องกัน common errors

---

## Overview

> **💡 Dimensioned Types = ตัวเลข + หน่วย + ชื่อ**
>
> ไม่ใช่แค่ `1000` แต่คือ `rho = 1000 kg/m³`

```cpp
dimensionedScalar rho("rho", dimDensity, 1000);
// Name: "rho"           → ใช้ใน output/debug
// Dimensions: [M L^-3]  → ตรวจสอบ physics
// Value: 1000           → ค่าจริง
```

---

## 1. Why Dimensioned Types?

| Benefit | Description |
|---------|-------------|
| **Type Safety** | Prevents unit mismatches |
| **Self-documenting** | Units visible in code |
| **Error Detection** | Catches physics errors early |
| **Automatic Checking** | Both compile and runtime |

---

## 2. Core Classes

### dimensionedScalar

```cpp
dimensionedScalar nu("nu", dimKinematicViscosity, 1e-6);

// Access
word name = nu.name();           // "nu"
dimensionSet dims = nu.dimensions();  // [0 2 -1 0 0 0 0]
scalar value = nu.value();       // 1e-6
```

### dimensionedVector

```cpp
dimensionedVector g("g", dimAcceleration, vector(0, 0, -9.81));
```

### dimensionedTensor

```cpp
dimensionedTensor I("I", dimless, tensor::I);
```

---

## 3. dimensionSet

```cpp
// 7 SI base dimensions
dimensionSet(M, L, T, Θ, I, N, J)

// Common:
dimless      // [0 0 0 0 0 0 0]
dimLength    // [0 1 0 0 0 0 0]
dimTime      // [0 0 1 0 0 0 0]
dimMass      // [1 0 0 0 0 0 0]
dimVelocity  // [0 1 -1 0 0 0 0]
dimPressure  // [1 -1 -2 0 0 0 0]
dimDensity   // [1 -3 0 0 0 0 0]
```

---

## 4. Creating Dimensioned Values

### From literals

```cpp
dimensionedScalar T0("T0", dimTemperature, 300.0);
```

### From dictionary

```cpp
// In constant/transportProperties:
// nu [0 2 -1 0 0 0 0] 1e-6;

dimensionedScalar nu("nu", dimKinematicViscosity, transProp);
```

### From file format

```cpp
// File format:
// nu nu [0 2 -1 0 0 0 0] 1e-6;
```

---

## 5. Operations

### Arithmetic

```cpp
dimensionedScalar a("a", dimLength, 2.0);
dimensionedScalar b("b", dimLength, 3.0);

dimensionedScalar c = a + b;    // OK: same dims
dimensionedScalar d = a * b;    // Result: dimArea
```

### Functions

```cpp
dimensionedScalar sqr_a = sqr(a);   // dimLength²
dimensionedScalar sqrt_a = sqrt(a); // dimLength^0.5
dimensionedScalar mag_v = mag(v);   // scalar from vector
```

---

## 6. Common Patterns

### Characteristic Length

```cpp
dimensionedScalar L("L", dimLength, mesh.bounds().span().x());
```

### Reynolds Number

```cpp
dimensionedScalar Re = rho * U * L / mu;
// [M L^-3][L T^-1][L][M^-1 L T] = [1]
```

### Time Scale

```cpp
dimensionedScalar tau = L / Uref;  // [L]/[L T^-1] = [T]
```

---

## 7. In Fields

```cpp
// Initialize field with dimensioned value
volScalarField T
(
    IOobject(...),
    mesh,
    dimensionedScalar("T", dimTemperature, 300)
);

// Uniform operations
T *= 1.0 + 0.01 * (runTime.value() / runTime.endTime().value());
```

---

## Quick Reference

| Method | Description |
|--------|-------------|
| `.name()` | Get name |
| `.value()` | Get scalar value |
| `.dimensions()` | Get dimensionSet |
| `.component(i)` | Get vector component |

---

## 🧠 Concept Check

<details>
<summary><b>1. ทำไมต้องใช้ dimensionedScalar แทน scalar?</b></summary>

เพื่อ **track physical units** — ป้องกัน errors จาก unit mismatches
</details>

<details>
<summary><b>2. dimensionSet 7 ตัวคืออะไร?</b></summary>

**SI base units**: Mass, Length, Time, Temperature, Current, Moles, Luminous Intensity
</details>

<details>
<summary><b>3. อ่าน dimensions จาก dictionary อย่างไร?</b></summary>

```cpp
dimensionedScalar nu("nu", dimViscosity, dict);
// หรือ
dict.lookup<dimensionedScalar>("nu")
```
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Mathematical Formulations:** [07_Mathematical_Formulations.md](07_Mathematical_Formulations.md)