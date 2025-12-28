# Common Pitfalls and Debugging

ข้อผิดพลาดที่พบบ่อยในการเขียนโค้ด OpenFOAM และวิธีแก้ไข

> [!TIP] ทำไมต้องเข้าใจ Common Pitfalls?
> **ความสำคัญ:** ข้อผิดพลาดเหล่านี้ทำให้เกิดปัญหาตั้งแต่ **Compilation error** (โค้ดไม่ผ่าน) ไปจนถึง **Numerical instability** (การคำนวณแตก) การเข้าใจ root cause จะช่วยให้ debug เร็วขึ้น 10 เท่า และเขียนโค้ดที่ **robust** และ **efficient**
> **ผลกระทบ:**
> - ✅ **Stability:** ป้องกัน simulation ดับกลางคัน (divergence)
> - ✅ **Correctness:** มั่นใจว่าผลลัพธ์ถูกต้องตามฟิสิกส์
> - ✅ **Performance:** หลีกเลี่ยง memory leak และ unnecessary copies
> - ✅ **Maintainability:** โค้ดอ่านง่าย แก้ไขได้ง่าย

---

## 1. Dimensional Inconsistency

> [!NOTE] **📂 OpenFOAM Context - Domain E (Coding)**
> **บริบท:** Section นี้เกี่ยวกับ **Dimensioned Type System** ในการเขียนโค้ด OpenFOAM ซึ่งเป็น **Compile-time Safety Mechanism**
> - **Files:** โค้ดของคุณเอง (custom solver, boundary condition, function object) ใน `src/` หรือ `solver/`
> - **Keywords:** `dimensionSet`, `dimLength`, `dimTime`, `dimensionedScalar`, `volScalarField`
> - **Error Messages:** `"Cannot add [1,-1,-2,0,0,0,0] + [0,1,-1,0,0,0,0]"` หมายถึง **Dimension mismatch** ระหว่าง pressure และ velocity
> - **ตำแหน่ง:** เกิดขึ้นตอน **compile-time** (เวลา `wmake`) ไม่ใช่ runtime

### ปัญหา

```cpp
// ❌ การบวก field ต่างหน่วย
volScalarField p;  // [1,-1,-2,0,0,0] Pa
volVectorField U;  // [0,1,-1,0,0,0]  m/s

auto result = p + U;  // Compiler error!
// "Cannot add [1,-1,-2] + [0,1,-1]"
```

### วิธีแก้

```cpp
// ✅ ใช้สูตรที่ถูกต้องทางฟิสิกส์
volScalarField dynamicP = 0.5 * rho * magSqr(U);  // [1,-1,-2]
volScalarField totalP = p + dynamicP;  // OK!
```

### Dimension Reference

| Field | Dimension | SI Unit |
|-------|-----------|---------|
| Pressure | `[1,-1,-2,0,0,0]` | Pa |
| Velocity | `[0,1,-1,0,0,0]` | m/s |
| Density | `[1,-3,0,0,0,0]` | kg/m³ |
| Temperature | `[0,0,0,1,0,0]` | K |
| Viscosity (ν) | `[0,2,-1,0,0,0]` | m²/s |

---

## 2. Neglecting Boundary Conditions

> [!NOTE] **📂 OpenFOAM Context - Domain A (Physics & Fields) + Domain E (Coding)**
> **บริบท:** Section นี้เกี่ยวกับ **Field-Boundary Synchronization** ซึ่งเป็นความสัมพันธ์ระหว่าง **Internal Field** และ **Boundary Field**
> - **Files:**
>   - `0/p`, `0/U`, `0/T` — Boundary condition definitions
>   - โค้ดของคุณใน `src/` หรือ custom solver
> - **Keywords:** `correctBoundaryConditions()`, `fixedValue`, `zeroGradient`, `patch`, `internalField`
> - **สถานการณ์:** เกิดขึ้นเมื่อคุณ **modify field** ด้วยโค้ด (เช่น `U = newVelocity;`) แล้วใช้ค่านั้นคำนวณต่อโดยไม่ sync BC
> - **ผลกระทบ:** Flux (`phi`) จะถูกคำนวณด้วย BC เก่า → Mass conservation error → Simulation diverge

### ปัญหา

```cpp
// ❌ ลืม update boundary หลังแก้ไข field
U = someNewVelocity;
phi = linearInterpolate(U) & mesh.Sf();  // ใช้ BC เก่า!
```

### วิธีแก้

```cpp
// ✅ เรียก correctBoundaryConditions() เสมอ
U = someNewVelocity;
U.correctBoundaryConditions();  // 🔑 สำคัญ!
phi = linearInterpolate(U) & mesh.Sf();
```

### Solver Pattern

```cpp
while (residual > tolerance)
{
    UEqn.solve();
    U.correctBoundaryConditions();  // หลัง solve()
    phi = linearInterpolate(U) & mesh.Sf();
}
```

---

## 3. Memory Management Confusion

> [!NOTE] **📂 OpenFOAM Context - Domain E (Coding)**
> **บริบท:** Section นี้เกี่ยวกับ **Reference Counting & Memory Ownership** ใน OpenFOAM ซึ่งใช้ **Smart Pointers** หลีกเลี่ยง manual memory management
> - **Files:** โค้ดของคุณใน `src/finiteVolume/`, `src/transportModels/`, หรือ custom solver
> - **Keywords:**
>   - `tmp<T>` — Temporary field (auto cleanup, reference counted)
>   - `autoPtr<T>` — Single ownership (move semantics)
>   - `refPtr<T>` — Reference counted pointer
>   - `clone()` — Deep copy method
> - **สถานการณ์:** เกิดขึ้นเมื่อ assign field (`p2 = p1`) และ modify ตัวใดตัวหนึ่ง → ตัวอื่นเปลี่ยนตาม (shallow copy)
> - **ผลกระทบ:** การคำนวณผิดพลาดเพราะ field ที่ควรเป็นอิสระแชร์ memory กัน → ผลลัพธ์ unpredictable
> - **การ debug:** ใช้ `gdb` หรือ `info()` เพื่อตรวจ address: `&p2[0]` vs `&p1[0]`

### ปัญหา

```cpp
// ❌ Shallow copy = shared data
volScalarField p1 = ...;
volScalarField p2 = p1;  // p2 ชี้ไป memory เดียวกับ p1!

p2[0] = 1000;  // p1[0] ก็เปลี่ยนด้วย!
```

### วิธีแก้

```cpp
// ✅ Deep copy methods
volScalarField p2 = p1.clone();           // Method 1: clone()
volScalarField p3(p1, true);              // Method 2: constructor
volScalarField p4(IOobject(...), p1);     // Method 3: new IOobject
```

### Smart Pointers

| Type | Use Case |
|------|----------|
| `tmp<T>` | Temporary fields (auto cleanup) |
| `autoPtr<T>` | Single ownership |
| `refPtr<T>` | Reference counting |

```cpp
// ใช้ tmp สำหรับ temporary
tmp<volScalarField> tGradP = fvc::grad(p);
gradP = tGradP();  // Detach
```

---

## 4. Time Management Errors

> [!NOTE] **📂 OpenFOAM Context - Domain C (Simulation Control) + Domain E (Coding)**
> **บริบท:** Section นี้เกี่ยวกับ **Temporal Field Management** ซึ่งเป็นการจัดการ **Time History** สำหรับ implicit time-stepping schemes
> - **Files:**
>   - `system/controlDict` — Time stepping control (`deltaT`, `writeInterval`)
>   - โค้ดของคุณใน custom solver
> - **Keywords:**
>   - `storeOldTime()` — เก็บค่าปัจจุบันเป็น `oldTime()`
>   - `oldTime()` — Access ค่า time step ก่อนหน้า
>   - `runTime.deltaT()` — ดึงค่า time step ปัจจุบัน
>   - `runTime.value()` — Current simulation time
> - **สถานการณ์:** เกิดขึ้นเมื่อใช้ transient term (เช่น `ddt(T)`) แต่ลืม store oldTime → ค่า `T.oldTime()` ผิดหรือ uninitialized
> - **ผลกระทบ:** Time derivative (`dT/dt`) ผิด → การคำนวณ unstable → ผลลัพธ์ non-physical
> - **Time Schemes:** ใช้กับ `Euler`, `backward`, `CrankNicolson` ใน `ddtSchemes` (system/fvSchemes)

### ปัญหา

```cpp
// ❌ ลืม store old time ก่อนแก้ไข
T = newTemperature;
T.storeOldTime();  // ผิด! ค่าเก่าหายไปแล้ว

auto dTdt = (T - T.oldTime()) / dt;  // ผิด!
```

### วิธีแก้

```cpp
// ✅ Store ก่อน modify
T.storeOldTime();     // เก็บค่าเก่าก่อน
T = newTemperature;   // แก้ไข
auto dTdt = (T - T.oldTime()) / runTime.deltaT();  // ถูกต้อง
```

### Time Loop Pattern

```cpp
while (!runTime.end())
{
    runTime++;
    
    // 1. Store old values FIRST
    U.storeOldTime();
    p.storeOldTime();
    T.storeOldTime();
    
    // 2. Solve
    solve(fvm::ddt(U) + fvm::div(phi,U) == -fvc::grad(p));
    solve(fvm::ddt(T) + fvm::div(phi,T) == fvm::laplacian(alpha,T));
    
    // 3. Update BCs
    U.correctBoundaryConditions();
    T.correctBoundaryConditions();
    
    // 4. Write
    runTime.write();
}
```

---

## 5. Template Errors

> [!NOTE] **📂 OpenFOAM Context - Domain E (Coding)**
> **บริบท:** Section นี้เกี่ยวกับ **Template Metaprogramming** ใน OpenFOAM ซึ่งใช้ Template สร้าง **Type-safe Code** ที่ flexible
> - **Files:** โค้ดของคุณใน `src/` (ทุก custom code)
> - **Keywords:**
>   - `GeometricField<scalar, fvPatchField, volMesh>` — Full template type
>   - `volScalarField` — Typedef ของ template ด้านบน
>   - `const_cast<T>()` — Cast away constness
>   - `tmp<volScalarField>` — Template instantiation กับ smart pointer
> - **สถานการณ์:** เกิดขึ้นเมื่อ compiler ไม่สามารถ **deduce template type** โดยอัตโนมัติ หรือ มี **template specialization** ไม่ตรงกัน
> - **Error Messages:** `"no matching function for call to 'volScalarField::...'"` หรือ `"candidate template ignored: deduced conflicting types"`
> - **การ debug:**
>   1. อ่าน error message อย่างละเอียด (compiler จะบอก expected type vs actual type)
>   2. ใช้ `typedef` เพื่อลดความซับซ้อนของ template syntax
>   3. Explicit template instantiation: `object.method<type>(args)`
> - **ผลกระทบ:** Compilation fail → ไม่สามารถสร้าง executable ได้

### ปัญหา

```
error: no matching function for call to 'volScalarField::...'
note: candidate template ignored...
```

### วิธีแก้

```cpp
// ✅ Explicit template types
volScalarField& pRef = const_cast<volScalarField&>(p);

// ✅ ใช้ typedef
typedef GeometricField<scalar, fvPatchField, volMesh> volScalarField;
```

---

## Debugging Checklist

> [!NOTE] **📂 OpenFOAM Context - Domain E (Coding) + Domain B (Numerics)**
> **บริบท:** Section นี้เป็น **Practical Debugging Workflow** ที่รวมทุก domain เข้าด้วยกัน
> - **Files:** โค้ดของคุณ + ไฟล์ case setup (`system/`, `0/`, `constant/`)
> - **Keywords:**
>   - Compilation: `dimensions`, `template types`, `#include headers`
>   - Runtime: `correctBoundaryConditions()`, `storeOldTime()`, field initialization
>   - Numerics: `checkMesh`, `residuals`, `min()`, `max()`
> - **Tools:**
>   - `wmake` → Compilation errors
>   - `gdb` → Runtime debugging
>   - `foamListTimes` → Check time directories
>   - `foamInfoExec` → Solver info
> - **Domain Mapping:**
>   - Compilation Errors → **Domain E** (Coding issues)
>   - Runtime Errors → **Domain A/E** (Field handling + Code)
>   - Numerical Issues → **Domain B** (Numerics + Mesh)

### Compilation Errors

- [ ] ตรวจ dimensions ว่าตรงกันไหม
- [ ] ตรวจ template types
- [ ] Include headers ครบไหม

### Runtime Errors

- [ ] เรียก `correctBoundaryConditions()` หลัง modify
- [ ] เรียก `storeOldTime()` ก่อน modify
- [ ] ตรวจ field initialization

### Numerical Issues

- [ ] Check mesh quality (`checkMesh`)
- [ ] Monitor residuals
- [ ] Check field bounds (`min(T)`, `max(p)`)

---

## Concept Check

<details>
<summary><b>1. ทำไมต้องเรียก correctBoundaryConditions()?</b></summary>

เพราะ OpenFOAM เก็บ internal field และ boundary field แยกกัน — เมื่อ modify internal field ค่า boundary ยังเป็นค่าเก่า ต้อง sync ก่อนคำนวณ flux
</details>

<details>
<summary><b>2. p2 = p1 เป็น shallow หรือ deep copy?</b></summary>

**Shallow copy** — p2 ชี้ไปที่ memory เดียวกับ p1 ใช้ `clone()` หรือ constructor ที่มี `true` สำหรับ deep copy
</details>

<details>
<summary><b>3. storeOldTime() ต้องเรียกเมื่อไหร่?</b></summary>

**ก่อน** modify field — เพื่อเก็บค่าปัจจุบันไว้เป็น oldTime() ก่อนที่จะถูกเขียนทับ
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [05_Mathematical_Type_Theory.md](05_Mathematical_Type_Theory.md)
- **บทถัดไป:** [07_Summary_and_Exercises.md](07_Summary_and_Exercises.md)