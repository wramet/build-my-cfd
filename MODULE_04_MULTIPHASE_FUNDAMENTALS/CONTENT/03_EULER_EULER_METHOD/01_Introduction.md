# 01 - Euler-Euler Method: แนวคิดและหลักการ

บทนำแนวคิด Euler-Euler Method: แนวคิด ความจำเป็น และสถาปัตยกรรมโดยรวม

---

## Learning Outcomes

หลังจากศึกษาบทนี้ คุณควรจะสามารถ:

- **อธิบาย** แนวคิด interpenetrating continua และ volume averaging
- **แยกแยะ** ความแตกต่างระหว่าง Euler-Euler กับวิธี multiphase อื่นๆ
- **วิเคราะห์** ความเหมาะสมของ Euler-Euler สำหรับปัญหาที่ต่างกัน
- **อธิบาย** สถาปัตยกรรมโดยรวมของแนวทาง Euler-Euler ใน OpenFOAM

---

## Knowledge Tables

| Concept | Definition | Context |
|---------|------------|---------|
| **Interpenetrating Continua** | เฟสทั้งสองถูกพิจารณาเป็น continuum ที่ซ้อนทับกันในปริมาตรเดียว | Euler-Euler เฉพาะ |
| **Volume Fraction (α)** | สัดส่วนของปริมาตรที่ครอบครองโดยเฟสหนึ่งๆ ในแต่ละเซลล์ | 0 ≤ α ≤ 1, Σα = 1 |
| **Volume Averaging** | เทคนิคการถ่วงน้ำหนักคุณสมบัติตาม volume fraction | พื้นฐานการสร้างสมการ |
| **Shared Pressure** | ทุกเฟสใช้ pressure field เดียวกัน | ลดความซับซ้อน |
| **Interphase Coupling** | การแลกเปลี่ยนโมเมนตัมระหว่างเฟสผ่านแรง interphase | ต้องใช้ closure models |

---

## 1. What is Euler-Euler Method?

### 1.1 แนวคิดพื้นฐาน

**Euler-Euler Method** เป็นแนวทางการจำลอง multiphase flow ที่พิจารณา **ทุกเฟสเป็น continuum** ที่ซ้อนทับกัน (interpenetrating)

```
┌─────────────────────────────────────┐
│          Control Volume             │
│  ┌─────────────────────────────┐   │
│  │    α₁ = 0.3    α₂ = 0.7     │   │
│  │    (Phase 1)    (Phase 2)   │   │
│  │                             │   │
│  │   u₁(x,y,z)   u₂(x,y,z)    │   │
│  │                             │   │
│  │   Both coexist everywhere!  │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

**จุดสำคัญ:**
- ไม่ใช่ "either/or" (มีเฟสเดียวในแต่ละจุด) → เป็น **"both/and"**
- แต่ละเฟสมี **velocity field** ของตัวเอง: $\mathbf{u}_1(\mathbf{x},t), \mathbf{u}_2(\mathbf{x},t)$
- Volume fraction $\alpha_k(\mathbf{x},t)$ บอกสัดส่วนของแต่ละเฟส

### 1.2 Volume Averaging

พื้นฐานของ Euler-Euler คือ **volume averaging** เหนือ control volume $V$:

$$\alpha_k = \frac{V_k}{V}$$

**ข้อจำกัด:**
$$\sum_k \alpha_k = 1 \quad \text{(เต็มปริมาตรเสมอ)}$$

$$0 \leq \alpha_k \leq 1$$

---

## 2. Why Use Euler-Euler?

### 2.1 แนวทางอื่นๆ vs Euler-Euler

| Method | Phase Treatment | Scale | Cost | Interface |
|--------|----------------|-------|------|-----------|
| **Euler-Euler** | Both continuum | Averaged | Moderate | Modeled |
| **Euler-Lagrange** | Continuous + particles | Individual | High | Resolved |
| **VOF** | Interface tracking | Resolved | Mesh-dependent | Sharp |

### 2.2 ข้อดีของ Euler-Euler

✅ **เหมาะกับระบบที่มี dispersed phase หนาแน่น**
- Bubbles หลายๆ อันในหนึ่งเซลล์
- Particles จำนวนมาก

✅ **มีประสิทธิภาพดีสำหรับ steady-state**
- Averaged nature = ไม่ต้อง resolve ทุก interface

✅ **จัดการกับหลายเฟสได้**
- N-phase สำหรับ multiphaseEulerFoam

### 2.3 ข้อเสีย/ข้อจำกัด

⚠️ **ต้องการ closure models**
- Interphase forces (drag, lift, etc.)
- Turbulence models
- Granular models (ถ้ามี particles)

⚠️ **สูญเสียข้อมูล local**
- Averaging ทำให้ wake, boundary layers ระหว่างเฟสหายไป
- ต้องใช้ models แทน

---

## 3. When to Use Euler-Euler?

### 3.1 เหมาะสมที่สุดสำหรับ:

| Application | Characteristic | Why EE? |
|-------------|----------------|---------|
| **Bubbly flow** | Bubbles เล็ก, จำนวนมาก, กระจาย | α ≈ 0.2-0.4, many per cell |
| **Fluidized beds** | Particles หนาแน่น, มีการเคลื่อนที่ | Granular models available |
| **Bubble columns** | Industrial reactors | Averaged flow sufficient |
| **Sediment transport** | Particles + liquid | Moderate cost vs DNS |

### 3.2 ไม่เหมาะสมสำหรับ:

| Application | Better Alternative | Why? |
|-------------|-------------------|------|
| **Sharp interfaces** | VOF | EE smears interface |
| **Dilute particles** | Lagrangian | EE เสีย cost เปล่าๆ |
| **Drop breakup** | VOF/Lagrangian | EE ไม่ resolve morphology |
| **Free surface flows** | VOF | EE เฉลี่ย interface จนไม่ชัด |

---

## 4. High-Level Architecture

### 4.1 สถาปัตยกรรม Euler-Euler

```mermaid
flowchart TB
    A[Volume Averaging] --> B[Transport Equations per Phase]
    B --> C[Continuity: ∂(αₖρₖ)/∂t + ...]
    B --> D[Momentum: ∂(αₖρₖuₖ)/∂t + ...]
    
    C --> E[Shared Pressure Field]
    D --> F[Interphase Forces Mₖ]
    
    F --> G[Drag Models]
    F --> H[Lift Models]
    F --> I[Virtual Mass]
    F --> J[Turbulent Dispersion]
    
    E --> K[Momentum Closure]
    F --> K
    
    K --> L[PIMPLE Algorithm]
    L --> M[Converged Solution]
    
    style A fill:#e1f5ff
    style E fill:#ffe1e1
    style F fill:#ffe1e1
    style K fill:#fff4e1
```

### 4.2 คอมโพเนนต์หลัก

**1. Transport Equations (ต่อเฟส)**
- Continuity: สมหุุน αₖρₖ
- Momentum: สมหุุน αₖρₖuₖ

**2. Shared Pressure**
- ทุกเฟสใช้ pressure เดียวกัน
- Pressure equation จาก **mixture continuity**

**3. Interphase Coupling**
- แรง Mₖ คือ sum ของ drag, lift, VM, TD
- Couple momentum equations ของทุกเฟส

**4. Closure Models**
- Drag coefficient functions
- Turbulence (k-ε per phase or mixture)
- Granular (ถ้ามี solids)

---

## 5. Euler-Euler in OpenFOAM

### 5.1 Solvers หลัก

| Solver | Phases | Use Cases |
|--------|--------|-----------|
| `twoPhaseEulerFoam` | 2 | Bubbly flow, particle suspensions |
| `multiphaseEulerFoam` | N | Complex multiphase systems |

### 5.2 สถาปัตยกรรมโค้ด (Conceptual)

```
twoPhaseEulerFoam
├── phaseSystem
│   ├── phaseModel (dispersed, continuous)
│   ├── dragModels
│   ├── liftModels
│   └── virtualMassModels
├── turbulence
│   └── phaseCompressibleTurbulenceModel
└── solutionControl
    └── pimpleLoop
```

**การจัดการ pressure:**
```cpp
// Shared pressure field
volScalarField p
(
    IOobject
    (
        "p",
        runTime.timeName(),
        mesh,
        IOobject::MUST_READ,
        IOobject::AUTO_WRITE
    ),
    mesh
);

// Phases reference SAME p
phase1.lookup("p") == p;
phase2.lookup("p") == p;
```

---

## Concept Check

<details>
<summary><b>1. "Interpenetrating continua" หมายความว่าอะไร?</b></summary>

หมายความว่า **ทั้งสองเฟสอยู่ในพื้นที่เดียวกันได้** — volume fraction α บอกว่าแต่ละจุดมีเฟสไหนเท่าไหร่ (ไม่ใช่ either/or แบบ VOF)

</details>

<details>
<summary><b>2. Euler-Euler เหมาะกับ bubbly flow ทำไม?</b></summary>

เพราะ **bubbles เล็กและจำนวนมาก** → แต่ละเซลล์มีหลาย bubbles → ใช้ averaged approach ได้ (ไม่จำเป็นต้อง resolve ทุก bubble)

</details>

<details>
<summary><b>3. Euler-Euler vs VOF ต่างกันอย่างไร?</b></summary>

| Aspect | VOF | Euler-Euler |
|--------|-----|-------------|
| Interface | **Resolved** (sharp) | **Modeled** (smeared) |
| Tracking | γ = 0 or 1 | α = 0 to 1 (continuous) |
| Mesh | Fine near interface | Coarser OK |
| Cost | Higher | Moderate |

</details>

<details>
<summary><b>4. ทำไมต้องใช้ interphase force models?</b></summary>

เพราะ **volume averaging** ทำให้ข้อมูล local (wake, boundary layer รองๆ bubbles/particles) หายไป → ต้องใช้ empirical models แทน เช่น:
- Drag: $\mathbf{F}_D \propto (\mathbf{u}_c - \mathbf{u}_d)$
- Lift: $\mathbf{F}_L \propto (\mathbf{u}_c - \mathbf{u}_d) \times \boldsymbol{\omega}$

</details>

---

## Related Documents

| File | Content | Connection |
|------|---------|------------|
| **[00_Overview.md](00_Overview.md)** | Roadmap, LOs, KT list | Navigation hub |
| **[02_Governing_Equations.md](02_Governing_Equations.md)** | Continuity, momentum, closure models | Mathematical formulation |
| **[03_Implementation_Concepts.md](03_Implementation_Concepts.md)** | phaseProperties, dragModels, PIMPLE | OpenFOAM implementation |

---

## Quick Reference

| Aspect | Description |
|--------|-------------|
| **Core concept** | Interpenetrating continua with volume fractions |
| **Key variable** | $\alpha_k$: volume fraction of phase k |
| **Pressure** | Shared across all phases |
| **Coupling** | Interphase forces (drag, lift, VM, TD) |
| **Solvers** | twoPhaseEulerFoam, multiphaseEulerFoam |
| **Best for** | Bubbly flow, fluidized beds, bubble columns |
| **Not for** | Sharp interfaces (use VOF) |