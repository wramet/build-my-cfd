# ระบบของเหลว-ของเหลว (Liquid-Liquid Systems)

## 1. บทนำ (Introduction)

> [!INFO] **ความสำคัญของระบบของเหลว-ของเหลว**
> ระบบของเหลว-ของเหลวมีบทบาทสำคัญในกระบวนการทางอุตสาหกรรม เช่น การสกัดน้ำมัน (Liquid-Liquid Extraction), การทำอิมัลชัน (Emulsification), และการแยกสารผสม

ระบบของเหลว-ของเหลวมีความท้าทายเฉพาะที่แตกต่างจากระบบก๊าซ-ของเหลว:

- **อัตราส่วนความหนาแน่นใกล้เคียงกัน** ($\rho_d/\rho_c \approx 1$) ทำให้แรงลอยตัวมีค่าน้อย
- **อัตราส่วนความหนืดแตกต่างกันอย่างมีนัยสำคัญ** ($\lambda = \mu_d/\mu_c$) ส่งผลต่อการไหลภายในหยด
- **ความตึงผิวต่ำ** เมื่อเทียบกับระบบก๊าซ-ของเหลว ทำให้เกิดการเสียรูปได้ง่าย

```mermaid
flowchart TD
    A[Liquid-Liquid Systems] --> B[Oil-Water Systems]
    A --> C[Organic-Aqueous Systems]
    A --> D[Emulsion Systems]

    B --> B1[Extraction Columns]
    B --> B2[Separators]
    B --> B3[Mixing Tanks]

    C --> C1[Solvent Extraction]
    C --> C2[Phase Transfer]
    C --> C3[Reactors]

    D --> D1[Stable Emulsions]
    D --> D2[Unstable Emulsions]
    D --> D3[Multiple Emulsions]
```

---

## 2. การจำแนกหยดของเหลว (Droplet Classification)

### 2.1 หยดขนาดเล็ก ($Eo < 0.5$)

หยดขนาดเล็กมีลักษณะเป็นทรงกลมแข็ง (Rigid sphere) เนื่องจากแรงตึงผิวมีอิทธิพลสูง

**ลักษณะเฉพาะ:**
- ทรงกลม
- Reynolds number ต่ำถึงปานกลาง ($Re_p < 1000$)
- ควบคุมโดยแรงตึงผิวเป็นหลัก
- การไหลภายในน้อย

**Eötvös Number:**
$$Eo = \frac{\Delta \rho \, g \, d^2}{\sigma}$$

**ตัวแปรในสมการ:**
- $\Delta \rho$: ความแตกต่างของความหนาแน่นระหว่างเฟสกระจายและเฟสต่อเนื่อง
- $g$: ความเร่งเนื่องจากความโน้มถ่วง
- $d$: เส้นผ่านศูนย์กลางของหยด
- $\sigma$: ค่าแรงตึงผิวระหว่างอินเตอร์เฟซ

> [!TIP] **โมเดลที่แนะนำ**
> - **Drag:** Schiller-Naumann
> - **Lift:** Legendre-Magnaudet (พิจารณาอัตราส่วนความหนืด $\lambda$)
> - **Heat Transfer:** Ranz-Marshall

#### สมการควบคุมการเคลื่อนที่

**แรงลากต้าน:**
$$\mathbf{f}_D = \frac{1}{8} C_D \rho_c \pi d^2 |\mathbf{u}_d - \mathbf{u}_c| (\mathbf{u}_d - \mathbf{u}_c)$$

**สัมประสิทธิ์การลากต้าน** $C_D$ สำหรับหยดทรงกลมทำตามสหสัมพันธ์ Schiller-Naumann:
$$C_D = \begin{cases}
\frac{24}{Re_p}(1 + 0.15Re_p^{0.687}) & \text{for } Re_p < 1000 \\
0.44 & \text{for } Re_p \geq 1000
\end{cases}$$

#### OpenFOAM Code Implementation

```cpp
// Small droplets configuration
phases
{
    dispersed
    {
        type            incompressible;
        equationOfState rhoConst;
        thermodynamics  hConst;
        transport       const;

        // Droplet diameter
        diameter        constant 0.001; // 1 mm
    }

    continuous
    {
        type            incompressible;
        equationOfState rhoConst;
        thermodynamics  hConst;
        transport       const;
    }
}

phaseInteraction
{
    dragModel       SchillerNaumann;
    liftModel       LegendreMagnaudet;
    virtualMassModel    constant;
    heatTransferModel   RanzMarshall;

    SchillerNaumannCoeffs
    {
        switch1 1000;
        Cd1     24;
        Cd2     0.44;
    }

    LegendreMagnaudetCoeffs
    {
        lambda      0.8; // อัตราส่วนความหนืด น้ำมัน/น้ำ
    }

    constantVirtualMassCoeffs
    {
        Cvm         0.5;
    }
}
```

**เหตุผลที่เลือกใช้แบบจำลอง:**

1. **แบบจำลอง Drag Schiller-Naumann**
   - เหมาะสมที่สุดสำหรับหยดทรงกลมที่ค่า Reynolds number ต่ำถึงปานกลาง
   - ให้การทำนายค่าสัมประสิทธิ์ drag ที่แม่นยำ

2. **แบบจำลอง Lift Legendre-Magnaudet**
   - คำนึงถึงอัตราส่วนความหนืดระหว่างเฟส
   - สำคัญสำหรับระบบของเหลว-ของเหลวที่มีความหนืดต่างกัน

3. **แบบจำลอง Virtual Mass**
   - จำเป็นเนื่องจากอัตราส่วนความหนาแน่นใกล้เคียงกัน
   - ส่งผลต่อความเสถียรของการคำนวณ

---

### 2.2 หยดที่ผิดรูป ($Eo > 0.5$)

หยดขนาดใหญ่เริ่มเสียรูปเป็นทรงรีหรือเกิดการสั่นของรูปร่าง

**ลักษณะเฉพฺ-specific:**
- ความผิดรูปที่สำคัญจากรูปทรงกลม
- รูปร่างทรงรีหรือรูปแบบที่ซับซ้อนมากขึ้น
- Reynolds number ปานกลางถึงสูง
- ผลกระทบอินเตอร์เฟซที่สำคัญ:
  - การสั่นพรำของรูปร่าง (Shape oscillations)
  - พื้นที่อินเตอร์เฟซที่เพิ่มขึ้น

**พารามิเตอร์การผิดรูป:**
$$D = \frac{L - W}{L + W}$$

**ตัวแปรในสมการ:**
- $L$: แกนหลักของหยดที่ผิดรูป
- $W$: แกนรองของหยดที่ผิดรูป

> [!WARNING] **คำเตือน**
> หยดที่ผิดรูปต้องการโมเดลที่ซับซ้อนขึ้น:
> - **Drag:** Grace Model (ออกแบบมาสำหรับหยดของเหลวโดยเฉพาะ)
> - **Turbulence:** Simonin Model (จัดการปฏิสัมพันธ์ระหว่างความปั่นป่วนและหยด)
> - **Population Balance:** จำเป็นสำหรับการทำนายการกระจายขนาดหยด

#### สหสัมพันธ์การลากต้านของ Grace

$$C_D = \frac{24}{Re_p}\left[1 + 0.15(1 + 0.283\lambda^{0.61})Re_p^{0.687}\right]$$

โดยที่ $\lambda = \mu_d/\mu_c$ คืออัตราส่วนความหนืด

#### แรงยก Legendre-Magnaudet

ในระบบของเหลว-ของเหลว สัมประสิทธิ์แรงยกขึ้นอยู่กับความหนืดภายในหยด:
$$C_L^{\text{inviscid}} = \frac{6}{\pi^2} \frac{(2 + \lambda)^2 + \lambda}{(1 + \lambda)^3} \tag{2.1}$$

#### OpenFOAM Code Implementation

```cpp
// Deformed droplets configuration
phaseInteraction
{
    dragModel       Grace;
    liftModel       LegendreMagnaudet;
    virtualMassModel    constant;
    turbulentDispersionModel    Simonin;

    GraceCoeffs
    {
        // พารามิเตอร์สำหรับหยดที่ผิดรูป
        C1          0.44;
        C2          24.0;
        C3          0.15;
        lambda      0.8; // อัตราส่วนความหนืด
    }

    LegendreMagnaudetCoeffs
    {
        lambda      0.8;
        // สัมประสิทธิ์แรงยกที่คำนึงถึงความหนืด
    }

    SimoninCoeffs
    {
        Ctd         1.0;
        D           1.0;
        // การกระจายความปั่นป่วน
    }
}

// Interfacial tension
sigma    constant 0.032; // N/m สำหรับระบบน้ำมัน-น้ำ
```

**เหตุผลที่เลือกใช้แบบจำลอง:**

1. **แบบจำลอง Drag Grace**
   - พัฒนาโดยเฉพาะสำหรับหยดที่ผิดรูป
   - คำนึงถึง form drag เพิ่มเติมเนื่องจากการเปลี่ยนแปลงรูปร่าง
   - พิจารณารูปร่างของหยดเป็นฟังก์ชันของ Eötvös และ Reynolds numbers
   - ให้การทำนาย drag ที่แม่นยำมากขึ้นสำหรับอินเตอร์เฟซที่ไม่ใช่ทรงกลม

2. **แรงตึงผิวที่ขึ้นอยู่กับอุณหภูมิ**
   - มีความสำคัญอย่างยิ่งสำหรับหยดที่ผิดรูป
   - พื้นที่อินเตอร์เฟซที่เพิ่มขึ้นทำให้ระบบมีความไวต่อการเปลี่ยนแปลงของอุณหภูมิมากขึ้น
   - ความสัมพันธ์: $\sigma(T) = \sigma_0 \left[1 - \gamma_T (T - T_0)\right]$
   - $\gamma_T$ คือสัมประสิทธิ์อุณหภูมิของแรงตึงผิว

3. **แบบจำลองการกระจายความปั่นป่วนแบบ Simonin**
   - ให้การจัดการขั้นสูงของปฏิสัมพันธ์ความปั่นป่วน-เฟสกระจาย
   - รวมถึงความไม่แน่นอนของความปั่นป่วนและผลกระทบของความเข้มข้นแบบเลือกสรร
   - มีความสำคัญอย่างยิ่งสำหรับหยดที่ใหญ่ขึ้นและผิดรูปที่โต้ตอบกับกระแสความปั่นป่วนได้ดีขึ้น

---

## 3. แบบจำลองที่แนะนำ (Recommended Models)

### 3.1 แรงยก Legendre-Magnaudet

ในระบบของเหลว-ของเหลว สัมประสิทธิ์แรงยกขึ้นอยู่กับความหนืดภายในหยด:
$$C_L^{\text{inviscid}} = \frac{6}{\pi^2} \frac{(2 + \lambda)^2 + \lambda}{(1 + \lambda)^3} \tag{3.1}$$

**ความสำคัญของอัตราส่วนความหนืด:**
- $\lambda = \mu_d/\mu_c$: อัตราส่วนความหนืด
- ค่า $\lambda$ สูง → การไหลภายในน้อย → หยดมีพฤติกรรมเหมือนของแข็ง
- ค่า $\lambda$ ต่ำ → การไหลภายในมาก → หยดมีความยืดหยุ่น

### 3.2 การรวมตัวและการแตกตัว (Population Balance Models)

หากความเข้มข้นหยดสูง ($\alpha_d > 0.1$) ต้องใช้ **Population Balance Models (PBM)**:

#### สมการสมดุลประชากร

$$\frac{\partial n(v)}{\partial t} + \nabla \cdot [\mathbf{u}_d n(v)] + \frac{\partial [G(v) n(v)]}{\partial v} = B_{breakup} - D_{breakup} + B_{coalescence} - D_{coalescence}$$

**ตัวแปรในสมการ:**
- $n(v,t)$: ความหนาแน่นจำนวนหยดขนาด $v$ ที่เวลา $t$
- $B_c, B_b$: อัตราการเกิดจากการรวมตัวและการแตกตัว
- $D_c, D_b$: อัตราการตายจากการรวมตัวและการแตกตัว

#### โมเดลการแตกตัว (Breakup Models)

**Weber Number Model:**
$$We = \frac{\rho_c u_{rel}^2 d}{\sigma} \tag{3.2}$$

การแตกตัวมักเกิดขึ้นเมื่อ $We > 12$ สำหรับระบบของเหลว-ของเหลว

**โมเดล Luo และ Svendsen:**
$$B_{breakup} = \int_v^{\infty} \beta(v,v') \Omega_{breakup}(v') n(v') \, dv'$$

กับความถี่การแตกตัว:
$$\Omega_{breakup} = 0.923(1 - \alpha_d) \frac{\varepsilon^{1/3}}{d^{2/3}} \exp\left(-\frac{U_{crit}^2}{\varepsilon^{2/3} d^{2/3}}\right)$$

#### โมเดลการรวมตัว (Coalescence Models)

**Film Drainage Model:**
- จับกลไกทางฟิสิกส์ที่หยดเข้าใกล้กัน
- เกิดการระบายของเหลวฟิล์มระหว่างอินเตอร์เฟซจนกว่าจะเกิดการแตกสลาย
- มีประสิทธิภาพด้านการคำนวณและมีความหมายทางฟิสิกส์สำหรับหยดทรงกลมขนาดเล็ก

**โมเดล Coulaloglou และ Tavlarides:**
$$\Omega_{coalescence} = C_{co} \frac{\pi}{4} (d_i + d_j)^2 \mathbf{u}_{t,ij} \exp\left(-\frac{t_{ij}}{t_{c,ij}}\right)$$

#### OpenFOAM Code Implementation

```cpp
populationBalance
{
    populationBalanceModel    sizeGroup;

    sizeGroups
    {
        SG1 { d: 0.0005; x: 0.2; } // 0.5 mm
        SG2 { d: 0.0010; x: 0.3; } // 1.0 mm
        SG3 { d: 0.0020; x: 0.3; } // 2.0 mm
        SG4 { d: 0.0040; x: 0.2; } // 4.0 mm
    }

    coalescenceModels
    {
        LuoCoalescence
        {
            Cco         0.1;
            Co          0.0;
        }
    }

    breakupModels
    {
        LuoBreakup
        {
            C1          0.923;
            C2          1.0;
            C3          2.45;
        }
    }
}

turbulence
{
    type            mixtureKEpsilon;

    mixtureKEpsilonCoeffs
    {
        Cmu         0.09;
        C1          1.44;
        C2          1.92;
        sigmaEps    1.3;
        sigmaK      1.0;
        muMixture   on;
        phaseTurbulence  on;
    }
}
```

---

## 4. การนำไปใช้ใน OpenFOAM

### 4.1 การตั้งค่าระบบสกัดน้ำมัน-น้ำ

ตัวอย่างการตั้งค่าใน `phaseProperties` สำหรับระบบสกัดน้ำมัน-น้ำ:

```cpp
// ระบบน้ำมัน-น้ำ (Oil-Water System)
phases
{
    oil
    {
        type            incompressible;
        equationOfState rhoConst;

        rho             rho [1 -3 0 0 0] 850; // kg/m³

        transport       const;
        mu              mu [0 2 -1 0 0] 0.05; // Pa·s
    }

    water
    {
        type            incompressible;
        equationOfState rhoConst;

        rho             rho [1 -3 0 0 0] 1000; // kg/m³

        transport       const;
        mu              mu [0 2 -1 0 0] 0.001; // Pa·s
    }
}

phaseInteraction
{
    dragModel       Grace;
    liftModel       LegendreMagnaudet;
    virtualMassModel    constant;
    turbulentDispersionModel    Burns;

    GraceCoeffs
    {
        // พารามิเตอร์สำหรับหยดที่ผิดรูป
        C1          0.44;
        C2          24.0;
        C3          0.15;
    }

    LegendreMagnaudetCoeffs
    {
        lambda      50; // อัตราส่วนความหนืด น้ำมัน/น้ำ
    }

    constantVirtualMassCoeffs
    {
        Cvm         0.5;
    }

    BurnsCoeffs
    {
        Ctd         1.0;
        D           1.0;
    }
}

// Interfacial tension
surfaceTensionModel   constant;
constantSurfaceTensionCoeffs
{
    sigma         0.032; // N/m
}
```

### 4.2 การเลือก Solver

```cpp
// สำหรับการไหลแบบ transient
simulationType  twoPhaseEulerFoam;

// การตั้งค่า solver
solver
{
    p               GAMG;
    pFinal          GAMG;
    U               smoothSolver;
    alpha           smoothSolver;
}

relaxationFactors
{
    fields
    {
        p           0.3;
        U           0.7;
        alpha       0.7;
    }
    equations
    {
        p           1;
        U           0.8;
        alpha       0.8;
    }
}
```

### 4.3 ข้อควรพิจารณา

> [!TIP] **ข้อควรพิจารณาสำคัญสำหรับระบบของเหลว-ของเหลว**

1. **อัตราส่วนความหนาแน่นใกล้เคียงกัน** ($\approx 1:1$)
   - ส่งผลให้การเชื่อมโยงความดัน-ความเร็ว (Pressure-Velocity Coupling) มีความเสถียรกว่าระบบ Gas-Liquid
   - แต่ต้องระวังเรื่องการทำนายขนาดหยดที่แม่นยำผ่าน PBM

2. **อัตราส่วนความหนืดแตกต่างกัน**
   - ส่งผลต่อการไหลภายในหยด (Internal circulation)
   - ควรใช้โมเดลที่คำนึงถึงผลของความหนืด (Grace, Legendre-Magnaudet)

3. **ความตึงผิวต่ำ**
   - ทำให้เกิดการเสียรูปได้ง่าย
   - จำเป็นต้องใช้โมเดล drag ที่เหมาะสมกับหยดที่ผิดรูป

4. **Population Balance Modeling**
   - สำคัญอย่างยิ่งสำหรับการทำนายการกระจายขนาดหยด
   - ต้องการทรัพยากรการคำนวณสูง

---

## 5. กรณีศึกษา (Case Studies)

### 5.1 เครื่องสกัดแบบแพร่สาร (Extraction Columns)

**ลักษณะเฉพาะ:**
- การไหลแบบ countercurrent ระหว่างเฟส
- ความเข้มข้นหยดปานกลางถึงสูง
- การรวมตัวและแตกตัวสำคัญ

**แบบจำลองที่แนะนำ:**
- Drag: Grace Model
- Lift: Legendre-Magnaudet
- Population Balance: MOC (Method of Classes)
- Turbulence: k-ε Model

### 5.2 เครื่องผสมแบบหมุน (Mixing Tanks)

**ลักษณะเฉพฺ-specific:**
- ความปั่นป่วนสูง
- การกระจายตัวของหยดไม่สม่ำเสมอ
- การแตกตัวเนื่องจาก shear สูง

**แบบจำลองที่แนะนำ:**
- Drag: Schiller-Naumann หรือ Grace
- Turbulent Dispersion: Simonin
- Population Balance: QMOM (Quadrature Method of Moments)
- Turbulence: Realizable k-ε

### 5.3 เครื่องแยกสาร (Separators)

**ลักษณะเฉพาะ:**
- การไหลที่ค่อยข้างสงบ
- การตกตะกอนโดยแรงโน้มถ่วง
- การรวมตัวของหยดเพื่อเพิ่มขนาด

**แบบจำลองที่แนะนำ:**
- Drag: Schiller-Naumann
- Lift: Legendre-Magnaudet
- Coalescence: Film Drainage Model
- Turbulence: Standard k-ε หรือ Laminar

---

## 6. สรุป (Summary)

| ประเด็น | คำอธิบาย |
|---------|-----------|
| **ความท้าทายหลัก** | อัตราส่วนความหนืดแตกต่างกัน ความตึงผิวต่ำ การเสียรูปของหยด |
| **โมเดล Drag** | Grace (หยดผิดรูป), Schiller-Naumann (หยดทรงกลม) |
| **โมเดล Lift** | Legendre-Magnaudet (คำนึงถึงอัตราส่วนความหนืด) |
| **Population Balance** | จำเป็นสำหรับความเข้มข้นหยดสูง |
| **การคำนวณ** | ต้องการทรัพยากรสูงเมื่อใช้ PBM |

---

## 7. อ้างอิงเพิ่มเติม

ดูข้อมูลเพิ่มเติมเกี่ยวกับ:
- [[01_Decision_Framework]] - กรอบการตัดสินใจเลือกแบบจำลอง
- [[02_Gas_Liquid_Systems]] - เปรียบเทียบกับระบบก๊าซ-ของเหลว
- [[06_Property-Based_Selection]] - การเลือกโมเดลตามคุณสมบัติ
- [[07_Computational_Considerations]] - ข้อควรพิจารณาด้านการคำนวณ
