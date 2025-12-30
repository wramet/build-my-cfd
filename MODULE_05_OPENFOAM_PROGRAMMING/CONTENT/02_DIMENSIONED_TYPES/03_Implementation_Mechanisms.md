# Implementation Mechanisms

กลไกการทำงานภายในของ Dimensioned Types — เบื้องหลัง Dimension Checking

> **ทำไมต้องรู้ Implementation?**
> - เข้าใจ **rules** ของ dimension operations (เมื่อไหร่บวก/คูณ dimensions)
> - Debug errors ได้เร็วขึ้น
> - เขียน custom dimensioned types ได้

---

## Learning Objectives

หลังจากอ่านบทนี้ คุณควรจะสามารถ:
- เข้าใจโครงสร้างภายในของ `dimensionSet` และ `dimensioned` types
- อธิบายวิธี operator overloading ทำ dimension checking
- ควบคุมและปรับแต่งการตรวจสอบ dimensions
- หลีกเลี่ยง common pitfalls ในการใช้งาน
- ใช้ dimensioned types อย่างมีประสิทธิภาพ

---

## Overview

> **💡 Dimension checking = Operator Overloading + Runtime Validation**
>
> ทุกครั้งที่ `+`, `-`, `*`, `/` → OpenFOAM ตรวจสอบ dimensions ก่อน

OpenFOAM ใช้ระบบ type-safe ที่ตรวจสอบความสมดุลของมิติในขณะ **compile-time** และ **runtime** ผ่าน:
- **Operator Overloading**: ทำให้ operations ตรวจสอบ dimensions โดยอัตโนมัติ
- **Runtime Validation**: ตรวจสอบและ abort เมื่อพบ dimension mismatches
- **Dimension Arithmetic**: คำนวณผลลัพธ์ของ dimensions โดยอัตโนมัติ

---

## 1. dimensionSet Class

`dimensionSet` เป็นหัวใจของระบบ dimension checking ใน OpenFOAM:

```cpp
class dimensionSet
{
    // 7 base dimensions: [M, L, T, Θ, I, N, J]
    scalar exponents_[7];  

public:
    // Constructors
    dimensionSet();  // dimensionless
    dimensionSet(scalar M, scalar L, scalar T, 
                 scalar Theta, scalar I, scalar N, scalar J);
    
    // Copy constructor
    dimensionSet(const dimensionSet& ds);

    // Dimension arithmetic operators
    dimensionSet operator*(const dimensionSet& ds) const;
    dimensionSet operator/(const dimensionSet& ds) const;
    dimensionSet operator+(const dimensionSet& ds) const;
    dimensionSet operator-(const dimensionSet& ds) const;
    dimensionSet operator^(scalar) const;  // power

    // Comparison operators
    bool operator==(const dimensionSet& ds) const;
    bool operator!=(const dimensionSet& ds) const;

    // Utility functions
    bool dimensionless() const;
    scalar operator[](int) const;  // access individual exponents
    
    // Global checking control
    static bool checking_;
    static bool checking() { return checking_; }
    static void checking(bool on) { checking_ = on; }
};
```

### Internal Representation

```cpp
// Density [M L^-3]
dimensionSet rho(1, -3, 0, 0, 0, 0, 0);

// Velocity [L T^-1]
dimensionSet U(0, 1, -1, 0, 0, 0, 0);

// Access individual exponents
Info << "Mass exponent: " << rho[0] << endl;  // 1
Info << "Length exponent: " << rho[1] << endl;  // -3
```

---

## 2. Dimension Arithmetic

### Multiplication

```cpp
// [M L^-3] * [L T^-1] = [M L^-2 T^-1]
dimensionSet a(1, -3, 0, 0, 0, 0, 0);  // density
dimensionSet b(0, 1, -1, 0, 0, 0, 0);  // velocity
dimensionSet c = a * b;  // [1, -2, -1, 0, 0, 0, 0]

Info << c << endl;  // Output: [1 -2 -1 0 0 0 0]
```

### Division

```cpp
// [M L^-1 T^-2] / [M L^-3] = [L² T^-2]
dimensionSet p(1, -1, -2, 0, 0, 0, 0);  // pressure
dimensionSet rho(1, -3, 0, 0, 0, 0, 0);  // density
dimensionSet result = p / rho;  // [0, 2, -2, 0, 0, 0, 0]

Info << result << endl;  // Output: [0 2 -2 0 0 0 0]
```

### Power

```cpp
// [L T^-1]² = [L² T^-2]
dimensionSet U(0, 1, -1, 0, 0, 0, 0);
dimensionSet U2 = pow(U, 2);  // [0, 2, -2, 0, 0, 0, 0]

// [M L^-3]^(-1) = [M^-1 L³]
dimensionSet rho(1, -3, 0, 0, 0, 0, 0);
dimensionSet invRho = pow(rho, -1);  // [-1, 3, 0, 0, 0, 0, 0]
```

### Addition/Subtraction (Must Match!)

```cpp
dimensionSet a(1, -3, 0, 0, 0, 0, 0);
dimensionSet b(1, -3, 0, 0, 0, 0, 0);
dimensionSet c = a + b;  // ✓ Same dimensions

dimensionSet d(0, 1, -1, 0, 0, 0, 0);
// dimensionSet e = a + d;  // ✗ Runtime error: dimension mismatch
```

---

## 3. dimensionedType Template

```cpp
template<class Type>
class dimensioned
{
    word name_;           // Variable name
    dimensionSet dimensions_;  // Dimension information
    Type value_;          // Actual value

public:
    // Constructors
    dimensioned(const word& name, const dimensionSet& ds, const Type& t);
    dimensioned(const word& name, const Type& t);
    dimensioned(const Type& t);
    dimensioned(const dimensioned<Type>&);

    // Access functions
    const word& name() const { return name_; }
    const dimensionSet& dimensions() const { return dimensions_; }
    const Type& value() const { return value_; }
    
    // Modify functions
    void setName(const word& name) { name_ = name; }
    void setDimensions(const dimensionSet& ds) { dimensions_ = ds; }
    void setValue(const Type& t) { value_ = t; }

    // Operators with dimension checking
    dimensioned operator+(const dimensioned&) const;
    dimensioned operator-(const dimensioned&) const;
    dimensioned operator*(const dimensioned&) const;
    dimensioned operator/(const dimensioned&) const;
    dimensioned operator-() const;  // unary minus
    
    // Power functions
    dimensioned pow(scalar) const;
    dimensioned sqrt() const;
    dimensioned mag() const;
};
```

### Usage Examples

```cpp
// Create dimensioned scalar
dimensionedScalar rho
(
    "rho",                    // name
    dimensionSet(1, -3, 0, 0, 0, 0, 0),  // dimensions
    1000.0                    // value [kg/m³]
);

// Create from existing
dimensionedScalar rho2("rho2", rho.dimensions(), rho.value());

// Access components
Info << "Name: " << rho.name() << endl;
Info << "Value: " << rho.value() << endl;
Info << "Dimensions: " << rho.dimensions() << endl;
```

---

## 4. Operator Checking Internals

### Addition/Subtraction (Strict Equality)

```cpp
template<class Type>
dimensioned<Type> operator+(const dimensioned<Type>& a,
                            const dimensioned<Type>& b)
{
    // Dimension validation - MUST be equal
    if (a.dimensions() != b.dimensions())
    {
        FatalErrorIn("operator+(const dimensioned<Type>&, const dimensioned<Type>&)")
            << "Dimensions of quantities are different\n"
            << "    LHS: " << a.dimensions() << "\n"
            << "    RHS: " << b.dimensions() << "\n"
            << "    LHS value: " << a.value() << "\n"
            << "    RHS value: " << b.value() << "\n"
            << abort(FatalError);
    }
    
    return dimensioned<Type>
    (
        a.name() + "+" + b.name(),
        a.dimensions(),  // Keep same dimensions
        a.value() + b.value()
    );
}
```

### Multiplication (Dimension Multiplication)

```cpp
template<class Type>
dimensioned<Type> operator*(const dimensioned<Type>& a,
                            const dimensioned<Type>& b)
{
    return dimensioned<Type>
    (
        a.name() + "*" + b.name(),
        a.dimensions() * b.dimensions(),  // Multiply exponents!
        a.value() * b.value()
    );
}
```

### Division (Dimension Division)

```cpp
template<class Type>
dimensioned<Type> operator/(const dimensioned<Type>& a,
                            const dimensioned<Type>& b)
{
    return dimensioned<Type>
    (
        a.name() + "/" + b.name(),
        a.dimensions() / b.dimensions(),  // Subtract exponents!
        a.value() / b.value()
    );
}
```

### Power Function

```cpp
dimensioned<scalar> dimensioned<scalar>::pow(scalar p) const
{
    return dimensioned<scalar>
    (
        name() + "^" + name(p),
        ::pow(dimensions(), p),  // Multiply exponents by p
        ::pow(value(), p)
    );
}

dimensioned<scalar> dimensioned<scalar>::sqrt() const
{
    return dimensioned<scalar>
    (
        "sqrt(" + name() + ")",
        ::pow(dimensions(), 0.5),  // Divide exponents by 2
        ::sqrt(value())
    );
}
```

---

## 5. Checking Control

### Global Checking Flag

```cpp
// Global static flag
bool dimensionSet::checking_ = true;
```

### Disabling Checks (Use Sparingly!)

```cpp
// Disable dimension checking globally
dimensionSet::checking(false);

// Perform operations without checking
dimensioned<scalar> a("a", dimless, 1.0);
dimensioned<scalar> b("b", dimensionSet(0, 1, -1, 0, 0, 0, 0), 2.0);
dimensioned<scalar> c = a + b;  // No error (checking disabled)

// Re-enable checking
dimensionSet::checking(true);
```

### Best Practices for Checking Control

> **⚠️ WARNING:** Disabling dimension checking removes critical safety net!

**When to Disable:**
1. **Temporary Workarounds**: เมื่อต้อง handling legacy code
2. **Special Operations**: เมื่อต้องทำ dimensionally inconsistent operations
3. **Testing**: Debug หรือ test specific scenarios

**Best Practices:**

```cpp
// BAD: Permanently disabled in constructor
MyClass::MyClass()
{
    dimensionSet::checking(false);  // Don't do this!
}

// GOOD: Temporary disable with RAII pattern
class CheckingDisabler
{
    bool oldState_;
public:
    CheckingDisabler() : oldState_(dimensionSet::checking()) 
    { 
        dimensionSet::checking(false); 
    }
    ~CheckingDisabler() 
    { 
        dimensionSet::checking(oldState_); 
    }
};

// Usage
void specialOperation()
{
    CheckingDisabler disabler;  // Disable in scope
    // ... operations without checking ...
    // Automatically restored on exit
}
```

**Better Alternative - Use Correct Dimensions:**

```cpp
// Instead of disabling checks, fix the dimensions!
dimensioned<scalar> value
(
    "value",
    dimless,  // Correctly specify dimensionless
    someCalculation()
);
```

### Checking Status

```cpp
// Check current status
if (dimensionSet::checking())
{
    Info << "Dimension checking is ENABLED" << endl;
}
else
{
    Info << "Dimension checking is DISABLED" << endl;
}
```

---

## 6. Common Type Aliases

```cpp
// Standard OpenFOAM typedefs
typedef dimensioned<scalar> dimensionedScalar;
typedef dimensioned<vector> dimensionedVector;
typedef dimensioned<tensor> dimensionedTensor;
typedef dimensioned<symmTensor> dimensionedSymmTensor;
typedef dimensioned<sphericalTensor> dimensionedSphericalTensor;
```

### Type Alias Usage

```cpp
// Scalar with dimensions
dimensionedScalar p("p", dimensionSet(1, -1, -2, 0, 0, 0, 0), 101325.0);

// Vector with dimensions
dimensionedVector g
(
    "g",
    dimensionSet(0, 1, -2, 0, 0, 0, 0),
    vector(0, 0, -9.81)
);

// Tensor with dimensions
dimensionedTensor tau
(
    "tau",
    dimensionSet(1, -1, -2, 0, 0, 0, 0),
    tensor::zero
);
```

---

## 7. Common Pitfalls

### 7.1 Disabling Checks Globally

```cpp
// PITFALL: Forgetting to re-enable checks
dimensionSet::checking(false);
someOperation();
// Forgot to re-enable! All subsequent code is unsafe!

// SOLUTION: Use RAII pattern or always re-enable
dimensionSet::checking(false);
someOperation();
dimensionSet::checking(true);
```

### 7.2 Wrong Dimensions for Dimensionless Quantities

```cpp
// PITFALL: Not specifying dimless for dimensionless values
dimensioned<scalar> Re("Re", dimensionSet(0, 0, 0, 0, 0, 0, 0), 1000);

// SOLUTION: Use dimless constant
dimensioned<scalar> Re("Re", dimless, 1000);
```

### 7.3 Mixing dimensioned and Non-dimensioned

```cpp
// PITFALL: Operations with plain scalars
dimensionedScalar a("a", dimensionSet(1, -3, 0, 0, 0, 0, 0), 1.0);
scalar b = 2.0;
dimensionedScalar c = a * b;  // OK, but be careful!

// SOLUTION: Use dimensioned explicitly
dimensionedScalar b_dim("b", dimless, 2.0);
dimensionedScalar c = a * b_dim;  // Clear intent
```

### 7.4 Assuming pow() Works with Non-Integer Exponents

```cpp
// PITFALL: Non-integer powers on dimensions
dimensionedScalar L("L", dimensionSet(0, 1, 0, 0, 0, 0, 0), 1.0);
dimensionedScalar L_half = pow(L, 0.5);  // OK
dimensionedScalar L_third = pow(L, 1.0/3.0);  // May cause issues

// Check dimensionSet implementation for non-integer support
```

### 7.5 Not Reading Error Messages Carefully

```cpp
// PITFALL: Ignoring detailed error messages
/*
--> FOAM FATAL ERROR:
Dimensions of quantities are different
    LHS: [0 1 -1 0 0 0 0]
    RHS: [1 -3 0 0 0 0 0]
    LHS value: (1 2 3)
    RHS value: 1000
*/

// SOLUTION: Read and understand the dimension mismatch
// LHS = [L T^-1] = velocity
// RHS = [M L^-3] = density
// Cannot add velocity + density!
```

---

## Quick Reference

### Dimension Arithmetic Rules

| Operation | Dimension Effect | Example |
|-----------|------------------|---------|
| a + b | Must match | [m/s] + [m/s] = [m/s] |
| a - b | Must match | [Pa] - [Pa] = [Pa] |
| a * b | Add exponents | [kg/m³] × [m/s] = [kg/(m²·s)] |
| a / b | Subtract exponents | [Pa] / [kg/m³] = [m²/s²] |
| pow(a, n) | Multiply exponents by n | [m/s]² = [m²/s²] |
| sqrt(a) | Divide exponents by 2 | √[m²/s²] = [m/s] |
| mag(a) | No change (magnitude only) | \|vector\| keeps dims |

### Base Dimension Reference

| Index | Symbol | Name | SI Unit |
|-------|--------|------|---------|
| 0 | M | Mass | kg |
| 1 | L | Length | m |
| 2 | T | Time | s |
| 3 | Θ | Temperature | K |
| 4 | I | Electric Current | A |
| 5 | N | Amount of Substance | mol |
| 6 | J | Luminous Intensity | cd |

### Common Dimensions

```cpp
// Dimensionless
const dimensionSet dimless(0, 0, 0, 0, 0, 0, 0);

// Common mechanical dimensions
const dimensionSet dimMass(1, 0, 0, 0, 0, 0, 0);        // [M]
const dimensionSet dimLength(0, 1, 0, 0, 0, 0, 0);     // [L]
const dimensionSet dimTime(0, 0, 1, 0, 0, 0, 0);       // [T]
const dimensionSet dimPressure(1, -1, -2, 0, 0, 0, 0); // [M L^-1 T^-2]
const dimensionSet dimDensity(1, -3, 0, 0, 0, 0, 0);   // [M L^-3]
const dimensionSet dimVelocity(0, 1, -1, 0, 0, 0, 0);  // [L T^-1]
const dimensionSet dimAcceleration(0, 1, -2, 0, 0, 0, 0); // [L T^-2]
```

---

## 🧠 Concept Check

<details>
<summary><b>1. Addition ต้อง dimension เหมือนกันไหม?</b></summary>

**ใช่** — Addition และ subtraction ต้องมี dimensions เหมือนกันทุกประการ  
ตัวอย่าง: pressure + pressure ✓, pressure + velocity ✗

```cpp
dimensionSet p(1, -1, -2, 0, 0, 0, 0);  // [M L^-1 T^-2]
dimensionSet U(0, 1, -1, 0, 0, 0, 0);  // [L T^-1]
// p + U;  // FatalError: Dimensions do not match
```
</details>

<details>
<summary><b>2. Multiplication ทำอะไรกับ dimensions?</b></summary>

**บวก exponents** เช่น [M L^-3] × [L T^-1] = [M L^-2 T^-1]

```cpp
dimensionSet a(1, -3, 0, 0, 0, 0, 0);  // [M L^-3]
dimensionSet b(0, 1, -1, 0, 0, 0, 0);  // [L T^-1]
dimensionSet c = a * b;  // [1, -2, -1, 0, 0, 0, 0] = [M L^-2 T^-1]
```
</details>

<details>
<summary><b>3. sqrt() ทำอะไรกับ dimensions?</b></summary>

**หาร exponents ด้วย 2** เช่น sqrt([L² T^-2]) = [L T^-1]

```cpp
dimensionSet a(0, 2, -2, 0, 0, 0, 0);  // [L² T^-2]
dimensionSet b = ::pow(a, 0.5);  // [0, 1, -1, 0, 0, 0, 0] = [L T^-1]
```
</details>

<details>
<summary><b>4. ทำไม dimension checking ถึงสำคัญ?</b></summary>

**ป้องกัน bugs จาก dimension mismatches:**
- ตรวจสอบใน runtime → พบ error ได้ทันที
- ทำให้สมการถูกต้อง dimensionally
- เพิ่มความชัดเจนของ code

```cpp
// Without dimension checking (bad):
scalar Re = rho * U * L / mu;  // What if dimensions are wrong?

// With dimension checking (good):
dimensionedScalar Re = rho * U * L / mu;  // Automatic validation
```
</details>

<details>
<summary><b>5. เมื่อไหร่ควร disable dimension checking?</b></summary>

**เกือบไม่มีกรณีที่ควร disable!**

ใช้เฉพาะ:
- Legacy code ที่แก้ไม่ได้
- Special operations ที่จำเป็นต้องใช้
- **และต้อง re-enable ทันทีหลังใช้**

```cpp
// Use RAII pattern for safety
CheckingDisabler disabler;
// ... temporary operations ...
// Auto-restore on exit
```
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **พื้นฐาน Dimensioned Types:** [01_Introduction.md](01_Introduction.md)
- **Template Metaprogramming:** [04_Template_Metaprogramming.md](04_Template_Metaprogramming.md)
- **SI Dimensions Reference:** [00_Overview.md](00_Overview.md#si-base-dimensions)