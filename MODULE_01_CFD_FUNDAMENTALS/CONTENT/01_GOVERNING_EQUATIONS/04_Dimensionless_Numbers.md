# เลขไร้มิติในพลศาสตร์ของไหล

> **Learning Objectives (3W Framework)**
> - **WHAT:** เลขไร้มิติคืออัตราส่วนของแรงหรือปรากฏการณ์ทางฟิสิกส์ที่บ่งบอกถึงความสำคัญสัมพัทธ์
> - **WHY:** ใช้จัดหมวดหมู่ระบอบการไหล เลือก solver เลือก turbulence model และ verify ผลลัพธ์ CFD
> - **WHEN:** ก่อนเริ่ม simulation ทุกครั้ง เพื่อวางแผนการตั้งค่าที่เหมาะสม

---

## Master Table: Dimensionless Numbers

| เลขไร้มิติ | สูตร | ความหมาย | Threshold Values | ใช้กับ | OpenFOAM Solvers |
|-----------|------|---------|-----------------|---------|------------------|
| **Reynolds** ($Re$) | $\frac{\rho U L}{\mu}$ | Inertial / Viscous | $<2300$ (lam)<br>$2300-4000$ (trans)<br>$>4000$ (turb) | ทุกปัญหา | ทุก solver |
| **Mach** ($Ma$) | $\frac{U}{c}$ | Flow / Sound speed | $<0.3$ (incomp)<br>$0.3-0.8$ (weak)<br>$>0.8$ (comp) | Compressible flow | `sonicFoam`, `rhoCentralFoam` |
| **Froude** ($Fr$) | $\frac{U}{\sqrt{gL}}$ | Inertial / Gravitational | $<1$ (subcrit)<br>$=1$ (crit)<br>$>1$ (supercrit) | Free surface | `interFoam`, `multiphaseInterFoam` |
| **Prandtl** ($Pr$) | $\frac{c_p \mu}{k}$ | Momentum / Thermal diffusivity | ~0.7 (gas)<br>~7 (water)<br>~0.01 (liquid metal) | Heat transfer | `buoyantSimpleFoam` |
| **Schmidt** ($Sc$) | $\frac{\mu}{\rho D}$ | Momentum / Mass diffusivity | ~0.7 (gas)<br>~1000 (liquid) | Mass transfer | `reactingFoam` |
| **Weber** ($We$) | $\frac{\rho U^2 L}{\sigma}$ | Inertial / Surface tension | $>12$ (droplet breakup) | Surface tension | `sprayFoam` |
| **Strouhal** ($St$) | $\frac{fL}{U}$ | Vortex shedding frequency | ~0.2 (cylinder) | Unsteady flows | `pimpleFoam` |

---

## Reynolds Number ($Re$) — The Most Important

**อัตราส่วนของแรงเฉื่อยต่อแรงหนืด:**

$$Re = \frac{\rho U L}{\mu} = \frac{\text{Inertial Forces}}{\text{Viscous Forces}}$$

โดยที่:
- $\rho$ = ความหนาแน่น [kg/m³]
- $U$ = ความเร็วลักษณะเฉพาะ [m/s]
- $L$ = ความยาวลักษณะเฉพาะ [m]
- $\mu$ = ความหนืดพลวัต [Pa·s]

> **💡 สัญชาตญาณ:**
> - **Re สูง** = คนวิ่งในสนามโล่ง → โมเมนตัมครอบงำ → Turbulent
> - **Re ต่ำ** = เดินฝ่าฝูงชนแน่น → ความหนืดครอบงำ → Laminar

### Flow Regime Classification

> **⚠️ IMPORTANT:** ค่า thresholds เหล่านี้ใช้สำหรับ **pipe flow** เท่านั้น Geometry อื่นมีค่าต่างกัน

| Reynolds Number | ระบอบการไหล | ลักษณะ | CFD Treatment |
|-----------------|-------------|--------|----------------|
| $Re < 2300$ | Laminar | เรียบ, เป็นชั้นๆ | `laminar` model |
| $2300 < Re < 4000$ | Transitional | ไม่เสถียร | Transition model หรือ LES |
| $Re > 4000$ | Turbulent | ปั่นป่วน, มีการผสมมาก | RANS/LES/DES |

**Critical Re สำหรับ geometries อื่นๆ:**
- **Flat plate:** $Re_x \approx 5 \times 10^5$ (transition ตามระยะทาง)
- **Flow past cylinder:** $Re \approx 200$ (vortex shedding เริ่ม)
- **Jet flow:** $Re \approx 10-30$ (เริ่ม unstable)

### How to Verify Your Re Calculation — Checklist

```
□ 1. ตรวจสอบหน่วยของตัวแปรทั้งหมด
     - ρ [kg/m³], U [m/s], L [m], μ [Pa·s]
     
□ 2. ยืนยัน L (characteristic length)
     - ท่อ: เส้นผ่านศูนย์กลาง D
     - แผ่น: ระยะทางจากจุด leading edge x
     - ตัวกีดขวาง: ขนาดความกว้าง
     
□ 3. ตรวจสอบ U (characteristic velocity)
     - Inlet velocity หรือ average velocity
     
□ 4. คำนวณ Re และตรวจสอบ order of magnitude
     - Re ~ 10-100: ขนาดเล็กมาก (microfluidics)
     - Re ~ 10³-10⁴: ขนาดปานกลาง (ท่อ, ducts)
     - Re ~ 10⁶-10⁸: ขนาดใหญ่ (รถยนต์, อากาศยาน)
     
□ 5. เปรียบเทียบกับค่า critical ของ geometry
     - อยู่ใกล้ threshold หรือไม่?
     - อาจต้องลองทั้ง laminar และ turbulent
```

---

## Mach Number ($Ma$) — Compressibility Indicator

$$Ma = \frac{U}{c}$$

โดยที่ $c = \sqrt{\gamma R T}$ สำหรับ Ideal Gas

### Flow Regime & Solver Selection

| Mach Number | ระบอบ | Compressibility | Solver แนะนำ |
|-------------|-------|-----------------|--------------|
| $Ma < 0.3$ | Incompressible | ละเลยได้ ($\rho \approx \text{const}$) | `simpleFoam`, `pimpleFoam` |
| $0.3 < Ma < 0.8$ | Subsonic compressible | เล็กน้อย | `rhoSimpleFoam`, `rhoPimpleFoam` |
| $0.8 < Ma < 1.2$ | Transonic | Shock waves เริ่มก่อตัว | `rhoPimpleFoam`, `sonicFoam` |
| $Ma > 1.2$ | Supersonic | Shock waves ชัดเจน | `sonicFoam`, `rhoCentralFoam` |

---

## Froude Number ($Fr$) — Free Surface Flows

$$Fr = \frac{U}{\sqrt{gL}}$$

| Froude Number | ระบอบ | ลักษณะ | ปรากฏการณ์ |
|---------------|-------|--------|-----------|
| $Fr < 1$ | Subcritical | ช้า, ลึก | คลื่นทวนน้ำได้ |
| $Fr = 1$ | Critical | — | Hydraulic jump |
| $Fr > 1$ | Supercritical | เร็ว, ตื้น | คลื่นทวนน้ำไม่ได้ |

**Solver:** `interFoam`, `multiphaseInterFoam`, `waveFoam`

---

## Prandtl & Schmidt Numbers — Transport Phenomena

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

---

## Wall Y-plus ($y^+$) — Turbulence Modeling Near Walls

$$y^+ = \frac{y u_\tau}{\nu}$$

โดยที่:
- $y$ = ระยะห่างจากผนัง [m]
- $u_\tau = \sqrt{\tau_w/\rho}$ = friction velocity [m/s]
- $\nu = \mu/\rho$ = kinematic viscosity [m²/s]
- $\tau_w$ = wall shear stress [Pa]

### Boundary Layer Velocity Profile

```
┌─────────────────────────────────────────────────────────────────────┐
│                     TURBULENT BOUNDARY LAYER                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Free Stream (U∞)                                                  │
│  │                                                                  │
│  ├─ y+ > 300 ─────────────────────────────────────────────┐         │
│  │    Outer Layer (Wake Region)                           │         │
│  │    u+ ≈ constant                                        │         │
│  │                                                          │         │
│  ├─ 30 < y+ < 300 ─────────────────────────────────────┐   │         │
│  │    Log-Law Region                                    │   │         │
│  │    u+ = (1/κ) ln(y+) + B                              │   │         │
│  │    where κ ≈ 0.41, B ≈ 5.0                           │   │         │
│  │    ✓ WALL FUNCTIONS WORK HERE                       │   │         │
│  │    ✓ Standard wall functions: 30 < y+ < 300         │   │         │
│  │    ✓ Low-Re wall functions: y+ ~ 1-5                │   │         │
│  │                                                          │         │
│  ├─ 5 < y+ < 30 ─────────────────────────────────────┐   │   │         │
│  │    Buffer Layer (Transition Zone)                 │   │   │         │
│  │    ✗ AVOID! Neither model works well              │   │   │         │
│  │    ✗ Hybrid approaches needed                     │   │   │         │
│  │                                                          │         │
│  ├─ y+ < 5 ──────────────────────────────────────────┐   │   │   │         │
│  │    Viscous Sublayer                               │   │   │   │         │
│  │    u+ = y+ (linear profile)                        │   │   │   │         │
│  │    ✓ MUST RESOLVE WITH FINE MESH                  │   │   │   │         │
│  │    ✓ Low-Re turbulence models                     │   │   │   │         │
│  │                                                             │   │   │   │         │
│  └─ WALL (u = 0)                                            │   │   │   │         │
└─────────────────────────────────────────────────────────────┴───┴───┴─────────┘
```

### Y-plus Strategy in OpenFOAM

| $y^+$ Range | บริเวณ | การจัดการ | Mesh Size ($\Delta y$) | Turbulence Model |
|-------------|--------|-------------|----------------------|------------------|
| $y^+ < 5$ | Viscous sublayer | Resolve โดยตรง | $\Delta y \approx 10^{-5}$ m | `kOmegaSST` (low-Re) |
| $5 < y^+ < 30$ | Buffer layer | ❌ หลีกเลี่ยง | — | ❌ ไม่ใช้ |
| $30 < y^+ < 300$ | Log-law region | Wall functions | $\Delta y \approx 10^{-3}$ m | `kEpsilon` + wall functions |

### Check Y-plus in OpenFOAM

```bash
# หลังจากรัน simulation
postProcess -func yPlus

# หรือ (สำหรับ RAS models)
yPlusRAS

# หรือใช้ function object ใน controlDict
functions
{
    yPlus
    {
        type        yPlus;
        functionObjectLibs ("libfieldFunctionObjects.so");
        writeControl writeTime;
    }
}
```

ผลลัพธ์อยู่ที่: `postProcessing/yPlus/<time>/`

---

## Dimensionless Number Calculator (Python)

```python
#!/usr/bin/env python3
"""
Dimensionless Number Calculator for OpenFOAM
Usage: python dimensionless_calculator.py
"""

import math

def calculate_reynolds(rho, U, L, mu):
    """Calculate Reynolds number"""
    return (rho * U * L) / mu

def calculate_mach(U, T, gamma=1.4, R=287.1):
    """Calculate Mach number (ideal gas)"""
    c = math.sqrt(gamma * R * T)
    return U / c

def calculate_froude(U, L, g=9.81):
    """Calculate Froude number"""
    return U / math.sqrt(g * L)

def calculate_prandtl(cp, mu, k):
    """Calculate Prandtl number"""
    return (cp * mu) / k

def estimate_yplus(U, L, rho, mu, delta_y):
    """Estimate y+ for given mesh size (simplified)"""
    nu = mu / rho
    Cf = 0.074 / (calculate_reynolds(rho, U, L, mu)**0.2)  # Flat plate
    tau_w = 0.5 * rho * U**2 * Cf
    u_tau = math.sqrt(tau_w / rho)
    return (delta_y * u_tau) / nu

def main():
    print("=" * 50)
    print("Dimensionless Number Calculator")
    print("=" * 50)
    
    # Input
    print("\nInput flow properties:")
    rho = float(input("Density ρ [kg/m³]: "))
    U = float(input("Velocity U [m/s]: "))
    L = float(input("Characteristic length L [m]: "))
    mu = float(input("Dynamic viscosity μ [Pa·s]: "))
    
    # Calculate
    Re = calculate_reynolds(rho, U, L, mu)
    
    print(f"\n{'='*50}")
    print("RESULTS:")
    print(f"{'='*50}")
    print(f"Reynolds Number: {Re:.2e}")
    
    # Flow regime
    if Re < 2300:
        regime = "LAMINAR"
        model = "laminar"
    elif Re < 4000:
        regime = "TRANSITIONAL"
        model = "transition model or LES"
    else:
        regime = "TURBULENT"
        model = "kEpsilon, kOmegaSST, LES"
    
    print(f"Flow Regime: {regime}")
    print(f"Suggested Model: {model}")
    
    # Optional: Mach
    try:
        T = float(input("\nTemperature T [K] (for Mach): "))
        Ma = calculate_mach(U, T)
        print(f"Mach Number: {Ma:.3f}")
        
        if Ma < 0.3:
            print("→ Incompressible (use simpleFoam)")
        elif Ma < 0.8:
            print("→ Weakly compressible (use rhoSimpleFoam)")
        else:
            print("→ Compressible (use sonicFoam/rhoCentralFoam)")
    except:
        pass
    
    # Optional: Froude
    try:
        use_froude = input("\nCalculate Froude? (y/n): ")
        if use_frouse.lower() == 'y':
            Fr = calculate_froude(U, L)
            print(f"Froude Number: {Fr:.3f}")
    except:
        pass
    
    # Optional: y+ estimation
    try:
        use_yplus = input("\nEstimate y+ for mesh? (y/n): ")
        if use_yplus.lower() == 'y':
            delta_y = float(input("First cell height Δy [m]: "))
            y_plus = estimate_yplus(U, L, rho, mu, delta_y)
            print(f"Estimated y+: {y_plus:.2f}")
            
            if y_plus < 5:
                print("→ Viscous sublayer (resolve with low-Re model)")
            elif 5 <= y_plus <= 30:
                print("→ Buffer layer (AVOID!)")
            elif 30 < y_plus < 300:
                print("→ Log-law region (wall functions OK)")
            else:
                print("→ Outer layer (y+ too high for wall functions)")
    except:
        pass

if __name__ == "__main__":
    main()
```

---

## Common Pitfalls

### ❌ Pitfall 1: Wrong Characteristic Length
**Problem:** ใช้ความยาวผิดสำหรับ geometry
- **ท่อ:** ใช้ความยาวท่อทั้งหมด → ❌ ผิด!
- **ท่อ:** ควรใช้เส้นผ่านศูนย์กลาง → ✓ ถูก

**Solution:** ดูตารางด้านล่าง

| Geometry | Characteristic Length |
|----------|---------------------|
| ท่อ (Pipe) | เส้นผ่านศูนย์กลาง (D) |
| แผ่น (Flat plate) | ระยะจาก leading edge (x) |
หรือความยาวแผ่น (L) |
| ตัวกีดขวาง (Bluff body) | ความกว้างตั้งฉากกับการไหล (W) |

### ❌ Pitfall 2: Ignoring Reynolds Number Near Thresholds
**Problem:** Re = 2500 อยู่ใน transitional zone แต่บังคับใช้ laminar

**Solution:** ทั้ง laminar และ turbulent เพื่อเปรียบเทียบ

### ❌ Pitfall 3: Y-plus in Buffer Layer
**Problem:** y+ = 15 อยู่ใน buffer layer ซึ่งไม่เหมาะกับทั้ง wall function และ low-Re model

**Solution:** 
- เลือก: y+ < 5 (resolve) หรือ y+ > 30 (wall function)
- หลีกเลี่ยง: 5 < y+ < 30

### ❌ Pitfall 4: Using Wrong Viscosity
**Problem:** สับสนระหว่าง dynamic viscosity ($\mu$) และ kinematic viscosity ($\nu$)

**Solution:** 
- $Re = \frac{\rho U L}{\mu}$ (ใช้ dynamic viscosity)
- $Re = \frac{U L}{\nu}$ (ใช้ kinematic viscosity)
- ตรวจสอบหน่วย: $\mu$ [Pa·s], $\nu$ [m²/s]

---

## Turbulence Intensity ($I$)

$$I = \frac{u'}{U_{avg}} \times 100\%$$

| ระดับ | I | ตัวอย่าง |
|-------|---|----------|
| ต่ำ | < 1% | Wind tunnel |
| ปานกลาง | 1-5% | การไหลในท่อ |
| สูง | > 5% | หลัง obstacle, Combustion |

**สูตรโดยประมาณ (ท่อ):** $I \approx 0.16 \cdot Re^{-1/8}$

**ใช้ในการตั้งค่า inlet turbulence:**
```
turbulenceIntensity 0.05;  // 5%
```

---

## (Optional Advanced) Weber & Strouhal Numbers

### Weber Number ($We$)

$$We = \frac{\rho U^2 L}{\sigma} = \frac{\text{Inertial Forces}}{\text{Surface Tension Forces}}$$

**ใช้เมื่อ:** Surface tension สำคัญ (droplets, sprays, bubbles)

**Threshold:** $We > 12$ → droplet breakup

**Solver:** `sprayFoam`, `multiphaseInterFoam`

### Strouhal Number ($St$)

$$St = \frac{fL}{U}$$

**ใช้เมื่อ:** Vortex shedding, unsteady flows

**Typical value:** $St \approx 0.2$ สำหรับ flow ผ่าน cylinder

**Solver:** `pimpleFoam`, `PisoFoam`

---

## Key Takeaways

1. **Re บอกทุกอย่าง:** Laminar vs Turbulent → กำหนด solver, model, mesh
2. **Ma บอก compressibility:** $Ma > 0.3$ → ต้องใช้ compressible solver
3. **Y-plus สำคัญมาก:** 30 < y+ < 300 สำหรับ wall functions, y+ < 5 สำหรับ low-Re
4. **ตรวจสอบ characteristic length:** อย่าใช้ความยาวผิดสำหรับ geometry
5. **หลีกเลี่ยง buffer layer:** 5 < y+ < 30 เป็นช่วงอันตราย

---

## Concept Check

<details>
<summary><b>1. Re = 5000 สำหรับท่อ ควรใช้ turbulence model หรือไม่?</b></summary>

ใช่ ควรใช้ turbulence model เพราะ Re > 4000 อยู่ในระบอบ turbulent
แนะนำ: `kEpsilon` หรือ `kOmegaSST`
</details>

<details>
<summary><b>2. เมื่อไหร่ต้องใช้ compressible solver?</b></summary>

เมื่อ $Ma > 0.3$ เพราะผลกระทบของ compressibility เริ่มมีนัยสำคัญ
ความหนาแน่นจะเปลี่ยนแปลงตามความดันและอุณหภูมิ
</details>

<details>
<summary><b>3. y+ = 50 ใช้ได้กับ wall function หรือไม่?</b></summary>

ได้ เพราะ 30 < y+ < 300 อยู่ใน log-law region
เหมาะสำหรับ standard wall functions
</details>

<details>
<summary><b>4. Characteristic length ของท่อคืออะไร?</b></summary>

เส้นผ่านศูนย์กลาง (D) ไม่ใช่ความยาวท่อ
</details>

---

## Navigation

```
┌─────────────────────────────────────────────────────────────────┐
│                   MODULE FLOW DIAGRAM                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [01: Conservation Laws] ──► [02: Finite Volume Method]         │
│         │                           │                           │
│         ▼                           ▼                           │
│  [03: Equation of State] ──► [04: Dimensionless Numbers] ◄────┘ │
│                                        │                        │
│                                        ▼                        │
│                           [05: OpenFOAM Implementation]         │
│                                        │                        │
│                                        ▼                        │
│                           [06: Boundary Conditions]              │
│                                        │                        │
│                                        ▼                        │
│                           [07: Turbulence Modeling]              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Related Documents

### ← Previous
- **[03_Equation_of_State.md](03_Equation_of_State.md)** — สมการสถานะ (ความหนาแน่น $\rho$ จำเป็นต่อการคำนวณ Re)

### → Next
- **[05_OpenFOAM_Implementation.md](05_OpenFOAM_Implementation.md)** — การนำหลักการไปใช้ใน OpenFOAM (การตั้งค่าตาม Re, Ma)

### See Also
- **[06_Boundary_Conditions.md](06_Boundary_Conditions.md)** — การตั้งค่า BCs และ wall functions ตาม y+ (คำนวณจาก Re)
- **[07_Turbulence_Modeling.md](07_Turbulence_Modeling.md)** — การเลือก turbulence model ตาม Re และ y+

---

## Glossary of Symbols

| Symbol | ชื่อ | หน่วย SI |
|--------|------|----------|
| $\rho$ | ความหนาแน่น | kg/m³ |
| $U$ | ความเร็วลักษณะเฉพาะ | m/s |
| $L$ | ความยาวลักษณะเฉพาะ | m |
| $\mu$ | ความหนืดพลวัต | Pa·s |
| $\nu$ | ความหนืดจลนศาสตร์ | m²/s |
| $c$ | ความเร็วเสียง | m/s |
| $g$ | ความเร่งเนื่องจากแรงโน้มถ่วง | m/s² |
| $y$ | ระยะห่างจากผนัง | m |
| $y^+$ | Y-plus (มิติไร้) | — |
| $u_\tau$ | Friction velocity | m/s |
| $\tau_w$ | Wall shear stress | Pa |