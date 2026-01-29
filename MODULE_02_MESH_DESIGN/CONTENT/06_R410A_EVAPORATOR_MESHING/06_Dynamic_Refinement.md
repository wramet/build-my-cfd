# Dynamic Refinement for R410A Interface (การ Refinement แบบ Dynamic สำหรับอินเตอร์เฟส R410A)

## Introduction to Dynamic Mesh Refinement

Dynamic mesh refinement is essential for accurately capturing the evolving liquid-vapor interface in R410A evaporator simulations. This technique adapts the mesh resolution based on local flow conditions, ensuring optimal computational efficiency while maintaining accuracy.

### ⭐ Why Dynamic Refinement for R410A?

**1. Evolving Interface**
- Interface location changes during evaporation
- Bubble formation and growth
- Film condensation dynamics

**2. Localized Phenomena**
- High gradients near the interface
- Heat transfer hotspots
- Critical flow regions

**3. Computational Efficiency**
- Refine only where needed
- Coarse mesh in developed regions
- Adaptive resource allocation

## Dynamic Refinement Fundamentals

### ⭐ Mesh Refinement Strategies

| Strategy | Trigger | Application | R410A Relevance |
|----------|---------|-------------|-----------------|
| Distance-based | Interface proximity | Two-phase regions | High |
| Gradient-based | Property gradients | Heat transfer | Medium |
| Feature-based | Flow features | Vortices, shocks | Low |
| Error-based | Solution error | General | Medium |

### R410A-Specific Refinement Requirements

```
Interface Resolution:
- Base mesh: 50-100 cells
- Refinement level 1: 25-50 cells
- Refinement level 2: 12-25 cells
- Total: 3,000-50,000 cells (3D)

Refinement Criteria:
- Distance to interface: < 1mm
- Temperature gradient: > 10 K/m
- Velocity gradient: > 1 m/s/m
- Void fraction gradient: > 0.1/m
```

## DynamicRefineFvMesh Configuration

### ⭐ Basic Configuration for R410A

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
    object      dynamicMeshDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dynamicFvMesh       dynamicRefineFvMesh;

// Refinement regions definition
refinementRegions
{
    // Interface refinement for two-phase flow
    interface
    {
        mode            distance;
        levels          ((0.001 2)(0.0005 3));

        // Distance thresholds for R410A
        distance        0.001;     // 1mm from interface
        maxLevel        3;         // Maximum refinement level
    }

    // Bend region refinement for secondary flows
    bendRegion
    {
        mode            inside;
        levels          ((0 1));
        cell            (
            (0.0275 -0.0025 -0.0025)
            (0.05 -0.0025 0.0025)
            (0.0275 0.0025 0.0025)
            (-0.0275 0.0025 -0.0025)
            (-0.0275 -0.0025 -0.0025)
            (0.0275 -0.0025 0.0025)
        );
    }

    // Heat transfer enhancement zone
    heatTransferRegion
    {
        mode            distance;
        levels          ((0.002 1)(0.001 2));
        distance        0.002;     // 2mm from wall
    }
}

// Refinement boxes for critical areas
refinementBoxes
{
    // Inlet region for flow development
    inletBox
    {
        box (0 -0.01 -0.01) (0.1 0.01 0.01);
        level 2;
    }

    // Evaporation zone
    evaporationZone
    {
        box (0.4 -0.003 -0.003) (0.6 0.003 0.003);
        level 1;
    }

    // Outlet region for stability
    outletBox
    {
        box (0.8 -0.01 -0.01) (1.0 0.01 0.01);
        level 1;
    }
}

// Mesh movement parameters
motionSolver      staticFvMesh;

// Refinement controls
refinement
{
    // Automatic refinement based on criteria
    automatic        true;

    // Refinement criteria
    criteria
    {
        // Interface tracking for R410A
        alphaLiquid
        {
            mode            field;
            field          alpha1;
            tolerance      0.1;        // 10% change
            absolute        true;
            level          2;
        }

        // Heat transfer refinement
        temperature
        {
            mode            gradient;
            field          T;
            tolerance      5.0;        // 5K gradient
            absolute        true;
            level          1;
        }

        // Velocity refinement for vortices
        velocity
        {
            mode            gradient;
            field          U;
            tolerance      2.0;        // 2 m/s/m gradient
            absolute        true;
            level          1;
        }
    }

    // Unrefinement controls
    unrefine
    {
        mode            automatic;
        criteria
        {
            alphaLiquid
            {
                mode            field;
                field          alpha1;
                tolerance      0.05;       // 5% change
                absolute        true;
            }
        }

        // Delay unrefinement to prevent oscillations
        delay           5;           // 5 timesteps

        // Minimum cells before unrefinement
        minCells       10000;
    }
}

// Merge patch settings
mergePatchPairs
(
);

// Additional R410A-specific parameters
r410aRefinement
{
    // Operating conditions
    massFlux        200;        // kg/m²s
    temperature     283;        // K
    pressure        1e6;        // Pa

    // Two-phase parameters
    surfaceTension  0.008;      // N/m for R410A
    contactAngle    30;         // degrees

    // Refinement optimization
    interfaceCells   3;          // Cells across interface
    maxRefinement   4;          // Maximum refinement level
    adaptiveStep    true;       // Adaptive time stepping
}
```

### ⭐ snappyHexMesh Integration

For more complex geometries, combine dynamic refinement with snappyHexMesh:

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
    object      dynamicMeshDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dynamicFvMesh       dynamicRefineFvMesh;

// Base mesh from snappyHexMesh
baseMesh           snappyHexMeshDict;

// Refinement regions
refinementRegions
{
    // Interface refinement for R410A
    twoPhaseInterface
    {
        mode            distance;
        levels          ((0.0005 3)(0.0002 4));
        distance        0.0005;     // 0.5mm from interface

        // R410A-specific thresholds
        maxLevel        4;
        minLevel        1;
    }

    // Microchannel refinement
    microchannel
    {
        mode            box;
        levels          ((0 1)(0.0005 2));
        box (0 0 0) (0.02 0.002 0.001);
    }
}

// Refinement controls
refinement
{
    automatic        true;

    criteria
    {
        // Interface detection
        voidFraction
        {
            mode            field;
            field          alpha;
            tolerance      0.1;
            absolute        true;
            level          3;
        }

        // Pressure gradient
        pressure
        {
            mode            gradient;
            field          p;
            tolerance      1000;       // Pa/m
            absolute        true;
            level          2;
        }
    }
}

// Mesh movement
motionSolver       solidBodyMotionFvMesh;

// Motion settings
solidBodyMotionFvMeshCoeffs
{
    // Static mesh for R410A
    type            staticFvMesh;
}
```

## Advanced Refinement Strategies

### ⭐ Multi-Level Refinement for R410A

```cpp
// Dynamic refinement with multiple levels
refinementRegions
{
    // Primary interface (highest priority)
    primaryInterface
    {
        mode            distance;
        levels          ((0.001 2)(0.0005 4));
        distance        0.001;     // 1mm from primary interface
        priority        1;         // Highest priority
    }

    // Secondary phenomena (bubbles, droplets)
    secondaryInterface
    {
        mode            distance;
        levels          ((0.0005 3)(0.0002 4));
        distance        0.0005;    // 0.5mm from secondary interface
        priority        2;         // Secondary priority
    }

    // Heat transfer regions
    heatTransfer
    {
        mode            gradient;
        levels          ((0.002 1)(0.001 2));
        field          T;
        gradient       5.0;       // 5K/m
        priority        3;         // Lower priority
    }
}

// Refined mesh parameters
meshRefinement
{
    // Cell size constraints
    minCellSize     1e-6;       // 1 μm minimum
    maxCellSize     1e-3;       // 1 mm maximum

    // Quality constraints
    maxSkewness     4.0;
    maxNonOrtho     70;

    // Balance between refinement and quality
    qualityPriority high;
}
```

### ⭐ Adaptive Refinement Based on Flow Features

```cpp
// Feature-based refinement
featureRefinement
{
    // Dean vortices in U-bend
    deanVortex
    {
        mode            vorticity;
        field          U;
        levels          ((0.01 1)(0.005 2));
        vorticity      50;         // 1/s threshold
        region         bend;
    }

    // Bubble tracking
    bubbleTracking
    {
        mode            feature;
        field          alpha;
        levels          ((0.1 2)(0.05 3));
        threshold      0.8;       // High void fraction
        detectBubbles   true;
    }

    // Wave tracking for annular flow
    waveTracking
    {
        mode            gradient;
        field          U;
        levels          ((0.1 1)(0.05 2));
        gradient       5.0;       // m/s/m threshold
        wavelength     0.01;      // 10mm wavelength
    }
}
```

## Performance Analysis

### ⭐ Computational Requirements

| Refinement Level | Cells Added | Memory (MB) | Time/iter (s) | Accuracy Impact |
|------------------|-------------|-------------|---------------|-----------------|
| Base mesh | 50,000 | 400 | 5-10 | 70% |
| Level 1 | 100,000 | 800 | 10-20 | 85% |
| Level 2 | 200,000 | 1,600 | 20-40 | 95% |
| Level 3 | 400,000 | 3,200 | 40-80 | 98% |

### R410A-Specific Performance Considerations

```cpp
// Performance optimization for R410A
performanceOptimization
{
    // Adaptive time stepping
    adaptiveTimeStep
    {
        enabled        true;
        maxCo          1.0;
        minCo          0.1;
        refinementImpact  true;   // Adjust time step based on refinement
    }

    // Load balancing
    loadBalancing
    {
        enabled        true;
        method         dynamic;
        targetBalance  0.9;       // 90% balance efficiency
    }

    // Memory management
    memoryManagement
    {
        maxMemory      8e9;       // 8GB RAM limit
        compression    true;
        cacheSize      1e9;       // 1GB cache
    }
}
```

## Implementation Workflow

### ⭐ Step-by-Step Implementation

```bash
# 1. Setup initial mesh
blockMesh

# 2. Check initial quality
checkMesh -all

# 3. Create dynamicMeshDict
cp /path/to/templates/dynamicMeshDict system/

# 4. Run with dynamic refinement
# Modify controlDict to enable dynamic refinement
sed -i 's/dynamicMesh false;/dynamicMesh true;/' system/controlDict
sed -i 's/writeFormat ascii;/writeFormat binary;/' system/controlDict

# 5. Run simulation
twoPhaseEulerFoam > dynamic_refinement_log.txt

# 6. Monitor refinement
watch -n 5 "foamListTimes -latest | tail -1"

# 7. Check refinement statistics
postProcess -func "refinementInfo" -latest
```

### ⭐ Refinement Monitoring and Control

```python
#!/usr/bin/env python3
# R410A dynamic refinement monitor
import subprocess
import time
import json

def monitor_refinement():
    while True:
        # Get current time
        result = subprocess.run(['foamListTimes', '-latest'],
                              capture_output=True, text=True)
        latest_time = result.stdout.strip().split('\n')[-1]

        # Check refinement stats
        result = subprocess.run(['postProcess', '-func', 'refinementInfo',
                              '-time', latest_time],
                              capture_output=True, text=True)

        # Extract and report statistics
        print(f"Time: {latest_time}, Refinement active")
        time.sleep(10)

# Run monitoring
if __name__ == "__main__":
    monitor_refinement()
```

## Validation and Quality Control

### ⭐ Refinement Validation Metrics

| Metric | Target Value | R410A Relevance |
|--------|--------------|-----------------|
| Interface cells | ≥ 3 | Critical for accuracy |
| Conservation error | < 1% | Mass conservation |
| Skewness in refined regions | < 3.0 | Numerical stability |
| Computational overhead | < 4x | Performance |

### Validation Commands

```bash
# Check mesh statistics
checkMesh -all -time latest

# Check conservation
postProcess -func "massFlowInlet massFlowOutlet" -time latest

# Visualize interface
paraFoam &
```

## Common Issues and Solutions

### ⭐ Issue 1: Excessive Refinement

**Problem**: Too many cells affecting performance
**Solution**:
```cpp
refinement
{
    automatic        true;
    maxLevel        3;         // Limit refinement level
    maxCells        500000;    // Cell count limit
    qualityControl  true;
}
```

### ⭐ Issue 2: Interface Oscillations

**Problem**: Interface jumping between refinement levels
**Solution**:
```cpp
unrefine
{
    mode            manual;
    criteria
    {
        alphaLiquid
        {
            tolerance      0.02;      // Stricter threshold
            absolute        true;
        }
    }
    delay           10;        // Longer delay
}
```

### ⭐ Issue 3: Memory Overflow

**Problem**: Memory exceeded during refinement
**Solution**:
```cpp
memoryManagement
{
    maxMemory      8e9;       // Reduce limit
    compression    true;
    maxCellSize    5e-4;      // Increase minimum size
}
```

## R410A-Specific Applications

### ⭐ Evaporator Simulation with Dynamic Refinement

```cpp
// R410A evaporator refinement setup
refinementRegions
{
    // Evaporation zone refinement
    evaporationZone
    {
        mode            distance;
        levels          ((0.002 1)(0.001 2));
        distance        0.002;     // 2mm from wall
        heatTransfer    true;
    }

    // Superheated vapor zone
    superheatedZone
    {
        mode            field;
        levels          ((0 1));
        field          T;
        threshold      300;       // K (above saturation)
    }

    // Liquid film region
    liquidFilm
    {
        mode            distance;
        levels          ((0.0005 3)(0.0002 4));
        distance        0.0005;    // 0.5mm from wall
        liquidOnly     true;
    }
}
```

### ⭐ Microchannel Array with Dynamic Refinement

```cpp
// Microchannel dynamic refinement
refinementRegions
{
    // Individual channel refinement
    channelRefinement
    {
        mode            box;
        levels          ((0 1)(0.0005 2));
        box (0 0 0) (0.02 0.001 0.001);
        perChannel      true;      // Apply to all channels
    }

    // Interface in microchannels
    microInterface
    {
        mode            distance;
        levels          ((0.0002 4)(0.0001 5));
        distance        0.0002;    // 0.2mm from interface
        maxLevel        5;
    }
}
```

## Performance Optimization Tips

### ⭐ Computational Efficiency

1. **Selective Refinement**: Refine only critical regions
2. **Adaptive Time Stepping**: Adjust time step based on refinement
3. **Load Balancing**: Distribute refined cells evenly
4. **Memory Management**: Monitor and limit memory usage

### ⭐ Best Practices for R410A

```cpp
// Optimal configuration for R410A
r410aOptimization
{
    // Interface tracking
    interface
    {
        resolution      0.001;     // 1mm resolution
        maxLevel        3;
        cellRatio       2;          // 2x refinement per level
    }

    // Quality control
    quality
    {
        maxSkewness     3.0;
        maxNonOrtho     60;
        aspectRatio     10;
    }

    // Performance targets
    performance
    {
        maxOverhead     3.0;       // 3x computational overhead
        targetCells     300000;    // Target cell count
        adaptive        true;      // Adaptive refinement
    }
}
```

---

*Previous: [05_U_Bend_Topology.md](05_U_Bend_Topology.md) | Next: [07_Quality_Criteria.md](07_Quality_Criteria.md)*