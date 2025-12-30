# Reacting Flows - Overview

ภาพรวม Reacting Flows (การไหลที่มีปฏิกิริยาเคมี)

---

## 📚 Learning Objectives (วัตถุประสงค์การเรียนรู้)

เมื่ออ่านจบบทนี้ คุณจะสามารถ:
1. **อธิบาย** แนวคิดพื้นฐานของ reacting flows และความสำคัญในการจำลอง CFD
2. **จำแนก** ประเภทของปฏิกิริยาเคมีและโมเดลที่ใช้ใน OpenFOAM
3. **เลือกใช้** solver ที่เหมาะสมกับปัญหา reacting flow ที่ต่างกัน
4. **ระบุ** ความแตกต่างระหว่าง finite-rate chemistry, EDC, PaSR, และ flamelet models
5. **ประเมิน** ข้อดีและข้อจำกัดของแต่ละแนวทางการจำลอง

---

## 🎯 Prerequisite Knowledge (ความรู้พื้นฐานที่ต้องมี)

ก่อนเริ่มบทนี้ คุณควรมีความเข้าใจใน:
- **Governing equations** สำหรับ single-phase flow (continuity, momentum, energy)
- **Turbulence modeling** (k-ε, k-ω, LES)
- **Basic thermodynamics** (enthalpy, temperature, equation of state)
- **OpenFOAM case structure** และ dictionary files

---

## 🏗️ 3W Framework: What? Why? How?

### 📦 What? (Reacting Flows คืออะไร?)

**Reacting flows** หมายถึง การไหลของไหลที่มี **chemical reactions** (ปฏิกิริยาเคมี) เกิดขึ้นภายในโดเมน ซึ่งมีการ:
- **Mass transfer** ระหว่าง chemical species
- **Heat release** จากปฏิกิริยา exothermic/endothermic
- **Species production/destruction** จาก kinetic rates

สมการพื้นฐาน:
```
∂(ρYᵢ)/∂t + ∇·(ρUYᵢ) = ∇·(ρDᵢ∇Yᵢ) + ωᵢ
```
เมื่อ:
- `Yᵢ` = mass fraction ของ species i
- `ωᵢ` = reaction rate (kg/m³s)
- `Dᵢ` = diffusion coefficient

---

### 🤔 Why? (ทำไมต้องเรียนรู้ Reacting Flows?)

**Applications ที่ใช้ reacting flows:**

| Domain | Examples |
|--------|----------|
| 🏭 **Industry** | Combustors, furnaces, chemical reactors |
| 🚗 **Automotive** | Engine combustion, aftertreatment systems |
| 🚀 **Aerospace** | Rocket engines, scramjets |
| 🔥 **Safety** | Fire propagation, explosion modeling |
| ⚡ **Energy** | Gas turbines, fuel cells |

**ความท้าทาย:**
- **Stiff chemistry** → timescales ต่างกันมาก (10⁻⁹ to 1 s)
- **Turbulence-chemistry interaction** → coupling ซับซ้อน
- **Heat release** → กระทบต่อ flow field และ temperature

---

### 🛠️ How? (ใช้ How ใน OpenFOAM?)

#### **Solver Selection**

| Solver | Application | Key Features |
|--------|-------------|--------------|
| `reactingFoam` | General reacting flows | Multi-species, finite-rate chemistry |
| `XiFoam` | Premixed combustion | Flame propagation, flame wrinkling |
| `sprayFoam` | Spray combustion | Lagrangian particles, evaporation |
| `fireFoam` | Fire simulation | Radiation, soot formation |
| `rhoCentralFoam` | High-speed reacting flows | Compressible, shock-capturing |

#### **Chemistry Modeling Approaches**

| Model | Computational Cost | Accuracy | Use Case |
|-------|-------------------|----------|----------|
| **Finite-Rate Chemistry** | ⭐⭐⭐⭐⭐ (Very High) | ⭐⭐⭐⭐⭐ | Detailed mechanisms, validation |
| **EDC** | ⭐⭐⭐⭐ (High) | ⭐⭐⭐⭐ | Turbulent flames |
| **PaSR** | ⭐⭐⭐ (Medium) | ⭐⭐⭐ | Industrial applications |
| **Flamelet** | ⭐⭐ (Low-Medium) | ⭐⭐⭐ | Non-premixed, fast simulations |

---

## 🔑 Key Concepts (แนวคิดสำคัญ)

### 1. **Species Transport**
แต่ละ chemical species มี transport equation ของตัวเอง:
```
Convection + Diffusion + Reaction = Accumulation
∇·(ρUYᵢ) + ∇·(ρDᵢ∇Yᵢ) + ωᵢ = ∂(ρYᵢ)/∂t
```

### 2. **Reaction Rate (ωᵢ)**
ขึ้นอยู่กับ:
- **Temperature** (Arrhenius dependence)
- **Species concentrations**
- **Pressure** (for gas-phase reactions)

### 3. **Heat Release**
Coupled กับ energy equation:
```
∂(ρh)/∂t + ∇·(ρUh) = ∇·(k∇T) + ΣωᵢΔHᵢ
```
เมื่อ `ΔHᵢ` = enthalpy of formation

### 4. **Turbulence-Chemistry Interaction**
- **Fast chemistry** → flamelet regime
- **Slow chemistry** → distributed reaction zone
- **Intermediate** → EDC, PaSR models

---

## 📂 Module Structure (โครงสร้างหลักสูตร)

| File | Topic | Key Content |
|------|-------|-------------|
| **00_Overview.md** | Introduction | Concepts, solver selection |
| **01_Fundamentals.md** | Species transport | Conservation equations, kinetics |
| **02_Chemistry_Models.md** | Chemistry approaches | Finite-rate, EDC, PaSR, flamelet |
| **03_Combustion_Models.md** | Combustion regimes | Premixed, non-premixed, partially premixed |
| **04_Combustion_Models.md** | Advanced topics | Soot, radiation, extinction |
| **05_Chemkin.md** | Chemistry files | Chemkin format, thermodynamics |
| **06_Workflow.md** | Practical setup | Case files, boundary conditions |

---

## 🎯 Quick Reference: Solver Selection Guide

```
Problem Type → Recommended Solver
─────────────────────────────────────────
General multi-species → reactingFoam
Premixed flame → XiFoam
Spray combustion → sprayFoam
Fire simulation → fireFoam
High-speed compressible → rhoCentralFoam
Laminar flame → reactingFoam (laminar RAS)
```

---

## 🧠 Concept Check (ทดสอบความเข้าใจ)

<details>
<summary><b>1. Species transport equation ประกอบด้วยกระบวนการใดบ้าง?</b></summary>

**Convection + Diffusion + Reaction** 
- Convection: `∇·(ρUYᵢ)` — transport by bulk flow
- Diffusion: `∇·(ρDᵢ∇Yᵢ)` — molecular mixing
- Reaction: `ωᵢ` — chemical source/sink term
</details>

<details>
<summary><b>2. EDC (Eddy Dissipation Concept) คืออะไร?</b></summary>

**Turbulence-chemistry interaction model** ที่สมมติว่า:
- Reaction occurs in fine structures (~Kolmogorov scale)
- Mass transfer ระหว่าง fine structures และ surrounding fluid
- Suitable for turbulent flames with moderate/fast chemistry
</details>

<details>
<summary><b>3. Chemkin format ใช้ทำอะไร?</b></summary>

**Define chemical mechanism** ใน OpenFOAM:
- Species list และ thermodynamic properties
- Elementary reactions และ Arrhenius parameters
- Used by `chemkinReader` หรือ `cantera` utilities
</details>

<details>
<summary><b>4. เมื่อไหร่ควรใช้ flamelet model?</b></summary>

**Use flamelet when:**
- Flow time scale >> chemistry time scale (fast chemistry)
- Non-premixed or partially premixed flames
- Need fast computations (design iterations)
- **Not suitable for:** detailed pollutant formation, extinction dynamics
</details>

---

## 📖 Related Documents (เอกสารที่เกี่ยวข้อง)

- **Fundamentals:** [01_Reacting_Flow_Fundamentals.md](01_Reacting_Flow_Fundamentals.md) — Species transport, chemical kinetics
- **Chemistry Models:** [02_Chemistry_Models.md](02_Chemistry_Models.md) — Finite-rate, EDC, PaSR, flamelet
- **Combustion:** [03_Combustion_Models.md](03_Combustion_Models.md) — Flame regimes, Damköhler number
- **Advanced:** [04_Combustion_Models.md](04_Combustion_Models.md) — Soot, radiation, validation
- **Practical:** [06_Workflow.md](06_Workflow.md) — Case setup, boundary conditions, solver settings

---

## 🔗 Prerequisites for Next Sections

ก่อนไปต่อ ควรอ่าน:
1. **Module 1: CFD Fundamentals** — Governing equations
2. **Module 3: Single-Phase Flow** — Turbulence modeling
3. **Module 5: OpenFOAM Programming** — Thermodynamics, chemistry classes