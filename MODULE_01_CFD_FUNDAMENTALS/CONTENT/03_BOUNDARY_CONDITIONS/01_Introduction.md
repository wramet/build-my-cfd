# บทนำ Boundary Conditions

Boundary Conditions บอก solver ว่าตัวแปรควรมีพฤติกรรมอย่างไรที่ขอบของโดเมน

> **ทำไม BC สำคัญ?**
> - PDE ต้องมี BC จึงจะมี **unique solution**
> - BC ผิด → simulation **diverge** หรือผลลัพธ์ผิดพลาด
> - ต้องรู้ **กฎ U-p coupling** — fixedValue ต้องคู่กับ zeroGradient

---

## หลักการพื้นฐาน

### PDE ต้องการ BC

สมการ Navier-Stokes:
$$\frac{\partial \mathbf{u}}{\partial t} + (\mathbf{u} \cdot \nabla)\mathbf{u} = -\frac{1}{\rho}\nabla p + \nu\nabla^2\mathbf{u}$$

ต้องมี BC ที่ทุกขอบเพื่อให้ได้ **unique solution**

### ประเภทขอบทั่วไป

| ขอบ | หน้าที่ | ตัวอย่าง |
|-----|--------|----------|
| **Inlet** | ของไหลเข้า | Pipe inlet, fan |
| **Outlet** | ของไหลออก | Pipe exit, atmosphere |
| **Wall** | ขอบแข็ง | ผนัง, วัตถุ |
| **Symmetry** | ระนาบสมมาตร | ลดขนาดโดเมน |
| **Cyclic** | ขอบที่เชื่อมกัน | Periodic flow |

---

## สามประเภทหลักของ BC

### 1. Dirichlet (Fixed Value)

$$\phi|_{\text{boundary}} = \phi_0$$

**กำหนดค่าโดยตรง**

```cpp
inlet
{
    type    fixedValue;
    value   uniform (10 0 0);  // m/s
}
```

**ใช้เมื่อ:** รู้ค่าที่ขอบ (velocity inlet, temperature wall)

### 2. Neumann (Fixed Gradient)

$$\frac{\partial \phi}{\partial n}\bigg|_{\text{boundary}} = g$$

**กำหนด gradient/flux**

```cpp
outlet
{
    type    zeroGradient;  // g = 0
}

heatFluxWall
{
    type    fixedGradient;
    gradient uniform 1000;  // W/m²
}
```

**ใช้เมื่อ:** Fully developed flow, adiabatic wall, specified heat flux

### 3. Robin (Mixed)

$$\alpha\phi + \beta\frac{\partial\phi}{\partial n} = \gamma$$

**ผสมทั้งสอง**

```cpp
convectiveWall
{
    type    mixed;
    refValue    uniform 300;        // Reference temperature
    refGradient uniform 0;          // Reference gradient
    valueFraction uniform 0.5;      // 0=Neumann, 1=Dirichlet
}
```

**ใช้เมื่อ:** Convective heat transfer, partial slip

---

## การตั้งค่าทั่วไป

### Inlet

| Field | Type | Value |
|-------|------|-------|
| U | `fixedValue` | `(Ux Uy Uz)` |
| p | `zeroGradient` | — |
| T | `fixedValue` | `T_inlet` |
| k | `fixedValue` | $\frac{3}{2}(U \cdot I)^2$ |
| ε | `fixedValue` | $C_\mu^{3/4} \frac{k^{3/2}}{l}$ |

### Outlet

| Field | Type | Value |
|-------|------|-------|
| U | `zeroGradient` หรือ `pressureInletOutletVelocity` | — |
| p | `fixedValue` | `0` (gauge) |
| T | `zeroGradient` | — |
| k | `zeroGradient` | — |
| ε | `zeroGradient` | — |

### Wall

| Field | Type | Value |
|-------|------|-------|
| U | `noSlip` | `(0 0 0)` |
| p | `zeroGradient` | — |
| T | `fixedValue` หรือ `zeroGradient` | ขึ้นกับ thermal BC |
| k | `kqRWallFunction` | — |
| ε | `epsilonWallFunction` | — |
| nut | `nutkWallFunction` | — |

---

## OpenFOAM File Structure

```cpp
// 0/U
FoamFile
{
    version     2.0;
    format      ascii;
    class       volVectorField;
    object      U;
}

dimensions      [0 1 -1 0 0 0 0];

internalField   uniform (0 0 0);

boundaryField
{
    inlet
    {
        type    fixedValue;
        value   uniform (10 0 0);
    }
    
    outlet
    {
        type    zeroGradient;
    }
    
    wall
    {
        type    noSlip;
    }
}
```

---

## Concept Check

<details>
<summary><b>1. ทำไม pressure ใช้ zeroGradient ที่ inlet?</b></summary>

เพราะเมื่อ velocity ถูกกำหนดที่ inlet แล้ว pressure จะถูกคำนวณจาก momentum equation → ปล่อยให้ pressure ปรับตัวตามธรรมชาติ
</details>

<details>
<summary><b>2. noSlip กับ fixedValue (0 0 0) ต่างกันไหม?</b></summary>

ผลลัพธ์เหมือนกัน (`noSlip` = shorthand) แต่ `noSlip` ชัดเจนกว่าและ OpenFOAM จะจัดการเรื่อง mesh motion ให้ถูกต้อง
</details>

<details>
<summary><b>3. valueFraction ใน mixed BC คืออะไร?</b></summary>

Weight ระหว่าง Dirichlet (1) กับ Neumann (0):
- `valueFraction = 1` → ใช้ `refValue` เท่านั้น
- `valueFraction = 0` → ใช้ `refGradient` เท่านั้น
- `valueFraction = 0.5` → ผสม 50-50
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [00_Overview.md](00_Overview.md) — ภาพรวม
- **บทถัดไป:** [02_Fundamental_Classification.md](02_Fundamental_Classification.md) — การจำแนกประเภท