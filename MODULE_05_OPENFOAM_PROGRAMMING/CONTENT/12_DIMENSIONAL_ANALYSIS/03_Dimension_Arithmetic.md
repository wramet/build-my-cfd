# Dimension Arithmetic

---

## 🎯 Learning Objectives

After completing this section, you will be able to:

- Understand how dimensions propagate through arithmetic operations
- Apply dimensional analysis to OpenFOAM calculations correctly
- Predict the dimensional result of complex expressions involving multiple operations
- Debug dimensional errors in CFD simulations

---

## Overview

> **Dimensions combine automatically according to physics rules**

In OpenFOAM, every arithmetic operation involving `dimensioned` types automatically checks and propagates dimensional information. This prevents physically meaningless calculations and catches errors at compile-time rather than runtime.

### What
Dimension arithmetic refers to how dimensional units combine through mathematical operations. OpenFOAM's type system tracks these combinations automatically using the `DimensionSet` class.

### Why
- **Physical correctness** — Prevents invalid operations like adding pressure to velocity
- **Early error detection** — Catches dimensional inconsistencies at compile-time
- **Self-documenting code** — Dimensional information is explicit and checkable
- **Unit safety** — Reduces conversion errors between different unit systems

### How
OpenFOAM overloads C++ operators for `dimensioned` types to automatically:
- Track exponents for multiplication, division, and powers
- Verify dimensional compatibility for addition and subtraction
- Maintain dimensional information through field operations (`fvc::`, `fvm::`)

---

## 1. Multiplication

**Exponents add together:**

```cpp
// Force calculation
dimensionedScalar m("m", dimMass, 2.5);      // [kg]
dimensionedScalar a("a", dimAcceleration, 9.81); // [m/s²]
dimensionedScalar F = m * a;                 // [kg·m/s²] = [N]
```

**Dynamic pressure example:**

```cpp
dimensionedScalar rho("rho", dimDensity, 1000);    // [kg/m³]
dimensionedScalar U("U", dimVelocity, 10);          // [m/s]
dimensionedScalar dynP = 0.5 * rho * sqr(U);
// Calculation: [kg/m³] × [m²/s²] = [kg/(m·s²)] = [Pa]
```

---

## 2. Division

**Exponents subtract:**

```cpp
// Kinematic viscosity from dynamic viscosity
dimensionedScalar mu("mu", dimPressure*dimTime, 0.001); // [Pa·s]
dimensionedScalar rho("rho", dimDensity, 1000);          // [kg/m³]
dimensionedScalar nu = mu / rho;
// Calculation: [kg/(m·s)] / [kg/m³] = [m²/s]
```

---

## 3. Powers

**Exponents multiply by the power:**

```cpp
dimensionedScalar L("L", dimLength, 5.0);

// Squaring
dimensionedScalar L2 = sqr(L);    // [m²]

// Cubing
dimensionedScalar L3 = pow3(L);   // [m³]

// Square root
dimensionedScalar A("A", dimArea, 25.0);
dimensionedScalar sqrtA = sqrt(A); // [m]
```

---

## 4. Addition and Subtraction

**Must have IDENTICAL dimensions:**

```cpp
dimensionedScalar p1("p1", dimPressure, 100000);  // [Pa]
dimensionedScalar p2("p2", dimPressure, 50000);   // [Pa]
dimensionedScalar totalP = p1 + p2;               // ✓ [Pa] + [Pa] = [Pa]

// This causes a COMPILATION ERROR:
dimensionedScalar U("U", dimVelocity, 10);        // [m/s]
// dimensionedScalar invalid = p1 + U;            // ✗ [Pa] + [m/s] = ERROR!
```

---

## 5. Dimensioned Field Operations

**All operators maintain dimensional consistency:**

```cpp
volScalarField rho(mesh.lookupObject<volScalarField>("rho"));  // [kg/m³]
volVectorField U(mesh.lookupObject<volVectorField>("U"));      // [m/s]
volScalarField p(mesh.lookupObject<volScalarField>("p"));      // [Pa]

// Complex expression
volScalarField result = rho * magSqr(U) + p;
// [kg/m³] × [m²/s²] + [Pa] = [Pa] + [Pa] = [Pa] ✓
```

### Differential Operations

**`fvc` (finite volume calculus) operations preserve dimensions:**

```cpp
// Pressure gradient
volVectorField gradP = fvc::grad(p);
// [Pa] → [Pa/m]

// Velocity divergence
volScalarField divU = fvc::div(U);
// [m/s] → [1/s]

// Laplacian of pressure
volScalarField lapP = fvc::laplacian(p);
// [Pa] → [Pa/m²]
```

---

## 6. Common CFD Calculations

| Expression | Physical Quantity | Resulting Dimension |
|------------|------------------|---------------------|
| ρU² | Dynamic pressure | [Pa] |
| μ∇U | Viscous stress | [Pa] |
| ∇p | Pressure gradient | [Pa/m] |
| U·∇U | Convective acceleration | [m/s²] |
| k·∇T | Heat flux | [W/m²] |
| ∇·U | Volume dilation | [1/s] |

---

## Quick Reference: Dimension Propagation Rules

| Operation | Dimension Behavior | Example |
|-----------|-------------------|---------|
| `A * B` | Add exponents | [m] × [m] = [m²] |
| `A / B` | Subtract exponents | [m²] / [m] = [m] |
| `sqr(A)` | Double exponents | [m] → [m²] |
| `pow3(A)` | Triple exponents | [m] → [m³] |
| `sqrt(A)` | Halve exponents | [m²] → [m] |
| `pow(A, n)` | Multiply by n | [m]ⁿ |
| `A + B` | Must match exactly | [Pa] + [Pa] |
| `A - B` | Must match exactly | [Pa] - [Pa] |

---

## 🔑 Key Takeaways

- **Multiplication/division** — Dimensions combine by adding/subtracting exponents
- **Powers** — Exponents multiply by the power (sqr doubles, sqrt halves)
- **Addition/subtraction** — Requires identical dimensions; enforced at compile-time
- **Field operations** — `fvc::` and `fvm::` operations automatically track dimensional changes through differential operators
- **Safety first** — Dimension checking prevents physical errors before runtime

---

## 🧠 Concept Check

<details>
<summary><b>1. What are the dimensions of ρU²?</b></summary>

**[Pa]** — Calculation: [kg/m³] × [m²/s²] = [kg/(m·s²)] = [Pa]

This represents dynamic pressure in Bernoulli's equation.
</details>

<details>
<summary><b>2. What is required for addition of dimensioned quantities?</b></summary>

**Identical dimensions** — Both operands must have the exact same `DimensionSet`

Otherwise, the code will not compile. This prevents physically meaningless operations.
</details>

<details>
<summary><b>3. How do square root operations affect dimensions?</b></summary>

**Halve the exponents** — For example, sqrt([m²]) = [m] or sqrt([Pa]) = [kg^0.5·m^-0.5·s^-1]

This is why taking the square root of an area gives a length.
</details>

<details>
<summary><b>4. What are the dimensions of ∇p (pressure gradient)?</b></summary>

**[Pa/m]** — The gradient operator adds [1/m] to the original dimensions

Useful for: pressure-driven flow calculations, buoyancy forces, porous media resistance
</details>

<details>
<summary><b>5. Why does OpenFOAM's dimension system matter for CFD?</b></summary>

**Compile-time safety** — Catches unit conversion errors, mismatched boundary conditions, and incorrect turbulence model formulations before the simulation runs, saving debugging time and preventing physically incorrect results
</details>

---

## 📖 Related Documentation

- **Overview:** [00_Overview.md](00_Overview.md)
- **DimensionSet internals:** [02_DimensionSet_Advanced.md](02_DimensionSet_Advanced.md)
- **Dimensioned types:** [03_Dimensioned_Types_Intro.md](03_Dimensioned_Types_Intro.md)
- **Field operations:** [05_Fields_GeometricFields/02_Design_Philosophy.md](../../05_FIELDS_GEOMETRICFIELDS/02_Design_Philosophy.md)