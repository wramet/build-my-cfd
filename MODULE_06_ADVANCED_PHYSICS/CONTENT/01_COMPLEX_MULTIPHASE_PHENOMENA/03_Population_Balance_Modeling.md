# Population Balance Modeling (การจำลองสมดุลประชากร)

> **PBM** = Track particle size distribution evolution

---

## 1. ภาพรวม (Overview)

Population Balance Modeling (PBM) ใช้สำหรับติดตามการกระจายขนาดของอนุภาคที่เปลี่ยนแปลงตามเวลา เช่น:
- ฟองอากาศที่เกิดและแตกตัว (Bubble breakup & coalescence)
- หยดของเหลวที่รวมตัวกัน (Droplet coalescence)
- การเติบโตของผลึก (Crystal growth)

### 1.1 ทำไมต้องใช้ PBM?

ในการจำลอง multiphase แบบดั้งเดิม มักสมมติว่า:
- ฟองมีขนาดคงที่ (Mean diameter)
- การกระจายขนาดไม่สำคัญ

แต่ในความเป็นจริง:
- ฟองมี **ขนาดต่างกัน** (Polydisperse)
- ฟอง **แตกตัว** (Breakup) เมื่อถูก shear สูง
- ฟอง **รวมตัว** (Coalescence) เมื่อชนกัน
- ขนาดฟองส่งผลต่อ **interfacial area** และ **mass transfer**

---

## 2. Population Balance Equation (สมการสมดุลประชากร)

### 2.1 สมการทั่วไป

$$\frac{\partial n}{\partial t} + \nabla \cdot (\mathbf{u} n) = \mathcal{B} - \mathcal{D} + \mathcal{B}_{breakup} - \mathcal{D}_{breakup}$$

โดยที่:
- $n(d, \mathbf{x}, t)$ = Number density function [1/m⁴]
- $d$ = Particle diameter [m]
- $\mathbf{x}$ = Position [m]
- $t$ = Time [s]
- $\mathcal{B}$ = Birth rate from coalescence
- $\mathcal{D}$ = Death rate from coalescence
- $\mathcal{B}_{breakup}$ = Birth rate from breakup
- $\mathcal{D}_{breakup}$ = Death rate from breakup

### 2.2 เงื่อนไขแหล่งกำเนิด (Source Terms)

**Coalescence (การรวมตัว):**
$$\mathcal{B}_{coal} = \frac{1}{2} \int_0^d \omega(d', d-d') n(d') n(d-d') \, dd'$$
$$\mathcal{D}_{coal} = n(d) \int_0^\infty \omega(d, d') n(d') \, dd'$$

**Breakup (การแตกตัว):**
$$\mathcal{B}_{break} = \int_d^\infty g(d') \beta(d|d') n(d') \, dd'$$
$$\mathcal{D}_{break} = g(d) n(d)$$

โดยที่:
- $\omega(d_i, d_j)$ = Coalescence rate [m³/s]
- $g(d)$ = Breakup rate [1/s]
- $\beta(d|d')$ = Daughter size distribution

---

## 3. การ Implement ใน OpenFOAM

### 3.1 การตั้งค่า Population Balance

```cpp
// constant/phaseProperties
populationBalanceCoeffs
{
    // ชื่อของ population balance
    populationBalance bubbles;

    // โมเดลการรวมตัว
    coalescenceModels
    (
        LehrMilliesMewes
        {
            // Coalescence parameters
        }
    );

    // โมเดลการแตกตัว
    breakupModels
    (
        LehrMilliesMewes
        {
            // Breakup parameters
        }
    );
}
```

### 3.2 การตั้งค่า Size Groups (Velocity Group Method)

```cpp
// constant/phaseProperties
diameterModel velocityGroup;

velocityGroupCoeffs
{
    populationBalance bubbles;

    // รูปร่างของฟอง
    shapeModel spherical;

    // กลุ่มขนาด (size groups)
    sizeGroups
    (
        f0 { d 1e-4; }    // 100 μm
        f1 { d 2e-4; }    // 200 μm
        f2 { d 4e-4; }    // 400 μm
        f3 { d 8e-4; }    // 800 μm
        f4 { d 1.6e-3; }  // 1.6 mm
    );
}
```

### 3.3 การคำนวณ Sauter Mean Diameter

OpenFOAM คำนวณ Sauter Mean Diameter (SMD) หรือ d32:

$$d_{32} = \frac{\sum n_i d_i^3}{\sum n_i d_i^2}$$

ซึ่งใช้สำหรับคำนวณพื้นที่ผิวรวม:

$$A_{int} = \frac{6 \alpha}{d_{32}}$$

---

## 4. แบบจำลอง Coalescence (การรวมตัว)

### 4.1 เปรียบเทียบโมเดล

| Model | การใช้งาน | ความซับซ้อน |
|-------|-------------|--------------|
| **LehrMilliesMewes** | Bubble coalescence | สูง |
| **CoulaloglouTavlarides** | Liquid drops | ปานกลาง |
| **Constant** | Simple testing | ต่ำ |
| **PrinceBlanch** | Bubbles in liquid | สูง |

### 4.2 แบบจำลอง Lehr-Millies-Mewes

อัตราการรวมตัวขึ้นกับ:
- **Collision frequency**: อัตราการชนกัน
- **Coalescence efficiency**: โอกาสที่จะรวมตัวเมื่อชน

$$\omega(d_i, d_j) = \frac{\pi}{4} (d_i + d_j)^2 |\mathbf{u}_i - \mathbf{u}_j| \cdot P_{coal}$$

```cpp
// การตั้งค่า LehrMilliesMewes
LehrMilliesMewes
{
    // ค่าสัมประสิทธิ์
    C1  0.15;   // Model coefficient
    C2  0.006;  // Model coefficient
}
```

---

## 5. แบบจำลอง Breakup (การแตกตัว)

### 5.1 เปรียบเทียบโมเดล

| Model | กลไกหลัก | การใช้งาน |
|-------|-----------|-------------|
| **LehrMilliesMewes** | Turbulent breakup | Bubbles ทั่วไป |
| **LuoSvendsen** | Energy-based | Drops ที่มีความหนืดสูง |
| **Laakkonen** | High shear | ระบบ shear สูง |
| **MartinezBazan** | Turbulence | Bubbles in turbulent flow |

### 5.2 แบบจำลอง Lehr-Millies-Mewes

ขึ้นกับ:
- **Turbulent kinetic energy** (k)
- **Dissipation rate** (ε)

$$g(d) = C_1 \frac{\epsilon^{1/3}}{d^{2/3}} \exp\left(-C_2 \frac{\sigma (1 + \Phi)^2}{\rho_d \epsilon^{2/3} d^{5/3}}\right)$$

```cpp
// การตั้งค่า LehrMilliesMewes
LehrMilliesMewes
{
    C1  0.084;  // Breakup coefficient
    C2  1.26;   // Viscosity correction

    // ค่าเพิ่มเติม
    WeCrit  1.3;  // Critical Weber number
}
```

---

## 6. Solvers

```bash
# Solvers หลักที่รองรับ PBM
multiphaseEulerFoam           # Euler-Euler multiphase พร้อม PBM
reactingTwoPhaseEulerFoam     # Reacting multiphase พร้อม PBM

# Solvers อื่นๆ
bubbleFoam                    # Bubble column พร้อม PBM
twoPhaseEulerFoam             # Two-phase Euler-Euler
```

---

## 7. การตั้งค่า Case แบบสมบูรณ์

### 7.1 Boundary Conditions สำหรับ Size Groups

```cpp
// 0/f0 (size group 0)
dimensions      [0 0 0 0 0 0 0];

internalField   uniform 0;  // เริ่มต้นไม่มีฟอง

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 0.2;  // 20% ปริมาตรของ size group 0
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

### 7.2 Numerical Schemes

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
    default         Gauss upwind;  // สำคัญสำหรับ size groups
}

laplacianSchemes
{
    default         Gauss linear corrected;
}
```

### 7.3 Solver Settings

```cpp
// system/fvSolution
solvers
{
    // Size group solver
    "\"f.*\""
    {
        solver          GAMG;
        tolerance       1e-6;
        relTol          0.01;
        smoother        GaussSeidel;
    }

    // Pressure solver
    p
    {
        solver          GAMG;
        tolerance       1e-7;
        relTol          0.01;
    }
}
```

---

## 8. ข้อควรระวังและปัญหาที่พบบ่อย

| ปัญหา | สาเหตุ | วิธีแก้ |
|--------|---------|---------|
| **Mass imbalance** | Size groups ไม่สมดุล | ตรวจสอบ Σα = 1 |
| **Slow convergence** | จำนวน size groups มาก | ลดจำนวน groups หรือเพิ่ม under-relaxation |
| **Unrealistic distribution** | Coalescence/Breakup params ผิด | ปรับ parameters ให้เหมาะสม |
| **Numerical diffusion** | Scheme ไม่เหมาะสม | ใช้ upwind scheme สำหรับ size groups |

---

## 9. การตรวจสอบและ Post-processing

### 9.1 การคำนวณ Sauter Mean Diameter

```cpp
// ใน controlDict หรือ custom function
functions
{
    d32Calculation
    {
        type            coded;
        functionObjectLibs ("libutilityFunctionObjects.so");
        writeTime       yes;

        code
        #{
            const volScalarField& alpha = mesh().lookupObject<volScalarField>("alpha.water");
            const volScalarField& d32 = mesh().lookupObject<volScalarField>("d32");

            // d32 ถูกคำนวณอัตโนมัติโดย population balance model
        #};
    }
}
```

### 9.2 การ Plot การกระจายขนาด

```bash
# Extract data at specific location
probesLocations
(
    (0.1 0 0)
    (0.2 0 0)
)

# Plot size distribution
python plotSizeDistribution.py
```

---

## Quick Reference

| Process | Models | Parameter |
|---------|--------|-----------|
| **Coalescence** | LehrMillies, Coulaloglou | ω = collision rate × efficiency |
| **Breakup** | Luo, Laakkonen, Lehr | g = f(ε, d, σ) |
| **Size groups** | velocityGroup | f0, f1, f2, ... |
| **SMD** | d32 | Σnd³/Σnd² |

---

## 🧠 Concept Check

<details>
<summary><b>1. PBM ใช้เมื่อไหร่?</b></summary>

**Track size distribution** — เช่น bubbles, drops

ใช้ PBM เมื่อ:
- ฟอง/หยดมี **ขนาดไม่สม่ำเสมอ** (Polydisperse)
- ต้องการรู้ **การกระจายขนาด** (Size distribution)
- มี **breakup** และ **coalescence** พร้อมกัน
- Interfacial area สำคัญต่อ mass/heat transfer

</details>

<details>
<summary><b>2. Coalescence คืออะไร?</b></summary>

**Particles merge** → larger size

Coalescence (การรวมตัว) คือกระบวนการที่อนุภาคเล็กๆ รวมตัวกันเป็นอนุภาคที่ใหญ่ขึ้น:

$$d_1 + d_2 \rightarrow d_{new}$$

**ปัจจัยที่ส่งผล:**
- **Collision frequency**: ความถี่การชนกัน
- **Film drainage time**: เวลาที่ฟิล์มของเหลวระหว่างฟองระเหย
- **Surface tension**: แรงดึงดูดผิว
- **Viscosity**: ความหนืดของของเหลว

</details>

<details>
<summary><b>3. Size groups คืออะไร?</b></summary>

**Discrete sizes** สำหรับ represent distribution

Size groups คือการ **แบ่งช่วงขนาด** ของอนุภาคเป็น discrete bins:

```
Bin 0: 0-100 μm      (f0)
Bin 1: 100-200 μm    (f1)
Bin 2: 200-400 μm    (f2)
...
```

**ข้อดี:**
- แก้ PBE ได้ง่ายกว่า continuous method
- สามารถ represent การกระจายที่ซับซ้อนได้
- ใช้ memory น้อยกว่า QMOM

**ข้อเสีย:**
- ต้องมีจำนวน groups เพียงพอ (trade-off กับ computational cost)
- การแบ่งช่วงต้องครอบคลุม range ที่สนใจ

</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md) — ภาพรวม Complex Multiphase
- **Phase Change:** [01_Phase_Change_Modeling.md](01_Phase_Change_Modeling.md) — การเปลี่ยนสถานะ
- **Cavitation:** [02_Cavitation_Modeling.md](02_Cavitation_Modeling.md) — การจำลอง Cavitation