# การเชื่อมโยงหลายฟิสิกส์ (Multiphysics Coupling)

> [!INFO] ภาพรวม
> การจำลอง Multiphysics ใน OpenFOAM เป็นการรวมฟิสิกส์หลายด้านเข้าด้วยกัน เช่น การไหลของไหล (fluid dynamics) การเสียรูปของโครงสร้าง (structural mechanics) การถ่ายเทความร้อน (heat transfer) และปฏิกิริยาเคมี (chemical reactions) เพื่อสร้างแบบจำลองที่สมจริงของระบบทางวิศวกรรมที่ซับซ้อน

---

## 🤝 1. Fluid-Structure Interaction (FSI)

FSI คือการศึกษาปฏิสัมพันธ์ระหว่างการไหลของของไหลและการเสียรูปของโครงแข็ง ซึ่งมีความสำคัญอย่างยิ่งในการออกแบบโครงสร้างทางวิศวกรรม เช่น อากาศยาน สะพาน และใบพัดกังหัน

### 1.1 แนวทางการเชื่อมโยง (Coupling Strategies)

#### **Weak (Partitioned) Coupling**

แก้สมการของไหลและของแข็งแยกกันทีละขั้นเวลา วิธีนี้ง่ายต่อการนำไปใช้แต่อาจเสี่ยงต่อความไม่เสถียร:

```cpp
// Pseudocode for weak coupling
for each time step:
    solve fluid equations (get fluid forces)
    transfer forces to structure
    solve structural equations
    update fluid mesh based on structural displacement
```

#### **Strong (Implicit) Coupling**

วนซ้ำภายในหนึ่งก้าวเวลาจนกว่าแรงและระยะขยับที่รอยต่อจะสมดุลกัน มีความเสถียรสูงกว่าแต่ซับซ้อนกว่า:

```cpp
// Pseudocode for strong coupling
for each time step:
    repeat until convergence:
        solve fluid equations
        transfer forces to structure
        solve structural equations
        update fluid mesh
        check convergence
```

| แนวทาง | คุณสมบัติ | ข้อดี | ข้อเสีย |
|---------|---------|--------|---------|
| **Partitioned** | Solver แยกสำหรับโดเมนของไหลและโครงสร้าง | ใช้ solver เฉพาะที่มีอยู่ | อาจประสบปัญหาความไม่เสถียร |
| **Monolithic** | Solver เดียวสำหรับระบบที่จับคู่กัน | ความเสถียรภาพเชิงตัวเลขดีกว่า | การนำไปใช้ซับซ้อนกว่า |

### 1.2 เงื่อนไขที่อินเทอร์เฟซ (Interface Conditions)

ที่ส่วนต่อประสานระหว่างของไหลและของแข็ง $\Gamma_{fsi}$:

#### **Kinematic Condition**
ความเร็วของไหลที่ผนังต้องเท่ากับความเร็วของโครงสร้าง:
$$\mathbf{u}_f = \frac{\partial \mathbf{d}_s}{\partial t}$$

#### **Dynamic Condition**
ความดันและความเค้นของไหลต้องเท่ากับภาระที่กระทำต่อของแข็ง:
$$\boldsymbol{\sigma}_f \cdot \mathbf{n}_f = \boldsymbol{\sigma}_s \cdot \mathbf{n}_s$$

### 1.3 การนำไปใช้ใน OpenFOAM

OpenFOAM ให้ความสามารถด้าน FSI ผ่าน:

- **`solidDisplacementFoam`** - สำหรับกลศาสตร์โครงสร้าง
- **`chtMultiRegionFoam`** - สำหรับการจำลองหลายบริเวณ
- **ไลบรารีการจับคู่** - สำหรับ solver โครงสร้างภายนอก
- **การบิดเบือน Mesh** - สำหรับขอบเขตที่เคลื่อนที่ได้

#### การตั้งค่า FSI ใน OpenFOAM

```cpp
regions
{
    fluid
    {
        solver          pimpleFoam;
        ...
    }

    solid
    {
        solver          solidDisplacementFoam;
        ...
    }
}

interface
{
    type            regionCoupledWall;
    ...
}
```

### 1.4 ข้อควรพิจารณาด้านความเสถียร

ความเสถียรภาพของ FSI ต้องการ:

- **การเลือก Time step ที่เหมาะสม** - เงื่อนไข CFL สำหรับทั้งสองโดเมน
- **การถ่ายโอนมวลและโมเมนตัม** ที่สอดคล้องกัน
- **การหน่วงเชิงตัวเลข** สำหรับโหมดความถี่สูง
- **การจัดการความไม่เป็นเชิงเส้นทางเรขาคณิต** อย่างระมัดระวัง

เทคนิค **Aitken relaxation** ช่วยให้มั่นใจในการลู่เข้าของการวนซ้ำที่ส่วนต่อประสาน:

$$\lambda^{n+1} = \lambda^n + \omega \frac{\langle \mathbf{r}^n, \mathbf{r}^{n-1} - \mathbf{r}^n \rangle}{\|\mathbf{r}^{n-1} - \mathbf{r}^n\|^2}$$

โดยที่ $\mathbf{r}^n$ คือ interface residual ที่การวนซ้ำครั้งที่ $n$

---

## 🌡️ 2. Conjugate Heat Transfer (CHT)

**Conjugate Heat Transfer (CHT)** สร้างแบบจำลองการถ่ายเทความร้อนระหว่างโดเมนของแข็งและของไหล ซึ่งเป็นสิ่งสำคัญในระบบ heat exchanger การระบายความร้อนอิเล็กทรอนิกส์ และเครื่องยนต์

### 2.1 เงื่อนไขที่อินเทอร์เฟซ

ที่ส่วนต่อประสานของของไหลและของแข็ง $\Gamma_{fs}$:

#### **Temperature Continuity**
อุณหภูมิต้องต่อเนื่องกันที่ผิวสัมผัส:
$$T_{fluid} = T_{solid}$$

#### **Heat Flux Continuity**
ฟลักซ์ความร้อนต้องสมดุลกัน:
$$-k_{fluid}(\nabla T \cdot \mathbf{n})_{fluid} = -k_{solid}(\nabla T \cdot \mathbf{n})_{solid}$$

### 2.2 สมการพลังงาน

#### **Fluid Domain**
$$\rho_{fluid} c_{p,fluid} \frac{\partial T_{fluid}}{\partial t} + \rho_{fluid} c_{p,fluid} \mathbf{u} \cdot \nabla T_{fluid} = k_{fluid} \nabla^2 T_{fluid} + Q_{fluid}$$

#### **Solid Domain**
$$\rho_{solid} c_{p,solid} \frac{\partial T_{solid}}{\partial t} = k_{solid} \nabla^2 T_{solid} + Q_{solid}$$

### 2.3 การนำไปใช้ใน OpenFOAM

CHT มีให้ใช้งานผ่าน **`chtMultiRegionFoam`**:

```cpp
regions
{
    fluid
    {
        solver          buoyantPimpleFoam;
        ...
    }

    solid
    {
        solver          laplacianFoam;
        ...
    }
}

interface
{
    type            regionCoupledWall;
    ...
}
```

> [!TIP] **หมายเหตุ:** OpenFOAM ใช้ **Robin boundary condition** เพื่อให้การกำหนดรูปแบบส่วนต่อประสานที่เป็นหนึ่งเดียว:
> $$k_f \frac{\partial T_f}{\partial n} + h_{\text{int}}(T_f - T_s) = 0$$
> โดยที่ $h_{\text{int}}$ คือค่าสัมประสิทธิ์การถ่ายเทความร้อนที่ส่วนต่อประสาน

### 2.4 การประยุกต์ใช้

CHT มีประสิทธิภาพสำหรับ:

- **การระบายความร้อนอิเล็กทรอนิกส์** (Electronics cooling)
- **Heat exchangers**
- **การทำความเย็นใบพัด turbine** (Turbine blade cooling)
- **การทำความร้อนอาคาร** (Building heating)
- **กระบวนการเชื่อม** (Welding processes)

---

## 🔥 3. การจำลองระบบปฏิกิริยาเคมีและการเผาไหม้ (Reacting Flows & Combustion)

การจำลองการไหลที่มีปฏิกิริยาเคมีและการเผาไหม้ต้องการการเชื่อมโยงระหว่าง:
- **Species Transport** - การขนส่งสารเคมีแต่ละชนิด
- **Finite-rate Chemistry** - ปฏิกิริยาที่มีอัตราความเร็วแตกต่างกัน
- **Turbulence-Chemistry Interaction (TCI)** - เช่น แบบจำลอง EDC (Eddy Dissipation Concept)

### 3.1 สมการขนส่งสาร (Species Transport Equation)

สำหรับ species $i$:

$$\frac{\partial (\rho Y_i)}{\partial t} + \nabla \cdot (\rho Y_i \mathbf{u}) = -\nabla \cdot \mathbf{J}_i + R_i$$

โดยที่:
- $Y_i$ = มวลส่วนของ species i
- $\mathbf{J}_i$ = flux การแพร่ของ species i
- $R_i$ = อัตราการเกิดปฏิกิริยาของ species i

### 3.2 แบบจำลองปฏิกิริยาเคมี

#### **Finite-Rate Chemistry**

อัตราปฏิกิริยาถูกกำหนดโดย kinetic เคมี:

$$R_i = M_i \sum_{j=1}^{N_r} \left( \nu_{i,j}'' - \nu_{i,j}' \right) k_{f,j} \prod_{k=1}^{N_s} [C_k]^{\nu_{k,j}'}$$

โดยที่:
- $\nu_{i,j}'$, $\nu_{i,j}''$ = สัมประสิทธิ์ stoichiometric
- $k_{f,j}$ = ค่าคงที่อัตราปฏิกิริยา
- $[C_k]$ = ความเข้มข้นของ species k

#### **Eddy Dissipation Concept (EDC)**

แบบจำลอง EDC จัดการกับ Turbulence-Chemistry Interaction:

$$R_i = \frac{\rho \varepsilon}{k} \min \left( R_{i,\text{kinetic}}, R_{i,\text{mixing}} \right)$$

### 3.3 การนำไปใช้ใน OpenFOAM

ใช้ Solver ตระกูล **`reactingFoam`**:

```cpp
 reactingFoam
{
    // สมการการขนส่ง species
    species
    {
        O2
        {
            transport        UNIFAQ;
            thermo            hConst;
        }
        N2
        {
            transport        UNIFAQ;
            thermo            hConst;
        }
        ...
    }

    // กลไกปฏิกิริยา
    reactions
    {
        type            irreversible;
        reaction         "H2 + 0.5 O2 => H2O";
        A               1.8e8;
        beta            0.0;
        Ta              4680;
    }
}
```

### 3.4 การประยุกต์ใช้

- **ห้องเผาไหม้ Gas turbine**
- **เตาอุตสาหกรรม**
- **เครื่องยนต์สันดาปภายใน**
- **การสร้างแบบจำลองการลุกลามของไฟป่า**

---

## ⚡ 4. เทคนิคการเชื่อมโยงขั้นสูง (Advanced Coupling Techniques)

### 4.1 Partitioned vs Monolithic Approaches

| แนวทาง | คุณสมบัติ | ข้อดี | ข้อเสีย |
|---------|---------|--------|---------|
| **Partitioned** | Sequential solving | Modular, existing solvers | Convergence issues |
| **Monolithic** | Simultaneous solving | Robust, stable | Complex implementation |
| **Quasi-direct** | Hybrid approach | Balanced performance | Moderate complexity |

### 4.2 การเร่งการลู่เข้า (Convergence Acceleration)

#### **Aitken Relaxation**

ช่วยปรับปรุงการลู่เข้าสำหรับ partitioned coupling:

$$\lambda^{n+1} = \lambda^n + \omega^n \mathbf{r}^n$$

$$\omega^n = \omega^{n-1} \frac{\langle \mathbf{r}^{n-1} - \mathbf{r}^n, \mathbf{r}^n \rangle}{\|\mathbf{r}^{n-1} - \mathbf{r}^n\|^2}$$

#### **Interface Quasi-Newton (IQN)**

วิธีการที่มีประสิทธิภาพสูงสำหรับ FSI ที่มีความแข็งแรง:

$$\mathbf{J}^{-1} \approx \mathbf{V}(\mathbf{W}^T \mathbf{V})^{-1} \mathbf{W}^T$$

### 4.3 เทคนิคการโอนถ่ายข้อมูล (Data Transfer Techniques)

#### **Conservative Interpolation**

รักษาการอนุรักษ์พลังงานและโมเมนตัม:

$$\int_{\Gamma_f} \mathbf{F}_f \cdot d\mathbf{A}_f = \int_{\Gamma_s} \mathbf{F}_s \cdot d\mathbf{A}_s$$

#### **Mortar Methods**

ใช้ weighted residuals สำหรับการโอนถ่ายข้อมูลที่แม่นยำ:

$$\int_{\Gamma} \mathbf{w} \cdot (\mathbf{u}_f - \mathbf{u}_s) d\Gamma = 0$$

---

## 🚀 5. บทสรุป: อนาคตของ CFD Multiphysics

เทคโนโลยีขั้นสูงเหล่านี้กำลังทำให้ CFD กลายเป็นเครื่องมือแบบ **"Digital Twin"** ที่สามารถ:

### 5.1 ความสามารถในการทำนาย

1. **ทำนายอายุการใช้งานของเครื่องจักร** - ผ่าน FSI และ Erosion
2. **ปรับปรุงประสิทธิภาพพลังงาน** - ผ่าน Optimization
3. **พยากรณ์สถานะแบบเรียลไทม์** - ผ่าน ML Integration

### 5.2 แนวโน้มในอนาคต

```mermaid
flowchart LR
    A[Current CFD] --> B[Digital Twins]
    B --> C[Real-time Simulation]
    C --> D[AI-Enhanced Physics]
    D --> E[Quantum CFD]
```
> **Figure 1:** วิวัฒนาการของการจำลองพลศาสตร์ของไหลเชิงคำนวณ (CFD Evolution) จากปัจจุบันไปสู่อนาคต โดยมุ่งเน้นการบูรณาการเทคโนโลยี Digital Twins การจำลองแบบเรียลไทม์ การใช้ปัญญาประดิษฐ์ (AI) เพื่อเสริมสร้างความแม่นยำทางฟิสิกส์ และก้าวไปสู่การประมวลผลแบบควอนตัม (Quantum CFD) เพื่อรองรับปัญหาที่มีความซับซ้อนมหาศาลความปลอดภัยทางฟิสิกส์ไม่ส่งผลกระทบต่อความเร็วในการจำลอง ผ่านการใช้พลังของ C++ Template Metaprogramming ในการตรวจสอบความสอดคล้องทางมิติทั้งหมดที่ขั้นตอนการคอมไพล์โปรแกรมเพียงครั้งเดียว

> [!INFO] **การพัฒนาในอนาคต**
> - **Machine Learning Integration** - การใช้ Neural Networks สำหรับ turbulence modeling
> - **Quantum Computing** - อัลกอริทึม HHL สำหรับระบบเชิงเส้นควอนตัม
> - **Digital Twin Technology** - การเชื่อมโยงเซ็นเซอร์ทางกายภาพกับ CFD

---

## 📚 ตัวอย่างการนำไปประยุกต์ใช้

### ตัวอย่าง 1: การไหลผ่านใบพัดที่มีการเสียรูป (Flow Through Flexible Blades)

```cpp
// การตั้งค่า FSI สำหรับใบพัด
applications
{
    // Fluid domain
    fluid
    {
        solver          pimpleFoam;
        rho             rho [1 -3 0 0 0] 1000;
        nu              nu [0 2 -1 0 0] 1e-6;
    }

    // Solid domain
    solid
    {
        solver          solidDisplacementFoam;
        rho             rho [1 -3 0 0 0] 7850;
        E               E [1 -1 -2 0 0] 2e11;
        nu              nu [0 0 0 0 0] 0.3;
    }
}
```

### ตัวอย่าง 2: Heat Exchanger พร้อม CHT

```cpp
// การตั้งค่า CHT สำหรับ heat exchanger
regions
{
    hotFluid
    {
        type            volScalarField;
        initialValue    350; // K
        boundaryField
        {
            interface
            {
                type            externalWallHeatFlux;
                mode            coefficient;
                h               uniform 1000;
                Ta              uniform 300;
            }
        }
    }

    coldFluid
    {
        type            volScalarField;
        initialValue    300; // K
    }

    solidWall
    {
        type            solidRegion;
        thermo           type constant;
        k               uniform 50; // W/mK
    }
}
```

---

**จบเนื้อหาโมดูล Single Phase Flow**
