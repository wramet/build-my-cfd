# Design Patterns with Templates

Design Patterns ที่ใช้ Templates

---

## Learning Objectives

**What** You Will Learn:
- Template-based design patterns used in OpenFOAM
- Policy-based design for configurable behavior
- CRTP for static polymorphism
- Type traits for compile-time type introspection
- Mixin classes for adding capabilities
- Expression templates for performance optimization

**Why** It Matters:
- Templates enable compile-time polymorphism without runtime overhead
- Design patterns provide reusable solutions to common CFD programming problems
- Understanding these patterns helps you read and extend OpenFOAM source code
- Proper pattern selection improves performance, maintainability, and flexibility

**How** You Will Apply This:
- Recognize when to use each pattern in your own code
- Implement policy-based classes for solver customization
- Use CRTP to avoid virtual function overhead in performance-critical code
- Leverage type traits for generic programming
- Apply expression templates to optimize field operations

**Mastery Level:**
- ⭐⭐ **Intermediate** - Requires solid template syntax knowledge
- Essential for advanced OpenFOAM library development

---

## Overview

> **Templates enable compile-time polymorphism patterns** that provide zero-overhead abstraction while maintaining code flexibility and reusability.

Design patterns in template programming offer structured approaches to solving common problems. Unlike runtime polymorphism (virtual functions), template-based patterns resolve all decisions at compile-time, resulting in:
- **Zero runtime overhead** - No virtual function calls or indirect jumps
- **Better inlining** - Compiler sees complete code structure
- **Type safety** - Errors caught during compilation
- **Code reuse** - Generic algorithms work with multiple types

**Key Patterns Covered:**
1. Policy-Based Design - Compose behavior from interchangeable policies
2. CRTP - Enable static polymorphism with compile-time binding
3. Type Traits - Query and manipulate type properties at compile-time
4. Mixins - Add orthogonal capabilities to existing classes
5. Expression Templates - Build lazy evaluation chains for performance

---

## 1. Policy-Based Design

**Concept:** Decompose complex classes into independent, interchangeable "policy" classes that control specific aspects of behavior. Policies are template parameters, enabling compile-time configuration.

### What It Does

Policy-based design separates concerns into small, focused policy classes that can be mixed and matched. Unlike inheritance, policies are composable at compile-time without virtual function overhead.

### Why Use It

- **Flexibility:** Configure behavior by selecting different policy combinations
- **Performance:** All policy calls are inlined, no virtual dispatch
- **Type safety:** Policy compatibility checked at compile-time
- **Reusability:** Individual policies can be reused across different contexts

### How It Works

```cpp
// Policy interfaces
struct ExplicitPolicy
{
    static word typeName() { return "explicit"; }
    
    template<class T>
    void update(T& field)
    {
        // Explicit time integration
        field = field.oldTime() + dt*fvc::ddt(field);
    }
};

struct ImplicitPolicy
{
    static word typeName() { return "implicit"; }
    
    template<class T>
    void update(T& field)
    {
        // Implicit time integration
        solve(fvm::ddt(field) == fvc::div(phi));
    }
};

struct NoLimiterPolicy
{
    template<class T>
    void limit(T& field) {}
};

struct VanLeerLimiterPolicy
{
    template<class T>
    void limit(T& field)
    {
        // Apply Van Leer flux limiter
        limitField(field, vanLeerLimiter);
    }
};

// Policy-based class
template<class TimePolicy, class LimiterPolicy>
class ConvectionScheme
{
    TimePolicy timeIntegrator_;
    LimiterPolicy limiter_;

public:
    void solve(volScalarField& T)
    {
        // Apply limiter if needed
        limiter_.limit(T);
        
        // Update with selected time policy
        timeIntegrator_.update(T);
    }
    
    word type() const
    {
        return TimePolicy::typeName();
    }
};

// Usage: Different configurations
ConvectionScheme<ImplicitPolicy, NoLimiterPolicy> implicitSolver;
ConvectionScheme<ExplicitPolicy, VanLeerLimiterPolicy> explicitLimiter;
```

### OpenFOAM Example: fvMesh

OpenFOAM's finite volume mesh uses policy-based design for solver configuration:

```cpp
// Simplified OpenFOAM linear solver configuration
template<class SolverPolicy, class PreconditionerPolicy>
class LUsolver
{
    SolverPolicy solver_;
    PreconditionerPolicy precond_;

public:
    void solve(fvScalarMatrix& matrix, scalarField& psi)
    {
        // Preconditioner applied first
        precond_.precondition(matrix);
        
        // Then solver
        solver_.solve(matrix, psi);
    }
};

// Common OpenFOAM solvers
LUsolver<CGSolver, DICPreconditioner> cgSolver;      // Conjugate Gradient
LUsolver<BICCGSolver, DILUPreconditioner> biccgSolver; // BiCGStab
LUsolver<GAMGSolver, nonePreconditioner> gamgSolver;  // Geometric-Algebraic Multi-Grid
```

---

## 2. CRTP (Curiously Recurring Template Pattern)

**Concept:** A derived class passes itself as a template parameter to its base class, enabling compile-time polymorphism without virtual functions.

### What It Does

CRTP enables the base class to call methods from the derived class at compile-time. The pattern "curiously recurses" because the derived class inherits from a base templated on itself.

### Why Use It

- **Static polymorphism:** Avoid virtual function call overhead
- **Type preservation:** Return derived type from base methods
- **Code reuse:** Common functionality in base, specialized in derived
- **Perfect forwarding:** Enable method chaining with correct types

### How It Works

```cpp
// CRTP Base class
template<class Derived>
class CloudFunctionObject
{
public:
    // Base class calls derived method
    void execute()
    {
        // Static cast to derived type
        auto& derived = static_cast<Derived&>(*this);
        derived.executeImpl();
    }
    
    // Enable method chaining with correct return type
    Derived& setOutput(bool output)
    {
        output_ = output;
        return static_cast<Derived&>(*this);
    }
    
protected:
    bool output_ = false;
};

// Derived class
class ParticleCollector : public CloudFunctionObject<ParticleCollector>
{
public:
    void executeImpl()
    {
        Info << "Collecting particles..." << endl;
        // Actual collection logic
    }
    
    // Returns ParticleCollector&, not CloudFunctionObject&
    ParticleCollector& setTime(scalar t)
    {
        time_ = t;
        return *this;
    }

private:
    scalar time_;
};

// Usage - method chaining works correctly
ParticleCollector collector;
collector.setOutput(true).setTime(0.5).execute();
```

### OpenFOAM Example: KinematicCloud

OpenFOAM extensively uses CRTP for Lagrangian particle clouds:

```cpp
// OpenFOAM source (simplified)
template<class CloudType>
class KinematicCloud : public Cloud<KinematicCloud<CloudType>>
{
public:
    // CloudType is the actual cloud type (e.g., MoleculeCloud)
    // This enables static polymorphism across cloud types
    
    void evolve()
    {
        // Template methods called without virtual dispatch
        this->preEvolve();
        this->motion();
        this->postEvolve();
    }
};

// Concrete cloud
class MoleculeCloud : public KinematicCloud<MoleculeCloud>
{
    // Inherits all KinematicCloud functionality
    // Can override specific methods if needed
};
```

---

## 3. Type Traits

**Concept:** Compile-time templates that provide information about types, enabling conditional compilation and type-based optimizations.

### What It Does

Type traits allow you to query type properties (is scalar? is pointer? has certain methods?) and perform type transformations (remove reference, add const, etc.) at compile-time.

### Why Use It

- **Type introspection:** Make decisions based on type properties
- **Code optimization:** Specialize code for specific types
- **Type safety:** Provide better error messages
- **Generic programming:** Write algorithms that work with many types

### How It Works

```cpp
// Custom type traits for OpenFOAM
template<class Type>
struct IsScalarField
{
    static const bool value = false;
};

template<>
struct IsScalarField<volScalarField>
{
    static const bool value = true;
};

template<>
struct IsScalarField<surfaceScalarField>
{
    static const bool value = true;
};

// Function using type traits
template<class FieldType>
void processField(const FieldType& field)
{
    if constexpr (IsScalarField<FieldType>::value)
    {
        Info << "Processing scalar field: " << field.name() << endl;
        // Scalar-specific optimizations
    }
    else
    {
        Info << "Processing vector/tensor field" << endl;
        // Vector/tensor handling
    }
}

// Type trait for dimension checking
template<class T1, class T2>
struct AreDimensionsCompatible
{
    static const bool value = 
        std::is_same<typename T1::dimType, typename T2::dimType>::value;
};

// Compile-time assertion
template<class T1, class T2>
void addFields(const T1& f1, const T2& f2)
{
    static_assert(
        AreDimensionsCompatible<T1, T2>::value,
        "Field dimensions must match"
    );
    
    tmp<GeometricField<typename outerProduct<typename T1::value_type, 
                                           typename T2::value_type>::type, 
                     fvPatchField, volMesh>> result;
    
    // Actual addition
    // ...
}
```

### OpenFOAM Example: pTraits

OpenFOAM uses type traits extensively for field operations:

```cpp
// OpenFOAM's pTraits (primitive traits)
template<class T>
class pTraits
{
public:
    typedef T cmptType;
    
    static const T zero;
    static const T one;
    static const T max;
    static const T min;
    static const T rootMax;
    static const T rootMin;
};

// Specializations for different types
template<>
class pTraits<scalar>
{
public:
    typedef scalar cmptType;
    static const scalar zero;
    static const scalar one;
    // ...
};

template<>
class pTraits<vector>
{
public:
    typedef scalar cmptType;
    static const vector zero;
    static const vector one;
    // ...
};
```

---

## 4. Mixins

**Concept:** Thin template classes that add orthogonal capabilities to existing classes through inheritance. Mixins provide optional features that can be combined as needed.

### What It Does

Mixins allow you to add capabilities (logging, serialization, printing, etc.) to classes without modifying the original class hierarchy. Multiple mixins can be combined.

### Why Use It

- **Code reuse:** Share common capabilities across unrelated classes
- **Composition over inheritance:** Avoid deep inheritance hierarchies
- **Optional features:** Add capabilities only when needed
- **Separation of concerns:** Keep core functionality separate from auxiliary features

### How It Works

```cpp
// Mixin: Add file I/O capability
template<class Base>
class Serializable : public Base
{
public:
    void write(const fileName& path) const
    {
        OFstream os(path);
        const Base& base = static_cast<const Base&>(*this);
        base.writeData(os);
    }
    
    void read(const fileName& path)
    {
        IFstream is(path);
        Base& base = static_cast<Base&>(*this);
        base.readData(is);
    }
};

// Mixin: Add runtime selection capability
template<class Base>
class Runnable : public Base
{
    word typeName_;

public:
    Runnable(const word& type) : typeName_(type) {}
    
    word type() const { return typeName_; }
    
    void run()
    {
        Info << "Running " << typeName_ << endl;
        static_cast<Base*>(this)->execute();
    }
};

// Mixin: Add timing capability
template<class Base>
class Timed : public Base
{
    clock_t startTime_;
    
public:
    void start()
    {
        startTime_ = std::clock();
    }
    
    scalar elapsed() const
    {
        return scalar(std::clock() - startTime_) / CLOCKS_PER_SEC;
    }
};

// Combine multiple mixins
class BasicSolver
{
public:
    void execute() { Info << "Solving..." << endl; }
    void writeData(Ostream& os) const { os << "Solver data"; }
};

// Mixin composition
class MySolver : public Serializable<Runnable<BasicSolver>>
{
    // Inherits Serializable and Runnable capabilities
};

// Usage
MySolver solver("mySolver");
solver.run();
solver.write("solver.dat");

// Add timing to an existing solver
class TimedSolver : public Timed<MySolver>
{
    // Adds timing capability to MySolver
};
```

### OpenFOAM Example: boundaryCondition Mixins

Many OpenFOAM boundary conditions use mixins to add optional capabilities:

```cpp
// Mixin for fixed value support
template<class Type>
class FixedValueMixin
{
    Field<Type> fixedValue_;
    
public:
    const Field<Type>& fixedValue() const { return fixedValue_; }
    void fixedValue(const Field<Type>& f) { fixedValue_ = f; }
};

// Mixin for gradient support
template<class Type>
class GradientMixin
{
    Field<Field<Type>> gradient_;
    
public:
    const Field<Field<Type>>& gradient() const { return gradient_; }
};

// Boundary condition using mixins
template<class Type>
class MixedBC 
: public FixedValueMixin<Type>, 
  public GradientMixin<Type>
{
    // Can use both fixed value and gradient
};
```

---

## 5. Expression Templates

**Concept:** Build expression trees as template types, enabling lazy evaluation and optimization of compound expressions. Avoid temporary objects in mathematical operations.

### What It Does

Expression templates represent computations as template types rather than immediately computing results. When the final value is needed, the entire expression tree is optimized and computed in a single pass.

### Why Use It

- **Eliminate temporaries:** Avoid creating intermediate objects in `a + b + c`
- **Loop fusion:** Combine multiple operations into single loop
- **Automatic optimization:** Compiler can optimize entire expression
- **Maintain readability:** Write natural mathematical expressions

### How It Works

```cpp
// Expression template base
template<class Derived>
class FieldExpr
{
public:
    // Access derived type
    const Derived& derived() const 
    { 
        return static_cast<const Derived&>(*this); 
    }
    
    // Evaluate expression at index i
    auto operator[](label i) const
    {
        return derived()[i];
    }
};

// Concrete field
class ScalarField : public FieldExpr<ScalarField>
{
    const scalarField& data_;
    
public:
    ScalarField(const scalarField& data) : data_(data) {}
    
    auto operator[](label i) const { return data_[i]; }
    
    label size() const { return data_.size(); }
};

// Addition expression
template<class E1, class E2>
class AddExpr : public FieldExpr<AddExpr<E1, E2>>
{
    const E1& e1_;
    const E2& e2_;
    
public:
    AddExpr(const FieldExpr<E1>& e1, const FieldExpr<E2>& e2) 
    : e1_(e1.derived()), e2_(e2.derived()) {}
    
    auto operator[](label i) const 
    { 
        return e1_[i] + e2_[i]; 
    }
};

// Multiplication expression
template<class E1, class E2>
class MulExpr : public FieldExpr<MulExpr<E1, E2>>
{
    const E1& e1_;
    const E2& e2_;
    
public:
    MulExpr(const FieldExpr<E1>& e1, const FieldExpr<E2>& e2) 
    : e1_(e1.derived()), e2_(e2.derived()) {}
    
    auto operator[](label i) const 
    { 
        return e1_[i] * e2_[i]; 
    }
};

// Operator overloads for expression building
template<class E1, class E2>
AddExpr<E1, E2> operator+(const FieldExpr<E1>& e1, const FieldExpr<E2>& e2)
{
    return AddExpr<E1, E2>(e1, e2);
}

template<class E1, class E2>
MulExpr<E1, E2> operator*(const FieldExpr<E1>& e1, const FieldExpr<E2>& e2)
{
    return MulExpr<E1, E2>(e1, e2);
}

// Usage - no temporaries created!
void computeTemperature()
{
    volScalarField T = ...; // Initial field
    volScalarField p = ...;
    volScalarField rho = ...;
    
    // Expression tree built, not computed yet
    auto expr = ScalarField(T) * ScalarField(p) / ScalarField(rho);
    
    // Single loop when finally evaluated
    scalarField result(T.size());
    forAll(result, i)
    {
        result[i] = expr[i]; // Entire expression computed here
    }
    // Equivalent to: result[i] = T[i] * p[i] / rho[i]
    // But done in ONE loop, no temporary arrays!
}
```

### Performance Comparison

```cpp
// WITHOUT expression templates (creates 3 temporaries)
tmp<volScalarField> result1 = T * p;       // Temporary 1
tmp<volScalarField> result2 = result1 / rho; // Temporary 2
// Final result assigned from temporary 2

// WITH expression templates (0 temporaries)
auto expr = T * p / rho;  // Just builds expression tree
volScalarField result = expr;  // Single evaluation, no temporaries
```

### OpenFOAM Example

OpenFOAM's field operations use expression templates internally:

```cpp
// OpenFOAM code (simplified)
tmp<volScalarField> rhoUEqn
(
    fvm::div(phi, U)  // Builds expression template
  + fvm::laplacian(turbulence->muEff(), U)  // More expressions
  - fvc::div(phi, turbulence->muEff()*dev2(fvc::grad(U)().T()))
);

// Expression tree is evaluated in optimized solve()
solve(rhoUEqn == -fvc::grad(p));
```

---

## Pattern Comparison Guide

| Pattern | Best Use Case | Pros | Cons | Performance |
|---------|--------------|------|------|-------------|
| **Policy-Based** | Configurable algorithms, solver selection | Compile-time flexibility, no v-table overhead | Template bloat, longer compile times | ⭐⭐⭐⭐⭐ Excellent (fully inlinable) |
| **CRTP** | Static polymorphism, base calling derived | Zero overhead, perfect forwarding | Verbose syntax, can be confusing | ⭐⭐⭐⭐⭐ Excellent (static binding) |
| **Type Traits** | Compile-time type decisions, optimizations | Type-safe, catches errors early | Complex syntax, limited to compile-time | ⭐⭐⭐⭐ Good (enables optimizations) |
| **Mixins** | Adding orthogonal capabilities, composition | Flexible, avoid deep inheritance | Name conflicts, multiple inheritance complexity | ⭐⭐⭐ Good (inlineable) |
| **Expression Templates** | Math operations, field algebra | Eliminates temporaries, automatic fusion | Complex implementation, slower compiles | ⭐⭐⭐⭐⭐ Excellent for complex expressions |

**When to Use Each:**

- **Use Policy-Based** when you need interchangeable behaviors at compile-time (solver schemes, discretization methods, boundary condition policies)
- **Use CRTP** when you want polymorphism without virtual functions (cloud functions, field operations with type-specific optimizations)
- **Use Type Traits** for conditional compilation based on type properties (scalar vs vector field optimizations, dimension checking)
- **Use Mixins** to add optional, independent features (serialization, logging, timing, debugging capabilities)
- **Use Expression Templates** for mathematical operations on large arrays (field algebra, matrix operations, tensor calculus)

---

## Key Takeaways

**Design Patterns with Templates**

1. **Compile-Time vs Runtime**
   - Template patterns resolve at compile-time → zero runtime overhead
   - Virtual functions resolve at runtime → flexibility but with cost
   - For CFD performance, compile-time patterns are preferred

2. **Pattern Selection**
   - **Policy-Based Design:** Use for configurable algorithms and solver selection. Best when behavior combinations are known at compile-time.
   - **CRTP:** Use for static polymorphism when virtual functions are too expensive. Common in OpenFOAM's cloud classes.
   - **Type Traits:** Use for type introspection and conditional compilation. Essential for generic field operations.
   - **Mixins:** Use to add orthogonal capabilities without deep inheritance. Combine multiple mixins for rich functionality.
   - **Expression Templates:** Use for optimizing mathematical operations on fields. Critical for performance in `fvMesh` operations.

3. **OpenFOAM Integration**
   - OpenFOAM uses these patterns extensively in `src/OpenFOAM/` and `src/finiteVolume/`
   - Understanding patterns helps navigate complex template code
   - Many OpenFOAM classes combine multiple patterns (e.g., policy + CRTP)

4. **Performance Impact**
   - Expression templates can eliminate 90%+ of temporary allocations in field operations
   - CRTP eliminates virtual function overhead (typically 5-10% performance gain)
   - Policy-based design enables aggressive compiler optimizations

5. **Trade-offs**
   - **Pros:** Zero runtime overhead, type safety, code reuse, compiler optimizations
   - **Cons:** Longer compile times, complex error messages, template bloat, steeper learning curve
   - **Rule of thumb:** Use template patterns in library code, simpler patterns in application code

6. **Best Practices**
   - Prefer composition (mixins, policies) over complex inheritance
   - Use `static_assert` with type traits for better error messages
   - Document template constraints clearly
   - Profile before optimizing with expression templates
   - Combine patterns judiciously - complexity can grow quickly

---

## 🧠 Concept Check

<details>
<summary><b>1. Policy-based design vs traditional inheritance?</b></summary>

**Policy-based design:**
- Compile-time selection of behaviors
- No virtual function overhead (fully inlinable)
- More flexible - policies can be combined in many ways
- Configuration happens at compile-time

**Traditional inheritance:**
- Runtime polymorphism via virtual functions
- Virtual dispatch overhead (indirect calls, harder to inline)
- Fixed hierarchy (hard to change at runtime)
- Configuration via virtual function calls

**Use policies** when behavior is known at compile-time and performance matters.
**Use inheritance** when you need runtime flexibility or have many implementations.

</details>

<details>
<summary><b>2. CRTP ดีอย่างไร? (Why is CRTP useful?)</b></summary>

**CRTP (Curiously Recurring Template Pattern)** provides:

1. **Static polymorphism** - No virtual call overhead
2. **Type preservation** - Methods return correct derived type (not base)
3. **Method chaining** - `derived.method1().method2()` works correctly
4. **Compile-time binding** - Compiler sees complete code for optimization

**Example benefit:**
```cpp
// Without CRTP - returns Base&, breaks chaining
Base* obj = new Derived();
obj->setX(1).setY(2); // Returns Base&, not Derived&

// With CRTP - returns Derived&, perfect chaining
Derived obj;
obj.setX(1).setY(2); // Returns Derived&, methods work correctly
```

**Performance:** 5-15% faster than virtual functions for tight loops in CFD calculations.

</details>

<details>
<summary><b>3. Type traits ใช้ทำอะไร? (What are type traits used for?)</b></summary>

**Type traits enable compile-time type introspection:**

1. **Query type properties:**
   - `IsScalarField<T>::value` - Is this a scalar field?
   - `std::is_pointer<T>::value` - Is this a pointer?
   - `std::is_const<T>::value` - Is this const?

2. **Type transformations:**
   - `std::remove_reference<T>::type` - Remove & from type
   - `std::add_const<T>::type` - Add const qualifier

3. **Conditional compilation:**
   ```cpp
   if constexpr (IsVectorField<T>::value) {
       // Vector-specific code
   } else {
       // Scalar-specific code
   }
   ```

4. **Better error messages:**
   ```cpp
   static_assert(IsFieldType<T>::value, 
       "Template argument must be a field type");
   ```

**OpenFOAM example:** `pTraits<T>` provides type-specific constants (zero, one, max, min) for all field types.

</details>

<details>
<summary><b>4. When should you use expression templates?</b></summary>

**Use expression templates when:**

✅ **DO use for:**
- Large array operations (fields with >10,000 elements)
- Compound expressions (`a + b * c / d`)
- Performance-critical loops (called frequently)
- Operations that would otherwise create many temporaries

❌ **DON'T use for:**
- Small arrays (<100 elements)
- Simple expressions (single operations)
- One-time calculations
- When compilation time is critical

**Performance impact:**
```cpp
// Without expression templates
auto temp1 = a * b;     // Allocates temporary array
auto temp2 = temp1 + c; // Allocates another temporary
result = temp2 / d;     // Final assignment

// With expression templates
result = a * b + c / d; // Single loop, zero temporaries
```

**For 100,000 element fields:** Expression templates can be 3-10x faster by eliminating memory allocations.

</details>

<details>
<summary><b>5. How do mixins differ from multiple inheritance?</b></summary>

**Mixins are a specific pattern using multiple inheritance:**

**Mixin characteristics:**
- Thin, focused classes that add ONE capability
- Template-based for flexibility (mix with any base)
- Orthogonal features (logging, serialization, timing)
- Don't modify core functionality

**Traditional multiple inheritance:**
- Can lead to diamond problem
- Tight coupling between classes
- Complex hierarchies

**Example:**
```cpp
// Mixin - adds one feature, template-based
template<class Base>
class Serializable : public Base {
    void write(const fileName& path);
};

// Use mixin to add serialization to any class
class MySolver : public Serializable<BasicSolver> {
    // Now MySolver can be serialized
};
```

**Key benefit:** Compose capabilities like building blocks rather than creating deep inheritance trees.

</details>

---

## 📖 Related Documentation

- **Overview:** [00_Overview.md](00_Overview.md)
- **Template Syntax:** [02_Template_Syntax.md](02_Template_Syntax.md)
- **Internal Mechanics:** [03_Internal_Mechanics.md](03_Internal_Mechanics.md)
- **Specialization:** [04_Specialization_and_Overloading.md](04_Specialization_and_Overloading.md)
- **Debugging:** [06_Common_Errors_and_Debugging.md](06_Common_Errors_and_Debugging.md)
- **Exercises:** [07_Advanced_Exercises.md](07_Advanced_Exercises.md)

---

## 🎯 Skills Checklist

After mastering this section, you should be able to:

- [ ] **Policy-Based Design**: Implement a policy class for solver configuration
- [ ] **CRTP**: Write a CRTP base class for static polymorphism
- [ ] **Type Traits**: Create and use custom type traits for type checking
- [ ] **Mixins**: Design mixin classes for adding optional capabilities
- [ ] **Expression Templates**: Build a simple expression template system
- [ ] **Pattern Selection**: Choose the appropriate pattern for a given problem
- [ ] **Performance Analysis**: Measure performance gains from template patterns
- [ ] **OpenFOAM Patterns**: Identify template patterns in OpenFOAM source code

**Next Steps:** Practice implementing these patterns in [07_Advanced_Exercises.md](07_Advanced_Exercises.md), then see debugging techniques in [06_Common_Errors_and_Debugging.md](06_Common_Errors_and_Debugging.md).