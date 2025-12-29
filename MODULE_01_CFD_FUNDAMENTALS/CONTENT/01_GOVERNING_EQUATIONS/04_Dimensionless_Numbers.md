# เลขไร้มิติในพลศาสตร์ของไหล

เลขไร้มิติ (Dimensionless Numbers) เป็นอัตราส่วนที่บ่งบอกถึง **ความสำคัญสัมพัทธ์ของปรากฏการณ์ทางฟิสิกส์**

> **ทำไมต้องรู้ Dimensionless Numbers?**
> - **Re บอกว่า laminar หรือ turbulent** → เลือก solver และ turbulence model
> - **Ma บอกว่า compressible หรือไม่** → เลือก solver ตระกูลไหน
> - **ใช้ verify ผลลัพธ์** → เปรียบเทียบกับ correlation และ experiment

---

## Reynolds Number ($Re$)

**เลขที่สำคัญที่สุดใน CFD** — อัตราส่วนของแรงเฉื่อยต่อแรงหนืด:

$$Re = \frac{\rho U L}{\mu} = \frac{\text{Inertial Forces}}{\text{Viscous Forces}}$$

โดยที่:
- $\rho$ = ความหนาแน่น [kg/m³]
- $U$ = ความเร็วลักษณะเฉพาะ [m/s]
- $L$ = ความยาวลักษณะเฉพาะ [m]
- $\mu$ = ความหนืดพลวัต [Pa·s]

> **💡 สัญชาตญาณ:**
> - **Re สูง** = เหมือนคนวิ่งในสนามโล่ง → โมเมนตัมครอบงำ → Turbulent
> - **Re ต่ำ** = เหมือนเดินฝ่าฝูงชนแน่น → ความหนืดครอบงำ → Laminar

### Flow Regime Classification

> **⚠️ ข้อจำกัด:** ค่า thresholds เหล่านี้ใช้สำหรับ **pipe flow** (การไหลในท่อ) เท่านั้น รูปทรงอื่นจะมีค่าต่างกัน

| Reynolds Number | ระบอบการไหล | ลักษณะ |
|-----------------|-------------|--------|
| $Re < 2300$ | Laminar | เรียบ, เป็นชั้นๆ |
| $2300 < Re < 4000$ | Transitional | ไม่เสถียร, กำลังเปลี่ยน |
| $Re > 4000$ | Turbulent | ปั่นป่วน, มีการผสมมาก |

**ค่า critical Re สำหรับ geometries อื่นๆ:**
- **Flat plate:** $Re_x \approx 5 \times 10^5$ (transition ตามระยะทาง)
- **Flow past cylinder:** $Re \approx 200$ (vortex shedding เริ่ม)
- **Jet flow:** $Re \approx 10-30$ (เริ่ม unstable)

> **💡 แนะนำ:** ถ้าไม่แน่ใจ — เริ่มจาก laminar, แล้ว check ผลลัพธ์ว่ามี unsteadiness หรือไม่

### ผลกระทบใน CFD

| ด้าน | Re ต่ำ | Re สูง |
|------|--------|--------|
| Turbulence Model | `laminar` | `kEpsilon`, `kOmegaSST`, `LES` |
| Mesh Resolution | หยาบได้ | ต้องละเอียดใกล้ผนัง |
| Wall Treatment | ไม่จำเป็น | ต้องใช้ wall function หรือ resolve |

---

## Mach Number ($Ma$)

อัตราส่วนของความเร็วการไหลต่อความเร็วเสียง:

$$Ma = \frac{U}{c}$$

โดยที่ $c = \sqrt{\gamma R T}$ สำหรับ Ideal Gas

### Flow Regime Classification

| Mach Number | ระบอบ | ผลกระทบ Compressibility |
|-------------|-------|------------------------|
| $Ma < 0.3$ | Incompressible | ละเลยได้ ($\rho \approx \text{const}$) |
| $0.3 < Ma < 0.8$ | Subsonic | เล็กน้อย |
| $0.8 < Ma < 1.2$ | Transonic | Shock waves เริ่มก่อตัว |
| $Ma > 1.2$ | Supersonic | Shock waves ชัดเจน |

### การเลือก Solver

| Mach | Solver ตัวอย่าง |
|------|-----------------|
| $Ma < 0.3$ | `simpleFoam`, `pimpleFoam` |
| $Ma > 0.3$ | `rhoSimpleFoam`, `rhoPimpleFoam` |
| $Ma > 0.8$ | `sonicFoam`, `rhoCentralFoam` |

---

## Froude Number ($Fr$)

อัตราส่วนของแรงเฉื่อยต่อแรงโน้มถ่วง — สำคัญสำหรับ **free surface flows**:

$$Fr = \frac{U}{\sqrt{gL}}$$

### Flow Classification

| Froude Number | ระบอบ | ลักษณะ |
|---------------|-------|--------|
| $Fr < 1$ | Subcritical | ช้า, ลึก, คลื่นทวนน้ำได้ |
| $Fr = 1$ | Critical | Hydraulic jump |
| $Fr > 1$ | Supercritical | เร็ว, ตื้น, คลื่นทวนน้ำไม่ได้ |

**Solver ที่เกี่ยวข้อง:** `interFoam`, `multiphaseInterFoam`

---

## เลขไร้มิติอื่นๆ

### Prandtl Number ($Pr$)

$$Pr = \frac{c_p \mu}{k} = \frac{\text{Momentum Diffusivity}}{\text{Thermal Diffusivity}}$$

| ของไหล | Pr | ความหมาย |
|--------|-----|---------|
| ก๊าซ | ~0.7 | Thermal BL หนากว่า Velocity BL |
| น้ำ | ~7 | Velocity BL หนากว่า Thermal BL |
| โลหะเหลว | ~0.01 | Thermal diffusion เร็วมาก |

**ใช้ใน:** การถ่ายเทความร้อน (`buoyantSimpleFoam`)

### Schmidt Number ($Sc$)

$$Sc = \frac{\mu}{\rho D} = \frac{\text{Momentum Diffusivity}}{\text{Mass Diffusivity}}$$

**ใช้ใน:** Mass transfer, Species transport (`reactingFoam`)

### Weber Number ($We$)

$$We = \frac{\rho U^2 L}{\sigma} = \frac{\text{Inertial Forces}}{\text{Surface Tension Forces}}$$

**ใช้ใน:** Droplet breakup, Spray dynamics ($We > 12$ → breakup)

### Strouhal Number ($St$)

$$St = \frac{fL}{U}$$

**ใช้ใน:** Vortex shedding frequency ($St \approx 0.2$ สำหรับ cylinder)

---

## Wall Y-plus ($y^+$)

พารามิเตอร์สำคัญสำหรับ turbulence modeling ใกล้ผนัง:

$$y^+ = \frac{y u_\tau}{\nu}$$

โดยที่:
- $y$ = ระยะห่างจากผนัง [m]
- $u_\tau = \sqrt{\tau_w/\rho}$ = friction velocity [m/s]
- $\nu = \mu/\rho$ = kinematic viscosity [m²/s]
- $\tau_w$ = wall shear stress [Pa]

### Boundary Layer Structure

```
┌─────────────────────────────────────────────────────────┐
│  TURBULENT BOUNDARY LAYER                                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Free Stream                                             │
│  │                                                       │
│  ├─ y+ > 300 ──────────────────────────────────┐         │
│  │    Outer Layer (wake region)                │         │
│  │                                              │         │
│  ├─ 30 < y+ < 300 ────────────────────────────┐ │         │
│  │    Log-law Region (u+ = (1/κ) ln(y+) + B) │ │         │
│  │    ✓ Wall Functions work well here        │ │         │
│  │                                              │         │
│  ├─ 5 < y+ < 30 ─────────────────────────────┐ │ │         │
│  │    Buffer Layer                            │ │ │         │
│  │    ✗ Avoid! Neither model works well     │ │ │         │
│  │                                              │ │ │         │
│  ├─ y+ < 5 ──────────────────────────────────┐ │ │ │         │
│  │    Viscous Sublayer (u+ = y+)            │ │ │ │         │
│  │    ✓ Must resolve with fine mesh         │ │ │ │         │
│  │                                             │ │ │ │         │
│  └─ WALL                                      │ │ │ │         │
└──────────────────────────────────────────────┴─┴─┴─┴─────────┘
```

| $y^+$ Range | บริเวณ | การจัดการใน CFD | ขนาด cell ใกล้ผนัง |
|-------------|--------|-----------------|-------------------|
| $y^+ < 5$ | Viscous sublayer | Resolve โดยตรง (low-Re model) | $\Delta y \approx 1 \times 10^{-5}$ m |
| $5 < y^+ < 30$ | Buffer layer | หลีกเลี่ยง | ไม่ใช้ทั้งสองแบบ |
| $30 < y^+ < 300$ | Log-law region | ใช้ Wall function | $\Delta y \approx 1 \times 10^{-3}$ m |

**หมายเหตุ:** ค่า $\Delta y$ ข้างต้นเป็นเพียงตัวอย่างสำหรับ Re ประมาณ $10^5$ ค่าจริงขึ้นกับ flow conditions

### ตรวจสอบ y+ ใน OpenFOAM

```bash
# หลังจากรัน simulation
postProcess -func yPlus

# หรือ (สำหรับ RAS models)
yPlusRAS
```

ผลลัพธ์จะถูกเขียนไปที่ `postProcessing/` directory — สามารถเปิดดูใน ParaView ได้

---

## Turbulence Intensity ($I$)

$$I = \frac{u'}{U_{avg}}$$

| ระดับ | I | ตัวอย่าง |
|-------|---|----------|
| ต่ำ | < 1% | Wind tunnel, High-quality inlet |
| ปานกลาง | 1-5% | การไหลในท่อ |
| สูง | > 5% | หลัง obstacle, Combustion |

**สูตรประมาณ (ท่อ):** $I \approx 0.16 \cdot Re^{-1/8}$

---

## ตารางสรุป

| เลขไร้มิติ | สูตร | ใช้ทำอะไร | Solver ตัวอย่าง |
|-----------|------|----------|-----------------|
| Reynolds ($Re$) | $\rho UL/\mu$ | Laminar vs Turbulent | ทุก solver |
| Mach ($Ma$) | $U/c$ | Incomp vs Comp | `sonicFoam` |
| Froude ($Fr$) | $U/\sqrt{gL}$ | Free surface | `interFoam` |
| Prandtl ($Pr$) | $c_p\mu/k$ | Heat transfer | `buoyantFoam` |
| Weber ($We$) | $\rho U^2 L/\sigma$ | Droplet/Spray | `sprayFoam` |

---

## Concept Check

<details>
<summary><b>1. Re = 5000 ควรใช้ turbulence model หรือไม่?</b></summary>

ใช่ ควรใช้ เพราะ Re > 4000 อยู่ในระบอบ turbulent ควรใช้ RANS model เช่น `kEpsilon` หรือ `kOmegaSST`
</details>

<details>
<summary><b>2. เมื่อไหร่ต้องใช้ compressible solver?</b></summary>

เมื่อ $Ma > 0.3$ เพราะผลกระทบของ compressibility มีนัยสำคัญ (ความหนาแน่นเปลี่ยนแปลงตาม $p$ และ $T$)
</details>

<details>
<summary><b>3. y+ = 50 ใช้ได้กับ wall function หรือไม่?</b></summary>

ได้ เพราะอยู่ในช่วง log-law region (30 < y+ < 300) ซึ่งเหมาะสำหรับ standard wall functions
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [03_Equation_of_State.md](03_Equation_of_State.md) — สมการสถานะ
- **บทถัดไป:** [05_OpenFOAM_Implementation.md](05_OpenFOAM_Implementation.md) — การนำไปใช้ใน OpenFOAM
- **การนำไปใช้:** [06_Boundary_Conditions.md](06_Boundary_Conditions.md) — การตั้งค่า BCs ตาม Re, y+