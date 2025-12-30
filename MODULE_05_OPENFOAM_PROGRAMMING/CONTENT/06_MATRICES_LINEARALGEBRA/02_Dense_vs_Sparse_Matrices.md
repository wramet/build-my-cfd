# 02. Dense vs Sparse Matrices

---

## Learning Objectives

เมื่ออ่านจบบทนี้ คุณจะสามารถ:
- **อธิบาย** ความแตกต่างระหว่าง Dense และ Sparse Matrix ทั้งในด้านโครงสร้างข้อมูลและผลกระทบต่อหน่วยความจำ
- **คำนวณ** ความต้องการหน่วยความจำของ Dense Matrix (O(n²)) เทียบกับ Sparse Matrix (O(n + n_faces)) สำหรับเคส CFD จริง
- **เลือกใช้** SquareMatrix หรือ lduMatrix อย่างเหมาะสมตามขนาดของระบบสมการและลักษณะของปัญหา
- **อธิบาย** วิธีการจัดเก็บข้อมูลแบบ LDU (Lower-Diagonal-Upper) และความสัมพันธ์กับ mesh topology
- **ประยุกต์** ความรู้เรื่องหน่วยความจำและ performance ในการตั้งค่า `system/fvSolution` สำหรับเคสขนาดใหญ่

---

## Quick Comparison: Why This Matters

> [!TIP] **ทำไมเรื่องนี้สำคัญกับการจำลอง?**
> เมทริกซ์คือหัวใจของการแก้สมการ PDEs ใน CFD — **การเลือกใช้ Dense หรือ Sparse Matrix ส่งผลโดยตรงต่อหน่วยความจำและความเร็วในการคำนวณ** ถ้าเลือกผิด การรันเคสขนาด 10M cells อาจต้องการหน่วยความจำ 800 TB (แบบ Dense) ซึ่งเป็นไปไม่ได้ แต่ Sparse ทำให้เราใช้แค่ ~120 MB — นั่นคือ **ความแตกต่างระหว่างการรันได้และรันไม่ได้**

| Aspect | Dense (SquareMatrix) | Sparse (lduMatrix) |
|--------|---------------------|-------------------|
| **Storage** | All elements | Non-zeros only |
| **Memory** | O(n²) | O(n + 2n_faces) |
| **Access Pattern** | Sequential | Indirect via mesh |
| **Use Case** | Small systems (3×3, 6×6) | Large CFD systems |
| **Example** | Gradient reconstruction | Pressure equation |
| **Typical Non-zeros/Row** | n | 5-15 (mesh-dependent) |

### Real-World Impact

**Case: 10M cells (n = 10,000,000)**
- **Dense Storage:** 10M × 10M × 8 bytes = **800 TB** ❌ ใช้งานไม่ได้
- **Sparse Storage:** ~10M × 7 (avg non-zeros) × 8 bytes ≈ **120 MB** ✅ ใช้งานได้

**Why:** CFD meshes produce matrices where each row has only 5-15 non-zero entries (determined by cell connectivity) — storing zeros wastes 99.99% of memory

---

## Dense Matrices: SquareMatrix

> [!NOTE] **📂 OpenFOAM Context**
> **Domain:** Coding/Customization (`src/`) & Numerics (`system/fvSchemes`)
> - **Code Location:** `src/OpenFOAM/matrices/SquareMatrix`
> - **Keywords:** `leastSquares`, `gradientScheme`, `SquareMatrix<Type>`
> - **ใช้จริงเมื่อ:** ต้องการแก้ระบบสมการขนาดเล็ก เช่น การคำนวณ gradient ด้วย least-squares method หรือสมการ stress-strain ใน turbulence models

### Data Structure

```cpp
template<class Type>
class SquareMatrix
{
    Type* v_;   // Row-major storage: v_[i*n + j]
    label n_;   // Dimension (n×n)
    
public:
    // O(1) direct access
    Type& operator()(label i, label j) {
        return v_[i * n_ + j];  // Row-major indexing
    }
    
    // Matrix operations
    SquareMatrix inv() const;  // O(n³) inversion
    Type det() const;          // Determinant
    void LU(SquareMatrix& L, SquareMatrix& U) const;
};
```

**Memory Layout:** Contiguous array `v_[0...n²-1]` in row-major order

### When to Use Dense Matrices

| Application | Matrix Size | Reason |
|-------------|-------------|--------|
| **Least-squares gradient** | 3×3 | Small, dense from polynomial fit |
| **Stress-strain relations** | 6×6 | Symmetric but dense |
| **Chemical kinetics** | <50×50 | ODE systems, all variables coupled |
| **Coordinate transforms** | 3×3 or 4×4 | Rotation/scaling matrices |
| **Jacobian inversion** | Variable | Small subsystems in implicit schemes |

### Specialized Dense Types

```cpp
// Symmetric: stores n(n+1)/2 elements (50% saving)
SymmetricSquareMatrix<scalar> stress(6);  // 21 elements vs 36

// Diagonal: stores n elements only
DiagonalMatrix<scalar> scaling(n);

// Fixed-size: stack allocation, no heap overhead
FixedMatrix<scalar, 3, 3> rotation;  // Compile-time size
```

**Why Specialization Matters:** Symmetric matrices appear in stress calculations (6 components for 3D) — storing half saves memory and avoids redundant computations

---

## Sparse Matrices: lduMatrix

> [!NOTE] **📂 OpenFOAM Context**
> **Domain:** Numerics & Linear Algebra (`system/fvSolution`) & Core Solver (`src/finiteVolume/`)
> - **Code Location:** `src/OpenFOAM/matrices/lduMatrix`
> - **Solver Config:** `system/fvSolution` → ส่วน `solvers` → ระบุ `solver`, `preconditioner`, `tolerance`, `relTol`
> - **Keywords:** `GAMG`, `PBiCGStab`, `DIC`, `DILU`, `smoothSolver`
> - **ใช้จริงเมื่อ:** แก้ pressure equation (Poisson), momentum equation, หรือ scalar transport ในทุก solver เช่น `simpleFoam`, `interFoam`, `rhoPimpleFoam`

### LDU Data Structure

**Concept:** Split matrix into three parts based on mesh connectivity

```
A × x = b

Where A = L + D + U

L = Lower triangle  (neighbor → owner contributions)
D = Diagonal        (self-coupling at each cell)
U = Upper triangle  (owner → neighbor contributions)
```

**Storage Format:**

```cpp
class lduMatrix
{
    const lduMesh& mesh_;
    
    scalarField* lowerPtr_;   // n_faces entries (lower triangle)
    scalarField* diagPtr_;    // n_cells entries (diagonal)
    scalarField* upperPtr_;   // n_faces entries (upper triangle)
    
public:
    const lduAddressing& lduAddr() const;  // Mesh connectivity
};
```

**Memory Usage:** 3×n_faces + n_cells ≈ 7×n_cells (for typical hex meshes)

### Mesh Addressing: The Sparsity Pattern

```cpp
class lduAddressing
{
    labelList owner_;      // Owner cell index for each face
    labelList neighbour_;  // Neighbor cell index for each face
    
public:
    const labelList& lowerAddr() const { return owner_; }    // "lower" = owner
    const labelList& upperAddr() const { return neighbour_; } // "upper" = neighbor
};
```

**Key Insight:** Matrix sparsity pattern **IS** mesh topology

```
Mesh:                    Matrix Sparsity Pattern:
cell0 -- face0 -- cell1   A[0,1] and A[1,0] exist (from face0)
  |                     |
face1                  face1 adds A[0,2], A[2,0]
  |                     
cell2                   A[1,2] doesn't exist (no direct face)
```

### Why LDU Works for CFD

1. **Finite Volume Discretization:** Coefficients computed **per face** — natural fit for LDU
2. **Mesh Locality:** Cell `i` only couples to immediate neighbors — matrix has narrow bandwidth
3. **Assembly Efficiency:** One loop over faces fills entire matrix
4. **Solver Compatibility:** Iterative solvers (GAMG, PBiCGStab) only need matrix-vector products — LDU provides this efficiently

---

## Memory Comparison: The Numbers

### Storage Formula

| Matrix Type | Memory (bytes) | Formula |
|-------------|----------------|---------|
| Dense (SquareMatrix) | 8n² | All elements stored |
| Sparse (lduMatrix) | 8(n + 2n_faces) | Diagonal + lower + upper |

### Example Calculation

**Hexahedral mesh: n = 1,000,000 cells**

```
n_faces ≈ 3 × n = 3,000,000 (internal faces)

Dense: 8 × (10⁶)² = 8 × 10¹² bytes = 8 TB ❌

Sparse: 8 × (10⁶ + 2×3×10⁶) = 8 × 7×10⁶ = 56 MB ✅

Savings: 99.9993%
```

**Why This Matters:** 
- **Desktop PC:** Can run 10M cell case (sparse: 120 MB) ❌ Cannot store dense version (8 TB)
- **HPC Cluster:** Memory bottleneck disappears with sparse — allows **100× larger meshes** on same hardware

---

## Operations: Data Structure Implications

> [!WARNING] **SCOPE CLARIFICATION**
> This section **introduces** operations — detailed algorithms are in **03_fvMatrix**. Here we focus on **how data structures enable operations**.

### Matrix-Vector Multiplication: Amul

**Dense Implementation:**
```cpp
// y = A × x  (Dense)
for (label i = 0; i < n; i++)
{
    y[i] = 0;
    for (label j = 0; j < n; j++)
        y[i] += A(i,j) * x[j];  // O(n²) operations
}
```

**Sparse Implementation:**
```cpp
// y = A × x  (Sparse LDU)
void lduMatrix::Amul(scalarField& y, const scalarField& x)
{
    // 1. Diagonal contribution (O(n))
    y = diag() * x;
    
    // 2. Lower triangle (O(n_faces))
    forAll(lowerAddr(), facei)
    {
        label own = lowerAddr()[facei];
        label nei = upperAddr()[facei];
        y[nei] += lower()[facei] * x[own];
    }
    
    // 3. Upper triangle (O(n_faces))
    forAll(upperAddr(), facei)
    {
        label own = lowerAddr()[facei];
        label nei = upperAddr()[facei];
        y[own] += upper()[facei] * x[nei];
    }
    
    // Total: O(n + n_faces) vs O(n²) for dense
}
```

**Performance Comparison (10M cells):**
- Dense: 10¹⁴ operations → **hours/days**
- Sparse: 7×10⁷ operations → **milliseconds**

### Transpose Multiplication: Tmul

```cpp
// y = Aᵀ × x  (Sparse)
void lduMatrix::Tmul(scalarField& y, const scalarField& x)
{
    // Same as Amul, but swap lower ↔ upper
    y = diag() * x;
    
    forAll(lowerAddr(), facei)
    {
        label own = lowerAddr()[facei];
        label nei = upperAddr()[facei];
        y[own] += lower()[facei] * x[nei];  // Note: swapped
    }
    
    forAll(upperAddr(), facei)
    {
        label own = lowerAddr()[facei];
        label nei = upperAddr()[facei];
        y[nei] += upper()[facei] * x[own];  // Note: swapped
    }
}
```

**Why Needed:** Adjoint problems, sensitivity analysis, some preconditioners (DIC)

---

## Solver Configuration: Matching Matrix Type to Solver

> [!NOTE] **📂 OpenFOAM Context**
> **Domain:** Simulation Control (`system/fvSolution`)
> - **Config File:** `system/fvSolution`
> - **Key Sections:** `solvers`
> - **Keywords:** `GAMG`, `PBiCGStab`, `DIC`, `DILU`

### Symmetric Matrices (e.g., Pressure Poisson)

**Matrix Properties:** 
- `A[i,j] = A[j,i]` (symmetric)
- Positive definite (pressure equation)

**Recommended Solvers:**

```cpp
// system/fvSolution
solvers
{
    p
    {
        solver          GAMG;              // Geometric-Algebraic Multigrid
        preconditioner  DIC;               // Diagonal Incomplete Cholesky
        tolerance       1e-06;
        relTol          0.01;
        smoother        GaussSeidel;       // GAMG smoother
    }
}
```

**Why GAMG + DIC:**
- **GAMG:** Exploits mesh hierarchy — coarse grid solves speed up convergence
- **DIC:** Preserves symmetry, cheap preconditioning (~O(n))
- **Convergence:** O(n) complexity vs O(n²) for direct methods

### Non-Symmetric Matrices (e.g., Momentum)

**Matrix Properties:**
- `A[i,j] ≠ A[j,i]` (convection creates asymmetry)
- May be indefinite (high Reynolds number)

**Recommended Solvers:**

```cpp
// system/fvSolution
solvers
{
    U
    {
        solver          PBiCGStab;         // Stabilized Biconjugate Gradient
        preconditioner  DILU;              // Diagonal Incomplete LU
        tolerance       1e-05;
        relTol          0.1;
    }
}
```

**Why PBiCGStab + DILU:**
- **PBiCGStab:** Handles non-symmetry, stabilized version avoids breakdown
- **DILU:** General-purpose preconditioner for non-symmetric systems
- **Faster convergence** than BiCGStab for convection-dominated flows

### Solver Selection Guide

| Matrix Property | Solver | Preconditioner | Use Case |
|-----------------|--------|----------------|----------|
| Symmetric + SPD | GAMG | DIC | Pressure, Poisson |
| Non-symmetric | PBiCGStab | DILU | Momentum, scalar transport |
| Mildly non-symmetric | PCG | DIC | Low Re turbulence |
| Highly ill-conditioned | GMRES | DILU/FDIP | Complex physics |

---

## Performance Tips

> [!NOTE] **📂 OpenFOAM Context**
> **Domain:** HPC Optimization (`system/fvSolution`) & Code Performance
> - **Keywords:** `cache blocking`, `SIMD`, `preconditioner efficiency`

### Cache-Friendly Operations

**Problem:** Sparse matrix access is **indirect** — poor cache locality

```cpp
// ❌ Cache-unfriendly (random access)
forAll(lowerAddr, facei)
{
    label nei = upperAddr()[facei];      // Random cell index
    y[nei] += lower[facei] * x[own];     // Cache miss likely
}
```

**Solution:** OpenFOAM optimizes via:
1. **Loop ordering:** Process faces in cache-friendly blocks
2. **Preconditioner design:** DIC/DILU use diagonal only (sequential access)
3. **Coloring:** GAMG uses mesh coloring to avoid race conditions

### Small Matrix Optimization

```cpp
// Stack allocation for small fixed-size matrices
FixedMatrix<scalar, 3, 3> rotation;  // No heap allocation

// Inlined operations (compiler optimization)
template<int N>
FixedMatrix<scalar, N, N> inv(const FixedMatrix<scalar, N, N>& A)
{
    // Compile-time unrolling for N ≤ 4
}
```

### Memory Bandwidth Bottleneck

**Reality Check:** Sparse operations are **memory-bound**, not compute-bound

```
Arithmetic Intensity = operations / byte accessed

Dense gemm: ~10 FLOPs/byte (compute-bound)
Sparse Amul: ~0.1 FLOPs/byte (memory-bound)
```

**Implication:** 
- **Upgrading CPU** → Minimal gain (waiting for memory)
- **Faster RAM** → Significant gain
- **Preconditioning quality** → Major impact (reduces iterations)

---

## 🧠 Concept Check

<details>
<summary><b>1. ทำไม CFD ใช้ sparse matrices?</b></summary>

เพราะแต่ละ cell เชื่อมต่อกับ neighbors ผ่าน faces เท่านั้น — matrix มี non-zero entries แค่ 5-15 ต่อ row (จาก 10M columns) ทำให้ประหยัดหน่วยความจำ 99.99% และลดเวลาคำนวณจาก O(n²) → O(n + n_faces)
</details>

<details>
<summary><b>2. LDU storage คืออะไร และทำไมถึงเหมาะกับ CFD?</b></summary>

LDU แยกเก็บเป็น 3 arrays: Diagonal (n entries), Lower (n_faces entries), Upper (n_faces entries) — เหมาะกับ CFD เพราะ finite volume discretization คำนวณ coefficients ต่อ face ซึ่ง map โดยตรงกับ lower/upper entries และ mesh topology กำหนด sparsity pattern โดยอัตโนมัติ
</details>

<details>
<summary><b>3. Mesh addressing เกี่ยวอะไรกับ matrix?</b></summary>

owner/neighbour arrays ใน lduAddressing กำหนดว่า matrix entries จะอยู่ที่ไหน — ถ้า face หนึ่งเชื่อม cell i กับ j จะมี entry A[i,j] ใน upper และ A[j,i] ใน lower นั่นหมายความว่า mesh structure กำหนด matrix structure โดยตรง ไม่ต้องสร้าง connectivity table แยก
</details>

<details>
<summary><b>4. เลือก GAMG หรือ PBiCGStab ยังไง?</b></summary>

- **GAMG + DIC:** สำหรับ symmetric matrices เช่น pressure equation (Poisson) — ใช้ mesh hierarchy เพื่อ accelerate convergence
- **PBiCGStab + DILU:** สำหรับ non-symmetric matrices เช่น momentum equation ที่มี convection — จัดการ asymmetry และ instability ได้ดีกว่า
</details>

<details>
<summary><b>5. Dense matrix ใช้ได้ไหมใน CFD?</b></summary>

ใช้ได้แต่ **เฉพาะ subsystems เล็กๆ** เช่น:
- 3×3 สำหรับ least-squares gradient reconstruction
- 6×6 สำหรับ stress-strain calculations
- Small ODE systems ใน chemical kinetics

สำหรับ main linear system (pressure/velocity) จะใช้ lduMatrix เสมอ เพราะ dense version ต้องการ memory เป็น TB สำหรับ realistic meshes
</details>

---

## Key Takeaways

1. **Memory Dominates Everything:** Dense matrices require O(n²) storage — for 10M cells this means 800 TB (impossible). Sparse matrices need only O(n + n_faces) ≈ 120 MB — this is why CFD works at all.

2. **LDU Exploits Mesh Structure:** The Lower-Diagonal-Upper format maps directly to finite volume discretization — faces become matrix entries. No separate connectivity table needed; mesh topology **IS** the matrix structure.

3. **Operation Complexity Matters:** Matrix-vector multiplication drops from O(n²) (dense) to O(n + n_faces) (sparse) — for 10M cells: 10¹⁴ operations vs 10⁷ operations. This is the difference between hours and milliseconds.

4. **Solver Choice Depends on Matrix Properties:** Symmetric positive definite matrices (pressure) use GAMG + DIC. Non-symmetric matrices (momentum) use PBiCGStab + DILU. Matching solver to matrix type determines convergence speed.

5. **Sparse is Memory-Bound:** Sparse operations spend most time waiting for memory, not computing. Faster RAM and better preconditioners (fewer iterations) matter more than CPU speed.

---

## 📖 เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [01_Introduction.md](01_Introduction.md) — Matrix fundamentals in OpenFOAM
- **บทถัดไป:** [03_LDU_Matrix_Implementation.md](03_LDU_Matrix_Implementation.md) — Operations and algorithms in detail