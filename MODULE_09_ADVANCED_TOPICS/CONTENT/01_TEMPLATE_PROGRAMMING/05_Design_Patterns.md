# Design Patterns with Templates

Design Patterns ที่ใช้ Templates

---

## Overview

> Templates enable **compile-time polymorphism** patterns

---

## 1. Policy-Based Design

```cpp
template<class SolverPolicy, class PreconditionerPolicy>
class LinearSolver
{
    SolverPolicy solver_;
    PreconditionerPolicy precond_;

public:
    void solve(fvMatrix& eqn)
    {
        precond_.apply();
        solver_.solve(eqn);
    }
};

// Usage
LinearSolver<CGSolver, DICPreconditioner> solver;
```

---

## 2. CRTP (Curiously Recurring Template Pattern)

```cpp
template<class Derived>
class Base
{
public:
    void interface()
    {
        // Call derived implementation
        static_cast<Derived*>(this)->implementation();
    }
};

class Derived : public Base<Derived>
{
public:
    void implementation()
    {
        // Actual work
    }
};
```

### OpenFOAM Example

```cpp
template<class CloudType>
class KinematicCloud : public Cloud<CloudType>
{
    // CRTP pattern
};
```

---

## 3. Type Traits

```cpp
template<class Type>
struct TypeTraits
{
    typedef Type value_type;
    static const bool is_scalar = false;
};

template<>
struct TypeTraits<scalar>
{
    typedef scalar value_type;
    static const bool is_scalar = true;
};
```

---

## 4. Mixins

```cpp
template<class Base>
class Printable : public Base
{
public:
    void print() const
    {
        Info << static_cast<const Base*>(this)->name() << endl;
    }
};

// Add printing capability to any class
class MyField : public Printable<FieldBase> { ... };
```

---

## 5. Expression Templates

```cpp
// Avoid temporaries in field operations
template<class E1, class E2>
class AddExpr
{
    const E1& e1_;
    const E2& e2_;
public:
    auto operator[](label i) const { return e1_[i] + e2_[i]; }
};
```

---

## Quick Reference

| Pattern | Use |
|---------|-----|
| Policy-based | Configurable behavior |
| CRTP | Static polymorphism |
| Type traits | Type information |
| Mixin | Add capabilities |

---

## 🧠 Concept Check

<details>
<summary><b>1. Policy-based vs inheritance?</b></summary>

**Policy**: Compile-time selection, no virtual overhead
</details>

<details>
<summary><b>2. CRTP ดีอย่างไร?</b></summary>

**Static polymorphism** — no virtual call overhead
</details>

<details>
<summary><b>3. Type traits ใช้ทำอะไร?</b></summary>

**Query type properties** at compile-time
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Errors:** [06_Common_Errors_and_Debugging.md](06_Common_Errors_and_Debugging.md)