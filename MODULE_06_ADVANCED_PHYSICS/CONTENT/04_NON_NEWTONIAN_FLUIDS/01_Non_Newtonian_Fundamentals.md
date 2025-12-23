# 01. พื้นฐานของไหลนอนนิวตัน (Non-Newtonian Fundamentals)

## 1. บทนำ: ปัญหาทาง Rheological

ทำไมขวดซอสมะเขือเทศถึงไหลยากในตอนแรก แต่พอเขย่าหรือตีแรงๆ แล้วไหลลื่น? หรือทำไมน้ำผึ้งถึงไหลหนืดเท่าเดิมเสมือไม่ว่าจะกวนแรงแค่ไหน?

ความแตกต่างพื้นฐานระหว่างของไหลแบบ **นิวตัน (Newtonian)** และ **นอนนิวตัน (Non-Newtonian)** อยู่ที่พฤติกรรมความหนืดของพวกมัน:

*   **ของไหลนิวตัน (เช่น น้ำ, อากาศ):** มีค่าความหนืด $\mu$ คงที่ ไม่ว่าจะได้รับแรงเฉือนมากแค่ไหน
*   **ของไหลนอนนิวตัน (เช่น เลือด, ซอส, สี):** มีค่าความหนืดที่เปลี่ยนแปลงตามสภาวะการไหล โดยเฉพาะ **อัตราการเฉือน (Shear Rate, $\dot{\gamma}$)**

> [!INFO] ความท้าทายทาง CFD
> ของไหลที่ไม่ใช่แบบนิวตันซึ่งมีค่าความหนืดเปลี่ยนแปลงตามอัตราการเฉือน—ก่อให้เกิดความท้าทายพื้นฐานสำหรับ CFD เนื่องจากความไม่เชิงเส้น (Non-linearity) ที่รุนแรงในสมการโมเมนตัม

OpenFOAM ตอบสนองความท้าทายนี้ด้วย **สถาปัตยกรรมแบบขยายได้ที่ใช้รูปแบบ Factory** ซึ่งให้คุณสลับไปมาระหว่างรุ่น Bird-Carreau, Herschel-Bulkley, Power-Law และแบบจำลอง rheological อื่นๆ โดยการเปลี่ยน dictionary entry เพียงรายการเดียว

---

## 2. กรอบทางคณิตศาสตร์

ใน OpenFOAM โมเดลเหล่านี้ถูก Implement ผ่านสมการเชิงโครงสร้าง (Constitutive Equation):

$$\boldsymbol{\tau} = \mu(\dot{\gamma}) \cdot \dot{\boldsymbol{\gamma}}$$

โดยที่:
- $\boldsymbol{\tau}$ คือเทนเซอร์ความเค้น (Stress Tensor)
- $\mu(\dot{\gamma})$ คือความหนืดปรากฏ (Apparent Viscosity) ที่ขึ้นกับอัตราการเฉือน
- $\dot{\boldsymbol{\gamma}}$ คือเทนเซอร์อัตราการเสียรูป (Rate-of-deformation Tensor)

![[shear_deformation_tensor.png]]

### ขนาดของอัตราการเฉือน (Shear Rate Magnitude)

อัตราการเฉือน $\dot{\gamma}$ คือค่าสเกลาร์ที่บอกความแรงของการเสียรูปในของไหล คำนวณจาก Invariant ที่สองของเทนเซอร์อัตราการเสียรูป $\mathbf{D}$:

$$\mathbf{D} = \frac{1}{2}\left(\nabla \mathbf{u} + (\nabla \mathbf{u})^T\right)$$

$$\dot{\gamma} = \sqrt{2\mathbf{D}:\mathbf{D}} = \sqrt{2\sum_{i,j} D_{ij}D_{ij}}$$

ใน OpenFOAM C++ คำนวณได้ดังนี้:

```cpp
volSymmTensorField D = symm(fvc::grad(U));
volScalarField shearRate = sqrt(2.0)*mag(D);
```

> [!TIP] การคำนวณเทนเซอร์อัตราการเสียรูป
> ฟังก์ชัน `symm()` ดึงส่วนสมมาตรของเทนเซอร์เกรเดียนต์ความเร็ว ซึ่งรับประกันการรักษาปริมาตรในการไหลที่ไม่บีบอัด

---

## 3. พฤติกรรมทาง Rheology ที่สำคัญ

![[viscosity_vs_shearrate_curves.png]]

| พฤติกรรม | คำอธิบาย | ตัวอย่าง | ค่าดัชนีกฎกำลัง $n$ |
| :--- | :--- | :--- | :--- |
| **Shear-Thinning** | ความหนืดลดลงเมื่ออัตราการเฉือนเพิ่มขึ้น (Pseudoplastic) | ซอสมะเขือเทศ, เลือด, สีทาบ้าน | $n < 1$ |
| **Shear-Thickening** | ความหนืดเพิ่มขึ้นเมื่ออัตราการเฉือนเพิ่มขึ้น (Dilatant) | แป้งข้าวโพดผสมน้ำ | $n > 1$ |
| **Yield Stress** | ต้องใช้แรงเค้นเกินค่าหนึ่งก่อนที่วัสดุจะเริ่มไหล | ยาสีฟัน, มายองเนส, เจล | ต้องมี $\tau_y$ |
| **Viscoelastic** | แสดงพฤติกรรมทั้งความหนืดและความยืดหยุ่น (มี "ความจำ") | โพลิเมอร์หลอมเหลว | ซับซ้อน |

```mermaid
graph LR
    A["Newtonian Fluid"] --> B["Constant Viscosity"]
    A --> C["Linear Stress-Strain"]
    D["Non-Newtonian Fluid"] --> E["Variable Viscosity"]
    D --> F["Non-Linear Stress-Strain"]
    B --> G["τ = μ·γ̇"]
    E --> H["τ = μ(γ̇)·γ̇"]
    G --> K["Water, Air"]
    H --> L["Blood, Ketchup, Paint"]

    style A fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style D fill:#fff9c4,stroke:#fbc02d,stroke-width:2px
```

---

## 4. โมเดล Rheological ทั่วไปใน OpenFOAM

### โมเดลกฎกำลัง (Power-Law Model)

แบบจำลองที่ไม่ใช่แบบนิวตันที่ง่ายที่สุดเชื่อมโยงความหนืดกับอัตราการเฉือนดังนี้:

$$\mu(\dot{\gamma}) = K \dot{\gamma}^{n-1}$$

โดยที่:
- $K$ คือดัชนีความสม่ำเสมอ (Consistency Index) [Pa·s$^n$]
- $n$ คือดัชนีกฎกำลัง (Power Law Index):
  - **$n < 1$**: พฤติกรรม Shear-thinning (pseudoplastic)
  - **$n > 1$**: พฤติกรรม Shear-thickening (dilatant)
  - **$n = 1$**: ลดรูปเป็นของไหลแบบนิวตัน

### โมเดล Bird-Carreau

แบบจำลองที่ซับซ้อนมากขึ้นซึ่งจับความหนืดเมื่อไม่มีการเฉือนและเมื่อเฉือนอย่างไม่สิ้นสุด:

$$\mu(\dot{\gamma}) = \mu_{\infty} + (\mu_0 - \mu_{\infty})\left[1 + (\lambda\dot{\gamma})^2\right]^{\frac{n-1}{2}}$$

โดยที่:
- $\mu_0$: ความหนืดเมื่อไม่มีการเฉือน (Zero-shear viscosity)
- $\mu_{\infty}$: ความหนืดเมื่อเฉือนอย่างไม่สิ้นสุด (Infinite-shear viscosity)
- $\lambda$: มาตราส่วนเวลาลักษณะเฉพาะ (Time constant)
- $n$: ดัชนีกฎกำลัง (Power law index)

**OpenFOAM Code Implementation:**

```cpp
// BirdCarreau viscosity calculation
return
    nuInf_
  + (nu0 - nuInf_)
   *pow
    (
        scalar(1)
      + pow
        (
            tauStar_.value() > 0
          ? nu0*strainRate/tauStar_
          : k_*strainRate,
            a_
        ),
        (n_ - 1.0)/a_
    );
```

### โมเดล Herschel-Bulkley

รวมพฤติกรรมแรงเฉือนให้ไหลด้วยการไหลแบบกฎกำลัง:

$$\mu(\dot{\gamma}) = \begin{cases}
\infty & \text{if } \tau < \tau_y \\
\tau_y/\dot{\gamma} + K\dot{\gamma}^{n-1} & \text{if } \tau \geq \tau_y
\end{cases}$$

โดยที่:
- $\tau_y$: แรงเฉือนให้ไหล (Yield stress)
- $\tau$: ขนาดความเค้นเฉือน
- $K$: ดัชนีความสม่ำเสมอ (Consistency index)
- $n$: ดัชนีพฤติกรรมการไหล (Flow behavior index)

**OpenFOAM Code Implementation:**

```cpp
// Herschel-Bulkley viscosity calculation with numerical safeguards
dimensionedScalar tone("tone", dimTime, 1.0);
dimensionedScalar rtone("rtone", dimless/dimTime, 1.0);

return
(
    min
    (
        nu0,
        (tau0_ + k_*rtone*pow(tone*strainRate, n_))
       /max
        (
            strainRate,
            dimensionedScalar ("vSmall", dimless/dimTime, vSmall)
        )
    )
);
```

> [!WARNING] การป้องกันทางตัวเลข
> OpenFOAM ใช้ `max(strainRate, vSmall)` เพื่อป้องกันการหารด้วยศูนย์ และ `min(nu0, ...)` เพื่อจำกัดความหนืดไม่ให้เกินค่าสูงสุดที่กำหนด

---

## 5. ทำไมต้องใช้ CFD จำลอง?

พฤติกรรมนอนนิวตันทำให้เกิดความไม่เชิงเส้น (Non-linearity) ที่รุนแรงในสมการโมเมนตัม:

$$\rho \left( \frac{\partial \mathbf{u}}{\partial t} + \mathbf{u} \cdot \nabla \mathbf{u} \right) = -\nabla p + \nabla \cdot (\mu(\dot{\gamma}) \nabla \mathbf{u})$$

เนื่องจาก $\mu$ ขึ้นกับ $\mathbf{u}$ (ผ่าน $\dot{\gamma}$) การแก้สมการจึงต้องใช้การวนซ้ำ (Iteration) เพื่อให้ค่าความหนืดและความเร็วสอดคล้องกัน

### ขั้นตอนการแก้ปัญหา

1. **Picard Iteration**: อัพเดตความหนืดตามการวนซ้ำก่อนหน้า
2. **Newton-Raphson**: แก้ระบบที่เชื่อมโยงพร้อมกับการแยกส่วนที่สอดคล้องกัน
3. **Under-Relaxation**: ป้องกันการเบี่ยงเบนด้วยการผ่อนคลายความหนืด

**OpenFOAM Code Implementation - Under-Relaxation:**

```cpp
// Under-relaxation for viscosity
mu_ = relaxationFactor_*mu_ + (1.0 - relaxationFactor_)*muOld_;
```

ซึ่ง OpenFOAM มีโครงสร้างที่รองรับเรื่องนี้อย่างมีประสิทธิภาพ

---

## 6. สถาปัตยกรรม OpenFOAM สำหรับ Non-Newtonian Fluids

### ลำดับชั้นของคลาส

OpenFOAM จัดระเบียบโมเดลของไหลที่ไม่ใช่นิวตันเป็นต้นไม้การสืบทอดที่ชัดเจน:

```mermaid
graph TD
    A[viscosityModel] --> B[generalisedNewtonianViscosityModel]
    B --> C[strainRateViscosityModel]
    C --> D[BirdCarreau]
    C --> E[HerschelBulkley]
    C --> F[powerLaw]
    C --> G[Cross Power Law]
```

### Factory Pattern การเลือกขณะ Runtime

OpenFOAM ใช้ **dictionary-driven factory pattern** ที่ซับซ้อนในการสร้างอินสแตนซ์ของโมเดลความหนืด:

```cpp
// Factory method for creating viscosity models
template<class BasicTransportModel>
autoPtr<viscosityModel<BasicTransportModel>>
viscosityModel<BasicTransportModel>::New
(
    const dictionary& dict,
    const BasicTransportModel& model
)
{
    const word modelType(dict.lookup("transportModel"));

    typename dictionaryConstructorTable::iterator cstrIter =
        dictionaryConstructorTablePtr_->find(modelType);

    return cstrIter()(dict, model);
}
```

**การระบุใน Dictionary:**

```cpp
transportModel  HerschelBulkley;

HerschelBulkleyCoeffs
{
    nu0          [0 2 -1 0 0 0 0] 1e-06;
    tauY         [0 2 -2 0 0 0 0] 10;
    k            [0 2 -1 0 0 0 0] 0.01;
    n            [0 0 0 0 0 0 0]  0.7;
}
```

> [!INFO] ข้อดีของ Factory Pattern
> - **Runtime Flexibility**: เปลี่ยนโมเดลได้โดยแก้ไข dictionary เท่านั้น
> - **Type Safety**: การตรวจสอบขณะ compile มั่นใจว่าโมเดลทั้งหมดนำอินเทอร์เฟซที่จำเป็นไปใช้งาน
> - **Extensibility**: เพิ่มโมเดลใหม่ได้โดยไม่ต้องคอมไพล์ OpenFOAM libraries หลักใหม่

---

## 7. การใช้งานและการประยุกต์ใช้

### Solvers ที่แนะนำ

| Solver | ชนิดของปัญหา | สภาวะการไหล | ความเหมาะสม |
|--------|-------------|-------------|-------------|
| **simpleFoam** | การไหลอัดตัวไม่ได้ | สภาวะคงตัว | กรณีศึกษาพื้นฐาน |
| **pimpleFoam** | การไหลอัดตัวไม่ได้ | สภาวะไม่คงตัว | กรณีศึกษาซับซ้อน |
| **nonNewtonianIcoFoam** | เฉพาะนิวตัน-นอนนิวตัน | สภาวะไม่คงตัว | เฉพาะทาง |

### การประยุกต์ใช้ทางอุตสาหกรรม

| การประยุกต์ใช้ | โมเดลที่เหมาะสม | ลักษณะเฉพาะ |
|----------------|-------------------|---------------|
| **การแปรรูปโพลีเมอร์** | Bird-Carreau, Cross Power Law | การขึ้นรูปฉีด, การอัดเป็นแท่ง |
| **การแปรรูปอาหาร** | Herschel-Bulkley, Power Law | การไหลของซอสและแป้ง |
| **การไหลของเลือด** | Bird-Carreau, Casson | การไหลในหลอดเลือดขนาดเล็ก |
| **ของเหลวขุดเจาะ** | Herschel-Bulkley | คลนและปูนซีเมนต์ |
| **การเคลือบ** | Power Law, Carreau-Yasuda | การปกคลุมพื้นผิว |

---

## 8. ข้อควรพิจารณาทางตัวเลข

### เทคนิคการปรับความสม่ำเสมอ (Regularization)

สำหรับแบบจำลองเช่น Herschel-Bulkley ความเสถียรทางตัวเลขต้องการการปรับความสม่ำเสมอ:

**Papanastasiou Regularization:**
```cpp
volScalarField regularizationFactor = tauY_/(m_*shearRate_ + dimensionedScalar("small", dimless, SMALL));
```

**Bercovier-Engleman Regularization:**
```cpp
volScalarField regularizationFactor = tauY_/(shearRate_ + epsilon_);
```

### การจัดการบริเวณ High-Gradient

ใกล้มุมแหลมหรือการขยายตัวกะทันหัน อัตราการเฉือนสามารถกลายเป็นขนาดใหญ่อย่างมาก ทำให้ความหนืดลดลงถึงค่าที่ไม่สมจริง

**วิธีการแก้ไข:**
1. **การตัดค่าความหนืด** (Viscosity Clipping):
```cpp
nu_ = max(nuMin_, min(nuMax_, nuPower));
```

2. **การปรับ Mesh**: เพิ่มการปรับ mesh ในพื้นที่ high-gradient
3. **เรขาคณิตที่ราบรื่น**: ใช้มุมมนแทนที่มุม 90° แหลม

---

## สรุป

ไหลนอนนิวตันใน OpenFOAM ถูกจัดการผ่านสถาปัตยกรรมที่ elegantly ออกแบบมาให้:

1. **ความยืดหยุ่น**: สลับโมเดลได้ทาง dictionary
2. **ความสอดคล้อง**: การคำนวณอัตราการเฉือนที่รวมศูนย์
3. **ความปลอดภัย**: การป้องกันทางตัวเลขในตัว
4. **ความสามารถขยาย**: เพิ่มโมเดลใหม่ได้ง่าย

สถาปัตยกรรมนี้ทำให้การจำลองพฤติกรรมที่ซับซ้อนของของไหลในชีวิตจริง — จากซอสมะเขือเทศไปจนถึงการไหลของเลือด — เป็นไปได้อย่างมีประสิทธิภาพและแม่นยำ
