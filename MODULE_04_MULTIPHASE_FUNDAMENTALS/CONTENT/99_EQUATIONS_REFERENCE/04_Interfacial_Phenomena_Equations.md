# Interfacial Phenomena Equations

สมการปรากฏการณ์ที่ผิวสัมผัส

---

## Learning Objectives

เป้าหมายการเรียนรู้ | Learning Objectives
---|---
- เข้าใจสมการทางกายภาพที่ควบคุมปรากฏการณ์ผิวสัมผัสในการไหลแบบหลายเฟส | Understand fundamental equations governing interfacial phenomena in multiphase flow
- อธิบายความสัมพันธ์ระหว่างความตึงผิว ความโค้ง และการกระจายตัวของเฟส | Explain relationship between surface tension, curvature, and phase distribution
- ประยุกต์ใช้สมการเหล่านี้กับปัญหาจริงใน OpenFOAM | Apply these equations to practical problems in OpenFOAM
- วิเคราะห์แรงที่ผิวสัมผัสและผลกระทบต่อการเคลื่อนที่ของฟลูอิด | Analyze interfacial forces and their impact on fluid motion
- คำนวณค่าตัวเลขไร้มิติสำหรับการไหลแบบหลายเฟส | Calculate dimensionless numbers for multiphase flow regimes

---

## 1. Young-Laplace Equation | สมการยัง-ลาปลาซ

### What is the Young-Laplace Equation? | สมการยัง-ลาปลาซคืออะไร?

**Definition:** The Young-Laplace equation describes the pressure jump across a curved interface due to surface tension.

**นิยาม:** สมการยัง-ลาปลาซอธิบายผลต่างความดันข้ามผิวสัมผัสโค้งเนื่องจากแรงตึงผิว

**Mathematical Form:**

$$\Delta p = p_{in} - p_{out} = \sigma \kappa = \sigma \left(\frac{1}{R_1} + \frac{1}{R_2}\right)$$

| Variable | Symbol | Meaning | หน่วย | Unit |
|----------|--------|---------|------|------|
| Pressure jump | Δp | Difference across interface | Pa | Pa |
| Surface tension | σ | Force per unit length | N/m | N/m |
| Mean curvature | κ | Interface curvature | 1/m | 1/m |
| Principal radii | R₁, R₂ | Local curvature radii | m | m |

---

### Why Does the Young-Laplace Equation Matter? | ทำไมสมการนี้สำคัญ?

**Physical Significance | ความสำคัญทางกายภาพ:**

1. **Pressure-Curvature Relationship:** Smaller bubbles → Higher internal pressure
   - ฟองเล็ก → ความดันภายในสูง

2. **Interface Stability:** Drives bubble coalescence and breakup
   - ขับเคลื่อนการรวมและแตกตัวของฟอง

3. **Shape Determination:** Explains why bubbles are spherical
   - อธิบายว่าทำไมฟองจึงเป็นทรงกลม

**Key Implications | ผลสำคัญ:**
- Flat interfaces → No pressure jump (κ = 0)
- ผิวแบน → ไม่มีผลต่างความดัน
- Spherical bubbles → Maximum pressure for given volume
- ฟองทรงกลม → ความดันสูงสุดสำหรับปริมาตรที่กำหนด

---

### How to Apply the Young-Laplace Equation? | การประยุกต์ใช้สมการ

**Special Cases | กรณีพิเศษ:**

| Shape | รูปร่าง | Curvature (κ) | Pressure Jump (Δp) | Application |
|-------|---------|---------------|-------------------|-------------|
| Sphere (R) | ทรงกลม | 2/R | 2σ/R | Bubbles, drops |
| Cylinder (R) | ทรงกระบอก | 1/R | σ/R | Liquid jets |
| Flat | แบน | 0 | 0 | Free surface |

**Example 1: Bubble Pressure Calculation | ตัวอย่าง 1: การคำนวณความดันในฟอง**

For an air bubble in water (σ = 0.072 N/m):

$$\Delta p = \frac{2\sigma}{R}$$

- **R = 1 mm:** Δp = 2(0.072)/0.001 = **144 Pa**
- **R = 1 μm:** Δp = 2(0.072)/0.000001 = **144,000 Pa** (~1.4 atm!)
- **R = 1 nm:** Δp = 2(0.072)/0.000000001 = **144 MPa** (~1420 atm!)

**Practical Insight | ข้อเข้าใจทางปฏิบัติ:**
- Nano-bubbles require extremely high pressures to maintain stability
- ฟองนาโนจำเป็นต้องมีความดันสูงมากเพื่อรักษาเสถียรภาพ
- This explains why nano-bubbles are rare in nature
- นี่อธิบายว่าทำไมฟองนาโนจึงหายากในธรรมชาติ

**Example 2: Droplet Coalescence | ตัวอย่าง 2: การรวมตัวของหยด**

When two droplets (R₁, R₂) merge:
- Total volume is conserved
- New radius: R = (R₁³ + R₂³)^(1/3)
- Surface area decreases → Energy is released
- พื้นที่ผิวลดลง → พลังงานถูกปลดปล่อย

---

### Common Pitfalls | ข้อผิดพลาดที่พบบ่อย

❌ **Incorrect:** Assuming all bubbles have the same internal pressure
✅ **Correct:** Δp ∝ 1/R for spherical interfaces - smaller bubbles have much higher pressure

❌ **Incorrect:** Neglecting curvature in flat surfaces
✅ **Correct:** Even small curvatures (κ ≈ 0.001 m⁻¹) create measurable pressure jumps

❌ **Incorrect:** Using Young-Laplace for turbulent interfaces
✅ **Correct:** The equation assumes static equilibrium; dynamic interfaces need additional terms

---

## 2. Continuum Surface Force (CSF) Model | โมเดล CSF

### What is the CSF Model? | โมเดล CSF คืออะไร?

**Definition:** A method to convert surface tension (a surface phenomenon) into a volume force for CFD calculations in fixed-grid methods like VOF.

**นิยาม:** วิธีการแปลงแรงตึงผิว (ปรากฏการณ์ผิว) เป็น volume force สำหรับการคำนวณ CFD ใน grid คงที่ เช่น VOF

**The CSF Formulation:**

$$\mathbf{F}_\sigma = \sigma \kappa \nabla \alpha$$

| Component | Meaning | ความหมาย |
|-----------|---------|-----------|
| σ | Surface tension coefficient | สัมประสิทธิ์ความตึงผิว |
| κ | Mean curvature (from α) | ความโค้งเฉลี่ย |
| ∇α | Volume fraction gradient | ไกรเดียนต์ของสัดส่วนปริมาตร |

---

### Why Use CSF in OpenFOAM? | ทำไมใช้ CSF ใน OpenFOAM

**Advantages | ข้อดี:**
- Compatible with fixed-grid Eulerian methods
- ใช้ได้กับ grid คงที่แบบ Eulerian
- Automatically captures interface topology
- จับลักษณะผิวสัมผัสอัตโนมัติ
- No explicit interface tracking needed
- ไม่ต้อง track ผิวสัมผัสโดยตรง
- Simple implementation in finite volume methods
- การนำไปใช้ง่ายในวิธีปริมาตรจำกัด

**Limitations | ข้อจำกัด:**
- "Spurious currents" (parasitic velocities) near interface
- กระแสปลอมๆ บริเวณผิวสัมผัส
- Sensitive to α field smoothness
- ไวต่อความเรียบของสนาม α
- Requires special numerical schemes
- ต้องใช้สูตรเชิงตัวเลขพิเศษ

---

### How is Curvature Calculated in CSF? | การคำนวณความโค้งใน CSF

**Curvature from Volume Fraction:**

$$\kappa = -\nabla \cdot \hat{\mathbf{n}} = -\nabla \cdot \left(\frac{\nabla \alpha}{|\nabla \alpha|}\right)$$

**Step-by-Step Calculation | ขั้นตอนการคำนวณ:**

1. **Compute gradient:** ∇α from volume fraction field
   - คำนวณ gradient จากสนามสัดส่วนปริมาตร

2. **Normalize to unit normal:** $\hat{\mathbf{n}} = \nabla \alpha / |\nabla \alpha|$
   - ทำให้เป็นเวกเตอร์หน่วย

3. **Calculate divergence:** κ = -∇ · n̂
   - คำนวณ divergence

4. **Apply CSF force:** Fσ = σκ∇α
   - ใช้แรง CSF

**Implementation in OpenFOAM | การนำไปใช้ใน OpenFOAM:**

```cpp
// OpenFOAM pseudo-code for curvature calculation
volVectorField n = fvc::grad(alpha);           // Gradient of alpha
volScalarField nMag(mag(n) + VSMALL);          // Magnitude (with small value)
volVectorField unitN(n/nMag);                  // Unit normal vector
volScalarField kappa(-fvc::div(unitN));        // Curvature
volVectorField Fsigma(sigma*kappa*n);          // CSF force
```

---

### Common Pitfalls | ข้อผิดพลาดที่พบบ่อย

❌ **Incorrect:** Directly computing κ from interface geometry
✅ **Correct:** Always compute κ from ∇α using CSF formulation

❌ **Incorrect:** Using CSF without interface compression
✅ **Correct:** Apply compression schemes (e.g., MULES) to maintain sharp α

❌ **Incorrect:** Ignoring spurious currents
✅ **Correct:** Monitor and control spurious currents (< 1% of characteristic velocity)

---

## 3. Contact Angle and Wetting Phenomena | มุมสัมผัสและปรากฏการณ์การเปียก

### What is Contact Angle? | มุมสัมผัสคืออะไร?

**Definition:** The angle (θ) formed between a liquid-solid-gas interface at the contact line, measuring wettability.

**นิยาม:** มุม (θ) ที่เกิดขึ้นที่แนวติดต่อระหว่างของเหลว-ของแข็ง-ก๊าซ ใช้วัดระดับการเปียก

**Visual Representation | ภาพประกอบ:**
```
       Gas (ก๊าซ)
      ∠θ  ← Contact angle (มุมสัมผัส)
    --------
   Liquid  Solid (ของเหลว ของแข็ง)
```

---

### Why Does Contact Angle Matter? | ทำไมมุมสัมผัสสำคัญ?

**Young's Equation - Force Balance at Contact Line:**

$$\cos\theta = \frac{\sigma_{SG} - \sigma_{SL}}{\sigma_{LG}}$$

| Interface | Symbol | Meaning |
|-----------|--------|---------|
| Solid-Gas | σSG | Solid-gas surface tension |
| Solid-Liquid | σSL | Solid-liquid surface tension |
| Liquid-Gas | σLG | Liquid-gas surface tension |

**Wettability Regimes | ระดับการเปียก:**

| Contact Angle | Behavior | พฤติกรรม |
|--------------|----------|-----------|
| θ < 90° | Hydrophilic (wetting) | ชอบน้ำ (เปียก) |
| θ > 90° | Hydrophobic (non-wetting) | รังเกียจน้ำ (ไม่เปียก) |
| θ = 0° | Complete wetting | เปียกทั้งหมด |
| θ = 180° | Complete non-wetting | ไม่เปียกเลย |

---

### How to Apply Contact Angle in Practice? | การประยุกต์ใช้มุมสัมผัส

**Example 1: Water on Glass | ตัวอย่าง 1: น้ำบนกระจก**

Surface tension values:
- σSG ≈ 0.072 N/m (glass-air)
- σSL ≈ 0.025 N/m (glass-water)
- σLG ≈ 0.072 N/m (water-air)

$$\cos\theta = \frac{0.072 - 0.025}{0.072} = 0.65$$
$$\theta \approx 49° \text{ (hydrophilic - เปียก)}$$

**Practical observation:** Water spreads on glass surfaces
- การสังเกตทางปฏิบัติ: น้ำกระจายบนพื้นผิวกระจก

---

**Example 2: Water on Teflon | ตัวอย่าง 2: น้ำบนเทฟลอน**

For Teflon (PTFE):
- σSG ≈ 0.018 N/m (Teflon-air)
- σSL ≈ 0.050 N/m (Teflon-water)
- σLG ≈ 0.072 N/m (water-air)

$$\cos\theta = \frac{0.018 - 0.050}{0.072} = -0.44$$
$$\theta \approx 116° \text{ (hydrophobic - ไม่เปียก)}$$

**Practical observation:** Water beads up on Teflon-coated surfaces
- การสังเกตทางปฏิบัติ: น้ำเกาะแตกบนพื้นผิวเคลือบเทฟลอน

---

**Example 3: Industrial Applications | ตัวอย่าง 3: การประยุกต์ใช้ทางอุตสาหกรรม**

**Oil Recovery | การผลิตน้ำมัน:**
- Modify θ to alter capillary pressure
- ปรับ θ เพื่อเปลี่ยนความดัน capillary
- Surfactants reduce θ → Improve oil displacement
- สารลดแรงตึงผิวลด θ → ปรับปรุงการแทนที่น้ำมัน

**Coating Processes | กระบวนการเคลือบ:**
- Control spreading behavior via θ
- ควบคุมการลาหลุ่งผ่าน θ
- Low θ → Uniform thin films
- θ ต่ำ → ฟิล์มบางสม่ำเสมอ

**Microfluidics | ไมโครฟลูอิดิกส์:**
- Design channel wetting properties
- ออกแบบคุณสมบัติการเปียกในช่องทาง
- Pattern hydrophilic/hydrophobic regions
- รูปแบบบริเวณชอบ/รังเกียจน้ำ

---

### Common Pitfalls | ข้อผิดพลาดที่พบบ่อย

❌ **Incorrect:** Assuming contact angle is only material-dependent
✅ **Correct:** θ depends on surface roughness, chemistry, and dynamic conditions

❌ **Incorrect:** Using static θ for dynamic contact lines
✅ **Correct:** Apply dynamic contact angle models for moving interfaces

❌ **Incorrect:** Neglecting hysteresis (θA ≠ θR)
✅ **Correct:** Account for advancing (θA) and receding (θR) angles

---

## 4. Capillary Pressure | ความดัน Capillary

### What is Capillary Pressure? | ความดัน Capillary คืออะไร?

**Definition:** The pressure difference between non-wetting and wetting phases across a curved interface.

**นิยาม:** ผลต่างความดันระหว่างเฟสที่ไม่เปียกและเฟสที่เปียกข้ามผิวสัมผัสโค้ง

$$p_c = p_{nw} - p_w = \sigma \kappa$$

| Phase | Symbol | Example | ตัวอย่าง |
|-------|--------|---------|-----------|
| Non-wetting | pnw | Air in water | อากาศในน้ำ |
| Wetting | pw | Water in porous media | น้ำในสื่อทะลุได้ |

---

### Why is Capillary Pressure Important? | ทำไมความดัน Capillary สำคัญ?

**Applications | การประยุกต์ใช้:**

**Porous Media Flow | การไหลในสื่อทะลุได้:**
- Oil recovery from reservoirs
- การผลิตน้ำมันจากแหล่งกักเก็บ
- Groundwater transport in soil
- การเคลื่อนที่ของน้ำใต้ดินในดิน

**Microfluidics | ไมโครฟลูอิดิกส์:**
- Capillary-driven flow without pumps
- การไหลโดย capillary โดยไม่ต้องใช้ปั๊ม
- Passive fluid control
- การควบคุมฟลูอิดแบบ passive

**Fuel Cells | เซลล์เชื้อเพลิง:**
- Water management in gas channels
- การจัดการน้ำในช่องก๊าซ
- Prevent flooding or drying
- ป้องกันการท่วมหรือการแห้ง

---

### How to Calculate Capillary Pressure? | การคำนวณความดัน Capillary

**Example: Capillary Rise in a Tube | ตัวอย่าง: การยกตัวโดย capillary ในท่อ**

$$p_c = \rho g h = \frac{2\sigma \cos\theta}{R}$$

For water in a glass tube:
- R = 0.5 mm (tube radius)
- σ = 0.072 N/m (water-air)
- θ = 49° (water-glass)
- ρ = 1000 kg/m³ (water density)
- g = 9.81 m/s² (gravity)

**Calculation | การคำนวณ:**

$$p_c = \frac{2 \times 0.072 \times \cos(49°)}{0.0005} = \textbf{187 Pa}$$

$$h = \frac{p_c}{\rho g} = \frac{187}{1000 \times 9.81} = \textbf{19 mm}$$

**Practical Insight | ข้อเข้าใจ:**
- Smaller tubes → Higher capillary rise
- ท่อเล็กกว่า → ยกตัวสูงกว่า
- This is why paper towels absorb water
- นี่คือเหตุผลที่ผ้าเย็นรองน้ำ

---

## 5. Marangoni Effect | ปรากฏการณ์มารังโกนี

### What is the Marangoni Effect? | ปรากฏการณ์มารังโกนีคืออะไร?

**Definition:** Fluid flow induced by surface tension gradients along an interface, typically caused by temperature or concentration variations.

**นิยาม:** การไหลของฟลูอิดที่เกิดจากการกระจายตัวของความตึงผิวตามผิวสัมผัส โดยปกติเกิดจากการเปลี่ยนแปลงของอุณหภูมิหรือความเข้มข้น

**The Marangoni Stress:**

$$\tau_M = \nabla_s \sigma = \frac{d\sigma}{dT} \nabla_s T$$

| Component | Meaning | ความหมาย |
|-----------|---------|-----------|
| τM | Marangoni stress (N/m²) | ความเครียดมารังโกนี |
| ∇sσ | Surface tension gradient | ไกรเดียนต์ความตึงผิว |
| dσ/dT | Temperature coefficient of σ | สัมประสิทธิ์อุณหภูมิของ σ |
| ∇sT | Surface temperature gradient | ไกรเดียนต์อุณหภูมิผิว |

---

### Why is the Marangoni Effect Significant? | ทำไมปรากฏการณ์มารังโกนีสำคัญ?

**Physical Mechanism | กลไกทางกายภาพ:**

1. **Surface Tension Gradient:** ∇σ creates shear stress at interface
   - ไกรเดียนต์ความตึงผิวสร้างความเครียดเฉือนที่ผิวสัมผัส

2. **Flow Direction:** Fluid moves from low σ to high σ regions
   - ฟลูอิดไหลจากบริเวณที่มี σ ต่ำไปสูง σ สูง

3. **Circulation Patterns:** Creates toroidal vortices
   - สร้างวัตถุพาข้อมูลรูปทอรัส

**Temperature Dependence | การพึ่งพาอุณหภูมิ:**
$$\frac{d\sigma}{dT} < 0 \text{ (most fluids)}$$
- Higher T → Lower σ → Fluid flows away from hot regions
- อุณหภูมิสูง → σ ต่ำ → ฟลูอิดไหลออกจากบริเวณร้อน

**Key Applications | การประยุกต์ใช้หลัก:**

| Application | Effect | ผลกระทบ |
|-------------|--------|----------|
| **Welding** | Marangoni convection affects pool shape | การพาความร้อนมารังโกนีส่งผลต่อรูปร่างการหลอมละลาย |
| **Crystal Growth** | Defect formation in melts | การเกิดตำหนิในหลอมละลาย |
| **Microfluidics** | Droplet actuation without pumps | การขับเคลื่อนหยดโดยไม่ใช้ปั๊ม |
| **Space Applications** | Thermocapillary flow in microgravity | การไหล thermocapillary ในไร้น้ำหนัก |
| **Coating Processes** | Film thickness uniformity | ความสม่ำเสมอของความหนาฟิล์ม |

---

### How to Model Marangoni Flow? | การจำลองการไหลมารังโกนี

**Example 1: Thermocapillary Migration | ตัวอย่าง 1: การเคลื่อนที่ Thermocapillary**

For a temperature gradient ∇T = 100 K/m with dσ/dT = -1.5 × 10⁻⁴ N/(m·K):

```
Hot region (T↑) → σ↓ → Fluid pulled toward cold region
                 ↑
            Marangoni flow ←
                 ↓
Cold region (T↓) → σ↑ → Fluid pulled from hot region
```

**Velocity Scale Estimation:**
$$U_M \sim \frac{|d\sigma/dT| \nabla T L}{\mu}$$

For L = 1 mm, μ = 0.001 Pa·s:
$$U_M \approx \frac{1.5 \times 10^{-4} \times 100 \times 0.001}{0.001} = \textbf{0.015 m/s}$$

---

**Example 2: Welding Pool Convection | ตัวอย่าง 2: การพาความร้อนในการเชื่อม**

In welding (steel):
- ∇T ≈ 10⁶ K/m (extreme gradient)
- dσ/dT ≈ -3 × 10⁻⁴ N/(m·K)
- L ≈ 5 mm (pool size)
- μ ≈ 0.006 Pa·s (molten steel)

$$U_M \approx \frac{3 \times 10^{-4} \times 10^6 \times 0.005}{0.006} = \textbf{0.25 m/s}$$

**Practical Impact | ผลกระทบทางปฏิบัติ:**
- Marangoni convection dominates pool shape
- การพามารังโกนีครอบงำรูปร่างการหลอมละลาย
- Affects penetration depth and weld quality
- ส่งผลต่อความลึกการเจาะทะลุและคุณภาพการเชื่อม

---

**Example 3: Microfluidic Droplet Actuation | ตัวอย่าง 3: การขับเคลื่อนหยดไมโครฟลูอิดิกส์**

Thermocapillary droplet motion:
- Localized heating creates σ gradient
- การให้ความร้อนเฉพาะที่สร้างไกรเดียนต์ σ
- Droplet moves toward cold region
- หยดเคลื่อนที่ไปยังบริเวณเย็น
- Applications: Lab-on-a-chip devices
- การประยุกต์: อุปกรณ์ห้องปฏิบัติการบนชิป

---

### Common Pitfalls | ข้อผิดพลาดที่พบบ่อย

❌ **Incorrect:** Neglecting Marangoni effects in high-temperature gradients
✅ **Correct:** Always assess ∇sσ when ΔT > 10 K across interface

❌ **Incorrect:** Assuming σ is constant along interface
✅ **Correct:** Model σ(T) or σ(C) for accurate predictions

❌ **Incorrect:** Ignoring Marangoni in microgravity applications
✅ **Correct:** Marangoni dominates when buoyancy is suppressed

---

## 6. Dimensionless Numbers for Interfacial Phenomena | จำนวนไร้มิติ

### Capillary Number (Ca) | จำนวน Capillary

**What:** Ratio of viscous to surface tension forces

$$Ca = \frac{\mu U}{\sigma}$$

| Ca Range | Regime | ระบบ |
|----------|--------|------|
| Ca << 1 | Surface tension dominates | ความตึงผิวครอบงำ |
| Ca ≈ 1 | Balanced forces | แรงสมดุล |
| Ca >> 1 | Viscous forces dominate | ความหนืดครอบงำ |

**Example | ตัวอย่าง:** Water flowing at 0.1 m/s (μ = 0.001 Pa·s, σ = 0.072 N/m):
$$Ca = \frac{0.001 \times 0.1}{0.072} = \textbf{0.0014} \text{ (surface tension dominates)}$$

---

### Weber Number (We) | จำนวน Weber

**What:** Ratio of inertial to surface tension forces

$$We = \frac{\rho U^2 L}{\sigma}$$

| We Range | Effect | ผลกระทบ |
|----------|--------|----------|
| We < 1 | Surface tension maintains integrity | ความตึงผิวรักษาความสมบูรณ์ |
| We ≈ 1 | Onset of deformation | เริ่มเสียรูป |
| We > 1 | Inertia breaks interfaces (droplet formation) | เฉื่อยทำลายผิวสัมผัส |

**Example | ตัวอย่าง:** Water jet (U = 5 m/s, L = 0.01 m, ρ = 1000 kg/m³):
$$We = \frac{1000 \times 25 \times 0.01}{0.072} = \textbf{3472} \text{ (atomization regime)}$$

---

### Eötvös Number (Eo) | จำนวน Eötvös

**What:** Ratio of buoyancy to surface tension forces

$$Eo = \frac{\Delta\rho g L^2}{\sigma}$$

| Eo Range | Behavior | พฤติกรรม |
|----------|----------|-----------|
| Eo < 1 | Surface tension dominates (spherical bubbles) | ฟองกลม |
| Eo ≈ 1 | Transitional shapes | รูปร่างเปลี่ยน |
| Eo > 1 | Buoyancy deforms bubbles | ฟองเสียรูป |

**Example | ตัวอย่าง:** Air bubble in water (L = 0.01 m, Δρ = 1000 kg/m³):
$$Eo = \frac{1000 \times 9.81 \times 0.0001}{0.072} = \textbf{13.6} \text{ (deformed bubble)}$$

---

### Marangoni Number (Ma) | จำนวน Marangoni

**What:** Ratio of Marangoni to viscous forces

$$Ma = \frac{|d\sigma/dT| \Delta T L}{\mu \alpha}$$

| Component | Meaning |
|-----------|---------|
| dσ/dT | Surface tension temperature coefficient |
| ΔT | Temperature difference across interface |
| α | Thermal diffusivity |

| Ma Range | Regime |
|----------|--------|
| Ma < 1000 | Conduction dominates |
| Ma > 1000 | Marangoni convection significant |

---

## 7. OpenFOAM Implementation | การนำไปใช้ใน OpenFOAM

### Surface Tension Setup | การตั้งค่าความตึงผิว

**Constant Properties | ค่าคงที่:**

```cpp
// constant/transportProperties
phases (water air);

water
{
    transportModel  Newtonian;
    nu              [0 2 -1 0 0 0 0] 1e-06;
    rho             [1 -3 0 0 0 0 0] 1000;
}

air
{
    transportModel  Newtonian;
    nu              [0 2 -1 0 0 0 0] 1.48e-05;
    rho             [1 -3 0 0 0 0 0] 1;
}

// Surface tension
sigma   [1 0 -2 0 0 0 0] 0.072;
```

---

### Contact Angle Boundary Condition | เงื่อนไขขอบเขตมุมสัมผัส

**Static Contact Angle BC:**

```cpp
// 0/alpha.water
wall
{
    type            constantAlphaContactAngle;
    theta0          70;      // Static contact angle [degrees]
    uTheta          0;       // Dynamic contact angle model
    limit           0;       // Theta limit
}
```

**Dynamic Contact Angle BC:**

```cpp
wall
{
    type            dynamicAlphaContactAngle;
    theta0          70;      // Equilibrium angle
    uTheta          1;       // Use velocity-dependent model
    thetaA          110;     // Advancing angle
    thetaR          50;      // Receding angle
}
```

---

### CSF Force Calculation | การคำนวณแรง CSF

**In fvOptions (optional):**

```cpp
// constant/fvOptions
surfaceTension
{
    type            surfaceTensionForce;
    libs            ("libfvOptions.so");

    field           alpha.water;
    sigma           0.072;
}
```

**Curvature Calculation Note:**
OpenFOAM automatically computes curvature in VOF solvers using the CSF formulation.

---

## Key Takeaways | สรุปสำคัญ

### Core Concepts | แนวคิดหลัก

✓ **Young-Laplace Equation** connects curvature to pressure jump (Δp = σκ)
- Smaller bubbles → Higher pressure (ฟองเล็กมีความดันสูง)
- Fundamental for understanding interfacial equilibrium
- พื้นฐานสำหรับการเข้าใจสมดุลผิวสัมผัส

✓ **CSF Model** converts surface tension to volume force (Fσ = σκ∇α)
- Essential for VOF methods in OpenFOAM
- จำเป็นสำหรับวิธี VOF ใน OpenFOAM
- Enables surface tension calculation on fixed grids
- ช่วยให้คำนวณความตึงผิวบน grid คงที่ได้

✓ **Contact Angle** determines wettability (θ < 90° = hydrophilic)
- Critical for wall-bounded multiphase flows
- สำคัญสำหรับการไหลหลายเฟสที่มีผนัง
- Dynamic angles differ from static values
- มุมพลวัตแตกต่างจากค่าสถิต

✓ **Marangoni Effect** drives flow via σ gradients (∇sσ)
- Important in high-temperature or concentration gradients
- สำคัญในไกรเดียนต์อุณหภูมิหรือความเข้มข้นสูง
- Dominates in microgravity environments
- ครอบงำในสภาวไร้น้ำหนัก

✓ **Dimensionless Numbers** characterize regime:
  - **Ca = μU/σ** (viscous vs. surface tension)
  - **We = ρU²L/σ** (inertia vs. surface tension)
  - **Eo = ΔρgL²/σ** (buoyancy vs. surface tension)
  - **Ma** (Marangoni vs. viscous forces)

---

### Practical Guidelines | แนวทางปฏิบัติ

🔧 **Model Selection | การเลือกโมเดล:**
- Use CSF for VOF methods (`interFoam`, `interIsoFoam`)
- ใช้ CSF สำหรับวิธี VOF
- Apply dynamic contact angle for moving contact lines
- ใช้มุมสัมผัสพลวัตสำหรับเส้นสัมผัสเคลื่อนที่
- Include Marangoni terms for large ∇T or ∇C
- รวมเทอร์มมารังโกนีสำหรับ ∇T หรือ ∇C ขนาดใหญ่

🔧 **Numerical Stability | เสถียรภาพเชิงตัวเลข:**
- Refine mesh near interfaces (Δx << interface thickness)
- ละเอียด mesh บริเวณผิวสัมผัส
- Use interface compression schemes (`MULES`)
- ใช้สูตรบีบอัดผิวสัมผัส
- Monitor spurious currents (should be < 1% of characteristic velocity)
- ติดตามกระแสปลอม (ควร < 1% ของความเร็วลักษณะ)

🔧 **Validation | การตรวจสอบ:**
- Compare static bubble pressure with Young-Laplace prediction
- เปรียบเทียบความดันฟองสถิตกับการทำนายยัง-ลาปลาซ
- Verify capillary rise matches analytical solutions
- ตรวจสอบการยกตัว capillary ตรงกับวิธีแก้สมการ
- Check mass conservation (Σ α should be constant)
- ตรวจสอบการอนุรักษ์มวล (Σ α ควรคงที่)

---

## 🧠 Concept Check

<details>
<summary><b>1. Why do smaller bubbles have higher internal pressure?</b></summary>

**คำตอบ | Answer:**

From Young-Laplace equation: Δp = 2σ/R

- Radius R appears in denominator
- Smaller R → Larger Δp
- Example: R = 1 μm → Δp ≈ 144,000 Pa (~1.4 atm!)

**Physical implication:** Nano-bubbles require extreme pressures to form and are highly unstable.

**ผลทางกายภาพ:** ฟองนาโนจำเป็นต้องมีความดันสูงมากในการก่อตัวและมีความไม่เสถียรสูง

</details>

<details>
<summary><b>2. How does CSF convert surface tension to volume force?</b></summary>

**คำตอบ | Answer:**

The CSF formulation: Fσ = σκ∇α

1. **Surface tension (σ):** Material property
   - ความตึงผิว: คุณสมบัติวัสดุ

2. **Curvature (κ):** Calculated from ∇ · (∇α/|∇α|)
   - ความโค้ง: คำนวณจาก ∇α

3. **Volume fraction gradient (∇α):** Localizes force at interface
   - ไกรเดียนต์สัดส่วนปริมาตร: ทำให้แรงกระจุกตัวที่ผิวสัมผัส

**Key insight:** ∇α is nonzero ONLY at interface, so Fσ acts exactly where needed.

**ข้อเข้าใจสำคัญ:** ∇α ไม่เป็นศูนย์เฉพาะที่ผิวสัมผัส ดังนั้น Fσ ทำงานตรงตำแหน่งที่ต้องการ

</details>

<details>
<summary><b>3. When does the Marangoni effect become important?</b></summary>

**คำตอบ | Answer:**

Marangoni dominates when:
- **Large temperature gradients:** ∇sT > 10 K/m
- **High dσ/dT fluids:** -dσ/dT > 10⁻⁴ N/(m·K) (e.g., molten metals)
- **Microgravity:** Buoyancy suppressed (space applications)
- **Small length scales:** L < 1 mm (microfluidics)

**Example:** In welding, ∇T ≈ 10⁶ K/m creates Marangoni velocities > 1 m/s!

**ตัวอย่าง:** ในการเชื่อม ∇T ≈ 10⁶ K/m สร้างความเร็วมารังโกนี > 1 m/s!

</details>

<details>
<summary><b>4. A water droplet on Teflon has θ = 116°. Is it hydrophilic or hydrophobic?</b></summary>

**คำตอบ | Answer:**

**Hydrophobic** (ไม่เปียก / รังเกียจน้ำ)

**Reasoning | การให้เหตุผล:**
- θ > 90° indicates non-wetting behavior
- มุม > 90° แสดงพฤติกรรมไม่เปียก
- cosθ is negative → σSL > σSG
- Droplet beads up (surface tension dominates)
- หยดเกาะแตก (ความตึงผิวครอบงำ)

**Practical implication:** Teflon coatings are used for water-repellent surfaces.

**ผลทางปฏิบัติ:** การเคลือบเทฟลอนใช้สำหรับพื้นผิวกันน้ำ

</details>

<details>
<summary><b>5. What dimensionless number determines if a droplet breaks up?</b></summary>

**คำตอบ | Answer:**

**Weber number (We = ρU²L/σ)**

**Regimes | ระบบ:**
- We < 1: Surface tension maintains droplet integrity
- We ≈ 1: Onset of deformation
- We > 1: Inertia overcomes surface tension → Breakup

**Example:** Fuel atomization in engines requires We > 10-100 for fine droplets.

**ตัวอย่าง:** การฉีดน้ำมันเชื้อเพลิงในเครื่องยนต์ต้องการ We > 10-100 สำหรับหยดละเอียด

</details>

<details>
<summary><b>6. How does contact angle affect capillary rise?</b></summary>

**คำตอบ | Answer:**

From capillary rise equation: h = (2σ cosθ)/(ρgR)

- **θ < 90°:** cosθ > 0 → Positive rise (wetting)
- มุม < 90°: การยกตัวเป็นบวก (เปียก)
- **θ > 90°:** cosθ < 0 → Depression (non-wetting)
- มุม > 90°: การกดตัวเป็นลบ (ไม่เปียก)
- **θ = 90°:** cosθ = 0 → No capillary effect
- มุม = 90°: ไม่มีผล capillary

**Example:** Mercury (θ ≈ 140°) depresses in glass tubes instead of rising.

**ตัวอย่าง:** ปรอท (θ ≈ 140°) กดตัวในท่อกระจกแทนที่จะยกตัว

</details>

---

## 📖 Related Documentation

### Core Equations | สมการหลัก
- **Mass Conservation:** [01_Mass_Conservation.md](01_Mass_Conservation.md) — Interface kinematics
- **Momentum Conservation:** [02_Momentum_Conservation.md](02_Momentum_Conservation.md) — Interfacial forces

### Applied Topics | หัวข้อประยุกต์
- **Drag Forces:** [../04_INTERPHASE_FORCES/01_DRAG/02_Specific_Drag_Models.md](../04_INTERPHASE_FORCES/01_DRAG/02_Specific_Drag_Models.md) — Effect of surface tension on drag
- **Implementation:** [../06_IMPLEMENTATION/03_Model_Architecture.md](../06_IMPLEMENTATION/03_Model_Architecture.md) — CSF in OpenFOAM solvers

### External Resources | แหล่งข้อมูลภายนอก
- Brackbill, J. U., et al. (1992). "A continuum method for modeling surface tension." *Journal of Computational Physics*.
- Tryggvason, G., et al. (2011). *Direct Numerical Simulations of Gas-Liquid Multiphase Flows*. Cambridge University Press.