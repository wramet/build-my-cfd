# แนวคิดพื้นฐาน VOF (The Volume of Fluid Concept)

**Volume of Fluid (VOF)** คือเทคนิคการจำลองการไหลแบบหลายเฟส (Multiphase Flow) ที่เป็น "มาตรฐานทองคำ" สำหรับการแก้ปัญหา **Free Surface Flows** (การไหลที่มีรอยต่อชัดเจน)

---

## 💡 แนวคิดเปรียบเทียบ (Analogy): ภาพแบบ Pixel vs Vector

ในการระบุตำแหน่งรอยต่อ (Interface) มี 2 แนวคิดหลัก:
1.  **Explicit Tracking (Vector)**: ลากเส้นตามผิว (เหมือนเอาหนังยางไปวางบนผิวน้ำ) ข้อดีคือคมชัด แต่ข้อเสียคือถ้าผิวขาดหรือรวมกัน (เช่น หยดน้ำรวมตัว) จะคำนวณยากมาก
2.  **VOF (Raster/Pixel)**: ไม่ได้เก็บเส้นผิว แต่เก็บ "ค่าสี" ในแต่ละ Cell ว่ามีน้ำอยู่กี่เปอร์เซ็นต์

```mermaid
graph LR
    subgraph Cell_Representation
        C1[Alpha = 1.0<br>Water]
        C2[Alpha = 0.5<br>Interface]
        C3[Alpha = 0.0<br>Air]
    end
    
    C1 --- C2 --- C3
    
    style C1 fill:#3498db,stroke:#333,stroke-width:2px
    style C2 fill:#85c1e9,stroke:#333,stroke-width:2px
    style C3 fill:#fff,stroke:#333,stroke-width:2px
```

## 1. ตัวแปร Phase Fraction (\alpha$)

ใน OpenFOAM เราใช้ตัวแปร `alpha.water` (\alpha$) เป็นตัวบ่งชี้สถานะ:

| ค่า \alpha$ | ความหมาย | สภาพใน Cell |
| :---: | :--- | :--- |
| **1.0** | Full Phase 1 | มีแต่น้ำเต็มเซลล์ |
| **0.0** | Full Phase 2 | มีแต่อากาศเต็มเซลล์ |
| **0 < \alpha$ < 1** | Interface | มีทั้งสองเฟสผสมกัน (รอยต่อ) |

## 2. คุณสมบัติ Mixture (Mixture Properties)

OpenFOAM มองว่าทั้งโดเมนคือของไหลชนิดเดียว (Single Fluid) ที่มีความหนาแน่นและความหนืด "เฉลี่ย" ตามสัดส่วนปริมาตร:

$$ \rho = \alpha \rho_1 + (1 - \alpha) \rho_2 $$
$$ \mu = \alpha \mu_1 + (1 - \alpha) \mu_2 $$

```mermaid
graph TD
    A[Alpha Field] --> RhoCalc[Calculate Mixture Density]
    A --> MuCalc[Calculate Mixture Viscosity]
    RhoCalc --> Momentum[Solve Navier-Stokes Equation]
    MuCalc --> Momentum
    Momentum --> NewU[New Velocity Field]
    NewU --> Advection[Advect Alpha to next step]
```

## 3. สมการการขนส่งผิว (The Interface Transport Equation)

รอยต่อเคลื่อนที่ไปตามความเร็วของไหล (\mathbf{U}$) โดยใช้สมการ Advection:

$$ \frac{\partial \alpha}{\partial t} + \nabla \cdot (\mathbf{U} \alpha) = 0 $$

### ปัญหา Numerical Diffusion (ผิวเบลอ)
ในการคำนวณจริง สมการนี้มักทำให้หน้าสัมผัส "เบลอ" ออกไป (Diffusion) จากที่ควรจะเป็นขั้นบันได (Step function) กลายเป็นทางลาด (Slope) ซึ่งจะทำให้แรงตึงผิวและฟิสิกส์ผิดเพี้ยน

> [!WARNING]
> หากผิวเบลอเกิน 3-4 เซลล์ แรงตึงผิว (Surface Tension) จะคำนวณผิดพลาดอย่างรุนแรง เพราะรัศมีความโค้ง (\kappa$) จะเพี้ยนไป

## 4. การแสดงผลใน ParaView (Visualization)

เนื่องจากเราไม่มี "เส้นผิว" จริงๆ เราจึงใช้เทคนิค **Isosurface** เพื่อสร้างผิวจำลองขึ้นมา

```mermaid
graph TD
    Data[Alpha Field Data<br>0.0 ... 1.0] --> Contour[Filter: Contour / Isosurface]
    Contour --> Value[Set Value = 0.5]
    Value --> Surface[Visualized Free Surface]
```

**ขั้นตอนใน ParaView:**
1.  Apply ข้อมูล และเลือกตัวแปร `alpha.water`
2.  ใช้ Filter **Contour**
3.  ใน Isosurfaces set ค่าเป็น `0.5`
4.  คุณจะได้พื้นผิวสีขาวที่ตัดแบ่งระหว่างน้ำและอากาศพอดี

## 🔑 สรุปหัวใจ VOF
*   **Mass Conservation:** VOF มีจุดเด่นคือรักษามวลได้ดีเยี่ยม (ของเหลวไม่ค่อยหาย)
*   **Topology Change:** จัดการการแตกตัว/รวมตัวของหยดน้ำและฟองอากาศได้อัตโนมัติ
*   **Computational Cost:** ประหยัดกว่าวิธีติดตามผิวแบบอื่นๆ แต่ต้องการ Mesh ที่ละเอียดบริเวณผิวสัมผัส