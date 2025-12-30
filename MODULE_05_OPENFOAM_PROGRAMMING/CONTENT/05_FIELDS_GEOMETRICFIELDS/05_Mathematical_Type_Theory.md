# Mathematical Type Theory

ทฤษฎีประเภททางคณิตศาสตร์ใน OpenFOAM — Tensors & Operations

> **🎯 วัตถุประสงค์การเรียนรู้ (Learning Objectives)**
> 
> **ภาษาไทย:**
> - เข้าใจลำดับชั้นของ tensor rank (scalar → vector → tensor) ใน OpenFOAM
> - คำนวณ tensor operations ได้คล่อง (tr, dev, symm, skew)
> - คำนวณ vorticity, strain rate ได้ถูกต้อง
> - เข้าใจ tensor decomposition และ invariants
> - ใช้ tensor operations แก้ปัญหา CFD ได้
>
> **English:**
> - Understand tensor rank hierarchy (scalar → vector → tensor) in OpenFOAM
> - Compute tensor operations proficiently (tr, dev, symm, skew)
> - Calculate vorticity and strain rate correctly
> - Understand tensor decomposition and invariants
> - Apply tensor operations to solve CFD problems

---

## ทำไม (ทำมา) - Why Mathematical Type Theory Matters

> **💎 Algebra = Physics Accuracy**
>
> ทำไมต้องเข้าใจ tensor algebra? เพราะ CFD ไม่ใช่แค่ "ตัวเลข" แต่เป็น **mathematical entities** ที่ต้องเก็บรักษา:
> - **Transformation properties** ภายใต้การหมุนระบบพิกัด
> - **Invariants** ที่ไม่เปลี่ยนแปลงตามระบบอ้างอิง
> - **Decomposition** เป็นส่วน isotropic/anisotropic

**Consequences ใน CFD:**
- ❌ **ผิด:** `scalar` ตั้งแต่เริ่ม → ระบบทำงานแต่ตอบโจทย์ผิด
- ✅ **ถูก:** เข้าใจ tensor algebra → implement turbulence models ได้ถูกต้อง

**Practical Impact:**
```
Strain Rate S = symm(gradU)  // ถูก
vs
Strain Rate S = gradU         // ผิด - รวม rotation เข้ามา
```

---

## Overview

> **💡 OpenFOAM Types = Mathematical Entities**
>
> ไม่ใช่แค่ตัวเลข แต่มี algebra ครบ — transformation, invariants, decomposition

### 📊 Framework Positioning

```mermaid
graph LR
    A[01_Introduction] --> B[02_Basic_Primitives]
    B --> C[03_Dimensioned_Types]
    C --> D[04_Memory_Containers]
    D --> E[05_Mathematical_Type_Theory]
    E --> F[06_Fields_GeometricFields]
    
    style E fill:#ff6b6b,stroke:#c92a2a
```

**Chapter Role:** เชื่อม abstract types กับ mathematical operations

---

## 1. Tensor Rank Hierarchy

### 📚 แนวคิดพื้นฐาน

**Tensor Rank** = จำนวน indices ที่ต้องการในการอธิบาย quantity

| Rank | Type | Components | Transformation | Example | Physical Meaning |
|------|------|------------|----------------|---------|------------------|
| 0 | `scalar` | 1 | φ' = φ (invariant) | p, T, k, ρ | Intensive/Extensive properties |
| 1 | `vector` | 3 | v' = R·v | U, F, g | Directional quantities |
| 2 | `tensor` | 9 | T' = R·T·Rᵀ | σ, ∇U | Stress, velocity gradient |
| 2 (symm) | `symmTensor` | 6 | T' = R·T·Rᵀ | R, S | Symmetric stress |
| 2 (spher) | `sphericalTensor` | 1 | φ' = φ (invariant) | pI | Isropic stress |

### 🔍 Visual Representation

```
Rank 0 (Scalar):        p = 100 Pa
                       └─ Single value

Rank 1 (Vector):        U = [Ux, Uy, Uz]
                       └─ 3 components

Rank 2 (Tensor):        ∇U = [∂Ux/∂x  ∂Ux/∂y  ∂Ux/∂z]
                            [∂Uy/∂x  ∂Uy/∂y  ∂Uy/∂z]
                            [∂Uz/∂x  ∂Uz/∂y  ∂Uz/∂z]
                       └─ 9 components

Rank 2 (SymmTensor):    S = [Sxx  Sxy  Sxz]
                            [Sxy  Syy  Syz]
                            [Sxz  Syz  Szz]
                       └─ 6 independent components
```

### 💻 Code Examples

```cpp
// Declaration and initialization
scalar p = 101325;              // Pressure [Pa]

vector U(10, 0, 0);             // Velocity [m/s]
U.x() = 5.0;                    // Access component
U.component(1) = 2.0;           // Alternative: y-component

tensor gradU(                   // Velocity gradient
    1.0, 0.5, 0.0,             // Row 0
    0.5, 2.0, 0.3,             // Row 1
    0.0, 0.3, 1.5              // Row 2
);

symmTensor S(                  // Strain rate tensor
    1.0,                       // xx
    0.5,                       // xy
    0.0,                       // xz
    2.0,                       // yy
    0.3,                       // yz
    1.5                        // zz
);
```

---

## 2. Transformation Rules

### 📐 แนวคิดสำคัญ

**Transformation Rules** บอกว่า quantity เหล่านี้เปลี่ยนอย่างไรภายใต้การหมุนระบบพิกัด (coordinate rotation)

### 🔬 Mathematical Foundation

**Coordinate Rotation:**
- R คือ rotation matrix (orthogonal: R·Rᵀ = I)
- det(R) = 1 สำหรับ proper rotation

**Transformation Properties:**

| Type | Transformation | Physical Meaning |
|------|----------------|------------------|
| `scalar` | φ' = φ (invariant) | Independent of coordinate system |
| `vector` | v' = R·v | Components change, magnitude preserved |
| `tensor` | T' = R·T·Rᵀ | Double contraction with rotation |

### 💡 Why This Matters in CFD

**Example: Stress Tensor**
```cpp
// Lab frame
tensor sigma_lab(100, 0, 0, 0, 50, 0, 0, 0, 20);

// Rotate 45° around z-axis
tensor R( cos45, sin45, 0,
         -sin45, cos45, 0,
          0,     0,     1);

tensor sigma_rotated = R & sigma_lab & R.T();
// Result: Different components, SAME physical state
```

**Application:**
- ✅ **Verification:** Invariants เท่ากันในทุกระบบพิกัด
- ✅ **Boundary Conditions:** รู้จัก traction vector ใช้ rotation rules
- ✅ **Post-processing:** Principal stresses ใช้ eigenvalue analysis

### 🔑 Key Insight

```
Physical Law ระบุ:  τ = n·σ
                         ↓
              ใช้ transformation rules
                         ↓
           Valid ในทุกระบบพิกัด
```

---

## 3. Tensor Invariants

### 📊 แนวคิดพื้นฐาน

**Invariants** = Quantities ที่ไม่เปลี่ยนค่าภายใต้ coordinate rotation

### 🔢 Principal Invariants

| Invariant | Formula | Mathematical Meaning | Code | Physical Application |
|-----------|---------|---------------------|------|----------------------|
| I₁ | tr(T) | Sum of diagonal elements | `tr(T)` | Mean stress, pressure |
| I₂ | ½(tr²(T) - tr(T²)) | Sum of principal minors | `invariantII(T)` | Deviatoric stress magnitude |
| I₃ | det(T) | Product of eigenvalues | `det(T)` | Volume change, Jacobian |

### 🧮 Calculation Details

**Trace (First Invariant):**
```
tr(T) = T_xx + T_yy + T_zz
```

**Second Invariant:**
```
I₂(T) = ½[(tr(T))² - tr(T²)]

For symmetric tensor S:
I₂(S) = S_xx·S_yy + S_yy·S_zz + S_zz·S_xx 
       - S_xy² - S_yz² - S_zx²
```

**Third Invariant:**
```
det(T) = T_xx(T_yy·T_zz - T_yz·T_zy) 
       - T_xy(T_yx·T_zz - T_yz·T_zx) 
       + T_xz(T_yx·T_zy - T_yy·T_zx)
```

### 💻 Practical Applications

#### Application 1: Strain Rate Magnitude

```cpp
// Calculate strain rate tensor
symmTensor S = symm(fvc::grad(U));

// Second invariant
scalar I2 = invariantII(S);

// Strain rate magnitude (used in k-epsilon model)
scalar strainRate = sqrt(2.0 * I2);

// In turbulence model
Info << "Strain rate: " << strainRate << endl;
```

**Physical Meaning:**
- I₂ = 0  →  Rigid body rotation (no deformation)
- I₂ > 0  →  Shear deformation present

#### Application 2: Principal Stresses

```cpp
// Stress tensor
symmTensor sigma = ...;

// Invariants
scalar I1 = tr(sigma);          // Mean stress × 3
scalar I2 = invariantII(sigma); // Deviatoric magnitude
scalar I3 = det(sigma);         // Volume change indicator

// Principal stresses from characteristic equation
// σ³ - I₁σ² + I₂σ - I₃ = 0
vector eigenVals = eigenValues(sigma);
scalar sigma1 = eigenVals.x();  // Maximum principal stress
scalar sigma2 = eigenVals.y();  // Intermediate
scalar sigma3 = eigenVals.z();  // Minimum
```

#### Application 3: Yield Criteria

```cpp
// von Mises stress (yield criterion)
scalar vonMises = sqrt(3.0 * invariantII(dev(sigma)));

if (vonMises > yieldStress) {
    Info << "Material yielding!" << endl;
}
```

### 🔑 Connection to Turbulence Modeling

**k-ε Model:**
```cpp
// Production term: P = 2ν_t S²
// where S² = 2I₂(S)

symmTensor S = symm(fvc::grad(U));
scalar magS = sqrt(2.0 * invariantII(S));
volScalarField P = 2.0 * nut * magS * magS;
```

---

## 4. Tensor Decomposition

### 📐 แนวคิดสำคัญ

**Tensor Decomposition** = การแยก tensor เป็นส่วนประกอบที่มีความหมายทางกายภาพ

### 🔢 Mathematical Framework

#### General Decomposition

$$T = \underbrace{\frac{1}{3}tr(T)I}_{\text{Spherical}} + \underbrace{dev(T)}_{\text{Deviatoric}}$$

**Where:**
- Spherical part: $\frac{1}{3}tr(T)I$ = Isotropic component
- Deviatoric part: $T - \frac{1}{3}tr(T)I$ = Anisotropic component

#### Velocity Gradient Decomposition

$$\nabla U = \underbrace{S}_{\text{Symmetric}} + \underbrace{\Omega}_{\text{Skew-symmetric}}$$

**Where:**
- $S = \frac{1}{2}(\nabla U + (\nabla U)^T)$ = Strain rate tensor
- $\Omega = \frac{1}{2}(\nabla U - (\nabla U)^T)$ = Rotation tensor

### 📊 Decomposition Types

| Decomposition | Code | Meaning | Trace | Physical Role |
|--------------|------|---------|-------|---------------|
| Spherical | `sph(T)` | Isotropic part | Preserved | Volume change |
| Deviatoric | `dev(T)` | Traceless part | Zero | Shape change |
| Symmetric | `symm(T)` | (T + Tᵀ)/2 | Preserved | Deformation |
| Skew-symmetric | `skew(T)` | (T - Tᵀ)/2 | Zero | Rotation |

### 💻 Code Examples

#### Example 1: Stress Decomposition

```cpp
// Total stress tensor
symmTensor sigma(100, 30, 10, 80, 20, 60);

// Spherical part (hydrostatic stress)
symmTensor sigmaSph = sph(sigma);  
// Result: (80*I) where mean stress = (100+80+60)/3 = 80

// Deviatoric part (deviatoric stress)
symmTensor sigmaDev = dev(sigma);
// Result: sigma - 80*I = [20, 30, 10, 0, 20, -20]

// Verification
scalar trDev = tr(sigmaDev);  // Should be ~0
Info << "Trace of deviatoric: " << trDev << endl;
```

**Physical Meaning:**
- Spherical: Volume change (compression/expansion)
- Deviatoric: Shape change (shear distortion)

#### Example 2: Velocity Gradient Decomposition

```cpp
// Velocity gradient
tensor gradU = fvc::grad(U);

// Strain rate tensor (symmetric part)
symmTensor S = symm(gradU);

// Rotation tensor (skew-symmetric part)
tensor Omega = skew(gradU);

// Verification: gradU = S + Omega
tensor reconstructed = S + Omega;
scalar error = mag(reconstructed - gradU);
Info << "Decomposition error: " << error << endl;
```

**Physical Interpretation:**
```
∇U  →  [S]  →  Deformation (stretching, shear)
            +
        [Ω]  →  Rigid body rotation
```

#### Example 3: Vorticity from Rotation Tensor

```cpp
// Rotation tensor Omega has components:
//     [  0   -ωz   ωy ]
// Ω = [ ωz    0   -ωx ]
//     [ -ωy  ωx    0  ]

// Vorticity vector ω = ∇ × U = 2 × vector(Omega)
tensor Omega = skew(gradU);
vector vorticity(
    -Omega.zy(),   // ωx = 2*Ω_zx
     Omega.xz(),   // ωy = 2*Ω_xy
    -Omega.yx()    // ωz = 2*Ω_yz
);

// Or simply:
volVectorField omega = fvc::curl(U);
```

### 🎯 Applications in CFD

#### Application 1: Incompressible Flow

```cpp
// For incompressible flow: tr(S) = 0
symmTensor S = symm(fvc::grad(U));
scalar divU = tr(S);

if (mag(divU) > SMALL) {
    Warning << "Flow not incompressible! divU = " << divU << endl;
}
```

#### Application 2: Turbulence Modeling

```cpp
// Reynolds stress decomposition
// R = 2/3*k*I - 2*ν_t*S
//    [Spherical]   [Deviatoric]

volScalarField k = turbulence->k();  // TKE
volScalarField nut = turbulence->nut();  // Eddy viscosity
symmTensor S = symm(fvc::grad(U));

symmTensor R = (2.0/3.0)*k*I - 2.0*nut*S;
```

#### Application 3: Non-Newtonian Fluids

```cpp
// Power-law fluid: μ = K(ẏ)^(n-1)
// where ẏ = √(2I₂(S)) = strain rate magnitude

symmTensor S = symm(fvc::grad(U));
scalar strainRateMag = sqrt(2.0 * invariantII(S));

volScalarField mu = K * pow(strainRateMag, n - 1.0);
```

---

## 5. Tensor Products

### 📚 แนวคิดพื้นฐาน

**Tensor Products** = Operations ระหว่าง tensors ที่เปลี่ยน rank ได้

### 🔢 Product Types

| Operation | Syntax | Rank Reduction | Mathematical Form | Physical Meaning |
|-----------|--------|----------------|-------------------|------------------|
| Dot (single) | `a & b` | -1 | $a_i b_i$ (vectors) | Projection, work |
| Double dot | `A && B` | -2 | $\sum_{i,j} A_{ij} B_{ij}$ | Stress power, contraction |
| Outer | `a * b` | +1 | $a_i b_j$ | Dyadic product |
| Cross | `a ^ b` | Vector (3D only) | $\varepsilon_{ijk} a_j b_k$ | Moment, vorticity |

### 💻 Code Examples

#### Example 1: Vector Operations

```cpp
vector v1(1, 0, 0);
vector v2(0, 1, 0);

// Dot product: scalar result
scalar dotProd = v1 & v2;  // 0.0

// Cross product: vector result
vector crossProd = v1 ^ v2;  // (0, 0, 1)

// Outer product: tensor result
tensor outerProd = v1 * v2;  // [[0,1,0],[0,0,0],[0,0,0]]
```

#### Example 2: Tensor-Vector Operations

```cpp
tensor T(1, 0, 0, 0, 2, 0, 0, 0, 3);
vector v(1, 1, 1);

// Tensor-vector: vector result
vector Tv = T & v;  // (1, 2, 3)

// Vector-tensor: vector result
vector vT = v & T;  // (1, 2, 3) for symmetric T
```

#### Example 3: Tensor-Tensor Operations

```cpp
tensor A(1, 2, 3, 4, 5, 6, 7, 8, 9);
tensor B(9, 8, 7, 6, 5, 4, 3, 2, 1);

// Dot product (single contraction): tensor result
tensor C = A & B;  // Matrix multiplication

// Double dot product: scalar result
scalar s = A && B;  // Sum of element-wise products
// = 1×9 + 2×8 + ... + 9×1
```

### 🎯 Physical Applications

#### Application 1: Stress Power

```cpp
// Stress power density: Φ = σ:∇U = σ && ∇U
volSymmTensorField sigma = ...;  // Stress
volTensorField gradU = fvc::grad(U);  // Velocity gradient

volScalarField stressPower = sigma && gradU;
```

**Physical Meaning:**
- Rate of work done by stresses
- Used in energy equation

#### Application 2: Traction Vector

```cpp
// Traction on surface with normal n: t = σ·n
symmTensor sigma(...);  // Stress tensor at point
vector n(1, 0, 0);      // Surface normal (x-plane)

vector traction = sigma & n;
```

**Physical Meaning:**
- Force per unit area on surface
- Boundary condition for stress

#### Application 3: Deformation Gradient

```cpp
// Deformation gradient: F = ∇x = I + ∇u
tensor I(1, 0, 0, 0, 1, 0, 0, 0, 1);  // Identity
tensor gradU = fvc::grad(U);  // Displacement gradient
tensor F = I + gradU;  // Deformation gradient
```

### 🔑 Rank Rules

```
Rank(a) × Rank(b) → Operation:
Vector(1) & Vector(1) → Scalar(0)  [dot]
Vector(1) ^ Vector(1) → Vector(1) [cross]
Vector(1) * Vector(1) → Tensor(2)  [outer]
Tensor(2) & Vector(1) → Vector(1)  [contraction]
Tensor(2) & Tensor(2) → Tensor(2)  [dot]
Tensor(2) && Tensor(2) → Scalar(0) [double dot]
```

---

## 6. Eigenvalue Problems

### 📐 แนวคิดพื้นฐาน

**Eigenvalue Problem:** หาค่า λ และ vector v ที่ satisfy:
$$T · v = λ · v$$

### 🔍 Physical Meaning

| Application | Tensor | Eigenvalues | Eigenvectors |
|-------------|--------|-------------|--------------|
| Stress analysis | σ | Principal stresses | Principal directions |
| Strain analysis | ε | Principal strains | Principal axes |
| Turbulence | R | Normal stresses | Principal stress directions |
| Inertia | I | Principal moments | Principal axes |

### 💻 Code Examples

#### Example 1: Principal Stresses

```cpp
// Stress tensor at a point
symmTensor sigma(
    100e6,  // σ_xx [Pa]
    30e6,   // τ_xy
    10e6,   // τ_xz
    80e6,   // σ_yy
    20e6,   // τ_yz
    60e6    // σ_zz
);

// Calculate eigenvalues (principal stresses)
vector principalStresses = eigenValues(sigma);
scalar sigma1 = principalStresses.x();  // Maximum (σ₁)
scalar sigma2 = principalStresses.y();  // Intermediate (σ₂)
scalar sigma3 = principalStresses.z();  // Minimum (σ₃)

// Calculate eigenvectors (principal directions)
tensor principalDirs = eigenVectors(sigma);
vector dir1 = principalDirs.x();  // Direction of σ₁
vector dir2 = principalDirs.y();  // Direction of σ₂
vector dir3 = principalDirs.z();  // Direction of σ₃

// Verification
Info << "Principal stresses [Pa]: " << principalStresses << endl;
Info << "Principal direction 1: " << dir1 << endl;

// Check invariants
scalar I1_calc = sigma1 + sigma2 + sigma3;
scalar I1_actual = tr(sigma);
Info << "I₁ verification: " << I1_calc << " vs " << I1_actual << endl;
```

#### Example 2: Von Mises Stress

```cpp
// Von Mises stress from principal stresses
scalar sigma1 = principalStresses.x();
scalar sigma2 = principalStresses.y();
scalar sigma3 = principalStresses.z();

scalar vonMises = sqrt(
    0.5 * (
        pow(sigma1 - sigma2, 2) +
        pow(sigma2 - sigma3, 2) +
        pow(sigma3 - sigma1, 2)
    )
);

// Alternative: from invariants
scalar vonMises_alt = sqrt(3.0 * invariantII(dev(sigma)));

Info << "Von Mises stress: " << vonMises << " Pa" << endl;
```

#### Example 3: Maximum Shear Stress

```cpp
// Maximum shear stress (Tresca criterion)
scalar tauMax = 0.5 * (sigma1 - sigma3);

// Direction: 45° from principal planes
scalar shearYield = tauMax / yieldShearStress;
if (shearYield > 1.0) {
    Warning << "Yielding according to Tresca!" << endl;
}
```

### 🎯 Applications in CFD

#### Application 1: Turbulent Kinetic Energy

```cpp
// Reynolds stress eigenvalues
symmTensor R = ...;  // Reynolds stress tensor
vector eigenR = eigenValues(R);

// Check realizability: all eigenvalues ≥ 0
if (eigenR.x() < 0 || eigenR.y() < 0 || eigenR.z() < 0) {
    Warning << "Non-realizable turbulence!" << endl;
}

// TKE from trace
scalar k = 0.5 * tr(R);
```

#### Application 2: Strain Rate Analysis

```cpp
// Principal strain rates
symmTensor S = symm(fvc::grad(U));
vector strainRates = eigenValues(S);

// Volumetric strain rate
scalar volStrain = tr(S);  // Should be 0 for incompressible

// Maximum shear strain rate
scalar maxShearStrain = 0.5 * (strainRates.x() - strainRates.z());
```

### 📊 Geometric Interpretation

```
Stress Ellipsoid:
  σ₁  →  Semi-major axis
  σ₂  →  Intermediate axis
  σ₃  →  Semi-minor axis
  
Principal directions → Ellipsoid orientation
```

---

## 7. Common Operations in CFD

### 🎯 การคำนวณที่ใช้บ่อยใน OpenFOAM

#### 7.1 Strain Rate Tensor

**Mathematical Definition:**
$$S = \frac{1}{2}\left(\nabla U + (\nabla U)^T\right)$$

**Component Form:**
$$S_{ij} = \frac{1}{2}\left(\frac{\partial u_i}{\partial x_j} + \frac{\partial u_j}{\partial x_i}\right)$$

**Code Implementation:**
```cpp
// Method 1: Explicit
volTensorField gradU = fvc::grad(U);
volSymmTensorField S = 0.5 * (gradU + gradU.T());

// Method 2: Using symm()
volSymmTensorField S = symm(fvc::grad(U));

// Method 3: With cell mask (for wall functions)
volSymmTensorField S = symm(fvc::grad(U));
```

**Physical Interpretation:**
- Diagonal components: Normal strain rates (stretching/compression)
- Off-diagonal: Shear strain rates
- Incompressible: tr(S) = 0

#### 7.2 Vorticity

**Mathematical Definition:**
$$\omega = \nabla \times U$$

**Component Form:**
$$\omega_x = \frac{\partial w}{\partial y} - \frac{\partial v}{\partial z}$$
$$\omega_y = \frac{\partial u}{\partial z} - \frac{\partial w}{\partial x}$$
$$\omega_z = \frac{\partial v}{\partial x} - \frac{\partial u}{\partial y}$$

**Code Implementation:**
```cpp
// Method 1: Built-in curl
volVectorField omega = fvc::curl(U);

// Method 2: Manual calculation
volTensorField gradU = fvc::grad(U);
volVectorField omega(
    -gradU.zy(),  // ∂w/∂y - ∂v/∂z
     gradU.xz(),  // ∂u/∂z - ∂w/∂x
    -gradU.yx()   // ∂v/∂x - ∂u/∂y
);

// Method 3: From skew-symmetric part
tensor Omega = skew(gradU);
vector omega(2*Omega.zy(), -2*Omega.xz(), 2*Omega.yx());
```

**Applications:**
- Vortex detection: Q-criterion, λ₂-criterion
- Turbulence modeling: Vorticity magnitude
- Flow visualization: Vortex cores

#### 7.3 Q-Criterion (Vortex Detection)

**Mathematical Definition:**
$$Q = \frac{1}{2}\left(||\Omega||^2 - ||S||^2\right)$$

**Code Implementation:**
```cpp
volTensorField gradU = fvc::grad(U);
volSymmTensorField S = symm(gradU);      // Strain rate
volTensorField Omega = skew(gradU);      // Rotation tensor

scalar magS2 = S && S;                    // ||S||²
scalar magOmega2 = Omega && Omega;        // ||Ω||²

volScalarField Q = 0.5 * (magOmega2 - magS2);

// Iso-surface Q > 0 shows vortex cores
```

**Physical Meaning:**
- Q > 0: Rotation dominates → Vortex region
- Q < 0: Strain dominates → Shear region

#### 7.4 Reynolds Stress Decomposition

**Mathematical Framework:**
$$R = \underbrace{\frac{2}{3}k I}_{\text{Isotropic}} + \underbrace{a}_{\text{Anisotropic}}$$

**Code Implementation:**
```cpp
// Reynolds stress from k-ε model
volScalarField k = turbulence->k();
volScalarField epsilon = turbulence->epsilon();
volScalarField nut = turbulence->nut();

// Isotropic part
symmTensor R_iso = (2.0/3.0) * k * I;

// Anisotropic part (deviatoric)
volSymmTensorField S = symm(fvc::grad(U));
symmTensor R_aniso = -2.0 * nut * S;

// Total Reynolds stress
symmTensor R = R_iso + R_aniso;
```

#### 7.5 Turbulent Dissipation Rate

**Mathematical Definition:**
$$\varepsilon = 2\nu \overline{S_{ij} S_{ij}}$$

**Code Implementation:**
```cpp
// Mean strain rate
volSymmTensorField S = symm(fvc::grad(U));

// Dissipation rate calculation
volScalarField epsilon = 2.0 * nu * (S && S);

// For turbulent flow (using eddy viscosity)
volScalarField epsilon_turb = 2.0 * nut * (S && S);
```

### 📋 Operation Reference Table

| Operation | Code | Formula | Application |
|-----------|------|---------|-------------|
| Strain rate | `symm(gradU)` | $\frac{1}{2}(\nabla U + \nabla U^T)$ | Turbulence modeling |
| Vorticity | `fvc::curl(U)` | $\nabla \times U$ | Vortex detection |
| Magnitude | `mag(S)` | $\sqrt{S:S}$ | Scaling |
| Deviatoric | `dev(T)` | $T - \frac{1}{3}tr(T)I$ | Shear stress |
| Spherical | `sph(T)` | $\frac{1}{3}tr(T)I$ | Pressure |
| Trace | `tr(T)` | $\sum T_{ii}$ | Invariants |
| Determinant | `det(T)` | - | Jacobian |
| Inverse | `inv(T)` | $T^{-1}$ | Transformation |
| Eigenvalues | `eigenValues(T)` | - | Principal values |

---

## 8. Best Practices & Common Pitfalls

### ✅ Best Practices

#### 1. Choose Correct Tensor Type

```cpp
// ✅ Use symmTensor for symmetric quantities
symmTensor S = symm(fvc::grad(U));  // Correct

// ❌ Don't use full tensor when symmetric is sufficient
tensor S_full = fvc::grad(U);  // Wastes memory
```

#### 2. Verify Tensor Properties

```cpp
// Verify decomposition
tensor gradU = fvc::grad(U);
symmTensor S = symm(gradU);
tensor Omega = skew(gradU);

tensor reconstructed = S + Omega;
scalar error = mag(reconstructed - gradU);

if (error > 1e-10) {
    Warning << "Decomposition error: " << error << endl;
}
```

#### 3. Use Invariants for Verification

```cpp
// Invariants should be coordinate-independent
symmTensor S = ...;
scalar I1 = tr(S);
scalar I2 = invariantII(S);
scalar I3 = det(S);

// After rotation
symmTensor S_rotated = R & S & R.T();
scalar I1_rot = tr(S_rotated);

if (mag(I1 - I1_rot) > 1e-10) {
    FatalError << "Invariant not preserved!" << exit(FatalError);
}
```

#### 4. Check Physical Realizability

```cpp
// Eigenvalues of Reynolds stress must be ≥ 0
vector eigenR = eigenValues(R);
if (eigenR.x() < 0 || eigenR.y() < 0 || eigenR.z() < 0) {
    Warning << "Non-realizable turbulence state!" << endl;
}
```

### ❌ Common Pitfalls

#### Pitfall 1: Confusing Strain Rate with Velocity Gradient

```cpp
// ❌ WRONG: Using full gradient
tensor gradU = fvc::grad(U);
scalar strainMag = mag(gradU);  // Includes rotation

// ✅ CORRECT: Use symmetric part
symmTensor S = symm(gradU);
scalar strainMag = sqrt(2.0 * invariantII(S));
```

#### Pitfall 2: Forgetting Deviatoric Part

```cpp
// ❌ WRONG: Total stress
symmTensor sigma = ...;

// ✅ CORRECT: Deviatoric stress for shear
symmTensor sigmaDev = dev(sigma);
scalar shearStress = mag(sigmaDev);
```

#### Pitfall 3: Wrong Product Type

```cpp
// ❌ WRONG: Using single dot for double contraction
scalar s = A & B;  // Wrong type (tensor result)

// ✅ CORRECT: Use double dot
scalar s = A && B;  // Scalar result
```

#### Pitfall 4: Neglecting Coordinate Systems

```cpp
// ❌ WRONG: Comparing invariants without checking transformation
scalar I1_original = tr(T);

// After coordinate rotation
tensor T_rot = R & T & R.T();
scalar I1_rotated = tr(T_rot);

// ✅ CORRECT: Should be equal
assert(mag(I1_original - I1_rotated) < SMALL);
```

#### Pitfall 5: Trace Miscalculation

```cpp
// ❌ WRONG: Manually summing diagonal
scalar trace = T.xx() + T.yy() + T.zz();

// ✅ CORRECT: Use built-in function
scalar trace = tr(T);
```

---

## 🔑 Key Takeaways

### 📌 Essential Concepts

1. **Tensor Rank Hierarchy:**
   - Rank 0 (scalar): 1 component, invariant
   - Rank 1 (vector): 3 components, transforms as v' = R·v
   - Rank 2 (tensor): 9 components, transforms as T' = R·T·Rᵀ

2. **Invariants:**
   - I₁ = tr(T): First invariant (mean)
   - I₂ = ½(tr²(T) - tr(T²)): Second invariant (deviatoric magnitude)
   - I₃ = det(T): Third invariant (volume change)

3. **Decomposition:**
   - Spherical: $\frac{1}{3}tr(T)I$ = isotropic part
   - Deviatoric: $T - \frac{1}{3}tr(T)I$ = traceless part
   - Symmetric: (T + Tᵀ)/2 = deformation
   - Skew: (T - Tᵀ)/2 = rotation

4. **Products:**
   - Single dot (&): Rank -1
   - Double dot (&&): Rank -2
   - Cross (^): Vector in 3D
   - Outer (*): Rank +1

### 🎯 Critical Skills

**✅ คุณสามารถ:**
1. เลือก tensor type ที่ถูกต้อง (scalar, vector, tensor, symmTensor)
2. คำนวณ strain rate, vorticity ได้ถูกต้อง
3. ใช้ invariants ตรวจสอบ transformation correctness
4. Decompose tensors แยก isotropic/anisotropic
5. แก้ eigenvalue problems หา principal values

**🔧 ใช้ได้แม่นยำ:**
- `symm(gradU)` → Strain rate
- `fvc::curl(U)` → Vorticity
- `dev(T)` → Deviatoric stress
- `eigenValues(T)` → Principal stresses
- `invariantII(T)` → Magnitude measures

### 🚀 Practical Applications

**CFD Implementation:**
- Turbulence modeling: strain rate magnitude
- Stress analysis: principal stresses, von Mises
- Vortex detection: Q-criterion, λ₂
- Post-processing: invariant verification

**Cross-Reference:**
- Foundation: 03_Dimensioned_Types_Intro.md (tensor types)
- Application: 06_Fields_GeometricFields.md (field operations)
- Advanced: 04_Mesh_Classes.md (gradient calculation)

---

## 📖 เอกสารที่เกี่ยวข้อง

### ในบทเดียวกัน
- **ภาพรวม:** [00_Overview.md](00_Overview.md) - Chapter structure
- **Design Philosophy:** [02_Design_Philosophy.md](02_Design_Philosophy.md) - Why types matter

### ที่เกี่ยวข้อง
- **Dimensioned Types:** [03_Dimensioned_Types_Intro.md](03_Dimensioned_Types_Intro.md) - Type system mechanics
- **Fields:** [06_Fields_GeometricFields.md](06_Fields_GeometricFields.md) - Field-level operations

### Module Cross-Reference
- **Turbulence:** MODULE_03/CONTENT/04_TURBULENCE_MODELING - k-ε, k-ω models
- **Stress Analysis:** MODULE_03/CONTENT/05_STRESS_ANALYSIS - Solid mechanics
- **Numerical Methods:** MODULE_02/CONTENT/04_FINITE_VOLUME_METHOD - Gradient schemes

---

## 🧪 Exercises

<details>
<summary><b>Exercise 1: Strain Rate Analysis</b></summary>

**Task:** คำนวณ strain rate magnitude และ principal strain rates

```cpp
// Given velocity field U
volVectorField U = ...;

// TODO: Calculate strain rate tensor
volSymmTensorField S = ...;

// TODO: Calculate strain rate magnitude
scalar magS = ...;

// TODO: Find principal strain rates
vector principalStrains = ...;

// Expected output:
// Strain rate magnitude: [value] s⁻¹
// Principal strains: [ε₁, ε₂, ε₃]
```

**Solution:**
```cpp
volSymmTensorField S = symm(fvc::grad(U));
scalar magS = sqrt(2.0 * invariantII(S));
vector principalStrains = eigenValues(S);
```
</details>

<details>
<summary><b>Exercise 2: Vortex Detection</b></summary>

**Task:** Implement Q-criterion for vortex visualization

```cpp
// TODO: Calculate Q = ½(||Ω||² - ||S||²)
volTensorField gradU = fvc::grad(U);
volScalarField Q = ...;

// Extract iso-surface where Q > 0
// TODO: Identify vortex cores
```

**Solution:**
```cpp
volSymmTensorField S = symm(gradU);
volTensorField Omega = skew(gradU);
volScalarField Q = 0.5 * ((Omega && Omega) - (S && S));
```
</details>

<details>
<summary><b>Exercise 3: Stress Decomposition</b></summary>

**Task:** Decompose stress tensor and calculate von Mises stress

```cpp
symmTensor sigma(...);

// TODO: Extract spherical part (hydrostatic stress)
symmTensor sigma_hydro = ...;

// TODO: Extract deviatoric part (shear stress)
symmTensor sigma_shear = ...;

// TODO: Calculate von Mises stress
scalar vonMises = ...;
```

**Solution:**
```cpp
symmTensor sigma_hydro = sph(sigma);
symmTensor sigma_shear = dev(sigma);
scalar vonMises = sqrt(3.0 * invariantII(sigma_shear));
```
</details>