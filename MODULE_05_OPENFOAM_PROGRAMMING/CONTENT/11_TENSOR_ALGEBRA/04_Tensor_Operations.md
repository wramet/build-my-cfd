# การดำเนินการเทนเซอร์ (Tensor Operations)

![[tensor_workshop_tools.png]]
> **มุมมองวิชาการ:** โต๊ะทำงานเฉพาะทางสำหรับเทนเซอร์ เครื่องมืออย่าง "ตัวรีด Trace" (tr), "ตาชั่ง Determinant" (det), และ "เครื่องกลับด้าน Inverter" (inv) วางเรียงราย เทนเซอร์กำลังถูกประมวลผลเพื่อดึงส่วน "Deviatoric" ออกมา

## ภาพรวมการดำเนินการเทนเซอร์

การดำเนินการเทนเซอร์ของ OpenFOAM เป็นรากฐานของการคำนวณ CFD ทำให้สามารถจัดการทางคณิตศาสตร์กับ **เทนเซอร์อันดับสอง** ได้อย่างมีประสิทธิภาพ ซึ่งจำเป็นสำหรับการขนส่งโมเมนตัม การวิเคราะห์ความเค้น และการแปลงฟิลด์

คลาสเทนเซอร์ใช้ประโยชน์จาก **Expression Templates** และ **Template Metaprogramming** เพื่อให้ได้ประสิทธิภาพสูงในขณะเดียวกันก็รักษาความชัดเจนทางคณิตศาสตร์

```mermaid
flowchart LR
%% Classes
classDef explicit fill:#ffccbc,stroke:#d84315,stroke-width:2px,color:#000
classDef implicit fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
subgraph Inputs[" Operands "]
    T["เทนเซอร์ T"]:::explicit
    V1["เวกเตอร์ A"]:::explicit
    V2["เวกเตอร์ B"]:::explicit
end

subgraph Results[" Result Types "]
    V["ผลลัพธ์เวกเตอร์"]:::implicit
    S["ผลลัพธ์สเกลาร์"]:::implicit
    T_Res["ผลลัพธ์เทนเซอร์"]:::implicit
end

T -->|"& dot"| V
T -->|"&& double dot"| S
V1 -->|"* outer"| T_Res
V2 -->|"* outer"| T_Res
```

> **Figure 1:** แผนภาพแสดงการทำงานของตัวดำเนินการเทนเซอร์ เช่น ผลคูณจุด (dot), ผลคูณจุดคู่ (double dot), และผลคูณภายนอก (outer product) ซึ่งใช้ในการเชื่อมโยงและแปลงข้อมูลระหว่างเวกเตอร์และเทนเซอร์

---

## 1. การคำนวณพื้นฐาน (Basic Arithmetic)

การดำเนินการทางคณิตศาสตร์พื้นฐานบนเทนเซอร์เป็นแบบ **Component-wise** (ทำทีละองค์ประกอบ) ซึ่งสะท้อนถึงนิยามทางคณิตศาสตร์ของพีชคณิตเทนเซอร์

### OpenFOAM Code Implementation

```cpp
// Create tensor objects with 9 components in order: xx, xy, xz, yx, yy, yz, zx, zy, zz
tensor A(1, 2, 3, 4, 5, 6, 7, 8, 9);
tensor B(9, 8, 7, 6, 5, 4, 3, 2, 1);

// Component-wise addition: C_ij = A_ij + B_ij
// Results: tensor(10, 10, 10, 10, 10, 10, 10, 10, 10)
tensor C = A + B;

// Component-wise subtraction: D_ij = A_ij - B_ij
// Results: tensor(-8, -6, -4, -2, 0, 2, 4, 6, 8)
tensor D = A - B;

// Scalar multiplication: E_ij = α·A_ij
// Results: tensor(2.5, 5, 7.5, 10, 12.5, 15, 17.5, 20, 22.5)
tensor E = 2.5 * A;
```

> **📂 แหล่งที่มา (Source):** `.applications/test/tensor/Test-tensor.C`
>
> **คำอธิบาย:**
> - **การสร้างเทนเซอร์:** ใช้ constructor ที่รับค่า components 9 ค่าตามลำดับ (xx, xy, xz, yx, yy, yz, zx, zy, zz)
> - **การบวกและลบ:** ดำเนินการแบบ component-wise ตรงตามนิยามพีชคณิตเชิงเส้น
> - **การคูณสเกลาร์:** คูณค่าสเกลาร์เข้ากับทุก component ของเทนเซอร์
>
> **หลักการสำคัญ:**
> - การดำเนินการเหล่านี้ถูก implement โดยใช้ **Expression Templates** ที่สร้าง lazy evaluation trees เพื่อประสิทธิภาพสูงสุด

---

## 2. ผลคูณภายในและภายนอก (Inner and Outer Products)

ผลคูณในแคลคูลัสเทนเซอร์มีการ **ลดอันดับ (Contraction)** ในระดับที่แตกต่างกัน โดยแต่ละแบบมีการตีความทางฟิสิกส์ที่เฉพาะเจาะจง:

| ตัวดำเนินการ | ชื่อการดำเนินการ | ความหมายทางคณิตศาสตร์ | ผลลัพธ์ |
|:---:|:---|:---|:---:|
| **`&`** | Single Contraction (Dot Product) | $\mathbf{T} \cdot \mathbf{v}$ หรือ $\mathbf{A} \cdot \mathbf{B}$ | **Vector** หรือ **Tensor** |
| **`&&`** | Double Contraction (Double Dot) | $\mathbf{A} : \mathbf{B} = \text{tr}(\mathbf{A} \cdot \mathbf{B}^T)$ | **Scalar** |
| **`*`** | Outer Product | $\mathbf{u} \otimes \mathbf{v}$ | **Tensor** |

### 2.1 การหดตัวหนึ่งระดับ (`&`) - Single Contraction

ตัวดำเนินการหดตัวหนึ่งระดับทำหน้าที่คูณ **Tensor-Vector** หรือ **Tensor-Tensor** โดยลด rank ลง 1 (กรณีคูณเวกเตอร์):

$$\mathbf{y} = \mathbf{T} \cdot \mathbf{v} \quad \text{โดยที่} \quad y_i = \sum_{j=1}^{3} T_{ij} v_j$$

#### ตัวอย่างโค้ด OpenFOAM
```cpp
vector v(1, 0, 0);
tensor A(1, 2, 3, 4, 5, 6, 7, 8, 9);

// Single contraction: tensor-vector multiplication
// Result vector w has components:
// w_x = 1*1 + 2*0 + 3*0 = 1
// w_y = 4*1 + 5*0 + 6*0 = 4
// w_z = 7*1 + 8*0 + 9*0 = 7
vector w = A & v;
```

> **ความสำคัญ:** ใช้ในการคำนวณแรงบนพื้นผิว (Traction vector = Stress tensor & Normal vector)

### 2.2 การหดตัวสองระดับ (`&&`) - Double Contraction

การหดตัวสองระดับ (**Scalar Product**) คำนวณผลคูณภายในแบบ **Frobenius** ซึ่งให้ค่าสเกลาร์เดียว:

$$\mathbf{A} : \mathbf{B} = \sum_{i,j=1}^{3} A_{ij} B_{ij}$$

#### ตัวอย่างโค้ด OpenFOAM
```cpp
// Double inner product
// s = sum of element-wise products
scalar s = A && B;
```

> **ความสำคัญ:** ใช้ในการคำนวณงานและพลังงาน เช่น Dissipation function $\Phi = \boldsymbol{\tau} : \nabla \mathbf{u}$

### 2.3 ผลคูณภายนอก (`*`) - Outer Product

สร้างเทนเซอร์อันดับสองจากเวกเตอร์สองตัวผ่าน **Dyadic Multiplication**:

$$\mathbf{T} = \mathbf{u} \otimes \mathbf{v} \quad \text{โดยที่} \quad T_{ij} = u_i v_j$$

#### ตัวอย่างโค้ด OpenFOAM
```cpp
vector u(1, 2, 3);
vector v(4, 5, 6);

// Outer product creates a tensor
tensor T = u * v;
```

> **ความสำคัญ:** ใช้สร้าง Reynolds Stress Tensor ($\tau_{ij} = -\rho \overline{u'_i u'_j}$)

---

## 3. ฟังก์ชันวิเคราะห์เทนเซอร์ (Tensor Analysis Functions)

ฟังก์ชันเหล่านี้คำนวณค่า **Invariants** ซึ่งเป็นคุณสมบัติที่ไม่เปลี่ยนค่าเมื่อเปลี่ยนระบบพิกัด

| ฟังก์ชัน | สูตร | คำอธิบาย |
|:---:|:---|:---|
| **`tr(T)`** | $T_{xx} + T_{yy} + T_{zz}$ | **Trace**: ผลรวมแนวทแยง (เช่น ความดัน) |
| **`det(T)`** | $\det(\mathbf{T})$ | **Determinant**: ปริมาตรสเกลลิ่ง |
| **`inv(T)`** | $\mathbf{T}^{-1}$ | **Inverse**: เมทริกซ์ผกผัน |
| **`T.T()`** | $T_{ji}$ | **Transpose**: สลับแถว-หลัก |

```cpp
tensor A(1, 2, 3, 4, 5, 6, 7, 8, 9);

tensor AT = A.T();        // Transpose
scalar trA = tr(A);       // Trace = 15
scalar detA = det(A);     // Determinant = 0 (singular)
tensor invA = inv(A);     // Inverse (if det != 0)
```

---

## 4. การดำเนินการเฉพาะใน CFD

### 4.1 Deviatoric, Symmetric, Skew

```cpp
// Deviatoric part: ตัดส่วนความดัน (isotropic) ออก เหลือแต่ shear
// dev(T) = T - 1/3*tr(T)*I
symmTensor S_dev = dev(T);

// Symmetric part: ส่วนสมมาตร (Deformation)
// symm(T) = 0.5 * (T + T^T)
symmTensor S = symm(T);

// Skew part: ส่วนไม่สมมาตร (Rotation)
// skew(T) = 0.5 * (T - T^T)
tensor Omega = skew(T);
```

> **📂 แหล่งที่มา (Source):** `.applications/test/tensor/Test-tensor.C`
>
> **การประยุกต์ใช้:**
> - **dev()**: ใช้ในกฎความหนืดของ Newton ($\tau = 2\mu \text{dev}(\mathbf{D})$)
> - **symm()**: ใช้หา Strain Rate Tensor
> - **skew()**: ใช้หา Vorticity Tensor

---

## 5. การสลายตัวของค่าลักษณะเฉพาะ (Eigenvalue Decomposition)

เครื่องมือสำคัญสำหรับวิเคราะห์ความเค้นหลัก (Principal Stresses) และทิศทางหลัก (Principal Directions)

### หลักการและการนำไปใช้

```cpp
// Create symmetric stress tensor
symmTensor stress(100, 50, 30, 80, 40, 60);

// Eigenvalues = Principal Stresses (sorted desc)
vector eigVals = eigenValues(stress);
scalar sigma1 = eigVals.x(); // Max tension
scalar sigma3 = eigVals.z(); // Max compression

// Eigenvectors = Principal Directions
tensor eigVecs = eigenVectors(stress);
vector dir1 = eigVecs.col(0); // Direction of sigma1
```

> **การใช้งาน:** ทำนายการล้มเหลวของวัสดุ (Failure Prediction) โดยตรวจสอบว่าความเค้นหลักเกินขีดจำกัดหรือไม่

---

## 6. แคลคูลัสเทนเซอร์ (Tensor Calculus)

การดำเนินการเชิงอนุพันธ์บนฟิลด์เทนเซอร์:

### 6.1 Gradient (`fvc::grad`)
สร้างเทนเซอร์อันดับ 3 (Rank-3) จากเทนเซอร์อันดับ 2:
$$(\nabla \mathbf{T})_{ijk} = \frac{\partial T_{ij}}{\partial x_k}$$
```cpp
volTensorTensorField gradT = fvc::grad(T);
```

### 6.2 Divergence (`fvc::div`)
ลด rank ลง 1 (Tensor $\to$ Vector):
$$(\nabla \cdot \mathbf{T})_i = \sum_j \frac{\partial T_{ij}}{\partial x_j}$$
```cpp
volVectorField DivT = fvc::div(T); // แรงต่อหน่วยปริมาตร
```

---

## 7. การเพิ่มประสิทธิภาพ (Performance Optimization)

OpenFOAM ใช้เทคนิคขั้นสูงเพื่อให้การคำนวณเร็วที่สุด:

| เทคนิค | คำอธิบาย | ประโยชน์ |
|:---|:---|:---|
| **Expression Templates** | Lazy evaluation (ไม่คำนวณจนกว่าจะจำเป็น) | ลดการสร้างตัวแปรชั่วคราว |
| **Loop Unrolling** | เขียนลูปออกมาเป็นคำสั่งเรียงกัน (สำหรับ 3x3) | ลด overhead ของลูป |
| **SIMD Vectorization** | ใช้คำสั่ง CPU แบบขนานระดับคำสั่ง | คำนวณเร็วขึ้น 2-4 เท่า |
| **Memory Alignment** | จัดข้อมูลให้ตรงล็อกหน่วยความจำ | อ่าน/เขียนข้อมูลเร็วขึ้น |

---

## สรุป

การเข้าใจตัวดำเนินการเทนเซอร์ทำให้คุณสามารถ:
1.  **แปลงสมการฟิสิกส์** เป็นโค้ด OpenFOAM ได้โดยตรง
2.  **วิเคราะห์ผลลัพธ์** ผ่าน Invariants (Trace, Det) และ Eigenvalues
3.  **เขียน Model ใหม่** ที่ซับซ้อนขึ้น เช่น Non-Newtonian หรือ Turbulence Models
4.  **เพิ่มประสิทธิภาพ** โค้ดผ่านความเข้าใจเรื่อง Contraction และ Memory Layout