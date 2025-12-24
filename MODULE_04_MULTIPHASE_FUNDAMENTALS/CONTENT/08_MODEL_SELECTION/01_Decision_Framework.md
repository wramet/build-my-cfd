# กรอบการตัดสินใจเลือกแบบจำลอง (Model Selection Decision Framework)

## 1. บทนำ (Introduction)

การจำลองการไหลหลายเฟสใน OpenFOAM มีความซับซ้อนเนื่องจากมีโมเดลให้เลือกจำนวนมาก กรอบการตัดสินใจนี้ช่วยให้นักวิจัยและวิศวกรสามารถเลือกแบบจำลองย่อย (Sub-models) ได้อย่างเป็นระบบตามหลักฟิสิกส์

> [!INFO] ความสำคัญของการเลือกโมเดลที่เหมาะสม
> การเลือกแบบจำลองที่เหมาะสมเป็นสิ่งสำคัญอย่างยิ่งสำหรับการทำนายปฏิสัมพันธ์ระหว่างเฟสและปรากฏการณ์ทางฟิสิกส์อย่างแม่นยำ การเลือกที่ผิดพลาดอาจนำไปสู่ผลลัพธ์ที่คลาดเคลื่อนอย่างมากหรือปัญหาความไม่เสถียรทางตัวเลข

---

## 2. กระบวนการตัดสินใจแบบลำดับชั้น (Hierarchical Process)

### ระดับที่ 1: การจำแนกระบบ (System Classification)

ระดับแรกของกรอบการตัดสินใจเกี่ยวข้องกับการจำแนกระบบหลายเฟสตามลักษณะทางกายภาพพื้นฐาน การจำแนกนี้กำหนดแนวทางการจำลองที่เหมาะสมและการเลือก Solver ใน OpenFOAM

#### **ประเภทเฟส (Phase Types)**

| ประเภทเฟส | ลักษณะเฉพาะ | ตัวอย่างการใช้งาน | Solver แนะนำ |
|-------------|----------------|-------------------|--------------|
| **ก๊าซ-ของเหลว** | ฟองก๊าซหรือหยดของเหลวในเฟสของเหลวต่อเนื่อง | คอลัมน์ฟองก๊าซ, การไหลของอากาศ-น้ำ | `multiphaseEulerFoam`, `interFoam` |
| **ของเหลว-ของเหลว** | ของเหลวที่ไม่ผสมกันโดยมีส่วนติดต่อที่แตกต่างกัน | การแยกน้ำมัน-น้ำ, เอมัลชัน | `interFoam`, `multiphaseInterFoam` |
| **ก๊าซ-ของแข็ง** | การไหลของก๊าซผ่านอนุภาคของแข็ง | เตาไฟฟลูไอด์, การขนถ่ายด้วยลม | `multiphaseEulerFoam`, `coalChemistryFoam` |
| **ของเหลว-ของแข็ง** | การขนส่งอนุภาคของแข็งด้วยของเหลว | การขนส่งตะกอน, การไหลของสลัร์รี่ | `multiphaseEulerFoam`, `twoPhaseEulerFoam` |

#### **รูปแบบการไหล (Flow Regimes)**

- **แยกชัด (Separated Flow)**: รูปแบบการไหลที่เฟสแยกจากกันอย่างชัดเจน เช่น การไหลแบบชั้น (stratified flow)
  - เลือก **VOF (`interFoam`)**
  - เหมาะสำหรับ: `α_d < 0.3` และอินเตอร์เฟสที่ชัดเจน

- **กระจาย (Dispersed Flow)**: รูปแบบการไหลที่เฟสหนึ่งกระจายเป็นฟอง/หยด/อนุภาคในเฟสต่อเนื่องอีกเฟสหนึ่ง
  - เลือก **Euler-Euler (`multiphaseEulerFoam`)**
  - เหมาะสำหรับ: ระบบที่มีส่วนปริมาตรเฟสกระจายสูง

```mermaid
flowchart TD
    A[เริ่มต้น] --> B{รูปแบบการไหล?}
    B -->|แยกชัด<br/>Separated| C[VOF Method<br/>interFoam]
    B -->|กระจาย<br/>Dispersed| D{ความเข้มข้น α_d?}
    D -->|> 0.3<br/>Dense| E[Euler-Euler + KTGF<br/>multiphaseEulerFoam]
    D -->|< 0.3<br/>Dilute| F{ความเร็ว Slip?}
    F -->|ต่ำ<br/>Low Slip| G[Homogeneous<br/>Single Velocity Field]
    F -->|สูง<br/>High Slip| H[Inhomogeneous<br/>Separate Velocity Fields]
```

---

### ระดับที่ 2: การประเมินพารามิเตอร์ทางกายภาพ (Physical Assessment)

ใช้ตัวเลขไร้มิติเพื่อระบุกลไกที่โดดเด่นและเลือกแบบจำลองย่อยที่เหมาะสม

#### **อัตราส่วนคุณสมบัติ (Property Ratios)**

**อัตราส่วนความหนาแน่น** ($\rho_d/\rho_c$):
$$\frac{\rho_d}{\rho_c} = \text{Density Ratio}$$

| ช่วงค่า | ลักษณะเฉพณะ | แรงที่โดดเด่น | คำแนะนำ |
|----------|--------------|----------------|-----------|
| **> 1000** | อนุภาคหนัก (Heavy Particles) | แรงเฉื่อย, แรงโน้มถ่วง | ละเลย Virtual Mass |
| **< 10** | อนุภาคเบา (Light Particles) | แรงลอยตัว, Virtual Mass | จำเป็นต้องรวม Virtual Mass |

**อัตราส่วนความหนืด** ($\mu_d/\mu_c$):
$$\frac{\mu_d}{\mu_c} = \text{Viscosity Ratio}$$

| ช่วงค่า | ลักษณะเฉพณะ | ผลต่อการไหลเวียนภายใน | คำแนะนำ |
|----------|--------------|---------------------|-----------|
| **> 100** | เฟสกระจายหนืดมาก | การไหลเวียนภายในถูกยับยั้ง | ใช้แบบจำลอง Grace Drag |
| **< 0.1** | เฟสกระจายหนืดต่ำ | การไหลเวียนภายในแข็งแกร่ง | ใช้แบบจำลอง Schiller-Naumann ดัดแปลง |

#### **ตัวเลขไร้มิติสำคัญ (Critical Dimensionless Numbers)**

**Particle Reynolds Number** ($Re_p$):
$$Re_p = \frac{\rho_c u_{rel} d_p}{\mu_c}$$

| ช่วง $Re_p$ | ลักษณะการไหล | รีจีม | แบบจำลอง Drag แนะนำ |
|-------------|----------------|---------|---------------------|
| $Re_p < 1$ | การไหลครีปปิ้ง | รีจีมสโตกส์ | Stokes: $C_D = \frac{24}{Re_p}$ |
| $1 < Re_p < 1000$ | การเปลี่ยนผ่าน | รีจีมการเปลี่ยนผ่าน | Schiller-Naumann |
| $Re_p > 1000$ | การไหลเฉื่อย | รีจีมเฉื่อย | Newton: $C_D = 0.44$ |

**Eötvös Number** ($Eo$):
$$Eo = \frac{g(\rho_c - \rho_d)d_p^2}{\sigma}$$

| ค่า $Eo$ | แรงที่โดดเด่น | ลักษณะอนุภาค | แบบจำลองแนะนำ |
|----------|----------------|----------------|------------------|
| $Eo < 1$ | ความตึงผิวโดดเด่น | อนุภาคทรงกลม | Schiller-Naumann |
| $Eo > 1$ | การลอยตัวโดดเด่น | อนุภาคที่ถูกแปรรูป | Ishii-Zuber, Tomiyama |
| $Eo > 4$ | การลอยตัวเด่นชัด | ฟองก๊าซแคป (Cap bubbles) | Tomiyama พร้อม Wall Lubrication |

**Weber Number** ($We$):
$$We = \frac{\rho_c u_{rel}^2 d_p}{\sigma}$$

ใช้ประเมินการเปลี่ยนรูปของฟองก๊าศ/หยด:
- **$We < 1$**: ไม่มีการเปลี่ยนรูปที่สำคัญ
- **$We > 1$**: เริ่มมีการเปลี่ยนรูป
- **$We > 4$**: การเปลี่ยนรูปอย่างมีนัยสำคัญ

**Volume Fraction** ($\alpha_d$):
$$\alpha_d = \frac{V_d}{V_{total}}$$

| ช่วง $\alpha_d$ | ความเข้มข้น | แนวทางการจำลอง | แบบจำลองเพิ่มเติม |
|-----------------|--------------|-------------------|---------------------|
| $0 < \alpha_d < 0.1$ | เจือจาง (Dilute) | Lagrangian หรือ Eulerian อย่างเดียว | ไม่ต้องการ KTGF |
| $0.1 < \alpha_d < 0.3$ | ปานกลาง (Intermediate) | Eulerian สองเฟส | พิจารณา KTGF |
| $\alpha_d > 0.3$ | หนาแน่น (Dense) | Eulerian หลายเฟส | ==จำเป็นต้องใช้ KTGF== |

---

### ระดับที่ 3: การเลือกแบบจำลองย่อย (Sub-model Selection)

โดยยึดตามการจำแนกระบบและพารามิเตอร์ทางกายภาพ แบบจำลองที่เหมาะสมจะถูกเลือกสำหรับปรากฏการณ์ทางกายภาพแต่ละประการ

#### **การเลือกแบบจำลอง Drag (Drag Model Selection)**

| แบบจำลอง | เงื่อนไข | สมการ $C_D$ | เหมาะสำหรับ |
|------------|------------|-------------------|--------------|
| **Stokes Drag** | $Re_p < 1$, อนุภาคทรงกลม | $C_D = \frac{24}{Re_p}$ | ฝุ่นละออง, อนุภาคเล็กมาก |
| **Schiller-Naumann** | $1 < Re_p < 1000$, รีจีมการเปลี่ยนผ่าน | $C_D = \frac{24}{Re_p}(1 + 0.15Re_p^{0.687})$ | ฟองก๊าศทรงกลม, หยดขนาดเล็ก |
| **Ishii-Zuber** | อนุภาคที่ถูกแปรรูป, $Eo > 1$ | พิจารณาผลกระทบรูปร่าง | ฟองก๊าศผิดรูปขนาดกลาง |
| **Tomiyama** | รวมผลกระทบผนังและแรงยก | เหมาะสำหรับการไหลในท่อ | ฟองก๊าศในท่อ, Slug flow |
| **Grace** | หยดที่ผิดรูป, อัตราส่วนความหนืดสูง | คำนึงถึง form drag | หยดน้ำมันในน้ำ |

สัมประสิทธิ์การลากตัว $C_D$ ปรากฏในพจน์การแลกเปลี่ยนโมเมนตัม:
$$\mathbf{M}_D = \frac{3}{4}\frac{\alpha_c\alpha_d\rho_c}{d_p}C_D|\mathbf{u}_d - \mathbf{u}_c|(\mathbf{u}_d - \mathbf{u}_c)$$

#### **การเลือกแบบจำลอง Lift (Lift Model Selection)**

| แบบจำลอง | เงื่อนไข | สมการ | เหมาะสำหรับ |
|------------|------------|-----------------|--------------|
| **Saffman-Mei** | อนุภาคทรงกลมขนาดเล็ก | $\mathbf{F}_L = C_L \rho_c V_d (\mathbf{u}_c - \mathbf{u}_d) \times (\nabla \times \mathbf{u}_c)$ | ฟองก๊าศเล็ก |
| **Tomiyama Lift** | ฟองก๊าศที่เปลี่ยนรูป | คำนึงถึงการเปลี่ยนเครื่องหมายของแรงยก | ฟองก๊าศในท่อ, Wall peaking |
| **Legendre-Magnaudet** | ฟองก๊าศที่มีการไหลเวียนภายใน | พิจารณาผลกระทบการไหลเวียน | ฟองก๊าศ clean |

> [!TIP] เคล็ดลับการเลือกแบบจำลอง Lift
> สำหรับฟองก๊าศในท่อแนวตั้ง แบบจำลอง **Tomiyama Lift** แนะนำอย่างยิ่งเนื่องจากจับปรากฏการณ์ "wall peaking" ที่ฟองก๊าศสะสมใกล้ผนังได้

#### **การเลือกแบบจำลอง Virtual Mass (Virtual Mass Model)**

$$\mathbf{F}_{VM} = C_{VM} \rho_c \alpha_d \left(\frac{D\mathbf{u}_c}{Dt} - \frac{D\mathbf{u}_d}{Dt}\right)$$

| สถานการณ์ | ค่า $C_{VM}$ แนะนำ | ความจำเป็น |
|------------|---------------------|--------------|
| อนุภาคหนัก ($\rho_d/\rho_c > 1000$) | สามารถละเลย | ต่ำ |
| อนุภาคเบา ($\rho_d/\rho_c < 10$) | $C_{VM} \approx 0.5$ | ==สูงมาก== |
| ฟองก๊าศในการไหลแบบไม่สมดุล | $C_{VM} = 0.5-1.0$ | สูง |

#### **การเลือกแบบจำลอง Turbulent Dispersion (Turbulent Dispersion Model)**

| แบบจำลอง | สมการ | เหมาะสำหรับ |
|------------|-----------------|--------------|
| **Burns** | $\mathbf{F}_{TD} = -C_{TD} \rho_c k \nabla \alpha_d$ | ระบบความปั่นป่วนสูง |
| **Simonin** | คำนึงถึง correlation ของความปั่นป่วน | การไหลที่มีความซับซ้อน |
| **Loth** | รวมผลกระทบของความเข้มข้น | ระบบที่มีการกระจายตัวแปรผัน |

#### **การเลือกแบบจำลอง Heat Transfer (Heat Transfer Model Selection)**

$$Pe = Re_p \cdot Pr = \frac{\rho_c c_{p,c} u_{rel} d_p}{k_c}$$

| แบบจำลอง | เงื่อนไข | สมการ $Nu$ | เหมาะสำหรับ |
|------------|------------|-------------------|--------------|
| **Ranz-Marshall** | $Pe > 1$ | $Nu = 2 + 0.6Re_p^{0.5}Pr^{0.33}$ | การถ่ายโอน convection โดดเด่น |
| **Friedlander** | จำนวนเป็กเล็ตต่ำ | การถ่ายโอนโดยการแพร่โดดเด่น | อนุภาคเล็กมาก |
| **Tomiyama** | ฟองก๊าศที่เปลี่ยนรูป | คำนึงถึงผลกระทบรูปร่าง | ฟองก๊าศขนาดกลาง-ใหญ่ |

#### **การเลือกแบบจำลอง Turbulence (Turbulence Model Selection)**

| แบบจำลอง | ความแม่นยำ | ต้นทุนการคำนาณ | เหมาะสำหรับ |
|------------|-------------|-------------------|--------------|
| **k-ε** | ปานกลาง | ต่ำ | การไหลจำนวนเรย์โนลด์สูง |
| **k-ω** | สูง (ใกล้ผนัง) | ปานกลาง | การไหลชั้นขอบเขต |
| **SST k-ω** | สูง | ปานกลาง-สูง | การไหลที่มีการแยกชั้น |
| **LES** | สูงมาก | สูงมาก | การวิเคราะห์รายละเอียด |
| **RANS** | ปานกลาง | ต่ำ | การคำนวณวิศวกรรมทั่วไป |

---

## 3. การนำไปใช้ใน OpenFOAM (Implementation in OpenFOAM)

### การกำหนดค่าแบบจำลอง (Model Configuration)

การเลือกทั้งหมดจะถูกระบุในไฟล์ `constant/phaseProperties`:

```cpp
// Example model configuration for gas-liquid system
// ตัวอย่างการกำหนดค่าแบบจำลองสำหรับระบบก๊าซ-ของเหลว
phases
{
    // Define gas phase properties
    gas
    {
        // Phase type: compressible gas
        type            gas;
        // Equation of state for ideal gas behavior
        equationOfState perfectGas;
        // Thermodynamics model: constant specific heat
        thermodynamics  hConst;
        // Transport properties: Sutherland's law for viscosity
        transport       sutherland;

        // Gas properties with SI units
        rho             rho [1 -3 0 0 0 0 0] 1.2;         // Density [kg/m³]
        mu              mu [1 -1 -1 0 0] 1.8e-5;          // Dynamic viscosity [Pa·s]
        Cp              Cp [0 2 -2 -1 -1 0 0] 1005;       // Specific heat [J/kg·K]
    }

    // Define liquid phase properties
    liquid
    {
        // Phase type: incompressible liquid
        type            incompressible;
        // Constant density equation of state
        equationOfState rhoConst;
        // Constant specific heat thermodynamics
        thermodynamics  hConst;
        // Constant transport properties
        transport       const;

        // Liquid properties with SI units
        rho             rho [1 -3 0 0 0 0 0] 1000;        // Density [kg/m³]
        mu              mu [1 -1 -1 0 0] 0.001;           // Dynamic viscosity [Pa·s]
        Cp              Cp [0 2 -2 -1 -1 0 0] 4180;       // Specific heat [J/kg·K]
        sigma           sigma [1 0 -2 0 0] 0.072;         // Surface tension [N/m]
    }
}

// Define inter-phase interaction models
phaseInteraction
{
    // Drag Model: Schiller-Naumann for spherical bubbles/drops
    dragModel       SchillerNaumann;

    SchillerNaumannCoeffs
    {
        switch1         1000;   // Reynolds number switch point
        Cd1             24.0;   // Drag coefficient for Stokes regime
        Cd2             0.44;   // Drag coefficient for Newton regime
    }

    // Lift Model: Tomiyama for deformable bubbles in pipes
    liftModel       Tomiyama;

    TomiyamaCoeffs
    {
        C1              0.44;   // Newton regime coefficient
        C2              24.0;   // Stokes regime coefficient
        C3              0.15;   // Transition exponent
        C4              6.0;    // Eötvös number coefficient
    }

    // Virtual Mass Model: Constant coefficient approach
    virtualMassModel    constant;

    constantVirtualMassCoeffs
    {
        Cvm             0.5;    // Virtual mass coefficient (0.5 for spheres)
    }

    // Turbulent Dispersion Model: Burns formulation
    turbulentDispersionModel Burns;

    BurnsCoeffs
    {
        Ctd             1.0;    // Turbulent dispersion coefficient
        D               1.0;    // Diffusion coefficient
    }

    // Wall Lubrication Model: Antal for wall-peaking prevention
    wallLubricationModel    Antal;

    AntalCoeffs
    {
        Cw1             -0.01;  // Wall lubrication coefficient 1
        Cw2             0.1;    // Wall lubrication coefficient 2
    }

    // Heat Transfer Model: Ranz-Marshall correlation
    heatTransferModel   RanzMarshall;

    RanzMarshallCoeffs
    {
        Pr              0.7;    // Prandtl number
    }
}

// Turbulence model configuration
turbulence
{
    // Base turbulence model: standard k-epsilon
    type            kEpsilon;

    kEpsilonCoeffs
    {
        Cmu             0.09;   // Turbulence viscosity coefficient
        C1              1.44;   // k-epsilon model constant C1
        C2              1.92;   // k-epsilon model constant C2
        sigmaEps        1.3;    // Turbulent Prandtl number for epsilon
        sigmaK          1.0;    // Turbulent Prandtl number for k
    }

    // Phase-specific turbulence modeling
    phaseModel
    {
        continuous     liquid;  // Continuous phase
        dispersed      gas;     // Dispersed phase

        // Dispersed phase turbulence model
        dispersedMultiphaseTurbulence
        {
            // Continuous gas Euler model for bubble turbulence
            type        continuousGasEuler;

            sigma        1.0;    // Prandtl number
            Cmu          0.09;   // Turbulence viscosity coefficient
            Prt          1.0;    // Turbulent Prandtl number
        }
    }
}
```

📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C`

**คำอธิบาย (Explanation):**
ไฟล์นี้แสดงการกำหนดค่าแบบจำลอง Inter-phase ทั้งหมดใน OpenFOAM ซึ่งเป็นการนำกรอบการตัดสินใจที่อธิบายไปแล้วมาใช้จริง โครงสร้างนี้สอดคล้องกับ `MomentumTransferPhaseSystem.C` ที่จัดการ Drag, Virtual Mass, Lift, Wall Lubrication และ Turbulent Dispersion อย่างเป็นระบบ

**แนวคิดสำคัญ (Key Concepts):**
- **Phase Properties**: การกำหนดค่าทางกายภาพของแต่ละเฟส (ความหนาแน่น ความหนืด ความตึงผิว) ต้องสอดคล้องกับอัตราส่วนคุณสมบัติที่ใช้ในการตัดสินใจ
- **Model Coefficients**: แต่ละแบบจำลองมีค่าสัมประสิทธิ์เฉพาะ (เช่น `Cvm = 0.5` สำหรับ Virtual Mass ของทรงกลม) ซึ่งได้มาจากการทดลองหรือทฤษฎี
- **Turbulence Coupling**: ระบบ Eulerian ต้องการแบบจำลองความปั่นป่วนเฉพาะสำหรับแต่ละเฟส โดยเฉพาะในระบบที่มีส่วนปริมาตรเฟสกระจายสูง

---

### การเลือก Solver ที่เหมาะสม (Solver Selection)

```cpp
// Select solver based on flow regime and system characteristics
// การเลือก Solver ตามรูปแบบการไหล
simulationType  twoPhaseEulerFoam;  // For 2-phase gas-liquid systems / สำหรับระบบก๊าซ-ของเหลว 2 เฟส
// simulationType  multiphaseEulerFoam;  // For multi-phase systems (>2 phases) / สำหรับระบบหลายเฟส (> 2 เฟส)
// simulationType  interFoam;  // For VOF method with sharp interfaces / สำหรับ VOF method
// simulationType  reactingMultiphaseEulerFoam;  // For reacting flows / สำหรับปฏิกิริยาเคมี
```

📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam`

**คำอธิบาย (Explanation):**
การเลือก Solver เป็นขั้นตอนแรกในกระบวนการตัดสินใจ ซึ่งขึ้นอยู่กับการจำแนกระบบที่อธิบายในระดับที่ 1 Solver แต่ละตัวถูกออกแบบมาเพื่อรูปแบบการไหลและวิธีการจำลองที่แตกต่างกัน

**แนวคิดสำคัญ (Key Concepts):**
- **VOF Solvers (`interFoam`)**: เหมาะสำหรับการไหลแยกชัดที่มีอินเตอร์เฟสชัดเจน ใช้ Volume of Fluid method
- **Eulerian Solvers (`multiphaseEulerFoam`, `twoPhaseEulerFoam`)**: เหมาะสำหรับการไหลกระจายที่มีหลายเฟส ใช้ Eulerian-Eulerian approach
- **Reacting Solvers**: สำหรับระบบที่มีปฏิกิริยาเคมีระหว่างเฟส ต้องการแบบจำลองเพิ่มเติมสำหรับ chemistry

---

### การตั้งค่า Solver และ Relaxation (Solver and Relaxation Settings)

```cpp
// Solver settings in system/fvSolution for stable convergence
// การตั้งค่า Solver ใน system/fvSolution
solvers
{
    // Pressure solver settings
    p
    {
        // Generalized Geometric-Algebraic Multi-grid solver
        solver          GAMG;
        // Absolute convergence tolerance
        tolerance       1e-6;
        // Relative convergence tolerance
        relTol          0.01;
        // Smoother for multi-grid method
        smoother        GaussSeidel;
    }

    // Final pressure solver (stricter tolerance)
    pFinal
    {
        solver          GAMG;
        tolerance       1e-8;
        relTol          0;
        smoother        GaussSeidel;
    }

    // Velocity solver settings
    U
    {
        // Smooth solver for velocity
        solver          smoothSolver;
        smoother        GaussSeidel;
        tolerance       1e-6;
        relTol          0;
    }

    // Phase fraction solver settings
    alpha
    {
        solver          smoothSolver;
        smoother        GaussSeidel;
        tolerance       1e-8;
        relTol          0;
    }
}

// Relaxation factors for under-relaxation to improve stability
// การตั้งค่า Relaxation Factors
relaxationFactors
{
    // Field variable relaxation
    fields
    {
        p               0.3;    // Pressure relaxation (conservative)
        U               0.7;    // Velocity relaxation
        alpha           0.7;    // Phase fraction relaxation
    }
    // Equation relaxation
    equations
    {
        p               1;      // No relaxation for pressure equation
        U               0.8;    // Momentum equation relaxation
        alpha           0.8;    // Phase fraction equation relaxation
    }
}
```

📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam`

**คำอธิบาย (Explanation):**
การตั้งค่า Solver และ Relaxation เป็นสิ่งสำคัญอย่างยิ่งสำหรับความเสถียรของการจำลอง Multiphase โดยเฉพาะอย่างยิ่งในระบบที่มี coupling ที่รุนแรงระหว่างเฟส การใช้ Under-relaxation ช่วยป้องกันการสั่นของผลลัพธ์

**แนวคิดสำคัญ (Key Concepts):**
- **Pressure-Velocity Coupling**: ความเสถียรของการแก้สมการ pressure-velocity coupling เป็นสิ่งสำคัญ โดยเฉพาะสำหรับ PISO/PIMPLE algorithms
- **Under-relaxation**: การใช้ค่า relaxation factors ต่ำ (0.3-0.7) ช่วยเพิ่มความเสถียร แต่อาจทำให้การบรรจบกันช้าลง
- **Tolerance Hierarchy**: การใช้ tolerance ที่แตกต่างกันระหว่าง intermediate และ final iterations ช่วยประหยัดเวลาคำนวณ

> [!WARNING] คำเตือนเรื่องความเสถียร
> ควรเริ่มจากแบบจำลองที่ง่ายที่สุด (เช่น Schiller-Naumann Drag และ No Lift) เพื่อตรวจสอบเสถียรภาพเบื้องต้นก่อนเพิ่มความซับซ้อน เช่น:
> 1. เริ่มด้วย Drag + Heat Transfer เท่านั้น
> 2. เพิ่ม Virtual Mass หากมีการเร่งความเร็วสูง
> 3. เพิ่ม Lift หากมี shear flow ที่สำคัญ
> 4. เพิ่ม Turbulent Dispersion หากความปั่นป่วนสูง

---

## 4. อัลกอริทึมการตัดสินใจแบบครบวงจร (Comprehensive Decision Algorithm)

```mermaid
flowchart TD
    A[เริ่มต้น] --> B{ระบุประเภทเฟส}
    B -->|Gas-Liquid| C{รูปแบบการไหล?}
    B -->|Liquid-Liquid| D{รูปแบบการไหล?}
    B -->|Gas-Solid| E{ความเข้มข้น?}
    B -->|Liquid-Solid| F{ความเข้มข้น?}

    C -->|Separated<br/>α_g < 0.3| C1[VOF<br/>interFoam]
    C -->|Dispersed<br/>α_g > 0.3| C2{Eo Number?}

    C2 -->|Eo < 1<br/>Spherical| C2a[Schiller-Naumann Drag<br/>+ Ranz-Marshall HT]
    C2 -->|1 < Eo < 4<br/>Deformed| C2b[Tomiyama Drag<br/>+ Tomiyama Lift]
    C2 -->|Eo > 4<br/>Cap bubbles| C2c[Tomiyama Drag<br/>+ Wall Lubrication<br/>+ Turbulent Dispersion]

    D -->|Separated<br/>α_d < 0.3| D1[VOF<br/>interFoam]
    D -->|Dispersed<br/>α_d > 0.3| D2{Viscosity Ratio?}

    D2 -->|μ_d/μ_c > 100<br/>High viscosity| D2a[Grace Drag<br/>+ Internal flow correction]
    D2 -->|μ_d/μ_c < 0.1<br/>Low viscosity| D2b[Schiller-Naumann Drag<br/>+ Circulation correction]

    E -->|α_s < 0.1<br/>Dilute| E1[Lagrangian<br/>DPMFoam]
    E -->|α_s > 0.1<br/>Dense| E2[Eulerian-Euler<br/>+ KTGF]

    F -->|α_s < 0.3<br/>Dilute| F1[Eulerian-Euler<br/>Wen-Yu Drag]
    F -->|α_s > 0.3<br/>Dense| F2[Eulerian-Euler<br/>+ KTGF<br/>+ Ergun Drag]

    C2a --> G{Density Ratio?}
    C2b --> G
    C2c --> G
    D2a --> G
    D2b --> G
    E1 --> G
    E2 --> G
    F1 --> G
    F2 --> G

    G -->|ρ_d/ρ_c > 1000<br/>Heavy| G1[ละเลย Virtual Mass]
    G -->|ρ_d/ρ_c < 10<br/>Light| G2[รวม Virtual Mass<br/>C_vm = 0.5]

    G1 --> H{Reynolds Number?}
    G2 --> H

    H -->|Re_p < 1000<br/>Laminar-Transition| H1[RANS k-ε]
    H -->|Re_p > 10000<br/>Fully Turbulent| H2[LES/DES<br/>สำหรับ High-fidelity]

    H1 --> I[ตั้งค่า OpenFOAM]
    H2 --> I

    I --> J[ทดสอบความเสถียร]
    J -->|เสถียร| K[เพิ่มแบบจำลองซับซ้อน]
    J -->|ไม่เสถียร| L[ปรับ Relaxation<br/>และ Time Step]
    L --> J
    K --> M[Validation<br/>กับข้อมูลทดลอง]
```

---

## 5. ตารางสรุปการเลือกแบบจำลอง (Model Selection Summary Table)

| ปรากฏการณ์ | เกณฑ์การตัดสินใจ | โมเดลแนะนำ | OpenFOAM Keyword |
|-----------|-----------------|-----------|------------------|
| **Drag - Spherical** | ทรงกลม / $Re_p < 1000$ | Schiller-Naumann | `SchillerNaumann` |
| **Drag - Deformed** | ฟองอากาศเสียรูป / $Eo > 1$ | Ishii-Zuber / Tomiyama | `IshiiZuber` / `Tomiyama` |
| **Drag - Heavy Particles** | อนุภาคหนัก / $\rho_d/\rho_c > 1000$ | Morsi-Alexander | `MorsiAlexander` |
| **Lift - Bubbles** | ฟองอากาศในท่อ | Tomiyama | `Tomiyama` |
| **Lift - Particles** | อนุภาคของแข็ง | Saffman-Mei | `SaffmanMei` |
| **Virtual Mass** | อนุภาคเบา / $\rho_d/\rho_c < 10$ | Constant ($C_{VM} = 0.5$) | `constantVirtualMass` |
| **Turbulent Dispersion** | ระบบที่มีความปั่นป่วนสูง | Burns / Simonin | `Burns` / `Simonin` |
| **Wall Lubrication** | ฟองอากาศในท่อ | Antal / Frank | `Antal` / `Frank` |
| **Heat Transfer** | ทั่วไป | Ranz-Marshall | `RanzMarshall` |
| **Turbulence - RANS** | การคำนวณวิศวกรรม | k-ε / k-ω SST | `kEpsilon` / `kOmegaSST` |
| **Turbulence - LES** | การวิเคราะห์รายละเอียด | LES Dynamic | `LES` |
| **Population Balance** | การกระจายขนาดแปรผัน | MOC / QMOM | `methodOfClasses` / `QMOM` |
| **Dense Phase** | $\alpha_d > 0.3$ | KTGF | `kineticTheory` |

---

## 6. ข้อควรพิจารณาเชิงปฏิบัติ (Practical Considerations)

### การเริ่มต้นอย่างง่าย (Start Simple Strategy)

```cpp
// STEP 1: Start with basic models only
// STEP 1: เริ่มต้นด้วยโมเดลพื้นฐาน
phaseInteraction
{
    dragModel       SchillerNaumann;
    // liftModel       none;  // Start without lift / เริ่มต้นไม่มี lift
    // virtualMassModel    none;  // Start without virtual mass / เริ่มต้นไม่มี virtual mass
    // turbulentDispersionModel none;  // Start without dispersion / เริ่มต้นไม่มี dispersion
    heatTransferModel   RanzMarshall;
}

// STEP 2: Add Virtual Mass for light particles
// STEP 2: เพิ่ม Virtual Mass สำหรับอนุภาคเบา
phaseInteraction
{
    dragModel       SchillerNaumann;
    virtualMassModel    constant;
    constantVirtualMassCoeffs { Cvm 0.5; }
    heatTransferModel   RanzMarshall;
}

// STEP 3: Add Lift for shear flow
// STEP 3: เพิ่ม Lift สำหรับ shear flow
phaseInteraction
{
    dragModel       SchillerNaumann;
    liftModel       Tomiyama;
    virtualMassModel    constant;
    heatTransferModel   RanzMarshall;
}

// STEP 4: Add Turbulent Dispersion for high turbulence
// STEP 4: เพิ่ม Turbulent Dispersion สำหรับความปั่นป่วนสูง
phaseInteraction
{
    dragModel       SchillerNaumann;
    liftModel       Tomiyama;
    virtualMassModel    constant;
    turbulentDispersionModel Burns;
    heatTransferModel   RanzMarshall;
}
```

📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/interfacialModels`

**คำอธิบาย (Explanation):**
กลยุทธ์ "Start Simple" เป็นแนวทางปฏิบัติที่สำคัญที่สุดในการจำลอง Multiphase การเพิ่มความซับซ้อนทีละน้อยช่วยให้สามารถระบุปัญหาและแก้ไขได้ง่าย รวมถึงทำให้เข้าใจผลกระทบของแต่ละแบบจำลองต่อผลลัพธ์

**แนวคิดสำคัญ (Key Concepts):**
- **Incremental Complexity**: การเพิ่มแบบจำลองทีละตัวทำให้สามารถวิเคราะห์ผลกระทบแยกกันได้
- **Baseline Validation**: การสร้าง baseline ที่เสถียรก่อนเป็นสิ่งจำเป็นสำหรับการเปรียบเทียบ
- **Debugging Strategy**: หากเกิดปัญหา สามารถย้อนกลับไปยังขั้นตอนก่อนหน้าที่เสถียรได้

---

### การปรับปรุงความเสถียร (Stability Improvements)

#### **การใช้ Implicit Coupling**
```cpp
// Implicit coupling scheme for improved stability
couplingScheme    implicit;    // Use implicit coupling between phases
maxIter          10;          // Maximum iterations per time step
residualTol      1e-6;        // Residual tolerance for convergence
```

#### **การปรับ Relaxation Factors**
```cpp
// Relaxation factors for stability
// การตั้งค่า Relaxation Factors
relaxationFactors
{
    phases        0.7;   // For phase fractions / สำหรับสัดส่วนปริมาตรเฟส
    drag          0.5;   // For drag forces / สำหรับแรง drag
    lift          0.5;   // For lift forces / สำหรับแรง lift
    turbulence    0.8;   // For turbulence / สำหรับความปั่นป่วน
}
```

#### **การใช้ Smoothing**
```cpp
// Smoothing coefficients to reduce numerical oscillations
// การใช้ Smoothing
smoothingCoeffs
{
    diameter           0.3;   // For particle diameter / สำหรับเส้นผ่านศูนย์กลาง
    interfacialArea    0.2;   // For interfacial area / สำหรับพื้นที่อินเตอร์เฟส
}
```

📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam`

**คำอธิบาย (Explanation):**
เทคนิคความเสถียรเหล่านี้เป็นสิ่งจำเป็นสำหรับการจำลอง Multiphase ที่ซับซ้อน Implicit coupling ช่วยลดความไวต่อ time step ส่วน Smoothing ช่วยลดการสั่นของค่าฟิสิกส์ใกล้อินเตอร์เฟส

**แนวคิดสำคัญ (Key Concepts):**
- **Implicit vs Explicit**: Implicit coupling แม้จะใช้เวลาคำนวณนานกว่า แต่ให้ความเสถียรที่ดีกว่าสำหรับระบบที่มี coupling สูง
- **Under-relaxation**: การลดค่า relaxation factors ช่วยป้องกันการสั่นและ divergence แต่ต้องแลกกับความเร็วในการบรรจบกัน
- **Smoothing**: การ smooth ค่าฟิลด์ช่วยลด gradient ที่สูงเกินไปและป้องกัน numerical instability

---

### การตรวจสอบความถูกต้อง (Validation)

#### **ขั้นตอนการตรวจสอบ**
1. **Mesh Independence**: ทดสอบกับ mesh ที่ละเอียดขึ้น 3 ระดับ
2. **Time Step Sensitivity**: ทดสอบกับ time step ที่แตกต่างกัน
3. **Comparison with Experiments**: เปรียบเทียบกับข้อมูลทดลอง
4. **Parameter Sensitivity**: วิเคราะห์ความไวต่อพารามิเตอร์แบบจำลอง

#### **เมตริกการตรวจสอบ**
| ประเภทเมตริก | ตัวชี้วัด | เกณฑ์การยอมรับ |
|---------------|-------------|-----------------|
| **ปริมาณโดยรวม** | ประสิทธิภาพการแยก, การลดแรงดัน | ±5% ของข้อมูลทดลอง |
| **ปรากฏการณ์ในพื้นที่** | รูปร่างส่วนต่อประสาน, โปรไฟล์ความเร็ว | ความคลาดเคลื่อน RMS < 10% |
| **มาตรการทางสถิติ** | ความคลาดเคลื่อน RMS, สัมประสิทธิ์สหสัมพันธ์ | R² > 0.85 |
| **ความสอดคล้องทางฟิสิกส์** | กฎการอนุรักษ์, เงื่อนไขขอบเขต | การละเมิด < 1% |

---

## 7. สรุป (Summary)

### หลักการสำคัญ (Key Principles)

1. **เริ่มต้นอย่างง่าย**: เริ่มจากแบบจำลองที่ง่ายที่สุดและเพิ่มความซับซ้อนทีละน้อย
2. **ใช้ตัวเลขไร้มิติ**: พารามิเตอร์เช่น $Re_p$, $Eo$, $We$ ชี้นำการเลือกแบบจำลอง
3. **คำนึงถึงอัตราส่วนคุณสมบัติ**: อัตราส่วนความหนาแน่นและความหนืดกำหนดแบบจำลองที่เหมาะสม
4. **ตรวจสอบความเสถียร**: ใช้ implicit coupling, relaxation, และ smoothing เพื่อความเสถียร
5. **ตรวจสอบความถูกต้อง**: เปรียบเทียบกับข้อมูลทดลองและทดสอบความไม่ขึ้นกับ mesh

### แผนภูมิการตัดสินใจแบบรวดเร็ว (Quick Decision Chart)

```
┌─────────────────────────────────────────────────────────────┐
│                  MODEL SELECTION QUICK GUIDE                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. System Classification                                    │
│     ├─ Gas-Liquid ──→ multiphaseEulerFoam / interFoam       │
│     ├─ Liquid-Liquid ──→ interFoam / multiphaseInterFoam    │
│     ├─ Gas-Solid ──→ multiphaseEulerFoam / DPMFoam          │
│     └─ Liquid-Solid ──→ multiphaseEulerFoam                 │
│                                                              │
│  2. Flow Regime                                             │
│     ├─ Separated (α_d < 0.3) ──→ VOF (interFoam)            │
│     └─ Dispersed (α_d > 0.3) ──→ Eulerian                   │
│                                                              │
│  3. Particle Reynolds (Re_p)                                │
│     ├─ < 1 ──→ Stokes Drag                                   │
│     ├─ 1-1000 ──→ Schiller-Naumann Drag                      │
│     └─ > 1000 ──→ Newton Drag (C_D = 0.44)                   │
│                                                              │
│  4. Deformation (Eo)                                        │
│     ├─ < 1 ──→ Spherical (Schiller-Naumann)                 │
│     ├─ 1-4 ──→ Deformed (Tomiyama)                           │
│     └─ > 4 ──→ Cap bubbles (Tomiyama + Wall Lubrication)    │
│                                                              │
│  5. Density Ratio (ρ_d/ρ_c)                                 │
│     ├─ > 1000 ──→ Heavy (Ignore Virtual Mass)                │
│     └─ < 10 ──→ Light (Include Virtual Mass, C_VM = 0.5)    │
│                                                              │
│  6. Volume Fraction (α_d)                                   │
│     ├─ < 0.1 ──→ Dilute (No KTGF)                            │
│     ├─ 0.1-0.3 ──→ Intermediate (Consider KTGF)              │
│     └─ > 0.3 ──→ Dense (REQUIRES KTGF)                       │
│                                                              │
│  7. Turbulence                                              │
│     ├─ Engineering ──→ RANS (k-ε, k-ω SST)                  │
│     └─ High-Fidelity ──→ LES / DES                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

> [!SUCCESS] คำแนะนำสุดท้าย
> การเลือกแบบจำลองที่เหมาะสมเป็นศาสตร์ที่ต้องอาศัยทั้งความเข้าใจทางฟิสิกส์และประสบการณ์ ใช้กรอบการตัดสินใจนี้เป็นแนวทาง แต่อย่าลืมที่จะปรับเปลี่ยนตามสถานการณ์เฉพาะของคุณ เมื่อสงสัย → **เริ่มต้นอย่างง่าย**