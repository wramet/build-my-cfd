# กฎการอนุรักษ์

กฎการอนุรักษ์เป็น **รากฐานทางคณิตศาสตร์** ของ CFD ทั้งหมด

> **ทำไมต้องเข้าใจกฎการอนุรักษ์?**
> - **มวล, โมเมนตัม, พลังงาน** — 3 กฎนี้คือทุกสิ่งใน CFD
> - FVM ใช้กฎเหล่านี้โดยตรง — integrate over control volume
> - เข้าใจกฎ = เข้าใจว่าทำไม simulation conserve หรือไม่ conserve

---

---

## การอนุรักษ์มวล (Continuity Equation)

### หลักการ

**"มวลไม่สามารถถูกสร้างหรือทำลายได้"**

> **💡 สัญชาตญาณทางกายภาพ:**
> คิดถึงอาคารสำนักงาน — จำนวนคนในอาคารเปลี่ยนแปลงตามผลต่างของคนเข้า-ออก ถ้าไม่มีใครเกิดหรือตายในอาคาร: คนเพิ่ม = คนเข้า − คนออก

### รูปแบบสมการ

**สำหรับของไหลอัดตัวได้ (Compressible):**
$$\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \mathbf{u}) = 0$$

**สำหรับของไหลอัดตัวไม่ได้ (Incompressible, $\rho = \text{constant}$):**
$$\nabla \cdot \mathbf{u} = 0$$

โดยที่:
- $\rho$ = ความหนาแน่น [kg/m³]
- $\mathbf{u}$ = เวกเตอร์ความเร็ว [m/s]

### การพิสูจน์

พิจารณา control volume ขนาด $dx \times dy \times dz$:

1. **มวลไหลเข้า** ที่ตำแหน่ง $x$: $\dot{m}_{in} = (\rho u_x) dy\, dz$
2. **มวลไหลออก** ที่ตำแหน่ง $x + dx$: $\dot{m}_{out} = \left( \rho u_x + \frac{\partial (\rho u_x)}{\partial x} dx \right) dy\, dz$
3. **ฟลักซ์มวลสุทธิ**: $\dot{m}_{in} - \dot{m}_{out} = - \frac{\partial (\rho u_x)}{\partial x} dV$
4. **รวมทุกทิศทาง**: $- \nabla \cdot (\rho \mathbf{u}) \, dV$
5. **สมดุลกับอัตราสะสมมวล**: $\frac{\partial \rho}{\partial t} dV$

ได้สมการ: $\boxed{\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \mathbf{u}) = 0}$

### ความหมายทางกายภาพ

| พจน์ | ความหมาย |
|------|----------|
| $\frac{\partial \rho}{\partial t}$ | การเปลี่ยนแปลงความหนาแน่น ณ จุดหนึ่ง (บวก = สะสมมวล, ลบ = สูญเสียมวล) |
| $\nabla \cdot (\rho \mathbf{u})$ | ฟลักซ์มวลสุทธิออกจากจุด (บวก = ไหลออกมากกว่าเข้า) |

สองพจน์นี้ต้องสมดุลกันเสมอ — นี่คือการอนุรักษ์มวล

---

## การอนุรักษ์โมเมนตัม (Navier-Stokes Equations)

### หลักการ

**"แรงสุทธิ = มวล × ความเร่ง"** — กฎข้อที่สองของนิวตัน

> **💡 สัญชาตญาณทางกายภาพ:**
> คิดถึงรถบนทางด่วน — ความเร็วรถเปลี่ยนเพราะ:
> - **แรงดัน**: รถคันหลังดันรถคันหน้า
> - **แรงหนืด**: แรงเสียดทานถนน
> - **แรงภายนอก**: แรงโน้มถ่วงตอนขึ้น/ลงเนิน

### รูปแบบสมการ

$$\rho \frac{\partial \mathbf{u}}{\partial t} + \rho (\mathbf{u} \cdot \nabla) \mathbf{u} = -\nabla p + \mu \nabla^2 \mathbf{u} + \mathbf{f}$$

### ความหมายแต่ละพจน์

| พจน์ | ชื่อ | ความหมาย |
|------|------|----------|
| $\rho \frac{\partial \mathbf{u}}{\partial t}$ | Local acceleration | การเปลี่ยนแปลงความเร็วตามเวลา ณ จุดคงที่ |
| $\rho (\mathbf{u} \cdot \nabla) \mathbf{u}$ | Convective acceleration | การเปลี่ยนแปลงความเร็วเมื่อของไหลเคลื่อนที่ผ่านจุดต่างๆ |
| $-\nabla p$ | Pressure force | แรงจาก gradient ความดัน (ไหลจากสูงไปต่ำ) |
| $\mu \nabla^2 \mathbf{u}$ | Viscous force | แรงเสียดทานภายในของไหล |
| $\mathbf{f}$ | Body force | แรงภายนอก เช่น แรงโน้มถ่วง |

### Viscous Stress Tensor

สำหรับ Newtonian fluid:
$$\boldsymbol{\tau} = \mu \left[ \nabla \mathbf{u} + (\nabla \mathbf{u})^T \right] - \frac{2}{3}\mu (\nabla \cdot \mathbf{u})\mathbf{I}$$

**รูปแบบที่ง่ายขึ้น** (Incompressible Newtonian fluid):
$$\rho \left(\frac{\partial \mathbf{u}}{\partial t} + \mathbf{u} \cdot \nabla \mathbf{u}\right) = -\nabla p + \mu \nabla^2 \mathbf{u} + \rho \mathbf{g}$$

---

## การอนุรักษ์พลังงาน (Energy Equation)

### หลักการ

**"พลังงานไม่สูญหาย เพียงเปลี่ยนรูป"** — กฎข้อที่หนึ่งของอุณหพลศาสตร์

### รูปแบบสมการ

**สมการพลังงานรวม:**
$$\frac{\partial (\rho E)}{\partial t} + \nabla \cdot (\rho E \mathbf{u}) = \nabla \cdot (k \nabla T) - \nabla \cdot (p \mathbf{u}) + \rho \mathbf{g} \cdot \mathbf{u} + \Phi$$

โดยที่ $E = e + \frac{1}{2}|\mathbf{u}|^2$ (พลังงานภายใน + พลังงานจลน์)

**สมการอุณหภูมิ** (รูปแบบที่ใช้บ่อย):
$$\rho c_p \frac{\partial T}{\partial t} + \rho c_p (\mathbf{u} \cdot \nabla) T = k \nabla^2 T + \Phi + Q$$

### ความหมายแต่ละพจน์

| พจน์ | ชื่อ | ความหมาย |
|------|------|----------|
| $\rho c_p \frac{\partial T}{\partial t}$ | Storage | การสะสมพลังงานความร้อน |
| $\rho c_p (\mathbf{u} \cdot \nabla) T$ | Convection | การพาความร้อนโดยการไหล |
| $k \nabla^2 T$ | Conduction | การนำความร้อนตามกฎ Fourier |
| $\Phi = \boldsymbol{\tau} : \nabla \mathbf{u}$ | Viscous dissipation | พลังงานกลที่กลายเป็นความร้อน |
| $Q$ | Source | แหล่งกำเนิด/ตัวรับความร้อน |

---

## สมการการขนส่งทั่วไป (General Transport Equation)

สมการอนุรักษ์ทั้งหมดสามารถเขียนในรูปแบบทั่วไป:

$$\frac{\partial (\rho \phi)}{\partial t} + \nabla \cdot (\rho \phi \mathbf{u}) = \nabla \cdot (\Gamma \nabla \phi) + S_\phi$$

| สมการ | $\phi$ | $\Gamma$ | $S_\phi$ |
|-------|--------|----------|----------|
| Continuity | 1 | 0 | 0 |
| Momentum | $\mathbf{u}$ | $\mu$ | $-\nabla p + \mathbf{f}$ |
| Energy | $T$ | $k/c_p$ | $Q/(\rho c_p)$ |

นี่คือ **รูปแบบที่ OpenFOAM ใช้** ในการ discretize ทุกสมการ

---

## ตารางสรุป
| สมการ | ปริมาณที่อนุรักษ์ | Compressible | Incompressible |
| :--- | :--- | :--- | :--- |
| **Continuity** | มวล | $\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \mathbf{u}) = 0$ | $\nabla \cdot \mathbf{u} = 0$ |
| **Momentum** | โมเมนตัม | $\rho \frac{D\mathbf{u}}{Dt} = -\nabla p + \nabla \cdot \boldsymbol{\tau} + \mathbf{f}$ | $\rho \frac{D\mathbf{u}}{Dt} = -\nabla p + \nabla \cdot \boldsymbol{\tau} + \mathbf{f}$ |
| **Energy** | พลังงาน | $\rho c_p \frac{DT}{Dt} = k \nabla^2 T + \Phi + Q$ | $\rho c_p \frac{DT}{Dt} = k \nabla^2 T + \Phi + Q$ |
---

## Concept Check

<details>
<summary><b>1. ถ้าการไหลเป็นแบบ Incompressible เทอมใดในสมการความต่อเนื่องจะหายไป?</b></summary>

เทอม $\frac{\partial \rho}{\partial t}$ หายไป เพราะความหนาแน่นคงที่ ทำให้เหลือเพียง $\nabla \cdot \mathbf{u} = 0$

</details>

<details>
<summary><b>2. เทอม $(\mathbf{u} \cdot \nabla) \mathbf{u}$ ทำให้เกิดปัญหาอะไรในการแก้สมการ?</b></summary>

ทำให้สมการเป็น **nonlinear** เพราะ $\mathbf{u}$ ปรากฏทั้งในฐานะ coefficient และ unknown ต้องใช้วิธีวนซ้ำ (iterative methods) ในการแก้

</details>

<details>
<summary><b>3. ทำไมสมการความต่อเนื่องไม่มีพจน์ diffusion?</b></summary>

เพราะมวลขนส่งผ่านการไหล (convection) เท่านั้น มวลไม่สามารถ "แพร่" ผ่านผิวได้ในบริบทของ single-species continuum mechanics

</details>
---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [01_Introduction.md](01_Introduction.md) — บทนำสู่สมการควบคุม
- **บทถัดไป:** [03_Equation_of_State.md](03_Equation_of_State.md) — สมการสถานะ
- **การนำไปใช้:** [05_OpenFOAM_Implementation.md](05_OpenFOAM_Implementation.md) — การ implement ใน OpenFOAM