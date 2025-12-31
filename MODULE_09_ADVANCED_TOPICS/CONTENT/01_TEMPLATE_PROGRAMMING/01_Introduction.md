# Template Programming - Introduction

บทนำ Template Programming — ทำไม OpenFOAM ถึงใช้ templates อย่างกว้างขวาง?

---

## 🎯 Learning Objectives

หลังจากอ่านบทนี้ คุณจะสามารถ:

1. **อธิบาย** ทำไม C++ templates ถึงสำคัญสำหรับ OpenFOAM
2. **เปรียบเทียบ** template-based polymorphism vs inheritance
3. **อ่าน** basic template declarations ใน OpenFOAM source code
4. **ระบุ** ประโยชน์ด้าน performance ของ templates
5. **เลือกใช้** templates vs inheritance อย่างเหมาะสม

---

## 🏗️ 3W Framework

### What: Templates คืออะไร?

**C++ Templates** คือ compile-time code generation mechanism ที่:
- เขียน code ครั้งเดียว ใช้ได้กับหลาย types
- สร้าง specialized code ตอน compile (ไม่ใช่ runtime)
- ไม่มี runtime overhead

**Before/After Comparison:**

**❌ Without Templates (Duplicate Code):**
```cpp
// ต้องเขียนแยกสำหรับทุก type
class ScalarField
{
    scalar* data_;
    label size_;
public:
    scalar sum() const { ... }
};

class VectorField
{
    vector* data_;
    label size_;
public:
    vector sum() const { ... }     // Duplicate logic!
};

class TensorField
{
    tensor* data_;
    label size_;
public:
    tensor sum() const { ... }     // Duplicate logic!
};
```

**✅ With Templates (Single Definition):**
```cpp
// เขียนครั้งเดียว ใช้ได้กับทุก type
template<class T>
class Field
{
    T* data_;
    label size_;
public:
    T sum() const
    {
        T result = Zero;
        for (label i = 0; i < size_; ++i)
        {
            result += data_[i];
        }
        return result;
    }
};

// Instantiate for specific types
typedef Field<scalar> scalarField;
typedef Field<vector> vectorField;
typedef Field<tensor> tensorField;
```

### Why: ทำไมต้องใช้ Templates?

| Approach | Pros | Cons |
|----------|------|------|
| **Copy-paste code** | Simple | Maintenance nightmare |
| **Inheritance** | Flexible | Runtime overhead (vtable) |
| **Templates** | Zero overhead, type-safe | Complex syntax |

**Templates ให้:**

1. **Zero Runtime Overhead**
   - Compiler generates specialized code for each type
   - No virtual function calls
   - Inline optimization possible

2. **Type Safety**
   - Compile-time type checking
   - ไม่มี implicit conversions ที่ไม่ต้องการ

3. **Code Reuse**
   - เขียนครั้งเดียว ใช้กับทุก type
   - DRY (Don't Repeat Yourself)

4. **Performance**
   - Loop unrolling possible
   - Vectorization by compiler
   - No indirection

### How: OpenFOAM Uses Templates

**OpenFOAM Template Classes ที่พบบ่อย:**

| Template | Purpose | Example Types |
|----------|---------|---------------|
| `Field<T>` | 1D array with math ops | scalar, vector, tensor |
| `GeometricField<T,...>` | Mesh-based field | volScalarField |
| `List<T>` | Dynamic array | List<label>, List<word> |
| `autoPtr<T>` | Smart pointer | autoPtr<Model> |
| `tmp<T>` | Temporary holder | tmp<volScalarField> |

**Reading Template Declarations:**

```cpp
// Template class declaration
template<class T>  // T = type parameter
class Field
{
    // ...
};

// Template function
template<class T>
T max(const Field<T>& f)
{
    return *std::max_element(f.begin(), f.end());
}

// Multiple parameters
template<class T, direction N>
class FixedList
{
    T v_[N];  // Compile-time sized array
};
```

---

## 📊 Templates vs Inheritance

### Comparison Table

| Feature | Templates | Inheritance |
|---------|-----------|-------------|
| **Binding** | Compile-time | Runtime |
| **Performance** | Zero overhead | vtable overhead |
| **Flexibility** | Static (known at compile) | Dynamic (runtime selection) |
| **Code size** | Larger (multiple instances) | Smaller (shared code) |
| **Error messages** | Complex | Simple |
| **Extensibility** | Limited (recompile needed) | Open (plugins possible) |

### When to Use What

**Use Templates:**
- Performance critical code (field operations)
- Type varies but known at compile time
- Need inlining and optimization

**Use Inheritance:**
- Runtime polymorphism needed (user-selected models)
- Plugin architecture
- Factory pattern (e.g., turbulenceModel::New())

**OpenFOAM Example:**

```cpp
// Templates: Performance-critical Field operations
template<class T>
T Foam::sum(const UList<T>& f)
{
    T result = Zero;
    forAll(f, i)
    {
        result += f[i];
    }
    return result;
}

// Inheritance: Runtime-selected models
class turbulenceModel
{
public:
    virtual ~turbulenceModel() = default;
    virtual void correct() = 0;  // Runtime polymorphism
    
    static autoPtr<turbulenceModel> New(const dictionary&);
};
```

---

## 🔍 Common Template Patterns in OpenFOAM

### 1. tmp<T> Pattern

```cpp
// Return temporary without copy
tmp<volScalarField> computeField(const volScalarField& T)
{
    return tmp<volScalarField>
    (
        new volScalarField("result", sqr(T))
    );
}

// Usage: automatic cleanup
tmp<volScalarField> result = computeField(T);
```

### 2. Type Traits

```cpp
// Check type properties at compile time
template<class T>
struct pTraits;

template<>
struct pTraits<scalar>
{
    static const direction nComponents = 1;
    static const direction rank = 0;
};

template<>
struct pTraits<vector>
{
    static const direction nComponents = 3;
    static const direction rank = 1;
};
```

### 3. Dimension Checking Templates

```cpp
// dimensioned<Type> combines value with units
template<class Type>
class dimensioned
{
    word name_;
    dimensionSet dimensions_;
    Type value_;
};

// Instantiations
typedef dimensioned<scalar> dimensionedScalar;
typedef dimensioned<vector> dimensionedVector;
```

---

## ⚠️ Common Pitfalls

| Problem | Cause | Solution |
|---------|-------|----------|
| "undefined reference" | Missing template instantiation | Add explicit instantiation |
| Cryptic error messages | Template substitution failure | Check type requirements |
| Code bloat | Too many instantiations | Use explicit instantiation |
| Long compile times | Header-only templates | Precompiled headers |

---

## 🧠 Concept Check

<details>
<summary><b>1. Templates และ inheritance ต่างกันอย่างไร?</b></summary>

**Templates:** Compile-time polymorphism
- Type resolved at compile time
- No runtime overhead
- Code generated for each type

**Inheritance:** Runtime polymorphism
- Type resolved at runtime via vtable
- Small overhead (virtual call)
- Shared code for all types
</details>

<details>
<summary><b>2. ทำไม OpenFOAM Field ใช้ templates?</b></summary>

**Performance:** 
- Field operations (sum, max, etc.) run millions of times
- Templates allow inlining and optimization
- No virtual call overhead

**Code reuse:**
- Same operations for scalar, vector, tensor, symmTensor
- เขียนครั้งเดียว ใช้ทุก type
</details>

<details>
<summary><b>3. Template instantiation คืออะไร?</b></summary>

**Compiler สร้าง concrete code จาก template:**

```cpp
// Template
template<class T>
T sum(const Field<T>& f);

// Instantiation (compiler generates)
scalar sum(const Field<scalar>& f);  // scalarField version
vector sum(const Field<vector>& f);  // vectorField version
```
</details>

---

## 📖 Related Documents

- [00_Overview.md](00_Overview.md) — Module roadmap
- [02_Template_Syntax.md](02_Template_Syntax.md) — Detailed syntax guide
- [03_Internal_Mechanics.md](03_Internal_Mechanics.md) — How templates work
- [04_Instantiation_and_Specialization.md](04_Instantiation_and_Specialization.md) — Advanced topics