# การจำแนก Boundary Conditions

## Learning Objectives

หลังจากอ่านบทนี้ คุณควรจะสามารถ:
- 🎯 **แยกแยะประเภททางคณิตศาสตร์**ของ Boundary Conditions ทั้ง 3 แบบ (Dirichlet, Neumann, Robin) และเข้าใจความหมายทางฟิสิกส์
- 🎯 **เขียนค่า BC ใน OpenFOAM** สำหรับแต่ละประเภทได้อย่างถูกต้อง
- 🎯 **เลือก Wall Functions** ที่เหมาะสมกับ y+ และ mesh resolution
- 🎯 **อธิบายความแตกต่าง**ระหว่าง BC types ที่ดูคล้ายกัน (เช่น `zeroGradient` vs `fixedGradient 0`)
- 🎯 **ประยุกต์ใช้ Mixed BC** สำหรับปัญหา convection heat transfer

---

## What: ประเภททางคณิตศาสตร์ของ Boundary Conditions

### ทำไม Boundary Conditions สำคัญ?

> - สมการ PDE **ไม่มีคำตอบ unique** ถ้าไม่มี BC
> - BC ที่ผิดพลาด = คำตอบที่ไม่มีความหมายทางกายภาพ
> - หลาย simulation ล้มเหลวเพราะ BC ไม่ใช่เพราะ solver

### Mental Model: น้ำในถัง

> **💡 คิดแบบนี้:**
> ลองนึกภาพน้ำในถัง — จะบอกพฤติกรรมที่ขอบได้ 3 แบบ:
> 1. **Dirichlet:** "ระดับน้ำที่ขอบ = 10 cm" (กำหนดค่า)
> 2. **Neumann:** "น้ำไหลเข้า = 1 L/s" (กำหนด flux)
> 3. **Robin:** "น้ำไหลออกขึ้นกับระดับน้ำ" (ผสมทั้งสอง)

<!-- IMAGE: IMG_01_005 -->
<!-- 
Purpose: เพื่อสร้างภาพจำ (Mental Model) ให้กับผู้เรียนเรื่อง Boundary Conditions 3 ประเภทหลักในทางคณิตศาสตร์ โดยใช้ "ความร้อน" (Heat Transfer) เป็นตัวอย่างเพราะเข้าใจง่ายที่สุด. ภาพนี้ต้องแยกแยะ 1) การกำหนดค่า (Dirichlet) 2) การกำหนดความชัน/Flux (Neumann) และ 3) การกำหนดความสัมพันธ์ (Robin)
Prompt: "Technical engineering triptych (3-panel diagram) illustrating Thermal Boundary Conditions. **Panel 1 (Left - Dirichlet):** A wall at fixed $T_{wall} = 300K$. The temperature profile curve explicitly connects to this fixed point. Label: 'Fixed Value'. **Panel 2 (Center - Neumann):** A wall with HEAT FLUX arrows ($q''$) entering. The temperature profile slope is fixed ($\partial T / \partial n = const$), but the wall temperature itself is floating. Label: 'Fixed Gradient'. **Panel 3 (Right - Robin):** A convection scenario ($h(T - T_{\infty})$). The profile slope depends on the temperature difference. Label: 'Mixed / Convective'. STYLE: Professional engineering textbook illustration, clean isometric or 2D cross-section, thermal gradient colors (blue to red), sharp black coordinate axes."
-->
![[IMG_01_005.JPg]]

### สรุปประเภททางคณิตศาสตร์

| ประเภท | สมการ | OpenFOAM | Physical Meaning |
|--------|-------|----------|------------------|
| **Dirichlet** | $\phi = \phi_0$ | `fixedValue` | กำหนดค่าโดยตรง |
| **Neumann** | $\frac{\partial\phi}{\partial n} = g$ | `fixedGradient`, `zeroGradient` | กำหนด flux/gradient |
| **Robin** | $a\phi + b\frac{\partial\phi}{\partial n} = c$ | `mixed` | ผสมทั้งสอง |

---

## Why: ทำไมต้องแยกประเภท?

การแยกประเภท BC ตามหลักคณิตศาสตร์ช่วยให้:
- ✅ **เลือก BC ที่เหมาะสม**กับสภาพปัญหาทางฟิสิกส์
- ✅ **หลีกเลี่ยงข้อผิดพลาด** เช่น กำหนด fixedValue ทุก boundary ทำให้ไม่ satisfy continuity
- ✅ **ทำความเข้าใจ solver behavior** เมื่อ BC ไม่เข้ากัน
- ✅ **ดีบักปัญหา divergence** ที่มักเกิดจาก BC ที่ขัดแย้งกัน

---

## How: การนำไปใช้ใน OpenFOAM

### 1. Dirichlet (Fixed Value)

$$\phi|_{\text{boundary}} = \phi_0$$

**"ฉันบอกค่าที่ขอบ — solver หาค่าข้างใน"**

```cpp
inlet
{
    type    fixedValue;
    value   uniform (10 0 0);   // Velocity = 10 m/s ในทิศ x
}

hotWall
{
    type    fixedValue;
    value   uniform 373.15;     // Temperature = 100°C
}
```

**ใช้เมื่อ:**
- ✅ รู้ค่าที่ขอบแน่นอน (inlet velocity, wall temperature)
- ✅ ต้องการ reference point (pressure outlet)

**ข้อควรระวัง:**
- ❌ ถ้าใช้ fixedValue ทุก boundary → อาจไม่ satisfy continuity
- ❌ Pressure ต้องมี reference point อย่างน้อย 1 จุด

---

### 2. Neumann (Fixed Gradient)

$$\frac{\partial\phi}{\partial n}\bigg|_{\text{boundary}} = g$$

**"ฉันบอก flux/gradient — ค่าที่ขอบคำนวณจากข้างใน"**

#### Zero Gradient ($g = 0$)

```cpp
outlet
{
    type    zeroGradient;   // ∂φ/∂n = 0
}
```

**ใช้เมื่อ:**
- ✅ Fully developed flow (outlet) — profile ไม่เปลี่ยนแปลง
- ✅ Adiabatic wall — ไม่มี heat flux
- ✅ Symmetry plane — gradient = 0 โดยธรรมชาติ

**ทำไม outlet ใช้ zeroGradient?**
- ถ้า flow พัฒนาเต็มที่ → profile ไม่เปลี่ยน → $\partial/\partial n = 0$
- ถ้าใกล้ outlet เกินไป → profile ยังไม่นิ่ง → **ต้องขยาย domain**

#### Fixed Gradient ($g \neq 0$)

```cpp
heatedWall
{
    type        fixedGradient;
    gradient    uniform 1000;   // q = 1000 W/m² (heat flux)
}
```

**ใช้เมื่อ:** รู้ flux แต่ไม่รู้ค่าที่ผิว (เช่น heater ให้ heat flux คงที่)

> **⚠️ หมายเหตุ:** ใน OpenFOAM `fixedGradient` กำหนด **gradient** ของ field โดยตรง ไม่ใช่ heat flux
> - สำหรับ Temperature: `gradient` = $\partial T/\partial n$ [K/m]
> - Actual heat flux: $q'' = -k \cdot \nabla T$ [W/m²] (โดย $k$ = thermal conductivity)

---

### 3. Robin (Mixed)

$$a\phi + b\frac{\partial\phi}{\partial n} = c$$

**"ค่าที่ขอบขึ้นกับทั้งตัวมันเองและ gradient"**

```cpp
convectiveWall
{
    type            mixed;
    refValue        uniform 300;      // T∞ = 300 K
    refGradient     uniform 0;        // default
    valueFraction   uniform 0.5;      // 50% Dirichlet, 50% Neumann
}
```

**ประยุกต์ที่สำคัญ: Convective Heat Transfer**

$$-k\frac{\partial T}{\partial n} = h(T_s - T_\infty)$$

- ถ้า $h$ สูงมาก → $T_s \approx T_\infty$ → เหมือน Dirichlet
- ถ้า $h$ ต่ำมาก → flux $\approx 0$ → เหมือน Neumann

**valueFraction คืออะไร?**
- 0 = ใช้ refGradient ทั้งหมด (Neumann)
- 1 = ใช้ refValue ทั้งหมด (Dirichlet)
- 0.5 = ผสมครึ่งๆ

---

### 4. Wall Functions (Turbulence)

**ปัญหา:** Boundary layer บางมาก → ต้อง mesh ละเอียดมากใกล้ผนัง

**ทางออก:** ใช้ **Wall Functions** = สูตรเชื่อมหรือ "กระโดดข้าม" viscous sublayer

```cpp
// system/0/ ไฟล์ต่างๆ
// k
wall { type kqRWallFunction; value uniform 0.1; }

// epsilon
wall { type epsilonWallFunction; value uniform 0.01; }

// omega
wall { type omegaWallFunction; value uniform 1000; }

// nut (turbulent viscosity)
wall
{
    type    nutkWallFunction;
    value   uniform 0;
    Cmu     0.09;
    kappa   0.41;   // von Karman constant
    E       9.8;    // log-law constant
}
```

**y+ requirements:**

| Approach | y+ Range | ข้อดี | ข้อเสีย |
|----------|----------|------|---------|
| **Wall functions** | 30 < y+ < 300 | Mesh หยาบได้ | ไม่แม่นยำใกล้ผนัง |
| **Low-Re models** | y+ < 5 | แม่นยำ | Mesh ละเอียดมาก |

---

### 5. Coupled/Special

#### Cyclic (Periodic)

```cpp
left  { type cyclic; }
right { type cyclic; }
```

**ใช้เมื่อ:** Flow เป็น pattern ซ้ำๆ → จำลองแค่ส่วนเดียว

**ต้องตั้งค่าใน `constant/polyMesh/boundary`:**
```cpp
left
{
    type            cyclic;
    neighbourPatch  right;
}
```

#### Symmetry

```cpp
symmetryPlane { type symmetry; }
```

**ใช้เมื่อ:** ปัญหา symmetric → ลดขนาดโดเมน → ลดเวลา compute

**Physics:**
- Velocity ตั้งฉากผนัง = 0
- Gradient ขนานผนัง = 0

#### Processor (Parallel)

```cpp
// สร้างอัตโนมัติเมื่อ decomposePar
procBoundary0to1 { type processor; }
```

**อย่าแก้ไข!** สร้างและจัดการโดย OpenFOAM เอง

---

## Visual Summary: BC Classification Decision Tree

```
┌─────────────────────────────────────────────────────────────┐
│           Boundary Condition Classification                 │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │   What do you know at BC?     │
              └───────────────┬───────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   Known Value         Known Flux            Both Related
   (Dirichlet)         (Neumann)              (Robin)
        │                     │                     │
        ▼                     ▼                     ▼
  ┌───────────┐       ┌─────────────┐     ┌──────────────┐
  │fixedValue │       │zeroGradient │     │    mixed     │
  │           │       │fixedGradient│     │              │
  │Examples:  │       │Examples:    │     │Examples:     │
  │- Inlet U  │       │- Outlet     │     │- Convection  │
  │- Wall T   │       │- Adiabatic  │     │- Radiation   │
  └───────────┘       └─────────────┘     └──────────────┘
                              │
                              │ For Turbulence
                              ▼
                    ┌─────────────────────┐
                    │   Wall Functions    │
                    │ (y+ dependent)      │
                    ├─────────────────────┤
                    │ 30 < y+ < 300:      │
                    │ Use wall functions  │
                    │                     │
                    │ y+ < 5:             │
                    │ Resolve viscous     │
                    │ sublayer            │
                    └─────────────────────┘
```

---

## Key Takeaways

### สรุปเปรียบเทียบทุกประเภท

| BC Type | คณิตศาสตร์ | ใช้ที่ | Keywords | ตัวอย่าง |
|---------|-----------|--------|----------|-----------|
| `fixedValue` | Dirichlet | Inlet U, Wall T | `value` | Velocity inlet, isothermal wall |
| `zeroGradient` | Neumann (g=0) | Outlet, Wall p | — | Fully developed outlet, adiabatic wall |
| `fixedGradient` | Neumann | Heat flux | `gradient` | Constant heat flux wall |
| `mixed` | Robin | Convection | `refValue`, `valueFraction` | Convective cooling |
| `noSlip` | Dirichlet (U=0) | Wall U | — | No-slip wall |
| `slip` | U⋅n=0, τ=0 | Inviscid wall | — | Frictionless wall |
| `symmetry` | Mirror | Symmetry plane | — | Symmetry boundary |
| `cyclic` | Periodic | Repeating | neighbourPatch | Periodic flow |
| `inletOutlet` | Switching | Backflow safe | `inletValue` | Outlet with potential backflow |
| `kqRWallFunction` | Wall Func | Turbulence k | — | Turbulent wall treatment |
| `epsilonWallFunction` | Wall Func | Turbulence ε | — | Turbulent dissipation |
| `omegaWallFunction` | Wall Func | Turbulence ω | — | SST k-ω model |

### หลักการสำคัญ

1. **Dirichlet vs Neumann:**
   - Dirichlet: กำหนดค่า → solver หา gradient
   - Neumann: กำหนด gradient → solver หาค่า

2. **Continuity requirement:**
   - Pressure ต้องมี reference point อย่างน้อย 1 จุด
   - ใช้ fixedValue ทุก boundary → อาจไม่ converge

3. **Wall Functions:**
   - 30 < y+ < 300: ใช้ wall functions
   - y+ < 5: ต้อง mesh ละเอียดมาก
   - 5 < y+ < 30: **หลีกเลี่ยง!** buffer zone

4. **Robin/Mixed BC:**
   - valueFraction = 1 → Dirichlet
   - valueFraction = 0 → Neumann
   - 0 < valueFraction < 1 → ผสมทั้งสอง

---

## Concept Check

<details>
<summary><b>1. zeroGradient กับ fixedGradient 0 ต่างกันไหม?</b></summary>

**ผลลัพธ์เหมือนกัน** แต่:
- `zeroGradient` เขียนสั้นกว่า ไม่ต้องระบุ value
- `zeroGradient` optimize ดีกว่าใน code (skip calculation)

**แนะนำ:** ใช้ `zeroGradient` เสมอเมื่อ gradient = 0
</details>

<details>
<summary><b>2. Wall function ใช้เมื่อไหร่? ทำไมต้องสนใจ y+?</b></summary>

**ใช้เมื่อ:** ต้องการ save compute cost โดยไม่ resolve viscous sublayer

**y+ คืออะไร:** ระยะห่างจากผนังในหน่วย wall units

$$y^+ = \frac{y \cdot u_\tau}{\nu}$$

โดยที่ $u_\tau = \sqrt{\frac{\tau_w}{\rho}}$ คือ friction velocity (ความเร็วเฉือนจากแรงเสียดทานผนัง)

**ทำไมสำคัญ:**
- y+ < 5: Viscous sublayer → ต้องใช้ Low-Re model
- 5 < y+ < 30: Buffer layer → **avoid!** ไม่ตรงกับสมมติฐานใด
- 30 < y+ < 300: Log-law region → ใช้ wall functions ได้
</details>

<details>
<summary><b>3. valueFraction ใน mixed หมายความว่าอะไร?</b></summary>

**Weight ระหว่าง Dirichlet (1) กับ Neumann (0):**

$$\phi_f = vf \cdot \text{refValue} + (1-vf) \cdot (\phi_P + \text{refGradient} \cdot \Delta)$$

- `valueFraction = 1` → ใช้ `refValue` เท่านั้น (Dirichlet)
- `valueFraction = 0` → ใช้ `refGradient` เท่านั้น (Neumann)
- `valueFraction = 0.5` → ผสมครึ่งๆ

**ประยุกต์:** Convection BC ที่ valueFraction คำนวณจาก h (heat transfer coefficient)
</details>

<details>
<summary><b>4. inletOutlet ใช้เมื่อไหร่?</b></summary>

**ใช้ที่ outlet เมื่อมีโอกาส backflow:**

```cpp
outlet
{
    type            inletOutlet;
    inletValue      uniform (0 0 0);  // ค่าถ้าไหลเข้า
    value           uniform (0 0 0);  // initial guess
}
```

**พฤติกรรม:**
- ถ้าไหลออก → `zeroGradient`
- ถ้าไหลเข้า (backflow) → `fixedValue = inletValue`

**ทำไมสำคัญ:** ป้องกัน diverge เมื่อ backflow เกิดขึ้นโดยไม่คาดคิด
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [01_Introduction.md](01_Introduction.md) — บทนำและแนวคิดเบื้องต้นเรื่อง Boundary Conditions
- **บทถัดไป:** [03_Selection_Guide_Which_BC_to_Use.md](03_Selection_Guide_Which_BC_to_Use.md) — คู่มือการเลือก BC ที่เหมาะสมกับแต่ละสถานการณ์
- **ดูเพิ่ม:** [05_Common_Boundary_Conditions_in_OpenFOAM.md](05_Common_Boundary_Conditions_in_OpenFOAM.md) — BC ที่ใช้บ่อยใน OpenFOAM พร้อมตัวอย่างโค้ด
- **ดูเพิ่ม:** [04_Advanced_Boundary_Conditions.md](04_Advanced_Boundary_Conditions.md) — BC ขั้นสูงและกรณีพิเศษ