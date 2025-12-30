# บทนำ Boundary Conditions

## Learning Objectives

หลังจากอ่านบทนี้ คุณจะสามารถ:
- เข้าใจ **แนวคิดพื้นฐาน** ของ Boundary Conditions (BC) ใน OpenFOAM
- อธิบาย **ทำไม** BC จำเป็นต้องมีสำหรับการแก้ PDE
- จำแนก **ประเภทของ BC** สามประเภทหลัก: Dirichlet, Neumann, และ Robin
- ใช้ **กฎ U-p coupling** ในการตั้งค่า BC อย่างถูกต้อง
- ตั้งค่า BC ขั้นต้นสำหรับ inlet, outlet, และ wall
- เขียน OpenFOAM BC file ตาม **โครงสร้างมาตรฐาน**

---

## 3W Framework

### What: Boundary Conditions คืออะไร?

**Boundary Conditions** คือเงื่อนไขขอบเขตที่ระบุพฤติกรรมของตัวแปร (velocity, pressure, temperature, ฯลฯ) ที่ขอบของ computational domain

แบ่งเป็น **3 ประเภททางคณิตศาสตร์**:

1. **Dirichlet BC** (Fixed Value) - กำหนดค่าโดยตรง
2. **Neumann BC** (Fixed Gradient) - กำหนด gradient/flux
3. **Robin BC** (Mixed) - ผสมทั้งสองแบบ

---

### Why: ทำไม BC สำคัญ?

> **"Boundary Conditions คือหัวใจของการ simulation"**

BC มีความสำคัญต่อเหตุผล 3 ประการ:

#### 1. PDE ต้องมี BC จึงจะมี **Unique Solution**
สมการ Navier-Stokes:
$$\frac{\partial \mathbf{u}}{\partial t} + (\mathbf{u} \cdot \nabla)\mathbf{u} = -\frac{1}{\rho}\nabla p + \nu\nabla^2\mathbf{u}$$

จากคณิตศาสตร์: **PDE ไม่มี BC → ไม่มีคำตอบที่ถูกต้อง** (ไม่ unique)

#### 2. BC ผิด → Simulation ล้มเหลว
- **Diverge:** ค่าตัวแปรเติบโตแบบ exponential จนคำนวณไม่ได้
- **ผลลัพธ์ผิด:** ได้คำตอบแต่ไม่ตรงกับความจริง
- **Non-physical:** ละเมิดกฎฟิสิกส์ (เช่น mass ไม่ conserve)

#### 3. กฎ **U-p Coupling** ต้องปฏิบัติตาม
- ถ้า **U** ใช้ `fixedValue` → **p** ต้องใช้ `zeroGradient`
- ถ้า **p** ใช้ `fixedValue` → **U** ต้องใช้ `zeroGradient` (หรือ variant)

> **⚠️ ละเมิดกฎนี้ → Solver diverge แบบรวดเร็ว!**

---

### How: การตั้งค่า BC ใน OpenFOAM

#### **ขั้นตอนที่ 1: ระบุประเภทขอบ (Boundary Type)**

| ขอบ | หน้าที่ | ตัวอย่าง | BC ที่ใช้บ่อย |
|-----|--------|----------|----------------|
| **Inlet** | ขอไหลเข้า | Pipe inlet, fan | `fixedValue` for U, `zeroGradient` for p |
| **Outlet** | ขอไหลออก | Pipe exit, atmosphere | `zeroGradient` for U, `fixedValue` for p |
| **Wall** | ขอแข็ง | ผนัง, วัตถุ | `noSlip` for U, thermal BC ตามประเภท |
| **Symmetry** | ระนาบสมมาตร | ลดขนาดโดเมน | `symmetry` |
| **Cyclic** | ขอบเชื่อมกัน | Periodic flow | `cyclic` |

#### **ขั้นตอนที่ 2: เลือกประเภท BC ตาม 3W Decision Tree**

```
รู้ค่าที่แน่นอนที่ขอบ?
│
├─ ใช่ → Dirichlet (fixedValue)
│
└─ ไม่ → รู้ gradient/flux?
    │
    ├─ ใช่ → Neumann (zeroGradient, fixedGradient)
    │
    └─ ไม่ → Robin (mixed) หรือ BC ขั้นสูง
```

#### **ขั้นตอนที่ 3: ตั้งค่าตาม U-p Coupling**
- **Inlet:** U = `fixedValue`, p = `zeroGradient`
- **Outlet:** U = `zeroGradient`, p = `fixedValue`
- **Wall:** U = `noSlip`, p = `zeroGradient`

#### **ขั้นตอนที่ 4: เขียนไฟล์ OpenFOAM**
สร้างไฟล์ในโฟลเดอร์ `0/` (เช่น `0/U`, `0/p`, `0/T`)

---

## สามประเภทหลักของ BC (รายละเอียด)

### 1. Dirichlet (Fixed Value)

**นิยามทางคณิตศาสตร์:**
$$\phi|_{\text{boundary}} = \phi_0$$

**กำหนดค่าโดยตรง** — ใช้เมื่อรู้ค่าที่ขอบ

```cpp
inlet
{
    type    fixedValue;
    value   uniform (10 0 0);  // m/s
}
```

**ตัวอย่างการใช้:**
- Velocity inlet
- Temperature wall (fixed temperature)
- Pressure outlet

---

### 2. Neumann (Fixed Gradient)

**นิยามทางคณิตศาสตร์:**
$$\frac{\partial \phi}{\partial n}\bigg|_{\text{boundary}} = g$$

**กำหนด gradient/flux** — ใช้เมื่อรู้อัตราการเปลี่ยนแปลง

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

**ตัวอย่างการใช้:**
- Fully developed flow outlet
- Adiabatic wall (zero heat flux)
- Specified heat flux boundary

---

### 3. Robin (Mixed)

**นิยามทางคณิตศาสตร์:**
$$\alpha\phi + \beta\frac{\partial\phi}{\partial n} = \gamma$$

**ผสมทั้งสองแบบ** — ใช้เมื่อมี coupling ระหว่างค่าและ gradient

```cpp
convectiveWall
{
    type            mixed;
    refValue        uniform 300;        // Reference temperature (Dirichlet)
    refGradient     uniform 0;          // Reference gradient (Neumann)
    valueFraction   uniform 0.5;        // 0=Neumann, 1=Dirichlet
}
```

**ความหมายของ `valueFraction`:**
- `valueFraction = 1` → ใช้ `refValue` เท่านั้น (pure Dirichlet)
- `valueFraction = 0` → ใช้ `refGradient` เท่านั้น (pure Neumann)
- `valueFraction = 0.5` → ผสม 50-50

**ตัวอย่างการใช้:**
- Convective heat transfer (h coefficient)
- Partial slip wall
- Porous jump boundary

---

## การตั้งค่าทั่วไปตามประเภทขอบ

### Inlet

| Field | Type | Value | หมายเหตุ |
|-------|------|-------|----------|
| **U** | `fixedValue` | `(Ux Uy Uz)` | กำหนด velocity ทิศทาง |
| **p** | `zeroGradient` | — | ปล่อยให้ปรับตาม flow |
| **T** | `fixedValue` | `T_inlet` | ถ้ามี heat transfer |
| **k** | `fixedValue` | $\frac{3}{2}(U \cdot I)^2$ | I = turbulence intensity (5-10%) |
| **ε** | `fixedValue` | $C_\mu^{3/4} \frac{k^{3/2}}{l}$ | $C_\mu = 0.09$, l = length scale |
| **nut** | `zeroGradient` | — | Eddy viscosity |

### Outlet

| Field | Type | Value | หมายเหตุ |
|-------|------|-------|----------|
| **U** | `zeroGradient` หรือ `pressureInletOutletVelocity` | — | ปล่อย flow ออก |
| **p** | `fixedValue` | `0` (gauge) | กำหนด reference pressure |
| **T** | `zeroGradient` | — | ถ้ามี heat transfer |
| **k** | `zeroGradient` | — | |
| **ε** | `zeroGradient` | — | |
| **nut** | `zeroGradient` | — | |

> **💡 เคล็ดลับ:** ใช้ `pressureInletOutletVelocity` ถ้ามี backflow ที่ outlet (flow ไหลกลับเข้ามาได้)

### Wall

| Field | Type | Value | หมายเหตุ |
|-------|------|-------|----------|
| **U** | `noSlip` | `(0 0 0)` | เทียบเท่า `fixedValue (0 0 0)` |
| **p** | `zeroGradient` | — | |
| **T** | `fixedValue` หรือ `zeroGradient` | ขึ้นกับ thermal BC | Fixed T หรือ adiabatic |
| **k** | `kqRWallFunction` | — | Wall function สำหรับ turbulence |
| **ε** | `epsilonWallFunction` | — | Wall function สำหรับ dissipation |
| **nut** | `nutkWallFunction` | — | Eddy viscosity wall function |

---

## OpenFOAM File Structure

### โครงสร้างไฟล์มาตรฐาน

```cpp
// 0/U
FoamFile
{
    version     2.0;
    format      ascii;
    class       volVectorField;      // volScalarField, volTensorField
    object      U;                    // ชื่อ field
}

dimensions      [0 1 -1 0 0 0 0];     // [mass length time temperature ...]

internalField   uniform (0 0 0);      // ค่าเริ่มต้นใน domain

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
        type    noSlip;               // เทียบเท่า fixedValue (0 0 0)
    }
    
    symmetryPlane
    {
        type    symmetry;
    }
}
```

### หมายเหตุสำคัญ
- **Header (`FoamFile`)**: บังคับสำหรับทุกไฟล์ OpenFOAM
- **Dimensions**: ใช้ [mass length time temperature...]
- **internalField**: ค่าเริ่มต้นที่ runtime เริ่มต้น
- **boundaryField**: ต้อง match กับชื่อใน `constant/polyMesh/boundary`

---

## Concept Check

<details>
<summary><b>1. ทำไม pressure ใช้ zeroGradient ที่ inlet?</b></summary>

เมื่อ velocity ถูกกำหนดที่ inlet (fixedValue) แล้ว:
- Pressure จะถูกคำนวณจาก **momentum equation**
- ปล่อยให้ pressure **ปรับตัวตามธรรมชาติ** เพื่อให้ satisfy momentum equation
- ใช้ zeroGradient เพื่อไม่กำหนด constraint เพิ่มเติม

**เทียบเท่ากับ:** ถ้ากำหนด p แล้ว → จะกำหนด constraint มากเกินไป → ไม่มี unique solution
</details>

<details>
<summary><b>2. noSlip กับ fixedValue (0 0 0) ต่างกันไหม?</b></summary>

**ผลลัพธ์เหมือนกัน** (velocity = 0 ที่ wall)

แต่ `noSlip` มีข้อดี:
- ✅ **ชัดเจนกว่า** — สื่อถึง "no-slip condition"
- ✅ **OpenFOAM จัดการ mesh motion** ให้ถูกต้อง (ถ้ามี moving mesh)
- ✅ **Best practice** — ใช้ `noSlip` สำหรับ stationary wall

**ใช้ `fixedValue (0 0 0)` เมื่อ:**
- Wall มี velocity ไม่เป็นศูนย์ (moving wall)
- ต้องการกำหนด velocity component บางตัว
</details>

<details>
<summary><b>3. valueFraction ใน mixed BC ทำงานอย่างไร?</b></summary>

**คือ weight ระหว่าง Dirichlet (1) กับ Neumann (0):**

```
valueFraction = 1   → 100% Dirichlet  (ใช้ refValue เท่านั้น)
valueFraction = 0   → 100% Neumann    (ใช้ refGradient เท่านั้น)
valueFraction = 0.5 → 50-50 Mixed     (ผสมทั้งสอง)
```

**ตัวอย่าง:** Convective heat transfer
```cpp
convectiveWall
{
    type            mixed;
    refValue        uniform 300;        // T_∞ (fluid temperature)
    refGradient     uniform 0;          
    valueFraction   uniform 0.3;        // 30% Dirichlet, 70% flux-based
}
```

การคำนวณจริง:
- OpenFOAM ใช้ weighted blend ระหว่าง refValue และ refGradient
- ใช้กับ **heat transfer coefficient (h)** หรือ **partial slip**
</details>

<details>
<summary><b>4. ถ้าตั้ง BC ผิด (ละเมิด U-p coupling) จะเกิดอะไร?</b></summary>

**อาการ:**
- Solver **diverge** ภายในไม่กี่ time step
- ค่า pressure/velocity **เติบโตแบบ exponential**
- ข้อความ error: `solution singularity` หรือ `matrix ill-conditioning`

**ตัวอย่าง BC ผิด:**
```cpp
// ❌ WRONG: ใช้ fixedValue ทั้งคู่
inlet
{
    U   { type fixedValue; value uniform (10 0 0); }
    p   { type fixedValue; value uniform 0; }      // ผิด!
}
```

**แก้:**
```cpp
// ✅ CORRECT: U-p coupling
inlet
{
    U   { type fixedValue; value uniform (10 0 0); }
    p   { type zeroGradient; }                     // ถูก!
}
```

**เหตุผลทางคณิตศาสตร์:**
- กำหนด U และ p พร้อมกัน → **over-constrained**
- ไม่มี unique solution ที่ satisfy momentum equation
</details>

---

## Key Takeaways

### ✅ สิ่งสำคัญที่ต้องจำ

1. **BC คือหัวใจ** — ไม่มี BC → ไม่มี unique solution
2. **3 ประเภทหลัก:**
   - Dirichlet (fixedValue) → รู้ค่า
   - Neumann (zeroGradient/fixedGradient) → รู้ flux
   - Robin (mixed) → ผสมทั้งสอง
3. **U-p Coupling ต้องถูกต้อง:**
   - U fixedValue ↔ p zeroGradient
   - U zeroGradient ↔ p fixedValue
4. **โครงสร้างไฟล์ OpenFOAM:**
   - FoamFile header → dimensions → internalField → boundaryField
5. **ใช้ `noSlip` แทน `fixedValue (0 0 0)`** สำหรับ stationary wall
6. **ใช้ `pressureInletOutletVelocity`** ถ้ามี backflow ที่ outlet

### 🎯 Best Practices

- ✅ ตรวจสอบ BC ทุกครั้งก่อน run
- ✅ ใช้ `checkMesh` เพื่อยืนยัน boundary names
- ✅ เริ่มจาก BC ง่ายๆ ก่อน (fixedValue/zeroGradient)
- ✅ อ่าน error log อย่างละเอียด — BC ผิดมัก diverge ตั้งแต่แรก

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [00_Overview.md](00_Overview.md) — ภาพรวม BC ใน OpenFOAM
- **บทถัดไป:** [02_Fundamental_Classification.md](02_Fundamental_Classification.md) — การจำแนกประเภท BC อย่างละเอียด
- **บทที่เกี่ยวข้อง:** [03_Specific_Boundary_Types.md](03_Specific_Boundary_Types.md) — BC เฉพาะทาง (inlet, outlet, wall, symmetry, cyclic)

---

## References

- OpenFOAM User Guide: Section 4.3 (Boundary Conditions)
- OpenFOAM Programmer's Guide: Chapter 3 (Field implementation)
- Jasak, H. (1996). "Error Analysis and Estimation for the Finite Volume Method"