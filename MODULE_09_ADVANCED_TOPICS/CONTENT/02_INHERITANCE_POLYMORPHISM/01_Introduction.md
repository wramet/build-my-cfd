# Inheritance - Introduction

บทนำ Inheritance และ Polymorphism

---

## Overview

> **Inheritance** = Code reuse และ type hierarchy
> **Polymorphism** = Same interface, different behavior

---

## 1. Why in OpenFOAM?

| Need | Solution |
|------|----------|
| Multiple turbulence models | Base class + derived |
| Pluggable BC types | fvPatchField hierarchy |
| Interchangeable solvers | Abstract interfaces |
| Runtime model selection | Virtual functions + RTS |

---

## 2. Basic Inheritance

```cpp
// Base class
class Shape
{
protected:
    point center_;
public:
    virtual scalar area() const = 0;  // Pure virtual
};

// Derived class
class Circle : public Shape
{
    scalar radius_;
public:
    virtual scalar area() const override
    {
        return M_PI * sqr(radius_);
    }
};
```

---

## 3. Polymorphism in Action

```cpp
// Use base pointer/reference
Shape* shape = new Circle(1.0);
scalar a = shape->area();  // Calls Circle::area()

// OpenFOAM example
autoPtr<turbulenceModel> turb = turbulenceModel::New(dict);
turb->correct();  // Calls correct() of actual model type
```

---

## 4. OpenFOAM Patterns

| Pattern | Example |
|---------|---------|
| Abstract base | `turbulenceModel`, `fvPatchField` |
| Run-Time Selection | `Model::New(dict)` |
| Template + Inheritance | `GeometricField<Type,...>` |

---

## 5. Module Contents

| File | Topic |
|------|-------|
| 02_Interfaces | Abstract classes |
| 03_Hierarchies | Class trees |
| 04_RTS | Run-Time Selection |
| 05_Patterns | Design patterns |
| 06_Errors | Debugging |
| 07_Performance | Overhead |
| 08_Exercise | Practice |

---

## Quick Reference

| Concept | Syntax |
|---------|--------|
| Pure virtual | `virtual void f() = 0;` |
| Override | `virtual void f() override;` |
| Base access | `Base::method()` |

---

## Concept Check

<details>
<summary><b>1. Abstract class คืออะไร?</b></summary>

Class ที่มี **pure virtual function** — ไม่สามารถ instantiate ได้
</details>

<details>
<summary><b>2. virtual function ทำงานอย่างไร?</b></summary>

**vtable lookup** at runtime เพื่อเรียก correct derived implementation
</details>

<details>
<summary><b>3. override keyword ทำอะไร?</b></summary>

**Compiler check** ว่า function นี้ override base class method จริง
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Interfaces:** [02_Abstract_Interfaces.md](02_Abstract_Interfaces.md)