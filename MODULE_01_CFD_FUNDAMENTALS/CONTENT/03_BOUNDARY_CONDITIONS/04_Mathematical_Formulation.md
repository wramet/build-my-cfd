# สูตรทางคณิตศาสตร์ของ Boundary Conditions

พื้นฐานทางคณิตศาสตร์และการ discretize BC ใน FVM

> **ทำไมต้องเข้าใจคณิตศาสตร์ของ BC?**
> - เข้าใจความแตกต่าง **Dirichlet vs Neumann vs Mixed**
> - รู้ว่า BC **ส่งผลต่อ matrix** อย่างไร
> - Debug ได้เมื่อ BC ไม่ทำงานตามคาด

---

## สามประเภทหลัก

### 1. Dirichlet (First Kind)

$$\phi|_{\partial\Omega} = \phi_0(\mathbf{x}, t)$$

**กำหนดค่าโดยตรงที่ขอบ**

| ตัวอย่าง | สมการ |
|---------|-------|
| Inlet velocity | $\mathbf{u} = \mathbf{u}_{\text{inlet}}$ |
| Wall temperature | $T = T_{\text{wall}}$ |
| Outlet pressure | $p = p_{\text{atm}}$ |

### 2. Neumann (Second Kind)

$$\frac{\partial\phi}{\partial n}\bigg|_{\partial\Omega} = g(\mathbf{x}, t)$$

**กำหนด normal derivative (flux) ที่ขอบ**

| ตัวอย่าง | สมการ |
|---------|-------|
| Adiabatic wall | $\frac{\partial T}{\partial n} = 0$ |
| Heat flux | $-k\frac{\partial T}{\partial n} = q''$ |
| Fully developed | $\frac{\partial \mathbf{u}}{\partial n} = 0$ |

### 3. Robin (Third Kind)

$$a\phi + b\frac{\partial\phi}{\partial n} = c$$

**ผสมค่าและ gradient**

| ตัวอย่าง | สมการ |
|---------|-------|
| Convection | $-k\frac{\partial T}{\partial n} = h(T - T_\infty)$ |
| Radiation | $-k\frac{\partial T}{\partial n} = \varepsilon\sigma(T^4 - T^4_\infty)$ |

---

## Discretization ใน FVM

### Dirichlet BC

สำหรับ cell P ติดกับ boundary face f:

$$a_P\phi_P = \sum_N a_N\phi_N + b_P$$

**การ modify:**

```
Diagonal: a_P → a_P + a_f
Source:   b_P → b_P + a_f × φ_boundary
Off-diag: เอา a_f ออกจาก neighbor term
```

**OpenFOAM implementation:**
```cpp
// Dirichlet contributes to diagonal and source
internalCoeffs = patchInternalCoeffs
boundaryCoeffs = patchField * patchInternalCoeffs
```

### Neumann BC

$$\frac{\partial\phi}{\partial n}\bigg|_f = g_f$$

**การ modify:**
```
Flux: F_f = -Γ × g_f × A_f
Source: b_P → b_P + F_f
```

สำหรับ `zeroGradient` ($g_f = 0$):
```
φ_f = φ_P  (extrapolate จาก cell center)
```

### Robin BC

$$a\phi_f + b\frac{\partial\phi}{\partial n}\bigg|_f = c$$

**การ modify:**
```
ใช้ linear interpolation:
φ_f = α × φ_boundary + (1-α) × extrapolated_value

α = valueFraction
```

---

## Well-Posedness (Hadamard)

ปัญหาเป็น **well-posed** ถ้า:

1. **Existence** — มีคำตอบ
2. **Uniqueness** — คำตอบเป็นเอกลักษณ์
3. **Stability** — คำตอบเปลี่ยนต่อเนื่องตาม BC

### ข้อกำหนดตามประเภท PDE

| PDE Type | ตัวอย่าง | BC Requirement |
|----------|---------|----------------|
| **Elliptic** | Laplace, Poisson | BC ที่ทุกขอบ |
| **Parabolic** | Heat diffusion | IC + BC |
| **Hyperbolic** | Wave equation | Characteristic-based |

---

## การ Couple ระหว่าง U และ p

### Incompressible Flow

สมการ continuity:
$$\nabla \cdot \mathbf{u} = 0$$

สมการ momentum:
$$\frac{\partial\mathbf{u}}{\partial t} + (\mathbf{u}\cdot\nabla)\mathbf{u} = -\frac{1}{\rho}\nabla p + \nu\nabla^2\mathbf{u}$$

**กฎ Coupling:**

| ถ้า U เป็น... | แล้ว p ต้องเป็น... |
|---------------|---------------------|
| `fixedValue` | `zeroGradient` |
| `zeroGradient` | `fixedValue` |

**เหตุผล:** ถ้ากำหนดทั้ง U และ p เป็น Dirichlet → **over-constrained** → diverge

---

## Reference Pressure

สำหรับ incompressible flow:
- สมการสนใจเฉพาะ $\nabla p$ ไม่ใช่ค่าสัมบูรณ์
- ต้องกำหนดอย่างน้อย 1 จุดเป็น reference

**วิธีใน OpenFOAM:**

```cpp
// system/fvSolution
SIMPLE
{
    pRefCell    0;
    pRefValue   0;
}
```

หรือใช้ `fixedValue` ที่ outlet

---

## Flux Conservation

ใน FVM flux ที่ face คำนวณครั้งเดียว:

$$F_f = \phi_f \cdot (\mathbf{u}_f \cdot \mathbf{S}_f)$$

**ผลลัพธ์:**
- สิ่งที่ออกจาก cell A = สิ่งที่เข้า cell B
- Conservation โดยธรรมชาติ

---

## Concept Check

<details>
<summary><b>1. ทำไม incompressible flow ต้องมี reference p?</b></summary>

เพราะสมการ momentum มีเฉพาะ $\nabla p$ → ค่าสัมบูรณ์ไม่ถูกกำหนด → ถ้าไม่มี reference จะได้คำตอบไม่จำกัด (floating pressure)
</details>

<details>
<summary><b>2. Over-constrained BC เกิดเมื่อไหร่?</b></summary>

เมื่อกำหนด Dirichlet ทั้ง U และ p ที่ boundary เดียวกัน → ขัดแย้งกับ continuity → solver ไม่สามารถหา consistent solution
</details>

<details>
<summary><b>3. Neumann BC ใส่ค่าใน matrix อย่างไร?</b></summary>

- ไม่แก้ diagonal หรือ off-diagonal
- เพิ่ม flux เข้า source term โดยตรง: $b_P \leftarrow b_P - \Gamma \cdot g \cdot A_f$
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [03_Selection_Guide_Which_BC_to_Use.md](03_Selection_Guide_Which_BC_to_Use.md) — คู่มือการเลือก BC
- **บทถัดไป:** [05_Common_Boundary_Conditions_in_OpenFOAM.md](05_Common_Boundary_Conditions_in_OpenFOAM.md) — BC ที่ใช้บ่อย