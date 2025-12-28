# แบบฝึกหัด FVM

แบบฝึกหัดเชิงปฏิบัติเพื่อฝึกทักษะ Discretization และการตั้งค่า OpenFOAM

> **ทำไมต้องทำแบบฝึกหัด?**
> - ฝึกคำนวณ **matrix, flux, Peclet number** ด้วยตัวเอง
> - ฝึก **debug** mesh quality และ divergence
> - เตรียมพร้อมสำหรับโปรเจคจริง

---

## แบบฝึกหัด 1: Matrix Assembly

### โจทย์

สมการ Diffusion 1D:
$$\frac{d^2\phi}{dx^2} = 0$$

| Parameter | Value |
|-----------|-------|
| Cells | 3 cells |
| BC | $\phi_1 = 0$, $\phi_4 = 100$ |
| $\Delta x$ | 1 |

### ทำ

1. Discretize สมการ โดยใช้ Central Difference
2. เขียน Matrix $[A][\phi] = [b]$
3. แก้หา $\phi_2, \phi_3$

<details>
<summary><b>คำตอบ</b></summary>

**Discretization:**

สำหรับ Cell P:
$$\frac{\phi_E - 2\phi_P + \phi_W}{\Delta x^2} = 0$$

เขียนใหม่:
$$-\phi_W + 2\phi_P - \phi_E = 0$$

**Matrix:**

$$\begin{bmatrix}
2 & -1 \\
-1 & 2
\end{bmatrix}
\begin{bmatrix}
\phi_2 \\
\phi_3
\end{bmatrix}
=
\begin{bmatrix}
0 \\
100
\end{bmatrix}$$

(เพราะ $\phi_1 = 0$ และ $\phi_4 = 100$)

**Solution:**
- $\phi_2 = 33.3$
- $\phi_3 = 66.7$
</details>

---

## แบบฝึกหัด 2: Face Flux Calculation

### โจทย์

| Parameter | Value |
|-----------|-------|
| $\phi_P$ | 10 |
| $\phi_N$ | 20 |
| $u$ | 1 m/s (P→N) |
| $\rho$ | 1 kg/m³ |
| $A_f$ | 1 m² |

คำนวณ Convective Flux $F = \rho u \phi_f A_f$ โดยใช้:
- a) Central Differencing
- b) Upwind Differencing

<details>
<summary><b>คำตอบ</b></summary>

**a) Central Differencing:**

$$\phi_f = \frac{\phi_P + \phi_N}{2} = \frac{10 + 20}{2} = 15$$

$$F_{CD} = 1 \times 1 \times 15 \times 1 = 15 \text{ kg/s}$$

**b) Upwind (เพราะ u > 0 → ใช้ค่าจาก upstream cell P):**

$$\phi_f = \phi_P = 10$$

$$F_{UDS} = 1 \times 1 \times 10 \times 1 = 10 \text{ kg/s}$$

**ความแตกต่าง:** 33% — สำคัญสำหรับ accuracy!
</details>

---

## แบบฝึกหัด 3: Scheme Selection

### โจทย์

กำหนด:
- $u = 2$ m/s
- $\Gamma = 0.1$ m²/s
- $\Delta x = 0.1$ m
- $\rho = 1$ kg/m³

1. คำนวณ Peclet Number
2. เลือก Convection Scheme ที่เหมาะสม

<details>
<summary><b>คำตอบ</b></summary>

**Peclet Number:**

$$Pe = \frac{\rho u \Delta x}{\Gamma} = \frac{1 \times 2 \times 0.1}{0.1} = 2$$

**การเลือก:**

| Pe | Scheme |
|----|--------|
| < 2 | `Gauss linear` (Central) |
| = 2 | บนขอบ — ทั้งสองใช้ได้ |
| > 2 | `Gauss upwind` หรือ TVD |

**สำหรับ Pe = 2:** แนะนำ `Gauss linearUpwind` หรือ `Gauss vanLeer` เพื่อ balance accuracy กับ stability
</details>

---

## แบบฝึกหัด 4: OpenFOAM Case Setup

### โจทย์

ตั้งค่า Convection-Diffusion problem:

$$\frac{\partial T}{\partial t} + \nabla \cdot (\mathbf{u} T) = \alpha \nabla^2 T$$

กำหนด:
- Domain: Box 1×1×0.1 m
- Inlet: $T = 300$ K
- Outlet: Zero gradient
- Walls: Adiabatic
- $\alpha = 0.01$ m²/s
- $|\mathbf{u}| = 0.5$ m/s

### เขียน `system/fvSchemes`

<details>
<summary><b>คำตอบ</b></summary>

**ก่อนอื่น คำนวณ Pe:**

$$Pe = \frac{u \cdot L}{\alpha} = \frac{0.5 \times 0.1}{0.01} = 5$$

Pe > 2 → ใช้ Upwind หรือ TVD

```cpp
// system/fvSchemes
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvSchemes;
}

ddtSchemes
{
    default         Euler;
}

gradSchemes
{
    default         Gauss linear;
}

divSchemes
{
    default         none;
    div(phi,T)      Gauss linearUpwind grad(T);  // Pe > 2
}

laplacianSchemes
{
    default         Gauss linear corrected;
}
```
</details>

---

## แบบฝึกหัด 5: Debugging Divergence

### โจทย์

Simulation diverges หลัง 50 iterations. Log แสดง:

```
time step continuity errors : sum local = 1.5e+10
```

`checkMesh` แสดง:
```
Max non-orthogonality: 75
Max skewness: 0.8
```

### วินิจฉัยและแก้ไข

<details>
<summary><b>คำตอบ</b></summary>

**ปัญหา:**

1. **Non-orthogonality 75° > 70°** → ต้องเพิ่ม correction
2. **Skewness 0.8 > 0.6** → mesh quality ไม่ดี

**การแก้ไขใน `system/fvSolution`:**

```cpp
SIMPLE
{
    nNonOrthogonalCorrectors 3;  // เพิ่มจาก 0
}

relaxationFactors
{
    p       0.2;  // ลดจาก 0.3
    U       0.5;  // ลดจาก 0.7
}
```

**การแก้ไขใน `system/fvSchemes`:**

```cpp
laplacianSchemes
{
    default     Gauss linear limited 0.5;  // เพิ่ม limited
}

divSchemes
{
    div(phi,U)  Gauss upwind;  // เปลี่ยนเป็น stable scheme
}
```

**หรือ:** แก้ไข mesh ให้มีคุณภาพดีกว่า
</details>

---

## แบบฝึกหัด 6: Transient vs Steady

### โจทย์

เปรียบเทียบ settings สำหรับ:
- a) Steady-state pipe flow (Re = 10,000)
- b) Transient vortex shedding (Re = 100)

<details>
<summary><b>คำตอบ</b></summary>

**a) Steady-state (SIMPLE):**

```cpp
// system/fvSolution
SIMPLE
{
    nNonOrthogonalCorrectors 1;
    residualControl
    {
        p       1e-4;
        U       1e-4;
    }
}

relaxationFactors
{
    fields { p 0.3; }
    equations { U 0.7; k 0.7; epsilon 0.7; }
}

// system/fvSchemes
ddtSchemes { default steadyState; }
divSchemes { div(phi,U) Gauss linearUpwind grad(U); }
```

**b) Transient (PIMPLE):**

```cpp
// system/fvSolution
PIMPLE
{
    nOuterCorrectors 2;
    nCorrectors 1;
    nNonOrthogonalCorrectors 1;
}

// ไม่ใช้ relaxation หรือใช้ค่าสูง
relaxationFactors
{
    equations { U 1; }
}

// system/fvSchemes
ddtSchemes { default backward; }  // 2nd order
divSchemes { div(phi,U) Gauss linear; }  // Re ต่ำ → ใช้ได้

// system/controlDict
deltaT      0.001;
maxCo       0.5;  // เพื่อ accuracy
```
</details>

---

## Concept Check

<details>
<summary><b>1. ทำไม Upwind ถึง stable แต่ diffusive?</b></summary>

เพราะใช้ค่าจาก upstream เท่านั้น → ไม่มี information จาก downstream ที่อาจทำให้ oscillate → stable

แต่ truncation error ของ 1st order scheme มี form เหมือน diffusion term:
$$\frac{u \Delta x}{2} \frac{\partial^2 \phi}{\partial x^2}$$
→ เพิ่ม numerical diffusion เข้าไป
</details>

<details>
<summary><b>2. TVD schemes ดีกว่า Upwind อย่างไร?</b></summary>

TVD (Total Variation Diminishing) ใช้:
- High-order scheme ที่ smooth regions → accuracy
- Limiter ที่ sharp gradients → boundedness
- ไม่มี oscillation และลด numerical diffusion
</details>

<details>
<summary><b>3. ทำไม pressure ใช้ GAMG และ velocity ใช้ PBiCGStab?</b></summary>

- **Pressure equation:** Elliptic, symmetric → GAMG (multigrid) เร็วมาก
- **Velocity equation:** Asymmetric (มี convection) → PBiCGStab รองรับ asymmetric matrix
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [07_Best_Practices.md](07_Best_Practices.md) — Best Practices
- **บทถัดไป:** กลับไปที่ [00_Overview.md](00_Overview.md) — Overview