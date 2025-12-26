# บทสรุปและแบบฝึกหัด (Summary & Exercises)

```mermaid
mindmap
root((การวิเคราะห์มิติ))
dimensionSet
หน่วย SI
เลขชี้กำลัง
isDimensionless
พีชคณิต
การบวก/ลบ
การคูณ/หาร
ยกกำลัง/ถอดราก
การทำให้ไร้มิติ
สเกลอ้างอิง
ความคล้ายคลึง
เสถียรภาพ
ขั้นสูง
การเชื่อมต่อ (Coupling)
หน่วยกำหนดเอง
ตาข่ายนิรภัย
```
> **Figure 1:** แผนผังความคิดสรุปองค์ประกอบของการวิเคราะห์มิติ ครอบคลุมทั้งโครงสร้าง dimensionSet กฎพีชคณิตมิติ เทคนิคการทำให้ไร้มิติ และการประยุกต์ใช้ในระบบหลายฟิสิกส์ความปลอดภัยทางฟิสิกส์ไม่ส่งผลกระทบต่อความเร็วในการจำลอง ผ่านการใช้พลังของ C++ Template Metaprogramming ในการตรวจสอบความสอดคล้องทางมิติทั้งหมดที่ขั้นตอนการคอมไพล์โปรแกรมเพียงครั้งเดียว

---

## 12.9. บทสรุป: ตาข่ายนิรภัยทางมิติ (The Dimensional Safety Net)

ระบบการวิเคราะห์มิติของ OpenFOAM แสดงถึงความก้าวหน้าพื้นฐานในความปลอดภัยและความน่าเชื่อถือของพลศาสตร์ของไหลเชิงคำนวณ โดยจะตรวจจับความไม่สอดคล้องทางมิติตั้งแต่ขั้นตอนแรกของการคอมไพล์หรือการเริ่มต้นรันไทม์

### ประโยชน์หลักของระบบมิติ

1. **การตรวจสอบความสอดคล้องอัตโนมัติ**: ป้องกันการดำเนินการที่ไม่มีความหมายทางฟิสิกส์ เช่น การบวกความดันเข้ากับความเร็ว
2. **ความปลอดภัยทางฟิสิกส์ระดับ Type**: ฝังมิติทางฟิสิกส์ลงในระบบชนิดข้อมูล C++ โดยตรง เพื่อตรวจสอบกฎการอนุรักษ์ในสมการควบคุม
3. **รองรับการทำให้ไร้มิติ**: ช่วยปรับปรุงเสถียรภาพเชิงตัวเลขและเปิดใช้งานการวิเคราะห์ความคล้ายคลึง (Similarity Analysis)
4. **การรวมหลายฟิสิกส์**: จัดการปฏิสัมพันธ์ระหว่างโดเมนทางฟิสิกส์ที่แตกต่างกัน (เช่น FSI, MHD) อย่างเข้มงวด

> [!INFO] **หลักการสำคัญ**
> ระบบการวิเคราะห์มิติทำงานทั้งใน **เวลาคอมไพล์และเวลารันไทม์** เพื่อตรวจสอบโดยอัตโนมัติว่าการดำเนินการทางคณิตศาสตร์ทั้งหมดมีความสอดคล้องทางมิติ ป้องกันข้อผิดพลาดในการแปลงหน่วยและการคำนวณที่ไม่ถูกต้องทางฟิสิกส์

### กฎพีชคณิตมิติพื้นฐาน

| การดำเนินการ | ข้อกำหนดทางมิติ | ตัวอย่าง |
|-----------|------------------------|---------|
| การบวก/การลบ | มิติที่เหมือนกันในทั้ง 7 ตำแหน่ง | `p + p` |
| การคูณ/การหาร | เลขชี้กำลังบวก/ลบทางพีชคณิต | `velocity * time = length` |
| การยกกำลัง | เลขชี้กำลังคูณด้วยค่ายกกำลัง | `length^2 = area` |
| ฟังก์ชันภายใน | อาร์กิวเมนต์ต้อง **ไร้มิติ** | `sin(angle)`, `exp(T/Tref)` |

### การตรวจสอบกฎการอนุรักษ์

ระบบมิติช่วยตรวจสอบว่ากฎการอนุรักษ์ถูกนำไปใช้อย่างถูกต้องโดยตรวจสอบให้แน่ใจว่าแต่ละเทอมในสมการการอนุรักษ์มีมิติที่เหมือนกัน

**การอนุรักษ์มวล:**
$$\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \mathbf{u}) = 0$$

**การตรวจสอบมิติ:**
- $\frac{\partial \rho}{\partial t}$: $[M \, L^{-3} \, T^{-1}]$
- $\nabla \cdot (\rho \mathbf{u})$: $[M \, L^{-3} \, T^{-1}]$

**การอนุรักษ์โมเมนตัม:**
$$\rho \frac{\partial \mathbf{u}}{\partial t} + \rho (\mathbf{u} \cdot \nabla) \mathbf{u} = -\nabla p + \mu \nabla^2 \mathbf{u} + \mathbf{f}$$

**การตรวจสอบมิติ:**
- ทุกเทอม: $[M \, L^{-2} \, T^{-2}]$ (แรงต่อหน่วยปริมาตร)

### ประโยชน์ของการรวมหลายฟิสิกส์

ในการจำลองหลายฟิสิกส์ที่ซับซ้อน ตาข่ายนิรภัยทางมิติจะมีค่ามากยิ่งขึ้นเนื่องจากจัดการปฏิสัมพันธ์ระหว่างโดเมนทางฟิสิกส์ที่แตกต่างกัน:

```cpp
// Multi-physics coupling with automatic dimensional checking
// Heat transfer affects fluid properties through temperature-dependent viscosity
volScalarField muEff(mu(T));          // Temperature-dependent viscosity
volScalarField alpha(k/(rho*cp));     // Thermal diffusivity

// Buoyancy force with correct dimensions
volVectorField gBuoyancy(rhok * g * T); // [kg/(m²·s²)]
```

---

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/populationBalanceModel/populationBalanceModel/populationBalanceModel.C`

**📋 คำอธิบาย:**
โค้ดตัวอย่างนี้แสดงการใช้ระบบ dimensional analysis ใน OpenFOAM เพื่อตรวจสอบความสอดคล้องของหน่วยในระบบ multi-physics แต่ละบรรทัดมีการดำเนินการทางฟิสิกส์ที่ต้องการหน่วยที่ถูกต้อง:

- **บรรทัดที่ 2**: `muEff` คำนวณค่า viscosity ที่ขึ้นกับอุณหภูมิ โดยระบบจะตรวจสอบว่าผลลัพธ์มีหน่วยของ dynamic viscosity [Pa·s] หรือ [M·L⁻¹·T⁻¹] อย่างถูกต้อง
- **บรรทัดที่ 3**: `alpha` คำนวณ thermal diffusivity จากสมการ k/(ρ·cp) โดยระบบจะยืนยันว่าผลลัพธ์มีหน่วย [m²/s] หรือ [L²·T⁻¹] 
- **บรรทัดที่ 6**: `gBuoyancy` คำนวณแรงลอยตัวจากความโน้มถ่วง โดยผลลัพธ์ต้องมีหน่วยของ force per volume [N/m³] หรือ [M·L⁻²·T⁻²] ซึ่งระบบจะตรวจสอบให้โดยอัตโนมัติ

**🔑 แนวคิดสำคัญ:**
- **Compile-time Dimensional Checking**: ระบบตรวจสอบหน่วยขณะคอมไพล์ ป้องกันการดำเนินการที่ไม่สอดคล้องกันทางมิติ
- **Type-Safe Physics Operations**: แต่ละ field มีข้อมูล dimension แนบอยู่ ป้องกันการบวกลบปริมาณที่มีหน่วยต่างกัน
- **Multi-Physics Coupling**: ระบบจัดการการเชื่อมต่อระหว่างฟิสิกส์หลายสาขา (heat transfer, fluid dynamics) อย่างปลอดภัย

**ประสิทธิภาพการพัฒนา:**
| ประโยชน์ | คำอธิบาย | ผลกระทบ |
|---------|-------------|--------|
| **การตรวจจับข้อผิดพลาดล่วงหน้า** | ปัญหาถูกจับในระหว่างการคอมไพล์ | ลดเวลาการคำนวณที่สูญเปล่า |
| **การระบุข้อผิดพลาดที่แม่นยำ** | ระบุตำแหน่งที่แน่นอนของความไม่สอดคล้องทางมิติ | เร่งการแก้ปัญหา |
| **ลดการลองผิดลองถูก** | การตรวจสอบอย่างเป็นระบบแทนที่จะเดาการแปลงหน่วย | เพิ่มความน่าเชื่อถือของโค้ด |

**ความน่าเชื่อถือของการจำลอง:**
- **ความถูกต้องทางฟิสิกส์**: ผลลัพธ์ได้รับการรับประกันว่าจะมีความสอดคล้องทางมิติ
- **การทำซ้ำได้**: กำจัดแหล่งที่มาของความผันแปรที่เกี่ยวข้องกับหน่วยระหว่างการจำลอง
- **การสนับสนุนการตรวจสอบ**: ให้รากฐานทางคณิตศาสตร์สำหรับขั้นตอนการตรวจสอบโค้ด

---

## แบบฝึกหัด (Exercises)

### ส่วนที่ 1: การวิเคราะห์มิติพื้นฐาน

เขียนอาร์เรย์ของเลขชี้กำลัง 7 ตำแหน่ง (`M L T Theta N I J`) สำหรับปริมาณต่อไปนี้:

1. **แรง (Force)**: $F = m \cdot a$
2. **พลังงาน (Energy)**: $E = F \cdot d$
3. **ความหนืดจลน์ (Kinematic Viscosity, $\nu$)**: หน่วยคือ $m^2/s$
4. **อัตราการไหลของมวล (Mass Flow Rate)**: หน่วยคือ $kg/s$

<details>
<summary>💡 เฉลย - ส่วนที่ 1</summary>

1. **แรง**: `[1 1 -2 0 0 0 0]` (นิวตัน: $kg \cdot m/s^2$)
2. **พลังงาน**: `[1 2 -2 0 0 0 0]` (จูล: $kg \cdot m^2/s^2$)
3. **ความหนืดจลน์**: `[0 2 -1 0 0 0 0]` ($m^2/s$)
4. **อัตราการไหลของมวล**: `[1 0 -1 0 0 0 0]` ($kg/s$)

</details>

---

### ส่วนที่ 2: การตรวจสอบความสอดคล้อง

สมการโมเมนตัมแบบง่ายคือ:
$$\frac{\mathbf{U}}{\Delta t} + \mathbf{U} \cdot \nabla \mathbf{U} = -\frac{\nabla p}{\rho}$$

**คำถาม**: จงพิสูจน์ว่าหน่วยของเทอมซ้ายสุด ($\mathbf{U}/\Delta t$) และเทอมขวาสุด ($\nabla p / \rho$) เท่ากันหรือไม่ (แสดงเลขชี้กำลัง)

<details>
<summary>💡 เฉลย - ส่วนที่ 2</summary>

**การวิเคราะห์เทอมซ้ายสุด ($\mathbf{U}/\Delta t$):**
- $\mathbf{U}$: $[L \, T^{-1}]$ (ความเร็ว)
- $\Delta t$: $[T]$ (เวลา)
- **ผลลัพธ์**: $[L \, T^{-1}] / [T] = [L \, T^{-2}]$ (ความเร่ง)

**การวิเคราะห์เทอมขวาสุด ($\nabla p / \rho$):**
- $\nabla p$: $[M \, L^{-1} \, T^{-2}] / [L] = [M \, L^{-2} \, T^{-2}]$
- $\rho$: $[M \, L^{-3}]$
- **ผลลัพธ์**: $[M \, L^{-2} \, T^{-2}] / [M \, L^{-3}] = [L \, T^{-2}]$ (ความเร่ง)

**สรุป**: ✓ ทั้งสองเทอมมีมิติที่เหมือนกันคือ $[L \, T^{-2}]$

</details>

---

### ส่วนที่ 3: สถานการณ์การใช้งาน

คุณกำลังแก้ปัญหาการไหลรอบทรงกระบอกและพบว่าผลลัพธ์จากกริดหยาบและละเอียดให้ค่าความดันที่แตกต่างกันอย่างมาก:

- หากคุณเปลี่ยนไปเปรียบเทียบในรูปของ **สัมประสิทธิ์ความดัน ($C_p$)** ซึ่งเป็นค่าไร้มิติ คุณจะเห็นแนวโน้มอย่างไร?
- เขียนโค้ด OpenFOAM เพื่อคำนวณ `Cp` จาก `p`, `p_inf`, `rho` และ `U_inf`

<details>
<summary>💡 เฉลย - ส่วนที่ 3</summary>

**การสังเกตแนวโน้ม:**
- คุณจะเห็นว่า $C_p$ **ลู่เข้าสู่ค่าเดียวกัน** แม้ว่าความดันดิบจะแตกต่างกัน (การศึกษาความเป็นอิสระของกริด)
- สัมประสิทธิ์ไร้มิติขจัดความแตกต่างของการปรับสเกลและเผยให้เห็นฟิสิกส์พื้นฐาน

**การนำไปใช้ใน OpenFOAM:**

```cpp
// Read reference quantities from transport properties dictionary
dimensionedScalar p_inf(
    "p_inf", 
    dimPressure, 
    readScalar(transportProperties.lookup("p_inf"))
);

dimensionedScalar rho(
    "rho", 
    dimDensity, 
    readScalar(transportProperties.lookup("rho"))
);

dimensionedScalar U_inf(
    "U_inf", 
    dimVelocity, 
    readScalar(transportProperties.lookup("U_inf"))
);

// Calculate pressure coefficient using Bernoulli equation
// Cp = (p - p_inf) / (0.5 * rho * U_inf^2)
volScalarField Cp
(
    IOobject("Cp", runTime.timeName(), mesh),
    (p - p_inf) / (0.5 * rho * sqr(U_inf))
);

Cp.write();  // Output field for post-processing
```

---

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/populationBalanceModel/populationBalanceModel/populationBalanceModel.C`

**📋 คำอธิบาย:**
โค้ดนี้แสดงการคำนวณ pressure coefficient ($C_p$) ซึ่งเป็นปริมาณไร้มิติที่ใช้ในการวิเคราะห์ผลลัพธ์จากการจำลอง CFD:

- **บรรทัดที่ 2-4**: ประกาศ `p_inf` ซึ่งเป็น reference pressure โดยระบุ `dimPressure` เพื่อให้แน่ใจว่ามีหน่วย [Pa] หรือ [M·L⁻¹·T⁻²] ถูกต้อง
- **บรรทัดที่ 6-8**: ประกาศ `rho` (density) และ `U_inf` (reference velocity) พร้อมระบุหน่วยให้ถูกต้อง
- **บรรทัดที่ 15-18**: คำนวณ $C_p$ จากสมการ $(p - p_\infty) / (0.5 \cdot \rho \cdot U_\infty^2)$ โดยระบบจะตรวจสอบว่าตัวหารและตัวตั้งมีหน่วยเหมือนกัน ทำให้ $C_p$ ไร้มิติโดยอัตโนมัติ

**🔑 แนวคิดสำคัญ:**
- **Non-Dimensionalization**: การแปลงปริมาณมิติให้เป็นไร้มิติช่วยให้เปรียบเทียบผลลัพธ์จาก mesh ต่างกันได้
- **Automatic Dimensional Verification**: ระบบตรวจสอบว่าสมการ $C_p$ ให้ผลลัพธ์ไร้มิติเสมอ
- **Grid Independence Study**: การใช้ค่าไร้มิติช่วยตรวจสอบว่า mesh ละเอียดพอแล้วหรือยัง

**การตรวจสอบมิติ:**
- ตัวเศษ: $(p - p_\infty)$ → $[M \, L^{-1} \, T^{-2}]$
- ตัวส่วน: $0.5 \cdot \rho \cdot U_\infty^2$ → $[M \, L^{-3}] \cdot [L^2 \, T^{-2}] = [M \, L^{-1} \, T^{-2}]$
- **ผลลัพธ์**: $C_p$ เป็นค่าไร้มติตามที่ต้องการ

</details>

---

### ส่วนที่ 4: ความท้าทายหลายฟิสิกส์ขั้นสูง

สำหรับการจำลองแมกเนโตไฮโดรไดนามิกส์ (MHD) คุณต้องตรวจสอบความสอดคล้องทางมิติสำหรับเทอมแรงลอเรนตซ์:

$$\mathbf{F}_L = \mathbf{J} \times \mathbf{B}$$

โดยที่:
- $\mathbf{J}$ = ความหนาแน่นกระแส ($A/m^2$)
- $\mathbf{B}$ = สนามแม่เหล็ก (Tesla)

**งาน:**
1. กำหนดมิติของแรงลอเรนตซ์ต่อหน่วยปริมาตร
2. เขียนโค้ด OpenFOAM เพื่อประกาศฟิลด์เหล่านี้พร้อมมิติที่เหมาะสม
3. แสดงให้เห็นว่าระบบมิติป้องกันการผสมฟิลด์ไฟฟ้าและแม่เหล็กอย่างไม่ถูกต้องได้อย่างไร

<details>
<summary>💡 เฉลย - ส่วนที่ 4</summary>

**1. การวิเคราะห์มิติ:**

| ปริมาณ | สัญลักษณ์ | มิติ | หน่วย SI |
|----------|--------|------------|---------|
| ความหนาแน่นกระแส | $\mathbf{J}$ | $[I \, L^{-2}]$ | $A/m^2$ |
| สนามแม่เหล็ก | $\mathbf{B}$ | $[M \, T^{-2} \, I^{-1}]$ | Tesla |
| ความหนาแน่นแรงลอเรนตซ์ | $\mathbf{F}_L$ | $[M \, L^{-2} \, T^{-2}]$ | $N/m^3$ |

**การตรวจสอบ:**
$$[\mathbf{J} \times \mathbf{B}] = [I \, L^{-2}] \cdot [M \, T^{-2} \, I^{-1}] = [M \, L^{-2} \, T^{-2}]$$

**2. การนำไปใช้ใน OpenFOAM:**

```cpp
// Define custom electromagnetic dimensions for MHD simulation
// dimensionSet(Mass, Length, Time, Temperature, Moles, Current, LuminousIntensity)
dimensionSet dimCurrentDensity(0, -2, 0, 0, 0, 1, 0);      // [I·L⁻²] = [A/m²]
dimensionSet dimMagneticField(1, 0, -2, 0, 0, -1, 0);      // [M·T⁻²·I⁻¹] = [Tesla]
dimensionSet dimForceDensity(1, -2, -2, 0, 0, 0, 0);       // [M·L⁻²·T⁻²] = [N/m³]

// Declare electromagnetic fields with proper dimensions
volVectorField J
(
    IOobject("J", runTime.timeName(), mesh, IOobject::MUST_READ),
    mesh,
    dimCurrentDensity
);

volVectorField B
(
    IOobject("B", runTime.timeName(), mesh, IOobject::MUST_READ),
    mesh,
    dimMagneticField
);

// Calculate Lorentz force using cross product operator (^)
// The dimensional system automatically verifies that J × B yields force density
volVectorField F_L("F_L", J ^ B);  

// Runtime dimensional verification
if (!F_L.dimensions().matches(dimForceDensity))
{
    FatalErrorIn("calculateLorentzForce")
        << "Lorentz force has incorrect dimensions: " << F_L.dimensions()
        << "Expected: " << dimForceDensity
        << exit(FatalError);
}
```

---

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/populationBalanceModel/populationBalanceModel/populationBalanceModel.C`

**📋 คำอธิบาย:**
โค้ดนี้แสดงการประยุกต์ใช้ระบบ dimensional analysis ในการจำลอง Magnetohydrodynamics (MHD) ซึ่งเป็น multi-physics ที่รวม electromagnetism กับ fluid dynamics:

- **บรรทัดที่ 2-4**: นิยามหน่วย custom สำหรับ current density โดยใช้ `dimensionSet(0, -2, 0, 0, 0, 1, 0)` ซึ่งแทนหน่วย [I·L⁻²] = [A/m²] ตามลำดับ (Mass, Length, Time, Temperature, Moles, Current, LuminousIntensity)
- **บรรทัดที่ 5**: นิยามหน่วย magnetic field [Tesla] ซึ่งมีค่าเท่ากับ [M·T⁻²·I⁻¹]
- **บรรทัดที่ 6**: นิยามหน่วย force density [N/m³] หรือ [M·L⁻²·T⁻²] เพื่อใช้ในการตรวจสอบผลลัพธ์
- **บรรทัดที่ 9-14**: ประกาศ field `J` (current density) และ `B` (magnetic field) โดยระบุ dimension ที่ถูกต้อง ซึ่งป้องกันการกำหนดค่าผิดพลาด
- **บรรทัดที่ 19**: คำนวณ Lorentz force ด้วย cross product operator (`^`) ซึ่งระบบจะตรวจสอบ dimension อัตโนมัติว่าผลลัพธ์มีหน่วยของ force density ถูกต้อง
- **บรรทัดที่ 22-28**: มีการตรวจสอบ dimension เพิ่มเติมขณะ runtime เพื่อความมั่นใจในกรณีที่มีการคำนวณที่ซับซ้อน

**🔑 แนวคิดสำคัญ:**
- **Custom Dimension Sets**: สามารถนิยามหน่วย custom สำหรับฟิสิกส์เฉพาะทาง (electromagnetism) ได้
- **Cross Product Dimensional Rules**: operator `^` (cross product) ทำงานร่วมกับระบบ dimensional เพื่อตรวจสอบหน่วย
- **Multi-Physics Safety**: ระบบป้องกันการผสมผสานปริมาณทางฟิสิกส์ที่ไม่สอดคล้องกัน เช่น การบวก current density กับ magnetic field

**3. การป้องกันข้อผิดพลาด:**

ระบบมิติช่วยป้องกันข้อผิดพลาดทั่วไปเหล่านี้:

```cpp
// ❌ ERROR: Caught by compiler or runtime
// volScalarField invalid = J + B;  
// Cannot add current density to magnetic field (dimensional mismatch)

// ❌ ERROR: Dimension mismatch detected
// volVectorField wrongForce = J * B;  
// Wrong operator - should be cross product for vector multiplication

// ❌ ERROR: Type system prevents mixing incompatible dimensions
// volVectorField badField = J * dimensionedScalar("bad", dimPressure, 1.0);
// Current density cannot multiply with pressure

// ✓ CORRECT: Proper cross product with automatic dimensional validation
volVectorField lorentzForce = J ^ B;  
// Dimensions automatically verified to produce force density
```

---

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/populationBalanceModel/populationBalanceModel/populationBalanceModel.C`

**📋 คำอธิบาย:**
ตัวอย่างนี้แสดงประเภทข้อผิดพลาดที่ระบบ dimensional analysis สามารถป้องกันได้ในการจำลอง MHD:

- **บรรทัดที่ 2-3**: พยายามบวก current density (`J`) กับ magnetic field (`B`) ซึ่งมีหน่วยต่างกัน → ระบบจะปฏิเสธเนื่องจาก dimensional mismatch
- **บรรทัดที่ 6-7**: ใช้ multiplication operator (`*`) แทน cross product (`^`) → ผิดทางคณิตศาสตร์และอาจให้หน่วยที่ผิด
- **บรรทัดที่ 10-11**: พยายามคูณ current density กับ pressure ซึ่งไม่มีความสัมพันธ์ทางฟิสิกส์ → ระบบป้องกันการดำเนินการที่ไม่สอดคล้องกัน
- **บรรทัดที่ 15**: การใช้ cross product operator (`^`) อย่างถูกต้อง → ระบบตรวจสอบ dimension และยืนยันผลลัพธ์

**🔑 แนวคิดสำคัญ:**
- **Type-Safe Physics**: แต่ละ field มี "type" ทางฟิสิกส์แนบอยู่ ป้องกันการดำเนินการที่ไม่สมเหตุสมผล
- **Operator Overloading with Dimension Awareness**: operator ทางคณิตศาสตร์ (`+`, `-`, `*`, `^`) ตรวจสอบ dimension อัตโนมัติ
- **Multi-Physics Discipline**: ระบบบังคับให้ผู้ใช้คำนึงถึงความสอดคล้องทางฟิสิกส์เสมอ

</details>

---

### ส่วนที่ 5: การสร้าง Solver ไร้มิติ

สร้างรูปแบบไร้มิติของสมการ Navier-Stokes แบบไม่อัดตัวสำหรับการไหลรอบสิ่งกีดขวาง

**ปริมาณอ้างอิง:**
- $L_{ref} = 1.0$ m (ความยาวลักษณะเฉพาะ)
- $U_{ref} = 10.0$ m/s (ความเร็วลักษณะเฉพาะ)
- $\nu = 1.5 \times 10^{-5}$ m²/s (ความหนืดจลน์)

**งาน:**
1. คำนวณเลข Reynolds
2. เขียนสมการโมเมนตัมไร้มิติ
3. นำไปใช้เงื่อนไขขอบเขตในรูปแบบไร้มิติ

<details>
<summary>💡 เฉลย - ส่วนที่ 5</summary>

**1. การคำนวณเลข Reynolds:**

$$Re = \frac{U_{ref} \cdot L_{ref}}{\nu} = \frac{10.0 \times 1.0}{1.5 \times 10^{-5}} \approx 666,667$$

**2. สมการโมเมนตัมไร้มิติ:**

$$\frac{\partial \mathbf{u}^*}{\partial t^*} + (\mathbf{u}^* \cdot \nabla^*) \mathbf{u}^* = -\nabla^* p^* + \frac{1}{Re} \nabla^{*2} \mathbf{u}^*$$

โดยที่:
- $\mathbf{u}^* = \mathbf{u} / U_{ref}$ (ความเร็วไร้มิติ)
- $p^* = p / (\rho U_{ref}^2)$ (ความดันไร้มิติ)
- $t^* = t \cdot U_{ref} / L_{ref}$ (เวลาไร้มิติ)
- $\nabla^* = L_{ref} \cdot \nabla$ (เกรเดียนต์ไร้มิติ)

**3. การนำไปใช้ใน OpenFOAM:**

```cpp
// createNonDimensionalFields.H
// Define reference quantities for non-dimensionalization
dimensionedScalar LRef("LRef", dimLength, 1.0);    // Reference length [m]
dimensionedScalar URef("URef", dimVelocity, 10.0); // Reference velocity [m/s]
dimensionedScalar nuRef("nuRef", dimKinematicViscosity, 1.5e-5); // Kinematic viscosity [m²/s]

// Calculate Reynolds number (automatically dimensionless)
// Re = (U_ref * L_ref) / ν
dimensionedScalar Re(
    "Re", 
    dimless,  // Explicitly mark as dimensionless
    URef * LRef / nuRef
);

Info << "Reynolds number: " << Re.value() << endl;

// Create non-dimensional velocity field
// u* = u / U_ref (automatically dimensionless due to dimensional division)
volVectorField Ustar
(
    IOobject("Ustar", runTime.timeName(), mesh),
    U / URef  // Dimensional division yields dimensionless field
);

// Create non-dimensional pressure field
// p* = p / (ρ * U_ref²)
volScalarField pstar
(
    IOobject("pstar", runTime.timeName(), mesh),
    p / (rho * sqr(URef))  // sqr(URef) gives [m²/s²]
);
```

---

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/populationBalanceModel/populationBalanceModel/populationBalanceModel.C`

**📋 คำอธิบาย:**
โค้ดนี้แสดงการสร้าง field ไร้มิติ (non-dimensional fields) สำหรับการจำลอง CFD โดยใช้ reference quantities:

- **บรรทัดที่ 2-4**: นิยาม reference length `LRef`, reference velocity `URef`, และ kinematic viscosity `nuRef` โดยระบุ dimension ให้ถูกต้องตามหน่วย SI
- **บรรทัดที่ 7-11**: คำนวณ Reynolds number โดยระบบจะตรวจสอบว่า `(URef * LRef) / nuRef` ให้ผลลัพธ์ไร้มิติ หากไม่สอดคล้องจะเกิด error ขณะคอมไพล์
- **บรรทัดที่ 15-19**: สร้าง non-dimensional velocity field `Ustar` โดยหาร velocity ด้วย `URef` ซึ่งระบบจะตรวจสอบว่าผลลัพธ์ไร้มิติ
- **บรรทัดที่ 22-26**: สร้าง non-dimensional pressure field `pstar` โดยใช้ `sqr(URef)` ซึ่งสร้าง [m²/s²] และคูณกับ density เพื่อให้ได้หน่วย pressure ที่เข้ากันได้

**🔑 แนวคิดสำคัญ:**
- **Reference Scales**: การกำหนด reference quantities ช่วยแปลงปัญหามิติให้เป็นไร้มิติ
- **Automatic Dimensionless Creation**: การหารหรือคูณปริมาณที่มีหน่วยเดียวกันสร้างค่าไร้มิติโดยอัตโนมัติ
- **Reynolds Number Parameter**: ค่า Re เป็นพารามิเตอร์เดียวที่ควบคุมฟิสิกส์ของปัญหาไร้มิติ
- **Numerical Advantages**: การแก้สมการไร้มิติช่วยปรับปรุง conditioning ของระบบ linear

**เงื่อนไขขอบเขตไร้มิติ (`0/Ustar`):**

```cpp
dimensions      [0 0 0 0 0 0 0];  // Explicitly dimensionless

internalField   uniform (1 0 0);  // U/U_ref = 1 at inlet (normalized)

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform (1 0 0);  // Non-dimensional inlet: u*/U* = 1
    }
    outlet
    {
        type            zeroGradient;  // ∂u*/∂n = 0
    }
    walls
    {
        type            fixedValue;
        value           uniform (0 0 0);  // No-slip condition in non-dimensional form
    }
}
```

---

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/populationBalanceModel/populationBalanceModel/populationBalanceModel.C`

**📋 คำอธิบาย:**
ไฟล์ boundary condition นี้แสดงการใช้ non-dimensional values สำหรับการจำลอง:

- **บรรทัดที่ 1**: ระบุ `dimensions [0 0 0 0 0 0 0]` เพื่อประกาศอย่างชัดเจนว่า field นี้ไร้มิติ ซึ่งช่วยให้ OpenFOAM ตรวจสอบความสอดคล้องได้
- **บรรทัดที่ 3**: `internalField` มีค่า `(1 0 0)` ซึ่งแทนค่า velocity ที่ normalize แล้ว (u/U_ref = 1)
- **บรรทัดที่ 7-10**: Inlet boundary condition กำหนดค่า `(1 0 0)` ซึ่งหมายความว่า normalized velocity ที่ inlet มีค่า 1 ในทิศทาง x
- **บรรทัดที่ 11-14**: Outlet ใช้ `zeroGradient` ซึ่งหมายความว่า gradient ของ velocity ไร้มิติในทิศทางปกติเป็นศูนย์
- **บรรทัดที่ 15-20**: Walls ใช้ `fixedValue (0 0 0)` ซึ่งแทน no-slip condition ในรูปแบบไร้มิติ

**🔑 แนวคิดสำคัญ:**
- **Non-Dimensional BCs**: ค่า boundary conditions ไร้มิติทำให้ผลลัพธ์ scale ได้ง่าย
- **Normalization**: การ normalize ค่า boundary conditions ช่วยลดความซับซ้อนของ setup
- **Physical Similarity**: การใช้ non-dimensional BCs ทำให้สามารถเปรียบเทียบกรณีที่ geometrically similar ได้

**สมการโมเมนตัมไร้มิติ (`UEqn.H`):**

```cpp
// UEqn.H - Non-dimensional form of Navier-Stokes
// The momentum equation is:
// ∂u*/∂t* + (u*·∇*)u* = -∇*p* + (1/Re)∇*²u*
{
    // Build the non-dimensional momentum equation matrix
    fvVectorMatrix UstarEqn
    (
        // Time derivative term: ∂u*/∂t*
        fvm::ddt(Ustar)                      
        
        // Convective term: (u*·∇*)u*
        // phiStar is the non-dimensional flux
      + fvm::div(phiStar, Ustar)             
        
        // Diffusive term: (1/Re)∇*²u*
        // Note: 1/Re is explicitly non-dimensional
      - fvm::laplacian(
            dimensionedScalar("invRe", dimless, 1.0/Re), 
            Ustar
        )  
    );

    // Relax the equation for improved convergence
    UstarEqn.relax();

    // Solve the momentum equation with pressure gradient
    if (pimple.momentumPredictor())
    {
        // -∇*p* term (pressure gradient)
        solve(UstarEqn == -fvc::grad(pstar));
    }
}
```

---

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/populationBalanceModel/populationBalanceModel/populationBalanceModel.C`

**📋 คำอธิบาย:**
ไฟล์ `UEqn.H` นี้แสดงการ implement non-dimensional momentum equation ใน OpenFOAM:

- **บรรทัดที่ 2**: แสดงสมการไร้มิติที่จะแก้: ∂u*/∂t* + (u*·∇*)u* = -∇*p* + (1/Re)∇*²u*
- **บรรทัดที่ 5**: สร้าง `fvVectorMatrix` สำหรับแก้สมการ momentum ไร้มิติ
- **บรรทัดที่ 8**: `fvm::ddt(Ustar)` แทน time derivative term (∂u*/∂t*) ซึ่งไร้มิติ
- **บรรทัดที่ 11-12**: `fvm::div(phiStar, Ustar)` แทน convective term ((u*·∇*)u*) โดย `phiStar` คือ non-dimensional flux
- **บรรทัดที่ 15-18**: `fvm::laplacian` แทน diffusive term ((1/Re)∇*²u*) โดยระบุค่าสัมประสิทธิ์ `1/Re` ซึ่งไร้มิติชัดเจน
- **บรรทัดที่ 21**: `relax()` ใช้ under-relaxation เพื่อปรับปรุงการลู่เข้าของวิธี iterative
- **บรรทัดที่ 24-27**: แก้สมการ momentum ร่วมกับ pressure gradient term (-∇*p*)

**🔑 แนวคิดสำคัญ:**
- **Non-Dimensional Operators**: `fvm::ddt`, `fvm::div`, `fvm::laplacian` ทำงานกับ field ไร้มิติได้โดยตรง
- **Reynolds Number as Coefficient**: 1/Re เป็นพารามิเตอร์เดียวที่ควบคุม viscous effects
- **SIMPLE/PIMPLE Algorithm**: การแก้ pressure-velocity coupling ยังคงใช้ได้กับสมการไร้มิติ
- **Numerical Stability**: การทำให้ไร้มิติช่วยปรับปรุง conditioning ของระบบ linear

**ข้อดีของรูปแบบไร้มิติ:**
- **การควบคุมด้วยพารามิเตอร์เดียว**: พารามิเตอร์เดียว (Re) ควบคุมฟิสิกส์ทั้งหมด
- **ความสามารถในการปรับสเกล**: ผลลัพธ์ปรับสเกลได้ง่ายสำหรับปัญหาที่คล้ายคลึงกันทางเรขาคณิต
- **การปรับปรุงเงื่อนไขเชิงตัวเลข**: ค่าไร้มิติมักอยู่ในช่วง O(1) ซึ่งดีต่อ solver
- **การเปรียบเทียบโดยตรงกับการทดลอง**: สามารถเปรียบเทียบกับข้อมูลการทดลองได้โดยตรง

</details>

---

## ประเด็นสำคัญ (Key Takeaways)

> [!TIP] **แนวทางปฏิบัติที่ดีที่สุด**
> 1. **ประกาศมิติอย่างชัดเจนเสมอ** เมื่อสร้างฟิลด์หรือค่าคงที่
> 2. **ใช้ `dimensionSet::matches()`** สำหรับการตรวจสอบมิติในรันไทม์
> 3. **บันทึกสเกลอ้างอิง** เมื่อใช้รูปแบบไร้มิติ
> 4. **ให้ OpenFOAM จัดการการแปลงหน่วย** โดยอัตโนมัติผ่านระบบมิติ
> 5. **ทดสอบด้วยหน่วยที่ทราบ** เพื่อตรวจสอบการนำ solver ไปใช้

> [!WARNING] **ข้อควรระวังทั่วไป**
> - การผสมสัดส่วนปริมาตรไร้มิติ ($\alpha$) กับความหนาแน่นที่มีมิติ ($\rho$)
> - ลืมว่า `sin()`, `exp()`, `log()` ต้องการอาร์กิวเมนต์ไร้มิติ
> - สูญเสียข้อมูลมิติเมื่อนำ solver ไร้มิติไปใช้
> - มิติเงื่อนไขขอบเขตไม่ถูกต้องในไฟล์ case

ระบบการวิเคราะห์มิติใน OpenFOAM ให้ **รากฐานทางคณิตศาสตร์สำหรับการจำลอง CFD ที่เชื่อถือได้** มั่นใจได้ว่าทั้งความถูกต้องเชิงตัวเลขและความหมายทางฟิสิกส์จะถูกรักษาไว้ตลอดกระบวนการคำนวณ