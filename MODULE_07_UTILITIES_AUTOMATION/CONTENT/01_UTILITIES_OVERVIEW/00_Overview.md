# Module 07: OpenFOAM Utilities & Workflow Automation

## 📋 Executive Summary

This module provides comprehensive training in OpenFOAM's extensive utilities ecosystem and workflow automation strategies, enabling efficient management of complete CFD workflows from geometry preparation to advanced post-processing and reporting.

**Core Focus**: Practical workflows, automation, and integration with OpenFOAM solvers for engineering applications.

---

## 🎯 Module Objectives

### Primary Goals

**Mastery of OpenFOAM Utilities**
- Control OpenFOAM utilities for mesh processing, case setup, and post-processing
- Develop proficiency in preprocessing utilities: `blockMesh`, `snappyHexMesh`, surface preparation tools
- Execute advanced field operations with `foamCalc` and custom post-processing workflows
- Implement automated boundary condition setup and field initialization

**Workflow Automation & Integration**
- Construct automated CFD pipelines using bash scripting and Python integration
- Develop parameter studies and design of experiments (DOE) frameworks
- Integrate OpenFOAM with HPC schedulers (SLURM, PBS) for batch processing
- Create end-to-end workflows from geometry to engineering reports

**Quality Assurance & Optimization**
- Implement comprehensive mesh quality assessment using metrics and automated checks
- Develop validation frameworks for solver-specific mesh requirements
- Optimize workflows for high-performance computing environments
- Establish best practices for code organization and version control

### Expected Outcomes

Upon completion, you will demonstrate expertise in:

- **Geometry Processing**: CAD format conversion, geometry repair, and surface mesh preparation
- **Mesh Generation**: Structured and unstructured mesh creation with `blockMesh`, `snappyHexMesh`, and specialized utilities
- **Case Management**: Boundary condition setup, initial conditions, and solver control parameter configuration
- **Automation**: Scripting for batch processing, parameter studies, and workflow optimization
- **Post-Processing**: Quantitative data extraction, visualization generation, and engineering reporting
- **Integration**: Connecting utilities with custom solvers and third-party tools

---

## 📚 Learning Path

### 🥉 Foundation: Essential Mesh Tools

#### 1. blockMesh Fundamentals

**Core Concepts**

`blockMesh` is OpenFOAM's foundational structured mesh generation utility, creating hexahedral meshes from definitions in `system/blockMeshDict`. The utility employs a block-based approach, dividing the computational domain into multiple hexahedral blocks, each defined by 8 vertices.

**Advanced Grading Techniques**

Edge grading enables variable mesh resolution through defined functions. The grading specification follows the format:

```cpp
// Edge grading syntax
edges
(
    spline 0 1
    (
        (0.0 0.0 0.0)
        (0.5 0.1 0.0)
        (1.0 0.0 0.0)
    )
);
```

**Grading Functions**
- **Linear grading**: Uniform cell size progression
- **Exponential grading**: Cell size follows exponential growth/decay
- **Power law grading**: Cell size follows $y = x^p$ where $p$ is the power parameter

**Mesh Topology Patterns**

```cpp
// O-grid topology for circular geometries
vertices
(
    (0 0 0)           // Center point
    (1 0 0)           // Inner radius
    (2 0 0)           // Outer radius
    // ... additional vertices
);
```

**Boundary Layer Considerations**

For boundary layer mesh quality, the first cell height calculation uses:

$$
y^+ = \frac{\rho u_\tau y}{\mu}
$$

where $u_\tau$ is the friction velocity computed from:

$$
u_\tau = \sqrt{\frac{\tau_w}{\rho}}
$$

#### 2. Surface Preparation

**Surface Requirements**

Quality surface meshes must satisfy:
- **Watertightness**: No gaps or holes in the triangulation
- **Normal consistency**: All face normals point outward
- **Triangle quality**: Aspect ratio < 10 for most regions
- **Feature preservation**: Sharp edges and corners maintained

**Surface Repair Utilities**

```bash
# Check surface quality
surfaceCheck geometry.stl

# Extract sharp features
surfaceFeatureExtract -angle 30 geometry.stl

# Smooth surface
surfaceSmoothFeatures geometry.stl
```

**Format Conversion Pipeline**

```mermaid
flowchart LR
    CAD[CAD File] --> STEP[STEP/IGES]
    STEP --> STL[STL Conversion]
    STL --> CHECK{Quality Check}
    CHECK -->|Pass| MESH[Meshing]
    CHECK -->|Fail| REPAIR[Repair Tools]
    REPAIR --> CHECK
```

#### 3. Mesh Quality Assessment

**Essential Quality Metrics**

- **Non-orthogonality**: $\theta = \cos^{-1}\left(\frac{\mathbf{n}_f \cdot \mathbf{d}_{PN}}{|\mathbf{n}_f| \cdot |\mathbf{d}_{PN}|}\right)$
  - Target: < 70° for general CFD
  - Target: < 40° for complex turbulence models

- **Aspect Ratio**: $AR = \frac{h_{max}}{h_{min}}$
  - Target: < 1000 for general applications
  - Target: < 100 for boundary layer regions

- **Skewness**: $\text{skewness} = \frac{|\mathbf{C} - \mathbf{C}_{ideal}|}{|\mathbf{C}_{PF} - \mathbf{C}_{ideal}|}$
  - Target: < 4 for most solvers
  - Target: < 2 for high-accuracy simulations

- **Expansion Ratio**: Local cell size variation
  - Target: < 1.3 for general CFD
  - Target: < 1.1 for boundary layers

**Automated Quality Checks**

```bash
# Comprehensive mesh analysis
checkMesh -allGeometry -allTopology -time 0

# Quality metrics only
checkMesh -meshQuality

# Detailed report with thresholds
checkMesh -allRegions -writeFields
```

### 🏦 Intermediate: Advanced Meshing Workflows

#### 1. snappyHexMesh Mastery

**Three-Stage Process**

```mermaid
flowchart TD
    START[Background Mesh] --> CAST[Castellation]
    CAST --> SNAP[Snapping]
    SNAP --> LAYER[Layer Addition]
    LAYER --> FINAL[Final Mesh]
```

**Castellation Stage**

```cpp
// snappyHexMeshDict - Castellation controls
castellatedMesh true;
castellatedMeshControls
{
    maxLocalCells        1000000;
    maxGlobalCells       20000000;
    minRefinementCells   10;

    nCellsBetweenLevels  3;

    features
    (
        {
            file "geometry.eMesh";
            level 2;
        }
    );

    refinementSurfaces
    {
        geometry
        {
            level (2 2);
            patchInfo
            {
                type wall;
            }
        }
    }

    resolveFeatureAngle 30;
}
```

**Snapping Stage**

```cpp
snapControls
{
    nSmoothPatch       3;
    tolerance          2.0;
    nSolveIter         30;
    nRelaxIter         5;

    nFeatureSnapIter   10;
    implicitFeatureSnap false;
    multiRegionFeatureSnap true;
}
```

**Layer Addition Stage**

```cpp
addLayersControls
{
    relativeSizes true;

    layers
    {
        "geometry.*"
        {
            nSurfaceLayers 3;
        }
    }

    expansionRatio      1.3;
    finalLayerThickness 0.3;
    minThickness        0.1;
    nGrow               1;

    featureAngle        60;
    nRelaxIter          3;
    nSmoothSurfaceNormals 3;
    nSmoothNormals      3;
}
```

#### 2. Multi-Block Domain Assembly

**Block Topology Planning**

```cpp
// Multi-block configuration example
blocks
(
    // Block 1: Inlet region
    hex (0 1 2 3 4 5 6 7) (100 50 1) simpleGrading (1 1 1)

    // Block 2: Main domain
    hex (8 9 10 11 12 13 14 15) (200 100 1) simpleGrading (1 1 1)

    // Block 3: Outlet region
    hex (16 17 18 19 20 21 22 23) (100 50 1) simpleGrading (1 1 1)
);

// Boundary connections
mergePatchPairs
(
    (
        block1_outlet
        block2_inlet
    )
    (
        block2_outlet
        block3_inlet
    )
);
```

#### 3. Adaptive Refinement Strategies

**Solution-Adaptive Refinement**

```cpp
// dynamicRefineFvMeshDict for runtime adaptation
dynamicFvMesh dynamicRefineFvMesh;

refiner
{
    refineInterval  5;
    field           alpha.water;
    lowerRefineLevel 0.3;
    upperRefineLevel 0.7;
    nRefineIterations 1;
    maxRefinement  4;
    maxCells       2000000;
}
```

**Error Indicator-Based Refinement**

$$
\epsilon = \left| \nabla \phi \right| \cdot h^2
$$

where $\phi$ is the field variable and $h$ is the local cell size.

### 🚀 Advanced: Specialized Applications

#### 1. Application-Specific Meshing

**Turbomachinery O-Grid**

```cpp
// O-grid topology for rotating machinery
blocks
(
    // O-grid block
    hex (0 1 2 3 4 5 6 7) (200 80 1) edgeGrading (1 1 1 1 4 4 1 1 1 1 4 4)

    // H-grid blocks for inlet/outlet
    hex (8 9 10 11 12 13 14 15) (50 20 1) simpleGrading (1 1 1)
);
```

**Boundary Layer $y^+$ Calculation**

$$
y = \frac{y^+ \mu}{\rho u_\tau}, \quad u_\tau = U_\infty \sqrt{\frac{C_f}{2}}
$$

For turbulent boundary layers:
$$
C_f \approx 0.0592 \cdot Re_x^{-0.2}
$$

#### 2. Dynamic Meshing

**Motion Solver Configuration**

```cpp
// dynamicMeshDict
dynamicFvMesh   dynamicMotionSolverFvMesh;

motionSolverLibs ("libfvMotionSolvers.so");

solver          displacementLaplacian;

displacementLaplacianCoeffs
{
    diffusivity uniform 1;
}
```

#### 3. Multi-Phase Meshing

**Interface Resolution Requirements**

$$
\Delta x < \frac{\sigma}{\rho U^2}
$$

where $\sigma$ is surface tension, $\rho$ is density, and $U$ is characteristic velocity.

**Adaptive Interface Tracking**

```cpp
refinementSurfaces
{
    interface
    {
        level (4 4);
        cellZone interface;
        faceZone interface;
    }
}
```

---

## 🛠️ Technical Outcomes

### 1. Advanced Mesh Generation & Management

**Structured Mesh with blockMesh**
- Master `blockMeshDict` syntax and topology definition
- Create multi-block structured meshes for complex geometries
- Implement grading functions for boundary layer resolution
- Apply advanced edge grading and curvature-based cell density control
- Generate conformal meshes with consistent connectivity

**Unstructured Mesh with snappyHexMesh**
- Configure surface-based meshing around STL/OBJ geometries
- Implement multi-level mesh refinement based on geometric features
- Optimize cell quality through layer addition and snapping processes
- Control refinement levels for regions of interest
- Generate high-quality boundary layer meshes with appropriate $y^+$ values

### 2. Process Automation & Workflow Optimization

**Automated Meshing Workflows**

```bash
#!/bin/bash
# Automated meshing workflow
for geom in geometries/*.stl; do
    case_name=$(basename "$geom" .stl)
    mkdir -p "cases/$case_name"
    cp mesh_template/* "cases/$case_name/"

    # Generate surface features
    surfaceFeatureExtract -case "cases/$case_name" "geometries/$case_name.stl"

    # Run meshing pipeline
    blockMesh -case "cases/$case_name"
    snappyHexMesh -case "cases/$case_name" -overwrite

    # Quality check
    checkMesh -case "cases/$case_name" > "cases/$case_name/mesh_quality.txt"
done
```

**Batch Processing for Parameter Studies**
- Implement parameter sweeps with automated case generation
- Create parallel processing workflows for HPC environments
- Develop custom scripts for systematic geometry variations
- Integrate with job schedulers (SLURM, PBS) for large-scale studies

**CAD Integration & Geometry Processing**
- Automate CAD file conversion and preprocessing
- Implement geometry cleaning and repair workflows
- Create parametric geometry generation scripts
- Integrate with CAD software APIs for seamless workflow

### 3. Comprehensive Quality Assessment

**Automated Quality Control Pipelines**

```python
# Python script for automated mesh quality assessment
import numpy as np
import pandas as pd
import re

def extract_metric(content, metric_name):
    """Extract metric value from checkMesh output."""
    pattern = rf"{metric_name}.*?([\d.]+)"
    match = re.search(pattern, content)
    return float(match.group(1)) if match else None

def calculate_quality_score(orthogonality, aspect_ratio, skewness):
    """Calculate composite quality score."""
    # Weighted quality metrics
    w_ortho = 0.4
    w_aspect = 0.3
    w_skew = 0.3

    # Normalize (lower is better for all metrics)
    score = (w_ortho * orthogonality / 70.0 +
             w_aspect * aspect_ratio / 1000.0 +
             w_skew * skewness / 4.0)
    return min(score, 1.0)  # Cap at 1.0

def assess_mesh_quality(case_path):
    # Parse checkMesh output
    with open(f"{case_path}/mesh_quality.txt", 'r') as f:
        content = f.read()

    # Extract key metrics
    orthogonality = extract_metric(content, "Non-orthogonality")
    aspect_ratio = extract_metric(content, "Aspect ratio")
    skewness = extract_metric(content, "Skewness")

    # Quality classification
    quality_score = calculate_quality_score(orthogonality, aspect_ratio, skewness)

    return {
        'case': case_path,
        'orthogonality': orthogonality,
        'aspect_ratio': aspect_ratio,
        'skewness': skewness,
        'quality_score': quality_score
    }
```

### 4. Custom Utility Development

**Custom OpenFOAM Utility Template**

```cpp
// Custom utility: meshStatisticsGenerator.C
#include "fvMesh.H"
#include "volFields.H"
#include "surfaceFields.H"
#include "OFstream.H"

using namespace Foam;

int main(int argc, char *argv[])
{
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"

    Info << "Calculating mesh statistics..." << endl;

    // Calculate mesh statistics
    const fvPatchList& patches = mesh.boundary();
    label nCells = mesh.nCells();
    label nFaces = mesh.nFaces();
    label nPoints = mesh.nPoints();
    label nInternalFaces = mesh.nInternalFaces();

    // Output detailed statistics
    OFstream outFile("meshStatistics.txt");
    outFile << "Mesh Statistics:" << nl
            << "  Cells: " << nCells << nl
            << "  Faces: " << nFaces << nl
            << "  Internal Faces: " << nInternalFaces << nl
            << "  Boundary Faces: " << (nFaces - nInternalFaces) << nl
            << "  Points: " << nPoints << nl
            << "  Patches: " << patches.size() << nl;

    // Calculate quality metrics
    scalar maxNonOrthog = 0.0;
    scalar maxSkewness = 0.0;

    // ... quality assessment implementation

    outFile << "\nQuality Metrics:" << nl
            << "  Max Non-orthogonality: " << maxNonOrthog << nl
            << "  Max Skewness: " << maxSkewness << nl;

    Info << "Mesh statistics generated successfully" << endl;
    return 0;
}
```

**Compilation and Usage**

```bash
# Compile custom utility
wmake

# Run on case
meshStatisticsGenerator -case <case_directory>
```

---

## 🎯 Module Integration

### Prerequisites

Before starting this module, ensure completion of:

**Required Modules**
- [x] **Module 03**: Mesh Generation and Geometry Fundamentals
- [x] **Module 04**: Basic Solver Development (SIMPLE/PISO implementation)

**Technical Skills**
- **OpenFOAM Commands**: Proficiency with `blockMesh`, `snappyHexMesh`, `refineMesh`, `checkMesh`
- **Shell Scripting**: BASH/Python scripting for automation
- **CAD Software**: Familiarity with CAD software and basic file formats
- **Command Line Tools**: Comfort with `grep`, `awk`, `sed`, and text processing utilities
- **File I/O Management**: Understanding of OpenFOAM file formats and data structures

### Recommended Learning Sequence

#### Foundation Phase
1. Master `blockMesh` fundamentals and topology
2. Develop surface preparation and repair skills
3. Implement mesh quality assessment workflows

#### Intermediate Phase
1. Master `snappyHexMesh` for complex geometries
2. Learn multi-block domain assembly
3. Develop systematic refinement strategies
4. Implement advanced quality enhancement techniques

#### Advanced Phase
1. Specialized CFD application meshing
2. Dynamic meshing for FSI applications
3. Multi-phase mesh requirements
4. GPU-accelerated solver considerations

---

## 📊 Module Structure

### Utility Library (`examples/`)

Organized by domain:
- **Mesh Preparation**: Advanced meshing workflows for complex geometries
- **Solver Setup**: Parameter studies and automated case generation
- **Boundary Conditions**: Boundary condition automation tools
- **Post-Processing**: Field analysis, force calculations, and visualization
- **Parallel Processing**: HPC workflow tools and batch operations
- **Multi-Phase**: Phase model configurations and specialized analysis
- **Development Tools**: C++ debugging, performance analysis, and testing frameworks

### Workflow Systems (`workflows/`)

End-to-end workflow coordination including:
- **Complete CFD Workflows**: From geometry to results with automated optimization
- **Mesh to Solver**: Integrated mesh preparation with solver validation
- **Post-Processing Pipelines**: Integrated analysis and reporting workflows

### Progressive Learning (`tutorials/`)

Structured lessons from beginner to expert:
- **Beginner**: Basic mesh creation, simple solvers, basic operations
- **Intermediate**: Complex geometries, advanced snappyHexMesh meshing
- **Advanced**: Turbulent flows, conjugate heat transfer, moving meshes
- **Expert**: Solver development, GPU acceleration, specialized physics

---

## 🔧 Key Features

### Automation-First Design

All utilities and workflows designed with automation as the primary requirement, reducing manual intervention and human error.

### Scalable Architecture

Tools scale from desktop CFD to HPC clusters and cloud environments, with built-in parallelization and optimization capabilities.

### End-to-End Coverage

From initial CAD import, mesh generation, solver execution, post-processing, to final reporting and documentation.

### Integration-Ready

Designed for integration with external tools, databases, and services, including CAD software, cloud platforms, and monitoring systems.

---

## 🎓 Professional Standards

### Code Documentation

- Follow OpenFOAM documentation guidelines
- Maintain comprehensive inline comments
- Provide usage examples for all custom utilities
- Document input parameters and expected outputs

### Industry Best Practices

- Version control workflows for CFD projects
- Automated testing and validation frameworks
- Code review processes for custom utilities
- Reproducible research practices

### Quality Assurance

- Mesh quality metrics and thresholds
- Solver convergence criteria
- Automated regression testing
- Performance benchmarking standards

---

## 📝 Summary

This module provides comprehensive technical training in OpenFOAM utilities and workflow automation, enabling you to develop complex CFD workflows capable of handling sophisticated engineering problems efficiently and reliably. The acquired skills will prepare you for advanced research and industrial applications where high-quality automated mesh generation and process optimization are critical requirements.

The module bridges the gap between basic OpenFOAM usage and professional-grade CFD practice, emphasizing:
- **Technical rigor** with mathematical foundations for all methods
- **Practical application** with working code examples and real-world workflows
- **Professional standards** for documentation, testing, and collaboration
- **Scalable solutions** from desktop to HPC environments

Upon completion, you will possess the complete toolkit necessary to tackle industrial CFD challenges with confidence and efficiency.
