# Coupled Physics - Overview

ภาพรวม Coupled Physics

---

## 🎯 Learning Objectives

หลังจากอ่านบทนี้ คุณจะสามารถ:
- Define coupled physics and identify different coupling types (What)
- Choose appropriate coupling strategies for different physical problems (Why)
- Navigate the module structure to find specific implementation details (How)
- Configure basic multi-region simulations in OpenFOAM (How)

---

## Overview

> **Coupled physics** = Multiple physics domains interacting with each other through boundary interfaces

ใน OpenFOAM, coupled physics simulations ถูกจำลองผ่าน **multi-region framework** ซึ่งอนุญาตให้ mesh และ physics แตกต่างกัน interact ผ่าน shared boundaries

---

## 1. What is Coupled Physics?

### Definition (What)
**Coupled Physics** คือการจำลองที่มี **หลายสาขาฟิสิกส์** หรือ **หลาย region** แยกกัน แต่มีการ **interact** กันที่ interfaces

### Why Coupled Physics? (Motivation)
Many real-world problems involve multiple physics:
- **Heat transfer** between fluid and solid (CHT)
- **Fluid-structure interaction** causing deformation (FSI)
- **Electromagnetic** effects on conducting fluids (MHD)
- **Chemical reactions** coupled with transport

### How It Works (Implementation)
```cpp
// constant/regionProperties - Define regions
regions 
(
    fluid (fluid)
    solid (heater)
);
```

---

## 2. Types of Coupling

| Coupling Type | Physics Domains | Example Applications | Solver |
|---------------|-----------------|---------------------|--------|
| **CHT** | Fluid + Solid heat | Heat exchangers, electronics cooling | chtMultiRegionFoam |
| **FSI** | Fluid + Structure | Blood vessels, wing flutter | fluidFoam + solid solvers |
| **MHD** | Fluid + Electromagnetics | Liquid metal pumps, metallurgy | mhdFoam |
| **Acoustic-Fluid** | Acoustics + Flow | Noise prediction, musical instruments | waveFoam |

---

## 3. Coupling Strategies

| Strategy | Description | When to Use | Pros | Cons |
|----------|-------------|-------------|------|------|
| **Weak Coupling** | Solve each region sequentially per timestep | Loose coupling, slow interactions | Lower computational cost | May diverge for tight coupling |
| **Strong Coupling** | Iterate within timestep until convergence | Tight coupling, fast interactions | More stable, accurate | Higher computational cost |

<details>
<summary><b>🔧 Implementation Details</b></summary>

**Weak Coupling Example:**
```cpp
// Pseudo-code
for (timestep; time < endTime; ++timestep)
{
    solve(fluidRegion);
    solve(solidRegion);
    // No iteration between regions
}
```

**Strong Coupling Example:**
```cpp
for (timestep; time < endTime; ++timestep)
{
    do
    {
        solve(fluidRegion);
        solve(solidRegion);
    } while (!converged());
}
```
</details>

---

## 4. Multi-Region Setup in OpenFOAM

### 4.1 Region Configuration

```cpp
// constant/regionProperties
regions 
(
    fluid
    (
        fluid
    )
    solid
    (
        heater
        walls
    )
);
```

### 4.2 Directory Structure

```
caseDirectory/
├── 0/                  # Initial conditions
│   ├── fluid/
│   │   └── T, U, p
│   └── solid/
│       └── T
├── constant/
│   ├── fluid/
│   │   └── polyMesh/
│   └── solid/
│       └── polyMesh/
└── system/
    ├── fluid/
    │   └── fvSchemes, fvSolution
    └── solid/
        └── fvSchemes, fvSolution
```

### 4.3 Interface Boundary Conditions

```cpp
// fluid region boundary
interface_to_solid
{
    type            compressible::turbulentTemperatureCoupledBaffleMixed;
    Tnbr            T;
    kappaMethodName fluidThermo;
    kappa           none;
    value           uniform 300;
}

// solid region boundary
interface_to_fluid
{
    type            compressible::turbulentTemperatureCoupledBaffleMixed;
    Tnbr            T;
    kappaMethodName solidThermo;
    kappa           none;
    value           uniform 300;
}
```

---

## 5. Solver Reference

| Solver | Physics | Regions | Key Features |
|--------|---------|---------|--------------|
| **chtMultiRegionFoam** | Conjugate Heat Transfer | Multiple | Fluid-solid heat exchange |
| **chtMultiRegionSimpleFoam** | Steady-state CHT | Multiple | Incompressible, steady |
| **chtMultiRegionFoam::verticalFlux** | Vertical CHT | Multiple | Specialized for buoyancy |
| **fluidFoam** | Fluid-structure | Multiple | FSI framework |

<details>
<summary><b>📝 chtMultiRegionFoam Details</b></summary>

**Purpose:** Transient/conjugate heat transfer between multiple regions

**Physics:**
- Compressible/turbulent flow in fluid regions
- Heat conduction in solid regions
- Coupled boundary conditions at interfaces

**Typical Applications:**
- Electronics cooling
- Heat exchangers
- Building thermal analysis
- Automotive thermal management

**Key Requirements:**
- Separate mesh for each region
- Conformal interfaces (matched face points)
- Compatible thermophysical models
</details>

---

## 6. Module Navigation

### Module Structure

| File | Content | Focus |
|------|---------|-------|
| **00_Overview** (this file) | Module map & catalog | What topics are covered |
| **01_Fundamentals** | Coupled physics theory | Mathematical framework |
| **02_CHT** | Conjugate heat transfer | Implementation & examples |
| **03_FSI** | Fluid-structure interaction | Structural coupling |
| **04_Registry** | Multi-region code | Programming framework |
| **05_Advanced** | Advanced topics | Optimization, stability |
| **06_Validation** | Verification & validation | Grid convergence, benchmarks |
| **07_Exercises** | Hands-on practice | Tutorial cases |

### Learning Path

```
START HERE (00_Overview)
    ↓
Choose path based on your needs:
    
    ├── → CHT focus: 01 → 02 → 07
    ├── → FSI focus: 01 → 03 → 05 → 07
    ├── → Programming: 01 → 04 → 05 → 07
    └ → Complete: 01 → 02 → 03 → 04 → 05 → 06 → 07
```

---

## 7. Quick Reference Guide

### Decision Tree: Which Coupling Type?

```
Need heat transfer between fluid/solid?
├── YES → CHT (chtMultiRegionFoam)
└── NO
    ├── Need structural deformation?
    │   ├── YES → FSI (fluidFoam + structural solver)
    │   └── NO
    │       ├── Electromagnetic fields present?
    │       │   ├── YES → MHD (mhdFoam)
    │       │   └── NO → Consider uncoupled simulation
```

### Common Boundary Conditions

| BC Type | Usage | Syntax |
|---------|-------|--------|
| `compressible::turbulentTemperatureCoupledBaffleMixed` | CHT interface | See Section 4.3 |
| `externalWallHeatFlux` | External convection | `h uniform 10;` |
| `fixedValue` | Dirichlet | `value uniform 300;` |
| `zeroGradient` | Neumann | - |

---

## 📊 Key Takeaways

1. **Coupled physics** requires multiple regions with shared interfaces
2. **CHT** is the most common coupling type (chtMultiRegionFoam)
3. **Weak vs Strong coupling** choice depends on interaction tightness and stability needs
4. **Multi-region structure** requires separate directories for each region (0/, constant/, system/)
5. **Interface BCs** are critical - use `coupled` boundary conditions for data transfer
6. **Solver selection** follows from physics type and coupling strategy

---

## 🧠 Concept Check

<details>
<summary><b>1. Multi-region simulation คืออะไร?</b></summary>

**Multi-region** คือการจำลองที่มี **หลาย mesh แยกกัน** แต่ coupled กันที่ interfaces

**ตัวอย่าง:**
- **CHT:** Fluid region + Solid region → แลกเปลี่ยนความร้อนที่ผนัง
- **FSI:** Fluid region + Structural solver → แลกเปลี่ยนแรงและการเสียรูป

```cpp
regions (fluid (fluid) solid (heater));
```

</details>

<details>
<summary><b>2. CHT (Conjugate Heat Transfer) ใช้เมื่อไหร่?</b></summary>

ใช้เมื่อต้องการจำลอง **การถ่ายเทความร้อนระหว่างของไหลและของแข็ง:**

**ตัวอย่าง:**
- Heat sink ระบายความร้อนจาก CPU
- เครื่องแลกเปลี่ยนความร้อน (Heat exchanger)
- การระบายความร้อนของ Electronic components

**Solver:** `chtMultiRegionFoam`

</details>

<details>
<summary><b>3. ความแตกต่างระหว่าง Weak และ Strong Coupling?</b></summary>

| Aspect | Weak Coupling | Strong Coupling |
|--------|---------------|-----------------|
| **วิธี** | แก้แต่ละ region ทีละครั้ง | วนซ้ำจนลู่เข้า |
| **ความเสถียร** | ดีสำหรับ loose coupling | ดีสำหรับ tight coupling |
| **ต้นทุน** | ต่ำกว่า | สูงกว่า |
| **ตัวอย่าง** | CHT ง่ายๆ | FSI ในน้ำ |

</details>

<details>
<summary><b>4. เมื่อไหร่ควรใช้ chtMultiRegionFoam?</b></summary>

ใช้ `chtMultiRegionFoam` เมื่อ:
1. มี **หลาย region** (fluid + solid)
2. มี **การแลกเปลี่ยนความร้อน** ระหว่าง regions
3. ต้องการ **transient** หรือ **steady-state** heat transfer
4. Fluid อาจเป็น **compressible** หรือ **incompressible**

**ไม่ใช้** เมื่อ:
- มีเพียง single region (ใช้ simpleFoam, buoyantFoam แทน)
- ไม่มี coupling (run separately)
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

### บทถัดไป (Recommended Reading Order)
- **พื้นฐาน:** [01_Coupled_Physics_Fundamentals.md](01_Coupled_Physics_Fundamentals.md) — Mathematical framework
- **CHT:** [02_Conjugate_Heat_Transfer.md](02_Conjugate_Heat_Transfer.md) — Heat transfer implementation
- **FSI:** [03_Fluid_Structure_Interaction.md](03_Fluid_Structure_Interaction.md) — Structure interaction
- **Programming:** [04_Registry_and_Multi-Region_Code.md](04_Registry_and_Multi-Region_Code.md) — OpenFOAM framework
- **ขั้นสูง:** [05_Advanced_Coupling_Topics.md](05_Advanced_Coupling_Topics.md) — Advanced techniques
- **Validation:** [06_Validation_and_Verification.md](06_Validation_and_Verification.md) — Best practices
- **ฝึกปฏิบัติ:** [07_Hands-On_Exercises.md](07_Hands-On_Exercises.md) — Tutorial cases

### Related Modules
- **MODULE_03:** Single-phase flow solvers
- **MODULE_04:** Multiphase fundamentals
- **MODULE_05:** OpenFOAM programming