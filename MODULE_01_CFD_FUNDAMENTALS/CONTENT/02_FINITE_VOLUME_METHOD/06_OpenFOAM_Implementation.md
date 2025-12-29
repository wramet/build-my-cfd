# OpenFOAM Implementation

การนำ FVM ไปใช้ใน OpenFOAM ผ่าน C++ Classes

> **ทำไมต้องเข้าใจ OpenFOAM internals?**
> - Debug ปัญหาได้ลึกกว่าแค่ดู error message
> - เขียน custom solver/BC/utility ได้
> - เข้าใจว่า settings ต่างๆ ไปทำอะไรจริงๆ

---

## Core Classes

### fvMesh - Mesh Structure

> **ทำไม fvMesh สำคัญ?**
> fvMesh คือ "โครงสร้างข้อมูล" ที่เก็บทุกอย่างเกี่ยวกับ mesh:
> volumes, areas, connectivity — ทุกสิ่งที่ FVM ต้องการ

```cpp
// Access mesh data
const fvMesh& mesh = ...;

mesh.V();       // Cell volumes (volScalarField)    →  Volume integrals
mesh.Sf();      // Face area vectors                →  Surface integrals
mesh.C();       // Cell centers (volVectorField)    →  ตำแหน่งเก็บค่า
mesh.Cf();      // Face centers                     →  ตำแหน่งคำนวณ flux
```

**Files ที่เกี่ยวข้อง:**
- `constant/polyMesh/points` — พิกัดจุดยอด (vertices)
- `constant/polyMesh/faces` — face ประกอบจากจุดอะไรบ้าง
- `constant/polyMesh/owner`, `neighbour` — cell ไหนเป็นเจ้าของ face

### volScalarField / volVectorField - Fields

> **ทำไมแยก vol กับ surface?**
> - **vol:** ค่าที่ Cell Centers (เก็บจริง)
> - **surface:** ค่าที่ Faces (interpolate มา)

```cpp
volScalarField p
(
    IOobject
    (
        "p",                      // ชื่อ field
        runTime.timeName(),       // Time directory (0, 0.1, 1, ...)
        mesh,                     // อ้างอิง mesh
        IOobject::MUST_READ,      // ต้องอ่านจาก file
        IOobject::AUTO_WRITE      // เขียน output อัตโนมัติ
    ),
    mesh
);
```

**Types:**

| Class | Description | Example | ทำไมใช้ |
|-------|-------------|---------|---------|
| `volScalarField` | Scalar ที่ cell centers | p, T, k | ค่าเดี่ยว |
| `volVectorField` | Vector ที่ cell centers | U | มี 3 components |
| `surfaceScalarField` | Scalar ที่ faces | phi (flux) | คำนวณ flux |

### fvMatrix - Equation System

> **ทำไม fvMatrix สำคัญ?**
> `fvMatrix` ไม่ใช่แค่ matrix — มันคือ **สมการทั้งระบบ** ที่รวม:
> - Matrix [A]
> - RHS vector [b]
> - Boundary condition contributions
> - Methods สำหรับ solve, relax, residual

```cpp
fvScalarMatrix TEqn
(
    fvm::ddt(T)               // Temporal → เพิ่ม diagonal
  + fvm::div(phi, T)          // Convection → เพิ่ม diagonal + off-diagonal
  - fvm::laplacian(k, T)      // Diffusion → เพิ่ม diagonal + off-diagonal
 ==
    Q                         // Source → เพิ่ม RHS
);

TEqn.solve();  // แก้ [A][T] = [b] ด้วย linear solver
```

---

## fvm vs fvc: ความแตกต่างที่สำคัญที่สุด

| Prefix | Name | Output | ใช้เมื่อ |
|--------|------|--------|---------|
| `fvm::` | Finite Volume Method | **Matrix** | Unknown ที่กำลังจะหา |
| `fvc::` | Finite Volume Calculus | **Field** | Known ที่รู้ค่าแล้ว |

> **💡 กฎง่ายๆ:**
> - $\phi$ ที่อยู่ใน "=" ฝั่งซ้าย และยังไม่รู้ค่า → **fvm::**
> - $\phi$ ที่รู้ค่าแล้ว หรืออยู่ฝั่งขวา → **fvc::**

**ตัวอย่าง Momentum Equation:**

$$\rho\frac{\partial \mathbf{u}}{\partial t} + \nabla \cdot (\rho \mathbf{u} \mathbf{u}) - \nabla \cdot (\mu \nabla \mathbf{u}) = -\nabla p$$

```cpp
fvVectorMatrix UEqn
(
    fvm::ddt(rho, U)          // U ไม่รู้ → Implicit
  + fvm::div(phi, U)          // U ไม่รู้ → Implicit
  - fvm::laplacian(mu, U)     // U ไม่รู้ → Implicit
);

solve(UEqn == -fvc::grad(p)); // p รู้แล้ว (จาก iteration ก่อน) → Explicit
```

**ทำไม `fvc::grad(p)`?**
- p มาจาก pressure correction ก่อนหน้า
- ค่า p "frozen" ระหว่าง solve U
- ใส่เป็น source (RHS) ไม่ใช่ unknown

---

## Discretization Operators

| Operator | Implicit (fvm) | Explicit (fvc) | ทำไม |
|----------|---------------|----------------|------|
| Time derivative | `fvm::ddt(φ)` | `fvc::ddt(φ)` | ddt ใช้ทั้งสองแบบได้ |
| Divergence | `fvm::div(F, φ)` | `fvc::div(F)` | div(F) ไม่มี unknown |
| Laplacian | `fvm::laplacian(Γ, φ)` | `fvc::laplacian(Γ, φ)` | ใช้ได้ทั้งสอง |
| Gradient | — | `fvc::grad(φ)` | **ไม่มี fvm::grad!** |

**ทำไมไม่มี `fvm::grad()`?**
- Gradient: $\nabla \phi$ ไม่สร้าง contribution ที่ useful ใน matrix
- Gradient ใช้แค่ "คำนวณค่า" ไม่ใช่ "แก้สมการ"
- ถ้าต้องการ gradient term ใน PDE ให้ย้ายไป RHS แล้วใช้ `fvc::grad()`

---

## Pressure-Velocity Coupling

### SIMPLE (Steady-State)

> **แนวคิด:** วน iterate ระหว่าง U และ p จนกระทั่ง converge

```cpp
// 1. Solve momentum predictor (ใช้ p จาก iteration ก่อน)
solve(UEqn == -fvc::grad(p));

// 2. คำนวณ pressure equation coefficients
volScalarField rAU(1.0/UEqn.A());    // 1/a_P (reciprocal of diagonal)
volVectorField HbyA(rAU*UEqn.H());   // H/A ("momentum interpolation")
surfaceScalarField phiHbyA(fvc::flux(HbyA));

// 3. Solve pressure Poisson equation (จาก continuity)
fvScalarMatrix pEqn(fvm::laplacian(rAU, p) == fvc::div(phiHbyA));
pEqn.solve();

// 4. Correct velocity ให้ satisfy continuity
U = HbyA - rAU*fvc::grad(p);
```

**ทำไมต้อง Under-relax?**
- SIMPLE ไม่ exact → ถ้าใช้ค่าใหม่ทั้งหมดจะ oscillate
- Under-relax: $\phi_{new} = \alpha \phi_{calc} + (1-\alpha)\phi_{old}$

### PISO (Transient)

```cpp
for (int corr = 0; corr < nCorr; corr++)
{
    // Multiple pressure corrections per time step
    // เพื่อให้ U และ p consistent ภายใน Δt
}
```

**ทำไม PISO ไม่ต้อง Under-relax?**
- ทุก time step ต้อง "accurate" (ไม่ใช่แค่ final state)
- Multiple correctors แก้ไข inconsistency แทน relaxation

---

## Configuration Files

### system/fvSchemes

```cpp
ddtSchemes
{
    default         Euler;          // 1st order, stable
}

gradSchemes
{
    default         Gauss linear;   // Standard gradient
}

divSchemes
{
    div(phi,U)      Gauss linearUpwind grad(U);   // 2nd order + stable
    div(phi,k)      Gauss upwind;                  // Turbulence: stability first
}

laplacianSchemes
{
    default         Gauss linear corrected;   // Non-ortho correction
}
```

### system/fvSolution

```cpp
solvers
{
    p
    {
        solver      GAMG;       // Multigrid for Laplacian
        tolerance   1e-6;       // Absolute residual
        relTol      0.01;       // Stop after 100x reduction
    }
    U
    {
        solver      PBiCGStab;  // For asymmetric matrix
        preconditioner DILU;    // Incomplete LU
        tolerance   1e-5;
        relTol      0.1;
    }
}

SIMPLE
{
    nNonOrthogonalCorrectors 1;   // วน correction สำหรับ mesh เบี้ยว
}

relaxationFactors
{
    fields { p 0.3; }       // Pressure: ค่อยๆ เปลี่ยน
    equations { U 0.7; }    // Velocity: เปลี่ยนเร็วกว่าได้
}
```

---

## Creating Custom Solvers

### File Structure

```
myFoam/
├── Make/
│   ├── files       # Source files to compile
│   └── options     # Include paths, libraries
└── myFoam.C        # Main solver code
```

### Main Solver Code

```cpp
#include "fvCFD.H"   // OpenFOAM header (includes everything)

int main(int argc, char *argv[])
{
    #include "setRootCase.H"      // Parse command line
    #include "createTime.H"       // สร้าง runTime object
    #include "createMesh.H"       // สร้าง mesh object
    #include "createFields.H"     // อ่าน fields (U, p, T, ...)

    while (runTime.loop())
    {
        Info << "Time = " << runTime.timeName() << endl;

        // Solve equations
        fvScalarMatrix TEqn
        (
            fvm::ddt(T) - fvm::laplacian(k, T) == Q
        );
        TEqn.solve();

        runTime.write();  // เขียน output ถ้าถึงเวลา
    }

    Info << "End\n" << endl;
    return 0;
}
```

### Compiling

```bash
wmake   # Compile using OpenFOAM's build system
```

**ทำไมใช้ wmake ไม่ใช่ make?**
- wmake รู้จัก OpenFOAM environment
- จัดการ dependencies อัตโนมัติ
- Link ถูก libraries

---

## Concept Check

<details>
<summary><b>1. fvm กับ fvc ต่างกันอย่างไร? ใช้เมื่อไหร่?</b></summary>

| | fvm | fvc |
|-|-----|-----|
| Output | Matrix coefficients ($a_P$, $a_N$) | Field values (numbers) |
| ใช้กับ | Unknown ที่กำลัง solve | Known ที่รู้ค่าแล้ว |

**ตัวอย่าง:**
```cpp
fvm::ddt(U)      // U ไม่รู้ → matrix
-fvc::grad(p)    // p รู้แล้ว → field (source)
```
</details>

<details>
<summary><b>2. ทำไมไม่มี fvm::grad()?</b></summary>

**เหตุผลทางคณิตศาสตร์:**
- `fvm::` สร้าง matrix โดย linearize operator กับ unknown
- $\nabla \phi$ ไม่มี $\phi$ คูณกับ coefficient → ไม่สร้าง "useful" matrix

**วิธีแก้:** ถ้าต้องการ gradient term ในสมการ:
- ย้ายไป RHS: `... == fvc::grad(p)`
- หรือใช้ implicit source: `fvm::Sp(coeff, phi)`
</details>

<details>
<summary><b>3. SIMPLE กับ PISO แตกต่างกันอย่างไร?</b></summary>

| | SIMPLE | PISO |
|-|--------|------|
| ใช้กับ | Steady-state | Transient |
| Pressure corrections | 1 per iteration | หลายครั้งต่อ time step |
| Under-relaxation | **ต้องใช้** | ไม่ต้อง |
| เป้าหมาย | Converge ไปที่ final state | แม่นยำทุก time step |

**PIMPLE = PISO + SIMPLE:** ใช้ outer loops (SIMPLE-like) + inner corrections (PISO-like)
</details>

<details>
<summary><b>4. UEqn.A() และ UEqn.H() คืออะไร?</b></summary>

จากสมการ $AU = H - \nabla p$:
- **A:** Diagonal coefficient ($a_P$) — เก็บ contribution จาก implicit terms
- **H:** Off-diagonal + source — เก็บ contribution จาก neighbors และ sources

**ใช้ใน pressure equation:**
$$\nabla \cdot \left(\frac{H}{A}\right) - \nabla \cdot \left(\frac{1}{A}\nabla p\right) = 0$$

นี่คือ "Rhie-Chow interpolation" ซึ่งป้องกัน pressure checkerboard
</details>

<!-- IMAGE: IMG_01_006 -->
<!--
Purpose: อธิบายปัญหา Checkerboard Pressure ที่เกิดขึ้นหากใช้ Linear Interpolation ปกติกับ Collocated Grid ซึ่งดูเหมือนถูกต้อง (Gradient=0) แต่จริงๆ ผิด (Oscillation). เปรียบเทียบกับ Rhie-Chow ที่แก้ปัญหานี้
Prompt: "Checkerboard Pressure Concept. **Top Panel (Collocated Grid):** A 1D row of cells showing pressure values [100, 0, 100, 0]. The central difference gradient is zero despite oscillation. Label: 'Unphysical Oscillation'. **Bottom Panel (Staggered/Rhie-Chow):** Smooth pressure gradient showing correct interpolation. Label: 'Rhie-Chow Corrected'. **Style:** Scientific plot or grid schematic, red oscillation vs green smooth line."
-->
![IMG_01_006: Checkerboard Pressure vs Rhie-Chow](IMG_01_006.jpg)

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [05_Matrix_Assembly.md](05_Matrix_Assembly.md) — Matrix Assembly
- **บทถัดไป:** [07_Best_Practices.md](07_Best_Practices.md) — Best Practices
- **Module 05:** OpenFOAM Programming — รายละเอียดการเขียน code