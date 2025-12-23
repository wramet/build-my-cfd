# Introduction to Vector Calculus in OpenFOAM

![[calculus_bridge_nabla.png]]
`A bridge connecting a cloud of abstract mathematical symbols (∇, ∇·, ∇²) to a concrete 3D mesh. On the mesh side, the symbols turn into arrows passing through faces, scientific textbook diagram, clean vector line art, white background, high definition, flat design, educational infographic --ar 16:9`

In computational fluid dynamics (CFD), we work with equations filled with mathematical operators like **$\nabla$** (Nabla/del), **$\nabla^2$** (Laplacian), **$\nabla \cdot$** (divergence), and **$\nabla \times$** (curl). OpenFOAM transforms these abstract symbols into practical, executable functions through two primary namespaces: **`fvc`** (finite volume calculus - explicit) and **`fvm`** (finite volume method - implicit).

## 📋 Section Overview

This section covers the fundamental **vector calculus operations** that form the mathematical backbone of computational fluid dynamics:

- **Gradient, Divergence, Curl, and Laplacian operations**
- **Finite Volume discretization methods**
- **Explicit vs Implicit operator distinctions**

```mermaid
flowchart LR
    V["Volume Integral: ∫∇·U dV"] -->|"Gauss Theorem"| S["Surface Integral: ∮U·dA"]
    S -->|"Discretization"| Sum["Sum: Σ(Uf · Sf)"]

    style S fill:#fff9c4,stroke:#fbc02d,stroke-width:2px
    style Sum fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
```
> **Figure 1:** พื้นฐานการคำนวณในวิธีปริมาตรจำกัดที่ใช้ทฤษฎีบทของเกาส์ในการเปลี่ยนรูปแบบอินทิกรัลเชิงปริมาตรให้กลายเป็นการหาผลรวมเชิงพีชคณิตบนหน้าเซลล์ที่คำนวณได้จริงความปลอดภัยทางฟิสิกส์ไม่ส่งผลกระทบต่อความเร็วในการจำลอง ผ่านการใช้พลังของ C++ Template Metaprogramming ในการตรวจสอบความสอดคล้องทางมิติทั้งหมดที่ขั้นตอนการคอมไพล์โปรแกรมเพียงครั้งเดียว

## 🏗️ The Foundation: Gauss's Divergence Theorem

OpenFOAM relies on **Gauss's Divergence Theorem** to convert volume integrals of derivatives into surface flux summations. This is the cornerstone of the Finite Volume Method (FVM):

![[of_gauss_theorem_visual.png]]
`A 3D control volume (cell) with arrows showing the divergence of a vector field being converted to a summation of fluxes across all faces, scientific textbook diagram, clean vector line art, white background, high definition, flat design, educational infographic --ar 16:9`

$$\int_V \nabla \cdot \mathbf{U} \, \mathrm{d}V = \oint_A \mathbf{U} \cdot \mathrm{d}\mathbf{A} \approx \sum_f \mathbf{U}_f \cdot \mathbf{S}_f$$

**where:**
- $V$ = control volume
- $A$ = surface area
- $\mathbf{U}_f$ = value interpolated to face $f$
- $\mathbf{S}_f = \mathbf{n}_f A_f$ = face area vector (normal × area)
- The sum $\sum_f$ runs over all faces of the cell

This mechanism enables OpenFOAM to accurately compute calculus on complex meshes while ==exactly preserving conservation laws==—critical for reliable CFD simulations.

## 🔧 Implementation: The `fvc::` Namespace

In OpenFOAM, vector calculus operations are implemented through the **`fvc::`** namespace for **explicit** calculations. These operators evaluate derivative terms directly using known field values from the current time step.

### 📊 What Makes `fvc::` Explicit?

Explicit operators (`fvc::`):
- **Evaluate derivative terms directly** using current field values
- **Use known values** from the current iteration/time step
- **Do not require solving** linear systems
- **Are essential for**: post-processing, source term evaluation, and explicit time integration schemes

### 🔍 The Explicit vs Implicit Distinction

> [!INFO] Key Concept
> The difference between `fvc::` (explicit) and `fvm::` (implicit) operators is fundamental to OpenFOAM:
> - **`fvc::grad(p)`** returns a `volVectorField` containing $\nabla p$ at cell centers
> - **`fvm::laplacian(D, T)`** adds diffusion terms to a system matrix for later solving

| Aspect | **Explicit (`fvc::`)** | **Implicit (`fvm::`)** |
|--------|------------------------|------------------------|
| **Computation** | Direct evaluation from known fields | Matrix coefficient construction |
| **Result** | Field value (evaluated immediately) | Matrix equation (requires solving) |
| **Use Case** | Post-processing, source terms, explicit time stepping | Implicit time stepping, steady-state problems |
| **Stability** | May require small time steps (CFL condition) | Generally unconditionally stable |
| **Cost per evaluation** | Low (O(N)) | Higher (matrix assembly + solve) |

## 🎯 The Four Fundamental Operators

### 1️⃣ **Gradient** (`∇φ`)

Computes the spatial rate of change of a field. Fundamental for transport phenomena.

$$\nabla \phi = \frac{\partial \phi}{\partial x}\mathbf{i} + \frac{\partial \phi}{\partial y}\mathbf{j} + \frac{\partial \phi}{\partial z}\mathbf{k}$$

**Physical meaning:**
- **Scalar field** → **Vector field** (direction of steepest ascent)
- **Vector field** → **Tensor field** (velocity gradient tensor)

**OpenFOAM Implementation:**
```cpp
// Pressure gradient (driving force in momentum equation)
volVectorField gradP = fvc::grad(p);

// Temperature gradient (heat flux calculation)
volVectorField gradT = fvc::grad(T);

// Velocity gradient (strain rate, vorticity)
volTensorField gradU = fvc::grad(U);
```

### 2️⃣ **Divergence** (`∇·φ`)

Measures the net flux out of a control volume. ==Critical for conservation laws==.

$$\nabla \cdot \mathbf{F} = \frac{\partial F_x}{\partial x} + \frac{\partial F_y}{\partial y} + \frac{\partial F_z}{\partial z}$$

**Physical meaning:**
- **Vector field** → **Scalar field** (source/sink strength)
- **Zero divergence** = incompressible flow ($\nabla \cdot \mathbf{U} = 0$)

**OpenFOAM Implementation:**
```cpp
// Continuity check (mass conservation)
volScalarField divU = fvc::div(U);

// Momentum flux divergence
volVectorField divPhi = fvc::div(phi);

// Convective term
volScalarField convTerm = fvc::div(phi, T);
```

### 3️⃣ **Curl** (`∇×φ`)

Evaluates the rotational component of a vector field. Essential for vorticity analysis.

$$\nabla \times \mathbf{u} = \begin{vmatrix} \mathbf{i} & \mathbf{j} & \mathbf{k} \\ \frac{\partial}{\partial x} & \frac{\partial}{\partial y} & \frac{\partial}{\partial z} \\ u_x & u_y & u_z \end{vmatrix}$$

**Physical meaning:**
- **Vector field** → **Vector field** (rotation axis and magnitude)
- **Zero curl** = irrotational/potential flow

**OpenFOAM Implementation:**
```cpp
// Vorticity calculation
volVectorField vorticity = fvc::curl(U);

// Vorticity magnitude for visualization
volScalarField vorticityMag = mag(vorticity);

// Q-criterion (vortex identification)
volTensorField gradU = fvc::grad(U);
volScalarField Q = 0.5*(magSqr(skew(gradU)) - magSqr(symm(gradU)));
```

### 4️⃣ **Laplacian** (`∇²φ`)

Represents diffusion processes. Necessary for heat conduction, viscous flow, and mass diffusion.

$$\nabla^2 \phi = \nabla \cdot (\nabla \phi) = \frac{\partial^2 \phi}{\partial x^2} + \frac{\partial^2 \phi}{\partial y^2} + \frac{\partial^2 \phi}{\partial z^2}$$

**Physical meaning:**
- **Any field** → **Same type field** (diffusion smoothing)
- Combines divergence of gradient

**OpenFOAM Implementation:**
```cpp
// Thermal diffusion (heat conduction)
volScalarField laplacianT = fvc::laplacian(DT, T);

// Viscous diffusion (momentum equation)
volVectorField laplacianU = fvc::laplacian(nu, U);

// Pressure Poisson equation
fvScalarMatrix pEqn(fvm::laplacian(1/rho, p) == fvc::div(U));
```

## 🔧 Discretization Schemes

The accuracy and stability of finite volume operations depend on the **interpolation schemes** specified in `system/fvSchemes`:

### Interpolation Schemes Comparison

| Scheme | Order | Accuracy | Stability | Typical Use |
|--------|-------|----------|-----------|-------------|
| **Gauss linear** | 2nd | Good | Moderate | Laminar flow, structured meshes |
| **Gauss upwind** | 1st | Low | Very High | Turbulent flow, high Reynolds |
| **Gauss limitedLinear** | 2nd (TVD) | Good | High | General purpose, flows with shocks |
| **Gauss leastSquares** | 2nd | Better | High | Unstructured meshes |
| **QUICK** | 3rd | Very Good | Low | High-accuracy calculations |

**Example `system/fvSchemes`:**
```cpp
gradSchemes
{
    default         Gauss linear;
    grad(p)         Gauss leastSquares;  // Better on unstructured meshes
    grad(U)         Gauss fourth;        // Higher accuracy
}

divSchemes
{
    default         Gauss linear;
    div(phi,U)      Gauss linearUpwindV grad(U);  // Blended scheme
    div(phi,T)      Gauss limitedLinearV 1;       // TVD scheme
}

laplacianSchemes
{
    default         Gauss linear corrected;  // Non-orthogonal correction
}
```

## 🎯 Why This Matters: The Developer's Perspective

Understanding when to use `fvc::grad(p)` versus `fvm::laplacian(T)` can mean the difference between:

- ✅ **A solver that converges smoothly**
- ❌ **A solver that diverges**

> [!WARNING] Common Pitfall
> A small misunderstanding can lead to catastrophic failure:
> - Using `fvc::laplacian` instead of `fvm::laplacian` in an implicit solver
> - Choosing an unstable scheme for high Reynolds number flows
> - Forgetting that `fvc::` returns fields while `fvm::` builds matrices

## 📚 What You'll Learn

In this section, we'll cover:

1. **[[02_🎯_Learning_Objectives\|Learning Objectives]]** - Detailed goals for each operation
2. **[[03_Understanding_the_`fvc`_Namespace\|Understanding the fvc Namespace]]** - Deep dive into explicit operations
3. **[[04_1._Gradient_Operations\|Gradient Operations]]** - Computing spatial derivatives
4. **[[05_2._Divergence_Operations\|Divergence Operations]]** - Enforcing conservation laws
5. **[[06_3._Curl_Operations\|Curl Operations]]** - Analyzing rotational flows
6. **[[07_4._Laplacian_Operations\|Laplacian Operations]]** - Modeling diffusion processes
7. **[[08_🔧_Practical_Exercises\|Practical Exercises]]** - Hands-on implementation
8. **[[09_📈_Project_Integration\|Project Integration]]** - Real-world applications
9. **[[10_🎓_Key_Takeaways\|Key Takeaways]]** - Summary and best practices

---

**Mastering these vector calculus operations is essential for implementing accurate, stable, and efficient CFD simulations in OpenFOAM.** Each operator transforms physical laws into computable discrete forms while preserving the fundamental conservation properties that govern fluid dynamics.
