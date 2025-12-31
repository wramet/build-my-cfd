# Common Errors and Debugging

ข้อผิดพลาดที่พบบ่อยใน Templates

---

## Learning Objectives

By the end of this section, you will be able to:
- Identify and fix the 6 most common template compilation errors
- Apply the `typename` and `template` keywords correctly in dependent contexts
- Resolve two-phase lookup issues in template inheritance
- Debug cryptic template error messages systematically
- Troubleshoot OpenFOAM-specific template errors in boundary conditions and turbulence models

---

## What is Template Debugging?

### What (Definition)

Template debugging is the process of identifying and resolving compilation errors that arise from template metaprogramming. Template errors are notoriously cryptic because:

1. **Two-phase compilation**: Errors can occur during template definition or instantiation
2. **Type substitution**: Errors show up after type substitution, often with deep template instantiation stacks
3. **Dependent names**: The compiler cannot determine whether dependent names are types or values without help

### Why (Importance in OpenFOAM)

OpenFOAM relies heavily on templates for:
- Geometric field classes (`GeometricField<Type, PatchField, GeoMesh>`)
- Boundary condition specialization (`fixedValueFvPatchField<Type>`)
- Turbulence models (`RASModels<kEpsilon>`)
- Matrix solvers and preconditioners

When you create custom boundary conditions, thermophysical models, or numerical schemes, you will inevitably encounter template errors. Understanding how to debug them efficiently saves hours of development time.

### How (Approach)

By mastering common error patterns and applying systematic troubleshooting strategies, you can quickly identify the root cause and apply the correct fix.

---

## 1. Missing `typename` Keyword

### What (The Problem)

The compiler cannot distinguish between a dependent type and a dependent value without explicit guidance.

```cpp
template<class Container>
void process()
{
    Container::iterator it;  // ❌ Error: 'iterator' is not a type or is ambiguous
}
```

### Why (The Cause)

When a type depends on a template parameter (a "dependent type"), the compiler assumes it's a value unless told otherwise with `typename`.

### How (The Solution)

```cpp
template<class Container>
void process()
{
    typename Container::iterator it;  // ✅ Tells compiler: 'iterator' is a type
}
```

#### OpenFOAM Example

```cpp
// In a custom boundary condition
template<class Type>
void customFvPatchField<Type>::evaluate()
{
    // ❌ Error: cannot access 'value_type' without typename
    // Field<Type>::value_type val = this->value_;

    // ✅ Correct: use typename
    typename Field<Type>::value_type val = this->value_;
}
```

---

## 2. Missing `template` Keyword

### What (The Problem)

Calling a template member function from a dependent template object requires the `template` keyword.

```cpp
template<class T>
void process(Container<T>& c)
{
    c.get<int>();  // ❌ Error: expected primary-expression
}
```

### Why (The Cause)

The parser needs to know that `<` starts a template argument list, not a comparison operator.

### How (The Solution)

```cpp
template<class T>
void process(Container<T>& c)
{
    c.template get<int>();  // ✅ Explicitly marks 'get' as a template
}
```

#### OpenFOAM Example

```cpp
// In a custom turbulence model
template<class BasicTurbulenceModel>
void myModel<BasicTurbulenceModel>::correct()
{
    // ❌ Error: parsing fails
    // const volScalarField& k = this->transport().lookup<volScalarField>("k");

    // ✅ Correct: use template keyword
    const volScalarField& k = this->transport().template lookup<volScalarField>("k");
}
```

---

## 3. Two-Phase Lookup Issues

### What (The Problem)

Base class members are not visible in derived template classes without qualification.

```cpp
template<class T>
class Base {
protected:
    int value_;
};

template<class T>
class Derived : public Base<T> {
    void func()
    {
        value_ = 0;  // ❌ Error: 'value_' was not declared
    }
};
```

### Why (The Cause)

During the first phase of template parsing, the compiler cannot inspect `Base<T>` (template-dependent), so it doesn't know what members exist.

### How (The Solution)

```cpp
template<class T>
class Derived : public Base<T> {
    void func()
    {
        this->value_ = 0;  // ✅ Defers lookup to instantiation phase
        // OR
        Base<T>::value_ = 0;  // ✅ Explicit qualification
    }
}
```

#### OpenFOAM Example

```cpp
// Creating a custom boundary condition
template<class Type>
class customFvPatchField : public fixedValueFvPatchField<Type>
{
public:
    void evaluate()
    {
        // ❌ Error: 'refGrad_' not declared (from parent fvPatchField<Type>)
        // refGrad_ = Zero;

        // ✅ Solution 1: use this->
        this->refGrad_ = Zero;

        // ✅ Solution 2: use full qualification
        fixedValueFvPatchField<Type>::refGrad_ = Zero;
    }
};
```

---

## 4. Undefined Reference Errors

### What (The Problem)

```
undefined reference to `Foam::myModel<Foam::kEpsilon>::correct()'
```

### Why (The Cause)

Template code must be visible where it's instantiated. Common causes:
1. Template implementation in .C file instead of .H file
2. Missing explicit instantiation declaration

### How (The Solution)

**Option 1: Keep implementation in header**

```cpp
// myModel.H
template<class BaseModel>
class myModel
{
public:
    void correct()
    {
        // Implementation here
    }
};

// ❌ Don't do this for templates:
// #include "myModel.H"
// #include "myModel.C"  // ❌ Undefined reference errors!

// ✅ Correct: Put implementation directly in .H or use .inl file
```

**Option 2: Explicit instantiation (for specific types)**

```cpp
// myModel.C
#include "myModel.H"

// Explicitly instantiate for commonly used types
template class myModel<kEpsilon>;
template class myModel<realizableKE>;
```

#### OpenFOAM Example

```cpp
// When creating a custom boundary condition library:
// 1. Keep ALL code in customFvPatchField.H
template<class Type>
class customFvPatchField : public fixedValueFvPatchField<Type>
{
public:
    virtual void evaluate();  // Declaration only

    // ✅ Implementation immediately after or in same file
};

template<class Type>
void customFvPatchField<Type>::evaluate()
{
    // Implementation
}

// 2. Make symbols for explicit instantiation
// customFvPatchFields.C
#include "customFvPatchField.H"

// Instantiate for scalar, vector, tensor, etc.
template class customFvPatchField<scalar>;
template class customFvPatchField<vector>;
template class customFvPatchField<symmTensor>;
```

---

## 5. Type Deduction Failures

### What (The Problem)

```cpp
template<class T>
void add(T a, T b);

add(1, 2.5);  // ❌ Error: T is int or double? Ambiguous deduction
```

### Why (The Cause)

Template parameter deduction fails when arguments have conflicting types.

### How (The Solution)

**Option 1: Explicit template arguments**

```cpp
add<double>(1, 2.5);  // ✅ Explicitly specify T as double
```

**Option 2: Two template parameters**

```cpp
template<class T1, class T2>
void add(T1 a, T2 b);  // ✅ Allows different types
```

**Option 3: Common type trait**

```cpp
#include <type_traits>

template<class T1, class T2>
void add(T1 a, T2 b)
{
    using Common = typename std::common_type<T1, T2>::type;
    Common result = a + b;
}
```

#### OpenFOAM Example

```cpp
// When working with field operations:
// ❌ Error: ambiguous type deduction
// max(scalarField, vectorField);

// ✅ Solution: specify return type or use compatible types
dimensionedScalar maxVal = max(mag(scalarField), mag(vectorField));
```

---

## 6. Cryptic Error Messages

### What (The Problem)

```
error: no match for 'operator='
note: candidate is: Foam::tmp<Foam::GeometricField<double, Foam::fvPatchField, Foam::volMesh>>& Foam::tmp<Foam::GeometricField<double, Foam::fvPatchField, Foam::volMesh>>::operator=(const Foam::tmp<Foam::GeometricField<double, Foam::fvPatchField, Foam::volMesh>>&)
```

### Why (The Cause)

Template errors expand full type names, creating massive error messages. The actual issue is often a simple type mismatch.

### How (The Solution - Systematic Debugging Strategy)

1. **Read only the FIRST error message** - subsequent errors are cascading failures
2. **Find the "instantiation" context** - shows what template parameters were used
3. **Look for the mismatched types** - compare expected vs. actual
4. **Create a minimal example** - isolate the problematic code
5. **Use `static_assert` with clearer messages**:

```cpp
template<class T>
void process(T value)
{
    static_assert(std::is_same<T, scalar>::value,
                 "process() requires scalar type, not vector/tensor");
    // ...
}
```

#### OpenFOAM-Specific Error Patterns

| Error Pattern | Common Cause | Quick Fix |
|---------------|--------------|-----------|
| `no matching function` | Wrong field type (scalar vs vector) | Check field dimensions in transportProperties |
| `cannot convert 'tmp<...>'` | Missing `.ref()` or dereference | Use `.ref()` to get reference, or auto-dereference |
| `invalid use of incomplete type` | Missing include for template base | Add `#include` for parent class header |
| `'TypeName' was not declared` | Missing TypeName macro in namespace | Add `TypeName("myModel");` in class definition |

---

## Quick Troubleshooting Reference

| Error Symptom | Likely Cause | Immediate Fix |
|---------------|--------------|---------------|
| `'X' is not a type` | Missing `typename` | Add `typename` before dependent type |
| `'X' was not declared` | Two-phase lookup issue | Use `this->X` or `Base<T>::X` |
| `undefined reference to` | Definition not visible | Move code to header or add explicit instantiation |
| `expected primary-expression before '<'` | Missing `template` keyword | Use `obj.template func<Type>()` |
| `ambiguous deduction` | Conflicting type arguments | Specify types explicitly: `func<Type>()` |
| `incomplete type` | Missing include | Add `#include` for base/derived class headers |

---

## OpenFOAM-Specific Template Errors

### Boundary Condition Errors

```cpp
// ❌ Common error when creating custom BC
// error: 'TypeName' was not declared in this scope

// ✅ Solution: Add TypeName macro
template<class Type>
class customBC : public fixedValueFvPatchField<Type>
{
    TypeName("customBC");  // Required for runtime selection
};
```

### Field Operation Errors

```cpp
// ❌ Error: cannot convert 'tmp<GeometricField<...>>' to 'GeometricField<...>&&'

// ✅ Solution: Assign to auto or use ref()
auto result = f1 + f2;  // Type deduction
const volScalarField& result = (f1 + f2).ref();  // Explicit reference
```

### Turbulence Model Errors

```cpp
// ❌ Error: invalid use of incomplete type 'class RASModel<kEpsilon>'

// ✅ Solution: Include correct header
#include "RASModel.H"
#include "kEpsilon.H"

template<class BaseModel>
class myCustomModel : public RASModel<BaseModel>
{
    // Now works correctly
};
```

---

## Troubleshooting Flowchart

```
┌─────────────────────────────┐
│   Template Error Detected   │
└──────────────┬──────────────┘
               │
               ▼
      ┌────────────────┐
      │ Is it a type   │──Yes──▶ Add 'typename' before dependent type
      │ related error? │
      └───────┬────────┘
              │ No
              ▼
      ┌────────────────┐
      │ Is it about    │──Yes──▶ Add 'this->' or 'Base<T>::'
      │ undeclared     │         before member
      │ members?       │
      └───────┬────────┘
              │ No
              ▼
      ┌────────────────┐
      │ Undefined      │──Yes──▶ Move implementation to .H or
      │ reference at   │         add explicit instantiation
      │ link time?     │
      └───────┬────────┘
              │ No
              ▼
      ┌────────────────┐
      │ Template       │──Yes──▶ Use 'obj.template func<Type>()'
      │ member call    │
      │ error?         │
      └───────┬────────┘
              │ No
              ▼
      ┌────────────────┐
      │ Type           │──Yes──▶ Specify types explicitly
      │ deduction      │         func<Type1, Type2>()
      │ failure?       │
      └───────┬────────┘
              │ No
              ▼
      ┌──────────────────────────┐
      │ Check OpenFOAM patterns: │
      │ • TypeName macro         │
      │ • Field dimensions       │
      │ • Include headers        │
      │ • Use .ref() for tmp<>   │
      └──────────────────────────┘
```

---

## Key Takeaways

✅ **Always use `typename`** before dependent types (types nested in template parameters)
✅ **Always use `template`** before dependent template member functions
✅ **Use `this->`** to access base class members in template-derived classes
✅ **Keep template implementations in headers** or use explicit instantiation
✅ **Read only the first error** - ignore cascading template instantiation errors
✅ **Check OpenFOAM-specific patterns** first: TypeName, field dimensions, tmp<> handling

---

## 🧠 Concept Check

<details>
<summary><b>1. When should you use the `typename` keyword?</b></summary>

**Answer:** Use `typename` whenever accessing a dependent type - a type nested inside a template parameter, such as `Container::iterator` where `Container` is a template parameter.
</details>

<details>
<summary><b>2. How do you fix "undefined reference" template errors?</b></summary>

**Answer:** Either move the template implementation into the header file (.H) so it's visible at instantiation, OR add explicit instantiation declarations for specific types in a .C file.
</details>

<details>
<summary><b>3. Why do you need `this->` in template-derived classes?</b></summary>

**Answer:** Template compilation is two-phase. In phase 1, the compiler cannot inspect the base class, so `this->` defers member lookup to phase 2 (instantiation) when the base class is known.
</details>

<details>
<summary><b>4. What's the first thing to check with cryptic template errors in OpenFOAM?</b></summary>

**Answer:** Check that you've added the `TypeName("myClass")` macro in your class definition, as this is required for runtime selection of templated OpenFOAM classes like boundary conditions and turbulence models.
</details>

---

## 📖 Related Documentation

- **Overview:** [00_Overview.md](00_Overview.md)
- **Syntax:** [02_Template_Syntax.md](02_Template_Syntax.md)
- **Internal Mechanics:** [03_Internal_Mechanics.md](03_Internal_Mechanics.md)
- **Practical Exercise:** [07_Practical_Exercise.md](07_Practical_Exercise.md)