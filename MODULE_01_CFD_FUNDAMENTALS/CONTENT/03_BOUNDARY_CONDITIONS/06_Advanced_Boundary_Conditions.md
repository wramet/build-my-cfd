# Advanced Boundary Conditions

BC ขั้นสูงสำหรับสถานการณ์พิเศษ

---

## Time-Varying BCs

### Table-Based

```cpp
inlet
{
    type            uniformFixedValue;
    uniformValue    table
    (
        (0      (0 0 0))
        (1      (5 0 0))
        (5      (10 0 0))
        (10     (10 0 0))
    );
}
```

**หมายเหตุ:** Interpolate เชิงเส้นระหว่าง data points

### Expression-Based (codedFixedValue)

```cpp
inlet
{
    type    codedFixedValue;
    value   uniform (0 0 0);
    name    pulsatingInlet;
    
    code
    #{
        scalar t = this->db().time().value();
        scalar U0 = 10.0;
        scalar freq = 0.5;
        
        vectorField& field = *this;
        field = vector(U0 * (1 + 0.3*sin(2*M_PI*freq*t)), 0, 0);
    #};
}
```

### CSV File

```cpp
inlet
{
    type            uniformFixedValue;
    uniformValue    csvFile;
    uniformValueCoeffs
    {
        nHeaderLine     1;
        refColumn       0;          // time column
        componentColumns (1 2 3);   // U components
        separator       ",";
        fileName        "inlet_data.csv";
    }
}
```

---

## Spatial Profiles

### mappedFixedValue

Map จาก internal field หรือ region อื่น

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

### fixedProfile

Non-uniform profile

```cpp
inlet
{
    type    fixedProfile;
    profile csvFile;
    profileCoeffs
    {
        nHeaderLine 1;
        refColumn   0;              // y-coordinate
        componentColumns (1);       // U_x
        separator   ",";
        fileName    "velocity_profile.csv";
    }
    direction   (0 1 0);
    origin      (0 0 0);
}
```

### Parabolic Profile (coded)

```cpp
inlet
{
    type    codedFixedValue;
    value   uniform (0 0 0);
    name    parabolicInlet;
    
    code
    #{
        const fvPatch& p = this->patch();
        const vectorField& Cf = p.Cf();
        
        scalar R = 0.01;    // Pipe radius
        scalar Umax = 1.0;  // Centerline velocity
        
        vectorField& field = *this;
        forAll(field, faceI)
        {
            scalar r = mag(Cf[faceI].y());
            field[faceI] = vector(Umax*(1 - sqr(r/R)), 0, 0);
        }
    #};
}
```

---

## Wall Functions

### Standard Wall Functions

| Field | BC Type | y+ Range |
|-------|---------|----------|
| nut | `nutkWallFunction` | 30-300 |
| k | `kqRWallFunction` | 30-300 |
| ε | `epsilonWallFunction` | 30-300 |
| ω | `omegaWallFunction` | 30-300 |

### Low-Re Wall Treatment

| Field | BC Type | y+ Range |
|-------|---------|----------|
| nut | `nutLowReWallFunction` | < 5 |
| k | `kLowReWallFunction` | < 5 |
| ε | `epsilonLowReWallFunction` | < 5 |
| ω | `omegaBlendedWallFunction` | Any |

### Scalable Wall Functions

```cpp
wall
{
    type    nutUSpaldingWallFunction;
    value   uniform 0;
}
```

**ใช้ได้ทุก y+** — blends viscous และ log-law regions

---

## Coupled BCs

### mappedWall (Multi-Region)

สำหรับ conjugate heat transfer:

```cpp
// Fluid side
wall
{
    type            mappedWall;
    sampleMode      nearestPatchFace;
    sampleRegion    solid;
    samplePatch     wall;
}

// Temperature BC (fluid side)
wall
{
    type            compressible::turbulentTemperatureCoupledBaffleMixed;
    Tnbr            T;
    value           uniform 300;
}
```

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

```cpp
baffle
{
    type    porousBafflePressure;
    D       1000;       // Darcy coefficient
    I       0.5;        // Inertial coefficient
    length  0.1;        // Baffle thickness
    value   uniform 0;
}
```

---

## Moving Mesh

### sixDoFRigidBodyMotion

```cpp
movingBody
{
    type            sixDoFRigidBodyMotion;
    mass            1.0;
    centreOfMass    (0 0 0);
    momentOfInertia (1 1 1);
    patches         (body);
    
    constraints     ();
    restraints      ();
}
```

### oscillatingVelocity

```cpp
piston
{
    type        oscillatingVelocity;
    amplitude   (0 0 0.01);
    omega       6.28;   // rad/s
    value       uniform (0 0 0);
}
```

---

## Turbulence Inlet

### turbulentInlet

Adds fluctuations to mean flow:

```cpp
inlet
{
    type                turbulentInlet;
    fluctuationScale    (0.1 0.1 0.1);
    referenceField      uniform (10 0 0);
    value               uniform (10 0 0);
}
```

### turbulentDigitalFilterInlet

Synthetic turbulence:

```cpp
inlet
{
    type    turbulentDFSEMInlet;
    delta   0.005;              // BL thickness
    nCellPerEddy    5;
    mapMethod       minDistance;
    value           uniform (10 0 0);
}
```

---

## Fan/Pump

### fan

Pressure jump across patch:

```cpp
fan
{
    type        fan;
    fanCurve    table
    (
        (0      100)
        (0.1    90)
        (0.2    50)
        (0.3    0)
    );
}
```

---

## Concept Check

<details>
<summary><b>1. codedFixedValue compile เมื่อไหร่?</b></summary>

Compile on-the-fly เมื่อเริ่ม run ครั้งแรก → มี delay เล็กน้อย แต่สะดวกไม่ต้อง recompile solver
</details>

<details>
<summary><b>2. nutUSpaldingWallFunction ดีกว่า nutkWallFunction อย่างไร?</b></summary>

`nutUSpaldingWallFunction` ใช้ได้ทุก y+ โดย blend ระหว่าง viscous sublayer และ log-law region ในขณะที่ `nutkWallFunction` ต้องการ y+ ในช่วง 30-300
</details>

<details>
<summary><b>3. Conjugate heat transfer ต้องใช้ BC อะไร?</b></summary>

- Fluid side: `turbulentTemperatureCoupledBaffleMixed`
- Solid side: `compressible::turbulentTemperatureCoupledBaffleMixed`
- ทั้งสองต้องใช้ `mappedWall` patch type
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [05_Common_Boundary_Conditions_in_OpenFOAM.md](05_Common_Boundary_Conditions_in_OpenFOAM.md) — BC ที่ใช้บ่อย
- **บทถัดไป:** [07_Troubleshooting_Boundary_Conditions.md](07_Troubleshooting_Boundary_Conditions.md) — การแก้ปัญหา