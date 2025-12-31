# Field Algebra - Introduction

บทนำ Field Algebra — ทำไม OpenFOAM ถึงสร้างระบบพีชคณิตให้ Fields?

---

## 🎯 Learning Objectives

หลังจากอ่านบทนี้ คุณจะสามารถ:

1. **อธิบาย** ทำไม OpenFOAM ต้องสร้าง field algebra system แทนการใช้ loops
2. **เข้าใจ** ประโยชน์ของ operator overloading สำหรับ CFD equations
3. **เชื่อมโยง** field algebra กับสมการ Navier-Stokes ในรูปแบบ OpenFOAM
4. **ประเมิน** ข้อดีด้าน readability และ performance ของ field operations

---

## What is Field Algebra?

> **💡 คิดแบบนี้:**
> Field Algebra = **เขียน math equations บน mesh เหมือนเขียนบนกระดาษ**
>
> แทนที่จะ loop ผ่านทุก cell แล้ว compute ทีละตัว
> เขียน `U = U + dt*gradP` แล้ว OpenFOAM จะทำให้ทุก cell อัตโนมัติ

### Traditional Approach vs OpenFOAM

**❌ Traditional C++ (loop-based):**
```cpp
// Update velocity field (millions of cells)
for (label i = 0; i < U.size(); i++)
{
    U[i] = U[i] + dt * gradP[i];
}
```

**✅ OpenFOAM Field Algebra:**
```cpp
// Same operation, cleaner syntax
U = U + dt*gradP;
```

**ความแตกต่าง:**
- **Readability**: OpenFOAM syntax ใกล้เคียงสมการคณิตศาสตร์
- **Safety**: Dimension checking ป้องกัน physics errors
- **Performance**: Optimized implementations, possible vectorization

---

## Why Field Algebra Matters for CFD

### 1. Mathematical Clarity

**Navier-Stokes Equation:**
$$\frac{\partial \mathbf{U}}{\partial t} + \nabla \cdot (\mathbf{U} \mathbf{U}) = -\frac{\nabla p}{\rho} + \nu \nabla^2 \mathbf{U}$$

**OpenFOAM Implementation:**
```cpp
fvVectorMatrix UEqn
(
    fvm::ddt(U)
  + fvm::div(phi, U)
  - fvm::laplacian(nu, U)
);

solve(UEqn == -fvc::grad(p));
```

**สังเกต**: OpenFOAM code อ่านคล้ายสมการคณิตศาสตร์

### 2. Operations Available

| Category | Operations | Example |
|----------|-----------|---------|
| **Arithmetic** | +, -, *, / | `T = T + 10.0` |
| **Statistical** | max, min, sum, average | `scalar maxT = max(T)` |
| **Calculus** | grad, div, laplacian, curl | `volVectorField gradP = fvc::grad(p)` |
| **Logical** | pos, neg, mag | `scalarField magU = mag(U)` |

### 3. Dimensional Safety

```cpp
volScalarField p(...);    // [Pa = kg/(m·s²)]
volVectorField U(...);    // [m/s]

// ❌ This will not compile - dimension mismatch
// volScalarField wrong = p + U;

// ✅ Correct - dimensions match
volScalarField pDynamic = 0.5 * rho * magSqr(U);  // [Pa]
```

---

## How Field Algebra Works

### Operator Overloading

OpenFOAM uses C++ operator overloading to make field operations look like regular math:

```cpp
// Behind the scenes of: scalarField C = A + B;

// 1. Operator+ is called on Field<scalar>
tmp<scalarField> operator+(const scalarField& A, const scalarField& B)
{
    tmp<scalarField> tResult(new scalarField(A.size()));
    scalarField& result = tResult.ref();
    
    forAll(result, i)
    {
        result[i] = A[i] + B[i];
    }
    
    return tResult;
}
```

### tmp Pattern for Efficiency

OpenFOAM uses `tmp<>` to avoid unnecessary copies:

```cpp
// Expression: T = A + B + C;

// Without tmp: 2 temporary arrays created, 2 copies
// With tmp: 1 temporary, move semantics

tmp<scalarField> result = A + B;  // tmp holds result
result.ref() += C;                // Modify in place
T = result;                       // Move, not copy
```

---

## Prerequisites

ก่อนเริ่มบทนี้ ควรเข้าใจ:

| หัวข้อ | ที่มา |
|--------|-------|
| Basic Primitives (scalar, vector, tensor) | 01_FOUNDATION_PRIMITIVES |
| Dimensioned Types | 02_DIMENSIONED_TYPES |
| Field Types (volScalarField, etc.) | 08_FIELD_TYPES |

---

## What's Next

| บท | เนื้อหา |
|----|--------|
| 02_Operator_Overloading.md | รายละเอียด operators ทั้งหมด |
| 03_Dimensional_Checking.md | ระบบตรวจสอบหน่วย |
| 04_Expression_Templates.md | Performance optimization ด้วย tmp |

---

## 🧠 Concept Check

<details>
<summary><b>1. ทำไม OpenFOAM ถึงใช้ operator overloading แทน functions?</b></summary>

**Readability**: ต้องสามารถเขียน code ที่ใกล้เคียงสมการคณิตศาสตร์
- `U = U + dt*gradP` อ่านง่ายกว่า `add(U, multiply(dt, gradP))`
- ลด bugs จากการอ่านผิด
</details>

<details>
<summary><b>2. Dimension checking ป้องกัน errors อะไรได้?</b></summary>

**Physics errors** ที่ compile ผ่านแต่ผลลัพธ์ผิด:
- บวก pressure กับ velocity
- หาร density ด้วย temperature
- คูณหน่วยที่ไม่ควบคู่กัน
</details>

<details>
<summary><b>3. tmp<> pattern ช่วย performance อย่างไร?</b></summary>

**ลด memory copies**:
- Temporary results ไม่ต้อง copy ระหว่าง expressions
- Move semantics แทน copy
- Reference counting สำหรับ shared data
</details>

---

## 📖 Related Documentation

**ภายใน Module นี้:**
- [00_Overview.md](00_Overview.md) — Technical reference สำหรับ field operations
- [02_Operator_Overloading.md](02_Operator_Overloading.md) — รายละเอียด operators

**Cross-Module:**
- `08_FIELD_TYPES` — ประเภทของ fields ใน OpenFOAM
- `10_VECTOR_CALCULUS` — fvc และ fvm operations