# MODULE_05 Section 05: Finite Volume Discretization
# หน่วยที่ 05 ส่วนที่ 05: การแบ่งส่วนปริมาตรจำกัด

## 1. Overview / ภาพรวม

### What is Finite Volume Discretization? / การแบ่งส่วนปริมาตรจำกัดคืออะไร?

Finite Volume Method (FVM) discretization converts partial differential equations (PDEs) into algebraic equations by:
- **Integrating** PDEs over control volumes (cells)
- **Applying** Gauss divergence theorem to convert volume integrals to surface integrals
- **Approximating** surface fluxes using interpolation schemes

วิธีการ Finite Volume (FVM) แปลงสมการอนุพันธ์ย่อยให้เป็นสมการพีชคณิตโดย:
- **อินทิเกรต** PDEs บนปริมาตรควบคุม (cells)
- **ใช้** ทฤษฎีบทเกาส์เพื่อแปลง volume integrals เป็น surface integrals
- **ประมาณค่า** การไหลผ่านพื้นผิวด้วย interpolation schemes

> **Key Insight for R410A Evaporator**: FVM conserves mass, momentum, and energy **exactly** at the discrete level, which is critical for:
> - Mass conservation during liquid-vapor phase change
> - Energy balance with latent heat transfer
> - Two-phase flow interface tracking

---

## 2. Gauss Divergence Theorem / ทฤษฎีบทเกาส์

### Mathematical Foundation / พื้นฐานคณิตศาสตร์

**⭐ The Fundamental Theorem of FVM**

> **File**: `openfoam_temp/src/finiteVolume/finiteVolume/fvc/fvcDiv.C`
> **Lines**: 42-56

Gauss theorem converts volume integrals to surface integrals:

$$
\int_{V_P} \nabla \cdot \mathbf{\phi} \, dV = \oint_{\partial V_P} \mathbf{\phi} \cdot \mathbf{n} \, dS
$$

For a discrete cell $P$ with $N$ faces:

$$
\int_{V_P} \nabla \cdot \mathbf{\phi} \, dV \approx \sum_{f=1}^{N} \mathbf{\phi}_f \cdot \mathbf{S}_f
$$

where:
- $\mathbf{S}_f = \mathbf{n}_f S_f$ is the **face area vector**
- $\mathbf{\phi}_f$ is the flux interpolated to face $f$
- $N$ is the number of faces of cell $P$

### OpenFOAM Implementation / การนำไปใช้ใน OpenFOAM

```cpp
// File: src/finiteVolume/finiteVolume/fvc/fvcDiv.C
// Lines 42-56

template<class Type>
tmp<VolField<typename innerProduct<vector, Type>::type>>
div
(
    const SurfaceField<Type>& ssf
)
{
    // Calculate surface integral: sum(phi_f * S_f)
    // Uses Gauss theorem: int(div(phi) dV) = sum(phi_f . S_f)

    return tmp<VolField<typename innerProduct<vector, Type>::type>>
    (
        new VolField<typename innerProduct<vector, Type>::type>
        (
            IOobject
            (
                "div(" + ssf.name() + ')',
                ssf.instance(),
                ssf.mesh(),
                IOobject::NO_READ,
                IOobject::NO_WRITE
            ),
            ssf.mesh(),
            dimensioned<typename innerProduct<vector, Type>::type>
            (
                "0",
                ssf.dimensions()/dimVol,
                Zero
            ),
            calculatedFvPatchScalarField::typeName
        )
    );

    // Implementation loops over all faces and accumulates flux
}
```

**⭐ Key Points**:
- Face area vector $\mathbf{S}_f$ is **precomputed** and stored in mesh
- Divergence is **exact** for constant fields (conservation property)
- Works for **any** cell shape (hex, tet, polyhedron)

---

## 3. Time Derivative Discretization / การแบ่งส่วนอนุพันธ์เชิงเวลา

### First-Order Euler Schemes / รูปแบบออยเลอร์อันดับหนึ่ง

**⭐ Euler Implicit Scheme**

> **File**: `openfoam_temp/src/finiteVolume/finiteVolume/ddtSchemes/EulerDdtScheme/EulerDdtScheme.H`
> **Lines**: 27-29

```cpp
// First-order Euler implicit: backward difference
// (phi_new - phi_old) / delta_t
```

$$
\frac{\partial \phi}{\partial t} \approx \frac{\phi^{n+1} - \phi^n}{\Delta t}
$$

**Characteristics**:
- **First-order accurate**: $O(\Delta t)$
- **Unconditionally stable** for diffusion problems
- **Implicit**: Requires matrix solution

```cpp
// File: src/finiteVolume/finiteVolume/fvm/fvmDdt.C
// Lines 78-95 (Euler implicit implementation)

template<class Type>
tmp<fvMatrix<Type>> ddt
(
    const VolField<Type>& vf
)
{
    // Euler implicit: (phi_new - phi_old) / delta_t
    // Matrix form: (1/delta_t) * phi_new = (1/delta_t) * phi_old

    const fvMesh& mesh = vf.mesh();

    scalarField rDeltaT =
        1.0/mesh.time().deltaTValue();

    tmp<fvMatrix<Type>> tfvm
    (
        new fvMatrix<Type>
        (
            vf,
            vf.dimensions()/dimTime
        )
    );

    fvMatrix<Type>& fvm = tfvm.ref();

    fvm.diag() = rDeltaT * mesh.V();        // Diagonal: V_P / delta_t
    fvm.source() = rDeltaT * mesh.V() * vf.oldTime().primitiveField();  // Source: V_P * phi_old / delta_t

    return tfvm;
}
```

### Second-Order Schemes / รูปแบบอันดับสอง

**⭐ Backward Scheme**

$$
\frac{\partial \phi}{\partial t} \approx \frac{3\phi^{n+1} - 4\phi^n + \phi^{n-1}}{2\Delta t}
$$

**Characteristics**:
- **Second-order accurate**: $O(\Delta t^2)$
- **More accurate** for transient simulations
- **Requires** 2 previous time steps

### R410A Evaporator Application / การนำไปใช้กับเครื่องระเหย R410A

For R410A evaporation simulation:

```cpp
// Time integration for phase fraction (alpha)
// Crank-Nicolson: second-order, blends implicit and explicit

ddtSchemes
{
    default         backward;  // Second-order for accuracy
    ddtrho(alpha)   Euler;     // First-order for stability
}
```

**⚠️ Stability Considerations**:
- **Phase change** requires small time steps during rapid evaporation
- **Heat transfer** benefits from second-order accuracy
- **VOF equation** may need first-order for boundedness

---

## 4. Spatial Derivative Discretization / การแบ่งส่วนอนุพันธ์เชิงพื้นที่

### 4.1 Gradient Schemes / รูปแบบเกรเดียนต์

### Gauss Gradient Scheme / รูปแบบเกรเดียนต์เกาส์

**⭐ Basic Second-Order Gradient**

> **File**: `openfoam_temp/src/finiteVolume/finiteVolume/gradSchemes/gaussGrad/gaussGrad.H`
> **Lines**: 27-29

$$
\nabla \phi \approx \frac{1}{V_P} \sum_f \phi_f \mathbf{S}_f
$$

where $\phi_f$ is interpolated to the face using a scheme like **linear** (central differencing):

$$
\phi_f = f_x \phi_P + (1 - f_x) \phi_N
$$

where $f_x$ is the interpolation factor.

```cpp
// File: src/finiteVolume/finiteVolume/gradSchemes/gaussGrad/gaussGrad.C
// Lines 65-82

tmp<VolField<vector>> gaussGrad<scalar>::calcGrad
(
    const VolField<scalar>& vsf,
    const word& name
) const
{
    // Gauss theorem: grad(phi) = sum(phi_f * S_f) / V_P

    tmp<VolField<vector>> tfld
    (
        new VolField<vector>
        (
            IOobject
            (
                "grad(" + vsf.name() + ')',
                vsf.instance(),
                vsf.mesh(),
                IOobject::NO_READ,
                IOobject::NO_WRITE
            ),
            vsf.mesh(),
            dimensionedVector("0", vsf.dimensions()/dimLength, Zero)
        )
    );

    VolField<vector>& grad = tfld.ref();

    // Interpolate phi to faces (linear by default)
    SurfaceField<scalar> phi_f = tinterpScheme_().interpolate(vsf);

    // Sum over faces: grad = sum(phi_f * S_f) / V_P
    const fvMesh& mesh = vsf.mesh();
    const labelUList& owner = mesh.owner();
    const labelUList& neighbour = mesh.neighbour();

    const vectorField& Sf = mesh.Sf();

    forAll(owner, facei)
    {
        label own = owner[facei];
        label nei = neighbour[facei];

        grad[own] += phi_f[facei] * Sf[facei];
        grad[nei] -= phi_f[facei] * Sf[facei];  // Opposite sign for neighbor
    }

    // Divide by cell volumes
    grad.primitiveFieldRef() /= mesh.V().primitiveField();

    // Correct boundary conditions
    correctBoundaryConditions(vsf, grad);

    return tfld;
}
```

### 4.2 Divergence Schemes / รูปแบบไดเวอร์เจนซ์

### Convection-Diffusion Divergence / การไหลแบบเกาส์

**⭐ General Divergence Form**

> **File**: `openfoam_temp/src/finiteVolume/finiteVolume/fvc/fvcDiv.H`
> **Lines**: 27-29

$$
\nabla \cdot (\rho \mathbf{U} \phi) = \frac{1}{V_P} \sum_f (\rho \mathbf{U} \phi)_f \cdot \mathbf{S}_f
$$

where the face flux is:

$$
(\rho \mathbf{U} \phi)_f = \dot{m}_f \phi_f
$$

and $\dot{m}_f = (\rho \mathbf{U})_f \cdot \mathbf{S}_f$ is the **mass flux**.

```cpp
// Divergence of volField using Gauss theorem
// File: src/finiteVolume/finiteVolume/convectionSchemes/gaussConvectionScheme/gaussConvectionScheme.C
// Lines 85-105

tmp<VolField<Type>> gaussConvectionScheme<Type>::fvcDiv
(
    const surfaceScalarField& faceFlux,
    const VolField<Type>& vf
) const
{
    // div(phi * U) = sum(phi_f * flux_f) / V_P

    tmp<VolField<Type>> tfvm
    (
        new VolField<Type>
        (
            IOobject
            (
                "div(" + faceFlux.name() + ',' + vf.name() + ')',
                vf.instance(),
                vf.mesh(),
                IOobject::NO_READ,
                IOobject::NO_WRITE
            ),
            vf.mesh(),
            vf.dimensions()*faceFlux.dimensions()/dimVol,
            zeroGradientFvPatchScalarField::typeName
        )
    );

    VolField<Type>& div = tfvm.ref();

    // Interpolate phi to faces using upwind or other scheme
    SurfaceField<Type> phi_f = interpScheme_().interpolate(vf, faceFlux);

    // Sum over faces: div = sum(phi_f * flux_f) / V_P
    const fvMesh& mesh = vf.mesh();
    const labelUList& owner = mesh.owner();
    const labelUList& neighbour = mesh.neighbour();

    const scalarField& flux = faceFlux;

    forAll(owner, facei)
    {
        label own = owner[facei];
        label nei = neighbour[facei];

        scalar flux_f = flux[facei];

        div[own] += flux_f * phi_f[facei];
        div[nei] -= flux_f * phi_f[facei];  // Opposite sign for neighbor
    }

    // Divide by cell volumes
    div.primitiveFieldRef() /= mesh.V().primitiveField();

    return tfvm;
}
```

### Upwind Interpolation Scheme / รูปแบบอัปวินด์

**⭐ Upwind Scheme for Boundedness**

> **File**: `openfoam_temp/src/finiteVolume/interpolation/surfaceInterpolationScheme/limitedSchemes/upwind/upwind.H`
> **Lines**: 42-44

```cpp
// Upwind: phi_f = phi_P if flux > 0, phi_f = phi_N if flux < 0
// First-order accurate, but bounded (no overshoots/undershoots)
```

$$
\phi_f = \begin{cases}
\phi_P & \text{if } \dot{m}_f > 0 \text{ (flow out of owner)} \\
\phi_N & \text{if } \dot{m}_f < 0 \text{ (flow into owner)}
\end{cases}
$$

**⚠️ Trade-off**: First-order accuracy vs. boundedness
- **Use upwind** for VOF (alpha must stay 0-1)
- **Use higher-order** (QUICK, vanLeer) for velocity, temperature

### 4.3 Laplacian Schemes / รูปแบบลาปลาเชียน

### Gauss Laplacian Scheme / รูปแบบลาปลาเชียนเกาส์

**⭐ Basic Second-Order Laplacian**

> **File**: `openfoam_temp/src/finiteVolume/finiteVolume/laplacianSchemes/gaussLaplacianScheme/gaussLaplacianScheme.H`
> **Lines**: 27-29

$$
\nabla \cdot (\Gamma \nabla \phi) \approx \frac{1}{V_P} \sum_f (\Gamma \nabla \phi)_f \cdot \mathbf{S}_f
$$

Using **orthogonal** correction:

$$
(\Gamma \nabla \phi)_f \cdot \mathbf{S}_f = \Gamma_f \frac{\phi_N - \phi_P}{|\mathbf{d}_f|} |\mathbf{S}_f| + \text{correction}
$$

where $\mathbf{d}_f$ is the distance vector between cell centers.

```cpp
// File: src/finiteVolume/finiteVolume/laplacianSchemes/gaussLaplacianScheme/gaussLaplacianScheme.C
// Lines 95-125

tmp<fvMatrix<scalar>> gaussLaplacianScheme<scalar, scalar>::fvmLaplacian
(
    const SurfaceField<scalar>& gamma,
    const VolField<scalar>& vf
)
{
    // laplacian(gamma, phi) = div(gamma * grad(phi))
    // Discretized: sum(gamma_f * (phi_N - phi_P) / d_f * S_f)

    const fvMesh& mesh = vf.mesh();

    tmp<fvMatrix<scalar>> tfvm
    (
        new fvMatrix<scalar>
        (
            vf,
            gamma.dimensions()*vf.dimensions()/dimVol/dimLength
        )
    );

    fvMatrix<scalar>& fvm = tfvm.ref();

    const labelUList& owner = mesh.owner();
    const labelUList& neighbour = mesh.neighbour();

    const vectorField& Sf = mesh.Sf();           // Face area vectors
    const scalarField& magSf = mesh.magSf();     // Face areas
    const vectorField& C = mesh.C();             // Cell centers

    // Interpolate gamma to faces (linear by default)
    SurfaceField<scalar> gamma_f = linearInterpolate(gamma);

    // Build matrix coefficients
    forAll(owner, facei)
    {
        label own = owner[facei];
        label nei = neighbour[facei];

        vector d = C[nei] - C[own];              // Distance vector
        scalar magD = mag(d);                     // Distance magnitude

        // Non-orthogonal correction factor
        scalar deltaCoeff = magSf[facei] / magD;

        // Coefficient for owner-neighbor connection
        scalar coeff = gamma_f[facei] * deltaCoeff;

        // Add to matrix (symmetric for orthogonal mesh)
        fvm.upper()[facei] = -coeff;
        fvm.lower()[facei] = -coeff;

        fvm.diag()[own] += coeff;
        fvm.diag()[nei] += coeff;
    }

    return tfvm;
}
```

### Non-Orthogonal Correction / การแก้ไขเชิงไม่ตั้งฉาก

For **non-orthogonal** meshes:

$$
(\Gamma \nabla \phi)_f \cdot \mathbf{S}_f = \Gamma_f |\mathbf{S}_f| \frac{\phi_N - \phi_P}{|\mathbf{d}_f|} + \Gamma_f (\mathbf{S}_f - \frac{|\mathbf{S}_f|}{|\mathbf{d}_f|}\mathbf{d}_f) \cdot (\nabla \phi)_f
$$

The correction term is:
- **Explicit** (treated as source) for stability
- **Iterated** for highly non-orthogonal meshes

---

## 5. FVM vs FDM / การเปรียบเทียบ FVM กับ FDM

| Aspect | Finite Volume Method (FVM) | Finite Difference Method (FDM) |
|--------|---------------------------|-------------------------------|
| **Conservation** | ✅ Exact (discrete level) | ❌ Only as $\Delta x \to 0$ |
| **Mesh flexibility** | ✅ Any cell shape | ❌ Structured only |
| **Boundary handling** | ✅ Natural on complex BCs | ⚠️ Difficult on curved boundaries |
| **Implementation** | ⚠️ Complex (face loops) | ✅ Simple (stencils) |
| **Memory** | ⚠️ Higher (face connectivity) | ✅ Lower (arrays only) |
| **OpenFOAM** | ✅ Uses FVM | ❌ Not used |

### R410A Evaporator-Specific Considerations / พิจารณาเฉพาะสำหรับเครื่องระเหย R410A

**⭐ Why FVM is Essential for R410A**:

1. **Mass Conservation** during phase change:
   - Liquid mass converted to vapor = **exactly** accounted for
   - No artificial mass loss/gain from discretization

2. **Energy Conservation** with latent heat:
   - Heat absorbed by evaporation = **exactly** removed from liquid
   - Energy balance maintained at discrete level

3. **Cylindrical Tube Geometry**:
   - FVM handles **curved boundaries** naturally
   - No stair-step approximation of tube wall

4. **Two-Phase Interface**:
   - VOF equation requires **bounded** schemes (upwind)
   - Interface sharpness maintained with compressive schemes

---

## 6. fvMatrix: Implicit Discretization / เมทริกซ์ fv: การแบ่งส่วนโดยนัย

### What is fvMatrix? / fvMatrix คืออะไร?

**⭐ Finite Volume Matrix System**

> **File**: `openfoam_temp/src/finiteVolume/fvMatrices/fvMatrix/fvMatrix.H`
> **Lines**: 55-60

The `fvMatrix` represents a **sparse linear system**:

$$
\underbrace{\mathbf{A}}_{N \times N} \underbrace{\mathbf{x}}_{N \times 1} = \underbrace{\mathbf{b}}_{N \times 1}
$$

where:
- $N$ is the number of cells
- $\mathbf{A}$ contains diagonal, upper, and lower coefficients
- $\mathbf{x}$ is the field being solved (e.g., pressure, velocity)
- $\mathbf{b}$ is the source term (boundary conditions, explicit terms)

### Matrix Structure / โครงสร้างเมทริกซ์

```cpp
// File: src/finiteVolume/fvMatrices/fvMatrix/fvMatrix.H
// Lines 150-180

template<class Type>
class fvMatrix
{
    // Diagonal coefficients (A_pp in A*x = b)
    scalarField diag_;

    // Upper coefficients (A_pN for internal faces, owner -> neighbor)
    scalarField upper_;

    // Lower coefficients (A_Np for internal faces, neighbor -> owner)
    scalarField lower_;

    // Source term (right-hand side b in A*x = b)
    Field<Type> source_;

    // Reference to field being solved
    GeometricField<Type, fvPatchField, volMesh>& psi_;
};
```

### Building the Matrix / การสร้างเมทริกซ์

**⭐ Example: Laplacian Matrix**

```cpp
// Solving: div(gamma * grad(T)) = 0
// Matrix form: A*T = b

fvScalarMatrix TEqn
(
    fvm::laplacian(gamma, T)  // Implicit Laplacian: adds to A and diag
);

// After discretization:
// - diag[own] += sum(coefficients for all faces of cell own)
// - upper[face] = -gamma_f * |S_f| / |d_f|
// - lower[face] = -gamma_f * |S_f| / |d_f|
// - source[own] = boundary contributions

TEqn.solve();  // Solves A*T = b using linear solver
```

### Explicit vs Implicit Terms / เทอมโดยชัดแจ้งกับโดยนัย

| Namespace | Form | Matrix | Use Case |
|-----------|------|--------|----------|
| **fvc** (finite volume calculus) | Explicit | ⛔ No | $\nabla \cdot (\rho \mathbf{U} \phi)$ with known $\phi$ |
| **fvm** (finite volume method) | Implicit | ✅ Yes | $\nabla \cdot (\Gamma \nabla \phi)$ to solve for $\phi$ |

```cpp
// Example: Convection-diffusion equation
// ddt(phi) + div(U * phi) - div(gamma * grad(phi)) = 0

fvScalarMatrix phiEqn
(
    fvm::ddt(phi)           // Implicit time derivative
  + fvm::div(phi, U)        // Implicit convection (may require under-relaxation)
  - fvm::laplacian(gamma, phi)  // Implicit diffusion
 ==
    fvOptions(phi)          // Explicit source terms
);

phiEqn.solve();
```

---

## 7. Discretization Schemes in fvSchemes / รูปแบบการแบ่งส่วนใน fvSchemes

### OpenFOAM Dictionary Structure / โครงสร้างพจนานุกรม OpenFOAM

```cpp
// File: system/fvSchemes

ddtSchemes
{
    default         backward;       // Second-order time integration
    ddtrho(alpha)   Euler;          // First-order for VOF stability
}

gradSchemes
{
    default         Gauss linear;   // Second-order gradient
    grad(p)         Gauss linear;   // Pressure gradient
}

divSchemes
{
    default         none;           // Must specify each term

    div(phi,U)      Gauss upwind;           // First-order for stability
    div(phi,k)      Gauss upwind;           // Turbulence kinetic energy
    div(phi,epsilon) Gauss upwind;          // Dissipation rate
    div(phi,alpha)  Gauss vanLeer;          // VOF: compressive scheme
    div((nuEff*dev2(T(grad(U))))) Gauss linear;  // Stress diffusion
}

laplacianSchemes
{
    default         Gauss linear corrected;  // Non-orthogonal correction
}

interpolationSchemes
{
    default         linear;
}

snGradSchemes
{
    default         corrected;  // Non-orthogonal correction for surface normal gradient
}
```

### Scheme Selection for R410A Evaporator / การเลือกรูปแบบสำหรับเครื่องระเหย R410A

**⭐ Recommended Schemes**:

```cpp
// R410A two-phase evaporator simulation

ddtSchemes
{
    default         Euler;          // Start with first-order
    // Switch to backward for production runs
}

gradSchemes
{
    default         Gauss linear;
}

divSchemes
{
    div(rhoPhi,U)   Gauss limitedLinearV 1;  // Velocity: TVD scheme
    div(rhoPhi,T)   Gauss limitedLinearV 1;  // Temperature: TVD scheme
    div(phi,alpha)  Gauss vanLeer;           // VOF: bounded compressive
    div(phirb,alpha) Gauss interfaceCompression;  // Sharp interface
}

laplacianSchemes
{
    default         Gauss linear corrected;
}
```

**⚠️ Scheme Hierarchy**:
1. **upwind** (first-order): Most stable, most diffusive
2. **linear** (second-order central): Unstable for convection-dominated flow
3. **limitedLinear** (TVD): Bounded second-order
4. **vanLeer** (TVD): Good balance of accuracy and boundedness
5. **interfaceCompression**: Specialized for VOF interface

---

## 8. R410A Evaporator: Special Discretization Issues / เครื่องระเหย R410A: ปัญหาการแบ่งส่วนพิเศษ

### Phase Change Expansion Term / เทอมขยายตัวการเปลี่ยนสถานะ

**⭐ Mass Conservation with Phase Change**

During evaporation, liquid density $\rho_l \approx 1100$ kg/m³ converts to vapor density $\rho_v \approx 50$ kg/m³:

$$
\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \mathbf{U}) = \dot{m}'''\rho_v - \dot{m}'''\rho_l = \dot{m}'''(\rho_v - \rho_l)
$$

where $\dot{m}'''$ is the volumetric mass transfer rate.

**Discretization Challenge**:
- Large density ratio $\rho_l / \rho_v \approx 22$
- Expansion term $\nabla \cdot \mathbf{U}$ must be **exactly** balanced
- Requires **conservative** discretization of continuity equation

### VOF Equation Boundedness / ความจำกัดของสมการ VOF

**⭐ VOF Transport Equation**

$$
\frac{\partial \alpha}{\partial t} + \nabla \cdot (\alpha \mathbf{U}) + \nabla \cdot [\alpha(1-\alpha)\mathbf{U}_r] = \frac{\dot{m}'''}{\rho_l}
$$

where:
- $\alpha$: Liquid volume fraction (0 = vapor, 1 = liquid)
- $\mathbf{U}_r$: Relative velocity for interface compression
- Last term: **compressive** to keep interface sharp

**Discretization Requirements**:
1. **Boundedness**: $0 \leq \alpha \leq 1$ (use **MULES** limiter)
2. **Sharpness**: Interface spread over 2-3 cells (use **compression**)
3. **Conservation**: Mass exactly conserved

```cpp
// OpenFOAM VOF solver (interFoam family)
// File: applications/solvers/multiphase/interFoam/alphaEqn.H

// Solve VOF equation with MULES limiter
{
    volScalarField::Internal alphaSource(
        phaseChangeModel_->alphaSource()
    );

    surfaceScalarField phiAlpha(phi);
    phiAlpha -= fvc::flux(phirb);

    MULES::explicitSolve
    (
        geometricOneField(),
        alpha,
        phi,
        phiAlpha,
        alphaSource,
        phaseChangeModel_->Su(),
        phaseChangeModel_->Sp()
    );
}
```

### Temperature-Energy Coupling / การเชื่อมโยงอุณหภูมิ-พลังงาน

**⭐ Enthalpy Equation with Latent Heat**

$$
\frac{\partial (\rho h)}{\partial t} + \nabla \cdot (\rho \mathbf{U} h) = \nabla \cdot (k \nabla T) + \dot{q}'''
$$

where $h$ is enthalpy and latent heat $L$ is included in $h$:

$$
h = c_p T + \alpha L
$$

**Discretization Challenge**:
- Temperature varies **continuously** across interface
- Enthalpy has **jump** of magnitude $L$
- Requires **special treatment** of phase change cells

```cpp
// Enthalpy-temperature coupling in phase change
// Iterative update of temperature from enthalpy

for (int corr = 0; corr < nAlphaCorr; corr++)
{
    // Solve enthalpy equation
    fvScalarMatrix hEqn
    (
        fvm::ddt(rho, h)
      + fvm::div(rhoPhi, h)
      - fvm::laplacian(k, T)
     ==
        fvOptions(h)
    );

    hEqn.solve();

    // Update temperature from enthalpy
    // T = h / cp for single-phase
    // T = T_sat for two-phase (during phase change)
    T = thermo.T();
}
```

---

## 9. Verification & Best Practices / การตรวจสอบและแนวปฏิบัติที่ดี

### Verification Tests / การทดสอบการตรวจสอบ

**⭐ Method of Manufactured Solutions (MMS)**

To verify FVM discretization:

1. **Choose** an analytical solution: $\phi_{exact}(\mathbf{x}, t)$
2. **Compute** source term to satisfy PDE
3. **Run simulation** with computed source
4. **Compare** numerical vs. exact solution
5. **Verify** convergence rate

**Example: 2D Diffusion**

$$
\frac{\partial T}{\partial t} = \alpha \nabla^2 T + S
$$

Choose: $T(x,y,t) = \sin(\pi x) \sin(\pi y) e^{-2\pi^2 \alpha t}$

Compute $S$ analytically and use as source term.

### Stability Criteria / เกณฑ์เสถียรภาพ

**⚠️ CFL Condition for Explicit Schemes**:

$$
\text{CFL} = \frac{|\mathbf{U}| \Delta t}{\Delta x} \leq 1
$$

For **implicit** schemes (OpenFOAM default):
- No CFL limit for **diffusion**
- Still need CFL < 1 for **sharp interfaces** in VOF

**⚠️ Diffusion Number**:

$$
D = \frac{\alpha \Delta t}{\Delta x^2} \leq \frac{1}{2} \quad \text{(for explicit)}
$$

Implicit: **unconditionally stable** for diffusion.

### Best Practices for R410A Simulations / แนวปฏิบัติที่ดีสำหรับการจำลอง R410A

1. **Start with first-order schemes** (upwind, Euler) for stability
2. **Refine mesh** near walls and interface (y+ < 5 for heat transfer)
3. **Use small time steps** during initial transients: $\Delta t \approx 10^{-5}$ s
4. **Monitor conservation**: Mass, energy, and VOF boundedness
5. **Verify** with single-phase flow before adding phase change
6. **Validate** with experimental data (heat transfer coefficient)

---

## 10. Summary / สรุป

### Key Takeaways / จุดสำคัญ

1. **Gauss Theorem** is the foundation of FVM
   - Converts volume to surface integrals
   - Ensures exact conservation

2. **fvc vs fvm**:
   - `fvc`: Explicit calculus (compute gradient, divergence)
   - `fvm`: Implicit method (build matrix for solver)

3. **Scheme selection** balances accuracy and stability:
   - First-order: Stable but diffusive
   - Second-order: Accurate but may be unstable
   - TVD schemes: Bounded second-order

4. **R410A evaporator** requires special treatment:
   - Bounded VOF scheme (MULES, interfaceCompression)
   - Conservative phase change discretization
   - Coupled enthalpy-temperature solver

5. **fvMatrix** is the sparse linear system solved at each time step:
   - Diagonal: sum of all coefficients for a cell
   - Upper/Lower: face coefficients between owner-neighbor
   - Source: boundary conditions and explicit terms

---

## References / อ้างอิง

1. **OpenFOAM Source Code**:
   - `src/finiteVolume/finiteVolume/fvc/` - Explicit calculus operations
   - `src/finiteVolume/finiteVolume/fvm/` - implicit method operations
   - `src/finiteVolume/finiteVolume/ddtSchemes/` - Time integration schemes
   - `src/finiteVolume/finiteVolume/gradSchemes/` - Gradient schemes
   - `src/finiteVolume/finiteVolume/divSchemes/` - Divergence schemes
   - `src/finiteVolume/finiteVolume/laplacianSchemes/` - Laplacian schemes

2. **Textbooks**:
   - Ferziger, J.H., & Peric, M. (2002). *Computational Methods for Fluid Dynamics*
   - Jasak, H. (1996). *Error Analysis and Estimation for the Finite Volume Method*

3. **OpenFOAM Documentation**:
   - User Guide: Chapter 4 (Discretisation Schemes)
   - Programmer's Guide: Chapter 2 (Finite Volume Method)

---

*Last Updated: 2026-01-28*
*Next Section: 06_Solver_Basics*
