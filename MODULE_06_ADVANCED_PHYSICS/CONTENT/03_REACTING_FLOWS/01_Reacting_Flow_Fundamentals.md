# Reacting Flow Fundamentals

พื้นฐาน Reacting Flows

---

## 🎯 Learning Objectives

หลังจากอ่านบทนี้ ผู้อ่านควรจะสามารถ:

- **อธิบาย (Explain):** สมการพื้นฐานของการ transport สารประกอบ (species transport) และปฏิกิริยาเคมีในกระแสไหล
- **วิเคราะห์ (Analyze):** บทบาทของ Arrhenius rate law และ ODE solver ในการจำลองปฏิกิริยาเคมี
- **ประยุกต์ (Apply):** การตั้งค่า OpenFOAM solver สำหรับปัญหา reacting flow ขั้นพื้นฐาน
- **เปรียบเทียบ (Compare):** ความแตกต่างระหว่าง solvers ที่ใช้สำหรับ reacting flow ประเภทต่างๆ

---

## 3W Framework: Reacting Flow Fundamentals

### What (อะไรคือ Reacting Flow Fundamentals?)

**Reacting Flow Fundamentals** คือพื้นฐานทางฟิสิกส์และคณิตศาสตร์ของการไหลของไหลพร้อมกับเกิดปฏิกิริยาเคมี (chemical reactions) ซึ่งรวมถึง:

1. **Species Transport Equations:** สมการ transport ของสารแต่ละชนิด
2. **Reaction Rate Laws:** กฎของอัตราปฏิกิริยา (เช่น Arrhenius)
3. **Energy Coupling:** การเชื่อมโยงระหว่าง heat release และ thermodynamics
4. **Numerical Methods:** เทคนิคการแก้ ODE สำหรับ stiff chemistry

### Why (ทำไมต้องเรียนรู้?)

พื้นฐานเหล่านี้จำเป็นเพราะ:

- **การเชื่อมโยงทางฟิสิกส์:** ปฏิกิริยาเคมีสร้าง heat release → เปลี่ยน temperature → เปลี่ยน density → กระทบ velocity field (two-way coupling)
- **ความแม่นยำของการจำลอง:** การเข้าใจ rate kinetics และ ODE solvers สำคัญต่อการทำนาย flame behavior ได้ถูกต้อง
- **การเลือก solver:** ปัญหา reacting flow แต่ละประเภท (premixed, non-premixed, laminar, turbulent) ต้องการ solver ที่แตกต่างกัน
- **พื้นฐานสำหรับ Combustion Models:** ก่อนจะไปใช้ combustion models ขั้นสูง (flamelet, PDF, EDC) ต้องเข้าใจ fundamentals นี้ก่อน

### How (OpenFOAM นำไปใช้อย่างไร?)

OpenFOAM นำพื้นฐานเหล่านี้มาใช้ผ่าน:

1. **Thermodynamics Package:** ระบบ `speciesThermo` + `reactionThermo` ใน `thermophysicalProperties`
2. **Chemistry Library:** `ODEChemistryModel` สำหรับแก้สมการ kinetics
3. ** reactingFoam Solver:** Solver หลักที่รวม species transport + energy + chemistry
4. **Flexible ODE Solvers:** รองรับ stiff solvers (seulex, rodas) สำหรับ fast chemistry
5. **Standardized Syntax:** การใช้ `reactionRate` dictionary และ `chemistryProperties` ที่เป็นมาตรฐาน

---

## Overview

> Chemical reactions in flowing fluids

<!-- IMAGE: IMG_06_003 -->
<!-- 
Purpose: เพื่อแสดงโครงสร้างของ "เปลวไฟ" (Flame Structure) ในเชิง CFD. ภาพนี้ต้องโชว์การเปลี่ยนแปลงของ 3 ตัวแปรหลักเมื่อผ่านเปลวไฟ: 1. เชื้อเพลิง ($Y_{Fuel}$) ลดลง 2. ผลิตภัณฑ์ ($Y_{Product}$) เพิ่มขึ้น 3. อุณหภูมิ ($T$) พุ่งสูงขึ้น และจุดที่กราฟตัดกันคือตำแหน่งของ "Reaction Zone"
Prompt: "Combustion Physics Profile Diagram (Pre-mixed Flame). **X-axis:** Distance through flame. **Y-axis:** Normalized Value (0 to 1). **Curves:** 1. **Fuel Mass Fraction (Blue):** Starts at 1, drops sharply to 0 at the flame front. 2. **Oxidizer Mass Fraction (Green):** Follows Fuel curve. 3. **Product Mass Fraction (Purple):** Starts at 0, rises sharply to 1. 4. **Temperature (Red):** S-Curve starting low (Unburnt) and rising to high (Burnt). **Highlight:** A vertical zone labeled 'Reaction Zone $\dot{\omega}$' where the gradients are steepest. STYLE: Textbook scientific plot, clear lines, distinct zones."
-->

![Flame Structure Profile](IMG_06_003.jpg)

**ภาพอธิบาย:** โครงสร้างเปลวไฟแบบ premixed แสดงการเปลี่ยนแปลงของ:
- **Fuel Mass Fraction (สีน้ำเงิน):** ลดลงจาก 1 → 0 ในบริเวณ reaction zone
- **Product Mass Fraction (สีม่วง):** เพิ่มขึ้นจาก 0 → 1 หลังผ่านเปลวไฟ
- **Temperature (สีแดง):** เพิ่มขึ้นแบบ S-curve จาก unburnt → burnt

---

## 1. Species Transport Equation

### 1.1 สมการหลัก (Governing Equation)

สมการ transport ของสารแต่ละชนิดใน reacting flow:

```
∂(ρYᵢ)/∂t + ∇·(ρUYᵢ) = ∇·(ρDᵢ∇Yᵢ) + ωᵢ
```

**ประกอบด้วย:**

| คำศัพท์ (Term) | ความหมาย (Meaning) | หน่วย (Unit) |
|-----------------|---------------------|---------------|
| `∂(ρYᵢ)/∂t` | Rate of change ของ mass fraction | kg/(m³·s) |
| `∇·(ρUYᵢ)` | Convection ของ species | kg/(m³·s) |
| `∇·(ρDᵢ∇Yᵢ)` | Diffusion ของ species | kg/(m³·s) |
| `ωᵢ` | **Reaction source term** | kg/(m³·s) |

### 1.2 ข้อจำกัดสำคัญ (Constraints)

```
ΣYᵢ = 1    (Sum of all mass fractions = 1)

Σωᵢ = 0    (Sum of all reaction rates = 0, mass conserved)
```

### 1.3 การนำไปใช้ใน OpenFOAM

สมการนี้ถูกแก้โดย automatic ใน `reactingFoam` ผ่าน:

```cpp
// ใน reactingFoam solver, species transport ถูกแก้โดยอัตโนมัติ
// แต่ละ species มี equation ของตัวเอง:
fvScalarMatrix YEqn
(
    fvm::ddt(rho, Yi)
  + fvm::div(phi, Yi)
  - fvm::laplacian(rho*Di, Yi)
 ==
    chemistry->R(Yi)  // Reaction source term
);
```

---

## 2. Reaction Rate Fundamentals

### 2.1 Arrhenius Rate Law

กฎของอัตราปฏิกิริยาแบบ **Arrhenius** (temperature-dependent):

```
k = A × Tⁿ × exp(-Ea / RT)
```

**ประกอบด้วย:**

| พารามิเตอร์ | ชื่อ (Name) | ความหมาย (Meaning) | หน่วย |
|-------------|-------------|---------------------|--------|
| `A` | Pre-exponential factor | ค่าคงที่ของความถี่ collision | (varies) |
| `Ea` | Activation energy | พลังงานขั้นต่ำที่ต้องใช้เพื่อเกิดปฏิกิริยา | J/mol |
| `n` | Temperature exponent | ความเข้มของอุณหภูมิต่อ rate | (-) |
| `R` | Universal gas constant | ค่าคงที่ก๊าซ | 8.314 J/(mol·K) |
| `T` | Temperature | อุณหภูมิ | K |

### 2.2 ตัวอย่างการใช้งานใน OpenFOAM

```cpp
// constant/chemistryProperties หรือ reactions file
reactions
{
    methane_reaction
    {
        type    ArrheniusReaction;
        
        // Arrhenius parameters
        A       1.68e10;      // Pre-exponential [m³/kmol/s]
        beta    0.0;          // Temperature exponent (n)
        Ea      1.0e5;        // Activation energy [J/kmol]
        
        // Species involved
        reaction    "CH4 + 2O2 => CO2 + 2H2O";
    }
}
```

### 2.3 ผลกระทบของ Temperature

**Exponential term `exp(-Ea/RT)`:**
- อุณหภูมิต่ำ → rate ต่ำมาก (ปฏิกิริยาช้ามาก)
- อุณหภูมิสูง → rate สูงมาก (ปฏิกิริยาเร็ว)
- **Stiff system:** ความแตกต่างของ timescale ทำให้ต้องใช้ ODE solver พิเศษ

---

## 3. Energy Equation with Heat Release

### 3.1 สมการพลังงาน (Energy Equation)

ใน reacting flow, สมการพลังงานต้องรวม **heat release from reactions (`Qdot`)**:

```cpp
// รูปแบบ OpenFOAM สำหรับ sensible enthalpy
fvScalarMatrix TEqn
(
    fvm::ddt(rho, he)           // Unsteady term
  + fvm::div(phi, he)           // Convection
  - fvm::laplacian(alphaEff, he) // Diffusion
 ==
    Qdot                         // Heat release from chemistry
);
```

### 3.2 Heat Release Calculation

```
Qdot = Σ(ωᵢ × h_f,i⁰)

ωᵢ = reaction rate of species i [kg/(m³·s)]
h_f,i⁰ = heat of formation of species i [J/kg]
```

### 3.3 Two-Way Coupling

**Physics of coupling:**

1. **Chemistry → Flow:** `Qdot` → temperature ↑ → density ↓ → velocity ↑
2. **Flow → Chemistry:** `convection` → transport species → reaction rate เปลี่ยน

---

## 4. OpenFOAM Setup Fundamentals

### 4.1 Chemistry Properties Configuration

```cpp
// constant/chemistryProperties
chemistryType
{
    // ODE solver for stiff chemistry
    chemistrySolver ode;
    
    // Thermodynamics type
    chemistryThermo psi;
}

// Enable chemistry
chemistry       on;

// Initial time step for chemistry (small for stiff system)
initialChemicalTimeStep 1e-7;
```

### 4.2 Thermophysical Properties

```cpp
// constant/thermophysicalProperties
thermoType
{
    type            heRhoThermo;
    mixture         multiComponentMixture;
    transport       sutherland;
    thermo          janaf;
    energy          sensibleEnthalpy;
    equationOfState perfectGas;
    specie          specie;
}

// Species definition
species
(
    CH4
    O2
    CO2
    H2O
    N2
);
```

---

## 5. Solver Selection Guide

| Solver | ประเภท (Type) | การใช้งาน (Use Case) | ความสามารถ |
|--------|---------------|---------------------|-------------|
| **reactingFoam** | General reacting | Laminar/turbulent reacting flow ทั่วไป | Species + Energy + Chemistry |
| **chemFoam** | 0D reactor | Zero-dimensional batch reactor | Chemistry kinetics เท่านั้น |
| **XiFoam** | Premixed flame | Premixed turbulent flames | Flame wrinkling model (Xi) |
| **rhoReactingFoam** | Compressible | Low-Mach reacting flows | Compressible พร้อม chemistry |
| **reactingEulerFoam** | Multiphase | Euler-Euler multiphase reactions | Gas-solid/liquid reactions |

**การเลือกใช้:**
- เริ่มต้น/ทั่วไป → `reactingFoam`
- Premixed combustion → `XiFoam`
- Multiphase reactions → `reactingEulerFoam`
- ทดสอบ kinetics → `chemFoam`

---

## 6. ODE Solver Configuration

### 6.1 ทำไมต้องใช้ ODE Solver พิเศษ?

**Stiff Chemistry System:**
- **Fast timescale:** การสลายตัวของ radicals (เช่น OH, H) = 10⁻⁹ s
- **Slow timescale:** การเผาไหม้เชื้อเพลิง = 10⁻³ s
- **ความแตกต่าง 6 อันดับของขนาด** → Explicit solvers ล้มเหลว!

### 6.2 ตัวเลือก ODE Solver ใน OpenFOAM

```cpp
// constant/chemistryProperties/odeCoeffs
odeCoeffs
{
    // Stiff solver (recommended for combustion)
    solver  seulex;      // หรือ rodas
    
    // Tolerance settings
    absTol  1e-8;        // Absolute tolerance
    relTol  1e-4;        // Relative tolerance
    
    // Step size control
    maxSteps 1000;       // Maximum internal steps
}
```

**ตัวเลือก Solver:**

| Solver | ประเภท | ความเหมาะสม | ความเร็ว |
|--------|--------|-------------|---------|
| `seulex` | Stiff (extrapolation) | **Combustion, stiff chemistry** | เร็วมาก |
| `rodas` | Stiff (Rosenbrock) | **Combustion, stiff chemistry** | เร็ว |
| `ode` | Non-stiff | **Slow reactions only** | ช้ามาก (ไม่แนะนำ) |

---

## Quick Reference

| สัญลักษณ์ (Symbol) | ความหมาย (Meaning) | หน่วย (Unit) |
|------------------|---------------------|-------------|
| `Yᵢ` | Mass fraction of species i | (-) 0-1 |
| `ωᵢ` | Reaction rate of species i | kg/(m³·s) |
| `Qdot` | Heat release rate | W/m³ |
| `Ea` | Activation energy | J/mol |
| `A` | Pre-exponential factor | (varies) |
| `Dᵢ` | Diffusivity of species i | m²/s |
| `h` | Specific enthalpy | J/kg |

---

## 🧠 Concept Check

<details>
<summary><b>1. Mass fraction sum (ผลรวม mass fraction) เท่ากับเท่าไหร่?</b></summary>

**ΣYᵢ = 1** — ผลรวมของ mass fractions ของทุก species ต้องเท่ากับ 1 (mass conservation)

</details>

<details>
<summary><b>2. Arrhenius law คืออะไรและทำไมสำคัญ?</b></summary>

**Arrhenius law** (`k = A × Tⁿ × exp(-Ea/RT)`) เป็นกฎที่อธิบายว่าอัตราปฏิกิริยาขึ้นกับ **temperature** แบบ exponential สำคัญเพราะ:
- อุณหภูมิเพิ่มนิดหน่อย → rate เพิ่มมาก
- ทำให้เกิด **stiff system** (timescale ต่างกันมาก)
- ต้องใช้ ODE solver พิเศษ

</details>

<details>
<summary><b>3. ODE solver ใน OpenFOAM ใช้ทำไม?</b></summary>

ODE solver พิเศษ (เช่น `seulex`, `rodas`) ใช้เพื่อแก้ **stiff chemistry system** ที่มี timescale ต่างกันหลายอันดับขนาด:
- Fast reactions (radicals) = 10⁻⁹ s
- Slow reactions (fuel burnout) = 10⁻³ s
- Explicit solvers จะไม่เสถียร ต้องใช้ **stiff solvers**

</details>

<details>
<summary><b>4. Heat release (Qdot) เชื่อมโยงกับ flow อย่างไร?</b></summary>

**Two-way coupling:**
1. `Qdot` → temperature ↑ → density ↓ → velocity ↑ (continuity)
2. Velocity → convection → species transport → reaction rate เปลี่ยน
3. เป็น **loop** ที่ strongly coupled ใน reacting flows

</details>

---

## 📚 เอกสารที่เกี่ยวข้อง

**ภายใน MODULE 06:**
- **ภาพรวม:** [00_Overview.md](00_Overview.md) — ภาพรวม Reacting Flows
- **Combustion Models:** [04_Combustion_Models.md](04_Combustion_Models.md) — โมเดลการเผาไหม้ขั้นสูง (flamelet, EDC)
- **Advanced Topics:** [05_Advanced_Topics.md](05_Advanced_Topics.md) — Detailed kinetics & mechanisms

**ภายใน MODULE 04 (Multiphase):**
- **Interphase Forces:** [04_Turbulent_Dispersion](../../MODULE_04_MULTIPHASE_FUNDAMENTALS/CONTENT/04_INTERPHASE_FORCES/04_TURBULENT_DISPERSION/01_Fundamental_Theory.md) — เทคนิค turbulent dispersion ที่ใช้ใน reacting flows

---

## 🎯 Key Takeaways

1. **Species Transport:** สมการ `∂(ρYᵢ)/∂t + ∇·(ρUYᵢ) = ∇·(ρDᵢ∇Yᵢ) + ωᵢ` เป็นพื้นฐานของ reacting flow simulation
2. **Stiff Chemistry:** Arrhenius rate law ทำให้เกิด timescale ต่างกันหลายอันดับขนาด → ต้องใช้ stiff ODE solvers (seulex, rodas)
3. **Two-Way Coupling:** Heat release (`Qdot`) เปลี่ยน temperature → density → velocity field ซึ่งกลับมากระทบ chemistry อีก (loop)
4. **Solver Selection:** `reactingFoam` สำหรับกรณีทั่วไป, `XiFoam` สำหรับ premixed flames, `chemFoam` สำหรับทดสอบ kinetics
5. **Configuration:** `chemistryProperties` + `thermophysicalProperties` เป็นไฟล์หลักที่ต้องตั้งค่า

---

## 🔗 ไฟล์ตัวอย่างใน OpenFOAM

เอกสารฉบับนี้อ้างอิงโครงสร้างไฟล์จาก:

- **Solver:** `applications/solvers/combustion/reactingFoam/`
- **Tutorials:** `tutorials/combustion/reactingFoam/`
- **Chemistry Library:** `src/thermophysicalModels/specie/chemistryModel/`