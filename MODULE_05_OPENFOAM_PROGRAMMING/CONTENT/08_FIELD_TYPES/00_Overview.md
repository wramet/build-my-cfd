# Overview: Field Types in OpenFOAM

> [!INFO] Overview
> This section provides a comprehensive introduction to OpenFOAM's field type system—the foundation for computational fluid dynamics (CFD) simulations.

---

## 🎯 Learning Objectives

By completing this section, you will be able to:

- ✅ Understand the inheritance hierarchy of Field types in OpenFOAM
- ✅ Master dimensional analysis with `dimensionSet`
- ✅ Correctly create and initialize Fields
- ✅ Understand Surface and Point Field types
- ✅ Comprehend performance characteristics and memory structure

---

## 📋 Prerequisites

### Essential Background Knowledge

**Complete [Chapter 4: C++ Programming in OpenFOAM](../../Chapter_04_Cpp_Programming_in_OpenFOAM/README.md)** - This foundational chapter provides essential C++ programming concepts specific to OpenFOAM's architecture, including:

- **Coding conventions** and OpenFOAM style guidelines
- **Memory management** using `autoPtr`, `tmp`, and reference counting
- **Template metaprogramming** used throughout OpenFOAM
- **Class hierarchies** for geometry and field classes

### Advanced C++ Concepts

**Template Programming**
Deep understanding of C++ templates is critical since OpenFOAM extensively uses templates for:

| Usage | Example |
|-------|---------|
| Field type definitions | `volScalarField`, `volVectorField`, `surfaceTensorField` |
| Geometry classes | `Vector<T>`, `Tensor<T>`, `SymmTensor<T>` |
| Mathematical operations | Dimension checking |
| Compile-time polymorphism | Solver implementations |

**Inheritance and Polymorphism**
Mastery of C++ inheritance patterns enables you to:

- Understand OpenFOAM's class hierarchy (e.g., `fvPatchField` implementations)
- Extend base classes for custom boundary conditions
- Work with abstract interfaces for turbulence models and thermodynamic properties
- Implement custom physics models following established patterns

### OpenFOAM Architecture Knowledge

**Case Structure Knowledge**
Comprehensive understanding of OpenFOAM case organization:

| Directory | Description |
|-----------|-------------|
| `0/` | Initial conditions and boundary condition specifications |
| `constant/` | Mesh data, physical properties, and simulation parameters |
| `system/` | Solution control, numerical schemes, and solver settings |

**Mesh Concepts**
Precise understanding of computational mesh fundamentals:

- **Mesh topology** of finite volume discretization (`polyMesh`, `fvMesh`)
- **Relationships** between cells, faces, and patches
- **Boundary condition management** and patch identification
- **Mesh quality requirements** for numerical stability
- **Mesh generation procedures** (`blockMesh`, `snappyHexMesh`)

---

## 1. "Hook": Excel Sheets vs. CFD Fields

Imagine having a massive Excel spreadsheet where each cell contains a physical quantity (pressure, velocity, temperature) at a specific location in your flow domain.

Now imagine needing to perform mathematical operations on millions of cells simultaneously while maintaining physical unit consistency.

**This is what OpenFOAM's field system does**—it's a **type-safe, dimension-aware, high-performance spreadsheet for CFD**

```mermaid
flowchart LR
    A[Excel Spreadsheet] --> B[Manual Cell Operations]
    A --> C[No Unit Checking]
    A --> D[Sequential Processing]

    E[OpenFOAM Fields] --> F[Automatic Field Operations]
    E --> G[Built-in Dimension Analysis]
    E --> H[Parallel Vectorized Computation]
```

### Field Architecture: Beyond Simple Arrays

While Excel cells are simple value containers, OpenFOAM fields are sophisticated computational objects that reflect the mathematical and physical rigor required for CFD simulations.

An **OpenFOAM Field** such as `volScalarField p` represents more than just an array of pressure values:

```cpp
// Example: Creating a pressure field in OpenFOAM
volScalarField p
(
    IOobject
    (
        "p",
        runTime.timeName(),
        mesh,
        IOobject::MUST_READ,
        IOobject::AUTO_WRITE
    ),
    mesh
);
```

This single declaration creates:

- **Internal field values**: Pressure at each cell center within control volumes
- **Boundary field values**: Pressure values on boundary patches
- **Dimensional consistency**: Guaranteed units of $\text{kg} \cdot \text{m}^{-1} \cdot \text{s}^{-2}$
- **Mesh linkage**: Direct connection to computational mesh topology
- **Time management**: Automatic read/write capability during simulations

```mermaid
graph TD
    A[volScalarField p] --> B[Internal Field]
    A --> C[Boundary Field]
    A --> D[dimensionSet]
    A --> E[mesh Reference]
    A --> F[IOobject]

    B --> B1[Cell Center Values]
    B --> B2[Contiguous Memory]

    C --> C1[Patch Values]
    C --> C2[Boundary Conditions]
```

### Mathematical Operations: Natural Physics Notation

The **power of OpenFOAM's field system** lies in its ability to express complex mathematical expressions using natural notation while maintaining dimensional consistency:

```cpp
// Momentum equation components in OpenFOAM
volVectorField U = ...;                    // Velocity field
volScalarField p = ...;                    // Pressure field
dimensionedScalar rho("rho", dimDensity, 1.2);    // Density

// Natural mathematical expression
fvVectorMatrix UEqn
(
    fvm::ddt(rho, U)                     // $\rho \frac{\partial \mathbf{U}}{\partial t}$
  + fvm::div(rho*U, U)                   // $\rho (\mathbf{U} \cdot \nabla) \mathbf{U}$
 ==
  - fvc::grad(p)                         // $-\nabla p$
);
```

**Key Operators:**
- `fvm::ddt`: Implicit temporal derivative
- `fvm::div`: Implicit divergence
- `fvc::grad`: Explicit gradient

---

## 2. Field Type Hierarchy: The Blueprint

OpenFOAM organizes field data through a sophisticated template hierarchy that enables efficient storage, manipulation, and mathematical operations on CFD data.

### Class Hierarchy Architecture

The field type hierarchy in OpenFOAM follows a systematic inheritance structure, building from simple data containers to complex geometric fields:

```mermaid
graph TD
    A[GeometricField&lt;Type, PatchField, GeoMesh&gt;] --> B[DimensionedField&lt;Type, GeoMesh&gt;]
    B --> C[Field&lt;Type&gt;]
    C --> D[List&lt;Type&gt;]
    B --> E[regIOobject]

    A --> F[GeometricBoundaryField]
    F --> G[FieldField&lt;PatchField&gt;]

    H[volScalarField] --> A
    I[volVectorField] --> A
    J[volTensorField] --> A
    K[surfaceScalarField] --> A
```

**At the base level:**
- `List<Type>` provides a dynamic array container for any data type
- `Field<Type>` extends this with mathematical operations specific to CFD calculations
- Supports vector operations, tensor operations, and field-wide algebra

### Core Field Components

#### **`GeometricField<Type, PatchField, GeoMesh>`**
The complete field class that combines both internal field values and boundary conditions.

**Template Parameters:**
- `Type`: Mathematical entity (scalar, vector, tensor, etc.)
- `PatchField`: Boundary field type for managing boundary conditions
- `GeoMesh`: Mesh type (volMesh for cell-centered fields, surfaceMesh for face-centered fields)

#### **`DimensionedField<Type, GeoMesh>`**
Extends the base field with:
- Dimensional information
- Mesh linkage
- Inherits from `Field<Type>` (data storage) and `regIOobject` (file I/O)
- Can automatically read and write field data

#### **`GeometricBoundaryField`**
A specialized container that manages:
- All boundary patches for a geometric field
- Collection of boundary condition objects
- Uniform access to boundary values and gradients

### Common Type Definitions

The most commonly used field types in OpenFOAM are defined as template specializations:

| Field Type | Template Specialization | Common Usage |
|------------|------------------------|--------------|
| `volScalarField` | `GeometricField<scalar, fvPatchField, volMesh>` | Pressure, Temperature |
| `volVectorField` | `GeometricField<vector, fvPatchField, volMesh>` | Velocity, Displacement |
| `volTensorField` | `GeometricField<tensor, fvPatchField, volMesh>` | Stress, Strain Rate |
| `surfaceScalarField` | `GeometricField<scalar, fvsPatchField, surfaceMesh>` | Fluxes, Heat Transfer Rates |

**Field Type Selection:**
- **Volume fields (`vol*`)**: Quantities naturally defined at cell centers
- **Surface fields (`surface*`)**: Quantities naturally defined at cell faces

---

## 3. Internal Mechanics: Template Parameters Explained

### Template Signature
```cpp
template<class Type, template<class> class PatchField, class GeoMesh>
class GeometricField : public DimensionedField<Type, GeoMesh>
```

The `GeometricField` class is one of OpenFOAM's most fundamental template classes, providing a flexible framework for representing data fields of various types on different meshes.

### Parameter 1: `Type` - What Data Do We Store?

The `Type` parameter determines the mathematical nature of the data stored at each mesh location.

| Type Parameter | Description | Usage Example | Resulting Field Class |
|----------------|-------------|----------------|----------------------|
| **`scalar`** | Single double-precision value | `volScalarField p` - Pressure<br>`volScalarField T` - Temperature | Volume Scalar Field |
| **`vector`** | 3D vector (x, y, z) | `volVectorField U` - Velocity<br>`volVectorField F` - Force | Volume Vector Field |
| **`tensor`** | 3×3 matrix (second-order quantity) | `volTensorField tau` - Stress<br>`volTensorField D` - Strain Rate | Volume Tensor Field |

### Parameter 2: `PatchField` - How Do We Handle Boundaries?

The `PatchField` parameter is a **template template parameter**—a template class that takes `Type` as a parameter, enabling compile-time polymorphism for boundary conditions.

| PatchField Type | Mesh Used | Management | Example |
|-----------------|-----------|------------|---------|
| **`fvPatchField<Type>`** | `volMesh` | Cell-centered values | `fvPatchField<scalar>` |
| **`fvsPatchField<Type>`** | `surfaceMesh` | Face-centered values | `fvsPatchField<scalar>` |
| **`pointPatchField<Type>`** | `pointMesh` | Mesh vertex values | `pointPatchField<vector>` |

```mermaid
graph TD
    A[PatchField Parameter] --> B[Boundary Policy Selection]
    B --> C[Compile-Time Polymorphism]
    B --> D[Type Safety]
    B --> E[Performance Optimization]
```

### Parameter 3: `GeoMesh` - Where Is the Data?

The `GeoMesh` parameter defines the discretization topology and provides geometric information.

| GeoMesh Type | Data Location | Special Characteristics | Main Usage |
|--------------|---------------|-------------------------|------------|
| **`volMesh`** | Cell centers | Cell volumes, cell centers, connectivity | Finite Volume Method |
| **`surfaceMesh`** | Face centers | Face areas, face centers, normals | Flux Calculations |
| **`pointMesh`** | Mesh vertices | Point coordinates, point connectivity | Mesh Deformation |

### Template Instantiation Example

```cpp
// Volume-centered scalar field (pressure)
typedef GeometricField<scalar, fvPatchField, volMesh> volScalarField;

// Volume-centered vector field (velocity)
typedef GeometricField<vector, fvPatchField, volMesh> volVectorField;

// Surface scalar field (mass flux)
typedef GeometricField<scalar, fvsPatchField, surfaceMesh> surfaceScalarField;

// Volume tensor field (stress)
typedef GeometricField<tensor, fvPatchField, volMesh> volTensorField;
```

### Design Benefits

This three-parameter template design provides significant advantages:

1. **Type Safety**: Compile-time checking prevents mixing incompatible field types
2. **Performance**: Template specialization optimizes operations
3. **Flexibility**: New field types can be created by combining existing parameters
4. **Extensibility**: New mesh types or boundary conditions can be added without modifying existing code
5. **Mathematical Clarity**: Field operations respect the mathematical properties of each Type

---

## 4. The Mechanism: How Fields Map to Mesh

### Internal vs. Boundary Fields

OpenFOAM's `GeometricField` class uses a sophisticated **dual data structure** that manages the mapping of physical quantities onto a computer mesh. This design separates internal domain values from boundary conditions, enabling **optimized memory access** and **flexible boundary condition management**.

```cpp
// Simplified view of GeometricField data members
class GeometricField
{
private:
    // Internal field (cell values)
    DimensionedField<Type, GeoMesh> internalField_;

    // Boundary field (patch values)
    GeometricBoundaryField<Type, PatchField, GeoMesh> boundaryField_;

    // Time tracking
    mutable label timeIndex_;
    mutable GeometricField* field0Ptr_;          // Old-time field
    mutable GeometricField* fieldPrevIterPtr_;   // Previous iteration
};
```

### Memory Architecture

The internal storage architecture follows a carefully optimized layout that reflects the topology of the computer mesh:

```
┌─────────────────────────────────────────────┐
│              GeometricField                 │
├─────────────────────┬───────────────────────┤
│   Internal Field    │   Boundary Field      │
│   (contiguous)      │   (per-patch)         │
│                     │                       │
│  [Cell 0]           │  Patch 0: [Face 0]    │
│  [Cell 1]           │          [Face 1]     │
│  ...                │          ...          │
│  [Cell N-1]         │                       │
│                     │  Patch 1: [Face 0]    │
│                     │          ...          │
└─────────────────────┴───────────────────────┘
```

**Internal Fields:**
- **Type**: Single contiguous `List<Type>`
- **Storage**: Values for all mesh cells
- **Advantages**:
  - Efficient vectorized operations
  - Optimal cache utilization
- **Usage**: Primary unknown quantities in CFD simulations typically stored at cell centers following a collocated grid arrangement

**Boundary Fields:**
- **Type**: `FieldField<PatchField, Type>`
- **Structure**: Hierarchical container managing boundary conditions per patch
- **Operation**: Each patch corresponds to a distinct geometric region of the mesh boundary and can maintain independent boundary condition types

### Boundary Field Architecture Benefits

| Feature | Description |
|---------|-------------|
| **Flexible Boundary Conditions** | Different patches can simultaneously use fixedValue, zeroGradient, mixed, or custom boundary conditions |
| **Memory Efficiency** | Requires storage for only boundary faces, avoiding allocation for interior faces |
| **Polymorphic Behavior** | Each patch field can inherit from specific boundary condition classes employing unique update algorithms |

---

## 5. Dimensional Analysis: The Safety Net

OpenFOAM integrates dimensional analysis directly into field operations through the `dimensionSet` class, enabling consistency checking at both compile-time and runtime for all mathematical operations.

### The dimensionSet Class

```cpp
// dimensionSet stores seven base dimensions:
// [MASS, LENGTH, TIME, TEMPERATURE, MOLES, CURRENT, LUMINOUS_INTENSITY]
class dimensionSet
{
    scalar exponents_[7];  // Exponents for each base dimension
};
```

### Base Dimensions and Examples

The dimensional system operates on seven SI base units, allowing complete representation of any physical quantity through exponent notation:

**Base Dimensions:**
- **Mass** $[M]$: kilogram (kg)
- **Length** $[L]$: meter (m)
- **Time** $[T]$: second (s)
- **Temperature** $[\Theta]$: kelvin (K)
- **Amount of Substance** $[N]$: mole (mol)
- **Electric Current** $[I]$: ampere (A)
- **Luminous Intensity** $[J]$: candela (cd)

**Dimension Examples:**

| Physical Quantity | Dimension Vector | Symbol | SI Unit |
|-------------------|------------------|---------|---------|
| **Velocity** | `[0 1 -1 0 0 0 0]` | $L^1 T^{-1}$ | m/s |
| **Pressure** | `[1 -1 -2 0 0 0 0]` | $M L^{-1} T^{-2}$ | N/m² |
| **Temperature** | `[0 0 0 1 0 0 0]` | $\Theta$ | K |
| **Force** | `[1 1 -2 0 0 0 0]` | $M L T^{-2}$ | N |
| **Energy** | `[1 2 -2 0 0 0 0]` | $M L^2 T^{-2}$ | J |
| **Dynamic Viscosity** | `[1 -1 -1 0 0 0 0]` | $M L^{-1} T^{-1}$ | Pa·s |

### Automatic Dimension Checking

OpenFOAM's dimensional analysis system provides automatic consistency verification through template metaprogramming:

```cpp
volScalarField p(
    IOobject("p", runTime.timeName(), mesh, IOobject::MUST_READ),
    mesh,
    dimensionSet(1, -1, -2, 0, 0, 0, 0)  // Pressure dimensions
);

volVectorField U(
    IOobject("U", runTime.timeName(), mesh, IOobject::MUST_READ),
    mesh,
    dimensionSet(0, 1, -1, 0, 0, 0, 0)  // Velocity dimensions
);

volScalarField rho(
    IOobject("rho", runTime.timeName(), mesh, IOobject::MUST_READ),
    mesh,
    dimensionSet(1, -3, 0, 0, 0, 0, 0)  // Density dimensions
);

// Automatic dimensional checking in mathematical operations
volScalarField dynamicPressure = 0.5 * rho * magSqr(U);  // ✓ Dimensionally consistent
// rho [M L^-3] * U^2 [L^2 T^-2] = [M L^-1 T^-2] = pressure dimensions

// Dimension error detection (compile-time or runtime)
// volScalarField invalid = p * U;  // ✗ Error: [M L^-1 T^-2] * [L T^-1] = [M L^0 T^-3]
```

### Dimensional Analysis in Navier-Stokes Equations

The dimensional analysis system extends to checking the consistency of entire equations, ensuring governing equations remain physically correct:

**Navier-Stokes Momentum Equation:**
$$\rho \frac{\partial \mathbf{u}}{\partial t} + \rho (\mathbf{u} \cdot \nabla) \mathbf{u} = -\nabla p + \mu \nabla^2 \mathbf{u} + \mathbf{f}$$

**Dimensional Analysis of Each Term:**
- **LHS** (Inertial terms): $[M L^{-3}][L T^{-2}] = [M L^{-2} T^{-2}]$
- **RHS** (Pressure gradient): $[L^{-1}][M L^{-1} T^{-2}] = [M L^{-2} T^{-2}]$
- **Viscous terms**: $[M L^{-1} T^{-1}][L^{-2}][L T^{-1}] = [M L^{-2} T^{-2}]$
- **Body force**: $[M L^{-2} T^{-2}]$ (force per unit volume)

**Result**: All terms have consistent dimensions: $[M L^{-2} T^{-2}]$ ✅

### Benefits of Dimensional Analysis System

This rigorous dimensional consistency checking:

- **Prevents implementation errors** in complex CFD simulations
- **Ensures mathematical correctness** throughout simulations
- **Validates multi-equation physics systems** that are coupled
- **Aids in debugging and development** by catching dimensional errors early

---

## 6. Volume vs. Surface Fields

### The Fundamental Distinction

A fundamental distinction in OpenFOAM's field system is between **volume fields** and **surface fields**. Volume fields (`vol*Field`) store values at cell centers and represent quantities integrated over control volumes, while surface fields (`surface*Field`) store values at face centers and represent fluxes or quantities integrated over control surface areas.

For a volume field $\phi$, the discrete approximation of a continuous field $\phi(\mathbf{x})$ is:

$$\phi(\mathbf{x}) \approx \phi_P \quad \text{for } \mathbf{x} \in V_P$$

Where:
- $\phi_P$ is the value stored at cell center $P$
- $V_P$ is the control volume surrounding that cell

Surface fields are particularly important for flux quantities, where the surface integral over a face is approximated as:

$$\int_{S_f} \mathbf{F} \cdot \mathbf{n}_f \, \mathrm{d}S \approx \mathbf{F}_f \cdot \mathbf{S}_f$$

Where:
- $\mathbf{F}_f$ is the surface field value at face center
- $\mathbf{S}_f = \mathbf{n}_f A_f$ is the face area vector

### Field Type Comparison

| Type | Location | Usage | Example |
|------|----------|-------|---------|
| **Volume Fields** (`vol*Field`) | Cell center values | Primary unknown fields | `volScalarField p` |
| **Surface Fields** (`surface*Field`) | Face center values | Flux terms, gradients | `surfaceScalarField phi` |
| **Point Fields** (`point*Field`) | Mesh vertices | Mesh deformation | `pointVectorField pointDisplacement` |

### Mathematical Relationship

The mathematical relationship between these fields:

$$\phi_f = \int_{S_f} \mathbf{u} \cdot \mathbf{n}_f \, \mathrm{d}S_f$$

Where:
- $\phi_f$ = surface flux at face $f$
- $\mathbf{u}$ = volume velocity field
- $\mathbf{n}_f$ = unit vector normal to face $f$
- $S_f$ = area of face $f$

### Usage Examples

```cpp
// Volume Field - for cell-centered quantities
volScalarField p("p", mesh, dimensionSet(1, -1, -2, 0, 0, 0, 0));

// Surface Field - for fluxes
surfaceScalarField phi("phi", fvc::interpolate(U) & mesh.Sf());

// Point Field - for mesh deformation
pointVectorField pointDisplacement("pointD", pointMesh);
```

---

## 7. Mathematical Tensor Rank Hierarchy

OpenFOAM fields are organized according to mathematical tensor rank, which determines transformation properties under coordinate rotations and algebraic behavior:

### Scalar Fields (Rank 0)

Represent quantities having magnitude only, without direction. Mathematically, they remain unchanged under coordinate transformations. Common scalar fields include:

- **Pressure**: $p(\mathbf{x},t)$
- **Temperature**: $T(\mathbf{x},t)$
- **Volume Fraction**: $\alpha(\mathbf{x},t)$
- **Turbulent Kinetic Energy**: $k(\mathbf{x},t)$

### Vector Fields (Rank 1)

Represent quantities having both magnitude and direction. They transform as first-order tensors under coordinate rotations. Key vector fields include:

- **Velocity**: $\mathbf{u}(\mathbf{x},t) = [u_x, u_y, u_z]$
- **Momentum**: $\rho\mathbf{u}(\mathbf{x},t)$
- **Force Density**: $\mathbf{f}(\mathbf{x},t)$
- **Heat Flux**: $\mathbf{q}(\mathbf{x},t)$

### Tensor Fields (Rank 2)

Represent linear operators that transform vectors to vectors. They transform as second-order tensors under coordinate rotations. Important tensor fields include:

- **Velocity Gradient Tensor**: $\nabla\mathbf{u} = \frac{\partial u_i}{\partial x_j}$
- **Strain Rate Tensor**: $\mathbf{S} = \frac{1}{2}(\nabla\mathbf{u} + (\nabla\mathbf{u})^T)$
- **Stress Tensor**: $\boldsymbol{\tau}$
- **Viscosity Tensor**: $\boldsymbol{\mu}$

### Symmetric Tensor Fields

Second-order tensors that are symmetric, meaning $\mathbf{A}_{ij} = \mathbf{A}_{ji}$. These appear frequently in fluid mechanics:

- **Reynolds Stress Tensor**: $\mathbf{R} = \overline{\mathbf{u}'\mathbf{u}'}$
- **Eddy Viscosity Tensor**: $\boldsymbol{\mu}_t$
- **Strain Rate Tensor**: $\mathbf{S}$ (always symmetric)

### Spherical Tensor Fields

Diagonal tensors with equal diagonal components, representing isotropic quantities:

- **Identity Tensor**: $\mathbf{I}$ (diagonal components = 1)
- **Pressure Stress Support**: $p\mathbf{I}$
- **Isotropic Turbulent Stress**: $\frac{2}{3}k\mathbf{I}$

---

## 8. Performance and Memory Architecture

### Memory Layout Considerations

**Contiguous Internal Storage** for optimal cache efficiency:

```cpp
class GeometricField
{
private:
    // Internal field - tightly packed for cache efficiency
    Field<Type> field_;

    // Boundary fields - separate allocation, organized by patch
    PtrList<PatchField<Type>> boundaryField_;
};
```

**Memory Access Patterns:**
- **Internal field access**: $O(N)$ with excellent spatial locality
- **Boundary field access**: $O(N_{boundary})$ with grouping by patch
- **Typical ratio**: $N_{boundary} \approx 0.1 \times N$ for well-posed problems

### Expression Template Optimization

The `tmp<T>` class implements **expression template-like optimization**:

```cpp
// Without tmp<T> - suboptimal implementation
volScalarField a = b + c + d;  // Multiple temporary objects created

// With tmp<T> - optimized implementation
volScalarField a = b + c + d;  // Single evaluation, minimal temporaries
```

### Performance Benefits

| Feature | Optimization Method | Impact |
|---------|---------------------|--------|
| **Contiguous Memory** | Tightly packed internal field values | Better cache efficiency |
| **Lazy Evaluation** | `tmp` class for expression templates | Reduced temporary objects |
| **SIMD Optimization** | Vector operations | Uses processor vector instructions |
| **Parallel Communication** | Non-blocking communication patterns | Reduced processor data transfer |

---

## 9. Boundary Conditions: More Than Edge Cells

OpenFOAM field boundaries are sophisticated objects that can:

- **Enforce physical constraints**: `fixedValue`, `zeroGradient`, `fixedFluxPressure`
- **Handle complex geometries**: `wall`, `symmetry`, `cyclic`, `empty`
- **Modify dynamically**: `timeVaryingMappedFixedValue`, `activePressureForceBaffleVelocity`

### Boundary Condition Example

```cpp
// Example boundary condition specification
dimensions      [0 1 -1 0 0 0 0];                    // Velocity: [m/s]
internalField   uniform (0 0 0);                   // Initial internal value

boundaryField
{
    inlet
    {
        type            fixedValue;                 // Specified velocity
        value           uniform (10 0 0);           // 10 m/s in x-direction
    }

    outlet
    {
        type            zeroGradient;               // No normal variation at boundary
    }

    walls
    {
        type            noSlip;                     // Zero velocity at walls
    }
}
```

### Major Boundary Condition Types

| Type | Usage | Equation |
|------|-------|----------|
| `fixedValue` | Specified value at boundary | $\phi = \phi_{\text{specified}}$ |
| `zeroGradient` | Zero normal derivative | $\frac{\partial \phi}{\partial n} = 0$ |
| `noSlip` | Zero velocity at walls | $\mathbf{U} = 0$ |
| `symmetry` | Symmetry | $\frac{\partial \phi}{\partial n} = 0$, $\mathbf{U}_n = 0$ |

---

## 10. Time-Dependent Fields

### Temporal Discretization

OpenFOAM's field system manages time-dependent quantities through specialized field types and temporal operators. Time integration schemes are applied to fields to advance solutions from one time step to the next.

**Time-Dependent Field Types:**

```cpp
// Old-time level fields (n-1)
volScalarField p_old = p.oldTime();

// Old-old-time level fields (n-2) for second-order schemes
volScalarField p_oldOld = p.oldTime().oldTime();

// Rate of change fields
volScalarField dU_dt = fvc::ddt(U);

// Implicitly time-derivative maintained
fvScalarMatrix pDDT = fvm::ddt(p);
```

### Time Integration Schemes

**Euler Explicit** (First-order):
$$\frac{\partial \phi}{\partial t} \approx \frac{\phi^{n+1} - \phi^n}{\Delta t}$$

**Euler Implicit** (First-order, unconditionally stable):
$$\frac{\partial \phi}{\partial t} \approx \frac{\phi^{n+1} - \phi^n}{\Delta t}$$

**Crank-Nicolson** (Second-order):
$$\frac{\partial \phi}{\partial t} \approx \frac{2\phi^{n+1} - \phi^n - \phi^{n-1}}{\Delta t}$$

**Backward Differencing** (Second-order):
$$\frac{\partial \phi}{\partial t} \approx \frac{3\phi^{n+1} - 4\phi^n + \phi^{n-1}}{2\Delta t}$$

---

## 11. Field Interpolation

OpenFOAM provides automatic interpolation for seamless field transformation:

```cpp
// Interpolation from cell centers to faces
surfaceScalarField phi = linearInterpolate(U) & mesh.Sf();  // Flux through faces

// Interpolation from cells to points for visualization
pointScalarField p_points = linearInterpolate(p);

// Converting volume fields to surface fields
surfaceVectorField Uf = linearInterpolate(U);
```

### Interpolation Types

| Method | Accuracy | Stability | Speed |
|--------|----------|-----------|-------|
| Linear | Second-order | Good | Fast |
| Upwind | First-order | Excellent | Very Fast |
| Central | Second-order | Moderate | Moderate |
| Quadratic | Higher-order | Moderate | Slow |

---

## 12. Key Architectural Patterns

### Policy-Based Design: PatchField Parameter

The `PatchField` hierarchy exemplifies policy-based design, where boundary behavior is parameterized through template specialization:

```cpp
template<class Type>
class PatchField
:
    public Field<Type>,
    public refCount
{
    // Policy interface for boundary conditions
    virtual void updateCoeffs() = 0;
    virtual void evaluate() = 0;
};
```

**This design enables:**
- Compile-time customization of boundary condition behavior
- Consistent interface maintenance
- Addition of new boundary condition types without modifying main field classes
- Support for Open-Closed Principle

### Composite Pattern: GeometricField Structure

The `GeometricField` class uses the composite pattern by combining multiple field components into a single interface:

$$\text{GeometricField<Type, PatchField, GeoMesh>} = \underbrace{\text{Field<Type>}}_{\text{Internal}} + \underbrace{\text{Field<PatchField<Type>>}}_{\text{Boundary}}$$

### RAII and Reference Counting: tmp<T> Management

The `tmp<T>` template class uses RAII (Resource Acquisition Is Initialization) combined with reference counting for efficient temporary field object management:

```cpp
template<class T>
class tmp
{
    T* ptr_;
    mutable bool refPtr_;

public:
    // Automatic cleanup when reference count reaches zero
    ~tmp()
    {
        if (ptr_ && !refPtr_) delete ptr_;
    }

    // Move semantics for efficient transfer
    tmp(tmp<T>&& t) noexcept;
    tmp<T>& operator=(tmp<T>&& t) noexcept;
};
```

---

## 📚 Further Reading

### Core Header Files

1. **`GeometricField.H`**: Base field class for all OpenFOAM fields
2. **`DimensionedField.H`**: Internal fields with dimensional consistency
3. **`Field.H`**: Mathematical operations on lists
4. **`dimensionSet.H`**: Dimensional analysis system
5. **`tmp.H`**: Reference-counted temporary class

### Key Concepts

- **Type Safety**: Compile-time checking prevents mixing incompatible field types
- **Dimensional Consistency**: Automatic verification of physical units
- **Memory Efficiency**: Contiguous storage for optimal cache performance
- **Parallel Computation**: Distributed operations across multiple processors

---

## 🔄 Next Steps

Proceed to [[Section 6.2: Basic Field Algebra]] to learn about mathematical operations on fields.

### What You'll Learn Next

**Field Operations**
- **Scalar Field Operations**: Addition, subtraction, multiplication, and division of `volScalarField` objects
- **Vector Field Mathematics**: Dot products, cross products, and calculus operations on `volVectorField` objects
- **Tensor Field Manipulation**: Contractions, multiplications, and advanced tensor algebra for `volTensorField` objects

### Mathematical Foundations

Mathematical operations in OpenFOAM are built upon the finite volume discretization framework:

$$\text{Field Operation: } (\phi \psi)_P = \phi_P \psi_P$$

$$\text{Gradient Operation: } \nabla \phi = \frac{1}{V_P} \sum_{f} \phi_f \mathbf{S}_f$$

$$\text{Divergence Operation: } \nabla \cdot \boldsymbol{\phi} = \frac{1}{V_P} \sum_{f} \boldsymbol{\phi}_f \cdot \mathbf{S}_f$$

---

## 💡 Summary

OpenFOAM's sophisticated field type system transforms it from a simple numerical equation solver into a powerful computational physics framework that:

- **Enables natural mathematical expression**
- **Guarantees dimensional consistency**
- **Maximizes computational efficiency**
- **Handles complex boundary and time management**
- **Provides automatic field interpolation and transformation**

This field system forms the robust foundation for reliable and complex CFD simulations in OpenFOAM.
