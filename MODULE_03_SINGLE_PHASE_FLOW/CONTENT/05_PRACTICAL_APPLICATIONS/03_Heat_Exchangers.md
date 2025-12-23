# เครื่องแลกเปลี่ยนความร้อน (Heat Exchangers)

## 📖 บทนำ (Introduction)

การจำลองเครื่องแลกเปลี่ยนความร้อนเป็นงานที่มีความซับซ้อนเนื่องจากเกี่ยวข้องกับของไหลสองกระแสและการนำความร้อนผ่านตัวนำ (ผนังท่อ) เราใช้แนวทาง **Conjugate Heat Transfer (CHT)** เพื่อจำลองการโต้ตอบนี้

---

## 🔍 1. ตัวชี้วัดประสิทธิภาพ (Performance Metrics)

### 1.1 ประสิทธิภาพ (Effectiveness, ε)
$$\varepsilon = \frac{q_{actual}}{q_{max}}$$
โดยที่ $q_{max} = C_{min} (T_{h,in} - T_{c,in})$

### 1.2 จำนวนหน่วยถ่ายเทความร้อน (NTU)
$$NTU = \frac{U A}{C_{min}}$$
พารามิเตอร์นี้ช่วยระบุขนาดของเครื่องแลกเปลี่ยนความร้อนที่ต้องการ

---

## 🛠️ 2. กลยุทธ์การจำลองใน OpenFOAM

### 2.1 Multi-Region Approach
ใช้ `chtMultiRegionFoam` เพื่อแก้สมการในแต่ละภูมิภาคแยกกัน:
- **Fluid Regions**: ร้อนและเย็น
- **Solid Region**: ผนังท่อหรือแผ่นกั้น

### 2.2 แบบจำลองสื่อพรุน (Porous Media Simplification)
สำหรับเครื่องแลกเปลี่ยนที่มีท่อนับพัน เรามักใช้การ Homogenization โดยแทนที่กลุ่มท่อด้วย **โซนพรุน** ที่มีแรงต้านการไหลเทียบเท่าอิงตามสมการ Darcy-Forchheimer:
$$\nabla p = -(\frac{\mu}{K} + \beta \rho |\mathbf{u}|) \mathbf{u}$$

---

## 💻 3. OpenFOAM Implementation

การกำหนดค่าแหล่งความร้อนในกรณีใช้ Porous Media ผ่าน `system/fvOptions`:

```cpp
heatSource
{
    type            scalarSemiImplicitSource;
    active          true;
    selectionMode   cellZone;
    cellZone        heatExchangerZone;
    scalarSemiImplicitSourceCoeffs
    {
        T
        {
            Su      10000; // แหล่งความร้อนคงที่ [W/m³] 
            Sp      0;
        }
    }
}
```

---

## 📈 4. การตรวจสอบความถูกต้อง (Validation)

ผลการจำลองควรได้รับการตรวจสอบเทียบกับ:
- **LMTD Method**: ผลเฉลยทางทฤษฎีสำหรับความแตกต่างอุณหภูมิเฉลี่ยลอการิทึม
- **Energy Balance**: $\dot{Q}_{hot} \approx \dot{Q}_{cold}$ (ตรวจสอบความคลาดเคลื่อนของสมดุลพลังงาน)

---
**จบเนื้อหาโมดูลการประยุกต์ใช้จริง**
