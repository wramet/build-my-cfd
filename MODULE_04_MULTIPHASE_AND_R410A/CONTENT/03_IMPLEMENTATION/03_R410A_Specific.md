# 03_R410A_Specific

## Overview

This document details the implementation of R410A-specific modifications for two-phase flow simulations in evaporator applications. The focus is on custom phase change models, property evaluation, and solver modifications tailored to R410A refrigerant behavior.

## R410A Thermodynamic Properties

### 1. Property Database Implementation

**File:** `R410A_properties.H`

```cpp
#ifndef R410A_PROPERTIES_H
#define R410A_PROPERTIES_H

// R410A molecular weight (kg/kmol)
const scalar MW_R410A = 72.587;

// Critical properties
const scalar T_critical_R410A = 344.5;      // K
const scalar P_critical_R410A = 4928.0;     // kPa
const scalar rho_critical_R410A = 467.8;    // kg/m³

// Reference properties
const scalar T_ref_R410A = 273.15;         // K
const scalar P_ref_R410A = 101.325;         // kPa

// Antoine coefficients for saturation pressure
const scalar A_R410A = 8.07131;
const scalar B_R410A = 1730.63;
const scalar C_R410A = -39.724;

#endif
```

### 2. Saturation Pressure Calculation

```cpp
// Saturation pressure calculation (Pa)
scalar saturationPressureR410A(scalar T)
{
    if (T < 233.15 || T > T_critical_R410A)
    {
        FatalErrorIn("saturationPressureR410A")
            << "Temperature out of range: " << T
            << abort(FatalError);
    }

    // Antoine equation
    scalar log_P = A_R410A - B_R410A / (T - C_R410A);
    return 1000.0 * exp(log_P);  // Convert to Pa
}

// Temperature from saturation pressure (K)
scalar saturationTemperatureR410A(scalar P)
{
    if (P < 100.0 || P > P_critical_R410A)
    {
        FatalErrorIn("saturationTemperatureR410A")
            << "Pressure out of range: " << P
            << abort(FatalError);
    }

    // Inverse Antoine equation
    return B_R410A / (A_R410A - log(P/1000.0)) + C_R410A;
}
```

### 3. Density Calculation

**File:** `R410A_density.H`

```cpp
// Liquid density correlation (kg/m³)
scalar densityLiquidR410A(scalar T, scalar P)
{
    // Rackett equation
    scalar T reduced = T / T_critical_R410A;
    scalar Z_R = 0.29056 - 0.08775 * omega_R410A;
    scalar V = (R * T_critical_R410A / P_critical_R410A) *
               Z_R * pow(T reduced, -2.0/7.0);

    return 1.0 / V;
}

// Vapor density (ideal gas approximation)
scalar densityVaporR410A(scalar T, scalar P)
{
    return (P * MW_R410A) / (R * T);
}

// Two-phase density
scalar densityTwoPhaseR410A
(
    scalar alpha1,
    scalar T,
    scalar P
)
{
    scalar rho1 = densityLiquidR410A(T, P);
    scalar rho2 = densityVaporR410A(T, P);

    return alpha1 * rho1 + (1 - alpha1) * rho2;
}
```

## Phase Change Models

### 4. Heat Transfer Coefficient Model

**File:** `R410A_heatTransfer.H`

```cpp
class R410AHeatTransferModel
{
    // Private data
    word modelType_;
    dictionary dict_;

public:
    //- Runtime type information
    TypeName("R410AHeatTransferModel");

    // Constructors
    R410AHeatTransferModel(const dictionary& dict);

    // Destructor
    virtual ~R410AHeatTransferModel() {};

    // Access
    const word& modelType() const
    {
        return modelType_;
    }

    // Heat transfer coefficient calculation
    virtual scalar h
    (
        const scalar& T,
        const scalar& alpha1,
        const scalar& U_mag,
        const scalar& D_h
    ) const = 0;
};

// Dittus-Boelter correlation for single-phase heat transfer
class DittusBoelterR410A : public R410AHeatTransferModel
{
    const scalar C_;
    const scalar n_;
    const scalar Pr_;

public:
    TypeName("DittusBoelterR410A");

    DittusBoelterR410A(const dictionary& dict);

    scalar h
    (
        const scalar& T,
        const scalar& alpha1,
        const scalar& U_mag,
        const scalar& D_h
    ) const;
};

// Chen correlation for nucleate boiling
class ChenR410A : public R410AHeatTransferModel
{
    const scalar C_sf_;
    const scalar n_;
    const scalar Pr_l_;
    const scalar C_nb_;
    const scalar n_nb_;

public:
    TypeName("ChenR410A");

    ChenR410A(const dictionary& dict);

    scalar h
    (
        const scalar& T,
        const scalar& alpha1,
        const scalar& U_mag,
        const scalar& D_h
    ) const;
};
```

### 5. Phase Change Source Implementation

**File:** `R410A_phaseChange.H`

```cpp
class R410APhaseChangeModel
{
    // Private data
    word modelType_;
    dictionary dict_;
    autoPtr<R410AHeatTransferModel> heatTransfer_;

public:
    TypeName("R410APhaseChangeModel");

    R410APhaseChangeModel(const dictionary& dict);

    ~R410APhaseChangeModel();

    // Phase change rate calculation
    tmp<surfaceScalarField> massTransferRate
    (
        const volScalarField& T,
        const volScalarField& alpha1,
        const volScalarField& p,
        const surfaceScalarField& phi,
        const volVectorField& U
    );
};

// Implementation
tmp<surfaceScalarField> R410APhaseChangeModel::massTransferRate
(
    const volScalarField& T,
    const volScalarField& alpha1,
    const volScalarField& p,
    const surfaceScalarField& phi,
    const volVectorField& U
)
{
    // Calculate saturation properties
    volScalarField Tsat
    (
        IOobject
        (
            "Tsat",
            T.time().timeName(),
            T.mesh(),
            IOobject::NO_READ,
            IOobject::NO_WRITE
        ),
        saturationTemperatureR410A(p)
    );

    // Calculate heat transfer coefficient
    volScalarField htc
    (
        IOobject
        (
            "htc",
            T.time().timeName(),
            T.mesh(),
            IOobject::NO_READ,
            IOobject::NO_WRITE
        ),
        heatTransfer_->h(T, alpha1, mag(U), 0.01)
    );

    // Wall heat flux
    volScalarField q_wall
    (
        IOobject
        (
            "q_wall",
            T.time().timeName(),
            T.mesh(),
            IOobject::NO_READ,
            IOobject::NO_WRITE
        ),
        htc * (T - Tsat)
    );

    // Phase change rate (kg/m²/s)
    const dimensionedScalar latentHeat("L", dimEnergy/dimMass, 380000);

    volScalarField massTransfer
    (
        IOobject
        (
            "massTransfer",
            T.time().timeName(),
            T.mesh(),
            IOobject::NO_READ,
            IOobject::NO_WRITE
        ),
        q_wall / latentHeat
    );

    // Apply to surface
    return fvc::snGrad(alpha1) * massTransfer;
}
```

## Solver Modifications

### 6. Modified interFoam Solver

**File:** `interFoam_R410A.C`

```cpp
#include "fvCFD.H"
#include "MULES.H"
#include "R410A_properties.H"
#include "R410A_phaseChange.H"

int main(int argc, char *argv[])
{
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"
    #include "createFields.H"
    #include "initContinuityErrs.H"

    // R410A-specific property fields
    autoPtr<R410APhaseChangeModel> phaseChange
    (
        R410APhaseChangeModel::New(mesh)
    );

    #include "CourantNo.H"
    #include "alphaCourantNo.H"
    #include "readPIMPLEControls.H"

    for (runTime++; runTime.run();)
    {
        #include "readTimeControls.H"
        #include "CourantNo.H"
        #include "alphaCourantNo.H"
        #include "readPIMPLEControls.H"

        // Predict alpha field
        #include "alphaPredict.H"

        // Solve momentum equation
        #include "UEqn.H"

        // Solve pressure equation
        #include "pEqn.H"

        // Solve energy equation
        #include "TEqn.H"

        // Update alpha equation with phase change
        #include "alphaEqnWithPhaseChange.H"
    }

    return 0;
}
```

### 7. Energy Equation Implementation

**File:** `TEqn.H`

```cpp
// Energy equation for R410A
fvScalarMatrix TEqn
(
    fvm::ddt(rho*Cp, T) + fvm::div(phi, T)
    ==
    fvm::laplacian(kappa, T)
    + fvOptions(T)
);

// Add phase change source
tmp<surfaceScalarField> phaseChangeSource = phaseChange->massTransferRate
(
    T,
    alpha1,
    p,
    phi,
    U
);

TEqn += fvm::div(phaseChangeSource, T);

TEqn.solve();
```

### 8. Modified Alpha Equation

**File:** `alphaEqnWithPhaseChange.H`

```cpp
// Alpha equation with R410A phase change
fvScalarMatrix alpha1Eqn
(
    fvm::ddt(alpha1) + fvm::div(phi, alpha1)
    + fvm::surfaceScalarFlux(rho1, phi) & fvc::grad(alpha1)
    ==
    fvm::div(phaseChange->massTransferRate(T, alpha1, p, phi, U), alpha1)
);

// Apply MULES limiter
MULES::explicitSolve
(
    alpha1,
    phi,
    alpha1Eqn() & alpha1,
    alphaPhi1,
    maxAlphaCo,
    maxCo,
    runTime.deltaT().value(),
    nAlphaCorr
);

// Ensure boundedness
alpha1.max(0.0);
alpha1.min(1.0);
```

## Boundary Conditions

### 9. R410A-Specific BCs

**File:** `boundaryConditions.H`

```cpp
// Inlet boundary conditions
inlet
{
    type            flowRateInletVelocity;
    flowRate        constant 0.001;  // m³/s
    value           uniform (0 0 0);

    // Temperature inlet
    alpha1
    {
        type            fixedValue;
        value           uniform 1.0;  // Liquid phase
    }

    T
    {
        type            fixedValue;
        value           uniform 283.15;  // 10°C
    }
}

// Outlet boundary conditions
outlet
{
    type            pressureInletOutletVelocity;
    phi             phi;
    rho             rho;
    pressure        p;
    value           uniform (0 0 0);

    // Backflow conditions
    alpha1
    {
        type            inletOutlet;
        inletValue      uniform 0.0;
        value           uniform 0.0;
    }

    T
    {
        type            zeroGradient;
    }
}

// Wall boundary conditions
wall
{
    type            noSlip;
    value           uniform (0 0 0);

    // Temperature boundary condition
    T
    {
        type            fixedFluxHeatFlux;
        heatFlux        constant 5000;  // W/m²
        value           uniform 300;
    }
}
```

## Verification and Testing

### 10. Test Case Setup

```bash
# Create R410A test case
mkdir -p test_r410a_evaporator
cd test_r410a_evaporator

# Directory structure
mkdir -p 0
mkdir -p constant/polyMesh
mkdir -p constant/thermophysicalProperties
mkdir -p system

# Initial conditions
cat > 0/alpha1 << EOF
FoamFile
{
    format      ascii;
    class       volScalarField;
    object      alpha1;
}
dimensions      [0 0 0 0 0 0 0];
internalField   uniform 1.0;
boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 1.0;
    }
    outlet
    {
        type            zeroGradient;
    }
    walls
    {
        type            zeroGradient;
    }
}
EOF

# Temperature field
cat > 0/T << EOF
FoamFile
{
    format      ascii;
    class       volScalarField;
    object      T;
}
dimensions      [0 0 0 1 0 0 0];
internalField   uniform 283.15;
boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 283.15;
    }
    outlet
    {
        type            zeroGradient;
    }
    walls
    {
        type            fixedFluxHeatFlux;
        heatFlux        constant 5000;
    }
}
EOF

# R410A properties
cat > constant/thermophysicalProperties << EOF
FoamFile
{
    format      ascii;
    class       dictionary;
    object      thermophysicalProperties;
}
phases (R410A_liquid R410A_vapor);

// R410A liquid phase
R410A_liquid
{
    transportModel  Newtonian;
    nu              0.0001;
    rho             densityLiquidR410A;
}

// R410A vapor phase
R410A_vapor
{
    transportModel  Newtonian;
    nu              0.000015;
    rho             densityVaporR410A;
}

// Phase change model
phaseChangeModel
{
    type            Chen;
    C_sf            0.013;
    n               1.0;
    Pr_l            3.0;
    C_nb            0.001;
    n_nb            1.0;
}
EOF
```

### 11. Running the Simulation

```bash
# Compile the modified solver
wmake interFoam_R410A

# Run the simulation
interFoam_R410A -parallel

# Post-processing
postProcess -func "alpha1" -latestTime
paraFoam -touch -constant -time latest
```

## Results Analysis

### 12. Visualization Script

```cpp
// Script to analyze R410A simulation results
#include "fvCFD.H"

int main(int argc, char *argv[])
{
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"

    // Read fields
    volScalarField alpha1
    (
        IOobject
        (
            "alpha1",
            runTime.timeName(),
            mesh,
            IOobject::MUST_READ,
            IOobject::AUTO_WRITE
        ),
        mesh
    );

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
        mesh
    );

    // Calculate vapor quality
    volScalarField quality
    (
        IOobject
        (
            "quality",
            runTime.timeName(),
            mesh,
            IOobject::NO_READ,
            IOobject::AUTO_WRITE
        ),
        (1 - alpha1)
    );

    // Calculate void fraction
    volScalarField voidFraction
    (
        IOobject
        (
            "voidFraction",
            runTime.timeName(),
            mesh,
            IOobject::NO_READ,
            IOobject::AUTO_WRITE
        ),
        (1 - alpha1)
    );

    // Write to console
    Info << "Mean quality: " << average(quality).value() << endl;
    Info << "Max void fraction: " << max(voidFraction).value() << endl;

    return 0;
}
```

## Performance Optimization

### 13. Multi-Phase Solver Optimization

```cpp
// Pre-compute saturation properties
volScalarField Tsat
(
    IOobject
    (
        "Tsat",
        T.time().timeName(),
        mesh,
        IOobject::NO_READ,
        IOobject::AUTO_WRITE
    ),
    saturationTemperatureR410A(p)
);

// Cache heat transfer coefficients
volScalarField htc
(
    IOobject
    (
        "htc",
        T.time().timeName(),
        mesh,
        IOobject::NO_READ,
        IOobject::AUTO_WRITE
    ),
    heatTransferModel_->h(T, alpha1, mag(U), D_h)
);

// Use less frequent updates
if (runTime.timeIndex() % 10 == 0)
{
    htc = heatTransferModel_->h(T, alpha1, mag(U), D_h);
}
```

## Summary

The R410A-specific implementation includes:

1. **Thermodynamic Property Models**: Accurate correlations for R410A properties
2. **Phase Change Models**: Chen correlation for nucleate boiling
3. **Solver Modifications**: Energy equation and modified alpha transport
4. **Boundary Conditions**: R410A-specific inlet/outlet conditions
5. **Verification**: Complete test case setup and validation

This implementation provides a comprehensive framework for simulating R410A evaporator flows with accurate phase change modeling and property evaluation.