# Template Metaprogramming in Dimensioned Types

> **Learning Objectives**
> - Understand how templates enable code reuse across scalar, vector, and tensor types
> - Read and write template-based dimensioned type code
> - Apply operator overloading for dimension-aware operations
> - Create custom dimensioned types with proper type traits
> - Debug template instantiation and SFINAE errors

---

## Overview

**Template metaprogramming** is the foundation of OpenFOAM's dimension system, enabling a single implementation to work seamlessly across scalar, vector, tensor, and field types while maintaining dimensional correctness at compile time.

### Why Templates Matter

1. **Code Reuse**: Single logic for `dimensioned<scalar>`, `dimensioned<vector>`, `dimensioned<tensor>`
2. **Type Safety**: Compile-time dimensional checking for all instantiated types
3. **Flexibility**: Easy extension to custom types and fields
4. **Performance**: Zero runtime overhead for dimensional checks

### Relationship to Other Topics

- **[03_Implementation_Mechanisms.md](03_Implementation_Mechanisms.md)**: Shows how templates compile and instantiate
- **[01_Introduction.md](01_Introduction.md)**: Uses these templates for physics-aware types
- **[02_Physics_Aware_Type_System.md](02_Physics_Aware_Type_System.md)**: Applies templates to dimensional operations

---

## 1. Template Class Structure

### Basic Template Declaration

```cpp
template<class Type>
class dimensioned
{
    // Private data members
    word name_;           // Variable name for debugging/output
    dimensionSet dimensions_;  // SI dimensions (mass, length, time, etc.)
    Type value_;          // The actual value (scalar, vector, tensor)

public:
    // Constructors
    dimensioned();
    dimensioned(const word& name, const dimensionSet& ds, const Type& val);
    dimensioned(const dimensioned<Type>& dt);
    
    // Accessors
    const word& name() const;
    const dimensionSet& dimensions() const;
    const Type& value() const;
    Type& value();
    
    // Member operators
    void operator+=(const dimensioned<Type>&);
    void operator-=(const dimensioned<Type>&);
};
```

### Type Aliases for Readability

```cpp
// Common dimensioned scalar types
typedef dimensioned<scalar> dimensionedScalar;

// Common dimensioned vector types
typedef dimensioned<vector> dimensionedVector;

// Common dimensioned tensor types
typedef dimensioned<tensor> dimensionedTensor;
typedef dimensioned<symmTensor> dimensionedSymmTensor;
typedef dimensioned<sphericalTensor> dimensionedSphericalTensor;
```

**Why Use Type Aliases?**
- **Readability**: `dimensionedScalar` is clearer than `dimensioned<scalar>`
- **Documentation**: Encodes the type intent in the name
- **IDE Support**: Better autocomplete and type hints

---

## 2. Operator Overloading

### Arithmetic Operators with Dimensional Checking

```cpp
// Addition: Dimensions MUST match
template<class Type>
dimensioned<Type> operator+(
    const dimensioned<Type>& a,
    const dimensioned<Type>& b)
{
    #ifdef FULLDEBUG
    if (a.dimensions() != b.dimensions()) {
        FatalErrorInFunction
            << "Dimensions do not match: " << a.dimensions()
            << " vs " << b.dimensions()
            << abort(FatalError);
    }
    #endif
    
    return dimensioned<Type>(
        '(' + a.name() + '+' + b.name() + ')',
        a.dimensions() + b.dimensions(),  // dimensionSet::operator+
        a.value() + b.value()
    );
}

// Multiplication: Dimensions COMBINE
template<class Type1, class Type2>
dimensioned<typename promo<Type1, Type2>::type> operator*(
    const dimensioned<Type1>& a,
    const dimensioned<Type2>& b)
{
    // Deduce return type from value types
    using ResultType = typename promo<Type1, Type2>::type;
    
    return dimensioned<ResultType>(
        a.name() + '*' + b.name(),
        a.dimensions() * b.dimensions(),  // dimensionSet::operator*
        a.value() * b.value()
    );
}

// Division: Dimensions COMBINE (inverse)
template<class Type1, class Type2>
dimensioned<typename promo<Type1, Type2>::type> operator/(
    const dimensioned<Type1>& a,
    const dimensioned<Type2>& b)
{
    using ResultType = typename promo<Type1, Type2>::type;
    
    return dimensioned<ResultType>(
        a.name() + '/' + b.name(),
        a.dimensions() / b.dimensions(),  // dimensionSet::operator/
        a.value() / b.value()
    );
}
```

### Promotion Rules

```cpp
// Type promotion table (simplified)
template<class Type1, class Type2>
struct promo;

// Scalar + Scalar → Scalar
template<>
struct promo<scalar, scalar>
{
    typedef scalar type;
};

// Scalar + Vector → Vector
template<>
struct promo<scalar, vector>
{
    typedef vector type;
};

// Vector + Tensor → Tensor
template<>
struct promo<vector, tensor>
{
    typedef tensor type;
};
```

---

## 3. Function Templates

### Mathematical Functions

```cpp
// Square root: dims → dims^0.5
template<class Type>
dimensioned<Type> sqrt(const dimensioned<Type>& ds)
{
    return dimensioned<Type>(
        "sqrt(" + ds.name() + ')',
        pow(ds.dimensions(), 0.5),  // dimensionSet::pow
        Foam::sqrt(ds.value())
    );
}

// Power: dims → dims^p
template<class Type>
dimensioned<Type> pow(
    const dimensioned<Type>& ds, 
    scalar p)
{
    return dimensioned<Type>(
        "pow(" + ds.name() + ',' + name(p) + ')',
        pow(ds.dimensions(), p),
        Foam::pow(ds.value(), p)
    );
}

// Transpose: dims unchanged (for tensors)
template<class Type>
dimensioned<Type> T(const dimensioned<Type>& ds)
{
    return dimensioned<Type>(
        "T(" + ds.name() + ')',
        ds.dimensions(),  // Dimensions unchanged
        T(ds.value())
    );
}

// Magnitude: dims unchanged, scalar output
template<class Type>
dimensioned<scalar> mag(const dimensioned<Type>& ds)
{
    return dimensioned<scalar>(
        "mag(" + ds.name() + ')',
        ds.dimensions(),  // Same dimensions
        mag(ds.value())
    );
}
```

---

## 4. Template Specialization

### Partial Specialization for Symmetric Tensors

```cpp
// Generic template
template<class Type>
class dimensioned
{
    // ... generic implementation
};

// Specialization for symmetric tensors
// (optimizes for symmetry properties)
template<>
class dimensioned<symmTensor>
{
    word name_;
    dimensionSet dimensions_;
    symmTensor value_;

public:
    // Symmetry-specific operations
    dimensioned<symmTensor> symmetrize() const;
    
    // Eigenvalue decomposition (tensor-specific)
    dimensioned<scalar> eigenvalues() const;
};
```

### Compile-Time Dimension Selection

```cpp
// Template parameter for dimensions
template<Mass M, Length L, Time T, Temperature K, Moles J, Current A>
struct FixedDimensionedType
{
    typedef dimensioned<scalar> type;
};

// Usage: acceleration = L·T⁻²
using acceleration = FixedDimensionedType<0, 1, -2, 0, 0, 0>::type;
```

---

## 5. Type Traits and SFINAE

### Dimensioned Type Detection

```cpp
// Type trait: is the type a dimensioned type?
template<class Type>
struct isDimensioned
:
    std::false_type
{};

template<class Type>
struct isDimensioned<dimensioned<Type>>
:
    std::true_type
{};

// Variable template for easier use
template<class Type>
constexpr bool isDimensioned_v = isDimensioned<Type>::value;
```

### SFINAE for Dimension-Aware Overloads

```cpp
// Only enabled if Type has a dimensions() member
template<class Type>
typename std::enable_if<
    hasDimensions<Type>::value,
    dimensioned<Type>
>::type
makeDimensioned(
    const word& name,
    const dimensionSet& dims,
    const Type& val)
{
    return dimensioned<Type>(name, dims, val);
}

// Only enabled if Type is NOT dimensioned
template<class Type>
typename std::enable_if<
    !hasDimensions<Type>::value,
    dimensioned<Type>
>::type
makeDimensioned(
    const word& name,
    const dimensionSet& dims,
    const Type& val)
{
    // Assume dimensionless
    return dimensioned<Type>(name, dimless, val);
}
```

---

## 6. Integration with Field Types

### DimensionedField Template

```cpp
// Field with dimensions (stored per element)
template<class Type, class GeoMesh>
class DimensionedField
:
    public regIOobject,
    public Field<Type>
{
    // Single dimensionSet for entire field
    dimensionSet dimensions_;
    
public:
    // Constructor with dimensioned type
    DimensionedField(
        const IOobject& io,
        const GeoMesh& mesh,
        const dimensioned<Type>& dt
    );
    
    // Access dimensions
    const dimensionSet& dimensions() const;
};

// Usage
DimensionedField<scalar, volMesh> pField(
    IOobject("p", ...),
    mesh,
    dimensionedScalar("p", dimPressure, 101325)  // Pascals
);
```

### GeometricField (Fields with Boundary Conditions)

```cpp
template<class Type, template<class> class PatchField, class GeoMesh>
class GeometricField
:
    public DimensionedField<Type, GeoMesh>
{
    // Boundary field (same dimensions as internal field)
    GeometricBoundaryField<PatchField, GeoMesh> boundaryField_;
};

// Usage: Create a pressure field
volScalarField p(
    IOobject("p", runTime.timeName(), mesh),
    mesh,
    dimensionedScalar("p", dimPressure, 0),
    pBCs  // Boundary conditions
);
```

---

## 7. Custom Dimensioned Types

### Example: Reynolds Number (Dimensionless)

```cpp
// Reynolds number = (ρ * v * L) / μ
// All dimensions cancel: [kg·m/s] * [m] / [m²/s] = [1]

dimensioned<scalar> calculateReynolds(
    const dimensioned<scalar>& rho,      // Density [kg/m³]
    const dimensioned<vector>& v,        // Velocity [m/s]
    const dimensioned<scalar>& L,        // Length [m]
    const dimensioned<scalar>& mu        // Dynamic viscosity [Pa·s]
)
{
    // mag(v) extracts scalar magnitude
    // dimensions automatically cancel if correct
    dimensioned<scalar> Re = (rho * mag(v) * L) / mu;
    
    #ifdef FULLDEBUG
    if (Re.dimensions() != dimless) {
        FatalErrorInFunction
            << "Reynolds number should be dimensionless, got: "
            << Re.dimensions()
            << abort(FatalError);
    }
    #endif
    
    return Re;
}

// Usage
auto Re = calculateReynolds(
    dimensionedScalar("rho", dimDensity, 1.225),
    dimensionedVector("v", dimVelocity, vector(10, 0, 0)),
    dimensionedScalar("L", dimLength, 0.1),
    dimensionedScalar("mu", dimPressure*dimTime, 1.81e-5)
);
// Re.value() ≈ 67,000
```

### Example: Heat Transfer Coefficient

```cpp
// h = q / (A * ΔT)
// [h] = [W]/([m²]·[K]) = [kg·s⁻³·K⁻¹]

dimensioned<scalar> calculateHeatTransferCoeff(
    const dimensioned<scalar>& heatFlux,     // q [W/m²]
    const dimensioned<scalar>& area,         // A [m²]
    const dimensioned<scalar>& deltaT        // ΔT [K]
)
{
    dimensionSet expectedDims(
        1,    // Mass [kg]
        0,    // Length [m]⁰ (m²/m² = 1)
        -3,   // Time [s]⁻³
        -1,   // Temperature [K]⁻¹
        0, 0  // Moles, Current
    );
    
    dimensioned<scalar> h = (heatFlux * area) / deltaT;
    
    #ifdef FULLDEBUG
    if (h.dimensions() != expectedDims) {
        FatalErrorInFunction
            << "Heat transfer coefficient dimension mismatch!"
            << abort(FatalError);
    }
    #endif
    
    return h;
}
```

---

## 8. Debugging Template Code

### Common Template Instantiation Errors

```cpp
// ERROR: dimension mismatch
dimensionedScalar p1("p1", dimPressure, 100000);
dimensionedScalar p2("p2", dimDensity, 1.225);
auto sum = p1 + p2;  // Compile-time or runtime error

// ERROR: type mismatch
dimensioned<scalar> ds(...);
dimensioned<vector> dv(...);
auto result = ds + dv;  // Won't compile (no matching operator+)
```

### Reading Template Error Messages

```bash
# What you'll see:
error: no match for 'operator+' (operand types are 
    'Foam::dimensioned<double>' and 'Foam::dimensioned<Foam::Vector<double>>')

# What it means:
# - No operator+ defined for these type combinations
# - Check if dimensions are compatible
# - Check if promotion rule exists
```

---

## Quick Reference

| Feature | Syntax Example | Description |
|---------|----------------|-------------|
| **Template class** | `dimensioned<Type>` | Single implementation for multiple types |
| **Type alias** | `dimensionedScalar` | `typedef dimensioned<scalar>` |
| **Arithmetic** | `a + b`, `a * b` | Dimension-aware operators |
| **Functions** | `sqrt(ds)`, `pow(ds, p)` | Template functions with dimensional checks |
| **Type traits** | `isDimensioned_v<T>` | Check if type is dimensioned |
| **SFINAE** | `enable_if<condition>` | Conditional function enablement |
| **Field integration** | `volScalarField` | `GeometricField<scalar, ...>` |

---

## 🧠 Concept Check

<details>
<summary><b>1. ทำไม OpenFOAM ใช้ template สำหรับ dimensioned types?</b></summary>

**Code reuse** — เขียน logic ครั้งเดียว ใช้ได้กับ scalar, vector, tensor ทั้งหมด โดยยังคง dimensional correctness ที่ compile time

**Type safety** —  compiler เช็ค dimension ให้อัตโนมัติ ไม่ต้องเขียน runtime checks

**Performance** — zero overhead abstraction คอมไพล์เลอร์ optimize ทิ้งหมดเหลือแต่ machine code ที่มีประสิทธิภาพ
</details>

<details>
<summary><b>2. Operator overloading ทำอะไรให้กับ dimensional analysis?</b></summary>

- **Compile-time enforcement**: ถ้า dimension ไม่ match คอมไพล์ไม่ผ่าน (เช่น บวก pressure กับ density)
- **Automatic combination**: `velocity * length` → `m/s * m = m²/s` อัตโนมัติ
- **Dimension preservation**: `mag(velocity)` ยังมีหน่วยเป็น m/s เหมือนเดิม
- **Clear error messages**: บอกตำแน่ง dimension mismatch แม่นยำ

</details>

<details>
<summary><b>3. SFINAE คืออะไร และช่วยอะไร?</b></summary>

**Substitution Failure Is Not An Error** — เทคนิค template ที่ enable/disable functions ตามเงื่อนไข type

ใน OpenFOAM ใช้สำหรับ:
- สร้าง overloaded functions สำหรับ types ที่มี dimensions กับ ไม่มี
- เลือก implementation ที่เหมาะสมกับ type (เช่น symmetric tensors)
- Enable functions เฉพาะเมื่อ type มี member functions ที่ต้องการ

ช่วยให้ code ทำงาน generic แต่ยังมี type-specific optimizations
</details>

<details>
<summary><b>4. เมื่อไหร่ควรสร้าง custom dimensioned type?</b></summary>

ใช้เมื่อ:
1. **Derived quantities** ที่ใช้บ่อย เช่น Reynolds number, Nusselt number
2. **Composite operations** ที่ต้องการ dimension checking เช่น `calculateReynolds()`
3. **Domain-specific types** เช่น `dimensionedMachNumber`, `dimensionedHeatFlux`
4. **Preventing errors** ใน calculations ที่ซับซ้อน

แต่ถ้าใช้ครั้งเดียว หรือเป็น intermediate calculation เฉยๆ อาจใช้ `dimensioned<scalar>` ตรงๆ ง่ายกว่า
</details>

---

## 📖 Related Documentation

### Prerequisites
- **[01_Introduction.md](01_Introduction.md)**: Basic dimensioned type usage
- **[02_Physics_Aware_Type_System.md](02_Physics_Aware_Type_System.md)**: Dimensional arithmetic

### Related Topics
- **[03_Implementation_Mechanisms.md](03_Implementation_Mechanisms.md)**: How templates compile and instantiate
- **[00_Overview.md](00_Overview.md)**: Reference tables for SI dimensions and operations

### Further Reading
- **C++ Templates**: Vandevoorde and Josuttis, *C++ Templates: The Complete Guide*
- **OpenFOAM Source**: `src/OpenFOAM/dimensioned/dimensioned.H`
- **Type Traits**: `src/OpenFOAM/dimensionSet/dimensionSet.H`