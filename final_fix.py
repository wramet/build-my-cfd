
import os

file_path = 'lecture/2025-12-27_OpenFOAM_Discretization_and_Configuration.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Fix 2.2
start_22 = text.find('### 2.2 `divSchemes`')
end_22 = text.find('### 2.3 `laplacianSchemes`')
if start_22 != -1 and end_22 != -1:
    new_22 = """### 2.2 `divSchemes` (Divergence / Convection)
*   **ฟิสิกส์:** จัดการพจน์การพาหรือการไหล ($\nabla \cdot (\rho \mathbf{u} \phi)$)
*   **ความท้าทาย:** ทิศทางลม ข้อมูลไหลจากต้นน้ำไปปลายน้า
*   **Schemes ยอดนิยม:**
    *   **`Gauss linear` (Central Differencing):** หาค่าเฉลี่ยตรงกลาง แม่นยำสูง (2nd order) แต่อาจไม่เสถียร (ค่ากระโดด) ถ้าการไหลรุนแรง
    *   **`Gauss upwind`:** เอาค่าจากต้นน้ำมาใช้เลย เสถียรมาก แต่ค่าจะเบลอๆ (Numerical Diffusion) แม่นยำต่ำ (1st order)
    *   **`Gauss linearUpwind` / `limitedLinear`:** ลูกผสม พยายามจะแม่นแบบ Linear แต่ถ้าค่าเริ่มแกว่งจะปรับเป็น Upwind เพื่อความชัวร์

"""
    text = text[:start_22] + new_22 + text[end_22:]

# Fix 2.3 & 2.4
start_23 = text.find('### 2.3 `laplacianSchemes`')
end_24 = text.find('### 2.5 Flux Field')
if start_23 != -1 and end_24 != -1:
    new_23_24 = """### 2.3 `laplacianSchemes` (Laplacian / Diffusion)
*   **ฟิสิกส์:** จัดการพจน์การแพร่หรือการกระจายตัว ($\nabla \cdot (\Gamma \nabla \phi)$)
*   **ความท้าทาย:** การคำนวณ **ความชัน (Gradient)** ที่หน้าสัมผัส ($\nabla \phi \cdot \mathbf{n}$)
*   **ปัญหาคุณภาพ Mesh (Non-Orthogonality):**
    *   ใน Mesh สี่เหลี่ยมเป๊ะ เส้นเชื่อมระหว่างเซลล์ ($\mathbf{d}$) จะตั้งฉากกับหน้าสัมผัส ($\mathbf{n}$)
    *   ใน Mesh จริง เส้นมักจะเบี้ยว ไม่ตั้งฉาก การคำนวณความชันตรงๆ จะผิด
*   **การแก้ไข (Correction):**
    *   **`Gauss linear uncorrected`:** ไม่แก้ (สมมติว่า Mesh ดีเลิศ) เร็วแต่ผิดถ้า Mesh เบี้ยว
    *   **`Gauss linear corrected`:** เพิ่มพจน์แก้ไขเพื่อชดเชยความเบี้ยว **(แนะนำให้ใช้เป็นมาตรฐาน)**
    *   **`Gauss linear limited`:** ถ้า Mesh เบี้ยวหนักมาก (> 70-80 องศา) การแก้เต็มสูบอาจทำให้ระเบิด ต้องแก้แบบยั้งๆ (Limited) เพื่อแลกความแม่นกับความเสถียร

---

### 2.4 รายละเอียดเชิงลึก: Non-Orthogonality Correction

**ปัญหา:** Mesh จริงมักไม่สวยงามเป็นสี่เหลี่ยมผืนผ้า เส้นเชื่อมระหว่างเซลล์ ($\mathbf{d}$) มักจะไม่ตั้งฉากกับหน้าสัมผัส ($\mathbf{n}$)

**Gradient ที่หน้าสัมผัส:**
เพื่อคำนวณ $\nabla \phi_f \cdot \mathbf{n}$ เราต้องการ gradient ที่หน้าสัมผัส แต่เรามีค่า $\phi$ ที่จุดกึ่งกลางเซลล์เท่านั้น

**วิธีการคำนวณ:**
$$\nabla \phi_f \cdot \mathbf{n} = \underbrace{\frac{\phi_N - \phi_P}{|\mathbf{d}|}}_{{\text{Orthogonal part}}} + \underbrace{\text{correction term}}_{{\text{Non-orthogonal correction}}}
$$

- $\phi_P$: ค่าที่เซลล์ปัจจุบัน (Owner)
- $\phi_N$: ค่าที่เซลล์ข้างเคียง (Neighbor)
- $\mathbf{d}$: เวกเตอร์เชื่อมระหว่างเซลล์ ($P \rightarrow N$)

**การแก้ไข 3 ระดับ:**

1.  **`uncorrected`:**
    - ใช้เฉพาะ orthogonal part: $\frac{\phi_N - \phi_P}{|\mathbf{d}|}$
    - **ข้อดี:** เร็ว
    - **ข้อเสีย:** ผิดมากถ้า mesh เบี้ยว
    - **เหมาะกับ:** High-quality orthogonal mesh (เช่น blockMesh)

2.  **`corrected`:**
    - เพิ่มพจน์แก้ไข: $\nabla \phi_f = \overline{\nabla \phi} + (\nabla \phi_f - \overline{\nabla \phi}) \cdot \mathbf{k}$
    - **ข้อดี:** แม่นยำขึ้นมากสำหรับ non-orthogonal mesh
    - **ข้อเสีย:** ช้าลง ต้อง iterate หลายรอบ (`nNonOrthogonalCorrectors`)
    - **เหมาะกับ:** snappyHexMesh, โดเมนซับซ้อน (ส่วนใหญ่ใช้ตัวนี้)

3.  **`limited`:**
    - แก้แบบยั้งๆ (limiter) เพื่อป้องกันค่ากระโดก
    - **ข้อดี:** เสถียรมาก แม้ mesh เบี้ยวหนัก (> 70°)
    - **ข้อเสีย:** แม่นยำน้อยกว่า `corrected`
    - **เหมาะกับ:** กรณีที่ `corrected` ทำให้ simulation ระเบิด

"""
    text = text[:start_23] + new_23_24 + text[end_24:]

# Fix 3.3
start_33 = text.find('### 3.3 โครงสร้างเมทริกซ์')
end_33 = text.find('### 3.4 Tolerance')
if start_33 != -1 and end_33 != -1:
    new_33 = """### 3.3 โครงสร้างเมทริกซ์ $Ax = b$ ใน FVM

เมื่อเราใช้ `fvm::` เพื่อ discretize สมการ OpenFOAM จะสร้าง **Sparse Matrix** ($A$) และ **Source vector** ($b$) ขึ้นมา:

$$ \begin{bmatrix} a_{1,1} & a_{1,2} & 0 & \cdots & a_{1,n} \\ a_{2,1} & a_{2,2} & a_{2,3} & \cdots & 0 \\ 0 & a_{3,2} & a_{3,3} & \cdots & 0 \\ \vdots & \vdots & \vdots & \ddots & \vdots \\ a_{n,1} & 0 & 0 & \cdots & a_{n,n} \end{bmatrix} \begin{bmatrix} x_1 \\ x_2 \\ x_3 \\ \vdots \\ x_n \end{bmatrix} = \begin{bmatrix} b_1 \\ b_2 \\ b_3 \\ \vdots \\ b_n \end{bmatrix} $$

**คุณสมบัติของเมทริกซ์ FVM:**

1.  **Sparse (เบาบาง):** เก็บเฉพาะค่าที่ไม่ใช่ศูนย์ (Neighbor cells เท่านั้น)
    - ปกติแต่ละแถวมี 7-27 ค่าที่ไม่ใช่ศูนย์ (ขึ้นกับ mesh dimensionality)
    - ช่วยลดหน่วยความจำและเวลาคำนวณ

2.  **Diagonally Dominant:** ค่า diagonal ($a_{P,P}$) มีขนาดใหญ่กว่าผลรวมของ off-diagonal
    - สำคัญมากต่อ **convergence** ของ iterative solvers
    - ยิ่ง $\Delta t$ เล็ก → diagonal dominance สูง → converge ง่ายขึ้น

3.  **Asymmetric:** สำหรับ convection-dominated flows ($\mathbf{u} \cdot \nabla \mathbf{u}$ เป็น non-linear)
    - ต้องใช้ solvers สำหรับ non-symmetric matrices (เช่น `PBiCGStab`)
    - สำหรับ pressure equation (symmetric) ใช้ `PCG`

**ตัวอย่างการประกอบเมทริกซ์:**
```cpp
// สมการ: ∂(ρU)/∂t + ∇·(ρUU) = -∇p + μ∇²U
// Discretized ด้วย fvm:
a_P * U_P + \sum a_N * U_N = b_P

// โดยที่:
// a_P = มวลของเซลล์ / Δt + \sum(flux out)  (Diagonal coefficient)
// a_N = -flux into cell from neighbor    (Neighbor coefficient)
// b_P = -∇p + source terms              (Source vector)
```
"""
    text = text[:start_33] + new_33 + text[end_33:]

# Fix section 4
start_4 = text.find('## 4. ตัวอย่างการแปลงร่าง: Time Derivative')
end_4 = text.find('## 5. การเขียนโค้ด: `createFields.H`')
if start_4 != -1 and end_4 != -1:
    new_4 = """## 4. ตัวอย่างการแปลงร่าง: Time Derivative
จาก Calculus ($\frac{\partial}{\partial t}$) กลายเป็น Algebra ได้อย่างไร?

1.  **Calculus:** $\frac{\partial \rho \phi}{\partial t}$
2.  **Integration:** อินทิเกรตครอบคลุมปริมาตรเซลล์ $V_P$
3.  **Discretization (Euler Scheme):** เปลี่ยนอนุพันธ์เป็นผลต่าง
    $$ \frac{(\rho \phi)_P^{\text{ใหม่}} - (\rho \phi)_P^{\text{เก่า}}}{\Delta t} V_P $$
4.  **Algebra ($Ax=b$):**
    *   เทอม **ใหม่** ($P^{\text{ใหม่}}$) ย้ายไปอยู่ฝั่งซ้าย ใส่ใน Matrix ($A$)
    *   เทอม **เก่า** ($P^{\text{เก่า}}$) ย้ายไปอยู่ฝั่งขวา เป็น Source ($b$)
    *   *สังเกต:* ยิ่ง $\Delta t$ เล็ก ตัวหารยิ่งใหญ่ ทำให้ Matrix $A$ มีค่า Diagonal สูง ส่งผลให้แก้สมการง่ายและเสถียร

"""
    text = text[:start_4] + new_4 + text[end_4:]

# Final touch: fix the \phi bug in code block assignment
text = text.replace('solve pressure equation\phi = fvc::flux(U);', 'solve pressure equation\n    phi = fvc::flux(U);')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)
