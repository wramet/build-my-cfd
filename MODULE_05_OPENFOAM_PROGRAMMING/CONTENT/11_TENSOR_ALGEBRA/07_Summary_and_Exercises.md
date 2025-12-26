# บทสรุปและแบบฝึกหัด: ความเชี่ยวชาญพีชคณิตเทนเซอร์ (Summary & Exercises: Tensor Algebra Mastery)

```mermaid
mindmap
root((พีชคณิตเทนเซอร์))
ประเภท (Types)
Full Tensor (9)
Symmetric (6)
Spherical (1)
การดำเนินการ (Operations)
Dot (&) / Double Dot (&&)
Trace / Det / Inv
Deviatoric / Skew
การวิเคราะห์ (Analysis)
Eigenvalues
Eigenvectors
Invariants
ฟิสิกส์ (Physics)
Stress / Strain
Reynolds Stress
Conductivity
```
> **Figure 1:** แผนผังความคิดสรุปองค์ประกอบของพีชคณิตเทนเซอร์ ครอบคลุมทั้งประเภทข้อมูล การดำเนินการพื้นฐาน การวิเคราะห์ค่าลักษณะเฉพาะ และการประยุกต์ใช้ในฟิสิกส์ของการจำลองความปลอดภัยทางฟิสิกส์ไม่ส่งผลกระทบต่อความเร็วในการจำลอง ผ่านการใช้พลังของ C++ Template Metaprogramming ในการตรวจสอบความสอดคล้องทางมิติทั้งหมดที่ขั้นตอนการคอมไพล์โปรแกรมเพียงครั้งเดียว

## ส่วนที่ 1: บทสรุปที่ครอบคลุม (Comprehensive Summary)

### รากฐานเทนเซอร์ใน OpenFOAM (The Tensor Foundation in OpenFOAM)

กรอบงานพีชคณิตเทนเซอร์ของ OpenFOAM เป็นรากฐานทางคณิตศาสตร์สำหรับการสร้างแบบจำลองฟิสิกส์ขั้นสูง ช่วยให้สามารถเป็นตัวแทนเชิงรูปธรรมของปริมาณที่มีทิศทางและการเปลี่ยนแปลงเชิงพื้นที่ในกลศาสตร์ต่อเนื่อง

กรอบงานนี้ขยายขอบเขตไปไกลกว่าคณิตศาสตร์สเกลาร์และเวกเตอร์อย่างง่าย เพื่อจับพฤติกรรมแอนไอโซทรอปิก (anisotropic) ที่ซับซ้อนที่พบในการไหลของของไหลจริงและการตอบสนองของวัสดุ

> [!INFO] สถาปัตยกรรมเทนเซอร์หลัก
> OpenFOAM ใช้ประเภทเทนเซอร์พื้นฐานสามประเภท แต่ละประเภทได้รับการปรับให้เหมาะสมสำหรับการใช้งานทางฟิสิกส์เฉพาะผ่านการจัดเก็บที่มีประสิทธิภาพหน่วยความจำและการดำเนินการที่ปรับให้เหมาะสมทางคำนวณ

#### ลำดับชั้นประเภทเทนเซอร์ (Tensor Type Hierarchy)

| ประเภทเทนเซอร์ | องค์ประกอบอิสระ | รูปแบบหน่วยความจำ | การใช้งานหลัก |
|-------------|------------------------|---------------|---------------------|
| **Tensor** | 9 องค์ประกอบ | `[xx, xy, xz, yx, yy, yz, zx, zy, zz]` | การดำเนินการหมุน, การแปลงทั่วไป |
| **symmTensor** | 6 องค์ประกอบ | `[xx, yy, zz, xy, yz, xz]` | เทนเซอร์ความเค้น, เทนเซอร์อัตราความเครียด |
| **sphericalTensor** | 1 องค์ประกอบ | `[ii]` | ความดันไอโซทรอปิก, คุณสมบัติวัสดุไอโซทรอปิก |

#### 1. เทนเซอร์เต็ม (`Tensor`)

เทนเซอร์ $3 \times 3$ สมบูรณ์ที่มี 9 องค์ประกอบอิสระ:

$$\mathbf{T} = \begin{bmatrix} T_{xx} & T_{xy} & T_{xz} \\ T_{yx} & T_{yy} & T_{yz} \\ T_{zx} & T_{zy} & T_{zz} \end{bmatrix}$$

**การประยุกต์ใช้ทางฟิสิกส์:**
- เกรเดียนต์ของการเสียรูป (Deformation gradients)
- เกรเดียนต์ความเร็ว (Velocity gradients - $\nabla\mathbf{u}$)
- เทนเซอร์การหมุนทั่วไป
- การกระจายความเค้นแบบไม่สมมาตร

#### 2. เทนเซอร์สมมาตร (`symmTensor`)

เทนเซอร์ $3 \times 3$ ที่มี 6 องค์ประกอบอิสระโดยบังคับ $T_{ij} = T_{ji}$:

$$\mathbf{S} = \begin{bmatrix} S_{xx} & S_{xy} & S_{xz} \\ S_{xy} & S_{yy} & S_{yz} \\ S_{xz} & S_{yz} & S_{zz} \end{bmatrix}$$

**ประสิทธิภาพหน่วยความจำ:** ลดลง 33% เมื่อเทียบกับเทนเซอร์เต็ม

**การประยุกต์ใช้ทางฟิสิกส์:**
- เทนเซอร์ความเค้น Cauchy: $\boldsymbol{\sigma}$
- เทนเซอร์อัตราความเครียด: $\mathbf{D} = \frac{1}{2}(\nabla\mathbf{u} + \nabla\mathbf{u}^T)$
- เทนเซอร์ความเค้น Reynolds: $\mathbf{R} = \overline{\mathbf{u}' \otimes \mathbf{u}'}$
- เทนเซอร์สัมประสิทธิ์การแพร่

#### 3. เทนเซอร์ทรงกลม (`sphericalTensor`)

เทนเซอร์ไอโซทรอปิกที่เป็นตัวแทนของ $\alpha\mathbf{I}$:

$$\boldsymbol{\Lambda} = \lambda\mathbf{I} = \lambda\begin{bmatrix} 1 & 0 & 0 \\ 0 & 1 & 0 \\ 0 & 0 & 1 \end{bmatrix}$$

**ประสิทธิภาพหน่วยความจำ:** ลดลง 89% เมื่อเทียบกับเทนเซอร์เต็ม

**การประยุกต์ใช้ทางฟิสิกส์:**
- สนามความดันไอโซทรอปิก
- การดำเนินการเทนเซอร์เอกลักษณ์
- คุณสมบัติวัสดุไอโซทรอปิก

---

### กรอบการทำงานของการดำเนินการทางคณิตศาสตร์ (Mathematical Operations Framework)

#### การหดตัวของเทนเซอร์ (Tensor Contractions)

**การหดตัวเดี่ยว (`&`):** การคูณเมทริกซ์-เวกเตอร์ หรือ เทนเซอร์-เทนเซอร์

$$\mathbf{y} = \mathbf{T} \cdot \mathbf{v} \quad \text{โดยที่} \quad y_i = \sum_{j=1}^{3} T_{ij} v_j$$

```cpp
// ตัวอย่าง Single contraction
vector w = T & v;       // Tensor-vector → vector
tensor C = A & B;       // Tensor-tensor → tensor
```

> **📚 แหล่งที่มา (Source):**
> - `.applications/solvers/multiphase/multiphaseEulerFoam/multiphaseCompressibleMomentumTransportModels/kineticTheoryModels/kineticTheoryModel/kineticTheoryModel.C:75`
> 
> **📖 คำอธิบาย (Explanation):**
> การดำเนินการ Single Contraction (`&`) เป็นการคูณเมทริกซ์กับเวกเตอร์หรือเทนเซอร์กับเทนเซอร์เพื่อให้ได้ผลลัพธ์เป็นเวกเตอร์หรือเทนเซอร์ตามลำดับ การดำเนินการนี้พบได้บ่อยในโค้ด OpenFOAM สำหรับการคำนวณแรงเฉือน การถ่ายเทโมเมนตัม และการแปลงค่าระหว่างเทนเซอร์

**การหดตัวคู่ (`&&`):** ผลคูณภายใน Frobenius (Frobenius inner product)

$$\mathbf{A} : \mathbf{B} = \sum_{i,j=1}^{3} A_{ij} B_{ij} = \text{tr}(\mathbf{A} \cdot \mathbf{B}^T)$$

```cpp
// Double contraction yields scalar
scalar s = A && B;      // Frobenius inner product
```

> **📚 แหล่งที่มา (Source):**
> - `.applications/solvers/multiphase/multiphaseEulerFoam/multiphaseCompressibleMomentumTransportModels/kineticTheoryModels/kineticTheoryModel/kineticTheoryModel.C:150`
> 
> **📖 คำอธิบาย (Explanation):**
> การดำเนินการ Double Contraction (`&&`) คือผลคูณภายในของ Frobenius ซึ่งเป็นการคูณสมาชิกทุกตัวของเทนเซอร์สองตัวแล้วบวกรวมกัน ให้ผลลัพธ์เป็นสเกลาร์ การดำเนินการนี้มีประโยชน์ในการคำนวณพลังงาน เช่น อัตราการกระจายของพลังงาน (energy dissipation rate)

**ความสำคัญทางฟิสิกส์:**
- การคำนวณอัตรางาน (Work rate calculations)
- ผลคูณความเค้น-ความเครียด (Stress-strain products)
- พจน์การสลายตัวของพลังงาน (Energy dissipation terms)

#### การแยกองค์ประกอบเทนเซอร์ (Tensor Decomposition)

**ส่วนสมมาตร (Symmetric Part):**

$$\mathbf{S} = \frac{1}{2}(\mathbf{T} + \mathbf{T}^T)$$

```cpp
symmTensor S = symm(T);  // แยกส่วนสมมาตร
```

> **📚 แหล่งที่มา (Source):**
> - `.applications/solvers/combustion/XiFoam/PDRFoam/PDRModels/dragModels/basic/basic.C:82`
> 
> **📖 คำอธิบาย (Explanation):**
> การแยกส่วนสมมาตรเกี่ยวข้องกับการยืดหดและการเฉือนที่ไม่ทำให้เกิดการหมุน

**ส่วนแอนตี้สมมาตร (Antisymmetric/Skew Part):**

$$\mathbf{A} = \frac{1}{2}(\mathbf{T} - \mathbf{T}^T)$$

```cpp
tensor A = skew(T);      // แยกส่วนแอนตี้สมมาตร
```

> **📚 แหล่งที่มา (Source):**
> - `.applications/solvers/multiphase/multiphaseEulerFoam/multiphaseCompressibleMomentumTransportModels/phasePressureModel/phasePressureModel.C:98`
> 
> **📖 คำอธิบาย (Explanation):**
> ส่วน antisymmetric เกี่ยวข้องกับการหมุนและ vorticity ซึ่งสำคัญในการวิเคราะห์การไหลแบบหมุน

**ส่วนเบี่ยงเบน (Deviatoric Part):**

$$\text{dev}(\mathbf{T}) = \mathbf{T} - \frac{1}{3}\text{tr}(\mathbf{T})\mathbf{I}$$

```cpp
symmTensor devT = dev(T);  // ส่วน Deviatoric (traceless)
```

> **📚 แหล่งที่มา (Source):**
> - `.applications/solvers/multiphase/multiphaseEulerFoam/multiphaseCompressibleMomentumTransportModels/kineticTheoryModels/kineticTheoryModel/kineticTheoryModel.C:210`
> 
> **📖 คำอธิบาย (Explanation):**
> ส่วน Deviatoric คือเทนเซอร์ที่หักลบส่วน isotropic ออกไป (trace เป็นศูนย์) ใช้วิเคราะห์ความเครียดเฉือนโดยไม่รวมความดันไฮโดรสแตติก

#### ค่าคงที่เทนเซอร์ (Tensor Invariants)

ค่าคงที่หลักของเทนเซอร์สมมาตร:

```cpp
symmTensor T;

// Invariant ที่ 1 (Trace)
scalar I1 = tr(T);

// Invariant ที่ 2
scalar I2 = 0.5 * (pow(tr(T), 2) - tr(T & T));

// Invariant ที่ 3 (Determinant)
scalar I3 = det(T);
```

> **📚 แหล่งที่มา (Source):**
> - `.applications/solvers/combustion/XiFoam/PDRFoam/XiModels/XiEqModels/XiEqModel/XiEqModel.C:145`
> 
> **📖 คำอธิบาย (Explanation):**
> Invariants คือค่าที่ไม่เปลี่ยนแปลงเมื่อมีการหมุนระบบพิกัด ใช้ในการวิเคราะห์สภาพของวัสดุ

**การตีความทางฟิสิกส์:**
- **I₁**: องค์ประกอบความเค้นไฮโดรสแตติก
- **I₂**: ขนาดความเค้นเบี่ยงเบน
- **I₃**: ตัวบ่งชี้การเปลี่ยนแปลงปริมาตร

---

### การแยกค่าลักษณะเฉพาะ (Eigenvalue Decomposition)

**ปัญหาค่าลักษณะเฉพาะ (The Eigenvalue Problem):**

$$\mathbf{A}\mathbf{v} = \lambda\mathbf{v}$$

โดยที่:
- $\lambda$: Eigenvalue (ค่าหลัก)
- $\mathbf{v}$: Eigenvector (ทิศทางหลัก)
- $\mathbf{A}$: Symmetric tensor

**การนำไปใช้ใน OpenFOAM:**

```cpp
symmTensor stressTensor;  // เทนเซอร์ความเค้นอินพุต
vector eigenvalues;       // ความเค้นหลัก [σ₁, σ₂, σ₃]
tensor eigenvectors;      // ทิศทางหลักในรูปคอลัมน์

// การแยกค่าลักษณะเฉพาะ
eigenValues(stressTensor, eigenvalues, eigenvectors);
```

> **📚 แหล่งที่มา (Source):**
> - `.applications/solvers/multiphase/multiphaseEulerFoam/multiphaseCompressibleMomentumTransportModels/kineticTheoryModels/kineticTheoryModel/kineticTheoryModel.C:320`
> 
> **📖 คำอธิบาย (Explanation):**
> การแยกค่าลักษณะเฉพาะช่วยในการหาทิศทางหลักและความเค้นหลัก ซึ่งสำคัญต่อการวิเคราะห์ความล้มเหลวและ anisotropy

**การวิเคราะห์ความเค้นหลัก (Principal Stress Analysis):**

```cpp
// เข้าถึงค่าหลักแต่ละตัว
scalar sigma1 = eigenvalues.x();  // ความเค้นหลักสูงสุด
scalar sigma2 = eigenvalues.y();
scalar sigma3 = eigenvalues.z();

// เข้าถึงทิศทางหลัก
vector n1 = eigenvectors.col(0);  // ทิศทางของ σ₁
```

**การประยุกต์ใช้:**
- เกณฑ์ความล้มเหลวในกลศาสตร์ของแข็ง
- การระบุลักษณะ Anisotropy ในแบบจำลองความปั่นป่วน
- การวิเคราะห์ทิศทางวัสดุคอมโพสิต

---

### การดำเนินการแคลคูลัสเทนเซอร์ (Tensor Calculus Operations)

#### การดำเนินการเกรเดียนต์ (Gradient Operations)

**เทนเซอร์เกรเดียนต์ความเร็ว (Velocity Gradient Tensor):**

$$[\nabla \mathbf{U}]_{ij} = \frac{\partial U_i}{\partial x_j}$$

```cpp
volVectorField U(mesh);
volTensorField gradU = fvc::grad(U);  // ∇U
```

**เทนเซอร์อัตราความเครียด (Strain-Rate Tensor):**

$$\mathbf{D} = \text{sym}(\nabla \mathbf{u})$$

```cpp
volSymmTensorField D = symm(gradU);  // ส่วนสมมาตร
```

**เทนเซอร์วอร์ติซิตี้ (Vorticity Tensor):**

$$\boldsymbol{\Omega} = \text{skew}(\nabla \mathbf{u})$$

```cpp
volTensorField Omega = skew(gradU);  // ส่วนแอนตี้สมมาตร
```

#### การดำเนินการไดเวอร์เจนซ์ (Divergence Operations)

**ไดเวอร์เจนซ์ความเค้น (Stress Divergence):**

$$(\nabla \cdot \boldsymbol{\tau})_i = \sum_{j=1}^{3} \frac{\partial \tau_{ij}}{\partial x_j}$$

```cpp
volSymmTensorField tau(mesh);
volVectorField divTau = fvc::div(tau);  // ∇·τ
```

**ความหมายทางฟิสิกส์:** แรงสุทธิต่อหน่วยปริมาตรจากเกรเดียนต์ความเค้น (N/m³)

---

### การประยุกต์ใช้ใน CFD (CFD Applications)

#### 1. Cauchy Stress Tensor

$$\boldsymbol{\sigma} = -p\mathbf{I} + 2\mu\mathbf{D} + \lambda(\nabla \cdot \mathbf{u})\mathbf{I}$$

```cpp
sigma = -p*I + 2*mu*D + lambda*(fvc::div(U))*I;
```

#### 2. Reynolds Stress Transport

**พจน์การผลิต (Production Term):**

```cpp
volSymmTensorField P = -(R & fvc::grad(U)) + (R & fvc::grad(U)).T();
```

#### 3. Von Mises Stress

$$\sigma_{vm} = \sqrt{\frac{3}{2}\mathbf{S}:\mathbf{S}}$$

```cpp
volScalarField vonMises = sqrt(1.5) * mag(dev(sigma));
```

---

### สถาปัตยกรรมการนำไปใช้งาน (Implementation Architecture)

#### การจัดเก็บที่มีประสิทธิภาพหน่วยความจำ (Memory-Efficient Storage)

`symmTensor` เก็บข้อมูลเพียง 6 ค่าแทนที่จะเป็น 9 ค่า ลดการใช้หน่วยความจำลง 33% และเพิ่มประสิทธิภาพ Cache

#### Template Specialization

OpenFOAM ใช้ Template Specialization เพื่อปรับการคำนวณให้เหมาะสมกับประเภทเทนเซอร์ เช่น การ Transpose ของเทนเซอร์สมมาตรคือตัวมันเอง (ไม่มีต้นทุนการคำนวณ)

#### การวิเคราะห์มิติ (Dimensional Analysis)

ระบบตรวจสอบหน่วย (Dimensions) ช่วยป้องกันข้อผิดพลาดทางฟิสิกส์ระหว่างคอมไพล์และรันไทม์

---

## ส่วนที่ 2: แบบฝึกหัด (Exercises)

### ส่วนที่ 1: การเลือกประเภทเทนเซอร์ (Tensor Type Selection)

**โจทย์:** เลือกประเภทเทนเซอร์ที่เหมาะสมที่สุด (`tensor`, `symmTensor`, หรือ `sphericalTensor`) สำหรับปริมาณต่อไปนี้:

1. ความดันไอโซทรอปิกในของไหล
2. Reynolds shear stress
3. เกรเดียนต์ความเร็ว ($\nabla\mathbf{U}$)
4. เทนเซอร์อัตราความเครียดของของไหล
5. เทนเซอร์เกรเดียนต์การเปลี่ยนรูป
6. การนำความร้อนในวัสดุแอนไอโซทรอปิก
7. การสเกลเทนเซอร์เอกลักษณ์ (Identity tensor scaling)
8. เทนเซอร์วอร์ติซิตี้ (Vorticity tensor)

---

### ส่วนที่ 2: การวิเคราะห์โค้ด (Code Analysis)

**โจทย์:** พิจารณาโค้ดต่อไปนี้:

```cpp
tensor T(1, 2, 3, 4, 5, 6, 7, 8, 9);
vector v(1, 0, 0);
auto res1 = T & v;
auto res2 = T && T;
```

**คำถาม:**
1. `res1` เป็นประเภทใด? มีค่าเท่าไร?
2. `res2` เป็นประเภทใด? มีค่าเท่าไร?
3. จะเกิดอะไรขึ้นถ้าคุณพยายามทำ `vector res3 = v && v`?

---

### ส่วนที่ 3: แคลคูลัสเทนเซอร์ (Tensor Calculus)

**โจทย์:** กำหนดสนามความเร็ว $\mathbf{U} = (U_x, U_y, U_z)$, จงเขียนโค้ด OpenFOAM เพื่อ:

1. คำนวณเทนเซอร์เกรเดียนต์ความเร็ว $\nabla\mathbf{U}$
2. แยกเทนเซอร์อัตราความเครียดสมมาตร $\mathbf{D}$
3. แยกเทนเซอร์วอร์ติซิตี้แอนตี้สมมาตร $\boldsymbol{\Omega}$
4. คำนวณ Trace ของเทนเซอร์อัตราความเครียด
5. คำนวณส่วน Deviatoric ของเทนเซอร์อัตราความเครียด

---

### ส่วนที่ 4: การประยุกต์ใช้วิเคราะห์ความเค้น (Stress Analysis Application)

**โจทย์:** คุณต้องคำนวณ **ความเค้น Von Mises** เพื่อวิเคราะห์ความล้มเหลวของวัสดุโดยใช้สูตร:

$$\sigma_{vm} = \sqrt{\frac{3}{2}\mathbf{S}:\mathbf{S}}$$

โดยที่ $\mathbf{S}$ คือส่วน Deviatoric ของเทนเซอร์ความเค้น $\boldsymbol{\sigma}$.

**ภารกิจ:**
1. เขียนโค้ดเพื่อคำนวณ `vonMises` จาก `volSymmTensorField sigma`
2. คำนวณความเค้นหลัก (Principal stresses) จาก `sigma`
3. หาความเค้นหลักสูงสุดและทิศทางของมัน
4. ตรวจสอบว่าวัสดุเสียหายหรือไม่ (เกิน Yield stress ที่ 250 MPa)

---

### ส่วนที่ 5: การสร้างแบบจำลองความปั่นป่วน (Turbulence Modeling)

**โจทย์:** ในการสร้างแบบจำลอง RANS เทนเซอร์ความเค้น Reynolds $\mathbf{R}$ ต้องการ:

1. นิยามสนามเทนเซอร์สมมาตรสำหรับ Reynolds stress
2. คำนวณพจน์การผลิต $P_{ij}$ จากเกรเดียนต์ความเร็วเฉลี่ย
3. คำนวณพลังงานจลน์ความปั่นป่วน: $k = \frac{1}{2}\text{tr}(\mathbf{R})$
4. คำนวณการแยกค่าลักษณะเฉพาะของ $\mathbf{R}$ เพื่อวิเคราะห์ Anisotropy

---

### ส่วนที่ 6: การแก้ไขปัญหา (Debugging)

**โจทย์:** ระบุและแก้ไขข้อผิดพลาดในโค้ดต่อไปนี้:

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

## ส่วนที่ 3: เฉลย (Solutions)

### เฉลยส่วนที่ 1: การเลือกประเภทเทนเซอร์

| ปริมาณ | ประเภทเทนเซอร์ | เหตุผล |
|----------|-------------|-----------|
| 1. ความดันไอโซทรอปิก | `sphericalTensor` | เท่ากันทุกทิศทาง |
| 2. Reynolds stress | `symmTensor` | สมมาตรตามนิยาม |
| 3. เกรเดียนต์ความเร็ว | `tensor` | โดยทั่วไปไม่สมมาตร |
| 4. อัตราความเครียด | `symmTensor` | สมมาตรตามนิยาม |
| 5. เกรเดียนต์การเปลี่ยนรูป | `tensor` | อาจรวมถึงการหมุน |
| 6. การนำความร้อนแอนไอโซทรอปิก | `symmTensor` | คุณสมบัติวัสดุสมมาตร |
| 7. การสเกล Identity | `sphericalTensor` | การสเกลแบบไอโซทรอปิก |
| 8. วอร์ติซิตี้ | `tensor` | แอนตี้สมมาตรตามนิยาม |

### เฉลยส่วนที่ 2: การวิเคราะห์โค้ด

```cpp
// res1: ประเภท vector, ค่า = (1, 4, 7)
vector res1 = T & v;

// res2: ประเภท scalar, ค่า = 285
scalar res2 = T && T;

// Error: Double contraction ของเวกเตอร์ไม่นิยาม
// ควรใช้ dot product: scalar s = v & v;
```

### เฉลยส่วนที่ 3: แคลคูลัสเทนเซอร์

```cpp
// 1. Velocity gradient tensor
volTensorField gradU = fvc::grad(U);

// 2. Strain-rate tensor (symmetric)
volSymmTensorField D = symm(gradU);

// 3. Vorticity tensor (antisymmetric)
volTensorField Omega = skew(gradU);

// 4. Trace (volumetric dilation rate)
volScalarField trD = tr(D);

// 5. Deviatoric strain-rate
volSymmTensorField devD = dev(D);
```

### เฉลยส่วนที่ 4: การวิเคราะห์ความเค้น

```cpp
volSymmTensorField sigma(mesh);
scalar yieldStress = 250e6;

// 1. Von Mises stress
volScalarField vonMises = sqrt(1.5) * mag(dev(sigma));

// 2. & 3. Principal stress analysis
forAll(sigma, i) {
    vector eigenvalues;
    tensor eigenvectors;
    eigenValues(sigma[i], eigenvalues, eigenvectors);

    // ความเค้นหลักสูงสุดและทิศทาง
    scalar maxS = max(eigenvalues);
    
    // 4. Yield check
    if (vonMises[i] > yieldStress) {
        // Material Yielding!
    }
}
```

### เฉลยส่วนที่ 5: การสร้างแบบจำลองความปั่นป่วน

```cpp
// 1. Reynolds stress tensor
volSymmTensorField R(IOobject("R", ...), mesh, ...);

// 2. Production term
volTensorField gradU = fvc::grad(U);
volSymmTensorField P = -(R & gradU) + (R & gradU).T();

// 3. Turbulent Kinetic Energy
volScalarField k = 0.5 * tr(R);

// 4. Eigenvalue analysis (inside loop over cells)
vector lambdas = eigenValues(R[cellI]);
```

### เฉลยส่วนที่ 6: การแก้ไขปัญหา

```cpp
// Fix 1: Single contraction returns vector
vector w1 = T & v;

// Fix 2: Match types (convert symmTensor to tensor if needed)
tensor result = T & tensor(S);

// Fix 3: Check determinant before inverse
if (mag(det(S)) > SMALL) { result = inv(S); }

// Fix 4: Correct mag call
scalar magT = mag(T);
```

---

## เส้นทางการสำรวจขั้นสูง (Advanced Exploration Paths)

### การศึกษาการนำไปใช้ขั้นสูง

1.  **ตรวจสอบซอร์สโค้ด** ใน `src/OpenFOAM/primitives/Tensor/`:
    - `TensorI.H`: การนำไปใช้งานเทนเซอร์หลัก
    - `symmTensorI.H`: การปรับแต่งสำหรับเทนเซอร์สมมาตร

2.  **ศึกษาแบบจำลองความปั่นป่วน** ที่ใช้พีชคณิตเทนเซอร์:
    - `RASModels/LaunderSharmaKE`: แนวทาง RANS
    - `LESModels/Smagorinsky`: การดำเนินการเทนเซอร์ LES

### พื้นที่การวิจัย

- **การไหลหลายเฟส (Multiphase Flow):** เทนเซอร์ความเค้นระหว่างหน้าสัมผัส
- **กลศาสตร์ของแข็ง (Solid Mechanics):** Hyperelasticity, Plasticity
- **การไหลทางชีวภาพ (Biological Flows):** เทนเซอร์วัสดุแอนไอโซทรอปิกสำหรับเนื้อเยื่อ

การเชี่ยวชาญพีชคณิตเทนเซอร์เปิดทางสู่การสร้างแบบจำลองฟิสิกส์ขั้นสูงที่สามารถจับธรรมชาติหลายมิติของการไหลและพฤติกรรมวัสดุได้อย่างแม่นยำ