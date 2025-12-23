# ลำดับชั้นและประเภทของตัวแก้ปัญหาเชิงเส้น (Linear Solvers)

![[multiscale_solver_gamg.png]]

> [!INFO] **ภาพรวม**
> Linear solvers ใน OpenFOAM แบ่งเป็นลำดับชั้นตามหลักการทำงาน การเลือก solver ที่เหมาะสมขึ้นอยู่กับประเภทของเมทริกซ์ ขนาดปัญหา และความต้องการความเร็วในการคำนวณ

---

## ⚙️ **กลไกหลัก: ลำดับชั้นของ Solver และการเลือกใช้งานขณะ Runtime**

### **ขั้นตอนที่ 1: Solver Base Class - "ชุดเครื่องมือของนักสืบ"**

สถาปัตยกรรมของ linear solver ใน OpenFOAM สร้างขึ้นบนระบบ **abstract base class** ที่สง่างาม ซึ่งมอบความสามารถในการเลือกใช้งานขณะ runtime

**🔧 หลักการทำงาน:**
- คลาส `lduMatrix::solver` ทำหน้าที่เป็น **รากฐาน** สำหรับ linear algebraic solvers ทั้งหมด
- ใช้ **factory pattern** สำหรับการเลือก solver แบบไดนามิก
- ผู้ใช้สามารถเปลี่ยน solvers โดยไม่ต้องคอมไพล์ใหม่

![[of_solver_hierarchy_factory.png]]

```cpp
// 🔧 กลไก: Abstract base class สำหรับ solvers ทั้งหมด
class lduMatrix::solver
{
protected:
    // ข้อมูลกรณี
    word fieldName_;           // Field ที่กำลังแก้
    const lduMatrix& matrix_;  // เมทริกซ์ (ข้อมูลเบาะแส)

    // ข้อมูลขอบเขต
    const FieldField<Field, scalar>& interfaceBouCoeffs_;
    const FieldField<Field, scalar>& interfaceIntCoeffs_;
    const lduInterfaceFieldPtrsList& interfaces_;

    // การควบคุม solver
    dictionary controlDict_;
    label maxIter_;     // ขั้นตอนการสอบสวนสูงสุด
    scalar tolerance_;  // ความต้องการความแม่นยำ
    scalar relTol_;    // ความแม่นยำสัมพันธ์

public:
    // Pure virtual solve method - นักสืบแต่ละคนนำเสนอแนวทางของตน
    virtual solverPerformance solve
    (
        scalarField& psi,        // ผลเฉลย (ที่ไม่ทราบค่า)
        const scalarField& source, // ด้านขวา
        const direction cmpt = 0   // Component สำหรับสมการเวกเตอร์
    ) const = 0;

    // Runtime type selection
    declareRunTimeSelectionTable
    (
        autoPtr,
        solver,
        symMatrix,  // สำหรับเมทริกซ์สมมาตร
        (/*...*/),
        (/*...*/)
    );

    declareRunTimeSelectionTable
    (
        autoPtr,
        solver,
        asymMatrix, // สำหรับเมทริกซ์ไม่สมมาตร
        (/*...*/),
        (/*...*/)
    );
};
```

**🏗️ โครงสร้างหลัก:**
- **Factory Pattern**: การสร้าง solver instance แบบไดนามิก
- **Runtime Selection**: เลือก solver ผ่าน `fvSolution` dictionary
- **Interface Handling**: รองรับการคำนวณแบบขนาน
- **Memory Management**: ใช้ reference-counted pointers (`autoPtr`)

### **ขั้นตอนที่ 2: Conjugate Gradient Solver - "นักสืบสมมาตรที่มีประสิทธิภาพ"**

**Preconditioned Conjugate Gradient (PCG)** solver เป็นอัลกอริทึมหลักสำหรับระบบ **symmetric positive definite** ใน OpenFOAM

**🔍 คุณสมบัติพิเศษ:**
- **เหมาะสมที่สุด** สำหรับการแก้สมการความดันในการจำลองการไหลแบบ incompressible
- **รับประกันการลู่เข้า** ในอย่างมาก $n$ iterations สำหรับระบบ $n \times n$
- **Minimizes energy norm**: $\|\mathbf{x} - \mathbf{x}^*\|_A$

**📐 หลักการคณิตศาสตร์:**

อัลกอริทึม PCG ทำงานโดยการ **ลดค่า energy norm** โดยที่ $\mathbf{A}$ เป็น coefficient matrix:

$$\|\mathbf{x} - \mathbf{x}^*\|_A = \sqrt{(\mathbf{x} - \mathbf{x}^*)^T \mathbf{A} (\mathbf{x} - \mathbf{x}^*)}$$

![[of_pcg_convergence_visual.png]]

```cpp
// 🔧 กลไก: PCG สำหรับเมทริกซ์ symmetric positive definite
class PCG : public lduMatrix::solver
{
public:
    // Runtime type information
    TypeName("PCG");

    solverPerformance solve
    (
        scalarField& psi,
        const scalarField& source,
        const direction cmpt
    ) const
    {
        // Initialize
        scalarField p(psi.size());      // ทิศทางการค้นหา
        scalarField r(psi.size());      // Residual
        scalarField wA(psi.size());     // Preconditioned residual

        // r = b - A·x
        matrix_.Amul(r, psi, interfaceBouCoeffs_, interfaces_, cmpt);
        r = source - r;

        // Precondition: wA = M⁻¹·r
        precon_->precondition(wA, r, cmpt);

        // Main CG iteration
        for (label iter = 0; iter < maxIter_; iter++)
        {
            // Matrix-vector: w = A·p
            scalarField w(p.size());
            matrix_.Amul(w, p, interfaceBouCoeffs_, interfaces_, cmpt);

            // α = (r·wA) / (p·w)
            scalar rDotwA = gSumProd(r, wA);
            scalar pDotw = gSumProd(p, w);
            scalar alpha = rDotwA / pDotw;

            // Update solution: x = x + αp
            psi += alpha * p;

            // Update residual: r = r - αw
            r -= alpha * w;

            // Check convergence
            scalar norm = gSumMag(r);
            if (norm < tolerance_)
                return solverPerformance(/*...*/);

            // Precondition: z = M⁻¹·r
            scalarField z(r.size());
            precon_->precondition(z, r, cmpt);

            // β = (r·z) / (r_old·wA_old)
            scalar rDotz = gSumProd(r, z);
            scalar beta = rDotz / rDotwA;

            // Update search direction: p = z + βp
            p = z + beta * p;
            wA = z;
        }
    }
};
```

**🔄 ขั้นตอนอัลกอริทึม CG:**

1. **Initialization**: คำนวณ residual เริ่มต้น $r_0 = b - Ax_0$
2. **Preconditioning**: ปรับปรุง residual ด้วย preconditioner
3. **Direction Update**: คำนวณทิศทางการค้นหาใหม่
4. **Step Length**: หาขนาดก้าวที่เหมาะสม $\alpha$
5. **Solution Update**: อัพเดทคำตอบ $x_{k+1} = x_k + \alpha p_k$
6. **Convergence Check**: ตรวจสอบความเที่ยงตรง

**📊 ประสิทธิภาพ:**
- **Guaranteed Convergence** ใน $n$ iterations สำหรับระบบ $n \times n$
- **Conjugate Directions**: $\mathbf{p}_i^T \mathbf{A} \mathbf{p}_j = 0$ สำหรับ $i \neq j$
- **Optimal Energy Norm Minimization** ในแต่ละ iteration

### **ขั้นตอนที่ 3: Preconditioners - "ผู้จัดระเบียบกรณี"**

**Preconditioners** เป็นส่วนประกอบสำคัญที่แปลงระบบเชิงเส้นต้นฉบับเป็นระบบที่มีคุณสมบัติการลู่เข้าที่ดีขึ้น

**🎯 วัตถุประสงค์:**
- **ปรับปรุง Condition Number** ของเมทริกซ์
- **เร่งการลู่เข้า** ของ iterative solvers
- **รักษาประสิทธิภาพ** การคำนวณ

**📋 Preconditioner Types:**

| Type | Matrix Type | Algorithm | Use Case |
|------|-------------|-----------|----------|
| **DIC** | Symmetric | Diagonal Incomplete Cholesky | Pressure Poisson |
| **DILU** | Asymmetric | Diagonal Incomplete LU | Momentum equations |
| **GAMG** | General | Geometric-Algebraic Multigrid | Large systems |
| **Diagonal** | General | Simple diagonal scaling | Quick preconditioning |

![[of_preconditioning_transform.png]]

```cpp
// 🔧 กลไก: DIC (Diagonal Incomplete Cholesky) สำหรับเมทริกซ์สมมาตร
class DICPreconditioner : public lduMatrix::preconditioner
{
private:
    // Precomputed reciprocal diagonal
    scalarField rD_;

public:
    void precondition
    (
        scalarField& wA,        // Output: M⁻¹·r
        const scalarField& rA,  // Input residual
        const direction cmpt
    ) const
    {
        // Forward sweep (lower triangle)
        scalarField w = rA;
        forAll(matrix_.lduAddr().lowerAddr(), facei)
        {
            label own = matrix_.lduAddr().lowerAddr()[facei];
            label nei = matrix_.lduAddr().upperAddr()[facei];

            w[nei] -= matrix_.lower()[facei] * w[own] * rD_[own];
        }

        // Diagonal scaling
        w *= rD_;

        // Backward sweep (upper triangle)
        forAllReverse(matrix_.lduAddr().upperAddr(), facei)
        {
            label own = matrix_.lduAddr().lowerAddr()[facei];
            label nei = matrix_.lduAddr().upperAddr()[facei];

            w[own] -= matrix_.upper()[facei] * w[nei] * rD_[nei];
        }

        wA = w;
    }
};
```

**📐 หลักการทางคณิตศาสตร์:**

DIC preconditioner ประมาณค่า **incomplete Cholesky factorization**:

$$\mathbf{M} \approx (\mathbf{D} + \mathbf{L})\mathbf{D}^{-1}(\mathbf{D} + \mathbf{U})$$

โดยที่:
- $\mathbf{L} + \mathbf{U} \approx \mathbf{A}$ (แทน off-diagonal elements)
- $\mathbf{D}$ = Diagonal matrix
- **Trade-off**: สมดุลระหว่างประสิทธิภาพการคำนวณและการเร่งการลู่เข้า

**🔄 ขั้นตอน DIC Algorithm:**

1. **Forward Sweep**: แก้ระบบล่าง $\mathbf{L}\mathbf{y} = \mathbf{r}$
2. **Diagonal Scaling**: คำนวณ $\mathbf{z} = \mathbf{D}^{-1}\mathbf{y}$
3. **Backward Sweep**: แก้ระบบบน $(\mathbf{D} + \mathbf{U})\mathbf{x} = \mathbf{z}$

**🎯 การเลือก Preconditioner:**

**สำหรับเมทริกซ์สมมาตร (Pressure Poisson):**
- **DIC**: ประสิทธิภาพสูงสุด
- **GAMG**: สำหรับระบบขนาดใหญ่
- **Diagonal**: เร็วแต่มีประสิทธิภาพต่ำ

**สำหรับเมทริกซ์ไม่สมมาตร (Momentum):**
- **DILU**: จัดการ convection terms ได้ดี
- **GAMG**: สำหรับปัญหาขนาดใหญ่
- **No Preconditioner**: สำหรับปัญหาง่ายๆ

```cpp
// 🔧 กลไก: DILU (Diagonal Incomplete LU) สำหรับเมทริกซ์ไม่สมมาตร
class DILUPreconditioner : public lduMatrix::preconditioner
{
    // Similar to DIC but stores both L and U factors
    // Handles asymmetric convection terms
};
```

**💡 ข้อดีของ Preconditioners:**
- **รักษา Sparsity**: เหมาะกับ CFD matrices
- **Low Memory Footprint**: เก็บเฉพาะ diagonal และ near-diagonal
- **Parallel Scalability**: ทำงานได้ดีกับ MPI
- **CFD-Optimized**: ออกแบบมาสำหรับ diagonal dominance matrices

---

## 🧠 **การทำงานของ GAMG (Multigrid)**

GAMG คือเทคโนโลยีขั้นสูงที่ทำให้ OpenFOAM โดดเด่น ด้วยหลักการ "แบ่งแยกและพิชิต" (Divide and Conquer)

### **ปรัชญา Multigrid**

Geometric Algebraic Multigrid (GAMG) solver เป็นหนึ่งในเครื่องมือพีชคณิตเชิงเส้นที่ซับซ้อนที่สุดของ OpenFOAM ซึ่งสะท้อนถึงหลักการทางคณิตศาสตร์ที่ว่าความถี่ความผิดพลาดที่แตกต่างกันนั้นถูกกำจัดได้ดีที่สุดในความละเอียดกริดที่แตกต่างกัน

แนวทางนี้จะแปลงงานที่ต้องการคำนวณมากในการแก้ระบบเชิงเส้นเบาบางขนาดใหญ่ให้เป็นลำดับชั้นของปัญหาที่หยาบขึ้นตามลำดับ โดยแต่ละระดับมุ่งเป้าไปที่คอมโพเนนต์ความถี่ความผิดพลาดเฉพาะ

### **รากฐานทางคณิตศาสตร์**

ข้อมูลเชิงลึกหลักของวิธีการ multigrid มาจากการสังเกตว่า **iterative solvers** เช่น Gauss-Seidel หรือ Jacobi สามารถกำจัดความผิดพลาดความถี่สูงได้อย่างมีประสิทธิภาพ แต่ติดขัดกับคอมโพเนนต์ความผิดพลาดความถี่ต่ำที่เรียบ

โดยการถ่ายโอนความผิดพลาดความถี่ต่ำเหล่านี้ไปยังกริดที่หยาบขึ้น ซึ่งในกริดเหล่านั้นพวกมันปรากฏเป็นความถี่สูงเมื่อเทียบกับระยะห่างกริด multigrid จึงบรรลุความซับซ้อนในการคำนวณที่เหมาะสมที่สุด

สำหรับระบบเชิงเส้น $A\mathbf{x} = \mathbf{b}$ ความผิดพลาด $\mathbf{e} = \mathbf{x} - \mathbf{x}^*$ จะเป็นไปตาม $A\mathbf{e} = \mathbf{r}$ โดยที่ $\mathbf{r} = \mathbf{b} - A\mathbf{x}$ คือ residual

อัลกอริทึม V-cycle ของ multigrid จะลดความผิดพลาดนี้อย่างเป็นระบบในหลายระดับความละเอียด:

$$\mathbf{e}^{(k+1)} = \mathbf{e}^{(k)} + P\left(A_c^{-1}R(\mathbf{b} - A\mathbf{e}^{(k)})\right)$$

**ตัวแปรในสมการ:**
- $\mathbf{e}^{(k)}$ = เวกเตอร์ความผิดพลาดที่ iteration ที่ k
- $P$ = ตัวดำเนินการ prolongation (แปลงจากกริดหยาบไปกริดละเอียด)
- $R$ = ตัวดำเนินการ restriction (แปลงจากกริดละเอียดไปกริดหยาบ)
- $A_c$ = ตัวดำเนินการกริดหยาบ (coarse grid operator)

```mermaid
flowchart TD
    F1[Fine Mesh: Solve & Smooth] --> C[Coarser Mesh: Aggregate]
    C --> CC[Coarsest Mesh: Direct Solve]
    CC --> C2[Coarser Mesh: Correct]
    C2 --> F2[Fine Mesh: Final Smooth]

    subgraph V_Cycle["V-Cycle"]
        F1
        C
        CC
        C2
        F2
    end

    style CC fill:#ffccbc,stroke:#e64a19
```

### **สถาปัตยกรรมการนำไปใช้งาน**

```cpp
// 🔧 MECHANISM: ลำดับชั้นของ GAMG solver
class GAMGSolver : public lduMatrix::solver
{
private:
    // ระดับกริดหยาบ
    PtrList<lduMatrix> coarseMatrices_;
    PtrList<FieldField<Field, scalar>> coarseBouCoeffs_;
    PtrList<FieldField<Field, scalar>> coarseIntCoeffs_;
    PtrList<lduInterfaceFieldPtrsList> coarseInterfaces_;

    // ตัวดำเนินการ Restriction และ prolongation
    PtrList<scalarField> restrictMatrices_;
    PtrList<scalarField> prolongMatrices_;

    // พารามิเตอร์ของ solver
    label nLevels_;
    label nPreSweeps_;
    label nPostSweeps_;
    label nCoarseSweeps_;

    // Smoother สำหรับกำจัดความผิดพลาดความถี่สูง
    autoPtr<lduMatrix::smoother> smoother_;

    // Direct solver สำหรับระดับที่หยาบที่สุด
    autoPtr<lduMatrix::solver> coarsestSolver_;

public:
    solverPerformance solve
    (
        scalarField& psi,
        const scalarField& source,
        const direction cmpt
    ) const
    {
        return Vcycle(0, psi, source, cmpt);
    }

private:
    solverPerformance Vcycle
    (
        const label level,
        scalarField& psi,
        const scalarField& source,
        const direction cmpt
    ) const
    {
        if (level == nLevels_ - 1)
        {
            return coarsestSolver_->solve(psi, source, cmpt);
        }

        // Pre-smoothing
        for (label sweep = 0; sweep < nPreSweeps_; sweep++)
        {
            smoother_->smooth(psi, source, cmpt);
        }

        // Compute residual
        scalarField res(source.size());
        matrix_.Amul(res, psi, interfaceBouCoeffs_, interfaces_, cmpt);
        res = source - res;

        // Restrict residual
        scalarField coarseRes = restrict(level, res);

        // Solve coarse grid problem
        scalarField coarseCorr(coarseRes.size(), 0.0);
        Vcycle(level + 1, coarseCorr, coarseRes, cmpt);

        // Prolong correction
        scalarField fineCorr = prolong(level, coarseCorr);

        // Apply correction
        psi += fineCorr;

        // Post-smoothing
        for (label sweep = 0; sweep < nPostSweeps_; sweep++)
        {
            smoother_->smooth(psi, source, cmpt);
        }

        return calculatePerformance(psi, source, cmpt);
    }
};
```

### **Algebraic vs. Geometric Multigrid**

| แนวทาง | หลักการ | ประโยชน์ |
|---------|----------|---------|
| **ด้านพีชคณิต** | ใช้สัมประสิทธิ์เมตริกซ์ในการกำหนดการจัดกลุ่มเซลล์ | รักษาคุณสมบัติทางคณิตศาสตร์ของระบบ |
| **ด้านเรขาคณิต** | ใช้ข้อมูลการเชื่อมต่อและรูปทรงของ mesh | รักษาคุณสมบัติทางกายภาพของโดเมน |

### **ตัวดำเนินการกริดหยาบของ Galerkin**

ตัวดำเนินการกริดหยาบ $A_c$ ถูกสร้างขึ้นโดยใช้แนวทางของ Galerkin:

$$A_c = RAP$$

**ตัวแปรในสมการ:**
- $A_c$ = ตัวดำเนินการกริดหยาบ
- $R$ = ตัวดำเนินการ restriction
- $A$ = ตัวดำเนินการกริดละเอียด
- $P$ = ตัวดำเนินการ prolongation

แนวทางนี้รักษาคุณสมบัติทางคณิตศาสตร์ของระบบดั้งเดิมโดยอัตโนมัติ ทำให้ **GAMG บรรลุความซับซ้อนที่เหมาะสมที่สุดในทางทฤษฎีคือ $\mathcal{O}(n)$ สำหรับปัญหา elliptic**

---

## 📊 **การเปรียบเทียบ Solver ทั้งหมด**

### **ตารางสรุปการเลือก Solver**

| ประเภทเมทริกซ์ | Solver ที่เหมาะสม | ความซับซ้อน | ข้อดี | ข้อเสีย |
|------------------|-------------------|--------------|--------|----------|
| **Symmetric Positive Definite** | PCG | $O(k \cdot n)$ | รับประกันการลู่เข้า | ต้องการ preconditioner |
| **Non-Symmetric** | PBiCGStab | $O(k \cdot n)$ | จัดการ convection ได้ | อาจไม่ลู่เข้า |
| **Large Systems** | GAMG | $O(n)$ | เร็วมาก | ตั้งค่าซับซ้อน |
| **Small Systems** | SmoothSolver | $O(k \cdot n)$ | เรียบง่าย | ช้าสำหรับระบบใหญ่ |

### **เกณฑ์การเลือก Solver**

> [!TIP] **คำแนะนำ**: สำหรับงานทั่วไป ใช้ **PCG/PBiCG** ก็เพียงพอ แต่สำหรับงานที่ขนาดใหญ่และต้องการความเร็วสูงสุด (โดยเฉพาะสมการความดัน) **GAMG** คือตัวเลือกอันดับหนึ่ง

**สำหรับสมการความดัน (Pressure Poisson):**
- เลือก **GAMG** เมื่อ: มีเซลล์ > 100,000 เซลล์
- เลือก **PCG + DIC** เมื่อ: เซลล์ < 100,000 เซลล์

**สำหรับสมการโมเมนตัม (Momentum):**
- เลือก **PBiCGStab + DILU** สำหรับ: convection-dominated flow
- เลือก **SmoothSolver** สำหรับ: ปัญหาง่ายๆ

### **การตั้งค่าใน `fvSolution`**

```cpp
// ตัวอย่างการตั้งค่า solver ใน system/fvSolution
solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-06;
        relTol          0.01;
        smoother        GaussSeidel;

        GAMG
        {
            nCellsInCoarseLevel 64;
            solver          GaussSeidel;
            tolerance       1e-06;
            relTol          0.01;
        }
    }

    U
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-05;
        relTol          0.1;
    }
}
```

---

## ⚠️ **อันตรายและวิธีแก้ไข**

### **ปัญหาที่ 1: ไม่ลู่เข้า (Non-Convergence)**

**สาเหตุ:**
- เมทริกซ์มี condition number สูง
- Preconditioner ไม่เหมาะสม
- Mesh quality แย่

**วิธีแก้ไข:**
```cpp
// 1. เพิ่มความแม่นยำ
tolerance       1e-08;
relTol          0.001;

// 2. เปลี่ยน preconditioner
preconditioner  GAMG;  // แทน Diagonal

// 3. เพิ่ม iterations
maxIter         1000;
```

### **ปัญหาที่ 2: ใช้หน่วยความจำมากเกินไป**

**สำหรับเมทริกซ์แบบ Sparse:**

> [!WARNING] **ข้อควรระวัง** อย่าใช้ Dense Matrix สำหรับปัญหา CFD!
>
> - เมทริกซ์ Dense: $O(n^2)$ memory → 8 TB สำหรับ 1M เซลล์ (เป็นไปไม่ได้)
> - เมทริกซ์ Sparse (LDU): $O(nnz)$ memory → 120 MB สำหรับ 1M เซลล์ (ใช้งานได้)

**วิธีแก้ไข:**
```cpp
// ❌ ผิด: ใช้ dense matrix
SquareMatrix<scalar> pressureMatrix(1000000);  // 8 TB!

// ✅ ถูก: ใช้ sparse matrix
lduMatrix pressureMatrix(mesh);  // 120 MB
```

### **ปัญหาที่ 3: ความไม่เสถียรทางตัวเลข**

**การวิเคราะห์ Condition Number:**

เลข condition ของเมทริกซ์: $\kappa(A) = \frac{\sigma_{\max}}{\sigma_{\min}}$

**มาตรฐาน:**
- **เมทริกซ์ดี**: $\kappa(A) < 10^3$
- **ปัญหา CFD**: $\kappa(A) \approx 10^{12}$

**เทคนิคการ Stabilization:**

```cpp
// 1. การทำ Preconditioning
GAMGPreconditioner precond(solverControls);

// 2. วิธีการ Relaxation
scalar alpha = 0.7;  // ตัวประกอบการผ่อนคลาย
fieldNew = (1-alpha)*fieldOld + alpha*fieldCorrection;

// 3. การทำ Regularization
scalar epsilon = 1e-12;
matrix.diagonal() += epsilon;
```

---

## 🎯 **สรุปและข้อแนะนำ**

### **แนวทางการเลือก Solver**

```mermaid
flowchart TD
    Start[เริ่มต้น: เลือก Solver] --> Q1{ขนาดระบบ}

    Q1 -->|เล็ก < 100K| Small[ใช้ PCG/PBiCGStab]
    Q1 -->|ใหญ่ > 100K| Q2{ประเภทเมทริกซ์}

    Q2 -->|Symmetric| Sym[ใช้ GAMG สำหรับความดัน]
    Q2 -->|Non-Symmetric| NonSym[ใช้ PBiCGStab + DILU]

    Small --> Check1[ตรวจสอบการลู่เข้า]
    Sym --> Check1
    NonSym --> Check1

    Check1 -->|ไม่ลู่เข้า| Fix[เปลี่ยน Preconditioner]
    Check1 -->|ลู่เข้า| Done[เสร็จสิ้น]

    Fix --> Check1
```

### **Best Practices**

1. **เริ่มต้นด้วย solver ง่ายๆ** (PCG, PBiCGStab)
2. **เปลี่ยนเป็น GAMG** เมื่อระบบใหญ่และต้องการความเร็ว
3. **ตรวจสอบ mesh quality** ก่อนเริ่มแก้ปัญหา
4. **ใช้ preconditioner ที่เหมาะสม** (DIC สำหรับสมมาตร, DILU สำหรับไม่สมมาตร)
5. **ตรวจสอบการลู่เข้า** ในทุก iteration
6. **บันทึก solver performance** เพื่อการวิเคราะห์ต่อไป

---

## 🔗 **อ้างอิงเพิ่มเติม**

- [[Sparse Matrix Storage|08_⚙️_Key_Mechanisms_Sparse_Matrix_Storage]]
- [[fvMatrix Architecture|13_⚙️_Key_Mechanisms_fvMatrix_Architecture]]
- [[GAMG Deep Dive|19_🧠_Under_the_Hood_Geometric_Algebraic_Multigrid_(GAMG)]]
- [[Matrix Assembly|14_🧠_Under_the_Hood_fvMatrix_Assembly_Patterns]]
- [[Common Pitfalls|05_⚠️_Common_Pitfalls_and_Solutions]]
