# Rhie-Chow Interpolation

## 🎯 ความสำคัญ

ใน OpenFOAM ซึ่งใช้การจัดวางตัวแปรแบบ **Collocated Grid** (ทั้งความเร็วและความดันถูกเก็บไว้ที่จุดศูนย์กลางเซลล์) หากใช้การประมาณค่าแบบ Linear ปกติจะเกิดปัญหา **Pressure-Velocity Decoupling** ซึ่งนำไปสู่สนามความดันที่แกว่งแบบตารางหมากรุก (Checkerboard oscillations)

**Rhie-Chow interpolation** (1983) เป็นเทคนิคที่ถูกพัฒนาขึ้นเพื่อแก้ปัญหานี้โดยเฉพาะ

---

## 📐 1. ปัญหา Checkerboard (The Checkerboard Problem)

เมื่อตัวแปรความดันถูกเก็บที่จุดศูนย์กลางเซลล์ เกรเดียนต์ความดันที่จุด $P$ ($\nabla p_P$) หากคำนวณจากเซลล์ข้างเคียง $W$ และ $E$ จะไม่รับรู้ถึงความแตกต่างของความดันระหว่างเซลล์ที่อยู่ติดกันโดยตรง:

$$\left( \frac{\partial p}{\partial x} \right)_P \approx \frac{p_E - p_W}{2\Delta x}$$

หาก $p$ มีลักษณะสลับฟันปลา (เช่น 10, 0, 10, 0) เกรเดียนต์ที่คำนวณได้จะเป็นศูนย์เสมอ ซึ่งไม่เป็นความจริงทางกายภาพ

```mermaid
flowchart LR
    A[Collocated Grid] --> B[Linear Interpolation]
    B --> C[Checkerboard Pressure Field]
    C --> D[Unphysical Oscillations]

    E[Rhie-Chow Interpolation] --> F[Pressure-Velocity Coupling]
    F --> G[Smooth Pressure Field]
    G --> H[Physical Solution]
```
> **Figure 1:** การเปรียบเทียบระหว่างผลลัพธ์จากการใช้การประมาณค่าแบบเชิงเส้นปกติ (Linear Interpolation) ซึ่งนำไปสู่ปัญหาการแยกตัวของความดันและความเร็ว (Checkerboard pattern) กับการใช้ Rhie-Chow Interpolation ที่ช่วยสร้างการเชื่อมโยงที่แข็งแกร่ง ส่งผลให้ได้สนามความดันที่เรียบและสอดคล้องกับหลักการทางฟิสิกส์บนเมชแบบ Collocated Grid

---

## 🔢 2. การกำหนดสูตรทางคณิตศาสตร์

### 2.1 สูตร Rhie-Chow พื้นฐาน

Rhie-Chow เสนอให้คำนวณความเร็วที่หน้าเซลล์ ($\mathbf{u}_f$) โดยการเพิ่มเทอม Numerical Diffusion ที่ขึ้นกับเกรเดียนต์ความดัน:

$$\mathbf{u}_f = \overline{\mathbf{u}}_f - \mathbf{D}_f (\nabla p_f - \overline{\nabla p}_f) \tag{2.1}$$

**นิยามตัวแปร:**
- $\overline{\mathbf{u}}_f$: ความเร็วที่หน้าเซลล์จากการเฉลี่ยแบบปกติ (Linear interpolation)
- $\mathbf{D}_f = \overline{\left(\frac{1}{a_P}\right)}_f$: สัมประสิทธิ์การแพร่ประสิทธิผลที่หน้าเซลล์
- $\nabla p_f$: เกรเดียนต์ความดันที่คำนวณที่หน้าเซลล์โดยตรง (Compact stencil)
- $\overline{\nabla p}_f$: เกรเดียนต์ความดันจากการเฉลี่ยเกรเดียนต์ที่จุดศูนย์กลางเซลล์

**ความหมายทางกายภาพ:** เทอมในวงเล็บแสดงถึงความแตกต่างระหว่างเกรเดียนต์ "จริง" ที่หน้าเซลล์ กับเกรเดียนต์ "เฉลี่ย" หากค่าทั้งสองเท่ากัน เทอมนี้จะเป็นศูนย์

### 2.2 การอนุพันธ์จากสมการโมเมนตัม

เริ่มจากสมการโมเมนตัมที่ถูกทำให้เป็นดิสครีต:

$$a_P \mathbf{u}_P + \sum_N a_N \mathbf{u}_N = \mathbf{b}_P - (\nabla p)_P$$

จัดเรียงใหม่เพื่อแสดงความเร็ว:

$$\mathbf{u}_P = \frac{\mathbf{b}_P - \sum_N a_N \mathbf{u}_N}{a_P} - \frac{1}{a_P}(\nabla p)_P$$

กำหนด **H-operator**:

$$\mathbf{H}(\mathbf{u}) = \frac{\mathbf{b}_P - \sum_N a_N \mathbf{u}_N}{a_P}$$

ดังนั้น:

$$\mathbf{u}_P = \mathbf{H}(\mathbf{u}) - \frac{1}{a_P}(\nabla p)_P \tag{2.2}$$

สำหรับความเร็วที่หน้าเซลล์:

$$\mathbf{u}_f = \mathbf{H}_f - \left(\frac{1}{a_P}\right)_f (\nabla p)_f$$

ใช้การประมาณค่า Rhie-Chow:

$$\mathbf{u}_f = \overline{\mathbf{H}}_f - \overline{\left(\frac{1}{a_P}\right)}_f \left[ \overline{(\nabla p)}_f - \left( \overline{(\nabla p)}_f - (\nabla p)_f \right) \right]$$

ซึ่งนำไปสู่รูปแบบสุดท้าย:

$$\mathbf{u}_f = \overline{\mathbf{u}}_f - \mathbf{D}_f (\nabla p_f - \overline{\nabla p}_f)$$

### 2.3 ความสัมพันธ์กับสมการความดัน

การใช้ Rhie-Chow interpolation ทำให้ได้สมการความดันที่แข็งแกร่ง:

$$\nabla \cdot \left( \frac{1}{a_P} \nabla p' \right) = \nabla \cdot \mathbf{u}^*$$

เมื่อใช้ความเร็วที่หน้าเซลล์จาก Rhie-Chow:

$$\phi_f = \mathbf{u}_f \cdot \mathbf{S}_f = \left[ \overline{\mathbf{u}}_f - \mathbf{D}_f (\nabla p_f - \overline{\nabla p}_f) \right] \cdot \mathbf{S}_f$$

---

## 💻 3. การนำไปใช้ใน OpenFOAM

### 3.1 โครงสร้างการนำไปใช้งาน

ใน OpenFOAM, Rhie-Chow ถูกนำมาใช้โดยปริยายผ่านการสร้าง **Flux ($\phi$)** ที่หน้าเซลล์ ซึ่งมักพบในไฟล์ `pEqn.H`:

```cpp
// 1. Calculate rAU (reciprocal of diagonal coefficient)
//    This represents 1/aP from the momentum equation discretization
volScalarField rAU(1.0/UEqn.A());

// 2. Calculate HbyA (H operator divided by aP)
//    HbyA represents the explicit part of momentum equation excluding pressure
volVectorField HbyA(constrainHbyA(rAU*UEqn.H(), U, p));

// 3. Create flux with Rhie-Chow correction
//    fvc::flux applies Rhie-Chow interpolation implicitly
surfaceScalarField phiHbyA
(
    "phiHbyA",
    fvc::flux(HbyA) // Interpolate HbyA to faces and dot with Sf
  + fvc::interpolate(rAU)*fvc::ddtCorr(U, phi) // Time derivative correction
);

// 4. Solve pressure equation using Laplacian operator
//    This enforces mass conservation through pressure-velocity coupling
fvScalarMatrix pEqn
(
    fvm::laplacian(rAU, p) == fvc::div(phiHbyA)
);
```

> **📂 Source:** `.applications/solvers/incompressible/simpleFoam/UEqn.H` (based on standard solver structure)  
> **คำอธิบาย:** โค้ดนี้แสดงการนำไปใช้ Rhie-Chow interpolation ใน OpenFOAM โดยอ้อม ผ่านฟังก์ชัน `fvc::flux()` ที่มีการใช้ Rhie-Chow interpolation อยู่ภายใน  
> **แนวคิดสำคัญ:**
> - **rAU**: ค่าผกผันของสัมประสิทธิ์ไดแอกอนัล $a_P$ ใช้เป็นน้ำหนักในการแก้ไขความดัน
> - **HbyA**: H-operator ที่ถูกหารด้วย $a_P$ แทนส่วนของสมการโมเมนตัมที่ไม่ขึ้นกับความดัน
> - **Rhie-Chow Correction**: ถูกนำไปใช้โดยอัตโนมัติใน `fvc::flux()` และ `fvc::interpolate()`
> - **Mass Conservation**: สมการความดันแบบ Laplacian รับประกันการอนุรักษ์มวล

### 3.2 รายละเอียดการทำงานของฟังก์ชัน

#### `fvc::flux(HbyA)`

ฟังก์ชันนี้ทำการประมาณค่า HbyA ไปยังหน้าเซลล์และคำนวณ flux:

```cpp
// Calculate surface flux by interpolating volume field to faces
// and taking dot product with face area vectors
tmp<surfaceScalarField> flux(const volVectorField& vvf)
{
    // Interpolate field from cell centers to faces (Rhie-Chow applied here)
    // Then dot with face surface vector to get flux
    return fvc::interpolate(vvf) & mesh.Sf();
}
```

ซึ่งเทียบเท่ากับ:
$$\phi_f = \overline{\mathbf{H}}_f \cdot \mathbf{S}_f$$

> **📂 Source:** `.applications/solvers/incompressible/simpleFoam/createFields.H` (derived from flux calculation pattern)  
> **คำอธิบาย:** ฟังก์ชัน `flux()` เป็นหัวใจของ Rhie-Chow interpolation ใน OpenFOAM  
> **แนวคิดสำคัญ:**
> - **Interpolation**: การประมาณค่าจาก cell center ไปยัง face ใช้ Rhie-Chow
> - **Face Area Vector**: $\mathbf{S}_f$ คือเวกเตอร์พื้นที่หน้าเซลล์
> - **Flux Definition**: $\phi_f = \mathbf{u}_f \cdot \mathbf{S}_f$ คืออัตราการไหลผ่านหน้าเซลล์
> - **Implicit Rhie-Chow**: การประมาณค่ามี correction term อยู่ภายในอัตโนมัติ

#### `fvc::ddtCorr(U, phi)`

ฟังก์ชันนี้คำนวณเทอมแก้ไขเชิงเวลาสำหรับ transient cases:

```cpp
// Time derivative correction term for transient simulations
// Ensures consistency between volume and surface fields during time stepping
tmp<surfaceScalarField> ddtCorr
(
    const volVectorField& U,
    const surfaceScalarField& phi
)
{
    // Calculate reciprocal of diagonal coefficient
    volScalarField rUA = 1.0/UEqn.A();
    
    // Interpolate rUA from cell centers to faces
    surfaceScalarField rUAf = fvc::interpolate(rUA);

    // Return correction term based on time derivative difference
    // between volume field rate of change and flux divergence
    return fvc::interpolate(rUA) * (fvc::ddt(phi) - fvc::div(phi));
}
```

> **📂 Source:** `.applications/solvers/incompressible/pimpleFoam/pEqn.H` (transient solver pattern)  
> **คำอธิบาย:** เทอมแก้ไขนี้สำคัญสำหรับการจำลองแบบ transient ให้ความสอดคล้องระหว่างฟิลด์ปริมาตรและผิว  
> **แนวคิดสำคัญ:**
> - **Transient Consistency**: รับประกันความสอดคล้องระหว่าง $\frac{\partial U}{\partial t}$ และ $\nabla \cdot \phi$
> - **Time Accuracy**: รักษาความแม่นยำเชิงเวลาอันดับสอง
> - **Mass Conservation**: แก้ไขความไม่สมดุลของมวลในแต่ละ time step

### 3.3 การนำไปใช้ใน Pressure Correction Loop

```cpp
// Pressure correction loop with Rhie-Chow interpolation
// Standard PISO/SIMPLE algorithm implementation in OpenFOAM
while (piso.correct())
{
    // Construct flux with Rhie-Chow interpolation applied
    // This creates the face flux that couples pressure and velocity
    surfaceScalarField phiHbyA
    (
        "phiHbyA",
        fvc::flux(HbyA)  // Rhie-Chow interpolation implicit in flux()
      + fvc::interpolate(rAU)*fvc::ddtCorr(U, phi)  // Time correction
    );

    // Solve pressure Poisson equation
    // This enforces mass conservation: div(phi) = 0
    fvScalarMatrix pEqn
    (
        fvm::laplacian(rAUf, p) == fvc::div(phiHbyA)
    );

    // Set reference pressure value (for incompressible cases)
    pEqn.setReference(pRefCell, pRefValue);
    pEqn.solve();

    // Correct face flux using pressure gradient
    // This updates phi to satisfy continuity
    phi = phiHbyA - pEqn.flux();

    // Correct cell-centered velocity field
    // Uses reconstructed velocity from corrected flux
    U -= rAU*fvc::grad(p);
    U.correctBoundaryConditions();
}
```

> **📂 Source:** `.applications/solvers/incompressible/pisoFoam/pEqn.H` (standard PISO implementation)  
> **คำอธิบาย:** วนจูนการแก้ไขความดันแบบ PISO ที่ใช้ Rhie-Chow interpolation ในการคำนวณ flux  
> **แนวคิดสำคัญ:**
> - **PISO Algorithm**: Pressure Implicit with Splitting of Operators
> - **Flux Calculation**: `phiHbyA` มี Rhie-Chow correction อยู่ภายใน
> - **Pressure Equation**: สมการ Poisson สำหรับความดัน บังคับการอนุรักษ์มวล
> - **Flux Correction**: `phi` ถูกอัปเดตด้วย pressure gradient ผ่าน `pEqn.flux()`
> - **Velocity Reconstruction**: ความเร็วถูกแก้ไขจาก flux ที่ถูกแก้ไขแล้ว

### 3.4 การนำไปใช้ใน `fvc::interpolate`

ภายใน OpenFOAM, การประมาณค่าที่หน้าเซลล์มีการใช้ Rhie-Chow interpolation โดยอัตโนมัติสำหรับฟิลด์ความเร็ว:

```cpp
// In interpolate.C - Rhie-Chow interpolation implementation
// Template function for interpolating volume fields to surface fields
template<class Type>
tmp<GeometricField<Type, fvsPatchField, surfaceMesh>>
interpolate
(
    const GeometricField<Type, fvPatchField, volMesh>& vf,
    const surfaceScalarField& faceFlux
)
{
    // Create interpolated surface field
    tmp<GeometricField<Type, fvsPatchField, surfaceMesh>> tinterp
    (
        new GeometricField<Type, fvsPatchField, surfaceMesh>
        (
            IOobject
            (
                "interpolate(" + vf.name() + ')',
                vf.instance(),
                vf.db(),
                IOobject::NO_READ,
                IOobject::NO_WRITE
            ),
            vf.mesh(),
            dimensioned<Type>("0", vf.dimensions(), 0)
        )
    );

    // Rhie-Chow interpolation logic is applied here
    // Prevents checkerboard patterns by adding pressure-based correction
    // Maintains coupling between pressure and velocity fields
    // Implementation details use explicit pressure gradient differences
    
    return tinterp;
}
```

> **📂 Source:** `.src/finiteVolume/interpolation/surfaceInterpolation/surfaceInterpolation/interpolate.C` (OpenFOAM core interpolation)  
> **คำอธิบาย:** ฟังก์ชัน interpolation พื้นฐานของ OpenFOAM ที่มี Rhie-Chow interpolation อยู่ภายใน  
> **แนวคิดสำคัญ:**
> - **Template Function**: ทำงานกับ field ทุกประเภท (scalar, vector, tensor)
> - **Rhie-Chow Built-in**: Correction ถูกนำไปใช้อัตโนมัติ
> - **Checkerboard Prevention**: ป้องกันการแกว่งของสนามความดัน
> - **Pressure-Velocity Coupling**: รักษาการเชื่อมโยงระหว่างความดันและความเร็ว

### 3.5 การใช้งานร่วมกับ Non-Orthogonal Mesh

สำหรับ Mesh ที่ไม่ตั้งฉาก จะมีการเพิ่มเทอมแก้ไข:

```cpp
// Non-orthogonal correction loop
// Required for meshes where face normals are not aligned with cell centers
for (int nonOrth = 0; nonOrth <= nNonOrthogonalCorrectors; nonOrth++)
{
    // Construct pressure equation with Laplacian
    // For non-orthogonal meshes, this includes explicit correction terms
    fvScalarMatrix pEqn
    (
        fvm::laplacian(rAUf, p) == fvc::div(phiHbyA)
    );

    // Set reference pressure only on final iteration
    if (nonOrth == nNonOrthogonalCorrectors)
    {
        pEqn.setReference(pRefCell, pRefValue);
    }

    // Solve pressure equation with appropriate solver settings
    pEqn.solve(mesh.solver(p.select(piso.finalInnerIter())));

    // Update flux only on final non-orthogonal correction
    if (nonOrth == nNonOrthogonalCorrectors)
    {
        phi = phiHbyA - pEqn.flux();
    }
}
```

> **📂 Source:** `.applications/solvers/incompressible/simpleFoam/pEqn.H` (non-orthogonal mesh handling)  
> **คำอธิบาย:** การจัดการ Mesh ที่ไม่ตั้งฉากด้วยการวนซ้ำการแก้ไขเพิ่มเติม  
> **แนวคิดสำคัญ:**
> - **Non-Orthogonality**: เกิดเมื่อ face normal ไม่ผ่าน line ระหว่าง cell centers
> - **Explicit Correction**: ใช้การแก้ไขแบบ explicit สำหรับ non-orthogonal terms
> - **Multiple Iterations**: ต้องการหลายครั้งเพื่อลู่เข้า
> - **Flux Update**: อัปเดต flux เฉพาะใน iteration สุดท้าย

---

## 📊 4. การวิเคราะห์และการประเมินผล

### 4.1 การเปรียบเทียบกับ Staggered Grid

| คุณสมบัติ | Staggered Grid | Collocated with Rhie-Chow |
|-----------|----------------|---------------------------|
| **การจัดเรียงตัวแปร** | ความดันที่ center, ความเร็วที่ faces | ทั้งคู่ที่ center |
| **ปัญหา Checkerboard** | ไม่เกิดโดยธรรมชาติ | ต้องใช้ Rhie-Chow |
| **ความซับซ้อนของโค้ด** | สูง (หลาย data structures) | ต่ำ (single data structure) |
| **ความยืดหยุ่น Mesh** | จำกัด (ส่วนใหญ่ structured) | สูง (unstructured ได้) |
| **ความแม่นยำ** | เทียบเท่า | เทียบเท่า |

### 4.2 การประเมินคุณภาพการแก้ปัญหา

**เกณฑ์ความสำเร็จ:**
1. **Smoothness**: สนามความดันต้องเรียบและไม่มีการแกว่ง
2. **Convergence**: การลู่เข้าของ solver ต้องเสถียร
3. **Mass Conservation**: การอนุรักษ์มวลต้องเป็นไปตามสมการความต่อเนื่อง
4. **Accuracy**: ความแม่นยำต้องเป็นอันดับสอง

### 4.3 การวิเคราะห์ข้อผิดพลาด

ข้อผิดพลาดจาก Rhie-Chow interpolation:

$$\epsilon_{RC} = \mathcal{O}(\Delta x^2) + \mathcal{O}(\Delta x^3 \frac{\partial^3 p}{\partial x^3})$$

สำหรับกริดที่สม่ำเสมอ เทอมหลักเป็นอันดับสอง ซึ่งสอดคล้องกับการประมาณค่าแบบ linear

---

## ✅ 5. ประโยชน์และข้อจำกัด

### 5.1 ประโยชน์

1. **ขจัด Checkerboard oscillations**: ทำให้สนามความดันเรียบและลู่เข้าได้ง่าย
2. **รักษาความแม่นยำ**: ยังคงความแม่นยำระดับอันดับสอง (Second-order accuracy)
3. **รองรับ Unstructured Mesh**: สามารถใช้งานได้กับ Mesh ที่ซับซ้อนใน OpenFOAM ได้อย่างมีประสิทธิภาพ
4. **ความเรียบง่ายในการนำไปใช้**: ไม่ต้องการ data structures แบบ staggered
5. **รักษาการอนุรักษ์มวล**: ทำให้การคำนวณ flux สอดคล้องกับสมการความต่อเนื่อง

### 5.2 ข้อจำกัด

1. **Numerical Diffusion**: การเพิ่มเทอม correction อาจเพิ่ม numerical diffusion
2. **ความไวต่อคุณภาพ Mesh**: ผลลัพธ์ขึ้นอยู่กับคุณภาพของ Mesh อย่างมาก
3. **Complexity ในการนำไปใช้**: ต้องเข้าใจรายละเอียดของการทำ interpolation อย่างลึกซึ้ง
4. **การปรับแต่งพารามิเตอร์**: บางครั้งต้องปรับเทอม correction สำหรับกรณีเฉพาะ

---

## 🔍 6. แนวทางปฏิบัติที่ดีที่สุด

### 6.1 การตรวจสอบคุณภาพ

```bash
# ตรวจสอบคุณภาพ Mesh
checkMesh -allGeometry -allTopology

# ตรวจสอบค่า orthogonality
checkMesh -ortho
```

**เกณฑ์ที่แนะนำ:**
- Non-orthogonality < 70°
- Skewness < 2
- Aspect ratio < 1000

### 6.2 การตั้งค่า Solver

```cpp
// ใน fvSolution
PIMPLE
{
    nCorrectors 2;
    nNonOrthogonalCorrectors 1;  // เพิ่มสำหรับ non-orthogonal mesh
    pRefCell 0;
    pRefValue 0;
}

// ใน fvSchemes สำหรับ interpolation schemes
interpolationSchemes
{
    interpolate(HbyA) linear;  // ใช้ linear interpolation
}
```

### 6.3 การแก้ไขปัญหา

| ปัญหา | อาการ | แนวทางแก้ไข |
|--------|---------|---------------|
| **Checkerboard patterns** | สนามความดันแกว่ง | ตรวจสอบว่า Rhie-Chow ถูกนำไปใช้อย่างถูกต้อง |
| **Slow convergence** | Residual ลดช้า | ปรับค่า under-relaxation หรือเพิ่ม nCorrectors |
| **Mass imbalance** | Flux ไม่สอดคล้อง | ตรวจสอบ boundary conditions และ mesh quality |
| **Divergence** | Solver ไม่ลู่เข้า | ลด time step หรือปรับ mesh quality |

---

## 📚 7. ตัวอย่างการนำไปใช้

### 7.1 กรณีศึกษา: Lid-Driven Cavity

```cpp
// In pEqn.H for lid-driven cavity flow
// Standard pressure-velocity coupling for incompressible flow
volScalarField rAU(1.0/UEqn.A());
volVectorField HbyA(constrainHbyA(rAU*UEqn.H(), U, p));

// Construct flux with Rhie-Chow interpolation
surfaceScalarField phiHbyA
(
    "phiHbyA",
    fvc::flux(HbyA)
  + fvc::interpolate(rAU)*fvc::ddtCorr(U, phi)
);

// Solve pressure Poisson equation
fvScalarMatrix pEqn
(
    fvm::laplacian(rAU, p) == fvc::div(phiHbyA)
);

pEqn.setReference(pRefCell, pRefValue);
pEqn.solve();

// Correct flux using pressure gradient
phi = phiHbyA - pEqn.flux();
```

> **📂 Source:** `.applications/tutorials/incompressible/icoFoam/cavity/cavity/system/pEqn.H` (lid-driven cavity tutorial)  
> **คำอธิบาย:** การใช้ Rhie-Chow interpolation สำหรับปัญหา lid-driven cavity  
> **แนวคิดสำคัญ:**
> - **Canonical Test Case**: Lid-driven cavity เป็นปัญหามาตรฐานสำหรับทดสอบ solver
> - **Pressure-Velocity Coupling**: ใช้ Rhie-Chow เพื่อให้ได้ coupling ที่ถูกต้อง
> - **Mass Conservation**: สมการความดันรับประกันการอนุรักษ์มวล
> - **Flux Correction**: การแก้ไข flux ผ่าน pressure equation

### 7.2 การติดตามผลลัพธ์

```python
# Python script for monitoring pressure field smoothness
# Helps verify Rhie-Chow interpolation is working correctly
import numpy as np
import matplotlib.pyplot as plt

# Read pressure data from OpenFOAM output
p = np.loadtxt('postProcessing/pressureField/0/p')

# Check smoothness by calculating gradient standard deviation
gradient_p = np.gradient(p)
smoothness = np.std(gradient_p)

plt.plot(p)
plt.title(f'Pressure Field (Smoothness: {smoothness:.2e})')
plt.xlabel('Cell Index')
plt.ylabel('Pressure (Pa)')
plt.grid(True)
plt.show()
```

> **📂 Source:** Custom post-processing script (not part of OpenFOAM source)  
> **คำอธิบาย:** Script สำหรับตรวจสอบความเรียบของสนามความดัน  
> **แนวคิดสำคัญ:**
> - **Gradient Analysis**: ใช้ gradient เพื่อตรวจจับการแกว่ง
> - **Smoothness Metric**: ส่วนเบี่ยงเบนมาตรฐานของ gradient ต่ำ = สนามเรียบ
> - **Verification Tool**: ช่วยตรวจสอบว่า Rhie-Chow ทำงานถูกต้อง

---

## 🔗 8. การเชื่อมโยงกับ Algorithm การเชื่อมโยงความดัน-ความเร็ว

### 8.1 การใช้ใน SIMPLE Algorithm

```cpp
// SIMPLE algorithm uses Rhie-Chow in every iteration
// Semi-Implicit Method for Pressure-Linked Equations
while (simple.loop())
{
    // Momentum predictor (solve momentum equation excluding pressure)
    solve(UEqn == -fvc::grad(p));

    // Calculate Rhie-Chow flux
    // This interpolation prevents checkerboard pressure patterns
    volScalarField rAU(1.0/UEqn.A());
    surfaceScalarField phiHbyA(fvc::flux(HbyA) + fvc::interpolate(rAU)*fvc::ddtCorr(U, phi));

    // Pressure correction (solve pressure Poisson equation)
    fvScalarMatrix pEqn(fvm::laplacian(rAU, p) == fvc::div(phiHbyA));
    pEqn.solve();

    // Correct flux using pressure gradient from solution
    phi = phiHbyA - pEqn.flux();
}
```

> **📂 Source:** `.applications/solvers/incompressible/simpleFoam/simpleFoam.C` (SIMPLE solver implementation)  
> **คำอธิบาย:** SIMPLE algorithm ใช้ Rhie-Chow interpolation ในทุก iteration  
> **แนวคิดสำคัญ:**
> - **SIMPLE**: Semi-Implicit Method for Pressure-Linked Equations
> - **Steady-State**: ใช้สำหรับ steady-state problems
> - **Under-Relaxation**: ต้องการ under-relaxation factors สำหรับความเสถียร
> - **Rhie-Chow in Flux**: ทุกการคำนวณ flux ใช้ Rhie-Chow interpolation

### 8.2 การใช้ใน PISO Algorithm

```cpp
// PISO algorithm uses Rhie-Chow in every correction step
// Pressure Implicit with Splitting of Operators
for (int corr = 0; corr < nCorrectors; corr++)
{
    // Construct flux with Rhie-Chow interpolation
    // Critical for maintaining pressure-velocity coupling
    surfaceScalarField phiHbyA(fvc::flux(HbyA) + fvc::interpolate(rAU)*fvc::ddtCorr(U, phi));

    // Pressure correction (solve pressure Poisson equation)
    fvScalarMatrix pEqn(fvm::laplacian(rAUf, p) == fvc::div(phiHbyA));
    pEqn.solve();

    // Correct flux using pressure gradient
    // This updates mass flux to satisfy continuity
    phi = phiHbyA - pEqn.flux();
}
```

> **📂 Source:** `.applications/solvers/incompressible/pisoFoam/pEqn.H` (PISO solver implementation)  
> **คำอธิบาย:** PISO algorithm ใช้ Rhie-Chow ในทุก correction step  
> **แนวคิดสำคัญ:**
> - **PISO**: Pressure Implicit with Splitting of Operators
> - **Transient**: ใช้สำหรับ transient simulations
> - **Multiple Corrections**: ใช้หลาย correction steps ต่อ time step
> - **No Under-Relaxation**: ไม่ต้องการ under-relaxation สำหรับ transient cases

---

## 📖 9. บทสรุป

**Rhie-Chow interpolation** เป็นเทคนิคสำคัญใน OpenFOAM ที่ทำให้การจำลอง CFD บน collocated grid เป็นไปได้อย่างมีประสิทธิภาพ:

1. **แก้ปัญหา Checkerboard**: ป้องกันการแกว่งของสนามความดัน
2. **รักษาความแม่นยำ**: ยังคงความแม่นยำอันดับสอง
3. **รองรับ Mesh ซับซ้อน**: ใช้ได้กับ unstructured mesh
4. **นำไปใช้โดยอัตโนมัติ**: มีการใช้งานใน OpenFOAM โดยปริยาย

การทำความเข้าใจ Rhie-Chow interpolation เป็นสิ่งสำคัญสำหรับการทำ CFD การจำลองที่เสถียรและแม่นยำ

---

**หัวข้อถัดไป**: [[การเปรียบเทียบอัลกอริทึมต่างๆ]](./05_Algorithm_Comparison.md)