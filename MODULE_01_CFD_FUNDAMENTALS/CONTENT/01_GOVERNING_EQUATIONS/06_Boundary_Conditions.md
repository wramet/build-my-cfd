# Boundary Conditions

Boundary Conditions (BCs) คือ **ข้อกำหนดทางคณิตศาสตร์** ที่บอก solver ว่าของไหลมีพฤติกรรมอย่างไรที่ขอบเขต

> **ทำไม BC สำคัญที่สุดหลัง mesh?**
> - BC ผิด → **simulation diverge** หรือผลลัพธ์ผิด
> - ต้องรู้กฎ **U-p coupling** — fixedValue + zeroGradient
> - เข้าใจ **wall functions** สำหรับ turbulence

---

---

## ประเภทของ Boundary Conditions

### ประเภททางคณิตศาสตร์

| ประเภท | ชื่อ | ความหมาย | OpenFOAM |
|--------|------|----------|----------|
| **Dirichlet** | Fixed Value | กำหนดค่าโดยตรง | `fixedValue` |
| **Neumann** | Fixed Gradient | กำหนด gradient | `zeroGradient`, `fixedGradient` |
| **Mixed** | ผสม | รวม Dirichlet + Neumann | `mixed` |

### ประเภททางกายภาพ

| ประเภท | ความหมาย | Velocity | Pressure |
|--------|----------|----------|----------|
| **Inlet** | ของไหลเข้า | `fixedValue` | `zeroGradient` |
| **Outlet** | ของไหลออก | `zeroGradient` | `fixedValue` (0) |
| **Wall** | ผนังแข็ง | `noSlip` (= 0) | `zeroGradient` |
| **Symmetry** | ระนาบสมมาตร | `symmetry` | `symmetry` |
| **Periodic** | การไหลซ้ำรอบ | `cyclic` | `cyclic` |

---

## รูปแบบไฟล์ใน OpenFOAM

BCs ถูกกำหนดในไฟล์ใน directory `0/`:

```cpp
// ไฟล์: 0/U
dimensions      [0 1 -1 0 0 0 0];   // m/s
internalField   uniform (0 0 0);    // ค่าเริ่มต้น

boundaryField
{
    inlet
    {
        type    fixedValue;
        value   uniform (10 0 0);   // 10 m/s ในทิศ x
    }
    
    outlet
    {
        type    zeroGradient;       // ปล่อยให้พัฒนาตามธรรมชาติ
    }
    
    walls
    {
        type    noSlip;             // ความเร็ว = 0 ที่ผนัง
    }
    
    symmetryPlane
    {
        type    symmetry;
    }
}
```

---

## Inlet Conditions

### Velocity Inlet

```cpp
inlet
{
    type    fixedValue;
    value   uniform (10 0 0);   // กำหนดความเร็วตรงๆ
}
```

### Pressure Inlet (สำหรับ compressible)

```cpp
inlet
{
    type    totalPressure;
    p0      uniform 101325;     // Total pressure [Pa]
}
```

### Turbulence ที่ Inlet

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
    value   uniform 14.855;     // epsilon = Cmu^0.75 * k^1.5 / l
}
```

---

## Outlet Conditions

### Zero Gradient (ใช้บ่อยที่สุด)

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

### จัดการ Backflow

```cpp
outlet
{
    type        inletOutlet;
    inletValue  uniform (0 0 0);    // ถ้าไหลกลับ ใช้ค่านี้
    value       uniform (0 0 0);
}
```

---

## Wall Conditions

### No-Slip Wall (Velocity)

```cpp
walls
{
    type    noSlip;             // u = 0
    // หรือ
    type    fixedValue;
    value   uniform (0 0 0);
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

### Wall Functions (Turbulence)

```cpp
// 0/nut
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
    Ta      uniform 300;        // K ambient
}
```

---

## Special Boundary Conditions

### Symmetry

```cpp
symmetryPlane
{
    type    symmetry;
    // ไม่ต้องระบุพารามิเตอร์เพิ่ม
}
```

### Periodic/Cyclic

```cpp
periodic1
{
    type    cyclic;
    // คู่กับ periodic2 ที่ถูกกำหนดใน constant/polyMesh/boundary
}
```

### Time-Varying

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

## กฎการจับคู่ BC

### Pressure-Velocity Coupling

| ตำแหน่ง | Velocity | Pressure | เหตุผล |
|---------|----------|----------|--------|
| Inlet | `fixedValue` | `zeroGradient` | กำหนด U, ปล่อย p |
| Outlet | `zeroGradient` | `fixedValue` | ปล่อย U, กำหนด p |
| Wall | `noSlip` | `zeroGradient` | U=0, ไม่มี flux ผ่านผนัง |

> ⚠️ **ข้อควรระวัง:** ห้ามกำหนดทั้ง U และ p เป็น `fixedValue` ที่ขอบเขตเดียวกัน → จะทำให้ solver ไม่เสถียร

---

## Wall Function Requirements

| $y^+$ Range | Wall Treatment | BC ที่ใช้ |
|-------------|----------------|-----------|
| $y^+ < 5$ | Wall-resolved | `fixedValue` |
| $30 < y^+ < 300$ | Wall function | `nutkWallFunction` |

ตรวจสอบ y+ หลังจากรัน:
```bash
postProcess -func yPlus
```

---

## ตารางสรุป BC ที่ใช้บ่อย

| Field | Inlet | Outlet | Wall | Symmetry |
|-------|-------|--------|------|----------|
| `U` | `fixedValue` | `zeroGradient` | `noSlip` | `symmetry` |
| `p` | `zeroGradient` | `fixedValue` | `zeroGradient` | `symmetry` |
| `T` | `fixedValue` | `zeroGradient` | `fixedValue`/`zeroGradient` | `symmetry` |
| `k` | `fixedValue` | `zeroGradient` | `kqRWallFunction` | `symmetry` |
| `epsilon` | `fixedValue` | `zeroGradient` | `epsilonWallFunction` | `symmetry` |
| `nut` | `calculated` | `calculated` | `nutkWallFunction` | `symmetry` |

---

## Concept Check

<details>
<summary><b>1. ทำไมต้องใช้ zeroGradient สำหรับ velocity ที่ outlet?</b></summary>

เพราะเราไม่รู้ล่วงหน้าว่าความเร็วที่ outlet จะเป็นเท่าไหร่ ควรปล่อยให้มันพัฒนาตามธรรมชาติจากการแก้สมการ (Neumann condition: ∂u/∂n = 0)
</details>

<details>
<summary><b>2. เมื่อไหร่ควรใช้ inletOutlet แทน zeroGradient?</b></summary>

เมื่อมีโอกาสเกิด backflow ที่ outlet (เช่น การไหลหลัง obstacle ที่มี recirculation) `inletOutlet` จะกำหนดค่าถ้ามีการไหลกลับ ป้องกัน numerical instability
</details>

<details>
<summary><b>3. noSlip BC มีความหมายทางกายภาพอย่างไร?</b></summary>

หมายความว่าของไหลติดกับผนัง (no relative motion) ความเร็วของของไหลที่ติดผนัง = ความเร็วของผนัง (ปกติ = 0 สำหรับผนังนิ่ง) นี่คือผลจากความหนืดของของไหลจริง
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [05_OpenFOAM_Implementation.md](05_OpenFOAM_Implementation.md) — การนำไปใช้ใน OpenFOAM
- **บทถัดไป:** [07_Initial_Conditions.md](07_Initial_Conditions.md) — เงื่อนไขเริ่มต้น
- **ดูเพิ่มเติม:** [04_Dimensionless_Numbers.md](04_Dimensionless_Numbers.md) — y+ และการออกแบบ mesh