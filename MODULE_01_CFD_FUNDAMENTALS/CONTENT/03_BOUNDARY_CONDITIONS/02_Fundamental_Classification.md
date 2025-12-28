# การจำแนก Boundary Conditions

ประเภทหลักของ Boundary Conditions ตามหลักคณิตศาสตร์และการใช้งานใน OpenFOAM

---

## ประเภททางคณิตศาสตร์

| ประเภท | สมการ | OpenFOAM | ใช้เมื่อ |
|--------|-------|----------|---------|
| **Dirichlet** | $\phi = \phi_0$ | `fixedValue` | กำหนดค่าโดยตรง |
| **Neumann** | $\frac{\partial\phi}{\partial n} = g$ | `fixedGradient`, `zeroGradient` | กำหนด flux/gradient |
| **Robin** | $a\phi + b\frac{\partial\phi}{\partial n} = c$ | `mixed` | ผสมทั้งสอง |

---

## 1. Dirichlet (Fixed Value)

$$\phi|_{\text{boundary}} = \phi_0$$

**กำหนดค่าตรงที่ขอบ**

```cpp
inlet
{
    type    fixedValue;
    value   uniform (10 0 0);   // Velocity m/s
}

hotWall
{
    type    fixedValue;
    value   uniform 373.15;     // Temperature K
}
```

**ใช้สำหรับ:**
- Velocity inlet
- Fixed temperature wall
- Pressure outlet (reference)

---

## 2. Neumann (Fixed Gradient)

$$\frac{\partial\phi}{\partial n}\bigg|_{\text{boundary}} = g$$

**กำหนด gradient/flux ที่ขอบ**

### Zero Gradient ($g = 0$)

```cpp
outlet
{
    type    zeroGradient;   // ∂φ/∂n = 0
}
```

**ใช้สำหรับ:**
- Fully developed outlet
- Adiabatic wall (no heat flux)
- Symmetry plane

### Fixed Gradient ($g \neq 0$)

```cpp
heatedWall
{
    type        fixedGradient;
    gradient    uniform 1000;   // Heat flux (W/m²)
}
```

**ใช้สำหรับ:**
- Specified heat flux
- Mass flux boundary

---

## 3. Robin (Mixed)

$$a\phi + b\frac{\partial\phi}{\partial n} = c$$

**ผสม Dirichlet + Neumann**

```cpp
convectiveWall
{
    type            mixed;
    refValue        uniform 300;      // Reference value
    refGradient     uniform 0;        // Reference gradient
    valueFraction   uniform 0.5;      // Weight (0=Neumann, 1=Dirichlet)
}
```

**ใช้สำหรับ:**
- Convective heat transfer: $-k\frac{\partial T}{\partial n} = h(T_s - T_\infty)$
- Partial slip conditions

---

## 4. Calculated/Derived

ค่าคำนวณจาก field อื่นหรือ physical model

### Wall Functions (Turbulence)

```cpp
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
    kappa   0.41;
    E       9.8;
}
```

**y+ requirements:**
- Standard wall functions: 30 < y+ < 300
- Low-Re models: y+ < 5

---

## 5. Coupled/Special

### Cyclic (Periodic)

```cpp
left  { type cyclic; }
right { type cyclic; }
```

**ใช้สำหรับ:** Periodic domains, heat exchangers

### Symmetry

```cpp
symmetryPlane { type symmetry; }
```

**ใช้สำหรับ:** ลดขนาดโดเมนครึ่งหนึ่ง

### Processor (Parallel)

```cpp
// สร้างอัตโนมัติเมื่อ decomposePar
procBoundary0to1 { type processor; }
```

---

## สรุป OpenFOAM Types

| BC Type | คณิตศาสตร์ | ใช้ที่ | Keywords |
|---------|-----------|--------|----------|
| `fixedValue` | Dirichlet | Inlet U, Wall T | `value` |
| `zeroGradient` | Neumann (g=0) | Outlet, Wall p | — |
| `fixedGradient` | Neumann | Heat flux | `gradient` |
| `mixed` | Robin | Convection | `refValue`, `valueFraction` |
| `noSlip` | Dirichlet (U=0) | Wall U | — |
| `slip` | U⋅n=0, τ=0 | Inviscid wall | — |
| `symmetry` | Mirror | Symmetry plane | — |
| `cyclic` | Periodic | Repeating | — |
| `inletOutlet` | Switching | Backflow safe | `inletValue` |

---

## Concept Check

<details>
<summary><b>1. zeroGradient กับ fixedGradient 0 ต่างกันไหม?</b></summary>

ผลลัพธ์เหมือนกัน แต่ `zeroGradient` เขียนสั้นกว่าและ optimize ดีกว่า
</details>

<details>
<summary><b>2. Wall function ใช้เมื่อไหร่?</b></summary>

เมื่อ y+ ของ cell แรกอยู่ในช่วง 30-300 (log-law region) เพื่อหลีกเลี่ยง mesh ละเอียดมากใกล้ผนัง
</details>

<details>
<summary><b>3. valueFraction ใน mixed หมายความว่าอะไร?</b></summary>

Weight ระหว่าง Dirichlet (1) กับ Neumann (0):
- `valueFraction = 1` → ใช้ `refValue` เท่านั้น
- `valueFraction = 0` → ใช้ `refGradient` เท่านั้น
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [01_Introduction.md](01_Introduction.md) — บทนำ
- **บทถัดไป:** [03_Selection_Guide_Which_BC_to_Use.md](03_Selection_Guide_Which_BC_to_Use.md) — คู่มือการเลือก BC