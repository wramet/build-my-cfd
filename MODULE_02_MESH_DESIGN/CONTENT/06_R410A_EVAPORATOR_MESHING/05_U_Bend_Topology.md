# R410A U-Bend Evaporator Meshing (คู่มือ Meshing เครื่องระเหยรูป U-Bend สำหรับ R410A)

## Introduction to U-Bend Meshing Challenges

U-bend evaporators are commonly used in R410A systems to enhance heat transfer through flow separation and recirculation. These geometries present unique meshing challenges due to complex flow patterns and curvature effects.

### ⭐ U-Bend Geometry Specifications

| Parameter | Value | Description |
|-----------|-------|-------------|
| Tube ID | 5mm | Inner diameter |
| Leg length | 0.3m | Each straight section |
| Bend radius | 30mm | Centerline radius |
| Total length | ~0.94m | Effective length |
| Bend angle | 180° | Full U-turn |
| Material | Copper | Thermal conductivity |

### Flow Characteristics in U-Bend

**1. Secondary Flows**
- Dean vortices in curved regions
- Centrifugal force effects
- Flow separation at inner/outer walls

**2. Two-Phase Effects**
- Phase separation due to centrifugal forces
- Liquid accumulation at outer bend
- Vapor formation at inner bend

**3. Heat Transfer Variations**
- Enhanced heat transfer in bend region
- Local boiling phenomena
- Film condensation on outer wall

## U-Bend Topology Design

### ⭐ O-Grid Approach for U-Bends

The O-grid approach is recommended for U-bend geometries as it provides good cell quality in curved regions.

```
┌─────────────────────────────────────────────────────────────┐
│  Inlet Block  │  Bend Region  │  Outlet Block              │
│               │               │                           │
│  Block 1      │   Bend       │  Block 3                  │
│  (50×100)     │   (60×60)    │  (50×100)                 │
├───────────────┼──────────────┼───────────────────────────┤
│  Block 2      │   Bend       │  Block 4                  │
│  (50×100)     │   (60×60)    │  (50×100)                 │
└─────────────────────────────────────────────────────────────┘
```

### Vertex Coordinates for U-Bend

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
|  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|   \\    /   O peration     | Version: 8.x                                    |
|    \\  /    A nd           | Web:      www.openfoam.com                      |
|     \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

convertToMeters 0.001;

// U-bend geometry with 30mm radius
// Tube diameter: 5mm (2.5mm radius)
// Leg length: 300mm each
// Total bend radius: 30mm (centerline)

vertices
(
    // Inlet leg vertices (z = 0)
    (-0.35, -0.0025, 0)      // 0: inlet bottom-left
    (-0.05, -0.0025, 0)      // 1: inlet bottom-right
    (-0.35, 0.0025, 0)       // 2: inlet top-left
    (-0.05, 0.0025, 0)       // 3: inlet top-right

    // Bend region vertices (inner side)
    (-0.05, -0.0025, -0.03)  // 4: bend inner bottom
    (-0.0275, -0.0025, -0.0275) // 5: bend inner-mid
    (-0.0275, -0.0025, -0.0025) // 6: bend inner-out
    (0.0275, -0.0025, -0.0025)  // 7: bend mid-out
    (0.05, -0.0025, -0.0025)   // 8: bend outer bottom
    (0.05, -0.0025, 0.0025)    // 9: bend outer-out
    (0.0275, -0.0025, 0.0025)  // 10: bend mid-out
    (0.0275, -0.0025, 0.0275)  // 11: bend outer-mid
    (0.0275, -0.0025, 0.03)   // 12: bend outer-end

    // Bend region vertices (outer side)
    (-0.05, 0.0025, -0.03)   // 13: bend inner-top
    (-0.0275, 0.0025, -0.0275) // 14: bend inner-mid
    (-0.0275, 0.0025, -0.0025) // 15: bend inner-out
    (0.0275, 0.0025, -0.0025)  // 16: bend mid-out
    (0.05, 0.0025, -0.0025)   // 17: bend outer top
    (0.05, 0.0025, 0.0025)    // 18: bend outer-out
    (0.0275, 0.0025, 0.0025)  // 19: bend mid-out
    (0.0275, 0.0025, 0.0275)  // 20: bend outer-mid
    (0.0275, 0.0025, 0.03)   // 21: bend outer-end

    // Outlet leg vertices (z = 0)
    (0.05, -0.0025, 0.03)    // 22: outlet bottom-left
    (0.35, -0.0025, 0.03)    // 23: outlet bottom-right
    (0.05, 0.0025, 0.03)     // 24: outlet top-left
    (0.35, 0.0025, 0.03)     // 25: outlet top-right
);

blocks
(
    // Inlet leg blocks
    hex (0 1 4 13 2 3 15 14) (50 100 1)  // Bottom inlet
    hex (1 5 4 0 3 14 15 2) (50 100 1)   // Bottom inlet

    // Bend region blocks (inner side)
    hex (4 5 6 13 13 14 15 15) (30 30 1)  // Inner bend section 1
    hex (5 7 6 0 14 16 15 2) (30 30 1)    // Inner bend section 2
    hex (7 8 9 0 16 18 19 2) (30 30 1)    // Outer bend section 1
    hex (9 10 11 0 19 20 21 2) (30 30 1)  // Outer bend section 2

    // Bend region blocks (outer side)
    hex (13 14 15 15 13 14 15 15) (30 30 1) // Outer bend section 1
    hex (14 16 15 13 15 19 20 14) (30 30 1) // Outer bend section 2
    hex (16 18 19 15 19 20 21 20) (30 30 1) // Outer bend section 3

    // Outlet leg blocks
    hex (11 21 22 22 21 25 24 24) (50 100 1) // Bottom outlet
    hex (21 22 23 25 24 25 26 26) (50 100 1)  // Bottom outlet
);
```

### Boundary Configuration for U-Bend

```cpp
boundary
{
    inlet
    {
        type patch;
        faces
        (
            (0 1 4 13 2 3 15 14)  // Inlet face
        );
    }

    outlet
    {
        type patch;
        faces
        (
            (11 21 22 25 24 25 26 26)  // Outlet face
        );
    }

    wall
    {
        type wall;
        faces
        (
            // Inlet leg walls
            (0 2 1 4)      // Inlet bottom wall
            (2 3 15 14)    // Inlet top wall
            (0 4 5 1)      // Inlet side walls

            // Bend region walls
            (4 5 6 13)     // Bend inner wall
            (13 15 14 6)   // Bend top wall
            (6 15 16 5)    // Bend outer wall

            (7 8 9 16)     // Bend outer bottom
            (16 19 18 9)   // Bend outer top

            // Outlet leg walls
            (11 21 22 24)  // Outlet bottom wall
            (24 25 26 21)  // Outlet top wall
            (22 23 25 24)  // Outlet side walls
        );

        // R410A-specific boundary layer
        boundaryLayer
        {
            nLayers        20;
            expansionRatio  1.25;
            firstCellThickness 5e-6;      // 5 μm for y+ < 1
            minThickness    0.00025;     // 250 μm total

            // Enhanced grading in bend region
            bendRefinement  true;
            maxCurvature    0.5;         // Maximum allowed curvature
        }
    }

    empty
    {
        type empty;
        faces
        (
            // Cross-sections for 2D axisymmetric case
            (0 1 4 13)     // Inlet cross-section
            (1 5 4 0)      // Inlet inner cross-section
            (4 5 6 13)     // Bend inner cross-section
            (6 15 16 5)    // Bend outer cross-section
            (11 21 22 24)  // Outlet cross-section
        );
    }
}

mergePatchPairs
(
);
```

## Quality Checks for U-Bend Mesh

### ⭐ Critical Quality Metrics for U-Bends

| Metric | Target Value | R410A Consideration |
|--------|--------------|---------------------|
| Non-orthogonality | < 60° | Critical in bend |
| Max skewness | < 3.0 | Important for accuracy |
| Aspect ratio | < 10 | Higher in bend regions |
| Cell volume ratio | < 100 | Monitor in transition |
| Curvature resolution | > 5 cells/bend | Ensure smooth flow |

### Quality Check Commands

```bash
# Basic mesh quality check
checkMesh -all -time 1

# Focus on orthogonality in bend regions
checkMesh -nonOrtho -time 1

# Report cell distribution
checkMesh -report -time 1 > ubend_quality_report.txt

# Visualize in ParaView
paraFoam
```

### Acceptable Orthogonality in Bend Regions

```
Bend Region Acceptance:
- Inner bend: < 50° orthogonality
- Outer bend: < 40° orthogonality
- Transition zones: < 60° orthogonality
- Straight sections: < 30° orthogonality
```

## Advanced U-Bend Strategies

### ⭐ Multi-Block Approach with Local Refinement

For better resolution in critical regions:

```cpp
// Add refinement zones for Dean vortices
refinementRegions
{
    deanVortexRegion
    {
        mode            distance;
        levels          ((0.005 3)(0.01 2));
        distance        0.005;      // 5mm from inner bend
    }

    heatTransferRegion
    {
        mode            distance;
        levels          ((0.005 2)(0.01 1));
        distance        0.005;      // 5mm from outer wall
    }
}
```

### ⭐ Curvature-Sensitive Grading

```cpp
// Implement grading that accounts for curvature
blocks
(
    // Straight sections (coarser grading)
    hex (0 1 4 13 2 3 15 14) (50 100 1)
    grading (1 1 30 1 1 30 1 1 1 1 1 1)  // Coarse radial grading

    // Bend region (finer grading)
    hex (4 5 6 13 13 14 15 15) (40 40 1)
    grading (40 1 40 40 1 40 40 1 40 1 40 40)  // Fine radial grading
);
```

### ⭐ R410A-Specific Considerations

#### Two-Phase Flow in U-Bend

```cpp
// Two-phase meshing considerations
twoPhaseMeshing
{
    // Interface refinement
    interfaceRefinement
    {
        mode            distance;
        levels          ((0.001 3)(0.005 2));
        distance        0.001;      // 1mm from interface
    }

    // Phase-specific meshing
    phaseDistribution
    {
        liquid
        {
            region         outerBend;  // Liquid accumulates here
            refinement      2;
        }
        vapor
        {
            region         innerBend;  // Vapor forms here
            refinement      3;
        }
    }
}
```

#### Heat Transfer Enhancement

```cpp
// Enhanced meshing for heat transfer regions
heatTransferMeshing
{
    // Wall-adjacent cells for heat transfer
    boundaryLayer
    {
        nLayers         25;
        expansionRatio  1.2;
        firstCellThickness 3e-6;      // 3 μm for heat transfer
        minThickness    0.0003;      // 300 μm total
    }

    // Temperature gradient refinement
    thermalGradient
    {
        mode            gradient;
        field          T;
        levels          ((0.001 2)(0.005 1));
    }
}
```

## Complete U-Bend Meshing Example

### ⭐ Complete blockMeshDict with All Features

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
|  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|   \\    /   O peration     | Version: 8.x                                    |
|    \\  /    A nd           | Web:      www.openfoam.com                      |
|     \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

convertToMeters 0.001;

vertices
(
    // Inlet leg vertices
    (-0.35, -0.0025, 0)      // 0
    (-0.05, -0.0025, 0)      // 1
    (-0.35, 0.0025, 0)       // 2
    (-0.05, 0.0025, 0)       // 3

    // Bend region vertices - inner
    (-0.05, -0.0025, -0.03)  // 4
    (-0.0275, -0.0025, -0.0275) // 5
    (-0.0275, -0.0025, -0.0025) // 6
    (0.0275, -0.0025, -0.0025)  // 7
    (0.05, -0.0025, -0.0025)   // 8
    (0.05, -0.0025, 0.0025)    // 9
    (0.0275, -0.0025, 0.0025)  // 10
    (0.0275, -0.0025, 0.0275)  // 11
    (0.0275, -0.0025, 0.03)   // 12

    // Bend region vertices - outer
    (-0.05, 0.0025, -0.03)   // 13
    (-0.0275, 0.0025, -0.0275) // 14
    (-0.0275, 0.0025, -0.0025) // 15
    (0.0275, 0.0025, -0.0025)  // 16
    (0.05, 0.0025, -0.0025)   // 17
    (0.05, 0.0025, 0.0025)    // 18
    (0.0275, 0.0025, 0.0025)  // 19
    (0.0275, 0.0025, 0.0275)  // 20
    (0.0275, 0.0025, 0.03)   // 21

    // Outlet leg vertices
    (0.05, -0.0025, 0.03)    // 22
    (0.35, -0.0025, 0.03)    // 23
    (0.05, 0.0025, 0.03)     // 24
    (0.35, 0.0025, 0.03)     // 25
);

blocks
(
    // Inlet leg
    hex (0 1 4 13 2 3 15 14) (50 100 1)
    grading (1 1 30 1 1 30 1 1 1 1 1 1)

    hex (1 5 4 0 3 14 15 2) (50 100 1)
    grading (30 1 30 30 1 30 30 1 30 1 30 30)

    // Bend region - inner
    hex (4 5 6 13 13 14 15 15) (40 40 1)
    grading (40 1 40 40 1 40 40 1 40 1 40 40)

    hex (5 7 6 0 14 16 15 2) (40 40 1)
    grading (40 1 40 40 1 40 40 1 40 1 40 40)

    hex (7 8 9 16 16 18 19 0) (40 40 1)
    grading (40 1 40 40 1 40 40 1 40 1 40 40)

    hex (9 10 11 0 19 20 21 2) (40 40 1)
    grading (40 1 40 40 1 40 40 1 40 1 40 40)

    // Bend region - outer
    hex (13 14 15 15 13 14 15 15) (40 40 1)
    grading (40 1 40 40 1 40 40 1 40 1 40 40)

    hex (14 16 15 13 15 19 20 14) (40 40 1)
    grading (40 1 40 40 1 40 40 1 40 1 40 40)

    hex (16 18 19 15 19 20 21 20) (40 40 1)
    grading (40 1 40 40 1 40 40 1 40 1 40 40)

    // Outlet leg
    hex (11 21 22 25 24 25 26 26) (50 100 1)
    grading (1 1 30 1 1 30 1 1 1 1 1 1)

    hex (21 22 23 25 24 25 26 26) (50 100 1)
    grading (30 1 30 30 1 30 30 1 30 1 30 30)
);

boundary
{
    inlet
    {
        type patch;
        faces
        (
            (0 1 4 13 2 3 15 14)
        );
    }

    outlet
    {
        type patch;
        faces
        (
            (11 21 22 25 24 25 26 26)
        );
    }

    wall
    {
        type wall;
        faces
        (
            // Inlet leg walls
            (0 2 1 4)      // Bottom
            (2 3 15 14)    // Top
            (0 4 5 1)      // Side

            // Bend region walls
            (4 5 6 13)     // Inner wall
            (13 15 14 6)   // Top wall
            (6 15 16 5)    // Outer wall

            (7 8 9 16)     // Outer bottom
            (16 19 18 9)   // Outer top

            // Outlet leg walls
            (11 21 22 24)  // Bottom
            (24 25 26 21)  // Top
            (22 23 25 24)  // Side
        );

        // R410A boundary layer
        boundaryLayer
        {
            nLayers         20;
            expansionRatio  1.25;
            firstCellThickness 5e-6;
            minThickness    0.00025;

            // Bend-specific parameters
            bendRefinement  true;
            maxCurvature    0.5;
            deanVortex      true;
        }
    }

    empty
    {
        type empty;
        faces
        (
            (0 1 4 13)     // Inlet cross-section
            (1 5 4 0)      // Inner inlet
            (4 5 6 13)     // Bend inner
            (6 15 16 5)    // Bend outer
            (11 21 22 24)  // Outlet cross-section
        );
    }
}

mergePatchPairs
(
);

// Add refinement regions
refinementRegions
{
    deanVortex
    {
        mode            distance;
        levels          ((0.005 3)(0.01 2));
        distance        0.005;
    }

    heatTransfer
    {
        mode            distance;
        levels          ((0.005 2)(0.01 1));
        distance        0.005;
    }
}
```

### ⭐ Mesh Generation and Validation

```bash
# Navigate to case directory
cd /path/to/r410a_ubend_case

# Generate mesh
blockMesh

# Check mesh quality
checkMesh -all

# Generate y+ report
yPlus -latestTime > ubend_yplus_report.txt

# Visualize and inspect
paraFoam

# Optional: Refine critical regions
snappyHexMesh -overwrite
```

## Performance Considerations for U-Bend Meshing

### ⭐ Computational Requirements

| Mesh Component | Cells | Memory (MB) | Time/iter (s) |
|----------------|-------|-------------|---------------|
| Inlet leg | 10,000 | 80 | 2-3 |
| Bend region | 64,000 | 512 | 5-8 |
| Outlet leg | 10,000 | 80 | 2-3 |
| Total | ~200,000 | ~1,200 | 15-25 |

### Optimization Strategies

1. **Symmetry**: Use 2D axisymmetric approximation
2. **Local refinement**: Only in critical regions
3. **Coarser grading**: In straight sections
4. **Parallel computing**: Domain decomposition

### Common Issues and Solutions

#### Issue 1: Poor Cell Quality in Bend
**Problem**: High skewness in curved regions
**Solution**:
1. Increase cells in bend: 40×40 → 60×60
2. Add intermediate vertices
3. Use smoother grading

```cpp
// Improved bend grading
hex (4 5 6 13 13 14 15 15) (60 60 1)
grading (60 1 60 60 1 60 60 1 60 1 60 60)
```

#### Issue 2: Insufficient Resolution for Dean Vortices
**Problem**: Can't capture secondary flows
**Solution**:
1. Add local refinement near inner bend
2. Increase radial resolution in bend
3. Implement dynamic refinement

```cpp
// Dean vortex refinement
refinementRegions
{
    deanVortex
    {
        mode            distance;
        levels          ((0.002 4)(0.005 2));
        distance        0.002;      // 2mm from inner wall
    }
}
```

#### Issue 3: Two-Phase Interface Accuracy
**Problem**: Interface not properly tracked in bend
**Solution**:
1. Implement interface refinement
2. Use higher-order schemes
3. Adaptive mesh refinement

```cpp
// Interface refinement
interfaceRefinement
{
    mode            distance;
    levels          ((0.0005 4)(0.001 3));
    distance        0.0005;     // 0.5mm from interface
}
```

## Advanced U-Bend Applications

### ⭐ Multiple U-Bend Configuration

For complex evaporator designs with multiple bends:

```cpp
// Additional bend configuration
vertices
(
    // Second bend vertices
    // ... (similar to first bend but different orientation)
);

blocks
(
    // First bend blocks
    // ... (as shown above)

    // Transition section
    hex (12 25 26 21 25 26 27 21) (50 50 1)

    // Second bend blocks (reversed orientation)
    // ... (mirror of first bend)
);
```

### ⭐ R410A-Specific Flow Considerations

```cpp
// R410A properties in U-bend flow
r410aFlowProperties
{
    // Operating conditions
    massFlux        200;        // kg/m²s
    temperature     283;        // K (10°C)
    pressure        1e6;        // Pa (1 MPa)

    // Two-phase parameters
    voidFraction    0.3;        // Initial void fraction
    heatFlux        15000;      // W/m² heat flux

    // Mesh requirements
    yPlusTarget     1.0;
    interfaceResolution 0.001;  // 1mm interface resolution
}
```

---

*Previous: [04_Boundary_Layer_Grading.md](04_Boundary_Layer_Grading.md) | Next: [06_Dynamic_Refinement.md](06_Dynamic_Refinement.md)*