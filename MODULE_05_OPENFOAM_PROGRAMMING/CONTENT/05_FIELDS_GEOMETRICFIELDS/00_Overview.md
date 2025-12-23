# โมดูล 05.05: Fields และ GeometricFields ใน OpenFOAM

> [!INFO] **ภาพรวมโมดูล**
> โมดูลนี้ศึกษา **GeometricField** ซึ่งเป็นหัวใจของการประมวลผลข้อมูลใน OpenFOAM — ออบเจกต์ที่รวมเอาข้อมูลเชิงตัวเลข เรขาคณิตของเมช และมิติทางฟิสิกส์เข้าด้วยกันอย่างสมบูรณ์

---

## แผนภาพโดยรวม

```mermaid
flowchart TD
    A[GeometricField Overview] --> B[Design Philosophy]
    B --> C[Inheritance Hierarchy]
    C --> D[Field Lifecycle]
    D --> E[Type Theory & Safety]
    E --> F[Common Pitfalls]
    F --> G[Summary & Exercises]

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style G fill:#00ff00,stroke:#333,stroke-width:2px
```
> **Figure 1:** แผนผังลำดับการเรียนรู้ในโมดูลเรื่องฟิลด์และฟิลด์เรขาคณิต (GeometricField) ครอบคลุมตั้งแต่สถาปัตยกรรมพื้นฐานไปจนถึงทฤษฎีประเภททางคณิตศาสตร์และการแก้ปัญหาขั้นสูงความปลอดภัยทางฟิสิกส์ไม่ส่งผลกระทบต่อความเร็วในการจำลอง ผ่านการใช้พลังของ C++ Template Metaprogramming ในการตรวจสอบความสอดคล้องทางมิติทั้งหมดที่ขั้นตอนการคอมไพล์โปรแกรมเพียงครั้งเดียว

## วัตถุประสงค์การเรียนรู้

- เข้าใจความแตกต่างระหว่าง `DimensionedField` และ `GeometricField`
- สามารถวิเคราะห์ลำดับชั้นการสืบทอดที่ซับซ้อนของคลาสฟิลด์ได้
- เข้าใจกลไกการทำงานของเงื่อนไขขอบเขต (Boundary Conditions) ที่ฝังอยู่ในฟิลด์
- สามารถเขียนโค้ดเพื่อจัดการฟิลด์ได้อย่างมีประสิทธิภาพและปลอดภัย
- รู้วิธีการดีบักปัญหาความไม่สอดคล้องของมิติในระดับสูง

---

## หัวข้อหลัก

1. **ลำดับชั้นคลาส Field (Inheritance Hierarchy)**: การสืบทอดจาก `List` → `Field` → `GeometricField`
2. **กรอบงานคณิตศาสตร์ (Mathematical Framework)**: การดำเนินการ Gradient, Divergence และ Laplacian บนฟิลด์
3. **Interpolation Schemes**: การประมาณค่าระหว่างจุดศูนย์กลางเซลล์และหน้า
4. **Boundary Conditions**: การจัดการเงื่อนไขขอบเขตที่ฝังตัวในฟิลด์
5. **Field Algebra**: พีชคณิตของฟิลด์และการประกอบเมทริกซ์
6. **ประสิทธิภาพและการจัดการหน่วยควาจำ**: การใช้ `tmp` และระบบ Reference Counting
7. **สรุปและแบบฝึกหัด (Summary & Exercises)**

---

## 1. ประเภท Field และลำดับชั้น

**ระบบการจัดการ field ของ OpenFOAM** เป็นพื้นฐานของการคำนวณ CFD โดยให้โครงสร้างลำดับชั้นสำหรับการจัดการข้อมูลการคำนวณข้ามแบบจำลองการกระจายต่างๆ และประเภท entity ฟิลด์

### 1.1 Fundamental Field Classes

**ลำดับชั้น field หลัก** ใน OpenFOAM ทำตามสถาปัตยกรรมแบบเลเยอร์:

```cpp
// Base field template classes
template<class Type>
class Field : public List<Type>
{
    // Stores field data as a list of values
    // Provides basic field operations and access
};

template<class Type, class GeoMesh>
class GeometricField : public DimensionedField<Type, GeoMesh>
{
    // Geometric field with spatial discretization information
    // Contains boundary conditions and interpolation functions
};
```

**ความแตกต่างที่สำคัญ** ระหว่าง `Field<Type>` และ `GeometricField<Type, GeoMesh>` อยู่ในบริบทการคำนวณ:

- **`Field<Type>`**: เป็นคอนเทนเนอร์ข้อมูลบริสุทธิ์โดยไม่มีบริบททางเรขาคณิต
- **`GeometricField<Type, GeoMesh>`**: คอนเทนเนอร์ข้อมูลที่มีข้อมูลการกระจายทางเรขาคณิต

### 1.2 Volume Fields

**Volume fields** แทนปริมาณที่นิยามที่จุดศูนย์กลางของเซลล์:

```cpp
// Volume field specializations
typedef GeometricField<scalar, fvPatchField, volMesh> volScalarField;
typedef GeometricField<vector, fvPatchField, volMesh> volVectorField;
typedef GeometricField<tensor, fvPatchField, volMesh> volTensorField;
typedef GeometricField<symmTensor, fvPatchField, volMesh> volSymmTensorField;
```

### 1.3 Surface Fields

**Surface fields** แทนปริมาณที่นิยามบนพื้นผิวของเซลล์:

```cpp
// Surface field specializations
typedef GeometricField<scalar, fvsPatchField, surfaceMesh> surfaceScalarField;
typedef GeometricField<vector, fvsPatchField, surfaceMesh> surfaceVectorField;
```

---

## 2. Field Operations และกรอบงานคณิตศาสตร์

**OpenFOAM fields** รองรับชุดของการดำเนินการทางคณิตศาสตร์อย่างครบถ้วน

### 2.1 Gradient Operations

**Gradient operator** แปลง volume fields เป็น surface fields:

$$\nabla \phi = \frac{\partial \phi}{\partial x_i} \mathbf{e}_i$$

ใน OpenFOAM:

```cpp
// Gradient of a scalar field
volVectorField gradPhi = fvc::grad(phi);

// For general tensor fields
template<class Type>
GeometricField<typename outerProduct<vector, Type>::type, fvPatchField, volMesh>
grad(const GeometricField<Type, fvPatchField, volMesh>& vf);
```

**การดำเนินการ gradient** ใช้ทฤษฎีบทของ Gauss:

$$\int_V \nabla \phi \, \mathrm{d}V = \oint_S \phi \mathbf{n} \, \mathrm{d}S$$

ซึ่งกระจายเป็น:

$$\nabla \phi|_P = \frac{1}{V_P} \sum_f \phi_f \mathbf{S}_f$$

### 2.2 Divergence Operations

**Divergence operator** แปลง surface fields เป็น volume fields:

$$\nabla \cdot \mathbf{F} = \frac{\partial F_i}{\partial x_i}$$

```cpp
// Divergence of a vector field (surfaceScalarField flux)
volScalarField divF = fvc::div(F);
```

### 2.3 Laplacian Operations

**Laplacian operator** เป็นพื้นฐานสำหรับเทอมการแพร่:

$$\nabla^2 \phi = \nabla \cdot (\nabla \phi)$$

```cpp
// Laplacian with constant diffusivity
volScalarField lapPhi = fvc::laplacian(D, phi);
```

---

## 3. Interpolation Schemes และ Field Transformations

### 3.1 Linear Interpolation

**Linear interpolation** สมมติว่ามีการเปลี่ยนแปลงเชิงเส้นระหว่างจุดศูนย์กลางของเซลล์:

$$\phi_f = f_P \phi_P + f_N \phi_N$$

โดยที่ $f_P = \frac{d_{fN}}{d_{PN}}$ และ $f_N = \frac{d_{fP}}{d_{PN}}$

### 3.2 Interpolation Scheme Comparison

| Scheme | Order | Stability | Accuracy | Use Case |
|--------|-------|-----------|----------|----------|
| Linear | 1st | Stable | Moderate | General purpose |
| Quadratic | 2nd | Moderate | High | Smooth flows |
| QUICK | 3rd | Conditional | Very High | Convection-dominated |
| MUSCL | 2nd | High | High | Shock-capturing |

---

## 4. Boundary Conditions และ Field Coupling

### 4.1 Boundary Condition Architecture

**แต่ละ geometric field** รักษาข้อมูลเงื่อนไขขอบเขต:

```cpp
template<class Type, class PatchField, class GeoMesh>
class GeometricField : public DimensionedField<Type, GeoMesh>
{
    // Boundary field container
    GeometricBoundaryField<PatchField, GeoMesh> boundaryField_;

    // Individual boundary patches
    const Field<Type>& boundaryField(const label patchi) const;
    Field<Type>& boundaryField(const label patchi);
};
```

### 4.2 Common Boundary Condition Types

| Type | Formula | Parameters | Use Case |
|------|---------|------------|----------|
| fixedValue | $\phi = \phi_{specified}$ | Value | Inlet, specified temperature |
| fixedGradient | $\nabla \phi \cdot \mathbf{n} = g_{specified}$ | Gradient | Wall heat flux |
| zeroGradient | $\nabla \phi \cdot \mathbf{n} = 0$ | None | Outlet, symmetry |
| mixed | $\phi = \alpha \phi_{value} + (1-\alpha) \phi_{gradient}$ | valueFraction | Robin conditions |

---

## 5. Field Algebra และ Matrix Assembly

**Fields** รองรับการดำเนินการทางพีชคณิตอย่างครบถ้วน

### 5.1 Implicit vs Explicit Operations

**Explicit Operations:** ค่าถูกคำนวณโดยตรงโดยใช้ค่า field ปัจจุบัน

```cpp
// Explicit convection term
surfaceScalarField phi_f = linearInterpolate<vector>(U) & mesh.Sf();
volScalarField convection = fvc::div(phi_f);
```

**Implicit Operations:** เทอร์มที่ส่งผลต่อเมทริกซ์สัมประสิทธิ์

```cpp
// Implicit diffusion term
fvScalarMatrix TEqn
(
    fvm::laplacian(DT, T)  // Implicit treatment
  - fvc::ddt(T)           // Explicit source term
);
```

---

## 6. Performance Optimization และ Memory Management

### 6.1 Reference Counting และ Memory Efficiency

**OpenFOAM** ใช้การจัดการหน่วยควาจำที่ซับซ้อน:

```cpp
// Reference-counted field types
typedef tmp<GeometricField<Type, PatchField, GeoMesh>> tmpGeometricField;

// Automatic memory management
tmp<volScalarField> divU = fvc::div(U);
// tmp object automatically deleted when scope ends
```

### 6.2 Field Caching และ Reuse

**การคำนวณ field ทั่วไป** จะถูก cached:

```cpp
// Gradient caching mechanism
const volVectorField& gradU = gradCache.lookup(U);
if (!gradU.valid())
{
    gradU = new volVectorField(fvc::grad(U));
    gradCache.store(U, gradU);
}
```

---

## 7. Advanced Field Operations

### 7.1 Tensor Field Operations

**Tensor fields** รองรับการดำเนินการเฉพาะ:

```cpp
// Tensor deformation rate
volTensorField D = symm(fvc::grad(U));

// Vorticity tensor
volTensorField W = skew(fvc::grad(U));

// Stress tensor for Newtonian fluid
volSymmTensorField tau = 2 * nu * D;
```

**Tensor Operation Equations:**
- **Deformation rate**: $\mathbf{D} = \frac{1}{2}(\nabla \mathbf{u} + \nabla \mathbf{u}^T)$
- **Vorticity tensor**: $\mathbf{W} = \frac{1}{2}(\nabla \mathbf{u} - \nabla \mathbf{u}^T)$
- **Stress tensor**: $\boldsymbol{\tau} = 2\mu \mathbf{D}$

---

## 8. Field I/O และ Data Persistence

### 8.1 Field Serialization

**Fields** สามารถเขียนและอ่านจากดิสก์:

```cpp
// Write field to disk
phi.write();

// Read field from disk
volScalarField phi
(
    IOobject
    (
        "phi",
        runTime.timeName(),
        mesh,
        IOobject::MUST_READ,
        IOobject::AUTO_WRITE
    ),
    mesh
);
```

---

## 9. Debugging และ Field Diagnostics

### 9.1 Field Validation

**เครื่องมือตรวจสอบ field**:

```cpp
// Check field bounds
scalar minVal = min(phi);
scalar maxVal = max(phi);

// Check for NaN or inf values
if (hasNaN(phi))
{
    FatalErrorIn("field computation") << "NaN detected" << exit(FatalError);
}
```

### 9.2 Field Statistics และ Analysis

**ความสามารถในการวิเคราะห์ทางสถิติ**:

```cpp
// Field statistics
scalar meanVal = average(phi);
scalar rmsVal = sqrt(sum(phi*phi)/phi.size());
```

---

## สรุป

**ระบบ field ของ OpenFOAM** ให้กรอบงานที่ครอบคลุมสำหรับการคำนวณ CFD โดยผสานผสาน:

- **ความเข้มงวดทางคณิตศาสตร์** ผ่านระบบประเภทและการวิเคราะห์มิติ
- **ประสิทธิภาพการคำนวณ** ผ่าน expression templates และ reference counting
- **ความสอดคล้องทางกายภาพ** ผ่านการจัดการ boundary conditions และ mesh-aware operations

**สถาปัตยกรรมที่ใช้เทมเพลต** ทำให้การดำเนินการประเภทที่ปลอดภัยได้ในขณะที่รักษาประสิทธิภาพผ่านการจัดการหน่วยความำที่เพิ่มประสิทธิภาพและการ assembly สัมประสิทธิ์อัตโนมัติ
