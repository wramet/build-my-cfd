# Template Syntax

ไวยากรณ์ Template

---

## Learning Objectives

By the end of this file, you will be able to:

1. **Recognize** the fundamental template syntax structure (`template<parameters> declaration`)
2. **Write** class templates, function templates, and member templates
3. **Apply** multiple template parameters, including non-type parameters
4. **Utilize** template template parameters for advanced generic programming
5. **Define** default template parameters for flexible APIs
6. **Create** type aliases using both `typedef` and `using` declarations
7. **Distinguish** between `class` and `typename` in template parameter declarations

---

## Overview

> Template syntax = `template<parameters> declaration`

C++ templates enable **generic programming**—writing code that works with multiple types while maintaining type safety. The template syntax consists of two parts:

1. **Template parameter list**: Specifies the types or values to be parameterized
2. **Declaration**: The actual class, function, or variable being templated

This syntax allows the compiler to generate type-specific versions of your code at compile-time, following the principle of **"Write Once, Generate Many"**.

<!-- IMAGE: IMG_09_001 -->
<!-- 
Purpose: เพื่อแสดงหลักการ "Generic Programming" ของ C++ Template. ภาพนี้ต้องสื่อว่า Code ต้นฉบับมีแค่ "แม่พิมพ์" (Template) อันเดียว แต่ Compiler ปั๊มออกมาเป็น Class หลายเวอร์ชัน (Instantiation) เช่น `GeometricField<scalar>`, `GeometricField<vector>`.
Prompt: "C++ Template Instantiation Mechanism. **Input Source:** A Blueprint Scroll marked `template<class T> class Field`. **Processing:** A Compiler Gear Machine interacting with the blueprint. **Output (Generated Code):** Three distinct Instantiated Classes popping out: 1. `Field<Scalar>` (Yellow). 2. `Field<Vector>` (Green). 3. `Field<Tensor>` (Red). **Concept:** 'Write Once, Generate Many'. STYLE: Compiler process conceptual art, crisp code blocks, industrial machine metaphor."
-->
![IMG_09_001: C++ Template Instantiation](IMG_09_001.jpg)

---

## 1. Class Templates

**What**: A class template defines a pattern for creating type-specific classes

**Why**: Enables containers and data structures to work with any data type without code duplication

**How**: Use `template<class T>` before the class declaration

```cpp
template<class Type>
class Container
{
    Type value_;
    
public:
    Container(const Type& val) : value_(val) {}
    const Type& value() const { return value_; }
    void setValue(const Type& val) { value_ = val; }
};

// Usage examples
Container<scalar> s(3.14);           // Container for scalar values
Container<vector> v(vector(1, 2, 3)); // Container for vector values
Container<label> l(42);               // Container for integer labels
```

**OpenFOAM Example**: `List<T>` is the fundamental container template in OpenFOAM:

```cpp
// From OpenFOAM: List.H
template<class T>
class List
{
    // Dynamic array of type T
};
```

---

## 2. Function Templates

**What**: A function template defines a pattern for creating type-specific functions

**Why**: Allows algorithms to work with multiple types without rewriting the function

**How**: Use `template<class T>` before the function declaration; types are often deduced automatically

```cpp
template<class Type>
Type maximum(const Type& a, const Type& b)
{
    return (a > b) ? a : b;
}

// Usage with type deduction (compiler infers Type = scalar)
scalar m = maximum(3.0, 5.0);

// Usage with explicit type specification
scalar m = maximum<scalar>(3.0, 5.0);
```

**OpenFOAM Example**: Mathematical operations are templated:

```cpp
// From OpenFOAM: Mathematical functions
template<class Type>
Type mag(const Type& t)
{
    return sqrt(t & t);  // Works for scalar, vector, tensor
}
```

---

## 3. Multiple Template Parameters

**What**: Templates can accept multiple type parameters

**Why**: Some classes need to be parameterized over multiple independent types (e.g., field type and mesh type)

**How**: Separate parameters with commas in the template parameter list

```cpp
// Multiple type parameters
template<class Type, class GeoMesh>
class DimensionedField
{
    Type* dataPtr_;
    const GeoMesh::Mesh& mesh_;
    
    // Combines a data type with a mesh type
};

// Usage in OpenFOAM
DimensionedField<scalar, volMesh> rho;      // Scalar field on volume mesh
DimensionedField<vector, volMesh> U;        // Vector field on volume mesh
```

### Non-Type Template Parameters

**What**: Templates can accept compile-time constant values (not just types)

**Why**: Enables size-specific optimizations and compile-time computations

**How**: Use integral types, enums, pointers, or references as parameters

```cpp
template<class Type, int N>
class FixedList
{
    Type data_[N];  // Fixed-size array known at compile-time
    
public:
    static constexpr int size() { return N; }
};

// Usage
FixedList<scalar, 3> coord;    // Array of 3 scalars
FixedList<label, 6> faces;     // Array of 6 labels
```

**OpenFOAM Example**: Fixed-size containers for performance-critical code:

```cpp
// From OpenFOAM: FixedList.H
template<class T, unsigned Size>
class FixedList
{
    T v_[Size];  // Stack-allocated, no dynamic memory
};

// Common uses
FixedList<scalar, 3> x;        // 3D coordinates
FixedList<label, 6> hexFaces;  // Hexahedron face labels
```

---

## 4. Template Template Parameters

**What**: A template parameter that is itself a template

**Why**: Allows generic code to accept templated types as parameters while preserving their templated nature

**How**: Declare the template parameter with its own template parameter list

```cpp
template<class Type, template<class> class PatchField, class GeoMesh>
class GeometricField
{
    // PatchField is itself a template that accepts Type
    // This enables flexible boundary field types
};

// OpenFOAM usage examples
GeometricField<scalar, fvPatchField, volMesh> p;      // Pressure
GeometricField<vector, fvPatchField, volMesh> U;      // Velocity
GeometricField<scalar, fvsPatchField, surfaceMesh> phi; // Flux
```

**Why This Matters in OpenFOAM**: This pattern allows fields to use different boundary condition types while maintaining a unified interface:

```cpp
// All use the same GeometricField template
// but with different PatchField implementations:
GeometricField<scalar, fixedValueFvPatchField, volMesh> inletT;
GeometricField<scalar, zeroGradientFvPatchField, volMesh> outletT;
GeometricField<scalar, calculatedFvPatchField, volMesh> wallT;
```

---

## 5. Default Template Parameters

**What**: Template parameters can have default values

**Why**: Reduces boilerplate and provides sensible defaults while allowing customization

**How**: Specify defaults using `=` in the template parameter list

```cpp
template<class Type = scalar, class Allocator = std::allocator<Type>>
class List
{
    // Type defaults to scalar if not specified
    // Allocator defaults to std::allocator
};

// Usage
List<> defaultList;           // List<scalar, std::allocator<scalar>>
List<vector> vectorList;      // List<vector, std::allocator<vector>>
List<label, CustomAllocator> customList;  // Explicit specification
```

**OpenFOAM Example**: Field type aliases with defaults:

```cpp
// From OpenFOAM: GeometricField.H
// Default mesh and patch field types are commonly specified
typedef GeometricField<scalar, fvPatchField, volMesh> volScalarField;
typedef GeometricField<vector, fvPatchField, volMesh> volVectorField;
typedef GeometricField<scalar, fvsPatchField, surfaceMesh> surfaceScalarField;

// Usage - much cleaner than full template specification
volScalarField p(mesh);  // Pressure field
volVectorField U(mesh);  // Velocity field
```

---

## 6. Member Function Templates

**What**: Individual member functions can be templated within a non-templated or templated class

**Why**: Allows specific functions to accept multiple types while the class remains non-templated or differently templated

**How**: Add `template<class T>` before the member function declaration

```cpp
class Converter
{
public:
    // Member template for type conversion
    template<class Type>
    Type convert(const scalar& val)
    {
        return Type(val);
    }
    
    // Different member template
    template<class InputType, class OutputType>
    OutputType transform(const InputType& input)
    {
        return static_cast<OutputType>(input);
    }
};

// Usage
Converter conv;
scalar s = conv.convert<scalar>(3.14);
vector v = conv.convert<vector>(1.0);
```

**OpenFOAM Example**: Field operations with mixed types:

```cpp
// From OpenFOAM: GeometricField.C
template<class Type, template<class> class PatchField, class GeoMesh>
template<class Type2>
void GeometricField<Type, PatchField, GeoMesh>::operator=
(
    const GeometricField<Type2, PatchField, GeoMesh>&
)
{
    // Allows assignment between fields of different types
    // e.g., volVectorField = volScalarField (with appropriate conversion)
}
```

---

## 7. Type Aliases

**What**: Create alternative names for complex template instantiations

**Why**: Improves code readability and reduces verbosity

**How**: Use `typedef` (traditional) or `using` (modern C++11 and later)

```cpp
// typedef style (C++98)
typedef GeometricField<scalar, fvPatchField, volMesh> volScalarField;
typedef GeometricField<vector, fvPatchField, volMesh> volVectorField;
typedef GeometricField<tensor, fvPatchField, volMesh> volTensorField;

// using style (C++11 - preferred)
using volScalarField = GeometricField<scalar, fvPatchField, volMesh>;
using volVectorField = GeometricField<vector, fvPatchField, volMesh>;
using volTensorField = GeometricField<tensor, fvPatchField, volMesh>;
```

**OpenFOAM Examples**: OpenFOAM extensively uses type aliases:

```cpp
// Field type aliases
using volScalarField = GeometricField<scalar, fvPatchField, volMesh>;
using volVectorField = GeometricField<vector, fvPatchField, volMesh>;
using surfaceScalarField = GeometricField<scalar, fvsPatchField, surfaceMesh>;

// Dimensional field aliases
using dimensionedScalar = DimensionedField<scalar, volMesh>;
using dimensionedVector = DimensionedField<vector, volMesh>;

// Common in OpenFOAM solvers
volScalarField p  // Pressure
volVectorField U  // Velocity
surfaceScalarField phi  // Flux
```

**Benefits**:
- **Readability**: `volScalarField` is clearer than `GeometricField<scalar, fvPatchField, volMesh>`
- **Maintainability**: Change the underlying template in one place
- **Documentation**: Type names communicate their purpose (volume vs surface, scalar vs vector)

---

## Quick Reference

| Syntax | Purpose | Example |
|--------|---------|---------|
| `template<class T>` | Single type parameter | `template<class Type> class List` |
| `template<class T, class U>` | Multiple type parameters | `template<class Type, class Mesh> class Field` |
| `template<class T, int N>` | Type + non-type parameter | `template<class T, int Size> class FixedList` |
| `template<class T = int>` | Default parameter | `template<class T = scalar> class Container` |
| `template<template<class> class T>` | Template template parameter | `template<class T, template<class> class Patch> class GeometricField` |
| `typedef Type Alias;` | Traditional type alias | `typedef Field<scalar> ScalarField` |
| `using Alias = Type;` | Modern type alias (C++11) | `using ScalarField = Field<scalar>` |

---

## 🧠 Concept Check

<details>
<summary><b>1. What is the difference between class and typename in template parameters?</b></summary>

**No difference**—`class` and `typename` are interchangeable for template type parameters in C++.

```cpp
template<class T>    // Traditional syntax
template<typename T> // Modern, more explicit syntax
```

Best practice: Use `typename` for type parameters (clearer intent), reserve `class` for actual template class parameters.

</details>

<details>
<summary><b>2. What types can be used as non-type template parameters?</b></summary>

**Integral types only**: `int`, `bool`, `char`, `long`, enums, pointers, references, and `std::nullptr_t`.

```cpp
template<int N>         // Valid: integer
template<bool B>        // Valid: boolean
template<int* ptr>      // Valid: pointer
template<int& ref>      // Valid: reference
template<float f>       // INVALID: floating-point not allowed
```

Common in OpenFOAM: `template<unsigned Size>` for fixed-size containers like `FixedList`.

</details>

<details>
<summary><b>3. When would you use a template template parameter?</b></summary>

When a parameter needs to be **a template itself**, not an instantiated type.

Use cases:
- **Containers**: Accept any container template regardless of stored type
- **Policy classes**: Allow customization of behavior through templated policies
- **OpenFOAM fields**: Different boundary condition types

```cpp
// Template template parameter
template<class T, template<class> class Container>
class DataStore
{
    Container<T> data;  // Container is a template, not a type
};

// Usage
DataStore<int, List> ints;    // List<int>
DataStore<double, List> doubles; // List<double>
```

</details>

<details>
<summary><b>4. What is type deduction in function templates?</b></summary>

The compiler **automatically determines** template arguments from function call arguments.

```cpp
template<class T>
T maximum(const T& a, const T& b) { return (a > b) ? a : b; }

// Type deduction: T deduced as scalar
maximum(3.0, 5.0);

// Type deduction: T deduced as int
maximum(3, 5);

// Explicit specification (rarely needed)
maximum<scalar>(3.0, 5.0);
```

**Limitation**: Cannot always deduce all parameters (e.g., return type only).

</details>

<details>
<summary><b>5. Why prefer using over typedef for type aliases?</b></summary>

**`using` is more powerful and readable** (C++11 and later):

```cpp
// typedef - can be confusing for complex types
typedef void (*FuncPtr)(int);

// using - clearer syntax
using FuncPtr = void(*)(int);

// typedef - templates require specialization
template<class T>
struct Alloc { typedef T value_type; };

// using - direct template aliases (C++11)
template<class T>
using AllocType = typename Alloc<T>::value_type;
```

Advantages:
- More readable for complex types
- Supports template aliases
- Consistent syntax with other declarations

</details>

---

## Key Takeaways

1. **Template Syntax Structure**: `template<parameters> declaration` - always specify parameters first, then the templated entity
2. **Two Main Template Types**: Class templates (for types) and function templates (for algorithms)
3. **Type vs Non-Type Parameters**: Templates accept both types (`class T`) and compile-time constants (`int N`)
4. **Template Template Parameters**: Enable generic code that accepts templated types while preserving their template nature
5. **Default Parameters**: Provide sensible defaults while allowing customization (`template<class T = scalar>`)
6. **Type Aliases**: Use `using` (C++11) instead of `typedef` for better readability and template support
7. **OpenFOAM Patterns**: Fields use complex template parameters (`GeometricField<Type, PatchField, Mesh>`) simplified through type aliases (`volScalarField`, `volVectorField`)
8. **Member Templates**: Individual functions can be templated independently of their class
9. **Type Deduction**: Function templates typically deduce types from arguments, reducing boilerplate
10. **class vs typename**: Interchangeable in template parameters, but `typename` is more explicit

---

## 📖 Related Documents

- **Overview**: [00_Overview.md](00_Overview.md) - Template concepts and motivations
- **Mechanics**: [03_Internal_Mechanics.md](03_Internal_Mechanics.md) - How templates work internally
- **Specialization**: [04_Template_Specialization.md](04_Template_Specialization.md) - Customizing templates for specific types
- **Examples**: [05_OpenFOAM_Examples.md](05_OpenFOAM_Examples.md) - Real OpenFOAM template usage
- **Exercises**: [06_Exercises.md](06_Exercises.md) - Practice problems and solutions