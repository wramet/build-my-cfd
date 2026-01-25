# Deep Dive: fvMatrix Class ใน OpenFOAM

**ตำแหน่งใน Roadmap:** Day 01 - Phase 1 Foundation Theory  
**ไฟล์ต้นฉบับ:** [`daily_learning/Phase_01_Foundation_Theory/2026-01-01.md:323-522`](daily_learning/Phase_01_Foundation_Theory/2026-01-01.md:323-522)

---

## 🔗 Prerequisites
- ความเข้าใจ Linear Algebra พื้นฐาน (Matrix, Vector)
- ความรู้เรื่อง Sparse Matrix Storage Formats
- ความเข้าใจ Finite Volume Discretization
- ความรู้เกี่ยวกับ Mesh Topology (Owner-Neighbour Addressing)

---

## 📝 Step-by-step Explanation

### 1. Architecture Overview: Dual Inheritance

`fvMatrix<Type>` ใน OpenFOAM ใช้ dual inheritance ที่ซับซ้อน:

```cpp
template<class Type>
class fvMatrix
:
    public refCount,          // สำหรับ reference counting memory management
    public lduMatrix          // สำหรับ sparse matrix storage ใน LDU format
{
private:
    // Reference ไปยัง field ที่กำลังถูก solve
    const GeometricField<Type, fvPatchField, volMesh>& psi_;
    
    // Matrix coefficients
    scalarField diag_;        // Diagonal coefficients (a_P)
    scalarField upper_;       // Upper triangle coefficients (a_N สำหรับ owner→neighbour)
    scalarField lower_;       // Lower triangle coefficients (a_N สำหรับ neighbour→owner)
    
    // Source vector
    Field<Type> source_;      // Right-hand side vector (b)
    
    // Boundary coefficients
    FieldField<Field, Type> internalCoeffs_;   // สำหรับ internal cells ที่ติด boundary
    FieldField<Field, Type> boundaryCoeffs_;   // สำหรับ boundary conditions
};
```

**ความสำคัญของแต่ละ inheritance:**
- **`refCount`**: จัดการ memory อัตโนมัติผ่าน reference counting
- **`lduMatrix`**: ให้ interface สำหรับ linear algebra operations บน LDU format

### 2. LDU (Lower-Diagonal-Upper) Storage Format

LDU format เป็น sparse matrix storage ที่เหมาะกับ unstructured meshes:

```
Matrix A ในรูปเต็ม:
[ a_P1  a_N12  0     0    ]
[ a_N21 a_P2   a_N23 0    ]
[ 0     a_N32  a_P3  a_N34]
[ 0     0      a_N43 a_P4 ]

ใน LDU format:
diag_  = [a_P1, a_P2, a_P3, a_P4]
upper_ = [a_N12, a_N23, a_N34]  // สำหรับ faces: 1-2, 2-3, 3-4
lower_ = [a_N21, a_N32, a_N43]  // สำหรับ faces: 2-1, 3-2, 4-3
```

**การแมปจาก Mesh Topology:**
- ทุก internal face สร้าง entry หนึ่งคู่ใน `upper_` และ `lower_`
- `owner()` cell → contribution ไปยัง `upper_`
- `neighbour()` cell → contribution ไปยัง `lower_`
- Boundary faces ไม่สร้าง off-diagonal entries แต่เพิ่ม contribution ไปยัง `diag_` และ `source_`

### 3. Matrix Assembly Process

กระบวนการประกอบ matrix จากสมการ PDEs:

```cpp
// ตัวอย่าง: Assembly ของ diffusion term
void assembleDiffusionTerm(
    const volScalarField& phi,
    const volScalarField& gamma
) {
    const fvMesh& mesh = phi.mesh();
    const labelUList& owner = mesh.owner();
    const labelUList& neighbour = mesh.neighbour();
    const vectorField& Sf = mesh.Sf();
    const scalarField& magSf = mesh.magSf();
    
    // Loop ผ่านทุก internal face
    forAll(owner, faceI) {
        label own = owner[faceI];
        label nei = neighbour[faceI];
        
        // คำนวณ diffusion coefficient
        scalar gammaFace = interpolate(gamma, faceI);
        vector delta = mesh.C()[nei] - mesh.C()[own];
        scalar magDelta = mag(delta);
        vector n = delta/magDelta;
        
        // คำนวณ face normal component
        scalar Sfdn = Sf[faceI] & n;
        
        // คำนวณ coefficient
        scalar coeff = gammaFace * magSf[faceI] / magDelta;
        
        // เพิ่มไปยัง matrix
        diag_[own] += coeff;
        diag_[nei] += coeff;
        upper_[faceI] -= coeff;
        lower_[faceI] -= coeff;
    }
}
```

**ขั้นตอนการ Assembly:**
1. **Initialization**: จอง memory สำหรับ `diag_`, `upper_`, `lower_`, `source_`
2. **Face Loop**: Loop ผ่านทุก internal face เพื่อ assemble off-diagonal terms
3. **Boundary Processing**: ประมวลผล boundary contributions
4. **Source Assembly**: รวม source terms ต่างๆ

### 4. Boundary Conditions Handling

Boundary conditions ใน `fvMatrix` ถูกจัดการผ่านสองระบบ:

```cpp
class fvMatrix {
private:
    // Boundary coefficients storage
    FieldField<Field, Type> internalCoeffs_;
    FieldField<Field, Type> boundaryCoeffs_;
    
public:
    // Method สำหรับจัดการ boundary conditions
    void setValues(const labelUList& cells, const Field<Type>& values);
    void setReference(label cellI, Type value);
    
    // Boundary condition application
    void addBoundaryDiag(scalarField& diag, const direction cmpt) const;
    void addBoundarySource(Field<Type>& source, const bool couples=true) const;
};
```

**ประเภทของ Boundary Conditions ใน Matrix Context:**
1. **Dirichlet (fixedValue)**: เพิ่ม large number ไปยัง `diag_` และปรับ `source_`
2. **Neumann (zeroGradient)**: ไม่เพิ่ม contribution ไปยัง matrix
3. **Mixed**: ผสมระหว่าง Dirichlet และ Neumann
4. **Cyclic**: สร้าง off-diagonal connections ระหว่าง periodic boundaries

### 5. Linearized Source Terms สำหรับ Phase Change

ตามที่ระบุใน Day 01 Section 2.2.4 เราต้องการ linearized source terms:

```cpp
class LinearizedSource {
public:
    enum LinearizationType {
        EXPLICIT,    // เพิ่มเข้า source เท่านั้น: S = S_u
        IMPLICIT,    // เพิ่มเข้า diagonal และ source: S = S_p*phi + S_u
        MIXED        // ผสมทั้งสองแบบ: S = α*S_p*phi + (1-α)*S_u
    };
    
private:
    scalarField Sp_;      // Implicit coefficient
    scalarField Su_;      // Explicit source
    
public:
    void applyTo(fvScalarMatrix& matrix) const {
        if (Sp_.size() > 0) {
            matrix.diag() += Sp_;      // เพิ่ม implicit part ไปยัง diagonal
        }
        if (Su_.size() > 0) {
            matrix.source() += Su_;    // เพิ่ม explicit part ไปยัง source
        }
    }
    
    // ตัวอย่าง: Linearization ของ expansion term
    static LinearizedSource createExpansionSource(
        const volScalarField& mDot,
        const dimensionedScalar& rho_v,
        const dimensionedScalar& rho_l,
        LinearizationType type = MIXED
    ) {
        scalarField expansion = mDot * (1.0/rho_v.value() - 1.0/rho_l.value());
        
        LinearizedSource src;
        switch (type) {
            case EXPLICIT:
                src.Su_ = expansion;
                break;
            case IMPLICIT:
                src.Sp_ = expansion / mDot;  // Simplified
                src.Su_ = expansion - src.Sp_ * mDot;
                break;
            case MIXED:
                scalar alpha = 0.5;  // 50% implicit
                src.Sp_ = alpha * expansion / mDot;
                src.Su_ = (1.0 - alpha) * expansion;
                break;
        }
        return src;
    }
};
```

**เหตุผลที่ต้อง Linearize:**
1. **Numerical Stability**: Implicit treatment เพิ่ม diagonal dominance
2. **Convergence Rate**: Linearized sources converge เร็วกว่า
3. **Physical Accuracy**: รักษา physical bounds ของตัวแปร

### 6. Matrix Solution Process

กระบวนการแก้สมการ $A\phi = b$:

```cpp
template<class Type>
SolverPerformance<Type> fvMatrix<Type>::solve(const dictionary& solverControls) {
    // 1. Create solver based on controls
    autoPtr<lduMatrix::solver> solver =
        lduMatrix::solver::New
        (
            this->psi().name(),
            *this,
            solverControls
        );
    
    // 2. Apply boundary conditions
    this->addBoundaryDiag(diag_, 0);
    this->addBoundarySource(source_, false);
    
    // 3. Solve the system
    SolverPerformance<Type> perf = solver->solve
    (
        this->psi().internalField(),
        source_
    );
    
    // 4. Update boundary values
    this->psi().correctBoundaryConditions();
    
    return perf;
}
```

**ประเภทของ Linear Solvers:**
1. **PCG (Preconditioned Conjugate Gradient)**: สำหรับ symmetric matrices (pressure)
2. **PBiCGStab (Preconditioned Bi-Conjugate Gradient Stabilized)**: สำหรับ asymmetric matrices (momentum)
3. **GAMG (Geometric Algebraic Multigrid)**: สำหรับ large-scale problems
4. **SmoothSolver**: ด้วย relaxation (DIC/DILU)

### 7. Performance Optimization Techniques

`fvMatrix` ใช้เทคนิคหลายอย่างเพื่อเพิ่มประสิทธิภาพ:

```cpp
// 1. Matrix-Vector Multiplication ที่ optimize
void fvMatrix::Amul
(
    scalarField& Apsi,
    const tmp<scalarField>& tpsi
) const {
    const scalarField& psi = tpsi();
    
    // Initialize with diagonal contribution
    Apsi = diag_ * psi;
    
    // Add lower triangle contribution
    forAll(lower_, faceI) {
        Apsi[owner_[faceI]] += lower_[faceI] * psi[neighbour_[faceI]];
    }
    
    // Add upper triangle contribution
    forAll(upper_, faceI) {
        Apsi[neighbour_[faceI]] += upper_[faceI] * psi[owner_[faceI]];
    }
}

// 2. Cache-friendly memory access
// - diag_, source_: contiguous memory
// - owner_, neighbour_: pre-sorted สำหรับ better cache locality
// - face addressing: grouped โดย patch type
```

**Optimization Strategies:**
1. **Contiguous Memory**: ใช้ `scalarField` สำหรับ contiguous storage
2. **Cache Locality**: Sort cells และ faces เพื่อเพิ่ม cache hits
3. **Vectorization**: ใช้ SIMD instructions สำหรับ scalar operations
4. **Parallelization**: Face-based decomposition สำหรับ parallel processing

---

## 💡 Key Insights

1. **LDU Format Efficiency**: เหมาะกับ unstructured meshes เพราะใช้ mesh topology โดยตรง
2. **Boundary Condition Integration**: BCs ถูก incorporate ไปใน matrix อย่าง seamless
3. **Template Flexibility**: ใช้ได้กับทั้ง scalar, vector, และ tensor equations
4. **Performance-Centric Design**: Optimized สำหรับ large-scale CFD problems

---

## 🧪 Quick Check

**คำถาม:** ทำไม `fvMatrix` ต้องเก็บทั้ง `upper_` และ `lower_` coefficients แยกกัน แม้ว่ามักจะมีค่าเท่ากันสำหรับ symmetric operators?

**คำตอบ:** มีเหตุผลสำคัญ 3 ข้อ:
1. **Asymmetric Operators**: สำหรับ convective terms หรือ turbulence models, `upper_` และ `lower_` อาจมีค่าไม่เท่ากัน
2. **Numerical Stability**: การเก็บแยกกันช่วยรักษา matrix properties สำหรับ iterative solvers
3. **Flexibility**: รองรับทั้ง symmetric และ asymmetric discretization schemes
4. **Performance**: การเข้าถึง memory แบบ contiguous สำหรับแต่ละ array มีประสิทธิภาพสูงกว่า

---

## 📚 Related Topics

- **Day 05:** Mesh Topology และ Owner-Neighbour Addressing
- **Day 07:** Linear Algebra และ LDU Matrix Format
- **Day 08:** Iterative Solvers (PCG, PBiCGStab)
- **Day 09:** Pressure-Velocity Coupling ที่ใช้ fvMatrix
- **Day 11:** Phase Change Source Terms ใน fvMatrix

---

## ⚠️ Common Pitfalls และ Solutions

### Pitfall 1: Incorrect Matrix Assembly
```cpp
// ❌ ผิด: ลืมเพิ่ม contribution ไปยังทั้ง owner และ neighbour
diag_[own] += coeff;
upper_[faceI] = -coeff;  // ลืม lower_ และ diag_[nei]

// ✅ ถูก: เพิ่ม contribution ไปยังทั้งสองเซลล์
diag_[own] += coeff;
diag_[nei] += coeff;
upper_[faceI] = -coeff;
lower_[faceI] = -coeff;
```

### Pitfall 2: Boundary Conditions Not Applied
```cpp
// ❌ ผิด: Solve โดยไม่ apply boundary conditions
solver->solve(psi.internalField(), source_);

// ✅ ถูก: Apply boundary conditions ก่อน solve
this->addBoundaryDiag(diag_, 0);
this->addBoundarySource(source_, false);
solver->solve(psi.internalField(), source_);
psi.correctBoundaryConditions();
```

### Pitfall 3: Memory Allocation Issues
```cpp
// ❌ ผิด: ไม่จอง memory ก่อน assembly
// diag_, upper_, lower_ ยังไม่มีขนาดที่ถูกต้อง

// ✅ ถูก: จอง memory ตาม mesh size
diag_.setSize(mesh.nCells(), 0.0);
upper_.setSize(mesh.nInternalFaces(), 0.0);
lower_.setSize(mesh.nInternalFaces(), 0.0);
source_.setSize(mesh.nCells(), 0.0);
```

### Pitfall 4: Incorrect Source Term Linearization
```cpp
// ❌ ผิด: เพิ่ม nonlinear source ไปยัง source_ โดยตรง
source_ += mDot * (1.0/rho_v - 1.0/rho_l);  // อาจทำให้ diverge

// ✅ ถูก: Linearize source term ก่อน
LinearizedSource expansionSrc = LinearizedSource::createExpansionSource(
    mDot, rho_v, rho_l, LinearizedSource::IMPLICIT
);
expansionSrc.applyTo(*this);
```

---

## 🎯 Engineering Impact

การเข้าใจ `fvMatrix` อย่างลึกซึ้งช่วยให้:
1. **Implement New Equations**: เพิ่มสมการใหม่ๆ ลงใน solver ได้ถูกต้อง
2. **Optimize Performance**: เข้าใจ memory layout และ access patterns
3. **Debug Convergence Issues**: วินิจฉัยปัญหา convergence ได้อย่างมีประสิทธิภาพ
4. **Customize Solvers**: ปรับแต่ง linear solvers และ preconditioners
5. **Handle Complex Physics**: จัดการ coupled equations และ nonlinear terms

---

## 🔬 Advanced Topics

### 1. Matrix-Free Methods
สำหรับ problems ขนาดใหญ่มากๆ อาจใช้ matrix-free approaches:
```cpp
// Matrix-vector product โดยไม่เก็บ matrix อย่างชัดเจน
void matrixFreeMul(scalarField& Apsi, const scalarField& psi) {
    // คำนวณ contributions จาก PDE operators โดยตรง
    Apsi = fvm::laplacian(gamma, psi) + fvm::div(phi, psi);
}
```

### 2. Block-Coupled Systems
สำหรับ strongly coupled equations (เช่น multiphase flow):
```cpp
// Block matrix สำหรับ coupled U-p system
BlockFvMatrix<Vector2> UPEqn
(
    fvm::ddt(U) + fvm::div(phi, U) - fvm::laplacian(nu, U) == -fvc::grad(p),
    fvc::div(U) == 0
);
```

### 3. Adaptive Matrix Storage
ปรับปรุง memory usage ตาม runtime requirements:
```cpp
// Dynamic switching ระหว่าง storage formats
if (isSymmetric(operator)) {
    storeSymmetricFormat();  // เก็บเฉพาะ upper_ + diag_
} else {
    storeFullFormat();       // เก็บทั้ง upper_ และ lower_
}
```

---

## Source Types and Linearization (ประเภทของแหล่งกำเนิดและการทำไลเนียไรเซชัน)

ในปัญหาการเปลี่ยนสถานะ (phase change) การจัดการ source terms เป็นสิ่งสำคัญอย่างยิ่ง Source terms สามารถแบ่งได้เป็นหลายประเภทตามลักษณะทางฟิสิกส์และวิธีการทางตัวเลข:

### 1. Classification of Source Terms

```cpp
enum SourceType {
    EXPLICIT_SOURCE,      // เพิ่มเข้า source vector เท่านั้น: S = S_u
    IMPLICIT_SOURCE,      // เพิ่มเข้า diagonal matrix: S = S_p * φ
    MIXED_SOURCE,         // ผสมทั้งสองแบบ: S = S_p * φ + S_u
    NONLINEAR_SOURCE,     // Source ที่ขึ้นกับ φ อย่างไม่เป็นเชิงเส้น
    COUPLED_SOURCE        // Source ที่ขึ้นกับ field อื่นๆ
};
```

### 2. Explicit vs Implicit Treatment

**Explicit Sources:**
- เพิ่มเข้า `source_` vector โดยตรง
- ใช้สำหรับ source terms ที่มีขนาดเล็กหรือไม่สำคัญต่อ stability
- ตัวอย่าง: Constant source terms, weak buoyancy

```cpp
// Explicit source addition
void addExplicitSource(
    fvMatrix<scalar>& matrix,
    const volScalarField& Su
) {
    matrix.source() += Su.internalField();
}
```

**Implicit Sources:**
- เพิ่มเข้า `diag_` ของ matrix
- ใช้สำหรับ source terms ที่มีขนาดใหญ่หรือสำคัญต่อ stability
- ตัวอย่าง: Phase change expansion term, strong damping terms

```cpp
// Implicit source addition
void addImplicitSource(
    fvMatrix<scalar>& matrix,
    const volScalarField& Sp
) {
    matrix.diag() += Sp.internalField();
}
```

### 3. Linearization Techniques

สำหรับ nonlinear source terms $S(\phi)$ ต้องทำ linearization:

```cpp
class SourceLinearizer {
public:
    // Taylor series linearization: S(φ) ≈ S(φ₀) + (∂S/∂φ)|φ₀ * (φ - φ₀)
    void linearizeTaylorSeries(
        const volScalarField& phi,
        const volScalarField& phi0,  // Reference value
        volScalarField& Sp,          // Implicit coefficient
        volScalarField& Su           // Explicit source
    ) const {
        // คำนวณ derivative ∂S/∂φ
        volScalarField dSdPhi = calculateDerivative(phi, phi0);
        
        // Linearized form: S ≈ Sp*φ + Su
        // โดยที่ Sp = ∂S/∂φ, Su = S(φ₀) - (∂S/∂φ)*φ₀
        Sp = dSdPhi;
        Su = calculateSource(phi0) - dSdPhi * phi0;
    }
    
    // Newton-Raphson linearization สำหรับ strongly nonlinear terms
    void linearizeNewtonRaphson(
        const volScalarField& phi,
        const volScalarField& phi0,
        volScalarField& Sp,
        volScalarField& Su,
        scalar relaxation = 0.5
    ) const {
        // Iterative Newton-Raphson
        volScalarField residual = calculateSource(phi) - (Sp * phi + Su);
        volScalarField jacobian = calculateJacobian(phi);
        
        // Update coefficients
        Sp += relaxation * jacobian;
        Su += relaxation * (residual - jacobian * phi);
    }
    
private:
    volScalarField calculateDerivative(
        const volScalarField& phi,
        const volScalarField& phi0
    ) const {
        // Finite difference approximation
        const scalar eps = 1e-6;
        volScalarField phiPlus = phi0 + eps;
        volScalarField phiMinus = phi0 - eps;
        
        return (calculateSource(phiPlus) - calculateSource(phiMinus)) / (2.0 * eps);
    }
};
```

### 4. Phase Change Source Linearization

สำหรับ expansion term จาก phase change:

```cpp
class PhaseChangeSourceLinearizer {
public:
    // Linearization ของ expansion term: S = mDot * (1/ρ_v - 1/ρ_l)
    void linearizeExpansionTerm(
        const volScalarField& mDot,
        const volScalarField& phi,      // Field being solved (e.g., pressure)
        const dimensionedScalar& rho_v,
        const dimensionedScalar& rho_l,
        volScalarField& Sp,
        volScalarField& Su
    ) const {
        // คำนวณ expansion coefficient
        volScalarField expansionCoeff = mDot * (1.0/rho_v - 1.0/rho_l);
        
        // ตรวจสอบว่า mDot ขึ้นกับ φ หรือไม่
        // ถ้า mDot ขึ้นกับ φ (เช่น ผ่าน temperature) ต้องคำนวณ derivative
        if (mDotDependsOnPhi_) {
            // ∂(mDot)/∂φ * (1/ρ_v - 1/ρ_l)
            volScalarField dMdotdPhi = calculateDMdotDPhi(phi, mDot);
            Sp = dMdotdPhi * (1.0/rho_v - 1.0/rho_l);
            Su = expansionCoeff - Sp * phi;
        } else {
            // mDot ไม่ขึ้นกับ φ → explicit source
            Sp = dimensionedScalar("zero", dimless/dimTime, 0.0);
            Su = expansionCoeff;
        }
    }
    
    // Linearization ของ latent heat source: S = -mDot * h_fg
    void linearizeLatentHeatSource(
        const volScalarField& mDot,
        const dimensionedScalar& h_fg,
        const volScalarField& T,        // Temperature field
        volScalarField& Sp,
        volScalarField& Su
    ) const {
        // สำหรับ Lee model: mDot = C * α * ρ * (T - T_sat)/T_sat
        // ดังนั้น ∂(mDot)/∂T = C * α * ρ / T_sat
        
        volScalarField dMdotdT = calculateDMdotDT(mDot, T);
        
        // Linearized form: S ≈ Sp * T + Su
        Sp = -dMdotdT * h_fg;
        Su = -mDot * h_fg - Sp * T;
    }
};
```

### 5. Stability Considerations

**Diagonal Dominance:**
- Implicit sources ช่วยเพิ่ม diagonal dominance
- สำหรับ source term ขนาดใหญ่ ต้องใช้ implicit treatment เพื่อรักษา stability

```cpp
// ตรวจสอบ diagonal dominance
bool checkDiagonalDominance(
    const fvMatrix<scalar>& matrix,
    scalar threshold = 1e-6
) const {
    const scalarField& diag = matrix.diag();
    const scalarField& upper = matrix.upper();
    const scalarField& lower = matrix.lower();
    
    forAll(diag, cellI) {
        scalar sumOffDiag = 0.0;
        // รวม off-diagonal contributions (simplified)
        // ในความเป็นจริงต้องคำนวณจาก mesh connectivity
        
        if (mag(diag[cellI]) < sumOffDiag + threshold) {
            return false;  // ไม่เป็น diagonally dominant
        }
    }
    return true;
}
```

**Under-relaxation สำหรับ Strong Sources:**
```cpp
void applyUnderRelaxation(
    fvMatrix<scalar>& matrix,
    const volScalarField& phi,
    scalar relaxationFactor
) {
    // A_relaxed = A/α + (1-α)/α * diag(φ_old)
    // b_relaxed = b/α + (1-α)/α * diag(φ_old) * φ_old
    
    scalarField& diag = matrix.diag();
    scalarField& source = matrix.source();
    
    diag /= relaxationFactor;
    source /= relaxationFactor;
    
    // เพิ่ม contribution จาก old value
    source += (1.0 - relaxationFactor)/relaxationFactor * diag * phi.oldTime().internalField();
}
```

---

## Jacobian Contribution (ส่วนร่วมของจาโคเบียน)

สำหรับ strongly coupled problems หรือเมื่อใช้ Newton-type solvers การคำนวณ Jacobian contribution เป็นสิ่งสำคัญ:

### 1. Jacobian Matrix Structure

Jacobian matrix $J_{ij} = \partial R_i / \partial \phi_j$ โดยที่ $R$ คือ residual vector:

```cpp
class JacobianCalculator {
public:
    // Calculate Jacobian contribution จาก source term
    void addJacobianContribution(
        fvMatrix<scalar>& matrix,
        const volScalarField& phi,
        const volScalarField& source,
        const word& fieldName
    ) const {
        // ∂S/∂φ สำหรับแต่ละ cell
        volScalarField dSdPhi = calculateSourceDerivative(phi, source);
        
        // เพิ่มไปยัง diagonal ของ matrix
        matrix.diag() += dSdPhi.internalField();
        
        // ถ้า source ขึ้นกับ neighboring cells ต้องเพิ่ม off-diagonal contributions
        if (hasNonLocalDependence_) {
            addNonLocalJacobian(matrix, phi, source);
        }
    }
    
private:
    // Finite difference สำหรับคำนวณ derivative
    volScalarField calculateSourceDerivative(
        const volScalarField& phi,
        const volScalarField& source
    ) const {
        const scalar eps = 1e-8;
        volScalarField dSdPhi(phi.mesh(), dimensionedScalar(dimless, 0.0));
        
        forAll(phi, cellI) {
            scalar phiVal = phi[cellI];
            scalar sourceVal = source[cellI];
            
            // Perturb phi
            scalar phiPerturbed = phiVal + eps;
            
            // คำนวณ source ที่ perturbed value (simplified)
            scalar sourcePerturbed = calculateSourceAtValue(phiPerturbed, cellI);
            
            // Finite difference
            dSdPhi[cellI] = (sourcePerturbed - sourceVal) / eps;
        }
        
        return dSdPhi;
    }
};
```

### 2. Cross-Coupling Jacobian Terms

สำหรับ coupled equations (เช่น U-p coupling, T-α coupling):

```cpp
class CrossCouplingJacobian {
public:
    // Jacobian สำหรับ coupled U-p system
    void addMomentumPressureJacobian(
        fvMatrix<vector>& UEqn,
        const volScalarField& p,
        const volVectorField& U
    ) const {
        // ∂(∇p)/∂U = 0 (pressure gradient ไม่ขึ้นกับ U โดยตรง)
        // แต่ใน Rhie-Chow interpolation มี implicit coupling
        
        // ∂(∇p)/∂p ถูก handle ใน pressure equation
        // ที่นี่เราต้องเพิ่ม contribution จาก convective term
    }
    
    // Jacobian สำหรับ coupled T-α system (phase change)
    void addTemperatureVolumeFractionJacobian(
        fvMatrix<scalar>& TEqn,
        fvMatrix<scalar>& alphaEqn,
        const volScalarField& T,
        const volScalarField& alpha
    ) const {
        // จาก Lee model: mDot = C * α * ρ * (T - T_sat)/T_sat
        
        // ∂(mDot)/∂T สำหรับ energy equation
        volScalarField dMdotdT = C_ * alpha * rho_ / T_sat_;
        TEqn.diag() += dMdotdT.internalField() * h_fg_;  // Latent heat contribution
        
        // ∂(mDot)/∂α สำหรับ volume fraction equation
        volScalarField dMdotdAlpha = C_ * rho_ * (T - T_sat_) / T_sat_;
        alphaEqn.diag() += dMdotdAlpha.internalField();
    }
};
```

### 3. Analytical Jacobian สำหรับ Common Terms

**Expansion Term Jacobian:**
```cpp
// S = mDot * (1/ρ_v - 1/ρ_l)
// ถ้า mDot = f(T) จาก Lee model
// แล้ว ∂S/∂T = (1/ρ_v - 1/ρ_l) * ∂(mDot)/∂T

volScalarField calculateExpansionJacobian(
    const volScalarField& T,
    const volScalarField& alpha,
    const dimensionedScalar& rho_v,
    const dimensionedScalar& rho_l
) const {
    // จาก Lee model: mDot = C * α * ρ * (T - T_sat)/T_sat
    // ดังนั้น ∂(mDot)/∂T = C * α * ρ / T_sat
    
    volScalarField dMdotdT = C_ * alpha * rho_mix_ / T_sat_;
    return dMdotdT * (1.0/rho_v - 1.0/rho_l);
}
```

**Latent Heat Jacobian:**
```cpp
// S = -mDot * h_fg
// ∂S/∂T = -h_fg * ∂(mDot)/∂T

volScalarField calculateLatentHeatJacobian(
    const volScalarField& T,
    const volScalarField& alpha,
    const dimensionedScalar& h_fg
) const {
    volScalarField dMdotdT = C_ * alpha * rho_mix_ / T_sat_;
    return -h_fg * dMdotdT;
}
```

### 4. Jacobian Update Strategies

**Full Newton:** อัพเดท Jacobian ทุก iteration
```cpp
void updateJacobianFullNewton(
    fvMatrix<scalar>& matrix,
    const volScalarField& phi,
    int iteration
) {
    // คำนวณ Jacobian ใหม่ทุก iteration
    if (iteration % 1 == 0) {
        recalculateJacobian(matrix, phi);
    }
}
```

**Modified Newton:** อัพเดท Jacobian เป็นระยะ
```cpp
void updateJacobianModifiedNewton(
    fvMatrix<scalar>& matrix,
    const volScalarField& phi,
    int iteration,
    int updateFrequency = 5
) {
    // อัพเดท Jacobian ทุกๆ updateFrequency iterations
    if (iteration % updateFrequency == 0) {
        recalculateJacobian(matrix, phi);
    }
}
```

**Quasi-Newton (BFGS):** อัพเดท Jacobian โดยใช้ secant method
```cpp
void updateJacobianBFGS(
    fvMatrix<scalar>& matrix,
    const volScalarField& phi,
    const volScalarField& phiOld,
    const volScalarField& residual,
    const volScalarField& residualOld
) {
    // BFGS update: J_new = J_old + ΔyΔyᵀ/ΔyᵀΔs - J_oldΔsΔsᵀJ_old/ΔsᵀJ_oldΔs
    // โดยที่ Δy = residual_new - residual_old, Δs = φ_new - φ_old
    
    volScalarField deltaY = residual - residualOld;
    volScalarField deltaS = phi - phiOld;
    
    // Simplified BFGS update สำหรับ diagonal Jacobian
    scalarField& diag = matrix.diag();
    
    forAll(diag, cellI) {
        scalar deltaY_val = deltaY[cellI];
        scalar deltaS_val = deltaS[cellI];
        scalar J_old = diag[cellI];
        
        if (mag(deltaS_val) > 1e-12) {
            // Rank-1 update
            diag[cellI] += (deltaY_val * deltaY_val) / (deltaY_val * deltaS_val)
                         - (J_old * deltaS_val * deltaS_val * J_old) / (deltaS_val * J_old * deltaS_val);
        }
    }
}
```

### 5. Implementation ใน Solver

```cpp
void EvaporatorSolver::assembleWithJacobian() {
    // Assemble momentum equation
    fvVectorMatrix UEqn = assembleMomentumEquation();
    
    // Assemble pressure equation with expansion term
    fvScalarMatrix pEqn = assemblePressureEquation();
    
    // เพิ่ม Jacobian contribution สำหรับ coupled terms
    if (useFullNewton_) {
        // เพิ่ม cross-coupling Jacobian terms
        crossCouplingJacobian_.addMomentumPressureJacobian(UEqn, p_, U_);
        crossCouplingJacobian_.addTemperatureVolumeFractionJacobian(TEqn_, alphaEqn_, T_, alpha_);
        
        // เพิ่ม source term Jacobians
        jacobianCalculator_.addJacobianContribution(pEqn, p_, expansionSource_, "p");
        jacobianCalculator_.addJacobianContribution(TEqn_, T_, latentHeatSource_, "T");
    }
    
    // Solve coupled system
    if (useCoupledSolve_) {
        // Block-coupled solve
        solveCoupledSystem(UEqn, pEqn, TEqn_, alphaEqn_);
    } else {
        // Segregated solve
        solveSegregated(UEqn, pEqn, TEqn_, alphaEqn_);
    }
}
```

### 6. Performance Considerations

**Jacobian Sparsity Pattern:**
- Jacobian matrix มี sparse structure เหมือนกับ original matrix
- สามารถ reuse sparsity pattern จาก discretization operators

**Jacobian Reuse:**
- สำหรับ slowly varying problems สามารถ reuse Jacobian หลาย iterations
- ตรวจสอบ convergence rate เพื่อตัดสินใจเมื่อไหร่ควร update Jacobian

**Parallel Jacobian Assembly:**
- Jacobian contributions สามารถคำนวณแบบ parallel ได้
- ใช้ domain decomposition สำหรับ distributed memory systems

---

**สรุป:** `fvMatrix` class เป็นหัวใจของ numerical solution process ใน OpenFOAM การออกแบบที่ซับซ้อนแต่มีประสิทธิภาพนี้ทำให้สามารถแก้สมการ PDEs ขนาดใหญ่บน unstructured meshes ได้อย่างมีประสิทธิภาพ
