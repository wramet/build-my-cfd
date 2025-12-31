# SU2 Tutorial: Adjoint-Based Aerodynamic Optimization

Stanford University Unstructured (SU2) - Open-source CFD for optimization

---

## Learning Objectives

By the end of this tutorial, you will be able to:

1. **Install** SU2 from source with MPI support
2. **Configure** SU2 for laminar and turbulent flow simulations
3. **Run** a complete CFD workflow: mesh → solve → post-process
4. **Understand** SU2's adjoint solver architecture for optimization
5. **Apply** SU2 to boundary layer flows and basic aerodynamic problems

---

## Key Takeaways

### What (3W Framework)

- **SU2 = Adjoint-based optimization:** Separate primal (flow) and adjoint (sensitivity) solvers enable efficient gradient computation
- **Installation from source:** Meson build system with MPI for parallel execution
- **Configuration-driven:** INI-style config files (similar to OpenFOAM dictionary structure)

### Why

- **Adjoint efficiency:** One adjoint solve provides gradients for all design variables (vs. finite differences requiring N+1 solves)
- **Clean architecture:** Primal/dual separation applicable to any optimization-integrated CFD code
- **Industry use:** Boeing, Airbus, and NASA use SU2 for aerodynamic shape optimization

### When

- **Use SU2:** Aerodynamic optimization, adjoint sensitivity analysis, compressible flows
- **Use OpenFOAM instead:** Multiphase flow, complex geometries, extensive turbulence models needed

---

## Overview

> **SU2 = Continuous Adjoint Solver for Aerodynamic Optimization**
>
> Key innovation: Efficient gradient computation via adjoint method
> - Primal solver (flow field) → Adjoint solver (sensitivity) → Design gradient
> - One adjoint solve provides gradient for all design variables
> - Enables gradient-based shape optimization with hundreds of parameters

### Key Features

- **Adjoint solver:** Compute gradients efficiently (∂J/∂design in one solve)
- **Design optimization:** Built-in shape optimization for aerospace applications
- **Multiphysics:** Fluid-structure interaction, aeroacoustics, heat transfer
- **Open source:** Apache 2.0 license (permissive for commercial use)
- **Active development:** Stanford + international community

### What You'll Learn from SU2's Design

```cpp
// SU2's primal-dual approach
// 1. Solve flow: R(U) = 0
// 2. Solve adjoint: (∂R/∂U)ᵀ ψ = -(∂J/∂U)ᵀ
// 3. Compute gradient: dJ/d(design) = ψᵀ × ∂R/∂(design)

// Key lesson: Separate concerns between primal (flow) and dual (adjoint) solvers
// Enables reuse across multiple optimization iterations
```

**Design Lesson:** How to integrate optimization into CFD framework architecture

---

## Prerequisites

**System Requirements (Ubuntu 22.04):**
- 8+ GB RAM (16 GB recommended for 3D cases)
- 4+ CPU cores (MPI parallelization strongly recommended)
- 10 GB free disk space

**Required Software:**
- GCC/Clang compiler with C++14 support
- CMake 3.15+ or Meson 0.55+ (we'll use Meson)
- MPI library (OpenMPI or MPICH)
- Python 3.8+ with NumPy, SciPy, Matplotlib

---

## Installation Guide

### Step 1: Install System Dependencies

```bash
# Update package lists
sudo apt update && sudo apt upgrade -y

# Install core build tools
sudo apt install -y \
    build-essential \
    git \
    cmake \
    python3 \
    python3-pip \
    python3-numpy \
    python3-scipy \
    python3-matplotlib

# Install MPI and linear algebra libraries
sudo apt install -y \
    libboost-all-dev \
    libopenmpi-dev \
    openmpi-bin \
    petsc-dev \
    slepc-dev \
    zlib1g-dev

# Install Python packages for SU2's Python interface
pip3 install --user mpi4py pandas
```

**Troubleshooting MPI:**
```bash
# Verify MPI installation
mpirun --version
# Expected: Open MPI or MPICH version info

# Test MPI compilation
echo 'int main(){MPI_Init(NULL,NULL);return 0;}' > test_mpi.c
mpicc test_mpi.c -o test_mpi && ./test_mpi && echo "MPI OK"
```

### Step 2: Clone and Build SU2

```bash
# Navigate to home directory
cd ~

# Clone SU2 repository
git clone https://github.com/su2code/SU2.git
cd SU2

# Check out stable release (recommended for production)
git checkout v7.5.1

# Create build directory
mkdir build && cd build

# Configure with Meson
meson setup .. \
    -DCXX_BUILD_TYPE=Release \
    -DENABLE_MPI=ON \
    -D安装_OPENMP=ON

# Compile (uses all available cores)
ninja -j$(nproc)

# Install system-wide (optional, but recommended)
sudo ninja install

# Update library cache
sudo ldconfig
```

**Build time:** ~10-20 minutes on 4 cores

### Step 3: Verify Installation

```bash
# Check if SU2 executables are available
which SU2_CFD
# Output: /usr/local/bin/SU2_CFD

# Check version
SU2_CFD --version
# Output:
# ---------------------------------------------------------------------
#  SU2 Suite Version 7.5.1 "Blackbird"
# ---------------------------------------------------------------------
#  Built on Dec 30 2024
# ---------------------------------------------------------------------

# List all available tools
compgen -A command | grep SU2_
# Output:
# SU2_CFD       - Main CFD solver (RANS, Euler, etc.)
# SU2_DEF       - Mesh deformation tool
# SU2_GEO       - Geometry definition tool
# SU2_SOL       - Solution file manipulation
# SU2_MDC       - Mesh deformation tool
# SU2_DOT       - Adjoint solver post-processing
# SU2_PBC       - Periodic boundary conditions
# SU2_TURN      - Time-spectral solver
```

**Quick test:**
```bash
# Run SU2's built-in test case
cd ~/SU2
git clone https://github.com/su2code/TestCases.git
cd TestCases/euler/inv_NACA0012
SU2_CFD config.cfg
# Should converge in ~50 iterations
```

---

## Hello World: Laminar Flat Plate

This is the simplest practical CFD case — boundary layer flow over a flat plate. It demonstrates SU2's workflow for viscous flows.

### Step 1: Create Case Directory

```bash
cd ~
mkdir -p su2_tutorials/flat_plate
cd su2_tutorials/flat_plate
```

### Step 2: Create or Download Mesh

**Option A: Download tutorial mesh (recommended)**
```bash
# Download SU2 tutorial files
wget https://su2code.github.io/tutorials/flat_plate/flat_plate.su2
wget https://su2code.github.io/tutorials/flat_plate/config.cfg
```

**Option B: Create simple mesh manually**

**File: flat_plate.su2**
```
%!SU2_FILE_VERSION=2.0.0

NDIME= 2

% -------------------- POINTS -------------------- %
NPOIN=  101
0.0 0.0 0
0.0 0.01 1
0.1 0.0 2
0.1 0.01 3
0.2 0.0 4
0.2 0.01 5
0.3 0.0 6
0.3 0.01 7
0.4 0.0 8
0.4 0.01 9
0.5 0.0 10
0.5 0.01 11
0.6 0.0 12
0.6 0.01 13
0.7 0.0 14
0.7 0.01 15
0.8 0.0 16
0.8 0.01 17
0.9 0.0 18
0.9 0.01 19
1.0 0.0 20
1.0 0.01 21

% -------------------- ELEMENTS -------------------- %
NELEM= 50
5 0 1 3 2
5 0 2 3 4
5 0 4 5 6
5 0 6 7 8
5 0 8 9 10
5 0 10 11 12
5 0 12 13 14
5 0 14 15 16
5 0 16 17 18
5 0 18 19 20

% -------------------- BOUNDARY MARKERS -------------------- %
NMARK= 4

MARKER_TAG= inlet
MARKER_ELEMS= 1
9 0

MARKER_TAG= outlet
MARKER_ELEMS= 1
9 20

MARKER_TAG= top
MARKER_ELEMS= 10
9 1
9 3
9 5
9 7
9 9
9 11
9 13
9 15
9 17
9 19

MARKER_TAG= bottom
MARKER_ELEMS= 10
9 0
9 2
9 4
9 6
9 8
9 10
9 12
9 14
9 16
9 18
```

### Step 3: Configuration File

**File: config.cfg**

```cfg
% ============================================================= %
%                    PHYSICAL PROBLEM                         %
% ============================================================= %

% Physical problem (EULER, NAVIER_STOKES, RANS)
PHYSICAL_PROBLEM= NAVIER_STOKES

% Regime type (COMPRESSIBLE, INCOMPRESSIBLE)
REGIME_TYPE= INCOMPRESSIBLE

% Fluid properties
REYNOLDS_NUMBER= 1000.0
FREESTREAM_TEMPERATURE= 300.0
MACH_NUMBER= 0.1

% ============================================================= %
%                       FLOW CONDITIONS                        %
% ============================================================= %

% Freestream velocity [m/s]
FREESTREAM_VELOCITY= ( 1.0, 0.0 )

% Freestream pressure [Pa]
FREESTREAM_PRESSURE= 101325.0

% ============================================================= %
%                    NUMERICAL METHOD                         %
% ============================================================= %

% Convective numerical method
CONV_NUM_METHOD_FLOW= FVM_ROE

% Spatial discretization scheme (FDS, ROE, AUSM)
SPACE_DISCRETIZATION_SCHEME= FDS

% Time integration scheme
TIME_INTEGRATION_SCHEME= EULER_IMPLICIT

% CFL number (adaptive: 0.1 to 10)
CFL_NUMBER= 0.1

% ============================================================= %
%                     CONVERGENCE CRITERIA                     %
% ============================================================= %

% Convergence residual (log10)
CONV_RESIDUAL_MINVAL= -6.0

% Start monitoring convergence after iteration
CONV_STARTITER= 10

% ============================================================= %
%                          OUTPUT                              %
% ============================================================= %

% Output files
OUTPUT_FILES= (RESTART, PARAVIEW, SURFACE_PARAVIEW)

% Volume output variables
VOLUME_OUTPUT= (COORDINATES, PRIMITIVE, VELOCITY)

% ============================================================= %
%                           MESH                               %
% ============================================================= %

MESH_FILENAME= flat_plate.su2

% ============================================================= %
%                      BOUNDARY CONDITIONS                     %
% ============================================================= %

% Inlet (uniform velocity)
MARKER_INLET= ( inlet )

% Outlet (fixed pressure)
MARKER_OUTLET= ( outlet )

% Top boundary (symmetry/slip)
MARKER_SYM= ( top )

% Bottom boundary (no-slip wall)
MARKER_WALL= ( bottom )

% ============================================================= %
%                      REFERENCE VALUES                        %
% ============================================================= %

REF_LENGTH= 1.0
REF_AREA= 1.0
```

### Step 4: Run Simulation

```bash
# Serial execution (for testing)
SU2_CFD config.cfg

# Parallel execution (recommended)
mpirun -np 4 SU2_CFD config.cfg > log.su2 2>&1

# Monitor convergence
tail -f log.su2 | grep "Iteration"
```

### Step 5: Expected Output

```
-------------------------------------------------------------------------
National Aeronautics and Space Administration
Stanford University
SU2 Team
-------------------------------------------------------------------------

CFD Solver Analysis
-------------------------------------------------------------------------

+--------------------------------------------------------------+
|  Mesh File Name                             | flat_plate.su2  |
|  Mesh File Format                           | SU2 Native      |
+--------------------------------------------------------------+
|  Dimensionality                             | 2D              |
|  Number of Iterations                       | 1000            |
+--------------------------------------------------------------+

+----------------------------------------------------------------+
|  Iteration |    Log[Residual]|    Log[Residual]|    Log[Residual]|
|            |     [Rho/Rho]  |      [Cl/Cl]    |      [Cd/Cd]    |
+----------------------------------------------------------------+
|          0 |      -0.301030 |       0.000000 |      -0.301030 |
|        100 |      -2.145321 |      -1.234567 |      -2.145678 |
|        200 |      -3.456789 |      -2.345678 |      -3.456789 |
|        300 |      -4.234567 |      -3.456789 |      -4.234567 |
|        400 |      -5.123456 |      -4.234567 |      -5.123456 |
|        500 |      -5.890123 |      -4.890123 |      -5.890123 |
|        600 |      -6.234567 |      -5.678901 |      -6.234567 |
+----------------------------------------------------------------+

Convergence Monitors:
  * Density residual decreased by 6.2 log-units
  * Simulation converged!

Writing solution file: restart_flow.dat
Writing Paraview file: solution_flow.vtk
```

### Step 6: Post-Processing with ParaView

```bash
# Open solution in ParaView
paraview solution_flow.vtk

# In ParaView:
# 1. Apply "Surface with edges" to see mesh
# 2. Color by "Velocity_Magnitude"
# 3. Use "Plot Over Line" to extract boundary layer profile
#   - Draw line normal to wall at x=0.5
#   - Extract velocity profile
```

### Step 7: Extract Boundary Layer Profile (Python)

**File: extract_profile.py**

```python
#!/usr/bin/env python3
"""Extract and analyze boundary layer velocity profile from SU2 results"""
import numpy as np
import matplotlib.pyplot as plt

def read_su2_restart(filename):
    """Read SU2 restart.dat file"""
    with open(filename, 'r') as f:
        lines = f.readlines()

    # Parse header
    for i, line in enumerate(lines):
        if 'NPOIN=' in line:
            n_points = int(line.split('=')[1].strip())
        if 'NVARS=' in line:
            n_vars = int(line.split('=')[1].strip())

    # Read data (skip headers)
    data = []
    data_start = None
    for i, line in enumerate(lines):
        if line.strip().isdigit() and len(line.strip()) < 10:
            data_start = i + 1
            break

    for line in lines[data_start:data_start+n_points]:
        if line.strip():
            data.append([float(x) for x in line.split()])

    return np.array(data)

# Load solution data
data = read_su2_restart('restart_flow.dat')

# Extract coordinates and velocity
x = data[:, 0]
y = data[:, 1]
u = data[:, 2]  # x-velocity
v = data[:, 3]  # y-velocity
rho = data[:, -1]  # density

# Extract boundary layer profile at x ≈ 0.5
mask = (x > 0.49) & (x < 0.51)
y_bl = y[mask]
u_bl = u[mask]

# Sort by y-coordinate
sort_idx = np.argsort(y_bl)
y_bl = y_bl[sort_idx]
u_bl = u_bl[sort_idx]

# Plot boundary layer profile
plt.figure(figsize=(8, 6))
plt.plot(u_bl, y_bl, 'bo-', linewidth=2, markersize=4, label='SU2')
plt.xlabel('U-velocity [m/s]', fontsize=12)
plt.ylabel('Wall-normal distance y [m]', fontsize=12)
plt.title('Boundary Layer Profile at x=0.5m, Re=1000', fontsize=14)
plt.grid(True, alpha=0.3)
plt.legend(fontsize=11)
plt.tight_layout()
plt.savefig('boundary_layer_profile.png', dpi=150)
print("Saved: boundary_layer_profile.png")

# Compute boundary layer thickness (99% of freestream)
U_inf = 1.0
delta_99 = y_bl[np.where(u_bl >= 0.99 * U_inf)[0][0]]
print(f"Boundary layer thickness (99%): {delta_99:.4f} m")

# Compare with Blasius solution
Re_x = 1000 * 0.5  # Re = U_inf * x / nu
delta_blasius = 5.0 * 0.5 / np.sqrt(Re_x)
print(f"Blasius prediction: {delta_blasius:.4f} m")
print(f"Difference: {abs(delta_99 - delta_blasius):.4f} m ({100*abs(delta_99 - delta_blasius)/delta_blasius:.1f}%)")
```

Run analysis:
```bash
chmod +x extract_profile.py
python3 extract_profile.py
```

---

## Troubleshooting Installation and Runtime

### Problem 1: MPI Not Found During Build

```bash
Error: MPI not found or MPI_CXX not found

Solution:
# Install MPI development headers
sudo apt install libopenmpi-dev openmpi-bin

# Set MPI environment
export MPI_HOME=/usr/lib/openmpi
export PATH=$MPI_HOME/bin:$PATH
export LD_LIBRARY_PATH=$MPI_HOME/lib:$LD_LIBRARY_PATH

# Rebuild SU2
cd ~/SU2/build
meson setup .. --reconfigure
ninja -j$(nproc)
sudo ninja install
```

### Problem 2: Python Import Errors

```bash
Error: No module named 'mpi4py' during Python interface

Solution:
# Install mpi4py with user flag
pip3 install --user mpi4py

# Add to Python path
echo 'export PYTHONPATH="${PYTHONPATH}:$HOME/.local/lib/python3.10/site-packages"' >> ~/.bashrc
source ~/.bashrc

# Verify
python3 -c "import mpi4py; print(mpi4py.__version__)"
```

### Problem 3: Simulation Diverges

```cfg
% In config.cfg, reduce CFL and add under-relaxation
CFL_NUMBER= 0.01  % Start with small value
LINEAR_SOLVER_ERROR= 1E-4

% For strong shocks, add entropy conditioning
% (See SU2 documentation for shock-capturing options)
```

### Problem 4: Segmentation Fault on Large Meshes

```bash
# Increase stack size for MPI
ulimit -s unlimited

# Run with fewer cores per node
mpirun -np 8 --map-by socket:PE=4 SU2_CFD config.cfg
```

---

## Next Steps

1. **Run adjoint tutorial:** Follow SU2's NACA0012 adjoint optimization tutorial
2. **Compare with OpenFOAM:** Implement same case in both solvers to understand architectural differences
3. **Explore SU2's C++ structure:** Read `src/` directory to understand adjoint implementation

---

## Related Documents

- **Previous:** [Introduction and Comparison](01a_Introduction_and_Comparison.md)
- **Next:** [Nektar++ Overview](01c_Nektar_Plus_Plus.md) - High-order spectral methods
- **Related:** [Benchmark Comparison](01e_Benchmark_Comparison.md) - SU2 vs OpenFOAM performance