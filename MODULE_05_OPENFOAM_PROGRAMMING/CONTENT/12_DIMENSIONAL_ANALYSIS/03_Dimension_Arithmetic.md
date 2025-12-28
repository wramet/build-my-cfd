# Dimension Arithmetic

การคำนวณทางคณิตศาสตร์กับ Dimensions

---

## Overview

> Dimensions combine automatically ตาม **physics rules**

---

## 1. Multiplication

```cpp
// Exponents add
dimensionedScalar F = m * a;
// [kg] * [m/s²] = [kg·m/s²] = [N]

// Example
dimensionedScalar rho("rho", dimDensity, 1000);
dimensionedScalar U("U", dimVelocity, 10);
dimensionedScalar dynP = 0.5 * rho * sqr(U);
// [kg/m³] * [m²/s²] = [kg/(m·s²)] = [Pa]
```

---

## 2. Division

```cpp
// Exponents subtract
dimensionedScalar nu = mu / rho;
// [Pa·s] / [kg/m³] = [m²/s]
```

---

## 3. Powers

```cpp
// Exponents multiply
dimensionedScalar L2 = sqr(L);    // [m²]
dimensionedScalar L3 = pow3(L);   // [m³]
dimensionedScalar sqrtA = sqrt(A);  // [m]
```

---

## 4. Addition/Subtraction

```cpp
// Must have SAME dimensions
dimensionedScalar total = p1 + p2;  // Both [Pa] ✓

// Error if different!
// result = p + U;  // [Pa] + [m/s] = ERROR!
```

---

## 5. Dimensioned Operations

```cpp
// All operators check dimensions
volScalarField result = rho * sqr(U) + p;
// [Pa] + [Pa] = [Pa] ✓

// fvc operations maintain dimensions
volVectorField gradP = fvc::grad(p);
// [Pa/m]
```

---

## 6. Common Calculations

| Calculation | Dimensions |
|-------------|------------|
| ρU² | [Pa] |
| μ∇U | [Pa] |
| ∇p | [Pa/m] |
| U·∇U | [m/s²] |

---

## Quick Reference

| Operation | Exponents |
|-----------|-----------|
| A * B | Add |
| A / B | Subtract |
| sqr(A) | Double |
| sqrt(A) | Halve |
| A + B | Must match |

---

## Concept Check

<details>
<summary><b>1. ρU² มี dimension อะไร?</b></summary>

**[Pa]** = [kg/m³][m²/s²] = [kg/(m·s²)]
</details>

<details>
<summary><b>2. Addition ต้องการอะไร?</b></summary>

**Same dimensions** — ไม่งั้น error
</details>

<details>
<summary><b>3. sqrt dimension ทำอย่างไร?</b></summary>

**Halve exponents** — sqrt(m²) = m
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **DimensionSet:** [02_DimensionSet_Advanced.md](02_DimensionSet_Advanced.md)