# Dimensioned Types - Pitfalls and Solutions

ปัญหาที่พบบ่อยและวิธีแก้ไข

---

## 1. Dimension Mismatch Error

### Problem

```
--> FOAM FATAL ERROR:
Inconsistent dimensions for +/-
   Left: [1 -1 -2 0 0 0 0]
   Right: [0 1 -1 0 0 0 0]
```

### Solution

ตรวจสอบว่า operands มี dimension เดียวกัน:

```cpp
// BAD
volScalarField result = p + U;  // pressure + velocity

// GOOD
volScalarField result = p;  // หรือใช้ที่ถูกต้องตาม physics
```

---

## 2. Wrong Dimension Specification

### Problem

```cpp
// Specifying wrong dimensions
dimensionedScalar nu("nu", dimDynamicViscosity, 1e-6);
// ERROR: 1e-6 is kinematic viscosity (m²/s), not dynamic (Pa·s)
```

### Solution

```cpp
// Correct
dimensionedScalar nu("nu", dimKinematicViscosity, 1e-6);
// or
dimensionedScalar mu("mu", dimDynamicViscosity, 1e-3);
```

---

## 3. Forgetting Dimensions in Fields

### Problem

```cpp
volScalarField T
(
    IOobject(...),
    mesh,
    scalar(300)  // Missing dimensions!
);
```

### Solution

```cpp
volScalarField T
(
    IOobject(...),
    mesh,
    dimensionedScalar("T", dimTemperature, 300)
);
```

---

## 4. Division by Dimensioned Scalar

### Problem

```cpp
dimensionedScalar dt("dt", dimTime, 0.001);
volScalarField result = T / dt.value();  // Loses dimension info!
```

### Solution

```cpp
volScalarField result = T / dt;  // Keep dimensioned
```

---

## 5. Incorrect Power Operations

### Problem

```cpp
// sqrt of negative dimension is problematic
dimensionedScalar a("a", dimPressure, 100);
dimensionedScalar b = sqrt(a);  // sqrt of [M L^-1 T^-2]?
```

### Solution

```cpp
// Ensure dimension makes sense for sqrt
dimensionedScalar U2("U2", dimVelocity*dimVelocity, 100);
dimensionedScalar U = sqrt(U2);  // √[L² T^-2] = [L T^-1] ✓
```

---

## 6. Disabling Dimension Check

### Problem

```cpp
// Tempting but dangerous
dimensionSet::checking(false);
// Now errors won't be caught!
```

### Solution

**Never disable** in production. Use only for:
- Debugging legacy code
- Temporary testing
- Always re-enable immediately

---

## 7. Dictionary Reading Errors

### Problem

```cpp
// In dictionary: nu [0 2 -1 0 0 0 0] 1e-6;
dimensionedScalar nu("nu", dimDynamicViscosity, dict);
// Mismatch between dict dimensions and specified!
```

### Solution

```cpp
// Either match dimensions
dimensionedScalar nu("nu", dimKinematicViscosity, dict);

// Or let dictionary define dimensions
dimensionedScalar nu(dict.lookup("nu"));
```

---

## 8. Comparison Operations

### Problem

```cpp
dimensionedScalar a("a", dimLength, 1.0);
dimensionedScalar b("b", dimTime, 1.0);

if (a.value() == b.value())  // Compares values, ignores dimensions!
```

### Solution

```cpp
// Check dimensions first
if (a.dimensions() != b.dimensions())
{
    FatalError << "Cannot compare different dimensions";
}
```

---

## Quick Troubleshooting

| Error | Check |
|-------|-------|
| Dimension mismatch | Verify equation physics |
| Wrong value | Check units (SI) |
| Field creation | Include dimensioned initial value |
| sqrt/pow errors | Verify result dimension makes sense |

---

## Concept Check

<details>
<summary><b>1. ทำไม dimension error เกิดขึ้น?</b></summary>

เพราะ **physics ผิด** — กำลังทำ operation ที่ไม่ make sense ทางฟิสิกส์
</details>

<details>
<summary><b>2. ควร disable dimension checking ไหม?</b></summary>

**ไม่ควร** — จะเสีย safety net ทั้งหมด
</details>

<details>
<summary><b>3. อ่าน dimensioned value จาก dict อย่างไรให้ถูก?</b></summary>

ให้ dict define dimensions: `dimensionedScalar nu(dict.lookup("nu"))`
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Engineering Benefits:** [06_Engineering_Benefits.md](06_Engineering_Benefits.md)