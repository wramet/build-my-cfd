# ภาพรวม Boundary Conditions ใน OpenFOAM

**Boundary Condition** เป็นองค์ประกอบพื้นฐานในการจำลองพลศาสตร์ของไหลเชิงคำนวณ (Computational Fluid Dynamics หรือ CFD) ซึ่งกำหนดว่าคุณสมบัติของไหลมีพฤติกรรมอย่างไรที่ขอบเขตทางกายภาพของโดเมนการคำนวณ

> [!INFO] ความสำคัญของ Boundary Condition
> Boundary Condition มีความสำคัญอย่างยิ่งในการจำลอง CFD เนื่องจากเป็นตัวกำหนดว่าของไหลมีปฏิสัมพันธ์กับขอบเขตโดเมนอย่างไร การเลือก Boundary Condition ที่เหมาะสมมีอิทธิพลอย่างมากต่อความแม่นยำและความเสถียรของการคำนวณ

---

## ความสำคัญและบทบาทของ Boundary Condition

### บทบาทหลัก

**Boundary Condition** มีหน้าที่สำคัญหลายประการในการจำลอง CFD:

- **การบังคับใช้ข้อจำกัดทางกายภาพ**: เช่น เงื่อนไขไม่ลื่น (no-slip conditions) ที่ผนังแข็ง
- **การระบุแรงขับเคลื่อน**: เช่น การไล่ระดับความดัน (pressure gradients) หรือความเร็วขาเข้าที่กำหนด
- **การรับรองการอนุรักษ์มวล**: ผ่านเงื่อนไขทางเข้า/ออก (inlet/outlet conditions) ที่เหมาะสม
- **การสร้างผลเฉลยเอกลักษณ์**: ให้แผนการแยกส่วนเชิงตัวเลขสร้างผลลัพธ์ที่มีความหมายทางกายภาพ

### ปัญหาที่กำหนดไม่ดี (Ill-posed Problems)

หากไม่มีการกำหนด Boundary Condition ที่เหมาะสม การกำหนดสูตรทางคณิตศาสตร์จะไม่สมบูรณ์ นำไปสู่ปัญหาที่กำหนดไม่ดี (ill-posed problems) ซึ่งไม่สามารถหาผลเฉลยที่เป็นเอกลักษณ์ได้

---

## พื้นฐานทางคณิตศาสตร์ของ Boundary Conditions

สำหรับตัวแปร Field ทั่วไป $\phi$, Boundary Condition สามารถแบ่งออกได้เป็นสามประเภททางคณิตศาสตร์หลักๆ

---

### Dirichlet Boundary Conditions (Fixed Value)

**Dirichlet Boundary Condition** กำหนดค่าของตัวแปร Field โดยตรงที่พื้นผิวขอบเขต ในทางคณิตศาสตร์ สามารถแสดงได้ดังนี้:

$$\phi|_{\partial\Omega} = \phi_{\text{specified}}$$

*   $\phi$ แทนตัวแปร Field (เช่น องค์ประกอบความเร็ว, อุณหภูมิ หรือความดัน)
*   $\partial\Omega$ แสดงถึงขอบเขตของโดเมนการคำนวณ $\Omega$

#### ความหมายทางกายภาพ
การตีความทางกายภาพของ Dirichlet Condition คือ **ขอบเขตทำหน้าที่เป็นแหล่งกำเนิดหรือแหล่งรับ** ที่รักษาระดับตัวแปร Field ไว้ที่ค่าที่กำหนด โดยไม่คำนึงถึงผลลัพธ์ภายใน

#### OpenFOAM Code Implementation

```cpp
// Example in OpenFOAM dictionary format for velocity field
boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform (10 0 0);  // Fixed velocity vector in m/s
    }

    wallTemperature
    {
        type            fixedValue;
        value           uniform 300;       // Fixed temperature in Kelvin
    }
}
```

**เงื่อนไขเหล่านี้มักใช้สำหรับ:**

*   **ความเร็วขาเข้า (Inlet velocities)**: การกำหนดโปรไฟล์ความเร็วที่ทางเข้าของไหล
*   **อุณหภูมิผนัง (Wall temperatures)**: การกำหนดการกระจายตัวของอุณหภูมิบนพื้นผิวที่ถูกทำให้ร้อน/เย็น
*   **ค่าความเข้มข้น (Concentration values)**: การกำหนดความเข้มข้นของสปีชีส์ที่ขอบเขตการถ่ายโอนมวล

---

### Neumann Boundary Conditions (Fixed Gradient)

**Neumann Boundary Condition** กำหนด Normal Gradient ของตัวแปร Field ที่ขอบเขต ซึ่งเทียบเท่ากับการกำหนด Flux ที่ไหลผ่านขอบเขตนั้น การแสดงทางคณิตศาสตร์คือ:

$$\frac{\partial \phi}{\partial n}\bigg|_{\partial\Omega} = g_{\text{specified}}$$

*   $\frac{\partial}{\partial n}$ แทนอนุพันธ์ในทิศทาง Normal ไปยังขอบเขต
*   $g_{\text{specified}}$ คือค่า Gradient ที่กำหนด

#### ความสำคัญทางกายภาพ
ความสำคัญทางกายภาพของ Neumann Condition คือ **การควบคุมอัตราการเปลี่ยนแปลงของตัวแปร Field** ในทิศทาง Normal ไปยังขอบเขต ซึ่งเป็นการจัดการ Flux ที่ไหลผ่านพื้นผิวขอบเขตได้อย่างมีประสิทธิภาพ

#### OpenFOAM Code Implementation

```cpp
boundaryField
{
    outlet
    {
        type            fixedGradient;
        gradient        uniform (0 0 0);   // Zero gradient (fully developed flow)
    }

    heatFluxWall
    {
        type            fixedGradient;
        gradient        uniform 1000;      // Heat flux in W/m²
    }
}
```

**เงื่อนไข Zero Gradient (`zeroGradient`) มีความสำคัญอย่างยิ่งสำหรับ:**

*   **ขอบเขตทางออก (Outlet boundaries)**: การสมมติว่าการไหลพัฒนาเต็มที่ (fully developed flow) ซึ่งการเปลี่ยนแปลงตามทิศทางการไหลมีค่าน้อยมาก
*   **ระนาบสมมาตร (Symmetry planes)**: ที่ไม่มี Flux ไหลผ่านขอบเขตสมมาตร
*   **ผนังฉนวนความร้อน (Adiabatic walls)**: ที่ไม่มีการถ่ายเทความร้อน (Heat Flux)

> [!TIP] ผนัง Adiabatic
> สำหรับปัญหา Heat Transfer, เงื่อนไข $\frac{\partial T}{\partial n} = 0$ หมายความว่าไม่มีการถ่ายเทความร้อนผ่านขอบเขต หรือผนังเป็นฉนวนความร้อนแบบสมบูรณ์

---

### Mixed Boundary Conditions (Robin Conditions)

**Mixed Boundary Condition** รวมการกำหนดทั้งค่าและ Gradient ผ่านพารามิเตอร์การถ่วงน้ำหนัก Robin Boundary Condition แสดงได้ดังนี้:

$$\alpha \phi + \beta \frac{\partial \phi}{\partial n} = \gamma$$

*   $\alpha$, $\beta$ และ $\gamma$ เป็นสัมประสิทธิ์ที่กำหนดความสำคัญสัมพัทธ์ของพจน์ค่าและพจน์ Gradient

#### การประยุกต์ใช้สำคัญ - Newton's Cooling Law

$$-k\frac{\partial T}{\partial n} = h(T_s - T_\infty)$$

โดยที่:
* $k$ = Thermal Conductivity
* $h$ = Convective Heat Transfer Coefficient
* $T_s$ = Surface Temperature
* $T_\infty$ = Ambient Fluid Temperature

#### OpenFOAM Code Implementation

```cpp
boundaryField
{
    convectiveWall
    {
        type            mixed;
        refGradient     uniform 0;
        refValue        uniform 300;
        valueFraction   uniform 0.5;     // Weighting factor (0 = gradient, 1 = value)
    }
}
```

พารามิเตอร์ `valueFraction` ควบคุลการถ่วงน้ำหนัก:

*   `valueFraction = 1`: Dirichlet Condition บริสุทธิ์
*   `valueFraction = 0`: Neumann Condition บริสุทธิ์
*   `0 < valueFraction < 1`: Mixed Condition

**Boundary Condition นี้มีประโยชน์อย่างยิ่งสำหรับ:**

*   **การถ่ายเทความร้อนแบบ Conjugate (Conjugate heat transfer)**: ซึ่งทั้งอุณหภูมิและผลกระทบของ Heat Flux มีความสำคัญ
*   **ขอบเขตการแผ่รังสี (Radiation boundaries)**: ซึ่งการถ่ายเทความร้อนแบบแผ่รังสีเชื่อมโยงกับการถ่ายเทความร้อนแบบพา
*   **เงื่อนไขการลื่นบางส่วน (Partial slip conditions)**: ในพลศาสตร์ของก๊าซเจือจาง

---

## สถาปัตยกรรมของ Boundary Conditions ใน OpenFOAM

ใน OpenFOAM, Boundary Condition ถูกนำมาใช้ผ่านคลาส Field เฉพาะทางที่สืบทอดมาจากคลาสพื้นฐาน `fvPatchField` ซึ่งเป็นโครงสร้างที่แข็งแกร่งสำหรับการจัดการสถานการณ์ทางกายภาพต่างๆ ที่พบในการประยุกต์ใช้ทางวิศวกรรม

```mermaid
graph LR
    A["Base fvPatchField Class<br/>Abstract Field Boundary"] --> B["Basic Types"]
    A --> C["Derived Types"]
    A --> D["Specialized Types"]

    B --> B1["fixedValue<br/>φ = φ₀ (constant)"]
    B --> B2["fixedGradient<br/>∇φ⋅n = g₀ (constant)"]
    B --> B3["zeroGradient<br/>∇φ⋅n = 0"]
    B --> B4["calculated<br/>Computed from other fields"]

    C --> C1["timeVaryingFixedValue<br/>φ = f(t)"]
    C --> C2["timeVaryingUniformFixedValue<br/>φ = f(t) spatially uniform"]
    C --> C3["uniformFixedValue<br/>φ = constant (spatially)"]
    C --> C4["mixedFixedValue<br/>φ = λφ₀ + (1-λ)φ_boundary"]

    D --> D1["turbulentInlet<br/>Random fluctuations"]
    D --> D2["wallFunction<br/>Wall modeling"]
    D --> D3["codedFixedValue<br/>User-defined expression"]
    D --> D4["regionCoupled<br/>Multi-region transfer"]

    style A fill:#f5f5f5,stroke:#333,stroke-width:3px,color:#000
    style B fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000
    style C fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
    style D fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#000
    style B1 fill:#c8e6c9,stroke:#388e3c,stroke-width:1px,color:#000
    style B2 fill:#c8e6c9,stroke:#388e3c,stroke-width:1px,color:#000
    style B3 fill:#c8e6c9,stroke:#388e3c,stroke-width:1px,color:#000
    style B4 fill:#c8e6c9,stroke:#388e3c,stroke-width:1px,color:#000
    style C1 fill:#bbdefb,stroke:#1976d2,stroke-width:1px,color:#000
    style C2 fill:#bbdefb,stroke:#1976d2,stroke-width:1px,color:#000
    style C3 fill:#bbdefb,stroke:#1976d2,stroke-width:1px,color:#000
    style C4 fill:#bbdefb,stroke:#1976d2,stroke-width:1px,color:#000
    style D1 fill:#ffe0b2,stroke:#f57c00,stroke-width:1px,color:#000
    style D2 fill:#ffe0b2,stroke:#f57c00,stroke-width:1px,color:#000
    style D3 fill:#ffe0b2,stroke:#f57c00,stroke-width:1px,color:#000
    style D4 fill:#ffe0b2,stroke:#f57c00,stroke-width:1px,color:#000
```
> **Figure 1:** สถาปัตยกรรมของเงื่อนไขขอบเขตใน OpenFOAM แสดงโครงสร้างคลาสที่สืบทอดมาจาก `fvPatchField` โดยแบ่งออกเป็นประเภทพื้นฐาน (Basic), ประเภทที่เปลี่ยนแปลงตามเวลา (Derived) และประเภทเฉพาะทาง (Specialized) เพื่อรองรับสถานการณ์ทางกายภาพที่หลากหลาย


ระบบ Boundary Condition ของ OpenFOAM เป็นไปตามหลักการออกแบบเชิงวัตถุ (Object-Oriented Design) โดยมีความสัมพันธ์การสืบทอดที่ชัดเจน:

```
fvPatchField<Type> (Abstract base class)
├── fixedValueFvPatchField<Type>
├── fixedGradientFvPatchField<Type>
├── mixedFvPatchField<Type>
├── zeroGradientFvPatchField<Type>
├── calculatedFvPatchField<Type>
├── cyclicFvPatchField<Type>
├── processorFvPatchField<Type>
└── [Specialized derived classes]
```

### กลไกการเลือกขณะรันไทม์ (Runtime Selection Mechanism)

OpenFOAM ใช้กลไกการเลือกขณะรันไทม์ที่ช่วยให้สามารถระบุ Boundary Condition ในไฟล์ Dictionary ได้โดยไม่ต้องคอมไพล์โค้ดใหม่:

```cpp
// Runtime selection table registration
addToRunTimeSelectionTable
(
    fvPatchScalarField,
    fixedValueFvPatchField,
    dictionary
);
```

รูปแบบการออกแบบนี้ช่วยให้สามารถ:

*   **การเลือกแบบไดนามิก (Dynamic selection)**: Boundary Condition สามารถเปลี่ยนแปลงได้ขณะรันไทม์
*   **ความสามารถในการขยาย (Extensibility)**: สามารถเพิ่ม Boundary Condition ใหม่ได้โดยไม่ต้องแก้ไขโค้ดที่มีอยู่
*   **ความยืดหยุ่นของผู้ใช้ (User flexibility)**: พารามิเตอร์การจำลองสามารถแก้ไขได้ผ่านไฟล์ข้อความ

---

## Boundary Condition ขั้นสูงและพิเศษ

### Calculated Boundary Conditions

**Calculated Boundary Condition** คำนวณค่าโดยอิงจากผลลัพธ์ของ Field อื่นๆ หรือความสัมพันธ์ทางกายภาพ สิ่งเหล่านี้เป็นแบบไดนามิกและจะอัปเดตระหว่างการจำลองโดยอิงจากสถานะปัจจุบันของตัวแปรอื่นๆ

#### Wall Functions for Turbulence

**Wall Function** เป็นตัวเชื่อมช่องว่างระหว่างทฤษฎี Turbulence ที่ถูกจำกัดด้วยผนังและข้อจำกัดของ Computational Mesh

กฎ Logarithmic Law of the Wall สำหรับความเร็วคือ:

$$u^+ = \frac{1}{\kappa} \ln(y^+) + B$$

*   $u^+ = \frac{u}{u_\tau}$ คือความเร็วไร้มิติ
*   $y^+ = \frac{y u_\tau}{\nu}$ คือระยะห่างจากผนังไร้มิติ
*   $u_\tau = \sqrt{\frac{\tau_w}{\rho}}$ คือความเร็วเสียดทาน (friction velocity)
*   $\kappa \approx 0.41$ คือค่าคงที่ von Kármán
*   $B \approx 5.2$ คือค่าคงที่เชิงประจักษ์

#### OpenFOAM Code Implementation

```cpp
boundaryField
{
    wall
    {
        type            nutkWallFunction;
        value           uniform 0;
        Cmu             0.09;
        kappa           0.41;
        E               9.8;
    }
}
```

#### Pressure Boundary Conditions

เงื่อนไขความดันมักเกี่ยวข้องกับการคำนวณโดยอิงจาก Velocity Field หรือตัวแปรที่เชื่อมโยงอื่นๆ

**สำหรับการไหลที่อัดตัวไม่ได้ (Incompressible Flows):**

```cpp
boundaryField
{
    inlet
    {
        type            zeroGradient;      // For pressure at velocity inlet
    }

    outlet
    {
        type            fixedValue;
        value           uniform 0;         // Reference pressure (gauge)
    }
}
```

---

### Time-Varying Boundary Conditions

OpenFOAM รองรับ Time-Dependent Boundary Condition ที่ซับซ้อน:

#### การป้อนข้อมูลแบบตาราง (Tabular Data Input)

```cpp
boundaryField
{
    inlet
    {
        type            uniformFixedValue;
        uniformValue    table
        (
            (0     (1 0 0))    // Time = 0s, velocity = (1,0,0) m/s
            (10    (2 0 0))    // Time = 10s, velocity = (2,0,0) m/s
            (20    (1.5 0 0))  // Time = 20s, velocity = (1.5,0,0) m/s
        );
    }
}
```

#### ฟังก์ชันทางคณิตศาสตร์ (Mathematical Functions)

```cpp
boundaryField
{
    pulsatingInlet
    {
        type            codedFixedValue;
        value           uniform (0 0 0);
        code
        #{
            // Sinusoidal velocity variation
            scalar t = this->db().time().value();
            vectorField& field = *this;
            field = vector(1.0 + 0.5*sin(2*pi*0.1*t), 0, 0);
        #};
    }
}
```

---

### Coupled Boundary Conditions

#### Cyclic Boundary Conditions

**Cyclic Boundary** เชื่อมต่อ Patch ขอบเขตสองส่วนที่แตกต่างกัน โดยบังคับใช้ความต่อเนื่องของค่า Field:

```cpp
boundaryField
{
    cyclic1
    {
        type            cyclic;
        value           uniform 0;
    }

    cyclic2
    {
        type            cyclic;
        value           uniform 0;
    }
}
```

สำหรับ Field $\phi$ ที่ใช้กับ Cyclic Boundary Conditions:
$$\phi_{\text{patch A}}(\mathbf{x}) = \phi_{\text{patch B}}(\mathbf{T}(\mathbf{x}))$$

โดยที่:
- $\mathbf{T}$ = การแปลงทางเรขาคณิตที่แมปพิกัดจาก Patch A ไปยัง Patch B
- $\phi$ = Field ที่ถูกบังคับใช้เงื่อนไข

#### Processor Boundaries

สำหรับการคำนวณแบบขนาน, Processor Boundary จะจัดการการสื่อสารระหว่างโดเมนการคำนวณที่แตกต่างกัน:

```cpp
boundaryField
{
    procBoundary0to1
    {
        type            processor;
        myProcessNo     0;
        neighbProcessNo 1;
        value           uniform 0;
    }
}
```

---

## สรุปประเภท Boundary Condition ทั่วไปใน OpenFOAM

| Boundary Condition Type | Mathematical Form | Physical Meaning | Common Applications |
|------------------------|-------------------|------------------|-------------------|
| **fixedValue** | $\phi|_{\partial\Omega} = \phi_{\text{specified}}$ | Direct value specification | Inlet velocity, wall temperature, concentration |
| **fixedGradient** | $\frac{\partial \phi}{\partial n}\bigg|_{\partial\Omega} = g_{\text{specified}}$ | Flux specification | Outlet flow, heat flux, symmetry |
| **zeroGradient** | $\frac{\partial \phi}{\partial n}\bigg|_{\partial\Omega} = 0$ | Zero flux condition | Fully developed flow, adiabatic walls |
| **mixed** | $\alpha \phi + \beta \frac{\partial \phi}{\partial n} = \gamma$ | Weighted value-gradient combination | Conjugate heat transfer, partial slip |
| **cyclic** | $\phi_1 = \phi_2$ | Field continuity across patches | Rotational symmetry, periodic domains |
| **processor** | MPI communication | Parallel domain coupling | Distributed computing |
| **noSlip** | $\mathbf{u} = \mathbf{0}$ | Zero velocity at wall | Viscous flow walls |
| **slip** | $\mathbf{u} \cdot \mathbf{n} = 0$ | Zero normal velocity | Inviscid walls, symmetry |
| **inletOutlet** | Switches based on flux | Direction-dependent condition | Outlets with potential backflow |

---

## แนวทางการเลือก Boundary Condition

### Inlet Boundary

| Variable | Recommended BC | หมายเหตุ |
|----------|----------------|-----------|
| **Velocity** | `fixedValue` | เมื่อทราบ Velocity Profile ของ Inlet |
| **Pressure** | `zeroGradient` | เพื่อให้ Pressure พัฒนาขึ้นตามธรรมชาติ |
| **Turbulence** | `fixedValue` | Turbulence Intensity 1-5% |

### Outlet Boundary

| Variable | Recommended BC | หมายเหตุ |
|----------|----------------|-----------|
| **Velocity** | `pressureInletOutletVelocity` หรือ `zeroGradient` | ขึ้นอยู่กับลักษณะการไหล |
| **Pressure** | `fixedValue` | โดยทั่วไป 0 (Gauge pressure) |
| **Turbulence** | `zeroGradient` | สำหรับ Developed Flow |

### Wall Boundary

| Variable | Recommended BC | หมายเหตุ |
|----------|----------------|-----------|
| **Velocity** | `noSlip` (viscous) หรือ `slip` (inviscid) | ขึ้นอยู่กับลักษณะการไหล |
| **Pressure** | `zeroGradient` | สำหรับกรณีส่วนใหญ่ |
| **Temperature** | `fixedValue` หรือ `fixedGradient` | ขึ้นอยู่กับเงื่อนไขความร้อน |
| **Turbulence** | Wall Function | เพื่อหลีกเลี่ยงการปรับ Mesh ที่มากเกินไป |

---

## ข้อควรพิจารณาสำคัญ

> [!WARNING] ความสอดคล้องของ Boundary Condition
> การเลือกและการนำ Boundary Condition ไปใช้อย่างเหมาะสมเป็นพื้นฐานสำคัญสำหรับการจำลอง CFD ที่แม่นยำ เนื่องจากมีอิทธิพลอย่างมากต่อ:
> - **Flow Physics** - ลักษณะการไหลที่เป็นจริง
> - **Solution Stability** - ความเสถียรของการคำนวณ
> - **Convergence** - การลู่เข้าสู่คำตอบ
> - **Physical Accuracy** - ความถูกต้องทางกายภาพ

### ปัญหาที่พบบ่อย

| Symptom | Probable Cause | Solution |
| :--- | :--- | :--- |
| **Divergence ที่ Inlet** | U และ p ไม่สอดคล้องกัน | ตรวจสอบ: หาก U ถูกกำหนดค่าตายตัว (fixed), p ควรเป็น zeroGradient (โดยปกติ) |
| **Inflow ที่ Outlet** | Vortices พุ่งชน Outlet | ใช้ `inletOutlet` หรือขยาย Domain ปลายน้ำ |
| **High Velocity ที่ Wall** | ประเภท BC ผิด | ตรวจสอบให้แน่ใจว่าใช้ `noSlip` หรือ `fixedValue (0 0 0)` |
| **Pressure Drifting** | Boundary Condition ประเภท Neumann ทั้งหมด | กำหนดค่าความดันที่จุดใดจุดหนึ่ง (Reference Pressure) หรือที่ Patch ใด Patch หนึ่ง |

---

## บทสรุป

**Boundary Condition** เป็นองค์ประกอบพื้นฐานและสำคัญที่สุดในการจำลอง CFD ใน OpenFOAM ซึ่ง:

1. **การเลือก Boundary Condition ที่เหมาะสม** สำคัญต่อความแม่นยำและความเสถียรของ CFD Simulations

2. **การจำแนกเป็น Dirichlet, Neumann, และ Robin** เป็นกรอบทางคณิตศาสตร์ที่รับประกัน Well-Posed Problems

3. **การประยุกต์ใช้ใน OpenFOAM** ต้องคำนึงถึง Physical Meaning และ Numerical Stability

4. **Boundary Conditions ขั้นสูง** ช่วยแก้ไขปัญหาที่ซับซ้อนใน Multiphysics และ Special Applications

การเข้าใจและการนำ Boundary Conditions ไปใช้งานอย่างถูกต้องเป็นพื้นฐานสำคัญสำหรับการสร้าง CFD Simulations ที่แม่นยำและเชื่อถือได้ใน OpenFOAM
