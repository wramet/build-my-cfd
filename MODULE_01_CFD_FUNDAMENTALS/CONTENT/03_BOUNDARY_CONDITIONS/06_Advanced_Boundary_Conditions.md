# Advanced Boundary Conditions

BC ขั้นสูงสำหรับสถานการณ์พิเศษ

> **ทำไมต้องรู้ Advanced BCs?**
> - ปัญหาจริงมักไม่ใช่ fixedValue/zeroGradient ง่ายๆ
> - Time-varying, profile, coupled BCs พบบ่อยในอุตสาหกรรม
> - บาง BC ช่วยประหยัดเวลาและเพิ่มความแม่นยำมาก

---

## Time-Varying BCs

### Table-Based

> **ใช้เมื่อ:** มีข้อมูลเป็น time series (เช่น จาก measurement)

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
}
```

**หมายเหตุ:** Interpolate เชิงเส้นระหว่าง data points

### Expression-Based (codedFixedValue)

> **ใช้เมื่อ:** ต้องการ function ที่ซับซ้อน (sine, exponential, ฯลฯ)

```cpp
inlet
{
    type    codedFixedValue;
    value   uniform (0 0 0);      // Initial guess
    name    pulsatingInlet;       // Unique name สำหรับ compile
    
    code
    #{
        scalar t = this->db().time().value();       // เวลาปัจจุบัน
        scalar U0 = 10.0;                            // Mean velocity
        scalar freq = 0.5;                           // Frequency (Hz)
        
        vectorField& field = *this;                  // Reference to BC field
        field = vector(U0 * (1 + 0.3*sin(2*M_PI*freq*t)), 0, 0);
    #};
}
```

**ทำไมใช้ codedFixedValue?**
- ไม่ต้อง compile solver ใหม่
- เขียน code C++ ได้เลยใน BC file
- Compile on-the-fly ตอนเริ่ม run

### CSV File

> **ใช้เมื่อ:** มีข้อมูลจาก external source (Excel, experiment)

```cpp
inlet
{
    type            uniformFixedValue;
    uniformValue    csvFile;
    uniformValueCoeffs
    {
        nHeaderLine     1;              // ข้าม header กี่บรรทัด
        refColumn       0;              // Column เวลา
        componentColumns (1 2 3);       // Columns สำหรับ U_x, U_y, U_z
        separator       ",";            // Delimiter
        fileName        "inlet_data.csv";
    }
}
```

---

## Spatial Profiles

### mappedFixedValue

> **ใช้เมื่อ:** ต้องการ map ค่าจาก ที่อื่น (outlet → inlet หรือ internal plane)

```cpp
outlet
{
    type        mappedFixedValue;
    interpolationScheme cellPoint;
    setAverage  false;
    average     (0 0 0);
    value       uniform (0 0 0);
}
```

**ใช้สำหรับ:** Recycling BC (นำ outlet profile กลับมาใช้ที่ inlet)

### fixedProfile

> **ใช้เมื่อ:** มี velocity profile เป็น function ของตำแหน่ง

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

### Parabolic Profile (coded)

> **ใช้สำหรับ:** Fully developed pipe flow (Hagen-Poiseuille)

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
        
        scalar R = 0.01;        // Pipe radius
        scalar Umax = 1.0;      // Centerline velocity
        
        vectorField& field = *this;
        forAll(field, faceI)
        {
            scalar r = mag(Cf[faceI].y());           // Radial distance
            field[faceI] = vector(Umax*(1 - sqr(r/R)), 0, 0);
        }
    #};
}
```

**Physics:** $u(r) = U_{max}\left(1 - \frac{r^2}{R^2}\right)$

---

## Wall Functions

### Standard Wall Functions (30 < y+ < 300)

| Field | BC Type | ทำไม |
|-------|---------|------|
| nut | `nutkWallFunction` | คำนวณ ν_t จาก log-law |
| k | `kqRWallFunction` | k ใช้ค่าจาก cell ใกล้ผนัง |
| ε | `epsilonWallFunction` | ε คำนวณจาก equilibrium |
| ω | `omegaWallFunction` | ω สำหรับ k-ω models |

### Low-Re Wall Treatment (y+ < 5)

| Field | BC Type | ทำไมใช้ |
|-------|---------|--------|
| nut | `nutLowReWallFunction` | Resolve viscous sublayer |
| k | `kLowReWallFunction` | k → 0 ที่ผนัง |
| ε | `epsilonLowReWallFunction` | ε จาก viscous region |
| ω | `omegaBlendedWallFunction` | Blend อัตโนมัติ |

### Scalable Wall Functions (ใช้ได้ทุก y+)

```cpp
wall
{
    type    nutUSpaldingWallFunction;
    value   uniform 0;
}
```

**ทำไม nutUSpaldingWallFunction ดี?**
- ใช้สูตรของ Spalding ที่ blend viscous และ log-law regions
- ไม่ต้องกังวลว่า y+ จะตกในช่วงไหน
- **แนะนำ** สำหรับ mesh ที่ไม่แน่ใจ y+

---

## Coupled BCs (Multi-Region)

### mappedWall (Conjugate Heat Transfer)

> **ใช้เมื่อ:** มี solid และ fluid regions ติดกัน

```cpp
// ========== Fluid side ==========
// constant/polyMesh/boundary
wall
{
    type            mappedWall;
    sampleMode      nearestPatchFace;
    sampleRegion    solid;              // ชื่อ solid region
    samplePatch     wall;               // Patch ใน solid ที่จับคู่
}

// 0/T
wall
{
    type            compressible::turbulentTemperatureCoupledBaffleMixed;
    Tnbr            T;                  // ชื่อ T field ใน neighbor region
    value           uniform 300;
}
```

**ทำไมต้อง coupled?**
- Fluid + Solid ต้อง "คุยกัน"
- Temperature ต้องต่อเนื่องที่ interface
- Heat flux ต้องเท่ากัน

### regionCouple

```cpp
wall
{
    type    regionCouple;
    Tnbr    T;
    value   uniform 300;
}
```

---

## Porous Media

### porousBafflePressure

> **ใช้สำหรับ:** Filter, screen, ตะแกรง

```cpp
baffle
{
    type    porousBafflePressure;
    D       1000;       // Darcy coefficient (viscous resistance)
    I       0.5;        // Inertial coefficient
    length  0.1;        // Baffle thickness [m]
    value   uniform 0;
}
```

**Physics:** Pressure drop: $\Delta p = \left(D\mu|U| + \frac{I\rho|U|^2}{2}\right) \cdot L$

---

## Moving Mesh

### sixDoFRigidBodyMotion

> **ใช้สำหรับ:** Floating objects, FSI

```cpp
movingBody
{
    type            sixDoFRigidBodyMotion;
    mass            1.0;                    // kg
    centreOfMass    (0 0 0);                // Initial position
    momentOfInertia (1 1 1);                // kg·m²
    patches         (body);                 // Patches that move together
    
    constraints     ();                     // Motion constraints
    restraints      ();                     // Springs, dampers
}
```

### oscillatingVelocity

> **ใช้สำหรับ:** Piston, vibrating surface

```cpp
piston
{
    type        oscillatingVelocity;
    amplitude   (0 0 0.01);       // Amplitude [m]
    omega       6.28;             // Angular frequency [rad/s] = 2π × frequency
    value       uniform (0 0 0);
}
```

---

## Turbulence Inlet

### turbulentInlet

> **ใช้เมื่อ:** ต้องการ velocity fluctuations ที่ inlet

```cpp
inlet
{
    type                turbulentInlet;
    fluctuationScale    (0.1 0.1 0.1);      // Relative fluctuation magnitude
    referenceField      uniform (10 0 0);   // Mean velocity
    value               uniform (10 0 0);
}
```

**ทำไมใช้?** สำหรับ LES/DES ที่ต้องการ realistic turbulence ที่ inlet

### turbulentDigitalFilterInlet (DFSEM)

> **ใช้สำหรับ:** High-fidelity LES

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

**ทำไม DFSEM ดีกว่า turbulentInlet?**
- สร้าง synthetic eddies ที่มี spatial correlation
- Realistic turbulent structures ตั้งแต่ inlet

---

## Fan/Pump

### fan

> **ใช้สำหรับ:** Model fan หรือ pump เป็น pressure jump

```cpp
fan
{
    type        fan;
    fanCurve    table
    (
        (0      100)        // Q = 0 m³/s → ΔP = 100 Pa
        (0.1    90)         // Q = 0.1 m³/s → ΔP = 90 Pa
        (0.2    50)         // Q = 0.2 m³/s → ΔP = 50 Pa
        (0.3    0)          // Q = 0.3 m³/s → ΔP = 0 Pa (max flow)
    );
}
```

**ทำไมใช้ fan curve?**
- Real fan: ΔP ลดลงเมื่อ flow rate เพิ่ม
- Curve มาจาก manufacturer datasheet

---

## Concept Check

<details>
<summary><b>1. codedFixedValue compile เมื่อไหร่?</b></summary>

**Compile on-the-fly** เมื่อเริ่ม run ครั้งแรก:
- มี delay เล็กน้อย (ไม่กี่วินาที)
- สะดวก: ไม่ต้อง recompile solver
- Code เก็บใน `dynamicCode/` folder

**ข้อควรระวัง:** ตรวจ syntax error ก่อน run!
</details>

<details>
<summary><b>2. nutUSpaldingWallFunction ดีกว่า nutkWallFunction อย่างไร?</b></summary>

| | nutkWallFunction | nutUSpaldingWallFunction |
|-|------------------|--------------------------|
| y+ range | 30-300 เท่านั้น | **ใช้ได้ทุก y+** |
| Physics | Log-law only | Blend viscous + log-law |
| Flexibility | ต้อง mesh ให้ได้ y+ ถูกต้อง | Mesh หยาบ/ละเอียดก็ใช้ได้ |

**แนะนำ:** ใช้ `nutUSpaldingWallFunction` เป็น default
</details>

<details>
<summary><b>3. Conjugate heat transfer ต้องใช้ BC อะไร?</b></summary>

**ทั้งสอง regions ต้องจับคู่กัน:**

1. **Patch type:** `mappedWall` (ทั้งสองฝั่ง)
2. **Temperature BC (Fluid):** `compressible::turbulentTemperatureCoupledBaffleMixed`
3. **Temperature BC (Solid):** `compressible::turbulentTemperatureCoupledBaffleMixed`

**ทำไม `Mixed`?**
- ผสม Dirichlet + Neumann ตาม thermal resistance
- ให้ T continuous และ q เท่ากันที่ interface
</details>

<details>
<summary><b>4. DFSEM ต่างจาก turbulentInlet อย่างไร?</b></summary>

| | turbulentInlet | DFSEM |
|-|----------------|-------|
| Fluctuations | Random noise | Synthetic eddies |
| Spatial correlation | ไม่มี | มี (realistic) |
| ใช้กับ | RANS | LES/DES |
| Cost | ต่ำ | สูงกว่า |

**ทำไม DFSEM ดีกว่าสำหรับ LES?**
- LES ต้องการ resolved turbulent structures
- Random noise จะ dissipate หลัง inlet
- DFSEM สร้าง structures ที่ survive ไปใน domain
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [05_Common_Boundary_Conditions_in_OpenFOAM.md](05_Common_Boundary_Conditions_in_OpenFOAM.md) — BC ที่ใช้บ่อย
- **บทถัดไป:** [07_Troubleshooting_Boundary_Conditions.md](07_Troubleshooting_Boundary_Conditions.md) — การแก้ปัญหา