# y+ Calculations for R410A Evaporator (การคำนวณ y+ สำหรับเครื่องระเหย R410A)

## Introduction to y+ in R410A Flows

The y+ parameter is crucial for ensuring proper resolution of the boundary layer in R410A evaporator simulations. This guide provides detailed calculations for y+ determination across different phases and flow conditions encountered in R410A systems.

### ⭐ Understanding y+ in Two-Phase Flow

y+ is the dimensionless distance from the wall, defined as:

$$
y^+ = \frac{y \cdot u_\tau}{\nu}
$$

where:
- $y$ = distance from wall (m)
- $u_\tau$ = friction velocity (m/s)
- $\nu$ = kinematic viscosity (m²/s)

For R410A, y+ requirements vary significantly between liquid and vapor phases due to different properties.

## Operating Conditions for R410A Evaporator

### ⭐ Standard Operating Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| Temperature | 10°C | Saturation temperature |
| Pressure | 1.0 MPa | Operating pressure |
| Mass flux | 200 kg/m²s | Typical value |
| Tube diameter | 5mm | Inner diameter |
| Heat flux | 10-20 kW/m² | Typical heat flux |

### Phase Properties at 10°C, 1.0 MPa

#### Liquid Phase (α = 1.0)
```
Density (ρ_l): 1200 kg/m³
Dynamic viscosity (μ_l): 1.2e-4 Pa·s
Kinematic viscosity (ν_l): 1.0e-7 m²/s
Thermal conductivity (k_l): 0.08 W/m·K
Specific heat (cp_l): 1400 J/kg·K
```

#### Vapor Phase (α = 0.0)
```
Density (ρ_v): 70 kg/m³
Dynamic viscosity (μ_v): 1.3e-5 Pa·s
Kinematic viscosity (ν_v): 1.86e-7 m²/s
Thermal conductivity (k_v): 0.014 W/m·K
Specific heat (cp_v): 1000 J/kg·K
```

## Detailed y+ Calculations

### ⭐ Liquid Phase Calculations (α = 1.0)

#### Step 1: Calculate Reynolds Number
$$
Re_l = \frac{G \cdot D}{\mu_l} = \frac{200 \times 0.005}{1.2e-4} = 8333
$$

#### Step 2: Determine Flow Regime
$Re_l = 8333$ indicates **turbulent flow** (Re > 4000)

#### Step 3: Calculate Friction Factor (Blasius equation)
$$
f_l = 0.316 \times Re_l^{-0.25} = 0.316 \times 8333^{-0.25} = 0.033
$$

#### Step 4: Calculate Wall Shear Stress
$$
\tau_{w,l} = \frac{1}{2} \cdot f_l \cdot \rho_l \cdot U^2
$$

First, calculate velocity:
$$
U_l = \frac{G}{\rho_l} = \frac{200}{1200} = 0.167 \text{ m/s}
$$

Then wall shear stress:
$$
\tau_{w,l} = \frac{1}{2} \times 0.033 \times 1200 \times 0.167^2 = 0.55 \text{ Pa}
$$

#### Step 5: Calculate Friction Velocity
$$
u_{\tau,l} = \sqrt{\frac{\tau_{w,l}}{\rho_l}} = \sqrt{\frac{0.55}{1200}} = 0.021 \text{ m/s}
$$

#### Step 6: Calculate First Cell Height for y+ = 1
$$
y_{l,+=1} = \frac{y^+ \cdot \nu_l}{u_{\tau,l}} = \frac{1 \times 1.0e-7}{0.021} = 4.8 \times 10^{-6} \text{ m} = 4.8 \mu m
$$

### ⭐ Vapor Phase Calculations (α = 0.0)

#### Step 1: Calculate Reynolds Number
$$
Re_v = \frac{G \cdot D}{\mu_v} = \frac{200 \times 0.005}{1.3e-5} = 76,923
$$

#### Step 2: Determine Flow Regime
$Re_v = 76,923$ indicates **highly turbulent flow**

#### Step 3: Calculate Friction Factor
$$
f_v = 0.316 \times Re_v^{-0.25} = 0.316 \times 76923^{-0.25} = 0.019
$$

#### Step 4: Calculate Wall Shear Stress
$$
U_v = \frac{G}{\rho_v} = \frac{200}{70} = 2.86 \text{ m/s}
$$

$$
\tau_{w,v} = \frac{1}{2} \times 0.019 \times 70 \times 2.86^2 = 5.4 \text{ Pa}
$$

#### Step 5: Calculate Friction Velocity
$$
u_{\tau,v} = \sqrt{\frac{\tau_{w,v}}{\rho_v}} = \sqrt{\frac{5.4}{70}} = 0.278 \text{ m/s}
$$

#### Step 6: Calculate First Cell Height for y+ = 1
$$
y_{v,+=1} = \frac{1 \times 1.86e-7}{0.278} = 6.7 \times 10^{-7} \text{ m} = 0.67 \mu m
$$

### ⭐ Two-Phase Calculations (α = 0.5)

For two-phase flow, use conservative liquid-phase specifications:

- **First cell height**: 5 μm (liquid phase requirement)
- **Boundary layer thickness**: 250 μm
- **Growth ratio**: 1.25
- **Total layers**: 20

This ensures adequate resolution for both phases during the transition.

## Boundary Layer Grading Calculations

### ⭐ Growth Ratio Calculation

Given:
- First cell height: $y_0 = 5 \mu m$
- Last cell height: $y_N = 250 \mu m$
- Number of layers: $N = 20$

For exponential growth:
$$
y_i = y_0 \times r^i
$$

Where $r$ is the growth ratio:
$$
r = \left(\frac{y_N}{y_0}\right)^{\frac{1}{N}} = \left(\frac{250}{5}\right)^{\frac{1}{20}} = 1.25
$$

### Layer-by-Layer Cell Heights

| Layer Number | Height (μm) | Cumulative (μm) | y+ (liquid) |
|--------------|-------------|-----------------|-------------|
| 0 | 5.0 | 5.0 | 1.0 |
| 1 | 6.25 | 11.25 | 1.25 |
| 2 | 7.81 | 19.06 | 1.56 |
| 3 | 9.77 | 28.83 | 1.95 |
| 4 | 12.21 | 41.04 | 2.44 |
| 5 | 15.26 | 56.30 | 3.05 |
| 6 | 19.08 | 75.38 | 3.81 |
| 7 | 23.85 | 99.23 | 4.76 |
| 8 | 29.81 | 129.04 | 5.96 |
| 9 | 37.26 | 166.30 | 7.45 |
| 10 | 46.58 | 212.88 | 9.32 |
| 11 | 58.22 | 271.10 | 11.64 |
| 12 | 72.78 | 343.88 | 14.56 |
| 13 | 90.97 | 434.85 | 18.19 |
| 14 | 113.71 | 548.56 | 22.74 |
| 15 | 142.14 | 690.70 | 28.43 |
| 16 | 177.68 | 868.38 | 35.54 |
| 17 | 222.10 | 1090.48 | 44.42 |
| 18 | 277.63 | 1368.11 | 55.52 |
| 19 | 347.04 | 1715.15 | 69.41 |

## y+ Guidelines for R410A Simulations

### ⭐ Recommended y+ Values

| Application | y+ Range | Meshing Approach |
|-------------|----------|-----------------|
| Wall functions | 30-300 | Coarse mesh |
| Transitional | 1-5 | Medium refinement |
| Low-Re k-ε | 0.1-1 | Fine mesh |
| DNS | < 0.1 | Very fine mesh |

### R410A-Specific Recommendations

#### For Evaporating Flow
- **Inlet region (liquid)**: y+ < 1 (low-Re treatment)
- **Mid region (two-phase)**: y+ < 1 (interface tracking)
- **Outlet region (vapor)**: y+ < 1 (low-Re treatment)

#### For Condensing Flow
- **Wall temperature gradients**: y+ < 1 (heat transfer)
- **Film condensation**: y+ < 0.5 (thin film resolution)

## Practical Implementation

### ⭐ blockMeshDict Configuration

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
    // Tube cross-section vertices
    (0, -0.0025, 0)        // 0
    (0.01, -0.0025, 0)     // 1
    (0.02, -0.0025, 0)     // 2
    (0.03, -0.0025, 0)     // 3
    (0.04, -0.0025, 0)     // 4
    (0.05, -0.0025, 0)     // 5
    (0, 0.0025, 0)         // 6
    (0.01, 0.0025, 0)      // 7
    (0.02, 0.0025, 0)      // 8
    (0.03, 0.0025, 0)      // 9
    (0.04, 0.0025, 0)      // 10
    (0.05, 0.0025, 0)      // 11
);

blocks
(
    hex (0 1 2 3 4 5 6 7 8 9 10 11) (50 200 1)  // 50 radial × 200 axial
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
            (0 6 1 7 2 8 3 9 4 10 5 11)  // Wall faces
        );

        // R410A-specific boundary layer
        boundaryLayer
        {
            nLayers        20;
            expansionRatio  1.25;
            firstCellThickness 5e-6;      // 5 μm for y+ < 1
            minThickness    0.00025;     // 250 μm total
        }
    }

    empty
    {
        type empty;
        faces
        (
            (0 1 7 6)      // Cross-section 1
            (1 2 8 7)      // Cross-section 2
            (2 3 9 8)      // Cross-section 3
            (3 4 10 9)     // Cross-section 4
            (4 5 11 10)    // Cross-section 5
        );
    }
}

mergePatchPairs
(
);
```

### ⭐ Post-Processing Validation

After mesh generation, verify y+ values:

```bash
# Run potentialFoam to get velocity field
potentialFoam

# Calculate y+ using utility
yPlus -latestTime > yPlus_report.txt

# View y+ distribution
paraFoam
```

### y+ Report Analysis

```bash
# Extract y+ statistics from report
grep -E "max|min|average" yPlus_report.txt

# Check if y+ < 1 for all wall faces
awk '/max/ {print $2}' yPlus_report.txt | awk '$1 < 1 {print "OK"}'
```

## Dynamic y+ Considerations

### ⭐ Phase Change Effects

During evaporation, the boundary layer properties change:

1. **Initial liquid phase**: y+ ≈ 1 (liquid properties)
2. **Boiling region**: Mixed properties, use conservative estimate
3. **Final vapor phase**: y+ ≈ 0.67 (vapor properties)

### Adaptive Mesh Refinement

For evolving two-phase interfaces:

```cpp
dynamicRefineFvMesh
{
    refine
    {
        mode    manual;
        cellBased yes;
    }

    criteria
    {
        yPlus
        {
            type    yPlus;
            value   1.0;  // Refine if y+ > 1
        }
    }
}
```

## Troubleshooting Common y+ Issues

### ⭐ Issue 1: y+ Too High

**Problem**: y+ > 1 but need low-Re treatment
**Solution**:
1. Reduce first cell height: 5 μm → 2 μm
2. Increase growth ratio: 1.25 → 1.3
3. Add more boundary layers: 20 → 30

### ⭐ Issue 2: Too Many Cells

**Problem**: y+ < 1 but excessive cell count
**Solution**:
1. Use wall functions (y+ = 30-300)
2. Coarsen interior cells
3. Use anisotropic meshing

### ⭐ Issue 3: Interface Resolution

**Problem**: Can't capture two-phase interface
**Solution**:
1. Implement local refinement near interface
2. Use finer mesh in transition regions
3. Consider adaptive mesh refinement

## Performance Metrics

### ⭐ Computational Requirements

| y+ Range | Cells Required | Memory (GB) | Time/iter (s) |
|---------|--------------|-------------|---------------|
| y+ < 0.1 | 1,000,000+ | 4-8 | 30-60 |
| y+ < 1 | 500,000 | 2-4 | 15-30 |
| y+ < 5 | 200,000 | 1-2 | 5-10 |
| y+ < 30 | 50,000 | 0.5-1 | 2-5 |

### Optimal Choice for R410A

For most R410A evaporator simulations:
- **Recommended y+**: 0.5-1.0
- **Cell count**: 200K-500K
- **Balance**: Accuracy vs. computational cost

---

*Previous: [02_Microchannel_Strategies.md](02_Microchannel_Strategies.md) | Next: [04_Boundary_Layer_Grading.md](04_Boundary_Layer_Grading.md)*