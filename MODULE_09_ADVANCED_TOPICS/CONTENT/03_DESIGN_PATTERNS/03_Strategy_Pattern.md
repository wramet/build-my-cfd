# Strategy Pattern

Strategy Pattern ใน OpenFOAM

---

## Overview

> **Strategy** = Define family of algorithms, make interchangeable

---

## 1. Problem

```cpp
// Hardcoded interpolation
scalar interpolate(scalar a, scalar b, scalar t)
{
    return a + t * (b - a);  // Only linear!
}
```

---

## 2. Strategy Solution

```cpp
class interpolationScheme
{
public:
    virtual scalar interpolate(scalar a, scalar b, scalar t) = 0;
};

class linear : public interpolationScheme
{
    scalar interpolate(scalar a, scalar b, scalar t) override
    {
        return a + t * (b - a);
    }
};

class cubic : public interpolationScheme
{
    scalar interpolate(scalar a, scalar b, scalar t) override
    {
        scalar t2 = sqr(t);
        return a + t2 * (3 - 2*t) * (b - a);
    }
};
```

---

## 3. OpenFOAM Schemes

```cpp
// fvSchemes dictionary
divSchemes
{
    div(phi,U)      Gauss upwind;
    div(phi,T)      Gauss linearUpwind grad(T);
}

laplacianSchemes
{
    laplacian(nu,U) Gauss linear corrected;
}
```

---

## 4. Usage

```cpp
// User code doesn't know which scheme
fvVectorMatrix UEqn(fvm::div(phi, U));

// Scheme selected from fvSchemes dictionary
```

---

## 5. Benefits

| Benefit | Description |
|---------|-------------|
| **Flexibility** | Change algorithm without code change |
| **Testing** | Easy to test each strategy |
| **Comparison** | Compare strategies easily |
| **Configuration** | Dictionary-driven selection |

---

## Quick Reference

| Component | Role |
|-----------|------|
| Interface | Abstract strategy |
| Concrete | Specific algorithm |
| Context | Uses strategy |
| Dictionary | Selects strategy |

---

## 🧠 Concept Check

<details>
<summary><b>1. Strategy vs inheritance?</b></summary>

**Strategy**: Algorithm as object, changeable at runtime
</details>

<details>
<summary><b>2. fvSchemes = Strategy?</b></summary>

**ใช่** — schemes are interchangeable strategies
</details>

<details>
<summary><b>3. ข้อดีของ dictionary selection?</b></summary>

**No recompile** — change scheme in dictionary only
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Factory:** [02_Factory_Pattern.md](02_Factory_Pattern.md)