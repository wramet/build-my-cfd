# Field Algebra - Common Pitfalls

ปัญหาที่พบบ่อยใน Field Algebra

---

## 1. Dimension Mismatch

### Problem

```
--> FOAM FATAL ERROR:
Inconsistent dimensions for +
```

### Solution

```cpp
// Check dimensions match before operations
// p + U is invalid (pressure + velocity)

// Correct:
volScalarField result = p + rho * magSqr(U);  // Both are [M L^-1 T^-2]
```

---

## 2. Division by Zero

### Problem

```cpp
volScalarField ratio = a / b;  // b may have zeros
```

### Solution

```cpp
// Add small value
volScalarField ratio = a / (b + SMALL);

// Or use stabilize
volScalarField ratio = a / stabilise(b, SMALL);
```

---

## 3. Temporary Lifetime

### Problem

```cpp
// Dangling reference
const volScalarField& bad = fvc::grad(p).component(0);
// tmp destroyed, reference invalid!
```

### Solution

```cpp
// Keep tmp alive
tmp<volVectorField> gradP = fvc::grad(p);
volScalarField gradPx = gradP().component(0);
```

---

## 4. Wrong fvm vs fvc

### Problem

```cpp
// Using fvm when fvc needed
volScalarField gradP = fvm::grad(p);  // Error: fvm doesn't have grad
```

### Solution

```cpp
// fvc for explicit calculations
volVectorField gradP = fvc::grad(p);

// fvm for matrix assembly
fvm::div(phi, T)
fvm::laplacian(alpha, T)
```

---

## 5. Boundary Not Updated

### Problem

```cpp
T = newValue;
// Boundary still has old values!
```

### Solution

```cpp
T = newValue;
T.correctBoundaryConditions();  // Update boundary
```

---

## 6. Implicit vs Explicit Source

### Problem

```cpp
// Large explicit source can destabilize
TEqn += fvc::Su(largeSource, T);
```

### Solution

```cpp
// Use implicit when possible
TEqn += fvm::Sp(coefficient, T);
```

---

## 7. Interpolation Order

### Problem

Using wrong interpolation affects accuracy

### Solution

```cpp
// Check fvSchemes
divSchemes
{
    div(phi,U)  Gauss linearUpwind grad(U);  // 2nd order
}
```

---

## Quick Troubleshooting

| Problem | Fix |
|---------|-----|
| Dimension error | Check equation physics |
| NaN values | Add SMALL to divisors |
| Dangling ref | Keep tmp alive |
| Wrong BC | Call correctBoundaryConditions |
| Unstable | Use implicit terms |

---

## Concept Check

<details>
<summary><b>1. ทำไมต้อง + SMALL?</b></summary>

**ป้องกัน division by zero** ที่ทำให้เกิด NaN
</details>

<details>
<summary><b>2. Sp vs Su ต่างกันอย่างไร?</b></summary>

- **Sp**: Implicit (stable, in matrix)
- **Su**: Explicit (can destabilize)
</details>

<details>
<summary><b>3. ทำไม tmp ต้อง keep alive?</b></summary>

เมื่อ tmp destroyed, **memory freed** → dangling reference
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Operators:** [03_Operator_Overloading.md](03_Operator_Overloading.md)