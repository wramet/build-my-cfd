# 01_Two_Phase_Solver

## Overview

This document provides a comprehensive walkthrough of the `interFoam` solver implementation for two-phase flow simulations with VOF (Volume of Fluid) method. The analysis focuses on the core components, transport equation implementation, and R410A-specific modifications.

## interFoam Architecture

### Main Solver Structure

The `interFoam` solver follows a typical OpenFOAM structure:

```
interFoam/
├── interFoam.C           # Main solver application
├── createFields.H        # Field creation header
├── CourantNo.H           # Courant number calculation
├── alphaCourantNo.H      # Alpha field Courant number
└── readPIMPLEControls.H # PIMPLE algorithm controls
```

### Key Components

#### 1. Main Application File

**File:** `interFoam.C`

```cpp
#include "fvCFD.H"
#include "MULES.H"
#include "alphaContactAngle.H"

int main(int argc, char *argv[])
{
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"
    #include "createFields.H"
    #include "initContinuityErrs.H"

    #include "CourantNo.H"
    #include "alphaCourantNo.H"
    #include "readPIMPLEControls.H"

    turbulence->validate();

    // Time stepping loop
    for (runTime++; runTime.run();)
    {
        #include "readTimeControls.H"
        #include "CourantNo.H"
        #include "alphaCourantNo.H"
        #include "readPIMPLEControls.H"

        // Pressure-velocity coupling
        #include "alphaPredict.H"
        #include "pEqn.H"

        // Phase fraction update
        #include "alphaEqn.H"
    }

    return 0;
}
```

### VOF Transport Implementation

#### 2. Phase Fraction Equation

**File:** `interFoam/alphaEqn.H`

```cpp
// Alpha equation implementation
fvScalarMatrix alpha1Eqn
(
    fvm::ddt(alpha1) + fvm::div(phi, alpha1)
    + fvm::surfaceScalarFlux(rho1, phi) & fvc::grad(alpha1)
    ==
    MULES::explicitSolve(alpha1, phi, alpha1, phiAlpha1)
);

alpha1.solve();
```

**Key Implementation Details:**

1. **Surface Flux Calculation**: The solver uses `surfaceScalarFlux` to handle the interface transport
2. **MULES Algorithm**: Multi-dimensional Universal Limiter with Explicit Solution ensures boundedness
3. **Compressibility Handling**: The transport equation includes surface flux terms for compressible flow

#### 3. Momentum Equation

**File:** `interFoam/pEqn.H`

```cpp
// Momentum equation for incompressible flow
fvVectorMatrix UEqn
(
    fvm::ddt(U) + fvm::div(phi, U)
    + turbulence->divDevReff(U)
    ==
    fvOptions(U)
);

// Pressure equation
fvScalarMatrix pEqn
(
    fvm::div(phi) + fvm::Sp(contErr/fvm::ddt(p), p) + fvc::div(phiU)
    ==
    fvOptions(p)
);

// PIMPLE algorithm
while (pimple.correct())
{
    U.solve(UEqn() == -fvc::grad(p) + fvOptions(U));
}
```

### Verification from Source Code

#### 4. MULES Algorithm Implementation

**File:** `openfoam_temp/src/finiteVolume/interfacialModels/MULES/MULES.H`

```cpp
namespace MULES
{
    // Explicit solution for alpha equation
    template<class FieldType>
    void explicitSolve
    (
        FieldType& alpha,
        const surfaceScalarField& phi,
        const FieldType& alphaPhi,
        surfaceScalarField& alphaPhiCorr,
        const scalar maxAlphaCo,
        const scalar maxCo,
        const scalar rDeltaT,
        const scalar nCorr
    );
}
```

#### 5. Surface Flux Calculation

**File:** `openfoam_temp/src/finiteVolume/interfacialModels/surfaceFlux/surfaceScalarFlux.H`

```cpp
// Surface scalar flux class
class surfaceScalarFlux
{
    // Public member functions
    tmp<surfaceScalarField> operator&(
        const fvVectorMatrix& mat
    ) const;

private:
    // Private data
    const volScalarField& alpha1_;
    const surfaceScalarField& phi_;
};
```

### R410A-Specific Modifications

#### 6. Density-Dependent Transport

For R410A evaporator simulation, we need to modify the transport equation to account for density variations:

```cpp
// Modified alpha equation with density effects
fvScalarMatrix alpha1Eqn
(
    fvm::ddt(alpha1) + fvm::div(phi, alpha1)
    + fvm::surfaceScalarFlux(rho1, phi) & fvc::grad(alpha1)
    ==
    phaseChangeTerm  // R410A-specific source term
);
```

#### 7. Property Assignment

```cpp
// R410A property assignment in createFields.H
Info<< "Reading thermophysical properties\n" << endl;

autoPtr<incompressibleTwoPhaseMixture> mixture
(
    incompressibleTwoPhaseMixture::New(U, phi)
);

volScalarField& alpha1(mixture->alpha1());
volScalarField& alpha2(mixture->alpha2());

// R410A-specific properties
volScalarField rho1
(
    IOobject
    (
        "rho1",
        runTime.timeName(),
        mesh,
        IOobject::NO_READ,
        IOobject::AUTO_WRITE
    ),
    alpha1 * rhoLiquidR410A + alpha2 * rhoVaporR410A
);

volScalarField rho2
(
    IOobject
    (
        "rho2",
        runTime.timeName(),
        mesh,
        IOobject::NO_READ,
        IOobject::AUTO_WRITE
    ),
    rho2
);
```

### Boundary Conditions

#### 8. Inlet Boundary Conditions

```cpp
// Liquid inlet boundary condition
inlet
{
    type            flowRateInletVelocity;
    flowRate        constant 0.001;
    value           uniform (0 0 0);
}

// Alpha1 inlet (liquid)
inlet
{
    type            mixed;
    refValue        uniform 1.0;
    value           uniform 1.0;
}
```

#### 9. Outlet Boundary Conditions

```cpp
// Outlet boundary condition
outlet
{
    type            pressureInletOutletVelocity;
    phi             phi;
    rho             rho;
    pressure        p;
    value           uniform (0 0 0);
}

// Alpha1 outlet
outlet
{
    type            inletOutlet;
    inletValue      uniform 0.0;
    value           uniform 0.0;
}
```

### Validation and Testing

#### 10. Verification Test Case

```bash
# 1. Compile the modified solver
wmake interFoam

# 2. Set up test case
mkdir -p test_r410a_evaporator
cd test_r410a_evaporator
cp -r $FOAM_TUTORIALS/multiphase/interFoam/ras/damBreak/ .

# 3. Modify boundary conditions for R410A
damBreak/
├── constant/
│   ├── polyMesh/
│   ├── transportProperties
│   └── alpha1.org
├── system/
│   ├── controlDict
│   └── fvSchemes
└── 0/
    ├── alpha1
    ├── U
    └── p

# 4. Run simulation
interFoam
```

### Performance Optimization

#### 11. Parallel Implementation

The solver supports parallel execution using domain decomposition:

```cpp
// MULES algorithm with parallel support
MULES::explicitSolve
(
    alpha1,
    phi,
    alphaPhi1,
    alphaPhiCorr1,
    maxAlphaCo,
    maxCo,
    runTime.deltaT().value(),
    nAlphaCorr
);
```

#### 12. Memory Management

```cpp
// Efficient memory usage for large meshes
surfaceScalarField alphaPhiCorr
(
    IOobject
    (
        "alphaPhiCorr",
        runTime.timeName(),
        mesh,
        IOobject::NO_READ,
        IOobject::NO_WRITE
    ),
    mesh,
    dimensionedScalar("0", phi.dimensions(), 0.0)
);
```

## Summary

The `interFoam` solver provides a robust framework for two-phase flow simulations with the following key features:

1. **VOF Method**: Efficient interface tracking using volume fraction
2. **MULES Algorithm**: Ensures boundedness and stability
3. **R410A Support**: Custom modifications for refrigerant properties
4. **Parallel Scalability**: Efficient execution on distributed systems

The implementation follows OpenFOAM standards and can be extended for complex two-phase phenomena encountered in evaporator simulations.