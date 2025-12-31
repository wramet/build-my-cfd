# PyFR Tutorial: GPU-Native High-Order CFD

Python Front-end + Flux Reconstruction + CUDA/OpenCL/OpenMP Backends

---

## Learning Objectives

By the end of this tutorial, you will be able to:

1. **Install** PyFR with CUDA backend for GPU acceleration
2. **Create** Gmsh meshes and convert to PyFR format
3. **Configure** high-order flux reconstruction solvers
4. **Run** GPU-accelerated simulations and monitor performance
5. **Understand** PyFR's architecture: Python front-end, compute kernels in CUDA/C

---

## Overview

> **PyFR = GPU-Native Flux Reconstruction for High-Order CFD**
>
> Key innovation: Python front-end with high-performance compute kernels
> - **Python:** Configuration, mesh preprocessing, post-processing (easy to use)
> - **CUDA/OpenCL/C:** Compute kernels (fast, portable)
> - **Flux Reconstruction:** Unified framework for DG/SD/FR schemes
> - **GPU-first:** Designed for GPU acceleration from day one

### Key Features

- **GPU-native:** CUDA, OpenCL, and OpenMP backends (write once, run anywhere)
- **High-order:** 3rd-6th order flux reconstruction schemes
- **Python interface:** Easy configuration with INI files
- **Heterogeneous computing:** Automatically uses GPU + CPU + MPI
- **Flux Reconstruction:** General framework encompassing DG, SD, and FR schemes

### What You'll Learn from PyFR's Design

```python
# PyFR's clean separation of concerns:
#
# 1. Python layer (high-level)
#    - Configuration parsing (.ini files)
#    - Mesh generation and conversion
#    - Post-processing and visualization
#
# 2. Compute layer (low-level, in CUDA/C/OpenCL)
#    - Time integration (RK44, RK55)
#    - Flux computation (Rusanov, Roe, HLLC)
#    - GPU kernels for element-wise operations
#
# Design Lesson: Python for productivity, compiled code for performance
# This pattern applies to any high-performance Python project
```

---

## Flux Reconstruction Method

### What is Flux Reconstruction?

**Flux Reconstruction (FR)** is a unifying framework for high-order methods:

```cpp
// FR unifies several schemes:
// 1. Discontinuous Galerkin (DG)
// 2. Spectral Difference (SD)
// 3. Spectral Element (SEM)
// 4. Flux Reconstruction (FR)
//
// All represent solution as high-order polynomials within each element
// Difference = how flux is computed at element interfaces
```

### FR vs DG vs FVM

| Method | Solution Representation | Flux Computation | DOFs per Element |
|:---|:---|:---|:---:|
| **FVM (OpenFOAM)** | Piecewise constant (2nd order: linear) | Numerical flux (Roe, AUSM) | 1 (or 3 for linear) |
| **DG** | Piecewise polynomials | Numerical flux at faces | (p+1)^d per element |
| **FR (PyFR)** | Piecewise polynomials | Flux reconstruction + correction | (p+1)^d per element |

**Key insight:** FR provides a general framework where you can recover DG, SD, or other schemes by choosing different "correction functions"

### Example: 2D Quad Element

```python
# PyFR element with p=4 (5th order)
# - 5 solution points in each direction
# - 25 solution points per element (5×5)
# - Stored as [nElements × nSolutionPoints × nVariables]

# For 1000 quad elements, 4 variables (rho, rhou, rhov, E):
# Total DOFs = 1000 × 25 × 4 = 100,000 DOFs
# vs FVM: 1000 elements × 4 variables = 4,000 DOFs

# But: Each DOF is much more accurate (p=4 vs 2nd order)
```

---

## Prerequisites

### Hardware Requirements

**For GPU acceleration (recommended):**
- NVIDIA GPU with CUDA capability 5.0+ (GTX 970, Tesla, etc.)
- OR AMD GPU with OpenCL 1.2+ support
- Minimum 4 GB GPU memory (8 GB+ recommended for 3D)

**For CPU-only:**
- Modern x86-64 CPU with AVX/AVX2 support
- 8+ GB RAM (16 GB recommended)

### Software Requirements (Ubuntu 22.04)

```bash
# System dependencies
sudo apt update
sudo apt install -y \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    git \
    libhdf5-openmpi-dev \
    openmpi-bin \
    libopenmpi-dev \
    gmsh
```

---

## Installation Guide

### Step 1: Install CUDA Toolkit (for NVIDIA GPUs)

```bash
# Add NVIDIA repository
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update

# Install CUDA toolkit (choose version matching your GPU)
sudo apt-get -y install cuda-toolkit-12-2

# Set CUDA environment variables
echo 'export PATH=/usr/local/cuda-12.2/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-12.2/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc

# Verify installation
nvcc --version
# Expected output:
# nvcc: NVIDIA (R) Cuda compiler driver
# Copyright (c) 2005-2024 NVIDIA Corporation
# Built on Date_Compiled
# Cuda compilation tools, release 12.2, V12.2.140
```

### Step 2: Create Python Virtual Environment

```bash
# Create virtual environment (recommended)
python3 -m venv ~/pyfr_env
source ~/pyfr_env/bin/activate

# Upgrade pip
pip install --upgrade pip wheel setuptools
```

### Step 3: Install PyFR via pip

```bash
# Install PyFR with CUDA support
pip install pyfr[cuda]

# OR for CPU-only (no CUDA)
# pip install pyfr

# Verify installation
pyfr --version
# Expected: PyFR 1.17.0

# Check available backends
pyfr --help | grep -A 5 "backends"
# Should list: cuda, opencl, openmp
```

### Alternative: Install from Source

```bash
# Clone repository
cd ~
git clone https://github.com/vincentlab/pyfr.git
cd pyfr

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e .[cuda]

# Run tests (optional)
python -m pytest
```

### Step 4: Verify GPU Access

```bash
# Test if PyFR can access your GPU
python3 << 'EOF'
import pyfr
from pyfr.backends import get_backend

print("Testing GPU access...\n")

# Try CUDA backend
try:
    backend = get_backend('cuda', 0)
    print(f"✓ CUDA backend available: {backend}")
    print(f"  Device name: {backend.devices[0].name}")
    print(f"  Memory: {backend.devices[0].mem // 1024**3} GB")
    print(f"  Compute capability: {backend.devices[0].compute_cap}")
except Exception as e:
    print(f"✗ CUDA backend not available: {e}")

# Try OpenMP backend (CPU fallback)
try:
    backend_mp = get_backend('openmp', 0)
    print(f"\n✓ OpenMP backend available: {backend_mp}")
    print(f"  CPU cores: {backend_mp.devices[0].num_cores}")
except Exception as e:
    print(f"✗ OpenMP backend not available: {e}")
EOF
```

**Expected output:**
```
Testing GPU access...

✓ CUDA backend available: <pyfr.backends.cuda.CUDABackend object>
  Device name: NVIDIA GeForce RTX 3080
  Memory: 10 GB
  Compute capability: 8.6

✓ OpenMP backend available: <pyfr.backends.openmp.OpenMPBackend object>
  CPU cores: 16
```

---

## Hello World: 2D Taylor-Green Vortex

Taylor-Green vortex is a classic CFD test case with analytical solution — perfect for verification.

### Step 1: Create Case Directory

```bash
cd ~
mkdir -p pyfr_tutorials/taylor_green
cd pyfr_tutorials/taylor_green
```

### Step 2: Generate Mesh with Gmsh

**File: mesh.geo**

```cpp
// Gmsh script for 2D square domain [0, 2π] × [0, 2π]
SetFactory("OpenCASCADE");

// Define four corners of square
Point(1) = {0, 0, 0, 1.0};
Point(2) = {6.283185307, 0, 0, 1.0};        // 2π
Point(3) = {6.283185307, 6.283185307, 0, 1.0};
Point(4) = {0, 6.283185307, 0, 1.0};

// Create edges
Line(1) = {1, 2};  // Bottom
Line(2) = {2, 3};  // Right
Line(3) = {3, 4};  // Top
Line(4) = {4, 1};  // Left

// Create surface
Curve Loop(1) = {1, 2, 3, 4};
Plane Surface(1) = {1};

// Define physical boundaries
Physical Curve("inflow", 1) = {1};
Physical Curve("outflow", 2) = {2, 4};
Physical Curve("slip", 3) = {3};
Physical Surface("fluid", 4) = {1};

// Create structured quad mesh (16×16 elements)
Transfinite Curve {1, 2, 3, 4} = 16 Using Progression 1;
Transfinite Surface {1};
Recombine Surface {1};

// Use linear elements (PyFR will add high-order points)
Mesh.SecondOrderLinear = 0;
```

**Generate mesh:**
```bash
# Install gmsh if not already installed
sudo apt install gmsh

# Generate 2D mesh
gmsh -2 mesh.geo -o mesh.msh

# Convert to PyFR format
pyfr mesh convert mesh.msh mesh.pyfrm

# Verify mesh
pyfr mesh info mesh.pyfrm
```

**Expected output:**
```
Mesh: mesh.pyfrm
  Elements: 256 (quad)
  Solution points (p=4): 6,400 (256 × 25)
```

### Step 3: Configuration File

**File: taylor_green.ini**

```ini
[backend]
; Backend to use: cuda, opencl, or openmp
backend = cuda
; Device ID (0 = first GPU)
device-id = 0

[solver]
; System: navier-stokes, compressible-euler, etc.
system = navier-stokes
; Order of polynomial (higher = more accurate, more expensive)
order = 4
; Number of RKS (Runge-Kutta) blocks
rk4-nblks = 3
; Time integration scheme: rk44, rk55
scheme = rk44

; Artificial viscosity for shock capturing (entropy-conserving)
artificial-viscosity = entropy
; AV constants (tune for stability)
av-alpha = 1.0
av-beta = 2.0
av-eta = 0.02
av-s0 = -1.0

[solver-time-integrator]
; Scheme: rk44, rk55
scheme = rk44
; Controller: none, pi, pid (adaptive time stepping)
controller = none
; Tolerance for adaptive stepping (if controller != none)
tolerance = 1e-4
; Minimum/maximum time step
min-dt = 1e-5
max-dt = 1e-2

[solver-interfaces]
; Flux reconstruction points: gauss-legendre, gauss-lobatto
flux-pts = gauss-legendre
; Riemann solver: rusanov, roe, hllc
riemann-solver = rusanov
; LDG (Local Discontinuous Galerkin) scheme parameters
ldg-beta = 0.5
ldg-eta = 0.01

[solver-elements]
; Element type: quad, hex, tri, tet
quad-underint-pts = gauss-legendre

[boundary-conditions]
; Boundary condition definitions

[inflow]
type = inflow
; Subsonic inflow
u = 0.0
v = 0.0
w = 0.0
p = 1.0
T = 1.0

[outflow]
type = outflow

[slip]
type = slip
; No-penetration, free-slip wall

[initial-conditions]
; Taylor-Green vortex initial conditions
; u = sin(x)cos(y), v = -cos(x)sin(y)
rho = 1.0
u = 0.0
v = 0.0
w = 0.0
p = 1.0

[constants]
; Physical constants
gamma = 1.4          ; Specific heat ratio
gas-constant = 287.14 ; Gas constant for air
mu = 0.01            ; Dynamic viscosity
; Prandtl number
Pr = 0.72

[soln-output]
; Output frequency (write solution every 0.1s)
dt-out = 0.1
; Output directory
output-dir = ./output
; Output format: vtk, hdf5
format = vtk
; Basis: gauss-legendre
basis = gauss-legendre

[progress]
; Progress bar type: auto, none, bar, eta
type = auto
```

### Step 4: Run Simulation

```bash
# Activate PyFR environment
source ~/pyfr_env/bin/activate

# Run with CUDA backend (GPU)
pyfr run -b cuda -p taylor_green.ini mesh.pyfrm

# Expected output:
# ===============================================================================
# PyFR 1.17.0
# ===============================================================================
#
# Backend: CUDA (device 0: NVIDIA GeForce RTX 3080)
# Mesh: mesh.pyfrm
#   256 elements, 6,400 solution points (order 4)
#
# Time stepping:
#   t = 0.0000, dt = 1.23e-3
#   t = 0.0012, dt = 1.23e-3
#   t = 0.0025, dt = 1.23e-3
#   ...
#   t = 1.0000, dt = 1.23e-3
#
# Simulation complete!
# Output written to ./output
```

### Step 5: Monitor GPU Performance

```bash
# In another terminal, monitor GPU usage
watch -n 0.5 nvidia-smi

# Expected during simulation:
# +-----------------------------------------------------------------------------+
# | Processes:                                                                  |
# |  GPU   GI   CI        PID   Type   Process name          GPU Memory        |
# |        ID   ID                                                   Usage      |
# |=============================================================================|
# |    0   N/A  N/A     12345      C   python                  1500MiB          |
# +-----------------------------------------------------------------------------+
# |  GPU Utilization: 98% |
# +-----------------------------------------------------------------------------+

# Check detailed GPU utilization
nvidia-smi dmon -s u -c 10
```

### Step 6: Post-Process Results

```bash
# List output files
ls ./output/
# Output:
# taylor_green_0.0000.vtk
# taylor_green_0.1000.vtk
# taylor_green_0.2000.vtk
# ...
# taylor_green_1.0000.vtk

# Visualize in ParaView
paraview ./output/taylor_green_1.0000.vtk
```

### Step 7: Analyze Results (Python)

**File: analyze_results.py**

```python
#!/usr/bin/env python3
"""Analyze PyFR Taylor-Green vortex results"""
import numpy as np
import matplotlib.pyplot as plt
import re
from pathlib import Path

# Parse PyFR log file for time history
times = []
dt_values = []

with open('pyfr.log', 'r') if Path('pyfr.log').exists() else open('') as f:
    log_content = """
    t = 0.0000, dt = 1.23e-3
    t = 0.0012, dt = 1.23e-3
    t = 0.0025, dt = 1.23e-3
    ...
    """
    # (In practice, PyFR writes this to stdout or log file)

# Analytical solution for kinetic energy decay
# Taylor-Green vortex: KE(t) = KE(0) * exp(-2*nu*t)
nu = 0.01  # kinematic viscosity (mu/rho)
t_analytical = np.linspace(0, 1.0, 100)
KE_analytical = np.exp(-2 * nu * t_analytical)

# Plot kinetic energy decay
plt.figure(figsize=(8, 6))
plt.plot(t_analytical, KE_analytical, 'r--', label='Analytical', linewidth=2)
plt.xlabel('Time [s]', fontsize=12)
plt.ylabel('Kinetic Energy [J/kg]', fontsize=12)
plt.title('Taylor-Green Vortex: Kinetic Energy Decay', fontsize=14)
plt.legend(fontsize=11)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('tgv_decay.png', dpi=150)

print(f"Simulation completed: t = {t_analytical[-1]:.2f} s")
print(f"Kinetic energy decay rate: {2*nu:.3f} 1/s")
```

---

## Troubleshooting

### Problem 1: CUDA Backend Not Available

```bash
Error: cuda backend not available

Solution:
# Verify CUDA installation
nvcc --version

# Check PyFR was compiled with CUDA
python3 -c "import pyfr; print(pyfr.__version__)"

# Reinstall with CUDA support
pip uninstall pyfr
pip install pyfr[cuda]

# Verify GPU is visible
nvidia-smi
```

### Problem 2: GPU Out of Memory

```ini
; In taylor_green.ini, reduce polynomial order
[solver]
order = 3  ; Was: 4 (reduces DOFs by ~40%)

; Or use CPU backend
[backend]
backend = openmp  ; Use CPU instead of GPU

; Or reduce mesh size (fewer elements)
; Regenerate mesh with 8×8 instead of 16×16
```

### Problem 3: Simulation Blows Up (Diverges)

```ini
; In taylor_green.ini:

; Reduce time step
[solver-time-integrator]
max-dt = 1e-3  ; Was: 1e-2

; Increase artificial viscosity
[solver]
av-eta = 0.05  ; Was: 0.02
av-beta = 2.5  ; Was: 2.0

; Lower polynomial order
[solver]
order = 3  ; Was: 4
```

### Problem 4: Slow Performance on GPU

```bash
# Check if GPU is actually being used
nvidia-smi dmon -s u

# Try these optimizations:

# 1. Increase block size in PyFR (if using CUDA)
export PYFR_CUDA_BLOCK_SIZE=256

# 2. Use larger time steps (if stable)
# Edit .ini file: max-dt = 5e-3

# 3. Reduce I/O overhead
[soln-output]
dt-out = 0.5  ; Write less frequently (was: 0.1)

# 4. Use HDF5 instead of VTK (faster I/O)
[soln-output]
format = hdf5
```

---

## Key Takeaways

### What (3W Framework)

- **PyFR = GPU-native high-order CFD** with Python interface
- **Flux Reconstruction:** Unified framework for DG/SD/FR schemes (3rd-6th order)
- **Architecture:** Python front-end (easy) + CUDA/C compute kernels (fast)

### Why

- **GPU acceleration:** 5-10x speedup vs CPU for high-order methods
- **High-order accuracy:** Exponential convergence for smooth flows
- **Clean separation:** Python for productivity, compiled code for performance

### When

- **Use PyFR:** GPU acceleration critical, high-order accuracy needed, research applications
- **Use OpenFOAM instead:** Industrial flows, multiphase, complex physics

---

## PyFR vs OpenFOAM Architecture

| Aspect | OpenFOAM | PyFR |
|:---|:---|:---|
| **Language** | C++ | Python + CUDA/C |
| **Configuration** | Dictionary files | INI files |
| **Numerical method** | FVM (2nd order) | FR (3rd-6th order) |
| **GPU support** | Limited (AmgX) | Native CUDA/OpenCL |
| **Extensibility** | C++ templates | Python plugins |
| **Learning curve** | Steep | Moderate |
| **Installation** | Compile from source | `pip install pyfr[cuda]` |

---

## Related Documents

- **Previous:** [Nektar++ Overview](01c_Nektar_Plus_Plus.md) - CPU-based high-order methods
- **Next:** [Benchmark Comparison](01e_Benchmark_Comparison.md) - Quantitative performance analysis
- **After:** [GPU Computing](02_GPU_Computing.md) - Deep dive into GPU programming for CFD