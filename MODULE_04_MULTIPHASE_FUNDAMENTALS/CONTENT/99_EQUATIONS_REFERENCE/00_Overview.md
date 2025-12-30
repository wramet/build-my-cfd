# สมการอ้างอิงสำหรับ Multiphase Flow
# Equations Reference Overview

ภาพรวมการอ้างอิงสมการสำหรับการไหลแบบหลายเฟสใน OpenFOAM พร้อมคำแนะนำการนำไปใช้งาน

---

## 🎯 Learning Objectives | เป้าหมายการเรียนรู้

After completing this overview, you should be able to:

**What will you learn?**
- ระบุสมการหลักที่ใช้ในการจำลองการไหลแบบหลายเฟส (Identify key equations for multiphase flow simulations)
- เลือกใช้ correlation ที่เหมาะสมกับแต่ละสภาวการณ์ (Select appropriate correlations for different flow conditions)
- เชื่อมโยงสมการทางทฤษฎีกับการตั้งค่าใน OpenFOAM (Connect theoretical equations to OpenFOAM setup)
- ทำความเข้าใจความสัมพันธ์ระหว่างตัวแปรต่างๆ ในสมการ (Understand relationships between equation variables)

**Why is this important?**
- การเลือกสมการที่ถูกต้องส่งผลต่อความแม่นยำของการจำลอง (Correct equation selection affects simulation accuracy)
- การทำความเข้าใจสมการช่วยในการตีความผลลัพธ์ (Understanding equations aids result interpretation)
- สามารถปรับเปลี่ยนแบบจำลองให้เหมาะกับปัญหาที่เจอได้ (Adapt models to specific problems)

---

## 1. Conservation Laws | กฎการอนุรักษ์

### What: สมการพื้นฐานของฟิสิกส์
สมการเหล่านี้เป็นพื้นฐานของกลศาสตร์ไหลที่อธิบายการเคลื่อนที่และการถ่ายเทของไหล

### Why: ทำไมต้องมีใน Multiphase Flow
- **Phase Interaction:** เฟสต่างๆ แลกเปลี่ยนมวล โมเมนตัม และพลังงานระหว่างกัน
- **Volume Fraction:** แต่ละเฟสมีสัดส่วนปริมาตร (α) ที่ต้องนับรวมในสมการ
- **Coupling:** สมการของทุกเฟสมีความสัมพันธ์กัน (coupled)

### How: การนำไปใช้ใน OpenFOAM
- ใช้ใน solver: `interFoam`, `twoPhaseEulerFoam`, `multiphaseInterFoam`
- กำหนดใน `fvSolution`: วิธีแก้สมการ coupled หรือ segregated
- Boundary conditions: ต้องกำหนดสำหรับแต่ละเฟส

**ความสัมพันธ์ระหว่างกัน:**

```
Mass (α) → Momentum (U, p) → Energy (T, h)
   ↓            ↓                 ↓
Phase Fraction → Velocity Field → Temperature Field
```

**ดูรายละเอียดเพิ่มเติมที่:**
- 📄 [01_Mass_Conservation.md](01_Mass_Conservation.md) - การอนุรักษ์มวลและ volume fraction
- 📄 [02_Momentum_Conservation.md](02_Momentum_Conservation.md) - การอนุรักษ์โมเมนตัม
- 📄 [03_Energy_Conservation.md](03_Energy_Conservation.md) - การอนุรักษ์พลังงาน

---

## 2. Interphase Forces | แรงระหว่างเฟส

### What: แรงที่เกิดจากการโต้ตอบระหว่างเฟส
แรงต่างๆ ที่กระทำต่ออนุภาค/ฟองของเฟสหนึ่งจากเฟสอื่น

### Why: สำคัญต่อการทำนายการเคลื่อนที่
- **Drag:** แรงต้านการไหล - สำคัญที่สุด กำหนด terminal velocity
- **Lift:** แรงยก - สำคัญในกระแสเสได้ การลอยตัว
- **Virtual Mass:** แรงเฉื่อย - สำคัญเมื่อมีการเร่งความเร็วสูง
- **Turbulent Dispersion:** การกระจาย - ช่วยทำนายการกระจายตัวของเฟส

### How: การเลือกแบบจำลอง
| แรง (Force) | เมื่อไรต้องพิจารณา (When to Include) | OpenFOAM Keyword |
|-------------|-----------------------------------|------------------|
| **Drag** | เสมอ - แรงหลัก | `dragModel` |
| **Lift** | มี shear หรือการหมุน | `liftModel` |
| **Virtual Mass** | ρ_d/ρ_c > 0.1 หรือ acceleration high | `virtualMassModel` |
| **Turbulent Dispersion** | โฟลว์มี turbulence | `turbulentDispersionModel` |

**Common Pitfall:**
❌ **ผิด:** เปิดใช้ทุกแรงเพื่อความ "แม่นยำ"  
✅ **ถูก:** เลือกเฉพาะแรงที่มีนัยสำคัญต่อปัญหา การใช้แรงมากเกินไปทำให้ไม่เสถียร

**ดูรายละเอียดเพิ่มเติมที่:**
- 📄 [04_Interfacial_Phenomena_Equations.md](04_Interfacial_Phenomena_Equations.md) - แรงระหว่างเฟสทั้งหมด
- 📘 Module 04, Section 04: Interphase Forces

---

## 3. Drag Correlations | สหสัมพันธ์แรงต้าน

### What: สมการเชื่อมโยง C_D กับ Re, Eo
ค่าสัมประสิทธิ์แรงต้าน (C_D) ขึ้นกับรูปร่างฟองและเงื่อนไขการไหล

### Why: รูปร่างฟองส่งผลต่อการเคลื่อนที่
ฟองเปลี่ยนรูปจากเรียบ → ผิวย่น → แตก ตาม Re และ Eo ที่เพิ่มขึ้น

### How: การเลือก Correlation
```
เริ่มจากคำนวณ Re และ Eo:
Re = ρUd/μ, Eo = gΔρd²/σ

แล้วเลือก:
1. Re < 1 → ใช้ Stokes (C_D = 24/Re)
2. Re < 1000, Eo < 4 → Schiller-Naumann
3. Eo > 4 → Ishii-Zuber (distorted)
4. ไม่แน่ใจ → Tomiyama (covers wide range)
```

**Common Pitfall:**
❌ **ผิด:** ใช้ Schiller-Naumann กับฟองใหญ่ที่เปลี่ยนรูป  
✅ **ถูก:** เช็ค Eo number ก่อนเลือก correlation

**ดูรายละเอียดเพิ่มเติมที่:**
- 📘 Module 04, Section 04.01: Drag Forces - 02_Specific_Drag_Models.md

---

## 4. Dimensionless Numbers | จำนวนไร้มิติ

### What: พารามิเตอร์ที่ใช้จัดกลุ่ม regime การไหล

### Why: ช่วยทำนายลักษณะการไหลและเลือกแบบจำลอง

### How: การใช้งานจริง
| Number | ใช้ทำอะไร (Application) | ตัวอย่าง (Example) |
|--------|------------------------|-------------------|
| **Re** | เลือก laminar/turbulent, drag model | Re < 2300 → laminar pipe flow |
| **Eo** | ทำนายรูปร่างฟอง | Eo < 4 → spherical, Eo > 40 → spherical cap |
| **Mo** | จัดประเภท fluid pair | ใช้ใน flow regime map |
| **We** | ทำนายการแตกของฟอง | We > 12 → bubble breakup |
| **Fr** | Froude number - free surface effect | Fr > 1 → supercritical flow |
| **St** | Stokes number - particle tracking | St << 1 → particles follow flow |

**Quick Check:**
```python
# สมมติ: air bubbles (d=5mm) in water
ρ_c=1000, ρ_d=1.2, μ=0.001, σ=0.072, U=0.5 m/s, g=9.81

Re = 1000 × 0.5 × 0.005 / 0.001 = 2500 (moderate)
Eo = 9.81 × (1000-1.2) × 0.005² / 0.072 = 3.4 (near spherical)
We = 1000 × 0.5² × 0.005 / 0.072 = 17.4 (may deform)

→ ใช้ Schiller-Naumann หรือ Tomiyama
```

---

## 5. Surface Tension | แรงตึงผิว

### What: แรงที่ผิวขอบเขตระหว่างเฟส

### Why: สำคัญในระบบที่มี interface ชัดเจน
- กำหนดรูปร่างฟอง/หยด
- ส่งผลต่อการแตกและรวมตัว (breakup/coalescence)
- มีผลต่อ flow pattern ในท่อจำลองแรงดัน (slug flow ต่างจาก bubbly flow)

### How: การใช้งานใน OpenFOAM
```cpp
// transportProperties
sigma sigma [0 2 -2 0 0 0 0] 0.07; // N/m for air-water

// ใช้ CSF model (default ใน interFoam):
interfaceCompressionScheme Gauss linear;
```

**Common Pitfall:**
❌ **ผิด:** ไม่กำหนด σ หรือใส่ค่าผิด (หน่วยผิด)  
✅ **ถูก:** ตรวจสอบหน่วย (N/m ใน SI) และค่าที่ต้องการ (air-water = 0.072 N/m)

**ดูรายละเอียดเพิ่มเติมที่:**
- 📘 Module 04, Section 01.02: Interfacial Phenomena

---

## 6. Heat Transfer | การถ่ายเทความร้อน

### What: การแลกเปลี่ยนความร้อนระหว่างเฟสและกำแพง

### Why: จำเป็นในระบบที่มีอุณหภูมิต่างกัน
- Boiling, condensation
- Heat exchangers
- Chemical reactors

### How: การนำไปใช้
```cpp
// ใช้ solver: twoPhaseEulerFoam หรือ compressibleInterFoam
// ใน thermophysicalProperties:
h  h [0 2 -2 0 0 0 0] ...;

// Interphase heat transfer coefficient:
interphaseHeatTransferModel RanzMarshall;
```

**Nu Number และความหมาย:**
- **Nu = 2:** conduction เท่านั้น (ไม่มี convection)
- **Nu > 2:** มี convection ช่วย
- **Ranz-Marshall:** Nu ขึ้นกับ Re^0.5 และ Pr^0.33

---

## 7. Terminal Velocity | ความเร็วปลายสุด

### What: ความเร็วคงที่ของฟอง/อนุภาคเมื่อแรงสมดุล

### Why: ใช้ตรวจสอบและประมาณค่า
- ใช้เป็นค่าเริ่มต้นในการจำลอง
- ตรวจสอบว่า drag model ถูกต้อง (เมื่อจำลองถึง steady state)

### How: การใช้งาน
```
เมื่อ Drag = Buoyancy - Weight
→ สามารถคำนวณ u_t จากสมการด้านบน

ใช้ประโยชน์:
1. ประมาณเวลาที่ฟองใช้ไหลผ่านระบบ
2. ตรวจสอบว่าการจำลองถึง steady state
   (ถ้า U_mean ≈ u_t แสดงว่าถึง steady)
```

---

## 8. Turbulence | ความปั่นป่วน

### What: สมการ k-ε สำหรับ multiphase

### Why: Turbulence ส่งผลต่อการผสมและการกระจาย
- กำหนด effective viscosity
- ส่งผลต่อ drag, dispersion
- สำคัญในสเกลเชิงอุตสาหกรรม

### How: การนำไปใช้ใน OpenFOAM
```cpp
// constant/turbulenceProperties
simulationType RAS;
RAS { RASModel kEpsilon; }

// สำหรับ multiphase มักใช้:
// - mixture k-ε: ใช้ค่าเฉลี่ย
// - per-phase k-ε: คำนวณแยกแต่ละเฟส
```

**Common Pitfall:**
❌ **ผิด:** ใช้ k-ε สำหรับ laminar flow (Re ต่ำ)  
✅ **ถูก:** เช็ค Re number ก่อนเลือก turbulence model

---

## 📋 Quick Reference Summary

สรุปสมการและตัวแปรสำคัญสำหรับการค้นหาเร็ว

| หมวดหมู่ (Category) | สมการหลัก (Key Equation) | ตัวแปรสำคัญ (Key Variables) | ไฟล์อ้างอิง (Reference) |
|---------------------|--------------------------|---------------------------|-------------------------|
| **Conservation Laws** | ∂(αρ)/∂t + ∇·(αρU) = ṁ | α, ρ, U, p | 01-03 |
| **Mass** | ∂(α_k ρ_k)/∂t + ∇·(α_k ρ_k U_k) | Σ α_k = 1 | 01 |
| **Momentum** | -α∇p + ∇·τ + M | τ, M (interphase) | 02 |
| **Energy** | ∂(αρh)/∂t + ∇·(αρhU) = Q | h, T, Q | 03 |
| **Interphase Forces** | F = K(U_c - U_d) | K, C_D, Re, Eo | 04 |
| **Drag** | F_D = K(U_c - U_d) | C_D(Re, Eo) | 04.01 |
| **Lift** | F_L = -C_L ρ_c α_d (U_r × ω) | C_L, ω | 04.02 |
| **Virtual Mass** | F_VM = C_VM ρ_c α_d D(U_r)/Dt | C_VM | 04.03 |
| **Turb. Dispersion** | F_TD = -C_TD ρ_c k_c ∇α_d | C_TD, k_c | 04.04 |
| **Surface Tension** | Δp = σκ, F_σ = σκ∇α | σ, κ | 04 |
| **Heat Transfer** | Q = hA(T_l - T_k) | h, Nu, Pr | 03 |
| **Terminal Velocity** | u_t = √(4Δρgd/3ρ_c C_D) | u_t, C_D | - |

**สัญลักษณ์ (Notation):**
- α: Volume fraction (สัดส่วนปริมาตร)
- ρ: Density (ความหนาแน่น)
- U: Velocity (ความเร็ว)
- p: Pressure (ความดัน)
- τ: Stress tensor (เทนเซอร์ความเครียด)
- M: Interphase force (แรงระหว่างเฟส)
- σ: Surface tension (แรงตึงผิว)
- κ: Curvature (ความโค้ง)

---

## 🎯 Key Takeaways | สรุปสิ่งสำคัญ

### สิ่งที่ควรนำไปใช้ (Key Principles):

1. **Consistency is Key**
   - ใช้ชุดสมการและแบบจำลองที่เข้ากันได้ (consistent set)
   - อย่าผสม drag model ที่มีพื้นฐานต่างกันโดยไม่เข้าใจ

2. **Know Your Flow Regime**
   - คำนวณ dimensionless numbers (Re, Eo, We) ก่อนเลือกแบบจำลอง
   - regime maps ช่วยลดความผิดพลาด

3. **Start Simple, Add Complexity**
   - เริ่มจาก drag เท่านั้น แล้วค่อยเพิ่ม lift, VM, TD
   - เปิดทีละตัวเพื่อดูผลต่อคำตอบ

4. **Validate Your Models**
   - เทียบกับ experimental data หรือ benchmark cases
   - ตรวจสอบ terminal velocity และ flow pattern

5. **Common Mistakes to Avoid**
   - ❌ ใช้ correlation นอกช่วงที่ใช้ได้ (outside valid range)
   - ❌ ลืม volume fraction constraint (Σ α = 1)
   - ❌ ใช้ single-phase BCs กับ multiphase
   - ❌ ไม่ตรวจสอบหน่วยของค่าที่ใส่

### การนำไปใช้ใน OpenFOAM (Practical Workflow):
```
1. วิเคราะห์ปัญหา → คำนวณ Re, Eo, We
2. เลือก solver → interFoam, twoPhaseEulerFoam, ...
3. เลือก drag model → ตาม regime map
4. ตั้งค่า transportProperties → σ, μ, ρ
5. รัน simulation → monitor residuals
6. ตรวจสอบผล → validate vs. experiment
```

---

## 🧠 Concept Check | ทดสอบความเข้าใจ

<details>
<summary><b>1. สมการ Continuity สำหรับ Multiphase แตกต่างจาก Single-phase อย่างไร?</b></summary>

**คำตอบ:**

สมการ continuity สำหรับ multiphase มีสองสิ่งที่เพิ่มขึ้นมา:

$$\frac{\partial(\alpha_k \rho_k)}{\partial t} + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k) = \sum_{l \neq k} \dot{m}_{lk}$$

1. **Volume Fraction ($\alpha_k$):**
   - **What:** สัดส่วนปริมาตรของเฟส k ในแต่ละเซลล์
   - **Why:** ใน multiphase หลายเฟสแชร์ปริมาตรเดียวกัน ต้องมีตัวแปรนี้เพื่อบอกว่าเฟสไหนครองเท่าไร
   - **How:** ใช้ constraint Σ α_k = 1 เพื่อให้แน่ใจว่าผลรวมเท่ากับ 1

2. **Mass Transfer ($\dot{m}_{lk}$):**
   - **What:** อัตราการถ่ายเทมวลจากเฟส l ไปเฟส k (kg/m³s)
   - **Why:** ในระบบที่มี phase change (evaporation, condensation) มวลของเฟสไม่คงที่
   - **How:** ใช้ mass transfer models ใน OpenFOAM (เช่น `liquidEvaporation`, `damping`)

**ตัวอย่างการใช้งาน:**
- **Boiling:** water (liquid) → steam (gas), มี $\dot{m}_{lg}$ จาก evaporation
- **Without phase change:** $\dot{m}_{lk} = 0$

</details>

<details>
<summary><b>2. Drag Correlation ไหนเหมาะกับฟองแบบต่างๆ?</b></summary>

**คำตอบ:**

การเลือก drag correlation ขึ้นกับรูปร่างฟองซึ่ง depend on Re และ Eo:

| Correlation | เหมาะกับ | ช่วงที่ใช้ได้ (Valid Range) | รูปร่างฟอง | เมื่อไรใช้ |
|-------------|----------|---------------------------|-------------|-------------|
| **Stokes** | ฟองเล็กมาก | Re < 1 | Spherical | ฟองจุลินทรีย์ |
| **Schiller-Naumann** | ฟองเล็ก-กลาง | Re < 1000 | Spherical | ฟองในน้ำทั่วไป |
| **Ishii-Zuber** | ฟองกลาง-ใหญ่ | Eo > 4 | Distorted/wobble | ฟองที่เริ่มเปลี่ยนรูป |
| **Tomiyama** | ครอบคลุม | All Re, Eo | Spherical → ellipsoidal | เมื่อไม่แน่ใจ หรือฟองผิดปกติ |
| **Grace** | ฟองใหญ่มาก | Eo > 40 | Spherical cap | slug flow |

**Flowchart การเลือก:**
```
เริ่ม: คำนวณ Re และ Eo
│
├─ Re < 1 → Stokes
│
├─ Re < 1000 AND Eo < 4 → Schiller-Naumann
│
├─ Eo > 4 AND Eo < 40 → Ishii-Zuber
│
├─ Eo > 40 → Grace หรือ Tomiyama
│
└─ ไม่แน่ใจ → Tomiyama (safe choice)
```

**ตัวอย่าง:**
- **Air bubbles in water (d=2mm, U=0.1m/s):**
  - Re ≈ 200, Eo ≈ 0.5 → Schiller-Naumann
  
- **Air bubbles in water (d=10mm, U=0.3m/s):**
  - Re ≈ 3000, Eo ≈ 13 → Ishii-Zuber หรือ Tomiyama

**Common Pitfall:**
❌ ใช้ Schiller-Naumann กับ distorted bubbles (Eo > 4)  
→ จะได้ C_D ต่ำเกินไป ทำให้ velocity สูงเกินจริง

</details>

<details>
<summary><b>3. ทำไมต้องใช้ Dimensionless Numbers?</b></summary>

**คำตอบ:**

Dimensionless numbers ช่วยให้เรา:

1. **Classify Flow Regimes:**
   - **Re < 1:** Creeping flow (Stokes flow)
   - **Re > 4000:** Turbulent flow
   - **Eo < 4:** Spherical bubbles
   - **Eo > 40:** Spherical cap bubbles

2. **Scale-Up/Scale-Down:**
   - ทำ lab-scale (เช่น d=1mm) → ขยายเป็น industrial (d=10cm)
   - ถ้ารักษา Re, Eo เท่ากัน → flow pattern เหมือนกัน

3. **Select Models:**
   - Re บอกว่าควรใช้ laminar หรือ turbulent model
   - Eo บอกว่าควรใช้ drag model ไหน
   - We บอกว่าจะเกิด breakup (We > 12)

**ตัวอย่างการใช้:**
```
Problem: Design bubble column

Given:
- Air in water: ρ_c=1000, μ=0.001, σ=0.072
- Want bubbles with d=5mm at U=0.2 m/s

Calculate:
Re = 1000 × 0.2 × 0.005 / 0.001 = 1000
Eo = 9.81 × 999 × 0.005² / 0.072 = 3.4
We = 1000 × 0.2² × 0.005 / 0.072 = 2.8

→ Use: Schiller-Naumann drag, no breakup (We < 12)
```

**Key Insight:**
Dimensionless numbers turn dimensional problems into dimensionless ones, making solutions more general and transferable.

</details>

<details>
<summary><b>4. Interphase Forces ไหนควรเปิดใช้เสมอ?</b></summary>

**คำตอบ:**

| Force | ใช้เสมอหรือไม่? | เหตุผล | เมื่อไรควรใช้ |
|-------|-------------------|---------|--------------|
| **Drag** | ✅ **เสมอ** | เป็นแรงหลักที่ balance buoyancy | All multiphase flows |
| **Lift** | ❌ ไม่เสมอ | สำคัญเมื่อมี shear | Shear flow, rotating systems |
| **Virtual Mass** | ❌ ไม่เสมอ | สำคัญเมื่อ ρ_d/ρ_c > 0.1 | High acceleration, bubbles in liquid |
| **Turb. Dispersion** | ❌ ไม่เสมอ | ช่วยกระจาย phase | Turbulent flows with high gradient |

**กฎง่ายๆ:**
1. **Minimum:** Drag เท่านั้น
2. **Typical:** Drag + Lift
3. **Complete:** Drag + Lift + VM + TD

**ตัวอย่าง:**

*Case 1: Large bubbles in stagnant water*
- Drag (only)
- Bubbles rise at terminal velocity, no shear

*Case 2: Small bubbles in turbulent pipe flow*
- Drag + Lift + Turbulent Dispersion
- Shear from wall → lift, turbulence → dispersion

*Case 3: Air bubbles accelerating in water*
- Drag + Virtual Mass
- High acceleration, ρ_d/ρ_c << 1 → VM significant

**Common Mistake:**
❌ เปิดทุกแรงเพื่อ "maximum accuracy"
→ อาจทำให้ solution diverge หรือไม่เสถียร

✅ เริ่มจาก drag เท่านั้น แล้วเพิ่มทีละตัว
→ ดูว่าแรงไหนมีผลจริง (compare magnitude)

</details>

<details>
<summary><b>5. จะตรวจสอบว่า Simulation Setup ถูกต้องหรือไม่?</b></summary>

**คำตอบ:**

**Checklist ก่อนรัน:**

1. **Physical Consistency:**
   - ✅ Σ α_k = 1 (volume fraction constraint)
   - ✅ ρ, μ, σ มีค่าที่เป็นไปได้ (ตรวจสอบหน่วย)
   - ✅ Initial conditions สอดคล้องกับ boundary conditions

2. **Numerical Stability:**
   - ✅ Courant number < 1 (for explicit schemes)
   - ✅ Mesh resolution sufficient (resolve interface)
   - ✅ Time step appropriate for velocity

3. **Model Selection:**
   - ✅ Drag model matches flow regime (check Re, Eo)
   - ✅ Turbulence model appropriate (laminar vs. turbulent)
   - ✅ Interphase forces justified

**หลังจากรัน (Post-Run Checks):**

1. **Terminal Velocity Check:**
   ```
   ถ้า single bubble rising:
   → ควรจะถึง steady state velocity
   → ควรใกล้กับค่าที่คำนวณจากสมการ terminal velocity
   ```

2. **Mass Balance:**
   ```
   ∫ α_k ρ_k dV ควรคงที่ (ถ้าไม่มี mass transfer)
   หรือเปลี่ยนตาม ṁ ที่กำหนด
   ```

3. **Flow Pattern:**
   ```
   เปรียบเทียบกับ regime map:
   - Bubbly flow: bubbles dispersed
   - Slug flow: large bubbles
   - Annular flow: film on wall
   ```

**ตัวอย่างการ Validate:**
```
Problem: Single air bubble (d=5mm) rising in water

Expected:
u_t = sqrt(4(1000-1.2)×9.81×0.005/(3×1000×C_D))
With C_D (Tomiyama) ≈ 1.2
→ u_t ≈ 0.25 m/s

Check simulation:
→ If U_bubble ≈ 0.23-0.27 m/s ✓
→ If U_bubble << 0.1 m/s ✗ (drag too high?)
→ If U_bubble >> 0.5 m/s ✗ (drag too low?)
```

**Tools:**
- OpenFOAM `functionObjects` สำหรับ monitoring mass, momentum balance
- ParaView สำหรับ visualize flow pattern

---

## 📖 เอกสารที่เกี่ยวข้อง | Related Documentation

### ในหมวด Equations Reference (เนื้อหาเชิงลึก):
- **📄 01_Mass_Conservation.md** - สมการอนุรักษ์มวลและ volume fraction transport
- **📄 02_Momentum_Conservation.md** - สมการอนุรักษ์โมเมนตัมและ stress tensor
- **📄 03_Energy_Conservation.md** - สมการอนุรักษ์พลังงานและ heat transfer
- **📄 04_Interfacial_Phenomena_Equations.md** - สมการแรงต่างๆ ระหว่างเฟส

### ใน Module 04 (Multiphase Fundamentals):
- **📘 Section 01: Fundamental Concepts** - Flow regimes, dimensionless numbers
- **📘 Section 02: VOF Method** - Interface tracking, surface tension
- **📘 Section 03: Euler-Euler Method** - Averaged equations, phase coupling
- **📘 Section 04: Interphase Forces** - Drag, lift, VM, TD in detail
- **📘 Section 05: Model Selection** - Decision framework for choosing models
- **📘 Section 06: Implementation** - OpenFOAM code architecture
- **📘 Section 07: Validation** - Benchmark problems and verification

### ใน Modules อื่นๆ:
- **📘 Module 03:** Single-phase flow fundamentals (turbulence, heat transfer)
- **📘 Module 02:** Meshing and boundary conditions for multiphase

---

## 🔍 Navigation Guide | คู่มือการนำทาง

**เริ่มต้นใหม่? (Beginner)**
1. เริ่มจาก Overview นี้เพื่อดูภาพรวม
2. ไปที่ **01_Mass_Conservation.md** เพื่อเข้าใจพื้นฐาน
3. อ่าน **02_Momentum_Conservation.md** เพื่อเข้าใจ interphase forces
4. ดู **Section 04** ใน Module 04 สำหรับรายละเอียดแรงต่างๆ

**มีพื้นฐานแล้ว? (Intermediate)**
1. ดู **04_Interfacial_Phenomena_Equations.md** สำหรับสมการแรงระหว่างเฟส
2. ไปที่ **Section 05: Model Selection** สำหรับ decision framework
3. ดู **Section 07: Validation** สำหรับ benchmark cases

**ต้องการ implement? (Advanced)**
1. ไปที่ **Section 06: Implementation** สำหรับ OpenFOAM code structure
2. ดู source code ใน `$FOAM_SRC/transportModels`
3. อ่าน **Section 07: Validation** สำหรับ verification methods

---

*Last Updated: 2025-12-30*  
*Next Review: After completing all detail files (01-04)*