# Mathematical Framework for Eulerian-Eulerian Multiphase Flow

**กรอบแนวคิดทางคณิตศาสตร์สำหรับการไหลแบบหลายเฟส (multiphase flows)** ใน OpenFOAM เป็นรากฐานสำหรับแนวทางการคำนวณแบบ Eulerian-Eulerian ผ่านกระบวนการเฉลี่ยที่เป็นระบบและความสัมพันธ์แบบปิด (closure relationships) เพื่อเปลี่ยนจากฟิสิกส์ระดับจุลภาคที่มีรอยต่อไม่ต่อเนื่อง ไปสู่สนามต่อเนื่องระดับมหภาคที่สามารถคำนวณได้

---

## 📊 กระบวนการเฉลี่ย (Averaging Procedures)

เนื่องจากการไหลแบบหลายเฟสในระดับจุลภาคประกอบด้วยพื้นผิวที่ขาดตอน (discontinuous interfaces) CFD จึงต้องการเทคนิคการเฉลี่ยที่เข้มงวดเพื่อสร้างสนามที่ต่อเนื่อง (continuous fields)

![[averaging_process_diagram.png]]
> `Scientific textbook diagram illustrating the volume averaging process in multiphase flow. Left side shows a microscopic view with distinct interfaces between liquid and gas bubbles. Right side shows the macroscopic continuum view.`

### 1. การเฉลี่ยเชิงปริมาตร (Volume Averaging)
สำหรับปริมาณใดๆ $\phi$ ในเฟส $k$ ตัวดำเนินการเฉลี่ยเชิงปริมาตรถูกนิยามดังนี้:
$$\langle \phi \rangle_k = \frac{1}{V_k} \int_{V_k} \phi \, \mathrm{d}V$$ 
โดยที่ $V_k$ คือปริมาตรชั่วขณะที่เฟส $k$ ครอบครองภายในปริมาตรเฉลี่ย $V$

### 2. การเฉลี่ยตามเฟส (Phase Averaging)
เชื่อมโยงปริมาณเฉลี่ยภายในเฟสเข้ากับกรอบอ้างอิงของส่วนผสม (mixture frame):
$$\bar{\phi}_k = \frac{1}{V} \int_{V_k} \phi \, \mathrm{d}V = \alpha_k \langle \phi \rangle_k$$ 
โดยที่ $\alpha_k = \frac{V_k}{V}$ คือสัดส่วนปริมาตร (volume fraction)

### 3. การเฉลี่ยตามเวลา (Temporal Averaging)
สำหรับการไหลที่มีความปั่นป่วน (Turbulent flows):
$$\tilde{\phi}_k = \frac{1}{\Delta t} \int_{t}^{t+\Delta t} \phi_k(\mathbf{x},\tau) \, \mathrm{d}\tau$$ 

---

## ⚖️ กฎการอนุรักษ์ในรูปแบบที่เฉลี่ยแล้ว (Conservation Laws)

### 1. การอนุรักษ์มวล (Continuity Equation)
$$\frac{\partial}{\partial t}(\alpha_k \rho_k) + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k) = \sum_{l \neq k} \dot{m}_{lk}$$ 

**การวิเคราะห์ทีละเทอม:**
- **Temporal term:** การสะสมหรือลดลงของมวลในจุดนั้นๆ
- **Convective term:** ฟลักซ์มวลสุทธิเนื่องจากการเคลื่อนที่
- **Source term ($\dot{m}_{lk}$):** การถ่ายเทมวลระหว่างเฟส (เช่น การควบแน่น/ระเหย) โดยมีเงื่อนไข $\dot{m}_{lk} = -\dot{m}_{kl}$

### 2. การอนุรักษ์โมเมนตัม (Momentum Equation)
$$\frac{\partial}{\partial t}(\alpha_k \rho_k \mathbf{u}_k) + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k \mathbf{u}_k) = -\alpha_k \nabla p + \nabla \cdot (\alpha_k \boldsymbol{\tau}_k) + \alpha_k \rho_k \mathbf{g} + \mathbf{M}_k$$ 

**การวิเคราะห์เทอมแรง (Force Terms):**
- **Pressure gradient ($-\alpha_k \nabla p$):** แรงดันที่ถ่วงน้ำหนักด้วยสัดส่วนเฟส
- **Viscous stress ($\boldsymbol{\tau}_k$):** สำหรับของไหลนิวตัน: $\boldsymbol{\tau}_k = \mu_k [\nabla \mathbf{u}_k + (\nabla \mathbf{u}_k)^T] - \frac{2}{3} \mu_k (\nabla \cdot \mathbf{u}_k) \mathbf{I}$
- **Interphase Transfer ($\mathbf{M}_k$):** แรงที่เกิดจากการปฏิสัมพันธ์ระหว่างเฟส

### 3. การอนุรักษ์พลังงาน (Energy Equation)
$$\frac{\partial}{\partial t}(\alpha_k \rho_k h_k) + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k h_k) = \alpha_k \frac{\mathrm{d}p_k}{\mathrm{d}t} + \nabla \cdot (\alpha_k \kappa_k \nabla T_k) + Q_k$$ 

---

## 🔧 แบบจำลองการปิด (Closure Models)

### 1. การถ่ายโอนโมเมนตัมระหว่างเฟส ($\mathbf{M}_k$)
$$\mathbf{M}_k = \sum_{l \neq k} \mathbf{K}_{kl} (\mathbf{u}_l - \mathbf{u}_k) + \mathbf{F}_k^{\text{lift}} + \mathbf{F}_k^{\text{vm}} + \mathbf{F}_k^{\text{disp}}$$ 

- **Drag Force ($\mathbf{K}_{kl}$):** แรงต้านหลักระหว่างเฟส
- **Lift Force ($\mathbf{F}_L$):** แรงแนวขวางเนื่องจากความเฉือน: $\mathbf{F}_{L,k} = C_L \rho_c \alpha_k (\mathbf{u}_k - \mathbf{u}_c) \times (\nabla \times \mathbf{u}_c)$
- **Virtual Mass ($\mathbf{F}_{VM}$):** แรงเนื่องจากการเร่งความเร็วสัมพัทธ์: $\mathbf{F}_{VM,k} = C_{VM} \rho_c \alpha_k (\frac{\mathrm{D}\mathbf{u}_c}{\mathrm{D}t} - \frac{\mathrm{D}\mathbf{u}_k}{\mathrm{D}t})$
- **Turbulent Dispersion ($\mathbf{F}_{TD}$):** การกระจายตัวเนื่องจากความปั่นป่วน: $\mathbf{F}_{TD,k} = -C_{TD} \rho_c k_{t,c} \nabla \alpha_k$

### 2. ความเค้นความปั่นป่วน (Turbulent Stress)
ใช้แบบจำลอง **Eddy Viscosity**:
$$\boldsymbol{\tau}_k^{\text{turb}} = \mu_{t,k} [\nabla \mathbf{u}_k + (\nabla \mathbf{u}_k)^T] - \frac{2}{3}\rho_k k_k \mathbf{I}$$ 

สำหรับ $k$-$\epsilon$ model ในแต่ละเฟส:
$$\frac{\partial (\alpha_k \rho_k k_k)}{\partial t} + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k k_k) = P_{k,k} - \alpha_k \rho_k \epsilon_k + \nabla \cdot [\alpha_k \frac{\mu_{t,k}}{\sigma_k} \nabla k_k] + S_{k,\text{int}}$$ 

---

## 🔢 ข้อพิจารณาเชิงตัวเลข (Numerical Considerations)

| คุณสมบัติ | ข้อกำหนด | ความสำคัญ |
|------------|------------|------------|
| **Boundedness** | $0 \leq \alpha_k \leq 1$ | ป้องกันค่าติดลบหรือเกิน 1 ซึ่งไม่ถูกต้องทางฟิสิกส์ |
| **Continuity constraint** | $\sum \alpha_k = 1$ | รักษาสัดส่วนปริมาตรรวม |
| **Stiffness** | Implicit coupling | แรงระหว่างเฟสที่รุนแรงต้องการการจัดการแบบ implicit เพื่อความเสถียร |
| **MULES** | Explicit/Semi-implicit | สกีมพิเศษใน OpenFOAM สำหรับแก้สมการ $\alpha$ |

---

## 💻 การนำไปใช้ใน OpenFOAM (C++ Implementation)

```cpp
// Phase continuity equation
fvScalarMatrix alphaEqn
(
    fvm::ddt(alpha, rho)
  + fvm::div(alphaPhi, rho)
 ==
    fvOptions(alpha, rho)
);

// Momentum equation for phase k
fvVectorMatrix UEqn
(
    fvm::ddt(alpha, rho, U)
  + fvm::div(alphaPhi, rho, U)
 ==
    -alpha*fvc::grad(p)
  + fvc::div(alpha*tau)
  + alpha*rho*g
  + interfacialMomentumTransfer // Kd*(U_other - U)
);
```

กรอบแนวคิดนี้ช่วยให้เราสามารถจำลองพฤติกรรมการไหลแบบหลายเฟสที่ซับซ้อนได้โดยไม่ต้องติดตามพื้นผิวของทุกฟองอากาศหรือทุกหยดของเหลว ทำให้สามารถประยุกต์ใช้ในงานวิศวกรรมระดับอุตสาหกรรมได้อย่างมีประสิทธิภาพ