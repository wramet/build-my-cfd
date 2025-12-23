# Summary & Exercises: Tensor Algebra Mastery

```mermaid
mindmap
  root((Tensor Algebra))
    Types
      Full Tensor (9)
      Symmetric (6)
      Spherical (1)
    Operations
      Dot (&) / Double Dot (&&)
      Trace / Det / Inv
      Deviatoric / Skew
    Analysis
      Eigenvalues
      Eigenvectors
      Invariants
    Physics
      Stress / Strain
      Reynolds Stress
      Conductivity
```
> **Figure 1:** แผนผังความคิดสรุปองค์ประกอบของพีชคณิตเทนเซอร์ ครอบคลุมทั้งประเภทข้อมูล การดำเนินการพื้นฐาน การวิเคราะห์ค่าลักษณะเฉพาะ และการประยุกต์ใช้ในฟิสิกส์ของการจำลองความปลอดภัยทางฟิสิกส์ไม่ส่งผลกระทบต่อความเร็วในการจำลอง ผ่านการใช้พลังของ C++ Template Metaprogramming ในการตรวจสอบความสอดคล้องทางมิติทั้งหมดที่ขั้นตอนการคอมไพล์โปรแกรมเพียงครั้งเดียว

## Part 1: Comprehensive Summary

### The Tensor Foundation in OpenFOAM

OpenFOAM's tensor algebra framework provides the mathematical foundation for advanced physics modeling, enabling concrete representation of directional quantities and spatial variations in continuum mechanics.

The framework extends far beyond simple scalar and vector mathematics to capture complex anisotropic behaviors found in real fluid flows and material responses.

> [!INFO] Core Tensor Architecture
> OpenFOAM implements three fundamental tensor types, each optimized for specific physical applications through memory-efficient storage and computationally optimized operations.

#### Tensor Type Hierarchy

| Tensor Type | Independent Components | Memory Layout | Primary Applications |
|-------------|------------------------|---------------|---------------------|
| **Tensor** | 9 components | `[xx, xy, xz, yx, yy, yz, zx, zy, zz]` | Rotation operations, general transformations |
| **symmTensor** | 6 components | `[xx, yy, zz, xy, yz, xz]` | Stress tensors, strain-rate tensors |
| **sphericalTensor** | 1 component | `[ii]` | Isotropic pressure, isotropic material properties |

#### 1. Full Tensor (`Tensor`)

Complete $3 \times 3$ tensor with 9 independent components:

$$\mathbf{T} = \begin{bmatrix} T_{xx} & T_{xy} & T_{xz} \\ T_{yx} & T_{yy} & T_{yz} \\ T_{zx} & T_{zy} & T_{zz} \end{bmatrix}$$

**Physical Applications:**
- Deformation gradients
- Velocity gradients ($\nabla\mathbf{u}$)
- General rotation tensors
- Non-symmetric stress distributions

#### 2. Symmetric Tensor (`symmTensor`)

$3 \times 3$ tensor with 6 independent components enforcing $T_{ij} = T_{ji}$:

$$\mathbf{S} = \begin{bmatrix} S_{xx} & S_{xy} & S_{xz} \\ S_{xy} & S_{yy} & S_{yz} \\ S_{xz} & S_{yz} & S_{zz} \end{bmatrix}$$

**Memory Efficiency:** 33% reduction compared to full tensors

**Physical Applications:**
- Cauchy stress tensor: $\boldsymbol{\sigma}$
- Strain-rate tensor: $\mathbf{D} = \frac{1}{2}(\nabla\mathbf{u} + \nabla\mathbf{u}^T)$
- Reynolds stress tensor: $\mathbf{R} = \overline{\mathbf{u}' \otimes \mathbf{u}'}$
- Diffusion coefficient tensors

#### 3. Spherical Tensor (`sphericalTensor`)

Isotropic tensor representing $\alpha\mathbf{I}$:

$$\boldsymbol{\Lambda} = \lambda\mathbf{I} = \lambda\begin{bmatrix} 1 & 0 & 0 \\ 0 & 1 & 0 \\ 0 & 0 & 1 \end{bmatrix}$$

**Memory Efficiency:** 89% reduction compared to full tensors

**Physical Applications:**
- Isotropic pressure fields
- Identity tensor operations
- Isotropic material properties

---

### Mathematical Operations Framework

#### Tensor Contractions

**Single Contraction (`&`):** Matrix-vector or tensor-tensor multiplication

$$\mathbf{y} = \mathbf{T} \cdot \mathbf{v} \quad \text{where} \quad y_i = \sum_{j=1}^{3} T_{ij} v_j$$

```cpp
// Single contraction examples
vector w = T & v;       // Tensor-vector → vector
tensor C = A & B;       // Tensor-tensor → tensor
```

**Double Contraction (`&&`):** Frobenius inner product

$$\mathbf{A} : \mathbf{B} = \sum_{i,j=1}^{3} A_{ij} B_{ij} = \text{tr}(\mathbf{A} \cdot \mathbf{B}^T)$$

```cpp
// Double contraction yields scalar
scalar s = A && B;      // Frobenius inner product
```

**Physical Significance:**
- Work rate calculations
- Stress-strain products
- Energy dissipation terms

#### Tensor Decomposition

**Symmetric Part:**

$$\mathbf{S} = \frac{1}{2}(\mathbf{T} + \mathbf{T}^T)$$

```cpp
symmTensor S = symm(T);  // Extract symmetric component
```

**Antisymmetric (Skew) Part:**

$$\mathbf{A} = \frac{1}{2}(\mathbf{T} - \mathbf{T}^T)$$

```cpp
tensor A = skew(T);      // Extract antisymmetric component
```

**Deviatoric Part:**

$$\text{dev}(\mathbf{T}) = \mathbf{T} - \frac{1}{3}\text{tr}(\mathbf{T})\mathbf{I}$$

```cpp
symmTensor devT = dev(T);  // Deviatoric (traceless) component
```

#### Tensor Invariants

Principal invariants of symmetric tensors:

```cpp
symmTensor T;

// First invariant (trace)
scalar I1 = tr(T);

// Second invariant
scalar I2 = 0.5 * (pow(tr(T), 2) - tr(T & T));

// Third invariant (determinant)
scalar I3 = det(T);
```

**Physical Interpretation:**
- **I₁**: Hydrostatic stress component
- **I₂**: Deviatoric stress magnitude
- **I₃**: Volume change indicator

---

### Eigenvalue Decomposition

**The Eigenvalue Problem:**

$$\mathbf{A}\mathbf{v} = \lambda\mathbf{v}$$

Where:
- $\lambda$: Eigenvalue (principal value)
- $\mathbf{v}$: Eigenvector (principal direction)
- $\mathbf{A}$: Symmetric tensor

**OpenFOAM Implementation:**

```cpp
symmTensor stressTensor;  // Input stress tensor
vector eigenvalues;       // Principal stresses [σ₁, σ₂, σ₃]
tensor eigenvectors;      // Principal directions as columns

// Eigenvalue decomposition
eigenValues(stressTensor, eigenvalues, eigenvectors);
```

**Principal Stress Analysis:**

```cpp
// Access individual principal values
scalar sigma1 = eigenvalues.x();  // Maximum principal stress
scalar sigma2 = eigenvalues.y();  // Intermediate principal stress
scalar sigma3 = eigenvalues.z();  // Minimum principal stress

// Access principal directions
vector n1 = eigenvectors.col(0);  // Direction of σ₁
vector n2 = eigenvectors.col(1);  // Direction of σ₂
vector n3 = eigenvectors.col(2);  // Direction of σ₃
```

**Applications:**
- **Principal Stress Analysis**: Solid mechanics failure criteria
- **Anisotropy Characterization**: Turbulence modeling
- **Material Orientation**: Composite material analysis

---

### Tensor Calculus Operations

#### Gradient Operations

**Velocity Gradient Tensor:**

$$[\nabla \mathbf{U}]_{ij} = \frac{\partial U_i}{\partial x_j}$$

```cpp
volVectorField U(mesh);
volTensorField gradU = fvc::grad(U);  // ∇U
```

**Strain-Rate Tensor:**

$$\mathbf{D} = \text{sym}(\nabla \mathbf{u}) = \frac{1}{2}\left(\nabla \mathbf{u} + (\nabla \mathbf{u})^T\right)$$

```cpp
volSymmTensorField D = symm(gradU);  // Symmetric part
```

**Vorticity Tensor:**

$$\boldsymbol{\Omega} = \text{skew}(\nabla \mathbf{u}) = \frac{1}{2}\left(\nabla \mathbf{u} - (\nabla \mathbf{u})^T\right)$$

```cpp
volTensorField Omega = skew(gradU);  // Antisymmetric part
```

#### Divergence Operations

**Stress Divergence:**

$$(\nabla \cdot \boldsymbol{\tau})_i = \sum_{j=1}^{3} \frac{\partial \tau_{ij}}{\partial x_j}$$

```cpp
volSymmTensorField tau(mesh);
volVectorField divTau = fvc::div(tau);  // ∇·τ
```

**Physical Meaning:** Net force per unit volume from stress gradients

**Units:** N/m³ (force per unit volume)

---

### CFD Applications

#### 1. Cauchy Stress Tensor

$$\boldsymbol{\sigma} = -p\mathbf{I} + 2\mu\mathbf{D} + \lambda(\nabla \cdot \mathbf{u})\mathbf{I}$$

```cpp
volSymmTensorField sigma
(
    IOobject("sigma", runTime.timeName(), mesh),
    mesh,
    dimensionedSymmTensor("zero", dimPressure, symmTensor::zero)
);

sigma = -p*I + 2*mu*D + lambda*(fvc::div(U))*I;
```

**Variable Definitions:**
- $\boldsymbol{\sigma}$: Cauchy stress tensor
- $p$: Pressure field
- $\mathbf{I}$: Identity tensor
- $\mu$, $\lambda$: Lamé constants (viscosity coefficients)
- $\mathbf{D}$: Rate-of-deformation tensor
- $\mathbf{u}$: Velocity vector

#### 2. Reynolds Stress Transport

**Production Term:**

$$P_{ij} = -[R_{ik}\frac{\partial u_j}{\partial x_k} + R_{jk}\frac{\partial u_i}{\partial x_k}]$$

```cpp
volSymmTensorField R
(
    IOobject("R", runTime.timeName(), mesh),
    mesh,
    dimensionedSymmTensor("zero", dimVelocity*dimVelocity, symmTensor::zero)
);

// Production term calculation
volSymmTensorField P = -(R & fvc::grad(U)) + (R & fvc::grad(U)).T();
```

**Transport Equation Components:**
- **Production ($P_{ij}$)**: Turbulence generation
- **Pressure-Strain ($\Phi_{ij}$)**: Energy redistribution
- **Dissipation ($\varepsilon_{ij}$)**: Turbulence decay
- **Diffusion ($D_{ij}$)**: Reynolds stress spatial transport

#### 3. Von Mises Stress

$$\sigma_{vm} = \sqrt{\frac{3}{2}\mathbf{S}:\mathbf{S}}$$

Where $\mathbf{S} = \boldsymbol{\sigma} - \frac{1}{3}\text{tr}(\boldsymbol{\sigma})\mathbf{I}$ is the deviatoric stress

```cpp
volScalarField vonMises = sqrt(1.5) * mag(dev(sigma));
```

**Application:** Equivalent stress measure for failure analysis

---

### Implementation Architecture

#### Memory-Efficient Storage

```cpp
// Symmetric tensor storage
class symmTensor {
private:
    scalar components_[6];  // [xx, yy, zz, xy, yz, xz]

public:
    // Access methods
    scalar xx() const { return components_[0]; }
    scalar yy() const { return components_[1]; }
    scalar zz() const { return components_[2]; }
    scalar xy() const { return components_[3]; }
    scalar yz() const { return components_[4]; }
    scalar xz() const { return components_[5]; }

    // Implicit symmetry
    scalar yx() const { return xy(); }  // Equal to xy()
    scalar zx() const { return xz(); }  // Equal to xz()
    scalar zy() const { return yz(); }  // Equal to yz()
};
```

**Memory Optimization Benefits:**
- **Storage Reduction**: 6 components instead of 9 (33% reduction)
- **Cache Efficiency**: Better contiguous storage access
- **Computational Speed**: Faster operations for symmetric tensors

#### Template Specialization

```cpp
template<>
class Tensor<symmTensor> {
    // Specialized operations enforcing symmetry
    static symmTensor transpose(const symmTensor& t) {
        return t;  // Symmetric tensor is its own transpose
    }

    // Optimized multiplication exploiting symmetry
    static symmTensor multiply(const symmTensor& a, const symmTensor& b);
};
```

**Optimization Benefits:**
- **Compile-time Optimization**: Property checking at compilation
- **Specialized Operations**: Symmetry-exploiting computations
- **Memory Efficiency**: Reduced memory footprint

---

### Dimensional Analysis

```cpp
dimensionSet stressDims(dimPressure);       // [M L⁻¹ T⁻²]
dimensionSet rateDims(dimless/dimTime);     // [T⁻¹]

symmTensorField stressField(stressDims);
symmTensorField rateField(rateDims);

// Result inherits dimensions: [M L⁻¹ T⁻²] * [T⁻¹] = [M L⁻¹ T⁻³]
symmTensorField powerDissipation = stressField & rateField;
```

**Dimension Analysis:**
- **stressDims**: Stress has dimensions [M L⁻¹ T⁻²]
- **rateDims**: Rate has dimensions [T⁻¹]
- **powerDissipation**: Power dissipation has dimensions [M L⁻¹ T⁻³]

---

## Part 2: Exercises

### Section 1: Tensor Type Selection

**Problem:** Select the most appropriate tensor type (`tensor`, `symmTensor`, or `sphericalTensor`) for the following quantities:

1. Isotropic pressure in a fluid
2. Reynolds shear stress in turbulence modeling
3. Velocity gradient ($\nabla\mathbf{U}$)
4. Fluid strain rate tensor
5. Deformation gradient tensor
6. Thermal conductivity in anisotropic material
7. Identity tensor scaling
8. Vorticity tensor

---

### Section 2: Code Analysis

**Problem:** Consider the following code:

```cpp
tensor T(1, 2, 3, 4, 5, 6, 7, 8, 9);
vector v(1, 0, 0);
auto res1 = T & v;
auto res2 = T && T;
```

**Questions:**
1. What type is `res1`? What is its value?
2. What type is `res2`? What is its value?
3. What would happen if you tried `vector res3 = v && v`?

---

### Section 3: Tensor Calculus

**Problem:** Given a velocity field $\mathbf{U} = (U_x, U_y, U_z)$, write OpenFOAM code to:

1. Compute the velocity gradient tensor $\nabla\mathbf{U}$
2. Extract the symmetric strain-rate tensor $\mathbf{D}$
3. Extract the antisymmetric vorticity tensor $\boldsymbol{\Omega}$
4. Calculate the trace of the strain-rate tensor
5. Compute the deviatoric part of the strain-rate tensor

---

### Section 4: Stress Analysis Application

**Problem:** You need to calculate the **Von Mises stress** for material failure analysis using:

$$\sigma_{vm} = \sqrt{\frac{3}{2}\mathbf{S}:\mathbf{S}}$$

Where $\mathbf{S}$ is the deviatoric part of the stress tensor $\boldsymbol{\sigma}$.

**Tasks:**
1. Write the OpenFOAM code to compute `vonMises` from a `volSymmTensorField sigma`
2. Compute the principal stresses from `sigma`
3. Determine the maximum principal stress and its direction
4. Check if the material yields (exceeds a yield stress of 250 MPa)

---

### Section 5: Turbulence Modeling

**Problem:** In RANS turbulence modeling, the Reynolds stress tensor $\mathbf{R}$ requires:

1. Define a symmetric tensor field for Reynolds stress
2. Calculate the production term $P_{ij}$ from mean velocity gradients
3. Compute the turbulent kinetic energy: $k = \frac{1}{2}\text{tr}(\mathbf{R})$
4. Calculate the eigenvalue decomposition of $\mathbf{R}$ to analyze anisotropy

---

### Section 6: Debugging

**Problem:** Identify and fix the errors in the following code:

```cpp
tensor T = ...;
symmTensor S = ...;
vector v = ...;

// Error 1
vector w1 = T && v;

// Error 2
scalar s = T & S;

// Error 3
tensor result = inv(S);  // S is nearly singular

// Error 4
volScalarField magT = mag(T);  // T is not a field
```

---

## Part 3: Solutions

### Section 1: Tensor Type Selection

| Quantity | Tensor Type | Rationale |
|----------|-------------|-----------|
| 1. Isotropic pressure | `sphericalTensor` | Equal in all directions |
| 2. Reynolds stress | `symmTensor` | By definition symmetric ($\overline{u_i' u_j'} = \overline{u_j' u_i'}$) |
| 3. Velocity gradient | `tensor` | Generally non-symmetric |
| 4. Strain rate | `symmTensor` | Symmetric by definition |
| 5. Deformation gradient | `tensor` | May include rotation |
| 6. Anisotropic conductivity | `symmTensor` | Material property symmetric |
| 7. Identity scaling | `sphericalTensor` | Isotropic scaling |
| 8. Vorticity | `tensor` | Antisymmetric by definition |

---

### Section 2: Code Analysis

**Solution:**

```cpp
tensor T(1, 2, 3, 4, 5, 6, 7, 8, 9);
vector v(1, 0, 0);

// res1: vector type, value = (1, 4, 7)
vector res1 = T & v;
// Calculation: w_x = 1*1 + 2*0 + 3*0 = 1
//             w_y = 4*1 + 5*0 + 6*0 = 4
//             w_z = 7*1 + 8*0 + 9*0 = 7

// res2: scalar type, value = 285
scalar res2 = T && T;
// Calculation: 1² + 2² + 3² + 4² + 5² + 6² + 7² + 8² + 9²
//             = 1 + 4 + 9 + 16 + 25 + 36 + 49 + 64 + 81
//             = 285

// Error: vector res3 = v && v;
// Double contraction of vectors is not defined
// Use dot product instead: scalar s = v & v;
```

---

### Section 3: Tensor Calculus

**Solution:**

```cpp
// 1. Velocity gradient tensor
volVectorField U(mesh);
volTensorField gradU = fvc::grad(U);

// 2. Strain-rate tensor (symmetric part)
volSymmTensorField D = symm(gradU);

// 3. Vorticity tensor (antisymmetric part)
volTensorField Omega = skew(gradU);

// 4. Trace of strain-rate tensor (volumetric dilation rate)
volScalarField trD = tr(D);

// 5. Deviatoric strain-rate tensor
volSymmTensorField devD = dev(D);

// Alternative: Manually calculate deviatoric
volSymmTensorField devD_manual = D - (1.0/3.0)*trD*symmTensor::I;
```

---

### Section 4: Stress Analysis

**Solution:**

```cpp
volSymmTensorField sigma(mesh);  // Stress tensor field
scalar yieldStress = 250e6;      // 250 MPa in Pascals

// 1. Von Mises stress calculation
volScalarField vonMises = sqrt(1.5) * mag(dev(sigma));

// 2. Principal stress calculation
volVectorField principalStresses(mesh);
volTensorField principalDirections(mesh);

forAll(sigma, i) {
    vector eigenvalues;
    tensor eigenvectors;
    eigenValues(sigma[i], eigenvalues, eigenvectors);

    principalStresses[i] = eigenvalues;
    principalDirections[i] = eigenvectors;
}

// 3. Maximum principal stress
scalar maxPrincipalStress = max(principalStresses.component(vector::X));

// 4. Yield check
volScalarField yieldIndicator = vonMises - yieldStress;
scalar maxYieldIndicator = max(yieldIndicator);

if (maxYieldIndicator > 0) {
    Info << "WARNING: Material yielding detected!" << endl;
    Info << "Maximum Von Mises stress: " << max(vonMises) << " Pa" << endl;
}

// Alternative: Check principal stress criterion
if (maxPrincipalStress > yieldStress) {
    Info << "WARNING: Maximum principal stress exceeds yield stress!" << endl;
}
```

---

### Section 5: Turbulence Modeling

**Solution:**

```cpp
// 1. Define Reynolds stress tensor field
volSymmTensorField R
(
    IOobject("R", runTime.timeName(), mesh),
    mesh,
    dimensionedSymmTensor("zero", dimVelocity*dimVelocity, symmTensor::zero)
);

// 2. Production term calculation
volTensorField gradU = fvc::grad(U);
volSymmTensorField P = -(R & gradU) + (R & gradU).T();

// Alternative formulation: P_ij = -[R_ik*∂U_j/∂x_k + R_jk*∂U_i/∂x_k]

// 3. Turbulent kinetic energy
volScalarField k = 0.5 * tr(R);

// 4. Eigenvalue analysis for anisotropy
volVectorField eigenValues_R(mesh);
volTensorField eigenVectors_R(mesh);

forAll(R, i) {
    vector lambdas;
    tensor eigvecs;
    eigenValues(R[i], lambdas, eigvecs);

    eigenValues_R[i] = lambdas;
    eigenVectors_R[i] = eigvecs;

    // Anisotropy analysis
    scalar lambda1 = lambdas.x();
    scalar lambda2 = lambdas.y();
    scalar lambda3 = lambdas.z();

    // Check for isotropy: λ₁ ≈ λ₂ ≈ λ₃ ≈ 2k/3
    scalar isotropyDeviation = mag(lambdas - (2.0/3.0)*k[i]);
}

// Lumley triangle anisotropy invariants
volSymmTensorField b = R - (2.0/3.0)*k*symmTensor::I;
volScalarField I1 = tr(b & b);
volScalarField I2 = tr(b & b & b);
```

---

### Section 6: Debugging

**Solution:**

```cpp
tensor T = ...;
symmTensor S = ...;
vector v = ...;

// Error 1: Double contraction returns scalar, not vector
// vector w1 = T && v;  // ❌ WRONG
scalar s1 = T && v;     // ✅ CORRECT (if v is promoted to tensor)
// OR
vector w1_correct = T & v;  // ✅ CORRECT (single contraction)

// Error 2: Single contraction between tensor and symmTensor
// scalar s = T & S;  // ❌ Type mismatch
tensor result = T & tensor(S);  // ✅ Convert symmTensor to tensor first
// OR
scalar s_correct = T && tensor(S);  // ✅ Double contraction

// Error 3: Inverting nearly singular tensor
// tensor result = inv(S);  // May fail or be numerically unstable
scalar detS = det(S);
if (mag(detS) < SMALL) {
    Warning << "Tensor is nearly singular!" << endl;
    // Use pseudo-inverse or regularization
    tensor result = inv(S + SMALL*tensor::I);
} else {
    tensor result = inv(S);
}

// Error 4: mag() on single tensor, not field
// volScalarField magT = mag(T);  // T is not a field
scalar magT = mag(T);  // ✅ CORRECT

// If T is a field:
// volTensorField TField(mesh);
// volScalarField magTField = mag(TField);  // ✅ CORRECT
```

---

## Performance Best Practices

### Memory Management

1. **Use appropriate tensor types**: `symmTensor` for symmetric quantities saves 33% memory
2. **Avoid unnecessary temporaries**: Use reference types where possible
3. **Leverage compile-time optimization**: Template specialization enables efficient code generation

### Computational Efficiency

```cpp
// Optimized tensor operations using OpenFOAM's methods
symmTensor S = symm(fvc::grad(U));  // Symmetric part of velocity gradient
scalar magS = mag(S);               // Frobenius norm: √(S_ij S_ij)

// Eigenvalue analysis for turbulence modeling
vector eigenValues;
tensor eigenVectors;
eigenValues(R, eigenValues, eigenVectors);
```

**Performance Metrics:**
- **Memory Access**: Contiguous storage for cache efficiency
- **Computational Complexity**: Algebraic properties reduce operation count
- **Vectorization**: SIMD instructions for tensor operations

### Debugging and Validation

```cpp
// Check tensor symmetry (should be near machine epsilon)
scalar symmetryError = mag(tau - tau.T());
Info << "Tensor symmetry error: " << symmetryError << endl;

// Check positive definiteness for physical tensors
vector eigenVals = eigenValues(tensorField);
scalar minEigenvalue = min(eigenVals);
if (minEigenvalue < 0) {
    Warning << "Tensor not positive definite!" << endl;
}
```

**Debugging Checklist:**
- **Symmetry Check**: $|T - T^T| \approx 0$ for symmetric tensors
- **Positive Definiteness**: $\lambda_i > 0$ for physical tensors
- **Dimensional Consistency**: Check units of each component
- **Numerical Stability**: Check for abnormal values (NaN, Inf)

---

## Advanced Exploration Paths

### Study of Advanced Implementations

1. **Examine source code** in `src/OpenFOAM/primitives/Tensor/`:
   - `TensorI.H`: Main tensor implementation
   - `symmTensorI.H`: Symmetric tensor specialization
   - `tensorField.H`: Field operations

2. **Study turbulence models** using tensor algebra:
   - `RASModels/LaunderSharmaKE`: RANS approach
   - `LESModels/Smagorinsky`: Large eddy simulation tensor operations

3. **Explore non-Newtonian models** with tensor-dependent viscosity:
   - `viscoelasticLaws/UCM`: Upper-Convected Maxwell model
   - `nonNewtonianIcsModels`: Power-law and Herschel-Bulkley fluids

### Research Applications

| Application | Tensor Usage | Related Models |
|-------------|--------------|----------------|
| **Multiphase Flow** | Interface stress tensors | VOF, Phase Field |
| **Solid Mechanics** | Stress tensors, deformation gradients | Hyperelasticity, Plasticity |
| **Electromagnetics** | Maxwell stress tensor | MHD, Electromagnetics |
| **Biological Flows** | Anisotropic material tensors | Tissue Mechanics, Biomaterials |

**Advanced Research Areas:**
- **Anisotropic Turbulence**: Direction-dependent turbulence modeling
- **Multiphysics Coupling**: Tensors from multiple physics domains
- **Machine Learning Integration**: Tensor-based CFD model training

---

Mastering tensor algebra opens pathways for advanced physics modeling that captures the multi-dimensional nature of fluid flows and material behavior with accuracy.

This enables simulation of complex engineering systems in scientific and industrial applications with proper physical fidelity.
