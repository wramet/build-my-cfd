# Cavitation Modeling (การจำลอง Cavitation)

> **Cavitation** = Phase change from liquid to vapor at low pressure

<!-- IMAGE: IMG_06_004 -->
<!--
Purpose: เพื่ออธิบายกลไกการเกิด Cavitation ที่ใบพัดหรือ Hydrofoil. ภาพนี้ต้องเชื่อมโยง "กราฟความดัน" ($C_p$) กับ "ตำแหน่งที่เกิดฟอง" (Vapor Region). จุดสำคัญคือ: ฟองจะเกิดเมื่อกราฟความดันจุ่มลงต่ำกว่าเส้น $P_{sat}$ (Saturation Pressure)
Prompt: "Physics Diagram of Hydrofoil Cavitation. **Scene:** A Hydrofoil cross-section in blue water flow. **Overlay Graphs:** 1. **Pressure Coefficient ($C_p$) Curve:** Plotted along the foil chord. The curve dips deeply on the upper surface (Suction side). 2. **Saturation Line ($P_{sat}$):** A horizontal dashed line intersecting the pressure curve. **Vapor Zone:** Calculate the area where Pressure Curve < Saturation Line $\rightarrow$ Highlight this region on the foil surface as 'Vapor/White Bubble Cloud'. **Collapse:** Show bubbles collapsing at the trailing edge where pressure recovers. STYLE: Mixed-media (Engineering Chart + Physical Flow), clear threshold indicators."
-->
![[IMG_06_004.jpg]]

---

## 1. ฟิสิกส์ของ Cavitation (Physics of Cavitation)

Cavitation เป็นปรากฏการณ์ที่เกิดจาก **ความดันต่ำกว่าความดันอิ่มตัว (Saturation Pressure)** ทำให้ของเหลวกลายเป็นไอ:

```
p < pSat → liquid → vapor (evaporation/เกิดฟอง)
p > pSat → vapor → liquid (condensation/ฟองยุบ)
```

### 1.1 ขั้นตอนการเกิด Cavitation

1. **Nucleation** (การเกิดฟองเริ่มแรก): เมื่อความดันต่ำกว่า $p_{sat}$
2. **Growth** (การเติบโตของฟอง): ฟองขยายตัวอย่างรวดเร็ว
3. **Collapse** (การยุบตัว): เมื่อฟองเคลื่อนไปยังบริเวณที่ความดันสูงกว่า

### 1.2 ผลกระทบของ Cavitation

| ผลกระทบ | คำอธิบาย |
|----------|-----------|
| **Material Damage** | การยุบตัวของฟองสร้าง shock wave ทำลายพื้นผิว |
| **Noise** | เสียงดังจากการยุบตัวของฟอง |
| **Performance Loss** | ส่งผลต่อประสิทธิภาพของปั๊ม/ใบพัด |
| **Vibration** | สร้างการสั่นสะเทือนในระบบ |

---

## 2. Solvers ใน OpenFOAM

```bash
# Cavitation solver (หลัก)
interPhaseChangeFoam

# Multiphase solvers ที่รองรับ cavitation
multiphaseEulerFoam
reactingTwoPhaseEulerFoam
```

---

## 3. แบบจำลอง Cavitation (Cavitation Models)

### 3.1 เปรียบเทียบแบบจำลอง

| Model | ความแม่นยำ | ความเสถียร | การใช้งาน |
|-------|------------|------------|-------------|
| **SchnerrSauer** | สูง | สูง | General purpose |
| **Kunz** | ปานกลาง | สูงมาก | Marine propellers |
| **Merkle** | สูง | ปานกลาง | Industrial |
| **Zwart** | สูง | สูง | Pumps, inducers |

### 3.2 แบบจำลอง SchnerrSauer

```cpp
// constant/phaseProperties
phaseChangeModel SchnerrSauer;

SchnerrSauerCoeffs
{
    n       1.6e13;  // Nucleation site density [1/m³]
    dNuc    2e-6;    // Nucleation diameter [m]
    Cc      1;       // Condensation coefficient
    Cv      1;       // Vaporization coefficient
}
```

**อัตราการถ่ายเทมวล (Mass Transfer Rate):**

$$\Gamma = \frac{\rho_v \rho_l}{\rho} \cdot \frac{3 \alpha (1-\alpha)}{R} \sqrt{\frac{2}{3} \frac{|p - p_{sat}|}{\rho_l}} \cdot \text{sign}(p_{sat} - p)$$

### 3.3 แบบจำลอง Kunz

```cpp
phaseChangeModel Kunz;

KunzCoeffs
{
    UInf    10;      // Freestream velocity [m/s]
    tInf    0.01;    // Characteristic time [s]
    Cc      0.01;    // Condensation coefficient
    Cv      1000;    // Vaporization coefficient
}
```

### 3.4 แบบจำลอง Merkle

```cpp
phaseChangeModel Merkle;

MerkleCoeffs
{
    UInf    10;      // Freestream velocity [m/s]
    tInf    0.01;    // Characteristic time [s]
    Cc      0.01;    // Condensation coefficient
    Cv      100;     // Vaporization coefficient
}
```

---

## 4. การตั้งค่า Thermophysical Properties

```cpp
// constant/transportProperties
phases (water vapor);

water
{
    transportModel  Newtonian;
    nu              1e-6;    // Kinematic viscosity [m²/s]
    rho             1000;    // Density [kg/m³]
}

vapor
{
    transportModel  Newtonian;
    nu              4.273e-4;  // Kinematic viscosity [m²/s]
    rho             0.023;     // Density [kg/m³]
}

// Saturation pressure
pSat    2300;  // [Pa] for water at 20°C
```

### 4.1 ค่าความดันอิ่มตัวที่อุณหภูมิต่างๆ (สำหรับน้ำ)

| อุณหภูมิ (°C) | pSat (Pa) | pSat (bar) |
|----------------|-----------|------------|
| 20 | 2339 | 0.023 |
| 25 | 3169 | 0.032 |
| 50 | 12349 | 0.123 |
| 75 | 38598 | 0.386 |
| 100 | 101325 | 1.013 |

---

## 5. สมการการถ่ายเทมวล (Mass Transfer Equation)

```cpp
// Source term in VOF equation
∂α/∂t + ∇·(Uα) = Γₑ - Γc

α  = Vapor volume fraction
Γₑ = Evaporation rate (liquid → vapor)
Γc = Condensation rate (vapor → liquid)
```

### 5.1 อัตราการเกิดและยุบตัวของฟอง

**Evaporation (เมื่อ p < p_sat):**
$$\Gammaₑ = C_v \cdot \frac{\rho_v \rho_l}{\rho} \cdot \frac{3 \alpha (1-\alpha)}{R} \sqrt{\frac{2}{3} \frac{p_{sat} - p}{\rho_l}}$$

**Condensation (เมื่อ p > p_sat):**
$$\Gamma_c = C_c \cdot \frac{\rho_v \rho_l}{\rho} \cdot \frac{3 \alpha (1-\alpha)}{R} \sqrt{\frac{2}{3} \frac{p - p_{sat}}{\rho_l}}$$

---

## 6. การตั้งค่าเชิงตัวเลข (Numerical Settings)

### 6.1 fvSchemes

```cpp
// system/fvSchemes
ddtSchemes
{
    default         Euler;
}

gradSchemes
{
    default         Gauss linear;
}

divSchemes
{
    div(rhoPhi,U)   Gauss linearUpwind grad(U);
    div(phi,alpha)  Gauss vanLeer;        // สำคัญสำหรับ VOF
    div(rhoPhi,k)   Gauss linearUpwind grad(k);
    div(rhoPhi,epsilon) Gauss linearUpwind grad(epsilon);
}

laplacianSchemes
{
    default         Gauss linear corrected;
}
```

### 6.2 fvSolution

```cpp
// system/fvSolution
PIMPLE
{
    nCorrectors      3;       // เพิ่มจำนวนรอบสำหรับ stability
    nNonOrthogonalCorrectors 0;
    nAlphaCorr      1;        // จำนวนรอบสำหรับ volume fraction
    nAlphaSubCycles 2;        // Sub-cycles สำหรับ alpha
}

solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-7;
        relTol          0.01;
    }

    pFinal
    {
        solver          GAMG;
        tolerance       1e-7;
        relTol          0;
    }
}
```

### 6.3 Control Dict

```cpp
// system/controlDict
application     interPhaseChangeFoam;

startFrom       startTime;

startTime       0;

stopAt          endTime;

endTime         0.01;

deltaT          1e-5;

writeControl    timeStep;

writeInterval   100;

adjustTimeStep  yes;

maxCo           0.3;      // สำคัญมากสำหรับ cavitation
maxAlphaCo      0.3;
}
```

---

## 7. Boundary Conditions

### 7.1 Pressure (p)

```cpp
// 0/p
dimensions      [1 -1 -2 0 0 0 0];

internalField   uniform 1e5;  // 1 bar

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 2e5;  // 2 bar
    }

    outlet
    {
        type            fixedValue;
        value           uniform 1e5;  // 1 bar
    }

    walls
    {
        type            zeroGradient;
    }
}
```

### 7.2 Velocity (U)

```cpp
// 0/U
dimensions      [0 1 -1 0 0 0 0];

internalField   uniform (10 0 0);  // 10 m/s

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform (10 0 0);
    }

    outlet
    {
        type            zeroGradient;
    }

    walls
    {
        type            noSlip;
    }
}
```

### 7.3 Volume Fraction (alpha.water)

```cpp
// 0/alpha.water
dimensions      [0 0 0 0 0 0 0];

internalField   uniform 1;  // Pure liquid initially

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 1;
    }

    outlet
    {
        type            zeroGradient;
    }

    walls
    {
        type            zeroGradient;
    }
}
```

---

## 8. ข้อควรระวังและเทคนิคการแก้ปัญหา

| ปัญหา | สาเหตุ | วิธีแก้ |
|--------|---------|---------|
| **Divergence** | Timestep ใหญ่ | ลด maxCo < 0.3 |
| **Oscillations** | Pressure-velocity coupling | เพิ่ม nCorrectors |
| **Unphysical cavitation** | pSat ตั้งผิด | ตรวจสอบค่า pSat |
| **Slow convergence** | mesh ห่างเกินไป | ใช้ mesh ละเอียดบริเวณ low pressure |

---

## Quick Reference

| Parameter | Typical Value | หน่วย |
|-----------|---------------|------|
| pSat (water 20°C) | 2300 | Pa |
| Nuclei density | 1e13 | 1/m³ |
| Nuclei size | 2e-6 | m |
| maxCo | < 0.3 | - |
| nCorrectors | 3-5 | - |

---

## 🧠 Concept Check

<details>
<summary><b>1. Cavitation เกิดเมื่อไหร่?</b></summary>

**p < pSat** — pressure below saturation pressure

เมื่อความดันในของเหลวต่ำกว่าความดันอิ่มตัว (saturation pressure) ที่อุณหภูมินั้น ของเหลวจะเริ่มเปลี่ยนสถานะเป็นไอ

</details>

<details>
<summary><b>2. SchnerrSauer model ทำอะไร?</b></summary>

**Mass transfer rate based on bubble dynamics**

แบบจำลอง SchnerrSauer คำนวณอัตราการถ่ายเทมวล (mass transfer rate) ระหว่างเฟสของเหลวและไอ โดยอิงจาก:
- จำนวนฟอง nucleation sites
- ขนาดเริ่มต้นของฟอง
- ความแตกต่างของความดันจากค่า saturation

</details>

<details>
<summary><b>3. ทำไม cavitation สำคัญในงานวิศวกรรม?</b></summary>

**Damage, noise, performance loss in pumps/propellers**

1. **Material Damage**: การยุบตัวของฟองสร้าง shock wave ที่สามารถทำลายพื้นผิวโลหะได้
2. **Noise**: สร้างเสียงดังที่เป็นปัญหาในงาน marine
3. **Performance Loss**: ลดประสิทธิภาพของปั๊มและใบพัด
4. **Vibration**: สร้างการสั่นสะเทือนที่เป็นอันตรายต่อโครงสร้าง

</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md) — ภาพรวม Complex Multiphase
- **Phase Change:** [01_Phase_Change_Modeling.md](01_Phase_Change_Modeling.md) — การเปลี่ยนสถานะ
- **Population Balance:** [03_Population_Balance_Modeling.md](03_Population_Balance_Modeling.md) — สมดุลประชากร
