# RANS Models

Reynolds-Averaged NavierStokes Turbulence Models

---

## Learning Objectives [เป้าหมายการเรียนรู้]

By the end of this module, you will be able to:

- **Explain** the Reynolds decomposition concept and RANS averaging approach
- **Compare** k-ε and k-ω SST models in terms of mathematical formulation and physical behavior
- **Select** appropriate turbulence models for different flow regimes (internal/external, separated/attached)
- **Configure** RANS models in OpenFOAM with proper boundary conditions
- **Apply** correct y+ requirements for wall function vs low-Re approaches

---

## Skills Progression [แนวทางการพัฒนาทักษะ]

Use this checklist to track your progress:

- [ ] **[What]** Define Reynolds decomposition and derive RANS equations
- [ ] **[What]** Write transport equations for k-ε and k-ω SST models
- [ ] **[Why]** Explain when to use k-ε vs k-ω SST based on flow physics
- [ ] **[Why]** Predict separation behavior and adverse pressure gradient effects
- [ ] **[How]** Set up turbulenceProperties in OpenFOAM
- [ ] **[How]** Specify appropriate boundary conditions for k, ε, ω, and nut
- [ ] **[How]** Calculate y+ and verify mesh resolution requirements
- [ ] **[How]** Run and post-process yPlus calculations

---

## Overview [ภาพรวม]

RANS models แก้สมการ **time-averaged** แทน instantaneous → ลด cost จากวันเหลือชั่วโมง

**Core Concept:** Reynolds decomposition

$$\phi = \overline{\phi} + \phi'$$

---

## 1. k-ε Model

### **[What]** Model Definitions [ความหมาย]

#### Transport Equations

**Turbulent Kinetic Energy:**
$$\frac{\partial k}{\partial t} + \nabla \cdot (\mathbf{u}k) = \nabla \cdot \left[\left(\nu + \frac{\nu_t}{\sigma_k}\right)\nabla k\right] + G - \varepsilon$$

**Dissipation Rate:**
$$\frac{\partial \varepsilon}{\partial t} + \nabla \cdot (\mathbf{u}\varepsilon) = \nabla \cdot \left[\left(\nu + \frac{\nu_t}{\sigma_\varepsilon}\right)\nabla \varepsilon\right] + C_1\frac{\varepsilon}{k}G - C_2\frac{\varepsilon^2}{k}$$

#### Eddy Viscosity

$$\nu_t = C_\mu \frac{k^2}{\varepsilon}$$

#### Standard Coefficients

| Constant | Value |
|----------|-------|
| $C_\mu$ | 0.09 |
| $C_1$ | 1.44 |
| $C_2$ | 1.92 |
| $\sigma_k$ | 1.0 |
| $\sigma_\varepsilon$ | 1.3 |

### **[Why]** Selection Criteria [เกณฑ์การเลือกใช้]

✅ **Advantages [ข้อดี]:** Stable, fast convergence, good for free-shear flows  
❌ **Disadvantages [ข้อเสีย]:** Poor near-wall treatment, under-predicts separation

**Best for [เหมาะสำหรับ]:** Internal flows, pipe flows, simple geometries without separation

### **[How]** OpenFOAM Implementation [การนำไปใช้ใน OpenFOAM]

```cpp
simulationType RAS;

RAS
{
    RASModel    kEpsilon;
    turbulence  on;
    printCoeffs on;
}
```

---

## 2. k-ω SST Model

### **[What]** Model Definitions [ความหมาย]

#### Blending Function

SST ใช้ $F_1$ เพื่อสลับ:
- Near wall ($F_1 \to 1$): k-ω behavior
- Free stream ($F_1 \to 0$): k-ε behavior

#### Eddy Viscosity Limiter

$$\nu_t = \frac{a_1 k}{\max(a_1\omega, SF_2)}$$

ป้องกัน over-prediction ใน separation zones

#### SST Coefficients

| Constant | Inner | Outer |
|----------|-------|-------|
| $\alpha_k$ | 0.85 | 1.0 |
| $\alpha_\omega$ | 0.5 | 0.856 |
| $\beta$ | 0.075 | 0.0828 |
| $\beta^*$ | 0.09 | 0.09 |
| $a_1$ | 0.31 | 0.31 |

### **[Why]** Selection Criteria [เกณฑ์การเลือกใช้]

✅ **Advantages [ข้อดี]:** Excellent near-wall treatment, good separation prediction, handles adverse pressure gradients  
❌ **Disadvantages [ข้อเสีย]:** Higher computational cost, more sensitive to mesh quality

**Best for [เหมาะสำหรับ]:** External aerodynamics, separated flows, airfoils, flows with adverse pressure gradients

### **[How]** OpenFOAM Implementation [การนำไปใช้ใน OpenFOAM]

```cpp
simulationType RAS;

RAS
{
    RASModel    kOmegaSST;
    turbulence  on;
    printCoeffs on;
}
```

---

## 3. Model Selection Guide [คำแนะนำการเลือกโมเดล]

| Flow Type | k-ε | k-ω SST |
|-----------|-----|---------|
| Internal (pipe) | ✓ | ✓ |
| External (airfoil) | ✗ | ✓ |
| Separation | ✗ | ✓ |
| Adverse pressure gradient | ✗ | ✓ |
| Fast computation | ✓ | ✗ |

### **[Why]** Recommendation [คำแนะนำ]

- **Default choice:** k-ω SST (most reliable for general engineering applications)
- **Simple internal flow:** k-ε acceptable (faster, stable)
- **Separation/external aerodynamics:** k-ω SST mandatory

---

## 4. OpenFOAM Implementation [การนำไปใช้ใน OpenFOAM]

### **[How]** Configuration Setup [การตั้งค่า]

#### turbulenceProperties

```cpp
simulationType RAS;

RAS
{
    RASModel    kOmegaSST;  // or kEpsilon
    turbulence  on;
    printCoeffs on;
}
```

#### Initial/Boundary Conditions [เงื่อนไขเริ่มต้นและขอบเขต]

**From Intensity and Length Scale:**

$$k = \frac{3}{2}(UI)^2, \quad \varepsilon = C_\mu^{3/4}\frac{k^{3/2}}{L_t}$$

```cpp
// 0/k
inlet
{
    type    turbulentIntensityKineticEnergyInlet;
    intensity 0.05;  // 5%
    value   uniform 0.01;
}

// 0/epsilon
inlet
{
    type    turbulentMixingLengthDissipationRateInlet;
    mixingLength 0.01;  // [m]
    value   uniform 0.01;
}
```

#### Wall Boundary Conditions [เงื่อนไขขอบเขตผนัง]

```cpp
// 0/k
wall { type kLowReWallFunction; value uniform 0; }

// 0/epsilon
wall { type epsilonWallFunction; value uniform 0; }

// 0/omega
wall { type omegaWallFunction; value uniform 0; }

// 0/nut
wall { type nutkWallFunction; value uniform 0; }
```

---

## 5. y+ Requirements [ข้อกำหนดค่า y+]

| Approach | y+ Range | Wall BC | Notes [หมายเหตุ] |
|----------|----------|---------|-------------------|
| Wall functions | 30-300 | `*WallFunction` | ประหยัดเซลล์ ไม่ resolve viscous sublayer |
| Low-Re (resolve) | ≈ 1 | `kLowReWallFunction` | Resolve viscous sublayer directly เซลล์เยอะ |

```bash
postProcess -func yPlus
```

---

## Concept Check [ทดสอบความเข้าใจ]

<details>
<summary><b>1. k-ε ทำไมทำนาย separation แย่?</b></summary>

เพราะ k-ε มักจะ **over-predict $\nu_t$** ใกล้ผนัง → flow เกาะผิวได้ดีเกินจริง → delay separation
</details>

<details>
<summary><b>2. SST "blend" ระหว่าง k-ω และ k-ε อย่างไร?</b></summary>

ใช้ **blending function $F_1$**:
- ใกล้ผนัง: $F_1 \to 1$ → k-ω (ดีสำหรับ boundary layer)
- ไกลผนัง: $F_1 \to 0$ → k-ε (เสถียรใน free stream)
</details>

<details>
<summary><b>3. $y^+ = 1$ จำเป็นเสมอไหม?</b></summary>

**ไม่** — ขึ้นกับ approach:
- Low-Re (resolve viscous sublayer): $y^+ \approx 1$
- Wall functions: $y^+ = 30-300$
</details>

<details>
<summary><b>4. เมื่อไหร่ควรเลือก k-ε แทน k-ω SST?</b></summary>

เลือก k-ε เมื่อ:
- Internal flow ที่ไม่มี separation (เช่น pipe flow)
- ต้องการ fast computation
- Mesh resolution จำกัด
- เวลา simulation สำคัญกว่าความแม่นยำใกล้ผนัง
</details>

<details>
<summary><b>5. Eddy viscosity limiter ใน SST ทำหน้าที่อะไร?</b></summary>

$$\nu_t = \frac{a_1 k}{\max(a_1\omega, SF_2)}$$

ช่วย **ป้องกัน over-prediction ของ $\nu_t$** ใน separation zones → ทำให้ทำนาย separation ได้ดีกว่า k-ω มาตรฐาน
</details>

---

## Key Takeaways [สรุปสิ่งสำคัญ]

### **[What]** - Definitions [ความหมาย]
- **RANS:** Time-averaged approach using Reynolds decomposition $\phi = \overline{\phi} + \phi'$
- **k-ε:** Two-equation model solving for turbulent kinetic energy ($k$) and dissipation rate ($\varepsilon$)
- **k-ω SST:** Blended model combining k-ω near walls and k-ε in free stream with eddy viscosity limiter

### **[Why]** - Physical Meaning [ความหมายทางฟิสิกส์]
- **k-ε weakness:** Over-predicts eddy viscosity near walls → delays flow separation
- **k-ω SST strength:** Blending function + eddy viscosity limiter → accurate separation prediction
- **Selection matters:** Wrong model choice leads to incorrect physics, not just numerical errors

### **[How]** - OpenFOAM Implementation [การนำไปใช้]
- **Setup:** Configure `RASModel` in `turbulenceProperties` (kEpsilon or kOmegaSST)
- **Inlet BCs:** Use `turbulentIntensityKineticEnergyInlet` and `turbulentMixingLengthDissipationRateInlet`
- **Wall BCs:** Choose between `*WallFunction` (y+ = 30-300) or `kLowReWallFunction` (y+ ≈ 1)
- **Verification:** Run `postProcess -func yPlus` to check y+ values
- **Default choice:** k-ω SST for most engineering applications

### Best Practices [แนวปฏิบัติที่ดี]
1. **Start with k-ω SST** unless you have strong reasons to use k-ε
2. **Check y+** before trusting results
3. **Verify mesh quality** → SST is more sensitive than k-ε
4. **Use wall functions** for initial runs, then refine to y+ ≈ 1 for final results

---

## Related Documents [เอกสารที่เกี่ยวข้อง]

- **บทก่อนหน้า:** [01_Turbulence_Fundamentals.md](01_Turbulence_Fundamentals.md)
- **บทถัดไป:** [03_Wall_Treatment.md](03_Wall_Treatment.md)
- **หัวข้อขั้นสูง:** [02_INHERITANCE_POLYMORPHISM](../../MODULE_09_ADVANCED_TOPICS/CONTENT/02_INHERITANCE_POLYMORPHISM/00_Overview.md) - Runtime selection for turbulence models