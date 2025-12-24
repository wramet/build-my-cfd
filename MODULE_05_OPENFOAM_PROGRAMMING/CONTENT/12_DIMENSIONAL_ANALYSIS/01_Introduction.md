# บทนำเกี่ยวกับการวิเคราะห์มิติ

![[physics_referee_dimensions.png]]
`A futuristic referee (The OpenFOAM Core) holding a magnifying glass over a physics equation. Each term in the equation is glowing with its unit (e.g., m/s²). If all units match, a green checkmark appears. If they don't, a red warning light flashes, scientific textbook diagram, clean vector line art, white background, high definition, flat design, educational infographic --ar 16:9`

จินตนาการว่าคุณกำลังสร้างสะพานและผสมหน่วยเมตริกและอิมพีเรียลโดยไม่ตั้งใจ: สกรูวัดเป็นนิ้ว แรงวัดเป็นนิวตัน และความเครียดวัดเป็น psi ผลลัพธ์จะเป็นความล้มเหลวอย่างร้ายแรง ระบบการวิเคราะห์มิติของ OpenFOAM ทำหน้าที่เป็น **การตรวจสอบหน่วย** สำหรับสมการ CFD ของคุณ โดยจับความไม่ตรงกันของหน่วยก่อนที่จะสร้างผลลัพธ์ที่ไม่สมเหตุสมผล

## 🔍 ตาข่ายนิรภัยของวิศวกร (The Safety Net)

```mermaid
graph LR
    C[Convection: m/s²] -- "Check" --> Match{Consistency}
    D[Diffusion: m/s²] -- "Check" --> Match
    S[Source: m/s²] -- "Check" --> Match

    Match -- "OK" --> Run[Simulation Starts]
    Match -- "Fail" --> Error[Fatal Error: Incompatible Units]

    style Match fill:#e8f5e9,stroke:#2e7d32
    style Error fill:#ffebee,stroke:#c62828
```
> **Figure 1:** แผนภาพ "ตาข่ายนิรภัย" ของวิศวกร ซึ่งแสดงให้เห็นว่าระบบจะบล็อกการจำลองทันทีหากพบว่าเทอมต่างๆ ในสมการมีหน่วยที่ไม่สอดคล้องกันความปลอดภัยทางฟิสิกส์ไม่ส่งผลกระทบต่อความเร็วในการจำลอง ผ่านการใช้พลังของ C++ Template Metaprogramming ในการตรวจสอบความสอดคล้องทางมิติทั้งหมดที่ขั้นตอนการคอมไพล์โปรแกรมเพียงครั้งเดียว

![[of_unit_consistency_check.png]]
`A flowchart of the unit consistency check process: comparing dimensions of terms in a transport equation and triggering a Fatal Error if a mismatch is detected, scientific textbook diagram, clean vector line art, white background, high definition, flat design, educational infographic --ar 16:9`

ในการคำนวณ CFD ที่ซับซ้อน เรามักต้องจัดการกับสมการที่มีพจน์จำนวนมาก:
-   เทอม Convection (m/s²)
-   เทอม Diffusion (m/s²)
-   เทอม Source (m/s²)

หากคุณลืมหารด้วยพื้นที่หรือคูณด้วยเวลาในบางพจน์ หน่วยของพจน์นั้นจะเปลี่ยนไปทันที ในซอฟต์แวร์อื่น คุณอาจไม่รู้ตัวจนกระทั่งผลลัพธ์ลู่ออก (Diverge) แต่ใน OpenFOAM **โปรแกรมจะหยุดรันและบอกสาเหตุทันที**

### สถาปัตยกรรมระบบมิติของ OpenFOAM

OpenFOAM ใช้ความสม่ำเสมอทางมิติผ่านส่วนประกอบหลักหลายอย่าง:

**คลาส dimensionSet**: โครงสร้างข้อมูลหลักที่แสดงมิติทางกายภาพโดยใช้หน่วยฐาน SI:

| หน่วยฐาน | สัญลักษณ์ | คำอธิบาย |
|------------|------------|------------|
| มวล | $M$ | Mass |
| ความยาว | $L$ | Length |
| เวลา | $T$ | Time |
| อุณหภูมิ | $\Theta$ | Temperature |
| ปริมาณของสาร | $N$ | Amount of substance |
| กระแสไฟฟ้า | $I$ | Electric current |
| ความเข้มแสง | $J$ | Luminous intensity |

**dimensionedScalar/vector/tensor**: คลาสเทมเพลตที่รวมค่ากับมิติของพวกมัน:

```cpp
// Example from OpenFOAM source code
// Pressure field with dimensions (M·L⁻¹·T⁻²)
dimensionedScalar p("p", dimPressure, 101325.0);  // Pressure in Pascals

// Velocity vector field with dimensions (L·T⁻¹)
dimensionedVector U("U", dimVelocity, vector(1.0, 0, 0));  // Velocity vector
```

> **📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/populationBalanceModel/populationBalanceModel/populationBalanceModel.C`  
> 
> **คำอธิบาย:** โค้ดตัวอย่างนี้แสดงการประกาศ `dimensionedScalar` และ `dimensionedVector` ซึ่งเป็นคลาสพื้นฐานของ OpenFOAM ที่ใช้สำหรับเก็บค่าทางกายภาพพร้อมกับข้อมูลมิติ (dimensions) ของปริมาณนั้นๆ  
> 
> **แนวคิดสำคัญ:**
> - **dimensionedScalar**: เก็บค่าสเกลาร์ (เช่น ความดัน อุณหภูมิ) พร้อมมิติ
> - **dimensionedVector**: เก็บค่าเวกเตอร์ (เช่น ความเร็ว) พร้อมมิติ
> - **dimPressure, dimVelocity**: ค่าคงที่ที่กำหนดมิติไว้ล่วงหน้า
> - การกำหนดมิติทำให้คอมไพเลอร์สามารถตรวจสอบความสอดคล้องของหน่วยได้

### รากฐาน: ความสม่ำเสมอทางมิติในฟิสิกส์

หลักการของความเป็นเนื้อเดียวกันทางมิติระบุว่าเทอมทั้งหมดในสมการที่มีความหมายทางกายภาพต้องมีมิติที่เหมือนกัน แนวคิดพื้นฐานนี้ ซึ่งเป็นทางการครั้งแรกโดย Fourier ในปี 1822 เป็นสิ่งจำเป็นเพราะ:

- **ความหมายทางกายภาพ**: เฉพาะปริมาณที่มีมิติเหมือนกันเท่านั้นที่สามารถเปรียบเทียบ บวก หรือเท่ากันได้อย่างมีความหมาย
- **ความไม่ขึ้นกับสเกล**: กฎฟิสิกส์ต้องทำงานไม่ว่าจะเลือกหน่วยใด
- **การตรวจจับข้อผิดพลาด**: การวิเคราะห์มิติให้วิธีการเป็นระบบในการตรวจสอบความถูกต้องของสมการ

### การวิเคราะห์มิติในการใช้งานจริง

พิจารณาสมการ Navier-Stokes สำหรับการไหลแบบไม่บีบอัด:
$$\rho \frac{\partial \mathbf{u}}{\partial t} + \rho (\mathbf{u} \cdot \nabla) \mathbf{u} = -\nabla p + \mu \nabla^2 \mathbf{u} + \mathbf{f}$$

มาตรวจสอบความสม่ำเสมอทางมิติเป็นเทอมๆ:

**เทอมชั่วคราว**: $\rho \frac{\partial \mathbf{u}}{\partial t}$
- $\rho$: $M/L^3$ (ความหนาแน่น)
- $\frac{\partial \mathbf{u}}{\partial t}$: $(L/T)/T = L/T^2$ (ความเร่ง)
- **ผลลัพธ์**: $M/L^3 × L/T^2 = M/(L^2·T^2)$

**เทอมพาพลศาสตร์**: $\rho (\mathbf{u} \cdot \nabla) \mathbf{u}$
- $(\mathbf{u} \cdot \nabla)$: $(L/T) × (1/L) = 1/T$
- $\mathbf{u}$: $L/T$
- **ผลลัพธ์**: $\rho × 1/T × L/T = M/(L^2·T^2)$

**การไล่ระดับความดัน**: $-\nabla p$
- $\nabla$: $1/L$
- $p$: $M/(L·T^2)$
- **ผลลัพธ์**: $1/L × M/(L·T^2) = M/(L^2·T^2)$

เทอมทั้งหมดมีมิติเหมือนกัน ซึ่งยืนยันความสม่ำเสมอทางมิติของสมการ

### ความสำคัญของการวิเคราะห์มิติ

การวิเคราะห์มิติเป็นเครื่องมือพื้นฐานในพลศาสตร์ของไหลเชิงคำนวณที่ทำให้มั่นใจได้ถึงความสอดคล้องทางคณิตศาสตร์และความเป็นจริงทางกายภาพในการจำลองเชิงตัวเลข

- **ความสอดคล้องทางกายภาพ**: ทำให้มั่นใจได้ว่าสมการทั้งหมดยังคงสมดุลมิติที่เหมาะสม
- **การป้องกันข้อผิดพลาด**: ตรวจจับข้อผิดพลาดที่เกี่ยวข้องกับหน่วยก่อนที่จะทำลายผลลัพธ์การจำลอง
- **การตรวจสอบ**: ให้การตรวจสอบเพิ่มเติมสำหรับ schemes เชิงตัวเลข
- **การดีบัก**: ช่วยระบุแหล่งที่มาของความไม่เสถียรเชิงตัวเลขหรือผลลัพธ์ที่ไม่เป็นไปตามกายภาพ

### ประโยชน์ของการนำไปใช้

**การตรวจจับข้อผิดพลาดยาว**: การตรวจสอบมิติของ OpenFOAM เกิดขึ้นในเวลาคอมไพล์สำหรับนิพจน์คงที่และในเวลาทำงานสำหรับการดำเนินการฟิลด์

```cpp
// This will fail to compile - dimension mismatch error
// Velocity (L/T) cannot be added to Pressure (M·L⁻¹·T⁻²)
dimensionedScalar invalidSum = U + p;  // Error: dimensions don't match

// Correct approach: only add quantities with same dimensions
dimensionedScalar velocitySum = U + U;  // OK: both have velocity dimensions
```

> **📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.C`  
> 
> **คำอธิบาย:** ตัวอย่างนี้แสดงให้เห็นถึงประสิทธิภาพของระบบตรวจสอบมิติของ OpenFOAM ที่สามารถจับข้อผิดพลาดได้ตั้งแต่ขั้นตอนการคอมไพล์ การพยายามบวกปริมาณที่มีมิติต่างกัน (เช่น ความเร็วกับความดัน) จะทำให้เกิด compile-time error  
> 
> **แนวคิดสำคัญ:**
> - **Compile-time checking**: ตรวจสอบความสอดคล้องของมิติขณะคอมไพล์
> - **Type safety**: ระบบ type ของ C++ ทำงานร่วมกับระบบมิติ
> - **Prevents runtime errors**: ลดโอกาสเกิดข้อผิดพลาดขณะรันโปรแกรม
> - **Documentation**: โค้ดที่มีการระบุมิติช่วยอธิบายความหมายทางกายภาพ

**เอกสารผ่านมิติ**: ทุกฟิลด์จะพกความหมายทางกายภาพโดยอัตโนมัติ ทำให้โค้ดเป็นเอกสารได้ด้วยตนเอง:

```cpp
// Temperature field - automatically has dimTemperature
volScalarField T(io, "T", mesh);  

// Velocity field - automatically has dimVelocity  
volVectorField U(io, "U", mesh);

// Pressure field - automatically has dimPressure
volScalarField p(io, "p", mesh);
```

> **📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/populationBalanceModel/populationBalanceModel/populationBalanceModel.C`  
> 
> **คำอธิบาย:** OpenFOAM ใช้กลไกการค้นหาจากฐานข้อมูล (database lookup) เพื่อกำหนดมิติให้กับฟิลด์โดยอัตโนมัติ เมื่อฟิลด์ถูกสร้างด้วยชื่อที่รู้จัก (เช่น "T", "U", "p") ระบบจะกำหนดมิติที่ถูกต้องให้  
> 
> **แนวคิดสำคัญ:**
> - **Automatic dimension assignment**: กำหนดมิติอัตโนมัติจากชื่อฟิลด์
> - **volScalarField**: ฟิลด์สเกลาร์บนพื้นที่ควบคุม (control volume)
> - **volVectorField**: ฟิลด์เวกเตอร์บนพื้นที่ควบคุม
> - **Self-documenting code**: ชื่อฟิลด์บอกความหมายและมิติ
> - **Database lookup**: ใช้ข้อมูลจากฐานข้อมูล OpenFOAM

**ความยืดหยุ่นของระบบหน่วย**: OpenFOAM แปลงระหว่างหน่วยที่เข้ากันได้โดยอัตโนมัติในขณะที่รักษาความสม่ำเสมอทางมิติ:

```cpp
// Pressure in psi (pounds per square inch)
dimensionedScalar p_in_psi("p", dimPressure, 14.7);  

// Automatic conversion to Pascals for internal calculations
dimensionedScalar p_in_pa = p_in_psi;  // Converts to Pa automatically
```

> **📂 Source:** `.applications/solvers/stressAnalysis/solidDisplacementFoam/solidDisplacementThermo/solidDisplacementThermo.C`  
> 
> **คำอธิบาย:** OpenFOAM รองรับการทำงานกับหลายหน่วยผ่านกลไกการแปลงอัตโนมัติ ผู้ใช้สามารถระบุค่าในหน่วยใดก็ได้ที่เข้ากันได้ และระบบจะแปลงเป็นหน่วยฐาน SI สำหรับการคำนวณภายใน  
> 
> **แนวคิดสำคัญ:**
> - **Unit conversion**: แปลงหน่วยอัตโนมัติเป็น SI
> - **dimension consistency**: รักษาความสอดคล้องของมิติ
> - **User flexibility**: รองรับหลายหน่วยใน input
> - **Internal standardization**: ใช้หน่วย SI ภายในระบบ
> - **Physical accuracy**: ลดความผิดพลาดจากการแปลงหน่วย

### การผสานรวมหลายฟิสิกส์

ในการจำลองหลายฟิสิกส์ การวิเคราะห์มิติกลายเป็นสิ่งสำคัญสำหรับการผสานปรากฏการณ์ทางกายภาพที่แตกต่างกัน:

**การถ่ายเทความร้อน**: สมการพลังงาน
$$\rho c_p \frac{\partial T}{\partial t} + \rho c_p \mathbf{u} \cdot \nabla T = k \nabla^2 T + Q$$

- **ตัวแปร:**
  - $\rho$: $M/L^3$ (ความหนาแน่น)
  - $c_p$: $L^2/(T^2·\Theta)$ (ความจุความร้อนค่าคงที่)
  - $T$: $\Theta$ (อุณหภูมิ)
  - $\mathbf{u}$: $L/T$ (ความเร็ว)
  - $k$: $M·L/(T^3·\Theta)$ (ความนำความร้อน)
  - $Q$: $M/(L·T^3)$ (แหล่งความร้อน)

- **เทอมทั้งหมดต้องมีหน่วยของ** $M/(L·T^3)$ (พลังงานต่อปริมาตรต่อหน่วยเวลา)
- นี่ทำให้มั่นใจในการผสานรวมที่เหมาะสมระหว่างฟิลด์ความเร็ว ($\mathbf{u}$) และฟิลด์อุณหภูมิ ($T$)

**การไหลหลายเฟส**: การขนส่งปริมาตรสัดส่วน
$$\frac{\partial \alpha}{\partial t} + \mathbf{u} \cdot \nabla \alpha = 0$$

- $\alpha$ ไม่มีมิติ (ปริมาตรสัดส่วน, $0 \leq \alpha \leq 1$)
- **เทอมทั้งหมดต้องไม่มีมิติ** ป้องกันการผสมกับปริมาณที่มีมิติ

```cpp
// Volume fraction field for multiphase flow
// dimensionless: represents phase fraction (0 to 1)
volScalarField alpha
(
    IOobject("alpha", runTime.timeName(), mesh),
    mesh,
    dimensionedScalar("alpha", dimless, 0.0)
);

// Dilatation error field for volume conservation
// dimensions: T⁻¹ (inverse time)
volScalarField dilatationError
(
    IOobject("dilatationError", runTime.timeName(), mesh),
    mesh,
    dimensionedScalar(inv(dimTime), 0)  // 1/T
);
```

> **📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/populationBalanceModel/populationBalanceModel/populationBalanceModel.C`  
> 
> **คำอธิบาย:** ในการไหลหลายเฟส ปริมาตรสัดส่วน (volume fraction) α เป็นปริมาณไร้มิติที่ระบุสัดส่วนของแต่ละเฟสในเซลล์ นอกจากนี้ ยังมีการตรวจสอบการอนุรักษ์ปริมาตรผ่าน dilatation error ที่มีมิติเป็น 1/T  
> 
> **แนวคิดสำคัญ:**
> - **Volume fraction (α)**: ปริมาณไร้มิติ (0 ≤ α ≤ 1)
> - **dimless**: ค่าคงที่สำหรับปริมาณไร้มิติ
> - **Dilatation error**: วัดความไม่สอดคล้องของปริมาตร
> - **inv(dimTime)**: ฟังก์ชันสร้างมิติย้อนกลับ (1/T)
> - **Multiphase conservation**: ตรวจสอบการอนุรักษ์มวล

### อันตรายทั่วไปและวิธีแก้ไข

**การทำให้ไม่มีมิติ**: บทความวิจัยจำนวนมากใช้สมการที่ไม่มีมิติ ระบบมิติของ OpenFOAM ต้องการการนำไปใช้อย่างระมัดระวัง:

```cpp
// ❌ BAD PRACTICE - loses dimensional information
dimensionedScalar Re("Re", dimless, 1000.0);  // Reynolds number

// ✅ BETTER APPROACH - preserve dimensional form
dimensionedScalar U_ref("U_ref", dimVelocity, 1.0);      // m/s
dimensionedScalar L_ref("L_ref", dimLength, 1.0);        // m
dimensionedScalar nu_ref("nu_ref", dimKinematicViscosity, 1e-6);  // m²/s

// Calculate dimensionless number from dimensional quantities
dimensionedScalar Re = U_ref * L_ref / nu_ref;
```

> **📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/multiphaseCompressibleMomentumTransportModels/kineticTheoryModels/kineticTheoryModel/kineticTheoryModel.C`  
> 
> **คำอธิบาย:** แนวทางปฏิบัติที่ดีคือการรักษาค่าอ้างอิงให้มีมิติจริง แล้วคำนวณจำนวนไร้มิติ (เช่น Reynolds number) จากค่าเหล่านั้น วิธีนี้ช่วยรักษาข้อมูลทางกายภาพและทำให้สามารถตรวจสอบความถูกต้องได้  
> 
> **แนวคิดสำคัญ:**
> - **Preserve dimensions**: รักษามิติของค่าอ้างอิง
> - **Calculate dimensionless numbers**: คำนวณจากค่าที่มีมิติ
> - **Traceability**: สามารถติดตามที่มาของค่าได้
> - **Physical meaning**: ค่ามีความหมายทางกายภาพชัดเจน
> - **Validation**: ตรวจสอบความถูกต้องได้ง่ายขึ้น

**ฟังก์ชันที่ผู้ใช้กำหนด**: เมื่อสร้างเงื่อนไขขอบเขตหรือโมเดลแบบกำหนดเอง การระบุมิติที่เหมาะสมเป็นสิ่งสำคัญ:

```cpp
// Custom boundary condition example
class MyBoundaryCondition : public fvPatchField<scalar>
{
    // Constructor must specify dimensions
    MyBoundaryCondition
    (
        const fvPatch& p,
        const DimensionedField<scalar, volMesh>& iF,
        const dictionary& dict
    )
    :
        // Correctly specify dimensionless field
        fvPatchField<scalar>(p, iF, dict, dimless)
    {}
    
    // Alternative: for dimensional quantities
    // fvPatchField<scalar>(p, iF, dict, dimPressure)  // For pressure BC
};
```

> **📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/ThermalPhaseChangePhaseSystem/ThermalPhaseChangePhaseSystem.C`  
> 
> **คำอธิบาย:** เมื่อสร้างเงื่อนไขขอบเขตแบบกำหนดเอง ผู้พัฒนาต้องระบุมิติที่ถูกต้องใน constructor ของคลาส สิ่งนี้สำคัญเพื่อให้แน่ใจว่าฟิลด์มีความสอดคล้องกับสมการฟิสิกส์  
> 
> **แนวคิดสำคัญ:**
> - **Constructor initialization**: ระบุมิติใน constructor
> - **fvPatchField**: คลาสฐานสำหรับเงื่อนไขขอบเขต
> - **Dimension consistency**: ต้องระบุมิติที่ถูกต้อง
> - **Type safety**: ระบบ type ช่วยป้องกันข้อผิดพลาด
> - **Inheritance**: สืบทอดจากคลาสฐานของ OpenFOAM

### การพิจารณาประสิทธิภาพ

การตรวจสอบมิติของ OpenFOAM ถูกนำไปใช้อย่างมีประสิทธิภาพ:

| ช่วงเวลา | การตรวจสอบ | โอเวอร์เฮด |
|------------|------------|------------|
| เวลาคอมไพล์ | ความสม่ำเสมอทางมิติสำหรับค่าคงที่และนิพจน์ | เล็กน้อย |
| เวลาทำงาน | โอเวอร์เฮดน้อยมากสำหรับการดำเนินการฟิลด์ | ส่วนใหญ่ในระหว่างการเริ่มต้น |
| การเพิ่มประสิทธิภาพ | คอมไพเลอร์จะลบการตรวจสอบมิติในบิลด์รีลีส | ไม่มีในบิลด์รีลีส |

**โอเวอร์เฮดหน่วยความจำ**: น้อยมาก - แต่ละประเภทที่มีมิติจัดเก็บข้อมูลมิติเพียงครั้งเดียว โดยค่าฟิลด์จัดเก็บข้อมูลตัวเลขจริง

### บทสรุป: นอกเหนือจากการตรวจจับข้อผิดพลาด

ในขณะที่ประโยชน์หลักของระบบการวิเคราะห์มิติของ OpenFOAM คือการป้องกันข้อผิดพลาด มันให้คุณค่าเพิ่มเติม:

1. **ความชัดเจนของโค้ด**: มิติทำหน้าที่เป็นเอกสารฝังตัว
2. **สัญชาตญาณทางกายภาพ**: นักพัฒนายังคงรับรู้ถึงความหมายทางกายภาพ
3. **ความไม่ขึ้นกับหน่วย**: โค้ดทำงานอย่างสม่ำเสมอไม่ว่าหน่วยอินพุตจะเป็นอย่างไร
4. **ความปลอดภัยหลายฟิสิกส์**: ป้องกันการผสมนวนปริมาณทางกายภาพที่ไม่เข้ากัน

แนวทางเชิงระบบนี้ในการรักษาความสม่ำเสมอทางมิติทำให้ OpenFOAM โดยเฉพาะอย่างยิ่งแข็งแกร่งสำหรับการจำลองหลายฟิสิกส์ที่ซับซ้อน ซึ่งการตรวจสอบด้วยตนเองจะไม่เป็นไปได้และมีแนวโน้มที่จะผิดพลาด

## 🎯 ขอบเขตของบทนี้

เราจะไม่ได้ศึกษาแค่ว่า "เมตรบวกเมตรได้เมตร" แต่เราจะดูไปถึง:
-   การจัดเก็บเลขชี้กำลังแบบบิต (Bit-level storage)
-   การคำนวณหน่วยในเทมเพลตนิพจน์ (Expression Templates)
-   การทำให้สมการไร้มิติ (Non-dimensionalization) เพื่อเพิ่มความแม่นยำทางตัวเลข

การเชี่ยวชาญการวิเคราะห์มิติจะเปลี่ยนคุณจาก "คนเขียนโค้ด" ให้กลายเป็น "วิศวกรจำลองสถานการณ์" ที่มีความเป็นมืออาชีพสูง