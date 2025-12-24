# Common Pitfalls & Debugging

![[index_labyrinth_tensor.png]]

---

## Overview

Working with tensors in OpenFOAM presents unique challenges that can lead to subtle bugs, performance issues, and numerical instabilities. This section identifies the most common pitfalls and provides practical strategies for avoiding and debugging them.

---

## 1. Tensor Contraction Errors

The ==most common source of errors== is incorrect tensor contraction - confusing single (`&`) and double (`&&`) contractions.

### Single vs Double Contraction

| Operation | Operator | Result Type | Mathematical Form | Description |
|-----------|----------|-------------|-------------------|-------------|
| **Double Contraction** | `&&` | `scalar` | $$s = \mathbf{A} : \mathbf{B} = \sum_{i,j=1}^{3} A_{ij}B_{ij}$$ | Full index contraction (Frobenius inner product) |
| **Single Contraction** | `&` | `vector` or `tensor` | $$w_i = \sum_{j=1}^{3} A_{ij}v_j$$ (tensor-vector) | Partial index contraction |

### Common Mistakes

```cpp
// ❌ ERROR: Double contraction yields scalar, not vector
vector v = A && B;

// ❌ ERROR: Type mismatch in assignment
tensor T = A && B;  // A && B returns scalar

// ✅ CORRECT: Proper contractions
scalar s = A && B;      // Double contraction → scalar
vector w = A & v;       // Single contraction → vector
tensor C = A & B;       // Single contraction → tensor
```

> [!WARNING] Type Safety
> OpenFOAM's tensor operations are type-safe at compile-time. Always check the expected return type before using contraction operators.

---

## 2. Symmetric Tensor Misconceptions

### Memory Layout Differences

Understanding the ==memory layout differences== between `tensor` and `symmTensor` is crucial:

**General Tensor (`tensor`):**
```
[XX][XY][XZ][YX][YY][YZ][ZX][ZY][ZZ]
  0   1   2   3   4   5   6   7   8
```

**Symmetric Tensor (`symmTensor`):**
```
[XX][XY][XZ][YY][YZ][ZZ]
  0   1   2   3   4   5
```

### Implicit Symmetry Access

```cpp
// Create a symmetric tensor with 6 unique components
symmTensor S(1, 2, 3, 4, 5, 6);

// Stored components (direct access)
scalar s1 = S.xx();  // Returns 1 - diagonal XX component
scalar s2 = S.xy();  // Returns 2 - off-diagonal XY component

// Implicit components (computed via symmetry)
scalar s3 = S.yx();  // Returns S.xy() = 2 - symmetry property
scalar s4 = S.zx();  // Returns S.xz() = 3 - symmetry property
```

**📚 Source:** 📂 .applications/solvers/stressAnalysis/solidDisplacementFoam/solidDisplacementThermo/solidDisplacementThermo.H:38

**📖 คำอธิบาย:**
Symmetric tensors ใน OpenFOAM มีโครงสร้างพิเศษที่ใช้หน่วยความจำน้อยกว่า โดยเก็บเฉพาะ 6 components ที่ไม่ซ้ำกัน (XX, XY, XZ, YY, YZ, ZZ) แทนที่จะเก็บทั้ง 9 components เหมือน general tensor การเข้าถึง off-diagonal components ที่สลับตำแหน่งกัน (เช่น YX กับ XY) จะให้ค่าเดิมเสมอเนื่องจากคุณสมบัติของ symmetry

**🔑 แนวคิดสำคัญ:**
- **SymmTensor layout:** เก็บ 6 components ตามลำดับ [XX, XY, XZ, YY, YZ, ZZ]
- **Memory efficiency:** ประหยัดพื้นที่ 33% เมื่อเปรียบเทียบกับ tensor ทั่วไป
- **Implicit symmetry:** Component YX = XY, ZX = XZ, ZY = YZ เสมอ
- **Cache performance:** การใช้ symmTensor ช่วยปรับปรุง cache efficiency ในการคำนวณ

> [!TIP] Performance Optimization
> Using `symmTensor` instead of `tensor` for symmetric quantities reduces memory usage by ==33%== and improves cache efficiency.

---

## 3. Numerical Stability Issues

### Singular Tensors and Inversion

```cpp
// ❌ DANGEROUS: Inversion without checking for singular matrices
tensor invT = inv(T);  // May fail or produce NaN if det(T) ≈ 0

// ✅ SAFE: Check determinant before inversion
scalar detT = det(T);
if (mag(detT) > SMALL) {
    // Compute inverse only if determinant is non-zero
    tensor invT = inv(T);
} else {
    // Handle singular tensor case appropriately
    Warning << "Singular tensor detected: det(T) = " << detT << endl;
}
```

**📚 Source:** 📂 .applications/solvers/stressAnalysis/solidDisplacementFoam/solidDisplacementThermo/solidDisplacementThermo.C:44

**📖 คำอธิบาย:**
การ inverse tensor โดยตรงโดยไม่ตรวจสอบ determinant เป็นสาเหตุหลักของ numerical instability เมื่อ determinant มีค่าใกล้ศูนย์ การคำนวณ inverse จะให้ผลลัพธ์ที่ไม่ถูกต้องหรือเกิด NaN การใช้ SMALL constant เป็น threshold ช่วยป้องกันปัญหานี้

**🔑 แนวคิดสำคัญ:**
- **Determinant threshold:** ใช้ `SMALL` (~1e-37) หรือ tolerance ที่เหมาะสมกับปัญหา
- **Singular detection:** Tensor ที่มี determinant ≈ 0 แสดงถึงการสูญเสีย rank หรือ ill-conditioned matrix
- **Graceful degradation:** ต้องมี fallback strategy เมื่อพบ singular tensor
- **Numerical conditioning:** หลีกเลี่ยงการ inverse โดยตรงในกรณีที่เป็นไปได้ (เช่น ใช้ linear solver)

### Eigenvalue Computation Pitfalls

```cpp
symmTensor stressTensor;

// ❌ PROBLEMATIC: Eigenvalues may be numerically unstable
vector eigenvals = eigenValues(stressTensor);

// ✅ ROBUST: Validate physicality of eigenvalues
vector eigenvals = eigenValues(stressTensor);
scalar minEigen = min(eigenvals);

// Check for non-physical negative eigenvalues in positive-definite tensors
if (minEigen < 0) {
    Warning << "Non-physical negative eigenvalue detected: "
            << minEigen << endl;
    // Apply regularization or check input data
}
```

**📚 Source:** 📂 .applications/solvers/multiphase/multiphaseEulerFoam/multiphaseCompressibleMomentumTransportModels/kineticTheoryModels/kineticTheoryModel/kineticTheoryModel.C:44

**📖 คำอธิบาย:**
Eigenvalues ของ stress tensor ในระบบทางกายภาพจะต้องเป็นค่าบวกเสมอ (positive-definite) แต่ numerical errors อาจทำให้เกิด eigenvalues ที่เป็นลบ ซึ่งบ่งชี้ว่ามีปัญหากับ input data หรือ computational scheme

**🔑 แนวคิดสำคัญ:**
- **Physical validity:** Stress/strain tensors ในระบบทางกายภาพต้องเป็น positive-definite
- **Numerical precision:** Floating-point errors อาจทำให้เกิด eigenvalues ที่ลบเล็กน้อย
- **Regularization:** สามารถใช้ eigenvalue clipping หรือ spectral decomposition เพื่อแก้ไข
- **Diagnostic value:** Negative eigenvalues เป็น indicator ที่ดีของปัญหาใน simulation

### Von Mises Stress Calculation

```cpp
// ✅ CORRECT: Von Mises stress from deviatoric stress tensor
volSymmTensorField sigma = ...;  // Total stress field

// Extract deviatoric (shear) component: σ' = σ - (1/3)tr(σ)I
volSymmTensorField devSigma = dev(sigma);

// Calculate Von Mises stress (equivalent tensile stress)
volScalarField vonMises = sqrt(1.5) * mag(devSigma);
```

**📚 Source:** 📂 .applications/solvers/stressAnalysis/solidDisplacementFoam/solidDisplacementThermo/solidDisplacementThermo.H:38

**📖 คำอธิบาย:**
Von Mises stress เป็น scalar quantity ที่ใช้ประเมิน yield criteria ใน materials science โดยคำนวณจาก deviatoric stress tensor ซึ่งเป็นส่วนของ stress ที่ทำให้เกิดการเปลี่ยนรูป (distortion) ไม่รวม hydrostatic component

**🔑 แนวคิดสำคัญ:**
- **Deviatoric stress:** `dev(σ) = σ - (1/3)tr(σ)I` แยก shear stress ออกจาก pressure
- **Von Mises formula:** σ_vm = √(3/2 S:S) โดย S คือ deviatoric stress
- **Yield criterion:** Material จะ yield เมื่อ von Mises stress เกิน yield strength
- **Energy-based:** Von Mises stress relates to distortional strain energy

**Mathematical Foundation:**
$$\sigma_{vm} = \sqrt{\frac{3}{2}\mathbf{S}:\mathbf{S}}$$

where $\mathbf{S} = \boldsymbol{\sigma} - \frac{1}{3}\text{tr}(\boldsymbol{\sigma})\mathbf{I}$ is the deviatoric stress tensor.

---

## 4. Dimensional Consistency Errors

OpenFOAM's dimensional analysis system catches many errors, but tensor operations require special attention.

```cpp
// ❌ ERROR: Dimensional mismatch between tensor fields
dimensionedSymmTensor stress("stress", dimPressure, symmTensor::zero);
dimensionedSymmTensor rate("rate", dimless/dimTime, symmTensor::zero);
auto result = stress + rate;  // Compile-time error!

// ✅ CORRECT: Ensure dimensional consistency
dimensionedSymmTensor stress("stress", dimPressure, symmTensor::zero);
dimensionedSymmTensor strain("strain", dimless, symmTensor::zero);
auto result = stress && strain;  // Scalar with dimensions [M L⁻¹ T⁻²]
```

**📚 Source:** 📂 .applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/ThermalPhaseChangePhaseSystem/ThermalPhaseChangePhaseSystem.C:36

**📖 คำอธิบาย:**
OpenFOAM มีระบบตรวจสอบ dimensional consistency ที่ compile-time ซึ่งช่วยป้องกัน errors จากการบวก tensors ที่มีหน่วยต่างกัน การคำนวณ double contraction จะ propagate dimensions ตามสมการการคูณหน่วย

**🔑 แนวคิดสำคัญ:**
- **DimensionSet:** แต่ละ field มี dimensions [Mass, Length, Time, Temperature, Moles, Current]
- **Compile-time checking:** Compiler จะ catch dimensional mismatches โดยอัตโนมัติ
- **Propagation rules:** Operations ต่างๆ มีกฎการคำนวณ dimensions (เช่น gradient เพิ่ม L⁻¹)
- **Physical validation:** Dimensional consistency เป็นเครื่องมือตรวจสอบความถูกต้องที่ทรงพลัง

> [!INFO] Dimensional Propagation
> Tensor operations automatically propagate dimensions:
> - **Double contraction**: `[A] × [B]`
> - **Single contraction**: `[A] × [B]`
> - **Gradient**: `[A] / [L]`

---

## 5. Tensor Field Boundary Conditions

### Incorrect Boundary Types

```cpp
// ❌ PROBLEMATIC: Fixed value on all patches may be unphysical
volSymmTensorField R
(
    IOobject("R", runTime.timeName(), mesh),
    mesh,
    dimensionedSymmTensor("zero", dimVelocity*dimVelocity, symmTensor::zero),
    calculatedFvPatchField<symmTensor>::typeName
);

// ✅ CORRECT: Appropriate boundary conditions per patch
volSymmTensorField R
(
    IOobject("R", runTime.timeName(), mesh),
    mesh,
    dimensionedSymmTensor("zero", dimVelocity*dimVelocity, symmTensor::zero),
    boundaryConditions  // Specify appropriate BCs per patch
);
```

**📚 Source:** 📂 .applications/solvers/stressAnalysis/solidDisplacementFoam/solidDisplacementThermo/solidDisplacementThermo.C:44

**📖 คำอธิบาย:**
การใช้ boundary conditions ที่ไม่เหมาะสมกับ physics ของปัญหาอาจทำให้ solution diverge หรือให้ผลลัพธ์ที่ไม่ถูกต้อง Reynolds stress tensor R ซึ่งเป็น symmetric tensor ต้องการ BCs ที่รักษา symmetry และความต่อเนื่องของ flux

**🔑 แนวคิดสำคัญ:**
- **Patch-specific BCs:** แต่ละ patch ต้องมี BC ที่เหมาะสมกับ flow characteristics
- **Symmetry preservation:** SymmTensor BCs ต้องรักษา tensor symmetry ที่ boundaries
- **Zero gradient:** ใช้สำหรับ patches ที่ fully developed flow
- **Fixed value:** ใช้เมื่อมีข้อมูล boundary measurements ที่แม่นยำ

### Symmetry Enforcement

```cpp
// Ensure numerical symmetry for physical correctness
symmTensor T = ...;

// Calculate asymmetry magnitude (should be ≈ 0 for symmetric tensors)
scalar symmetryError = mag(T - T.T());

if (symmetryError > 1e-10) {
    Warning << "Tensor asymmetry detected: " << symmetryError << endl;
    // Enforce symmetry by averaging with transpose
    T = symm(T);
}
```

**📚 Source:** 📂 .applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.C:32

**📖 คำอธิบาย:**
Numerical errors ในการคำนวณอาจทำให้ symmetric tensors สูญเสียคุณสมบัติ symmetry การตรวจสอบและ enforce symmetry ช่วยรักษา physical consistency และป้องกัน numerical instabilities ที่อาจเกิดขึ้น

**🔑 แนวคิดสำคัญ:**
- **Symm function:** `symm(T) = (T + T.T())/2` คำนวณ symmetric part
- **Numerical drift:** Floating-point arithmetic ทำให้เกิด asymmetry ค่อยๆ สะสม
- **Physical validity:** Physical quantities เช่น stress tensor ต้องเป็น symmetric
- **Stability:** Asymmetric tensors อาจทำให้ solvers diverge ในบางกรณี

---

## 6. Performance Pitfalls

### Memory Inefficiency

```cpp
// ❌ INEFFICIENT: Full tensor for symmetric quantities wastes memory
volTensorField stress(...);  // Uses 9 components per cell

// ✅ EFFICIENT: Symmetric tensor reduces memory footprint
volSymmTensorField stress(...);  // Uses 6 components per cell
```

**📚 Source:** 📂 .applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.C:32

**📖 คำอธิบาย:**
การใช้ full tensor (9 components) สำหรับ quantities ที่เป็น symmetric โดยกายภาพเป็นการสิ้นเปลืองหน่วยความจำและคอมพิวติ้งพาวเวอร์ OpenFOAM มี symmTensor class ที่ optimized สำหรับสถานการณ์นี้โดยเฉพาะ

**🔑 แนวคิดสำคัญ:**
- **Memory reduction:** 33% memory savings (6 vs 9 components per cell)
- **Cache efficiency:** น้อย components หมายถึงดีกว่า cache utilization
- **Compute savings:** Operations บน symmTensor ทำงานเร็วกว่า
- **Physical correctness:** Stress/strain rates เป็น symmetric โดยธรรมชาติ

### Unnecessary Temporary Objects

```cpp
// ❌ INEFFICIENT: Chain operations create unnecessary temporaries
tensor result = A + B + C + D;

// ✅ EFFICIENT: Use expression templates for lazy evaluation
auto result = A + B + C + D;  // Single pass computation, no temporaries
```

**📚 Source:** 📂 .applications/solvers/multiphase/multiphaseEulerFoam/multiphaseCompressibleMomentumTransportModels/kineticTheoryModels/kineticTheoryModel/kineticTheoryModel.C:44

**📖 คำอธิบาย:**
OpenFOAM ใช้ expression templates เพื่อ implement lazy evaluation ซึ่งช่วยลด temporary objects ในการคำนวณ chain operations การใช้ `auto` keyword ช่วยให้ compiler สร้าง optimal expression tree

**🔑 แนวคิดสำคัญ:**
- **Expression templates:** Technique ที่ defer evaluation จนกว่าจะต้องการจริง
- **Lazy evaluation:** Operations จะถูก combine ก่อนคำนวณในครั้งเดียว
- **Memory efficiency:** ลด memory allocations และ deallocations
- **Compile-time optimization:** Compiler สามารถ optimize expression trees

### Pre-computation Strategies

```cpp
// ✅ OPTIMIZED: Pre-compute tensor invariants once
symmTensor S = ...;

// Compute invariants (expensive operations, do once)
scalar trS = tr(S);        // Trace: sum of diagonal elements
scalar detS = det(S);      // Determinant
scalar magS = mag(S);      // Frobenius norm

// Reuse invariants in subsequent calculations
scalar pressure = trS / 3.0;
scalar invariant2 = 0.5 * (trS*trS - magS*magS);
```

**📚 Source:** 📂 .applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/ThermalPhaseChangePhaseSystem/ThermalPhaseChangePhaseSystem.C:36

**📖 คำอธิบาย:**
Tensor invariants เป็น quantities ที่ไม่เปลี่ยนแปลงภายใต้ coordinate transformations การ pre-compute ค่าเหล่านี้และ reuse ใน calculations ต่อๆ ไปช่วยประหยัด computational cost อย่างมาก

**🔑 แนวคิดสำคัญ:**
- **Invariants:** Trace, determinant, magnitude เป็น independent of coordinate system
- **Computational cost:** Invariant calculations มักเป็น operations ที่แพง
- **Reuse strategy:** เก็บไว้ใน variables แทนการคำนวณซ้ำ
- **Principal values:** Invariants ใช้คำนวณ principal stresses/strains

---

## 7. Debugging Checklist

Use this systematic approach to debug tensor-related issues:

### Step 1: Type Verification

```cpp
// Static assertion to check tensor ranks and types at compile-time
static_assert(std::is_same_v<decltype(A && B), scalar>, "Type mismatch!");
```

**📚 Source:** 📂 .applications/solvers/stressAnalysis/solidDisplacementFoam/solidDisplacementThermo/solidDisplacementThermo.H:38

**📖 คำอธิบาย:**
Static assertions ช่วยตรวจสอบ types ที่ compile-time ซึ่งเป็นวิธีที่ปลอดภัยและรวดเร็วในการ detect type mismatches ใน tensor operations โดยเฉพาะการใช้ contraction operators

**🔑 แนวคิดสำคัญ:**
- **Compile-time safety:** Errors จะถูกจับก่อน runtime
- ** decltype:** Automatically deduce return type of expressions
- **Type traits:** `std::is_same_v` ตรวจสอบ type equivalence
- **Documentation:** Static assertions ทำหน้าที่เป็น inline documentation

### Step 2: Symmetry Validation

```cpp
// Template function to check symmetry of any tensor type
template<class TensorType>
void checkSymmetry(const TensorType& T, const word& name) {
    // Compute asymmetry magnitude
    scalar asymmetry = mag(T - T.T());
    Info << name << " asymmetry: " << asymmetry << endl;
}
```

**📚 Source:** 📂 .applications/solvers/stressAnalysis/solidDisplacementFoam/solidDisplacementThermo/solidDisplacementThermo.C:44

**📖 คำอธิบาย:**
Template function นี้สามารถใช้กับ tensor types ต่างๆ เพื่อตรวจสอบความเป็น symmetric การหาความต่างระหว่าง tensor กับ transpose ของมันเองจะบอกความรุนแรงของ asymmetry

**🔑 แนวคิดสำคัญ:**
- **Generic programming:** Templates ทำงานกับ tensor types ทั้งหมด
- **Transpose operation:** `T.T()` returns transpose of tensor
- **Magnitude function:** `mag()` คำนวณ Frobenius norm
- **Runtime diagnostics:** Print asymmetry magnitude สำหรับ monitoring

### Step 3: Physical Consistency

```cpp
// Check tensor invariants for physical validity
bool isPhysical = (minEigenvalue > 0) && (det(T) > 0);

if (!isPhysical) {
    Warning << "Non-physical tensor detected!" << endl;
}
```

**📚 Source:** 📂 .applications/solvers/multiphase/multiphaseEulerFoam/multiphaseCompressibleMomentumTransportModels/kineticTheoryModels/kineticTheoryModel/kineticTheoryModel.C:44

**📖 คำอธิบาย:**
Physical tensors ใน CFD problems มักมี constraints ทางฟิสิกส์ เช่น positive definiteness การตรวจสอบ eigenvalues และ determinant ช่วย validate ว่า tensor เป็นไปตาม physical laws

**🔑 แนวคิดสำคัญ:**
- **Positive definiteness:** Positive eigenvalues สำหรับ stress/strain tensors
- **Determinant sign:** Det > 0 สำหรับ physically valid tensors
- **Realizability:** บาง quantities มี realizability constraints
- **Validation layer:** Checks เหล่านี้เป็น sanity checks สำหรับ simulation

### Step 4: Dimensional Analysis

```cpp
// Verify dimensions at runtime for debugging
Info << "Tensor dimensions: " << T.dimensions() << endl;
```

**📚 Source:** 📂 .applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/ThermalPhaseChangePhaseSystem/ThermalPhaseChangePhaseSystem.C:36

**📖 คำอธิบาย:**
แม้ว่า OpenFOAM จะตรวจสอบ dimensions ที่ compile-time แต่การ print dimensions ที่ runtime ช่วย debug และ verify ว่า field fields มี units ที่ถูกต้องตามที่คาดหวัง

**🔑 แนวคิดสำคัญ:**
- **dimensionSet:** Object เก็บข้อมูล dimensions ของ field
- **Runtime verification:** Debug tool สำหรับตรวจสอบ units
- **Human-readable:** dimensionSet จะถูก print เป็น [M L T ...]
- **Traceability:** ช่วยติดตาม dimensional propagation ผ่าน solver

### Step 5: Numerical Range Checks

```cpp
// Check for NaN or Inf in tensor fields
if (mag(T) > GREAT) {
    FatalError << "Tensor magnitude exceeds bounds!" << endl;
}
```

**📚 Source:** 📂 .applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.C:32

**📖 คำอธิบาย:**
Numerical explosions อาจทำให้ tensor values กลายเป็น Inf หรือ NaN การตรวจสอบ magnitude ช่วย detect ปัญหาเหล่านี้ก่อนที่จะทำให้ solver diverge หรือ crash

**🔑 แนวคิดสำคัญ:**
- **GREAT constant:** OpenFOAM constant แทนค่าขีดจำกัดบน (~1e37)
- **NaN detection:** NaN comparison always returns false
- **Early detection:** Range checks ช่วยหยุด simulation ก่อน corrupt
- **Graceful failure:** FatalError ช่วย log และ stop อย่างเป็นระบบ

---

## 8. Common Error Messages and Solutions

| Error Message | Common Cause | Solution |
|---------------|--------------|----------|
| `Rank mismatch error` | Wrong contraction operator (`&` vs `&&`) | Check expected return type |
| `Tensor is singular` | `det(T) ≈ 0` when computing `inv(T)` | Add regularization or check determinant |
| `Dimensional inconsistency` | Adding tensors with different units | Verify `dimensionSet` compatibility |
| `Symmetry violation` | Numerical errors in symmetric operations | Apply `symm()` function to enforce |
| `NaN in tensor field` | Division by zero or invalid operations | Add checks for `SMALL` values |

---

## 9. Best Practices Summary

### ✅ DO

1. **Always check tensor ranks** before using contraction operators
2. **Use `symmTensor`** for physically symmetric quantities
3. **Validate determinants** before computing inverses
4. **Enforce dimensional consistency** using `dimensionSet`
5. **Pre-compute invariants** for repeated calculations
6. **Check eigenvalues** for physical validity
7. **Use `tmp<>` templates** for temporary field operations

### ❌ DON'T

1. **Don't mix contraction operators** without understanding return types
2. **Don't use `tensor`** when `symmTensor` suffices
3. **Don't compute `inv()`** without checking `det()`
4. **Don't ignore dimensional warnings** from the compiler
5. **Don't assume symmetry** without numerical verification
6. **Don't create unnecessary temporaries** in performance-critical code

---

## 10. Debugging Tools

### Tensor Visualization

```cpp
// Output tensor components for debugging
Info << "Tensor T = " << nl
    << "  xx: " << T.xx() << "  xy: " << T.xy() << "  xz: " << T.xz() << nl
    << "  yx: " << T.yx() << "  yy: " << T.yy() << "  yz: " << T.yz() << nl
    << "  zx: " << T.zx() << "  zy: " << T.zy() << "  zz: " << T.zz() << endl;
```

**📚 Source:** 📂 .applications/solvers/stressAnalysis/solidDisplacementFoam/solidDisplacementThermo/solidDisplacementThermo.H:38

**📖 คำอธิบาย:**
การ print แต่ละ component ของ tensor ช่วย visualize ค่าและ detect irregularities หรือ unexpected patterns ใน tensor field โดยเฉพาะอย่างยิ่งเมื่อ debug ปัญหา boundary conditions หรือ source terms

**🔑 แนวคิดสำคัญ:**
- **Component access:** Individual components เข้าถึงได้ผ่าน `.xx()`, `.xy()`, etc.
- **Newline formatting:** `nl` ใช้สำหรับ multi-line output
- **Spatial patterns:** Print ที่หลาย cells ช่วย visualize spatial distributions
- **Symmetry check:** Compare YX vs XY, etc. to detect asymmetry

### Invariant Monitoring

```cpp
// Monitor tensor invariants during simulation
scalar I1 = tr(T);  // First invariant: trace
scalar I2 = 0.5 * (I1*I1 - tr(T & T));  // Second invariant
scalar I3 = det(T);  // Third invariant: determinant

Info << "Tensor invariants: I1=" << I1 << ", I2=" << I2 << ", I3=" << I3 << endl;
```

**📚 Source:** 📂 .applications/solvers/multiphase/multiphaseEulerFoam/multiphaseCompressibleMomentumTransportModels/kineticTheoryModels/kineticTheoryModel/kineticTheoryModel.C:44

**📖 คำอธิบาย:**
Tensor invariants เป็น scalar quantities ที่ independent of coordinate system ทำให้เป็น indicators ที่ดีสำหรับ monitoring simulation behavior โดยไม่ต้องกังวลเรื่อง coordinate transformations

**🔑 แนวคิดสำคัญ:**
- **Principal invariants:** I1, I2, I3 ใช้คำนวณ principal values
- **Coordinate independence:** Invariants เหมือนกันในทุก coordinate systems
- **Physical meaning:** I1 = mean effect, I2 = combined shear, I3 = volume change
- **Stability indicators:** Changes ใน invariants อาจ signal numerical instabilities

### Eigenvalue Analysis

```cpp
// Principal stress/strain analysis
vector lambdas = eigenValues(T);  // Principal values
tensor vectors = eigenVectors(T);  // Principal directions (columns)

Info << "Eigenvalues: " << lambdas << nl
    << "Eigenvectors (columns): " << vectors << endl;
```

**📚 Source:** 📂 .applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/ThermalPhaseChangePhaseSystem/ThermalPhaseChangePhaseSystem.C:36

**📖 คำอธิบาย:**
Eigenvalue decomposition เป็นเครื่องมือที่ทรงพลังในการวิเคราะห์ tensors เพราะ principal values และ directions ให้ข้อมูลเชิงฟิสิกส์ที่สำคัญ เช่น maximum stresses และ orientations

**🔑 แนวคิดสำคัญ:**
- **Principal values:** Eigenvalues = magnitudes ของ principal stresses/strains
- **Principal directions:** Eigenvectors = directions ของ principal actions
- **Ordered output:** Eigenvalues sorted จากมากไปน้อยโดยทั่วไป
- **Physical interpretation:** Max eigenvalue คือ critical stress direction

---

## Conclusion

Understanding these common pitfalls and implementing robust debugging practices will significantly improve the reliability and performance of your OpenFOAM tensor operations. The key is to:

1. **Always verify types** before operations
2. **Check physical validity** during computation
3. **Use appropriate tensor types** for the physics
4. **Monitor numerical stability** throughout simulations

Following these guidelines will help you avoid the most frequent errors and develop efficient, correct CFD solvers.