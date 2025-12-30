# Practical Workflow

> **ขั้นตอนการตั้งค่าและดำเนินการจำลอง Reacting Flow**

---

## 🎯 Learning Objectives

หลังจากอ่านบทนี้ คุณจะสามารถ:
- อธิบายวัตถุประสงค์และบทบาทของแต่ละไฟล์ในโครงสร้าง case สำหรับ reacting flow simulation
- ตั้งค่า species fields และ boundary conditions อย่างถูกต้อง
- กำหนด reaction mechanisms พร้อม Arrhenius parameters ที่เหมาะสม
- เลือกและกำหนดค่า combustion model ที่เหมาะสมกับปัญหา (laminar/EDC/PaSR)
- ดำเนินการจำลอง reactingFoam พร้อม monitoring convergence อย่างเหมาะสม
- ตรวจสอบและ validate ผลลัพธ์ด้วยเกณฑ์ mass conservation, energy balance และ visualization checklist
- วินิจฉัยและแก้ไขปัญหาที่พบบ่อยในการจำลอง reacting flow (divergence, mass fraction issues, temperature explosion)

---

## 3W Framework

### What
ขั้นตอนการ setup case และดำเนินการจำลองสำหรับปัญหา reacting flow ใน OpenFOAM ตั้งแต่การเตรียม mesh การกำหนด species และ reactions การเลือก combustion model ไปจนถึงการรันและตรวจสอบผลลัพธ์

### Why
Reacting flow simulation มีความซับซ้อนกว่า single-phase flow ทั่วไปเนื่องจาก:
- ต้องการการกำหนดค่า chemical species และ reaction mechanisms หลายไฟล์
- การเลือก combustion model ส่งผลต่อความแม่นยำและ computational cost
- การ monitoring convergence ต้องตรวจสอบทั้ง flow field และ chemical quantities
- ข้อผิดพลาดในการ setup มักนำไปสู่การ diverge หรือผลลัพธ์ที่ไม่สมเหตุสมผล

การเข้าใจ workflow ที่ถูกต้องจะช่วยลดเวลาในการ setup และเพิ่มความมั่นใจในความถูกต้องของผลลัพธ์

### How
1. **Setup โครงสร้างไฟล์ case** - สร้าง directory และไฟล์ที่จำเป็นทั้งหมด
2. **กำหนด species และ reaction mechanisms** - เขียน `constant/reactions` และ `constant/thermo.compressibleGas`
3. **ตั้งค่า boundary conditions** - กำหนด initial conditions สำหรับ flow field และ species fields
4. **เลือกและกำหนดค่า combustion model** - กำหนด `combustionProperties` และ `chemistryProperties`
5. **ดำเนินการจำลองและ monitoring** - รัน reactingFoam พร้อมตรวจสอบ convergence
6. **ตรวจสอบและ validate ผลลัพธ์** - ใช้ post-processing functions และ validation checklist

---

## 1. Case Setup Structure

### 1.1 Directory Organization

```
case/
├── 0/                           # Initial conditions
│   ├── U                        # Velocity field
│   ├── p                        # Pressure field
│   ├── T                        # Temperature field
│   ├── CH4, O2, CO2, H2O, N2    # Species mass fractions
│   └── Ydefault                 # Template boundary condition for species
├── constant/
│   ├── chemistryProperties      # Chemistry solver settings
│   ├── combustionProperties     # Combustion model selection
│   ├── reactions                # Species and reaction definitions
│   └── thermo.compressibleGas   # Thermodynamic properties
└── system/
    ├── controlDict              # Time control and output
    ├── fvSchemes                # Discretization schemes
    └── fvSolution               # Linear solver settings
```

### 1.2 File Purposes (คำอธิบายรายละเอียด)

| File | หน้าที่หลัก | รายละเอียด |
|------|-------------|-------------|
| **0/U** | Velocity field | กำหนดความเร็วของ fluid เริ่มต้น และ boundary conditions เช่น inlet velocity, outlet pressure |
| **0/p** | Pressure field | กำหนดความดันเริ่มต้น และ boundary conditions (ใช้ transonic หรือ incompressible ตาม compressibility) |
| **0/T** | Temperature field | กำหนดอุณหภูมิเริ่มต้นและ boundary conditions - สำคัญมากสำหรับ ignition |
| **0/CH4, O2, ...** | Species mass fractions | กำหนดสัดส่วนมวลของแต่ละ chemical species เริ่มต้น และ BCs ที่ inlet/outlet |
| **0/Ydefault** | BC template for species | กำหนด BC ร่วมสำหรับทุก species ช่วยลดการซ้ำซ้อนและลดความผิดพลาด |
| **constant/chemistryProperties** | Chemistry solver settings | ตั้งค่า ODE solver (method, tolerance, relaxation factors) สำหรับ chemical kinetics integration |
| **constant/combustionProperties** | Combustion model selection | เลือก combustion model (laminar/EDC/PaSR) และตั้งค่า parameters เฉพาะ model |
| **constant/reactions** | Species & reactions | รายชื่อ species ทั้งหมดในระบบ และ reaction mechanisms พร้อม Arrhenius parameters (A, Ta, β) |
| **constant/thermo.compressibleGas** | Thermodynamic properties | คุณสมบัติทางเทอร์โมไดนามิกส์ (Cp, H, S) และ formation enthalpy (Hf) สำหรับแต่ละ species |
| **system/controlDict** | Time control & output | ควบคุมเวลา (start, stop, deltaT), time step adjustment, write interval และ run-time selectable functions |
| **system/fvSchemes** | Discretization schemes | รูปแบบการ discretization สำหรับ gradient, divergence, Laplacian - ส่งผลต่อ stability และ accuracy |
| **system/fvSolution** | Linear solver settings | ตั้งค่า tolerances และ algorithms สำหรับ linear solvers ของ pressure, velocity, species ฯลฯ |

### 1.3 Interdependencies Between Files

```
constant/reactions (species list)
        ↓
        ├─→ constant/thermo.compressibleGas (thermo data สำหรับแต่ละ species)
        ├─→ 0/*species files (ICs & BCs สำหรับแต่ละ species)
        └─→ 0/Ydefault (BC template)

constant/combustionProperties (model selection)
        ↓
        ├─→ constant/chemistryProperties (ODE solver settings matching model)
        └─→ system/fvSolution (solver tolerances สำหรับ combustion)
```

---

## 2. Define Species

### 2.1 Species Declaration

```cpp
// constant/reactions
species
(
    CH4      // Methane - fuel
    O2       // Oxygen - oxidizer
    CO2      // Carbon dioxide - product
    H2O      // Water vapor - product
    N2       // Nitrogen - inert diluent
);
```

**Key Points:**
- **ชื่อต้องตรงกัน:** Species names ต้องตรงกับที่กำหนดใน `thermo.compressibleGas` ทุกตัว
- **ลำดับ:** ไม่มีความสำคัญทางเทคนิค แต่ควรจัดกลุ่มเพื่อความชัดเจน (fuel → oxidizer → products → inert)
- **Complex mechanisms:** สามารถมีได้มากกว่า 5 species สำหรับ detailed mechanisms (เช่น GRI-Mech 3.0 มี 53 species)
- **ห้ามซ้ำ:** อย่าระบุ species ซ้ำ - จะเกิด error ตอน runtime

### 2.2 Species Initial Conditions

```cpp
// 0/CH4 (example: fuel inlet region)
dimensions      [0 0 0 0 0 0 0];

internalField   uniform 0;

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 0.1;  // 10% CH4 by mass
    }
    
    outlet
    {
        type            inletOutlet;
        inletValue      uniform 0;
        value           uniform 0;
    }
    
    walls
    {
        type            zeroGradient;
    }
}
```

**หมายเหตุ:** สำหรับรายละเอียดเพิ่มเติมเกี่ยวกับ species BCs และการใช้ `Ydefault` ให้ดู [02_Species_Transport.md](02_Species_Transport.md) - ส่วนนี้มีคำอธิบายอย่างละเอียดเกี่ยวกับ BC types และ mass conservation

### 2.3 Common Boundary Condition Types for Species

| BC Type | เมื่อไรใช้ | ตัวอย่าง |
|---------|-------------|----------|
| **fixedValue** | กำหนดค่าสเปกซีส์คงที่ที่ inlet | Fuel inlet: `value uniform 0.1;` (10% CH4) |
| **inletOutlet** | Outlet ที่อาจมี backflow | ป้องกัน backflow ของ products |
| **zeroGradient** | Walls/symmetry (ไม่มี diffusion flux) | Adiabatic walls |
| **calculated** | ใช้ร่วมกับ compressible flow | อนุญาตให้ recalculate จาก equation |

---

## 3. Define Reactions

### 3.1 Single-Step Reaction Example

```cpp
// constant/reactions
reactions
(
    // CH4 + 2O2 -> CO2 + 2H2O
    methaneReaction
    {
        type    irreversibleArrheniusReaction;
        reaction    "CH4 + 2O2 = CO2 + 2H2O";
        
        // Arrhenius parameters
        A           1.5e11;     // Pre-exponential factor [m³/kmol.s]^(n-1)
        Ta          24370;      // Activation temperature [K] = Ea/R
    }
);
```

### 3.2 Arrhenius Rate Parameters

| Parameter | Symbol | Unit | ความหมาย | Typical Range |
|-----------|--------|------|----------|---------------|
| **A** | Pre-exponential factor | m³/kmol.s | ความถี่ของการชนระหว่างโมเลกุล | 10⁶ - 10¹⁴ |
| **Ta** | Activation temperature | K | อุณหภูมิที่ต้องใช้เพื่อเริ่มปฏิกิริยา = Ea/R | 1000 - 50000 |
| **β** | Temperature exponent | - | ค่าชดเชยอุณหภูมิใน rate equation | -0.5 - 2.0 |

**Reaction Rate:**
$$ k = A T^\beta \exp\left(-\frac{T_a}{T}\right) $$

**Interpretation:**
- **A สูง** = Reaction rate เร็ว (collision frequency สูง)
- **Ta สูง** = Reaction ต้องการอุณหภูมิสูงกว่า (activation energy สูง)
- **β > 0** = Rate เพิ่มขึ้นเมื่อ T เพิ่ม

### 3.3 Multi-Step Mechanism Example

```cpp
reactions
(
    // Reaction 1: CH4 + OH → CH3 + H2O
    reaction1
    {
        type    irreversibleArrheniusReaction;
        reaction    "CH4 + OH = CH3 + H2O";
        A           1.6e7;
        Ta          2460;
    }
    
    // Reaction 2: CH3 + O2 → CH2O + OH
    reaction2
    {
        type    irreversibleArrheniusReaction;
        reaction    "CH3 + O2 = CH2O + OH";
        A           5.0e11;
        Ta          15000;
    }
);
```

**หมายเหตุ:** สำหรับ detailed mechanisms หลายสิบ reactions ควรใช้ไฟล์ Chemkin format และ import ผ่าน `foamChemkinToOpenFOAM` - ดูรายละเอียดใน [05_Chemkin_Parsing.md](05_Chemkin_Parsing.md)

### 3.4 Reaction Stoichiometry Validation

**สมการ stoichiometry ต้อง balance:**
- **Mass balance:** จำนวนอะตอมของแต่ละ element ต้องเท่ากันฝั่ง reactants และ products
- **Charge balance:** (สำหรับ ionic reactions) จำนวนประจุต้องสมดุล

**ตัวอย่างการตรวจสอบ:**
```
CH4 + 2O2 → CO2 + 2H2O

C: 1 → 1 ✓
H: 4 → 4 ✓ (2 × 2)
O: 4 → 4 ✓ (2 + 2 × 1)
```

---

## 4. Combustion Model Selection

### 4.1 Model Configuration

```cpp
// constant/combustionProperties
combustionModel  laminar;    // Direct chemistry integration
// or
combustionModel  EDC;        // Eddy Dissipation Concept
// or
combustionModel  PaSR;       // Partially Stirred Reactor
```

### 4.2 Model Comparison

| Model | คำอธิบาย | เมื่อไรใช้ | Computational Cost | ข้อดี | ข้อเสีย |
|-------|-----------|-------------|-------------------|--------|---------|
| **laminar** | Direct chemistry integration, ไม่มี turbulence-chemistry interaction | • Laminar flames<br>• DNS<br>• Detailed mechanism validation<br>• Re < 1000 | Low | • ง่ายต่อการตั้งค่า<br>• แม่นยำสำหรับ laminar<br>• ใช้ detailed mechanisms ได้ | • ไม่เหมาะ turbulent flows<br>• Underpredict burning rate ใน turbulent |
| **EDC** | Eddy Dissipation Concept - fine structures ใน turbulent flow ทำ chemistry | • Turbulent non-premixed flames<br>• Industrial burners<br>• Moderate Damköhler (0.1 < Da < 10)<br>• Re > 4000 | Medium-High | • พิจารณา fine structures<br>• แม่นยำสำหรับ turbulent<br>• ใช้ detailed mechanisms ได้ | • ค่าใช้จ่ายสูง<br>• ตั้งค่าซับซ้อน |
| **PaSR** | Partially Stirred Reactor - simple turbulence-chemistry interaction | • Turbulent premixed flames<br>• Engineering applications<br>• Large-scale simulations | Medium | • รวดเร็วกว่า EDC<br>• ง่ายต่อการ converge<br>• เหมาะ large cases | • น้อยเกินไปบางสถานการณ์<br>• ขาด fine structure details |

### 4.3 Selecting the Right Model

**Decision Tree:**
```
Is Re < 1000? ──Yes──> Use laminar
       │
       No
       ↓
Is flame premixed? ──Yes──> Use PaSR (faster)
       │
       No
       ↓
Need detailed chemistry? ──Yes──> Use EDC
       │
       No
       ↓
Use PaSR (default)
```

### 4.4 Chemistry Solver Settings

```cpp
// constant/chemistryProperties
chemistryType
{
    solver          ode;
    method          Rosenbrock34;    // 2nd-3rd order adaptive
    tolerance       1e-9;            // Relative tolerance
    relTol          0.01;            // Absolute tolerance
}
```

**Available ODE Methods:**

| Method | Order | เมื่อไรใช้ | Stability |
|--------|-------|-------------|-----------|
| **Rosenbrock34** | 2-3 | General purpose, stiff systems | Good |
| **Radau5** | 5 | High accuracy requirements | Excellent |
| **Euler** | 1 | Testing, non-stiff | Poor |
| **speedCHEM** | - | Large mechanisms (>50 species) | Variable |

**หมายเหตุ:** สำหรับ detailed mechanisms (>50 species) ควรพิจารณาใช้ ISAT (In-situ Adaptive Tabulation) เพื่อเร่งความเร็ว:

```cpp
chemistryType
{
    solver          ISAT;
    tolerance       1e-3;
    maxTabSize      1e6;        // Maximum table entries
    retireTolerance 0.01;       // Retire old entries
}
```

---

## 5. Run Simulation

### 5.1 Complete Workflow

```bash
# 1. Generate mesh
blockMesh

# 2. Check mesh quality
checkMesh

# 3. Initialize fields (optional - ถ้ามี regions พิเศษ)
setFields -dict system/setFieldsDict

# 4. (Optional) Decompose for parallel
decomposePar

# 5. Run reactingFoam
# Serial:
reactingFoam > log.reactingFoam &
# Parallel:
mpirun -np 4 reactingFoam -parallel > log.reactingFoam &

# 6. Monitor convergence
tail -f log.reactingFoam

# 7. Post-process
paraFoam
```

### 5.2 Time Step Control

```cpp
// system/controlDict
application     reactingFoam;

startFrom       startTime;
startTime       0;

stopAt          endTime;
endTime         0.1;                    // [s]

deltaT          1e-5;                   // Initial time step [s]
adjustTimeStep  yes;

maxCo           0.8;                    // Max Courant number
maxDi          10;                     // Max diffusion number

writeControl    timeStep;
writeInterval   100;
```

### 5.3 Time Step Estimation

**Constraint 1: Courant-Friedrichs-Lewy (CFL) Condition**
$$ \Delta t < \frac{Co \cdot \Delta x}{u_{max}} $$

**Constraint 2: Diffusion Number**
$$ \Delta t < \frac{Di \cdot \Delta x^2}{D_{max}} $$

**Constraint 3: Chemistry Timescale (มักเป็น limiting factor)**
$$ \Delta t < \frac{0.1}{k_{chem}} = \frac{0.1}{A \cdot T^\beta \cdot \exp(-T_a/T)} $$

**Combined:**
$$ \Delta t < \min\left(\frac{Co \cdot \Delta x}{u}, \frac{Di \cdot \Delta x^2}{D}, \frac{0.1}{k_{chem}}\right) $$

**ตัวอย่าง:** สำหรับ methane-air flame:
- Flow timescale: τflow ≈ Δx/u ≈ 0.01 m / 10 m/s = **1 ms**
- Chemistry timescale: τchem ≈ 1/(1.5×10¹¹ × exp(-24370/2000)) ≈ **0.1 μs**

ดังนั้น chemistry controls Δt → เริ่มต้นที่ `1e-6` ถึง `1e-7` s

### 5.4 Initial Condition Strategies

**Strategy 1: Uniform Cold Flow**
```cpp
// 0/T
internalField   uniform 300;  // [K] ambient

// 0/CH4, 0/O2
internalField   uniform 0;
```
- ใช้เมื่อ: Auto-ignition จาก hot walls or spontaneous ignition
- ข้อดี: ง่าย, stable
- ข้อเสีย: อาจใช้เวลานานในการ ignite

**Strategy 2: Hot Spot Ignition**
```bash
# system/setFieldsDict
regions
(
    boxToCell
    {
        box (0 0 0) (0.01 0.01 0.01);
        fieldValues
        (
            volScalarFieldValue T 2000  // [K] spark temperature
            volScalarFieldValue CH4 0.1  // Fuel in ignition zone
        );
    }
);
```
- ใช้เมื่อ: Spark ignition, controlled ignition
- ข้อดี: Fast ignition, controlled location
- ข้อเสีย: ต้องกำหนด region อย่างแม่นยำ

**Strategy 3: Stratified Reactants**
```cpp
// Fuel at bottom, oxidizer at top
setFields -dict system/setFieldsDict
```
- ใช้เมื่อ: Non-premixed flames, diffusion flames
- ข้อดี: สมจริงสำหรับ diffusion combustion
- ข้อเสีย: ต้องการ careful mixing setup

---

## 6. Monitoring and Validation

### 6.1 Convergence Monitoring

```bash
# Monitor species residuals
grep 'O2' log.reactingFoam | tail -5

# Monitor temperature range
grep 'T max' log.reactingFoam | tail -5
grep 'T min' log.reactingFoam | tail -5

# Monitor continuity (mass conservation)
grep 'Continuity' log.reactingFoam | tail -5

# Monitor chemistry ODE solves
grep 'chemistry' log.reactingFoam | tail -5

# Monitor Courant number
grep 'Co' log.reactingFoam | tail -5
```

### 6.2 Interpretation Guidelines

| Quantity | Good Convergence | Potential Issues | Action Required |
|----------|------------------|------------------|-----------------|
| **Species residuals** | < 1e-6, monotonically decreasing | Oscillations > 1e-4 | Chemistry instability → ลด Δt หรือ relax tolerance |
| **Temperature max** | Stable or slowly changing peak T (หลัง ignite) | Spiking → T เพิ่มเร็วมาก | ลด Δt, ตรวจสอบ reactions, verify thermodynamics |
| **Heat release** | Smooth, positive, consistent with expected power | Negative values | Reaction direction ผิด หรือ thermodynamics error |
| **Continuity error** | < 1e-6 | High values > 1e-4 | Mass conservation issues → ตรวจ BCs, mesh quality |
| **Courant number** | < maxCo (default 0.8) | Exceeds maxCo frequently | Δt ใหญ่เกินไป → ใช้ adjustTimeStep |
| **Σ Yi** | 1.0 ± 0.01 throughout domain | Deviates > ±0.05 | BCs ไม่สอดคล้อง, numerical diffusion | ใช้ bounded schemes |

### 6.3 Physical Validation Checks

**1. Mass Conservation:**
$$ \sum_{i=1}^{n_s} Y_i = 1.0 \pm 0.01 $$

ตรวจสอบด้วย:
```bash
# ใน paraFoam
# Plot Y_CH4 + Y_O2 + Y_CO2 + Y_H2O + Y_N2 over time
# ควร ≈ 1.0 throughout domain
```

**2. Energy Balance:**
$$ \dot{Q}_{release} \approx \dot{m}_{fuel} \cdot LHV $$

ตรวจสอบ:
```bash
postProcess -func 'Qdot' -latestTime
# Integrate Qdot over domain ควร ≈ fuel flow rate × LHV
```

**3. Flame Temperature:**
- Adiabatic flame temperature สำหรับ methane-air: **Tad ≈ 2220 K**
- Actual flame temperature (with heat loss): **T ≈ 1800-2200 K**
- ถ้า T > 2500 K → ตรวจสอบ thermodynamic properties
- ถ้า T < 1500 K → ตรวจสอบว่า reaction กำลังเกิดหรือไม่

### 6.4 Post-Processing Functions

```bash
# Heat release rate [W/m³]
postProcess -func 'Qdot'

# Reaction rate [kg/m³.s]
postProcess -func 'reactionRate'

# Species mass fractions visualization
postProcess -func 'speciesMassFractions'

# Adiabatic flame temperature (theoretical)
postProcess -func 'adiabaticFlameT'

# Mixture fraction (useful for non-premixed)
postProcess -func 'mixtureFraction'

# Combustion efficiency
postProcess -func 'combustionEfficiency'
```

### 6.5 Visualization Checklist

ก่อนที่จะเชื่อถือผลลัพธ์:

- [ ] **Temperature field:** แสดง flame shape และ location ที่สมเหตุสมผล (ไม่แปลกปลอม)
- [ ] **Fuel consumption:** CH4 ลดลงใน combustion zone (จาก inlet → products)
- [ ] **Product formation:** CO2, H2O เพิ่มขึ้นใน flame region
- [ ] **Oxidizer depletion:** O2 ลดลงใน flame zone (สัดส่วนเหมาะสมกับ stoichiometry)
- [ ] **Heat release rate:** ตรงกับ expected power (ไม่เป็นค่าลบ หรือสูงผิดปกติ)
- [ ] **No unphysical values:** ไม่มี negative species, T → ∞, หรือ Y > 1
- [ ] **Smooth gradients:** Fields เปลี่ยนแบบ smooth (ไม่ oscillate รุนแรง)

### 6.6 Quantitative Validation Metrics

| Metric | Definition | Good Value |
|--------|-----------|------------|
| **Combustion efficiency** | ηc = (T - T_unburnt) / (Tad - T_unburnt) | > 0.9 |
| **Mass conservation error** | |Σ Yi - 1| | < 0.01 |
| **Energy imbalance** | |E_in - E_out| / E_in | < 0.05 |
| **Flame speed** | S_L = dx_flame / dt (compare to literature) | ±20% of theoretical |

---

## 7. Troubleshooting

### 7.1 Issue: Simulation Diverges Early

**Symptoms:**
```
Time = 0.001

diagonal:  Solving for CH4, Initial residual = 0.999, Final residual = 5.2e+12, No Iterations 99

--> FOAM FATAL ERROR: Maximum number of iterations exceeded
```

**Possible Causes:**
1. Time step too large for chemistry timescale
2. Incompatible initial conditions (e.g., fuel+oxidizer mixed everywhere → immediate explosion)
3. Incorrect Arrhenius parameters (rate too fast, Ta too low)
4. Mesh quality issues (high non-orthogonality)

**Diagnostic Commands:**
```bash
# Check time step
grep 'deltaT' log.reactingFoam | tail -10

# Check mesh quality
checkMesh > log.checkMesh
# Look for: "non-orthogonality > 70"

# Check reaction rates
grep 'reactionRate' log.reactingFoam | tail -5
```

**Solutions:**

**Solution 1: Reduce Time Step**
```cpp
// system/controlDict
deltaT  1e-7;  // Reduce from 1e-5
```

**Solution 2: Gradual Ignition**
```bash
# system/setFieldsDict - separate fuel and oxidizer initially
regions
(
    boxToCell
    {
        box (0 0 0) (0.01 0.01 0.01);
        fieldValues
        (
            volScalarFieldValue CH4 0.1   // Fuel only in zone 1
        );
    }
    boxToCell
    {
        box (0.01 0 0) (0.02 0.01 0.01);
        fieldValues
        (
            volScalarFieldValue O2 0.23    // Oxidizer only in zone 2
        );
    }
);
```

**Solution 3: Check Reaction Parameters**
```cpp
// constant/reactions - verify Ta is reasonable
A       1.5e11;    // OK
Ta      24370;     // OK (~2500 K activation)

// ถ้า Ta ต่ำเกินไป (< 5000):
// → ปฏิกิริยาเกิดเร็วเกินไป → explosion
```

**Solution 4: Improve Mesh**
```bash
# ใน blockMeshDict
//  Reduce non-orthogonality
//  Add grading near flame zone
//  Increase resolution in high-gradient regions
```

---

### 7.2 Issue: Species Mass Fractions Don't Sum to 1

**Symptoms:**
```
# In log file or paraFoam
sum(Yi) = 1.35  // หรือ 0.65, etc.
```

**Possible Causes:**
1. Boundary conditions ไม่ conserve mass (inlet ≠ outlet)
2. Numerical errors from advection scheme (upwind too diffusive)
3. Incorrect BC types (mixed fixedValue/inletOutlet)
4. Missing species in sum (some species not initialized)

**Solutions:**

**Solution 1: Use `correctPhi`**
```cpp
// system/controlDict
application     reactingFoam;
correctPhi      yes;    // Correct flux for consistency
```

**Solution 2: Check Boundary Condition Consistency**
```cpp
// 0/CH4, 0/O2, 0/CO2, ... - all should use same BC type
boundaryField
{
    inlet
    {
        type            fixedValue;     // Same for all species
        value           $internalField;
    }
    
    outlet
    {
        type            inletOutlet;    // Same for all species
        inletValue      uniform 0;
        value           uniform 0;
    }
}
```

**Solution 3: Enable Bounded Schemes**
```cpp
// system/fvSchemes
divSchemes
{
    div(phi,Yi_h)  Gauss limitedLinearV 1;  // Bounded scheme
    // หรือ
    div(phi,Yi_h)  Gauss upwind;            // Most stable
}
```

**Solution 4: Verify All Species Included**
```bash
# ตรวจสอบว่าทุก species ใน constant/reactions มีไฟล์ 0/species
ls -la 0/ | grep -E "(CH4|O2|CO2|H2O|N2)"
```

---

### 7.3 Issue: Temperature Explodes

**Symptoms:**
```
T max: 2847 K → 5423 K → 1.2e5 K → inf
```

**Possible Causes:**
1. Exothermic reaction with no heat removal (adiabatic + unrealistic)
2. Incorrect thermodynamic properties (Cp too small → enthalpy error)
3. Missing energy equation coupling
4. Wrong sign in formation enthalpy (Hf should be negative for fuels)

**Solutions:**

**Solution 1: Verify Formation Enthalpy**
```cpp
// constant/thermo.compressibleGas
species
{
    CH4
    {
        thermo  hConst;  // หรือ janaf, polynomial
        Hf      -74600;  // [J/kg] formation enthalpy - MUST be negative
        Cp      2200;    // [J/kg.K] specific heat
    }
    
    // Check: Hf for fuels < 0, products ~ 0
    // (Hf_CH4 = -74.6 MJ/kg, Hf_CO2 ≈ 0, Hf_H2O ≈ -13.4 MJ/kg for vapor)
}
```

**Solution 2: Add Heat Loss at Walls**
```cpp
// 0/T
boundaryField
{
    walls
    {
        type            externalWallHeatFlux;
        mode            coefficient;
        h               50;      // [W/m².K] heat transfer coefficient
        Ta              300;     // [K] ambient temperature
        thickness       0.01;    // [m] wall thickness (optional)
        kappa           50;      // [W/m.K] wall conductivity (optional)
    }
}
```

**Solution 3: Use Realistic Cp Values**
```cpp
// ใช้ janaf thermodynamics (temperature-dependent Cp)
species
{
    CH4
    {
        thermo  janaf;
        Hf      -74600;
        Cp_coeffs  (1000 5.1493 -0.01353 0.0);  // T-dependent
    }
}
```

**Solution 4: Check Energy Equation**
```bash
# ตรวจสอบว่า energy equation ถูก solve
grep 'Solving for T' log.reactingFoam | tail -5

# ถ้าไม่มี → ตรวจสอบ fvSolution
```

---

### 7.4 Issue: Flame Won't Ignite

**Symptoms:**
- No temperature rise (T ≈ initial T)
- Species unchanged (Y_CH4, Y_O2 ≈ constant)
- No heat release (Qdot ≈ 0)

**Possible Causes:**
1. Activation temperature too high (Ta > 30000 K)
2. Insufficient mixing (fuel and oxidizer in separate zones, not mixing)
3. Energy equation not solving or disabled
4. Wrong combustion model (laminar in highly turbulent flow)
5. Time step too large (chemistry not resolving)

**Solutions:**

**Solution 1: Add Hot Spot Ignition**
```cpp
// 0/T
internalField   uniform 300;  // [K] ambient

boundaryField
{
    ignitionZone
    {
        type            fixedValue;
        value           uniform 2000;  // [K] spark temperature
    }
    
    // หรือใช้ setFields
}
```

```bash
# system/setFieldsDict
regions
(
    sphereToCell
    {
        centre (0.01 0.01 0.01);
        radius 0.005;
        fieldValues
        (
            volScalarFieldValue T 2000
        );
    }
);
```

**Solution 2: Reduce Activation Temperature (Temporary)**
```cpp
// constant/reactions
methaneReaction
{
    type    irreversibleArrheniusReaction;
    reaction    "CH4 + 2O2 = CO2 + 2H2O";
    A           1.5e11;
    Ta          20000;  // Lower from 24370 K for testing
}
```
**⚠️ Warning:** ใช้เฉพาะ testing เท่านั้น - restore ค่าเดิมเมื่อ simulation converge

**Solution 3: Verify Combustion Model Selection**
```bash
grep 'combustionModel' constant/combustionProperties
# Output: combustionModel laminar; (or EDC, PaSR)
```

ถ้า flow is turbulent (Re > 4000):
```cpp
// constant/combustionProperties
combustionModel  EDC;  // หรือ PaSR
```

**Solution 4: Check Mixing**
```bash
# ใน paraFoam
# Plot mixture fraction or fuel mass fraction
# ตรวจสอบว่า fuel และ oxidizer mix กันหรือไม่
```

**Solution 5: Reduce Time Step**
```cpp
// system/controlDict
deltaT  1e-7;  // Chemistry may not resolve at larger Δt
```

---

### 7.5 Issue: Excessive Computational Time

**Symptoms:**
- Each time step takes >10 minutes
- Simulation ไม่ progress เร็วพอ

**Possible Causes:**
1. Detailed mechanism with >50 species
2. Small time step for chemistry stiffness
3. Excessive chemistry ODE tolerance (เคร่งเกินไป)
4. Inefficient ODE solver method

**Solutions:**

**Solution 1: Use Reduced Mechanism**
```
Full GRI-Mech 3.0: 53 species, 325 reactions
↓
Skeletal mechanism: 20-30 species
↓
Global mechanism: 5-10 species
```

ดู [05_Chemkin_Parsing.md](05_Chemkin_Parsing.md) สำหรับวิธี reduction

**Solution 2: Enable Chemistry Tabulation**
```cpp
// constant/chemistryProperties
chemistryType
{
    solver          ISAT;       // In-situ Adaptive Tabulation
    tolerance       1e-3;       // Tabulation tolerance
    maxTabSize      1e6;        // Max table entries
    retireTolerance 0.01;       // Retire old entries
}
```
**Speedup:** 10-100x สำหรับ mechanisms >20 species

**Solution 3: Relax ODE Tolerance**
```cpp
// constant/chemistryProperties
tolerance   1e-6;  // Was 1e-9 (looser)
relTol      0.05;  // Was 0.01
```
**Tradeoff:** Accuracy ↓ แต่ speed ↑ 10-100x

**Solution 4: Use Faster ODE Method**
```cpp
chemistryType
{
    solver          ode;
    method          Rosenbrock34;  // 2-3rd order, faster than Radau5
    // method          Radau5;      // 5th order, slower
}
```

**Solution 5: Coarse-Grain Parallelization**
```bash
# ใช้ cores มากขึ้น (ถ้ามี)
decomposePar -nproc 16
mpirun -np 16 reactingFoam -parallel
```

---

### 7.6 Validation Checklist

**Before Trusting Results:**

**1. Grid Independence**
- [ ] Run with refined mesh (2x resolution)
- [ ] Confirm <5% change in key quantities (T_max, flame position, combustion efficiency)
- [ ] Document mesh resolution used for final results

**2. Mass Conservation**
- [ ] `Σ Yi = 1 ± 0.01` throughout domain
- [ ] No systematic drift over time
- [ ] Mass flow rate at inlet ≈ outlet (steady state)

**3. Energy Balance**
- [ ] Heat release ≈ enthalpy change of reactants → products
- [ ] Energy imbalance < 5%
- [ ] Temperature range physically reasonable

**4. Comparison to Data**
- [ ] Flame temperature matches literature (±10%)
- [ ] Species profiles match experimental data (if available)
- [ ] Flame speed/shape aligns with known correlations

**5. Grid Convergence**
- [ ] Residuals monotonically decreasing (not oscillating)
- [ ] Linear solver convergence each time step

**6. Time Step Independence**
- [ ] Halving Δt changes results <2%
- [ ] Co < maxCo throughout simulation

**7. Physical Consistency**
- [ ] No unphysical values (Y < 0, Y > 1, T → ∞)
- [ ] Boundary conditions applied correctly
- [ ] Flame propagates in correct direction

---

## Quick Reference

| Step | Action | Command/File | Notes |
|------|--------|--------------|-------|
| 1 | Define species list | `constant/reactions` → `species()` | Must match thermo file |
| 2 | Write reaction mechanisms | `constant/reactions` → `reactions()` | Include A, Ta, β |
| 3 | Set thermo properties | `constant/thermo.compressibleGas` | Cp, Hf, S for each species |
| 4 | Choose combustion model | `constant/combustionProperties` | laminar/EDC/PaSR |
| 5 | Configure chemistry solver | `constant/chemistryProperties` | ODE method, tolerance |
| 6 | Set initial conditions | `0/*` files | U, p, T, species |
| 7 | Run simulation | `reactingFoam` | Serial or parallel |
| 8 | Monitor convergence | `grep` log file | Species, T, continuity |
| 9 | Post-process | `paraFoam`, `postProcess` | Qdot, reactionRate |
| 10 | Validate | Checklist above | Grid independence, conservation |

---

## 📋 Key Takeaways

1. **Case Structure:** Reacting flow ต้องการ species fields, chemistry/combustion properties, และ thermodynamic data เพิ่มเติมจาก standard flow case - แต่ละไฟล์มีบทบาทที่ชัดเจน

2. **Species & Reactions:** ต้องกำหนด species list และ reaction mechanisms อย่างชัดเจนใน `constant/reactions` พร้อม Arrhenius parameters (A, Ta, β) ที่ถูกต้อง - ชื่อต้องตรงกับ thermo file

3. **Combustion Model:** เลือก model ตาม flow regime:
   - `laminar` → laminar flames, DNS, detailed mechanism validation
   - `EDC` → turbulent non-premixed flames, industrial burners
   - `PaSR` → turbulent premixed flames, engineering applications (faster)

4. **Time Step:** Chemistry timescale (τchem) มักเป็น limiting factor - ใช้ `adjustTimeStep yes` และ `maxCo`, `maxDi` เพื่อ maintain stability - เริ่มต้นที่ `1e-6` ถึง `1e-7` s สำหรับ methane

5. **Validation:** ตรวจสอบ mass conservation (`Σ Yi = 1 ± 0.01`), energy balance (heat release ≈ ΔH), และ compare กับ experimental data/literature - ใช้ visualization checklist ก่อนเชื่อถือผลลัพธ์

6. **Monitoring:** Convergence ต้องตรวจสอบหลาย levels: linear solver residuals, species conservation, temperature stability, และ heat release rate - ใช้ interpretation guidelines เพื่อ identify issues

7. **Troubleshooting:** ปัญหาที่พบบ่อย ได้แก่ divergence (Δt ใหญ่เกิน, ผิดพลาดใน reactions), mass conservation issues (BCs ไม่สอดคล้อง), temperature explosion (Hf ผิด, Cp เล็กเกิน), และ slow convergence (mechanism ซับซ้อน, ODE tolerance เคร่ง)

8. **Workflow:** ทำตาม step-by-step workflow: setup files → define species/reactions → configure model → run simulation → monitor convergence → validate results → troubleshoot ถ้าจำเป็น

---

## 🧠 Concept Check

<details>
<summary><b>1. Ydefault ใช้ทำอะไรและมีประโยชน์อย่างไร?</b></summary>

**Ydefault** เป็น boundary condition template ที่ใช้กำหนด BC ร่วมกันสำหรับทุก species fields แทนที่จะต้องเขียนซ้ำในแต่ละ file (`0/CH4`, `0/O2`, `0/CO2`, ...) ช่วยลดความผิดพลาดและง่ายต่อการแก้ไข

**ตัวอย่างการใช้งาน:**
```cpp
// 0/Ydefault
dimensions      [0 0 0 0 0 0 0];

internalField   uniform 0;

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 0;
    }
    
    outlet
    {
        type            inletOutlet;
        inletValue      uniform 0;
        value           uniform 0;
    }
    
    walls
    {
        type            zeroGradient;
    }
}

// 0/CH4, 0/O2, 0/CO2, etc. จะสืบทอด BC นี้โดยอัตโนมัติ
// เพียงแต่ override เฉพาะ inlet values:
// 0/CH4: inlet value uniform 0.1 (10% CH4)
// 0/O2:  inlet value uniform 0.23 (23% O2)
```

**ข้อดี:**
- ลดการซ้ำซ้อน (DRY principle)
- ลดความผิดพลาดจากการ copy-paste
- แก้ไข BCs ทั้งหมดในที่เดียว

</details>

<details>
<summary><b>2. EDC vs laminar combustion model - เลือกใช้เมื่อไร?</b></summary>

| Model | เมื่อไรใช้ | Reynolds Number | Turbulence-Chemistry Interaction | Computational Cost |
|-------|-------------|-----------------|----------------------------------|-------------------|
| **laminar** | • Laminar flames<br>• Direct Numerical Simulation (DNS)<br>• Detailed mechanism validation<br>• Low Re flows | Re < 1000-2000 | None (direct integration) | Low |
| **EDC** | • Turbulent non-premixed flames<br>• Industrial burners<br>• Moderate Damköhler (0.1 < Da < 10)<br>• High Re | Re > 4000 | Yes (fine structures) | Medium-High |
| **PaSR** | • Turbulent premixed flames<br>• Engineering applications<br>• Large-scale simulations | Re > 4000 | Yes (simple model) | Medium |

**Guideline:**
- ถ้า `Re > 4000` หรือมี turbulence model (`k-ε`, `k-ω-SST`, LES) → ใช้ EDC หรือ PaSR
- ถ้า `Re < 2000` หรือทำ DNS → ใช้ laminar
- ถ้าต้องการ speed และยอมรับ accuracy ลดลง → ใช้ PaSR
- ถ้าต้องการ accuracy สูงสุด → ใช้ EDC

**Damköhler Number (Da):**
$$ Da = \frac{\tau_{flow}}{\tau_{chem}} = \frac{\text{flow timescale}}{\text{chemistry timescale}} $$

- `Da >> 1`: Fast chemistry (equilibrium) → ใช้ EDC
- `Da << 1`: Slow chemistry (frozen) → ใช้ laminar
- `Da ≈ 1`: Comparable scales → ใช้ EDC หรือ PaSR

</details>

<details>
<summary><b>3. ตรวจสอบ convergence ของ reacting flow simulation อย่างไร?</b></summary>

**3 Levels ของ Convergence:**

**1. Linear Solver Convergence** (per time step)
```bash
# Residuals ต่ำกว่า tolerance แต่ละ time step
grep "Final residual" log.reactingFoam | tail -10
# ดูว่า < 1e-6 หรือ tolerance ที่กำหนด
```

**2. Time-Accuracy Convergence**
```bash
# Monitor quantities ไม่เปลี่ยนมากเมื่อ time progress
grep 'T max' log.reactingFoam | tail -20
# ควร converge ไปยังค่าคงที่ (steady state) หรือ oscillate เล็กน้อย (periodic)

# Monitor species
grep 'Y_CH4' log.reactingFoam | tail -20
# ควร converge (steady) หรือ oscillate รอบๆ steady value
```

**3. Physical Convergence**
```bash
# Mass conservation
# Σ Yi = 1 ± 0.01 throughout domain
postProcess -func 'speciesMassFractions'
# ใน paraFoam: plot Y_CH4 + Y_O2 + Y_CO2 + Y_H2O + Y_N2

# Energy balance
# Temperature profile สมเหตุสมผล
# - Methane-air adiabatic flame temp: Tad ≈ 2220 K
# - Actual flame (with heat loss): T ≈ 1800-2200 K
grep 'T max' log.reactingFoam | tail -20

# Reaction rate
grep 'reactionRate' log.reactingFoam | tail -20
# ควร > 0 (positive heat release)
```

**Additional Checks:**

**4. Grid Convergence**
```bash
# Run 2-3 mesh resolutions
# Compare key quantities (T_max, flame position, efficiency)
# ความแตกต่าง < 5% ถ้า grid-independent
```

**5. Time Step Independence**
```bash
# Halve Δt (เช่น 1e-5 → 5e-6)
# Run simulation ใหม่
# Compare results < 2% difference
```

**Convergence Indicators:**
| Indicator | Good | Bad |
|-----------|------|-----|
| Species residuals | < 1e-6, decreasing | > 1e-4, oscillating |
| Temperature max | Stable or slowly changing | Spiking, erratic |
| Σ Yi | 1.0 ± 0.01 | Outside ±0.05 |
| Heat release | Positive, smooth | Negative, noisy |
| Courant number | < maxCo | Exceeds maxCo frequently |

</details>

<details>
<summary><b>4. ทำไม simulation ต้องลด time step มากกว่า standard flow case?</b></summary>

**Chemistry Timescale (τchem) vs Flow Timescale (τflow):**

$$ \tau_{chem} \approx \frac{1}{A \cdot T^\beta \cdot \exp(-T_a/T)} $$

$$ \tau_{flow} \approx \frac{\Delta x}{u} $$

สำหรับ methane oxidation (CH4 + 2O2 → CO2 + 2H2O):
- **τflow** ≈ Δx/u ≈ 0.01 m / 10 m/s = **1 ms** (0.001 s)
- **τchem** ≈ 1/(1.5×10¹¹ × exp(-24370/2000 K)) ≈ **0.1 μs** (1×10⁻⁷ s)

Time step ต้องเล็กกว่า timescale ที่เร็วที่สุด:
$$ \Delta t < \min(\tau_{flow}, \tau_{chem}) = \tau_{chem} $$

ดังนั้น Δt ≈ 0.1 × τchem ≈ **1e-7 to 1e-8 s** (initially)

**ใน controlDict:**
```cpp
deltaT          1e-6;           // Initial guess
adjustTimeStep  yes;            // Let solver adapt
maxCo           0.8;            // Flow CFL constraint
maxDi          10;             // Diffusion constraint

// Chemistry stiffness controls actual Δt
// ตัว solver จะลด Δt automatically ถ้า chemistry ไม่ converge
```

**Why Chemistry is Stiff:**
- Arrhenius rate ขึ้นอยู่กับ T อย่างรุนแรง: `exp(-Ta/T)`
- เมื่อ T เพิ่มจาก 1500 K → 2000 K:
  - Rate increases โดย factor ≈ exp(24370/1500) / exp(24370/2000) ≈ **1000x**
- ดังนั้น Δt ต้องเล็กมากเมื่อ T สูง

**Best Practice:**
1. Start small: `deltaT 1e-6` หรือ `1e-7`
2. Enable `adjustTimeStep yes`
3. Let solver increase Δt automatically when convergence allows
4. Monitor `Co` and `Di` in log file
5. Use chemistry tabulation (ISAT) ถ้า mechanism ใหญ่

**Speedup Strategies:**
- Use reduced mechanism (fewer species → less stiffness)
- Enable ISAT tabulation (10-100x faster)
- Relax ODE tolerance (accept small accuracy loss)
- Use PaSR instead of EDC (simpler model)

</details>

<details>
<summary><b>5. แก้ปัญหา "mass fractions don't sum to 1" อย่างไร?</b></summary>

**Diagnostic:**
```bash
# Check sum in log file
grep 'sum(Yi)' log.reactingFoam | tail -10

# Check in paraFoam
# Plot: Y_CH4 + Y_O2 + Y_CO2 + Y_H2O + Y_N2
# Should be 1.0 everywhere
```

**Root Causes & Solutions:**

**1. Boundary Condition Inconsistency**
```cpp
// ❌ WRONG: Different BC types
// 0/CH4
inlet   { type fixedValue; value uniform 0.1; }
// 0/O2
inlet   { type zeroGradient; }  // Inconsistent!

// ✅ CORRECT: Same BC type for all species
// 0/CH4, 0/O2, 0/CO2, ...
inlet
{
    type            fixedValue;
    value           $internalField;  // Override individually
}
```

**2. Flux Correction Disabled**
```cpp
// system/controlDict
application     reactingFoam;
correctPhi      yes;    // ✅ Enable flux correction
// correctPhi      no;     // ❌ Can cause mass imbalance
```

**3. Unbounded Numerical Scheme**
```cpp
// system/fvSchemes
divSchemes
{
    // ❌ Too diffusive (causes Y < 0 or Y > 1)
    div(phi,Yi_h)  Gauss upwind;
    
    // ✅ Bounded scheme
    div(phi,Yi_h)  Gauss limitedLinearV 1;
    
    // ✅ Most stable (but diffusive)
    div(phi,Yi_h)  Gauss upwind;
}
```

**4. Missing Species**
```bash
# Check if all species in constant/reactions have 0/ files
ls 0/ | grep -E "(CH4|O2|CO2|H2O|N2)"

# If missing, create:
cp 0/Ydefault 0/MISSING_SPECIES
```

**5. Time Step Too Large**
```cpp
// Reduce Δt if numerical errors accumulate
deltaT  5e-7;  // From 1e-6
```

**Validation:**
```bash
# Sum should be 1.0 ± 0.01
postProcess -func 'sumSpecies'  # Custom function, or:
# In paraFoam, use calculator:
// Y_sum = Y_CH4 + Y_O2 + Y_CO2 + Y_H2O + Y_N2
// Plot Y_sum over domain
```

</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

### Sequence Recommendation
```
00_Overview.md (ภาพรวม reacting flows ใน OpenFOAM)
    ↓
01_Reacting_Flow_Fundamentals.md (conservation equations, combustion terminology)
    ↓
02_Species_Transport.md (species boundary conditions, Ydefault usage)
    ↓
03_Chemistry_Models.md (ODE solvers, stiff systems, detailed chemistry)
    ↓
04_Combustion_Models.md (turbulence-chemistry interaction: EDC, PaSR)
    ↓
05_Chemkin_Parsing.md (importing detailed mechanisms from Chemkin format)
    ↓
06_Practical_Workflow.md ← (คุณอยู่ที่นี่ - การนำไปปฏิบัติ)
```

### Related Documents
- **ภาพรวม:** [00_Overview.md](00_Overview.md) - Overview of reacting flow capabilities in OpenFOAM
- **พื้นฐาน:** [01_Reacting_Flow_Fundamentals.md](01_Reacting_Flow_Fundamentals.md) - Conservation equations and combustion terminology
- **Species Transport:** [02_Species_Transport.md](02_Species_Transport.md) - Species boundary conditions and Ydefault usage (รายละเอียดเพิ่มเติม)
- **Chemistry Models:** [03_Chemistry_Models.md](03_Chemistry_Models.md) - ODE solvers, stiff systems, detailed chemistry (ODE solver settings)
- **Combustion Models:** [04_Combustion_Models.md](04_Combustion_Models.md) - Turbulence-chemistry interaction models (EDC, PaSR details)
- **Chemkin:** [05_Chemkin_Parsing.md](05_Chemkin_Parsing.md) - Importing detailed mechanisms from Chemkin format

### External Resources
- **OpenFOAM Guide:** [reactingFoam documentation](https://www.openfoam.com/documentation/guides/latest/doc/guide-applications-solvers-utilities-reacting-foam.html)
- **Combustion Theory:** Kuo, "Principles of Combustion" (2nd ed., 2005) - Chapter 3: Chemical Kinetics
- **Tutorial:** `tutorials/combustion/reactingFoam/RAS` in OpenFOAM installation
- **GRI-Mech:** [GRI-Mech 3.0](http://combustion.berkeley.edu/gri-mech/) - Detailed methane mechanism (53 species)
- **Chemkin:** [Chemkin Documentation](https://www.anys.com/products/chemistry) - For detailed mechanism format