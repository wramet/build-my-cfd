# Dimensional Checking

การตรวจสอบมิติใน OpenFOAM

> [!TIP] ทำไม Dimensional Checking สำคัญ?
> การตรวจสอบมิติ (Dimensional Checking) เป็นกลไกป้องกันข้อผิดพลาดที่ทรงพลังที่สุดใน OpenFOAM มันช่วย:
> - **ป้องกันสมการทางฟิสิกส์ผิดพลาด**: เช่น บวก pressure กับ velocity ไม่ได้
> - **ตรวจจับ bug ตั้งแต่ compile-time**: ก่อนรันจริง
> - **รับประกันความถูกต้องของหน่วย**: ทุก field ต้องมีหน่วย SI ถูกต้อง
> - **ช่วย debug**: แจ้ง error พร้อม dimension ที่คาดหวัง vs จริง
>
> **ในภาษาอื่น (Python/MATLAB)**: คุณอาจคำนวณ `p + U` ได้ แต่ผลลัพธ์ผิดทางฟิสิกส์
> **ใน OpenFOAM**: Compiler จะฟ้อง error ทันทีว่า "dimension mismatch"
>
> สิ่งนี้ทำให้โค้ด CFD ของคุณ **ปลอดภัยกว่า** และ **debug ง่ายกว่า** อย่างมาก

---

## Overview

> OpenFOAM checks dimensions at **compile-time** and **run-time**

---

## 1. dimensionSet

> [!NOTE] **📂 OpenFOAM Context**
> **ไฟล์ที่เกี่ยวข้อง:**
> - `src/OpenFOAM/dimensionSet/dimensionSet.H` (การนิยาม class)
> - `src/OpenFOAM/dimensionSets/dimensionSets.H` (predefined aliases)
> - `0/` field files (ระบุ `dimensions [ ... ]` ในทุก field)
> - `constant/transportProperties`, `constant/turbulenceProperties` (กำหนด dimension ของค่าคงที่)
>
> **Keywords:**
> - `dimensions [0 1 -1 0 0 0 0]` → ระบุหน่วยใน field files
> - `dimensionSet(1, -1, -2, 0, 0, 0, 0)` → ในโค้ด C++
> - `[M L T Θ I N J]` → Mass, Length, Time, Temperature, Current, Moles, Luminous
>
> **ใน case ของคุณ:**
> - ทุก field ใน `0/p`, `0/U`, `0/T` มีบรรทัด `dimensions [...]`
> - ถ้าหน่วยไม่ตรง → Solver crash ทันที

```cpp
// 7 dimensions: [M, L, T, Θ, I, N, J]
dimensionSet(mass, length, time, temp, moles, current, luminous)

// Examples
dimPressure   = dimensionSet(1, -1, -2, 0, 0, 0, 0)  // kg/(m·s²)
dimVelocity   = dimensionSet(0, 1, -1, 0, 0, 0, 0)   // m/s
dimDensity    = dimensionSet(1, -3, 0, 0, 0, 0, 0)   // kg/m³
dimless       = dimensionSet(0, 0, 0, 0, 0, 0, 0)    // -
```

---

## 2. Common Dimensions

> [!NOTE] **📂 OpenFOAM Context**
> **การใช้งานใน Case Files:**
> - **Pressure fields** (`0/p`, `0/p_rgh`): `dimensions [1 -1 -2 0 0 0 0]` (Pa)
> - **Velocity fields** (`0/U`): `dimensions [0 1 -1 0 0 0 0]` (m/s)
> - **Density** (`constant/transportProperties`): `dimensions [1 -3 0 0 0 0 0]` (kg/m³)
> - **Turbulence fields** (`0/k`, `0/epsilon`): `dimensions [0 2 -2 0 0 0 0]` (m²/s²)
>
> **สิ่งที่ต้องจำ:**
> - ทุก field ใน OpenFOAM ต้องมีหน่วย SI (ไม่มี inch, psi, ฯลฯ)
> - ถ้าเปลี่ยนหน่วย → แก้ใน `dimensions [...]` และค่าทุกค่าใช้หน่วยเดียวกัน
> - Solver จะ check อัตโนมัติว่า equation ถูกต้องหรือไม่

| Quantity | dimensionSet | Unit |
|----------|--------------|------|
| Length | `[0 1 0 0 0 0 0]` | m |
| Time | `[0 0 1 0 0 0 0]` | s |
| Mass | `[1 0 0 0 0 0 0]` | kg |
| Velocity | `[0 1 -1 0 0 0 0]` | m/s |
| Pressure | `[1 -1 -2 0 0 0 0]` | Pa |
| Viscosity | `[1 -1 -1 0 0 0 0]` | Pa·s |
| k (TKE) | `[0 2 -2 0 0 0 0]` | m²/s² |
| ε | `[0 2 -3 0 0 0 0]` | m²/s³ |

---

## 3. How Checking Works

> [!NOTE] **📂 OpenFOAM Context**
> **เมื่อ Solver ทำงาน:**
> - **Compilation**: เวลา compile solver/custom boundary condition → ตรวจสอบ type safety
> - **Runtime**: เวลา solver รัน → ตรวจสอบ arithmetic operations
> - **Field algebra**: ทุกครั้งที่บวก/ลบ/คูณ/หา fields → ตรวจสอบหน่วย
>
> **Error messages ที่พบบ่อย:**
> ```
> --> FOAM FATAL ERROR:
> LHS and RHS of + have different dimensions
>     LHS: [0 2 -2 0 0 0 0]
>     RHS: [1 -1 -2 0 0 0 0]
>
> From function operator+(...) in file ...
> ```
> → แปลว่า: คุณบวก field 2 ตัวที่มีหน่วยไม่ตรงกัน (เช่น บวก pressure กับ kinetic energy)

### Valid Operations

```cpp
volScalarField p;  // [M L^-1 T^-2]
volScalarField rho;  // [M L^-3]
volVectorField U;  // [L T^-1]

// OK: dimensions match
volScalarField dynP = 0.5 * rho * magSqr(U);
// [M L^-3] * [L^2 T^-2] = [M L^-1 T^-2] ✓
```

### Invalid Operations

```cpp
// ERROR: dimension mismatch
// volScalarField bad = p + U;
// [M L^-1 T^-2] + [L T^-1] = ERROR!
```

---

## 4. Predefined Aliases

> [!NOTE] **📂 OpenFOAM Context**
> **ไฟล์ต้นทาง:**
> - `src/OpenFOAM/dimensionSets/dimensionSets.H` → นิยาม `dimPressure`, `dimVelocity`, ฯลฯ
> - ถ้าหาไม่เจอ → ต้องระบุเป็น `dimensionSet(1, -1, -2, 0, 0, 0, 0)` เอง
>
> **การใช้งานใน Custom Code:**
> ```cpp
> // ใน custom boundary condition หรือ solver
> dimensionSet pressureDims = dimPressure;  // สะดวกกว่าจำตัวเลข
> ```
> → ทำให้โค้ดอ่านง่ายขึ้น และลดความผิดพลาดจากการพิมพ์ตัวเลขผิด

```cpp
// From dimensionSets.H
dimless         // Dimensionless
dimLength       // [0 1 0 0 0 0 0]
dimTime         // [0 0 1 0 0 0 0]
dimMass         // [1 0 0 0 0 0 0]
dimTemperature  // [0 0 0 1 0 0 0]
dimVelocity     // [0 1 -1 0 0 0 0]
dimPressure     // [1 -1 -2 0 0 0 0]
dimDensity      // [1 -3 0 0 0 0 0]
dimDynamicViscosity  // [1 -1 -1 0 0 0 0]
dimKinematicViscosity // [0 2 -1 0 0 0 0]
dimForce        // [1 1 -2 0 0 0 0]
dimEnergy       // [1 2 -2 0 0 0 0]
dimPower        // [1 2 -3 0 0 0 0]
```

---

## 5. Operations on Dimensions

> [!NOTE] **📂 OpenFOAM Context**
> **การคำนวณระหว่าง Fields:**
> - **Multiplication**: `p * rho` → หน่วยคูณกัน (pressure × density = energy density)
> - **Division**: `p / rho` → หน่วยหารกัน (pressure/density = velocity²)
> - **Power**: `magSqr(U)` → velocity ยกกำลังสอง (m²/s²)
>
> **ตัวอย่างใน Solver:**
> ```cpp
> // dynamic pressure ใน simpleFoam
> volScalarField dynP = 0.5 * rho * magSqr(U);  // [kg/m³] × [m²/s²] = [Pa]
> ```
> → Solver จะ check อัตโนมัติว่า `dynP` มีหน่วยเป็น pressure จริงไหม
>
> **สิ่งที่เกิดขึ้นเบื้องหลัง:**
> - ทุกครั้งที่คูณ/หา fields → `dimensionSet` จะคำนวณหน่วยให้
> - ถ้าผลลัพธ์ไม่ตรงกับ `dimensions[...]` ของ field ปลายทาง → ERROR

### Multiplication

```cpp
// dims = [1 -1 -2] * [1 -3 0] = [2 -4 -2]
dimensionSet result = dimPressure * dimDensity;
```

### Division

```cpp
// dims = [1 -1 -2] / [1 -3 0] = [0 2 -2]
dimensionSet result = dimPressure / dimDensity;
```

### Power

```cpp
// dims = [0 1 -1]^2 = [0 2 -2]
dimensionSet result = pow(dimVelocity, 2);
```

---

## 6. Checking Control

> [!NOTE] **📂 OpenFOAM Context**
> **เมื่อไหร่ควร Disable Checking?**
> - **โดยปกติ: ไม่ควรทำเลย!** (เป็นการปิด safety mechanism)
> - **กรณีที่อาจต้องการ:**
>   - Debug โค้ดเก่า (legacy code) ที่ไม่มี dimension
>   - ทดสอบ algorithm ใหม่ที่ยังไม่สมบูรณ์
>   - แปลงโค้ดจากภาษาอื่น (Python/MATLAB → OpenFOAM)
>
> **วิธีการ:**
> ```cpp
> dimensionSet::checking(false);  // อันตราย! ใช้เฉพาะ debug
> ```
> → **หลังจาก debug เสร็จ → ต้องเปิดกลับมาทันที!**
>
> **ผลกระทบ:**
> - ถ้าปิด checking → สมการผิดจะไม่ error แต่ผลลัพธ์จะ **ผิดทางฟิสิกส์**
> - ค่าที่คำนวณได้อาจมีหน่วยปนกัน (เช่น บวก pressure กับ velocity)

```cpp
// Disable checking (dangerous!)
dimensionSet::checking(false);

// Re-enable
dimensionSet::checking(true);
```

### When to Disable

- **Never** in production
- Only for debugging specific issues
- Legacy code migration

---

## 7. Debug Messages

> [!NOTE] **📂 OpenFOAM Context**
> **วิธีอ่าน Error Messages:**
> เมื่อเกิด dimension error ใน log file (เช่น `log.simpleFoam`):
> ```
> --> FOAM FATAL ERROR:
> Dimensions of ... are not consistent
>     dimensions: [0 2 -2 0 0 0 0]
>     required: [1 -1 -2 0 0 0 0]
> ```
>
> **การแก้ปัญหา:**
> 1. **ดูว่า error ที่บรรทัดไหน** → จะบอกชื่อ field และ operation
> 2. **เปรียบเทียบ dimension**:
>    - `dimensions: [...]` → หน่วยของค่าที่คุณกำลังคำนวณ
>    - `required: [...]` → หน่วยที่ field ปลายทางต้องการ
> 3. **ตรวจสอบสมการ** → ดูว่าคูณ/หา/ยกกำลังถูกไหม
> 4. **ตรวจสอบ input fields** → ดู `0/` files ว่า `dimensions[...]` ถูกไหม
>
> **ตัวอย่าง:**
> - ถ้าได้ `[0 2 -2]` แต่ต้องการ `[1 -1 -2]` → คุณคำนวณ kinetic energy (m²/s²) แต่ field ต้องการ pressure (Pa)
> - แก้โดยคูณ density: `rho * kE` → `[kg/m³] × [m²/s²] = [kg/(m·s²)] = [Pa]` ✓

```cpp
// When dimension error occurs:
// --> FOAM FATAL ERROR:
// Dimension set of ... is not the same as ...
// Expected: [1 -1 -2 0 0 0 0]
// Actual:   [0 2 -2 0 0 0 0]
```

---

## Quick Reference

> [!NOTE] **📂 OpenFOAM Context**
> **การใช้งานใน Custom Boundary Conditions หรือ Function Objects:**
> ```cpp
> // ตรวจสอบ dimension ของ field
> if (!p.dimensions().dimensionless())
> {
>     Info << "Field p has dimensions: " << p.dimensions() << endl;
> }
>
> // เปรียบเทียบ dimension
> if (U.dimensions() == dimVelocity)
> {
>     // OK: U เป็น velocity field
> }
> ```
>
> **การ Debug ใน Solver:**
> - พิมพ์ dimension ออกมาดู: `Info << field.dimensions() << endl;`
> - ตรวจสอบว่า field เป็น dimensionless ไหม: `field.dimensions().dimensionless()`
> - เปรียบเทียบกับ predefined: `field.dimensions() == dimPressure`

| Method | Description |
|--------|-------------|
| `field.dimensions()` | Get dimensionSet |
| `dims.dimensionless()` | Check if dimless |
| `dims == other` | Compare dimensions |
| `dims * other` | Multiply dimensions |

---

## 🧠 Concept Check

<details>
<summary><b>1. ทำไม 7 dimensions?</b></summary>

**SI base units**: Mass, Length, Time, Temperature, Current, Moles, Luminous Intensity
</details>

<details>
<summary><b>2. OpenFOAM ตรวจ dimension เมื่อไหร่?</b></summary>

- **Compile-time**: Type mismatches
- **Run-time**: Arithmetic operations
</details>

<details>
<summary><b>3. ถ้า dimension error เกิดขึ้น ทำอย่างไร?</b></summary>

1. ตรวจสอบสูตร/สมการ
2. ตรวจสอบหน่วยของ inputs
3. อย่าใช้ `checking(false)`!
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Dimensioned Types:** [../02_DIMENSIONED_TYPES/00_Overview.md](../02_DIMENSIONED_TYPES/00_Overview.md)