# Dimensioned Types - Pitfalls and Solutions

Common Pitfalls and Solutions — Learn from Others' Mistakes

## Learning Objectives

By the end of this section, you should be able to:
- Identify and resolve the most common dimension-related errors in OpenFOAM
- Distinguish between compile-time and runtime dimension errors
- Apply best practices for dimensional consistency in your code
- Use dimension checking as an effective debugging tool
- Avoid dangerous shortcuts that compromise dimensional safety

---

> **Why This Section Matters**
> - **OpenFOAM error messages are cryptic** — This section translates them
> - Recognize common traps → Avoid them proactively
> - Debug faster when dimension errors occur
> - Understanding pitfalls prevents hours of frustration

---

## Quick Troubleshooting Reference

| Error Pattern | Most Likely Cause | Quick Check |
|---------------|-------------------|-------------|
| `Inconsistent dimensions for +/-` | Adding/subtracting incompatible quantities | Verify equation physics |
| `LHS dimensions are` vs `RHS dimensions are` | Assignment with wrong dimensions | Check both sides match |
| `dimensions of [...] are not equal` | Comparison or operation mismatch | Verify operands compatible |
| Wrong value but no error | Incorrect dimension specification | Verify SI units correct |
| Field creation warning | Missing dimensions in constructor | Include dimensioned initial value |
| sqrt/pow errors | Invalid result dimensions | Check mathematical operation validity |

---

## 1. Compile-Time vs Runtime Errors

### Understanding the Difference

**Compile-Time Errors** (Preferred):
- Caught during code compilation
- Prevent invalid code from executing
- Usually indicate clear dimension mismatches

**Runtime Errors** (More Dangerous):
- Occur during simulation execution
- Often result from dictionary input mismatches
- May only appear under specific conditions

### Strategy
- Design code to catch errors at compile time when possible
- Use runtime checks for dictionary-dependent code
- Never silence dimension errors to "make it work"

---

## 2. Dimension Mismatch in Operations

### Problem: Arithmetic with Incompatible Dimensions

```cpp
--> FOAM FATAL ERROR:
Inconsistent dimensions for +/-
   Left:  [1 -1 -2 0 0 0 0]  // pressure [M L⁻¹ T⁻²]
   Right: [0 1 -1 0 0 0 0]   // velocity [L T⁻¹]
```

**Root Cause**: Attempting to add physically incompatible quantities.

**Solutions**:

```cpp
// BAD - Adding pressure and velocity
volScalarField result = p + U;

// GOOD - Only add compatible dimensions
volScalarField result = p + p;  // pressure + pressure

// GOOD - If you need non-dimensional, explicitly non-dimensionalize
volScalarField result = p / pRef + U / URef;
```

---

## 3. Incorrect Dimension Specification

### Problem: Wrong Dimension Set

```cpp
// Common mistake: confusing kinematic and dynamic viscosity
dimensionedScalar nu("nu", dimDynamicViscosity, 1e-6);
// ERROR: 1e-6 m²/s is kinematic viscosity, not Pa·s
```

**Understanding the Units**:
- **Kinematic viscosity** (ν): [L² T⁻¹] → `dimKinematicViscosity` → m²/s
- **Dynamic viscosity** (μ): [M L⁻¹ T⁻¹] → `dimDynamicViscosity` → Pa·s

**Solutions**:

```cpp
// Correct - kinematic viscosity
dimensionedScalar nu("nu", dimKinematicViscosity, 1e-6);  // m²/s

// Correct - dynamic viscosity
dimensionedScalar mu("mu", dimDynamicViscosity, 1e-3);  // Pa·s

// Correct relationship
dimensionedScalar nu = mu / rho;  // ν = μ/ρ
```

---

## 4. Missing Dimensions in Field Construction

### Problem: Forgetting dimensionedScalar wrapper

```cpp
volScalarField T
(
    IOobject
    (
        "T",
        runTime.timeName(),
        mesh,
        IOobject::NO_READ,
        IOobject::AUTO_WRITE
    ),
    mesh,
    scalar(300)  // ⚠️ Missing dimensions! Field becomes dimensionless
);
```

**Why This Happens**: Using plain `scalar` instead of `dimensionedScalar`.

**Solutions**:

```cpp
// GOOD - Always specify dimensions
volScalarField T
(
    IOobject
    (
        "T",
        runTime.timeName(),
        mesh,
        IOobject::NO_READ,
        IOobject::AUTO_WRITE
    ),
    mesh,
    dimensionedScalar("T", dimTemperature, 300)  // ✓ [K]
);

// Alternative - using predefined dimension set
volScalarField T
(
    IOobject
    (
        "T",
        runTime.timeName(),
        mesh,
        IOobject::NO_READ,
        IOobject::AUTO_WRITE
    ),
    mesh,
    dimensionedScalar
    (
        "T",
        dimensionSet(0, 0, 0, 1, 0, 0, 0),  // [θ] temperature
        300
    )
);
```

---

## 5. Dimension Loss in Operations

### Problem: Using `.value()` in calculations

```cpp
dimensionedScalar dt("dt", dimTime, 0.001);
volScalarField temperatureRate = (T_new - T) / dt.value();  // ⚠️ Loses dimensions!
// Result becomes dimensionless instead of [K T⁻¹] = [K/s]
```

**Why This Happens**: `.value()` extracts only the numeric value, discarding dimension information.

**Solutions**:

```cpp
// GOOD - Keep operations dimensioned
volScalarField temperatureRate = (T_new - T) / dt;  // ✓ [K/s]

// GOOD - If you truly need non-dimensional, be explicit
volScalarField nonDimRate = (T_new - T) / (T_ref * dt);  // ✓ dimensionless
```

---

## 6. Invalid Mathematical Operations

### Problem: sqrt/pow with invalid dimensions

```cpp
// sqrt of pressure - what does this mean physically?
dimensionedScalar p("p", dimPressure, 100000);  // [M L⁻¹ T⁻²]
dimensionedScalar result = sqrt(p);  // ⚠️ [M^0.5 L^-0.5 T^-1] - nonsense!
```

**Understanding the Issue**: Not all operations make physical sense, even if mathematically possible.

**Solutions**:

```cpp
// GOOD - sqrt of velocity squared
dimensionedScalar U2("U2", dimVelocity*dimVelocity, 100);  // [L² T⁻²]
dimensionedScalar U = sqrt(U2);  // ✓ [L T⁻¹] - physically meaningful

// GOOD - sqrt of area → length
dimensionedScalar A("A", dimArea, 0.01);  // [L²]
dimensionedScalar L = sqrt(A);  // ✓ [L] - side length of equivalent square

// For pressure, consider what you actually need:
dimensionedScalar p("p", dimPressure, 100000);
dimensionedScalar c = sqrt(dimless * p / rho);  // Speed of sound: √(γP/ρ)
```

**General Rule**: Before applying sqrt/pow, ask: "Does the result have physical meaning?"

---

## 7. Dictionary Dimension Mismatches

### Problem: Conflicting dimension sources

```cpp
// In transportProperties dictionary:
// nu              [0 2 -1 0 0 0 0] 1e-6;  // [L² T⁻¹] kinematic viscosity

// In code:
dimensionedScalar nu("nu", dimDynamicViscosity, dict);  // ⚠️ [M L⁻¹ T⁻¹]
// ERROR: Dictionary dimensions don't match specified dimensions!
```

**Why This Happens**: Dictionary defines one dimension, code specifies another.

**Solutions**:

```cpp
// Option 1: Match dimensions in code
dimensionedScalar nu("nu", dimKinematicViscosity, dict);

// Option 2: Let dictionary control (preferred for flexibility)
dimensionedScalar nu(dict.lookup("nu"));

// Option 3: Verify dimensions match explicitly
dimensionedScalar nu
(
    "nu",
    dimKinematicViscosity,
    dict
);
if (nu.dimensions() != dimKinematicViscosity)
{
    FatalErrorInFunction
        << "Incorrect dimensions for nu in dictionary" << endl
        << exit(FatalError);
}
```

---

## 8. Unsafe Comparison Operations

### Problem: Comparing values without dimension check

```cpp
dimensionedScalar length("L", dimLength, 1.0);      // [L]
dimensionedScalar time("t", dimTime, 1.0);          // [T]

// ⚠️ This compiles but compares meaningless values
if (length.value() == time.value())
{
    Info << "Equal!" << endl;  // 1.0 == 1.0, but meaningless comparison
}

// ⚠️ Silent failure - comparison without dimension check
dimensionedScalar result = max(length, time);  // Runtime error or undefined
```

**Why This Happens**: `.value()` bypasses dimension checking.

**Solutions**:

```cpp
// GOOD - Explicit dimension check
if (length.dimensions() == time.dimensions())
{
    if (length.value() > time.value())
    {
        // Safe to compare
    }
}
else
{
    FatalErrorInFunction
        << "Cannot compare incompatible dimensions" << endl
        << exit(FatalError);
}

// GOOD - Use templated max with dimension awareness
dimensionedScalar result = max(length, length);  // Same dimensions

// For operations that should preserve dimensions:
dimensionedScalar smallerDim = min(length, 2.0 * length);  // ✓ [L]
```

---

## 9. The Dangerous Temptation: Disabling Dimension Checks

### Problem: Silencing the messenger

```cpp
// ⚠️⚠️⚠️ NEVER DO THIS IN PRODUCTION ⚠️⚠️⚠️
dimensionSet::checking(false);

// Now all dimension errors are silently ignored!
// You can add pressure to velocity and it won't complain
// Your simulation will run with wrong physics
```

**When People Use It** (and why it's wrong):
- "Legacy code doesn't work" → Fix the legacy code!
- "Just testing" → Tests should verify dimensions too!
- "I know what I'm doing" → Everyone makes mistakes

**Acceptable Use Cases** (with strict safeguards):

```cpp
// ONLY for debugging, with immediate re-enable
{
    const bool oldCheck = dimensionSet::checking();
    dimensionSet::checking(false);
    
    // Debug specific line
    // volatileOperation();
    
    dimensionSet::checking(oldCheck);  // ALWAYS restore
}

// Better: Use nonDimensional instead
dimensionedScalar p_star = p / pRef;  // Explicit non-dimensionalization
```

**Remember**: Dimension checking is a **safety net**, not an inconvenience.

---

## 10. Common Pitfalls by Severity

### 🔴 Critical (Simulation-Killing)

1. **Disabled dimension checking** in production
2. **Wrong dimension specification** in boundary conditions
3. **Dimension loss in `.value()` operations**

### 🟡 Important (Results-Affecting)

1. **Inconsistent dictionary dimensions**
2. **Missing dimensions** in field constructors
3. **Invalid mathematical operations** (sqrt of pressure)

### 🟢 Minor (Code Quality)

1. **Inconsistent naming** (nu vs mu vs viscosity)
2. **Redundant dimension checks** (trust the compiler)
3. **Magic numbers** without dimensions

---

## Best Practices Summary

### ✅ DO

- **Always specify dimensions** when creating fields
- **Let dictionary control dimensions** when reading input
- **Use dimensioned types throughout** calculations
- **Verify physics** before implementing equations
- **Check dimensions first** in comparisons
- **Use nonDimensional explicitly** when needed

### ❌ DON'T

- **Never disable dimension checking** in production
- **Never use `.value()` in calculations** (unless intentional)
- **Never assume dimensions match** without checking
- **Never ignore dimension warnings**
- **Never mix naming conventions** (nu/mu, U/magU)

---

## 🧠 Concept Check

<details>
<summary><b>1. Why do dimension errors occur?</b></summary>

**Dimension errors indicate physics problems** — you're attempting an operation that doesn't make physical sense. This is OpenFOAM protecting you from implementing incorrect equations.

</details>

<details>
<summary><b>2. Should you ever disable dimension checking?</b></summary>

**Never in production code**. You lose the primary safety net that prevents physical errors. Only use temporarily for debugging legacy code, and always re-enable immediately.

</details>

<summary><b>3. How do you safely read dimensioned values from dictionaries?</b></summary>

```cpp
// Best practice - let dictionary define dimensions
dimensionedScalar nu(dict.lookup("nu"));

// If you must specify dimensions, verify they match
dimensionedScalar nu("nu", dimKinematicViscosity, dict);
```

</details>

<details>
<summary><b>4. What's the difference between compile-time and runtime dimension errors?</b></summary>

- **Compile-time**: Caught during compilation, usually from operations in code
- **Runtime**: Occur during execution, typically from dictionary mismatches
- **Strategy**: Design code to catch errors at compile time when possible

</details>

<details>
<summary><b>5. Why is `sqrt(pressure)` problematic?</b></summary>

The result [M^0.5 L^-0.5 T^-1] has no clear physical meaning. Before applying sqrt/pow, verify the result dimension corresponds to a meaningful physical quantity.

</details>

---

## 📚 Related Documentation

- **Overview & Design Philosophy**: [00_Overview.md](00_Overview.md)
- **Dimension Sets Reference**: [00_Overview.md](00_Overview.md#dimension-sets-reference)
- **Engineering Benefits**: [06_Engineering_Benefits.md](06_Engineering_Benefits.md)
- **Implementation Details**: [03_Implementation_Mechanisms.md](03_Implementation_Mechanisms.md)

---

## Debug Flow: When You Get a Dimension Error

```
1. READ THE ERROR MESSAGE
   └─ Note the left and right dimensions shown

2. INTERPRET THE DIMENSIONS
   └─ Use SI reference table to understand units
   └─ What quantities are you trying to combine?

3. CHECK THE PHYSICS
   └─ Is the equation correct?
   └─ Are you adding incompatible quantities?

4. VERIFY THE CODE
   └─ Are dimensions specified correctly?
   └─ Did you lose dimensions with .value()?

5. FIX THE ROOT CAUSE
   └─ Not by disabling checks!
   └─ Fix the equation or dimension specification
```

**Remember**: Dimension errors are your friend. They're catching mistakes before your simulation produces nonsense results.