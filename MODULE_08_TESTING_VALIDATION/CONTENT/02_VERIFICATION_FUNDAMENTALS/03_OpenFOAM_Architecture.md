# OpenFOAM Architecture for Testing

# สถาปัตยกรรม OpenFOAM สำหรับการทดสอบ

---

## Overview

> เข้าใจโครงสร้างภายใน OpenFOAM เพื่อออกแบบและดำเนินการทดสอบได้อย่างมีประสิทธิภาพ

Understanding OpenFOAM's internal architecture is essential for designing effective verification tests. This module explores how the codebase is organized and how different components relate to testing strategies.

**Learning Objectives:**
- Understand OpenFOAM's directory structure and core library organization
- Identify key classes that are critical for verification testing
- Learn how to access and test internal components through RTS and other mechanisms
- Apply architectural knowledge to design comprehensive test suites
- Recognize entry points for testing at different abstraction levels

---

## What: Architecture Overview

### Directory Structure

OpenFOAM's codebase is organized hierarchically, separating core libraries from applications and test infrastructure:

```
$WM_PROJECT_DIR/
├── src/                           # Core libraries
│   ├── OpenFOAM/                  # Primitives, containers, fields
│   │   ├── fields/                # Field classes (volScalarField, etc.)
│   │   ├── matrices/              # Matrix classes (fvMatrix, etc.)
│   │   ├── db/                    # Database, Time, IO
│   │   └── memory/                # Memory management
│   ├── finiteVolume/              # FV method implementation
│   │   ├── fvMesh/                # Mesh structure
│   │   ├── fvc/                   # Explicit operators (fvc::div, etc.)
│   │   ├── fvm/                   # Implicit operators (fvm::div, etc.)
│   │   └── interpolation/         # Interpolation schemes
│   ├── meshTools/                 # Mesh manipulation tools
│   ├── sampling/                  # Field sampling utilities
│   └── conversion/                # Format conversion tools
├── applications/
│   ├── solvers/                   # Solver applications
│   │   ├── incompressible/        # Incompressible flow solvers
│   │   ├── compressible/          # Compressible flow solvers
│   │   ├── multiphase/            # Multiphase solvers
│   │   └── heatTransfer/          # Heat transfer solvers
│   └── utilities/                 # Utility applications
│       ├── mesh/                  # Mesh generation/manipulation
│       ├── pre-processing/        # Pre-processing tools
│       └── post-processing/       # Post-processing tools
└── tutorials/                     # Tutorial cases
    ├── basic/                     # Basic tutorials
    ├── heatTransfer/              # Heat transfer examples
    └── multiphase/                # Multiphase examples
```

**Key Testing Implications:**
- **Source libraries** (`src/`) contain the core functionality that needs verification
- **Solvers** (`applications/solvers/`) provide integration test targets
- **Utilities** (`applications/utilities/`) offer pre-built testing tools

### Core Class Hierarchy

```cpp
// Base class hierarchy
GeometricField<Type>
├── volScalarField (cell-centered scalar)
├── volVectorField (cell-centered vector)
└── surfaceScalarField (face-centered scalar)

fvMesh (finite volume mesh)
├── points_ (vertex coordinates)
├── faces_ (face definitions)
├── cells_ (cell connectivity)
└── boundary_ (boundary conditions)

lduMatrix (sparse matrix system)
├── fvMatrix<Type> (FV discretization matrix)
└── lduAddressing (matrix addressing)
```

**Critical Testing Points:**
- **Field operations**: Creation, manipulation, boundary conditions
- **Mesh operations**: Validity checks, decomposition, interpolation
- **Matrix operations**: Assembly, solving, convergence

---

## Why: Architecture's Importance for Testing

### 1. Test Coverage Mapping

Understanding architecture ensures comprehensive test coverage:

```cpp
// Testing field creation (src/OpenFOAM/fields/)
volScalarField T
(
    IOobject("T", runTime.timeName(), mesh),
    mesh,
    dimensionedScalar("T", dimTemperature, 293.15)
);

// Testing mesh validity (src/finiteVolume/fvMesh/)
if (!mesh.checkMesh(true)) {
    FatalError << "Invalid mesh";
}

// Testing matrix assembly (src/finiteVolume/fvm/)
fvScalarMatrix TEqn(
    fvm::ddt(T)
  + fvm::div(phi, T)
  - fvm::laplacian(alpha, T)
);
```

### 2. Runtime Selection (RTS) Verification

RTS is a key architectural feature requiring specific testing:

```cpp
// Path: src/turbulenceModels/turbulenceModel/turbulenceModel.H
autoPtr<incompressible::turbulenceModel> turb
(
    incompressible::turbulenceModel::New(U, phi, laminarTransport)
);

// Verification requires:
// 1. Check correct model instantiation
ASSERT_EQ(turb->type(), word("kEpsilon"));

// 2. Verify model reads correct coefficients
const scalar Cmu = turb->coeffDict().getScalar("Cmu");
ASSERT_NEAR(Cmu, 0.09, 1e-6);

// 3. Test model behavior
turb->correct();
ASSERT_TRUE(turb->k().size() == mesh.nCells());
```

### 3. Boundary Condition Architecture

Testing BCs requires understanding the BC inheritance hierarchy:

```cpp
// Path: src/finiteVolume/fields/fvPatchFields/
// Base class: fvPatchField<Type>
// Derived classes: fixedValueFvPatchField, zeroGradientFvPatchField, etc.

// Test BC application
volScalarField& T = ...;
T.correctBoundaryConditions();

// Verify BC values on specific patch
label patchI = mesh.boundaryMesh().findPatchID("inlet");
const fvPatchScalarField& T_inlet = T.boundaryField()[patchI];

forAll(T_inlet, faceI) {
    // Verify expected values
    ASSERT_NEAR(T_inlet[faceI], expectedValue[faceI], tolerance);
}
```

### 4. Parallel Decomposition Architecture

Parallel testing requires understanding domain decomposition:

```cpp
// Path: src/decompositionMethods/
// Test decomposition consistency
// 1. Decompose domain
runTime.controlDict().set("writeFormat", "ascii");
decomposePar decomposeObj;
decomposeObj.decompose();

// 2. Run in parallel
// mpirun -np 4 solver -parallel

// 3. Verify decomposition
// - Check global mass conservation
// - Verify field values match at processor boundaries
// - Compare results with serial run
```

---

## How: Testing Strategies

### 1. Field-Level Testing

**Target**: Core field operations in `src/OpenFOAM/fields/`

```cpp
// Test file: test/testFields.C
#include "volFields.H"

void testFieldOperations()
{
    // Create test mesh
    fvMesh mesh(createTestMesh());

    // Test field creation
    volScalarField T1
    (
        IOobject("T1", runTime.timeName(), mesh),
        mesh,
        dimensionedScalar("T1", dimTemperature, 300.0)
    );

    // Test field assignment
    volScalarField T2(T1);
    ASSERT_EQ(T1.size(), T2.size());

    // Test field operations
    volScalarField T3 = T1 + T2;
    volScalarField T4 = sqr(T1);
    volScalarField T5 = sqrt(T1);

    // Verify values
    forAll(T1, cellI) {
        ASSERT_NEAR(T3[cellI], T1[cellI] + T2[cellI], 1e-10);
        ASSERT_NEAR(T4[cellI], T1[cellI] * T1[cellI], 1e-10);
    }

    // Test boundary conditions
    T1.correctBoundaryConditions();
    label patchI = mesh.boundaryMesh().findPatchID("walls");
    const fvPatchScalarField& T_patch = T1.boundaryField()[patchI];
    
    ASSERT_TRUE(T_patch.size() > 0);
}
```

### 2. Mesh-Level Testing

**Target**: Mesh operations in `src/finiteVolume/fvMesh/`

```cpp
// Test file: test/testMesh.C
#include "fvMesh.H"

void testMeshValidity()
{
    fvMesh mesh(createTestMesh());

    // Test mesh validity
    bool valid = mesh.checkMesh(true);
    ASSERT_TRUE(valid);

    // Test geometric properties
    const volVectorField& C = mesh.C();      // Cell centers
    const surfaceVectorField& Cf = mesh.Cf(); // Face centers

    // Verify cell centers are within mesh bounds
    forAll(C, cellI) {
        ASSERT_TRUE(mag(C[cellI]) < GREAT);
    }

    // Test mesh motion (if dynamic mesh)
    if (mesh.dynamic()) {
        mesh.update();
        ASSERT_TRUE(mesh.checkMesh(true));
    }
}
```

### 3. Solver-Level Testing

**Target**: Application solvers in `applications/solvers/`

```cpp
// Test: Integration test for simpleFoam solver
// File: test/testSimpleFoam.C

void testSimpleFoam()
{
    // Setup case
    auto caseDir = prepareTestCase("simpleFoam_verification");

    // Run solver
    runSolver("simpleFoam", caseDir);

    // Load results
    Time runTime(Time::controlDictName, caseDir);
    fvMesh mesh(IOobject("region0", runTime.timeName(), runTime));
    
    volScalarField p
    (
        IOobject("p", runTime.timeName(), mesh, IOobject::MUST_READ),
        mesh
    );
    volVectorField U
    (
        IOobject("U", runTime.timeName(), mesh, IOobject::MUST_READ),
        mesh
    );

    // Verify convergence
    const dictionary& solverDict = mesh.solutionDict().subDict("solvers");
    label maxIter = solverDict.lookupOrDefault<label>("maxIter", 1000);
    
    // Check final residual
    scalar residual = computeResidual(p, U);
    ASSERT_LT(residual, 1e-5);

    // Verify mass conservation
    scalar massImbalance = computeMassImbalance(U, mesh);
    ASSERT_LT(massImbalance, 1e-8);
}
```

### 4. Matrix-Level Testing

**Target**: Matrix operations in `src/finiteVolume/fvm/`

```cpp
// Test file: test/testMatrix.C
#include "fvMatrices.H"

void testMatrixOperations()
{
    fvMesh mesh(createTestMesh());
    volScalarField T(createTestField(mesh, "T"));

    // Test explicit operator (fvc)
    surfaceScalarField lapT = fvc::laplacian(dimensionedScalar("DT", dimArea, 1.0), T);

    // Test implicit operator (fvm)
    fvScalarMatrix TEqn(fvm::laplacian(dimensionedScalar("DT", dimArea, 1.0), T));

    // Verify matrix properties
    ASSERT_EQ(TEqn.source().size(), mesh.nCells());
    ASSERT_GT(TEqn.diag().size(), 0);

    // Test matrix assembly
    TEqn.solve();

    // Verify solution
    ASSERT_TRUE(TEqn.converged());
}
```

### 5. Model Testing (RTS)

**Target**: Turbulence and transport models in `src/turbulenceModels/`

```cpp
// Test file: test/testTurbulenceModel.C
#include "incompressible/turbulenceModel/turbulenceModel.H"

void testTurbulenceModel()
{
    // Setup flow fields
    volVectorField U(createTestVelocityField());
    surfaceScalarField phi(createTestFluxField());
    singlePhaseTransportModel laminarTransport(createTestTransportDict());

    // Create turbulence model using RTS
    autoPtr<incompressible::turbulenceModel> turb
    (
        incompressible::turbulenceModel::New(U, phi, laminarTransport)
    );

    // Test model type
    ASSERT_EQ(turb->type(), word("kEpsilon"));

    // Test coefficient reading
    const dictionary& coeffDict = turb->coeffDict();
    ASSERT_NEAR(coeffDict.getScalar("Cmu"), 0.09, 1e-6);
    ASSERT_NEAR(coeffDict.getScalar("C1"), 1.44, 1e-6);
    ASSERT_NEAR(coeffDict.getScalar("C2"), 1.92, 1e-6);

    // Test model correction
    turb->correct();

    // Verify turbulence fields are computed
    const volScalarField& k = turb->k();
    const volScalarField& epsilon = turb->epsilon();
    const volScalarField& nut = turb->nut();

    ASSERT_EQ(k.size(), mesh.nCells());
    ASSERT_EQ(epsilon.size(), mesh.nCells());
    ASSERT_EQ(nut.size(), mesh.nCells());

    // Verify positivity
    forAll(k, cellI) {
        ASSERT_GT(k[cellI], 0.0);
        ASSERT_GT(epsilon[cellI], 0.0);
        ASSERT_GE(nut[cellI], 0.0);
    }
}
```

### 6. Boundary Condition Testing

**Target**: Boundary conditions in `src/finiteVolume/fields/fvPatchFields/`

```cpp
// Test file: test/testBoundaryConditions.C
#include "fvPatchFields.H"

void testFixedValueBC()
{
    fvMesh mesh(createTestMesh());
    volScalarField T(createTestField(mesh, "T"));

    // Set fixed value BC on patch "inlet"
    label patchI = mesh.boundaryMesh().findPatchID("inlet");
    
    fvPatchScalarField& T_inlet = 
        const_cast<fvPatchScalarField&>(T.boundaryField()[patchI]);
    
    scalarField& T_inlet_value = 
        const_cast<scalarField&>(T_inlet);
    
    // Set fixed value
    T_inlet = 350.0;

    // Apply BC
    T.correctBoundaryConditions();

    // Verify BC applied correctly
    forAll(T_inlet, faceI) {
        ASSERT_NEAR(T_inlet[faceI], 350.0, 1e-10);
    }

    // Test gradient at boundary
    tmp<scalarField> tgrad = T_inlet.gradient();
    const scalarField& grad = tgrad();
    ASSERT_EQ(grad.size(), T_inlet.size());
}

void testZeroGradientBC()
{
    fvMesh mesh(createTestMesh());
    volScalarField T(createTestField(mesh, "T"));

    // Set zero gradient BC on patch "outlet"
    label patchI = mesh.boundaryMesh().findPatchID("outlet");
    
    fvPatchScalarField& T_outlet = 
        const_cast<fvPatchScalarField&>(T.boundaryField()[patchI]);

    // Apply BC
    T.correctBoundaryConditions();

    // Verify zero gradient
    tmp<scalarField> tgrad = T_outlet.gradient();
    const scalarField& grad = tgrad();

    forAll(grad, faceI) {
        ASSERT_NEAR(grad[faceI], 0.0, 1e-10);
    }
}
```

### 7. Parallel Testing

**Target**: Decomposition and parallel execution

```bash
#!/bin/bash
# Test script: testParallel.sh

CASE_DIR="test_cases/cavity"
NP=4

# 1. Run serial reference
echo "Running serial..."
cd $CASE_DIR/serial
blockMesh
simpleFoam > log.serial 2>&1
SERIAL_RES=$(tail -20 log.serial | grep "Final residual")
cd ../..

# 2. Decompose for parallel
echo "Decomposing..."
cd $CASE_DIR
cp -r serial parallel
cd parallel
decomposePar > log.decompose 2>&1

# 3. Run parallel
echo "Running parallel with $NP processors..."
mpirun -np $NP simpleFoam -parallel > log.parallel 2>&1
PARALLEL_RES=$(tail -20 log.parallel | grep "Final residual")
cd ..

# 4. Reconstruct
cd parallel
reconstructPar > log.reconstruct 2>&1
cd ..

# 5. Compare results
echo "Comparing results..."
python3 << EOF
import numpy as np

# Load serial results
serial_p = np.loadtxt('serial/0/p')
serial_U = np.loadtxt('serial/0/U')

# Load reconstructed parallel results
parallel_p = np.loadtxt('parallel/0/p')
parallel_U = np.loadtxt('parallel/0/U')

# Compare
p_diff = np.max(np.abs(serial_p - parallel_p))
U_diff = np.max(np.abs(serial_U - parallel_U))

print(f"Max pressure difference: {p_diff}")
print(f"Max velocity difference: {U_diff}")

assert p_diff < 1e-10, f"Pressure difference too large: {p_diff}"
assert U_diff < 1e-10, f"Velocity difference too large: {U_diff}"

print("Parallel test PASSED")
EOF
```

### 8. Utility-Based Testing

**Target**: Built-in utilities for verification

```bash
# Test: Mesh quality
# Utility: checkMesh (applications/utilities/mesh/generation/checkMesh)

checkMesh -allGeometry -allTopology -time 0

# Expected output verification:
# - Mesh topology: OK
# - Mesh geometry: OK
# - Face orthogonality: < 70°
# - Cell non-orthogonality: < 70°

# Test: Field consistency
# Utility: fieldMinMax (applications/utilities/postProcessing/fieldMinMax)

fieldMinMax

# Verify output shows:
# - No NaN values
# - No infinite values
# - Within physical bounds

# Test: Mass conservation
# Utility: forces (applications/utilities/postProcessing/forces)

forces -time 0:100

# Verify:
# - Net force balance
# - Consistency across time steps
```

---

## Testing Framework

### OpenFOAM's Built-in Test Framework

OpenFOAM includes a testing infrastructure in `src/`:

```cpp
// Path: src/OpenFOAM/db/IOstreams/memory/memoryStream.H
// Test macros available in OpenFOAM

// Basic assertions
ASSERT_TRUE(condition);
ASSERT_FALSE(condition);
ASSERT_EQ(expected, actual);
ASSERT_NEAR(expected, actual, tolerance);

// Field assertions
ASSERT_FIELD_EQ(expectedField, actualField);
ASSERT_FIELD_NEAR(expectedField, actualField, tolerance);

// Mesh assertions
ASSERT_MESH_VALID(mesh);
ASSERT_MESH_CONSISTENT(mesh);
```

### Custom Test Framework Integration

```cpp
// Test file: test/runVerificationTest.C

#include "fvCFD.H"
#include "gtest/gtest.h"

class OpenFOAMVerificationTest : public ::testing::Test
{
protected:
    void SetUp() override {
        // Initialize OpenFOAM
        argList args
        (
            Foam::setRootCaseLists(Foam::None(), Foam::None())
        );
        
        runTime = Time::New(args);
        mesh = fvMesh::New(IOobject("region0", runTime->timeName(), *runTime));
    }

    void TearDown() override {
        mesh.clear();
        runTime.clear();
    }

    autoPtr<Time> runTime;
    autoPtr<fvMesh> mesh;
};

TEST_F(OpenFOAMVerificationTest, FieldCreation)
{
    volScalarField T
    (
        IOobject("T", runTime->timeName(), *mesh),
        *mesh,
        dimensionedScalar("T", dimTemperature, 300.0)
    );

    ASSERT_EQ(T.size(), mesh->nCells());
    ASSERT_GT(T.internalField().size(), 0);
}

int main(int argc, char** argv)
{
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
```

---

## Quick Reference

| Architecture Component | Test Strategy | Key Files/Paths |
|------------------------|---------------|-----------------|
| **Fields** | Create, manipulate, verify operations | `src/OpenFOAM/fields/`, `volScalarField.H` |
| **Mesh** | Validity checks, geometric properties | `src/finiteVolume/fvMesh/`, `checkMesh` |
| **Operators** | Explicit (fvc) vs implicit (fvm) | `src/finiteVolume/fvc/`, `src/finiteVolume/fvm/` |
| **Matrices** | Assembly, solving, convergence | `fvMatrix.H`, `lduMatrix.H` |
| **Solvers** | Integration tests, residual monitoring | `applications/solvers/` |
| **Models (RTS)** | Type verification, coefficient reading | `src/turbulenceModels/`, `turbulenceModel.H` |
| **Boundary Conditions** | Value verification, gradient checks | `src/finiteVolume/fields/fvPatchFields/` |
| **Parallel** | Compare with serial, decomposition consistency | `src/decompositionMethods/` |

---

## Concept Check

<details>
<summary><b>1. ทำไมต้องเข้าใจ architecture ของ OpenFOAM สำหรับการทดสอบ?</b></summary>

**Understanding architecture is essential because it tells us:**

1. **What to test** - Identify critical components (fields, mesh, matrices, models)
2. **How to access internals** - Know which classes and methods to call
3. **Where tests should focus** - Entry points at different abstraction levels
4. **How to ensure coverage** - Map architecture to test suite design

Without architectural knowledge, tests may miss critical components or fail to verify integration between layers.

</details>

<details>
<summary><b>2. Runtime Selection (RTS) ทดสอบอย่างไร?</b></summary>

**RTS testing involves:**

1. **Type verification** - Confirm correct model instantiation:
   ```cpp
   ASSERT_EQ(turb->type(), word("kEpsilon"));
   ```

2. **Coefficient validation** - Verify model reads correct parameters:
   ```cpp
   const scalar Cmu = turb->coeffDict().getScalar("Cmu");
   ASSERT_NEAR(Cmu, 0.09, 1e-6);
   ```

3. **Behavior testing** - Test model produces expected outputs:
   ```cpp
   turb->correct();
   ASSERT_TRUE(turb->k().size() == mesh.nCells());
   ```

RTS is critical because OpenFOAM heavily uses runtime polymorphism for models, boundary conditions, and numerical schemes.

</details>

<details>
<summary><b>3. Parallel testing ทำไมจำเป็นและดำเนินการอย่างไร?</b></summary>

**Parallel testing is necessary because:**

1. **Decomposition correctness** - Domain decomposition must preserve solution integrity
2. **Boundary consistency** - Processor boundary communication must be correct
3. **Load balancing** - Each processor should have equal computational load
4. **Numerical consistency** - Results should match serial within machine precision

**Testing methodology:**

```bash
# 1. Run serial reference
simpleFoam > serial.log

# 2. Decompose and run parallel
decomposePar
mpirun -np 4 simpleFoam -parallel > parallel.log

# 3. Reconstruct and compare
reconstructPar
diff -r 0_serial 0_parallel
```

**Key assertions:**
- Final residuals match within tolerance
- Field values match at all cell centers
- Mass/energy conservation maintained
- Performance scales with processor count

</details>

<details>
<summary><b>4. Boundary condition testing ต้องตรวจสอบอะไรบ้าง?</b></summary>

**BC testing must verify:**

1. **Value correctness** - BC applies specified values:
   ```cpp
   const fvPatchScalarField& T_patch = T.boundaryField()[patchI];
   forAll(T_patch, faceI) {
       ASSERT_NEAR(T_patch[faceI], expectedValue, tolerance);
   }
   ```

2. **Gradient correctness** - BC gradient is computed correctly:
   ```cpp
   tmp<scalarField> tgrad = T_patch.gradient();
   const scalarField& grad = tgrad();
   // Verify gradient matches expected value
   ```

3. **Update mechanism** - BC updates when `correctBoundaryConditions()` is called
4. **Type consistency** - BC reads correct type from dictionary
5. **Coupling** - For coupled BCs (e.g., cyclic, processor), verify data exchange

</details>

---

## Key Takeaways

### สิ่งสำคัญที่ต้องจำ

**Architecture-Driven Testing:**
- **Map tests to architecture** - Each component (field, mesh, matrix, model) should have dedicated tests
- **Test at multiple levels** - Unit tests for classes, integration tests for solvers, system tests for complete cases
- **Leverage OpenFOAM's structure** - Use existing utilities and test infrastructure where possible

**Critical Testing Areas:**
1. **Field operations** - Creation, manipulation, boundary conditions
2. **Mesh validity** - Quality, consistency, decomposition
3. **Numerical schemes** - Explicit (fvc) vs implicit (fvm) operators
4. **Model behavior** - RTS verification, coefficient reading, output validation
5. **Parallel execution** - Compare with serial, verify decomposition
6. **Solver convergence** - Residual monitoring, mass conservation

**Best Practices:**
- Start with **simple unit tests** for core classes
- Build **integration tests** for solver workflows
- Include **MMS test cases** for method verification
- Use **utilities** (checkMesh, fieldMinMax) for validation
- Maintain **serial vs parallel** consistency checks
- Document test coverage by architecture component

---

## Related Documents

**Module Structure:**
- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Introduction:** [01_Introduction.md](01_Introduction.md)
- **Method of Manufactured Solutions:** [02a_Method_of_Manufactured_Solutions_MMS.md](02a_Method_of_Manufactured_Solutions_MMS.md)
- **Richardson Extrapolation:** [02b_Richardson_Extrapolation_GCI.md](02b_Richardson_Extrapolation_GCI.md)

**OpenFOAM Documentation:**
- **Source Code:** `$WM_PROJECT_DIR/src/`
- **Applications:** `$WM_PROJECT_DIR/applications/`
- **Tutorials:** `$WM_PROJECT_DIR/tutorials/`