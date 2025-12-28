# Dimensioned Types Introduction

บทนำ Dimensioned Types — ระบบตรวจสอบหน่วยอัตโนมัติ

> **ทำไม Dimensioned Types สำคัญที่สุด?**
> - **ป้องกัน physics errors ที่ compiler จับไม่ได้**
> - Bug: บวก pressure + velocity → ผลลัพธ์ผิดแต่ compile ผ่าน
> - Dimensioned types จับ error นี้ได้ทันที

---

## Overview

> **💡 คิดแบบนี้:**
> `dimensionedScalar` = **ตัวเลข + ป้ายบอกหน่วย**
>
> เหมือนเขียน "1000 kg/m³" แทน "1000"
> ถ้าพยายามบวก "1000 kg/m³" + "10 m/s" → รู้ทันทีว่าผิด

```cpp
dimensionedScalar rho("rho", dimDensity, 1000);
// Name: "rho"
// Units: [M L^-3] = kg/m³
// Value: 1000
```

---

## 1. Why Dimensioned Types?

| ปัญหา | ผลกระทบ | Dimensioned Types ช่วยอย่างไร |
|-------|---------|------------------------------|
| ลืมแปลงหน่วย | ผลลัพธ์ผิด 1000x | Dimension mismatch error |
| บวก/ลบค่าต่าง units | Physics ผิด | Compile/runtime error |
| Debug ยาก | หา bug ไม่เจอ | Error บอกตำแหน่งชัด |

**ตัวอย่างจริง:**
```cpp
// ❌ Without dimension checking (ผิดแต่ compile ผ่าน)
double p = 1000;    // Pa? kPa? bar?
double U = 10;      // m/s? km/h?
double result = p + U;  // = 1010... แต่ไม่มีความหมาย!

// ✅ With dimension checking
dimensionedScalar p("p", dimPressure, 1000);
dimensionedScalar U("U", dimVelocity, 10);
// p + U;  // ERROR! Dimension mismatch
```

---

## 2. Core Classes

### dimensionSet — ระบบหน่วย SI

```cpp
// 7 SI base dimensions: [M, L, T, Θ, I, N, J]
// Mass, Length, Time, Temperature, Current, Moles, Luminous Intensity

dimensionSet(1, -3, 0, 0, 0, 0, 0)  // Density: kg/m³ = [M L^-3]
```

**การอ่าน dimensionSet:**
```
[1, -3, 0, 0, 0, 0, 0]
 ↓   ↓  ↓  ↓  ↓  ↓  ↓
 M  L^-3 T^0 Θ^0 I^0 N^0 J^0
= kg/m³
```

### Common Aliases — ใช้บ่อย

| Alias | Value | Unit | ใช้สำหรับ |
|-------|-------|------|----------|
| `dimless` | `[0 0 0 0 0 0 0]` | - | Coefficients |
| `dimLength` | `[0 1 0 0 0 0 0]` | m | Distance |
| `dimTime` | `[0 0 1 0 0 0 0]` | s | Time |
| `dimMass` | `[1 0 0 0 0 0 0]` | kg | Mass |
| `dimVelocity` | `[0 1 -1 0 0 0 0]` | m/s | Velocity |
| `dimPressure` | `[1 -1 -2 0 0 0 0]` | Pa | Pressure |
| `dimDensity` | `[1 -3 0 0 0 0 0]` | kg/m³ | Density |
| `dimKinematicViscosity` | `[0 2 -1 0 0 0 0]` | m²/s | ν |

---

## 3. dimensionedScalar

> **ใช้บ่อยที่สุด** — properties ส่วนใหญ่เป็น scalar

```cpp
// Create: name, dimensions, value
dimensionedScalar rho("rho", dimDensity, 1000);
dimensionedScalar nu("nu", dimKinematicViscosity, 1e-6);

// Access methods
word n = rho.name();           // "rho"
dimensionSet d = rho.dimensions();  // [M L^-3]
scalar v = rho.value();        // 1000
```

### Arithmetic Operations

```cpp
dimensionedScalar rho("rho", dimDensity, 1000);
dimensionedScalar nu("nu", dimKinematicViscosity, 1e-6);

// ✅ Valid: μ = ρν
dimensionedScalar mu = rho * nu;  // [M L^-3] * [L^2 T^-1] = [M L^-1 T^-1]

// μ is automatically dimDynamicViscosity!
```

---

## 4. dimensionedVector

```cpp
dimensionedVector g
(
    "g",              // Name
    dimAcceleration,  // [L T^-2]
    vector(0, 0, -9.81)  // Value
);

// Access components
scalar gz = g.value().z();  // -9.81

// Vector operations
dimensionedScalar gh = g & h;  // Dot product with position
```

---

## 5. Dimension Checking

### Valid Operations (dimensions multiply/divide correctly)

```cpp
dimensionedScalar rho("rho", dimDensity, 1000);      // [M L^-3]
dimensionedScalar U("U", dimVelocity, 10);           // [L T^-1]

// Dynamic pressure: 0.5 * ρ * U²
// [M L^-3] * [L T^-1]² = [M L^-3] * [L² T^-2] = [M L^-1 T^-2] = [Pa]
dimensionedScalar dynP = 0.5 * rho * sqr(U);  // ✅ OK
```

### Invalid Operations (dimension mismatch)

```cpp
dimensionedScalar p("p", dimPressure, 1000);  // [M L^-1 T^-2]
dimensionedScalar U("U", dimVelocity, 10);    // [L T^-1]

// p + U → [M L^-1 T^-2] + [L T^-1] = ???
// ERROR: Cannot add pressure + velocity

// dimensionedScalar bad = p + U;  // ❌ Runtime error!
```

---

## 6. Reading from Dictionary

> **ทำไมสำคัญ?**
> ส่วนใหญ่ค่าจะอ่านจาก file ไม่ได้ hardcode

```cpp
// In constant/transportProperties:
// rho rho [1 -3 0 0 0 0 0] 1000;

// Read in solver:
IOdictionary transportProperties(...);
dimensionedScalar rho("rho", dimDensity, transportProperties);
```

**Format ใน dictionary:**
```cpp
// name dimensions value
rho rho [1 -3 0 0 0 0 0] 1000;
//  ↑    ↑              ↑
// name  dimensions     value
```

---

## 7. Common Patterns

### Characteristic Scales (ใช้บ่อยใน non-dimensionalization)

```cpp
dimensionedScalar L("L", dimLength, 0.1);        // Length scale
dimensionedScalar Uref("Uref", dimVelocity, 1.0);  // Velocity scale
dimensionedScalar tRef = L / Uref;  // Time scale: [L] / [L T^-1] = [T]
```

### Reynolds Number (dimensionless check)

```cpp
dimensionedScalar Re = rho * U * L / mu;
// [M L^-3] * [L T^-1] * [L] * [M^-1 L T] = [1] = dimless

// Re.dimensions() == dimless → ถูกต้อง!
```

### Safe Operations

```cpp
// Always specify dimensions when creating
dimensionedScalar small("small", dimless, SMALL);  // Machine precision
dimensionedScalar great("great", dimless, GREAT);  // Large number

// Use in stabilization
rho / max(rho, small);  // ป้องกัน divide by zero
```

---

## Quick Reference

| Method | Description | ตัวอย่าง |
|--------|-------------|---------|
| `.name()` | Get name | `rho.name()` → "rho" |
| `.value()` | Get scalar value | `rho.value()` → 1000 |
| `.dimensions()` | Get dimensionSet | `rho.dimensions()` |
| `.component(i)` | Vector component | `g.value().z()` |

---

## 🧠 Concept Check

<details>
<summary><b>1. dimensionSet มีกี่ตัว? คืออะไรบ้าง?</b></summary>

**7 ตัว (SI base units):**
1. **M** — Mass [kg]
2. **L** — Length [m]
3. **T** — Time [s]
4. **Θ** — Temperature [K]
5. **I** — Current [A]
6. **N** — Moles [mol]
7. **J** — Luminous Intensity [cd]

**ตัวอย่าง:**
- Velocity: [0 1 -1 0 0 0 0] = m/s = L/T
- Pressure: [1 -1 -2 0 0 0 0] = Pa = kg/(m·s²) = M/(L·T²)
</details>

<details>
<summary><b>2. ทำไม dimension checking สำคัญ?</b></summary>

**ป้องกัน physics errors:**
```cpp
// Real bug that happened:
// Forgot to convert km to m
double distance = 1.5;    // Intended: 1.5 km = 1500 m
double speed = 10;        // m/s
double time = distance / speed;  // = 0.15 s... wrong!

// With dimensioned types:
dimensionedScalar L("L", dimLength, 1500);  // Must be in SI (meters)
dimensionedScalar U("U", dimVelocity, 10);
dimensionedScalar t = L / U;  // = 150 s ✓
```
</details>

<details>
<summary><b>3. อ่าน dimensioned value จาก dict อย่างไร?</b></summary>

**Dictionary format:**
```cpp
// constant/transportProperties
nu nu [0 2 -1 0 0 0 0] 1e-6;
```

**Code:**
```cpp
dimensionedScalar nu("nu", dimKinematicViscosity, transportProperties);
```

หรือถ้าไม่รู้ dimensions ล่วงหน้า:
```cpp
dimensionedScalar nu(transportProperties.lookup("nu"));
```
</details>

<details>
<summary><b>4. ถ้า dimensions ไม่ตรง error อะไร?</b></summary>

**Runtime error:**
```
--> FOAM FATAL ERROR:
LHS and RHS of + have different dimensions
dimensions: [1 -1 -2 0 0 0 0] + [0 1 -1 0 0 0 0]
```

**อ่าน dimensions:**
- LHS: [1 -1 -2 0 0 0 0] = Pa (pressure)
- RHS: [0 1 -1 0 0 0 0] = m/s (velocity)
- Cannot add pressure + velocity!
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **บทก่อน:** [02_Basic_Primitives.md](02_Basic_Primitives.md) — scalar, vector
- **บทถัดไป:** [04_Smart_Pointers.md](04_Smart_Pointers.md) — autoPtr, tmp
- **Deep Dive:** [../02_DIMENSIONED_TYPES/00_Overview.md](../02_DIMENSIONED_TYPES/00_Overview.md)