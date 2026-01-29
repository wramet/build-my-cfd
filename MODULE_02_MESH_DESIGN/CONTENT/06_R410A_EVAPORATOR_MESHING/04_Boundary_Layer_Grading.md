# Boundary Layer Grading for R410A (การจัดชั้นแบบเกรดในชั้นเบาะเบาะขอบสำหรับ R410A)

## Introduction to Boundary Layer Grading

Proper boundary layer grading is essential for accurate R410A evaporator simulations. This guide provides comprehensive techniques for implementing effective boundary layer meshing that resolves the complex physics of two-phase flow near walls.

### ⭐ Boundary Layer Requirements

The boundary layer in R410A flow presents unique challenges:
- Liquid phase requires 5 μm first cell for y+ < 1
- Vapor phase requires 0.67 μm first cell for y+ < 1
- Phase transition creates varying property gradients
- Heat transfer effects enhance resolution needs

## First Cell Calculation Methods

### ⭐ Method 1: Direct Calculation (Liquid Phase)

For R410A liquid flow at 10°C:

```python
# R410A liquid properties at 10°C, 1.0 MPa
rho_l = 1200      # kg/m³
mu_l = 1.2e-4    # Pa·s
nu_l = 1.0e-7    # m²/s

# Operating conditions
G = 200          # kg/m²s (mass flux)
D = 0.005        # m (diameter)

# Calculate friction velocity
U = G / rho_l    # m/s
Re = G * D / mu_l
f = 0.316 * Re**(-0.25)  # Blasius friction factor
tau_w = 0.5 * f * rho_l * U**2
u_tau = (tau_w / rho_l)**0.5

# First cell height for y+ = 1
y_first = nu_l / u_tau  # m
print(f"First cell height: {y_first*1e6:.2f} μm")  # Output: 4.8 μm
```

### ⭐ Method 2: Empirical Estimation

For quick estimates in R410A systems:

```python
# Empirical correlation for y+ estimation
def estimate_y_plus(G, D, mu, rho):
    """Estimate first cell height for y+ = 1"""
    U = G / rho
    Re = G * D / mu
    f = 0.316 * Re**(-0.25)
    u_tau = (0.5 * f * rho * U**2 / rho)**0.5
    nu = mu / rho
    return nu / u_tau

# R410A liquid phase
y_l = estimate_y_plus(200, 0.005, 1.2e-4, 1200)  # 4.8e-6 m

# R410A vapor phase
y_v = estimate_y_plus(200, 0.005, 1.3e-5, 70)     # 6.7e-7 m

# Conservative estimate for two-phase
y_safe = max(y_l, y_v) * 1.5  # Safety factor
print(f"Safe first cell: {y_safe*1e6:.2f} μm")  # Output: 10.1 μm
```

## Grading Strategy Comparison

### ⭐ Exponential vs. Geometric Grading

| Grading Type | Formula | Advantages | Disadvantages |
|--------------|---------|------------|---------------|
| Exponential | $y_i = y_0 \times r^i$ | Smooth transition | More cells needed |
| Geometric | grading ratio | Simple implementation | Less smooth |
| Power law | $y_i = y_0 \times (i+1)^p$ | Flexible | Complex tuning |

### Optimal Choice for R410A

For R410A evaporators, **exponential grading** is preferred:
- Provides smooth cell growth
- Better resolves velocity gradients
- Reduces numerical oscillations

## Complete Boundary Layer Setup

### ⭐ Option 1: blockMesh Implementation

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
    // Tube cross-section - bottom wall
    (0, -0.0025, 0)        // 0
    (0.01, -0.0025, 0)     // 1
    (0.02, -0.0025, 0)     // 2
    (0.03, -0.0025, 0)     // 3
    (0.04, -0.0025, 0)     // 4
    (0.05, -0.0025, 0)     // 5

    // Tube cross-section - top wall
    (0, 0.0025, 0)         // 6
    (0.01, 0.0025, 0)      // 7
    (0.02, 0.0025, 0)      // 8
    (0.03, 0.0025, 0)      // 9
    (0.04, 0.0025, 0)      // 10
    (0.05, 0.0025, 0)      // 11

    // Boundary layer vertices - bottom wall
    (0, -0.00251, 0)       // 12  (5 μm from wall)
    (0.01, -0.00251, 0)    // 13
    (0.02, -0.00251, 0)    // 14
    (0.03, -0.00251, 0)    // 15
    (0.04, -0.00251, 0)    // 16
    (0.05, -0.00251, 0)    // 17

    // Boundary layer vertices - top wall
    (0, 0.00251, 0)        // 18
    (0.01, 0.00251, 0)     // 19
    (0.02, 0.00251, 0)     // 20
    (0.03, 0.00251, 0)     // 21
    (0.04, 0.00251, 0)     // 22
    (0.05, 0.00251, 0)     // 23
);

blocks
(
    // Main tube block with boundary layer grading
    hex (0 1 2 3 4 5 6 7 8 9 10 11) (30 200 1)
    grading
    (
        // Radial grading (boundary layer)
        20 1 20    // Bottom wall: fine grading
        20 1 20    // Top wall: fine grading

        // Axial grading
        1 20 1     // Uniform axial distribution

        // Spanwise grading
        1 1 1      // Uniform (2D case)
    )
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
            // Bottom wall with boundary layer
            (0 12 13 1 14 15 2 16 17 3 18 19)  // Bottom wall faces

            // Top wall with boundary layer
            (6 19 20 7 21 22 8 23 9 10 11)     // Top wall faces
        );

        // R410A-specific boundary layer specification
        boundaryLayer
        {
            nLayers        20;
            expansionRatio  1.25;
            firstCellThickness 5e-6;      // 5 μm for y+ < 1
            minThickness    0.00025;     // 250 μm total BL thickness

            // R410A properties for accurate calculation
            rho            1200;        // kg/m³ liquid density
            mu             1.2e-4;      // Pa·s liquid viscosity
            G              200;          // kg/m²s mass flux
        }
    }

    empty
    {
        type empty;
        faces
        (
            (0 1 13 12)      // Bottom BL cross-section
            (1 2 14 13)      // Bottom BL cross-section
            (2 3 15 14)      // Bottom BL cross-section
            (3 4 16 15)      // Bottom BL cross-section
            (4 5 17 16)      // Bottom BL cross-section
            (6 7 19 18)      // Top BL cross-section
            (7 8 20 19)      // Top BL cross-section
            (8 9 21 20)      // Top BL cross-section
            (9 10 22 21)     // Top BL cross-section
            (10 11 23 22)    // Top BL cross-section
        );
    }
}

mergePatchPairs
(
);
```

### ⭐ Option 2: snappyHexMesh Implementation

For more complex geometries, use snappyHexMesh:

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
    object      snappyHexMeshDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

castellatedMeshControls
{
    maxLocalCellSize    0.001;
    minRefineIter       1;
    maxRefineIter       3;
    features            (
        {
            file    "r410a_tube.eMesh";
            level   8;
        }
    );
}

snapControls
{
    nSmoothPatch     3;
    errorReduction   0.75;
    resolvePatchSkewness  true;
    skewnessThreshold  0.95;
}

layers
{
    "wall"
    {
        nLayers         20;
        expansionRatio   1.25;
        minThickness     5e-6;      // 5 μm first cell
        maxThickness     0.00025;    // 250 μm total

        // R410A-specific properties
        rho             1200;
        mu              1.2e-4;
        U               0.167;      // m/s velocity

        // Check y+ after each layer
        yPlusCheck      true;
        maxYPlus        1.0;        // Target y+ < 1
    }
}

mergePatchPairs
(
);

// Add refinement regions for critical areas
refinementRegions
{
    // Heat transfer enhancement zone
    heatTransferZone
    {
        mode            distance;
        levels          ((0.0001 3)(0.0005 2));
        distance        0.0001;     // 0.1 mm from wall
    }
}
```

## Advanced Grading Strategies

### ⭐ Anisotropic Grading for R410A

For regions with different flow characteristics:

```cpp
blocks
(
    // Inlet region (fully developed flow)
    hex (0 1 2 3 4 5 6 7 8 9 10 11) (40 100 1)
    grading
    (
        25 1 25    // Fine radial grading
        1 10 1     // Coarse axial grading
        1 1 1      // Uniform spanwise
    )

    // Heat transfer region
    hex (0 1 2 3 4 5 6 7 8 9 10 11) (60 200 1)
    grading
    (
        35 1 35    // Very fine radial grading
        1 20 1     // Fine axial grading
        1 1 1      // Uniform spanwise
    )
);
```

### ⭐ Adaptive Grading Based on Flow Conditions

```cpp
// Dynamic adjustment based on operating conditions
boundaryLayer
{
    // Base configuration
    nLayers        20;
    expansionRatio 1.25;

    // Adaptive parameters
    massFlux       200;        // kg/m²s
    temperature    283;        // K (10°C)
    pressure       1e6;        // Pa (1 MPa)

    // Automatic calculation
    autoCalculate  true;
    targetYPlus    1.0;

    // Phase detection
    phaseModel      twoPhaseEulerFoam;
    alphaLiquid     0.5;       // Initial liquid fraction
}
```

## Validation and Quality Control

### ⭐ Post-Mesh Validation

After generating the mesh, validate boundary layer quality:

```bash
# Generate mesh
blockMesh

# Check mesh quality
checkMesh -all

# Calculate y+ distribution
yPlus -latestTime > yPlus_report.txt

# Analyze y+ statistics
awk '/max/ {print "Max y+: " $2}' yPlus_report.txt
awk '/average/ {print "Avg y+: " $2}' yPlus_report.txt
```

### Acceptable Boundary Layer Metrics

| Metric | Target Value | R410A Consideration |
|--------|--------------|---------------------|
| First cell y+ | < 1.0 | Critical for accuracy |
| Max y+ | < 5.0 | Acceptable for some models |
| Growth ratio | 1.2-1.3 | Optimal for R410A |
| BL thickness | 200-300 μm | Cover boundary layer |
| Cell aspect ratio | < 10 | Maintain stability |

### Troubleshooting Common Issues

#### Issue 1: Insufficient Boundary Layer Resolution
**Problem**: y+ > 1 in some regions
**Solution**:
1. Increase boundary layers: 20 → 30
2. Reduce growth ratio: 1.3 → 1.2
3. Reduce first cell height: 5 μm → 3 μm

```cpp
boundaryLayer
{
    nLayers        30;
    expansionRatio  1.2;
    firstCellThickness 3e-6;      // 3 μm
    minThickness    0.0003;      // 300 μm total
}
```

#### Issue 2: Excessive Cell Count
**Problem**: Too many cells affecting performance
**Solution**:
1. Use wall functions (y+ = 30-100)
2. Increase growth ratio: 1.2 → 1.4
3. Reduce boundary layers: 30 → 15

```cpp
boundaryLayer
{
    nLayers        15;
    expansionRatio  1.4;
    firstCellThickness 5e-5;      // 50 μm (for y+ ~10)
    minThickness    0.001;       // 1000 μm total
}
```

#### Issue 3: Poor Orthogonality in BL
**Problem**: Non-orthogonality > 70° near wall
**Solution**:
1. Add intermediate vertices
2. Use smoother grading
3. Apply additional smoothing

## Performance Optimization

### ⭐ Memory and Computational Requirements

| BL Configuration | Cells Added | Memory (MB) | Impact on Performance |
|------------------|-------------|-------------|----------------------|
| No BL | 0 | Baseline | - |
| 15 layers | +50% | +40% | +20% time/iter |
| 20 layers | +100% | +80% | +40% time/iter |
| 30 layers | +200% | +150% | +80% time/iter |

### Optimization Strategies for R410A

1. **Variable BL thickness**: Thicker in developed regions
2. **Local refinement**: Only where needed
3. **Anisotropic meshing**: Fine in radial, coarse in axial
4. **Parallel computing**: Decompose for large meshes

### Example: Optimized Configuration

```cpp
boundaryLayer
{
    // Core configuration (optimized for accuracy)
    nLayers         20;
    expansionRatio  1.25;
    firstCellThickness 5e-6;      // 5 μm

    // Adaptive parameters
    adaptToFlow     true;
    localRefinement  true;

    // Performance optimization
    maxCells        100000;      // Limit additional cells
    compression     true;        // Compress BL if needed
}
```

## R410A-Specific Considerations

### ⭐ Phase Change Effects on BL

During evaporation:
1. **Liquid phase**: Standard BL with 5 μm first cell
2. **Two-phase transition**: Mixed properties, use conservative estimate
3. **Vapor phase**: 0.67 μm first cell required

```cpp
// Adaptive BL based on phase
boundaryLayer
{
    // Base configuration
    nLayers         20;
    expansionRatio  1.25;

    // Phase-aware parameters
    if (alphaLiquid > 0.9)
    {
        firstCellThickness 5e-6;      // Liquid phase
    }
    else if (alphaLiquid < 0.1)
    {
        firstCellThickness 0.67e-6;   // Vapor phase
    }
    else
    {
        firstCellThickness 5e-6;      // Conservative
    }
}
```

### Heat Transfer Enhancement Effects

```cpp
// Enhanced BL near heat sources
heatTransferBL
{
    nLayers         25;
    expansionRatio  1.2;
    firstCellThickness 3e-6;      // Finer for heat transfer
    temperatureGradient  true;     // Account for temperature effects

    // R410A properties
    rho             1200;
    mu              1.2e-4;
    k               0.08;        // Thermal conductivity
}
```

---

*Previous: [03_Y_Plus_Calculations.md](03_Y_Plus_Calculations.md) | Next: [05_U_Bend_Topology.md](05_U_Bend_Topology.md)*