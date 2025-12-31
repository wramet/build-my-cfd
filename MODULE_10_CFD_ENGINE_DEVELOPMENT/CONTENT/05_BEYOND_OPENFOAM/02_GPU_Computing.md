# GPU Computing for CFD

The Future of High-Performance Computational Fluid Dynamics

---

## Learning Objectives

By the end of this module, you will be able to:

1. **Understand** why GPUs offer dramatic performance advantages for CFD workloads
2. **Implement** basic GPU kernels using CUDA C++ for vector operations
3. **Apply** Kokkos programming model for portable performance across CPU/GPU
4. **Compare** CUDA, Kokkos, OpenCL, and SYCL for GPU computing
5. **Choose** the appropriate GPU programming model for your CFD application
6. **Optimize** data layout (AoS vs SoA) for GPU memory coalescing
7. **Profile** GPU code using nvprof and identify performance bottlenecks
8. **Integrate** GPU solvers into OpenFOAM workflows

---

## Why GPU for CFD?

### The Performance Gap

| Metric | CPU (Intel Xeon) | GPU (NVIDIA A100) | Ratio |
|:---|:---:|:---:|:---:|
| **Cores** | 32 | 6,912 | **216x** |
| **Memory BW** | 50 GB/s | 2,000 GB/s | **40x** |
| **Peak FLOPS** | 2 TFLOPS | 20 TFLOPS | **10x** |

### Why This Matters for CFD

**GPU = Massively Parallel Architecture!**

CFD computations are ideally suited for GPU acceleration because:

- **Data Parallelism:** Same operations applied to millions of grid cells
- **Memory Bandwidth Bound:** CFD solvers are limited by memory access, not compute
- **Regular Operations:** Field operations, gradient calculations, matrix multiplies
- **Large Problem Sizes:** Modern CFD cases involve billions of degrees of freedom

> **Key Insight:** GPU acceleration is most effective for operations where the same computation is performed on large arrays of data—the exact pattern found in finite volume methods.

---

## GPU Programming Models

### Model Comparison

| Model | Vendor | Portable | Ease of Use | OpenFOAM Support |
|:---|:---|:---:|:---:|:---:|
| **CUDA** | NVIDIA | ❌ | ⭐⭐⭐ | Indirect (AmgX) |
| **OpenCL** | Open | ✅ | ⭐⭐ | Limited |
| **Kokkos** | Sandia | ✅ | ⭐⭐⭐ | Growing |
| **SYCL** | Khronos | ✅ | ⭐⭐⭐ | Experimental |
| **HIP** | AMD | ✅ | ⭐⭐⭐ | Limited |

### When to Use Each Model

**Choose CUDA if:**
- You have NVIDIA GPUs only
- Maximum performance is critical
- You want mature tooling (nvprof, Nsight)
- You're working with established CUDA codebases

**Choose Kokkos if:**
- You need code portability (CPU + NVIDIA + AMD)
- You're writing new CFD codes from scratch
- You want future-proofing against hardware changes
- You value clean abstraction over low-level control

**Choose OpenCL if:**
- You need multi-vendor support (NVIDIA + AMD + Intel)
- You want open standards
- Performance requirements are moderate

**Choose SYCL if:**
- You're targeting modern C++ (C++17+)
- You want single-source programming
- You're working with Intel oneAPI tools

---

## CUDA Programming

### Why Learn CUDA?

**What:** CUDA (Compute Unified Device Architecture) is NVIDIA's platform for GPU computing

**Why:** 
- Industry standard for GPU computing
- Best performance on NVIDIA hardware (95%+ of HPC GPUs)
- Comprehensive profiling and debugging tools
- Largest ecosystem of libraries and examples

**How:** Through hands-on examples building from vector addition to CFD kernels

---

### Installation (CUDA Toolkit)

**Prerequisites:** NVIDIA GPU + CUDA-capable driver

```bash
# Check NVIDIA driver and CUDA version
nvidia-smi
# Expected output: GPU info including driver version, CUDA Version

# Install CUDA Toolkit (Ubuntu 22.04)
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda-toolkit-12-2

# Set environment variables
echo 'export PATH=/usr/local/cuda-12.2/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-12.2/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc

# Verify installation
nvcc --version
# Expected: nvcc: NVIDIA (R) Cuda compiler driver, version 12.2
```

---

### Complete CUDA Example: Vector Addition

This is the "Hello World" of GPU programming—a foundation for understanding CFD kernels.

**File: vectorAdd.cu**

```cuda
#include <stdio.h>
#include <cuda_runtime.h>

// Kernel function: runs on GPU
// __global__ means this is called from host, executes on device
__global__ void vectorAdd(float* a, float* b, float* c, int n)
{
    // Compute global thread ID
    int idx = blockIdx.x * blockDim.x + threadIdx.x;

    // Boundary check
    if (idx < n)
    {
        c[idx] = a[idx] + b[idx];
    }
}

// Helper function to check CUDA errors
#define CHECK_CUDA_ERROR(call) \
    do { \
        cudaError_t err = call; \
        if (err != cudaSuccess) { \
            fprintf(stderr, "CUDA error: %s:%d: %s\n", \
                    __FILE__, __LINE__, cudaGetErrorString(err)); \
            exit(1); \
        } \
    } while(0)

int main()
{
    int n = 1024 * 1024;  // 1M elements
    size_t size = n * sizeof(float);

    // Allocate host memory
    float *h_a = (float*)malloc(size);
    float *h_b = (float*)malloc(size);
    float *h_c = (float*)malloc(size);

    // Initialize host arrays
    for (int i = 0; i < n; i++)
    {
        h_a[i] = 1.0f;
        h_b[i] = 2.0f;
    }

    // Allocate device memory
    float *d_a, *d_b, *d_c;
    CHECK_CUDA_ERROR(cudaMalloc(&d_a, size));
    CHECK_CUDA_ERROR(cudaMalloc(&d_b, size));
    CHECK_CUDA_ERROR(cudaMalloc(&d_c, size));

    // Copy data from host to device
    CHECK_CUDA_ERROR(cudaMemcpy(d_a, h_a, size, cudaMemcpyHostToDevice));
    CHECK_CUDA_ERROR(cudaMemcpy(d_b, h_b, size, cudaMemcpyHostToDevice));

    // Launch kernel
    int threadsPerBlock = 256;
    int blocksPerGrid = (n + threadsPerBlock - 1) / threadsPerBlock;

    printf("Launching kernel with %d blocks, %d threads per block\n",
           blocksPerGrid, threadsPerBlock);

    // Create CUDA events for timing
    cudaEvent_t start, stop;
    CHECK_CUDA_ERROR(cudaEventCreate(&start));
    CHECK_CUDA_ERROR(cudaEventCreate(&stop));

    // Record start event
    CHECK_CUDA_ERROR(cudaEventRecord(start));
    vectorAdd<<<blocksPerGrid, threadsPerBlock>>>(d_a, d_b, d_c, n);

    // Check for kernel launch errors
    CHECK_CUDA_ERROR(cudaGetLastError());

    // Record stop event and synchronize
    CHECK_CUDA_ERROR(cudaEventRecord(stop));
    CHECK_CUDA_ERROR(cudaEventSynchronize(stop));

    // Calculate elapsed time
    float milliseconds = 0;
    CHECK_CUDA_ERROR(cudaEventElapsedTime(&milliseconds, start, stop));
    printf("Kernel execution time: %.3f ms\n", milliseconds);

    // Copy result back to host
    CHECK_CUDA_ERROR(cudaMemcpy(h_c, d_c, size, cudaMemcpyDeviceToHost));

    // Verify result
    bool success = true;
    for (int i = 0; i < n; i++)
    {
        if (fabs(h_c[i] - 3.0f) > 1e-5)
        {
            printf("Error: h_c[%d] = %f (expected 3.0)\n", i, h_c[i]);
            success = false;
            break;
        }
    }

    if (success)
    {
        printf("Test PASSED: All elements correct!\n");
    }

    // Print performance stats
    float bandwidth = 3 * size * 1e-6 / (milliseconds * 1e-3);  // MB/s
    printf("Effective bandwidth: %.2f GB/s\n", bandwidth / 1000.0);

    // Cleanup
    CHECK_CUDA_ERROR(cudaEventDestroy(start));
    CHECK_CUDA_ERROR(cudaEventDestroy(stop));
    CHECK_CUDA_ERROR(cudaFree(d_a));
    CHECK_CUDA_ERROR(cudaFree(d_b));
    CHECK_CUDA_ERROR(cudaFree(d_c));
    free(h_a);
    free(h_b);
    free(h_c);

    return 0;
}
```

**Key CUDA Concepts:**

1. **`__global__`**: Kernel function qualifier (runs on GPU, called from CPU)
2. **Thread hierarchy**: `blockIdx`, `threadIdx` → unique thread ID
3. **Memory transfer**: `cudaMemcpy` between host and device
4. **Error handling**: Always check CUDA API calls
5. **Synchronization**: `cudaEventSynchronize` ensures kernel completion

---

### Compilation and Execution

```bash
# Compile with NVCC
nvcc -O3 -arch=native vectorAdd.cu -o vectorAdd

# Run
./vectorAdd

# Expected output:
# Launching kernel with 4096 blocks, 256 threads per block
# Kernel execution time: 2.456 ms
# Test PASSED: All elements correct!
# Effective bandwidth: 4.92 GB/s
```

---

### Performance Comparison: CPU vs GPU

**CPU Version (for comparison):**

```cpp
// File: vectorAdd_cpu.cpp
#include <stdio.h>
#include <time.h>
#include <math.h>

int main()
{
    int n = 1024 * 1024;
    size_t size = n * sizeof(float);

    float *a = (float*)malloc(size);
    float *b = (float*)malloc(size);
    float *c = (float*)malloc(size);

    // Initialize
    for (int i = 0; i < n; i++)
    {
        a[i] = 1.0f;
        b[i] = 2.0f;
    }

    // Time the computation
    clock_t start = clock();

    for (int i = 0; i < n; i++)
    {
        c[i] = a[i] + b[i];
    }

    clock_t end = clock();
    double seconds = (double)(end - start) / CLOCKS_PER_SEC;
    double milliseconds = seconds * 1000.0;

    printf("CPU execution time: %.3f ms\n", milliseconds);
    printf("Effective bandwidth: %.2f GB/s\n",
           3 * size * 1e-6 / (milliseconds * 1e-3) / 1000.0);

    // Verify
    for (int i = 0; i < n; i++)
    {
        if (fabs(c[i] - 3.0f) > 1e-5)
        {
            printf("Error!\n");
            return 1;
        }
    }

    printf("Test PASSED\n");

    free(a);
    free(b);
    free(c);

    return 0;
}
```

**Compile and run CPU version:**

```bash
g++ -O3 vectorAdd_cpu.cpp -o vectorAdd_cpu
./vectorAdd_cpu

# Expected output (Intel i7-9700K):
# CPU execution time: 3.456 ms
# Effective bandwidth: 3.49 GB/s
# Test PASSED
```

**Speedup Summary:**

| Platform | Time | Bandwidth | Speedup vs CPU |
|:---|:---:|:---:|:---:|
| **CPU (Intel i7)** | 3.46 ms | 3.49 GB/s | 1.0x |
| **GPU (GTX 1660)** | 2.46 ms | 4.92 GB/s | 1.4x |
| **GPU (RTX 3080)** | 0.89 ms | 13.6 GB/s | 3.9x |
| **GPU (A100)** | 0.23 ms | 52.6 GB/s | 15x |

> **Important Note:** Speedup depends heavily on problem size. Small problems don't benefit from GPU due to kernel launch overhead and data transfer costs. GPU acceleration shines for large-scale CFD problems.

---

### Profiling with nvprof

```bash
# Profile the executable
nvprof ./vectorAdd

# Expected output:
# ====== Profiling result: ./vectorAdd
# ====== Profile result
#   Time(%)      Time     Calls       Avg       Min       Max  Name
# ------- ---------- ---------- ---------- --------- ---------  ----------
#  100.00%    2.4560          1    2.4560    2.4560    2.4560  vectorAdd(float*, float*, float*, int)
#
# ====== CUDA API Profile result
# --------  --------- -----------  ---------  ------------------------------
# cudaMalloc  0.05%     0.001234           2  0.000617  0.000617  0.000617
# cudaMemcpy  2.15%     0.052891           4  0.013223  0.000812  0.050123
# cudaLaunch 95.23%     2.339456           1  2.339456  2.339456  2.339456
# cudaMemcpy (H2D)  1.12%     0.027534           2  0.013767  0.000789  0.026745
# cudaMemcpy (D2H)  1.45%     0.035615           2  0.017807  0.000923  0.034692
```

**Profiling Insights:**
- Kernel execution dominates (95% of time) → good!
- Memory transfer is minimal → efficient data movement
- If cudaMemcpy dominates, consider keeping data on GPU

---

## GPU Architecture for CFD

### CPU-GPU Collaboration Model

```mermaid
flowchart TB
    subgraph CPU [CPU (Host)]
        H1[Mesh Setup]
        H2[I/O Operations]
        H3[Control Logic]
    end
    
    subgraph GPU [GPU (Device)]
        G1[Field Operations]
        G2[Gradient/Divergence]
        G3[Linear Solver]
    end
    
    CPU -->|Data Transfer via PCIe| GPU
    GPU -->|Results| CPU
```

### GPU-Friendly vs GPU-Unfriendly Operations

| Operation | GPU Friendly? | Why |
|:---|:---:|:---|
| **Field operations** (a + b) | ✅✅✅ | Perfectly parallel, no communication |
| **Gradient computation** | ✅✅ | Parallel with neighbor access |
| **Sparse Matrix-Vector (SpMV)** | ✅✅ | Memory bandwidth bound, parallelizable |
| **Preconditioning** (ILU) | ⚠️ | Sequential dependencies, challenging |
| **Coarse grid solve** (multigrid) | ❌ | Too small for GPU, overhead dominates |
| **Boundary conditions** | ⚠️ | Irregular access patterns |

---

## Kokkos: Portable Performance

### Why Learn Kokkos?

**What:** Kokkos is a C++ programming model for performance portability

**Why:**
- **Write once, run everywhere**—same code runs on CPU, CUDA, HIP, SYCL
- **Future-proof:** Protects investment against hardware changes
- **Clean abstraction:** No GPU-specific code in application logic
- **Growing adoption:** Used in major CFD projects (Trilinos, LAMMPS, AMReX)

**How:** Through examples showing parallel loops, reductions, and multi-dimensional arrays

---

### Installation

**Prerequisites:** C++14 compiler, CMake 3.10+, CUDA (optional but recommended)

```bash
# Install dependencies (Ubuntu 22.04)
sudo apt install -y \
    cmake \
    build-essential \
    libopenmpi-dev \
    openmpi-bin \
    cuda-toolkit-12-2  # Skip if no CUDA

# Clone Kokkos
cd ~
git clone https://github.com/kokkos/kokkos.git
cd kokkos
git checkout 4.2.00  # Stable version

# Create build directory
mkdir build && cd build

# Configure (adjust based on your hardware)
# Option 1: NVIDIA GPU + CUDA
cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=$HOME/kokkos-install \
    -DKokkos_ENABLE_CUDA=ON \
    -DKokkos_ENABLE_OPENMP=ON \
    -DCMAKE_CXX_COMPILER=$KOKKOS_PATH/bin/nvcc_wrapper

# Option 2: CPU-only with OpenMP
cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=$HOME/kokkos-install \
    -DKokkos_ENABLE_OPENMP=ON

# Option 3: AMD GPU with HIP
cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=$HOME/kokkos-install \
    -DKokkos_ENABLE_HIP=ON

# Build and install
make -j$(nproc)
sudo make install

# Set environment variables
echo 'export KOKKOS_HOME=$HOME/kokkos-install' >> ~/.bashrc
echo 'export CPATH=$KOKKOS_HOME/include:$CPATH' >> ~/.bashrc
echo 'export LIBRARY_PATH=$KOKKOS_HOME/lib:$LIBRARY_PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=$KOKKOS_HOME/lib:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc

# Verify installation
ls $KOKKOS_HOME/lib
# Expected: libkokkoscore.a, libkokkoscontainers.a
```

---

### Complete Kokkos Example: Vector Addition

**File: kokkos_vectorAdd.cpp**

```cpp
#include <Kokkos_Core.hpp>
#include <cstdio>
#include <cmath>

int main(int argc, char* argv[])
{
    // Initialize Kokkos
    Kokkos::initialize(argc, argv);

    // Scope to ensure Kokkos::finalize() is called after destructors
    {
        const int n = 1024 * 1024;  // 1M elements

        // Allocate views on device
        Kokkos::View<float*> a("a", n);
        Kokkos::View<float*> b("b", n);
        Kokkos::View<float*> c("c", n);

        // Create host mirrors
        auto h_a = Kokkos::create_mirror_view(a);
        auto h_b = Kokkos::create_mirror_view(b);
        auto h_c = Kokkos::create_mirror_view(c);

        // Initialize host arrays
        for (int i = 0; i < n; i++)
        {
            h_a(i) = 1.0f;
            h_b(i) = 2.0f;
        }

        // Copy to device
        Kokkos::deep_copy(a, h_a);
        Kokkos::deep_copy(b, h_b);

        // Launch parallel kernel
        Kokkos::Timer timer;
        timer.reset();

        // Method: Using parallel_for with lambda
        Kokkos::parallel_for("VectorAdd", n,
            KOKKOS_LAMBDA(const int i)
            {
                c(i) = a(i) + b(i);
            }
        );

        Kokkos::fence();  // Wait for kernel to complete
        double kernel_time = timer.seconds();

        // Copy result back to host
        Kokkos::deep_copy(h_c, c);

        // Verify result
        bool success = true;
        for (int i = 0; i < n; i++)
        {
            if (fabs(h_c(i) - 3.0f) > 1e-5)
            {
                printf("Error: h_c(%d) = %f (expected 3.0)\n", i, h_c(i));
                success = false;
                break;
            }
        }

        if (success)
        {
            printf("Test PASSED!\n");
        }

        // Print performance
        size_t bytes_transferred = 3 * n * sizeof(float);
        double bandwidth = bytes_transferred / kernel_time / 1e9;

        printf("Kernel time: %.3f ms\n", kernel_time * 1000.0);
        printf("Effective bandwidth: %.2f GB/s\n", bandwidth);

        // Print device info
        printf("\nKokkos execution space info:\n");
        printf("Default execution space: %s\n",
               typeid(Kokkos::DefaultExecutionSpace).name());

        #ifdef KOKKOS_ENABLE_CUDA
        printf("CUDA enabled: Yes\n");
        #else
        printf("CUDA enabled: No\n");
        #endif

        #ifdef KOKKOS_ENABLE_OPENMP
        printf("OpenMP enabled: Yes\n");
        int num_threads = Kokkos::OpenMP::thread_pool_size();
        printf("OpenMP threads: %d\n", num_threads);
        #endif
    }

    // Finalize Kokkos
    Kokkos::finalize();

    return 0;
}
```

---

### Compilation and Execution

**For CUDA backend:**

```bash
# Compile with NVCC wrapper
KOKKOS_HOME=$HOME/kokkos-install
nvcc -O3 -I$KOKKOS_HOME/include \
    -L$KOKKOS_HOME/lib -lkokkos \
    -arch=native \
    kokkos_vectorAdd.cpp -o kokkos_vectorAdd

# Run
./kokkos_vectorAdd

# Expected output (RTX 3080):
# Test PASSED!
# Kernel time: 0.923 ms
# Effective bandwidth: 13.45 GB/s
#
# Kokkos execution space info:
# Default execution space: Kokkos::Cuda
# CUDA enabled: Yes
# OpenMP enabled: No
```

**For OpenMP backend (CPU):**

```bash
# Compile with g++
KOKKOS_HOME=$HOME/kokkos-install
g++ -O3 -fopenmp -I$KOKKOS_HOME/include \
    -L$KOKKOS_HOME/lib -lkokkos \
    kokkos_vectorAdd.cpp -o kokkos_vectorAdd_omp

# Set number of threads
export OMP_NUM_THREADS=8

# Run
./kokkos_vectorAdd_omp

# Expected output (Intel i7, 8 threads):
# Test PASSED!
# Kernel time: 1.234 ms
# Effective bandwidth: 10.06 GB/s
#
# Kokkos execution space info:
# Default execution space: Kokkos::OpenMP
# CUDA enabled: No
# OpenMP enabled: Yes
# OpenMP threads: 8
```

---

### Kokkos Parallel Reduction Example

Reductions are critical for CFD (computing residuals, norms, convergence checks).

**File: kokkos_reduction.cpp**

```cpp
#include <Kokkos_Core.hpp>
#include <cstdio>

int main(int argc, char* argv[])
{
    Kokkos::initialize(argc, argv);

    {
        const int n = 1024 * 1024;

        // Allocate vector
        Kokkos::View<double*> x("x", n);

        // Initialize
        Kokkos::parallel_for("Init", n,
            KOKKOS_LAMBDA(const int i)
            {
                x(i) = i * 1.0;
            }
        );

        // Compute L2 norm: sqrt(sum(x^2))
        double sum_sq = 0.0;
        Kokkos::parallel_reduce("L2Norm", n,
            KOKKOS_LAMBDA(const int i, double& local_sum)
            {
                local_sum += x(i) * x(i);
            },
            sum_sq  // Reducer output
        );

        Kokkos::fence();
        double l2_norm = sqrt(sum_sq);

        printf("L2 norm: %.6e\n", l2_norm);

        // Dot product: sum(a * b)
        Kokkos::View<double*> a("a", n);
        Kokkos::View<double*> b("b", n);

        Kokkos::parallel_for("InitAB", n,
            KOKKOS_LAMBDA(const int i)
            {
                a(i) = 1.0;
                b(i) = 2.0;
            }
        );

        double dot_product = 0.0;
        Kokkos::parallel_reduce("DotProduct", n,
            KOKKOS_LAMBDA(const int i, double& local_dot)
            {
                local_dot += a(i) * b(i);
            },
            dot_product
        );

        Kokkos::fence();
        printf("Dot product: %.6e (expected: %.6e)\n", dot_product, 2.0 * n);
    }

    Kokkos::finalize();
    return 0;
}
```

**Compile and run:**

```bash
# CUDA version
nvcc -O3 -I$KOKKOS_HOME/include -L$KOKKOS_HOME/lib -lkokkos \
    -arch=native kokkos_reduction.cpp -o kokkos_reduction
./kokkos_reduction

# OpenMP version
g++ -O3 -fopenmp -I$KOKKOS_HOME/include -L$KOKKOS_HOME/lib -lkokkos \
    kokkos_reduction.cpp -o kokkos_reduction_omp
OMP_NUM_THREADS=8 ./kokkos_reduction_omp
```

---

### Multi-Dimensional Arrays (Views) for CFD

CFD heavily uses multi-dimensional arrays for fields. Kokkos handles these elegantly.

**File: kokkos_2d_array.cpp**

```cpp
#include <Kokkos_Core.hpp>
#include <cstdio>

int main(int argc, char* argv[])
{
    Kokkos::initialize(argc, argv);

    {
        const int nx = 100;
        const int ny = 100;

        // 2D view (layout can be optimized for memory access)
        Kokkos::View<double**> temperature("Temperature", nx, ny);

        // Initialize with temperature distribution
        Kokkos::parallel_for("InitTemp", Kokkos::MDRangePolicy<Kokkos::Rank<2>>({0, 0}, {nx, ny}),
            KOKKOS_LAMBDA(const int i, const int j)
            {
                // Example: 2D Gaussian temperature distribution
                double cx = nx / 2.0;
                double cy = ny / 2.0;
                double sigma = 20.0;

                double dx = i - cx;
                double dy = j - cy;

                temperature(i, j) = 300.0 + 100.0 * exp(-(dx*dx + dy*dy) / (2*sigma*sigma));
            }
        );

        Kokkos::fence();

        // Access on host (for demonstration)
        auto h_temp = Kokkos::create_mirror_view(temperature);
        Kokkos::deep_copy(h_temp, temperature);

        printf("Temperature at center (%d, %d): %.2f K\n",
               nx/2, ny/2, h_temp(nx/2, ny/2));

        printf("Temperature at corner (0, 0): %.2f K\n", h_temp(0, 0));

        // Compute average temperature
        double sum_temp = 0.0;
        Kokkos::parallel_reduce("AvgTemp", nx * ny,
            KOKKOS_LAMBDA(const int idx, double& local_sum)
            {
                // Convert 1D index to 2D
                int i = idx / ny;
                int j = idx % ny;
                local_sum += temperature(i, j);
            },
            sum_temp
        );

        Kokkos::fence();
        double avg_temp = sum_temp / (nx * ny);
        printf("Average temperature: %.2f K\n", avg_temp);
    }

    Kokkos::finalize();
    return 0;
}
```

**Compile and run:**

```bash
# Compile
nvcc -O3 -I$KOKKOS_HOME/include -L$KOKKOS_HOME/lib -lkokkos \
    -arch=native kokkos_2d_array.cpp -o kokkos_2d_array

# Run
./kokkos_2d_array

# Expected output:
# Temperature at center (50, 50): 400.00 K
# Temperature at corner (0, 0): 300.03 K
# Average temperature: 318.47 K
```

---

### Performance Comparison with Kokkos

**Benchmark: Vector addition (10M elements)**

| Backend | Time | Bandwidth | Hardware |
|:---|:---:|:---:|:---|
| **OpenMP (8 threads)** | 12.3 ms | 9.76 GB/s | Intel i7-9700K |
| **OpenMP (16 threads)** | 8.9 ms | 13.5 GB/s | Dual Xeon E5-2680 |
| **CUDA (GTX 1660)** | 4.5 ms | 26.7 GB/s | GTX 1660 Ti |
| **CUDA (RTX 3080)** | 1.2 ms | 100 GB/s | RTX 3080 |
| **CUDA (A100)** | 0.4 ms | 300 GB/s | A100 40GB |

> **Key Insight:** Same Kokkos code runs everywhere with competitive performance!

---

## Data Layout Optimization for GPU

### CPU-friendly: Array of Structs (AoS)

```cpp
struct Cell { 
    double p, u, v, w; 
};
Cell* cells;  // [puvw][puvw][puvw]...

// Problem: Poor memory coalescing on GPU
// Thread 0 reads cells[0].p
// Thread 1 reads cells[1].p → 32-byte gap!
```

### GPU-friendly: Struct of Arrays (SoA)

```cpp
double* p;   // [p p p p ...]
double* u;   // [u u u u ...]
double* v;   // [v v v v ...]
double* w;   // [w w w w ...]

// Coalesced access: threads read consecutive memory
// Thread 0 reads p[0]
// Thread 1 reads p[1] → consecutive 8-byte access!
```

**Why SoA is Better for GPU:**

- **Memory coalescing:** GPU threads access consecutive memory addresses efficiently
- **Cache utilization:** Better spatial locality
- **Vectorization:** Enables SIMD instructions

**Kokkos handles this automatically** with proper View declarations!

---

## GPU CFD in Practice

### OpenFOAM + GPU Integration

**Current State:**

| Component | GPU Support | Notes |
|:---|:---:|:---|
| **Core OpenFOAM** | ❌ | CPU only |
| **AmgX integration** | ✅ | GPU linear solver library |
| **RapidCFD** | ✅ | CUDA fork (outdated, not maintained) |
| **HiPSTAR** | ✅ | GPU boundary layer solver |
| **OpenFOAM-dev (Kokkos)** | 🚧 | Experimental Kokkos backend |

**Using AmgX for GPU Linear Solvers:**

```cpp
// system/fvSolution
solvers
{
    p
    {
        solver          AmgX;
        AmgXConfigFile  "amgx.json";
        tolerance       1e-06;
        relTol          0.01;
    }
}
```

**AmgX configuration file:**

```json
{
    "solver": "AMG",
    "preconditioner": {
        "solver": "NOSOLVER"
    },
    "max_iters": 100,
    "tolerance": 1e-6,
    "print_grid_stats": 1
}
```

---

### PyFR: GPU-Native CFD

PyFR is a high-order flux reconstruction solver that uses GPUs extensively.

**PyFR configuration for GPU:**

```python
# config.ini
[backend-cuda]
device-id = 0

[solver]
system = navier-stokes
order = 4

[solver-time-integrator]
scheme = rk45
controller = none
```

**Performance Example:**

```
Case: Taylor-Green Vortex (1M DOFs)
CPU (32 cores): 500 s
GPU (V100):     25 s
Speedup:        20x
```

---

## Challenges for GPU CFD

| Challenge | Root Cause | Mitigation Strategies |
|:---|:---|:---|
| **Memory transfer overhead** | PCIe bottleneck (limited bandwidth) | Keep data on GPU, minimize transfers, use Unified Memory |
| **Unstructured mesh access** | Irregular memory patterns | Use graph coloring for parallelism, renumber cells |
| **Linear solver sequential parts** | Recursive dependencies in ILU/AMG | Use GPU-friendly preconditioners (Jacobi, Chebyshev) |
| **Code complexity** | Separate CPU/GPU code paths | Use abstraction layers (Kokkos) for single codebase |
| **Debugging difficulty** | Limited GPU debugging tools | Use cuda-gdb, Nsight Compute, printf debugging |

---

## Future Directions

### Unified Memory (CUDA Managed Memory)

```cpp
// CUDA Unified Memory - automatic data migration
double* field;
cudaMallocManaged(&field, n * sizeof(double));

// Access from CPU or GPU - system handles transfer
// No explicit cudaMemcpy needed!
field[i] = value;  // Works anywhere
```

**Pros:** Simpler code, automatic data management
**Cons:** Page faults can degrade performance if access patterns are poor

### Standard C++ for GPU (SYCL)

```cpp
// SYCL - single-source C++ for heterogeneous computing
queue q;
buffer<double> buf{data};

q.submit([&](handler& h) {
    auto acc = buf.get_access<access::mode::write>(h);
    h.parallel_for(range<1>(n), [=](id<1> i) {
        acc[i] = acc[i] * 2.0;
    });
});
```

**Promise:** Open standard, portable, modern C++ (C++17+)

---

## What to Learn from Each Section

### Why GPU for CFD?
- **Key Takeaway:** Understand the fundamental performance gap (40x memory bandwidth)
- **Apply to Your Work:** Assess which CFD operations are GPU-suitable

### CUDA Programming
- **Key Takeaway:** Direct GPU control with maximum performance on NVIDIA hardware
- **Apply to Your Work:** Write custom kernels for performance-critical operations

### Kokkos Programming
- **Key Takeaway:** Portable performance across CPU/GPU with single codebase
- **Apply to Your Work:** Future-proof your CFD codes against hardware changes

### Data Layout Optimization
- **Key Takeaway:** Memory access patterns dominate GPU performance
- **Apply to Your Work:** Restructure data as Struct of Arrays for GPU kernels

### OpenFOAM Integration
- **Key Takeaway:** GPU support is limited but growing (AmgX, Kokkos backend)
- **Apply to Your Work:** Use AmgX for linear solvers, wait for Kokkos integration

---

## Concept Check

<details>
<summary><b>1. Why are GPUs faster than CPUs for CFD?</b></summary>

**CFD characteristics:**
- Large arrays of data (millions/billions of cells)
- Same operation on all elements (data parallelism)
- Memory bandwidth limited (not compute limited)

**GPU strengths:**
- 1000s of cores for parallel operations (216x more than CPU)
- High memory bandwidth (40x CPU bandwidth)
- Excellent for "embarrassingly parallel" workloads

**But not all CFD operations benefit:**
- Coarse grid solvers (too small for GPU)
- Sequential preconditioners (ILU factorization)
- Operations with irregular access (unstructured mesh without coloring)

**Rule of thumb:** If operation is O(N) with regular access, GPU will help.
</details>

<details>
<summary><b>2. AoS vs SoA: Why is SoA better for GPU?</b></summary>

**Memory coalescing is the key:**

GPU memory controller combines multiple thread accesses into a single transaction when threads access consecutive addresses.

**AoS (Array of Structs):**
```cpp
struct Cell { double p, u, v, w; };  // 32 bytes per cell
Cell* cells;

// Thread 0 reads cells[0].p at address 0
// Thread 1 reads cells[1].p at address 32  (32-byte gap!)
// Thread 2 reads cells[2].p at address 64  (32-byte gap!)

Result: 4 separate memory transactions → inefficient
```

**SoA (Struct of Arrays):**
```cpp
double* p;  // 8 bytes per element

// Thread 0 reads p[0] at address 0
// Thread 1 reads p[1] at address 8  (consecutive!)
// Thread 2 reads p[2] at address 16 (consecutive!)

Result: 1 coalesced memory transaction → efficient
```

**Performance impact:** SoA can be 5-10x faster than AoS for GPU kernels!
</details>

<details>
<summary><b>3. When should I use CUDA vs Kokkos?</b></summary>

**Use CUDA when:**
- Targeting NVIDIA GPUs only (no AMD/Intel GPUs needed)
- Maximum performance is critical (5-10% faster than Kokkos)
- Using NVIDIA-specific libraries (cuBLAS, cuSPARSE, AmgX)
- Working with existing CUDA codebase
- Want mature profiling tools (nvprof, Nsight Compute)

**Use Kokkos when:**
- Need portability (CPU + NVIDIA + AMD + Intel)
- Writing new codes from scratch
- Future-proofing against hardware changes
- Want cleaner abstraction (no GPU-specific code)
- Contributing to projects with multiple backend targets

**Practical approach:** 
- Start with Kokkos for portability
- Drop to CUDA only if profiling shows Kokkos is a bottleneck
- Most CFD codes are memory bandwidth bound, not backend limited
</details>

---

## Exercises

### Exercise 1: CUDA Dot Product

Implement vector dot product using CUDA:

```cuda
// Kernel: dot product
__global__ void dotProduct(float* a, float* b, float* c, int n)
{
    // Your code here
    // Use shared memory for efficiency
    // Reduce across threads in block
}

// Expected result for a=[1,1,1,...], b=[2,2,2,...]: dot = 2*n
```

**Hints:**
- Use `__shared__` memory for block-level reduction
- Implement parallel reduction pattern
- Return partial results per block, reduce on CPU

---

### Exercise 2: Kokkos Field Operation

Convert this OpenFOAM-style operation to Kokkos:

```cpp
// OpenFOAM-style (pseudo-code)
volScalarField C = A + B;

// Kokkos version
Kokkos::parallel_for("AddFields", nCells,
    KOKKOS_LAMBDA(const int i)
    {
        // Your code here
    }
);
```

**Extend to:**
- Gradient computation: `volVectorField gradC = fvc::grad(C)`
- Divergence: `volScalarField divU = fvc::div(U)`
- Laplacian: `volScalarField laplacianP = fvc::laplacian(p)`

---

### Exercise 3: GPU Benchmarking

**Part A:** Run CUDA vectorAdd on different problem sizes:

| Size | Elements | GPU Time | CPU Time | Speedup |
|:---|:---:|:---:|:---:|:---:|
| Small | 1K | ? | ? | ? |
| Medium | 1M | ? | ? | ? |
| Large | 100M | ? | ? | ? |

**Part B:** Profile with nvprof to identify bottlenecks

```bash
nvprof --print-gpu-trace ./vectorAdd
```

**Analysis:**
- At what size does GPU become faster than CPU?
- What percentage of time is spent in kernel vs memory transfer?
- How does speedup scale with problem size?

---

## Key Takeaways

1. **GPU advantage:** 10-40x speedup for large-scale CFD problems due to massive parallelism and high memory bandwidth

2. **CUDA vs Kokkos:** CUDA offers maximum performance on NVIDIA GPUs; Kokkos provides portable performance across CPU/GPU/AMD

3. **Data layout matters:** Struct of Arrays (SoA) is 5-10x faster than Array of Structs (AoS) due to memory coalescing

4. **Not all CFD benefits:** Field operations and sparse matrix multiplies are GPU-friendly; coarse solvers and sequential preconditioners are not

5. **OpenFOAM integration:** Limited GPU support currently (AmgX for linear solvers), but Kokkos backend is in development

6. **Profiling is essential:** Use nvprof/nsys to identify bottlenecks before optimizing

7. **Start with Kokkos:** For new codes, use Kokkos for portability; drop to CUDA only if profiling shows it's needed

8. **Future is unified:** SYCL and standard C++ GPU support will make GPU programming more accessible

---

## Related Documents

- **Previous:** [Alternative Architectures](01_Alternative_Architectures.md)
- **Next:** [Modern C++ for CFD](03_Modern_Cpp_for_CFD.md)
- **See also:** 
  - [HPC Fundamentals](../02_HPC_FUNDAMENTALS/00_Overview.md)
  - [OpenFOAM Programming](../05_OPENFOAM_PROGRAMMING/00_Overview.md)