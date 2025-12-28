# การตั้งค่าเคส interFoam (Setting Up interFoam)

> [!TIP] ทำไมการตั้งค่า interFoam ถึงสำคัญ?
> การตั้งค่าเคส **interFoam** มีความละเอียดอ่อนกว่าเคส Single-phase ทั่วไป โดยเฉพาะเรื่องของ **เงื่อนไขขอบเขต (Boundary Conditions)** และ **การกำหนดค่าเริ่มต้น (Initial Fields)** บทนี้จะพาคุณไปดูจุดสำคัญที่ "ห้ามพลาด"
>
> ในบทนี้คุณจะได้เรียนรู้:
> - การกำหนดคุณสมบัติทางกายภาพของสองเฟส (Viscosity, Density, Surface Tension)
> - การสร้าง "เฟสเริ่มต้น" (Initial Condition) ด้วย `setFields`
> - ความแตกต่างระหว่าง `p` และ `p_rgh` (สำคัญมาก!)
> - การเลือก Boundary Condition ที่เสถียรสำหรับกรณีเปิดสู่บรรยากาศ
> - การเลือก Numerical Schemes ที่เหมาะกับ VOF
>
> หากตั้งค่าผิด ได้ผลลัพธ์คือ **ผิวน้ำกระจาย (Spurious)**, **การคำนวณ Diverge**, หรือ **น้ำไหลผิดธรรมชาติ**

---

## 1. การกำหนดคุณสมบัติกายภาพ (`transportProperties`)

> [!NOTE] **📂 OpenFOAM Context**
> ส่วนนี้เกี่ยวข้องกับ **Domain A: Physics & Fields**
> - **ไฟล์ที่เกี่ยวข้อง**: `constant/transportProperties`
> - **คำสั่ง/คีย์เวิร์ดที่ใช้**: `phases`, `transportModel`, `nu` (Kinematic Viscosity), `rho` (Density), `sigma` (Surface Tension)
> - **ผลต่อการจำลอง**: ค่าที่กำหนดที่นี่จะถูกเรียกใช้โดย Solver โดยตรง เพื่อคำนวณแรงตึงผิวและอัตราส่วนความหนาแน่นของเฟส
> - **ความสำคัญ**: ถ้ากำหนดผิด อาจทำให้ **หยดน้ำไม่กลม**, **ผิวน้ำสั่นไหว**, หรือ **Time Step ต้องเล็กมากเกินไป**

ไฟล์: `constant/transportProperties`

นี่คือที่ที่เรากำหนดว่า "น้ำคือน้ำ" และ "อากาศคืออากาศ" รวมถึงแรงตึงผิวและคุณสมบัติอื่นๆ

```cpp
phases (water air);

// 1. กำหนด เฟสที่ 1 (ของเหลว)
water
{
    transportModel  Newtonian;
    nu              1e-06;    // Kinematic Viscosity (m^2/s) [Water @ 20C]
    rho             1000;     // Density (kg/m^3)
}

// 2. กำหนด เฟสที่ 2 (ก๊าซ)
air
{
    transportModel  Newtonian;
    nu              1.48e-05; // [Air @ 20C]
    rho             1;
}

// 3. แรงตึงผิว (สำคัญมาก!)
sigma           0.07;         // Surface Tension (N/m) between phases
```

> [!TIP]
> **ลำดับการเขียนสำคัญมาก!** ถ้าเขียน `phases (water air);` แสดงว่า OpenFOAM จะมอง `water` เป็น phase1 (alpha=1) และ `air` เป็น phase2 (alpha=0) เสมอ

---

## 2. การกำหนดค่าเริ่มต้นด้วย `setFields`

> [!NOTE] **📂 OpenFOAM Context**
> ส่วนนี้เกี่ยวข้องกับ **Domain C: Simulation Control & Domain A: Initial Fields**
> - **ไฟล์ที่เกี่ยวข้อง**: `system/setFieldsDict` และ `0/alpha.water`
> - **คำสั่ง/คีย์เวิร์ดที่ใช้**: `defaultFieldValues`, `boxToCell`, `volScalarFieldValue`, `fieldValues`
> - **Utility ที่ใช้**: `setFields` (เป็น Pre-processing Utility ที่ทำงานก่อนเรัน Solver)
> - **ผลต่อการจำลอง**: การกำหนดค่าเริ่มต้นที่ผิด หรือผิวน้ำไม่ชัดเจน อาจทำให้เกิด **Spurious Currents** (กระแสน้ำวิ่งไปมาไม่หยุด) ในช่วงแรกของการจำลอง

ไฟล์: `system/setFieldsDict`

ก่อนรันเคส เราต้อง "เทน้ำ" ลงในโดเมนก่อน วิธีมาตรฐานคือใช้ `setFields` utility:

```cpp
defaultFieldValues
(
    volScalarFieldValue alpha.water 0 // ถมดำทั้งโดเมนเป็น "อากาศ" ก่อน
);

regions
(
    // สร้างก้อนน้ำรูปสี่เหลี่ยม (Dam Break)
    boxToCell
    {
        box (0 0 0) (0.146 0.292 0.1); // พิกัด (minX minY minZ) (maxX maxY maxZ)
        fieldValues
        (
            volScalarFieldValue alpha.water 1 // เปลี่ยนค่าในกล่องนี้เป็น "น้ำ"
        );
    }
);
```

**คำสั่งรัน:**
```bash
setFields
```

---

## 3. ปริศนา `p_rgh` (Why not just p?)

> [!NOTE] **📂 OpenFOAM Context**
> ส่วนนี้เกี่ยวข้องกับ **Domain A: Physics & Fields (Boundary Conditions)**
> - **ไฟล์ที่เกี่ยวข้อง**: `0/p_rgh`, `0/p`
> - **คำสั่ง/คีย์เวิร์ดที่ใช้**: `p_rgh` (Reduced Pressure - ความดันลดรูป), `p` (Total Pressure), `totalPressure` BC
> - **ความสำคัญ**: **interFoam แก้ p_rgh ไม่ใช่ p!** ถ้ากำหนด Boundary Condition ให้ `p` โดยตรงจะเกิด Error
> - **การคำนวณ**: $p_{rgh} = p - \rho \mathbf{g} \cdot \mathbf{x}$ (เทอม $\rho \mathbf{g} \cdot \mathbf{x}$ ถูกกำหนดใน `constant/g`)

ใน interFoam เราจะไม่แก้ `p` (Total Pressure) โดยตรง แต่จะแก้ **`p_rgh`** แทน:

$$ p_{rgh} = p - \rho \mathbf{g} \cdot \mathbf{x} $$

**ทำไมถึงต้องใช้ `p_rgh`?**
- แรงดันของของเหลวจะเพิ่มขึ้นตามความลึก (Hydrostatic Pressure: $\rho g h$)
- ถ้าเรากำหนด BC เป็นค่าคงที่ (เช่น `p = 0`) ที่ทางออก น้ำจะไหลออกผิดธรรมชาติเพราะ Pressure ไม่สมดุลกับความลึก
- การใช้ `p_rgh` ช่วยตัดเทอมความสูงออกไป ทำให้เราสามารถกำหนด `p_rgh = 0` ที่ทางออกได้ง่ายๆ โดยไม่ต้องเขียนฟังก์ชันความลึกให้ยุ่งยาก

---

## 4. สูตรสำเร็จของเงื่อนไขขอบเขต (The BC "Combo")

> [!NOTE] **📂 OpenFOAM Context**
> ส่วนนี้เกี่ยวข้องกับ **Domain A: Physics & Fields (Boundary Conditions)**
> - **ไฟล์ที่เกี่ยวข้อง**: `0/alpha.water`, `0/U`, `0/p_rgh`, `0/p`
> - **Boundary Condition Types**: `inletOutlet`, `pressureInletOutletVelocity`, `totalPressure`, `fixedValue`, `slip`, `constantAlphaContactAngle`
> - **ความสำคัญ**: การเลือก BC ผิดที่ Patch เปิดสู่บรรยากาศ อาจทำให้เกิด **Reflected Waves** (คลื่นสะท้อน), **Backflow** (น้ำไหลย้อน), หรือ **Mass Loss**
> - **Best Practice**: ต้องใช้ "Combo" ที่ตรงกันข้ามระหว่าง `alpha`, `U`, และ `p_rgh` เสมอ

สำหรับ VOF ที่มีการไหลเข้า-ออก หรือเปิดสู่บรรยากาศ (Atmosphere) การเลือก BC ผิดชีวิตเปลี่ยน! นี่คือคอมโบยอดฮิตที่เสถียรที่สุด:

### กรณีเปิดสู่บรรยากาศ (Atmosphere / Top Patch)

| ตัวแปร | Type | ค่า | เหตุผล |
| :--- | :--- | :--- | :--- |
| **alpha.water** | `inletOutlet` | `inletValue uniform 0` | ให้อากาศไหลเข้าได้ แต่น้ำไหลออกได้อย่างเดียว (ป้องกันน้ำไหลย้อนจากฟ้า) |
| **U** | `pressureInletOutletVelocity` | `value uniform (0 0 0)` | ยอมให้ไหลเข้าออกตามความดัน แต่ถ้าไหลเข้าให้ใช้ความเร็วเป็น 0 (หรือตาม Flux) |
| **p_rgh** | `totalPressure` | `p0 uniform 0` | กำหนดความดันรวมคงที่ เหมาะสำหรับเปิดสู่บรรยากาศ |

### กรณีผนังลื่น (Slippery Wall) vs ผนังเกาะ (No-slip)

*   **No-slip:** น้ำเกาะผนัง (`U = fixedValue uniform (0 0 0)`)
*   **Slip:** น้ำไหลลื่นไม่ติดผนัง (`U = slip`) หรือใช้กับผนังสมมาตร

### มุมสัมผัส (Contact Angle)
สำหรับ `alpha.water` ที่ผนัง เราสามารถกำหนดความ "ชอบน้ำ" ของวัสดุได้:
```cpp
wall
{
    type            constantAlphaContactAngle;
    theta0          90;     // 90 = Neutral
                            // < 90 = Hydrophilic (น้ำชอบเกาะ)
                            // > 90 = Hydrophobic (น้ำกลิ้งหนี - ใบบัว)
    limit           gradient;
    value           uniform 0;
}
```

---

## 5. การตั้งค่า `fvSchemes`

> [!NOTE] **📂 OpenFOAM Context**
> ส่วนนี้เกี่ยวข้องกับ **Domain B: Numerics & Linear Algebra**
> - **ไฟล์ที่เกี่ยวข้อง**: `system/fvSchemes`
> - **คำสั่ง/คีย์เวิร์ดที่ใช้**: `divSchemes`, `gradSchemes`, `laplacianSchemes`
> - **Schemes สำคัญ**: `Gauss vanLeer`, `Gauss interfaceCompression`, `Gauss linear`, `Gauss upwind`
> - **ผลต่อการจำลอง**: การเลือก Scheme ผิด โดยเฉพาะสำหรับ `alpha` จะทำให้ **ผิวน้ำกระจาย (Interface Smearing)**, **Spurious Currents**, หรือ **การคำนวณ Diverge**
> - **คำเตือน**: ห้ามใช้ `upwind` กับ `alpha.water` หากต้องการผิวน้ำที่คมชัด!

สำหรับ VOF การเลือก Scheme ใน `system/fvSchemes` ส่งผลต่อรูปร่างของผิวโดยตรง:

```cpp
divSchemes
{
    // สำคัญมากสำหรับ Alpha! ต้องใช้ VanLeer หรือ interfaceCompression
    div(rhoPhi,alpha.water)     Gauss vanLeer;
    div(phi,alpha.water)        Gauss vanLeer;
    
    // เทอมบีบอัด (Compression Term)
    div(phirb,alpha)            Gauss linear;
}
```

> **Note:** การใช้ Upwind กับ Alpha จะทำให้ผิวเบลอมาก ห้ามใช้เด็ดขาด! แนะนำ `vanLeer`, `superBee`, หรือ `interfaceCompression`

---

## 🧠 Concept Check: ทดสอบความเข้าใจ

1.  **ถ้าเราจะจำลอง "หยดน้ำกลิ้งบนใบบัว" เราต้องตั้งค่า Contact Angle เท่าไหร่?**
    <details>
    <summary>เฉลย</summary>
    ต้องตั้งค่า `theta0` ให้มากกว่า 90 องศา (Hydrophobic) เช่น 150 องศา เพื่อให้หยดน้ำคงรูปร่างเป็นก้อนกลมและกลิ้งได้ง่าย
    </details>

2.  **ทำไมเราต้องตั้ง `alpha.water` ที่ขอบบรรยากาศเป็น `inletOutlet` แทนที่จะเป็น `zeroGradient`?**
    <details>
    <summary>เฉลย</summary>
    เพราะถ้าเกิดความดันต่ำในโดเมน อากาศภายนอกควรจะสามารถไหลเข้ามาเติมเต็มได้ (Inflow) ซึ่ง `inletOutlet` ยอมให้อากาศ ($\alpha=0$) ไหลเข้า แต่ `zeroGradient` จะบังคับให้ค่าที่ขอบเท่ากับค่าข้างใน ซึ่งอาจดูด "น้ำ" กลับเข้ามาจากอากาศได้ (Unphysical)
    </details>

3.  **ทำไมต้องใช้ `p_rgh` แทน `p` ใน interFoam?**
    <details>
    <summary>เฉลย</summary>
    เพื่อแยกความดันเนื่องจากความสูงของของเหลว (Hydrostatic Pressure $\rho gh$) ออกจากการคำนวณ ทำให้การกำหนด Boundary Condition ง่ายขึ้น โดยเฉพาะที่ทางออกหรือผิวน้ำที่เราต้องการระบุแค่ความดันสถิตย์อ้างอิง (เช่น 0) โดยไม่ต้องกังวลเรื่องระดับความลึก
    </details>

---

## 📖 เอกสารที่เกี่ยวข้อง

*   **บทก่อนหน้า**: [02_Interface_Compression.md](02_Interface_Compression.md)
*   **บทถัดไป**: [04_Adaptive_Time_Stepping.md](04_Adaptive_Time_Stepping.md)