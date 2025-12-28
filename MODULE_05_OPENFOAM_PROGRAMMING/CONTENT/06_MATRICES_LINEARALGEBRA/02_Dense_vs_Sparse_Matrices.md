> [!TIP] ทำไมเรื่องนี้สำคัญกับการจำลอง?
> เมทริกซ์คือหัวใจของการแก้สมการ偏微分方程 (PDEs) ใน CFD — **การเลือกใช้ Dense หรือ Sparse Matrix ส่งผลโดยตรงต่อหน่วยความจำและความเร็วในการคำนวณ** ถ้าเลือกผิด การรันเคสขนาด 10M cells อาจต้องการหน่วยความจำ 800 TB (แบบ Dense) ซึ่งเป็นไปไม่ได้ แต่ Sparse ทำให้เราใช้แค่ ~120 MB — นั่นคือ **ความแตกต่างระหว่างการรันได้และรันไม่ได้**

# Dense vs Sparse Matrices

การจัดเก็บและการคำนวณเมทริกซ์ใน OpenFOAM

---

## Quick Comparison

| Aspect | Dense (SquareMatrix) | Sparse (lduMatrix) |
|--------|---------------------|-------------------|
| **Storage** | All elements | Non-zeros only |
| **Memory** | O(n²) | O(n + 2m faces) |
| **Use case** | Small systems (3×3, 6×6) | Large CFD systems |
| **Example** | Gradient reconstruction | Pressure equation |

**10M cells:**
- Dense: 800 TB (impossible!)
- Sparse: ~120 MB (practical)

---

## Dense Matrices (SquareMatrix)

> [!NOTE] **📂 OpenFOAM Context**
> **Domain:** Coding/Customization (`src/`) & Numerics (`system/fvSchemes`)
> - **Code Location:** `src/OpenFOAM/matrices/SquareMatrix` (สำหรับการเขียน custom boundary condition หรือ turbulence model)
> - **Keywords:** `leastSquares`, `gradientScheme`, `SquareMatrix<Type>`
> - **ใช้จริงเมื่อ:** ต้องการแก้ระบบสมการขนาดเล็ก เช่น การคำนวณ gradient ด้วย least-squares method หรือสมการ stress-strain ใน turbulence models

### When to Use
- Least-squares gradient (3×3 per cell)
- Stress-strain relations (6×6)
- Chemical kinetics (small ODE systems)
- Coordinate transformations (3×3)

### Implementation

```cpp
template<class Type>
class SquareMatrix
{
    Type* v_;   // Row-major storage
    label n_;   // Dimension
    
public:
    // O(1) access
    Type& operator()(label i, label j) {
        return v_[i * n_ + j];  // Row-major indexing
    }
    
    SquareMatrix inv() const;  // Matrix inversion
    Type det() const;          // Determinant
};
```

### Specialized Types

```cpp
// Symmetric: stores n(n+1)/2 elements (50% saving)
SymmetricSquareMatrix<scalar> stress(6);

// Diagonal: stores n elements only
DiagonalMatrix<scalar> scaling(n);
```

---

## Sparse Matrices (lduMatrix)

> [!NOTE] **📂 OpenFOAM Context**
> **Domain:** Numerics & Linear Algebra (`system/fvSolution`) & Core Solver (`src/finiteVolume/`)
> - **Code Location:** `src/OpenFOAM/matrices/lduMatrix` (พื้นฐานของการแก้ linear system ทั้งหมดใน OpenFOAM)
> - **Solver Config:** `system/fvSolution` → ส่วน `solvers` → ระบุ `solver`, `preconditioner`, `tolerance`, `relTol`
> - **Keywords:** `GAMG`, `PBiCGStab`, `DIC`, `DILU`, `smoothSolver`
> - **ใช้จริงเมื่อ:** แก้ pressure equation (Poisson), momentum equation, หรือ scalar transport ในทุก solver เช่น `simpleFoam`, `interFoam`, `rhoPimpleFoam`

### LDU Format

```
Matrix A = L + D + U

L = Lower triangle (neighbor → owner)
D = Diagonal (self-coupling)
U = Upper triangle (owner → neighbor)
```

### Implementation

```cpp
class lduMatrix
{
    const lduMesh& mesh_;
    
    scalarField* lowerPtr_;   // Off-diagonal (lower)
    scalarField* diagPtr_;    // Diagonal
    scalarField* upperPtr_;   // Off-diagonal (upper)
    
public:
    // Access mesh connectivity
    const lduAddressing& lduAddr() const;
};
```

### Mesh Addressing

```cpp
class lduAddressing
{
    labelList owner_;      // Owner cell for each face
    labelList neighbour_;  // Neighbor cell for each face
    
public:
    const labelList& lowerAddr() const { return owner_; }
    const labelList& upperAddr() const { return neighbour_; }
};
```

**Key insight:** Matrix sparsity pattern = Mesh connectivity

---

## Matrix Assembly

> [!NOTE] **📂 OpenFOAM Context**
> **Domain:** Coding/Customization (`src/finiteVolume/`) & Numerical Schemes (`system/fvSchemes`)
> - **Code Location:** `src/finiteVolume/fvMatrices/` — สำหรับการเขียน custom discretization scheme หรือ source term
> - **Schemes Config:** `system/fvSchemes` → ส่วน `laplacianSchemes`, `divSchemes`, `gradSchemes`
> - **Keywords:** `fvMatrix`, `fvm::laplacian`, `fvm::div`, `fvm::ddt`
> - **ใช้จริงเมื่อ:** OpenFOAM สร้าง linear system อัตโนมัติจาก discretized PDEs เช่น `fvm::laplacian(nu, U)` จะ assemble matrix coefficients ผ่าน face-by-face loop

### Face-by-Face Pattern

```cpp
void assembleLaplacian(lduMatrix& matrix, scalar gamma)
{
    const lduAddressing& addr = matrix.lduAddr();
    
    forAll(addr.upperAddr(), facei)
    {
        label own = addr.lowerAddr()[facei];
        label nei = addr.upperAddr()[facei];
        
        // Geometric coefficient
        scalar coeff = gamma * magSf[facei] / magDelta[facei];
        
        // Diagonal contributions
        diag[own] += coeff;
        diag[nei] += coeff;
        
        // Off-diagonal contributions
        upper[facei] = -coeff;
        lower[facei] = -coeff;
    }
}
```

---

## Matrix-Vector Multiplication

> [!NOTE] **📂 OpenFOAM Context**
> **Domain:** Solver Core (`src/OpenFOAM/matrices/lduMatrix/`) & Linear Solvers (`src/OpenFOAM/matrices/solvers/`)
> - **Code Location:** `src/OpenFOAM/matrices/lduMatrix/lduMatrixOperations.C` — ฟังก์ชัน `Amul`, `Tmul`, `Hmul` สำหรับ matrix-vector operations
> - **Solver Config:** ถูกเรียกโดย solvers ใน `system/fvSolution` เช่น `GAMG`, `PBiCGStab`, `smoothSolver`
> - **Keywords:** `lduMatrix::Amul`, `lduMatrix::Tmul`, `lduMatrix::Hmul`, `preconditioner`
> - **ใช้จริงเมื่อ:** ทุกครั้งที่ linear solver ทำ iteration — smooth, precondition, หรือ compute residual — ต้องใช้ matrix-vector multiplication

### Sparse Amul: y = A·x

```cpp
void lduMatrix::Amul(scalarField& y, const scalarField& x)
{
    // 1. Diagonal contribution
    y = diag() * x;
    
    // 2. Lower triangle
    forAll(lowerAddr, facei)
    {
        y[nei[facei]] += lower[facei] * x[own[facei]];
    }
    
    // 3. Upper triangle
    forAll(upperAddr, facei)
    {
        y[own[facei]] += upper[facei] * x[nei[facei]];
    }
    
    // Complexity: O(n + n_faces) vs O(n²) for dense
}
```

---

## Solver Configuration

> [!NOTE] **📂 OpenFOAM Context**
> **Domain:** Simulation Control (`system/fvSolution`) & Numerical Tuning
> - **Config File:** `system/fvSolution` — นี่คือไฟล์ที่คุณ **ต้องแก้** เพื่อเลือก solver และปรับ convergence criteria
> - **Key Sections:** `solvers` → ระบุ solver สำหรับแต่ละ field (p, U, T, k, epsilon, etc.)
> - **Keywords:** `GAMG` (Geometric-Algebraic Multigrid), `PBiCGStab` (Stabilized Biconjugate Gradient), `DIC` (Diagonal Incomplete Cholesky), `DILU` (Diagonal Incomplete LU), `tolerance`, `relTol`
> - **ใช้จริงเมื่อ:** ตั้งค่า **ทุกเคส OpenFOAM** — เลือก solver ที่เหมาะกับชนิด matrix (symmetric vs non-symmetric) และปรับ tolerance เพื่อ balance ระหว่าง speed กับ accuracy

```cpp
// system/fvSolution
solvers
{
    p
    {
        solver          GAMG;      // Multigrid for Poisson
        preconditioner  DIC;       // Diagonal IC
        tolerance       1e-06;
        relTol          0.01;
    }
    
    U
    {
        solver          PBiCGStab; // For non-symmetric
        preconditioner  DILU;
        tolerance       1e-05;
        relTol          0.1;
    }
}
```

---

## Performance Tips

> [!NOTE] **📂 OpenFOAM Context**
> **Domain:** HPC Optimization (`system/fvSolution`) & Code Performance (`src/`)
> - **Solver Config:** `system/fvSolution` → `preconditioner`, `smoother` → ส่งผลต่อ cache efficiency
> - **Code Location:** เมื่อเขียน custom solver หรือ scheme ใน `src/` — ต้องรู้เรื่อง loop ordering และ memory layout
> - **Keywords:** `cache blocking`, `loop unrolling`, `SIMD`, `preconditioner efficiency`, `GAMG smoother`
> - **ใช้จริงเมื่อ:** ปรับ performance สำหรับ large cases (>10M cells) หรือ HPC environments — cache misses คือ bottleneck หลักของ sparse matrix operations

### Cache-Friendly Access

```cpp
// ❌ Column-major (cache-unfriendly)
for (i) for (j) for (k)
    C(i,j) += A(i,k) * B(k,j);  // Strided access

// ✅ Row-major (cache-friendly)
for (i) for (k) for (j)
    C(i,j) += A(i,k) * B(k,j);  // Sequential access
```

### Small Matrix Optimization

```cpp
// Stack allocation for small fixed-size matrices
FixedMatrix<scalar, 3, 3> rotation;  // No heap allocation
```

---

## 🧠 Concept Check

<details>
<summary><b>1. ทำไม CFD ใช้ sparse matrices?</b></summary>

เพราะแต่ละ cell เชื่อมต่อกับ neighbors ผ่าน faces เท่านั้น — matrix มี non-zero entries แค่ 5-15 ต่อ row (จาก 10M columns) ทำให้ประหยัดหน่วยความจำ 99.99%
</details>

<details>
<summary><b>2. LDU storage คืออะไร?</b></summary>

แยกเก็บ 3 arrays: Diagonal (n entries), Lower (n_faces entries), Upper (n_faces entries) — แทนเมทริกซ์เต็ม n×n
</details>

<details>
<summary><b>3. Mesh addressing เกี่ยวอะไรกับ matrix?</b></summary>

owner/neighbour arrays กำหนด sparsity pattern — ถ้า face เชื่อม cell i กับ j จะมี entry A[i,j] และ A[j,i] ใน matrix
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [01_Matrix_Fundamentals.md](01_Matrix_Fundamentals.md)
- **บทถัดไป:** [03_LDU_Matrix_Implementation.md](03_LDU_Matrix_Implementation.md)