# พื้นฐาน Primitives: องค์ประกอบหลักของ OpenFOAM

## ภาพรวม

สถาปัตยกรรมของ OpenFOAM สร้างขึ้นบนพื้นฐานของคลาส primitive หลักที่ซับซ้อน ซึ่งเป็นองค์ประกอบพื้นฐานสำหรับการคำนวณ CFD ทั้งหมด พื้นฐาน primitives เหล่านี้ให้โครงสร้างข้อมูลและอัลกอริทึมพื้นฐานที่เปิดให้สามารถจำลองทางตัวเลขของพลศาสตร์ของไหลและปรากฏการณ์ทางกายภาพที่เกี่ยวข้องได้อย่างมีประสิทธิภาพ

```mermaid
graph TD
    Start((เริ่มต้น)) --> Basic[พื้นฐาน Primitives]
    Basic --> Types[ประเภทข้อมูลพื้นฐาน]
    Types --> Dimensions[มิติทางฟิสิกส์]
    Dimensions --> Memory[การจัดการหน่วยความจำ]
    Memory --> Containers[คอนเทนเนอร์]
    Containers --> Fields[คลาสฟิลด์]
    Fields --> Mesh[โครงสร้าง Mesh]
    Mesh --> Solvers[ระบบ Solver]

    style Start fill:#f9f,stroke:#333,stroke-width:2px
    style Solvers fill:#00ff00,stroke:#333,stroke-width:2px
    classDef step fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    class Basic,Types,Dimensions,Memory,Containers,Fields,Mesh step
```

> **Figure 1:** แผนผังลำดับชั้นขององค์ประกอบใน OpenFOAM ที่แสดงให้เห็นการสร้างระบบจากพื้นฐานขนาดเล็ก (Primitives) ไปสู่ระบบที่มีความซับซ้อนสูง (Solvers) โดยแต่ละระดับจะต่อยอดจากระดับก่อนหน้าเพื่อสร้างโครงสร้างที่สมบูรณ์สำหรับการคำนวณ CFD

## ทำไมต้อง Redefine ประเภทข้อมูลพื้นฐานของ C++?

OpenFOAM ไม่ได้ใช้ standard C++ types เช่น `int` และ `double` โดยตรง แต่จะ define primitives ของตัวเอง: `label`, `scalar` และอื่นๆ การเลือกแบบนี้มีจุดประสงค์สำคัญ 3 ประการ:

### 1. **Portability** (การพกพา)

การจำลอง CFD ทำงานได้บนอุปกรณ์ต่างๆ ตั้งแต่ laptop ไปจนถึง supercomputer ที่มีสถาปัตยกรรมแตกต่างกัน (32-bit vs 64-bit, single vs double precision)

> [!INFO] ความสำคัญของ Portable Types
> Primitives ของ OpenFOAM มี consistent behavior บนทุก platform:
> - เมื่อ compile OpenFOAM บนระบบต่างๆ underlying primitive types จะปรับเปลี่ยนโดยอัตโนมัติ
> - เพื่อ optimal representation สำหรับ hardware นั้นๆ
> - ทำให้ CFD code ของคุณทำงานเหมือนเดิมไม่ว่าจะรันบน development laptop หรือ production cluster

### 2. **Precision Control** (การควบคุมความแม่นยำ)

ปัญหา CFD ที่แตกต่างกันต้องการ numerical precision ที่แตกต่างกัน

| ระดับความแม่นยำ | Use Case | ผลกระทบด้านประสิทธิภาพ |
|-------------------|----------|----------------------|
| Single | Rapid prototyping, educational purposes | เร็วกว่า ~2x, ใช้หน่วยความจำลดลง ~50% |
| Double | High-fidelity simulations, production | มาตรฐาน, สมดุลระหว่างความเร็วและความแม่นยำ |
| Extended | Research requiring extreme accuracy | ช้าที่สุด แต่ความแม่นยำสูงสุด |

### 3. **Physics Safety** (ความปลอดภัยทางฟิสิกส์)

Primitives ของ OpenFOAM บังคับให้มี dimensional consistency และป้องกันการดำเนินการที่ไม่มีความหมายทางฟิสิกส์

> [!WARNING] ตัวอย่างการป้องกันข้อผิดพลาด
> ```cpp
> // Adding pressure to velocity - not allowed!
> volScalarField p = ...;      // [kg/(m·s²)]
> volVectorField U = ...;      // [m/s]
> volScalarField error = p + U; // Compile error: dimensional inconsistency
> ```
>
> ประโยชน์ใน CFD:
> - ป้องกัน dimensional errors ที่นำไปสู่ simulation crashes
> - หลีกเลี่ยง physically incorrect results ที่ดูเหมือนสมเหตุสมผล
> - Type system ทำหน้าที่เป็น first line of defense ต่อ implementation mistakes

## ประเภทข้อมูลพื้นฐาน

### คลาสเวกเตอร์และเทนเซอร์

ใจกลางของเครื่องมือคำนวณของ OpenFOAM คือคลาส geometric primitive ที่จัดการกับคณิตศาสตร์เวกเตอร์และเทนเซอร์

**คลาสเวกเตอร์ (`Vector<Type>`)**:
คลาสเทมเพลต Vector ให้การดำเนินการเวกเตอร์พื้นฐานสำหรับปริมาณมิติและไร้มิติ

- `Vector<scalar>`: เวกเตอร์ 3 มิติของค่าสเกลาร์ (typedef'd ว่า `vector`)
- `Vector<label>`: เวกเตอร์ 3 มิติของดัชนีจำนวนเต็ม (typedef'd ว่า `labelVector`)

**การดำเนินการหลัก:**
```cpp
vector a(1, 2, 3);
vector b(4, 5, 6);
vector c = a + b;          // Vector addition
scalar mag = a.mag();      // Magnitude: sqrt(a_x^2 + a_y^2 + a_z^2)
scalar dot = a & b;        // Dot product: a · b
vector cross = a ^ b;      // Cross product: a × b
```

**คลาสเทนเซอร์:**
OpenFOAM ใช้ลำดับชั้นเทนเซอร์ที่ครอบคลุม:

| คลาสเทนเซอร์ | คำอธิบาย | จำนวนส่วนประกอบ |
|---------------|------------|------------------|
| `Tensor<Type>` | เทนเซอร์อันดับสอง | 9 ส่วนประกอบ |
| `SymmTensor<Type>` | เทนเซอร์สมมาตร | 6 ส่วนประกอบอิสระ |
| `SphericalTensor<Type>` | เทนเซอร์ทรงกลม | ส่วนประกอบแนวทแยงเดียว |

**การดำเนินการทางคณิตศาสตร์ตามกฎของพีชคณิตเทนเซอร์:**
$$\boldsymbol{\tau}_{ij} = \mu \left(\frac{\partial u_i}{\partial x_j} + \frac{\partial u_j}{\partial x_i}\right)$$

โดยที่:
- $\boldsymbol{\tau}_{ij}$: เทนเซอร์ความเค้น
- $\mu$: ความหนืดไดนามิก
- $u_i$, $u_j$: ส่วนประกอบความเร็ว
- $x_i$, $x_j$: พิกัดทิศทาง

### คลาสฟิลด์

คลาสฟิลด์เป็นศูนย์กลางของการจัดการข้อมูลของ OpenFOAM โดยให้คอนเทนเนอร์สำหรับปริมาณทางกายภาพที่กำหนดไว้บนโดเมนการคำนวณ

**ฟิลด์เรขาคณิต:**
- `GeometricField<Type, PatchField, GeoMesh>`: คลาสเทมเพลตสำหรับฟิลด์
- `volScalarField`: ฟิลด์สเกลาร์ที่กำหนดไว้ที่ศูนย์กลางเซลล์
- `volVectorField`: ฟิลด์เวกเตอร์ที่กำหนดไว้ที่ศูนย์กลางเซลล์
- `surfaceScalarField`: ฟิลด์สเกลาร์ที่กำหนดไว้ที่ศูนย์กลางหน้า

**การดำเนินการฟิลด์ใช้ประโยชน์จากเทมเพลตนิพจน์เพื่อประสิทธิภาพการคำนวณ:**
```cpp
volScalarField p(mesh);                    // Pressure field
volVectorField U(mesh);                    // Velocity field
volVectorField UgradU = fvc::grad(U) & U;  // Convection term: (U · ∇)U
```

---

**คำอธิบาย:**

**แหล่งที่มา:** แนวคิดการใช้ฟิลด์เรขาคณิตและการดำเนินการเวกเตอร์/เทนเซอร์ถูกนำไปใช้ใน multiphase solver ของ OpenFOAM

**คำอธิบาย:**
- `volScalarField` ใช้เก็บปริมาณสเกลาร์ เช่น ความดัน (pressure), ค่า volume fraction (α) ของแต่ละเฟส
- `volVectorField` ใช้เก็บปริมาณเวกเตอร์ เช่น ความเร็ว (velocity) ของแต่ละเฟส
- `fvc::grad(U)` คำนวณ gradient ของฟิลด์ความเร็ว ซึ่งจำเป็นสำหรับการคำนวณเทอม convection และ drag forces

**แนวคิดสำคัญ:**
- **GeometricField**: คลาสพื้นฐานสำหรับฟิลด์ทั้งหมดใน OpenFOAM
- **Volume Field (vol)**: ฟิลด์ที่กำหนดที่จุดศูนย์กลางเซลล์
- **Surface Field**: ฟิลด์ที่กำหนดที่ผิวหน้าเซลล์
- **Expression Templates**: เทคนิคการเขียนโปรแกรมที่ช่วยเพิ่มประสิทธิภาพการคำนวณ

---

## โครงสร้างพื้นฐาน Mesh

### คลาส fvMesh

คลาส `fvMesh` ให้โครงสร้าง mesh ปริมาตรจำกัดพื้นฐาน:

```cpp
class fvMesh : public polyMesh
{
    // Cell geometry
    const volScalarField& V() const;        // Cell volumes
    const surfaceScalarField& Sf() const;   // Face area vectors
    const surfaceScalarField& magSf() const; // Face areas

    // Mesh topology
    const labelList& owner() const;         // Face owner cells
    const labelList& neighbour() const;     // Face neighbour cells
};
```

**คำอธิบาย:**

**แหล่งที่มา:** โครงสร้าง mesh ถูกใช้ในทุก solver ของ OpenFOAM รวมทั้ง multiphaseEulerFoam

**คำอธิบาย:**
- `V()`: ส่งคืนฟิลด์ปริมาตรเซลล์ ใช้ในการคำนวณ volume integrals
- `Sf()`: ส่งคืนเวกเตอร์พื้นที่หน้า ใช้ใน surface integrals และการคำนวณ flux
- `owner()`, `neighbour()`: ให้ข้อมูลโทโพโลยี mesh สำหรับการเชื่อมโยงเซลล์ข้างเคียง

**แนวคิดสำคัญ:**
- **Finite Volume Mesh**: แบ่งโดเมนเป็นเซลล์ชิดกันสำหรับการคำนวณ
- **Face Area Vector**: เวกเตอร์ที่มีขนาดเท่ากับพื้นที่หน้าและทิศทางตั้งฉากกับหน้า
- **Owner-Neighbour**: โครงสร้างข้อมูลที่เชื่อมโยงหน้ากับเซลล์สองด้าน

---

### การดำเนินการ Mesh

การดำเนินการ mesh หลัก ได้แก่ การคำนวณเรขาคณิตและการประมาณค่า

**การคำนวณ Gradient:**
$$\nabla \phi_f = \frac{\phi_N - \phi_P}{d_{PN}}$$

**การคำนวณ Divergence:**
$$\nabla \cdot \mathbf{u} = \frac{1}{V_P} \sum_f \mathbf{S}_f \cdot \mathbf{u}_f$$

**การคำนวณ Laplacian:**
$$\nabla^2 \phi = \nabla \cdot (\Gamma \nabla \phi)$$

โดยที่:
- $\phi_f$: ค่าของฟิลด์ที่หน้า f
- $\phi_P$, $\phi_N$: ค่าของฟิลด์ที่เซลล์เจ้าของ (P) และเซลล์ข้างเคียง (N)
- $d_{PN}$: ระยะห่างระหว่างเซลล์
- $V_P$: ปริมาตรของเซลล์ P
- $\mathbf{S}_f$: เวกเตอร์พื้นที่หน้า f
- $\Gamma$: สัมประสิทธิ์การแพร่กระจาย

## การจัดการหน่วยความจำ

### Smart Pointers

OpenFOAM ใช้ smart pointers ที่นับการอ้างอิงสำหรับการจัดการหน่วยความจำอัตโนมัติ

**autoPtr:**
```cpp
autoPtr<volScalarField> pField
(
    new volScalarField
    (
        IOobject("p", runTime.timeName(), mesh),
        mesh
    )
);
```

**tmp:**
```cpp
tmp<volVectorField> gradP = fvc::grad(p);
volVectorField& gradPRef = gradP();  // Automatic reference counting
```

---

**คำอธิบาย:**

**แหล่งที่มา:** Smart pointers ถูกใช้อย่างแพร่หลายใน OpenFOAM solvers ทั้งหมด

**คำอธิบาย:**
- **autoPtr**: เป็น smart pointer ที่มีเจ้าของคนเดียว (exclusive ownership) ใช้สำหรับการส่งผ่านออบเจกต์ที่สร้างขึ้นใหม่
- **tmp**: เป็น smart pointer ที่ใช้ร่วมกันได้ (shared ownership) พร้อมระบบนับการอ้างอิง (reference counting)

**แนวคิดสำคัญ:**
- **Reference Counting**: ติดตามจำนวนการอ้างอิงถึงออบเจกต์
- **Automatic Memory Management**: ป้องกัน memory leaks โดยการทำลายออบเจกต์อัตโนมัติเมื่อไม่มีการอ้างอิง
- **Expression Templates**: tmp ช่วยให้สามารถส่งค่ากลับชั่วคราวจากฟังก์ชันได้โดยไม่ต้องคัดลอกข้อมูล

---

> [!TIP] ประโยชน์ของ Smart Pointers
> - **ป้องกัน memory leaks**: การทำลายออบเจกต์อัตโนมัติเมื่อไม่มีการอ้างอิง
> - **การแชร์ข้อมูลอย่างปลอดภัย**: การนับการอ้างอิงป้องกันการเข้าถึงข้อมูลที่ถูกทำลาย
> - **ประสิทธิภาพ**: การส่งผ่านออบเจกต์โดยไม่ต้องคัดลอกข้อมูล

## ระบบพีชคณิตเชิงเส้น

### คลาส LduMatrix

คลาส `LduMatrix` ใช้ระบบเชิงเส้นเบาบางโดยใช้รูปแบบ Lower-Diagonal-Upper:

```cpp
template<class Type, class DType, class LUType>
class LduMatrix
{
    // Matrix coefficients
    const Field<DType>& diag() const;      // Diagonal
    const Field<LUType>& upper() const;    // Upper part
    const Field<LUType>& lower() const;    // Lower part

    // Solver interface
    SolverPerformance<Type> solve
    (
        Field<Type>& psi,
        const Field<Type>& source,
        const dictionary& solverControls
    ) const;
};
```

**คำอธิบาย:**

**แหล่งที่มา:** ระบบ LduMatrix เป็นพื้นฐานของการแก้สมการเชิงเส้นใน OpenFOAM

**คำอธิบาย:**
- **LduMatrix**: เก็บเมทริกซ์แบบเบาบางในรูปแบบ Lower-Diagonal-Upper
- **diag()**: เก็บสัมประสิทธิ์เส้นทแยงมุม (a_P)
- **upper()**, **lower()**: เก็บสัมประสิทธิ์ข้างเคียง (a_N)
- **solve()**: อินเทอร์เฟซสำหรับการแก้สมการเชิงเส้น

**แนวคิดสำคัญ:**
- **Sparse Matrix Storage**: เก็บเฉพาะสัมประสิทธิ์ที่ไม่ใช่ศูนย์เพื่อประหยัดหน่วยความจำ
- **Finite Volume Discretization**: โครงสร้างเมทริกซ์สะท้อนถึง connectivity ของ mesh
- **Iterative Solvers**: ใช้ iterative methods เช่น GAMG, PCG, PBiCGStab ในการแก้สมการ

---

### การประกอบเมทริกซ์

สัมประสิทธิ์เมทริกซ์ถูกประกอบโดยใช้การกระจายตามปริมาตรจำกัด

**สมการ Convection-Diffusion:**
$$\frac{\partial \phi}{\partial t} + \nabla \cdot (\mathbf{u} \phi) = \nabla \cdot (\Gamma \nabla \phi) + S_\phi$$

**รูปแบบกระจาย:**
$$a_P \phi_P + \sum_N a_N \phi_N = b_P$$

โดยที่:
- $a_P$: สัมประสิทธิ์เส้นทแยงมุม (เซลล์ P)
- $a_N$: สัมประสิทธิ์ข้างเคียง
- $b_P$: เทอมต้นทาง
- $\phi_P$, $\phi_N$: ค่าของฟิลด์ที่เซลล์ P และ N

**OpenFOAM Code Implementation:**
```cpp
// Matrix assembly for convection-diffusion equation
fvScalarMatrix phiEqn
(
    fvm::ddt(phi)                    // Temporal term: ∂φ/∂t
  + fvm::div(phi, U)                 // Convection term: ∇·(uφ)
  - fvm::laplacian(Diffusivity, phi) // Diffusion term: ∇·(Γ∇φ)
 ==
    Source                           // Source term: S_φ
);
```

**คำอธิบาย:**

**แหล่งที่มา:** การประกอบเมทริกซ์เป็นแกนหลักของ multiphase momentum equations ใน MomentumTransferPhaseSystem

**คำอธิบาย:**
- **fvm::ddt()**: เทอม temporal derivative ใช้ implicit discretization
- **fvm::div()**: เทอม convection ใช้ finite volume discretization
- **fvm::laplacian()**: เทอม diffusion ใช้ central differencing
- **fvm** (finite volume method): สร้างเมทริกซ์ coefficients สำหรับการแก้ implicit
- **fvc** (finite volume calculus): คำนวณ explicit terms

**แนวคิดสำคัญ:**
- **Implicit vs Explicit**: implicit terms ถูกเพิ่มเข้าไปในเมทริกซ์, explicit terms ถูกคำนวณโดยตรง
- **Linear System**: สมการที่ discretized ถูกแปลงเป็นระบบเชิงเส้น Ax = b
- **Matrix Assembly**: การรวบรวม coefficients จากแต่ละ term ในสมการ

---

## ระบบ Input/Output

### คลาส IO

OpenFOAM ให้ระบบ I/O ที่ครอบคลุมสำหรับการอ่าน/เขียนข้อมูลการจำลอง

**คลาส IOobject:**
```cpp
IOobject pHeader
(
    "p",                          // Name
    runTime.timeName(),           // Time instance
    mesh,                         // Registry
    IOobject::MUST_READ,          // Read option
    IOobject::AUTO_WRITE          // Write option
);
```

**ฟิลด์ I/O:**
```cpp
volScalarField p(pHeader, mesh);
p.write();                       // Write to file
```

**คำอธิบาย:**

**แหล่งที่มา:** ระบบ I/O ของ OpenFOAM ถูกใช้ในทุก solver สำหรับการจัดการ field data

**คำอธิบาย:**
- **IOobject**: คลาสพื้นฐานสำหรับการจัดการไฟล์ I/O
- **MUST_READ**: ต้องอ่านไฟล์ ถ้าไม่พบจะเกิด error
- **AUTO_WRITE**: เขียนไฟล์อัตโนมัติเมื่อ simulation บันทึกผลลัพธ์
- **Time Instance**: ระบุ directory ของข้อมูล (เช่น 0/, 0.1/, 0.2/)

**แนวคิดสำคัญ:**
- **Dictionary-based I/O**: ข้อมูลถูกเก็บในรูปแบบ text-based dictionary
- **Time Directories**: แต่ละ time step มี directory ของตัวเอง
- **Field Registration**: ฟิลด์ถูกจดทะเบียนใน mesh object registry

---

### ระบบ Dictionary

คลาส `dictionary` ให้การจัดเก็บพารามิเตอร์แบบลำดับชั้น:

```cpp
dictionary transportProperties
(
    IOobject("transportProperties", runTime.constant(), mesh)
);

scalar nu = transportProperties.lookupOrDefault<scalar>("nu", 1e-5);
word turbulenceModel = transportProperties.lookup<word>("turbulenceModel");
```

**คำอธิบาย:**

**แหล่งที่มา:** Dictionary system ถูกใช้อย่างแพร่หลายใน OpenFOAM สำหรับ configuration และ parameter settings

**คำอธิบาย:**
- **dictionary**: เก็บ key-value pairs ในรูปแบบลำดับชั้น
- **lookup()**: ค้นหาค่าจาก dictionary ถ้าไม่พบจะเกิด error
- **lookupOrDefault()**: ค้นหาค่า ถ้าไม่พบใช้ค่า default
- **constant()**: directory ที่เก็บข้อมูลคงที่ (ไม่ขึ้นกับเวลา)

**แนวคิดสำคัญ:**
- **Hierarchical Structure**: dictionaries สามารถซ้อนกันได้
- **Type Safety**: lookup functions ตรวจสอบ type ของข้อมูล
- **Default Values**: สามารถระบุค่า default สำหรับ optional parameters

---

**ตัวเลือกการอ่าน/เขียน IOobject:**

| ค่า | ความหมาย | การใช้งาน |
|------|------------|------------|
| `MUST_READ` | ต้องอ่านไฟล์ | ฟิลด์เริ่มต้นที่จำเป็น |
| `READ_IF_PRESENT` | อ่านถ้ามี | ฟิลด์ที่มีหรือไม่มีก็ได้ |
| `NO_READ` | ไม่อ่าน | สร้างฟิลด์ใหม่ |
| `AUTO_WRITE` | เขียนอัตโนมัติ | บันทึกผลลัพธ์ |
| `NO_WRITE` | ไม่เขียน | ฟิลด์ชั่วคราว |

---

พื้นฐาน primitives เหล่านี้เป็นหลักมูลของเฟรมเวิร์กการคำนวณของ OpenFOAM ซึ่งเปิดให้สามารถพัฒนา CFD solvers ที่ซับซ้อนผ่านการประกอบและการขยายองค์ประกอบหลักเหล่านี้

ในหัวข้อถัดไป เราจะเจาะลึกแต่ละ primitive type เพื่อความเข้าใจที่ลึกซึ้งยิ่งขึ้น:
- [[01_Introduction|บทนำ]] - แนะนำระบบประเภทข้อมูล
- [[02_Topic_1_Basic_Primitives_(`label`,_`scalar`,_`word`)|Primitive พื้นฐาน]] - label, scalar, word
- [[03_Topic_2_Dimensioned_Types_(`dimensionedType`)|ประเภทที่มีมิติ]] - dimensionedType
- [[04_Topic_3_Smart_Pointers_(`autoPtr`,_`tmp`)|Smart Pointers]] - autoPtr, tmp
- [[05_Topic_4_Containers_(`List`)|คอนเทนเนอร์]] - List, PtrList
- [[06_Summary_&_Reference|สรุปและอ้างอิง]] - ภาพรวมและตารางอ้างอิง