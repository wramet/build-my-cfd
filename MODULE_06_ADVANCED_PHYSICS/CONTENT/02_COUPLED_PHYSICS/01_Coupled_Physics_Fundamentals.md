# Coupled Physics Fundamentals

พื้นฐาน Coupled Physics

---

## Overview

> Coupling = Multiple physics solved together

---

## 1. Coupling Types

| Type | Method |
|------|--------|
| Weak | Sequential |
| Strong | Iterate |
| Monolithic | Single matrix |

---

## 2. Interface

```cpp
// Heat flux continuity
q_fluid = q_solid
T_fluid = T_solid
```

---

## 3. Implementation

```cpp
forAll(fluidRegions, i) { solveFluid(); }
forAll(solidRegions, i) { solveSolid(); }
```

---

## Quick Reference

| Coupling | When |
|----------|------|
| Weak | Loose coupling |
| Strong | Tight coupling |

## 🧠 Concept Check

<details>
<summary><b>1. ความแตกต่างระหว่าง Weak กับ Strong Coupling?</b></summary>

| Aspect | Weak Coupling | Strong Coupling |
|--------|---------------|-----------------|
| **วิธี** | แก้แต่ละ physics ทีละครั้ง | วนซ้ำจนค่าลู่เข้า |
| **ความถูกต้อง** | ต่ำกว่า (lag ระหว่าง physics) | สูงกว่า |
| **ต้นทุน** | ถูกกว่า | แพงกว่า |

**เลือกใช้:** Weak สำหรับ loose coupling, Strong สำหรับ $\rho_f \approx \rho_s$

</details>

<details>
<summary><b>2. Interface Conditions ใน CHT คืออะไร?</b></summary>

ที่ interface ระหว่าง fluid และ solid ต้องมี **ความต่อเนื่อง:**

```cpp
// Temperature continuity (Dirichlet-Dirichlet)
T_fluid = T_solid

// Heat flux continuity (Neumann-Neumann)
q_fluid = q_solid  // k·∂T/∂n เท่ากัน
```

ใช้ `compressible::turbulentTemperatureCoupledBaffleMixed` BC

</details>

<details>
<summary><b>3. Monolithic vs Partitioned Approach ต่างกันอย่างไร?</b></summary>

| Approach | คำอธิบาย | ข้อดี |
|----------|----------|-------|
| **Monolithic** | แก้ทุก physics ใน matrix เดียว | Robust มาก |
| **Partitioned** | แยก solver แต่ละ domain | ยืดหยุ่น |

**OpenFOAM ใช้ Partitioned approach:**
```cpp
forAll(fluidRegions, i) { solveFluid(); }
forAll(solidRegions, i) { solveSolid(); }
```

</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md) — ภาพรวม Coupled Physics
- **บทถัดไป:** [02_Conjugate_Heat_Transfer.md](02_Conjugate_Heat_Transfer.md) — Conjugate Heat Transfer
- **FSI:** [03_Fluid_Structure_Interaction.md](03_Fluid_Structure_Interaction.md) — Fluid-Structure Interaction
- **Registry:** [04_Object_Registry_Architecture.md](04_Object_Registry_Architecture.md) — Object Registry