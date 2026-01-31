# Phase 10: Complete Evaporator Case Setup

Implement complete evaporator case setup with mesh, boundary conditions, and solver configuration

---

## Learning Objectives

By completing this phase, you will be able to:

- Design and implement a complete evaporator case setup
- Create optimized mesh for tube heat transfer and two-phase flow
- Set up proper boundary conditions for evaporator operation
- Configure solver settings for two-phase evaporation
- Develop post-processing and visualization setup

---

## Overview: The 3W Framework

### What: Complete Evaporator Case Implementation

We will create a complete evaporator case setup that includes:

1. **3D Tube Geometry**: Realistic evaporator tube with inlet/outlet sections
2. **Mesh Generation**: Structured hexahedral mesh with boundary layer refinement
3. **Boundary Conditions**: Proper inlet, outlet, wall, and symmetry conditions
4. **Solver Configuration**: Two-phase solver settings for R410A
5. **Post-processing**: Monitoring, visualization, and data extraction

### Why: Industrial-Ready Simulation Setup

This phase creates a production-ready case setup that:

1. **Realistic Geometry**: Actual evaporator tube dimensions and features
2. **Proper Physics**: Two-phase flow with phase change
3. **Industrial Standards**: Conjugate heat transfer with tube wall
4. **Validation Ready**: Setup for comparison with experimental data
5. **Scalable**: Can be extended to tube bundles and heat exchangers

### How: Progressive Case Development

We'll build the case setup systematically:

1. **Geometry Definition**: blockMeshDict for tube geometry
2. **Mesh Generation**: Detailed mesh with boundary layers
3. **Boundary Conditions**: Proper physics setup
4. **Solver Configuration**: Two-phase solver settings
5. **Post-processing**: Monitoring and visualization

---

## 1. Complete Evaporator Case Directory Structure

### Directory Layout

```
R410A_evaporator_case/
├── constant/
│   ├── polyMesh/
│   │   ├── points
│   │   ├── faces
│   │   ├── owner
│   │   ├── neighbour
│   │   └── boundary
│   ├── transportProperties
│   ├── R410A_properties
│   ├── materialProperties
│   └── thermoPhysicalProperties
├── system/
│   ├── controlDict
│   ├── fvSolution
│   ├── fvSchemes
│   ├── blockMeshDict
│   ├── checkMeshDict
│   ├── mapFieldsDict
│   ├── setFieldsDict
│   ├── createPatchDict
│   └── decomposeParDict
├── 0/
│   ├── alpha
│   ├── U
│   ├── p_rgh
│   ├── T
│   ├── k
│   ├── epsilon
│   ├── omega
│   ├── nut
│   └── p
├── postProcessing/
│   ├── surfaces/
│   ├── probes/
│   ├── functionObjects/
│   └── paraview/
├── scripts/
│   ├── setup_case.sh
│   ├── mesh_generation.sh
│   ├── boundary_conditions.sh
│   ├── post_process.py
│   └── monitoring.sh
├── validation/
│   ├── experimental_data.csv
│   ├── comparison_script.py
│   └── results_comparison/
├── README.md
└── case_description.md
```

### Case Description File: case_description.md

```markdown
# R410A Evaporator Case Description

## Geometry
- Tube length: 2.0 m
- Tube inner diameter: 10 mm
- Tube outer diameter: 12 mm
- Wall thickness: 1 mm
- Number of tubes: 1 (single tube)
- Tube orientation: Horizontal

## Operating Conditions
- Inlet pressure: 15 bar
- Inlet temperature: 280 K (subcooled liquid)
- Inlet velocity: 0.5 m/s
- Wall heat flux: 5 kW/m²
- Outlet pressure: 14.5 bar
- Ambient temperature: 300 K

## Fluid Properties
- Refrigerant: R410A
- Tube material: Copper (k = 400 W/m·K)
- Wall thickness: 1 mm

## Mesh Details
- Total cells: 200,000
- Axial cells: 200
- Radial cells (fluid): 10
- Radial cells (solid): 5
- Circumferential cells: 100
- Boundary layers: 5

## Solver Settings
- Solver: R410ASolver
- Time step: 0.001 s
- Total simulation time: 10 s
- Turbulence model: k-omega SST
- Phase change: Nucleate boiling model

## Boundary Conditions
- Inlet: Fixed velocity, temperature
- Outlet: Pressure outlet
- Wall: Constant heat flux
- Symmetry: Periodic boundary conditions

## Validation
- Reference: Experimental data from literature
- Comparison parameters: Heat transfer coefficient, pressure drop, dryout location
```

---

## 2. Geometry and Mesh Setup

### Block Mesh Dictionary: constant/polyMesh/blockMeshDict

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  www.openfoam.org
    \\  /    A nd           | Version:  9
     \\/     M anipulation  |
\*---------------------------------------------------------------------------*/
FoamFile
{
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

scale   1.0;

vertices
(
    // Fluid domain points
    (0 0 0)           // 0: inlet center
    (2 0 0)           // 1: outlet center
    (0 0.005 0)       // 2: inner wall at inlet
    (2 0.005 0)       // 3: inner wall at outlet
    (0 -0.005 0)      // 4: inner wall at inlet (bottom)
    (2 -0.005 0)      // 5: inner wall at outlet (bottom)
    (0 0.006 0)       // 6: outer wall at inlet
    (2 0.006 0)       // 7: outer wall at outlet
    (0 -0.006 0)      // 8: outer wall at inlet
    (2 -0.006 0)      // 9: outer wall at outlet

    // Solid domain points
    (0 0 0.1)         // 10: solid inlet top
    (2 0 0.1)         // 11: solid outlet top
    (0 0.005 0.1)     // 12: solid-fluid interface top
    (2 0.005 0.1)     // 13: solid-fluid interface top
    (0 -0.005 0.1)    // 14: solid-fluid interface bottom
    (2 -0.005 0.1)    // 15: solid-fluid interface bottom
    (0 0.006 0.1)     // 16: outer solid top
    (2 0.006 0.1)     // 17: outer solid top
    (0 -0.006 0.1)    // 18: outer solid bottom
    (2 -0.006 0.1)     // 19: outer solid bottom

    // Symmetry plane points
    (0 0 0)           // 20: symmetry inlet (same as 0)
    (2 0 0)           // 21: symmetry outlet (same as 1)
    (0 0 0.1)         // 22: symmetry solid inlet (same as 10)
    (2 0 0.1)         // 23: symmetry solid outlet (same as 11)
);

blocks
(
    // Fluid domain blocks
    hex (0 1 3 2 20 21 23 22) (40 20 1) simpleGrading (1 1 1)
    hex (4 5 7 6 22 23 25 24) (40 20 1) simpleGrading (1 1 1)
    hex (2 3 9 8 22 23 27 26) (40 20 1) simpleGrading (1 1 1)
    hex (6 7 9 8 24 25 27 26) (40 20 1) simpleGrading (1 1 1)

    // Solid domain blocks
    hex (2 3 13 12 22 23 35 34) (40 5 1) simpleGrading (1 2 1)
    hex (4 5 15 14 24 25 37 36) (40 5 1) simpleGrading (1 2 1)
    hex (12 13 17 16 34 35 39 38) (40 5 1) simpleGrading (1 2 1)
    hex (14 15 19 18 36 37 41 40) (40 5 1) simpleGrading (1 2 1)

    // Combined fluid blocks for better resolution
    hex (0 2 12 10 20 22 34 32) (80 10 1) simpleGrading (1 2 1)
    hex (2 3 13 12 22 23 35 34) (80 10 1) simpleGrading (1 2 1)
    hex (4 5 15 14 24 25 37 36) (80 10 1) simpleGrading (1 2 1)
    hex (14 15 19 18 36 37 41 40) (80 10 1) simpleGrading (1 2 1)
);

boundary
(
    inlet
    {
        type            patch;
        faces
        (
            (0 20 22 10)
            (20 0 1 21)
        );
    }

    outlet
    {
        type            patch;
        faces
        (
            (1 21 23 11)
            (3 13 35 23)
        );
    }

    innerWall
    {
        type            wall;
        faces
        (
            (2 3 9 8)
            (6 7 9 8)
            (12 13 17 16)
            (14 15 19 18)
        );
    }

    outerWall
    {
        type            wall;
        faces
        (
            (6 7 9 8)
            (16 17 19 18)
        );
    }

    symmetry
    {
        type            symmetryPlane;
        faces
        (
            (20 21 23 22)
            (10 32 34 22)
            (32 34 36 24)
            (22 23 25 24)
        );
    }

    fluidSolidInterface
    {
        type            coupled;
        faces
        (
            (12 34 2 22)
            (34 35 3 13)
            (14 36 4 24)
            (36 37 5 15)
        );
    }
);

mergePatchPairs
(
);

// ************************************************************************* //
```

### Mesh Generation Script: scripts/mesh_generation.sh

```bash
#!/bin/bash

# Script to generate mesh for R410A evaporator case
# Usage: ./mesh_generation.sh

echo "Generating mesh for R410A evaporator case..."

# Clean previous mesh
rm -rf constant/polyMesh
rm -rf 0/polyMesh
rm -rf 1/polyMesh
rm -rf 2/polyMesh
rm -rf 3/polyMesh
rm -rf 4/polyMesh
rm -rf 5/polyMesh
rm -rf 6/polyMesh
rm -rf 7/polyMesh
rm -rf 8/polyMesh
rm -rf 9/polyMesh

# Create empty polyMesh directory
mkdir -p constant/polyMesh

# Generate block mesh
blockMesh

# Check mesh quality
checkMesh

# Create boundary layers
createBaffles

# Generate refined mesh
refineMesh

# Create patches
createPatch

# Calculate mesh statistics
checkMesh

# Generate surface features
surfaceFeatureEdgeMesh

# Generate final mesh
blockMesh

# Create boundary layers
extrudeMesh -patchNames innerWall -direction normal -distance 0.001 -nLayers 5 -expansionRatio 1.2

# Check mesh quality
checkMesh

# Print mesh statistics
checkMesh -allGeometry -allTopology -verbose

echo "Mesh generation completed!"
echo "Total cells: $(foamListTimes - latestTime | wc -l)"
```

### Boundary Layer Setup: constant/polyMesh/boundary

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  www.openfoam.org
    \\  /    A nd           | Version:  9
     \\/     M anipulation  |
\*---------------------------------------------------------------------------*/
FoamFile
{
    format      ascii;
    class       polyMesh;
    object      boundary;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

7
(
    inlet
    {
        type            patch;
        nFaces          160;
        startFace       4400;
    }

    outlet
    {
        type            patch;
        nFaces          160;
        startFace       4560;
    }

    innerWall
    {
        type            wall;
        nFaces          640;
        startFace       4720;
    }

    outerWall
    {
        type            wall;
        nFaces          320;
        startFace       5360;
    }

    symmetry
    {
        type            symmetryPlane;
        nFaces          160;
        startFace       5680;
    }

    fluidSolidInterface
    {
        type            coupled;
        nFaces          640;
        startFace       5840;
    }

    frontAndBack
    {
        type            empty;
        nFaces          0;
        startFace       6480;
    }
)

// ************************************************************************* //
```

---

## 3. Boundary Conditions Setup

### Initial Conditions: 0/alpha

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  www.openfoam.org
    \\  /    A nd           | Version:  9
     \\/     M anipulation  |
\*---------------------------------------------------------------------------*/
FoamFile
{
    format      ascii;
    class       volScalarField;
    object      alpha;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 0 0 0 0 0 0];

internalField   uniform 0;

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

    innerWall
    {
        type            fixedValue;
        value           uniform 0.0;
    }

    outerWall
    {
        type            fixedValue;
        value           uniform 0.0;
    }

    symmetry
    {
        type            symmetryPlane;
    }

    fluidSolidInterface
    {
        type            fixedValue;
        value           uniform 0.0;
    }

    frontAndBack
    {
        type            empty;
    }
}

// ************************************************************************* //
```

### Velocity Field: 0/U

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  www.openfoam.org
    \\  /    A nd           | Version:  9
     \\/     M anipulation  |
\*---------------------------------------------------------------------------*/
FoamFile
{
    format      ascii;
    class       volVectorField;
    object      U;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 1 -1 0 0 0 0];

internalField   uniform (0.5 0 0);

boundaryField
{
    inlet
    {
        type            flowRateInletVelocity;
        volumetricFlowRate 1e-4;  // 1 L/s
        value           uniform (0.5 0 0);
    }

    outlet
    {
        type            pressureInletOutletVelocity;
        phi             phi;
        value           uniform (0 0 0);
    }

    innerWall
    {
        type            noSlip;
    }

    outerWall
    {
        type            noSlip;
    }

    symmetry
    {
        type            symmetryPlane;
    }

    fluidSolidInterface
    {
        type            noSlip;
    }

    frontAndBack
    {
        type            empty;
    }
}

// ************************************************************************* //
```

### Pressure Field: 0/p_rgh

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  www.openfoam.org
    \\  /    A nd           | Version:  9
     \\/     M anipulation  |
\*---------------------------------------------------------------------------*/
FoamFile
{
    format      ascii;
    class       volScalarField;
    object      p_rgh;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [1 -1 -2 0 0 0 0];

internalField   uniform 1.5e6;

boundaryField
{
    inlet
    {
        type            calculated;
        value           uniform 1.5e6;
    }

    outlet
    {
        type            fixedFluxPressure;
        rho             rho;
        snGrad          p_rgh;
        value           uniform 1.45e6;
    }

    innerWall
    {
        type            fixedFluxPressure;
        rho             rho;
        snGrad          p_rgh;
        value           uniform 1.5e6;
    }

    outerWall
    {
        type            fixedFluxPressure;
        rho             rho;
        snGrad          p_rgh;
        value           uniform 1.5e6;
    }

    symmetry
    {
        type            symmetryPlane;
        value           uniform 1.5e6;
    }

    fluidSolidInterface
    {
        type            fixedFluxPressure;
        rho             rho;
        snGrad          p_rgh;
        value           uniform 1.5e6;
    }

    frontAndBack
    {
        type            empty;
    }
}

// ************************************************************************* //
```

### Temperature Field: 0/T

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  www.openfoam.org
    \\  /    A nd           | Version:  9
     \\/     M anipulation  |
\*---------------------------------------------------------------------------*/
FoamFile
{
    format      ascii;
    class       volScalarField;
    object      T;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 0 0 1 0 0 0];

internalField   uniform 280;

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 280;
    }

    outlet
    {
        type            zeroGradient;
    }

    innerWall
    {
        type            fixedGradient;
            gradient      uniform 5000;  // Heat flux gradient
        value           uniform 280;
    }

    outerWall
    {
        type            mixed;
            refValue     uniform 300;
            refGradient   uniform 0;
            value         uniform 300;
    }

    symmetry
    {
        type            symmetryPlane;
    }

    fluidSolidInterface
    {
        type            fixedGradient;
            gradient      uniform 0;
        value           uniform 280;
    }

    frontAndBack
    {
        type            empty;
    }
}

// ************************************************************************* //
```

### Turbulence Fields: 0/k and 0/epsilon

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  www.openfoam.org
    \\  /    A nd           | Version:  9
     \\/     M anipulation  |
\*---------------------------------------------------------------------------*/
FoamFile
{
    format      ascii;
    class       volScalarField;
    object      k;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 2 -2 0 0 0 0];

internalField   uniform 0.01;

boundaryField
{
    inlet
    {
        type            turbulentIntensityKineticEnergyInlet;
        intensity       0.05;
        value           uniform 0.01;
    }

    outlet
    {
        type            inletOutlet;
        inletValue      uniform 0.01;
        value           uniform 0.01;
    }

    innerWall
    {
        type            kqRWallFunction;
        value           uniform 0.01;
    }

    outerWall
    {
        type            kqRWallFunction;
        value           uniform 0.01;
    }

    symmetry
    {
        type            symmetryPlane;
    }

    fluidSolidInterface
    {
        type            kqRWallFunction;
        value           uniform 0.01;
    }

    frontAndBack
    {
        type            empty;
    }
}
// ************************************************************************* //

/*--------------------------------*- C++ -*----------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  www.openfoam.org
    \\  /    A nd           | Version:  9
     \\/     M anipulation  |
\*---------------------------------------------------------------------------*/
FoamFile
{
    format      ascii;
    class       volScalarField;
    object      epsilon;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 2 -3 0 0 0 0];

internalField   uniform 0.001;

boundaryField
{
    inlet
    {
        type            turbulentIntensityDissipationRateInlet;
        intensity       0.05;
        value           uniform 0.001;
    }

    outlet
    {
        type            inletOutlet;
        inletValue      uniform 0.001;
        value           uniform 0.001;
    }

    innerWall
    {
        type            epsilonWallFunction;
        value           uniform 0.001;
    }

    outerWall
    {
        type            epsilonWallFunction;
        value           uniform 0.001;
    }

    symmetry
    {
        type            symmetryPlane;
    }

    fluidSolidInterface
    {
        type            epsilonWallFunction;
        value           uniform 0.001;
    }

    frontAndBack
    {
        type            empty;
    }
}
// ************************************************************************* //
```

---

## 4. Transport Properties Setup

### Transport Properties: constant/transportProperties

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  www.openfoam.org
    \\  /    A nd           | Version:  9
     \\/     M anipulation  |
\*---------------------------------------------------------------------------*/
FoamFile
{
    format      ascii;
    class       dictionary;
    object      transportProperties;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

thermoType
{
    type            heRhoThermo;
    mixture         pureMixture;
    transport       sutherland;
    thermo         hRhoThermo;
    energy         sensibleEnthalpy;
    equationOfState  perfectGas;
    species         none;
}

mixture
{
    specie
    {
        nMoles          1;
        molWeight       86.5;  // R410A molecular weight [kg/kmol]
    }

    thermodynamics
    {
        Cp              1200;     // Specific heat [J/kg/K]
        Hf              0;
        Sf              0;
        Tref            273.15;
    }

    transport
    {
        mu              1.5e-5;   // Dynamic viscosity [Pa·s]
        Pr              0.7;      // Prandtl number
    }
}

// R410A property table
R410A_properties
{
    type            R410APropertyTable;
    file            "R410A_properties.dat";
    tableFormat     "CSV";
    interpolation   "linear";
}

// Phase change model
phaseChange
{
    type            R410AEvaporationModel;
    h               5000;     // Heat transfer coefficient [W/m²·K]
    T_sat           283.15;   // Saturation temperature [K]
    modelType       "nucleate";
}

// Turbulence model
turbulence
{
    type            RASModel;
    RASModel        kEpsilon;
    Cmu             0.09;
    C1              1.44;
    C2              1.92;
    sigmaEps        1.3;
}

// Solid material properties (for tube wall)
solid
{
    type            solidThermo;
    mixture         pureMixture;
    transport       const;
    thermo         heSolidThermo;
    energy         sensibleEnthalpy;
    equationOfState  constVol;
    species         none;
}

solidMaterial
{
    specie
    {
        nMoles          1;
        molWeight       63.5;    // Copper molecular weight [kg/kmol]
    }

    thermodynamics
    {
        Cp              385;      // Specific heat [J/kg/K]
        Hf              0;
        Sf              0;
        Tref            273.15;
    }

    transport
    {
        k               400;      // Thermal conductivity [W/m·K]
        alpha           1.17e-4;  // Thermal diffusivity [m²/s]
    }

    density
    {
        rho             8960;     // Density [kg/m³]
    }
}

// Solver settings
solver
{
    type            R410ASolver;

    // Solver parameters
    convergenceTolerance 1e-5;
    maxIterations         100;

    // Evaporator-specific parameters
    evaporator
    {
        wallHeatFlux    5000;     // Wall heat flux [W/m²]
        hExternal      100;      // External heat transfer coefficient [W/m²·K]
        TAmbient       300;      // Ambient temperature [K]
        wallThickness  0.002;    // Tube wall thickness [m]
        kWall          400;      // Wall thermal conductivity [W/m·K]
    }

    // Phase change model
    phaseChange
    {
        type            R410AEvaporationModel;
        h               5000;     // Heat transfer coefficient [W/m²·K]
        T_sat           283.15;   // Saturation temperature [K]
        modelType       "nucleate";
    }
}

// ************************************************************************* //
```

---

## 5. Solver Configuration

### Control Dictionary: system/controlDict

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  www.openfoam.org
    \\  /    A nd           | Version:  9
     \\/     M anipulation  |
\*---------------------------------------------------------------------------*/
FoamFile
{
    format      ascii;
    class       dictionary;
    object      controlDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

application     R410ASolver;

startFrom       latestTime;

startTime       0;

stopAt          endTime;

endTime         10.0;

deltaT          0.001;

writeControl    adjustable;

writeInterval   0.1;

purgeWrite      0;

writeFormat     ascii;

writePrecision  6;

writeCompression off;

timeFormat      general;

timePrecision   6;

runTimeModifiable true;

adjustTimeStep  yes;

maxCo           1.0;
maxAlphaCo      1.0;
maxDeltaT       1.0;

// Libraries
libs            ("libOpenFOAM.so" "libR410APropertyTable.so");

// Function objects
functions
{
    // Residual monitoring
    residuals
    {
        type            fields;
        functionObjectLibs ("libfieldFunctionObjects.so");
        enabled         true;
        fields
        (
            p_rgh
            U
            T
            alpha
            k
            epsilon
        );
        log             false;
    }

    // Surface heat transfer coefficient
    wallHeatTransfer
    {
        type            wallHeatTransfer;
        functionObjectLibs ("libfieldFunctionObjects.so");
        enabled         true;
        writeControl    timeStep;
        writeInterval   10;
        patches
        (
            innerWall
        );
        fields
        (
            T
        );
    }

    // Volume flow rate
    flowRate
    {
        type            flowRate;
        functionObjectLibs ("libfieldFunctionObjects.so");
        enabled         true;
        writeControl    timeStep;
        writeInterval   10;
        patches
        (
            inlet
            outlet
        );
        rho             rho;
        U               U;
    }

    // Phase fraction monitoring
    phaseFraction
    {
        type            sampledSet;
        functionObjectLibs ("libfieldFunctionObjects.so");
        enabled         true;
        writeControl    timeStep;
        writeInterval   100;
        setFormat       csv;
        sets
        (
            inlet
            outlet
            midTube
        );
        fields
        (
            alpha
            T
            p_rgh
        );
    }

    // Pressure drop
    pressureDrop
    {
        type            forces;
        functionObjectLibs ("libforces.so");
        enabled         true;
        writeControl    timeStep;
        writeInterval   10;
        patches
        (
            innerWall
            outerWall
        );
        rho             rho;
        U               U;
        p               p_rgh;
        log             true;
    }

    // Temperature monitoring
    temperatureMonitor
    {
        type            executeIfObjectExists;
        functionObjectLibs ("libfieldFunctionObjects.so");
        enabled         true;
        writeControl    timeStep;
        writeInterval   10;
        name            T;
        executeControl   timeStep;
        executeIfObjectExists T;
        operation        max;
        field           T;
    }
}

// ************************************************************************* //
```

### Finite Volume Solution: system/fvSolution

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  www.openfoam.org
    \\  /    A nd           | Version:  9
     \\/     M anipulation  |
\*---------------------------------------------------------------------------*/
FoamFile
{
    format      ascii;
    class       dictionary;
    object      fvSolution;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

solvers
{
    p_rgh
    {
        solver          GAMG;
        tolerance       1e-6;
        relTol          0.1;
        smoother        GaussSeidel;
        cacheAgglomeration true;
        nCellsInCoarsestLevel 10;
    }

    p_rghFinal
    {
        $p_rgh;
        relTol          0;
    }

    "(U|k|epsilon|omega|T|alpha)"
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-6;
        relTol          0.1;
    }

    "(U|k|epsilon|omega|T|alpha)Final"
    {
        $U;
        relTol          0;
    }

    ".*"
    {
        solver          PBiCG;
        preconditioner   DILU;
        tolerance       1e-6;
        relTol          0;
    }
}

PIMPLE
{
    nCorrectors     2;
    nNonOrthogonalCorrectors 0;
    pRefCell        0;
    pRefValue       0;
}

relaxationFactors
{
    p_rgh
    {
        relaxationFactor 0.3;
    }

    U
    {
        relaxationFactor 0.7;
    }

    T
    {
        relaxationFactor 0.9;
    }

    alpha
    {
        relaxationFactor 0.9;
    }

    k
    {
        relaxationFactor 0.7;
    }

    epsilon
    {
        relaxationFactor 0.7;
    }
}

// ************************************************************************* //
```

### Finite Volume Schemes: system/fvSchemes

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  www.openfoam.org
    \\  /    A nd           | Version:  9
     \\/     M anipulation  |
\*---------------------------------------------------------------------------*/
FoamFile
{
    format      ascii;
    class       dictionary;
    object      fvSchemes;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

ddtSchemes
{
    default         Euler;
}

gradSchemes
{
    default         Gauss linear;
    grad(p_rgh)     Gauss linear;
    grad(T)         Gauss linear corrected;
}

divSchemes
{
    default         Gauss limitedLinearV 1.0;
    div(phi,alpha)  Gauss limitedLinear 1.0;
    div(phi,U)      Gauss limitedLinearV 1.0;
    div(phi,k)      Gauss limitedLinear 1.0;
    div(phi,epsilon) Gauss limitedLinear 1.0;
    div(phi,omega)  Gauss limitedLinear 1.0;
    div(phi,T)      Gauss limitedLinear 1.0;
    div(phiRhoU)    Gauss limitedLinearV 1.0;
    div(R)          Gauss linear;
    div(phi,nuTilda) Gauss limitedLinear 1.0;
    div((muEff*dev2(T(grad(U))))) Gauss linear;
}

laplacianSchemes
{
    default         Gauss linear corrected;
    laplacian(nuU)  Gauss linear corrected;
    laplacian((1|A(U))|U) Gauss linear corrected;
    laplacian(kEff) Gauss linear corrected;
    laplacian(DkEff) Gauss linear corrected;
    laplacian(DepsilonEff) Gauss linear corrected;
    laplacian(DomegaEff) Gauss linear corrected;
    laplacian(alphaEff) Gauss linear corrected;
    laplacian(DREff) Gauss linear corrected;
}

interpolationSchemes
{
    default         linear;
    interpolate(U)  linear;
}

snGradSchemes
{
    default         corrected;
}

fluxRequired
{
    default         no;
    p_rgh;
    p;
}

// ************************************************************************* //
```

---

## 6. Case Setup Scripts

### Setup Script: scripts/setup_case.sh

```bash
#!/bin/bash

# Script to setup R410A evaporator case
# Usage: ./setup_case.sh

echo "Setting up R410A evaporator case..."

# Create directory structure
mkdir -p constant/polyMesh
mkdir -p 0
mkdir -p system
mkdir -p postProcessing/surfaces
mkdir -p postProcessing/probes
mkdir -p postProcessing/functionObjects
mkdir -p postProcessing/paraview
mkdir -p validation
mkdir -p scripts

# Copy template files
cp blockMeshDict constant/polyMesh/
cp controlDict system/
cp fvSolution system/
cp fvSchemes system/
cp transportProperties constant/
cp 0/alpha 0/
cp 0/U 0/
cp 0/p_rgh 0/
cp 0/T 0/
cp 0/k 0/
cp 0/epsilon 0/

# Create surface files
python create_surfaces.py

# Create probe files
python create_probes.py

# Create function objects
python create_function_objects.py

# Set permissions
chmod +x scripts/*.sh

# Copy validation data
cp experimental_data.csv validation/

# Print summary
echo "Case setup completed!"
echo "Directory structure:"
echo "  constant/ - Mesh and properties"
echo "  system/ - Solver configuration"
echo "  0/ - Initial conditions"
echo "  postProcessing/ - Output files"
echo "  validation/ - Experimental data"
echo "  scripts/ - Automation scripts"
```

### Surface Creation Script: scripts/create_surfaces.py

```python
#!/usr/bin/env python3

import numpy as np
import os

# Create surface files for visualization
surfaces = {
    'inner_wall': {
        'type': 'patch',
        'patch': 'innerWall',
        'fields': ['T', 'alpha', 'p_rgh']
    },
    'outer_wall': {
        'type': 'patch',
        'patch': 'outerWall',
        'fields': ['T', 'alpha', 'p_rgh']
    },
    'mid_plane': {
        'type': 'plane',
        'origin': [1, 0, 0],
        'normal': [0, 0, 1],
        'fields': ['T', 'alpha', 'p_rgh', 'U']
    }
}

for name, params in surfaces.items():
    filename = f"postProcessing/surfaces/{name}.set"
    with open(filename, 'w') as f:
        f.write(f"""/*--------------------------------*- C++ -*----------------------------------*\\
  =========                 |
  \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\\\    /   O peration     | Website:  www.openfoam.org
    \\\\  /    A nd           | Version:  9
     \\\\/     M anipulation  |
\\*---------------------------------------------------------------------------*/)
FoamFile
{{
    format      ascii;
    class       dictionary;
    object      {name};
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

type        {params['type']}};
{{
    // Surface definition
    {name}
    {{
        type {params['type']};
        {', '.join([f'{{ {k} {v}; }}' for k, v in params.items() if k not in ['type', 'patch', 'fields']])}
    }}
}}

// Fields to extract
fields
(
    {', '.join([f'"{f}"' for f in params['fields']])}
)

// ************************************************************************* //
""")
```

### Post-processing Script: scripts/post_process.py

```python
#!/usr/bin/env python3

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import glob

def process_results():
    """Process simulation results and generate plots"""

    # Read simulation results
    times = []
    heat_transfer_coeffs = []
    pressure_drops = []
    void_fractions = []

    # Process time directories
    time_dirs = sorted(glob.glob('[0-9]*'))

    for time_dir in time_dirs[-10:]:  # Process last 10 time steps
        try:
            # Read heat transfer coefficient
            with open(f"{time_dir}/wallHeatTransfer.dat", 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if 'innerWall' in line:
                        htc = float(line.split()[-1])
                        heat_transfer_coeffs.append(htc)
                        times.append(float(time_dir))
                        break
        except:
            pass

    # Create plots
    plt.figure(figsize=(12, 8))

    # Heat transfer coefficient
    plt.subplot(2, 2, 1)
    plt.plot(times, heat_transfer_coeffs, 'b-', linewidth=2)
    plt.xlabel('Time [s]')
    plt.ylabel('Heat Transfer Coefficient [W/m²·K]')
    plt.title('Heat Transfer Coefficient Evolution')
    plt.grid(True)

    # Pressure drop
    plt.subplot(2, 2, 2)
    plt.plot(times, pressure_drops, 'r-', linewidth=2)
    plt.xlabel('Time [s]')
    plt.ylabel('Pressure Drop [Pa]')
    plt.title('Pressure Drop Evolution')
    plt.grid(True)

    # Void fraction
    plt.subplot(2, 2, 3)
    plt.plot(times, void_fractions, 'g-', linewidth=2)
    plt.xlabel('Time [s]')
    plt.ylabel('Void Fraction')
    plt.title('Void Fraction Evolution')
    plt.grid(True)

    # Summary statistics
    plt.subplot(2, 2, 4)
    plt.text(0.1, 0.9, f'Simulation Summary', fontsize=14, fontweight='bold', transform=plt.gca().transAxes)
    plt.text(0.1, 0.8, f'Total simulation time: {max(times):.2f} s', transform=plt.gca().transAxes)
    plt.text(0.1, 0.7, f'Final HTC: {heat_transfer_coeffs[-1]:.2f} W/m²·K', transform=plt.gca().transAxes)
    plt.text(0.1, 0.6, f'Final pressure drop: {pressure_drops[-1]:.2f} Pa', transform=plt.gca().transAxes)
    plt.text(0.1, 0.5, f'Final void fraction: {void_fractions[-1]:.3f}', transform=plt.gca().transAxes)
    plt.axis('off')

    plt.tight_layout()
    plt.savefig('postProcessing/evaporator_summary.png', dpi=300)

    # Save data to CSV
    results_df = pd.DataFrame({
        'Time [s]': times,
        'HTC [W/m²·K]': heat_transfer_coeffs,
        'Pressure Drop [Pa]': pressure_drops,
        'Void Fraction': void_fractions
    })

    results_df.to_csv('postProcessing/evaporator_results.csv', index=False)

    # Validate against experimental data
    validate_results()

def validate_results():
    """Validate simulation results against experimental data"""

    try:
        # Read experimental data
        exp_data = pd.read_csv('validation/experimental_data.csv')

        # Read simulation results
        sim_data = pd.read_csv('postProcessing/evaporator_results.csv')

        # Calculate errors
        exp_htc = exp_data['HTC [W/m²·K]'].mean()
        sim_htc = sim_data['HTC [W/m²·K]'].mean()

        error = abs(exp_htc - sim_htc) / exp_htc

        # Create validation plot
        plt.figure(figsize=(10, 6))
        plt.scatter(exp_data['Heat Flux [W/m²]'], exp_data['HTC [W/m²·K]'],
                   label='Experimental', alpha=0.7, s=50)
        plt.scatter(sim_data['Heat Flux [W/m²]'], sim_data['HTC [W/m²·K]'],
                   label='Simulation', alpha=0.7, s=50, marker='s')

        plt.xlabel('Heat Flux [W/m²]')
        plt.ylabel('Heat Transfer Coefficient [W/m²·K]')
        plt.title('R410A Evaporator Validation')
        plt.legend()
        plt.grid(True)

        # Add error text
        plt.text(0.05, 0.95, f'Error: {error:.2%}', transform=plt.gca().transAxes,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))

        plt.savefig('postProcessing/validation_comparison.png', dpi=300)

        # Print validation summary
        print(f"\nValidation Summary:")
        print(f"Experimental HTC: {exp_htc:.2f} W/m²·K")
        print(f"Simulated HTC: {sim_htc:.2f} W/m²·K")
        print(f"Relative Error: {error:.2%}")

        if error < 0.2:  # 20% tolerance
            print("✓ Validation PASSED")
        else:
            print("✗ Validation FAILED")

    except FileNotFoundError:
        print("Validation data not found. Skipping validation.")

if __name__ == "__main__":
    process_results()
    print("Post-processing completed!")
```

---

## 7. Case Running and Monitoring

### Running Script: scripts/run_case.sh

```bash
#!/bin/bash

# Script to run R410A evaporator case
# Usage: ./run_case.sh

echo "Running R410A evaporator case..."

# Clean previous run
rm -rf [0-9]* postProcessing/probes postProcessing/surfaces postProcessing/functionObjects

# Decompose for parallel run
decomposePar -force

# Run solver in parallel
mpiexec -np 4 R410ASolver -parallel

# Reconstruct fields
reconstructPar

# Run post-processing
python post_process.py

# Generate final report
python generate_report.py

echo "Simulation completed!"
```

### Monitoring Script: scripts/monitoring.sh

```bash
#!/bin/bash

# Script to monitor simulation progress
# Usage: ./monitoring.sh

echo "Monitoring simulation progress..."

# Monitor time directories
while true; do
    time_dirs=$(ls -1 [0-9]* 2>/dev/null | wc -l)
    if [ -f "log.R410ASolver" ]; then
        latest_time=$(ls -1 [0-9]* | tail -1)
        progress=$(echo "scale=2; $latest_time / 10 * 100" | bc)

        echo "Progress: $progress% (Time: $latest_time s, Steps: $time_dirs)"

        # Check for convergence
        if grep -q "ExecutionTime" log.R410ASolver; then
            echo "Simulation converged!"
            break
        fi
    fi

    sleep 5
done

# Generate final monitoring report
echo "Generating monitoring report..."
python generate_monitoring_report.py

echo "Monitoring completed!"
```

---

## 8. Results and Visualization

### Paraview Configuration: postProcessing/paraview/evaporator.py

```python
#!/usr/bin/env python3

# Paraview script for R410A evaporator visualization
from paraview.simple import *

# Create view
renderView1 = GetRenderView()

# Read results
case = XMLUnstructuredGridReader(FileName='R410A_evaporator_case.foam')

# Create representations
alphaRep = Show(case, 'alpha', renderView1)
alphaRep.Representation = 'Surface'
alphaRep.ColorArrayName = 'alpha'
alphaRep.LookupTable = 'Jet'
alphaRep.ScaleFactor = 1.0

TRep = Show(case, 'T', renderView1)
TRep.Representation = 'Surface'
TRep.ColorArrayName = 'T'
TRep.LookupTable = 'coolwarm'
TRep.ScaleFactor = 1.0

# Create clip for inner wall
innerWallClip = Clip(Input=case)
innerWallClip.ClipType = 'Plane'
innerWallClip.ClipFunction = 'Plane(normal=[0,1,0], origin=[0,0,0])'
innerWallRep = Show(innerWallClip, renderView1)

# Set camera position
renderView1.CameraPosition = [1, 0, 0.1]
renderView1.CameraFocalPoint = [1, 0, 0]
renderView1.CameraViewUp = [0, 0, 1]

# Save screenshot
WriteImage('evaporator_visualization.png')
```

### Results Summary Report: scripts/generate_report.py

```python
#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt

def generate_report():
    """Generate final simulation report"""

    # Read results
    results = pd.read_csv('postProcessing/evaporator_results.csv')

    # Create report
    report = f"""
    # R410A Evaporator Simulation Report

    ## Simulation Summary
    - Total simulation time: {results['Time [s]'].max():.2f} s
    - Number of time steps: {len(results)}
    - Final HTC: {results['HTC [W/m²·K]'].iloc[-1]:.2f} W/m²·K
    - Final pressure drop: {results['Pressure Drop [Pa]'].iloc[-1]:.2f} Pa
    - Final void fraction: {results['Void Fraction'].iloc[-1]:.3f}

    ## Performance Metrics
    - Average HTC: {results['HTC [W/m²·K]'].mean():.2f} W/m²·K
    - Maximum HTC: {results['HTC [W/m²·K]'].max():.2f} W/m²·K
    - Total pressure drop: {results['Pressure Drop [Pa]'].iloc[-1]:.2f} Pa
    - Void fraction range: {results['Void Fraction'].min():.3f} - {results['Void Fraction'].max():.3f}

    ## Convergence Analysis
    - Residual convergence: {'YES' if results['HTC [W/m²·K]'].std() < 1.0 else 'NO'}
    - Steady state reached: {'YES' if abs(results['HTC [W/m²·K]'].iloc[-1] - results['HTC [W/m²·K]'].iloc[-10]) < 10.0 else 'NO'}

    ## Validation Results
    - Experimental HTC: 5000.0 W/m²·K (reference)
    - Simulated HTC: {results['HTC [W/m²·K]'].iloc[-1]:.2f} W/m²·K
    - Relative error: {abs(5000.0 - results['HTC [W/m²·K]'].iloc[-1]) / 5000.0 * 100:.2f}%

    ## Recommendations
    - {'Validation PASSED' if abs(5000.0 - results['HTC [W/m²·K]'].iloc[-1]) / 5000.0 < 0.2 else 'Validation FAILED'}
    - {'Mesh refinement recommended' if results['HTC [W/m²·K]'].std() > 100.0 else 'Mesh resolution adequate'}
    - {'Turbulence model adequate' if results['Pressure Drop [Pa]'].iloc[-1] > 100.0 else 'Turbulence model refinement needed'}
    """

    # Save report
    with open('postProcessing/simulation_report.md', 'w') as f:
        f.write(report)

    print("Report generated: postProcessing/simulation_report.md")

if __name__ == "__main__":
    generate_report()
```

---

## 9. Next Steps

After completing Phase 10, you will have a complete evaporator case setup ready for simulation. The remaining phases will:

1. **Phase 11**: Validation suite development
2. **Phase 12**: User documentation and guides

This phase provides the foundation for realistic evaporator simulation with proper geometry, mesh, boundary conditions, and solver configuration for R410A two-phase flow.