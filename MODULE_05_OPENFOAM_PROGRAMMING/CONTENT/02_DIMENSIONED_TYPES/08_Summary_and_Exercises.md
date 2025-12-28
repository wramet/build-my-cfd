# Dimensioned Types - Summary and Exercises

สรุปและแบบฝึกหัด

---

## Summary

### Core Concepts

| Concept | Description |
|---------|-------------|
| `dimensionSet` | 7 SI exponents |
| `dimensionedScalar` | Scalar + dimensions |
| `dimensionedVector` | Vector + dimensions |
| Checking | Compile + runtime |

### Common Dimensions

| Alias | Value |
|-------|-------|
| `dimless` | `[0 0 0 0 0 0 0]` |
| `dimLength` | `[0 1 0 0 0 0 0]` |
| `dimVelocity` | `[0 1 -1 0 0 0 0]` |
| `dimPressure` | `[1 -1 -2 0 0 0 0]` |
| `dimDensity` | `[1 -3 0 0 0 0 0]` |

---

## Exercise 1: Create Dimensioned Values

```cpp
// Create common physical quantities
dimensionedScalar rho("rho", dimDensity, 1000);
dimensionedScalar nu("nu", dimKinematicViscosity, 1e-6);
dimensionedScalar mu("mu", dimDynamicViscosity, 1e-3);
dimensionedVector g("g", dimAcceleration, vector(0, 0, -9.81));
```

---

## Exercise 2: Dimension Checking

```cpp
// Which are valid?
dimensionedScalar a("a", dimPressure, 100);
dimensionedScalar b("b", dimDensity, 1000);
dimensionedScalar c("c", dimVelocity, 10);

dimensionedScalar d = a / b;   // Valid: [L² T^-2]
dimensionedScalar e = a * b;   // Valid: [M² L^-4 T^-2]
// dimensionedScalar f = a + c;  // Error: dimension mismatch
```

---

## Exercise 3: Reynolds Number

```cpp
// Calculate Reynolds number
dimensionedScalar rho("rho", dimDensity, 1000);
dimensionedScalar U("U", dimVelocity, 1.0);
dimensionedScalar L("L", dimLength, 0.1);
dimensionedScalar mu("mu", dimDynamicViscosity, 1e-3);

dimensionedScalar Re = rho * U * L / mu;

// Verify dimensionless
Info << "Re = " << Re << endl;
Info << "Dimensionless? " << Re.dimensions().dimensionless() << endl;
```

---

## Exercise 4: Field with Dimensions

```cpp
volScalarField T
(
    IOobject("T", runTime.timeName(), mesh, IOobject::NO_READ),
    mesh,
    dimensionedScalar("T", dimTemperature, 300)
);

volScalarField p
(
    IOobject("p", runTime.timeName(), mesh, IOobject::NO_READ),
    mesh,
    dimensionedScalar("p", dimPressure, 0)
);
```

---

## Exercise 5: Read from Dictionary

```cpp
// In transportProperties:
// nu nu [0 2 -1 0 0 0 0] 1e-6;

IOdictionary transportProperties(...);
dimensionedScalar nu(transportProperties.lookup("nu"));

Info << "nu = " << nu << endl;
Info << "dimensions = " << nu.dimensions() << endl;
```

---

## Solutions

### Exercise 2

- `a / b`: `[1 -1 -2] - [1 -3 0] = [0 2 -2]` ✓
- `a * b`: `[1 -1 -2] + [1 -3 0] = [2 -4 -2]` ✓
- `a + c`: Error — pressure ≠ velocity

### Exercise 3

Re = `[M L^-3][L T^-1][L][M^-1 L T] = [1]` = dimless ✓

---

## Quick Reference

| Method | Returns |
|--------|---------|
| `.name()` | word |
| `.value()` | scalar/vector |
| `.dimensions()` | dimensionSet |
| `.dimensionless()` | bool |

---

## Concept Check

<details>
<summary><b>1. ทำไม Re ต้องเป็น dimless?</b></summary>

เพราะ Re เป็น **ratio of forces** → dimensions หักล้างกัน
</details>

<details>
<summary><b>2. อ่าน dimensioned value จาก dict อย่างไร?</b></summary>

```cpp
dimensionedScalar nu(dict.lookup("nu"));
```
</details>

<details>
<summary><b>3. สร้าง field พร้อม dimension อย่างไร?</b></summary>

ใช้ `dimensionedScalar("name", dims, value)` ใน constructor
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Pitfalls:** [05_Pitfalls_and_Solutions.md](05_Pitfalls_and_Solutions.md)