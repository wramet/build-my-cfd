# Troubleshooting Boundary Conditions

การวินิจฉัยและแก้ปัญหาที่เกิดจาก BC

---

## ปัญหาที่พบบ่อย

### 1. Divergence ที่ Inlet

**อาการ:**
```
FOAM FATAL ERROR:
Maximum number of iterations exceeded.
```

**สาเหตุและวิธีแก้:**

| สาเหตุ | วิธีแก้ |
|--------|---------|
| U และ p เป็น Dirichlet ทั้งคู่ | เปลี่ยน p เป็น `zeroGradient` |
| Velocity สูงเกินไป | ลด inlet velocity |
| Turbulence initial ไม่ดี | ปรับ k, ε ให้สอดคล้อง |

```cpp
// ❌ ผิด
inlet { type fixedValue; value uniform (10 0 0); }  // U
inlet { type fixedValue; value uniform 0; }         // p

// ✅ ถูก
inlet { type fixedValue; value uniform (10 0 0); }  // U
inlet { type zeroGradient; }                        // p
```

### 2. Backflow ที่ Outlet

**อาการ:**
- Negative velocity ที่ outlet
- Solution unstable

**สาเหตุและวิธีแก้:**

```cpp
// ❌ อาจมีปัญหา
outlet { type zeroGradient; }

// ✅ ดีกว่า
outlet
{
    type        inletOutlet;
    inletValue  uniform (0 0 0);
    value       uniform (10 0 0);
}
```

หรือขยาย outlet domain ให้ไกลจากบริเวณ recirculation

### 3. High Velocity ที่ Wall

**อาการ:**
- Velocity ไม่เป็น 0 ที่ผนัง
- Unrealistic results

**สาเหตุและวิธีแก้:**

```cpp
// ❌ ผิด
wall { type zeroGradient; }

// ✅ ถูก
wall { type noSlip; }
// หรือ
wall { type fixedValue; value uniform (0 0 0); }
```

### 4. Pressure Drifting

**อาการ:**
- Pressure เพิ่มขึ้นหรือลดลงเรื่อยๆ
- ไม่ converge

**สาเหตุ:** ไม่มี reference pressure

**วิธีแก้:**

```cpp
// Option 1: fixedValue ที่ outlet
outlet { type fixedValue; value uniform 0; }

// Option 2: pRef ใน fvSolution
SIMPLE
{
    pRefCell    0;
    pRefValue   0;
}
```

### 5. Turbulence Instability

**อาการ:**
- k หรือ ε กลายเป็นลบ
- NaN ใน turbulence fields

**วิธีแก้:**

```cpp
// ใช้ bounded schemes
divSchemes
{
    div(phi,k)      Gauss upwind;       // ไม่ใช่ linear
    div(phi,epsilon) Gauss upwind;
}

// ใช้ relaxation
relaxationFactors
{
    equations
    {
        k       0.5;
        epsilon 0.5;
    }
}
```

### 6. y+ ไม่อยู่ในช่วง

**อาการ:**
- Wall shear stress ผิด
- Velocity profile ใกล้ผนังไม่สมเหตุสมผล

**วินิจฉัย:**
```bash
postProcess -func yPlus
```

**วิธีแก้:**

| y+ | Wall Function |
|----|---------------|
| < 5 | Low-Re model หรือ `nutLowReWallFunction` |
| 5-30 | ❌ Buffer layer — หลีกเลี่ยง! |
| 30-300 | Standard wall functions |
| > 300 | Mesh หยาบเกินไป — refine |

---

## Diagnostic Commands

### ตรวจสอบ BC Types

```bash
foamListBoundaryPatches
```

### ตรวจสอบ Patch Names

```bash
grep -A 5 boundaryField 0/U
```

### Mesh Quality

```bash
checkMesh
```

### Residuals

```bash
foamLog log.simpleFoam
gnuplot residuals.gp
```

### Field Range

```bash
postProcess -func "fieldMinMax(U)"
```

---

## Common Mistakes

### 1. Patch Name ไม่ตรงกับ polyMesh

```cpp
// ❌ constant/polyMesh/boundary มี "inlet" แต่
// 0/U ใช้ "Inlet" (ตัวใหญ่ต่างกัน)
boundaryField
{
    Inlet { ... }   // ❌ ไม่ตรง
    inlet { ... }   // ✅ ตรง
}
```

### 2. ลืม BC สำหรับบาง Patch

```cpp
// ❌ ไม่มี BC สำหรับ "sides"
boundaryField
{
    inlet  { ... }
    outlet { ... }
    // sides หายไป → FATAL ERROR
}
```

### 3. Units ผิด

```cpp
// ❌ Dimensions ผิด
dimensions [0 1 -1 0 0 0 0];   // velocity
value uniform 10;              // ≠ vector!

// ✅ ถูก
dimensions [0 1 -1 0 0 0 0];
value uniform (10 0 0);        // vector
```

### 4. Value ไม่ consistent กับ Type

```cpp
// ❌ zeroGradient ไม่ต้องการ value
outlet
{
    type  zeroGradient;
    value uniform 0;    // ไม่จำเป็น (แต่ไม่ error)
}

// ✅ fixedValue ต้องการ value
outlet
{
    type  fixedValue;
    value uniform 0;    // จำเป็น!
}
```

---

## Debugging Checklist

1. ✅ Patch names ตรงกับ `constant/polyMesh/boundary`
2. ✅ ทุก patch มี BC ครบ
3. ✅ U และ p coupling ถูกต้อง
4. ✅ มี reference pressure อย่างน้อย 1 จุด
5. ✅ Dimensions ถูกต้อง
6. ✅ Value format ถูก (scalar vs vector)
7. ✅ y+ อยู่ในช่วงที่เหมาะกับ wall function
8. ✅ Turbulence BC consistent กับ model

---

## Concept Check

<details>
<summary><b>1. ทำไม buffer layer (5 < y+ < 30) ควรหลีกเลี่ยง?</b></summary>

เพราะไม่มี wall function ที่ถูกต้องสำหรับ region นี้ — viscous sublayer model และ log-law model ต่างก็ให้ความผิดพลาดสูง
</details>

<details>
<summary><b>2. Over-specification คืออะไร?</b></summary>

การกำหนด BC มากเกินไปที่ boundary เดียว เช่น fixedValue ทั้ง U และ p → solver ไม่สามารถหา consistent solution
</details>

<details>
<summary><b>3. Under-specification คืออะไร?</b></summary>

การกำหนด BC ไม่พอ เช่น zeroGradient ทุกที่ไม่มี reference pressure → pressure ลอย (floating)
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [06_Advanced_Boundary_Conditions.md](06_Advanced_Boundary_Conditions.md) — BC ขั้นสูง
- **บทถัดไป:** [08_Exercises.md](08_Exercises.md) — แบบฝึกหัด