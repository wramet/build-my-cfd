# 02_Expansion_Term

## Introduction

The expansion term is a critical component in two-phase flow simulations, accounting for compressibility effects and phase change phenomena. In the context of R410A evaporator simulations, this term becomes particularly important due to significant density variations between liquid and vapor phases.

## Mathematical Foundation

### Compressible Flow Equation

The general compressible flow equation includes the expansion term:

$$
\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \mathbf{U}) = 0
$$

For two-phase flow with VOF method, this expands to:

$$
\frac{\partial \alpha_1 \rho_1}{\partial t} + \nabla \cdot (\alpha_1 \rho_1 \mathbf{U}) = \Gamma_{1}
$$

where $\Gamma_{1}$ represents the expansion/source term.

## Implementation Details

### 1. Source Code Reference

**File:** `openfoam_temp/src/finiteVolume/interFoam/alphaEqn.H`

```cpp
// Main alpha equation implementation
fvScalarMatrix alpha1Eqn
(
    fvm::ddt(alpha1) + fvm::div(phi, alpha1)
    + fvm::surfaceScalarFlux(rho1, phi) & fvc::grad(alpha1)
    ==
    fvOptions(alpha1)  // Expansion term included here
);
```

### 2. Surface Flux Calculation

The surface flux calculation is crucial for handling compressibility:

```cpp
// Surface scalar flux implementation
tmp<surfaceScalarField> surfaceScalarFlux::operator&(
    const fvVectorMatrix& mat
) const
{
    // Calculate surface flux
    return fvc::interpolate
    (
        alpha1_
    ) * fvc::interpolate
    (
        rho1_
    ) * phi_;
}
```

### 3. MULES Integration

**File:** `openfoam_temp/src/finiteVolume/interfacialModels/MULES/MULES.H`

```cpp
// MULES algorithm with expansion term
template<class FieldType>
void MULES::explicitSolve
(
    FieldType& alpha,
    const surfaceScalarField& phi,
    const FieldType& alphaPhi,
    surfaceScalarField& alphaPhiCorr,
    const scalar maxAlphaCo,
    const scalar maxCo,
    const scalar rDeltaT,
    const scalar nCorr
)
{
    // Limiter application ensures boundedness
    for (int corr=0; corr<nCorr; corr++)
    {
        // Apply limiter to alpha
        alpha.max(0.0);
        alpha.min(1.0);
    }
}
```

## R410A-Specific Implementation

### 4. Property-Dependent Expansion

For R410A, we need to account for temperature-dependent density:

```cpp
// R410A density calculation
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
    alpha1 * rhoLiquidR410A(T) + alpha2 * rhoVaporR410A(T)
);

// Expansion term implementation
fvScalarMatrix alpha1Eqn
(
    fvm::ddt(alpha1) + fvm::div(phi, alpha1)
    + fvm::surfaceScalarFlux(rho1, phi) & fvc::grad(alpha1)
    ==
    phaseChangeTerm  // R410A-specific source
);
```

### 5. Phase Change Source Term

```cpp
// Phase change calculation
tmp<surfaceScalarField> phaseChangeTerm
(
    new surfaceScalarField
    (
        IOobject
        (
            "phaseChangeTerm",
            runTime.timeName(),
            mesh,
            IOobject::NO_READ,
            IOobject::NO_WRITE
        ),
        mesh,
        dimensionedScalar("0", phi.dimensions(), 0.0)
    )
);

// Mass transfer rate calculation
const dimensionedScalar latentHeat("L", dimEnergy/dimMass, 380000);
const dimensionedScalar criticalTemperature("Tc", dimTemperature, 344.5);

// Evaporation rate
scalar evapRate = 0.0;
if (T > Tsat && alpha1 > 0.01)
{
    evapRate = K * (T - Tsat) * alpha1;
}

// Condensation rate
scalar condRate = 0.0;
if (T < Tsat && alpha2 > 0.01)
{
    condRate = K * (Tsat - T) * alpha2;
}

// Update phase change term
(*phaseChangeTerm) = evapRate - condRate;
```

## Advanced Implementation

### 6. Compressible VOF Scheme

**File:** `openfoam_temp/src/finiteVolume/interfacialModels/compressibleVoF/compressibleVoF.H`

```cpp
class compressibleVoF
{
    // Compressible VOF implementation
    tmp<surfaceScalarField> flux
    (
        const volScalarField& alpha1,
        const surfaceScalarField& phi,
        const volScalarField& rho1,
        const volScalarField& rho2
    ) const;

    // Boundedness correction
    void correct
    (
        volScalarField& alpha1,
        surfaceScalarField& alphaPhi1
    );
};
```

### 7. Interface Compression

```cpp
// Interface compression implementation
void compressibleVoF::correct
(
    volScalarField& alpha1,
    surfaceScalarField& alphaPhi1
)
{
    // Calculate compression factor
    surfaceScalarField compression
    (
        "compression",
        pos0(phi)
      * (phi/mesh.magSf())
    );

    // Apply compression
    alphaPhi1 += compression * (1.0 - alpha1);
    alphaPhi1 -= compression * alpha1;
}
```

## Verification and Validation

### 8. Test Case Setup

```bash
# Create test case for expansion term verification
mkdir -p test_expansion_term
cd test_expansion_term

# 0 directory setup
mkdir -p 0
mkdir -p constant/polyMesh
mkdir -p system

# Initial conditions
cat > 0/alpha1 << EOF
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
|  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|   \\    /   O peration     | Version:  v2306                                |
|    \\  /    A nd           | Website:  www.openfoam.com                      |
|     \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    format      ascii;
    class       volScalarField;
    object      alpha1;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 0 0 0 0 0 0];

internalField   uniform 0.5;

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
    frontAndBack
    {
        type            empty;
    }
}

// ************************************************************************* //
EOF

# Transport properties
cat > constant/transportProperties << EOF
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
|  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|   \\    /   O peration     | Version:  v2306                                |
|    \\  /    A nd           | Website:  www.openfoam.com                      |
|     \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    format      ascii;
    class       dictionary;
    object      transportProperties;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

phases (water air);

phase1
{
    transportModel  Newtonian;
    nu              0.001;
}

phase2
{
    transportModel  Newtonian;
    nu              1.5e-5;
}

// ************************************************************************* //
EOF

# Control dictionary
cat > system/controlDict << EOF
application     interFoam;
startFrom       latestTime;
startTime       0;
stopAt          endTime;
endTime         0.1;
deltaT          1e-4;
writeControl    adjustable;
writeInterval   0.01;
purgeWrite      0;
writeFormat     ascii;
writePrecision  6;
writeCompression off;
timeFormat      general;
timePrecision    6;
runTimeModifiable true;
adjustTimeStep  yes;
maxCo           0.5;
maxAlphaCo      0.5;
EOF
```

### 9. Verification Script

```cpp
// Script to verify expansion term implementation
#include "fvCFD.H"

int main(int argc, char *argv[])
{
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"

    // Read alpha1 field
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

    // Calculate divergence of alpha flux
    surfaceScalarField alphaPhi
    (
        IOobject
        (
            "alphaPhi",
            runTime.timeName(),
            mesh,
            IOobject::NO_READ,
            IOobject::NO_WRITE
        ),
        fvc::flux(alpha1)
    );

    // Calculate expansion term
    volScalarField expansion
    (
        IOobject
        (
            "expansion",
            runTime.timeName(),
            mesh,
            IOobject::NO_READ,
            IOobject::AUTO_WRITE
        ),
        -fvc::div(alphaPhi)
    );

    // Write to console
    Info << "Max expansion: " << max(expansion).value() << endl;
    Info << "Min expansion: " << min(expansion).value() << endl;

    return 0;
}
```

## Performance Optimization

### 10. GPU Acceleration

```cpp
// OpenACC directives for GPU acceleration
#pragma acc parallel loop present(alpha1, alphaPhi, mesh)
forAll(alpha1, i)
{
    alpha1[i] = max(0.0, min(1.0, alpha1[i]));
}

#pragma acc parallel loop present(alphaPhi, mesh)
forAll(alphaPhi, i)
{
    alphaPhi[i] = mag(alphaPhi[i]);
}
```

### 11. Adaptive Mesh Refinement

```cpp
// AMR based on gradient of alpha1
volScalarField gradAlpha
(
    IOobject
    (
        "gradAlpha",
        runTime.timeName(),
        mesh,
        IOobject::NO_READ,
        IOobject::AUTO_WRITE
    ),
    mag(fvc::grad(alpha1))
);

// Mark cells for refinement
const scalar refinementThreshold = 0.1;
const label nRefinementCells = 10;

// Create refinement fields
refineMesh refiner(mesh);
refiner.refineBasedOnGradient
(
    gradAlpha,
    refinementThreshold,
    nRefinementCells
);
```

## Troubleshooting

### 12. Common Issues

**Issue 1: Unbounded alpha values**

```cpp
// Solution: Apply limiter
alpha1 = max(0.0, min(1.0, alpha1));
```

**Issue 2: Numerical diffusion**

```cpp
// Solution: Use high-resolution scheme
divSchemes
{
    div(phi,alpha1)  Gauss vanLeer;
}
```

**Issue 3: Mass loss**

```cpp
// Solution: Check total mass
scalar totalMass = fvc::domainIntegrate
(
    alpha1 * rho1 + (1 - alpha1) * rho2
).value();
```

## Summary

The expansion term implementation in two-phase flow solvers requires careful attention to:

1. **Compressibility Effects**: Proper handling of density variations
2. **Boundedness**: Ensuring alpha values remain within [0, 1]
3. **Phase Change**: R410A-specific mass transfer terms
4. **Numerical Stability**: MULES algorithm and limiting procedures
5. **Performance**: GPU acceleration and parallel optimization

This implementation provides a robust foundation for R410A evaporator simulations with accurate representation of compressibility effects.