# Advanced Boundary Conditions in OpenFOAM

> **BC ขั้นสูงสำหรับสถานการณ์พิเศษ**

---

## 🎯 Learning Objectives

หลังจากศึกษาบทนี้ คุณจะสามารถ:

1. **เลือกและใช้** Advanced BCs ที่เหมาะสมกับปัญหาที่ซับซ้อน
2. **Implement** Time-varying BCs (table, coded, CSV), Spatial profiles, และ Coupled BCs
3. **เข้าใจและใช้** Wall functions ที่เหมาะสมกับ mesh resolution
4. **จำแนกและใช้** Turbulence inlet BCs สำหรับ RANS vs LES
5. **สร้าง** Coupled regions สำหรับ conjugate heat transfer
6. **แก้ปัญหา** Common issues กับ advanced BCs

### Prerequisites
- ความเข้าใจ Basic BCs (fixedValue, zeroGradient, fixedFluxPressure) — ดู [05_Common_Boundary_Conditions_in_OpenFOAM.md](05_Common_Boundary_Conditions_in_OpenFOAM.md)
- ความเข้าใจ y+ และ near-wall treatment
- พื้นฐาน C++ syntax (สำหรับ coded BCs)

---

## 📋 Quick Use-Case Decision Table

| Use Case | Recommended BC | Complexity | When to Use |
|----------|----------------|------------|-------------|
| **Time-varying inlet (tabular data)** | `uniformFixedValue` + `table` | Low | Measurement data, transient experiments |
| **Complex time function** | `codedFixedValue` | High | Pulsating, sine, custom functions |
| **CSV/Excel data** | `uniformFixedValue` + `csvFile` | Medium | External experimental data |
| **Recycle outlet → inlet** | `mappedFixedValue` | Medium | Developing flow, recycling BC |
| **Velocity profile** | `fixedProfile` | Medium | Boundary layer profiles |
| **Fully developed pipe flow** | `codedFixedValue` (parabolic) | High | Hagen-Poiseuille flow |
| **General y+ mesh** | `nutUSpaldingWallFunction` | Low | Unknown y+, mixed mesh |
| **Low y+ (≤ 5)** | `nutLowReWallFunction` | Medium | Resolving viscous sublayer |
| **Standard y+ (30-300)** | `nutkWallFunction` | Low | Wall functions, high Re |
| **Conjugate heat transfer** | `mappedWall` + coupled T BC | High | Fluid-solid heat transfer |
| **Porous media** | `porousBafflePressure` | Low | Filters, screens |
| **Moving mesh (6-DOF)** | `sixDoFRigidBodyMotion` | High | Floating objects, FSI |
| **Oscillating surface** | `oscillatingVelocity` | Medium | Pistons, vibrations |
| **RANS turbulence inlet** | `turbulentInlet` | Low | RANS with fluctuations |
| **LES/DES inlet** | `turbulentDFSEMInlet` | High | High-fidelity LES |
| **Fan/Pump model** | `fan` | Low | Pressure jump devices |

---

## 🔍 What Are Advanced Boundary Conditions?

**Advanced Boundary Conditions** คือ BC types ที่ออกแบบมาสำหรับสถานการณ์ที่ซับซ้อนเหนือไปจาก fixedValue/zeroGradient พื้นฐาน:

- **Temporal complexity:** BCs ที่เปลี่ยนแปลงตามเวลา (transient data, periodic functions)
- **Spatial complexity:** BCs ที่มี profile ตามตำแหน่ง (boundary layers, pipe profiles)
- **Multi-region coupling:** BCs ที่เชื่อมระหว่าง fluid/solid regions
- **Physics-based models:** Wall functions, turbulence inlets, porous media
- **Dynamic boundaries:** Moving meshes, 6-DOF motion

---

## 💡 Why Use Advanced BCs?

**ปัญหาจริงมักไม่ใช่ fixedValue/zeroGradient ง่ายๆ**

| Challenge | Basic BC | Advanced BC |
|-----------|----------|-------------|
| Time-varying inlet | ❌ ไม่รองรับ | ✅ `uniformFixedValue`, `codedFixedValue` |
| Spatial profiles | ❌ ต้อง hardcode | ✅ `fixedProfile`, `mappedFixedValue` |
| Realistic turbulence | ❌ Random noise | ✅ `turbulentDFSEMInlet` |
| Fluid-solid coupling | ❌ ไม่รองรับ | ✅ `mappedWall` + coupled BC |
| Unknown y+ | ❌ ต้อง re-mesh | ✅ `nutUSpaldingWallFunction` |

**Benefits:**
- **ความแม่นยำ:** ใกล้เคียงสถานการณ์จริงมากกว่า
- **ประหยัดเวลา:** ไม่ต้อง modify solver หรือ re-mesh
- **ความยืดหยุ่น:** ปรับแต่งได้ตาม requirement

---

## 🛠️ How to Implement Advanced BCs

### 1. Time-Varying BCs

#### 1.1 Table-Based (uniformFixedValue)

> **ใช้เมื่อ:** มีข้อมูลเป็น time series (เช่น จาก measurement)

**What:** ใช้ table ของ (time, value) pairs และ interpolate เชิงเส้น

**Why:** ง่าย, ไม่ต้องเขียน code, เหมาะกับ experimental data

**How:**

```cpp
inlet
{
    type            uniformFixedValue;
    uniformValue    table
    (
        (0      (0 0 0))        // t=0: U = 0
        (1      (5 0 0))        // t=1: U = 5 m/s
        (5      (10 0 0))       // t=5: U = 10 m/s
        (10     (10 0 0))       // t=10: U = 10 m/s (คงที่)
    );
    value           uniform (0 0 0);    // Initial value
}
```

**Notes:**
- Linear interpolation ระหว่าง data points
- Extends last value หลังจาก final time

---

#### 1.2 Expression-Based (codedFixedValue)

> **ใช้เมื่อ:** ต้องการ function ที่ซับซ้อน (sine, exponential, ฯลฯ)

**What:** เขียน C++ code โดยตรงใน BC file และ compile on-the-fly

**Why:** ไม่ต้อง compile solver ใหม่, ยืดหยุ่นมาก

**How:**

```cpp
inlet
{
    type    codedFixedValue;
    value   uniform (0 0 0);              // Initial guess
    name    pulsatingInlet;               // Unique name สำหรับ compile

    code
    #{
        // Get current time
        scalar t = this->db().time().value();
        
        // Parameters
        scalar U0 = 10.0;                          // Mean velocity [m/s]
        scalar freq = 0.5;                         // Frequency [Hz]
        scalar amplitude = 0.3;                    // Relative fluctuation
        
        // Calculate velocity: U = U0 * (1 + A * sin(2πft))
        vectorField& field = *this;
        scalar U_x = U0 * (1 + amplitude * sin(2*constant::mathematical::pi*freq*t));
        
        // Assign to field
        field = vector(U_x, 0, 0);
    #};
}
```

> **⚠️ Important:** ใช้ `constant::mathematical::pi` แทน `M_PI`
> - `M_PI` อาจไม่มีในทุกระบบ/standard
> - `constant::mathematical::pi` เป็น OpenFOAM constant ที่ใช้ได้เสมอ

**Performance:** Compile on-the-fly ตอนเริ่ม run (delay ไม่กี่วินาที)

---

#### 1.3 CSV File Input

> **ใช้เมื่อ:** มีข้อมูลจาก external source (Excel, experiment)

**What:** อ่าน CSV file และ map columns ไปยัง field components

**Why:** ใช้ data จาก measurement/simulation อื่นๆ โดยตรง

**How:**

```cpp
inlet
{
    type            uniformFixedValue;
    uniformValue    csvFile;
    uniformValueCoeffs
    {
        nHeaderLine     1;              // ข้าม header กี่บรรทัด
        refColumn       0;              // Column เวลา (0-based)
        componentColumns (1 2 3);       // Columns สำหรับ U_x, U_y, U_z
        separator       ",";            // Delimiter
        fileName        "inlet_data.csv";
    }
    value           uniform (0 0 0);
}
```

**CSV Format:**
```csv
time, U_x, U_y, U_z
0, 0, 0, 0
0.5, 2.5, 0, 0
1.0, 5.0, 0, 0
...
```

---

### 2. Spatial Profiles

#### 2.1 Profile from CSV (fixedProfile)

> **ใช้เมื่อ:** มี velocity profile เป็น function ของตำแหน่ง

**What:** Map spatial coordinate → value จาก CSV

**Why:** เหมาะสำหรับ experimental profile data

**How:**

```cpp
inlet
{
    type    fixedProfile;
    profile csvFile;
    profileCoeffs
    {
        nHeaderLine 1;
        refColumn   0;              // y-coordinate
        componentColumns (1);       // U_x(y)
        separator   ",";
        fileName    "velocity_profile.csv";
    }
    direction   (0 1 0);            // Profile varies in y
    origin      (0 0 0);            // Reference point
}
```

---

#### 2.2 Mapped from Another Patch (mappedFixedValue)

> **ใช้เมื่อ:** ต้องการ map ค่าจากที่อื่น (outlet → inlet หรือ internal plane)

**What:** Copy/couple values จาก neighbor patch หรือ internal face zone

**Why:** Recycling BC, periodic flows, developing boundary layers

**How:**

```cpp
inlet
{
    type            mappedFixedValue;
    interpolationScheme cellPoint;   // Interpolation method
    setAverage      false;           // Adjust average?
    average         (0 0 0);         // Target average
    value           uniform (0 0 0);
}
```

**Configuration (polyMesh/boundary):**
```cpp
inlet
{
    type            mappedPatch;
    sampleMode      nearestPatchFace;
    samplePatch     outlet;          // Source patch
    sampleRegion    region0;         // Source region
}
```

---

#### 2.3 Parabolic Profile (coded)

> **ใช้สำหรับ:** Fully developed pipe flow (Hagen-Poiseuille)

**What:** Implement parabolic velocity profile: $u(r) = U_{max}(1 - r^2/R^2)$

**Why:** Laminar pipe flow, ทางออกที่แม่นยำกว่า uniform

**How:**

```cpp
inlet
{
    type    codedFixedValue;
    value   uniform (0 0 0);
    name    parabolicInlet;

    code
    #{
        const fvPatch& p = this->patch();
        const vectorField& Cf = p.Cf();              // Face centers

        scalar R = 0.01;        // Pipe radius [m]
        scalar Umax = 1.0;      // Centerline velocity [m/s]

        vectorField& field = *this;
        forAll(field, faceI)
        {
            // Calculate radial distance from pipe centerline
            // Assuming pipe aligned along x-axis, centered at (0, 0, 0)
            scalar r = sqrt(sqr(Cf[faceI].y()) + sqr(Cf[faceI].z()));

            // Parabolic profile: u(r) = Umax * (1 - r²/R²)
            field[faceI] = vector(Umax*(1 - sqr(r/R)), 0, 0);
        }
    #};
}
```

**Physics:** Hagen-Poiseuille flow สำหรับ laminar, fully developed pipe

> **⚠️ Correction:** เวอร์ชันก่อนหน้าใช้ `mag(Cf[faceI].y())` ซึ่งถือเฉพาะ component-y เท่านั้น
> เวอร์ชันที่ถูกต้อง: `scalar r = sqrt(sqr(Cf[faceI].y()) + sqr(Cf[faceI].z()));`

---

### 3. Wall Functions

#### 3.1 Decision Tree

```
Need Wall Treatment
│
├─ y+ known and controlled
│  ├─ y+ ≤ 5 (Low-Re)
│  │  └─ nutLowReWallFunction (resolve viscous sublayer)
│  ├─ 30 ≤ y+ ≤ 300 (Standard)
│  │  └─ nutkWallFunction (log-law)
│  └─ y+ outside range
│     └─ Re-mesh!
│
└─ y+ unknown or variable
   └─ nutUSpaldingWallFunction (all y+)
```

#### 3.2 Standard Wall Functions (30 < y+ < 300)

**What:** Log-law based wall functions สำหรับ high-Re turbulence

**Why:** ประหยัด cells (ไม่ต้อง resolve viscous sublayer)

**How:**

| Field | BC Type | Physics |
|-------|---------|---------|
| `nut` | `nutkWallFunction` | ν_t จาก log-law |
| `k` | `kqRWallFunction` | k ใช้ค่าจาก cell ใกล้ผนัง |
| `epsilon` | `epsilonWallFunction` | ε จาก equilibrium assumption |
| `omega` | `omegaWallFunction` | ω สำหรับ k-ω models |

```cpp
wall
{
    type            nutkWallFunction;
    value           uniform 0;
}
```

**Prerequisites:** 30 < y+ < 300 ทั่วทั้งผนัง

---

#### 3.3 Low-Re Wall Treatment (y+ < 5)

**What:** Resolve viscous sublayer โดยตรง (no wall functions)

**Why:** ความแม่นยำสูง, จำเป็นสำหรับ heat transfer, separation

**How:**

| Field | BC Type | Physics |
|-------|---------|---------|
| `nut` | `nutLowReWallFunction` | ν_t → 0 ที่ผนัง |
| `k` | `kLowReWallFunction` | k → 0 ที่ผนัง |
| `epsilon` | `epsilonLowReWallFunction` | ε จาก viscous region |
| `omega` | `omegaBlendedWallFunction` | Auto-blend low/high-Re |

```cpp
wall
{
    type            nutLowReWallFunction;
    value           uniform 0;
}
```

**Prerequisites:** y+ < 5, mesh ละเอียดมาก

---

#### 3.4 Scalable Wall Functions (All y+)

**What:** Spalding's law ที่ blend viscous + log-law regions smoothly

**Why:** ไม่ต้องกังวลเรื่อง y+, ใช้ได้กับทุก mesh resolution

**How:**

```cpp
wall
{
    type    nutUSpaldingWallFunction;
    value   uniform 0;
}
```

**Benefits:**
- ✅ ใช้ได้ทุก y+ (automatic blending)
- ✅ ไม่ต้อง re-mesh ถ้า y+ เปลี่ยน
- ✅ Smooth transition ระหว่าง regions

**Recommendation:** ใช้เป็น default สำหรับ cases ที่ไม่แน่ใจ y+

---

### 4. Coupled BCs (Multi-Region)

#### 4.1 Conjugate Heat Transfer (mappedWall)

> **ใช้เมื่อ:** มี solid และ fluid regions ติดกัน

**What:** Couple temperature และ heat flux ระหว่าง regions

**Why:** Fluid + Solid ต้อง "คุยกัน" — T ต่อเนื่อง, q เท่ากันที่ interface

**How:**

**Step 1: Configure patch type (fluid/constant/polyMesh/boundary)**
```cpp
wall
{
    type            mappedWall;
    sampleMode      nearestPatchFace;
    sampleRegion    solid;              // ชื่อ solid region
    samplePatch     wall;               // Patch ใน solid ที่จับคู่
}
```

**Step 2: Temperature BC (Fluid side - 0/T)**
```cpp
wall
{
    type            compressible::turbulentTemperatureCoupledBaffleMixed;
    Tnbr            T;                  // ชื่อ T field ใน neighbor region
    value           uniform 300;        // Initial guess [K]
}
```

**Step 3: Temperature BC (Solid side - solid/0/T)**
```cpp
wall
{
    type            compressible::turbulentTemperatureCoupledBaffleMixed;
    Tnbr            T;                  // ชื่อ T field ใน neighbor region (fluid)
    value           uniform 300;
}
```

**Why "Mixed"?**
- ผสม Dirichlet (fixed T) + Neumann (fixed flux) ตาม thermal resistance
- ให้ T continuous และ q เท่ากันที่ interface

---

#### 4.2 Region Coupling (regionCouple)

```cpp
wall
{
    type    regionCouple;
    Tnbr    T;
    value   uniform 300;
}
```

**Usage:** CHT, FSI, multi-region conjugate problems

---

### 5. Porous Media

#### 5.1 Porous Baffle (porousBafflePressure)

> **ใช้สำหรับ:** Filter, screen, ตะแกรง

**What:** Model pressure drop ผ่าน porous media

**Why:** ไม่ต้อง mesh ภายใน porous media, ใช้ empirical correlations

**How:**

```cpp
baffle
{
    type    porousBafflePressure;
    D       1000;       // Darcy coefficient [1/s²] - viscous resistance
    I       0.5;        // Inertial coefficient [1/m] - form drag
    length  0.1;        // Baffle thickness [m]
    value   uniform 0;
}
```

**Physics:** Pressure drop: $\Delta p = \left(D\mu|U| + \frac{I\rho|U|^2}{2}\right) \cdot L$

- **D term:** Viscous resistance (dominant at low Re)
- **I term:** Inertial resistance (dominant at high Re)

---

### 6. Moving Mesh

#### 6.1 6-DOF Rigid Body (sixDoFRigidBodyMotion)

> **ใช้สำหรับ:** Floating objects, FSI

**What:** 6-degree-of-freedom rigid body dynamics

**Why:** Objects ที่เคลื่อนที่/หมุนอย่างอิสระภายใต้ forces

**How:**

```cpp
movingBody
{
    type            sixDoFRigidBodyMotion;
    mass            1.0;                    // Mass [kg]
    centreOfMass    (0 0 0);                // Initial position [m]
    momentOfInertia (1 1 1);                // Moments [kg·m²]
    patches         (body);                 // Patches that move together
    
    constraints     ();                     // Motion constraints
    restraints      ();                     // Springs, dampers
    
    // External forces (optional)
    // ...
}
```

**Applications:** Ships, floating bodies, wind turbines, FSI

---

#### 6.2 Oscillating Velocity (oscillatingVelocity)

> **ใช้สำหรับ:** Piston, vibrating surface

**What:** Harmonic oscillation: $x(t) = A \sin(\omega t)$

**Why:** Pistons, pumps, vibrating boundaries

**How:**

```cpp
piston
{
    type        oscillatingVelocity;
    amplitude   (0 0 0.01);       // Amplitude [m]
    omega       6.28;             // Angular frequency [rad/s] = 2π × frequency
    value       uniform (0 0 0);
}
```

**Parameters:**
- `amplitude`: Maximum displacement
- `omega`: Angular frequency = 2πf [rad/s]

---

### 7. Turbulence Inlet

#### 7.1 Decision: RANS vs LES

| Requirement | RANS | LES/DES |
|-------------|------|---------|
| Inlet fluctuations | Simple | Realistic structures |
| BC type | `turbulentInlet` | `turbulentDFSEMInlet` |
| Cost | Low | High |
| Accuracy | Moderate | High |

---

#### 7.2 RANS Turbulence Inlet (turbulentInlet)

**What:** Random velocity fluctuations บน mean flow

**Why:** RANS ที่ต้องการ turbulence intensity ที่ inlet

**How:**

```cpp
inlet
{
    type                turbulentInlet;
    fluctuationScale    (0.1 0.1 0.1);      // Relative fluctuation magnitude (10%)
    referenceField      uniform (10 0 0);   // Mean velocity [m/s]
    value               uniform (10 0 0);
}
```

**Notes:**
- Random noise (no spatial correlation)
- เหมาะสำหรับ RANS ที่ไม่ต้องการ resolved structures

---

#### 7.3 LES Inlet (turbulentDFSEMInlet / DFSEM)

**What:** Digital Filter Synthetic Eddy Method — สร้าง synthetic turbulent eddies

**Why:** LES/DES ต้องการ realistic turbulent structures ที่มี spatial correlation

**How:**

```cpp
inlet
{
    type    turbulentDFSEMInlet;
    delta   0.005;              // Boundary layer thickness [m]
    nCellPerEddy    5;          // Resolution of synthetic eddies
    mapMethod       minDistance;
    value           uniform (10 0 0);
}
```

**Why DFSEM ดีกว่า turbulentInlet?**
- ✅ สร้าง synthetic eddies ที่มี spatial correlation
- ✅ Realistic turbulent structures ตั้งแต่ inlet
- ✅ Structures survive ไปใน domain (ไม่ dissipate ทันที)

**Applications:** LES, DES, high-fidelity turbulence simulations

---

### 8. Fan/Pump

#### 8.1 Fan Curve (fan)

> **ใช้สำหรับ:** Model fan หรือ pump เป็น pressure jump

**What:** Pressure jump ที่เป็น function ของ flow rate

**Why:** Real fans: ΔP ลดลงเมื่อ flow rate เพิ่ม

**How:**

```cpp
fan
{
    type        fan;
    fanCurve    table
    (
        (0      100)        // Q = 0 m³/s → ΔP = 100 Pa
        (0.1    90)         // Q = 0.1 m³/s → ΔP = 90 Pa
        0.2    50)         // Q = 0.2 m³/s → ΔP = 50 Pa
        (0.3    0)          // Q = 0.3 m³/s → ΔP = 0 Pa (max flow)
    );
    value       uniform 0;
}
```

**Data source:** Manufacturer datasheet (performance curves)

---

## ⚡ Performance Considerations

| BC Type | Runtime Overhead | Memory | Notes |
|---------|------------------|--------|-------|
| `uniformFixedValue` (table) | Low | Low | Linear interpolation |
| `codedFixedValue` | **First run:** Compile (5-10s) <br> **Subsequent:** Low | Low | Dynamic code in `dynamicCode/` |
| `csvFile` | Low | Low | File I/O at start |
| `mappedFixedValue` | Medium | Medium | Interpolation every timestep |
| `fixedProfile` | Low | Low | Interpolation at start |
| `nutUSpaldingWallFunction` | Low (+5-10%) | Low | Additional calculations |
| `turbulentDFSEMInlet` | **High** (+20-50%) | Medium | Synthetic eddy generation |
| `sixDoFRigidBodyMotion` | High | Medium | Mesh motion + dynamics |

**Tips:**
- `codedFixedValue`: Compile overhead ครั้งแรกเท่านั้น
- `turbulentDFSEMInlet`: ใช้เฉพาะ khi necessary (LES)
- `nutUSpaldingWallFunction`: Negligible overhead vs `nutkWallFunction`

---

## 📚 Concept Check

<details>
<summary><b>1. codedFixedValue compile เมื่อไหร่?</b></summary>

**Compile on-the-fly** เมื่อเริ่ม run ครั้งแรก:
- มี delay เล็กน้อย (5-10 วินาที)
- สะดวก: ไม่ต้อง recompile solver
- Code เก็บใน `dynamicCode/` folder
- Subsequent runs: ไม่ต้อง compile ใหม่

**ข้อควรระวัง:** ตรวจ syntax error ก่อน run! Compile errors จะหยุด simulation
</details>

<details>
<summary><b>2. nutUSpaldingWallFunction ดีกว่า nutkWallFunction อย่างไร?</b></summary>

| | nutkWallFunction | nutUSpaldingWallFunction |
|-|------------------|--------------------------|
| y+ range | 30-300 เท่านั้น | **ใช้ได้ทุก y+** |
| Physics | Log-law only | Blend viscous + log-law |
| Flexibility | ต้อง mesh ให้ได้ y+ ถูกต้อง | Mesh หยาบ/ละเอียดก็ใช้ได้ |
| Robustness | ❌ Fails ถ้า y+ ผิด | ✅ Robust |

**แนะนำ:** ใช้ `nutUSpaldingWallFunction` เป็น default สำหรับ cases ที่ y+ ไม่แน่นอน
</details>

<details>
<summary><b>3. Conjugate heat transfer ต้องใช้ BC อะไร?</b></summary>

**ทั้งสอง regions ต้องจับคู่กัน:**

1. **Patch type:** `mappedWall` (ทั้งสองฝั่งใน `polyMesh/boundary`)
2. **Temperature BC (Fluid):** `compressible::turbulentTemperatureCoupledBaffleMixed`
3. **Temperature BC (Solid):** `compressible::turbulentTemperatureCoupledBaffleMixed`

**ทำไม `Mixed`?**
- ผสม Dirichlet (fixed T) + Neumann (fixed flux) ตาม thermal resistance
- ให้ T continuous และ q เท่ากันที่ interface
- Handle ทั้ง conduction และ convection resistances
</details>

<details>
<summary><b>4. DFSEM ต่างจาก turbulentInlet อย่างไร?</b></summary>

| | turbulentInlet | turbulentDFSEMInlet (DFSEM) |
|-|----------------|----------------------------|
| Fluctuations | Random noise | Synthetic eddies |
| Spatial correlation | ❌ ไม่มี | ✅ มี (realistic) |
| Temporal correlation | ❌ No | ✅ Yes |
| ใช้กับ | RANS | LES/DES |
| Cost | ต่ำ | สูงกว่า (+20-50%) |
| Realism | Low | High |

**ทำไม DFSEM ดีกว่าสำหรับ LES?**
- LES ต้องการ resolved turbulent structures
- Random noise จะ dissipate หลัง inlet (unphysical)
- DFSEM สร้าง structures ที่ survive ไปใน domain
- Correct spatial + temporal correlations
</details>

<details>
<summary><b>5. เมื่อไหร่ใช้ fixedProfile vs codedFixedValue?</b></summary>

| Criteria | fixedProfile | codedFixedValue |
|----------|--------------|-----------------|
| Data source | CSV file | Mathematical function |
| Complexity | Low | Medium-High |
| Maintenance | Edit CSV | Edit C++ code |
| Flexibility | Low (discrete data) | High (any function) |

**Guidelines:**
- ใช้ `fixedProfile`: มี experimental data เป็น CSV
- ใช้ `codedFixedValue`: รู้สูตรทางคณิตศาสตร์ (parabolic, power law)
</details>

---

## 🔗 Cross-References

### Related Files in This Module
- **Previous:** [05_Common_Boundary_Conditions_in_OpenFOAM.md](05_Common_Boundary_Conditions_in_OpenFOAM.md) — Basic BCs (fixedValue, zeroGradient)
- **Next:** [07_Troubleshooting_Boundary_Conditions.md](07_Troubleshooting_Boundary_Conditions.md) — Debugging BC issues
- **See Also:** [03_Selection_Guide_Which_BC_to_Use.md](03_Selection_Guide_Which_BC_to_Use.md) — Decision trees for BC selection

### Prerequisite Knowledge
- **Classification:** [02_Fundamental_Classification.md](02_Fundamental_Classification.md) — Dirichlet, Neumann, Robin BCs
- **Mathematics:** [04_Mathematical_Formulation.md](04_Mathematical_Formulation.md) — BC math in OpenFOAM

---

## 📌 Key Takeaways

### ✅ Core Concepts
1. **Advanced BCs = Real-world complexity:** Time-varying, spatial profiles, coupled regions
2. **Trade-offs:** Complexity vs accuracy vs performance
3. **Scalability:** `nutUSpaldingWallFunction` ใช้ได้ทุก y+, robust สำหรับ production runs

### ✅ Best Practices
1. **Start simple:** ใช้ table/CSV ก่อน, upgrade เป็น coded ถ้าจำเป็น
2. **Match physics to BC:**
   - RANS → `turbulentInlet`
   - LES → `turbulentDFSEMInlet`
   - Unknown y+ → `nutUSpaldingWallFunction`
3. **Validate:** ตรวจ coded BC syntax ก่อน run (compile errors = wasted time)

### ✅ Common Pitfalls to Avoid
1. ❌ `codedFixedValue`: ลืมใช้ `constant::mathematical::pi` (ใช้ `M_PI` → error)
2. ❌ Wall functions: ใช้ `nutkWallFunction` กับ low y+ mesh → wrong physics
3. ❌ CHT: ลืม set `mappedWall` ใน `polyMesh/boundary` → coupling fails
4. ❌ DFSEM: ใช้กับ RANS → waste computational resources

### ✅ Quick Reference
- **Time-varying:** `uniformFixedValue` (table/CSV), `codedFixedValue` (functions)
- **Spatial:** `fixedProfile` (CSV), `mappedFixedValue` (recycling)
- **Walls:** `nutUSpaldingWallFunction` (all y+), `nutLowReWallFunction` (y+ < 5)
- **CHT:** `mappedWall` + `compressible::turbulentTemperatureCoupledBaffleMixed`
- **LES:** `turbulentDFSEMInlet` (realistic eddies)

---

**หัวข้อถัดไป:** [07_Troubleshooting_Boundary_Conditions.md](07_Troubleshooting_Boundary_Conditions.md) — การวินิจฉัยและแก้ปัญหา BCs