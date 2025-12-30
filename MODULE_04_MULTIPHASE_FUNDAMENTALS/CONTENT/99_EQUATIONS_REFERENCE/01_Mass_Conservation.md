# Mass Conservation Equations

สมการอนุรักษ์มวลสำหรับ Multiphase Flow | Mass Conservation Equations for Multiphase Flow

---

## Learning Objectives | วัตถุประสงค์การเรียนรู้

After completing this section, you should be able to:

- **Understand** the mathematical foundation of mass conservation in multiphase flows
- **Distinguish** between different forms of mass conservation equations and when to apply each
- **Explain** the volume fraction constraint and its numerical implementation
- **Apply** the appropriate equation form for specific multiphase scenarios (VOF, Euler-Euler, with/without mass transfer)
- **Implement** mass conservation equations in OpenFOAM with proper numerical treatment

หลังจากการเรียนตอนนี้ คุณควรจะสามารถ:
- เข้าใจหลักการคณิตศาสตร์ของสมการอนุรักษ์มวลในการไหลแบบหลายเฟส
- แยกแยะรูปแบบต่างๆ ของสมการอนุรักษ์มวลและวิธีการเลือกใช้
- อธิบายข้อจำกัดของปริมาตรและการนำไปใช้ในการคำนวณเชิงตัวเลข
- นำรูปสมการที่เหมาะสมไปใช้กับสถานการณ์การไหลแบบหลายเฟสที่แตกต่างกัน
- นำสมการอนุรักษ์มวลไปใช้ใน OpenFOAM อย่างถูกต้อง

---

## Overview | ภาพรวม

### What is Mass Conservation in Multiphase Flow? | สมการอนุรักษ์มวลคืออะไร?

**Mass conservation** states that mass cannot be created or destroyed, only transformed between phases. In multiphase flows, we must track mass for **each phase separately** while ensuring that **all phases together fill the entire volume**.

**กฎข้อที่หนึ่งของอนุรักษ์มวล** ระบุว่ามวลไม่สามารถถูกสร้างหรือทำลายได้ แต่สามารถเปลี่ยนสถานะระหว่างเฟสได้ ในการไหลแบบหลายเฟส เราต้องติดตามมวลของ **แต่ละเฟสแยกกัน** ในขณะที่รับประกันว่า **ทุกเฟสรวมกันเติมเต็มปริมาตรทั้งหมด**

### Why Do We Need Different Forms? | ทำไมต้องมีหลายรูปแบบ?

Different multiphase scenarios require different mathematical formulations:

| Scenario | Why Different? | ใช้กรณีใด |
|----------|----------------|-------------|
| **General compressible flow** | Density varies significantly — must track full ρα product | การไหลที่ความหนาแน่นเปลี่ยนแปลงมาก |
| **Incompressible liquids** | ρ ≈ constant — can simplify by dividing out ρ | ของเหลวที่ไม่อัดตัวได้ |
| **VOF method** | Sharp interface needs compression term — prevents smearing | อินเตอร์เฟซที่ชัดเจนต้องการเทอม compression |
| **Without mass transfer** | No phase change — source term = 0 | ไม่มีการเปลี่ยนสถานะเฟส |

### How is it Implemented? | การนำไปใช้งาน

1. **Solve** α equation for each phase
2. **Normalize** all α to ensure Σα = 1
3. **Apply** interface compression (VOF only)
4. **Enforce** bounds: 0 ≤ α ≤ 1

---

## 1. General Form | รูปแบบทั่วไป

### What is This Form? | รูปแบบนี้คืออะไร?

The most complete form of mass conservation, applicable to **all multiphase flows** including compressible flows with mass transfer:

$$\frac{\partial(\alpha_k \rho_k)}{\partial t} + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k) = \sum_{l \neq k} \dot{m}_{lk}$$

### When to Use It? | เมื่อไหร่ควรใช้?

- **Compressible flows** where ρ varies significantly
- **With phase change** (evaporation, condensation, reaction)
- **High-speed gas-liquid flows** with significant density variations
- **Euler-Euler simulations** with separate velocity fields per phase

### How Does it Differ? | แตกต่างจากรูปแบบอื่นอย่างไร?

| Aspect | General Form | ความแตกต่าง |
|--------|--------------|---------------|
| Tracks | α × ρ (full product) | ติดตามค่ารวม |
| Complexity | Most complete | สมบูรณ์ที่สุด |
| Computation | Most expensive | ใช้เวลาคำนวณมากที่สุด |
| Applicability | All scenarios | ใช้ได้ทุกกรณี |

### Term-by-Term Breakdown | การแยกส่วนของสมการ

| Mathematical Term | Physical Meaning | ความหมายทางฟิสิกส์ | OpenFOAM Implementation |
|-------------------|------------------|----------------------|-------------------------|
| $\frac{\partial(\alpha_k \rho_k)}{\partial t}$ | **Mass storage** — rate of mass accumulation in cell | การสะสมมวลในเซลล์ | `fvm::ddt(alpha, rho)` |
| $\nabla \cdot (\alpha_k \rho_k \mathbf{u}_k)$ | **Convection** — mass flux across cell faces | การไหลของมวลผ่านหน้าเซลล์ | `fvm::div(phi, alpha*rho)` |
| $\sum_{l \neq k} \dot{m}_{lk}$ | **Mass transfer** — source from phase change | แหล่งกำเนิดจากการเปลี่ยนเฟส | `massTransferSource` |

### Practical Example | ตัวอย่างการใช้งาน

**Scenario:** Steam condensation in a cooling pipe

```cpp
// Phase k = liquid water receiving mass from steam
dimensionedScalar m_lk("m_lk", dimMass/dimTime, condensationRate);

fvScalarMatrix alphaKEqn
(
    fvm::ddt(alpha, rho)
  + fvm::div(phi, alpha*rho)
 ==
    m_lk  // Mass source from condensation
);
```

---

## 2. Volume Fraction Constraint | ข้อจำกัดของปริมาตรเศษส่วน

### What is This Constraint? | ข้อจำกัดนี้คืออะไร?

$$\sum_k \alpha_k = 1$$

All phases must **completely fill** the computational domain — no voids or overlaps allowed.

### Why is it Critical? | ทำไมสำคัญ?

| Reason | Explanation | คำอธิบาย |
|--------|-------------|-----------|
| **Physical reality** | Space cannot be empty or doubly-filled | ปริมาตรไม่สามารถว่างหรือซ้อนทับกันได้ |
| **Numerical stability** | Prevents runaway values | ป้องกันค่าที่เพิ่มขึ้นโดยไม่มีที่สิ้นสุด |
| **Conservation** | Ensures total mass consistent | รับประกันการอนุรักษ์มวลโดยรวม |

### How to Enforce It? | วิธีการบังคับใช้

```cpp
// After solving ALL phase equations
volScalarField sumAlpha = zeroAlpha;
forAll(phases, i)
{
    sumAlpha += phases[i];
}

forAll(phases, i)
{
    phases[i] /= max(sumAlpha, SMALL);  // Normalize
}
```

---

## 3. Incompressible Form | รูปแบบของไหลที่ไม่อัดตัวได้

### What is This Form? | รูปแบบนี้คืออะไร?

When ρₖ = **constant**, we can simplify by dividing through by ρₖ:

$$\frac{\partial \alpha_k}{\partial t} + \nabla \cdot (\alpha_k \mathbf{u}_k) = \frac{\dot{m}_k}{\rho_k}$$

### When to Use It? | เมื่อไหร่ควรใช้?

- **Liquid-liquid systems** (water-oil, acid-base)
- **Low-speed gas-liquid** where ρ ≈ constant
- **VOF simulations** of free surface flows
- **Microfluidics** with incompressible fluids

### How Does it Simplify Computation? | ทำให้การคำนวณง่ายขึ้นอย่างไร?

| Aspect | General Form | Incompressible Form | ประโยชน์ |
|--------|--------------|---------------------|----------|
| Variables | α × ρ | α only | ลดตัวแปร |
| Storage | 2 fields | 1 field | ประหยัดหน่วยความจำ |
| Operations | More multiplications | Fewer | คำนวณเร็วขึ้น |
| Stability | Condition-dependent | More robust | เสถียรกว่า |

### Practical Example | ตัวอย่างการใช้งาน

**Scenario:** Oil-water separation in a tank

```cpp
// Both phases: rho = constant
dimensionedScalar rhoOil("rhoOil", dimDensity, 800);
dimensionedScalar rhoWater("rhoWater", dimDensity, 1000);

// Oil phase equation (no mass transfer)
fvScalarMatrix alphaOilEqn
(
    fvm::ddt(alphaOil)
  + fvm::div(phi, alphaOil)
 ==
    zeroField  // No phase change
);
```

---

## 4. Form Without Mass Transfer | รูปแบบไม่มีการถ่ายเทมวล

### What is This Form? | รูปแบบนี้คืออะไร?

When **no phase change** occurs (ṁ = 0):

$$\frac{\partial \alpha_k}{\partial t} + \nabla \cdot (\alpha_k \mathbf{u}_k) = 0$$

### When to Use It? | เมื่อไหร่ควรใช้?

| Application | Why No Mass Transfer? | ทำไมไม่มีการถ่ายเทมวล |
|-------------|----------------------|--------------------------|
| **Free surface flows** | Single fluid, no phase change | ของไหลเดียว ไม่เปลี่ยนสถานะ |
| **Immiscible liquids** | No mixing between phases | ของเหลวไม่ผสมกัน |
| **Particle transport** | Solid particles, no phase change | อนุภาคของแข็ง ไม่เปลี่ยนสถานะ |
| **Slurry flows** | Suspended particles, no dissolution | อนุภาคลอยตัว ไม่ละลาย |

### Practical Example | ตัวอย่างการใช้งาน

**Scenario:** Dam break simulation (water + air)

```cpp
// interFoam-style VOF equation
fvScalarMatrix alphaEqn
(
    fvm::ddt(alpha)
  + fvm::div(phi, alpha)
 ==
    zeroField  // Source term = 0
);

alphaEqn.solve();

// Compression term applied separately
surfaceScalarField phic = mag(phi/mesh.magSf());
phic = min(interfaceCompression*phic, phic/max(alpha, scalar(1)-alpha));

surfaceScalarField alphaPhi = alphaEqn.flux();
alphaPhi += fvc::flux(-phic*interfaceAlpha*nHatf);
```

---

## 5. VOF Form with Interface Compression | รูปแบบ VOF พร้อม Interface Compression

### What is This Form? | รูปแบบนี้คืออะไร?

The VOF-specific form includes **artificial compression** to maintain sharp interfaces:

$$\frac{\partial \alpha}{\partial t} + \nabla \cdot (\alpha \mathbf{U}) + \nabla \cdot (\alpha(1-\alpha)\mathbf{U}_r) = 0$$

### Term Breakdown | การแยกส่วน

| Term | Purpose | หน้าที่ |
|------|---------|---------|
| $\frac{\partial \alpha}{\partial t}$ | Time evolution | การพัฒนาตามเวลา |
| $\nabla \cdot (\alpha \mathbf{U})$ | Standard convection | การพาคอนเวกชันปกติ |
| $\nabla \cdot (\alpha(1-\alpha)\mathbf{U}_r)$ | **Interface compression** | การบีบอัดอินเตอร์เฟซ |

### Why is Compression Needed? | ทำไมต้องมีการบีบอัด?

**Without compression →** interface smears over multiple cells  
**With compression →** interface stays sharp (typically 1-2 cells)

### How Does Compression Work? | การบีบอัดทำงานอย่างไร?

```cpp
// MULES or similar compression scheme
surfaceScalarField phiAlpha = fvc::flux(phi, alpha);

// Add compression flux
surfaceScalarField phiAlphaC
(
    "phiAlphaC",
    phiAlpha
  + fvc::flux
    (
        -fvc::flux(-phic*interfaceAlpha*nHatf),
        alpha,
        "flux(alpha)"
    )
);

// Apply boundedness
MULES::limit
(
    1.0/mesh.time().deltaT(),
    geometricOneField(),
    alpha,
    phi,
    phiAlphaC,
    zeroField(),
    zeroField(),
    1,
    0,
    3
);
```

### Practical Example | ตัวอย่างการใช้งาน

**Scenario:** Droplet impact on liquid surface

```cpp
// Compression coefficient
scalar cAlpha = 1.0;  // Typically 0.5-2.0

// Interface normal
surfaceVectorField nHatf = nHat & mesh.Sf();

// Compression velocity
surfaceScalarField phic = mag(phi/mesh.magSf());
phic = min(cAlpha*phic, phic/max(alpha, scalar(1) - alpha));

// Compressive flux
surfaceScalarField phiComp = phic*interfaceAlpha*nHatf;
```

---

## 6. OpenFOAM Implementation | การนำไปใช้ใน OpenFOAM

### Complete Solver Structure | โครงสร้าง Solver ทั้งหมด

```cpp
// =====================
// 1. Define Phase Fields
// =====================
volScalarField alpha1
(
    IOobject
    (
        "alpha.water",
        runTime.timeName(),
        mesh,
        IOobject::READ_IF_PRESENT,
        IOobject::AUTO_WRITE
    ),
    mesh,
    dimensionedScalar("alpha1", dimless, 0)
);

volScalarField alpha2 = scalar(1) - alpha1;

// =====================
// 2. Construct Mass Equation
// =====================
surfaceScalarField phi = fvc::interpolate(U) & mesh.Sf();

fvScalarMatrix alpha1Eqn
(
    fvm::ddt(alpha1)
  + fvm::div(phi, alpha1)
 ==
    massTransferSource  // Zero if no phase change
);

// =====================
// 3. Apply Interface Compression (VOF only)
// =====================
surfaceScalarField phiAlpha1 = alpha1Eqn.flux();

// Compression flux
surfaceScalarField phic = mag(phi/mesh.magSf());
surfaceScalarField phir = phic*interfaceAlpha*nHatf;

phiAlpha1 += fvc::flux(-phir);

// =====================
// 4. Solve with Boundedness
// =====================
MULES::explicitSolve
(
    geometricOneField(),
    alpha1,
    phi,
    phiAlpha1,
    zeroField(),
    zeroField(),
    1,    // maxAlpha
    0,    // minAlpha
    3     // nAlphaSubCycles
);

// =====================
// 5. Normalize
// =====================
alpha2 = scalar(1) - alpha1;

// =====================
// 6. Enforce Bounds
// =====================
alpha1.max(0);
alpha1.min(1);
alpha2.max(0);
alpha2.min(1);
```

### Key Implementation Considerations | ข้อควรพิจารณาสำคัญ

| Consideration | Best Practice | แนวปฏิบัติที่ดี |
|---------------|---------------|-----------------|
| **Time stepping** | Use adaptive time stepping with Co < 0.3 | ใช้เวลา adaptive กับ Co < 0.3 |
| **Mesh resolution** | Minimum 4-5 cells across interface | อย่างน้อย 4-5 เซลล์ข้ามอินเตอร์เฟซ |
| **Compression coefficient** | Start with cAlpha = 1.0 | เริ่มต้นด้วย cAlpha = 1.0 |
| **Under-relaxation** | Essential for stability | จำเป็นสำหรับความเสถียร |

---

## 7. Comparison of All Forms | การเปรียบเทียบทุกรูปแบบ

### Decision Flowchart | แผนภูมิการตัดสินใจ

```
                    Start
                      │
        Does ρ vary significantly?
                      │
         ┌────────────┴────────────┐
        │ Yes                      │ No
        ▼                          ▼
   General Form          Incompressible Form
        │                          │
    Phase change?              Phase change?
        │                          │
   ┌────┴────┐              ┌──────┴──────┐
  Yes        No             Yes           No
   │          │              │             │
   ▼          ▼              ▼             ▼
Full source  ṁ=0       With source    ṁ=0
             │                          │
        Sharp interface?           Sharp interface?
             │                          │
        ┌────┴────┐                ┌────┴────┐
       Yes        No              Yes        No
        │          │               │          │
        ▼          ▼               ▼          ▼
      VOF      Standard          VOF    Standard
   +compress                     +compress
```

### Summary Table | ตารางสรุป

| Form | Equation | When to Use | Complexity | ความซับซ้อน |
|------|----------|-------------|------------|-------------|
| **General** | ∂(αρ)/∂t + ∇·(αρU) = ṁ | Compressible + phase change | Highest | สูงสุด |
| **Incompressible** | ∂α/∂t + ∇·(αU) = ṁ/ρ | Incompressible + phase change | Medium | ปานกลาง |
| **No transfer** | ∂α/∂t + ∇·(αU) = 0 | No phase change | Lower | ต่ำกว่า |
| **VOF** | + compression term | Sharp interface needed | Medium | ปานกลาง |

---

## 8. Common Pitfalls | ปัญหาที่พบบ่อย

### Pitfall 1: Forgetting Normalization | ลืม normalize

**Problem:** Σα ≠ 1 leads to mass imbalance

```cpp
// ❌ WRONG — no normalization
alpha1.correctBoundaryConditions();
alpha2 = scalar(1) - alpha1;
```

```cpp
// ✅ CORRECT
volScalarField sumAlpha = alpha1 + alpha2;
alpha1 /= max(sumAlpha, SMALL);
alpha2 = scalar(1) - alpha1;
```

### Pitfall 2: Wrong Compression Sign | เครื่องหมาย compression ผิด

**Problem:** Interface smears instead of sharpens

```cpp
// ❌ WRONG — sign error
phiComp = +phic*nHatf;  // Wrong direction
```

```cpp
// ✅ CORRECT
phiComp = -phic*nHatf;  // Correct compression direction
```

### Pitfall 3: Not Enforcing Bounds | ไม่บังคับขอบเขต

**Problem:** α goes outside [0, 1]

```cpp
// ❌ WRONG — no bounds
alphaEqn.solve();
```

```cpp
// ✅ CORRECT
alphaEqn.solve();
alpha.max(0);  // Enforce lower bound
alpha.min(1);  // Enforce upper bound
```

### Pitfall 4: Wrong Form for Scenario | ใช้รูปแบบผิดกับสถานการณ์

| Scenario | ❌ Wrong | ✅ Correct |
|----------|---------|-----------|
| High-speed gas | Incompressible | General form |
| Dam break | With source | No source |
| Sharp droplet | No compression | With compression |

---

## 9. Validation Checklist | รายการตรวจสอบความถูกต้อง

Before trusting your simulation results, verify:

- [ ] **Σα = 1** everywhere (within tolerance)
- [ ] **0 ≤ α ≤ 1** for all phases
- [ ] **Mass balance** error < 1%
- [ ] **Interface sharpness** matches expected
- [ ] **Boundary conditions** physically meaningful
- [ ] **Time step** satisfies Co criterion

ก่อนที่จะเชื่อถือผลการจำลอง ให้ตรวจสอบ:
- [ ] ผลรวม α เท่ากับ 1 ทุกที่
- [ ] ค่า α อยู่ระหว่าง 0 ถึง 1
- [ ] ความคลาดเคลื่อนของสมดุลมวล < 1%
- [ ] ความคมของอินเตอร์เฟซตรงตามที่คาดหวัง
- [ ] เงื่อนไขขอบเขตมีความหมายทางฟิสิกส์
- [ ] ขนาดขั้นเวลาเป็นไปตามเกณฑ์ Co

---

## Key Takeaways | สรุปสำคัญ

### Core Concepts | แนวคิดหลัก

1. **Mass conservation** applies separately to each phase
2. **Volume fraction constraint** (Σα = 1) is fundamental
3. **Different forms** exist for different physical scenarios
4. **Interface compression** is essential for VOF sharpness
5. **Numerical bounds** (0 ≤ α ≤ 1) must be enforced

### Selection Guide | แนวทางการเลือกใช้

| Scenario | Recommended Form | รูปแบบที่แนะนำ |
|----------|------------------|-----------------|
| Compressible + phase change | General form | รูปแบบทั่วไป |
| Incompressible + phase change | Incompressible with source | แบบไม่อัดตัวพร้อม source |
| Free surface, immiscible | No transfer form | แบบไม่มีการถ่ายเท |
| Sharp interface needed | VOF with compression | VOF พร้อมการบีบอัด |

### Best Practices | แนวปฏิบัติที่ดี

- **Always normalize** α after solving
- **Use adaptive time stepping** for stability
- **Check mass balance** every timestep
- **Choose appropriate form** for your physics
- **Validate bounds** rigorously

---

## Concept Check | ทดสอบความเข้าใจ

<details>
<summary><b>1. Why must we normalize α after solving?</b></summary>

Numerical errors from discretization and solver tolerance can cause Σα to drift from 1. Normalization enforces the **physical constraint** that all phases must fill the volume completely.

**คำตอบ:** ความผิดพลาดเชิงตัวเลขจากการ discontinue และความทนทานของ solver อาจทำให้ Σα ลอยตัวจาก 1 การทำ normalization บังคับใช้ **ข้อจำกัดทางฟิสิกส์** ว่าทุกเฟสต้องเติมเต็มปริมาตรทั้งหมด
</details>

<details>
<summary><b>2. What does the interface compression term do?</b></summary>

The term $\nabla \cdot (\alpha(1-\alpha)\mathbf{U}_r)$ adds **artificial flux** at the interface region (where 0 < α < 1). This counteracts numerical diffusion and **sharpens the interface** to maintain it within 1-2 cells.

**คำตอบ:** เทอม $\nabla \cdot (\alpha(1-\alpha)\mathbf{U}_r)$ เพิ่ม **flux เทียม** ที่บริเวณอินเตอร์เฟซ (ที่ซึ่ง 0 < α < 1) ซึ่งต่อต้านการ diffuse เชิงตัวเลขและ **ทำให้อินเตอร์เฟซคมขึ้น** เพื่อรักษาให้ยังอยู่ภายใน 1-2 เซลล์
</details>

<details>
<summary><b>3. Where does the mass transfer source ṁ come from?</b></summary>

ṁ<sub>lk</sub> comes from **phase change models**:
- **Evaporation/condensation** models (thermal-driven)
- **Chemical reactions** consuming/producing phases
- **Cavitation models** (liquid → vapor)
- **Dissolution/precipitation** (mass exchange between phases)

**คำตอบ:** ṁ<sub>lk</sub> มาจาก **โมเดลการเปลี่ยนสถานะเฟส:**
- โมเดล **การระเหย/การควบแน่น** (ขับเคลื่อนด้วยความร้อน)
- **ปฏิกิริยาเคมี** ที่บริโภค/ผลิตเฟส
- โมเดล **แควิเทชัน** (ของเหลว → ไอ)
- **การละลาย/การตกตะกอน** (การแลกเปลี่ยนมวลระหว่างเฟส)
</details>

<details>
<summary><b>4. When should I use the general form vs. incompressible form?</b></summary>

Use **general form** when:
- Density variations > 5% during simulation
- High-speed gas flows (Ma > 0.3)
- Significant pressure/temperature changes

Use **incompressible form** when:
- Liquids at moderate conditions (Δρ < 5%)
- Low-speed flows (Ma < 0.1)
- Isothermal conditions

**คำตอบ:** ใช้ **รูปแบบทั่วไป** เมื่อ:
- ความหนาแน่นเปลี่ยนแปลง > 5% ระหว่างการจำลอง
- การไหลของก๊าซความเร็วสูง (Ma > 0.3)
- การเปลี่ยนแปลงความดัน/อุณหภูมิอย่างมีนัยสำคัญ

ใช้ **รูปแบบไม่อัดตัวได้** เมื่อ:
- ของเหลวภายใต้เงื่อนไขปานกลาง (Δρ < 5%)
- การไหลความเร็วต่ำ (Ma < 0.1)
- เงื่อนไขอุณหภูมิคงที่
</details>

<details>
<summary><b>5. Why does VOF need compression but Euler-Euler doesn't?</b></summary>

**VOF** tracks a **sharp interface** (α jumps from 0 to 1 across ~1 cell). Numerical diffusion smears this interface, so compression counteracts it.

**Euler-Euler** assumes **interpenetrating continua** where phases coexist in each cell (0 < α < 1 everywhere). No sharp interface = no compression needed.

**คำตอบ:** **VOF** ติดตาม **อินเตอร์เฟซที่คม** (α กระโดดจาก 0 เป็น 1 ผ่าน ~1 เซลล์) การ diffuse เชิงตัวเลขทำให้อินเตอร์เฟซเลอะเทะ ดังนั้นการบีบอัดจึงต่อต้านมัน

**Euler-Euler** สมมติ **continua ที่แทรกซึมกัน** ซึ่งเฟสร่วมกันอยู่ในแต่ละเซลล์ (0 < α < 1 ทุกที่) ไม่มีอินเตอร์เฟซคม = ไม่ต้องการการบีบอัด
</details>

---

## Related Documents | เอกสารที่เกี่ยวข้อง

### Navigation | การนำทาง

- **← Previous:** [00_Overview.md](00_Overview.md) — Introduction to multiphase equations
- **Next:** [02_Momentum_Conservation.md](02_Momentum_Conservation.md) — Momentum equations and interphase forces

### Fundamentals | พื้นฐาน

- **Flow Regimes:** [01_Flow_Regimes.md](../01_FUNDAMENTAL_CONCEPTS/01_Flow_Regimes.md)
- **Interfacial Phenomena:** [02_Interfacial_Phenomena.md](../01_FUNDAMENTAL_CONCEPTS/02_Interfacial_Phenomena.md)

### Methods | วิธีการ

- **VOF Method:** [01_The_VOF_Concept.md](../02_VOF_METHOD/01_The_VOF_Concept.md)
- **Euler-Euler:** [01_Introduction.md](../03_EULER_EULER_METHOD/01_Introduction.md)

### Implementation | การนำไปใช้

- **Solver Overview:** [01_Solver_Overview.md](../06_IMPLEMENTATION/01_Solver_Overview.md)
- **Model Architecture:** [03_Model_Architecture.md](../06_IMPLEMENTATION/03_Model_Architecture.md)

---

**Last Updated:** 2024-12-30 | **OpenFOAM Version:** v2312+ | **Difficulty Level:** ⭐⭐⭐☆☆