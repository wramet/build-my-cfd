# Template Programming - Practical Exercise

แบบฝึกหัด Template Programming

---

## Exercise 1: Basic Template Class

### Task

สร้าง template class สำหรับ wrapper ข้อมูล

```cpp
template<class Type>
class DataWrapper
{
    word name_;
    Type value_;

public:
    DataWrapper(const word& name, const Type& val)
    : name_(name), value_(val) {}

    const word& name() const { return name_; }
    const Type& value() const { return value_; }
    Type& value() { return value_; }
};

// Usage
DataWrapper<scalar> temperature("T", 300);
DataWrapper<vector> velocity("U", vector(1, 0, 0));
```

---

## Exercise 2: Template Function

### Task

สร้าง template function สำหรับ interpolation

```cpp
template<class Type>
Type linearInterpolate(const Type& a, const Type& b, scalar t)
{
    return a + t * (b - a);
}

// Usage
scalar T = linearInterpolate<scalar>(300, 400, 0.5);  // 350
vector U = linearInterpolate<vector>(U1, U2, 0.3);
```

---

## Exercise 3: Template Specialization

### Task

Specialize template สำหรับ specific type

```cpp
// General template
template<class Type>
void printInfo(const Type& val)
{
    Info << "Value: " << val << endl;
}

// Specialization for vector
template<>
void printInfo<vector>(const vector& val)
{
    Info << "Vector: (" << val.x() << ", " << val.y() << ", " << val.z() << ")"
         << " mag=" << mag(val) << endl;
}
```

---

## Exercise 4: SFINAE

### Task

ใช้ SFINAE เพื่อ enable/disable functions

```cpp
// Only for scalar types
template<class Type>
typename std::enable_if<std::is_scalar<Type>::value, Type>::type
absolute(const Type& val)
{
    return val >= 0 ? val : -val;
}
```

---

## Exercise 5: OpenFOAM Template Usage

### Task

ใช้ OpenFOAM templates ในโค้ด

```cpp
// Create dimensioned field
tmp<volScalarField> computeField(const volScalarField& T)
{
    return tmp<volScalarField>
    (
        new volScalarField
        (
            IOobject("result", T.time().timeName(), T.mesh()),
            T.mesh(),
            dimensionedScalar("zero", T.dimensions(), 0)
        )
    );
}
```

---

## Quick Reference

| Concept | Syntax |
|---------|--------|
| Class template | `template<class T> class Name` |
| Function template | `template<class T> T func(T)` |
| Specialization | `template<> void func<Type>()` |
| SFINAE | `std::enable_if<condition, Type>` |

---

## 🧠 Concept Check

<details>
<summary><b>1. Template instantiation เกิดเมื่อไหร่?</b></summary>

**Compile-time** เมื่อใช้ template กับ concrete type
</details>

<details>
<summary><b>2. Specialization ใช้เมื่อไหร่?</b></summary>

เมื่อต้องการ **different behavior** สำหรับ specific type
</details>

<details>
<summary><b>3. tmp ใน OpenFOAM คืออะไร?</b></summary>

**Reference-counted temporary** สำหรับ automatic memory management
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Template Syntax:** [02_Template_Syntax.md](02_Template_Syntax.md)