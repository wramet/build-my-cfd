# Foundation Primitives - Exercises

แบบฝึกหัดสำหรับ OpenFOAM Primitives — ลงมือทำเพื่อเข้าใจจริง

> **ทำไมต้องทำ Exercises?**
> - อ่านอย่างเดียวไม่พอ — **ต้องเขียน code เอง**
> - ผิดพลาดตอนทำแบบฝึกหัด ดีกว่าผิดตอน production
> - Compile และ run จริง → เข้าใจ error messages

---

## Exercise 1: Basic Types

### Task

สร้างโปรแกรมที่ใช้ OpenFOAM primitives

```cpp
#include "fvCFD.H"

int main(int argc, char *argv[])
{
    // 1. Create scalars
    scalar a = 5.0;
    scalar b = 3.0;

    // 2. Create vectors
    vector v1(1, 2, 3);
    vector v2(4, 5, 6);

    // 3. Operations
    scalar dot = v1 & v2;      // Dot product
    vector cross = v1 ^ v2;    // Cross product
    scalar mag_v1 = mag(v1);   // Magnitude

    Info << "Dot: " << dot << endl;
    Info << "Cross: " << cross << endl;
    Info << "Mag: " << mag_v1 << endl;

    return 0;
}
```

### Expected Output

```
Dot: 32
Cross: (-3 6 -3)
Mag: 3.74166
```

---

## Exercise 2: Dimensioned Types

### Task

สร้าง dimensioned scalars และตรวจสอบ dimension checking

```cpp
#include "fvCFD.H"

int main(int argc, char *argv[])
{
    // Dimensioned scalars
    dimensionedScalar rho("rho", dimDensity, 1000);
    dimensionedScalar U("U", dimVelocity, 10);
    dimensionedScalar L("L", dimLength, 0.1);
    dimensionedScalar mu("mu", dimDynamicViscosity, 0.001);

    // Calculate Reynolds number
    dimensionedScalar Re = rho * U * L / mu;

    Info << "Re = " << Re << endl;
    Info << "Is dimensionless? " << Re.dimensions().dimensionless() << endl;

    return 0;
}
```

### Expected Output

```
Re = Re [0 0 0 0 0 0 0] 1e+06
Is dimensionless? 1
```

---

## Exercise 3: Tensor Operations

### Task

สร้าง tensor และทำ operations

```cpp
#include "fvCFD.H"

int main(int argc, char *argv[])
{
    // Create symmetric tensor (stress)
    symmTensor sigma
    (
        100, 20, 10,    // xx, xy, xz
             80, 5,     // yy, yz
                 60     // zz
    );

    // Operations
    scalar trace = tr(sigma);           // Trace
    scalar det = Foam::det(sigma);      // Determinant
    symmTensor dev_sigma = dev(sigma);  // Deviatoric part

    Info << "Trace: " << trace << endl;
    Info << "Det: " << det << endl;
    Info << "Deviatoric: " << dev_sigma << endl;

    return 0;
}
```

---

## Exercise 4: Lists and Fields

### Task

สร้าง Field และทำ operations

```cpp
#include "fvCFD.H"

int main(int argc, char *argv[])
{
    // Create scalar field
    scalarField p(10, 1.0);  // 10 elements, value 1.0

    // Modify
    forAll(p, i)
    {
        p[i] = sqr(i);  // p[i] = i^2
    }

    // Statistics
    Info << "Sum: " << sum(p) << endl;
    Info << "Max: " << max(p) << endl;
    Info << "Average: " << average(p) << endl;

    return 0;
}
```

---

## Exercise 5: Compile Custom Application

### Make/files

```
exercise.C

EXE = $(FOAM_USER_APPBIN)/exercise
```

### Make/options

```
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude

EXE_LIBS = \
    -lfiniteVolume
```

### Compile

```bash
wmake
```

---

## Solutions Summary

| Exercise | Key Concepts |
|----------|--------------|
| 1 | scalar, vector, operations |
| 2 | dimensionedScalar, dimension checking |
| 3 | tensor, symmTensor, invariants |
| 4 | Field, forAll, statistics |
| 5 | wmake, Make/files, Make/options |

---

## 🧠 Concept Check

<details>
<summary><b>1. & และ ^ ต่างกันอย่างไร?</b></summary>

- **&**: Dot product (inner) → returns scalar
- **^**: Cross product (outer) → returns vector
</details>

<details>
<summary><b>2. ทำไม dimensionedScalar ดีกว่า scalar?</b></summary>

เพราะ **tracks units** → ป้องกัน errors จาก dimension mismatch
</details>

<details>
<summary><b>3. forAll macro ทำอะไร?</b></summary>

**Loop over all elements**: `forAll(field, i)` = `for(label i=0; i<field.size(); i++)`
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Basic Primitives:** [02_Basic_Primitives.md](02_Basic_Primitives.md)
- **Containers:** [05_Containers.md](05_Containers.md)