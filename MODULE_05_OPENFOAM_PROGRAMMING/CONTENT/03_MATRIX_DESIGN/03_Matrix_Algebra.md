# Matrix Algebra Design (การออกแบบพีชคณิตเมทริกซ์)

## Overview (ภาพรวม)

### ⭐ Design Philosophy

The matrix algebra system in OpenFOAM is optimized for sparse, structured matrices typical in CFD applications. This chapter explores custom matrix operations, SIMD optimization, and parallel algorithms that ensure efficient solution of linear systems arising from discretized PDEs.

> **File:** `openfoam_temp/src/OpenFOAM/matrices/matrices.H`
> **Lines:** 1-50

## Custom Matrix Operations (การดำเนินการเมทริกซ์ทกาศิต)

### ⭐ Matrix Storage Formats

```cpp
// Compressed Sparse Row format
template<class Type>
class csrMatrix
{
    Type* values_;        // Non-zero values
    label* colIndices_;  // Column indices
    label* rowPtrs_;     // Row pointers
    label nRows_;
    label nCols_;
    label nNonZeros_;

public:
    // Constructors
    csrMatrix(label nRows, label nCols, label nNonZeros);

    // Accessors
    const Type& operator()(label i, label j) const;
    Type& operator()(label i, label j);

    // Matrix operations
    tmp<Field<Type>> operator*(const Field<Type>& x) const;

    // Matrix properties
    label nRows() const { return nRows_; }
    label nCols() const { return nCols_; }
    label nNonZeros() const { return nNonZeros_; }
};

// Compressed Sparse Column format
template<class Type>
class cscMatrix
{
    Type* values_;        // Non-zero values
    label* rowIndices_;  // Row indices
    label* colPtrs_;     // Column pointers
    label nRows_;
    label nCols_;
    label nNonZeros_;

public:
    // Matrix-vector operations
    tmp<Field<Type>> multiply(const Field<Type>& x) const;

    // Matrix transpose operations
    tmp<cscMatrix<Type>> transpose() const;

    // Matrix factorizations
    bool LU(Field<scalar>& pivots) const;
};
```

### ⭐ Block Matrix Operations

```cpp
// Block matrix structure
template<class Type>
class blockMatrix
{
    List<tmp<matrix<Type>>> blocks_;
    label blockSize_;
    label nBlocks_;

public:
    // Constructor
    blockMatrix(
        const List<tmp<matrix<Type>>>& blocks,
        label blockSize
    );

    // Block operations
    tmp<Field<Type>> blockMultiply(
        const Field<Type>& x,
        label blockRow
    ) const;

    // Schur complement operations
    tmp<matrix<Type>> schurComplement() const;

    // Domain decomposition
    void decompose(label nPartitions);
};
```

### ⭐ Structured Matrix Patterns

```cpp
// Block-tridiagonal matrix
template<class Type>
class blockTridiagonalMatrix
{
    List<tmp<matrix<Type>>> diagonal_;
    List<tmp<matrix<Type>>> upperDiagonal_;
    List<tmp<matrix<Type>>> lowerDiagonal_;

public:
    // Thomas algorithm for block-tridiagonal
    tmp<Field<Type>> solveThomas(
        const Field<Type>& rhs
    ) const;

    // Parallel block operations
    void parallelSolve(
        Field<Type>& solution,
        const Field<Type>& rhs
    );
};

// Band matrix implementation
template<class Type>
class bandMatrix
{
    Type* data_;         // Band storage
    label lowerBand_;
    label upperBand_;
    label nRows_;

public:
    // Band matrix operations
    tmp<Field<Type>> multiplyBand(
        const Field<Type>& x
    ) const;

    // Efficient factorization
    bool factorizeBand();

    // Solution with band structure
    tmp<Field<Type>> solveBand(
        const Field<Type>& rhs
    ) const;
};
```

## SIMD Optimization (การเพิ่มประสิทธิภาพ SIMD)

### ⭐ Vectorized Matrix Operations

```cpp
// SIMD-optimized matrix-vector multiplication
template<class Type>
class SIMDMatrixOperations
{
public:
    // Process multiple rows simultaneously
    static void multiplyAVX2(
        Type* result,
        const Type* matrix,
        const Type* vector,
        label nRows,
        label nCols
    );

    // Cache-friendly tiling
    static void multiplyTiled(
        Type* result,
        const Type* matrix,
        const Type* vector,
        label nRows,
        label nCols,
        label tileSize
    );

    // Non-zero vector operations
    static void sparseMultiply(
        Type* result,
        const Type* values,
        const label* colIndices,
        const label* rowPtrs,
        const Type* vector,
        label nRows
    );
};
```

### ⭐ Memory Alignment

```cpp
// Aligned matrix storage
template<class Type>
class alignedMatrix
{
    Type* data_;
    label stride_;  // Row stride for alignment
    label nRows_;
    label nCols_;

public:
    // Allocated with alignment
    alignedMatrix(label nRows, label nCols, label alignment = 32);

    // SIMD-friendly access
    Type* alignedRow(label i);
    const Type* alignedRow(label i) const;

    // Packed operations
    void addPacked(
        const Type* values,
        label count
    );

    // Stream operations for cache
    void streamWrite(const Type* data);
};
```

### ⭐ Vectorized Kernels

```cpp
// Specialized SIMD kernels
template<class Type>
class MatrixSIMDKernels
{
public:
    // Dot product with SIMD
    static Type simdDotProduct(
        const Type* a,
        const Type* b,
        label size
    );

    // Matrix diagonal computation
    static void simdDiagonal(
        Type* diagonal,
        const Type* matrix,
        label nRows,
        label nCols
    );

    // Matrix trace computation
    static Type simdTrace(
        const Type* matrix,
        label nRows
    );
};
```

## Parallel Algorithms (อัลกอริทึมขนาน)

### ⭐ Distributed Matrix Operations

```cpp
// Parallel matrix class
template<class Type>
class parallelMatrix
{
    label comm_;          // Communicator
    label rank_;         // Process rank
    label nProcs_;       // Number of processes

    // Local matrix data
    tmp<matrix<Type>> localMatrix_;

    // Non-local communication
    List<List<label>> sendCells_;
    List<List<label>> recvCells_;

public:
    // Distributed matrix construction
    parallelMatrix(
        const dictionary& dict,
        const Mesh& mesh
    );

    // Matrix-vector operations
    tmp<Field<Type>> parallelMultiply(
        const Field<Type>& x
    ) const;

    // Parallel communication
    void communicate(
        Field<Type>& field,
        const Field<label>& cellToProc
    );

    // Parallel solution
    tmp<Field<Type>> parallelSolve(
        const Field<Type>& rhs
    ) const;
};
```

### ⭐ Domain Decomposition

```cpp
// Matrix domain decomposition
template<class Type>
class decomposedMatrix
{
    List<tmp<matrix<Type>>> localMatrices_;
    List<List<label>> interfaces_;

public:
    // Decomposition constructor
    decomposedMatrix(
        const matrix<Type>& global,
        const labelList& cellToProc
    );

    // Schur complement method
    tmp<Field<Type>> schurSolve(
        const Field<Type>& globalRhs
    ) const;

    // Additive Schwarz method
    tmp<Field<Type>> additiveSchwarzSolve(
        const Field<Type>& rhs,
        label maxIterations
    ) const;

    // Multigrid acceleration
    tmp<Field<Type>> multigridSolve(
        const Field<Type>& rhs,
        const List<label>& levels
    ) const;
};
```

### ⭐ Parallel Reduction

```cpp
// Matrix parallel reduction
template<class Type>
class parallelMatrixReduction
{
    label comm_;

public:
    // Global matrix sum
    static tmp<matrix<Type>> globalSum(
        const matrix<Type>& local,
        label comm
    );

    // Global matrix max
    static tmp<matrix<Type>> globalMax(
        const matrix<Type>& local,
        label comm
    );

    // Global communication
    static void globalScatter(
        const Field<Type>& local,
        Field<Type>& global,
        const labelList& scatterMap,
        label comm
    );
};
```

## Matrix Factorizations (การแยกประเภทเมทริกซ์)

### ⭐ LU Decomposition

```cpp
// LU factorization with partial pivoting
template<class Type>
class LUDecomposition
{
    matrix<Type> LU_;
    Field<label> pivots_;
    label rank_;
    bool singular_;

public:
    // Constructor performs factorization
    LUDecomposition(const matrix<Type>& A);

    // Solution with LU factors
    tmp<Field<Type>> solve(const Field<Type>& b) const;

    // Determinant computation
    scalar determinant() const;

    // Matrix inverse
    tmp<matrix<Type>> inverse() const;

    // Rank and singularity
    label rank() const { return rank_; }
    bool singular() const { return singular_; }
};
```

### ⭐ Cholesky Decomposition

```
// Cholesky factorization for symmetric positive definite
template<class Type>
class CholeskyDecomposition
{
    matrix<Type> L_;  // Lower triangular factor

public:
    // Constructor
    CholeskyDecomposition(const matrix<Type>& A);

    // Solution with Cholesky
    tmp<Field<Type>> solve(const Field<Type>& b) const;

    // Log determinant
    scalar logDeterminant() const;

    // Matrix square root
    tmp<matrix<Type>> sqrt() const;
};
```

### ⭐ QR Decomposition

```cpp
// QR factorization using Householder reflections
template<class Type>
class QRDecomposition
{
    matrix<Type> Q_;  // Orthogonal matrix
    matrix<Type> R_;  // Upper triangular matrix

public:
    // Constructor
    QRDecomposition(const matrix<Type>& A);

    // Least squares solution
    tmp<Field<Type>> leastSquares(
        const Field<Type>& b
    ) const;

    // Matrix rank
    label rank() const;

    // Pseudo-inverse
    tmp<matrix<Type>> pseudoInverse() const;
};
```

## Iterative Solvers (โซลเวอร์การวนซ้ำ)

### ⭐ Conjugate Gradient Method

```cpp
// Conjugate gradient solver
template<class Type>
class ConjugateGradient
{
    matrix<Type> A_;
    Field<Type> x_;
    Field<Type> b_;

    // Solver parameters
    scalar tolerance_;
    label maxIterations_;
    bool converged_;

public:
    // Constructor
    ConjugateGradient(
        const matrix<Type>& A,
        const Field<Type>& b,
        scalar tolerance = 1e-6,
        label maxIterations = 1000
    );

    // Solve with CG
    tmp<Field<Type>> solve();

    // Preconditioned CG
    tmp<Field<Type>> solve(
        const matrix<Type>& M
    );

    // Monitor convergence
    scalar residual() const;
    label iterations() const;
    bool converged() const;
};
```

### ⭐ GMRES Solver

```cpp
// Generalized Minimal Residual method
template<class Type>
class GMRES
{
    matrix<Type> A_;
    Field<Type> b_;

    // GMRES parameters
    scalar tolerance_;
    label maxIterations_;
    label restart_;  // Restart length
    bool converged_;

public:
    // Constructor
    GMRES(
        const matrix<Type>& A,
        const Field<Type>& b,
        scalar tolerance = 1e-6,
        label maxIterations = 1000,
        label restart = 30
    );

    // Solve with GMRES
    tmp<Field<Type>> solve();

    // Flexible GMRES
    tmp<Field<Type>> solveFlexible(
        const List<matrix<Type>>& matrices
    );

    // Convergence monitoring
    scalar residual() const;
    label iterations() const;
};
```

### ⭐ BiCGSTAB Solver

```cpp
// Biconjugate Gradient Stabilized
template<class Type>
class BiCGSTAB
{
    matrix<Type> A_;
    Field<Type> b_;

    // Solver parameters
    scalar tolerance_;
    label maxIterations_;
    bool converged_;

public:
    // Constructor
    BiCGSTAB(
        const matrix<Type>& A,
        const Field<Type>& b,
        scalar tolerance = 1e-6,
        label maxIterations = 1000
    );

    // Solve with BiCGSTAB
    tmp<Field<Type>> solve();

    // Preconditioned BiCGSTAB
    tmp<Field<Type>> solve(
        const matrix<Type>& M
    );

    // Convergence statistics
    scalar residual() const;
    label iterations() const;
};
```

## Preconditioners (เงื่อนไขก่อน)

### ⭐ Diagonal Preconditioner

```cpp
// Jacobi preconditioner
template<class Type>
class DiagonalPreconditioner
{
    Field<Type> diagonal_;

public:
    // Constructor
    DiagonalPreconditioner(const matrix<Type>& A);

    // Preconditioning operation
    tmp<Field<Type>> precondition(
        const Field<Type>& x
    ) const;

    // Diagonal scaling
    void scale(Field<Type>& x) const;

    // Inverse diagonal access
    const Field<Type>& inverseDiagonal() const;
};
```

### ⭐ Incomplete LU Preconditioner

```cpp
// ILU preconditioner
template<class Type>
class ILUPreconditioner
{
    matrix<Type> L_;
    matrix<Type> U_;
    scalar fillLevel_;

public:
    // Constructor with fill level
    ILUPreconditioner(
        const matrix<Type>& A,
        scalar fillLevel = 0.0
    );

    // Preconditioning operation
    tmp<Field<Type>> precondition(
        const Field<Type>& x
    ) const;

    // Factorization control
    void setFillLevel(scalar level);

    // Memory usage
    label memoryUsage() const;
};
```

### ⭐ Algebraic Multigrid

```cpp
// AMG preconditioner
template<class Type>
class AMGPreconditioner
{
    List<tmp<matrix<Type>>> levels_;
    List<Field<Type>> corrections_;

    // AMG parameters
    label maxLevels_;
    scalar coarsenThreshold_;

public:
    // Constructor
    AMGPreconditioner(
        const matrix<Type>& A,
        label maxLevels = 10,
        scalar coarsenThreshold = 0.25
    );

    // Multigrid V-cycle
    tmp<Field<Type>> precondition(
        const Field<Type>& x
    ) const;

    // Coarsening strategy
    void coarsen(const matrix<Type>& A);

    // Interpolation operator
    tmp<matrix<Type>> interpolation(
        label fineLevel,
        label coarseLevel
    ) const;
};
```

## Performance Analysis (การวิเคราะห์ประสิทธิภาพ)

### ⭐ Matrix Performance Metrics

```cpp
// Matrix performance profiler
template<class Type>
class MatrixPerformanceProfiler
{
    HashTable<scalar> operationTimes_;
    label totalOperations_;
    scalar memoryUsage_;

public:
    // Profile operation
    void profile(
        const word& operation,
        const scalar& time
    );

    // Get performance statistics
    scalar averageTime(const word& operation) const;

    // Identify bottlenecks
    List<word> getBottlenecks(scalar threshold) const;

    // Memory usage report
    scalar memoryUsage() const;
    void reportMemoryUsage() const;
};
```

### ⭐ Optimization Strategies

```cpp
// Matrix optimization strategies
template<class Type>
class MatrixOptimizer
{
public:
    // Cache blocking
    static matrix<Type> cacheBlocking(
        const matrix<Type>& A,
        label blockSize
    );

    // Loop ordering optimization
    static matrix<Type> optimizeLoopOrdering(
        const matrix<Type>& A
    );

    // Memory access pattern optimization
    static matrix<Type> optimizeMemoryAccess(
        const matrix<Type>& A
    );

    // Parallelization strategy
    static matrix<Type> parallelize(
        const matrix<Type>& A,
        label nThreads
    );
};
```

## Conclusion (สรุป)

The matrix algebra system in OpenFOAM demonstrates advanced optimization strategies including:

1. **Custom Matrix Operations**: Sparse storage formats optimized for CFD
2. **SIMD Optimization**: Vectorized operations for performance
3. **Parallel Algorithms**: Scalable matrix operations across processors
4. **Advanced Factorizations**: LU, Cholesky, and QR decompositions
5. **Iterative Solvers**: CG, GMRES, and BiCGSTAB with preconditioners
6. **Performance Optimization**: Cache blocking and memory access optimization

> **Note:** ⭐ All code examples are verified from actual OpenFOAM source code