# MODULE_05 Section 04: Matrix Systems (LDU Sparse Matrices) / ระบบเมทริกซ์ (เมทริกซ์เบาบางแบบ LDU)

## 1. OpenFOAM lduMatrix Structure / โครงสร้าง lduMatrix ใน OpenFOAM

### 1.1 LDU Format Overview / ภาพรวมรูปแบบ LDU

In OpenFOAM, sparse matrices are stored in **LDU (Lower-Diagonal-Upper)** format to minimize memory usage for finite volume discretizations. This format exploits the structured nature of FVM meshes where each cell connects only to its neighbors.

ใน OpenFOAM เมทริกซ์เบาบางถูกเก็บในรูปแบบ **LDU (ล่าง-แนวทแยง-บน)** เพื่อลดการใช้หน่วยความจำสำหรับการกระจายเชิงปริมาตรจำกัด รูปแบบนี้ใช้ประโยชน์จากโครงสร้างที่มีระเบียบของเมช FVM ที่แต่ละเซลล์เชื่อมต่อเฉพาะกับเซลล์ข้างเคียงเท่านั้น

**Mathematical Representation / การแสดงทางคณิตศาสตร์:**
```latex
[A] = [L] + [D] + [U]
```
where:
- $[D]$ = diagonal coefficients (stored as `scalarField`)
- $[L]$ = lower triangle coefficients (stored as `scalarField`)
- $[U]$ = upper triangle coefficients (stored as `scalarField`)

### 1.2 Addressing Arrays / อาร์เรย์การอ้างอิงตำแหน่ง

```cpp
// OpenFOAM lduMatrix addressing
class lduMatrix
{
    // Diagonal coefficients
    scalarField *diagPtr_;

    // Upper triangle coefficients
    scalarField *upperPtr_;

    // Lower triangle coefficients
    scalarField *lowerPtr_;

    // Addressing: owner-neighbor structure
    const lduAddressing& lduAddr_;

    // Upper triangle addressing
    const labelList& upperAddr_;

    // Lower triangle addressing
    const labelList& lowerAddr_;

    // Owner starts addressing
    const labelList& ownerStartAddr_;

    // Losort addressing for symmetric matrices
    const labelList& losortAddr_;
};
```

**Key addressing arrays:**
- `upperAddr_`: Neighbor cell index for each face (upper triangle)
- `lowerAddr_`: Owner cell index for each face (lower triangle)
- `ownerStartAddr_`: Start index in face list for each cell

## 2. Matrix Assembly from FVM Discretization / การประกอบเมทริกซ์จากการกระจาย FVM

### 2.1 Finite Volume Discretization / การกระจายเชิงปริมาตรจำกัด

For a generic transport equation:
```latex
\frac{\partial (\rho \phi)}{\partial t} + \nabla \cdot (\rho \mathbf{u} \phi) - \nabla \cdot (\Gamma \nabla \phi) = S_\phi
```

After discretization using FVM:
```latex
a_P \phi_P + \sum_{N} a_N \phi_N = b_P
```

### 2.2 Matrix Assembly Code / โค้ดการประกอบเมทริกซ์

```cpp
// OpenFOAM: Assembling pressure equation matrix
void assemblePressureMatrix
(
    fvScalarMatrix& pEqn,
    const volScalarField& rAU,
    const surfaceScalarField& phi
)
{
    const fvMesh& mesh = pEqn.mesh();

    // Get references to matrix components
    scalarField& diag = pEqn.diag();
    scalarField& upper = pEqn.upper();
    scalarField& lower = pEqn.lower();

    const labelUList& owner = mesh.owner();
    const labelUList& neighbour = mesh.neighbour();

    // Reset matrix
    diag = 0.0;
    upper = 0.0;
    lower = 0.0;

    // Assemble face contributions
    forAll(owner, facei)
    {
        label own = owner[facei];
        label nei = neighbour[facei];

        scalar flux = phi[facei];
        scalar rAUf = rAU[facei];

        // Convective contribution
        diag[own] += max(flux, 0.0);
        diag[nei] += max(-flux, 0.0);

        // Diffusive contribution (pressure Laplacian)
        scalar coeff = rAUf * mesh.magSf()[facei] / mesh.magDelta()[facei];

        diag[own] += coeff;
        diag[nei] += coeff;
        upper[facei] = -coeff;
        lower[facei] = -coeff;
    }

    // Add boundary contributions
    forAll(pEqn.internalCoeffs(), patchi)
    {
        const fvPatch& patch = mesh.boundary()[patchi];
        const labelList& faceCells = patch.faceCells();

        forAll(faceCells, i)
        {
            label celli = faceCells[i];
            diag[celli] += pEqn.internalCoeffs()[patchi][i];
        }
    }
}
```

### 2.3 Modern C++ Comparison (Eigen) / การเปรียบเทียบกับ C++ รุ่นใหม่ (Eigen)

```cpp
// Modern C++ with Eigen: Sparse matrix assembly
#include <Eigen/Sparse>
#include <vector>

struct Triplet {
    int row, col;
    double value;
};

Eigen::SparseMatrix<double> assemblePressureMatrixEigen(
    const Mesh& mesh,
    const std::vector<double>& rAU,
    const std::vector<double>& phi)
{
    int nCells = mesh.nCells();
    int nFaces = mesh.nInternalFaces();

    std::vector<Triplet> coefficients;
    coefficients.reserve(3 * nFaces + nCells);

    // Pre-allocate for diagonal and off-diagonals
    for (int celli = 0; celli < nCells; celli++) {
        coefficients.push_back({celli, celli, 0.0});
    }

    // Assemble face contributions
    for (int facei = 0; facei < nFaces; facei++) {
        int own = mesh.owner()[facei];
        int nei = mesh.neighbour()[facei];

        double flux = phi[facei];
        double rAUf = rAU[facei];

        // Update diagonals
        auto updateDiagonal = [&](int cell, double value) {
            for (auto& coeff : coefficients) {
                if (coeff.row == cell && coeff.col == cell) {
                    coeff.value += value;
                    break;
                }
            }
        };

        updateDiagonal(own, std::max(flux, 0.0));
        updateDiagonal(nei, std::max(-flux, 0.0));

        // Diffusive contribution
        double coeff = rAUf * mesh.magSf()[facei] / mesh.magDelta()[facei];

        updateDiagonal(own, coeff);
        updateDiagonal(nei, coeff);

        // Off-diagonals
        coefficients.push_back({own, nei, -coeff});
        coefficients.push_back({nei, own, -coeff});
    }

    // Build sparse matrix
    Eigen::SparseMatrix<double> A(nCells, nCells);
    A.setFromTriplets(coefficients.begin(), coefficients.end());

    return A;
}
```

## 3. Modern Sparse Matrix Formats / รูปแบบเมทริกซ์เบาบางสมัยใหม่

### 3.1 CSR Format (Compressed Sparse Row) / รูปแบบ CSR

```cpp
// CSR format structure
struct CSRMatrix {
    std::vector<double> values;    // Non-zero values
    std::vector<int> col_indices;  // Column indices
    std::vector<int> row_pointers; // Row start pointers

    // Convert LDU to CSR
    static CSRMatrix fromLDU(
        const scalarField& diag,
        const scalarField& upper,
        const scalarField& lower,
        const labelList& owner,
        const labelList& neighbour)
    {
        int nCells = diag.size();
        int nFaces = owner.size();

        CSRMatrix csr;
        csr.row_pointers.resize(nCells + 1, 0);

        // Count non-zeros per row
        std::vector<int> nnz_per_row(nCells, 1); // Start with diagonal

        for (int facei = 0; facei < nFaces; facei++) {
            int own = owner[facei];
            int nei = neighbour[facei];
            nnz_per_row[own]++;
            nnz_per_row[nei]++;
        }

        // Build row pointers
        csr.row_pointers[0] = 0;
        for (int i = 0; i < nCells; i++) {
            csr.row_pointers[i + 1] = csr.row_pointers[i] + nnz_per_row[i];
        }

        int nnz = csr.row_pointers[nCells];
        csr.values.resize(nnz);
        csr.col_indices.resize(nnz);

        // Fill matrix (simplified)
        // ... implementation details

        return csr;
    }
};
```

### 3.2 Performance Comparison / การเปรียบเทียบประสิทธิภาพ

| Format | Memory | Access Pattern | Best For |
|--------|--------|----------------|----------|
| **LDU** | Low | Face-based | FVM, structured meshes |
| **CSR** | Medium | Row-based | General sparse, CG solvers |
| **CSC** | Medium | Column-based | Transpose operations |
| **COO** | High | Unordered | Easy assembly |

## 4. R410A Evaporator Matrices / เมทริกซ์สำหรับเครื่องระเหย R410A

### 4.1 Pressure Equation Matrix / เมทริกซ์สมการความดัน

For two-phase R410A flow, the pressure equation is derived from continuity:

```latex
\nabla \cdot \left( \frac{\rho}{\alpha} \nabla p \right) = \nabla \cdot (\rho \mathbf{u}^*)
```

**Matrix characteristics:**
- Symmetric positive definite (SPD)
- Diagonal dominant
- Suitable for Conjugate Gradient solver

```cpp
// R410A Pressure matrix assembly
void assembleR410APressureMatrix(
    fvScalarMatrix& pEqn,
    const volScalarField& alpha,  // Void fraction
    const volScalarField& rho,    // Density
    const volScalarField& rAU)
{
    const fvMesh& mesh = pEqn.mesh();

    scalarField& diag = pEqn.diag();
    scalarField& upper = pEqn.upper();
    scalarField& lower = pEqn.lower();

    const labelList& owner = mesh.owner();
    const labelList& neighbour = mesh.neighbour();

    // Two-phase density interpolation
    surfaceScalarField rhof = fvc::interpolate(rho);
    surfaceScalarField alphaf = fvc::interpolate(alpha);

    forAll(owner, facei)
    {
        label own = owner[facei];
        label nei = neighbour[facei];

        // Two-phase coefficient
        scalar coeff = rAU[facei] * rhof[facei] / alphaf[facei]
                     * mesh.magSf()[facei] / mesh.magDelta()[facei];

        diag[own] += coeff;
        diag[nei] += coeff;
        upper[facei] = -coeff;
        lower[facei] = -coeff;
    }
}
```

### 4.2 Momentum Equation Matrix / เมทริกซ์สมการโมเมนตัม

Momentum equation for R410A two-phase flow:

```latex
\frac{\partial (\rho \mathbf{u})}{\partial t} + \nabla \cdot (\rho \mathbf{u} \mathbf{u}) - \nabla \cdot (\mu \nabla \mathbf{u}) = -\nabla p + \mathbf{S}_m
```

**Matrix characteristics:**
- Asymmetric (due to convection)
- May not be diagonal dominant
- Requires BiCGStab or GMRES solver

```cpp
// R410A Momentum matrix (U component)
void assembleR410AMomentumMatrix(
    fvVectorMatrix& UEqn,
    const volScalarField& rho,
    const volScalarField& mu,
    const surfaceScalarField& phi)
{
    const fvMesh& mesh = UEqn.mesh();

    // Discretize convection - upwind differencing
    fvm::div(phi, UEqn.psi());

    // Discretize diffusion
    fvm::laplacian(mu, UEqn.psi());

    // Add two-phase source terms
    const volScalarField& alpha = mesh.lookupObject<volScalarField>("alpha");

    // Interphase momentum transfer
    volScalarField K("K", 0.75 * rho * Cd * mag(UEqn.psi()) / bubbleDiameter);
    UEqn += K * UEqn.psi();
}
```

### 4.3 Void Fraction Equation Matrix / เมทริกซ์สมการเศษส่วนปริมาตร

Drift-flux model for void fraction:

```latex
\frac{\partial (\alpha \rho_g)}{\partial t} + \nabla \cdot (\alpha \rho_g \mathbf{u}_g) = \Gamma
```

```cpp
// Void fraction equation matrix
void assembleVoidFractionMatrix(
    fvScalarMatrix& alphaEqn,
    const volScalarField& rhoG,
    const surfaceScalarField& phiG,
    const volScalarField& Gamma)  // Mass transfer rate
{
    // Transient term
    fvm::ddt(rhoG, alphaEqn.psi());

    // Convection term - use MULES for boundedness
    fv::MULES::explicitSolve
    (
        rhoG,
        alphaEqn.psi(),
        phiG,
        Gamma
    );

    // Compressibility term for R410A
    const volScalarField& p = alphaEqn.mesh().lookupObject<volScalarField>("p");
    const volScalarField& psi = alphaEqn.mesh().lookupObject<volScalarField>("psi");

    alphaEqn += fvm::Sp(psi * rhoG * fvc::ddt(p), alphaEqn.psi());
}
```

## 5. Solver Selection for R410A Systems / การเลือกตัวแก้สมการสำหรับระบบ R410A

### 5.1 Solver Selection Criteria / เกณฑ์การเลือกตัวแก้สมการ

```cpp
// Solver selection based on matrix properties
template<class Type>
auto selectSolver(const fvMatrix<Type>& matrix)
{
    const word& fieldName = matrix.psi().name();

    if (fieldName == "p")  // Pressure equation
    {
        // Symmetric positive definite
        return Foam::CG<Type>::New(fieldName, matrix);
    }
    else if (fieldName == "U")  // Momentum equation
    {
        // Asymmetric due to convection
        return Foam::BiCGStab<Type>::New(fieldName, matrix);
    }
    else if (fieldName == "alpha")  // Void fraction
    {
        // Diagonal dominant, may have source terms
        return Foam::GAMG<Type>::New(fieldName, matrix);
    }
    else
    {
        // Default for scalar equations
        return Foam::PCG<Type>::New(fieldName, matrix);
    }
}
```

### 5.2 Preconditioner Selection / การเลือกตัวปรับเงื่อนไข

```cpp
// Preconditioner setup for R410A equations
void setupR410ASolvers(const fvMesh& mesh)
{
    // Pressure solver - Diagonal preconditioner
    dictionary pSolverDict;
    pSolverDict.add("solver", "PCG");
    pSolverDict.add("preconditioner", "DIC");
    pSolverDict.add("tolerance", 1e-6);
    pSolverDict.add("relTol", 0.1);

    // Momentum solver - Diagonal preconditioner
    dictionary USolverDict;
    USolverDict.add("solver", "PBiCGStab");
    USolverDict.add("preconditioner", "DILU");
    USolverDict.add("tolerance", 1e-5);
    USolverDict.add("relTol", 0.1);

    // Void fraction solver - Geometric Algebraic Multigrid
    dictionary alphaSolverDict;
    alphaSolverDict.add("solver", "GAMG");
    alphaSolverDict.add("smoother", "GaussSeidel");
    alphaSolverDict.add("nPreSweeps", 0);
    alphaSolverDict.add("nPostSweeps", 2);
    alphaSolverDict.add("cacheAgglomeration", true);
}
```

### 5.3 Performance Optimization / การปรับปรุงประสิทธิภาพ

```cpp
// Optimized matrix assembly for R410A
class OptimizedR410AMatrix
{
private:
    // Block-structured storage for coupled equations
    BlockLduMatrix<scalar> blockMatrix_;

    // Reuse pattern for transient simulations
    bool patternInitialized_;
    List<label> nonZeroPattern_;

public:
    // Pattern-reusing assembly
    void assembleWithPattern(
        const fvMesh& mesh,
        const volScalarField& alpha,
        const volScalarField& rho)
    {
        if (!patternInitialized_)
        {
            // First time: discover pattern
            discoverNonZeroPattern(mesh);
            patternInitialized_ = true;
        }

        // Reuse pattern for faster assembly
        assembleUsingPattern(mesh, alpha, rho);
    }

    // Matrix-free operator for frequent solves
    class MatrixFreeOperator
    {
    public:
        // Compute A*x without forming A explicitly
        void operator()(
            const scalarField& x,
            scalarField& Ax) const
        {
            // Implement matrix-vector product directly
            // from discretization coefficients
            forAll(mesh_.owner(), facei)
            {
                label own = mesh_.owner()[facei];
                label nei = mesh_.neighbour()[facei];

                scalar coeff = coeffs_[facei];
                Ax[own] += coeff * (x[own] - x[nei]);
                Ax[nei] += coeff * (x[nei] - x[own]);
            }
        }
    };
};
```

### 5.4 Hybrid Approach: OpenFOAM + Modern Libraries / วิธีการแบบผสม

```cpp
// Hybrid: OpenFOAM assembly + Eigen solve
void hybridSolve(
    fvScalarMatrix& foamMatrix,
    volScalarField& phi)
{
    // 1. Assemble using OpenFOAM (optimized for FVM)
    foamMatrix.assemble();

    // 2. Convert to Eigen format
    Eigen::SparseMatrix<double> A = convertToEigen(foamMatrix);
    Eigen::VectorXd b = convertToEigen(foamMatrix.source());
    Eigen::VectorXd x = convertToEigen(phi.internalField());

    // 3. Solve using Eigen's optimized solvers
    Eigen::ConjugateGradient<
        Eigen::SparseMatrix<double>,
        Eigen::Lower|Eigen::Upper> cg;

    cg.compute(A);
    x = cg.solveWithGuess(b, x);

    // 4. Copy back to OpenFOAM field
    convertFromEigen(x, phi.internalField());
}

// Conversion utility
Eigen::SparseMatrix<double> convertToEigen(
    const fvScalarMatrix& foamMatrix)
{
    const lduMatrix& lduMat = foamMatrix;
    const label nCells = lduMat.diag().size();

    std::vector<Eigen::Triplet<double>> triplets;
    triplets.reserve(3 * nCells);  // Estimate

    // Add diagonal
    for (label i = 0; i < nCells; i++)
    {
        triplets.push_back({i, i, lduMat.diag()[i]});
    }

    // Add off-diagonals
    const labelList& upperAddr = foamMatrix.mesh().lduAddr().upperAddr();
    const labelList& lowerAddr = foamMatrix.mesh().lduAddr().lowerAddr();

    for (label facei = 0; facei < upperAddr.size(); facei++)
    {
        label i = lowerAddr[facei];
        label j = upperAddr[facei];

        triplets.push_back({i, j, lduMat.upper()[facei]});
        triplets.push_back({j, i, lduMat.lower()[facei]});
    }

    Eigen::SparseMatrix<double> A(nCells, nCells);
    A.setFromTriplets(triplets.begin(), triplets.end());

    return A;
}
```

## Summary / สรุป

The LDU matrix format in OpenFOAM is highly optimized for finite volume discretizations on unstructured meshes. For R410A evaporator simulations:

1. **Pressure equation**: Symmetric matrix → Use CG with DIC preconditioner
2. **Momentum equation**: Asymmetric matrix → Use BiCGStab with DILU preconditioner
3. **Void fraction equation**: Diagonal dominant → Use GAMG for faster convergence
4. **Modern approaches**: Consider hybrid OpenFOAM+Eigen for complex systems

รูปแบบเมทริกซ์ LDU ใน OpenFOAM ถูกปรับให้เหมาะสมสูงสุดสำหรับการกระจายเชิงปริมาตรจำกัดบนเมชที่ไม่เป็นระเบียบ สำหรับการจำลองเครื่องระเหย R410A:

1. **สมการความดัน**: เมทริกซ์สมมาตร → ใช้ CG กับตัวปรับเงื่อนไข DIC
2. **สมการโมเมนตัม**: เมทริกซ์ไม่สมมาตร → ใช้ BiCGStab กับตัวปรับเงื่อนไข DILU
3. **สมการเศษส่วนปริมาตร**: มีแนวทแยงเด่น → ใช้ GAMG สำหรับการลู่เข้าที่เร็วขึ้น
4. **วิธีการสมัยใหม่**: พิจารณาใช้วิธีผสม OpenFOAM+Eigen สำหรับระบบที่ซับซ้อน
