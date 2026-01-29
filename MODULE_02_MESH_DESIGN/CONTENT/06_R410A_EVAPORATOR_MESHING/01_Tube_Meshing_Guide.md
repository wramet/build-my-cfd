# R410A Evaporator Tube Meshing Guide (คู่มือ Meshing ท่อระเหย R410A)

## Straight Tube Meshing for R410A

This guide provides detailed instructions for meshing straight tube evaporators used in R410A refrigeration systems. The focus is on achieving optimal resolution for two-phase flow while maintaining computational efficiency.

### ⭐ R410A Evaporator Tube Specifications

### Standard Dimensions
| Parameter | Value | Typical Range | Importance |
|-----------|-------|---------------|------------|
| Tube Inner Diameter (ID) | 5mm | 3-9mm | Affects cell count |
| Tube Length | 1.0m | 0.5-2.0m | Determines axial resolution |
| Wall Thickness | 0.8mm | 0.5-1.2mm | For thermal analysis |
| Material | Copper | Aluminum, Steel | Thermal conductivity |
| Operating Pressure | 1.0 MPa | 0.8-1.5 MPa | Property variations |

### Mesh Requirements
| Aspect | Target | Rationale |
|--------|--------|-----------|
| Radial Cells | 30-50 | Resolve velocity profile and phase change |
| Axial Cells | 200-400 | Capture flow development and heat transfer |
| Boundary Layer | 20 layers | Ensure y+ < 1 for wall functions |
| Total Cells | 200K-400K | Balance accuracy and computational cost |
| Aspect Ratio | < 5 | Maintain numerical stability |

### Step-by-Step Meshing Process

#### Step 1: Define Geometry Vertices

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
    // Bottom face vertices (z = 0)
    (0    -0.0025 -0.0025)  // 0: inlet bottom-left
    (0.5  -0.0025 -0.0025)  // 1: mid bottom-left
    (1.0  -0.0025 -0.0025)  // 2: outlet bottom-left

    // Top face vertices (z = 0.0025)
    (0     0.0025 -0.0025)  // 3: inlet top-left
    (0.5    0.0025 -0.0025)  // 4: mid top-left
    (1.0    0.0025 -0.0025)  // 5: outlet top-left

    // Bottom face vertices (z = 0.0025)
    (0    -0.0025  0.0025)  // 6: inlet bottom-right
    (0.5  -0.0025  0.0025)  // 7: mid bottom-right
    (1.0  -0.0025  0.0025)  // 8: outlet bottom-right

    // Top face vertices (z = -0.0025)
    (0     0.0025  0.0025)  // 9: inlet top-right
    (0.5    0.0025  0.0025)  // 10: mid top-right
    (1.0    0.0025  0.0025)  // 11: outlet top-right
);
```

#### Step 2: Define Block Structure

```cpp
blocks
(
    // Main tube block
    hex (0 1 2 5 4 3 7 8) (50 200 1)  // Main tube: 50 radial × 200 axial × 1 span

    // Inlet extension (optional)
    hex (0 1 2 5 4 3 7 8) (10 50 1)   // Inlet: 10 radial × 50 axial
);
```

#### Step 3: Configure Boundary Layer Grading

```cpp
boundary
{
    inlet
    {
        type patch;
        faces
        (
            (0 1 2 3 4 5)  // Inlet face
        );
    }

    outlet
    {
        type patch;
        faces
        (
            (6 7 8 9 10 11)  // Outlet face
        );
    }

    wall
    {
        type wall;
        faces
        (
            (0 3 6 9)      // Inlet wall
            (5 8 11 2)     // Outlet wall
            (0 6 7 1)      // Bottom wall
            (3 5 4 9)      // Top wall
        );
    }

    empty
    {
        type empty;
        faces
        (
            (0 1 4 3)      // Inlet cross-section
            (1 2 5 4)      // Mid cross-section
            (2 8 11 5)     // Outlet cross-section
            (6 7 8 9)      // Bottom cross-section
            (9 10 11 3)    // Top cross-section
        );
    }
}
```

#### Step 4: Implement Edge Grading for Boundary Layer

```cpp
mergePatchPairs
(
);
```

## Complete blockMeshDict Template for R410A Tube

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
    // Bottom face vertices (z = 0)
    (0    -0.0025 -0.0025)  // 0: inlet bottom-left
    (0.5  -0.0025 -0.0025)  // 1: mid bottom-left
    (1.0  -0.0025 -0.0025)  // 2: outlet bottom-left

    // Top face vertices (z = 0.0025)
    (0     0.0025 -0.0025)  // 3: inlet top-left
    (0.5    0.0025 -0.0025)  // 4: mid top-left
    (1.0    0.0025 -0.0025)  // 5: outlet top-left

    // Bottom face vertices (z = 0.0025)
    (0    -0.0025  0.0025)  // 6: inlet bottom-right
    (0.5  -0.0025  0.0025)  // 7: mid bottom-right
    (1.0  -0.0025  0.0025)  // 8: outlet bottom-right

    // Top face vertices (z = -0.0025)
    (0     0.0025  0.0025)  // 9: inlet top-right
    (0.5    0.0025  0.0025)  // 10: mid top-right
    (1.0    0.0025  0.0025)  // 11: outlet top-right
);

blocks
(
    // Main tube block
    hex (0 1 2 5 4 3 7 8) (50 200 1)

    // Inlet extension for fully developed flow
    hex (0 1 2 5 4 3 7 8) (10 50 1)
);

boundary
{
    inlet
    {
        type patch;
        faces
        (
            (0 1 2 3 4 5)  // Inlet face
        );
    }

    outlet
    {
        type patch;
        faces
        (
            (6 7 8 9 10 11)  // Outlet face
        );
    }

    wall
    {
        type wall;
        faces
        (
            (0 3 6 9)      // Inlet wall
            (5 8 11 2)     // Outlet wall
            (0 6 7 1)      // Bottom wall
            (3 5 4 9)      // Top wall
        );
    }

    empty
    {
        type empty;
        faces
        (
            (0 1 4 3)      // Inlet cross-section
            (1 2 5 4)      // Mid cross-section
            (2 8 11 5)     // Outlet cross-section
            (6 7 8 9)      // Bottom cross-section
            (9 10 11 3)    // Top cross-section
        );
    }
}

mergePatchPairs
(
);
```

## R410A-Specific Meshing Considerations

### ⭐ Boundary Layer Requirements for R410A

#### Liquid Phase (α = 1.0)
- **First cell height**: 5 μm (for y+ < 1)
- **Growth ratio**: 1.25
- **Total layers**: 20
- **Boundary layer thickness**: ~250 μm

#### Vapor Phase (α = 0.0)
- **First cell height**: 0.67 μm (for y+ < 1)
- **Growth ratio**: 1.25
- **Total layers**: 20
- **Boundary layer thickness**: ~50 μm

#### Two-Phase (α = 0.5)
Use conservative liquid-phase specifications:
- **First cell height**: 5 μm
- **Total boundary layer**: 250 μm

### Mesh Quality Validation

#### Check Commands
```bash
# Basic mesh quality check
checkMesh -allGeometry -allTopology

# Detailed quality report
checkMesh -all -time 1
```

#### Acceptable Metrics for R410A
| Metric | Value | Action Required |
|--------|-------|----------------|
| Non-orthogonality | < 70° | OK |
| Max skewness | < 4.0 | Monitor |
| Aspect ratio | < 5.0 | OK for R410A |
| Volume ratio | < 100 | Acceptable |
| Face concavity | No concave faces | Must fix |

### Performance Considerations

#### Computational Requirements
- **Base mesh**: 250K cells
- **Memory usage**: ~2 GB RAM
- **Time per iteration**: 5-10 seconds
- **Convergence**: 1000-2000 iterations

#### Optimization Tips
1. **Use inflation layers** instead of many radial cells
2. **Apply symmetry** for 2D axisymmetric cases
3. **Coarsen inlet/outlet regions** where gradients are small
4. **Monitor y+** during simulation and adjust if needed

### Common Issues and Solutions

#### Issue 1: High Aspect Ratio
**Problem**: Aspect ratio > 5 in tube
**Solution**: Increase radial cells to 60-80

#### Issue 2: Poor Orthogonality
**Problem**: Non-orthogonality > 70°
**Solution**: Add intermediate vertices in curved regions

#### Issue 3: Insufficient Resolution
**Problem**: Can't capture bubble dynamics
**Solution**: Implement local refinement near predicted interface

### Example: BlockMesh Execution

```bash
# Navigate to case directory
cd /path/to/r410a_tube_case

# Generate mesh
blockMesh

# Check mesh quality
checkMesh -all

# Convert for ParaView
paraFoam

# Optional: Decompose for parallel
decomposePar
```

### Next Steps

After mastering straight tube meshing, proceed to:

1. **Microchannel Strategies** - Learn compact heat exchanger meshing
2. **U-Bend Topology** - Handle complex geometries
3. **Dynamic Refinement** - Adapt to evolving interfaces

---

*Previous: [00_Overview.md](00_Overview.md) | Next: [02_Microchannel_Strategies.md](02_Microchannel_Strategies.md)*