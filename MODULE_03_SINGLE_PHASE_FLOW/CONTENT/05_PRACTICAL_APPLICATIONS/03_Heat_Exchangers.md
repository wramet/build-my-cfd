# Heat Exchangers: Conjugate Heat Transfer in OpenFOAM

การจำลองเครื่องแลกเปลี่ยนความร้อนด้วย Conjugate Heat Transfer

---

## Learning Objectives

หลังจากศึกษาบทนี้ คุณจะสามารถ:

1. **เลือกแนวทางการจำลองที่เหมาะสม** (Multi-Region CHT หรือ Porous Media) โดยพิจารณาจากความแม่นยำ เวลาคำนวณ และเป้าหมายของการจำลอง (design optimization vs system-level analysis)

2. **ตั้งค่า Multi-Region CHT** ด้วย `chtMultiRegionFoam` อย่างเป็นระบบ รวมถึงการกำหนด region properties ที่ถูกต้อง การกำหนด thermophysical properties สำหรับ fluid และ solid domains และการตั้งค่า interface boundary conditions

3. **ตั้งค่าและปรับแต่ง interface boundary conditions** โดยใช้ `turbulentTemperatureCoupledBaffleMixed` BC เพื่อบังคับ continuity ของ temperature และ heat flux ระหว่าง regions

4. **คำนวณและวิเคราะห์ประสิทธิภาพเครื่องแลกเปลี่ยนความร้อน** โดยใช้ effectiveness-NTU method ($\varepsilon = Q_{actual}/Q_{max}$) และ LMTD method ($\Delta T_{LMTD}$) พร้อมทั้งตีความผลลัพธ์

5. **ตรวจสอบความถูกต้องของการจำลอง CHT** ผ่าน 3 ระดับ: energy balance check (error < 5%), LMTD method validation (error < 10%), และ Nusselt number correlation comparison (within 20%)

6. **วินิจฉัยและแก้ไขปัญหา interface coupling failures** และ convergence issues ในการจำลอง CHT โดยใช้เทคนิค relaxation, mesh refinement และ BC verification

---

## 1. WHAT - Application Domain

### Engineering Context

เครื่องแลกเปลี่ยนความร้อน (Heat Exchangers) เป็นอุปกรณ์ที่สำคัญในอุตสาหกรรม:

- **Power Plants:** Condensers, feedwater heaters, steam generators
- **Automotive:** Radiators, intercoolers, oil coolers, EGR coolers
- **HVAC:** Evaporators, condensers, cooling coils
- **Process Industry:** Shell-and-tube, plate heat exchangers, finned-tube exchangers
- **Electronics:** Cold plates, heat sinks, liquid cooling systems

**ความท้าทายทาง CFD:** ต้องแก้สมการของไหลและสมการความร้อนพร้อมกันใน fluid และ solid domains โดยรักษาความต่อเนื่องของ:

- **Temperature continuity:**1$T_{fluid} = T_{solid}1ที่ interface
- **Heat flux continuity:**1$q_{fluid} = q_{solid}1ที่ interface
- **Conservation of energy:**1$\dot{Q}_{hot} = \dot{Q}_{cold}1(ใน steady state)

### Types of Heat Exchangers

| Type | Flow Arrangement | Typical Applications | CFD Complexity |
|------|------------------|---------------------|----------------|
| **Shell-and-tube** | Counter/cross-flow | Power plants, oil refineries | High (turbulent, baffles) |
| **Plate** | Counter-flow | Food processing, HVAC | Medium (narrow channels) |
| **Finned-tube** | Cross-flow | Radiators, air coils | High (conjugate, extended surface) |
| **Microchannel** | Counter/parallel | Electronics cooling | High (small scales, laminar) |

---

## 2. WHY - Physical Importance

### Performance Metrics

เครื่องแลกเปลี่ยนความร้อนถูกประเมินด้วย parameters:

**Effectiveness ($\varepsilon$):**
$$\varepsilon = \frac{q_{actual}}{q_{max}} = \frac{q_{actual}}{C_{min}(T_{h,in} - T_{c,in})}$$

โดยที่:
-1$C_{min} = \min(\dot{m}_h c_{p,h}, \dot{m}_c c_{p,c})1— minimum heat capacity rate
-1$\varepsilon \in [0, 1]1— 1 คือ ideal heat exchanger

**Number of Transfer Units (NTU):**
$$NTU = \frac{UA}{C_{min}}$$

เป็น measure ของ size ของ heat exchanger — NTU สูงแสดงถึง heat transfer area หรือ coefficient สูง

**Log-Mean Temperature Difference (LMTD):**
$$\Delta T_{LMTD} = \frac{\Delta T_1 - \Delta T_2}{\ln(\Delta T_1/\Delta T_2)}$$

สำหรับ counter-flow:
-1$\Delta T_1 = T_{h,in} - T_{c,out}$
-1$\Delta T_2 = T_{h,out} - T_{c,in}$

**Heat Transfer Rate:**
$$Q = \varepsilon C_{min}(T_{h,in} - T_{c,in}) = UA \Delta T_{LMTD}$$

### Why CHT is Critical

**Physical Phenomena Requiring CHT:**

1. **Conjugate Heat Transfer:** Heat conduction ใน solid walls ร่วมกับ convection ใน fluid
   - Wall conduction resistance:1$R_{wall} = \frac{t_w}{k_w A_w}$
   - Fluid convection resistance:1$R_{fluid} = \frac{1}{h A}$

2. **Temperature-Dependent Properties:** Viscosity, conductivity, density เปลี่ยนตาม temperature
   - ส่งผลต่อ flow distribution และ heat transfer coefficient
   - โดยเฉพาะใน liquids (water, oils) ที่ viscosity แปรผันตาม temperature สูง

3. **Local Hot Spots:** จุดที่มีอุณหภูมิสูงผิดปกติที่อาจทำให้เกิดความเสียหาย
   - Critical ใน electronics cooling และ high-temperature applications
   - ต้องใช้ CFD เพื่อ detect จุดเหล่านี้

### Cross-Reference

ทฤษฎีพื้นฐานของการถ่ายเทความร้อน:
- **สมการพลังงาน:** ดู [Energy Equation Fundamentals](../../04_HEAT_TRANSFER/01_Energy_Equation_Fundamentals.md)
- **Conjugate Heat Transfer:** ดู [Conjugate Heat Transfer](../../04_HEAT_TRANSFER/04_Conjugate_Heat_Transfer.md)
- **Turbulence modeling สำหรับ heat transfer:** ดู [Wall Treatment](../../03_TURBULENCE_MODELING/03_Wall_Treatment.md)

---

## 3. HOW - OpenFOAM Implementation

### 3.1 Approach Selection Comparison

**2 แนวทางหลัก:**

| Aspect | Multi-Region CHT | Porous Media |
|--------|------------------|--------------|
| **Solver** | `chtMultiRegionFoam` | `simpleFoam` + `fvOptions` |
| **ความแม่นยำ** | สูง - แก้สมการจริงในทุก domain | ปานกลาง - ต้อง calibrate |
| **เวลาคำนวณ** | ช้า (3-10x) | เร็ว |
| **Memory** | สูง | ปานกลาง |
| **Mesh** | ต้อง mesh แยกทุก region | ของไหลเดียว |
| **Setup complexity** | สูง - regions, interface BCs | ปานกลาง - fvOptions |
| **Output details** | Temperature distribution in solid, local heat flux | Bulk parameters only |
| **เหมาะกับ** | Design optimization, detailed analysis, novel geometries | System-level simulation, parametric studies, known performance |

**คำแนะนำการเลือก:**
- ใช้ **Multi-Region CHT** เมื่อต้องการดู temperature distribution ใน solid walls, หรือ design เรื่อง geometry, หรือทำ optimization รายละเอียด, หรือทำงานกับ novel geometries ที่ไม่มีข้อมูล performance
- ใช้ **Porous Media** เมื่อทราบ performance characteristics (จาก experiment หรือ detailed CFD) แล้ว และต้องการผลลัพธ์รวดเร็วสำหรับ system-level analysis หรือ parametric studies

### 3.2 Multi-Region CHT Setup - Step-by-Step Workflow

**Workflow Overview:**

```
1. Define Regions → 2. Create Directory Structure → 3. Configure Thermophysical Properties → 4. Define Interface BCs → 5. Run Simulation → 6. Monitor and Post-Process
```

#### Step 1: Define Regions

```cpp
// constant/regionProperties
regions
(
    hotFluid
    coldFluid
    solidWall
);
```

**หมายเหตุ:** สามารถมีได้มากกว่า 3 regions สำหรับ complex geometries (เช่น fins, multiple solid domains)

#### Step 2: Create Directory Structure

```
caseDirectory/
├── constant/
│   ├── regionProperties
│   ├── hotFluid/
│   │   ├── polyMesh/
│   │   │   ├── blockMeshDict
│   │   │   └── boundary
│   │   └── thermophysicalProperties
│   ├── coldFluid/
│   │   ├── polyMesh/
│   │   └── thermophysicalProperties
│   └── solidWall/
│       ├── polyMesh/
│       └── thermophysicalProperties
│
├── 0/
│   ├── hotFluid/
│   │   ├── T
│   │   ├── p
│   │   └── U
│   ├── coldFluid/
│   │   ├── T
│   │   ├── p
│   │   └── U
│   └── solidWall/
│       └── T
│
└── system/
    ├── controlDict
    ├── fvSchemes
    ├── fvSolution
    ├── hotFluid/
    │   └── fvSchemes
    └── coldFluid/
        └── fvSchemes
```

**Procedure:**

```bash
# 1. Create initial mesh for complete domain
blockMesh

# 2. Create cellZones for each region (ใน blockMeshDict หรือ topoSet)
topoSet -dict system/topoSetDict

# 3. Split mesh into regions
splitMeshRegions -cellZones -overwrite

# หลังจาก split จะได้ directory structure ดังกล่าว
```

#### Step 3: Configure Thermophysical Properties

**Fluid Properties (Hot Fluid - e.g., Air):**
```cpp
// constant/hotFluid/thermophysicalProperties
thermoType
{
    type            heRhoThermo;
    mixture         pureMixture;
    transport       const;
    thermo          hConst;
    equationOfState perfectGas;
    energy          sensibleEnthalpy;
}

mixture
{
    specie
    {
        molWeight       28.9;
    }
    thermodynamics
    {
        Cp              1005;
        Hf              0;
    }
    transport
    {
        mu              1.8e-5;
        Pr              0.71;
    }
    equationOfState
    {
        R               287;
        rho             1.225;
    }
}
```

**Fluid Properties (Cold Fluid - e.g., Water):**
```cpp
// constant/coldFluid/thermophysicalProperties
thermoType
{
    type            heRhoThermo;
    mixture         pureMixture;
    transport       const;
    thermo          hConst;
    equationOfState rhoConst;
    energy          sensibleEnthalpy;
}

mixture
{
    specie
    {
        molWeight       18;
    }
    thermodynamics
    {
        Cp              4181;
        Hf              0;
    }
    transport
    {
        mu              8.9e-4;
        Pr              6.14;
    }
    equationOfState
    {
        rho             997;
    }
}
```

**Solid Properties (e.g., Aluminum):**
```cpp
// constant/solidWall/thermophysicalProperties
thermoType
{
    type            heSolidThermo;
    mixture         pureMixture;
    transport       constIso;
    thermo          hConst;
    equationOfState rhoConst;
    energy          sensibleEnthalpy;
}

mixture
{
    thermodynamics
    {
        Cp              903;
        Hf              0;
    }
    transport
    {
        kappa           237;  // Thermal conductivity (W/m·K)
    }
    equationOfState
    {
        rho             2700;
    }
}
```

**Material Properties Reference:**

| Material | k (W/m·K) | ρ (kg/m³) | Cp (J/kg·K) | Typical Application |
|----------|-----------|-----------|-------------|---------------------|
| **Copper** | 401 | 8960 | 385 | High-performance heat exchangers |
| **Aluminum** | 237 | 2700 | 903 | Radiators, automotive heat exchangers |
| **Steel** | 50 | 7850 | 500 | Shell-and-tube exchangers |
| **Stainless Steel** | 16 | 8000 | 500 | Corrosive environments |
| **Brass** | 111 | 8500 | 380 | Marine applications |

#### Step 4: Define Interface Boundary Conditions

**Fluid-Side Interface (Hot Fluid):**
```cpp
// 0/hotFluid/T
dimensions      [0 0 0 1 0 0 0];

internalField   uniform 300;

boundaryField
{
    hotFluid_to_solidWall
    {
        type            compressible::turbulentTemperatureCoupledBaffleMixed;
        Tnbr            T;
        value           uniform 300;
        kappa           solidThermo;
        kappaName       none;
    }

    hotInlet
    {
        type            compressible::turbulentTemperatureRadCoupledMixed;
        T               uniform 350;
        value           uniform 350;
    }

    hotOutlet
    {
        type            inletOutlet;
        inletValue      uniform 300;
        value           uniform 300;
    }

    // ... other boundaries
}
```

**Solid-Side Interface:**
```cpp
// 0/solidWall/T
dimensions      [0 0 0 1 0 0 0];

internalField   uniform 300;

boundaryField
{
    solidWall_to_hotFluid
    {
        type            compressible::turbulentTemperatureCoupledBaffleMixed;
        Tnbr            T;
        value           uniform 300;
        kappa           solidThermo;
        kappaName       none;
    }

    solidWall_to_coldFluid
    {
        type            compressible::turbulentTemperatureCoupledBaffleMixed;
        Tnbr            T;
        value           uniform 300;
        kappa           solidThermo;
        kappaName       none;
    }

    // ... other boundaries
}
```

**คำอธิบาย Interface BC:**
- `turbulentTemperatureCoupledBaffleMixed` บังคับ continuity ของ temperature และ heat flux
- **Temperature matching:**1$T_{fluid} = T_{solid}1ที่ interface
- **Heat flux continuity:**1$q = -k_{fluid}\nabla T_{fluid} = -k_{solid}\nabla T_{solid}$
- **ความสำคัญ:** ต้องระบุ `Tnbr` (temperature neighbor) และ `kappa` (conductivity) อย่างถูกต้อง

**Velocity Boundary Conditions (Fluid Regions):**
```cpp
// 0/hotFluid/U
dimensions      [0 1 -1 0 0 0 0];

internalField   uniform (0 0 0);

boundaryField
{
    hotFluid_to_solidWall
    {
        type            noSlip;
    }

    hotInlet
    {
        type            surfaceNormalFixedValue;
        refValue        uniform 5;  // m/s
    }

    hotOutlet
    {
        type            zeroGradient;
    }

    // ... other boundaries
}
```

**Pressure Boundary Conditions:**
```cpp
// 0/hotFluid/p
dimensions      [1 -1 -2 0 0 0 0];

internalField   uniform 101325;

boundaryField
{
    hotFluid_to_solidWall
    {
        type            zeroGradient;
    }

    hotInlet
    {
        type            zeroGradient;
    }

    hotOutlet
    {
        type            fixedValue;
        value           uniform 101325;
    }

    // ... other boundaries
}
```

#### Step 5: Configure Solver Settings

**Discretization Schemes:**
```cpp
// system/fvSchemes
ddtSchemes
{
    default         steadyState;
}

gradSchemes
{
    default         Gauss linear;
    grad(T)         Gauss linear;
}

divSchemes
{
    default         none;
    div(phi,U)      bounded Gauss linearUpwind grad(U);
    div(phi,T)      bounded Gauss linearUpwind grad(T);
    div(phi,k)      bounded Gauss linearUpwind grad(k);
    div(phi,epsilon) bounded Gauss linearUpwind grad(epsilon);
}

laplacianSchemes
{
    default         Gauss linear corrected;
}

interpolationSchemes
{
    default         linear;
}

snGradSchemes
{
    default         corrected;
}
```

**Solution Settings:**
```cpp
// system/fvSolution
solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-6;
        relTol          0.01;
        smoother        GaussSeidel;
    }

    U
    {
        solver          smoothSolver;
        smoother        GaussSeidel;
        tolerance       1e-5;
        relTol          0.1;
    }

    T
    {
        solver          smoothSolver;
        smoother        GaussSeidel;
        tolerance       1e-6;
        relTol          0.1;
    }

    "(k|epsilon|omega)"
    {
        solver          smoothSolver;
        smoother        GaussSeidel;
        tolerance       1e-5;
        relTol          0.1;
    }
}

relaxationFactors
{
    p               0.3;
    U               0.7;
    T               0.7;  // สำคัญสำหรับ CHT stability
    k               0.7;
    epsilon         0.7;
}

SIMPLE
{
    nCorrectors     2;
    nNonOrthogonalCorrectors 1;
    pRefCell        0;
    pRefValue       101325;
    residualControl
    {
        p               1e-4;
        U               1e-5;
        T               1e-6;
        "(k|epsilon)"   1e-5;
    }
}

outerCorrectors  3;  // สำคัญสำหรับ coupling ระหว่าง regions
```

#### Step 6: Run Simulation

```bash
# 1. Split regions (ถ้า mesh เดียว)
splitMeshRegions -cellZones -overwrite

# 2. Decompose (แต่ละ region)
decomposePar -region hotFluid
decomposePar -region coldFluid
decomposePar -region solidWall

# 3. Run solver
mpirun -np 8 chtMultiRegionFoam -parallel

# 4. Reconstruct
reconstructParMesh -region hotFluid
reconstructParMesh -region coldFluid
reconstructParMesh -region solidWall

reconstructPar -region hotFluid
reconstructPar -region coldFluid
reconstructPar -region solidWall
```

#### Step 7: Monitor and Post-Process

```cpp
// system/controlDict
application     chtMultiRegionFoam;

startFrom       startTime;

startTime       0;

stopAt          endTime;

endTime         1000;

deltaT          1;

adjustTimeStep  no;

functions
{
    // Inlet/Outlet Temperatures
    tempInletHot
    {
        type            surfaceFieldValue;
        libs            ("libfieldFunctionObjects.so");
        writeInterval   10;
        operation       weightedAverage;
        weightField     phi;
        fields          (T);
        region          hotFluid;
        patches         (hotInlet);
        writeFields     false;
    }

    tempOutletHot
    {
        type            surfaceFieldValue;
        libs            ("libfieldFunctionObjects.so");
        writeInterval   10;
        operation       weightedAverage;
        weightField     phi;
        fields          (T);
        region          hotFluid;
        patches         (hotOutlet);
        writeFields     false;
    }

    tempInletCold
    {
        type            surfaceFieldValue;
        libs            ("libfieldFunctionObjects.so");
        writeInterval   10;
        operation       weightedAverage;
        weightField     phi;
        fields          (T);
        region          coldFluid;
        patches         (coldInlet);
        writeFields     false;
    }

    tempOutletCold
    {
        type            surfaceFieldValue;
        libs            ("libfieldFunctionObjects.so");
        writeInterval   10;
        operation       weightedAverage;
        weightField     phi;
        fields          (T);
        region          coldFluid;
        patches         (coldOutlet);
        writeFields     false;
    }

    // Pressure Drop
    pressureDropHot
    {
        type            pressureDifference;
        libs            ("libfieldFunctionObjects.so");
        writeInterval   10;
        region          hotFluid;
        patches         (hotInlet hotOutlet);
    }

    // Heat Transfer Coefficient
    heatTransferCoeff
    {
        type            wallHeatTransferCoeff;
        libs            ("libfieldFunctionObjects.so");
        writeInterval   50;
        region          hotFluid;
        patches         ("hotFluid_to_solidWall.*");
        h               none;  // Calculate locally
    }

    // Wall Heat Flux
    wallHeatFlux
    {
        type            wallHeatFlux;
        libs            ("libfieldFunctionObjects.so");
        writeInterval   50;
        region          hotFluid;
        patches         ("hotFluid_to_solidWall.*");
    }

    // Energy Balance
    energySource
    {
        type            energySource;
        libs            ("libfieldFunctionObjects.so");
        writeInterval   10;
        region          hotFluid;
    }
}
```

**คำนวณ Effectiveness จาก Results:**
```python
# Python post-processing
# Read from function objects output
T_hot_in = 350.0  # K (from tempInletHot)
T_hot_out = 330.0  # K (from tempOutletHot)
T_cold_in = 300.0  # K (from tempInletCold)
T_cold_out = 320.0  # K (from tempOutletCold)

m_dot_hot = 0.5  # kg/s
m_dot_cold = 0.6  # kg/s
Cp_hot = 1005  # J/kg·K
Cp_cold = 4181  # J/kg·K

# Heat capacity rates
C_hot = m_dot_hot * Cp_hot
C_cold = m_dot_cold * Cp_cold
C_min = min(C_hot, C_cold)
C_max = max(C_hot, C_cold)

# Actual heat transfer
Q_actual = m_dot_hot * Cp_hot * (T_hot_in - T_hot_out)  # W
Q_cold = m_dot_cold * Cp_cold * (T_cold_out - T_cold_in)  # W

# Maximum possible heat transfer
Q_max = C_min * (T_hot_in - T_cold_in)

# Effectiveness
effectiveness = Q_actual / Q_max

# NTU (for counter-flow, C_min = C_hot)
NTU = -np.log((1 - effectiveness * (1 + C_min/C_max)) / 
              (1 + effectiveness * (1 + C_min/C_max))) / (1 - C_min/C_max)

# Energy balance check
energy_balance_error = abs(Q_actual - Q_cold) / Q_actual * 100

print(f"Effectiveness: {effectiveness:.3f}")
print(f"NTU: {NTU:.3f}")
print(f"Energy balance error: {energy_balance_error:.2f}%")
```

Cross-reference: ดู function objects รายละเอียดใน [Introduction to Function Objects](../../06_RUNTIME_POST_PROCESSING/01_Introduction_to_FunctionObjects.md)

### 3.3 Porous Media Approach

#### Step 1: Define Cell Zone

```bash
# สร้าง cellZone สำหรับ heat exchanger region
topoSet -dict system/topoSetDict
```

```cpp
// system/topoSetDict
actions
(
    {
        name    heatExchangerZone;
        type    cellZone;
        action  new;
        source  boxToCell;
        box     (0.1 0 0) (0.3 0.1 0.5);  // Define bounding box
    }
);
```

#### Step 2: Configure fvOptions

```cpp
// system/fvOptions
porousHeatExchanger
{
    type            explicitPorositySource;
    active          on;
    selectionMode   cellZone;
    cellZone        heatExchangerZone;

    explicitPorositySourceCoeffs
    {
        type            DarcyForchheimer;
        coordinateSystem
        {
            type    cartesian;
            origin  (0 0 0);
            coordinateRotation
            {
                type    axes;
                e1      (1 0 0);
                e2      (0 1 0);
            }
        }

        // Darcy (linear) coefficient: D = μ/α
        D   (1e5 1e5 1e5);  // Pa·s/m²

        // Forchheimer (quadratic) coefficient: F = C_F·ρ/√α
        F   (10 10 10);      // kg/m⁴

        // Principal directions (anisotropic porosity)
        e1  (1 0 0);         // Flow direction
        e2  (0 1 0);
        e3  (0 0 1);
    }
}

heatSource
{
    type            scalarSemiImplicitSource;
    active          on;
    selectionMode   cellZone;
    cellZone        heatExchangerZone;

    scalarSemiImplicitSourceCoeffs
    {
        // Q_dot = Su + Sp * T  (W/m³)
        // ใช้ calibrate จาก experiment หรือ detailed CFD
        volumeMode      absolute;  // or specific
        T
        {
            Su      10000;  // Explicit source (W/m³)
            Sp      -100;   // Implicit coefficient (W/m³·K)
        }
    }
}
```

**คำนวณ Porosity Coefficients:**

Darcy-Forchheimer equation:
$$\nabla p = -\frac{\mu}{\alpha} \mathbf{u} - \frac{C_F \rho}{\sqrt{\alpha}} |\mathbf{u}| \mathbf{u}$$

เมื่อ:
-1$\alpha1= permeability (m²)
-1$C_F1= inertial resistance coefficient
- **Darcy coefficient (linear):**1$D = \frac{\mu}{\alpha}$
- **Forchheimer coefficient (quadratic):**1$F = \frac{C_F \rho}{\sqrt{\alpha}}$

**Calibration Procedure:**

1. **Measure pressure drop vs flow rate** จาก experiment หรือ detailed CFD
2. **Fit to quadratic equation:**1$\Delta p = A \dot{m} + B \dot{m}^2$
3. **Extract coefficients:**
   -1$D = \frac{A \cdot A_{flow}}{\mu}$
   -1$F = \frac{B \cdot A_{flow}^2}{\rho}$

เมื่อ1$A_{flow}1= cross-sectional area

Cross-reference: ดูการใช้ `topoSet` และ cellZones ใน [Using TopoSet and CellZones](../../05_MESH_QUALITY_AND_MANIPULATION/02_Using_TopoSet_and_CellZones.md)

#### Step 3: Alternative - Heat Transfer Coefficient Method

ถ้าทราบ heat transfer coefficient ($h$) และ surface area ($A$):

```cpp
// system/fvOptions
heatExchangerModel
{
    type            externalHeatFluxSource;
    active          on;
    selectionMode   cellZone;
    cellZone        heatExchangerZone;

    externalHeatFluxSourceCoeffs
    {
        // Q = h * A * (T_fluid - T_secondary)
        mode            coefficient;

        // Overall heat transfer coefficient (W/m²·K)
        h               500;

        // Surface area per unit volume (m²/m³)
        A               100;

        // Secondary fluid temperature (K)
        Tambient       300;
    }
}
```

---

## 4. Validation Methods

### 4.1 Energy Balance Check

**Global Energy Balance (Critical):**

$$\left|\frac{\dot{Q}_{hot} - \dot{Q}_{cold}}{\dot{Q}_{hot}}\right| < 5\%$$

เมื่อ:
-1$\dot{Q}_{hot} = \dot{m}_h c_{p,h} (T_{h,in} - T_{h,out})1— Heat lost by hot fluid
-1$\dot{Q}_{cold} = \dot{m}_c c_{p,c} (T_{c,out} - T_{c,in})1— Heat gained by cold fluid

**Diagnosis:**
- **Error > 5%:** ตรวจสอบ convergence, mesh quality, boundary conditions
- **Error > 10%:** น่าจะมี error ร้ายแรง — interface coupling, thermophysical properties

### 4.2 LMTD Method

Compare CFD results with theoretical LMTD:

$$Q_{CFD} = \dot{m} c_p (T_{in} - T_{out})$$

$$Q_{theory} = U A \Delta T_{LMTD}$$

เมื่อ:
$$\Delta T_{LMTD} = \frac{\Delta T_1 - \Delta T_2}{\ln(\Delta T_1/\Delta T_2)}$$

**Validation Criterion:**
$$Error = \left|\frac{Q_{CFD} - Q_{theory}}{Q_{theory}}\right| < 10\%$$

**Calculate Overall Heat Transfer Coefficient:**

$$\frac{1}{UA} = \frac{1}{h_h A_h} + \frac{t_w}{k_w A_w} + \frac{1}{h_c A_c}$$

เมื่อ:
-1$h_h, h_c1= heat transfer coefficients สำหรับ hot/cold fluids
-1$t_w1= wall thickness
-1$k_w1= wall thermal conductivity
-1$A_h, A_w, A_c1= surface areas

**Procedure:**
1. Extract1$h1จาก CFD:1$h = \frac{q_{wall}}{T_{wall} - T_{bulk}}$
2. Calculate1$U1จาก equation ข้างบน
3. Compare1$Q_{theory} = U A \Delta T_{LMTD}1กับ1$Q_{CFD}$

### 4.3 Nusselt Number Correlations

Compare with empirical correlations:

**Dittus-Boelter (turbulent, heating):**
$$Nu = 0.023 Re^{0.8} Pr^{0.4}$$

**Dittus-Boelter (turbulent, cooling):**
$$Nu = 0.023 Re^{0.8} Pr^{0.3}$$

**Gnielinski (more accurate for1$3000 < Re < 5 \times 10^6$):**
$$Nu = \frac{(f/8)(Re - 1000)Pr}{1 + 12.7\sqrt{f/8}(Pr^{2/3} - 1)}$$

เมื่อ:
-1$f = (0.79 \ln Re - 1.64)^{-2}1— friction factor
-1$Re = \frac{\rho u D_h}{\mu}1— Reynolds number
-1$Pr = \frac{c_p \mu}{k}1— Prandtl number

**Validation Criterion:**
$$\left|\frac{Nu_{CFD} - Nu_{corr}}{Nu_{corr}}\right| < 20\%$$

**Procedure:**
```python
# Calculate Nu from CFD
h_cfd = 500  # W/m²·K (from wallHeatTransferCoeff function)
D_h = 0.01  # Hydraulic diameter (m)
k_fluid = 0.026  # Thermal conductivity (W/m·K)
Nu_cfd = h_cfd * D_h / k_fluid

# Calculate from correlation
Re = 10000
Pr = 0.71
Nu_correlation = 0.023 * Re**0.8 * Pr**0.4

error = abs(Nu_cfd - Nu_correlation) / Nu_correlation * 100
print(f"Nu_CFD: {Nu_cfd:.1f}, Nu_corr: {Nu_correlation:.1f}, Error: {error:.1f}%")
```

Cross-reference: ดู Nusselt correlations รายละเอียดใน [Heat Transfer Mechanisms](../../04_HEAT_TRANSFER/02_Heat_Transfer_Mechanisms.md)

### 4.4 Grid Independence Study

**Procedure:**
1. Run simulation กับ 3 mesh sizes: coarse, medium, fine
2. Monitor key outputs: effectiveness, pressure drop, max temperature
3. Verify การเปลี่ยนแปลง < 2% ระหว่าง medium และ fine meshes

**Example:**
| Mesh | Cells | Effectiveness | Δp (Pa) | T_max (K) |
|------|-------|---------------|---------|-----------|
| Coarse | 500K | 0.712 | 245 | 355.2 |
| Medium | 2M | 0.728 | 258 | 352.1 |
| Fine | 8M | 0.731 | 261 | 351.5 |
| **Change** | - | **0.4%** | **1.2%** | **0.2%** |

ถ้าการเปลี่ยนแปลง < 2% → mesh independent

---

## 5. Mesh Guidelines

### 5.1 Mesh Quality Requirements

| Parameter | Target | Maximum | Reason |
|-----------|--------|---------|--------|
| **$y^+$** | ≈ 1 | < 2 | Accurate wall heat flux and temperature gradient |
| **Expansion ratio** | < 1.2 | < 1.5 | Numerical stability, especially at interfaces |
| **Non-orthogonality** | < 50° | < 65° | Gradient accuracy for heat conduction |
| **Aspect ratio** | < 50 | < 100 | Avoid numerical diffusion |
| **Skewness** | < 0.5 | < 0.8 | Solution accuracy |
| **Layers on interface** | 5 | ≥ 3 | Capture heat transfer across interface |
| **Cell size ratio (cross-interface)** | < 3 | < 5 | Prevent interpolation errors |

### 5.2 Special Considerations for CHT

**Interface Meshing:**
- **Face matching:** Interface patches ต้องมีจำนวน faces เท่ากันทั้ง 2 regions
- **Cell size compatibility:** ความแตกต่างของ cell size ระหว่าง regions < 5:1
- **Layer cells:** ใช้ 3-5 layer cells ที่ fluid-solid interface
- **Boundary layer:** Resolve viscous sublayer ด้วย1$y^+ \approx 1$

**Meshing Strategy:**
```
Solid region:
├── Coarser mesh acceptable (heat conduction สำคัญ)
└── Focus on interface connectivity

Fluid region:
├── Boundary layers at walls (y+ ≈ 1)
├── Refinement in high velocity gradient regions
└── Inlet/outlet: uniform mesh

Interface:
├── Match face centers ระหว่าง regions
├── Use mergeMeshPairs ถ้า mesh แยกกัน
└── Verify ด้วย checkMesh -allgeometry -alltopology
```

**Example blockMeshDict for Interface:**
```cpp
// constant/hotFluid/polyMesh/blockMeshDict
boundary
(
    hotFluid_to_solidWall
    {
        type            wall;
        faces           (...);  // Match faces with solid region
    }
);
```

Cross-reference: ดู mesh quality criteria รายละเอียดใน [Mesh Quality Criteria](../../05_MESH_QUALITY_AND_MANIPULATION/01_Mesh_Quality_Criteria.md)

---

## 6. Common Pitfalls and Troubleshooting

### 6.1 Interface Coupling Failures

**Problem:** Simulation diverges at interfaces

**Symptoms:**
- Residuals oscillate หรือ diverge หลังจาก few iterations
- Temperature spikes ที่ interface
- "Temperature coupling failed" warnings

**Diagnosis:**
```bash
# Check interface matching
checkMesh -region hotFluid -allgeometry -alltopology
checkMesh -region solidWall -allgeometry -alltopology

# Verify interface names match
ls constant/hotFluid/polyMesh/boundary
ls constant/solidWall/polyMesh/boundary

# Check face counts
grep "hotFluid_to_solidWall" constant/hotFluid/polyMesh/boundary
grep "solidWall_to_hotFluid" constant/solidWall/polyMesh/boundary
```

**Solutions:**

1. **Ensure Face Matching:**
   - Interface patches ต้องมีจำนวน faces เท่ากัน
   - ใช้ `mergeMeshPairs` ถ้า mesh แยกกัน:
     ```bash
     mergeMeshPairs . hotFluid solidWall -overwrite
     ```

2. **Check Naming Convention:**
   - `hotFluid_to_solidWall` in hotFluid ต้อง match กับ `solidWall_to_hotFluid` in solidWall
   - ต้องเป็นแบบสลับ region names

3. **Adjust Relaxation Factors:**
   ```cpp
   // system/fvSolution
   relaxationFactors
   {
       T       0.5;  // ลดลงจาก 1.0 (start low)
       U       0.7;
       p       0.3;
   }
   outerCorrectors  5;  // Increase from 3
   ```

4. **Start from Isothermal Solution:**
   ```cpp
   // 0/hotFluid/T และ 0/coldFluid/T
   // Set uniform temperature everywhere
   internalField   uniform 300;
   
   // Run without heat transfer first (converge flow field)
   // Then gradually enable heat transfer
   ```

**Best Practices:**
- Start from isothermal flow solution (no heat transfer)
- Gradually enable heat transfer with lower relaxation
- Monitor interface residuals separately
- Verify conductivity values before running
- Use `maxCo` < 1 สำหรับ transient simulations

### 6.2 Convergence Issues

**Problem:** Residuals stall or oscillate

**Symptoms:**
- Residuals plateau ที่ 10⁻² ถึง 10⁻³ ไม่ลดลงต่อ
- Oscillations ใน residuals
- Heat balance error > 10%

**Solutions:**

1. **Increase Outer Correctors:**
   ```cpp
   // system/fvSolution
   outerCorrectors  5;  // Increase from default (3)
   ```
   - Improves coupling ระหว่าง regions
   - เพิ่ม stability แต่เพิ่ม computational cost

2. **Adjust Solver Tolerances:**
   ```cpp
   solvers
   {
       T
       {
           solver          smoothSolver;
           smoother        GaussSeidel;
           tolerance       1e-6;   // Tighten from 1e-5
           relTol          0.1;    // Loosen for stability
           nSweeps         2;
       }
   }
   ```

3. **Use Under-Relaxation:**
   ```cpp
   relaxationFactors
   {
       T       0.5;  // Start low, increase to 0.7 after convergence
       U       0.7;
       p       0.3;
   }
   ```

4. **Improve Mesh Quality:**
   - Reduce non-orthogonality (< 50°)
   - Add boundary layers ($y^+ \approx 1$)
   - Refine at interfaces

5. **Start from Better Initial Guess:**
   - Run single-phase flow first (converge flow field)
   - Use converged flow field as initial condition for CHT
   - Gradually increase temperature difference

6. **Check Thermophysical Properties:**
   ```bash
   # Verify properties are reasonable
   cat constant/hotFluid/thermophysicalProperties
   cat constant/solidWall/thermophysicalProperties
   ```
   - Conductivity ต้องมี order of magnitude ถูกต้อง
   - Units ต้อง consistent (W/m·K, J/kg·K, kg/m³)

### 6.3 Incorrect Heat Flux

**Problem:** Heat flux not continuous at interface

**Symptoms:**
- Energy balance error > 5%
- Heat flux jump ที่ interface
- Unrealistic temperature gradients

**Diagnosis:**

1. **Check Interface Heat Flux:**
   ```cpp
   // system/controlDict
   functions
   {
       heatFluxHotSide
       {
           type            surfaceFieldValue;
           operation       sum;
           weightField     none;
           fields          (q);  // Wall heat flux
           region          hotFluid;
           patches         ("hotFluid_to_solidWall.*");
       }
       
       heatFluxSolidSide
       {
           type            surfaceFieldValue;
           operation       sum;
           weightField     none;
           fields          (q);
           region          solidWall;
           patches         ("solidWall_to_hotFluid.*");
       }
   }
   ```

2. **Verify Conductivity Values:**
   ```bash
   # Check thermophysical properties
   grep -A10 "transport\|kappa" constant/hotFluid/thermophysicalProperties
   grep -A10 "transport\|kappa" constant/solidWall/thermophysicalProperties
   ```

**Solutions:**

1. **Verify Conductivity Values:**
   - Ensure solid conductivity ถูกต้อง (e.g., Aluminum: 237 W/m·K)
   - Check units (W/m·K, not W/m·°C)
   - Verify temperature dependence (ถ้าใช้ `heSolidThermo`)

2. **Check1$y^+$:**
   - ต้องอยู่ใกล้ 1 สำหรับ accurate heat flux
   - ใช้ `wallHeatFlux` function object ตรวจสอบ

3. **Refine Mesh at Interface:**
   - เพิ่ม boundary layers (5-10 layers)
   - ลด cell size ที่ interface
   - ใช้ `refineMesh` หรือ `addLayers`:
     ```bash
     addLayers -region hotFluid -overwrite
     ```

4. **Verify Interface BC:**
   ```cpp
   // 0/hotFluid/T
   hotFluid_to_solidWall
   {
       type            compressible::turbulentTemperatureCoupledBaffleMixed;
       Tnbr            T;  // Must point to neighbor field
       value           uniform 300;
       kappa           solidThermo;  // Must be correct
       kappaName       none;
   }
   ```

### 6.4 High Temperature Gradient

**Problem:** Unrealistic temperature spikes near walls

**Symptoms:**
- Temperature ที่ wall ผิดปกติสูง/ต่ำ
- Gradient สูงผิดปกติใน boundary layer
- Local hot spots ที่ไม่น่าจะเกิดขึ้น

**Solutions:**

1. **Check Boundary Conditions:**
   ```cpp
   // Verify fixedValue vs zeroGradient
   hotInlet
   {
       type            fixedValue;  // Should be fixedValue
       value           uniform 350;
   }
   
   hotOutlet
   {
       type            inletOutlet;  // Better than zeroGradient
       inletValue      uniform 300;
       value           uniform 300;
   }
   ```

2. **Verify Time Step (ถ้า transient):**
   ```cpp
   // system/controlDict
   maxCo           0.5;  // Reduce from 1.0
   deltaT          0.001;
   ```

3. **Check Turbulence Model:**
   - ใช้ low-Re model สำหรับ accurate heat transfer
   - หรือใช้ enhanced wall treatment
   - Cross-reference: [Wall Treatment](../../03_TURBULENCE_MODELING/03_Wall_Treatment.md)

4. **Verify Thermophysical Properties:**
   - Temperature-dependent properties อาจต้องใช้
   - ตรวจสอบ Cp, k, μ ที่ temperature range ที่ใช้

### 6.5 Memory Issues

**Problem:** Out of memory สำหรับ large multi-region cases

**Solutions:**

1. **Decompose Aggressively:**
   ```bash
   # Use more cores than usual
   decomposePar -region hotFluid -np 16
   decomposePar -region coldFluid -np 16
   decomposePar -region solidWall -np 16
   ```

2. **Use Recursive Decomposition:**
   ```cpp
   // system/decomposeParDict
   method          scotch;
   numberOfSubdomains 16;
   recursive       true;  // Important for multi-region
   ```

3. **Optimize Mesh:**
   - Remove unnecessary cells in solid regions
   - Use coarser mesh ใน solid (heat conduction ไม่ sensitive)

---

## Key Takeaways

- **Approach Selection:** Multi-Region CHT (`chtMultiRegionFoam`) ให้ความแม่นยำสูงสำหรับ design optimization โดยแก้สมการจริงในทุก domain (fluid + solid) พร้อมกัน ในขณะที่ Porous Media approach (`fvOptions` กับ `simpleFoam`) เหมาะสำหรับ system-level simulation ที่รวดเร็วเมื่อทราบ performance characteristics แล้ว โดย trade-off คือความแม่นยำ vs computational cost

- **NTU Method:** Effectiveness-NTU method เป็นเครื่องมือสำคัญในการประเมิน performance:1$\varepsilon = Q_{actual}/Q_{max}$,1$NTU = UA/C_{min}1โดยไม่ต้องทราบ outlet temperature ล่วงหน้า ทำให้เหมาะสำหรับ design และ optimization โดยมีความสัมพันธ์กับ flow arrangement (counter-flow, parallel-flow, cross-flow)

- **Interface BCs:** `turbulentTemperatureCoupledBaffleMixed` BC เป็นหัวใจของ CHT — บังคับ continuity ของทั้ง temperature ($T_{fluid} = T_{solid}$) และ heat flux ($q_{fluid} = q_{solid}$) ระหว่าง regions โดยอัตโนมัติ โดยต้องระบุ Tnbr และ kappa อย่างถูกต้อง และ patch names ต้อง match ระหว่าง regions (e.g., `hotFluid_to_solidWall` ↔ `solidWall_to_hotFluid`)

- **Validation Criteria:** การตรวจสอบความถูกต้องต้องผ่าน 3 เกณฑ์: (1) Energy balance error < 5% — heat ที่เสียไปจาก hot fluid ต้องเท่ากับ heat ที่ cold fluid ได้รับ, (2) LMTD method error < 10% — compare1$Q_{CFD}1กับ1$Q_{theory} = U A \Delta T_{LMTD}$, (3) Nusselt number ต้อง match กับ empirical correlations (Dittus-Boelter, Gnielinski) ภายใน 20%

- **Mesh Requirements:**1$y^+ \approx 11สำคัญมากสำหรับ heat transfer applications เพื่อ capture temperature gradient ใน viscous sublayer ควรมี 5-10 layer cells ที่ fluid-solid interface และ cell size ratio ระหว่าง regions < 5:1 เพื่อ prevent interpolation errors และ maintain flux continuity

- **Pitfall Prevention:** สามขั้นตอนหลักในการแก้ปัญหา CHT: (1) ตรวจสอบ interface matching และ naming consistency — patches ต้องมีจำนวน faces เท่ากันและ names ต้อง match, (2) ปรับ relaxation factors (เริ่มจาก 0.5, increase ถ้า stable) และ increase outerCorrectors (3-5), (3) Verify conductivity values และ mesh quality ก่อน run โดย start from isothermal solution แล้ว gradually enable heat transfer

- **Heat Exchanger Performance:** Effectiveness ($\varepsilon$) และ NTU เป็น parameters สำคัญในการประเมิน performance โดย NTU = UA/C_min แสดงถึง size ของ heat exchanger และ1$\varepsilon1แสดงถึงประสิทธิภาพในการถ่ายเทความร้อน เมื่อเปรียบเทียบกับ maximum possible heat transfer ($Q_{max} = C_{min} \Delta T_{max}$)

---

## Concept Check

<details>
<summary><b>1. Multi-Region CHT กับ Porous Media approach ต่างกันอย่างไร? เมื่อไหร่ควรใช้แบบไหน?</b></summary>

**Multi-Region CHT (`chtMultiRegionFoam`):**
- แก้สมการ Navier-Stokes และ energy equation จริงในทุก domain (fluid + solid)
- แม่นยำสูง — ได้ temperature distribution, heat flux, และ local details
- เสียเวลาในการ setup (mesh แยก, thermophysical properties แยก) และคำนวณช้า (3-10x)
- เหมาะสำหรับ: design optimization, detailed analysis, novel geometries

**Porous Media (`simpleFoam` + `fvOptions`):**
- แทนที่โครงสร้างด้วย resistance terms (Darcy + Forchheimer) และ heat source terms
- เร็ว — ไม่ต้อง mesh solid regions
- ต้อง calibrate coefficients จาก experiment หรือ detailed CFD
- เหมาะสำหรับ: system-level simulation, parametric studies, ที่มีข้อมูล performance อยู่แล้ว

**คำแนะนำ:** เริ่มจาก Multi-Region CHT เพื่อให้ได้ performance data แล้วใช้ Porous Media สำหรับ parametric studies
</details>

<details>
<summary><b>2. `turbulentTemperatureCoupledBaffleMixed` boundary condition ทำงานอย่างไร?</b></summary>

BC นี้ enforce 2 conditions พร้อมกันที่ fluid-solid interface:

1. **Temperature continuity:**
1$$T_{fluid} = T_{solid}$$
   Temperature ที่ interface เท่ากันทั้ง 2 ข้าง

2. **Heat flux continuity:**
1$$q_{fluid} = q_{solid}$$
1$$-k_{fluid} \left(\frac{\partial T}{\partial n}\right)_{fluid} = -k_{solid} \left(\frac{\partial T}{\partial n}\right)_{solid}$$

**การ implement:**
- ต้องกำหนด BC นี้ทั้งใน fluid และ solid regions
- `Tnbr` ชี้ไปที่ field name ใน neighboring region (usually `T`)
- `kappa` ระบุว่าดึง conductivity จากที่ไหน:
  - `fluidThermo` — ดึงจาก fluid properties
  - `solidThermo` — ดึงจาก solid properties
- **Naming convention:** `fluid_to_solid` ใน fluid region ต้อง match กับ `solid_to_fluid` ใน solid region

**Common pitfalls:**
- ลืมระบุ `Tnbr` หรือ `kappa` → coupling failed
- Patch names ไม่ match → simulation diverges
- Conductivity values ผิด → unrealistic heat flux
</details>

<details>
<summary><b>3. ทำไม1$y^+1ใกล้ 1 จึงสำคัญสำหรับ heat transfer simulations?</b></summary>

Temperature gradient สูงสุดอยู่ใน **viscous sublayer** (buffer layer) ใกล้ผนัง:

- **Physics:** สำหรับ flow over heated wall: Temperature หายไปอย่างรวดเร็วจาก1$T_w1ถึง1$T_{\infty}1ในบริเวณนี้
- **Numerical issue:** ถ้า1$y^+1สูงเกินไป (mesh หยาบเกินไป): จะ miss gradient นี้ → underestimate heat flux
- **Consequence:** Heat transfer coefficient จะผิดพลาด 20-50% ถ้า1$y^+ > 30$

**Practical Guideline:**
- **$y^+ \approx 1$:** Resolves viscous sublayer → แม่นยำสำหรับ heat transfer (< 5% error)
- **$30 < y^+ < 300$:** ใช้ wall functions → แม่นยำพอสมควรสำหรับ engineering (10-20% error)
- **$y^+ > 300$:** หยาบเกินไปสำหรับ heat transfer → ผิดพลาดสูง (> 30% error)

**Verification:**
```bash
# Check y+ after simulation
wallHeatTransferCoeff function object
yPlus = wallDist yPlus
```

Cross-reference: ดูรายละเอียดเพิ่มเติมใน [Wall Treatment](../../03_TURBULENCE_MODELING/03_Wall_Treatment.md)
</details>

<details>
<summary><b>4. จะตรวจสอบว่าการจำลอง CHT ถูกต้องหรือไม่?</b></summary>

**3 Levels of Validation:**

**1. Energy Balance (แรกสุด — must pass):**
1$$\left|\frac{\dot{Q}_{hot} - \dot{Q}_{cold}}{\dot{Q}_{hot}}\right| < 5\%$$
   Heat ที่เสียไปจาก hot fluid ต้องเท่ากับ heat ที่ cold fluid ได้รับ
   - **Error > 5%:** ตรวจสอบ convergence, interface coupling, thermophysical properties
   - **Error > 10%:** น่าจะมี error ร้ายแรง — restart simulation

**2. LMTD Method (design validation):**
   Compare1$Q_{CFD}1กับ1$Q_{theory} = U A \Delta T_{LMTD}$
1$$Error = \left|\frac{Q_{CFD} - Q_{theory}}{Q_{theory}}\right| < 10\%$$
   - Calculate1$U1จาก:1$\frac{1}{UA} = \frac{1}{h_h A_h} + \frac{t_w}{k_w A_w} + \frac{1}{h_c A_c}$
   - Extract1$h1จาก CFD:1$h = \frac{q_{wall}}{T_{wall} - T_{bulk}}$

**3. Nusselt Number (physics validation):**
   Compare1$Nu_{CFD} = \frac{h L}{k}1กับ correlations:
   - Dittus-Boelter:1$Nu = 0.023 Re^{0.8} Pr^{0.4}1(heating)
   - Gnielinski:1$Nu = \frac{(f/8)(Re - 1000)Pr}{1 + 12.7\sqrt{f/8}(Pr^{2/3} - 1)}1(more accurate)
1$$\left|\frac{Nu_{CFD} - Nu_{corr}}{Nu_{corr}}\right| < 20\%$$

**ถ้าทั้ง 3 ผ่าน → การจำลองน่าเชื่อถือ**
</details>

<details>
<summary><b>5. จะ handle interface coupling failures ใน CHT simulation อย่างไร?</b></summary>

**Step-by-step Troubleshooting:**

**1. Verify Interface Matching:**
```bash
checkMesh -region hotFluid -allgeometry -alltopology
checkMesh -region solidWall -allgeometry -alltopology

# Check face counts match
grep "hotFluid_to_solidWall" constant/hotFluid/polyMesh/boundary
grep "solidWall_to_hotFluid" constant/solidWall/polyMesh/boundary
```
- ตรวจสอบว่า interface patches มีจำนวน faces เท่ากัน
- Confirm naming: `hotFluid_to_solidWall` ↔ `solidWall_to_hotFluid`

**2. Adjust Relaxation Factors:**
```cpp
// system/fvSolution
relaxationFactors
{
    T       0.5;  // ลดลงจาก 1.0 (start low)
    U       0.7;
    p       0.3;
}
outerCorrectors  5;  // Increase from 3 for better coupling
```

**3. Start from Isothermal Solution:**
- Run flow-only simulation first (no heat transfer)
- Use converged flow field as initial condition for CHT
- Gradually enable heat transfer with low relaxation:
  ```cpp
  // Set uniform temperature everywhere
  internalField   uniform 300;
  
  // Run until convergence, then gradually increase temperature difference
  ```

**4. Verify Conductivity Values:**
```bash
cat constant/*/thermophysicalProperties | grep -A5 "kappa\|transport"
```
- Ensure solid conductivity is correct (order of magnitude check)
  - Copper: ~400 W/m·K
  - Aluminum: ~200 W/m·K
  - Steel: ~50 W/m·K
- Verify units are consistent (W/m·K)

**5. Monitor Interface Residuals:**
```cpp
// system/controlDict
functions
{
    interfaceTempJump
    {
        type            surfaceFieldValue;
        operation       weightedAverage;
        fields          (T);
        region          hotFluid;
        patches         ("hotFluid_to_solidWall.*");
    }
}
```
- Temperature jump ต้อง < 1 K
- Heat flux difference ต้อง < 5%

**Prevention Strategies:**
- Use consistent mesh sizing ระหว่าง regions (ratio < 5:1)
- Add sufficient boundary layers (5-10 layers)
- Verify thermophysical properties before running
- Start with simple 2-region case before 3+ regions
</details>

<details>
<summary><b>6. Effectiveness-NTU method ใช้อย่างไรในการประเมิน performance?</b></summary>

**Effectiveness ($\varepsilon$):**
$$\varepsilon = \frac{q_{actual}}{q_{max}} = \frac{q_{actual}}{C_{min}(T_{h,in} - T_{c,in})}$$

เป็น measure ของประสิทธิภาพ — 1 คือ ideal heat exchanger

**Number of Transfer Units (NTU):**
$$NTU = \frac{UA}{C_{min}}$$

เป็น measure ของ size — NTU สูงแสดงถึง heat transfer area หรือ coefficient สูง

**Relationship (Counter-flow):**
$$\varepsilon = \frac{1 - \exp[-NTU(1 - C_r)]}{1 - C_r \exp[-NTU(1 - C_r)]}$$

เมื่อ1$C_r = C_{min}/C_{max}1— heat capacity ratio

**การใช้ใน CFD:**
1. **Extract from simulation:**
   ```python
   # From function objects
   T_hot_in = 350, T_hot_out = 330
   T_cold_in = 300, T_cold_out = 320
   m_dot_hot = 0.5, Cp_hot = 1005
   m_dot_cold = 0.6, Cp_cold = 4181
   
   C_hot = m_dot_hot * Cp_hot
   C_cold = m_dot_cold * Cp_cold
   C_min = min(C_hot, C_cold)
   
   Q_actual = m_dot_hot * Cp_hot * (T_hot_in - T_hot_out)
   Q_max = C_min * (T_hot_in - T_cold_in)
   epsilon = Q_actual / Q_max
   ```

2. **Compare กับ theory:**
   - Calculate NTU จาก geometry ($U$,1$A$)
   - Verify1$\varepsilon1matches theoretical value ภายใน 10%

3. **Optimization:**
   - Vary geometry และ monitor1$\varepsilon$
   - Target: maximize1$\varepsilon1สำหรับ given pressure drop

**ข้อดีของ NTU method:**
- ไม่ต้องทราบ outlet temperatures ล่วงหน้า
- เหมาะสำหรับ design optimization
- ใช้ได้กับทุก flow arrangements
</details>

---

## Related Documents

### Prerequisites
- **Heat Transfer Fundamentals:** [Energy Equation Fundamentals](../../04_HEAT_TRANSFER/01_Energy_Equation_Fundamentals.md)
- **Conjugate Heat Transfer Theory:** [Conjugate Heat Transfer](../../04_HEAT_TRANSFER/04_Conjugate_Heat_Transfer.md)
- **Turbulence Wall Treatment:** [Wall Treatment](../../03_TURBULENCE_MODELING/03_Wall_Treatment.md)

### Related Applications
- **บทก่อนหน้า:** [Internal Flow and Piping](02_Internal_Flow_and_Piping.md)
- **บทถัดไป:** [04_HVAC_Applications.md](04_HVAC_Applications.md)

### Practical Skills
- **Mesh Quality:** [Mesh Quality Criteria](../../05_MESH_QUALITY_AND_MANIPULATION/01_Mesh_Quality_Criteria.md)
- **Cell Zones and topoSet:** [Using TopoSet and CellZones](../../05_MESH_QUALITY_AND_MANIPULATION/02_Using_TopoSet_and_CellZones.md)
- **Function Objects:** [Introduction to Function Objects](../../06_RUNTIME_POST_PROCESSING/01_Introduction_to_FunctionObjects.md)
- **Forces and Coefficients:** [Forces and Coefficients](../../06_RUNTIME_POST_PROCESSING/02_Forces_and_Coefficients.md)