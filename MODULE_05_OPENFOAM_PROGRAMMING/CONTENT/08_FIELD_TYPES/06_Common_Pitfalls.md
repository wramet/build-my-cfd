# Common Pitfalls & Debugging

![[mismatched_puzzle_pitfall.png]]

> [!WARNING] Overview
> This section covers the most common mistakes developers encounter when working with OpenFOAM field types, along with proven solutions and debugging techniques.

---

## Dimensional Inconsistency Errors

### Problem: Type Mismatch in Field Operations

**The most common error** in OpenFOAM development is attempting operations between incompatible field types:

```cpp
volScalarField wrong = p + U;  // ERROR: Cannot add scalar to vector
```

**Root Cause**: OpenFOAM enforces ==strict compile-time dimensional checking==. The expression `p + U` attempts to add a pressure field (scalar) with a velocity field (vector), which is mathematically invalid.

**Solutions**:

| Desired Result | Correct Solution | Explanation |
|----------------|------------------|-------------|
| Kinetic pressure | `p + 0.5 * rho * magSqr(U)` | Uses dot product for kinetic energy |
| Pressure + speed | `p + mag(U)` | Uses magnitude for vector size |
| Specific velocity component | `p + U.component(0)` | Uses component access for x-axis |

> [!TIP] Dimensional Consistency Check
> $$\text{Dimension}_{\text{result}} = \text{Dimension}_{\text{operand}_1} + \text{Dimension}_{\text{operand}_2}$$

---

## Incomplete Field Initialization

### Problem: Missing Constructor Arguments

**Insufficient field initialization** leads to undefined behavior:

```cpp
volScalarField T(mesh);  // ERROR: No dimensions or IOobject
```

**Root Cause**: The minimal constructor `volScalarField(mesh)` creates an uninitialized field without:
- **Physical dimensions** (required for dimensional consistency)
- **IOobject information** (required for file I/O)
- **Initial field values** or **boundary conditions**

**Correct Implementation**:

```cpp
volScalarField T
(
    IOobject
    (
        "T",
        runTime.timeName(),
        mesh,
        IOobject::MUST_READ,
        IOobject::AUTO_WRITE
    ),
    mesh,
    dimensionSet(0, 0, 0, 1, 0, 0, 0),  // [Θ] = K
    TInit.value()  // Uniform initial value
);
```

> [!INFO] Initialization Sequence
> 1. **IOobject** → Defines I/O behavior
> 2. **GeometricField** → Creates field with mesh and dimensions
> 3. **Internal Field** → Initializes cell center values
> 4. **Boundary Fields** → Sets boundary conditions

---

## Incorrect Patch Field Types

### Problem: Wrong Field Type for Surface vs. Volume Mesh

```cpp
surfaceScalarField phi
(
    IOobject(...),
    mesh,
    dimensionSet(0, 3, -1, 0, 0, 0, 0)  // [L³/T] = m³/s
);
// Must use fvsPatchField for surfaceMesh, not fvPatchField
```

**Root Cause**: OpenFOAM distinguishes between:

| Field Type | Base Class | Boundary Condition | Physical Location |
|------------|------------|-------------------|-------------------|
| Volume Fields | `volScalarField`, `volVectorField` | `fvPatchField` | Cell centers |
| Surface Fields | `surfaceScalarField`, `surfaceVectorField` | `fvsPatchField` | Face centers |

**Correct Boundary Specification**:

```cpp
// For volume fields
volScalarField::Boundary& Tbf = T.boundaryField();
Tbf.set(0, fixedValueFvPatchField<scalar>(mesh.boundary()[0], T));

// For surface fields
surfaceScalarField::Boundary& phibf = phi.boundaryField();
phibf.set(0, calculatedFvsPatchField<scalar>(mesh.boundary()[0], phi));
```

---

## Memory Management with `tmp<T>`

### Problem: Improper Temporary Field Handling

**Incorrect temporary management** leads to ==dangling references==:

```cpp
tmp<volScalarField> tTemp = p + q;
volScalarField& ref = tTemp();  // Creates non-const reference
// If tTemp leaves scope, ref becomes dangling!
```

**Root Cause**: The `tmp<T>` class uses ==automatic memory management== where the contained object is deleted when all references leave scope. Creating a non-const reference bypasses this safety mechanism.

**Safe Usage Patterns**:

#### Option 1: Const Reference (Recommended for temporary access)

```cpp
tmp<volScalarField> tTemp = p + q;
const volScalarField& ref = tTemp();  // Safe const reference
// Use ref only within current scope
```

#### Option 2: Keep a Copy (For long-term storage)

```cpp
tmp<volScalarField> tTemp = p + q;
volScalarField permanentCopy = tTemp();  // Creates copy independent of tmp
// permanentCopy persists after tTemp is destroyed
```

#### Option 3: Direct Assignment (For immediate use)

```cpp
volScalarField result = p + q;  // Automatic tmp handling
```

> [!WARNING] Dangling Reference Prevention
> ```cpp
> // NEVER do this:
> volScalarField& badRef = (p + q)();  // Temporary destroyed immediately!
>
> // ALWAYS do this:
> const volScalarField& goodRef = (p + q)();  // Safe while in scope
> ```

---

## Advanced Error Patterns

### Array Bounds Violation

```cpp
// DANGEROUS: Accessing beyond available patches
label badPatch = mesh.boundary().size();  // Out of bounds!
scalarField& badField = T.boundaryField()[badPatch];  // Segmentation fault
```

**Safe Pattern**:

```cpp
if (patchID < mesh.boundary().size())
{
    scalarField& patchField = T.boundaryField()[patchID];
    // Safe operations
}
```

### Dimensional Analysis Failure

```cpp
// Subtle error: Time derivative has wrong units
volScalarField dTdt = fvc::ddt(T);  // Correct: [K/s]
volScalarField wrong = dTdt * T;    // Wrong: [K²/s]
volScalarField correct = dTdt * rho*T;  // Correct: [kg·K/(m³·s)]
```

### Ghost Cell Access Problem

```cpp
// ERROR: Directly accessing internal field values near boundary
forAll(T.internalField(), i)
{
    label faceI = mesh.faceNeighbour()[i];  // May access invalid face
    // Should use proper cell-to-face mapping
}
```

**Correct Ghost Cell Handling**:

```cpp
// Proper cell value access
forAll(T, cellI)
{
    scalar cellValue = T[cellI];  // Direct cell access
    // Use geometric fields for face values
}
```

---

## Debugging Techniques

### Compile-Time Dimensional Checking

Use explicit dimension sets to catch errors early:

```cpp
dimensionSet velocityDim(0, 1, -1, 0, 0, 0, 0);  // [m/s]
dimensionSet pressureDim(1, -1, -2, 0, 0, 0, 0); // [Pa]

// This will fail at compile-time if dimensions don't match
volScalarField kineticEnergy = 0.5 * magSqr(U);  // [m²/s²]
```

### Runtime Validation

Add boundary checks for robustness:

```cpp
void validateField(const volScalarField& field)
{
    if (min(field).value() < 0 && field.name() == "T")
    {
        WarningInFunction << "Negative temperature detected in "
                         << field.name() << endl;
    }

    if (gMax(field.internalField()) > GREAT)
    {
        FatalErrorInFunction << "Infinite values in " << field.name()
                            << abort(FatalError);
    }
}
```

> [!TIP] Best Practice Question
> Always ask yourself: **"Where does this data live on the mesh?"** This simple question will guide you to the correct field type.

---

## Performance Considerations

### Memory Access Patterns

```cpp
// GOOD: Contiguous memory access
forAll(T, cellI)
{
    T[cellI] = T[cellI] + source[cellI];
}

// BAD: Random memory access through boundary conditions
forAll(mesh.boundary(), patchI)
{
    forAll(T.boundaryField()[patchI], faceI)
    {
        T.boundaryField()[patchI][faceI] = value;
    }
}
```

### Reducing Temporary Fields

```cpp
// INEFFICIENT: Creates multiple temporaries
volScalarField result = p + 0.5 * rho * magSqr(U);

// EFFICIENT: Reduce temporaries
tmp<volScalarField> tKE = 0.5 * rho * magSqr(U);
volScalarField result = p + tKE;
```

---

## Summary of Common Pitfalls

| Pitfall Category | Symptom | Solution |
|-----------------|---------|----------|
| **Dimensional mismatch** | Compile-time error | Check dimensions match for arithmetic operations |
| **Incomplete initialization** | Runtime segfault | Provide IOobject, dimensions, and initial values |
| **Wrong patch field type** | Boundary condition errors | Use `fvPatchField` for volume, `fvsPatchField` for surface |
| **Dangling references** | Memory corruption | Use const references or copies with `tmp<T>` |
| **Array bounds violation** | Segmentation fault | Always validate indices before accessing |
| **Ghost cell misuse** | Incorrect boundary values | Use proper field-to-face mapping |

> [!INFO] Key Takeaway
> OpenFOAM's field system provides powerful abstractions, but requires careful attention to dimensional consistency, memory management, and proper initialization. Understanding the underlying architecture prevents these common pitfalls.
