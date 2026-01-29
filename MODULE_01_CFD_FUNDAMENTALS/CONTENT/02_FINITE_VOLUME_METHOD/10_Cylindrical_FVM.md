# Cylindrical Coordinate FVM for R410A Tube Flow
# การใช้วิธีขอบในสี่เหลี่ยมจัตุรัสสำหรับระบบพิกัดทรงกระบอก (R410A การไหลในท่อระเหย)

> **โครงร่าง:** FVM ในระบบพิกัดทรงกระบอกสำหรับการจำลองการไหลของ R410A ในท่อระเหย
>
> **เป้าหมาย:** เข้าใจความแตกต่างระหว่าง FVM สี่เหลี่ยมจัตุรัสและทรงกระบอก และการปรับตัวให้เข้ากับท่อระเหย

## Prerequisites

⚠️ **ควรอ่านก่อน:** [03_Spatial_Discretization.md](03_Spatial_Discretization.md) และ [05_Two_Phase_Flow_Fundamentals.md](../05_TWO_PHASE_FLOW/00_Two_Phase_Flow_Fundamentals.md) เพื่อความเข้าใจเรื่อง:
- การ discretization พื้นฐาน
- การไหลสองเฟสในท่อ

## Learning Objectives

หลังจากอ่านบทนี้ คุณจะสามารถ:
- **อธิบาย** ความแตกต่างทางคณิตศาสตร์ระหว่าง FVM และ FVM สี่เหลี่ยมจัตุรัส
- **แปลง** สมการอนุรักษ์เป็นระบบพิกัดทรงกระบอก
- **นำไปใช้** วิธี discretization ในท่อระเหย
- **สร้าง** mesh สำหรับท่อระเหย
- **แก้ปัญหา** numerical issues ที่เกิดจากความไม่สมมาตรในทรงกระบอก

---

## 1. Introduction to Cylindrical FVM

### 1.1 Why Cylindrical Coordinates for Tube Flow?

**ปัญหาพื้นฐาน:** ท่อมีเส้นผ่านศูนย์กลางและความยาวคงที่ - ใช้ระบบพิกัดทรงกระบอกเหมาะสมกว่า

```
สี่เหลี่ยมจัตุรัส: ใช้เมทริกซ์แบบหนาแน่น
ทรงกระบอก: ใช้เมทริกซ์แบบกระจาย (ทฤษฎีอุ่นเย็น)
```

**เหตุผล:**
- ลดจำนวน cell: $r_{max} = 10\text{mm}$, $L = 1000\text{mm}$
  - 2D: 10 cells × 100 cells = 1,000 cells
  - 3D: 10 × 100 × 100 = 100,000 cells
- ความแม่นยมดีขึ้น: Grid lines ตามเส้นการไหล
- Boundary conditions ง่าย: Symmetry ที่เส้นผ่านศูนย์กลาง

### 1.2 Coordinate System for R410A Evaporator

**พิกัดที่ใช้:**
- $r$: รัศมี (radial coordinate)
- $z$: ระยะห่างตามแกน (axial coordinate)
- $\theta$: มุม (azimuthal coordinate)

**สำหรับท่อระเหย:** อาจจะเป็น 2D axisymmetric (r,z) หรือ 3D full (r,z,θ)

**เวกเตอร์ตำแหน่ง:**
$$
\mathbf{r} = r\mathbf{e}_r + z\mathbf{e}_z
$$

**เวกเตอร์ความเร็ว:**
$$
\mathbf{U} = u_r\mathbf{e}_r + u_\theta\mathbf{e}_\theta + u_z\mathbf{e}_z
$$

> **NOTE:** สำหรับ R410A evaporator ท่มีรูปทรงเป็นวงกลมสมมาตร เราสามารถใช้ 2D axisymmetric ได้

---

## 2. FVM in Cylindrical Coordinates

### 2.1 Volume Elements

⭐ **หน่วยปริมาตรในระบบพิกัดทรงกระบอก:**
$$
dV = r\,dr\,d\theta\,dz
$$

**สำหรับ cell ในท่อ:**
```
        z-axis
        ↑
        │
        │
        │
        P
    fN  │  fE
    ●───────────●
    │           │
    │           │
    │           │
    │           │
    ●───────────●
    fP  │  fW
        │
        └───────────────► r-axis
```

**ปริมาตรของ cell P:**
$$
V_P = \Delta r_P \cdot r_P \cdot \Delta \theta_P \cdot \Delta z_P
$$

โดยที่:
- $\Delta r_P = r_E - r_W$ (radial width)
- $r_P = \frac{r_E + r_W}{2}$ (radial midpoint)
- $\Delta \theta_P = 2\pi/N$ (angular width)
- $\Delta z_P = z_N - z_S$ (axial height)

### 2.2 Surface Vectors in Cylindrical Coordinates

**พื้นที่หน้าตัดและเวกเตอร์พื้นที่:**
```
การไหล axially (z-direction):
- Sf_N = 2π · r_P · Δr_P/2 · Δz_N (north face)
- Sf_S = 2π · r_P · Δr_P/2 · Δz_S (south face)

การไหล radially (r-direction):
- Sf_E = 2π · r_E · Δθ_E · Δz_P/2 (east face)
- Sf_W = 2π · r_W · Δθ_W · Δz_P/2 (west face)

การไหล azimuthally (θ-direction):
- ใช้ใน 3D เท่านั้น
```

**เวกเตอร์พื้นที่:**
- Axial: $\mathbf{S}_f = (0, 0, \pm S_f)$
- Radial: $\mathbf{S}_f = (\pm S_f, 0, 0)$
- Azimuthal: $\mathbf{S}_f = (0, \pm S_f, 0)$

### 2.3 Discretization Differences from Cartesian

**ความแตกต่างที่สำคัญ:**

| ประเภท | Cartesian | Cylindrical |
|--------|-----------|-------------|
| **Volume** | $V = \Delta x \Delta y \Delta z$ | $V = r\Delta r \Delta \theta \Delta z$ |
| **Flux** | $\Phi_f = \mathbf{U}_f \cdot \mathbf{S}_f$ | $\Phi_f = \mathbf{U}_f \cdot \mathbf{S}_f$ |
| **Integration** | $\int dV$ | $\int r\,dr\,d\theta\,dz$ |
| **Gradient** | $\frac{\partial \phi}{\partial x}$ | $\frac{\partial \phi}{\partial r} + \frac{1}{r}\frac{\partial \phi}{\partial \theta} + \frac{\partial \phi}{\partial z}$ |

---

## 3. Conservation Laws in Cylindrical Coordinates

### 3.1 Continuity Equation

⭐ ⭐ **สมการการอนุรักษ์มวล:**
$$
\frac{\partial \rho}{\partial t} + \frac{1}{r}\frac{\partial}{\partial r}(r\rho u_r) + \frac{1}{r}\frac{\partial}{\partial \theta}(\rho u_\theta) + \frac{\partial}{\partial z}(\rho u_z) = 0
$$

⭐ **FVM Discretization:**
$$
\frac{\rho_P^{n+1} - \rho_P^n}{\Delta t} V_P + \sum_f \Phi_f = 0
$$

โดยที่:
$$
\Phi_f = \rho_f (\mathbf{U}_f \cdot \mathbf{S}_f)
$$

### 3.2 Momentum Equations

#### Radial Momentum:
⭐ $$
\frac{\partial (\rho u_r)}{\partial t} + \frac{1}{r}\frac{\partial}{\partial r}(r\rho u_r u_r) + \frac{1}{r}\frac{\partial}{\partial \theta}(\rho u_\theta u_r) + \frac{\partial}{\partial z}(\rho u_z u_r) = -\frac{\partial p}{\partial r} + \mu \left[\frac{1}{r}\frac{\partial}{\partial r}\left(r\frac{\partial u_r}{\partial r}\right) - \frac{u_r}{r^2} + \frac{1}{r^2}\frac{\partial^2 u_r}{\partial \theta^2} + \frac{\partial^2 u_r}{\partial z^2}\right]
$$

#### Axial Momentum:
⭐ $$
\frac{\partial (\rho u_z)}{\partial t} + \frac{1}{r}\frac{\partial}{\partial r}(r\rho u_r u_z) + \frac{1}{r}\frac{\partial}{\partial \theta}(\rho u_\theta u_z) + \frac{\partial}{\partial z}(\rho u_z u_z) = -\frac{\partial p}{\partial z} + \mu \left[\frac{1}{r}\frac{\partial}{\partial r}\left(r\frac{\partial u_z}{\partial r}\right) + \frac{1}{r^2}\frac{\partial^2 u_z}{\partial \theta^2} + \frac{\partial^2 u_z}{\partial z^2}\right]
$$

### 3.3 Energy Equation

**สำหรับ R410A evaporator:**
$$
\frac{\partial (\rho h)}{\partial t} + \frac{1}{r}\frac{\partial}{\partial r}(r\rho u_r h) + \frac{1}{r}\frac{\partial}{\partial \theta}(\rho u_\theta h) + \frac{\partial}{\partial z}(\rho u_z h) = \frac{1}{r}\frac{\partial}{\partial r}\left(r\frac{k}{c_p}\frac{\partial h}{\partial r}\right) + \frac{1}{r^2}\frac{\partial}{\partial \theta}\left(\frac{k}{c_p}\frac{\partial h}{\partial \theta}\right) + \frac{\partial}{\partial z}\left(\frac{k}{c_p}\frac{\partial h}{\partial z}\right) + \frac{\dot{q}_w}{r}
$$

โดยที่ $\dot{q}_w$ คือ heat flux จากผนังท่อ

---

## 4. Discretization Implementation

### 4.1 Surface Area Calculations

```cpp
// File: cylindricalFVM.H
// การคำนวณพื้นที่หน้าตัดในท่อ

class CylindricalMesh {
private:
    scalarField r_;       // Radial coordinates
    scalarField z_;       // Axial coordinates
    scalarField theta_;   // Angular coordinates
    label nCells_;        // Number of cells

public:
    // Calculate face areas for axial faces (r-direction)
    tmp<surfaceScalarField> axialArea() const;

    // Calculate face areas for axial faces (z-direction)
    tmp<surfaceScalarField> radialArea() const;

    // Calculate cell volumes
    tmp<volScalarField> cellVolumes() const;
};

// Implementation: cylindricalFVM.C
tmp<surfaceScalarField> CylindricalMesh::axialArea() const
{
    auto axArea = surfaceScalarField::New(
        "axialArea",
        mesh_,
        dimensionedScalar("axialArea", dimArea, 0.0)
    );

    forAll(axArea, faceI) {
        // For radial faces: A = 2π × r_face × Δz
        const label own = mesh_.faceOwner()[faceI];
        const label nei = mesh_.faceNeighbour()[faceI];

        // Average radius at face
        scalar rFace = 0.5 * (r_[own] + r_[nei]);
        scalar dz = z_[own] - z_[nei];

        axArea[faceI] = 2.0 * M_PI * rFace * fabs(dz);
    }

    return axArea;
}

tmp<surfaceScalarField> CylindricalMesh::radialArea() const
{
    auto radArea = surfaceScalarField::New(
        "radialArea",
        mesh_,
        dimensionedScalar("radialArea", dimArea, 0.0)
    );

    forAll(radArea, faceI) {
        // For axial faces: A = π × r² (if axisymmetric)
        const label own = mesh_.faceOwner()[faceI];

        radArea[faceI] = M_PI * sqr(r_[own]);
    }

    return radArea;
}

tmp<volScalarField> CylindricalMesh::cellVolumes() const
{
    auto cellVol = volScalarField::New(
        "cellVolume",
        mesh_,
        dimensionedScalar("cellVolume", dimVolume, 0.0)
    );

    forAll(cellVol, cellI) {
        // Cell volume: V = Δr × r_cell × Δθ × Δz
        scalar dr = (cellI < r_.size()-1) ? r_[cellI+1] - r_[cellI] : 0.0;
        scalar rCell = r_[cellI];
        scalar dTheta = 2.0 * M_PI / nCells_;  // Axisymmetric
        scalar dz = (cellI < z_.size()-1) ? z_[cellI+1] - z_[cellI] : 0.0;

        cellVol[cellI] = dr * rCell * dTheta * dz;
    }

    return cellVol;
}
```

### 4.2 Flux Calculations

```cpp
// Surface integration in cylindrical coordinates
tmp<volScalarField> cylindricalDiv(
    const surfaceScalarField& phi,
    const volVectorField& U
)
{
    const fvMesh& mesh = U.mesh();

    auto divPhi = volScalarField::New(
        "div(" + phi.name() + ')',
        mesh,
        dimensionedScalar("div(" + phi.name() + ')', phi.dimensions()/dimTime, 0.0)
    );

    // Get cell volumes
    const scalarField& V = mesh.V();

    // Get face areas (already includes r factor)
    const surfaceScalarField& Sf = phi.mesh().magSf();

    // Surface integration
    forAll(mesh.cells(), cellI) {
        scalar sumFlux = 0.0;
        const labelList& own = mesh.faceOwner();
        const labelList& nei = mesh.faceNeighbour();

        forAll(mesh.cells()[cellI], faceI) {
            label faceLabel = mesh.cells()[cellI][faceI];

            scalar flux = phi[faceLabel];
            scalar area = Sf[faceLabel];

            // Check if face is boundary
            if (faceLabel < own.size()) {
                if (own[faceLabel] == cellI) {
                    sumFlux += flux * area;
                } else {
                    sumFlux -= flux * area;
                }
            } else {
                // Boundary face
                sumFlux += boundaryFlux(phi, faceLabel);
            }
        }

        divPhi[cellI] = sumFlux / V[cellI];
    }

    return divPhi;
}
```

### 4.3 Boundary Conditions

```cpp
// Boundary conditions for cylindrical tube flow
void setTubeBCs(
    volVectorField& U,
    volScalarField& p,
    volScalarField& h,
    const word& inletType,
    const word& outletType,
    const word& wallType
)
{
    // Inlet BC
    if (inletType == "velocityInlet") {
        U.boundaryFieldRef()[0] = fvPatchField<scalar>::
            New(U.mesh().boundary()[0], "U", U.boundaryField()[0],
                dictionary());
        U.boundaryFieldRef()[0].assign(U.dimensions()*dimLength/dimTime);
        U.boundaryFieldRef()[0] = uniformDimensionedVectorField("Uinlet",
            vector(0.0, 0.0, 1.0));  // Axial inlet
    }

    // Outlet BC
    if (outletType == "pressureOutlet") {
        p.boundaryFieldRef()[1].refValue() =
            dimensionedScalar("p", p.dimensions(), 101325.0);
        p.boundaryFieldRef()[1].valueFraction() = 1.0;
    }

    // Wall BC (no-slip)
    if (wallType == "noSlip") {
        forAll(U.boundaryField(), patchI) {
            if (isA<wallFvPatch>(U.boundaryField()[patchI])) {
                U.boundaryFieldRef()[patchI] = vector::zero;
            }
        }
    }

    // Symmetry BC at centerline (r=0)
    forAll(U.boundaryField(), patchI) {
        if (isA<symmetryFvPatch>(U.boundaryField()[patchI])) {
            // For axisymmetric: radial velocity = 0
            U.boundaryFieldRef()[patchI].component(vector::X) = 0.0;
        }
    }
}
```

---

## 5. R410A Evaporator Specific Considerations

### 5.1 Phase Change in Tube Flow

**ความท้าทายเฉพาะของ R410A evaporator:**
- Two-phase flow pattern: bubbly → slug → annular
- Variable properties along the tube
- Heat transfer coefficient changes with quality
- Pressure drop due to friction and acceleration

**สมการการเปลี่ยนเฟส:**
$$
\frac{\partial}{\partial t}(\alpha_g \rho_g) + \nabla \cdot (\alpha_g \rho_g \mathbf{U}_g) = \dot{m}_{evap}
$$

โดยที่:
- $\alpha_g$ = void fraction (gas phase)
- $\dot{m}_{evap}$ = evaporation rate

### 5.2 Property Interpolation

```cpp
// R410A property interpolation for cylindrical coordinates
class R410AProperties {
private:
    scalarField T_;      // Temperature field
    scalarField p_;      // Pressure field
    scalarField x_;      // Quality
    scalarField rho_;    // Density
    scalarField mu_;     // Viscosity
    scalarField k_;      // Thermal conductivity
    scalarField Cp_;     // Specific heat

public:
    // Update properties based on local conditions
    void updateProperties();

    // Interpolate properties for two-phase flow
    scalar rho_twoPhase(scalar x, scalar rho_l, scalar rho_g) const {
        return 1.0 / (x/rho_g + (1-x)/rho_l);
    }

    scalar mu_twoPhase(scalar x, scalar mu_l, scalar mu_g) const {
        return x*mu_g + (1-x)*mu_l;  // Simplified mixing rule
    }

    scalar k_twoPhase(scalar x, scalar k_l, scalar k_g) const {
        return x*k_g + (1-x)*k_l;    // Simplified mixing rule
    }
};

void R410AProperties::updateProperties()
{
    forAll(T_, cellI) {
        scalar T = T_[cellI];
        scalar p = p_[cellI];
        scalar x = x_[cellI];

        // Look up saturated properties
        scalar rho_l = getLiquidDensity(T, p);
        scalar rho_g = getVaporDensity(T, p);
        scalar mu_l = getLiquidViscosity(T, p);
        scalar mu_g = getVaporViscosity(T, p);
        scalar k_l = getLiquidConductivity(T, p);
        scalar k_g = getVaporConductivity(T, p);

        // Two-phase properties
        rho_[cellI] = rho_twoPhase(x, rho_l, rho_g);
        mu_[cellI] = mu_twoPhase(x, mu_l, mu_g);
        k_[cellI] = k_twoPhase(x, k_l, k_g);

        // Specific heat (simplified)
        if (x < 0.001) {
            Cp_[cellI] = getLiquidCp(T, p);
        } else if (x > 0.999) {
            Cp_[cellI] = getVaporCp(T, p);
        } else {
            Cp_[cellI] = x*getVaporCp(T, p) + (1-x)*getLiquidCp(T, p);
        }
    }
}
```

### 5.3 Heat Transfer Enhancement

**การเพิ่มประสิทธิภาพการถ่ายเทความร้อนในท่อ:**
- Micro-fin tubes: Increase surface area
- Turbo inserts: Create swirl flow
- Grooved tubes: nucleate bubble sites

**สมการการถ่ายเทความร้อน:**
$$
q'' = h \cdot (T_w - T_b)
$$

โดยที่ $h$ คือ heat transfer coefficient ซึ่งขึ้นอยู่กับ:
- Reynolds number: $Re = \frac{\rho u D}{\mu}$
- Prandtl number: $Pr = \frac{C_p \mu}{k}$
- Quality (for two-phase)

---

## 6. Implementation Example: 2D Axisymmetric Evaporator

### 6.1 Mesh Generation

```cpp
// cylindricalMesh.C - Generate mesh for tube evaporator
#include "fvMesh.H"
#include "volFields.H"
#include "surfaceFields.H"

void createCylindricalMesh(
    fvMesh& mesh,
    scalar tubeRadius,
    scalar tubeLength,
    label nRadial,
    label nAxial
)
{
    // Create mesh points
    pointField points(nRadial * nAxial);

    scalar deltaR = tubeRadius / (nRadial - 1);
    scalar deltaZ = tubeLength / (nAxial - 1);

    // Build mesh coordinates
    label pointI = 0;
    for (label j = 0; j < nAxial; j++) {
        scalar z = j * deltaZ;
        for (label i = 0; i < nRadial; i++) {
            scalar r = i * deltaR;
            points[pointI++] = point(r, 0.0, z);  // 2D axisymmetric
        }
    }

    // Create cells
    List<List<label>> cells;
    List<labelList> boundaries;

    for (label j = 0; j < nAxial - 1; j++) {
        for (label i = 0; i < nRadial - 1; i++) {
            // Cell connectivity
            label cell = j * (nRadial - 1) + i;

            // Cell faces
            label p0 = j * nRadial + i;
            label p1 = j * nRadial + i + 1;
            label p2 = (j + 1) * nRadial + i + 1;
            label p3 = (j + 1) * nRadial + i;

            // Hex cell: 8 vertices (for 3D) but 4 for 2D
            // Convert to axisymmetric
            labelList hexCell(8);
            hexCell[0] = hexCell[4] = p0;
            hexCell[1] = hexCell[5] = p1;
            hexCell[2] = hexCell[6] = p2;
            hexCell[3] = hexCell[7] = p3;

            cells.append(hexCell);
        }
    }

    // Create boundary patches
    // - Axis of symmetry (r=0)
    // - Outer wall (r=R)
    // - Inlet (z=0)
    // - Outlet (z=L)

    // Convert to OpenFOAM mesh format
    // ... (simplified)

    Info << "Created cylindrical mesh: " << cells.size() << " cells" << endl;
}
```

### 6.2 Solver Setup

```cpp
// cylindricalFoam.C - Main solver for R410A evaporator
#include "fvCFD.H"
#include "R410AProperties.H"
#include "turbulenceModel.H"

int main(int argc, char *argv[])
{
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"
    #include "createFields.H"

    #include "initContinuityErrs.H"
    #include "createControls.H"

    turbulence->validate();

    for (runTime++; runTime.run(); runTime++)
    {
        #include "readTimeControls.H"
        #include "CourantNo.H"
        #include "alphaCourantNo.H"
        #include "setInitialDeltaT.H"

        mesh.update();

        // --- Solve pressure-velocity coupling ---

        #include "rhoEqn.H"          // Continuity equation
        #include "UEqn.H"             // Momentum equations
        #include "hEqn.H"             // Energy equation

        // Update properties after solution
        R410A_props.updateProperties();

        // --- Check convergence ---
        #include "continuityErrs.H"

        runTime.write();

        runTime.print();
    }

    return 0;
}
```

### 6.3 Main Equations

```cpp
// UEqn.H - Momentum equations in cylindrical coordinates
{
    // Create incompressible, turbulent flow field
    volVectorField U(
        IOobject(
            "U",
            runTime.timeName(),
            mesh,
            IOobject::MUST_READ,
            IOobject::AUTO_WRITE
        ),
        mesh
    );

    // Pressure field
    volScalarField p(
        IOobject(
            "p",
            runTime.timeName(),
            mesh,
            IOobject::MUST_READ,
            IOobject::AUTO_WRITE
        ),
        mesh
    );

    // Create turbulence model
    autoPtr<turbulenceModel> turbulence(
        turbulenceModel::New(U, phi, R)
    );

    // Momentum equation
    fvVectorMatrix UEqn(
        fvm::div(phi, U)
        + turbulence->divDevReff(U)
        == fvm::laplacian(nu, U)
    );

    // Solve momentum equation
    UEqn.solve();

    // Update boundary conditions
    U.correctBoundaryConditions();
}

// hEqn.H - Energy equation
{
    volScalarField h(
        IOobject(
            "h",
            runTime.timeName(),
            mesh,
            IOobject::MUST_READ,
            IOobject::AUTO_WRITE
        ),
        mesh
    );

    // Energy equation with phase change
    fvScalarMatrix hEqn(
        fvm::div(phi, h)
        == fvm::laplacian(alpha*turbulence->nut()/Pr, h)
        + heatTransfer
    );

    // Solve energy equation
    hEqn.solve();
}
```

---

## 7. Common Issues and Solutions

### 7.1 Numerical Issues in Cylindrical Coordinates

**ปัญหา 1: Singularity at r=0**

```cpp
// Solution: Special treatment at centerline
void handleCenterlineSingularity(volScalarField& phi)
{
    forAll(phi.boundaryField(), patchI) {
        if (isA<symmetryFvPatch>(phi.boundaryField()[patchI])) {
            // L'Hôpital's rule for r→0
            // ∂φ/∂r = 0 at r=0
            phi.boundaryFieldRef()[patchI] =
                2.0 * phi.internalField()[0];
        }
    }
}
```

**ปัญหา 2: Non-orthogonality in curved meshes**

```cpp
// Solution: Non-orthogonal correction
tmp<volScalarField> correctNonOrthogonal(
    const volScalarField& phi,
    const surfaceScalarField& flux
)
{
    const fvMesh& mesh = phi.mesh();

    // Non-orthogonal correction
    tmp<volScalarField> correction(
        fvc::div(flux, phi.name() + "Corr")
    );

    return correction;
}
```

### 7.2 Convergence Tips

1. **Under-relaxation:**
   ```cpp
   U.relax(0.7);
   p.relax(0.3);
   h.relax(0.5);
   ```

2. **CFL condition:**
   ```cpp
   adjustDeltaT(runTime, mesh);
   ```

3. **Grid independence study:**
   - Start with coarse grid
   - Refine in critical regions
   - Monitor key parameters

---

## 8. Verification and Validation

### 8.1 Verification Studies

**Analytical solution for laminar flow:**
```
Poiseuille flow in circular tube:
u(r) = (ΔP/(4μL)) × (R² - r²)
```

```cpp
// Compare with analytical solution
void verifyAnalyticalSolution(
    const volVectorField& U,
    scalar pressureDrop,
    scalar tubeRadius,
    scalar tubeLength,
    scalar viscosity
)
{
    scalar dpdz = pressureDrop / tubeLength;

    scalarField r(mesh.C().component(vector::X));
    scalarField u_analytical = -dpdz * (sqr(tubeRadius) - sqr(r)) / (4 * viscosity);

    scalar error = gSum mag(U.internalField() - u_analytical) /
                   gSum mag(u_analytical);

    Info << "Analytical solution error: " << error * 100 << "%" << endl;
}
```

### 8.2 Validation Against Experimental Data

**Key parameters to validate:**
- Pressure drop vs. experimental correlations
- Heat transfer coefficient
- Void fraction distribution
- Temperature profile

---

## 9. Best Practices

### 9.1 Mesh Generation

1. **Aspect ratio:** Keep Δr/Δz < 0.5 for stability
2. **Resolution:** Resolve boundary layer (y+ < 1)
3. **Grid refinement:** Near walls and phase change regions

### 9.2 Solution Strategy

1. **Initialization:** Start with single-phase, then introduce two-phase
2. **Transient simulation:** Use time-dependent solution for better convergence
3. **Monitoring:** Track key parameters during iteration

### 9.3 Physical Modeling

1. **Turbulence modeling:** Use k-ε or k-ω with wall functions
2. **Phase change model:** Use evaporating-condensing model
3. **Property models:** Use realistic correlations for R410A

---

## 10. References and Further Reading

### 10.1 OpenFOAM Source Code

- **File:** `openfoam_temp/src/meshTools/coordinateSystems/cylindricalCS.C`
- **Lines:** 44-100
- **Code:**
  ```cpp
  // Coordinate transformation in cylindrical CS
  vector lc(sqrt(sqr(lc.x()) + sqr(lc.y())), atan2(lc.y(), lc.x()), lc.z());
  ```

- **File:** `openfoam_temp/src/finiteVolume/finiteVolume/fvc/fvcDiv.C`
- **Lines:** 44-200
- **Code:**
  ```cpp
  // General divergence implementation
  return VolField<Type>::New
  (
      "div("+ssf.name()+')',
      fvc::surfaceIntegrateExtrapolate(ssf)
  );
  ```

### 10.2 Textbooks and Papers

1. **Patankar, S. V. (1980)** - *Numerical Heat Transfer and Fluid Flow*
2. **Incropera, F. P. et al. (2007)** - *Fundamentals of Heat and Mass Transfer*
3. **Kandlikar, S. G. (1991)** - *Heat Transfer Enhancement in Condensation and Evaporation in Passages*

### 10.3 R410A Properties

1. **CoolProp database** - http://www.coolprop.org
2. **ASHRAE Handbook** - Refrigerant Properties
3. **NIST Chemistry WebBook** - Thermodynamic Properties

---

## Summary

ในบทนี้เราได้เรียนรู้เกี่ยวกับ FVM ในระบบพิกัดทรงกระบอกสำหรับการจำลองการไหลของ R410A ในท่อระเหย ประกอบด้วย:

1. **ความแตกต่างระหว่าง FVM สี่เหลี่ยมจัตุรัสและทรงกระบอก**
   - การคำนวณปริมาตร (ด้วย r factor)
   - พื้นที่หน้าตัดและเวกเตอร์พื้นที่
   - การ discretization ที่ซับซ้อนขึ้น

2. **การประยุกต์ใช้กับ R410A evaporator**
   - การคำนวณคุณสมบัติ two-phase
   - การจัดการ phase change
   - การคำนวณ heat transfer coefficient

3. **การ implement ใน OpenFOAM**
   - การสร้าง mesh สำหรับท่อ
   - การแก้สมการควบคุม
   - การจัดการ boundary conditions

ข้อสำคัญสุดท้ายคือ **การเลือก coordinate system ที่เหมาะสม** สำหรับปัญหาที่เป็นเส้นตรง (ท่อ) การใช้ระบบพิกัดทรงกระบอกจะช่วยลดจำนวน cell และเพิ่มความแม่นยมในการจำลอง