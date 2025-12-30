# Internal Flow and Piping

การจำลองการไหลในท่อและระบบท่อสำหรับการออกแบบระบบขนส่งของไหล

---

## Learning Objectives

เมื่ออ่านจบบทนี้ คุณจะสามารถ:

1. **ระบุ flow regime** ได้อย่างถูกต้องจากค่า Reynolds number และเลือก turbulence model ที่เหมาะสม
2. **คำนวณ pressure drop** ในท่อโดยใช้ Darcy-Weisbach equation พร้อมทั้งประเมิน friction factor สำหรับ laminar/turbulent flow
3. **ตั้งค่า boundary conditions** ใน OpenFOAM สำหรับ internal flow problems ทั้ง steady-state และ transient cases
4. **ประเมิน entry length requirements** เพื่อกำหนด velocity profile ที่เหมาะสมสำหรับ inlet
5. **ใช้ function objects** เพื่อตรวจสอบ pressure drop, wall shear stress, และ forces ระหว่าง simulation

---

## 1. Why Internal Flow Matters

### WHAT: Internal Flow Applications

Internal flow simulation คือการวิเคราะห์การไหลของของไหลภายในพื้นที่จำกัด เช่น ท่อ ช่องทาง หรือ ducts

**Engineering Applications:**
- **Piping systems:** ท่อส่งน้ำ ท่อน้ำมัน ท่อก๊าซ
- **HVAC ducts:** ระบบระบายอากาศและปรับอากาศ
- **Heat exchangers:** ช่องทางภายในเครื่องแลกเปลี่ยนความร้อน
- **Blood vessels:** การไหลของเลือดในหลอดเลือด (biofluid mechanics)
- **Fuel lines:** ระบบส่งเชื้อเพลิงในเครื่องยนต์

### WHY: Physical Importance

**Pump Sizing & Energy Consumption:**
- Pressure drop สัมพันธ์โดยตรงกับ **pump power requirement**: $P = \dot{m} \Delta p / \rho$
- การเลือกเส้นทางท่อและขนาดท่อที่เหมาะสมสามารถลด **operating cost** ได้มหาศาล
- Friction losses คิดเป็น 10-30% ของพลังงานทั้งหมดในระบบส่งน้ำมันขนาดใหญ่

**Flow Regime Impact:**
- **Laminar flow:** Viscous forces dominate → friction factor ∝ 1/Re → pressure drop ∝ velocity
- **Turbulent flow:** Inertial forces dominate → friction factor ~constant → pressure drop ∝ velocity²

**Design Implications:**
- การทำนาย pressure drop อย่างแม่นยำช่วยป้องกัน **cavitation** ใน pumps
- Entry length effects สำคัญใน compact heat exchangers
- Wall shear stress สำคัญใน erosion/corrosion prediction

### HOW: OpenFOAM Implementation

OpenFOAM จัดเตรียม solvers และ tools สำหรับ internal flow:

| Component | Purpose |
|-----------|---------|
| `simpleFoam` | Steady-state incompressible flow |
| `pimpleFoam` | Transient incompressible flow |
| `buoyantSimpleFoam` | Heat transfer with buoyancy |
| `wallShearStress` function object | Compute τ_w on walls |
| `surfaceFieldValue` function object | Monitor pressure at boundaries |

**Cross-references:**
- Turbulence modeling: → MODULE_03_SINGLE_PHASE_FLOW/CONTENT/03_TURBULENCE_MODELING
- Heat transfer: → MODULE_03_SINGLE_PHASE_FLOW/CONTENT/04_HEAT_TRANSFER
- Wall treatment: → MODULE_03_SINGLE_PHASE_FLOW/CONTENT/03_TURBULENCE_MODELING/03_Wall_Treatment.md

---

## 2. Flow Regime Identification

### Reynolds Number for Pipe Flow

$$Re_D = \frac{\rho U D_h}{\mu} = \frac{U D_h}{\nu}$$

ที่ไหน:
- $D_h$ = hydraulic diameter ($4A/P$ for non-circular ducts)
- $U$ = average velocity ($\dot{V}/A$)

### Flow Regime Criteria

| $Re_D$ Range | Regime | Characteristics | Velocity Profile |
|--------------|--------|-----------------|------------------|
| < 2300 | **Laminar** | Viscous forces dominant, streamline flow | Parabolic: $u(r) = 2U_{avg}[1-(r/R)^2]$ |
| 2300-4000 | **Transitional** | Intermittent turbulence, unstable | Varies, difficult to predict |
| > 4000 | **Turbulent** | Inertial forces dominant, chaotic mixing | Plug-like with thin viscous sublayer |

### Velocity Profile Comparison

**Laminar Profile (Parabolic):**
$$u(r) = 2U_{avg}\left[1 - \left(\frac{r}{R}\right)^2\right]$$

- Centerline velocity: $u_{center} = 2U_{avg}$
- Mean velocity: $U_{avg} = 0.5 u_{center}$
- Wall shear stress: $\tau_w = \frac{8\mu U_{avg}}{D}$

**Turbulent Profile (Law of the Wall):**
$$u^+ = \frac{1}{\kappa}\ln y^+ + B$$

ที่ไหน:
- $u^+ = u/u_\tau$ (dimensionless velocity)
- $y^+ = y u_\tau/\nu$ (dimensionless wall distance)
- $\kappa \approx 0.41$ (von Kármán constant)
- $B \approx 5.0$ (intercept constant)

- Centerline velocity: $u_{center} \approx 1.2-1.3 U_{avg}$ (depends on Re)
- Thinner boundary layer compared to laminar
- Higher mixing → better heat transfer but higher friction

### Practical Application in OpenFOAM

**Choosing Turbulence Model:**
```cpp
// RASProperties laminar vs turbulent
simulationType  RAS;

RAS
{
    RASModel kEpsilon;  // Re > 4000
    turbulence on;
    
    // For laminar flow (Re < 2300):
    // RASModel laminar;
    // turbulence off;
}
```

---

## 3. Pressure Drop Calculation

### Darcy-Weisbach Equation

**Why This Matters for Pump Sizing:**
$$\Delta p = f \frac{L}{D} \frac{\rho U^2}{2}$$

แต่ละ component:
- $\Delta p$ = pressure drop (Pa)
- $f$ = Darcy friction factor
- $L$ = pipe length (m)
- $D$ = pipe diameter (m)
- $\rho$ = fluid density (kg/m³)
- $U$ = average velocity (m/s)

**Pump Power Requirement:**
$$P_{pump} = \frac{\dot{m} \Delta p_{total}}{\rho \eta} = \frac{Q \Delta p_{total}}{\eta}$$

ที่ไหน:
- $\dot{m}$ = mass flow rate (kg/s)
- $Q$ = volumetric flow rate (m³/s)
- $\eta$ = pump efficiency (typically 0.6-0.8)

### Friction Factor Determination

**Laminar Flow (Re < 2300):**
$$f = \frac{64}{Re_D}$$

- Exact solution from Navier-Stokes
- Independent of surface roughness

**Turbulent Flow (Re > 4000):**

*Smooth Pipes (Blasius):*
$$f = \frac{0.316}{Re_D^{0.25}} \quad (4000 < Re < 10^5)$$

*Rough Pipes (Colebrook-White):**
$$\frac{1}{\sqrt{f}} = -2\log_{10}\left(\frac{\epsilon/D}{3.7} + \frac{2.51}{Re_D\sqrt{f}}\right)$$

ที่ไหน $\epsilon$ = absolute roughness height (m)

**Typical Roughness Values:**
| Material | $\epsilon$ (mm) |
|----------|-----------------|
| PVC/plastic | 0.0015 |
| Steel (new) | 0.045 |
| Steel (rusty) | 0.15-0.3 |
| Concrete | 0.3-3.0 |

### Minor Losses (Fittings)

**Why Minor Losses Matter:**
ในระบบท่อจริง การสูญเสียจาก fittings อาจคิดเป็น 20-50% ของ total pressure loss

$$\Delta p_{minor} = K \frac{\rho U^2}{2}$$

| Fitting Type | Loss Coefficient $K$ |
|--------------|---------------------|
| 90° smooth elbow (R/D = 1.5) | 0.2-0.3 |
| 90° sharp elbow | 1.1 |
| Tee junction (flow through) | 0.6 |
| Tee junction (branch flow) | 1.8 |
| Gate valve (fully open) | 0.15 |
| Globe valve (fully open) | 10 |

**Total Pressure Drop:**
$$\Delta p_{total} = \Delta p_{friction} + \sum \Delta p_{minor}$$

### OpenFOAM Verification

```cpp
// system/controlDict for pressure monitoring
pDrop
{
    type            surfaceFieldValue;
    libs            ("libfieldFunctionObjects.so");
    
    operation       weightedAverage;
    weightField     phi;
    
    region          patches;
    patches         (inlet outlet);
    
    fields
    (
        p
    );
    
    writeFields     false;
    writeLocation   none;
}
```

---

## 4. Entry Length Requirements

### Why Entry Length Matters

**Developing vs Fully-Developed Flow:**
- **Entrance region:** Velocity profile กำลัง develop จาก uniform profile → parabolic/turbulent profile
- **Fully-developed region:** Profile ไม่เปลี่ยนแปลงตามแกนท่อ
- **Wall shear stress:** สูงกว่าใน entrance region → friction factor สูงกว่าค่า theoretical

**Design Impact:**
- ถ้าท่อสั้นกว่า entry length → ใช้ fully-developed formulas จะ **underpredict pressure drop**
- Compact heat exchensors → อาจทำงานใน developing flow region เป็นหลัก
- ต้องใช้ inlet BC ที่ถูกต้องเพื่อให้ simulation realistic

### Entry Length Formulas

| Flow Regime | Entry Length $L_e$ | Practical Implication |
|-------------|-------------------|----------------------|
| Laminar | $L_e \approx 0.06 \cdot D \cdot Re_D$ | Can be very long: $L_e = 60D$ at Re=1000 |
| Turbulent | $L_e \approx 4.4 \cdot D \cdot Re_D^{1/6}$ | Shorter: $L_e \approx 20-30D$ for most cases |

**Example Calculation:**
- Water flow ($D=50$ mm, $U=1$ m/s, $\nu=10^{-6}$ m²/s)
- $Re = (1 \times 0.05)/10^{-6} = 50,000$ (turbulent)
- $L_e = 4.4 \times 0.05 \times (50000)^{1/6} \approx 1.1$ m ($22D$)

### OpenFOAM Boundary Conditions

**Case 1: Long Pipe (L >> L_e) — Use Uniform Inlet**
```cpp
// 0/U
inlet
{
    type            fixedValue;
    value           uniform (1 0 0);  // Uniform velocity
}
```

**Case 2: Short Pipe (L < L_e) — Use Developed Profile**
```cpp
// 0/U — Parabolic profile (codedFixedValue)
inlet
{
    type            codedFixedValue;
    value           uniform (0 0 0);
    
    code
    #{
        const faceList& faces = patch().patch().faceList();
        const vectorField& Cf = patch().Cf();
        
        vectorField& field = *this;
        
        scalar Uavg = 1.0;
        scalar R = 0.025;  // Pipe radius
        
        forAll(faces, i)
        {
            scalar r = mag(Cf[i].component(1));  // Distance from centerline
            field[i] = vector(2*Uavg*(1 - sqr(r/R)), 0, 0);
        }
    #};
}
```

**Case 3: Turbulent Profile (Power Law)**
$$u(r) = u_{max}\left(1 - \frac{r}{R}\right)^{1/n}$$

ที่ไหน $n \approx 7$ (for Re ≈ 10⁵)

---

## 5. OpenFOAM Solver Selection and Setup

### Solver Selection Guide

| Solver | Application | Key Features |
|--------|-------------|--------------|
| `simpleFoam` | Steady-state incompressible | SIMPLE algorithm, fast convergence |
| `pimpleFoam` | Transient incompressible | PISO/PIMPLE, time-accurate |
| `buoyantSimpleFoam` | Steady heat transfer | Boussinesq approximation |
| `buoyantPimpleFoam` | Transient heat transfer | Natural convection capable |
| `boundaryFoam` | Developing flow | 1D-like, for entrance region |

**Cross-reference:** → MODULE_03_SINGLE_PHASE_FLOW/CONTENT/01_INCOMPRESSIBLE_FLOW_SOLVERS/02_Standard_Solvers.md

### Boundary Condition Setup

**0/U — Velocity:**
```cpp
dimensions      [0 1 -1 0 0 0 0];

internalField   uniform (0 0 0);

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform (1 0 0);  // Or mapped/parabolic
    }
    
    outlet
    {
        type            zeroGradient;     // Fully-developed assumption
    }
    
    walls
    {
        type            noSlip;            // u_wall = 0
    }
}
```

**0/p — Pressure:**
```cpp
dimensions      [0 2 -2 0 0 0 0];

internalField   uniform 0;

boundaryField
{
    inlet
    {
        type            zeroGradient;
    }
    
    outlet
    {
        type            fixedValue;
        value           uniform 0;        // Reference pressure (gauge)
    }
    
    walls
    {
        type            zeroGradient;
    }
}
```

**0/k — Turbulent Kinetic Energy (if applicable):**
```cpp
dimensions      [0 2 -2 0 0 0 0];

internalField   uniform 0.1;

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 0.1;      // I = 0.05-0.10 for pipes
    }
    
    outlet
    {
        type            zeroGradient;
    }
    
    walls
    {
        type            kqRWallFunction;
        value           uniform 0;
    }
}
```

**0/nuTilda — Spalart-Allmaras (alternative):**
```cpp
boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 1e-6;
    }
    
    walls
    {
        type            nutWallFunction;
        value           uniform 0;
    }
}
```

### fvSchemes and fvSolution

**system/fvSchemes:**
```cpp
ddtSchemes
{
    default         steadyState;  // or Euler for transient
}

gradSchemes
{
    default         Gauss linear;
}

divSchemes
{
    default         Gauss upwind;  // Use linear for converged cases
}

laplacianSchemes
{
    default         Gauss linear corrected;
}
```

**system/fvSolution:**
```cpp
solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-06;
        relTol          0.01;
    }
    
    U
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-05;
        relTol          0.1;
    }
}

SIMPLE
{
    nNonOrthogonalCorrectors 0;
    
    consistent      yes;  // Better convergence for pressure
}

relaxationFactors
{
    fields
    {
        p               0.3;
        U               0.7;
    }
}
```

---

## 6. Function Objects for Analysis

### Pressure Drop Monitoring

**Why Monitor During Simulation:**
- Verify convergence (pressure should stabilize)
- Detect numerical oscillations early
- Compare with empirical correlations

```cpp
// system/controlDict

pressureMonitor
{
    type            surfaceFieldValue;
    libs            ("libfieldFunctionObjects.so");
    
    writeFields     false;
    
    operation       weightedAverage;
    weightField     phi;
    
    region          patches;
    patches         (inlet outlet);
    
    fields
    (
        p
    );
    
    // Log pressure drop
    log             true;
    
    // Write to file
    execute         100;
    writeTime       yes;
}
```

### Wall Shear Stress

**Why Wall Shear Matters:**
- Directly related to friction factor: $f = \frac{8\tau_w}{\rho U^2}$
- Erosion/corrosion prediction
- Boundary layer verification

```cpp
wallShear
{
    type            wallShearStress;
    libs            ("libfieldFunctionObjects.so");
    
    // Write wall shear field
    writeFields     true;
    
    // Calculate on specific patches
    patches         (walls);
    
    execute         writeTime;
    writeTime       yes;
}
```

### Force Calculation

```cpp
forceCoeffs
{
    type            forceCoeffs;
    libs            ("libforces.so");
    
    patches         (walls);
    
    rhoInf          1000;       // Reference density (water)
    CofR            (0 0 0);    // Center of rotation
    
    liftDir         (0 1 0);
    dragDir         (1 0 0);
    pitchAxis       (0 0 1);
    
    magUInf         1.0;        // Reference velocity
    
    // Calculate coefficients
    log             true;
    writeFields     false;
}
```

### Flow Rate Monitoring

```cpp
flowRate
{
    type            surfaceFieldValue;
    libs            ("libfieldFunctionObjects.so");
    
    operation       sum;
    weightField     none;
    
    region          patches;
    patches         (inlet);
    
    fields
    (
        phi         // Volumetric flow rate [m³/s]
    );
    
    writeFields     false;
    log             true;
}
```

---

## 7. Mesh Guidelines for Internal Flow

### Mesh Quality Criteria

| Criterion | Target | Why It Matters |
|-----------|--------|----------------|
| Orthogonality | > 60° | Prevents non-orthogonal corrections |
| Aspect ratio | < 1000 | Avoids stiff equations in thin pipes |
| Skewness | < 0.85 | Maintains solution accuracy |
| Non-orthogonality | < 70° | Important for near-wall cells |

### y+ Requirements

**Why y+ Matters:**
- Incorrect y+ → wrong wall shear → wrong friction factor
- Affects turbulence model performance near walls

| Approach | Target y+ | Wall Treatment |
|----------|-----------|----------------|
| Wall functions | 30-300 | `nutWallFunction` (coarse mesh) |
| Low-Re models | < 1 | Resolve viscous sublayer (fine mesh) |

**Cross-reference:** → MODULE_03_SINGLE_PHASE_FLOW/CONTENT/03_TURBULENCE_MODELING/03_Wall_Treatment.md

### Boundary Layer Meshing

**Why Boundary Layers:**
- Resolve high velocity gradients near walls
- Critical for accurate wall shear stress
- Required for low-Re turbulence models

**snappyHexMeshDict Setup:**
```cpp
addLayers
{
    // Switch on layers
    layers
    {
        walls  // Patch name
        {
            nSurfaceLayers  15;        // Number of layers
            
            // Layer thickness parameters
            expansionRatio  1.2;       // Growth rate
            
            // Target final layer thickness
            finalLayerThickness  0.0005;  // [m]
            
            // Minimum thickness
            minThickness  0.0001;
            
            // Layer thickness controls
            relativeSizes  false;      // Use absolute [m]
        }
    }
    
    // General layer controls
    nGrow           0;                // Number of cell expansion
    featureAngle    180;              // Feature angle
    maxFaceThicknessRatio 0.5;
    
    // Quality controls
    nSmoothNormals  3;
    nSmoothThickness 10;
    minMedianAxisAngle 90;
}
```

**Estimating First Cell Height:**

For wall functions (y+ ≈ 50):
$$\Delta y = \frac{y^+ \nu}{u_\tau} = \frac{50 \nu}{U \sqrt{f/8}}$$

**Example:** Water flow at 1 m/s in 50 mm pipe (turbulent)
- $Re = 50,000$, $f \approx 0.021$
- $u_\tau = 1 \times \sqrt{0.021/8} = 0.051$ m/s
- $\Delta y = 50 \times 10^{-6} / 0.051 = 0.98$ mm

### Pipe Cross-Section Meshing

**Structured Mesh (blockMesh):**
```cpp
// cylinder block
hex (0 1 2 3 4 5 6 7) (100 20 1) simpleGrading (1 1 1)
```

Advantages:
- Highly orthogonal
- Efficient for circular pipes
- Easy boundary layer control

**O-Grid Mesh:**
Better for complex geometries and fittings

**Cross-reference:** → MODULE_02_MESHING_AND_CASE_SETUP/CONTENT/02_BLOCKMESH_MASTERY

---

## 8. Heat Transfer in Internal Flow

### Why Heat Transfer in Pipes Matters

**Applications:**
- Heat exchangers (shell and tube, plate heat exchangers)
- Solar thermal collectors
- Engine cooling systems
- Process industry (heating/cooling of fluids)

**Key Concepts:**
- Convective heat transfer coefficient $h$ depends on flow regime
- Turbulent flow → better mixing → higher $h$
- Entry effects → enhanced heat transfer

### Dittus-Boelter Correlation (Turbulent)

**Why This Correlation:**
- Widely used for internal turbulent flow (Re > 10,000)
- Valid for fully-developed flow with moderate temperature differences

$$Nu = 0.023 \cdot Re_D^{0.8} \cdot Pr^n$$

ที่ไหน:
- $n = 0.4$ for heating (wall hotter than fluid)
- $n = 0.3$ for cooling (wall cooler than fluid)

**Heat Transfer Coefficient:**
$$h = \frac{Nu \cdot k}{D}$$

ที่ไหน:
- $k$ = thermal conductivity of fluid [W/(m·K)]
- $D$ = pipe diameter [m]

**Heat Transfer Rate:**
$$\dot{Q} = h A (T_{wall} - T_{fluid})$$

### Laminar Flow Heat Transfer

**Constant Wall Temperature:**
$$Nu = 3.66 \quad \text{(fully-developed)}$$

**Constant Heat Flux:**
$$Nu = 4.36 \quad \text{(fully-developed)}$$

**Entry Length Effect:**
$$Nu_{entry} = Nu_{fd} \left(1 + \frac{0.0668 (D/L) Re Pr}{1 + 0.04 [(D/L) Re Pr]^{2/3}}\right)$$

### Prandtl Number Effects

| Fluid | Pr | Heat Transfer Characteristics |
|-------|-----|-------------------------------|
| Air | 0.7 | Thermal BL ≈ velocity BL |
| Water | 6-7 | Thermal BL thinner than velocity BL |
| Oils | > 100 | Thermal BL much thinner |
| Liquid metals | < 0.1 | Thermal BL much thicker |

**Cross-reference:** → MODULE_03_SINGLE_PHASE_FLOW/CONTENT/04_HEAT_TRANSFER/02_Heat_Transfer_Mechanisms.md

### OpenFOAM Thermal BCs

**0/T — Temperature:**
```cpp
dimensions      [0 0 0 1 0 0 0];

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 300;  // [K]
    }
    
    outlet
    {
        type            zeroGradient;
    }
    
    walls
    {
        type            fixedValue;  // Constant wall temperature
        value           uniform 350;  // [K]
        
        // OR: fixedFluxPressure (constant heat flux)
        // type            externalWallHeatFlux;
        // q               uniform 1000;  // [W/m²]
    }
}
```

---

## 9. Troubleshooting Common Issues

### Convergence Problems

| Symptom | Possible Cause | Solution |
|---------|----------------|----------|
| Residuals stuck at 10⁻² | Poor mesh quality | Check orthogonality, skewness |
| Pressure oscillating | Incorrect outlet BC | Use `fixedValue` with `zeroGradient` for U |
| Velocity diverging | Time step too large (transient) | Reduce Courant number < 1 |
| Slow convergence | Inadequate relaxation | Increase under-relaxation factors |

### Pressure Drop Discrepancies

**Measured ≠ Simulated:**

1. **Check Reynolds number:**
   ```bash
   # Post-process Re calculation
   foamCalc mag U
   # Average U × D / nu
   ```

2. **Verify wall treatment:**
   - y+ too high → wall functions invalid
   - y+ too low → coarse mesh resolving sublayer incorrectly

3. **Confirm fully-developed flow:**
   - Check if L > L_e
   - Compare velocity profiles at inlet vs outlet

4. **Minor losses:**
   - Did you include fittings in geometry?
   - Consider K factors in design calculations

### Entry Length Issues

**Problem:** Developing flow affects results

**Solutions:**
- Use longer pipe (L > 5×L_e)
- Apply developed velocity profile at inlet
- Use `boundaryFoam` for entrance region

### Turbulence Model Selection

**Cross-reference:** → MODULE_03_SINGLE_PHASE_FLOW/CONTENT/03_TURBULENCE_MODELING/02_RANS_Models.md

| Flow Type | Recommended Model | Why |
|-----------|-------------------|-----|
| Straight pipe (high Re) | k-ε or k-ω SST | Well-validated |
| Curved pipes/fittings | k-ω SST | Better for adverse pressure gradients |
| Low Re (< 10,000) | Spalart-Allmaras | More robust |
| Swirling flow | Reynolds Stress Model (RSM) | Captures anisotropy |

---

## 10. Practical Example: Water Pipe Flow

### Problem Statement

Calculate pressure drop for water flowing through a 50 mm diameter steel pipe, 10 m long, at 2 m/s average velocity.

**Given:**
- Water: $\rho = 998$ kg/m³, $\mu = 0.001$ Pa·s
- Pipe: $D = 50$ mm, $L = 10$ m, steel ($\epsilon = 0.045$ mm)

### Hand Calculation

**1. Reynolds Number:**
$$Re = \frac{998 \times 2 \times 0.05}{0.001} = 99,800 \quad \text{(turbulent)}$$

**2. Relative Roughness:**
$$\epsilon/D = 0.045/50 = 0.0009$$

**3. Friction Factor (Colebrook-White):**
Using Moody diagram or iterative solution:
$$f \approx 0.021$$

**4. Pressure Drop:**
$$\Delta p = 0.021 \times \frac{10}{0.05} \times \frac{998 \times 2^2}{2} = 8,380 \text{ Pa} \approx 0.08 \text{ bar}$$

**5. Pump Power (assuming η = 0.7):**
$$P = \frac{Q \Delta p}{\eta} = \frac{(\pi/4 \times 0.05^2 \times 2) \times 8380}{0.7} = 47 \text{ W}$$

### OpenFOAM Verification

**Setup:**
```bash
# Case directory structure
pipeFlow/
├── 0/
│   ├── U
│   ├── p
│   ├── k
│   └── omega
├── constant/
│   ├── transportProperties
│   └── turbulenceProperties
├── system/
│   ├── controlDict
│   ├── fvSchemes
│   └── fvSolution
└── Allrun
```

**Expected Results:**
- Simulation Δp should be within 5-10% of hand calculation
- Wall shear stress: $\tau_w = \Delta p \cdot D / (4L) = 10.5$ Pa
- Friction velocity: $u_\tau = \sqrt{\tau_w/\rho} = 0.103$ m/s
- y+ for first cell (0.5 mm): $y^+ = 0.0005 \times 0.103 / 10^{-6} = 51.5$ ✓

---

## Key Takeaways

### Critical Thresholds
- **Laminar flow:** Re < 2,300 → use parabolic inlet, $f = 64/Re$
- **Turbulent flow:** Re > 4,000 → use turbulent inlet or uniform profile, Colebrook-White for $f$
- **Transitional:** 2,300 < Re < 4,000 → avoid, unstable region

### Entry Length Formulas
- **Laminar:** $L_e \approx 0.06 \cdot D \cdot Re$ (can be > 60D)
- **Turbulent:** $L_e \approx 4.4 \cdot D \cdot Re^{1/6}$ (typically 20-30D)

### Common Boundary Condition Patterns
| Application | Inlet U | Outlet p | Inlet p | Outlet U |
|-------------|---------|----------|---------|----------|
| Standard pipe | fixedValue (uniform/profile) | fixedValue (0) | zeroGradient | zeroGradient |
| Mass flow specified | flowRateInletVelocity | fixedValue (0) | — | — |
| Pressure driven | zeroGradient | fixedValue (0) | fixedValue | zeroGradient |

### Pressure Drop Calculation
$$\Delta p = \left(f \frac{L}{D} + \sum K\right) \frac{\rho U^2}{2}$$

### y+ Guidelines
- **Wall functions:** 30 < y+ < 300 (typically ~50 for pipes)
- **Low-Re models:** y+ < 1 (fine mesh required)

### Cross-References
- Turbulence modeling → MODULE_03_SINGLE_PHASE_FLOW/CONTENT/03_TURBULENCE_MODELING
- Heat transfer → MODULE_03_SINGLE_PHASE_FLOW/CONTENT/04_HEAT_TRANSFER
- Mesh quality → MODULE_02_MESHING_AND_CASE_SETUP/CONTENT/05_MESH_QUALITY_AND_MANIPULATION
- Function objects → MODULE_02_MESHING_AND_CASE_SETUP/CONTENT/06_RUNTIME_POST_PROCESSING

---

## Concept Check

<details>
<summary><b>1. ทำไม $\Delta p \propto U^2$ ในช่วง Turbulent แต่ $\Delta p \propto U$ ในช่วง Laminar?</b></summary>

**Laminar flow:** Viscous forces dominate → shear stress $\tau_w \propto \mu (du/dy) \propto U$  
ดังนั้น $\Delta p \propto \tau_w \propto U$

**Turbulent flow:** Inertial forces dominate → shear stress สัมพันธ์กับ Reynolds stress $\tau_{turb} \sim \rho u'^2 \propto \rho U^2$  
และ friction factor $f \approx$ constant (weak function of Re)  
ดังนั้น $\Delta p = f \frac{L}{D} \frac{\rho U^2}{2} \propto U^2$

**Practical implication:** การเพิ่ม flow rate ใน turbulent regime ทำให้ pump power เพิ่มขึ้นรวดเร็วมาก ($P \propto U^3$)
</details>

<details>
<summary><b>2. Entry length สำคัญอย่างไรต่อการออกแบบระบบท่อ?</b></summary>

**Design consequences:**

1. **Short pipes (L < L_e):**
   - Wall shear stress สูงกว่า fully-developed flow
   - ใช้ friction factor มาตรฐานจะ **underpredict pressure drop** 10-30%
   - ต้องใช้ inlet BC ที่ realistic (parabolic/turbulent profile)

2. **Long pipes (L >> L_e):**
   - Fully-developed flow ในส่วนใหญ่ของท่อ
   - ใช้ standard correlations ได้แม่นยำ
   - Uniform inlet ยอมรับได้เพราะ developing region เล็กเมื่อเทียบกับ total length

3. **Compact heat exchangers:**
   - มักทำงานใน developing flow region
   - Heat transfer coefficient สูงกว่า fully-developed (entrance effect)
   - ต้องใช้ correlations ที่รองรับ entry effects

**CFD practice:** ตรวจสอบว่า inlet และ outlet profiles คล้ายกันหรือไม่ → ถ้าใช่ แสดงว่า fully-developed
</details>

<details>
<summary><b>3. `zeroGradient` ที่ outlet หมายความว่าอย่างไร และใช้ได้ทำไม?</b></summary>

**Mathematical definition:**
$$\frac{\partial \phi}{\partial n} = 0$$

เมื่อ $\phi$ คือ field variable (U, p, k, etc.) และ $n$ คือทิศทางตั้งฉากกับ boundary

**Physical interpretation:**
- Field ไม่เปลี่ยนแปลงเมื่อไหลผ่าน outlet
- การเปลี่ยนแปลงทั้งหมดเกิดขึ้น upstream แล้ว
- Equivalent to "fully-developed outflow" assumption

**When valid:**
- Outlet อยู่ไกลจาก disturbances (fittings, bends)
- Flow ไม่มี recirculation หรือ backflow
- Single-phase, incompressible flow

**Warning signs:**
- ถ้าเห็น reverse flow ใน results → outlet อยู่ใกล้ disturbances มากเกินไป
- แก้ไข: เลื่อน outlet ไกลออกหรือใช้ `outletInlet` BC

**Alternatives:**
- `pressureInletOutletVelocity`: แก้ปัญหา backflow
- `convectiveOutlet`: สำหรับ transient flow
</details>

<details>
<summary><b>4. ทำไมต้องใช้ wall functions? ไม่ resolve ทั้ง boundary layer เลย?</b></summary>

**Why wall functions exist:**

| Approach | First Cell Height | Cells in BL | Mesh Size | Computational Cost |
|----------|------------------|-------------|-----------|-------------------|
| Low-Re (resolve BL) | y+ < 1 | 20-50 | ~10⁶-10⁷ cells | High |
| Wall functions | y+ ≈ 30-100 | 1-5 | ~10⁴-10⁵ cells | Low |

**Trade-offs:**

**Wall functions (recommended for most industrial applications):**
- ✓ Mesh efficient สำหรับ high Re flows
- ✓ แม่นยำพอสำหรับ engineering design (±10-20%)
- ✗ ไม่เหมาะกับ low Re, strong pressure gradients, หรือ separation

**Low-Re models (resolve BL):**
- ✓ แม่นยำกว่า (±5%)
- ✓ จำเป็นสำหรับ heat transfer, separation flows
- ✗ Mesh intensive
- ✗ ต้องใช้ fine mesh ตลอด boundary layer

**Practical rule:** 
- Start with wall functions (y+ ≈ 50)
- Switch to resolved BL เฉพาะกรณีที่ต้องการความแม่นยำสูงหรือ low Re

**Cross-reference:** → MODULE_03_SINGLE_PHASE_FLOW/CONTENT/03_TURBULENCE_MODELING/03_Wall_Treatment.md
</details>

<details>
<summary><b>5. จะเลือกระหว่าง `simpleFoam` และ `pimpleFoam` อย่างไร?</b></summary>

**Decision flowchart:**

```
Is flow steady?
├─ Yes → simpleFoam (faster)
└─ No → pimpleFoam
    │
    Is flow inherently unsteady?
    ├─ Yes (vortex shedding, pulsating flow) → pimpleFoam
    └─ No (just transients) → simpleFoam might converge
```

**simpleFoam characteristics:**
- ✓ Steady-state solver
- ✓ Faster convergence (10-100 iterations)
- ✓ Lower memory usage
- ✗ Cannot capture transient phenomena
- ✗ May not converge for highly separated flows

**pimpleFoam characteristics:**
- ✓ Transient solver (PISO/PIMPLE algorithm)
- ✓ Captures time-dependent physics
- ✓ More robust for complex flows
- ✗ Requires many time steps (10³-10⁶)
- ✗ Higher computational cost

**Rule of thumb:**
- **Internal pipe flow (single phase, steady conditions)** → simpleFoam
- **Start-up transients, pulsatile flow, flow instabilities** → pimpleFoam
- **Unsure?** Run simpleFoam first, check residuals; if not converging, switch to pimpleFoam

**Cross-reference:** → MODULE_03_SINGLE_PHASE_FLOW/CONTENT/01_INCOMPRESSIBLE_FLOW_SOLVERS/02_Standard_Solvers.md
</details>

---

## Related Documents

- **บทก่อนหน้า:** [01_External_Aerodynamics.md](01_External_Aerodynamics.md)
- **บทถัดไป:** [03_Heat_Exchangers.md](03_Heat_Exchangers.md)
- **Turbulence modeling:** MODULE_03_SINGLE_PHASE_FLOW/CONTENT/03_TURBULENCE_MODELING
- **Heat transfer:** MODULE_03_SINGLE_PHASE_FLOW/CONTENT/04_HEAT_TRANSFER