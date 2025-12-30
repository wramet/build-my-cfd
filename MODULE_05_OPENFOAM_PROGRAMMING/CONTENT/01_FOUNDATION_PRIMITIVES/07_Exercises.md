# Foundation Primitives - Exercises

แบบฝึกหัดสำหรับ OpenFOAM Primitives — ลงมือทำเพื่อเข้าใจจริง

---

## 🎯 Learning Objectives

**What You Will Learn:**
- ✅ Practice using basic OpenFOAM primitive types (scalar, vector, tensor)
- ✅ Understand dimensioned types and unit checking
- ✅ Master tensor operations and invariants
- ✅ Work with Fields and perform statistical operations
- ✅ Compile and run custom OpenFOAM applications
- ✅ Debug common compilation errors
- ✅ Apply the 3W Framework (What/Why/How) to practical problems

---

## 📋 Why These Exercises Matter

### What Are These Exercises?
Practical coding problems designed to reinforce your understanding of OpenFOAM's fundamental data types and operations.

### Why Complete Them?
- **Reading alone is insufficient** — You must write code yourself
- **Better to fail during exercises** than in production simulations
- **Compile and run real code** → Understand error messages deeply
- **Build muscle memory** for common OpenFOAM patterns

### How to Approach Them?
1. Read the problem statement carefully
2. Write the code yourself before looking at solutions
3. Compile and run to verify your solution
4. Experiment with modifications
5. Review solutions and compare approaches
6. Complete Challenge Problems for advanced practice

---

## Exercise 1: Basic Types

### 🎯 What You Will Learn
- Declare and initialize scalar and vector types
- Perform dot product and cross product operations
- Calculate vector magnitude
- Use OpenFOAM's operator overloading (`&` for dot, `^` for cross)

### 📝 Task

สร้างโปรแกรมที่ใช้ OpenFOAM primitives

```cpp
#include "fvCFD.H"

int main(int argc, char *argv[])
{
    // 1. Create scalars
    scalar a = 5.0;
    scalar b = 3.0;

    // 2. Create vectors
    vector v1(1, 2, 3);
    vector v2(4, 5, 6);

    // 3. Operations
    scalar dot = v1 & v2;      // Dot product
    vector cross = v1 ^ v2;    // Cross product
    scalar mag_v1 = mag(v1);   // Magnitude

    Info << "Dot: " << dot << endl;
    Info << "Cross: " << cross << endl;
    Info << "Mag: " << mag_v1 << endl;

    return 0;
}
```

### 🎯 Expected Output

```
Dot: 32
Cross: (-3 6 -3)
Mag: 3.74166
```

### 💡 Key Concepts

| Operation | Operator | Input Type | Output Type | Physical Meaning |
|-----------|----------|------------|-------------|------------------|
| Dot Product | `&` | vector × vector | scalar | Projection, work, angle |
| Cross Product | `^` | vector × vector | vector | Torque, rotation, area |
| Magnitude | `mag()` | vector | scalar | Length, amplitude |

### ⚠️ Common Pitfalls
- **Wrong operator**: Using `*` instead of `&` for dot product
- **Initialization**: Forgetting to initialize vector components
- **Type confusion**: Expecting `mag()` to return a vector

### 🚀 Challenge Problem

<details>
<summary><b>Challenge: Vector Angle Calculator</b></summary>

**Task**: Write a function that calculates the angle between two vectors using dot product.

```cpp
#include "fvCFD.H"
#include <cmath>

scalar angleBetween(const vector& a, const vector& b)
{
    // Your code here
    // Hint: Use dot product, magnitude, and acos()
}

int main(int argc, char *argv[])
{
    vector v1(1, 0, 0);
    vector v2(1, 1, 0);
    
    scalar angle = angleBetween(v1, v2);
    Info << "Angle (rad): " << angle << endl;
    Info << "Angle (deg): " << angle * 180.0 / constant::mathematical::pi << endl;
    
    return 0;
}
```

**Expected Output**: Angle should be 45 degrees (π/4 radians)
</details>

---

## Exercise 2: Dimensioned Types

### 🎯 What You Will Learn
- Create dimensioned scalars with proper units
- Perform dimensional analysis automatically
- Verify dimensionless quantities
- Understand OpenFOAM's dimension system

### 📝 Task

สร้าง dimensioned scalars และตรวจสอบ dimension checking

```cpp
#include "fvCFD.H"

int main(int argc, char *argv[])
{
    // Dimensioned scalars
    dimensionedScalar rho("rho", dimDensity, 1000);
    dimensionedScalar U("U", dimVelocity, 10);
    dimensionedScalar L("L", dimLength, 0.1);
    dimensionedScalar mu("mu", dimDynamicViscosity, 0.001);

    // Calculate Reynolds number
    dimensionedScalar Re = rho * U * L / mu;

    Info << "Re = " << Re << endl;
    Info << "Is dimensionless? " << Re.dimensions().dimensionless() << endl;

    return 0;
}
```

### 🎯 Expected Output

```
Re = Re [0 0 0 0 0 0 0] 1e+06
Is dimensionless? 1
```

### 💡 Key Concepts

**Dimension System** - OpenFOAM uses 7 base dimensions:

| Symbol | Dimension | Unit |
|--------|-----------|------|
| Mass | [1 0 0 0 0 0 0] | kg |
| Length | [0 1 0 0 0 0 0] | m |
| Time | [0 0 1 0 0 0 0] | s |
| Temperature | [0 0 0 1 0 0 0] | K |
| Moles | [0 0 0 0 1 0 0] | mol |
| Current | [0 0 0 0 0 1 0] | A |
| Luminous | [0 0 0 0 0 0 1] | cd |

**Derived Dimensions**:
- `dimDensity` = mass/length³ = [1 -3 0 0 0 0 0]
- `dimVelocity` = length/time = [0 1 -1 0 0 0 0]
- `dimDynamicViscosity` = mass/(length·time) = [1 -1 -1 0 0 0 0]

### 🔍 Why Dimension Checking Matters

**What**: Automatic verification that equations are dimensionally consistent

**Why**: 
- **Prevents errors** like adding velocity to pressure
- **Self-documenting** - Units are explicit in code
- **Physics verification** - Catches wrong equations

**How**: OpenFOAM tracks dimensions at **compile-time** for dimensioned types

### ⚠️ Common Pitfalls
- **Wrong dimension**: Using `dimPressure` instead of `dimStress` (same units, different meaning)
- **Missing dimension**: Using plain `scalar` when physical quantity intended
- **Dimension mismatch**: Forgetting that `sqrt()` affects dimensions

### 🚀 Challenge Problem

<details>
<summary><b>Challenge: Drag Force Calculator</b></summary>

**Task**: Calculate drag force using drag equation and verify dimensions.

```cpp
#include "fvCFD.H"

int main(int argc, char *argv[])
{
    // Given: Fluid properties
    dimensionedScalar rho("rho", dimDensity, 1.225);      // Air density (kg/m³)
    dimensionedScalar U("U", dimVelocity, 50.0);           // Velocity (m/s)
    dimensionedScalar A("A", dimArea, 1.0);                // Cross-sectional area (m²)
    dimensionedScalar Cd("Cd", dimless, 0.47);             // Drag coefficient (sphere)

    // TODO: Calculate drag force Fd = 0.5 * rho * U² * A * Cd
    // Verify that result has dimensions of force (mass*length/time²)

    Info << "Drag force: " << Fd << endl;
    Info << "Is force? " << (Fd.dimensions() == dimForce) << endl;

    return 0;
}
```

**Hint**: You'll need to define `dimArea` and `dimForce` or use existing equivalents.
</details>

---

## Exercise 3: Tensor Operations

### 🎯 What You Will Learn
- Create symmetric tensors for stress/strain representation
- Calculate tensor invariants (trace, determinant)
- Compute deviatoric (dev) and volumetric parts
- Understand tensor operations in CFD

### 📝 Task

สร้าง tensor และทำ operations

```cpp
#include "fvCFD.H"

int main(int argc, char *argv[])
{
    // Create symmetric tensor (stress)
    symmTensor sigma
    (
        100, 20, 10,    // xx, xy, xz
             80, 5,     // yy, yz
                 60     // zz
    );

    // Operations
    scalar trace = tr(sigma);           // Trace
    scalar det = Foam::det(sigma);      // Determinant
    symmTensor dev_sigma = dev(sigma);  // Deviatoric part

    Info << "Trace: " << trace << endl;
    Info << "Det: " << det << endl;
    Info << "Deviatoric: " << dev_sigma << endl;

    return 0;
}
```

### 🎯 Expected Output

```
Trace: 240
Det: 492000
Deviatoric: (-20 20 10 0 5 -40)
```

### 💡 Key Concepts

**Tensor Decomposition**:
```
σ = σ' + σ_vol
where:
  σ' = dev(σ)          (Deviatoric - shape change)
  σ_vol = (1/3)tr(σ)I  (Volumetric - volume change)
```

**Invariants** (coordinate-independent quantities):

| Invariant | Formula | Physical Meaning |
|-----------|---------|------------------|
| Trace | `tr(σ)` = σxx + σyy + σzz | Sum of normal stresses |
| Determinant | `det(σ)` | Volume change factor |
| Eigenvalues | `eigenValues(σ)` | Principal stresses |

**Tensor Types**:

| Type | Components | Use Case |
|------|------------|----------|
| `tensor` | 9 (full) | General stress, rotation matrices |
| `symmTensor` | 6 (symmetric) | Stress, strain rate |
| `sphericalTensor` | 1 (diagonal) | Isropic pressure, turbulence k |

### 🔍 Why Deviatoric Part?

**What**: Deviatoric tensor = total tensor - (1/3)trace(I)

**Why**:
- **Deformation vs. dilation**: Deviatoric causes shape change, volumetric causes volume change
- **Yield criteria**: Plasticity depends on deviatoric stress (von Mises)
- **Turbulence**: Reynolds stress anisotropy

**How**: Use `dev(tensor)` function

### ⚠️ Common Pitfalls
- **Wrong constructor**: `symmTensor(a,b,c,d,e,f)` takes 6 components in specific order
- **Namespace conflict**: `det()` needs `Foam::` prefix in some versions
- **Type mismatch**: Trying to assign `tensor` to `symmTensor`

### 🚀 Challenge Problem

<details>
<summary><b>Challenge: Principal Stresses</b></summary>

**Task**: Calculate eigenvalues (principal stresses) of the stress tensor.

```cpp
#include "fvCFD.H"

int main(int argc, char *argv[])
{
    // Stress tensor (MPa)
    symmTensor sigma
    (
        100, 50, 30,    // xx, xy, xz
             80, 20,    // yy, yz
                 60     // zz  (all in MPa)
    );

    // TODO: Find principal stresses (eigenvalues)
    // Hint: Use eigenValues() function
    
    // TODO: Calculate von Mises stress
    // σ_vm = sqrt(3/2 * dev(σ) : dev(σ))
    // where ":" is double contraction
    
    Info << "Principal stresses: " << eigenValues << endl;
    Info << "Von Mises: " << vonMises << " MPa" << endl;

    return 0;
}
```

**Physical Meaning**: Principal stresses are the normal stresses on planes where shear stress is zero. Von Mises stress predicts yielding in metals.
</details>

---

## Exercise 4: Lists and Fields

### 🎯 What You Will Learn
- Create and populate scalar fields
- Use `forAll` macro for looping
- Perform statistical operations (sum, max, average)
- Understand field operations for CFD

### 📝 Task

สร้าง Field และทำ operations

```cpp
#include "fvCFD.H"

int main(int argc, char *argv[])
{
    // Create scalar field
    scalarField p(10, 1.0);  // 10 elements, value 1.0

    // Modify
    forAll(p, i)
    {
        p[i] = sqr(i);  // p[i] = i^2
    }

    // Statistics
    Info << "Sum: " << sum(p) << endl;
    Info << "Max: " << max(p) << endl;
    Info << "Average: " << average(p) << endl;

    return 0;
}
```

### 🎯 Expected Output

```
Sum: 285
Max: 81
Average: 28.5
```

### 💡 Key Concepts

**Field Types** - Template containers for mesh data:

| Type | Declaration | Use Case |
|------|-------------|----------|
| `scalarField` | `Field<scalar>` | Pressure, temperature, volume fraction |
| `vectorField` | `Field<vector>` | Velocity, position |
| `tensorField` | `Field<tensor>` | Stress, strain rate |

**Loop Macros**:

| Macro | Equivalent | Use When |
|-------|------------|----------|
| `forAll(list, i)` | `for(label i=0; i<list.size(); i++)` | Forward loop |
| `forAllReverse(list, i)` | `for(label i=list.size()-1; i>=0; i--)` | Backward loop |

**Field Operations**:

| Operation | Function | Returns |
|-----------|----------|---------|
| Sum | `sum(field)` | Sum of all elements |
| Product | `prod(field)` | Product of all elements |
| Statistics | `max()`, `min()`, `average()` | Extremes and mean |
| Transform | `pow(field, n)`, `sqr(field)` | Element-wise math |

### 🔍 Why Fields Instead of Arrays?

**What**: `Field<T>` is OpenFOAM's templated container

**Why**:
- **Automatic memory management** - No manual allocation
- **Operator overloading** - `field1 + field2` works element-wise
- **Built-in operations** - Statistics, transformations, searching
- **Parallel-ready** - Decomposition for MPI built-in

**How**: Declare as `Field<Type>(size, initialValue)`

### ⚠️ Common Pitfalls
- **Index bounds**: `forAll` prevents this, but `[]` doesn't check bounds
- **Empty fields**: Calling `sum()` on empty field returns 0 (not error)
- **Type mismatch**: `scalarField f = vectorField(...)` won't compile

### 🚀 Challenge Problem

<details>
<summary><b>Challenge: Field Operations and Normalization</b></summary>

**Task**: Create a pressure field from a function, then normalize it.

```cpp
#include "fvCFD.H"

int main(int argc, char *argv[])
{
    // Create mesh-like field (cell centers)
    const label nCells = 100;
    scalarField x(nCells, 0.0);
    scalarField y(nCells, 0.0);
    
    // Initialize coordinates (0 to 1)
    forAll(x, i)
    {
        x[i] = scalar(i) / nCells;
        y[i] = Foam::sin(2.0 * constant::mathematical::pi * x[i]);
    }
    
    // TODO: Create pressure field p(x) = 1 + 0.5*sin(2πx)
    
    // TODO: Calculate statistics
    // - Mean pressure
    // - RMS pressure
    // - Max pressure and its location
    
    // TODO: Normalize to [0, 1] range
    // p_norm = (p - p_min) / (p_max - p_min)
    
    Info << "Original field:" << tab << p << endl;
    Info << "Normalized field:" << tab << p_norm << endl;

    return 0;
}
```

**Application**: This pattern is used in CFD for:
- Normalizing residuals
- Non-dimensionalization
- Visualization scaling
</details>

---

## Exercise 5: Compile Custom Application

### 🎯 What You Will Learn
- Structure of OpenFOAM applications
- Create `Make/files` and `Make/options`
- Compile using `wmake`
- Link against OpenFOAM libraries

### 📝 Task

#### Make/files

```
exercise.C

EXE = $(FOAM_USER_APPBIN)/exercise
```

#### Make/options

```
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude

EXE_LIBS = \
    -lfiniteVolume
```

#### Compile

```bash
wmake
```

### 💡 Key Concepts

**Directory Structure**:
```
exercise/
├── exercise.C          # Source code
└── Make/
    ├── files           # Source files and executable name
    └── options         # Include paths and libraries
```

**Make/files**:
- **First line**: Source files (`.C` files)
- **EXE**: Executable name and location
  - `$(FOAM_USER_APPBIN)` → `$WM_PROJECT_USER_DIR/platforms/.../bin/`

**Make/options**:
- **EXE_INC**: Include paths (search directories for headers)
- **EXE_LIBS**: Libraries to link against

**Common Libraries**:

| Library | Use For |
|---------|---------|
| `lfiniteVolume` | FVM operations, fvMesh |
| `lmeshTools` | Mesh manipulation, topological changes |
| `ltriSurface` | Surface mesh, STL files |
| `lODE` | Ordinary differential equation solvers |
| `lregionModels` | Region modeling (porous, heat transfer) |

### 🔍 Build Process

**What**: `wmake` compiles OpenFOAM applications

**Why**: 
- **Dependency management** - Automatically recompiles changed files
- **Platform-aware** - Handles different compilers/OS
- **Consistent** - Same command across all OpenFOAM code

**How**: 
1. Parse `Make/files` for sources
2. Check dependencies (header modifications)
3. Compile `.C` → `.o` (object files)
4. Link `.o` files with libraries → executable
5. Install to `$(FOAM_APPBIN)`

### ⚠️ Common Pitfalls

| Error | Cause | Solution |
|-------|-------|----------|
| `error: fvCFD.H: No such file` | Missing include | Add `-I$(LIB_SRC)/finiteVolume/lnInclude` |
| `undefined reference to Foam::...` | Missing library | Add library to `EXE_LIBS` |
| `wmake error: ...` | Syntax in Make files | Check spaces/tabs, use backslash for line continuation |

### 🚀 Challenge Problem

<details>
<summary><b>Challenge: Create a Utility</b></summary>

**Task**: Create a utility that reads a field file and prints statistics.

**Directory structure**:
```
fieldStats/
├── fieldStats.C
└── Make/
    ├── files
    └── options
```

**fieldStats.C skeleton**:
```cpp
#include "fvCFD.H"

int main(int argc, char *argv[])
{
    // TODO: Add argument checking
    // TODO: Read time from command line
    // TODO: Load mesh
    // TODO: Read pressure field
    // TODO: Calculate and print:
    //   - Min, max, average pressure
    //   - Cell count
    //   - Boundedness check (negative p?)
    
    Info << "\nField Statistics:\n"
         << "  Cells: " << mesh.nCells() << nl
         << "  Min p: " << min(p) << nl
         << "  Max p: " << max(p) << nl
         << "  Avg p: " << average(p) << nl
         << endl;

    return 0;
}
```

**Usage**: `fieldStats <caseDir> -time 0.5`

**Hint**: Look at existing utilities in `$FOAM_APP/utilities/` for examples of reading cases.
</details>

---

## 📊 Solutions Summary

| Exercise | Key Concepts | Related Files |
|----------|--------------|---------------|
| 1 | scalar, vector, `&`, `^`, `mag()` | [02_Basic_Primitives.md](02_Basic_Primitives.md) |
| 2 | dimensionedScalar, dimensions, unit checking | [03_Dimensioned_Types_Intro.md](03_Dimensioned_Types_Intro.md) |
| 3 | tensor, symmTensor, invariants, dev() | [02_Basic_Primitives.md](02_Basic_Primitives.md) |
| 4 | Field, forAll, statistics, element-wise ops | [05_Containers.md](05_Containers.md) |
| 5 | wmake, Make/files, Make/options, libraries | [06_Summary.md](06_Summary.md) |

---

## 🧠 Concept Check

<details>
<summary><b>1. & และ ^ ต่างกันอย่างไร?</b></summary>

- **& (ampersand)**: Dot product (inner product) → returns **scalar**
  - Formula: **a** · **b** = |**a**| |**b**| cos(θ)
  - Use for: projection, work, angle calculation
  
- **^ (caret)**: Cross product → returns **vector**
  - Formula: **a** × **b** = |**a**| |**b**| sin(θ) **n̂**
  - Use for: torque, area normal, rotation axis
</details>

<details>
<summary><b>2. ทำไม dimensionedScalar ดีกว่า scalar?</b></summary>

เพราะ **tracks units automatically** → ป้องกัน errors จาก dimension mismatch

**Scalar problems**:
- ❌ No unit information
- ❌ Can add pressure to velocity (nonsense)
- ❌ Hard to debug wrong equations

**DimensionedScalar advantages**:
- ✅ Units encoded in type
- ✅ Compile-time checking of equations
- ✅ Self-documenting code
- ✅ Catches physics errors early

**Example**:
```cpp
dimensionedScalar p("p", dimPressure, 101325);
dimensionedScalar U("U", dimVelocity, 10.0);
scalar wrong = p + U;  // ❌ Compilation error!
```
</details>

<details>
<summary><b>3. forAll macro ทำอะไร?</b></summary>

**Loop over all elements**: `forAll(field, i)` = `for(label i=0; i<field.size(); i++)`

**Advantages**:
- ✅ Cleaner syntax
- ✅ Prevents off-by-one errors
- ✅ Automatically gets correct size
- ✅ Standard OpenFOAM idiom

**Variants**:
```cpp
forAll(list, i)              // Forward loop
forAllReverse(list, i)       // Backward loop
```
</details>

<details>
<summary><b>4. symmTensor และ tensor ต่างกันอย่างไร?</b></summary>

| Property | tensor | symmTensor |
|----------|--------|------------|
| Components | 9 (full 3×3) | 6 (unique components) |
| Memory | 9 scalars | 6 scalars |
| Symmetry | Can be asymmetric | Always symmetric |
| Use case | Rotation, gradient | Stress, strain rate |

**symmTensor storage** (6 components):
```
(xx, xy, xz,
     yy, yz
         zz)
```
Equivalent to:
```
(xx, xy, xz
 xy, yy, yz
 xz, yz, zz)
```

**Use symmTensor when**:
- Tensor is physically symmetric (stress, strain)
- Want to save memory (33% reduction)
- Working with turbulence models

**Use tensor when**:
- Need full asymmetry (velocity gradient)
- Rotation matrices
- General transformations
</details>

<details>
<summary><b>5. wmake ทำอะไรบ้าง?</b></summary>

**What**: OpenFOAM's build system (wrapper around make)

**Steps**:
1. **Parse** `Make/files` for source files
2. **Check** file dependencies (header modifications)
3. **Compile** `.C` → `.o` using compiler rules
4. **Link** object files with libraries
5. **Install** to target directory

**Advantages over make**:
- ✅ Automatic dependency generation
- ✅ Platform detection (compiler, OS)
- ✅ Consistent flags across OpenFOAM
- ✅ Parallel compilation support

**Common commands**:
```bash
wmake          # Build current directory
wclean         # Clean build files
wmake all      # Build all subdirectories
```
</details>

---

## 🔗 Cross-References

### Within This Module
- **Basic Primitives**: [02_Basic_Primitives.md](02_Basic_Primitives.md) - Type definitions
- **Dimensioned Types**: [03_Dimensioned_Types_Intro.md](03_Dimensioned_Types_Intro.md) - Unit system
- **Containers**: [05_Containers.md](05_Containers.md) - Field operations

### Related Modules
- **Finite Volume Method**: Uses fields for mesh data
- **Boundary Conditions**: Dimension checking prevents BC errors
- **Turbulence Modeling**: Tensor operations for Reynolds stress

---

## 🎓 Key Takeaways

### What You Learned
1. **Basic Types**: OpenFOAM provides optimized scalar, vector, tensor types with operator overloading
2. **Dimensioned Types**: Automatic unit checking prevents physics errors
3. **Tensors**: Stress/strain representation with invariants and decomposition
4. **Fields**: Container classes for mesh data with built-in operations
5. **Build System**: wmake handles compilation consistently

### Why It Matters
- **Type safety** → Fewer runtime errors
- **Unit consistency** → Correct equations
- **Tensor math** → CFD fundamentals
- **Field operations** → Mesh data manipulation
- **Build process** → Create custom tools

### How to Apply
1. **Always use dimensioned types** for physical quantities
2. **Use forAll** instead of raw loops
3. **Check dimensions** when debugging
4. **Build incrementally** → Compile early, compile often
5. **Study utilities** → Learn from `$FOAM_APP/utilities/`

---

## 📚 Further Reading

### OpenFOAM Source Code
- `$FOAM_SRC/OpenFOAM/fields/` - Field implementations
- `$FOAM_SRC/OpenFOAM/primitives/` - Type definitions
- `$FOAM_APP/utilities/` - Example applications

### External Resources
- **OpenFOAM Programmer's Guide**: Chapter 3 - Fields and Dimensions
- **CFD Online**: OpenFOAM programming forums
- **Source code documentation**: `doxygen` docs in `$FOAM_DOC`

---

## 🏁 Next Steps

After completing these exercises:
1. **Review** [00_Overview.md](00_Overview.md) for module context
2. **Practice** with your own mini-projects
3. **Explore** OpenFOAM utility source code
4. **Proceed to** [02_Basic_Primitives.md](02_Basic_Primitives.md) for deeper understanding
5. **Challenge yourself** with the advanced problems above

**Remember**: The best way to learn OpenFOAM programming is to:
- ✅ Read the code
- ✅ Write the code
- ✅ Break the code
- ✅ Fix the code
- ✅ Repeat