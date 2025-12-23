# สถาปัตยกรรมของคลาส Time

![[chronos_controller.png]]
`A high-tech clock tower representing the Time class. The clock hands move in discrete steps (deltaT). From the tower, pneumatic tubes (File I/O) lead to different folders labeled "0", "0.1", "0.2", scientific textbook diagram, clean vector line art, white background, high definition, flat design, educational infographic --ar 16:9`

---

## 1. รู้จักคลาส `Time`: ผู้ควบคุมการเดินทางข้ามเวลา

คลาส `Time` ใน OpenFOAM คือ ==ผู้อำนวยความสะดวกหลัก== ในการควบคุมการจำลองแบบ CFD ทั้งหมด มันทำหน้าที่เป็น **Chronos Controller** ที่จัดการ:

- **การก้าวเวลา** (time stepping) จาก `startTime` ถึง `endTime`
- **การบันทึกข้อมูล** (data writing) ลงในโฟลเดอร์ตามลำดับเวลา (`0/`, `0.1/`, `0.2/`, ...)
- **การติดตามดัชนีเวลา** (time indexing) สำหรับการแก้สมการที่ขึ้นกับเวลา
- **การอ่าน/เขียนไฟล์** อัตโนมัติผ่านระบบ `regIOobject`

```cpp
// การประกาศคลาส Time แบบง่าย
class Time : public IOobject, public clock {
private:
    scalar startTime_;       // เวลาเริ่มต้น [s]
    scalar endTime_;         // เวลาสิ้นสุด [s]
    scalar deltaT_;          // ขนาดก้าวเวลา [s]
    scalar value_;           // ค่าเวลาปัจจุบัน [s]
    label timeIndex_;        // ดัชนีเวลาปัจจุบัน

public:
    // การควบคุมการวนซ้ำเวลา
    bool loop() {
        value_ += deltaT_;
        timeIndex_++;
        return value_ < endTime_;
    }

    // การเข้าถึงข้อมูลเวลา
    const word& timeName() const;      // ชื่อโฟลเดอร์เวลา เช่น "0.5"
    scalar value() const;               // ค่าเวลาปัจจุบัน
    scalar deltaTValue() const;         // ขนาดก้าวเวลา
};
```

> [!INFO] **Time vs runTime**
> ในโค้ด solver คุณมักจะเห็น `runTime` ซึ่งเป็นออบเจกต์ `Time` ที่ถูกสร้างขึ้นในสคริปต์สำหรับการจำลองแบบ:
> ```cpp
> Foam::Time runTime(Foam::Time::controlDictName, args);
> ```

---

## 2. แบบแผน: สถาปัตยกรรมเทมเพลตและโครงสร้างการสืบทอด

### **2.1 พารามิเตอร์เทมเพลตหลัก: "รหัสพันธุกรรม"**

ที่หัวใจของระบบฟิลด์ของ OpenFOAM มีเทมเพลต `GeometricField` - ซึ่งเป็นหนึ่งในการออกแบบเทมเพลตที่ซับซ้อนที่สุดในพลศาสตร์ของไหลเชิงคำนวณ เทมเพลตนี้แสดงถึงการสรุปความหมายขั้นสูงสุดของปริมาณทางกายภาพในการจำลอง CFD:

```cpp
template<class Type, template<class> class PatchField, class GeoMesh>
class GeometricField : public DimensionedField<Type, GeoMesh>
```

พารามิเตอร์เทมเพลตทั้งสามนี้สร้างระบบข้อกำหนดที่สมบูรณ์ที่ตอบคำถามพื้นฐานของการแสดงฟิลด์ทางกายภาพ:

#### **พารามิเตอร์ Type: ปริมาณทางกายภาพ**

พารามิเตอร์ `Type` กำหนด **สิ่งที่** เรากำลังแสดงถึง ชนิด C++ พื้นฐานนี้กำหนดลักษณะทางคณิตศาสต์ของฟิลด์:

- `scalar`: ปริมาณค่าเดียวเช่น อุณหภูมิ ความดัน ความหนาแน่น
- `vector`: ปริมาณสามมิติเช่น ความเร็ว โมเมนตัม ตำแหน่ง
- `tensor`: เทนเซอร์อันดับสองเช่น ความเค้น อัตราการไหล เมทริกซ์การหมุน
- `symmTensor`: เทนเซอร์สมมาตรสำหรับความเค้น/ความเครียดสมมาตร
- `sphericalTensor`: เทนเซอร์ทรงกลมสำหรับคุณสมบัติไอโซทรอปิก

![[of_field_types_viz.png]]
`A visualization of different field types (Scalar, Vector, Tensor) mapped onto a 3D CFD mesh, showing how data rank affects the physical representation, scientific textbook diagram, clean vector line art, white background, high definition, flat design, educational infographic --ar 16:9`

ระบบชนิดนี้จะรับประกันความสม่ำเสมอทางคณิตศาสตตลอดการจำลอง - คุณไม่สามารถบวกฟิลด์เวคเตอร์กับฟิลด์สกาลาร์โดยไม่ตั้งใจได้

#### **พารามิเตอร์ PatchField: พฤติกรรมขอบเขต**

พารามิเตอร์เทมเพลต `PatchField` กำหนด **วิธี** ที่ฟิลด์มีพฤติกรรมที่ขอบเขต ซึ่งเป็นสิ่งสำคัญสำหรับ CFD ที่ซึ่งเงื่อนไขขอบเขตมักขับเคลื่อนฟิสิกส์:

```cpp
template<class Type>
class fvPatchField {
    virtual void evaluate(const Pstream::commsTypes commsType) = 0;
    virtual void operator=(const fvPatchField<Type>&) = 0;
};
```

ชนิด `PatchField` ทั่วไป ได้แก่:

- `fvPatchField`: เงื่อนไขขอบเขตปริมาตรจำกัด (Dirichlet, Neumann, Robin)
- `pointPatchField`: เงื่อนไขขอบเขตยึดตามจุดสำหรับการเปลี่ยนรูปเมช
- `fvsPatchField`: เงื่อนไขขอบเขตฟิลด์พื้นผิวสำหรับการคำนวณฟลักซ์

#### **พารามิเตอร์ GeoMesh: โดเมนเชิงพื้นที่**

พารามิเตอร์ `GeoMesh` กำหนด **ตำแหน่งที่** ค่าฟิลด์ตั้งอยู่ภายในโดเมนการคำนวณ:

```cpp
class volMesh {
    // ค่าฟิลด์ที่จุดศูนย์ถ่วงของเซลล์
    // ตำแหน่งหลักสำหรับการเปลี่ยนรูปปริมาตรจำกัด
};

class surfaceMesh {
    // ค่าฟิลด์ที่จุดศูนย์ถ่วงของหน้า
    // ตำแหน่งตามธรรมชาติสำหรับการคำนวณฟลักซ์
};

class pointMesh {
    // ค่าฟิลด์ที่จุดเมช
    // ใช้สำหรับการเคลื่อนที่ของเมชและการแปลงค่า
};
```

| พารามิเตอร์ | ความหมายทางกายภาพ | ค่าเทียบเท่า CFD | ตัวอย่าง |
|-----------|------------------|----------------|---------|
| `Type` | **สิ่งที่** เราวัด | ชนิดข้อมูลฟิลด์ | `scalar` (อุณหภูมิ), `vector` (ความเร็ว) |
| `PatchField` | **วิธี** ขอบเขตมีพฤติกรรม | ชนิดเงื่อนไขขอบเขต | `fvPatchField` (ปริมาตรจำกัด), `pointPatchField` (จุด) |
| `GeoMesh` | **ตำแหน่งที่** การวัดอยู่ | ชนิดเรขาคณิตเมช | `volMesh` (เซลล์), `surfaceMesh` (หน้า), `pointMesh` (จุด) |

---

### **2.2 ลำดับชั้นการสืบทอด: "ต้นไม้ตระกูล"**

คลาส `GeometricField` สืบทอดมาจากลำดับชั้นที่สร้างขึ้นอย่างระมัดระวังซึ่งสร้างฟังก์ชันการทำงานเป็นชั้นๆ:

![[of_geometricfield_inheritance.png]]
`A diagram showing the inheritance hierarchy of GeometricField, from the base Field container through DimensionedField to the final complete GeometricField object, scientific textbook diagram, clean vector line art, white background, high definition, flat design, educational infographic --ar 16:9`

```
Field<Type> (คอนเทนเนอร์ข้อมูลดิบ)
    ↑
regIOobject (ความสามารถ I/O)
    ↑
DimensionedField<Type, GeoMesh> (หน่วยทางกายภาพ + การอ้างอิงเมช)
    ↑
GeometricField<Type, PatchField, GeoMesh> (ฟิลด์สมบูรณ์พร้อมขอบเขต)
    |
    ├── internalField_ (ค่าที่จุดศูนย์ถ่วงเซลล์)
    ├── boundaryField_ (ค่าหน้าขอบเขต)
    ├── timeIndex_ (การติดตามเวลา)
    └── การอ้างอิงเมช (บริบทเชิงพื้นที่)
```

#### **ชั้นรากฐาน: Field<Type>**

คลาสฐาน `Field<Type>` ให้การจัดเก็บข้อมูลดิบและการดำเนินการทางคณิตศาสตร์พื้นฐาน:

```cpp
template<class Type>
class Field : public List<Type> {
public:
    // การดำเนินการทางคณิตศาสตร์
    Field<Type>& operator=(const Field<Type>&);
    Field<Type>& operator+=(const Field<Type>&);
    Field<Type>& operator*=(const scalarField&);

    // การดำเนินการลดลง
    Type sum() const;
    Type max() const;
    Type min() const;
};
```

#### **ชั้น I/O: regIOobject**

คลาส `regIOobject` เพิ่มความสามารถ I/O ไฟล์อัตโนมัติโดยใช้ระบบรีจิสทรีออบเจกต์ของ OpenFOAM:

```cpp
class regIOobject : public IOobject {
    // ฟังก์ชันการอ่าน/เขียนอัตโนมัติ
    bool readIfModified();
    bool writeObject(IOstream::streamFormat fmt) const;

    // การจัดการรีจิสทรี
    void checkOut();
    void rename(const word& newName);
};
```

#### **ชั้นทางกายภาพ: DimensionedField**

คลาส `DimensionedField` เพิ่มมิติทางกายภาพและการเชื่อมโยงเมช:

```cpp
template<class Type, class GeoMesh>
class DimensionedField : public Field<Type>, public regIOobject, public GeoMesh {
    dimensionSet dimensions_;  // มิติทางกายภาพ (M, L, T, θ, I, N, J)
    const GeoMesh& mesh_;      // การอ้างอิงถึงเมช

public:
    const dimensionSet& dimensions() const { return dimensions_; }
    const GeoMesh& mesh() const { return mesh_; }
};
```

#### **ชั้นสมบูรณ์: GeometricField**

คลาส `GeometricField` สุดท้ายเพิ่มการจัดการขอบเขตและการติดตามเชิงเวลา:

```cpp
template<class Type, template<class> class PatchField, class GeoMesh>
class GeometricField : public DimensionedField<Type, GeoMesh> {
    DimensionedField<Type, GeoMesh> internalField_;    // ค่าที่จุดศูนย์ถ่วงเซลล์
    FieldField<PatchField, Type> boundaryField_;       // เงื่อนไขขอบเขต
    label timeIndex_;                                  // การติดตามเวลา

public:
    // การเข้าถึงฟิลด์ขอบเขต
    const Boundary& boundaryField() const { return boundaryField_; }
    Boundary& boundaryField() { return boundaryField_; }

    // การเข้าถึงฟิลด์ภายใน
    const Internal& internalField() const { return internalField_; }
    Internal& internalField() { return internalField_; }

    // การดำเนินการเชิงเวลา
    void oldTime();
    void writeOldTime() const;
};
```

---

### **2.3 นามแฝงชนิด: "ชื่อที่ใช้งานง่าย"**

OpenFOAM ให้ชุดนามแฝงชนิดที่หลากหลายซึ่งทำให้การประกาศฟิลด์เป็นไปอย่างเป็นธรรมชาติและมีความหมายทางกายภาพ:

```cpp
// Finite Volume Fields - จุดศูนย์ถ่วงเซลล์
typedef GeometricField<scalar, fvPatchField, volMesh> volScalarField;
typedef GeometricField<vector, fvPatchField, volMesh> volVectorField;
typedef GeometricField<tensor, fvPatchField, volMesh> volTensorField;
typedef GeometricField<symmTensor, fvPatchField, volMesh> volSymmTensorField;
typedef GeometricField<sphericalTensor, fvPatchField, volMesh> volSphericalTensorField;

// Surface Fields - จุดศูนย์ถ่วงหน้า
typedef GeometricField<scalar, fvsPatchField, surfaceMesh> surfaceScalarField;
typedef GeometricField<vector, fvsPatchField, surfaceMesh> surfaceVectorField;

// Point Fields - จุดศูนย์ถ่วงจุด
typedef GeometricField<scalar, pointPatchField, pointMesh> pointScalarField;
typedef GeometricField<vector, pointPatchField, pointMesh> pointVectorField;

// Internal Fields - สำหรับการดำเนินการทางคณิตศาสตร์
typedef DimensionedField<scalar, volMesh> volScalarField::Internal;
typedef DimensionedField<vector, volMesh> volVectorField::Internal;
```

---

## 3. Internal Mechanics: Memory Layout and Data Structures

### **3.1 Core Data Members: The "Field Anatomy"**

คลาส `GeometricField` แสดงถึงแนวทางที่ซับซ้อนของ OpenFOAM ในการจัดการข้อมูลฟิลด์การคำนวณผ่านลำดับชั้นการสืบทอดที่ออกแบบมาอย่างพิถีพิถัน

ในแกนกลางของคลาสเทมเพลตนี้ทำหน้าที่เป็นรากฐานสำหรับการแสดงถึงปริมาณทางกายภาพทั่วทั้งโดเมนการคำนวณ:

- **ฟิลด์สเกลาร์**: ความดัน อุณหภูมิ
- **ฟิลด์เวกเตอร์**: ความเร็ว
- **ฟิลด์เทนเซอร์**: ความเค้นและความเครียด

```cpp
template<class Type, template<class> class PatchField, class GeoMesh>
class GeometricField {
private:
    // Time management for temporal schemes
    mutable label timeIndex_;                    // Current time index for time dependency tracking
    mutable GeometricField* field0Ptr_;          // Pointer to field at previous time step (n-1)
    mutable GeometricField* fieldPrevIterPtr_;   // Pointer to field from previous iteration (n)

    // Boundary condition management
    Boundary boundaryField_;                     // GeometricBoundaryField containing all patch conditions

    // Inherited from DimensionedField<Type, GeoMesh>:
    // const Mesh& mesh_                         // Reference to the underlying computational mesh
    // dimensionSet dimensions_                  // Physical dimensions (e.g., [M^1 L^-1 T^-2] for pressure)
    // Field<Type> data_                         // Actual data storage for internal field values
};
```

**ความสามารถในการจัดการเวลา**:
- `timeIndex_` รับประกันการติดตามการก้าวหน้าของเวลาที่เหมาะสม
- `field0Ptr_` และ `fieldPrevIterPtr_` อำนวยความสะดวกในรูปแบบการประมาณค่าเวลาที่แม่นยำระดับที่สอง
- รองรับรูปแบบ: **backward differencing**, **Crank-Nicolson** และรูปแบบเชิงเวลาอื่น ๆ

---

### **3.2 Memory Layout Visualization**

[Diagram: โครงสร้างหน่วยความจำแบบลำดับชั้นของ GeometricField]

การจัดระเบียบหน่วยความจำของ `GeometricField` ทำตามโครงสร้างลำดับชั้นที่แยกการจัดเก็บฟิลด์ภายในจากการจัดการเงื่อนไขขอบเขต:

```
GeometricField<scalar, fvPatchField, volMesh> (volScalarField representation)
├── DimensionedField<scalar, volMesh> (base class)
│   ├── Field<scalar> data_ = [p₁, p₂, ..., pₙ]  (n = total cells)
│   │   ├── p₁ = pressure at cell center 1
│   │   ├── p₂ = pressure at cell center 2
│   │   └── pₙ = pressure at cell center n
│   ├── dimensionSet dims_ = [1 -2 -2 0 0 0 0] (pressure: M L^-1 T^-2)
│   └── const volMesh& mesh_ (reference to finite volume mesh)
└── GeometricBoundaryField (boundary condition management)
    ├── fvPatchField<scalar>[0] (patch 0: inlet)
    │   ├── Reference to fvPatch (geometric information)
    │   ├── Reference to internalField (coupling to interior)
    │   └── Field<scalar> (values at boundary faces)
    ├── fvPatchField<scalar>[1] (patch 1: outlet)
    ├── fvPatchField<scalar>[2] (patch 2: walls)
    └── ... (n patches total)
```

**การตีความทางกายภาพ**:
พิจารณาฟิลด์อุณหภูมิ $T(\mathbf{x}, t)$ ที่ถูกแบ่งส่วนบนตาข่ายการคำนวณ:

- `Field<scalar>` เก็บค่าศูนย์กลางเซลล์: $[T_1, T_2, ..., T_N]$ โดยที่แต่ละ $T_i$ แทนอุณหภูมิเฉลี่ยในเซลล์ $i$
- `boundaryField_` รักษาค่าอุณหภูมิที่หน้าขอบเขต: $T_{\text{boundary}}^{(j)}$ สำหรับแต่ละชิ้นส่วนขอบเขต $j$
- `dimensions_` บังคับให้มีความสอดคล้องของมิติ: $[T] = \Theta$ (หน่วยอุณหภูมิ)

**ประสิทธิภาพการดำเนินการ**:
โครงสร้างนี้ทำให้สามารถดำเนินการแบบเวกเตอร์ได้อย่างมีประสิทธิภาพในขณะที่รักษาการแยกอย่างชัดเจนระหว่างการคำนวณโดเมนจำนวนมากและการรักษาเงื่อนไขขอบเขตเฉพาะทาง

---

### **3.3 Boundary Field Organization**

[Diagram: สถาปัตยกรรม GeometricBoundaryField และความสัมพันธ์กับ PatchField]

สถาปัตยกรรมเงื่อนไขขอบเขตแสดงให้เห็นถึงแนวทางที่ยืดหยุ่นและขยายได้ของ OpenFOAM ในการจัดการข้อจำกัดทางกายภาพที่หลากหลาย

```cpp
class GeometricBoundaryField {
    PtrList<PatchField<Type>> patches_;  // Dynamic array of boundary patch fields

    // Each fvPatchField<Type> instance contains:
    // - Reference to fvPatch (geometric boundary information)
    // - Reference to internalField (for coupled boundary conditions)
    // - Field<Type> (actual boundary face values)
    // - Virtual methods for boundary condition evaluation
};
```

**หลักการออกแบบสำคัญ**:
- **Patch-specific but type-consistent**: แต่ละชิ้นส่วนขอบเขตสามารถมีเงื่อนไขทางกายภาพที่แตกต่างกันได้
- ชิ้นส่วนขอบเขตทั้งหมดภายในฟิลด์ยังคง 유型เทมเพลตเดียวกัน
- **Runtime Polymorphism**: ความปลอดภัยของประเภทในเวลาคอมไพล์ พร้อมการเลือกพฤติกรรมในเวลาทำงาน

#### **ประเภทของเงื่อนไขขอบเขต**

| ประเภท | OpenFOAM | สมการ | ตัวอย่างการใช้งาน |
|--------|----------|---------|------------------|
| **Dirichlet** | `fixedValue` | $$\phi\|_{\partial\Omega} = \phi_0(\mathbf{x}, t)$$ | อุณหภูมิคงที่: $T = 300\text{ K}$ ที่ผนัง<br>ความเร็วคงที่: $\mathbf{u} = \mathbf{u}_0$ ที่ทางเข้า |
| **Neumann** | `fixedGradient` | $$\frac{\partial \phi}{\partial n}\bigg\|_{\partial\Omega} = q_0(\mathbf{x}, t)$$ | Heat flux: $-k \nabla T \cdot \mathbf{n} = q''$ ที่ผนัง<br>Stress-free: $\boldsymbol{\tau} \cdot \mathbf{n} = \mathbf{0}$ ที่ทางออก |
| **Coupled** | `processor`, `cyclic` | การสื่อสารระหว่างโดเมน | `processor`: ขอบเขตการแบ่งโดเมนสำหรับ MPI<br>`cyclic`: ขอบเขตเป็นระยะ<br>`wallFunction`: การรักษาความปั่นป่วนใกล้ผนัง |

**ประสิทธิภาพหน่วยความจำ**:
- การนำไปใช้ `PtrList` เก็บเฉพาะการอ้างอิงถึงออบเจกต์ฟิลด์ขอบเขต
- หลีกเลี่ยงการทำซ้ำข้อมูลที่ไม่จำเป็น
- เมื่อเงื่อนไขขอบเขตถูกอัปเดต การอ้างอิงฟิลด์ภายในยังคงไม่เปลี่ยนแปลง
- ทำให้สามารถแก้ปัญหาอัลกอริทึมการวนซ้ำได้อย่างมีประสิทธิภาพ

---

## 4. กลไก: ตรรกะฟังก์ชันการทำงานและปฏิสัมพันธ์กับ Mesh

### **4.1 การสร้างฟิลด์: "ใบประกาศแรกเกิด"**

ในสถาปัตยกรรมของ OpenFOAM การสร้าง computational field เป็นกระบวนการที่ถูกออกแบบมาอย่างระมัดระวัง ซึ่งกำหนดเอกลักษณ์ คุณสมบัติทางกายภาพ และความสัมพันธ์กับ computational mesh ของฟิลด์นั้นๆ

**Constructor ของ `volScalarField`** ทำหน้าที่เป็น "ใบประกาศแรกเกิด" ของฟิลด์ โดยเข้ารหัสข้อมูลสำคัญที่ควบคุมพฤติกรรมของฟิลด์ตลอดการจำลอง

```cpp
volScalarField p
(
    IOobject
    (
        "p",                    // ชื่อฟิลด์
        runTime.timeName(),     // ไดเรกทอรีเวลา
        mesh,                   // การอ้างอิง fvMesh
        IOobject::MUST_READ,    // อ่านจากดิสก์
        IOobject::AUTO_WRITE    // เขียนโดยอัตโนมัติ
    ),
    mesh,                       // Mesh สำหรับกำหนดขนาด
    dimensionedScalar("p", dimPressure, 101325)  // ค่าเริ่มต้น + หน่วย
);
```

[Diagram: โครงสร้างการสร้างฟิลด์ใน OpenFOAM แสดง IOobject, Mesh และค่าเริ่มต้น]

กระบวนการสร้างนี้เป็นไปตามโปรโตคอลหลายขั้นตอนอย่างเคร่งครัด:

#### **ขั้นที่ 1: การสร้าง IOobject**
กำหนดเอกลักษณ์ถาวรและกลยุทธ์การจัดการข้อมูลของฟิลด์

- **`IOobject`** ทำหน้าที่เป็นอินเทอร์เฟซระหว่างฟิลด์และระบบไฟล์
- **`IOobject::MUST_READ`** บังคับให้ฟิลด์อ่านจากดิสก์ระหว่างการสร้าง (โดยทั่วไปจากไฟล์ `0/p`)
- **`IOobject::AUTO_WRITE`** ทำให้มั่นใจได้ว่าจะมีการส่งออกโดยอัตโนมัติในแต่ละ time step

#### **ขั้นที่ 2: การกำหนดขนาดของ Mesh**
กำหนดมิติเชิงพื้นที่ของฟิลด์ผ่านการดำเนินการ `volMesh(mesh).size()`

- นับจำนวน computational cells ใน mesh
- สร้างความสัมพันธ์หนึ่งต่อหนึ่งระหว่างค่าฟิลด์และเซลล์ของ mesh
- แน่ใจว่าแต่ละจุดศูนย์ถ่วงของเซลล์จะมีค่าฟิลด์ที่เกี่ยวข้อง

#### **ขั้นที่ 3: การตรวจสอบมิติ**
บังคับใช้ความสม่ำเสมอทางกายภาพผ่านระบบ dimensional analysis ของ OpenFOAM

- **`dimPressure`** (มิติ: $M L^{-1} T^{-2}$) ทำให้มั่นใจได้ว่าการดำเนินการทั้งหมดจะรักษาความสม่ำเสมอของมิติ
- ป้องกันการคำนวณที่ไม่มีความหมายทางกายภาพในช่วย compile time

#### **ขั้นที่ 4: การตั้งค่าเขตแดน**
อ่านและประมวลผลข้อมูลจำเพาะของเขตแดนจาก field dictionary

- การแยกวิเคราะห์ประเภทของเขตแดน (fixedValue, zeroGradient, เป็นต้น)
- ค่าที่เกี่ยวข้อง
- Interpolation schemes
- สร้างการกำหนดค่าฟิลด์ที่สมบูรณ์ที่จำเป็นสำหรับการจำลอง

---

### **4.2 การ Overload Operator: "ไวยากรณ์คณิตศาสตร์"**

Field operators ของ OpenFOAM ใช้ไวยากรณ์คณิตศาสตร์ที่ซับซ้อน ซึ่งช่วยให้สามารถคำนวณได้ตรงตามสัญชาตญาณและปลอดภัยต่อมิติ

[Diagram: แผนภาพการทำงานของ operator overloading ใน OpenFOAM]

#### **OpenFOAM Code Implementation**
```cpp
// Dimensional-safe operations
volScalarField p = rho*R*T;               // p = ρRT (ideal gas law)
volVectorField gradP = fvc::grad(p);      // ∇p (pressure gradient)
volScalarField divU = fvc::div(U);        // ∇·U (velocity divergence)

// Compile-time dimensional checking
dimensionSet dims = p.dimensions() * U.dimensions();  // [p·U] = ML⁻¹T⁻² · LT⁻¹ = ML⁻²T⁻³
```

ระบบ operator overloading บังคับใช้ฟิสิกส์อย่างเคร่งครัดผ่านการตรวจสอบความสอดคล้องของมิติ:

#### **การดำเนินการเชิงบวก** ($+$, $-$)
- ต้องการมิติที่เหมือนกันระหว่าง operands
- นิพจน์เช่น `p + T` ล้มเหลวในช่วย compile time
- ความดัน ($M L^{-1} T^{-2}$) และอุณหภูมิ ($Θ$) มีมิติที่ไม่เข้ากัน
- ป้องกันการดำเนินการที่ไม่มีความหมายทางกายภาพ

#### **การดำเนินการเชิงคูณ** ($\times$, $\div$)
- ผสมและทำให้มิติง่ายขึ้นโดยอัตโนมัติตามกฎฟิสิกส์
- ตัวอย่าง: `U * t` (ความเร็ว × เวลา) ผลิตการกระจัดโดยธรรมชาติด้วยมิติของความยาว ($L$)

#### **Differential Operators**
ใช้การแปลงมิติเฉพาะที่สะท้อนคำจำกัดความทางคณิตศาสตร์:

| Operator | สัญลักษณ์ | การเปลี่ยนแปลงมิติ | คำอธิบาย |
|----------|------------|-------------------|------------|
| Gradient | $\nabla$ | เพิ่ม $L^{-1}$ | อนุพันธ์เชิงพื้นที่ |
| Divergence | $\nabla \cdot$ | เพิ่ม $L^{-1}$ | การไหลออก |
| Laplacian | $\nabla^2$ | เพิ่ม $L^{-2}$ | อนุพันธ์อันดับสอง |

ระบบความปลอดภัยของมิตินี้ขยายไปถึงนิพจน์ที่ซับซ้อนเช่น $\nabla \cdot (\rho \mathbf{U})$ ซึ่งระบบจะตรวจสอบโดยอัตโนมัติว่า mass flux divergence รักษามิติที่ถูกต้องของ mass rate per unit volume ($M L^{-3} T^{-1}$)

---

### **4.3 ปฏิสัมพันธ์กับ Mesh: "บริบทเชิงพื้นที่"**

ความสัมพันธ์ระหว่างฟิลด์และ mesh ใน OpenFOAM เป็นตัวอย่างของการออกแบบเชิงวัตถุที่มีประสิทธิภาพ

[Diagram: แผนภาพแสดงความสัมพันธ์ระหว่าง Field และ Mesh ใน OpenFOAM]

#### **OpenFOAM Code Implementation**
```cpp
// Field knows its mesh through GeoMesh template
const fvMesh& mesh = p.mesh();  // Access underlying mesh

// Mesh-aware operations
const vectorField& cellCenters = mesh.C();  // Cell center coordinates
const scalarField& cellVolumes = mesh.V();  // Cell volumes

// Field interpolation uses mesh geometry
surfaceScalarField phi = linearInterpolate(U) & mesh.Sf();  // Flux
```

#### **สถาปัตยกรรม Reference-Based Design**
`GeometricField` objects เก็บการอ้างอิงไปยัง mesh ของตนมากกว่าเป็นเจ้าของโดยตรง

**ประโยชน์ของ Reference-Based Design:**

| คุณสมบัติ | คำอธิบาย | ประโยชน์ |
|------------|------------|------------|
| **ประสิทธิภาพหน่วยควาจำ** | ฟิลด์หลายฟิลด์อ้างอิง mesh เดียวกันได้ | ลดการใช้หน่วยความจำอย่างมีนัยสำคัญ |
| **การรับประกันการซิงโครไนซ์** | ฟิลด์อ้างอิง mesh มากกว่าการคัดลอก | การปรับเปลี่ยน mesh สะท้อนโดยอัตโนมัติ |
| **ความเข้ากันได้แบบขนาน** | ข้อมูลฟิลด์ตาม mesh partitioning โดยธรรมชาติ | รองรับ domain decomposition ราบรื่น |

#### **การดำเนินการเชิงพื้นที่ที่ซับซ้อน**
ความตระหนักเกี่ยวกับ mesh ช่วยให้การดำเนินการเชิงพื้นที่ที่ซับซ้อนซึ่งใช้ประโยชน์จากข้อมูลทางเรขาคณิต:

- **การคำนวณ Flux**: `phi = linearInterpolate(U) & mesh.Sf()`
  - คำนวณ face fluxes โดยการ interpolation ค่าความเร็วจากจุดศูนย์ถ่วงของเซลล์ไปยังจุดศูนย์ถ่วงของหน้า
  - Dot product กับเวกเตอร์ปกติของพื้นผิวหน้า $\mathbf{S_f}$

- **การคำนวณ Gradient**:
  - อนุพันธ์เชิงพื้นที่ใช้ mesh connectivity
  - สร้าง finite-volume approximations โดยยึดตามค่าของเซลล์ใกล้เคียงและเรขาคณิตของหน้า

- **การดำเนินการ Integration**:
  - Volume integrals ใช้ `mesh.V()`
  - ถ่วงน้ำหนักค่าฟิลด์ด้วยปริมาตรเซลล์สำหรับการ integration เชิงพื้นที่ที่แม่นยำ

---

### **4.4 การจัดการเวลา: "ความทรงจำเชิงเวลา"**

OpenFOAM ใช้ระบบการจัดการเวลาที่ซับซ้อน ซึ่งช่วยให้ temporal discretization ที่แม่นยำในขณะเดียวกันรักษาประสิทธิภาพการคำนวณ

[Diagram: แผนภาพการจัดการเวลาใน OpenFOAM แสดงระดับเวลาต่างๆ]

#### **OpenFOAM Code Implementation**
```cpp
void GeometricField::storeOldTime() {
    if (!field0Ptr_) {
        field0Ptr_ = new GeometricField(*this);  // Copy current field
    }
}

scalarField ddt = (p - p.oldTime())/runTime.deltaT();  // ∂p/∂t ≈ Δp/Δt
```

#### **สถาปัตยกรรมการจัดการเวลา**
สนับสนุนหลาย temporal discretization schemes ผ่านระบบจัดเก็บแบบลำดับชั้น:

**กลยุทธ์การจัดสรรแบบล่าช้า**:
- วิธี `storeOldTime()` ใช้การจัดการหน่วยความจำที่มีประสิทธิภาพ
- จัดสรรพื้นที่จัดเก็บสำหรับระดับเวลาก่อนหน้าเฉพาะเมื่อต้องการ
- ป้องกันการใช้หน่วยความจำโดยไม่จำเป็นในการจำลองสภาวะคงที่

#### **Temporal Schemes และการจัดเก็บ**

| Scheme | ระดับเวลาที่ต้องการ | การจัดเก็บ | สมการ |
|--------|---------------------|-------------|----------|
| **Euler implicit** | 1 ระดับ ($p^{n}$) | `field0Ptr_` | $p^{n+1} = p^n + \Delta t \cdot f(p^{n+1})$ |
| **Backward differentiation** | 2 ระดับ ($p^{n}$, $p^{n-1}$) | `oldTime()` ซ้อนกัน | - |
| **Crank-Nicolson** | 2 ระดับ | การถ่วงน้ำหนัก | $p^{n+\frac{1}{2}} = \frac{1}{2}(p^n + p^{n+1})$ |

#### **การคำนวณอนุพันธ์เชิงเวลา**
ตามการประมาณค่า finite-difference มาตรฐาน:
$$\frac{\partial p}{\partial t} \approx \frac{p^{n+1} - p^n}{\Delta t}$$

ระบบนี้ช่วยให้ OpenFOAM สามารถสลับระหว่าง temporal schemes ที่แตกต่างกันได้อย่างราบรื่นโดยไม่ต้องแก้ไขโค้ด เนื่องจากระบบการจัดการฟิลด์จะจัดหาข้อมูลประวัติศาสตร์ที่จำเป็นโดยอัตโนมัติตาม discretization method ที่เลือก

---

## 5. "เหตุผล": รูปแบบการออกแบบและการตัดสินใจทางสถาปัตยกรรม

### 5.1 Template Metaprogramming: ฟิสิกส์ระดับคอมไพล์

**การใช้ Template Metaprogramming** อย่างกว้างขวางของ OpenFOAM เป็นหนึ่งในการตัดสินใจทางสถาปัตยกรรมที่ซับซ้อนที่สุดใน codebase

**หลักการพื้นฐาน**:
- คอมไพเลอร์สามารถ deduce ประเภทและเพิ่มประสิทธิภาพโดยยึดตามคุณสมบัติทางคณิตศาสตร์
- การดำเนินการทางคณิตศาสตร์รักษาความสอดคล้องด้านมิติโดยอัตโนมัติในระดับคอมไพล์
- ไม่ต้องพึ่งพาการตรวจสอบระยะเวลาทำงาน

[Diagram: Template Metaprogramming Flow - แสดงการ compile-time type deduction และ optimization]

#### การ Implement Inner Product Operator

```cpp
template<class Type1, class Type2>
typename innerProduct<Type1, Type2>::type
operator&(const GeometricField<Type1, PatchField, GeoMesh>& f1,
          const GeometricField<Type2, PatchField, GeoMesh>& f2);
```

คลาส trait `innerProduct` กำหนดประเภทผลลัพธ์ตามประเภทอินพุต:

| อินพุตประเภทที่ 1 | อินพุตประเภทที่ 2 | ประเภทผลลัพธ์ | การดำเนินการ |
|-------------------|-------------------|----------------|------------------|
| `vector` | `vector` | `scalar` | Dot product |
| `vector` | `tensor` | `vector` | Tensor-vector multiplication |
| `tensor` | `tensor` | `tensor` | Tensor-tensor multiplication |

#### ประโยชน์ของ Template Metaprogramming

**✅ ความปลอดภัยของประเภท**:
- การดำเนินการที่ไม่มีความหมายทางฟิสิกส์จะเป็น **compiler error** แทน bug ในระยะเวลาทำงาน
- ตัวอย่าง: `scalar & scalar` compile ไม่ผ่านเพราะไม่ได้กำหนด `innerProduct<scalar, scalar>::type`

**⚡ ประสิทธิภาพ**:
- คอมไพเลอร์สร้าง code ที่เพิ่มประสิทธิภาพสำหรับแต่ละชุดประเภทเฉพาะ
- กำจัด overhead ของการตรวจสอบประเภทในระยะเวลาทำงาน
- Template instantiation ในระดับคอมไพล์สร้าง machine code ที่มีประสิทธิภาพสูง

**🎯 ความสามารถในการแสดงออก**:
- Code อ่านง่ายเป็นนิพจน์ทางคณิตศาสตร์โดยยังคงการตรวจสอบประเภทอย่างเข้มงวด
- ผู้ใช้เขียน `U & U` สำหรับพลังงานจลน์หรือ `tau & gradU` สำหรับงานความเครียดโดยไม่ต้องกังวลเกี่ยวกับการแปลงประเภท

#### พีชคณิต Field ที่ซับซ้อน

```cpp
template<class Type>
class GeometricField {
    template<class Type2>
    tmp<GeometricField<typename product<Type, Type2>::type, PatchField, GeoMesh>>
    operator*(const GeometricField<Type2, PatchField, GeoMesh>&) const;
};
```

Trait `product` ช่วยให้มั่นใจว่า:
- การคูณความเร็ว field (vector) กับความหนาแน่น field (scalar)
- สร้างโมเมนตัมฟลักซ์ field (vector) พร้อมกับหน่วยมิติที่ถูกต้องโดยอัตโนมัติ

---

### 5.2 Policy-Based Design: ความยืดหยุ่นของ Boundary Condition

**การออกแบบแบบ Policy-Based** ของ OpenFOAM เป็นการประยุกต์ใช้พารามิเตอร์ template อย่างชาญฉลาดเพื่อให้ได้ความยืดหยุ่นในระยะเวลาทำงานโดยไม่เสียสละการเพิ่มประสิทธิภาพในระดับคอมไพล์

[Diagram: Policy-Based Design Architecture - แสดง GeometricField กับ PatchField policies ต่างๆ]

#### โครงสร้าง Policy Template

```cpp
template<template<class> class PatchField, class GeoMesh>
class GeometricField {
    // Core field operations independent of boundary treatment
    // Boundary behavior delegated to PatchField<Type> policy
};
```

สถาปัตยกรรมนี้ช่วยให้การ implement `GeometricField` เดียวกันทำงานได้อย่างราบรื่นในแบบจำลองที่แตกต่างกัน:

| ประเภท Field | Template Parameters | การใช้งาน |
|--------------|-------------------|-------------|
| Finite Volume | `GeometricField<Type, fvPatchField, volMesh>` | Standard FV discretization |
| Finite Element | `GeometricField<Type, femPatchField, femMesh>` | Finite element formulations |
| Finite Area | `GeometricField<Type, faPatchField, faMesh>` | Surface-based simulations |
| Point-Based | `GeometricField<Type, pointPatchField, pointMesh>` | Mesh-less particle methods |

#### การ Implement Policy Class

```cpp
template<class Type>
class fvPatchField : public Field<Type> {
    const fvPatch& patch_;           // Geometric boundary information
    const DimensionedField<Type, volMesh>& internalField_;  // Connection to interior

    // Policy-specific boundary evaluation
    virtual void evaluate(const Pstream::commsTypes) = 0;
};
```

**ประเภท Boundary Condition เฉพาะ**:

```cpp
template<class Type>
class fixedValueFvPatchField : public fvPatchField<Type> {
    virtual void evaluate(const Pstream::commsTypes) {
        // Set boundary values to fixed prescribed values
        this->operator==(this->refValue());
    }
};

template<class Type>
class zeroGradientFvPatchField : public fvPatchField<Type> {
    virtual void evaluate(const Pstream::commsTypes) {
        // Copy interior gradient to boundary (zero gradient condition)
        this->operator==(this->internalField().boundaryField()[this->patchIndex()].patchNeighbourField());
    }
};
```

#### ความสามารถในการขยายตัว

ผู้ใช้สามารถสร้างประเภท boundary condition แบบกำหนดเองโดยไม่ต้องแก้ไข core field algebra:

```cpp
template<class Type>
class customBoundaryFvPatchField : public fvPatchField<Type> {
    // Custom boundary evaluation logic
    virtual void evaluate(const Pstream::commsTypes) {
        // User-defined boundary behavior
        this->operator==(customEvaluationFunction(this->internalField()));
    }
};
```

**ประโยชน์ของ Policy-Based Design**:
- **ความยืดหยุ่น**: รองรับไลบรารี boundary conditions ที่กว้างขวาง
- **ส่วนติดต่อที่เป็นเนื้อเดียวกัน**: ตัวดำเนินการทางคณิตศาสตร์เดียวกันทำงานเหมือนกันไม่ว่าการ implement boundary condition เฉพาะจะเป็นอย่างไร
- **การพัฒนาอิสระ**: สามารถพัฒนา boundary conditions ใหม่โดยไม่กระทบต่อ core field operations

---

### 5.3 RAII (Resource Acquisition Is Initialization)

**กลยุทธ์การจัดการหน่วยความจำ** ของ OpenFOAM พึ่งพาหลักการ RAII อย่างมากเพื่อให้มั่นใจถึงความปลอดภัยของ exception และป้องกันการรั่วไหลของทรัพยากรในการจำลอง CFD ที่ซับซ้อน

[Diagram: RAII Memory Management - แสดง autoPtr และ tmp วงจรชีวิต]

#### คลาส `autoPtr`: การเป็นเจ้าของแบบเอกสิทธิ์

```cpp
template<class T>
class autoPtr {
private:
    T* ptr_;  // Raw pointer to managed object

public:
    // Constructor takes ownership
    explicit autoPtr(T* p = nullptr) : ptr_(p) {}

    // Destructor automatically deletes managed object
    ~autoPtr() { delete ptr_; }

    // Move transfer (no copy - exclusive ownership)
    autoPtr(autoPtr&& ap) noexcept : ptr_(ap.ptr_) { ap.ptr_ = nullptr; }

    // Access operators
    T& operator*() const { return *ptr_; }
    T* operator->() const { return ptr_; }
    T* get() const { return ptr_; }

    // Release ownership
    T* release() { T* tmp = ptr_; ptr_ = nullptr; return tmp; }
};
```

**การใช้งานใน Solver Algorithm**:

```cpp
// Create temporary field with automatic cleanup
autoPtr<volScalarField> pField
(
    new volScalarField
    (
        IOobject("p", runTime.timeName(), mesh, IOobject::NO_READ),
        mesh,
        dimensionedScalar("p", dimPressure, 0.0)
    )
);

// Field automatically destroyed when pField goes out of scope
// No need for manual delete, even if exceptions occur
```

#### คลาส `tmp`: Reference Counting สำหรับ Temporary Fields

```cpp
template<class T>
class tmp {
private:
    mutable T* ptr_;
    mutable bool refCount_;

public:
    // Constructor from raw pointer (takes ownership)
    tmp(T* p, bool transfer = true) : ptr_(p), refCount_(!transfer) {}

    // Constructor from object (creates reference)
    tmp(T& t) : ptr_(&t), refCount_(true) {}

    // Copy constructor increments reference count
    tmp(const tmp<T>& t) : ptr_(t.ptr_), refCount_(true) {
        if (t.refCount_) t.refCount_ = false;
    }

    // Destructor manages cleanup based on reference count
    ~tmp() {
        if (ptr_ && !refCount_) delete ptr_;
    }

    // Automatic conversion to underlying type
    operator T&() const { return *ptr_; }
    T& operator()() const { return *ptr_; }
};
```

**การดำเนินการพีชคณิต Field อย่างมีประสิทธิภาพ**:

```cpp
// tmp enables efficient temporary field chaining
tmp<volScalarField> magU = mag(U);                    // Creates temporary
tmp<volScalarField> magU2 = sqr(magU);               // Reuses temporary without copy
tmp<volVectorField> gradP = fvc::grad(p);            // Automatic cleanup

// Field operations return tmp objects for efficiency
tmp<volScalarField> divPhi = fvc::div(phi);          // Temporary divergence field
tmp<volVectorField> U2 = U + U;                      // Temporary sum field
```

#### RAII สำหรับ File I/O

รูปแบบ RAII ขยายไปถึงไฟล์ I/O ผ่านคลาสฐาน `regIOobject`:

```cpp
class regIOobject : public IOobject {
    virtual bool write() const = 0;          // Pure virtual write operation
    virtual bool read() = 0;                 // Pure virtual read operation

    // Automatic file handle management
    // Files opened in constructor, closed in destructor
};
```

#### ประโยชน์ของ RAII แบบครอบคลุม

**✅ Exception Safe**: ทรัพยากรถูกทำความสะอาดอย่างถูกต้องเมื่อเกิด exception
**✅ Memory Leak Free**: การเก็บขยะอัตโนมัติป้องกันการรั่วไหลของหน่วยความจำ
**✅ Performance Optimized**: Reference counting ลดการคัดลอกที่ไม่จำเป็น
**✅ Maintainable**: Semantics ของความเป็นเจ้าของที่ชัดเจนลดความซับซ้อนในการ debug

---

### 5.4 Type Erasure ผ่าน Typedefs

**OpenFOAM ใช้ Type Erasure** เชิงกลยุทธ์ผ่านลำดับชั้น typedef ที่ออกแบบอย่างระมัดระวังซึ่งซ่อนความซับซ้อนของ template โดยยังคงความปลอดภัยของประเภทและประสิทธิภาพ

[Diagram: Type Erasure Hierarchy - แสดงการซ่อนความซับซ้อน template ผ่าน typedefs]

#### โครงสร้าง Typedef พื้นฐาน

```cpp
// Core field typedefs hiding template complexity
typedef GeometricField<scalar, fvPatchField, volMesh> volScalarField;
typedef GeometricField<vector, fvPatchField, volMesh> volVectorField;
typedef GeometricField<tensor, fvPatchField, volMesh> volTensorField;
typedef GeometricField<symmTensor, fvPatchField, volMesh> volSymmTensorField;

// Surface field equivalents
typedef GeometricField<scalar, fvsPatchField, surfaceMesh> surfaceScalarField;
typedef GeometricField<vector, fvsPatchField, surfaceMesh> surfaceVectorField;

// Point mesh fields
typedef GeometricField<scalar, pointPatchField, pointMesh> pointScalarField;
```

#### การใช้งานที่เข้าใจง่าย

```cpp
// User code reads naturally without template syntax
volScalarField p    // Pressure field
(
    IOobject("p", runTime.timeName(), mesh, IOobject::MUST_READ),
    mesh
);

volVectorField U    // Velocity field
(
    IOobject("U", runTime.timeName(), mesh, IOobject::MUST_READ),
    mesh
);

volScalarField T    // Temperature field
(
    IOobject("T", runTime.timeName(), mesh, IOobject::MUST_READ),
    mesh
);

// Mathematical expressions maintain natural syntax
volScalarField magU = mag(U);                    // Velocity magnitude
volScalarField ke = 0.5 * magU * magU;           // Kinetic energy
tmp<volVectorField> gradT = fvc::grad(T);       // Temperature gradient
```

#### การวิเคราะห์มิติผ่าน Specialized Typedefs

```cpp
// Dimensioned scalar fields with embedded unit information
typedef DimensionedField<scalar, volMesh> volScalarField::Internal;
typedef DimensionedField<vector, volMesh> volVectorField::Internal;

// User can create fields with physical dimensions
dimensionedScalar rho
(
    "rho",
    dimensionSet(1, -3, 0, 0, 0, 0, 0),  // [kg/m³]
    1.2                                  // Initial value
);

volScalarField rhoField
(
    IOobject("rho", runTime.timeName(), mesh, IOobject::NO_READ),
    mesh,
    rho                                  // Inherits dimensional information
);
```

#### ประโยชน์ของ Type Erasure Strategy

**✅ ความเข้าถึงได้**: วิศวกรสามารถมุ่งเน้นที่ฟิสิกส์และเชิงตัวเลขแทนที่จะเป็นไวยากรณ์ template
**✅ ความสอดคล้อง**: ประเภท field ทั้งหมดทำตามรูปแบบส่วนติดต่อเดียวกัน
**✅ การบำรุงรักษา**: การเปลี่ยนแปลงการ implement template พื้นฐานไม่กระทบต่อ code ของผู้ใช้
**✅ ความสามารถในการขยายตัว**: ประเภท field ใหม่สามารถเพิ่มผ่านการประกาศ typedef
**✅ ประสิทธิภาพ**: ไม่มี overhead ในระยะเวลาทำงาน - typedefs เป็นโครงสร้างในระดับคอมไพล์เท่านั้น

ลำดับชั้น typedef เป็นการสมดุลระหว่าง template metaprogramming ที่ซับซ้อนกับการใช้งานจริงอย่างชาญฉลาด

---

## 6. การควบคุมลูปเวลา (Time Loop)

```mermaid
flowchart TD
    Start([Start Simulation]) --> Loop{runTime.loop?}
    Loop -- Yes --> Increment[runTime++]
    Increment --> Physics[Solve Physics Equations]
    Physics --> Write{Time to write?}
    Write -- Yes --> Disk[Write to Folder /timeName/]
    Write -- No --> Loop
    Disk --> Loop
    Loop -- No --> End([End Simulation])
```
> **Figure 1:** ลำดับขั้นตอนการทำงานของลูปเวลา (Time Loop) ในตัวแก้ปัญหา ซึ่งครอบคลุมการก้าวเวลา การคำนวณฟิสิกส์ และการตรวจสอบเงื่อนไขการบันทึกข้อมูลลงดิสก์ความปลอดภัยทางฟิสิกส์ไม่ส่งผลกระทบต่อความเร็วในการจำลอง ผ่านการใช้พลังของ C++ Template Metaprogramming ในการตรวจสอบความสอดคล้องทางมิติทั้งหมดที่ขั้นตอนการคอมไพล์โปรแกรมเพียงครั้งเดียว

ในโค้ดของโซลเวอร์ เราจะเห็นรูปแบบการใช้งานมาตรฐานดังนี้:

```cpp
while (runTime.loop()) // วนลูปจนกว่าจะถึง endTime
{
    Info << "Time = " << runTime.timeName() << endl;

    runTime++; // ก้าวเข้าสู่เวลาถัดไป (t = t + deltaT)

    // ... ส่วนการคำนวณฟิสิกส์ ...

    runTime.write(); // ตรวจสอบเงื่อนไขและเขียนผลลัพธ์ลงดิสก์หากถึงเวลา
}
```

---

## ⚙️ เมธอดที่สำคัญ

| เมธอด | หน้าที่ |
| :--- | :--- |
| **`runTime.timeName()`** | ส่งคืนชื่อโฟลเดอร์เวลาปัจจุบันเป็น String (เช่น "0.5") |
| **`runTime.value()`** | ส่งคืนค่าเวลาปัจจุบันเป็นตัวเลข Scalar |
| **`runTime.deltaTValue()`** | ส่งคืนขนาดของก้าวเวลาปัจจุบัน |
| **`runTime.write()`** | สั่งให้บันทึกออบเจกต์ทั้งหมดที่จดทะเบียนไว้ใน Registry ลงดิสก์ |

**สรุป**: คลาส `Time` คือจุดเชื่อมต่อระหว่าง **"ตรรกะเชิงเวลา"** และ **"ระบบไฟล์"** ซึ่งทำให้การจัดการข้อมูล CFD ขนาดใหญ่มีความเป็นระเบียบและเป็นระบบ
