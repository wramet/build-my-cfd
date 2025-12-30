# Common Pitfalls in Dimensional Analysis

ปัญหาที่พบบ่อยใน Dimensional Analysis

---

## 🎯 Learning Objectives

After completing this section, you will be able to:

- Identify and resolve dimension mismatch errors in OpenFOAM simulations
- Properly use `dimensionedScalar` instead of plain `scalar` in operations
- Ensure source terms have correct dimensions matching their equations
- Handle division operations safely with dimensional awareness
- Debug dimensional issues using dimension checking techniques
- Avoid common pitfalls with fvc/fvm operations and boundary conditions

---

## 1. Dimension Mismatch

### Problem

```
--> FOAM FATAL ERROR:
Inconsistent dimensions for +
   [0 1 -1 0 0 0 0] + [1 -1 -2 0 0 0 0]
```

**What:** Attempting to add or subtract fields with incompatible dimensions
**Why:** OpenFOAM's type system enforces dimensional consistency at compile and runtime
**How:** Verify physical correctness and dimension compatibility

### Solution

```cpp
// Check physics - can't add velocity + pressure
// Correct equation dimensions

// Bad
result = U + p;  // Error! [m/s] + [kg/(m·s²)]

// Good
result = U + fvc::grad(p) / rho;  // Both are [L/T²]
```

**Key Point:** Every term in an equation must have identical dimensions

---

## 2. Missing dimless in Scalar Operations

### Problem

```cpp
scalar factor = 2.0;
result = factor * T;  // Error: scalar has no dimensions
```

**What:** Plain `scalar` type has no dimensional information
**Why:** OpenFOAM requires dimensional metadata for all operations
**How:** Use `dimensionedScalar` with `dimless` for numeric factors

### Solution

```cpp
// Use dimensionedScalar for operations
dimensionedScalar factor("f", dimless, 2.0);
result = factor * T;

// Or use literal with same dimensions
result = 2.0 * T;  // Works for scalar literals (auto-promoted)
```

**Key Point:** Explicitly declare dimensionless scalars using `dimless`

---

## 3. Inconsistent Source Term Dimensions

### Problem

```cpp
fvScalarMatrix TEqn
(
    fvm::ddt(T) == source  // Source has wrong dimensions
);
```

**What:** Source term dimensions don't match the equation's temporal derivative
**Why:** `ddt(T)` has dimensions [Θ/s], source must match
**How:** Calculate and specify correct dimensions

### Solution

```cpp
// ddt(T) has dimensions [T/s] = [Θ/s]
// Source must match
dimensionedScalar source("S", dimTemperature/dimTime, 100);

// Full equation
fvScalarMatrix TEqn
(
    fvm::ddt(T) == fvm::laplacian(DT, T) + source
);
```

**Key Point:** Source terms must match the dimensions of the equation's LHS

---

## 4. Division by Zero and Dimension Mismatch

### Problem

```cpp
result = a / b;  // b might be zero, and dimensions may not match
```

**What:** Division operations risk zero division and dimension errors
**Why:** Numerical stability requires SMALL values, but SMALL is dimensionless
**How:** Wrap SMALL in dimensionedScalar with matching dimensions

### Solution

```cpp
// Add SMALL to prevent division by zero
// Note: SMALL is dimensionless, must match divisor dimensions
result = a / (b + dimensionedScalar("small", b.dimensions(), SMALL));

// Alternative: max function
result = a / max(b, dimensionedScalar("eps", b.dimensions(), 1e-10));
```

**Key Point:** Always preserve dimensions when adding safety constants

---

## 5. Dimension Propagation in fvc/fvm Operations

### Problem

```cpp
// Incorrect dimension assumptions
volScalarField gradU = fvc::grad(U);  // gradU now has [1/s]
volScalarField laplacianP = fvc::laplacian(p);  // [kg/(m³·s²)]
```

**What:** fvc/fvm operations change field dimensions in non-obvious ways
**Why:** Differential operators add/remove length dimensions
**How:** Track dimension changes through operations

### Solution

```cpp
// Track dimensions carefully
// grad(U): [L/T] → [1/T]
// laplacian(p): [M/(L·T²)] → [M/(L³·T²)]
// div(phi, U): [L²/T] × [L/T] → [L²/T²]

// Verify dimensions before use
volScalarField gradU = fvc::grad(U);
Info << "gradU dimensions: " << gradU.dimensions() << endl;
```

**Key Point:** Always check dimension output from differential operators

---

## 6. Incorrect Dimension Specifications in Boundary Conditions

### Problem

```cpp
// Wrong dimension specification in boundary condition
boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 100;  // Missing dimensions!
    }
}
```

**What:** Boundary condition values lack dimension specifications
**Why:** OpenFOAM can't infer dimensions from numeric values alone
**How:** Specify dimensions explicitly in field files or boundary conditions

### Solution

```cpp
// Always specify dimensions in dictionary
dimensions      [0 0 1 0 0 0 0];  // Temperature [Θ]

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 300;  // Now dimensions match
    }
}

// Or use coded lookups with dimension checking
dict.readEntry("Tinlet", TInlet);  // Checks dimensions automatically
```

**Key Point:** Boundary condition values inherit dimensions from field definition

---

## 7. Mixing dimensionedScalar with Plain Scalar

### Problem

```cpp
dimensionedScalar T("T", dimTemperature, 300);
scalar threshold = 350;  // No dimensions

if (T > threshold)  // May cause issues in some contexts
{
    // ...
}
```

**What:** Mixing dimensioned and non-dimensioned types in conditionals
**Why:** Type system may not catch all dimension mismatches in comparisons
**How:** Use consistent dimensioned types or explicit conversions

### Solution

```cpp
// Better: use dimensionedScalar for threshold
dimensionedScalar threshold("thresh", dimTemperature, 350);

if (T > threshold)
{
    // ...
}

// Or explicitly compare values
if (T.value() > 350)
{
    // ...
}
```

**Key Point:** Maintain dimensional consistency in comparisons and conditionals

---

## 8. Wrong Unit Interpretation in Dictionary Files

### Problem

Reading dictionary with wrong units assumption

**What:** Numeric values interpreted without unit awareness
**Why:** OpenFOAM uses SI units internally by default
**How:** Specify dimensions explicitly in dictionary files

### Solution

```cpp
// Always specify dimensions in dictionary
U0  U0 [0 1 -1 0 0 0 0] (1 0 0);  // Velocity [L/T]

// Or use coded lookups with dimension checking
dict.readEntry("U0", U0);  // Automatically checks dimensions
```

**Key Point:** Dictionary entries must include dimension specifications

---

## 9. Debug Tips

### Printing Dimensions

```cpp
// Print field dimensions
Info << "T dimensions: " << T.dimensions() << endl;
Info << "U dimensions: " << U.dimensions() << endl;

// Print dimension sets as text
Info << "Dimension set: " 
     << T.dimensions() << " = " 
     << dimSet(T.dimensions()) << endl;
```

### Checking Dimensionless Quantities

```cpp
// Check if result is dimensionless
if (!result.dimensions().dimensionless())
{
    WarningInFunction
        << "Result should be dimensionless but has dimensions: "
        << result.dimensions() << endl;
}
```

### Dimension Comparison

```cpp
// Compare dimensions explicitly
if (field1.dimensions() != field2.dimensions())
{
    FatalErrorInFunction
        << "Dimension mismatch: "
        << field1.dimensions() << " vs " << field2.dimensions()
        << exit(FatalError);
}
```

---

## Quick Troubleshooting

| Error Type | Common Cause | Solution |
|------------|--------------|----------|
| Dimension mismatch | Adding incompatible fields | Check equation physics and dimensions |
| Can't add scalar to field | Using plain `scalar` | Use `dimensionedScalar` with `dimless` |
| Source term error | Wrong dimensions | Match equation LHS dimensions |
| Division by zero | Zero divisor without protection | Add dimensioned SMALL value |
| BC dimension error | Missing dimension specification | Add dimensions to field file |
| fvc/fvm dimension error | Incorrect dimension assumption | Print dimensions after operation |

---

## 📋 Key Takeaways

1. **Dimensional Consistency is Non-Negotiable**: Every term in an equation must have identical dimensions
2. **Always Use dimensionedScalar**: Never use plain `scalar` in dimensional computations
3. **Match Source Term Dimensions**: Source terms must match the dimensions of the equation's temporal derivative
4. **Track fvc/fvm Dimension Changes**: Differential operators modify dimensions - verify after each operation
5. **Protect Division Operations**: Use dimensioned SMALL or epsilon values with matching dimensions
6. **Specify BC Dimensions Explicitly**: Boundary conditions inherit dimensions from field definitions
7. **Debug with dimension()**: Always print dimensions when troubleshooting dimensional errors
8. **SI Units by Default**: OpenFOAM uses SI units internally unless otherwise specified

---

## 🧠 Concept Check

<details>
<summary><b>1. Why does `scalar * field` produce an error?</b></summary>

**Plain `scalar` has no dimensions** — use `dimensionedScalar` with `dimless` for numeric factors
</details>

<details>
<summary><b>2. How do you use SMALL with dimensional quantities?</b></summary>

**Wrap SMALL in `dimensionedScalar`** with dimensions matching the divisor: `dimensionedScalar("small", b.dimensions(), SMALL)`
</details>

<details>
<summary><b>3. How do you check field dimensions?</b></summary>

**Print** `.dimensions()` method: `Info << T.dimensions() << endl;` or check error messages for dimension sets
</details>

<details>
<summary><b>4. What dimensions must a source term have?</b></summary>

**Must match the equation's LHS dimensions** — if using `fvm::ddt(T)`, source must have dimensions `[Θ/s]`
</details>

<details>
<summary><b>5. How do fvc operations affect dimensions?</b></summary>

**They add/remove length dimensions** — `grad()` adds `[1/L]`, `div()` adds `[1/L]`, `laplacian()` adds `[1/L²]`
</details>

---

## 📖 Related Documents

- **Overview:** [00_Overview.md](00_Overview.md)
- **Dimension Arithmetic:** [03_Dimension_Arithmetic.md](03_Dimension_Arithmetic.md)
- **Non-Dimensionalization:** [04_Non_Dimensionalization.md](04_Non_Dimensionalization.md)
- **Advanced Applications:** [05_Advanced_Applications.md](05_Advanced_Applications.md)