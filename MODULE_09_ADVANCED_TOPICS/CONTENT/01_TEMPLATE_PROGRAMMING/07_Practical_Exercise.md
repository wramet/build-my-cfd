# Template Programming - Practical Exercises

Template Programming - แบบฝึกหัดทักษะ

---

## Learning Objectives

**What** you will learn:
- Hands-on template programming techniques for OpenFOAM development
- Practical implementation of template classes, functions, and specializations
- SFINAE concepts and applications
- Working with OpenFOAM's template infrastructure

**Why** these exercises matter:
- Templates are fundamental to OpenFOAM's architecture
- Enable type-safe generic programming with minimal runtime overhead
- Understanding templates is essential for extending OpenFOAM capabilities
- Provides foundation for reading and modifying OpenFOAM source code

**How** you will master it:
- Progressive exercises from basic to advanced template usage
- Real OpenFOAM examples and use cases
- Template specialization and SFINAE techniques
- Working with tmp<> and other OpenFOAM template utilities

---

## Exercise 1: Basic Template Class

### What You're Building

Create a **generic data wrapper** that can store any OpenFOAM data type with associated metadata.

### Why This Matters

Template classes are the foundation of OpenFOAM's type-safe generic programming. This pattern appears throughout OpenFOAM for wrapping fields, boundary conditions, and numerical data.

### Task: Implement DataWrapper

```cpp
template<class Type>
class DataWrapper
{
    word name_;
    Type value_;

public:
    // Constructor
    DataWrapper(const word& name, const Type& val)
    : name_(name), value_(val) {}

    // Accessors
    const word& name() const { return name_; }
    const Type& value() const { return value_; }
    Type& value() { return value_; }
    
    // Print method
    void print() const
    {
        Info << "DataWrapper: " << name_ << " = " << value_ << endl;
    }
};
```

### Usage Examples

```cpp
// Scalar data wrapper
DataWrapper<scalar> temperature("T", 300);
temperature.print();

// Vector data wrapper  
DataWrapper<vector> velocity("U", vector(1, 0, 0));
velocity.print();

// Tensor data wrapper
DataWrapper<symmTensor> stress("sigma", symmTensor::zero);
```

### Expected Output

```
DataWrapper: T = 300
DataWrapper: U = (1 0 0)
DataWrapper: sigma = (0 0 0 0 0 0)
```

### Exercise Tasks

1. Add a `setValue()` method that updates the value
2. Add a `clone()` method that creates a copy of the wrapper
3. Add template specialization for `vector` that prints magnitude

<details>
<summary><b>💡 Solution Hints</b></summary>

```cpp
// setValue() method
void setValue(const Type& newVal)
{
    value_ = newVal;
}

// clone() method
DataWrapper<Type> clone() const
{
    return DataWrapper<Type>(name_, value_);
}

// Specialization for vector
template<>
void DataWrapper<vector>::print() const
{
    Info << "Vector " << name_ 
         << ": (" << value_.x() << ", " << value_.y() << ", " << value_.z() << ")"
         << " mag=" << mag(value_) << endl;
}
```
</details>

---

## Exercise 2: Template Function

### What You're Building

Implement **generic interpolation** functions that work with any OpenFOAM mathematical type.

### Why This Matters

Template functions enable compile-time polymorphism. OpenFOAM uses them extensively for mathematical operations on fields, vectors, and tensors.

### Task: Implement Interpolation Functions

```cpp
template<class Type>
Type linearInterpolate(const Type& a, const Type& b, scalar t)
{
    // Linear interpolation: a + t*(b-a)
    return a + t * (b - a);
}

template<class Type>
Type bilinearInterpolate
(
    const Type& f00, const Type& f10,
    const Type& f01, const Type& f11,
    scalar x, scalar y
)
{
    // Bilinear interpolation in 2D
    Type fx0 = linearInterpolate(f00, f10, x);
    Type fx1 = linearInterpolate(f01, f11, x);
    return linearInterpolate(fx0, fx1, y);
}
```

### Usage Examples

```cpp
// Scalar interpolation
scalar T_mid = linearInterpolate<scalar>(300, 400, 0.5);  
// Result: 350

// Vector interpolation
vector U1(0, 0, 0);
vector U2(1, 0, 0);
vector U_mid = linearInterpolate<vector>(U1, U2, 0.3);
// Result: (0.3 0 0)

// Tensor interpolation
tensor T1(tensor::I);
tensor T2(tensor::zero);
tensor T_mid = linearInterpolate<tensor>(T1, T2, 0.5);
// Result: 0.5*I

// Bilinear interpolation on a cell face
scalar f00 = 1.0, f10 = 2.0, f01 = 3.0, f11 = 4.0;
scalar f_center = bilinearInterpolate<scalar>(f00, f10, f01, f11, 0.5, 0.5);
// Result: 2.5
```

### Exercise Tasks

1. Implement `inverseDistanceInterpolate()` function
2. Add bounds checking to ensure `t` is in [0, 1]
3. Create a template function for field interpolation

<details>
<summary><b>💡 Solution Hints</b></summary>

```cpp
// Inverse distance interpolation
template<class Type>
Type inverseDistanceInterpolate
(
    const Type& a, const Type& b,
    scalar da, scalar db
)
{
    scalar wa = 1.0/max(da, SMALL);
    scalar wb = 1.0/max(db, SMALL);
    return (wa*a + wb*b)/(wa + wb);
}

// Bounds-checked version
template<class Type>
Type linearInterpolateBounded(const Type& a, const Type& b, scalar t)
{
    scalar tBounded = max(min(t, 1.0), 0.0);
    return linearInterpolate<Type>(a, b, tBounded);
}
```
</details>

---

## Exercise 3: Template Specialization

### What You're Learning

How to provide **type-specific implementations** while maintaining a generic interface.

### Why This Matters

Specialization allows optimization for specific types and custom behavior without losing generic programming benefits. Common in OpenFOAM for vector/tensor operations.

### Task: Specialize Print Functions

```cpp
// General template - works for any type
template<class Type>
void printInfo(const Type& val)
{
    Info << "Value: " << val << endl;
}

// Full specialization for vector
template<>
void printInfo<vector>(const vector& val)
{
    Info << "Vector: (" << val.x() << ", " << val.y() << ", " << val.z() << ")"
         << ", magnitude=" << mag(val) << endl;
}

// Full specialization for symmTensor
template<>
void printInfo<symmTensor>(const symmTensor& val)
{
    Info << "SymmTensor: " << val 
         << ", trace=" << tr(val)
         << ", det=" << det(val) << endl;
}
```

### Usage Examples

```cpp
// General type
printInfo(3.14159);
// Output: Value: 3.14159

// Vector specialization
printInfo(vector(1, 2, 2));
// Output: Vector: (1, 2, 2), magnitude=3

// Tensor specialization
symmTensor s(1, 0, 0, 1, 0, 1);
printInfo(s);
// Output: SymmTensor: (1 0 0 1 0 1), trace=3, det=1
```

### Partial Specialization (Class Templates Only)

```cpp
// Primary template
template<class Type, class SizeFunction>
class FieldCalculator
{
public:
    static Type calculate(const Type& x)
    {
        return SizeFunction::f(x);
    }
};

// Partial specialization for scalar (SizeFunction ignored)
template<class SizeFunction>
class FieldCalculator<scalar, SizeFunction>
{
public:
    static scalar calculate(const scalar& x)
    {
        return x * 2.0;  // Simple doubling
    }
};
```

### Exercise Tasks

1. Add specialization for `tensor` type
2. Add specialization for `word` type (with quotes)
3. Create partial specialization for pair types

<details>
<summary><b>💡 Solution Hints</b></summary>

```cpp
// Tensor specialization
template<>
void printInfo<tensor>(const tensor& val)
{
    Info << "Tensor: " << val 
         << ", trace=" << tr(val)
         << ", det=" << det(val) << endl;
}

// Word specialization
template<>
void printInfo<word>(const word& val)
{
    Info << "Word: \"" << val << "\"" << endl;
}

// Pair partial specialization
template<class T1, class T2>
class Pair
{
    T1 first_;
    T2 second_;
public:
    Pair(const T1& a, const T2& b) : first_(a), second_(b) {}
    void print() const { Info << "(" << first_ << ", " << second_ << ")"; }
};

// Specialize when both are same type
template<class T>
class Pair<T, T>
{
    T first_;
    T second_;
public:
    Pair(const T& a, const T& b) : first_(a), second_(b) {}
    void print() const 
    { 
        Info << "(" << first_ << ", " << second_ << ") [same type]"; 
    }
};
```
</details>

---

## Exercise 4: SFINAE (Substitution Failure Is Not An Error)

### What Is SFINAE?

**SFINAE** is a C++ compile-time technique that allows the compiler to **select between different template function overloads** based on type properties. If template argument substitution fails, the compiler removes that candidate from consideration rather than producing an error.

### Why SFINAE Matters

SFINAE enables **type-based function dispatch** at compile-time:
- Provide different implementations for different type categories
- Enable functions only for types with specific properties
- Improve code safety by preventing invalid template instantiations
- Heavily used in OpenFOAM for type traits and conditional compilation

### Task: Implement SFINAE Functions

```cpp
// Traditional SFINAE with enable_if (C++11/14)

// Only enabled for scalar types (int, float, double, etc.)
template<class Type>
typename std::enable_if<std::is_scalar<Type>::value, Type>::type
absolute(const Type& val)
{
    return val >= 0 ? val : -val;
}

// Only enabled for OpenFOAM vector-like types
template<class Type>
typename std::enable_if
<
    std::is_same<Type, vector>::value ||
    std::is_same<Type, Vector<double>>::value,
    Type
>::type
absolute(const Type& val)
{
    return Type(mag(val), mag(val), mag(val));
}
```

### Modern SFINAE (C++17+)

```cpp
// Using if constexpr (cleaner syntax)
template<class Type>
Type absoluteModern(const Type& val)
{
    if constexpr (std::is_scalar<Type>::value)
    {
        return val >= 0 ? val : -val;
    }
    else if constexpr (std::is_same<Type, vector>::value)
    {
        return vector(mag(val), mag(val), mag(val));
    }
    else
    {
        return val;  // Fallback
    }
}

// Using concepts (C++20)
template<std::integral T>
T absoluteConcept(T val)
{
    return val < 0 ? -val : val;
}
```

### Usage Examples

```cpp
// Works with scalar types
scalar s = absolute(-5.0);      // OK: returns 5.0
int i = absolute(-3);           // OK: returns 3

// Works with vector
vector v = absolute(vector(-1, -2, -3));  
// Returns: (2.36, 2.36, 2.36) where 2.36 ≈ mag((-1,-2,-3))

// Compile-time error for unsupported types
// absolute<word>("hello");  // ERROR: no matching function
```

### Real OpenFOAM Example: Field Type Checking

```cpp
// Function only for scalar fields
template<class GeoField>
typename std::enable_if
<
    std::is_same<typename GeoField::value_type, scalar>::value,
    void
>::type
processField(const GeoField& field)
{
    Info << "Processing scalar field: " << field.name() << endl;
    // Scalar-specific processing
}

// Function only for vector fields
template<class GeoField>
typename std::enable_if
<
    std::is_same<typename GeoField::value_type, vector>::value,
    void
>::type
processField(const GeoField& field)
{
    Info << "Processing vector field: " << field.name() << endl;
    // Vector-specific processing
}
```

### Exercise Tasks

1. Add SFINAE function that only works with integral types
2. Create SFINAE overload that detects if a type has a `mag()` method
3. Implement type trait to check if a type is an OpenFOAM field

<details>
<summary><b>💡 Solution Hints</b></summary>

```cpp
// Integral-only function
template<class Type>
typename std::enable_if<std::is_integral<Type>::value, bool>::type
isEven(const Type& val)
{
    return val % 2 == 0;
}

// Detect if type has mag() method (using decltype)
template<class Type>
auto hasMagMethod(int) -> decltype(std::declval<Type>().mag(), std::true_type{})
{
    return std::true_type{};
}

template<class Type>
auto hasMagMethod(...) -> std::false_type
{
    return std::false_type{};
}

// Usage
static_assert(hasMagMethod<vector>::value, "vector has mag()");
static_assert(!hasMagMethod<scalar>::value, "scalar doesn't have mag()");

// Check if type is an OpenFOAM field
template<class T>
struct isField : std::false_type {};

template<class Type, template<class> class GeoField>
struct isField<GeoField<Type>> : std::true_type {};

// Usage
static_assert(isField<volScalarField>::value, "volScalarField is a field");
```
</details>

---

## Exercise 5: OpenFOAM Template Infrastructure

### What You're Learning

How to work with **OpenFOAM's template utilities** including tmp<>, refPtr<>, and field types.

### Why This Matters

OpenFOAM's template infrastructure is central to efficient memory management and field operations. Understanding it is essential for:
- Writing efficient boundary conditions
- Creating custom turbulence models
- Implementing source terms
- Understanding OpenFOAM library internals

### Task: Working with tmp<T>

The `tmp<T>` class provides **reference-counted temporary object management**:

```cpp
// Create temporary field
tmp<volScalarField> computeField(const volScalarField& T)
{
    // tmp manages memory automatically
    return tmp<volScalarField>
    (
        new volScalarField
        (
            IOobject
            (
                "result",
                T.time().timeName(),
                T.mesh(),
                IOobject::NO_READ,
                IOobject::NO_WRITE
            ),
            T.mesh(),
            dimensionedScalar("zero", T.dimensions(), 0)
        )
    );
}

// Using tmp
tmp<volScalarField> tT = computeField(T);

// Access underlying object
volScalarField& Tresult = tT.ref();  // Reference
const volScalarField& Tconst = tT(); // Const reference

// tmp is automatically destroyed when out of scope
```

### Modern C++ Style (OpenFOAM+)

```cpp
// Using makeTmp (type deduction)
tmp<volScalarField> computeFieldModern(const volScalarField& T)
{
    auto tresult = tmp<volScalarField>::New
    (
        "result",
        T.time().timeName(),
        T.mesh()
    );
    
    tresult.ref() = 2 * T;
    
    return tresult;
}
```

### refPtr<T> - Reference or Pointer

```cpp
template<class Type>
void processData(refPtr<volScalarField> fieldPtr)
{
    if (fieldPtr.isTmp())
    {
        Info << "Managing temporary field" << endl;
    }
    else
    {
        Info << "Managing external reference" << endl;
    }
    
    // Access works regardless
    fieldPtr.ref() += dimensionedScalar("one", dimless, 1);
}

// Can accept temporary or reference
tmp<volScalarField> tempField = ...;
volScalarField& permanentField = ...;

processData(tempField);      // Takes ownership
processData(permanentField); // Just stores reference
```

### Generic Field Processing

```cpp
// Template function working with any field type
template<class GeoField>
void normalizeField(GeoField& field)
{
    // Find min/max
    typename GeoField::value_type minVal = min(field).value();
    typename GeoField::value_type maxVal = max(field).value();
    
    // Normalize to [0, 1]
    field = (field - minVal) / max(maxVal - minVal, SMALL);
}

// Usage with different field types
volScalarField& p = mesh.lookupObject<volScalarField>("p");
volVectorField& U = mesh.lookupObject<volVectorField>("U");

normalizeField(p);  // Works for scalar
normalizeField(U);  // Works for vector
```

### Exercise Tasks

1. Create a function returning tmp<> with field algebra
2. Implement generic field clamping function
3. Add const-correctness handling with tmp<const T>

<details>
<summary><b>💡 Solution Hints</b></summary>

```cpp
// Returning tmp with field algebra
tmp<volScalarField> computeT2(const volScalarField& T)
{
    return tmp<volScalarField>::New
    (
        T * T  // Square of temperature
    );
}

// Generic clamping
template<class GeoField>
void clampField
(
    GeoField& field,
    const typename GeoField::value_type& minVal,
    const typename GeoField::value_type& maxVal
)
{
    field = max(min(field, maxVal), minVal);
}

// Const tmp handling
void processTemp(const tmp<volScalarField>& tT)
{
    // tT() returns const reference
    Info << "Max value: " << max(tT()).value() << endl;
    
    // If we need to modify, we must const_cast or ref()
    if (!tT.isTmp())
    {
        // Non-temporary: can't modify
        WarningInFunction << "Cannot modify const reference" << endl;
    }
}
```
</details>

---

## Exercise 6: Complete OpenFOAM Template Example

### What You're Building

A **generic boundary condition** using template metaprogramming techniques.

### Task: Template Boundary Condition

```cpp
// Generic fixed-value boundary condition template
template<class Type>
class GenericFixedValueFvPatchField
:
    public fvPatchField<Type>
{
    // Private data
    Type value_;
    
public:
    // Constructors
    GenericFixedValueFvPatchField
    (
        const fvPatch& p,
        const DimensionedField<Type, volMesh>& iF
    )
    :
        fvPatchField<Type>(p, iF),
        value_(pTraits<Type>::zero)
    {
        // Type-specific zero initialization
    }
    
    // Evaluation (called by solver)
    virtual void updateCoeffs()
    {
        if (this->updated())
        {
            return;  // Already updated
        }
        
        // Set patch values
        fvPatchField<Type>::operator==(value_);
        
        fvPatchField<Type>::updated();
    }
    
    // Write
    virtual void write(Ostream& os) const
    {
        fvPatchField<Type>::write(os);
        writeEntry(os, "value", value_);
    }
};
```

### Specialization for Vector Fields

```cpp
// Specialization for vector with additional functionality
template<>
class GenericFixedValueFvPatchField<vector>
:
    public fvPatchField<vector>
{
    vector value_;
    bool normalize_;
    
public:
    virtual void updateCoeffs()
    {
        if (this->updated())
        {
            return;
        }
        
        vector finalValue = value_;
        
        if (normalize_)
        {
            // Normalize to unit magnitude
            scalar magVal = mag(value_);
            if (magVal > SMALL)
            {
                finalValue /= magVal;
            }
        }
        
        fvPatchField<vector>::operator==(finalValue);
        fvPatchField<vector>::updated();
    }
};
```

### Exercise Tasks

1. Add time-varying value support
2. Implement gradient calculation
3. Add serialization/deserialization

<details>
<summary><b>💡 Solution Hints</b></summary>

```cpp
// Time-varying support
private:
    Function1<Type>* valueFunction_;

public:
    virtual void updateCoeffs()
    {
        if (this->updated())
        {
            return;
        }
        
        scalar t = this->db().time().value();
        Type currentValue = valueFunction_->value(t);
        
        fvPatchField<Type>::operator==(currentValue);
        fvPatchField<Type>::updated();
    }

// Gradient calculation
virtual tmp<Field<Type>> gradientInternalCoeffs() const
{
    return tmp<Field<Type>>::New(this->size(), pTraits<Type>::zero);
}

virtual tmp<Field<Type>> gradientBoundaryCoeffs() const
{
    return tmp<Field<Type>>::New
    (
        this->patch().patchInternalField(this->patchInternalField())
    );
}
```
</details>

---

## Quick Reference: Template Programming

| Concept | Syntax | Example |
|---------|--------|---------|
| **Class Template** | `template<class T> class Name` | `template<class Type> class Field` |
| **Function Template** | `template<class T> T func(T)` | `template<class T> T max(T a, T b)` |
| **Full Specialization** | `template<> void func<Type>()` | `template<> void print<vector>()` |
| **Partial Specialization** | `template<class T> class A<T, int>` | `template<class T> class Pair<T,T>` |
| **Default Type** | `template<class T = double>` | `template<class T = scalar>` |
| **Non-type Template** | `template<int N>` | `template<unsigned Size>` |
| **Template Template** | `template<template<class> class C>` | `template<template<class> class List>` |
| **SFINAE (C++11)** | `std::enable_if<cond, T>::type` | `typename std::enable_if<std::is_scalar<T>::value, T>::type` |
| **if constexpr (C++17)** | `if constexpr (cond)` | `if constexpr (std::is_integral_v<T>)` |
| **Concepts (C++20)** | `template<Concept T>` | `template<std::integral T>` |

### OpenFOAM Template Utilities

| Class | Purpose | Common Usage |
|-------|---------|--------------|
| `tmp<T>` | Reference-counted temporary | `tmp<volScalarField>` |
| `refPtr<T>` | Reference or pointer wrapper | `refPtr<field>` |
| `autoPtr<T>` | Unique pointer (ownership transfer) | `autoPtr<mesh>` |
| `List<T>` | Dynamic array | `List<scalar>` |
| `Field<T>` | Geometric field | `Field<vector>` |
| `DimensionedField<T, GeoMesh>` | Mesh-associated field | `DimensionedField<scalar, volMesh>` |
| `GeometricField<T, PatchField, GeoMesh>` | Complete field | `GeometricField<scalar, fvPatchField, volMesh>` |

---

## Concept Check

<details>
<summary><b>1. When does template instantiation occur?</b></summary>

**Answer:** At **compile-time** when the compiler encounters a template used with a concrete type. Each unique type combination generates separate compiled code.

Example:
```cpp
DataWrapper<scalar> ds(...);  // Instantiates DataWrapper<scalar>
DataWrapper<vector> dv(...);  // Instantiates DataWrapper<vector>
```
</details>

<details>
<summary><b>2. When should you use template specialization?</b></summary>

**Answer:** When you need **different behavior or implementation** for a specific type, while maintaining the same interface.

Common use cases:
- Type-specific optimizations (e.g., vector operations)
- Different output formatting (e.g., print functions)
- Exploiting type-specific capabilities (e.g., tensor algebra)
- Handling special cases (e.g., zero-sized containers)
</details>

<details>
<summary><b>3. What is SFINAE and why is it useful?</b></summary>

**Answer:** **S**ubstitution **F**ailure **I**s **N**ot **A**n **E**rror is a C++ compile-time mechanism that:
- Allows function overload resolution based on type properties
- Enables or disables functions based on template conditions
- Provides type safety at compile-time without runtime overhead
- Used extensively for type traits and concepts

Practical benefits:
- Prevents compilation errors for invalid type substitutions
- Enables static polymorphism
- Supports type-based optimization and specialization
</details>

<details>
<summary><b>4. What is tmp<T> in OpenFOAM?</b></summary>

**Answer:** A **reference-counted temporary object manager** used for:
- **Automatic memory management** of temporary fields
- **Delayed evaluation** of expressions
- **Performance optimization** through object reuse
- **Expression templates** in field algebra

Key features:
- `t()` returns const reference
- `t.ref()` returns mutable reference
- `t.ptr()` releases ownership (returns raw pointer)
- Automatic destruction when reference count reaches zero

Always use `tmp<>` when returning temporary fields from functions!
</details>

<details>
<summary><b>5. What's the difference between full and partial specialization?</b></summary>

**Answer:**
- **Full specialization:** All template parameters specified
  ```cpp
  template<> class MyClass<int>  // Fully specialized
  ```
  
- **Partial specialization:** Some parameters specified, others remain templated (class templates only)
  ```cpp
  template<class T> class MyClass<T, int>  // Partially specialized
  ```

Partial specialization works for class templates but **NOT** function templates. Functions must use overloading instead.
</details>

---

## Key Takeaways

### Template Programming Fundamentals
- **Templates enable compile-time polymorphism** with zero runtime overhead
- **Type safety** is enforced at compilation, not execution
- **Code reuse** without sacrificing performance

### Template Types
- **Function templates**: Generic algorithms (e.g., `min()`, `max()`)
- **Class templates**: Generic containers (e.g., `List<T>`, `Field<T>`)
- **Variable templates** (C++14): Compile-time constants

### Advanced Techniques
- **Specialization**: Customize behavior for specific types
- **SFINAE**: Conditionally enable/disable template overloads
- **Template metaprogramming**: Computation at compile-time
- **Expression templates**: Optimize mathematical expressions

### OpenFOAM-Specific
- **`tmp<T>`**: Essential for efficient field operations
- **`refPtr<T>`**: Flexible reference/pointer handling
- **Field types**: Heavily templated throughout OpenFOAM
- **Boundary conditions**: Custom BCs require template knowledge

### Best Practices
- **Prefer templates over macros** for type safety
- **Use specialization sparingly** - prefer generic code
- **Document template requirements** with concepts or type traits
- **Test with multiple types** to ensure true generic behavior
- **Be aware of code bloat** - common instantiations share code

---

## Related Documentation

### Prerequisites
- **Template Syntax:** [02_Template_Syntax.md](02_Template_Syntax.md)
- **C++ Templates:** External C++ template resources

### This Module
- **Internal Mechanics:** [03_Internal_Mechanics.md](03_Internal_Mechanics.md)
- **Instantiation:** [04_Instantiation_and_Specialization.md](04_Instantiation_and_Specialization.md)

### Application
- **Design Patterns:** [05_Design_Patterns.md](05_Design_Patterns.md)
- **Debugging:** [06_Common_Errors_and_Debugging.md](06_Common_Errors_and_Debugging.md)

---

**Practice makes perfect!** Work through these exercises systematically, experiment with variations, and refer to OpenFOAM source code for real-world template usage examples.