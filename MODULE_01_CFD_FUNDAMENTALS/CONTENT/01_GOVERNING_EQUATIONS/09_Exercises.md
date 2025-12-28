# แบบฝึกหัด: สมการควบคุมและ OpenFOAM

แบบฝึกหัดเหล่านี้ช่วยให้คุณเชื่อมโยงทฤษฎีกับการใช้งานจริง

> **ทำไมต้องทำแบบฝึกหัด?**
> - **ทฤษฎีอย่างเดียวไม่พอ** — ต้องลองคำนวณด้วยตัวเองจึงจะเข้าใจ
> - ฝึก **debug** ปัญหาที่พบบ่อย
> - เตรียมพร้อมสำหรับโปรเจคจริง

---

---

## แบบฝึกหัดที่ 1: การอนุรักษ์มวล

**โจทย์:** หาสมการ Continuity สำหรับการไหล 1 มิติโดยใช้ control volume

### ขั้นตอน

1. พิจารณา control volume ขนาด $dx$ และพื้นที่หน้าตัด $A$
2. คำนวณ:
   - มวลไหลเข้า: $\dot{m}_{in} = \rho u A$
   - มวลไหลออก: $\dot{m}_{out} = \left(\rho u + \frac{\partial(\rho u)}{\partial x}dx\right)A$
   - การสะสมมวล: $\frac{\partial \rho}{\partial t} A\, dx$

3. สมดุลมวล: สะสม = เข้า − ออก

<details>
<summary><b>ดูคำตอบ</b></summary>

$$\frac{\partial \rho}{\partial t} + \frac{\partial(\rho u)}{\partial x} = 0$$

สำหรับ incompressible ($\rho = \text{const}$):
$$\frac{\partial u}{\partial x} = 0$$

**ใน OpenFOAM:** สมการนี้ถูกบังคับผ่าน pressure correction ใน SIMPLE/PISO algorithm
</details>

---

## แบบฝึกหัดที่ 2: ลดรูป Navier-Stokes

**โจทย์:** ลดรูปสมการ Navier-Stokes สำหรับ steady, incompressible, 2D flow

### สมการเต็ม

$$\rho \left(\frac{\partial \mathbf{u}}{\partial t} + \mathbf{u} \cdot \nabla \mathbf{u}\right) = -\nabla p + \mu \nabla^2 \mathbf{u} + \mathbf{f}$$

<details>
<summary><b>ดูคำตอบ</b></summary>

**ขั้นที่ 1: Steady** ($\partial/\partial t = 0$)
$$\rho \mathbf{u} \cdot \nabla \mathbf{u} = -\nabla p + \mu \nabla^2 \mathbf{u} + \mathbf{f}$$

**ขั้นที่ 2: 2D** ($\partial/\partial z = 0$, $w = 0$)

**X-momentum:**
$$\rho \left(u \frac{\partial u}{\partial x} + v \frac{\partial u}{\partial y}\right) = -\frac{\partial p}{\partial x} + \mu \left(\frac{\partial^2 u}{\partial x^2} + \frac{\partial^2 u}{\partial y^2}\right)$$

**Y-momentum:**
$$\rho \left(u \frac{\partial v}{\partial x} + v \frac{\partial v}{\partial y}\right) = -\frac{\partial p}{\partial y} + \mu \left(\frac{\partial^2 v}{\partial x^2} + \frac{\partial^2 v}{\partial y^2}\right)$$

**ใน OpenFOAM:** ใช้ `simpleFoam` กับ `ddtSchemes { default steadyState; }`
</details>

---

## แบบฝึกหัดที่ 3: เลือก Solver

**โจทย์:** เลือก solver ที่เหมาะสมสำหรับสถานการณ์ต่อไปนี้

| กรณี | $Re$ | $Ma$ | ประเภท | Solver? |
|------|------|------|--------|---------|
| A | 1500 | 0.1 | Steady | ? |
| B | 50000 | 0.05 | Transient | ? |
| C | 10000 | 0.5 | Steady | ? |
| D | 500 | 0.02 | Transient + Free Surface | ? |

<details>
<summary><b>ดูคำตอบ</b></summary>

| กรณี | Solver | เหตุผล |
|------|--------|--------|
| A | `simpleFoam` (laminar) | Steady, Incomp, Laminar ($Re < 2300$) |
| B | `pimpleFoam` + kEpsilon | Transient, Incomp, Turbulent ($Re > 4000$) |
| C | `rhoSimpleFoam` | Steady, Compressible ($Ma > 0.3$), Turbulent |
| D | `interFoam` (laminar) | Transient, Free surface, Laminar |

</details>

---

## แบบฝึกหัดที่ 4: Boundary Conditions

**โจทย์:** เขียน BCs สำหรับ pipe flow ที่มี inlet velocity = 10 m/s

```
case/
├── 0/
│   ├── U     ← เขียน BC
│   └── p     ← เขียน BC
```

<details>
<summary><b>ดูคำตอบ: 0/U</b></summary>

```cpp
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
    walls
    {
        type    noSlip;
    }
}
```
</details>

<details>
<summary><b>ดูคำตอบ: 0/p</b></summary>

```cpp
dimensions      [0 2 -2 0 0 0 0];
internalField   uniform 0;

boundaryField
{
    inlet
    {
        type    zeroGradient;
    }
    outlet
    {
        type    fixedValue;
        value   uniform 0;
    }
    walls
    {
        type    zeroGradient;
    }
}
```
</details>

---

## แบบฝึกหัดที่ 5: Initial Conditions for Turbulence

**โจทย์:** คำนวณค่าเริ่มต้น k และ epsilon สำหรับ:
- Velocity: $U = 10$ m/s
- Turbulence intensity: $I = 5\%$
- Length scale: $l = 0.01$ m

<details>
<summary><b>ดูคำตอบ</b></summary>

$$k = \frac{3}{2}(I \cdot U)^2 = \frac{3}{2}(0.05 \times 10)^2 = 0.375 \text{ m}^2/\text{s}^2$$

$$\epsilon = C_\mu^{0.75} \cdot k^{1.5} / l = 0.09^{0.75} \times 0.375^{1.5} / 0.01 \approx 3.73 \text{ m}^2/\text{s}^3$$

**ไฟล์ 0/k:**
```cpp
internalField   uniform 0.375;
```

**ไฟล์ 0/epsilon:**
```cpp
internalField   uniform 3.73;
```
</details>

---

## แบบฝึกหัดที่ 6: แปลสมการเป็น OpenFOAM

**โจทย์:** แปลสมการ scalar transport เป็น fvMatrix

$$\frac{\partial T}{\partial t} + \nabla \cdot (\mathbf{u} T) = \nabla \cdot (D \nabla T) + S$$

<details>
<summary><b>ดูคำตอบ</b></summary>

```cpp
fvScalarMatrix TEqn
(
    fvm::ddt(T)                    // ∂T/∂t
  + fvm::div(phi, T)               // ∇·(uT)
  - fvm::laplacian(D, T)           // -∇·(D∇T)
 ==
    fvOptions(T)                   // Source term S
);

TEqn.relax();
TEqn.solve();
```
</details>

---

## แบบฝึกหัดที่ 7: เลือก Discretization Scheme

**โจทย์:** เลือก scheme ใน `fvSchemes` สำหรับ high-Re turbulent flow

| Term | Scheme? | เหตุผล? |
|------|---------|---------|
| `div(phi,U)` | ? | ? |
| `laplacian(nuEff,U)` | ? | ? |
| `grad(p)` | ? | ? |

<details>
<summary><b>ดูคำตอบ</b></summary>

```cpp
divSchemes
{
    default         none;
    div(phi,U)      Gauss linearUpwind grad(U);  // 2nd order, stable
    div(phi,k)      Gauss upwind;                // 1st order for turbulence
    div(phi,epsilon) Gauss upwind;
}

laplacianSchemes
{
    default         Gauss linear corrected;      // 2nd order, unbounded
}

gradSchemes
{
    default         Gauss linear;                // Standard central
    grad(U)         cellLimited Gauss linear 1;  // Limited for stability
}
```

**เหตุผล:**
- Convection (div): `linearUpwind` ให้ความแม่นยำ 2nd order และเสถียรกว่า `linear`
- Turbulence: `upwind` เสถียรกว่า เพราะ k, epsilon sensitive
- Laplacian: `linear corrected` สำหรับ non-orthogonal mesh
</details>

---

## แบบฝึกหัดที่ 8: Debug Divergence

**โจทย์:** Simulation diverge ที่ time step แรก เห็นใน log:

```
Solving for Ux, Initial residual = 1, Final residual = 1e+20, No Iterations 1
Floating point exception
```

สาเหตุที่เป็นไปได้? วิธีแก้?

<details>
<summary><b>ดูคำตอบ</b></summary>

**สาเหตุที่เป็นไปได้:**
1. Initial conditions ไม่ถูกต้อง (เช่น k = 0, epsilon = 0)
2. BC ขัดแย้งกัน (เช่น fixedValue ทั้ง U และ p ที่ outlet)
3. Mesh คุณภาพต่ำ (non-orthogonality สูง)
4. Time step ใหญ่เกินไป (Co > 1)

**วิธีแก้:**
1. ตรวจสอบ `0/k`, `0/epsilon` ไม่ให้เป็น 0
2. ตรวจสอบ BC ว่า inlet = fixedValue U + zeroGradient p
3. รัน `checkMesh` ดู non-orthogonality
4. ลด `deltaT` หรือใช้ `adjustTimeStep yes;`
5. เพิ่ม under-relaxation ใน `fvSolution`
</details>

---

## แบบฝึกหัดที่ 9: Wall y+

**โจทย์:** คำนวณ first cell height สำหรับ:
- $y^+ = 50$
- $U = 20$ m/s
- $L = 1$ m (ความยาวลักษณะเฉพาะ)
- $\nu = 1.5 \times 10^{-5}$ m²/s

<details>
<summary><b>ดูคำตอบ</b></summary>

**ขั้นที่ 1:** ประมาณ Re และ $C_f$

$$Re = \frac{UL}{\nu} = \frac{20 \times 1}{1.5 \times 10^{-5}} = 1.33 \times 10^6$$

$$C_f \approx 0.058 \cdot Re^{-0.2} = 0.058 \times (1.33 \times 10^6)^{-0.2} \approx 0.00345$$

**ขั้นที่ 2:** คำนวณ $u_\tau$

$$u_\tau = U \sqrt{C_f/2} = 20 \times \sqrt{0.00345/2} \approx 0.83 \text{ m/s}$$

**ขั้นที่ 3:** คำนวณ $y$

$$y = \frac{y^+ \cdot \nu}{u_\tau} = \frac{50 \times 1.5 \times 10^{-5}}{0.83} \approx 0.0009 \text{ m} = 0.9 \text{ mm}$$

**สรุป:** First cell height ≈ 0.9 mm สำหรับ $y^+ = 50$
</details>

---

## แบบฝึกหัดที่ 10: Algorithm Selection

**โจทย์:** เมื่อไหร่ใช้ SIMPLE, PISO, PIMPLE?

<details>
<summary><b>ดูคำตอบ</b></summary>

| Algorithm | ใช้เมื่อ | ข้อดี |
|-----------|---------|-------|
| **SIMPLE** | Steady-state | วนซ้ำจนลู่เข้า, เสถียร |
| **PISO** | Transient, $\Delta t$ เล็ก | ไม่ต้อง outer loop, เร็ว |
| **PIMPLE** | Transient, $\Delta t$ ใหญ่ | Outer corrections รองรับ Co > 1 |

**การตั้งค่าใน fvSolution:**

```cpp
// SIMPLE
SIMPLE
{
    nNonOrthogonalCorrectors 1;
    residualControl { p 1e-4; U 1e-4; }
}

// PISO
PISO
{
    nCorrectors 2;
    nNonOrthogonalCorrectors 1;
}

// PIMPLE
PIMPLE
{
    nOuterCorrectors 2;
    nCorrectors 1;
    nNonOrthogonalCorrectors 0;
}
```
</details>

---

## Concept Check

<details>
<summary><b>1. fvm กับ fvc ต่างกันอย่างไร?</b></summary>

- `fvm::` = Implicit, สร้าง matrix coefficient, แก้ร่วมกับ unknown
- `fvc::` = Explicit, คำนวณจาก field ปัจจุบัน, ใส่ใน source term
</details>

<details>
<summary><b>2. ทำไม pressure gradient ใช้ fvc ไม่ใช่ fvm?</b></summary>

เพราะ $-\nabla p$ ไม่มี unknown $\mathbf{u}$ อยู่ในนั้น มันเป็นแรงที่มาจาก pressure field ที่คำนวณแยก (pressure correction) จึงเป็น explicit term
</details>

<details>
<summary><b>3. เมื่อไหร่ต้องใช้ nNonOrthogonalCorrectors > 0?</b></summary>

เมื่อ mesh มี non-orthogonality สูง (> 70°) การ correction ช่วยให้ gradient ที่ face ถูกต้องมากขึ้น
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [08_Key_Points_to_Remember.md](08_Key_Points_to_Remember.md) — สรุปประเด็นสำคัญ
- **ภาพรวม:** [00_Overview.md](00_Overview.md) — ภาพรวมบทนี้
- **การนำไปใช้:** [05_OpenFOAM_Implementation.md](05_OpenFOAM_Implementation.md) — รายละเอียด implementation