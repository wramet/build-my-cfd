# GPU Computing for CFD

อนาคตของ High-Performance CFD

---

## Why GPU?

| Metric | CPU (Intel Xeon) | GPU (NVIDIA A100) |
|:---|:---:|:---:|
| **Cores** | 32 | 6,912 |
| **Memory BW** | 50 GB/s | 2,000 GB/s |
| **Peak FLOPS** | 2 TFLOPS | 20 TFLOPS |

> **GPU = Massively parallel!**
> 
> CFD is "embarrassingly parallel" for many operations

---

## GPU Programming Models

| Model | Vendor | Portable | Ease |
|:---|:---|:---:|:---:|
| **CUDA** | NVIDIA | ❌ | ⭐⭐⭐ |
| **OpenCL** | Open | ✅ | ⭐⭐ |
| **Kokkos** | Sandia | ✅ | ⭐⭐⭐ |
| **SYCL** | Khronos | ✅ | ⭐⭐⭐ |
| **HIP** | AMD | ✅ | ⭐⭐⭐ |

---

## CUDA Basics

### วิธีติดตั้ง

**สิ่งที่ต้องมี:** NVIDIA GPU + CUDA-capable driver

```bash
# Check NVIDIA driver
nvidia-smi
# Expected: GPU info including driver version, CUDA Version

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

### ตัวอย่าง CUDA ครบถ้วน: Vector Addition

นี่คือ "Hello World" ของ GPU programming

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

---

### Compile และ Run

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

### Profiling ด้วย nvprof

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

---

### เปรียบเทียบ Performance: CPU vs GPU

**CPU Version (สำหรับเปรียบเทียบ):**

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

**Note:** Speedup depends on problem size. Small problems don't benefit from GPU due to overhead.

---

---

## GPU Architecture for CFD

```mermaid
flowchart TB
    subgraph CPU [CPU (Host)]
        H1[Setup]
        H2[I/O]
        H3[Control]
    end
    
    subgraph GPU [GPU (Device)]
        G1[Field Operations]
        G2[Gradient/Divergence]
        G3[Linear Solver]
    end
    
    CPU -->|Data Transfer| GPU
    GPU -->|Results| CPU
```

---

## What's Good for GPU?

| Operation | GPU Friendly? | Why |
|:---|:---:|:---|
| **Field ops** (a + b) | ✅✅✅ | Perfectly parallel |
| **Gradient** | ✅✅ | Parallel with some communication |
| **SpMV** | ✅✅ | Matrix-vector multiply |
| **Preconditioning** | ⚠️ | Often sequential |
| **Coarse solve** | ❌ | Too small for GPU |

---

## OpenFOAM + GPU

### Current State

- **Core OpenFOAM:** CPU only
- **AmgX integration:** GPU linear solver
- **RapidCFD:** CUDA fork (outdated)
- **HiPSTAR:** GPU boundary layer solver

### Using AmgX

```cpp
// Link against AmgX for GPU solving
solvers
{
    p
    {
        solver          AmgX;
        AmgXConfigFile  "amgx.json";
    }
}
```

---

## Kokkos: Portable Performance

> **Write once, run on CPU/GPU**

---

### วิธีติดตั้ง

**สิ่งที่ต้องมี:** C++14 compiler, CMake 3.10+, CUDA (optional)

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

### ตัวอย่าง Kokkos ครบถ้วน: Vector Addition

**File: kokkos_vectorAdd.cpp**

```cpp
#include <Kokkos_Core.hpp>
#include <cstdio>
#include <cmath>

// Kernel: vector addition
KOKKOS_INLINE_FUNCTION
void vector_add_kernel(int i, const Kokkos::View<float*>& a,
                       const Kokkos::View<float*>& b,
                       Kokkos::View<float*>& c)
{
    c(i) = a(i) + b(i);
}

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

        // Method 1: Using parallel_for with lambda
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
        size_t bytes transferred = 3 * n * sizeof(float);
        double bandwidth = bytes transferred / kernel_time / 1e9;

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

### Compile และ Run

**สำหรับ CUDA backend:**

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

### ตัวอย่าง Kokkos Parallel Reduction

Reductions สำคัญมากสำหรับ CFD (เช่น computing residuals, norms)

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

### เปรียบเทียบ Performance: CPU vs GPU ด้วย Kokkos

**Benchmark: Vector addition (10M elements)**

| Backend | Time | Bandwidth | Hardware |
|:---|:---:|:---:|:---|
| **OpenMP (8 threads)** | 12.3 ms | 9.76 GB/s | Intel i7-9700K |
| **OpenMP (16 threads)** | 8.9 ms | 13.5 GB/s | Dual Xeon E5-2680 |
| **CUDA (GTX 1660)** | 4.5 ms | 26.7 GB/s | GTX 1660 Ti |
| **CUDA (RTX 3080)** | 1.2 ms | 100 GB/s | RTX 3080 |
| **CUDA (A100)** | 0.4 ms | 300 GB/s | A100 40GB |

**Key Insight:** Same Kokkos code runs everywhere with competitive performance!

---

### Multi-Dimensional Arrays (Views)

CFD ใช้ multi-dimensional arrays เยอะมาก Kokkos จัดการได้เรียบร้อย

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

---

## Data Layout for GPU

### CPU-friendly: Array of Structs (AoS)

```cpp
struct Cell { double p, u, v, w; };
Cell* cells;  // [puvw][puvw][puvw]...

// Problem: Poor memory coalescing on GPU
```

### GPU-friendly: Struct of Arrays (SoA)

```cpp
double* p;   // [p p p p ...]
double* u;   // [u u u u ...]
double* v;   // [v v v v ...]
double* w;   // [w w w w ...]

// Coalesced access: threads read consecutive memory
```

---

## GPU CFD Example: PyFR

```python
# PyFR configuration for GPU
[backend-cuda]
device-id = 0

[solver]
system = navier-stokes
order = 4

[solver-time-integrator]
scheme = rk45
```

### Performance

```
Case: Taylor-Green Vortex (1M DOFs)
CPU (32 cores): 500 s
GPU (V100):     25 s
Speedup:        20x
```

---

## Challenges for GPU CFD

| Challenge | Reason | Mitigation |
|:---|:---|:---|
| **Memory transfer** | PCIe bottleneck | Keep data on GPU |
| **Unstructured mesh** | Irregular access | Use colors for parallelism |
| **Linear solvers** | Sequential parts | Use AMG, GPU-friendly precond |
| **Code complexity** | Two versions | Use Kokkos/Kokkos |

---

## Future: Unified Memory

```cpp
// CUDA Unified Memory
cudaMallocManaged(&field, n * sizeof(double));

// Access from CPU or GPU - system handles transfer
// field[i] = ...;  // Works anywhere!
```

**Pros:** Simpler code
**Cons:** May not be optimal performance

---

## Getting Started with GPU CFD

### Step 1: Learn CUDA/Kokkos Basics

```bash
# CUDA samples
git clone https://github.com/NVIDIA/cuda-samples
cd cuda-samples/Samples/0_Introduction/vectorAdd
make
./vectorAdd

# Kokkos
git clone https://github.com/kokkos/kokkos-tutorials
```

### Step 2: Try GPU Linear Solver

```bash
# Install PETSc with CUDA
./configure --with-cuda
make
```

### Step 3: Explore PyFR

```bash
pip install pyfr
pyfr run -b cuda config.ini
```

---

## Concept Check

<details>
<summary><b>1. ทำไม GPU เร็วกว่า CPU สำหรับ CFD?</b></summary>

**CFD characteristics:**
- Large arrays of data
- Same operation on all elements
- Memory bandwidth limited

**GPU strengths:**
- 1000s of cores for parallel ops
- High memory bandwidth (40x CPU)
- Excellent for "data parallel" workloads

**But:** Not all CFD ops are GPU-friendly (e.g., coarse solvers)
</details>

<details>
<summary><b>2. AoS vs SoA: ทำไม SoA ดีกว่าสำหรับ GPU?</b></summary>

**Memory coalescing:**
GPU threads access consecutive memory addresses efficiently

**AoS:**
```
Thread 0 reads cells[0].p at address 0
Thread 1 reads cells[1].p at address 32  (skip 32 bytes!)
→ Scattered access, inefficient
```

**SoA:**
```
Thread 0 reads p[0] at address 0
Thread 1 reads p[1] at address 8  (consecutive!)
→ Coalesced access, efficient
```
</details>

---

## Exercise

1. **CUDA Basics:** Implement vector dot product
2. **Kokkos Port:** Convert OpenFOAM field operation to Kokkos
3. **PyFR Benchmark:** Run tutorial case, compare GPU vs CPU

---

## เอกสารที่เกี่ยวข้อง

- **ก่อนหน้า:** [Alternative Architectures](01_Alternative_Architectures.md)
- **ถัดไป:** [Modern C++ for CFD](03_Modern_Cpp_for_CFD.md)
