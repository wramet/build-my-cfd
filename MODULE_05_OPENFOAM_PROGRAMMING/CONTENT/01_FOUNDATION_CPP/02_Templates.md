# C++ Templates for CFD Applications

Templates are the foundation of generic programming in C++ and are essential for building reusable CFD components. This section explores template patterns used in OpenFOAM-style field systems.

## Template Fundamentals

### Basic Template Syntax

```cpp
#include <type_traits>

// Simple generic function template
template<typename T>
T max(T a, T b) {
    return (a > b) ? a : b;
}

// Template class
template<typename T>
class Vector {
private:
    T data_[3];

public:
    Vector() : data_{0, 0, 0} {}

    T& operator[](int i) { return data_[i]; }
    const T& operator[](int i) const { return data_[i]; }

    Vector<T> operator+(const Vector<T>& other) const {
        Vector<T> result;
        for (int i = 0; i < 3; ++i) {
            result[i] = data_[i] + other[i];
        }
        return result;
    }
};
```

### Template Specialization

```cpp
// Primary template - general case
template<typename T>
class FieldInterpolator {
public:
    T interpolate(const T& a, const T& b, scalar weight) {
        return a * (1 - weight) + b * weight;
    }
};

// Specialization for vector fields
template<>
class FieldVectorizer {
private:
    scalar weight_;

public:
    FieldVectorizer(scalar weight) : weight_(weight) {}

    // Vector interpolation with magnitude preservation
    vector interpolate(const vector& a, const vector& b, scalar weight) {
        scalar magA = mag(a);
        scalar magB = mag(b);

        if (magA > SMALL && magB > SMALL) {
            scalar interpolatedMag = magA * (1 - weight) + magB * weight;
            vector direction = (a + b) / (mag(a) + mag(b) + SMALL);
            return direction * interpolatedMag;
        }
        return vector::zero;
    }
};
```

## Field Template System

### Core Field Template Class

```cpp
#include "volFields.H"
#include "surfaceFields.H"

// Generic field template based on OpenFOAM design
template<typename Type>
class VolField {
private:
    Type* ptr_;
    label size_;

public:
    // Constructors
    VolField(label size)
    : ptr_(new Type[size]), size_(size) {}

    VolField(const VolField& other)
    : ptr_(new Type[other.size_]), size_(other.size_) {
        std::copy(other.ptr_, other.ptr_ + size_, ptr_);
    }

    VolField(VolField&& other) noexcept
    : ptr_(other.ptr_), size_(other.size_) {
        other.ptr_ = nullptr;
        other.size_ = 0;
    }

    // Destructor
    ~VolField() {
        delete[] ptr_;
    }

    // Assignment operators
    VolField& operator=(const VolField& other) {
        if (this != &other) {
            delete[] ptr_;
            ptr_ = new Type[other.size_];
            size_ = other.size_;
            std::copy(other.ptr_, other.ptr_ + size_, ptr_);
        }
        return *this;
    }

    VolField& operator=(VolField&& other) noexcept {
        if (this != &other) {
            delete[] ptr_;
            ptr_ = other.ptr_;
            size_ = other.size_;
            other.ptr_ = nullptr;
            other.size_ = 0;
        }
        return *this;
    }

    // Element access
    Type& operator[](label i) { return ptr_[i]; }
    const Type& operator[](label i) const { return ptr_[i]; }

    // Iterator support
    Type* begin() { return ptr_; }
    Type* end() { return ptr_ + size_; }
    const Type* begin() const { return ptr_; }
    const Type* end() const { return ptr_ + size_; }

    // Field operations
    VolField<Type> operator+(const VolField<Type>& other) const {
        VolField<Type> result(size_);
        for (label i = 0; i < size_; ++i) {
            result[i] = (*this)[i] + other[i];
        }
        return result;
    }

    VolField<Type> operator*(scalar factor) const {
        VolField<Type> result(size_);
        for (label i = 0; i < size_; ++i) {
            result[i] = (*this)[i] * factor;
        }
        return result;
    }
};
```

### R410A Property Template Specialization

```cpp
#include "R410AProperties.H"

// Primary template for general properties
template<typename PropertyType>
class PropertyCalculator {
public:
    PropertyType calculate(scalar T, scalar p) const {
        // Default calculation - overridden by specializations
        return PropertyType(0);
    }
};

// Specialization for density
template<>
class PropertyCalculator<scalar> {
public:
    scalar calculate(scalar T, scalar p) const {
        // R410A density calculation
        return calculateR410ADensity(T, p);
    }
};

// Specialization for enthalpy
template<>
class PropertyCalculator<dimensionedScalar> {
public:
    dimensionedScalar calculate(scalar T, scalar p) const {
        // R410A enthalpy calculation with proper units
        return dimensionedScalar(
            "h",
            dimEnergy/dimMass,
            calculateR410AEnthalpy(T, p)
        );
    }
};

// Specialization for thermal conductivity
template<>
class PropertyCalculator<tensor> {
public:
    tensor calculate(scalar T, scalar p) const {
        // Anisotropic thermal conductivity
        scalar k = calculateR410AThermalConductivity(T, p);
        return tensor::diag(k, k, k);
    }
};

// Generic property field with type-specific calculations
template<typename PropertyType>
class R410APropertyField : public VolField<PropertyType> {
private:
    PropertyCalculator<PropertyType> calculator_;
    scalar referencePressure_;

public:
    R410APropertyField(label size, scalar refP = 101325)
    : VolField<PropertyType>(size), referencePressure_(refP) {}

    // Calculate properties for all cells
    void calculateProperties(const VolField<scalar>& T, const VolField<scalar>& p) {
        for (label cellI = 0; cellI < this->size(); ++cellI) {
            (*this)[cellI] = calculator_.calculate(T[cellI], p[cellI]);
        }
    }

    // Property gradient calculation
    VolField<PropertyType> calculateGradient() const {
        // Implementation of finite difference gradient
        VolField<PropertyType> gradient(this->size());

        for (label cellI = 1; cellI < this->size() - 1; ++cellI) {
            gradient[cellI] = ((*this)[cellI + 1] - (*this)[cellI - 1]) / (2 * delta_);
        }

        return gradient;
    }
};
```

## C++20 Concepts for CFD Constraints

### Defining Field Concepts

```cpp
#include <concepts>
#include <ranges>

// Concept for numeric field types
template<typename T>
concept NumericField = std::is_arithmetic_v<T> ||
                       std::is_same_v<T, scalar> ||
                       std::is_same_v<T, label>;

// Concept for vector-like types
template<typename T>
concept VectorLike = requires(T a, T b, scalar s) {
    { a + b } -> std::convertible_to<T>;
    { a - b } -> std::convertible_to<T>;
    { a * s } -> std::convertible_to<T>;
    { s * a } -> std::convertible_to<T>;
    { mag(a) } -> std::convertible_to<scalar>;
    { a & b } -> std::convertible_to<scalar>;
};

// Concept for field operations
template<typename Field>
concept FieldWithOperations = requires(Field f1, Field f2, scalar s) {
    { f1 + f2 } -> std::same_as<Field>;
    { f1 - f2 } -> std::same_as<Field>;
    { f1 * s } -> std::same_as<Field>;
    { s * f1 } -> std::same_as<Field>;
    { f1 / s } -> std::same_as<Field>;
    { dot(f1, f2) } -> NumericField;
    { mag(f1) } -> NumericField;
};
```

### Constrained Template Functions

```cpp
// Field average with concept constraints
template<FieldWithOperations Field>
scalar averageField(const Field& field) {
    scalar sum = 0;
    for (const auto& value : field) {
        sum += value;
    }
    return sum / field.size();
}

// Vector field operations with concept
template<VectorLike VectorType>
VectorType normalize(const VectorType& v) {
    scalar magV = mag(v);
    if (magV > SMALL) {
        return v / magV;
    }
    return VectorType::zero;
}

// Generic field solver with constraints
template<FieldWithOperations Field>
class FieldSolver {
public:
    void solve(Field& field, const Field& source, scalar dt) {
        // Implicit solver: A·φ = b
        Field A = calculateMatrix(field);
        Field b = source + dt * A * field;

        // Solve linear system
        Field solution = solveLinearSystem(A, b);

        // Update field
        field = solution;
    }

private:
    Field calculateMatrix(const Field& field) {
        // Assembly of coefficient matrix
        Field matrix(field.size());
        for (label i = 0; i < field.size(); ++i) {
            matrix[i] = calculateDiagonal(field[i]) +
                       calculateOffDiagonal(field[i]);
        }
        return matrix;
    }

    Field solveLinearSystem(const Field& A, const Field& b) {
        // Linear solver implementation
        Field x(b.size());

        // Gauss-Seidel iteration
        for (int iter = 0; iter < maxIter_; ++iter) {
            for (label i = 0; i < x.size(); ++i) {
                scalar sum = 0;
                for (label j = 0; j < i; ++j) {
                    sum += A[i] * x[j];
                }
                for (label j = i + 1; j < x.size(); ++j) {
                    sum += A[i] * x[j];
                }
                x[i] = (b[i] - sum) / A[i];
            }
        }

        return x;
    }
};
```

### R410A Property Calculator with Concepts

```cpp
// Concepts for R410A property calculations
template<typename PropertyType>
concept R410AProperty = requires(PropertyType p, scalar T, scalar P) {
    { p.isValid() } -> std::convertible_to<bool>;
    { p.temperature() } -> std::convertible_to<scalar>;
    { p.pressure() } -> std::convertible_to<scalar>;
};

// Constrained property calculator
template<typename PropertyType>
requires R410AProperty<PropertyType>
class R410APropertyCalculator {
public:
    PropertyType calculatePhaseProperty(scalar T, scalar P, Phase phase) const {
        if (!isInValidRange(T, P)) {
            return PropertyType::invalid();
        }

        switch (phase) {
            case Phase::LIQUID:
                return calculateLiquidProperties(T, P);
            case Phase::VAPOR:
                return calculateVaporProperties(T, P);
            case Phase::TWOPHASE:
                return calculateTwoPhaseProperties(T, P);
            default:
                return PropertyType::invalid();
        }
    }

private:
    bool isInValidRange(scalar T, scalar P) const {
        return T >= 173.15 && T <= 473.15 && // Valid temperature range
               P >= 100000 && P <= 4000000;  // Valid pressure range
    }

    PropertyType calculateLiquidProperties(scalar T, scalar P) const {
        // Liquid R410A properties
        return PropertyType(T, P, Phase::LIQUID);
    }

    PropertyType calculateVaporProperties(scalar T, scalar P) const {
        // Vapor R410A properties
        return PropertyType(T, P, Phase::VAPOR);
    }

    PropertyType calculateTwoPhaseProperties(scalar T, scalar P) const {
        // Two-phase mixture properties
        return PropertyType(T, P, Phase::TWOPHASE);
    }
};
```

## Template Metaprogramming for CFD

### Compile-Time Field Size Calculation

```cpp
// Type traits for field properties
template<typename Field>
struct FieldTraits {
    using ValueType = typename Field::value_type;
    static constexpr int Dimension = Field::Dimension;
    static constexpr bool IsVector = Field::IsVector;
};

// Compile-time field dimension checking
template<int N>
class FixedSizeField {
    static_assert(N > 0, "Field size must be positive");

private:
    std::array<scalar, N> data_;

public:
    static constexpr size_t Size = N;

    scalar& operator[](size_t i) { return data_[i]; }
    const scalar& operator[](size_t i) const { return data_[i]; }
};

// Compile-time array operations
template<int N>
FixedSizeField<N> operator+(const FixedSizeField<N>& a, const FixedSizeField<N>& b) {
    FixedSizeField<N> result;
    for (int i = 0; i < N; ++i) {
        result[i] = a[i] + b[i];
    }
    return result;
}
```

### Type Traits for CFD Types

```cpp
#include "fieldTypes.H"

// Custom type traits for OpenFOAM types
template<typename T>
struct CFDTypeTraits;

// Specialization for scalar fields
template<>
struct CFDTypeTraits<volScalarField> {
    static constexpr bool IsField = true;
    static constexpr int Rank = 0;
    using FieldType = volScalarField;
    using ValueType = scalar;
};

// Specialization for vector fields
template<>
struct CFDTypeTraits<volVectorField> {
    static constexpr bool IsField = true;
    static constexpr int Rank = 1;
    using FieldType = volVectorField;
    using ValueType = vector;
};

// Generic field processor with type traits
template<typename T>
class FieldProcessor {
public:
    void process(T& field) {
        if constexpr (CFDTypeTraits<T>::IsField) {
            processField(field);
        } else {
            processScalar(field);
        }
    }

private:
    void processField(T& field) {
        // Field-specific processing
        for (auto& value : field) {
            value = applyBoundaryConditions(value);
        }
    }

    void processScalar(scalar& value) {
        // Scalar processing
        value = applyBoundaryConditions(value);
    }

    template<typename ValueType>
    ValueType applyBoundaryConditions(ValueType value) {
        // Apply boundary conditions
        if (value < 0) value = 0;
        if (value > 1e6) value = 1e6;
        return value;
    }
};
```

## Advanced Template Patterns for CFD

### Curiously Recurring Template Pattern (CRTP)

```cpp
// Base class for field operations
template<typename Derived>
class FieldOperationsBase {
public:
    Derived& derived() { return static_cast<Derived&>(*this); }
    const Derived& derived() const { return static_cast<const Derived&>(*this); }

    // Common field operations
    scalar max() const {
        scalar maxVal = -std::numeric_limits<scalar>::max();
        for (const auto& val : derived()) {
            maxVal = max(maxVal, val);
        }
        return maxVal;
    }

    scalar min() const {
        scalar minVal = std::numeric_limits<scalar>::max();
        for (const auto& val : derived()) {
            minVal = min(minVal, val);
        }
        return minVal;
    }
};

// Vol field with CRTP
template<typename Type>
class VolFieldCRTP : public FieldOperationsBase<VolFieldCRTP<Type>> {
private:
    Type* data_;
    label size_;

public:
    VolFieldCRTP(label size) : size_(size), data_(new Type[size]) {}

    Type& operator[](label i) { return data_[i]; }
    const Type& operator[](label i) const { return data_[i]; }

    // Iterator support
    Type* begin() { return data_; }
    Type* end() { return data_ + size_; }
    const Type* begin() const { return data_; }
    const Type* end() const { return data_ + size_; }

    size_t size() const { return size_; }
};

// Usage
using ScalarField = VolFieldCRTP<scalar>;
using VectorField = VolFieldCRTP<vector>;

// Field solver using CRTP
template<typename Field>
class FieldSolverCRTP : public FieldOperationsBase<FieldSolverCRTP<Field>> {
public:
    void solve(Field& field, const Field& source) {
        // Use CRTP for static polymorphism
        field = this->solveInternal(field, source);
    }

private:
    Field solveInternal(Field& field, const Field& source) {
        // Specific solver implementation
        Field result(field.size());
        for (size_t i = 0; i < field.size(); ++i) {
            result[i] = (source[i] + field[i]) / 2.0;
        }
        return result;
    }
};
```

### Variadic Templates for Multi-Field Operations

```cpp
// Variadic template for multiple field operations
template<typename... FieldTypes>
class MultiFieldOperator {
public:
    // Sum multiple fields
    template<typename... Fields>
    static auto sum(const Fields&... fields) {
        using ResultType = std::common_type_t<typename Fields::value_type...>;
        MultiField<ResultType> result(fields.front().size());

        for (size_t i = 0; i < result.size(); ++i) {
            result[i] = (fields[i] + ...);
        }

        return result;
    }

    // Weighted average of multiple fields
    template<typename... Fields, typename... Weights>
    static auto weightedAverage(const std::tuple<Fields...>& fields,
                               const std::tuple<Weights...>& weights) {
        using ResultType = std::common_type_t<typename Fields::value_type...>;
        MultiField<ResultType> result(std::get<0>(fields).size());

        for (size_t i = 0; i < result.size(); ++i) {
            result[i] = (std::get<0>(fields)[i] * std::get<0>(weights) + ...);
        }

        return result;
    }
};

// Usage
auto pressureField = getPressureField();
auto velocityField = getVelocityField();
auto temperatureField = getTemperatureField();

// Sum multiple fields
auto totalField = MultiFieldOperator::sum(pressureField, velocityField, temperatureField);

// Weighted average
auto weights = std::make_tuple(0.3, 0.5, 0.2);
auto averagedField = MultiFieldOperator::weightedAverage(
    std::make_tuple(pressureField, velocityField, temperatureField),
    weights
);
```

## Template Performance Optimization

### Compile-Time Optimization

```cpp
// Compile-time field size constants
template<int N>
class OptimizedField {
private:
    std::array<scalar, N> data_;

public:
    // Compile-time known size enables optimizations
    static constexpr int Size = N;

    // Optimized operations
    scalar dotProduct(const OptimizedField& other) const {
        scalar result = 0;
        for (int i = 0; i < N; ++i) {
            result += data_[i] * other[i];
        }
        return result;
    }

    // Loop unrolling hint
    void add(const OptimizedField& other) {
        #pragma omp simd
        for (int i = 0; i < N; ++i) {
            data_[i] += other[i];
        }
    }
};

// Template specialization for common sizes
template<>
class OptimizedField<3> {
private:
    scalar data_[3];

public:
    // Specialized operations for 3D vectors
    scalar magnitude() const {
        return std::sqrt(data_[0]*data_[0] + data_[1]*data_[1] + data_[2]*data_[2]);
    }

    vector toVector() const {
        return vector(data_[0], data_[1], data_[2]);
    }
};
```

### Type Erasure for Flexible Field Handling

```cpp
// Type-erased field interface
class AnyField {
private:
    struct FieldConcept {
        virtual ~FieldConcept() = default;
        virtual scalar average() const = 0;
        virtual scalar max() const = 0;
        virtual scalar min() const = 0;
    };

    template<typename Field>
    struct FieldModel : FieldConcept {
        Field field;

        FieldModel(Field f) : field(std::move(f)) {}

        scalar average() const override { return averageField(field); }
        scalar max() const override { return field.max(); }
        scalar min() const override { return field.min(); }
    };

    std::unique_ptr<FieldConcept> model_;

public:
    template<typename Field>
    AnyField(Field field) : model_(std::make_unique<FieldModel<Field>>(std::move(field))) {}

    scalar average() const { return model_->average(); }
    scalar max() const { return model_->max(); }
    scalar min() const { return model_->min(); }
};

// Usage with different field types
void processFields(const std::vector<AnyField>& fields) {
    for (const auto& field : fields) {
        Info << "Field average: " << field.average()
             << ", max: " << field.max()
             << ", min: " << field.min() << endl;
    }

    // Can handle different field types polymorphically
    auto scalarField = VolField<scalar>(100);
    auto vectorField = VolField<vector>(100);

    std::vector<AnyField> fields;
    fields.push_back(scalarField);
    fields.push_back(vectorField);

    processFields(fields);
}
```

## Summary

C++ templates provide powerful tools for building generic CFD components:

1. **Template Classes**: Create reusable field types with different data types
2. **Template Specialization**: Optimize specific implementations for common cases
3. **C++20 Concepts**: Enforce type safety and document interface requirements
4. **Template Metaprogramming**: Perform computations at compile time
5. **CRTP**: Achieve static polymorphism for performance-critical code

When using templates in CFD applications:
- Use concepts to document and enforce interface requirements
- Specialize for common cases to improve performance
- Be aware of compilation time and code bloat
- Use type traits for compile-time type information
- Consider type erasure for flexible interfaces

The examples demonstrate how templates enable writing generic, type-safe CFD code while maintaining performance and flexibility.