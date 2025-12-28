# Common Pitfalls

ปัญหาที่พบบ่อยใน Dimensional Analysis

---

## 1. Dimension Mismatch

### Problem

```
--> FOAM FATAL ERROR:
Inconsistent dimensions for +
   [0 1 -1 0 0 0 0] + [1 -1 -2 0 0 0 0]
```

### Solution

```cpp
// Check physics - can't add velocity + pressure
// Correct equation dimensions

// Bad
result = U + p;  // Error!

// Good
result = U + fvc::grad(p) / rho;  // Both are [L/T²]
```

---

## 2. Missing dimless

### Problem

```cpp
scalar factor = 2.0;
result = factor * T;  // Error: scalar has no dimensions
```

### Solution

```cpp
// Use dimensionedScalar for operations
dimensionedScalar factor("f", dimless, 2.0);
result = factor * T;

// Or use literal with same dimensions
result = 2.0 * T;  // Works for scalar literals
```

---

## 3. Inconsistent Source Term

### Problem

```cpp
fvScalarMatrix TEqn
(
    fvm::ddt(T) == source  // Source has wrong dimensions
);
```

### Solution

```cpp
// ddt(T) has dimensions [T/s] = [Θ/s]
// Source must match
dimensionedScalar source("S", dimTemperature/dimTime, 100);
```

---

## 4. Division Issues

### Problem

```cpp
result = a / b;  // b might be zero, and dimensions may not match
```

### Solution

```cpp
// Add SMALL to prevent division by zero
// Note: SMALL is dimensionless
result = a / (b + dimensionedScalar("small", b.dimensions(), SMALL));
```

---

## 5. Wrong Unit Interpretation

### Problem

Reading dictionary with wrong units assumption

### Solution

```cpp
// Always specify dimensions in dictionary
U0  U0 [0 1 -1 0 0 0 0] (1 0 0);  // Velocity

// Or use coded lookups
dict.readEntry("U0", U0);  // Check dimensions
```

---

## 6. Debug Tips

```cpp
// Print dimensions
Info << "T dimensions: " << T.dimensions() << endl;

// Check dimensionless
if (!result.dimensions().dimensionless())
{
    Warning << "Result should be dimensionless";
}
```

---

## Quick Troubleshooting

| Error | Fix |
|-------|-----|
| Dimension mismatch | Check equation physics |
| Can't add | Same dimensions required |
| Source term | Match equation dimensions |
| Division | Check divisor dimensions |

---

## 🧠 Concept Check

<details>
<summary><b>1. ทำไม scalar * field error?</b></summary>

**scalar has no dimensions** — use dimensionedScalar
</details>

<details>
<summary><b>2. SMALL ใช้อย่างไรกับ dimensions?</b></summary>

**Wrap in dimensionedScalar** with matching dimensions
</details>

<details>
<summary><b>3. ตรวจ dimensions อย่างไร?</b></summary>

**Print** `.dimensions()` หรือ check error messages
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Arithmetic:** [03_Dimension_Arithmetic.md](03_Dimension_Arithmetic.md)