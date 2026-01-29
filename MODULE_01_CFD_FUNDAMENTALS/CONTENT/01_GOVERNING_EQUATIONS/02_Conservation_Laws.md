# การอนุรักษ์มวล โมเมนตัม และพลังงาน (Conservation Laws)

## Learning Objectives

หลังจากศึกษาบทนี้ คุณควรจะสามารถ:
- **อธิบาย** หลักการของกฎการอนุรักษ์ทั้งสาม (มวล โมเมนตัม พลังงาน)
- **เขียน** สมการควบคุมในรูปแบบ differential และ integral
- **เชื่อมโยง** แต่ละพจน์ในสมการกับความหมายทางกายภาพ
- **จำแนก** สมการที่เหมาะสมสำหรับ compressible และ incompressible flows
- **ระบุ** OpenFOAM solvers ที่ใช้สมการเหล่านี้
- **วินิจฉัย** ปัญหาการละเมิดกฎการอนุรักษ์ในการจำลอง

---

## Navigation Map

```
01_Introduction (Navier-Stokes Concepts)
         │
         ▼
02_Conservation_Laws ← YOU ARE HERE
         │
    ├────┴────┐
    ▼         ▼
03_EOS       04_FVM_Discretization
(Material   (Numerical Implementation)
 Properties)
```

---

## Overview

กฎการอนุรักษ์เป็น **รากฐานทางคณิตศาสตร์** ของ CFD ทั้งหมด ทุก solver ใน OpenFOAM สร้างขึ้นจากการแก้สมการเหล่านี้

> **ทำไมต้องเข้าใจกฎการอนุรักษ์?**
> - **มวล, โมเมนตัม, พลังงาน** — 3 กฎนี้คือทุกสิ่งใน CFD
> - FVM ใช้กฎเหล่านี้โดยตรง — integrate over control volume
> - เข้าใจกฎ = เข้าใจว่าทำไม simulation conserve หรือไม่ conserve
> - สามารถวินิจฉัยปัญหาเมื่อ simulation แก่ไม่ตก

---

## สัญลักษณ์และสัญชาตญาณ (Notation & Physical Intuition)

### สัญลักษณ์หลัก

| สัญลักษณ์ | ความหมาย | หน่วย | ชื่อใน OpenFOAM |
|-----------|----------|--------|-----------------|
| $\rho$ | ความหนาแน่น | kg/m³ | `rho` |
| $\mathbf{u}$ | เวกเตอร์ความเร็ว | m/s | `U` |
| $p$ | ความดัน | Pa | `p` |
| $T$ | อุณหภูมิ | K | `T` |
| $\mu$ | ความหนืด (dynamic viscosity) | Pa·s | `mu` or `nu` |
| $k$ | ความนำความร้อน | W/(m·K) | `k` |
| $c_p$ | ความจุความร้อนที่คงความดัน | J/(kg·K) | `Cp` |
| $\mathbf{g}$ | ความเร่งเนื่องจากแรงโน้มถ่วง | m/s² | `g` |

### สัญชาตญาณทางกายภาพ

> **💡 อนาล็อกอาคารสำนักงาน:**
> คิดถึงอาคารที่มีคนเข้า-ออก:
> - **การอนุรักษ์มวล** → คนในอาคาร = คนเข้า − คนออก
> - **การอนุรักษ์โมเมนตัม** → ความเร็วคนเปลี่ยนเพราะแรงดัน (คนดันคน) และแรงเสียดทาน
> - **การอนุรักษ์พลังงาน** → ความร้อนในอาคาร = ความร้อนจากคน + เครื่องปรับอากาศ + แสงแดด

---

## 1. การอนุรักษ์มวล (Continuity Equation)

### หลักการ

**"มวลไม่สามารถถูกสร้างหรือทำลายได้"**

### รูปแบบสมการ

**สำหรับของไหลอัดตัวได้ (Compressible):**
$$\boxed{\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \mathbf{u}) = 0}$$

**สำหรับของไหลอัดตัวไม่ได้ (Incompressible, $\rho = \text{constant}$):**
$$\boxed{\nabla \cdot \mathbf{u} = 0}$$

### การพิสูจน์ (Differential Approach)

พิจารณา control volume ขนาด $dx \times dy \times dz$:

**Step 1: มวลไหลเข้าที่แกน x**
$$\dot{m}_{in,x} = (\rho u_x) dy\, dz$$

**Step 2: มวลไหลออกที่แกน x**
$$\dot{m}_{out,x} = \left( \rho u_x + \frac{\partial (\rho u_x)}{\partial x} dx \right) dy\, dz$$

**Step 3: ฟลักซ์มวลสุทธิ (x-direction)**
$$\dot{m}_{net,x} = \dot{m}_{in,x} - \dot{m}_{out,x} = - \frac{\partial (\rho u_x)}{\partial x} dV$$

**Step 4: รวมทุกทิศทาง** (ใช้ Divergence Theorem)
$$\sum_{\text{faces}} \dot{m} = - \left[ \frac{\partial (\rho u_x)}{\partial x} + \frac{\partial (\rho u_y)}{\partial y} + \frac{\partial (\rho u_z)}{\partial z} \right] dV = - \nabla \cdot (\rho \mathbf{u}) \, dV$$

**Step 5: สมดุลกับอัตราสะสมมวล**
$$\frac{\partial \rho}{\partial t} dV = \nabla \cdot (\rho \mathbf{u}) \, dV$$

ได้สมการ: $\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \mathbf{u}) = 0$

> **💡 หมายเหตุ:** Gauss's Divergence Theorem แปลง surface integral → volume integral:
> $$\oint_S \mathbf{F} \cdot d\mathbf{S} = \int_V (\nabla \cdot \mathbf{F}) \, dV$$
> นี่คือหลักการพื้นฐานที่ทำให้ FVM ทำงานได้

### ความหมายทางกายภาพ

| พจน์ | ความหมาย | OpenFOAM Implementation |
|------|----------|------------------------|
| $\frac{\partial \rho}{\partial t}$ | การเปลี่ยนแปลงความหนาแน่น ณ จุดหนึ่ง | `fvm::ddt(rho)` |
| $\nabla \cdot (\rho \mathbf{u})$ | ฟลักซ์มวลสุทธิออกจากจุด (บวก = ไหลออกมากกว่าเข้า) | `fvm::div(rhoPhi, U)` |

สองพจน์นี้ต้องสมดุลกันเสมอ — นี่คือการอนุรักษ์มวล

---

## 2. การอนุรักษ์โมเมนตัม (Navier-Stokes Equations)

### หลักการ

**"แรงสุทธิ = อัตราการเปลี่ยนแปลงโมเมนตัม"** — กฎข้อที่สองของนิวตัน

### รูปแบบสมการ

**รูปแบบสมการทั่วไป:**
$$\boxed{\rho \frac{\partial \mathbf{u}}{\partial t} + \rho (\mathbf{u} \cdot \nabla) \mathbf{u} = -\nabla p + \nabla \cdot \boldsymbol{\tau} + \mathbf{f}}$$

**รูปแบบง่ายสำหรับ Incompressible Newtonian Fluid:**
$$\boxed{\rho \left(\frac{\partial \mathbf{u}}{\partial t} + \mathbf{u} \cdot \nabla \mathbf{u}\right) = -\nabla p + \mu \nabla^2 \mathbf{u} + \rho \mathbf{g}}$$

### ความหมายแต่ละพจน์

| พจน์ | ชื่อ | ความหมาย | อนาล็อก | OpenFOAM Implementation |
|------|------|----------|---------|------------------------|
| $\rho \frac{\partial \mathbf{u}}{\partial t}$ | Local acceleration | การเปลี่ยนแปลงความเร็วตามเวลา ณ จุดคงที่ | รถจอดอยู่แล้วเริ่มวิ่ง | `fvm::ddt(rho, U)` |
| $\rho (\mathbf{u} \cdot \nabla) \mathbf{u}$ | Convective acceleration | การเปลี่ยนแปลงความเร็วเมื่อของไหลเคลื่อนที่ผ่านจุดต่างๆ | รถเข้าโค้งเปลี่ยนทิศทาง | `fvm::div(rhoPhi, U)` |
| $-\nabla p$ | Pressure force | แรงจาก gradient ความดัน (ไหลจากสูงไปต่ำ) | รถคันหลังดันรถคันหน้า | `fvm::grad(p)` |
| $\mu \nabla^2 \mathbf{u}$ | Viscous force | แรงเสียดทานภายในของไหล | แรงเสียดทานถนน | `fvm::laplacian(nu, U)` |
| $\mathbf{f}$ | Body force | แรงภายนอก เช่น แรงโน้มถ่วง | แรงโน้มถ่วงตอนขึ้นเนิน | `rho*g` |

### Viscous Stress Tensor

**สำหรับ Newtonian fluid:**
$$\boldsymbol{\tau} = \mu \left[ \nabla \mathbf{u} + (\nabla \mathbf{u})^T \right] - \frac{2}{3}\mu (\nabla \cdot \mathbf{u})\mathbf{I}$$

**สำหรับ Incompressible flow ($\nabla \cdot \mathbf{u} = 0$):**
$$\boldsymbol{\tau} = \mu \left[ \nabla \mathbf{u} + (\nabla \mathbf{u})^T \right]$$

### ปัญหา Nonlinearity

เทอม $(\mathbf{u} \cdot \nabla) \mathbf{u}$ ทำให้สมการเป็น **nonlinear**:
- $\mathbf{u}$ ปรากฏทั้งในฐานะ coefficient และ unknown
- ต้องใช้วิธีวนซ้ำ (iterative methods) เช่น **PISO/SIMPLE**
- ใน OpenFOAM: แก้โดยการ predict pressure แล้ว correct velocity ซ้ำๆ

---

## 3. การอนุรักษ์พลังงาน (Energy Equation)

### หลักการ

**"พลังงานไม่สูญหาย เพียงเปลี่ยนรูป"** — กฎข้อที่หนึ่งของอุณหพลศาสตร์

### รูปแบบสมการ

**สมการพลังงานรวม (Total Energy):**
$$\frac{\partial (\rho E)}{\partial t} + \nabla \cdot (\rho E \mathbf{u}) = \nabla \cdot (k \nabla T) - \nabla \cdot (p \mathbf{u}) + \rho \mathbf{g} \cdot \mathbf{u} + \Phi$$

โดยที่ $E = e + \frac{1}{2}|\mathbf{u}|^2$ (พลังงานภายใน + พลังงานจลน์)

**สมการอุณหภูมิ** (รูปแบบที่ใช้บ่อย):
$$\boxed{\rho c_p \frac{\partial T}{\partial t} + \rho c_p (\mathbf{u} \cdot \nabla) T = k \nabla^2 T + \Phi + Q}$$

### ความหมายแต่ละพจน์

| พจน์ | ชื่อ | ความหมาย | OpenFOAM Implementation |
|------|------|----------|------------------------|
| $\rho c_p \frac{\partial T}{\partial t}$ | Storage | การสะสมพลังงานความร้อน | `fvm::ddt(rho, Cp, T)` |
| $\rho c_p (\mathbf{u} \cdot \nabla) T$ | Convection | การพาความร้อนโดยการไหล | `fvm::div(rhoPhi, Cp, T)` |
| $k \nabla^2 T$ | Conduction | การนำความร้อนตามกฎ Fourier | `fvm::laplacian(k, T)` |
| $\Phi = \boldsymbol{\tau} : \nabla \mathbf{u}$ | Viscous dissipation | พลังงานจลน์ที่กลายเป็นความร้อน | `viscous::Dissipation()` |
| $Q$ | Source | แหล่งกำเนิด/ตัวรับความร้อน | `Q_source` |

### Viscous Dissipation: เมื่อไหร่สำคัญ?

**Viscous dissipation** ($\Phi$) คืออัตราที่พลังงานจลน์ถูก "สลาย" เป็นความร้อนเนื่องจากแรงเสียดทานภายในของไหล

$$\Phi = 2\mu \left[ \left(\frac{\partial u}{\partial x}\right)^2 + \left(\frac{\partial v}{\partial y}\right)^2 + \left(\frac{\partial w}{\partial z}\right)^2 \right] + \mu \left[ \left(\frac{\partial u}{\partial y} + \frac{\partial v}{\partial x}\right)^2 + \cdots \right]$$

| Flow Condition | สำคัญหรือไม่? | ตัวอย่าง |
|----------------|------------------|----------|
| **Low speed flow** | ❌ เล็กมาก (< 1%) | การไหลน้ำในท่อ, อากาศพัดลม |
| **High speed flow** | ✅ สำคัญมาก | การไหลของน้ำมันเครื่อง, ชั้นบรรยากาศ |
| **Polymer processing** | ✅ สำคัญมาก | ฉีดพลาสติก (viscosity สูงมาก) |
| **Microfluidics** | ⚠️ อาจสำคัญ | Shear rate สูงมากใน channel เล็กๆ |

**ตัวอย่างเชิงตัวเลข:**

สำหรับการไหลของน้ำมันเครื่อง ($\mu \approx 0.1$ Pa·s) ผ่านช่องแคบ 0.5 mm ด้วยความเร็ว 10 m/s:
- Shear rate $\dot{\gamma} \approx \frac{U}{h} = \frac{10}{0.0005} = 20,000$ s⁻¹
- $\Phi \approx \mu \dot{\gamma}^2 \approx 0.1 \times (20000)^2 \approx 40,000,000$ W/m³
- **นี่คือความร้อนที่เกิดขึ้นเอง** จากแรงเสียดทาน!

> **💡 ใน OpenFOAM:**
> - Solvers ส่วนใหญ่ **ignore** $\Phi$ สำหรับ low-speed flows
> - สำหรับ high-speed compressible flows, solver เช่น `rhoCentralFoam` จะคิด $\Phi$ ให้อัตโนมัติ
> - ถ้าต้องการเปิดใช้: ตั้ง `viscous yes` ใน thermophysical properties

---

## 4. สมการการขนส่งทั่วไป (General Transport Equation)

สมการอนุรักษ์ทั้งหมดสามารถเขียนในรูปแบบทั่วไป:

$$\boxed{\frac{\partial (\rho \phi)}{\partial t} + \nabla \cdot (\rho \phi \mathbf{u}) = \nabla \cdot (\Gamma \nabla \phi) + S_\phi}$$

| สมการ | $\phi$ (Quantity) | $\Gamma$ (Diffusion Coeff) | $S_\phi$ (Source) |
|-------|------------------|--------------------------|------------------|
| Continuity | 1 | 0 | 0 |
| Momentum | $\mathbf{u}$ | $\mu$ | $-\nabla p + \mathbf{f}$ |
| Energy | $T$ | $k/c_p$ | $Q/(\rho c_p)$ |

**นี่คือรูปแบบที่ OpenFOAM ใช้:**
```cpp
// General form in OpenFOAM
fvm::ddt(rho, phi) + fvm::div(rhoPhi, phi) - fvm::laplacian(Gamma, phi) == S
```

---

## 5. ตารางเปรียบเทียบสมการอนุรักษ์

| สมการ | ปริมาณที่อนุรักษ์ | Compressible Form | Incompressible Form | OpenFOAM Solvers |
| :--- | :--- | :--- | :--- | :--- |
| **Continuity** | มวล | $\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \mathbf{u}) = 0$ | $\nabla \cdot \mathbf{u} = 0$ | ทุก solver |
| **Momentum** | โมเมนตัม | $\rho \frac{D\mathbf{u}}{Dt} = -\nabla p + \nabla \cdot \boldsymbol{\tau} + \mathbf{f}$ | $\rho \frac{D\mathbf{u}}{Dt} = -\nabla p + \mu \nabla^2 \mathbf{u} + \rho \mathbf{g}$ | `simpleFoam`, `pimpleFoam`, `rhoPimpleFoam` |
| **Energy** | พลังงาน | $\rho c_p \frac{DT}{Dt} = k \nabla^2 T + \Phi + Q$ | $\rho c_p \frac{DT}{Dt} = k \nabla^2 T + Q$ | `buoyantSimpleFoam`, `buoyantPimpleFoam` |

---

## 6. เมื่อการอนุรักษ์ล้มเหลว (When Conservation Breaks)

### สาเหตุของการละเมิดกฎการอนุรักษ์

| สาเหตุ | ผลกระทบ | การวินิจฉัย | การแก้ไข |
|--------|----------|-------------|-----------|
| **Coarse mesh** | Flux imbalance ระหว่าง faces | ตรวจสอบ ` continuity error ` ใน log | Refine mesh ใกล้ high gradient regions |
| **Large time step** | ไม่ converge → mass leak | ลองลด `deltaT` แล้วดูผล | ปรับ `maxCo` number |
| **Bad boundary conditions** | Mass/momentum เข้าไม่เท่าออก | Check `sum(phi)` ที่ inlet/outlet | ตรวจสอบว่า flowRate conservation |
| **Non-orthogonal cells** | Diffusion flux คลาดเคลื่อน | Check mesh quality `checkMesh` | Improve mesh orthogonality |
| **High Courant number** | Convection instability | Check `Co` number ใน log | ลด `deltaT` หรือ refine mesh |

### ตัวอย่าง Troubleshooting: Mass Imbalance

```
Problem:  continuity error ค่ามาก (เช่น 1e-2 แทนที่จะ 1e-6)

Diagnostic Steps:
1.  check initial → look for "max non-orthogonality"
2. grep "continuityError" log.simpleFoam | tail -20
3.  sum phi) ใน paraFoam

Solutions:
- ถ้า mesh quality แย่:  improve mesh or reduce nonOrthogonality correction
- ถ้า time step ใหญ่เกินไป:  reduce maxCo or adjust time step
- ถ้า BC ผิด:  verify inlet/outlet area conservation
```

### Numerical Errors vs Physical Violations

| ประเภท | ลักษณะ | ตัวอย่าง |
|--------|---------|---------|
| **Numerical error** | Conservation violated เพราะ discretization | Round-off error, truncation error |
| **Physical violation** | Physics model ผิดเอง | Wrong viscosity, missing source term |

---

## 7. OpenFOAM Implementation Links

### Solvers ที่ใช้สมการเหล่านี้

| Solver | สมการที่ใช้ | ใช้ทำอะไร |
|--------|-------------|-----------|
| `simpleFoam` | Mass + Momentum (incompressible, steady) | การไหลแบบ steady-state |
| `pimpleFoam` | Mass + Momentum (incompressible, transient) | การไหลแบบ transient |
| `rhoPimpleFoam` | Mass + Momentum + Energy (compressible) | การไหล compressible |
| `buoyantSimpleFoam` | Mass + Momentum + Energy (buoyancy) | การไหลแบบ natural convection |
| `rhoCentralFoam` | Mass + Momentum + Energy (high-speed) | การไหล transonic/supersonic |

### Code Snippets

```cpp
// Mass conservation (continuity)
surfaceScalarField phi(fvc::flux(U));
// หรือสำหรับ compressible:
surfaceScalarField phi(fvc::flux(rho*U));

// Momentum equation (incompressible)
tmp<fvVectorMatrix> tUEqn
(
    fvm::ddt(U) + fvm::div(phi, U)
  - fvm::laplacian(nu, U)
  ==
    fvOptions(U)
);
fvVectorMatrix& UEqn = tUEqn.ref();

// Energy equation
fvScalarMatrix TEqn
(
    fvm::ddt(T)
  + fvm::div(phi, T)
  - fvm::laplacian(k/rho/Cp, T)
  ==
    fvOptions(T)
);
```

---

## 8. Common Pitfalls (ข้อผิดพลาดที่พบบ่อย)

| Pitfall | สาเหตุ | ผลกระทบ | การแก้ไข |
|---------|--------|----------|-----------|
| **ใช้ incompressible solver กับ compressible flow** | $\nabla \cdot \mathbf{u} = 0$ ผิด | Mass conservation violated | ใช้ compressible solver เช่น `rhoPimpleFoam` |
| **ลืม viscous dissipation** ใน high-speed flow | $\Phi$ มีค่าสำคัญ | Temperature under-predicted | เปิด `viscous` ใน thermophysicalProperties |
| **Boundary conditions ไม่สมดุล** | Mass in ≠ mass out | Continuity error สูง | ตรวจสอบ flow rate ที่ inlets/outlets |
| **Mesh ไม่ sufficiently fine** | Gradient สูงในช่วงเล็ก | Flux imbalance | Refine mesh ใกล้ walls, gradients |
| **Time step ใหญ่เกินไป** | Courant number > 1 | Solution diverges | ลด `deltaT` ให้ Co < 1 (หรือ < 0.5 สำหรับ explicit) |

---

## 9. Transition to Next Topic

เราได้เรียนรู้สมการควบคุมทางคณิตศาสตร์แล้ว แต่ยังขาดอย่างหนึ่ง:

**"เราจะรู้ได้ไงว่าความหนาแน่น ($\rho$) คืออะไร หรือความหนืด ($\mu$) คืออะไร?"**

สมการข้างต้นมีตัวแปร **properties** ของของไหลที่ยังไม่ได้กำหนด ในบทถัดไป เราจะเรียนรู้:

- **สมการสถานะ (Equation of State)** — ความสัมพันธ์ $\rho = f(p, T)$
- **Thermophysical models** — วิธีกำหนด $\mu, k, c_p$ ใน OpenFOAM
- **Ideal gas vs. Incompressible** — เลือก model อะไรตอนไหน

---

## Concept Check

<details>
<summary><b>1. ถ้าการไหลเป็นแบบ Incompressible เทอมใดในสมการความต่อเนื่องจะหายไป?</b></summary>

**คำตอบ:** เทอม $\frac{\partial \rho}{\partial t}$ หายไป เพราะความหนาแน่นคงที่ ($\rho = \text{constant}$) ทำให้เหลือเพียง $\nabla \cdot \mathbf{u} = 0$

**ความสำคัญ:** นี่คือเหตุผลที่ incompressible solvers (เช่น `simpleFoam`) ไม่ต้องแก้สมการความต่อเนื่องแยก — velocity field ถูกกำหนดโดย $\nabla \cdot \mathbf{u} = 0$ โดยตรง

</details>

<details>
<summary><b>2. เทอม $(\mathbf{u} \cdot \nabla) \mathbf{u}$ ทำให้เกิดปัญหาอะไรในการแก้สมการ?</b></summary>

**คำตอบ:** ทำให้สมการเป็น **nonlinear** เพราะ:
- $\mathbf{u}$ ปรากฏทั้งในฐานะ coefficient และ unknown
- Linear solvers (เช่น conjugate gradient) แก้ไม่ได้โดยตรง
- ต้องใช้วิธีวนซ้ำ (iterative methods) เช่น **PISO/SIMPLE** algorithms
- ใน OpenFOAM: แก้โดยการ predict pressure แล้ว correct velocity ซ้ำๆ

**ใน code:** `fvm::div(phi, U)` — operator นี้ถูก linearize ในแต่ละ iteration

</details>

<details>
<summary><b>3. ทำไมสมการความต่อเนื่องไม่มีพจน์ diffusion?</b></summary>

**คำตอบ:** เพราะมวลขนส่งผ่านการไหล (convection) เท่านั้น มวลไม่สามารถ "แพร่" ผ่านผิวได้ในบริบทของ single-species continuum mechanics

**ต่างกับ:** 
- Momentum: มี diffusion (viscous term $\mu \nabla^2 \mathbf{u}$)
- Energy: มี diffusion (conduction term $k \nabla^2 T$)
- Mass: ไม่มี diffusion (เว้นแต่ multicomponent flows)

</details>

<details>
<summary><b>4. ถ้า simulation แสดง continuity error = 1e-2 แสดงว่าอะไร?</b></summary>

**คำตอบ:** แสดงว่า mass conservation ถูกละเมิดอย่างมาก (1% mass leak) อาจเกิดจาก:

1. **Mesh หยาบเกินไป** → Refine ใกล้ high-gradient regions
2. **Time step ใหญ่เกินไป** → ลด `maxCo` number
3. **Boundary conditions ไม่สมดุล** → Check mass flow rate in/out
4. **Non-orthogonal cells** → Improve mesh quality

**Diagnostic:** `grep "continuityError" log.simpleFoam` เพื่อดู trend ของ error ตลอด simulation

</details>

---

## เอกสารที่เกี่ยวข้อง

### บทก่อนหน้า
- **[01_Introduction.md](01_Introduction.md)** — บทนำสู่สมการควบคุม และแนวคิด Navier-Stokes

### บทถัดไป
- **[03_Equation_of_State.md](03_Equation_of_State.md)** — สมการสถานะ: วิธีกำหนด $\rho$, $\mu$, $k$, $c_p$ ใน OpenFOAM

### บทที่เกี่ยวข้อง
- **[04_Finite_Volume_Method.md](04_Finite_Volume_Method.md)** — วิธี discretization สมการเหล่านี้
- **[05_OpenFOAM_Implementation.md](05_OpenFOAM_Implementation.md)** — การ implement ใน OpenFOAM code
- **[06_Turbulence_Modeling.md](06_Turbulence_Modeling.md)** — การจำลองการไหลแบบ turbulent

---

## 10. Two-Phase Flow with Phase Change (R410A Evaporator)
## 10. การไหลสองเฟสพร้อมการเปลี่ยนเฟส (เครื่องระเหย R410A)

> **🔧 R410A Evaporator Focus**
>
> สำหรับการจำลองเครื่องระเหย R410A สมการอนุรักษ์ต้องถูกปรับปรุงเพื่อรองรับ:
> - **การเปลี่ยนเฟส** (ของเหลว → ไอ) พร้อมการขยายตัวของปริมาตรอย่างมหาศาล
> - **ความร้อนแฝง** (latent heat) ที่ถูกดูดซับระหว่างการระเหย
> - **การติดตาม interface** ระหว่างของเหลวและไอด้วย void fraction

### 10.1 สมการความต่อเนื่องที่มี Phase Change

ในการระเหย ปริมาตรขยายตัวอย่างมากเนื่องจากความแตกต่างของความหนาแน่น:

$$
\boxed{\nabla \cdot \mathbf{U} = \dot{m}\left(\frac{1}{\rho_v} - \frac{1}{\rho_l}\right)}
$$

โดยที่ $\dot{m}$ คืออัตราการถ่ายโอนมวลต่อหน่วยปริมาตร (kg/m³s)

**สำหรับ R410A ที่ $T_{sat} \approx 283$ K:**
| คุณสมบัติ | ค่า | หน่วย |
|---------|------|------|
| ความหนาแน่นของเหลว ($\rho_l$) | ~1000 | kg/m³ |
| ความหนาแน่นไอ ($\rho_v$) | ~30 | kg/m³ |
| อัตราส่วนความหนาแน่น ($\rho_v/\rho_l$) | ~1/30 | - |
| ความร้อนแฝง ($L$) | ~200 | kJ/kg |

> **💡 Physical Intuition:** เมื่อ 1 kg ของ R410A ระเหย → ปริมาตรขยายตัว ~30 เท่า!

### 10.2 แบบจำลอง Lee สำหรับการระเหย/ควบแน่น

$$
\dot{m} =
\begin{cases}
r_e \alpha_l \rho_l \dfrac{T - T_{sat}}{T_{sat}} & \text{for evaporation } (T > T_{sat}) \\[10pt]
r_c \alpha_v \rho_v \dfrac{T_{sat} - T}{T_{sat}} & \text{for condensation } (T < T_{sat})
\end{cases}
$$

โดยที่:
- $r_e, r_c$ = สัมประสิทธิ์การระเหย/ควบแน่น (s⁻¹) → ค่าทั่วไป: $r_e = 0.1$, $r_c = 0.01$
- $\alpha_l, \alpha_v$ = เศษส่วนปริมาตรของเหลว/ไอ ($\alpha_l + \alpha_v = 1$)

**สัญชาตญาณ:**
- ยิ่ง $T$ เกิน $T_{sat}$ มาก → อัตราการระเหยเร็วขึ้น
- ยิ่ง $\alpha_l$ มาก → มีของเหลวให้ระเหยมากขึ้น

### 10.3 สมการพลังงานที่มี Latent Heat

$$
\frac{\partial (\rho h)}{\partial t} + \nabla \cdot (\rho \mathbf{U} h) = \nabla \cdot (k \nabla T) + \underbrace{\dot{m} L}_{S_e}
$$

เทอมต้นกำเนิด $S_e = \dot{m} L$ คำนึงถึง:
- **การระเหย** ($\dot{m} > 0$): ดูดซับความร้อน → อุณหภูมิลดลง
- **การควบแน่น** ($\dot{m} < 0$): ปลดปล่อยความร้อน → อุณหภูมิเพิ่มขึ้น

### 10.4 สมการ Void Fraction Transport

เพื่อติดตาม interface ระหว่างของเหลวและไอ:

$$
\frac{\partial \alpha_v}{\partial t} + \nabla \cdot (\alpha_v \mathbf{U}) = \frac{\dot{m}}{\rho_v}
$$

หรือสำหรับเศษส่วนของเหลว:
$$
\frac{\partial \alpha_l}{\partial t} + \nabla \cdot (\alpha_l \mathbf{U}) = -\frac{\dot{m}}{\rho_l}
$$

### 10.5 C++ Implementation สำหรับ Phase Change

```cpp
// Lee phase change model for R410A evaporator
class LeePhaseChangeModel {
    double r_evap;        // Evaporation coefficient [s⁻¹]
    double r_cond;        // Condensation coefficient [s⁻¹]
    double T_sat;         // Saturation temperature [K]
    double latent_heat;   // Latent heat of vaporization [J/kg]

public:
    LeePhaseChangeModel(double re, double rc, double Tsat, double L)
        : r_evap(re), r_cond(rc), T_sat(Tsat), latent_heat(L) {}

    // Calculate mass transfer rate [kg/m³s]
    auto calculateMassSource(const auto& alpha_l, const auto& alpha_v,
                              const auto& T, const auto& rho_l, const auto& rho_v) {
        double delta_T = T - T_sat;
        double m_dot;

        if (delta_T > 0) {
            // Evaporation: liquid → vapor
            m_dot = r_evap * alpha_l * rho_l * delta_T / T_sat;
        } else {
            // Condensation: vapor → liquid
            m_dot = r_cond * alpha_v * rho_v * (-delta_T) / T_sat;
        }

        // Return pair: (mass source, energy source)
        return std::make_pair(m_dot, m_dot * latent_heat);
    }
};

// R410A evaporator example
LeePhaseChangeModel r410a(0.1, 0.01, 283.0, 200000.0);

// In solver loop:
auto [m_dot, S_energy] = r410a.calculateMassSource(
    alpha_l[cellI], alpha_v[cellI],
    T[cellI], rho_l, rho_v
);

// Update equations:
continuity_eqn += m_dot * (1.0/rho_v - 1.0/rho_l);
energy_eqn += S_energy;
```

### 10.6 Mixture Properties (สมบัติส่วนผสม)

เนื่องจากมีทั้งของเหลวและไอ ต้องคำนวณสมบัติส่วนผสม:

$$
\rho_{mix} = \alpha_v \rho_v + \alpha_l \rho_l
$$

$$
\mu_{mix} = \alpha_v \mu_v + \alpha_l \mu_l
$$

```cpp
// Calculate mixture density
double calculateMixtureDensity(double alpha_v, double rho_v, double rho_l) {
    return alpha_v * rho_v + (1.0 - alpha_v) * rho_l;
}
```

### 10.7 ข้อควรพิจารณาสำหรับ R410A Evaporator

| ประเด็น | คำอธิบาย | การแก้ไข |
|---------|-----------|-----------|
| **Strong source terms** | Phase change สร้าง source term ที่แรงมาก | ใช้ under-relaxation (0.1-0.3) |
| **Property variations** | $\rho, \mu, k$ เปลี่ยนมากกับ T, P | ใช้ lookup tables จาก CoolProp |
| **Interface diffusion** | Numerical diffusion เบลอ interface | ใช้ interface compression scheme |
| **Time step constraints** | CFL จำกัดโดยความเร็วเฟส | ใช้ adaptive time stepping |

> **🔗 See Also:**
> - Day 05: [Two-Phase Flow Fundamentals](../05_TWO_PHASE_FLOW/00_Two_Phase_Flow_Fundamentals.md) — VOF method, interface compression
> - Day 06: [Phase Change Theory](../06_PHASE_CHANGE_THEORY/00_Expansion_Term.md) — Expansion term derivation
> - Day 07: [Refrigerant Properties](../07_REFRIGERANT_PROPERTIES/00_Refrigerant_Properties.md) — R410A property tables

---

### อ้างอิงข้าม Module
- **Reynolds Number** → ดูรายละเอียดใน [04_Turbulence_Basics](../04_TURBULENCE_MODELING/CONTENT/01_Turbulence_Basics.md)
- **Wall Treatment** → ดู y+ calculation ใน [06_Wall_Functions](../04_TURBULENCE_MODELING/CONTENT/06_Wall_Functions.md)