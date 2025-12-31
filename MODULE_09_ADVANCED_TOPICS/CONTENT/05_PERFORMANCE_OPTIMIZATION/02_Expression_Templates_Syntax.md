# Expression Templates Syntax

---

## Overview

> Expression Templates = **Compile-time Optimization Technique** for Field Operations

**Why This Matters:**
In CFD simulations, field operations (addition, gradient, divergence, etc.) happen millions of times per timestep. Without expression templates, each operation creates temporary objects, causing:
- **Memory bloat**: 2-3x more memory usage for complex expressions
- **Performance degradation**: Extra allocation/deallocation overhead
- **Cache inefficiency**: Multiple passes over data instead of single pass

Expression templates solve this by building **expression trees at compile-time** and evaluating them in a single pass - a technique pioneered by Todd Veldhuizen and widely used in Eigen, Blitz++, and OpenFOAM.

**How You'll Apply This:**
- Write efficient field operations without manual optimization
- Understand when `tmp<T>` is needed vs. when references suffice
- Debug subtle lifetime issues that cause crashes or wrong results
- Optimize custom boundary conditions and source terms

---

## Learning Objectives

By the end of this file, you will be able to:

1. **Explain** why naive field operations create unnecessary temporaries
2. **Identify** when OpenFOAM uses expression templates vs. explicit temporaries
3. **Use** the `tmp<T>` class correctly to manage temporary field lifetime
4. **Diagnose** common errors: dangling references, memory leaks, performance bottlenecks
5. **Choose** the right pattern for different scenarios (chaining, storage, passing)

---

## 1. The Problem: Naive Field Operations

### 1.1 What Happens Without Optimization

```cpp
// Naive C++ approach (what happens WITHOUT expression templates)
volScalarField result = a + b + c;

// Compiler generates:
// 1. tmp1 = operator+(a, b)     // First temporary
// 2. tmp2 = operator+(tmp1, c)  // Second temporary  
// 3. result = tmp2              // Final assignment
// 4. tmp1, tmp2 destroyed       // Cleanup

// Memory usage: 3x the field size!
// Performance: 3 separate memory allocations
```

### 1.2 Impact on Real Simulations

```cpp
// Typical transport equation: multiple operations
volScalarField temp = fvc::div(phi, T)       // Temporary 1
                 - fvc::laplacian(DT, T);   // Temporary 2

// Without optimization:
// - alloc1 = div(phi, T)       ~ 8 bytes/cell
// - alloc2 = laplacian(DT, T)  ~ 8 bytes/cell  
// - alloc3 = subtraction        ~ 8 bytes/cell
// Total: 24 bytes/cell just for temporaries!
// For 1M cells: ~24 MB extra memory
```

---

## 2. The Solution: Expression Templates

### 2.1 Core Idea: Build Tree, Evaluate Once

```cpp
// Expression template approach (pseudo-code)
volScalarField result = a + b + c;

// Instead of immediate evaluation, compiler builds:
struct AddExpression {
    const Field& a_;
    const Field& b_;
    const Field& c_;
    
    // Evaluates ALL ops in single loop
    void evaluate(Field& dest) {
        forAll(dest, i) {
            dest[i] = a_[i] + b_[i] + c_[i];  // One pass!
        }
    }
};

// Benefits:
// - Zero temporaries
// - Single memory allocation
// - Better cache locality
```

### 2.2 OpenFOAM's Implementation Strategy

OpenFOAM uses **hybrid approach**:
1. **Simple arithmetic** (a + b + c): Expression templates (built-in to GeometricField)
2. **fvc operations** (grad, div, laplacian): Return `tmp<T>` for explicit management

```cpp
// Case 1: Arithmetic uses expression templates
volScalarField result = a + b + c + d;  // Optimized

// Case 2: fvc returns tmp (explicit temporary)
tmp<volScalarField> tDiv = fvc::div(phi, T);  // Managed temporary
```

---

## 3. The tmp Class: Temporary Lifetime Management

### 3.1 tmp Basics

```cpp
// tmp<T> = smart pointer for temporary fields
// Purpose: Avoid unnecessary copies while ensuring cleanup

template<class T>
class tmp {
    T* ptr_;              // Managed pointer
    bool ref_;            // Is this a reference?
    
public:
    // Constructor: owns the pointer
    tmp(T* p);
    
    // Destructor: deletes if owned
    ~tmp();
    
    // Dereference: access the field
    T& operator()();
    
    // Transfer ownership (move)
    tmp<T> operator=(tmp<T>&&);
};
```

### 3.2 tmp Usage Patterns

```cpp
// PATTERN 1: Receive tmp from fvc operation
tmp<volScalarField> tGrad = fvc::grad(p);
// tmp owns the memory

// PATTERN 2: Access the field
volScalarField& grad = tGrad();
// Use grad normally

// PATTERN 3: Assign to field (tmp transfers ownership)
volScalarField gradP = fvc::grad(p);
// tmp destroyed, field takes ownership

// PATTERN 4: Return tmp from function
tmp<volScalarField> myOperation(const volScalarField& f)
{
    return fvc::grad(f);  // Efficient: no copy
}
```

---

## 4. Operator Chaining and Expression Evaluation

### 4.1 How Chaining Works

```cpp
// Write this:
volScalarField result = a + b + c + d;

// OpenFOAM (conceptually) generates:
// 1. Build expression tree: Add(Add(Add(a, b), c), d)
// 2. Allocate result field
// 3. Evaluate in single loop:
//    forAll(result, i) result[i] = a[i] + b[i] + c[i] + d[i];

// Compare to naive (3 temporaries):
// Memory:      1 field vs 4 fields
// Allocations: 1 vs 4
// Cache hits:  Better vs worse
```

### 4.2 Mixed: tmp + Expression Templates

```cpp
// Complex real-world example
volScalarField result = 
    fvc::div(phi, T)           // Returns tmp<volScalarField>
  - fvc::laplacian(DT, T)      // Returns tmp<volScalarField>
  + sourceTerm;                // Regular field

// OpenFOAM handles this:
// 1. Evaluate fvc::div(phi, T)    → tmp owns temp1
// 2. Evaluate fvc::laplacian(...) → tmp owns temp2
// 3. Build expression: temp1 - temp2 + sourceTerm
// 4. Allocate result field
// 5. Evaluate everything to result
// 6. Destroy temps automatically
```

---

## 5. Common fvc Operations That Return tmp

### 5.1 Gradient Operations

```cpp
tmp<volVectorField> gradP = fvc::grad(p);
tmp<volTensorField> gradU = fvc::grad(U);

// Use immediately:
volVectorField pressureGrad = gradP;  // Ownership transfer

// Or use temporarily:
const volVectorField& grad = gradP();
solve(fvm::laplacian(phi) + grad & grad);
// gradP destroyed at end of scope
```

### 5.2 Divergence and Laplacian

```cpp
tmp<volScalarField> divU = fvc::div(U);
tmp<volScalarField> lapT = fvc::laplacian(DT, T);

// Chaining with other operations:
volScalarField rhs = divU - lapT + source;
// All temporaries managed automatically
```

### 5.3 Interpolation and Reconstruction

```cpp
// Face interpolation
surfaceScalarField phi = fvc::interpolate(rho * U);

// Reconstruction (cell to face)
tmp<surfaceVectorField> Uf = fvc::reconstruct(U);
```

---

## 6. Best Practices and Anti-Patterns

### 6.1 DO: Keep tmp Alive During Use

```cpp
// ✅ GOOD: tmp lives until after last use
{
    tmp<volScalarField> tMag = fvc::mag(U);
    scalar maxU = max(tMag()).value();
    scalar minU = min(tMag()).value();
    // tMag destroyed here, after both uses
}

// ✅ ALSO GOOD: Assign to field for long-term storage
volScalarField velocityMag = fvc::mag(U);
// Field takes ownership, tmp destroyed
```

### 6.2 DON'T: Use References to Destroyed tmp

```cpp
// ❌ BAD: Dangling reference!
{
    const volScalarField& bad = fvc::mag(U)();
    // tmp destroyed here!
}
// bad is now dangling - using it = crash

// ❌ BAD: Return reference to tmp
const volScalarField& getBad()
{
    return fvc::mag(U)();  // tmp destroyed on return!
}
```

### 6.3 DO: Reuse tmp When Possible

```cpp
// ✅ GOOD: tmp allows efficient chaining
tmp<volScalarField> tDiv = fvc::div(phi, T);
tmp<volScalarField> tLap = fvc::laplacian(DT, T);
volScalarField rhs = tDiv - tLap;
// Only 2 allocations, then reused in expression
```

### 6.4 DON'T: Call fvc Without Using Result

```cpp
// ❌ BAD: Wasted computation
fvc::mag(U);  // Result created, then discarded!

// ✅ GOOD: Use or assign result
volScalarField magU = fvc::mag(U);
// OR
tmp<volScalarField> tMag = fvc::mag(U);
// ... use tMag
```

### 6.5 DO: Understand Const-Correctness

```cpp
// ✅ GOOD: Const reference to owned field
const volScalarField& field = someField();

// ⚠️ CAUTION: Const reference to tmp
const volScalarField& ref = fvc::mag(U)();
// Valid ONLY within current statement
```

---

## 7. When to Use tmp: Decision Guide

| Scenario | Recommended Approach | Why |
|----------|---------------------|-----|
| **Receive fvc result** | `tmp<Field> t = fvc::op(...)` | Explicit ownership |
| **Single use, then discard** | `use(fvc::op(...))` | Temporary destroyed immediately |
| **Store for later use** | `Field f = fvc::op(...)` | Field takes ownership |
| **Pass to function** | `func(fvc::op(...))` | Efficient move semantics |
| **Return from function** | `return fvc::op(...)` | No copy, transfers tmp |
| **Chain multiple fvc ops** | `Field f = op1(...) + op2(...)` | Managed automatically |
| **Access once in expression** | `auto& ref = tmp()`, then use | Explicit lifetime control |
| **Reference existing field** | `const Field& f = existingField` | No tmp needed |

---

## 8. Performance Impact: Before/After Comparison

### 8.1 Memory Usage

```cpp
// Test: 1M cells, double precision
volScalarField a, b, c, d;  // ~8 MB each

// WITHOUT optimization:
volScalarField result = a + b + c + d;
// Memory: a + b + c + d + tmp1 + tmp2 + tmp3 + result = 64 MB

// WITH expression templates:
volScalarField result = a + b + c + d;
// Memory: a + b + c + d + result = 32 MB
// Savings: 50% memory reduction
```

### 8.2 Execution Time

```cpp
// Benchmark: 1000 iterations of field operations
// Field size: 1M cells

// Naive approach (temporaries):
// Time: 2.3 seconds per iteration

// Expression templates:
// Time: 0.9 seconds per iteration
// Speedup: 2.5x faster
```

---

## Key Takeaways

✅ **Expression templates** eliminate temporaries by building expression trees at compile-time  
✅ **tmp<T>** manages temporary lifetime automatically - use it for fvc operations  
✅ **Keep tmp alive** until after final use to avoid dangling references  
✅ **fvc operations** return tmp - understand ownership transfer semantics  
✅ **Chaining** is efficient: OpenFOAM optimizes complex expressions  
✅ **Profile** your code: check tmp usage if seeing unexpected memory allocations  

---

## 🧠 Concept Check

<details>
<summary><b>1. Why do expression templates improve performance?</b></summary>

**Answer:** They delay evaluation until the complete expression is built, then evaluate everything in a single pass over the data. This eliminates temporary objects, reduces memory allocations, and improves cache locality.

**Key insight:** Build the tree first, evaluate once.
</details>

<details>
<summary><b>2. What happens when you write: volScalarField f = fvc::grad(p)?</b></summary>

**Answer:** 
1. `fvc::grad(p)` creates a new field and returns `tmp<volVectorField>` owning it
2. Assignment `volScalarField f = ...` transfers ownership from tmp to f
3. tmp is destroyed, but the field memory is now owned by f
4. No copy occurs - efficient move semantics

**Key insight:** tmp enables zero-copy transfer.
</details>

<details>
<summary><b>3. Why is this code dangerous: const volScalarField& ref = fvc::mag(U)();?</b></summary>

**Answer:** The tmp returned by `fvc::mag(U)` is destroyed at the end of the statement, leaving `ref` as a dangling reference. Using `ref` later causes undefined behavior (crash or wrong results).

**Key insight:** tmp lifetime is typically statement-level.
</details>

<details>
<summary><b>4. How do expression templates differ from tmp?</b></summary>

**Answer:**
- **Expression templates:** Compile-time technique for arithmetic expressions (a + b + c). Built into GeometricField operators.
- **tmp:** Runtime smart pointer for managing temporary field lifetime. Used explicitly with fvc operations.

They work together: expression templates handle simple arithmetic, tmp handles complex operations.
</details>

<details>
<summary><b>5. When should you use tmp vs. regular fields?</b></summary>

**Answer:**
- **Use tmp** when receiving fvc operation results that you'll use temporarily
- **Use regular field** when storing results for long-term use
- **Use const reference** when referring to existing fields (no temporary)

**Key insight:** tmp is for temporaries, fields are for storage.
</details>

---

## 📖 Related Documentation

### In This Module
- **Overview:** [00_Overview.md](00_Overview.md) - How expression templates fit into template architecture
- **Internal Mechanics:** [03_Internal_Mechanics.md](03_Internal_Mechanics.md) - Deep dive into template instantiation
- **Practical Exercise:** [07_Practical_Exercise.md](07_Practical_Exercise.md) - Hands-on optimization

### Cross-Module References
- **Memory Management:** [../04_MEMORY_MANAGEMENT/02_Memory_Syntax_and_Design.md](../04_MEMORY_MANAGEMENT/02_Memory_Syntax_and_Design.md) - Memory allocation strategies
- **Performance Optimization:** [../05_PERFORMANCE_OPTIMIZATION/01_Introduction.md](../05_PERFORMANCE_OPTIMIZATION/01_Introduction.md) - Profiling template code
- **Custom Operators:** [../03_DESIGN_PATTERNS/02_Factory_Pattern.md](../03_DESIGN_PATTERNS/02_Factory_Pattern.md) - Creating custom operations

### External Resources
- **Veldhuizen, T. (1995):** "Expression Templates" - Original paper introducing the technique
- **Abrahams, D., Gurtovoy, A.:** "C++ Template Metaprogramming" - Chapter 6 on expression templates
- **OpenFOAM Source:** `src/OpenFOAM/fields/Fields/tmp/tmp.H` - tmp implementation

---

## ⚠️ Common Pitfalls

### Pitfall 1: Storing Reference to Temporary

```cpp
// ❌ WRONG
const volScalarField& saved = fvc::mag(U)();
solve(...);
// saved is dangling here!

// ✅ RIGHT
volScalarField saved = fvc::mag(U);
solve(...);
// saved still valid
```

### Pitfall 2: Unnecessary Copy

```cpp
// ❌ WRONG: Unnecessary copy
volScalarField temp1 = fvc::mag(U);
volScalarField temp2 = temp1;  // Copies entire field!

// ✅ RIGHT: Use reference or tmp
const volScalarField& temp2 = temp1;
// OR just reuse temp1
```

### Pitfall 3: Returning Reference to Local tmp

```cpp
// ❌ WRONG: Returns dangling reference
const volScalarField& getGrad(const volScalarField& p)
{
    return fvc::grad(p)();  // tmp dies!
}

// ✅ RIGHT: Return tmp or field
tmp<volScalarField> getGrad(const volScalarField& p)
{
    return fvc::grad(p);
}
```

---

## 🎯 Next Steps

1. **Practice:** Work through [07_Practical_Exercise.md](07_Practical_Exercise.md) to implement expression templates
2. **Deep Dive:** Read [03_Internal_Mechanics.md](03_Internal_Mechanics.md) to understand compiler internals
3. **Apply:** Review your own solvers for tmp usage patterns and optimization opportunities
4. **Profile:** Use memory profiling tools to verify expression template effectiveness in your cases