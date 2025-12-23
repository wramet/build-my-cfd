# การไหลภายในและเครือข่ายท่อ (Internal Flows and Piping)

## 📖 บทนำ (Introduction)

การไหลภายในเป็นพื้นฐานของระบบวิศวกรรมมากมาย เช่น ท่อส่งน้ำมัน ระบบระบายอากาศ (HVAC) และเครื่องปฏิกรณ์เคมี ความท้าทายหลักคือการคาดการณ์ความดันตกคร่อมและประสิทธิภาพการผสม

---

## 🔍 1. ฟิสิกส์ของการไหลในท่อ

### 1.1 ความดันตกคร่อม (Pressure Drop)
การสูญเสียพลังงานเนื่องจากแรงเสียดทานอธิบายด้วยสมการ **Darcy-Weisbach**:
$$\Delta p = f \frac{L}{D} \frac{\rho U^2}{2}$$
- $f$ คือ Friction factor ซึ่งขึ้นอยู่กับความหยาบผิวและ Reynolds number

ใน OpenFOAM เราวัดค่านี้ได้จาก:
$$\Delta p = p_{inlet} - p_{outlet}$$

### 1.2 ลักษณะโปรไฟล์ความเร็ว (Velocity Profiles)
- **Laminar Flow**: โปรไฟล์แบบพาราโบลา
- **Turbulent Flow**: โปรไฟล์ที่แบนลงตรงกลาง (Plug-like) พร้อมความชันสูงที่ผนัง

---

## 🛠️ 2. การสร้างแบบจำลองการผสม (Mixing Analysis)

ในระบบท่อที่มีการผสมสาร (เช่น Static Mixers) เราใช้ตัวชี้วัดเพื่อระบุประสิทธิภาพ:

### 2.1 ดัชนีการผสม (Mixing Index, MI)
$$MI = 1 - \frac{\sigma}{\sigma_0}$$
โดยที่ $\sigma$ คือส่วนเบี่ยงเบนมาตรฐานของความเข้มข้นที่หน้าตัดใดๆ

### 2.2 เวลากักตัว (Residence Time Distribution, RTD)
ใช้สเกลาร์พาสซีฟ (Passive scalar) เพื่อติดตามเวลาที่อนุภาคของไหลใช้ในระบบ:
$$\bar{t} = \frac{V}{\dot{V}}$$

---

## 💻 3. การนำไปใช้ใน OpenFOAM

ตัวอย่างการใช้ `surfaceFieldValue` เพื่อหาค่าความดันเฉลี่ยที่ทางเข้าและทางออก:

```cpp
functions
{
    pInlet
    {
        type            surfaceFieldValue;
        libs            (fieldFunctionObjects);
        operation       weightedAverage;
        weightField     phi;
        region          region0;
        surfaceFormat   none;
        fields          (p);
        patches         (inlet);
    }
}
```

---

## 📋 4. ข้อควรระวังในการจำลองการไหลภายใน

1. **Entry Length**: ตรวจสอบว่าความยาวท่อเพียงพอให้การไหลพัฒนาเต็มที่ (Fully developed) หรือไม่ หากไม่เพียงพอต้องระบุโปรไฟล์ที่ทางเข้า
2. **Mesh Quality**: บริเวณข้อต่อ (Elbows) มักเกิดการแยกตัวของการไหล (Separation) ต้องการ Mesh ที่ละเอียดเป็นพิเศษเพื่อจับภาพกระแสวนทุติยภูมิ (Dean vortices)

---
**หัวข้อถัดไป**: [เครื่องแลกเปลี่ยนความร้อน](./03_Heat_Exchangers.md)
