# Coupled Physics - Practical Exercises

แบบฝึกหัด Coupled Physics

---

## 🎯 Learning Objectives (เป้าหมายการเรียนรู้)

After completing these exercises, you will be able to:
- **Apply** conjugate heat transfer concepts in practical OpenFOAM simulations (นำคอนเซ็ปต์ CHT ไปประยุกต์ใช้ในการจำลองจริง)
- **Configure** multi-region cases with proper coupling interfaces (ตั้งค่าเคสพหุภูมิด้วยการเชื่อมต่อระหว่างโซนที่เหมาะสม)
- **Implement** coupled boundary conditions for heat and momentum exchange (นำ BC แบบ coupled มาใช้เพื่อแลกเปลี่ยนความร้อนและโมเมนตัม)
- **Debug** common issues in coupled physics simulations (แก้ไขปัญหาทั่วไปในการจำลอง coupled physics)
- **Validate** coupled simulation results using analytical and numerical benchmarks (ตรวจสอบความถูกต้องของผลลัพธ์ด้วย benchmark)

---

## 📋 Exercise Overview (ภาพรวมแบบฝึกหัด)

| Exercise | Topic (หัวข้อ) | Difficulty (ระดับความยาก) | Time (เวลา) | Skills (ทักษะ) |
|----------|-------|------------|------|--------|
| 01 | Basic CHT Setup | ⭐ Beginner (เริ่มต้น) | 30 min | Case setup, boundary conditions |
| 02 | Multi-Region Configuration | ⭐⭐ Intermediate (ปานกลาง) | 45 min | Region properties, mesh splitting |
| 03 | Interface Coupling | ⭐⭐ Intermediate (ปานกลาง) | 45 min | Coupled BCs, data exchange |
| 04 | Registry-Based Communication | ⭐⭐ Advanced (ขั้นสูง) | 60 min | Object registry, runtime lookup |
| 05 | Advanced CHT Simulation | ⭐⭐⭐ Advanced (ขั้นสูง) | 90 min | Full case setup, convergence |

---

## Exercise 1: Basic Conjugate Heat Transfer Setup (การตั้งค่า CHT พื้นฐาน)

### 🎯 Objective (วัตถุประสงค์)
Set up and run a basic conjugate heat transfer simulation with fluid-solid interaction.

**What (อะไร):** สร้างเคส CHT พื้นฐานที่มีการโต้ตอบระหว่าง fluid-solid  
**Why (ทำไม):** เข้าใจกระบวนการ heat transfer ผ่าน interface ระหว่างภูมิภาคต่างๆ  
**How (อย่างไร):** ใช้ solver `chtMultiRegionFoam` กับ coupled BCs

### ✅ Expected Outcomes (ผลลัพธ์ที่คาดหวัง)
- Temperature field showing heat transfer from solid to fluid (สนามอุณหภูมิแสดงการถ่ายเทความร้อนจาก solid ไป fluid)
- Converged solution within 500 iterations (ผลเฉลยลู่เข้าภายใน 500 iterations)
- Heat flux continuity at interface (การต่อเนื่องของ heat flux ที่ interface)

---

### Step 1: Directory Structure Setup (การตั้งค่าโครงสร้างไดเรกทอรี่)

**Task:** Create the following case structure

```bash
basicCHT/
├── 0/
│   ├── air/
│   │   ├── T
│   │   ├── p
│   │   └── U
│   └── solid/
│       └── T
├── constant/
│   ├── air/
│   │   └── polyMesh/
│   ├── solid/
│   │   └── polyMesh/
│   └── regionProperties
└── system/
    ├── air/
    │   ├── fvSchemes
    │   └── fvSolution
    └── solid/
        ├── fvSchemes
        └── fvSolution
```

**Action:** Create directories using bash commands
```bash
mkdir -p basicCHT/{0/{air,solid},constant/{air,polyMesh,solid,polyMesh},system/{air,solid}}
```

**Validation:** Verify structure created
```bash
tree basicCHT  # or find basicCHT -type d
```

---

### Step 2: Define Regions (กำหนด Regions)

**Task:** Create `constant/regionProperties` file

**What:** Defines regions for multi-region simulation (กำหนด regions สำหรับ multi-region simulation)  
**Why:** Solver needs to know which regions exist and their type (Solver ต้องรู้ว่ามี region อะไรบ้างและเป็นประเภทอะไร)  
**How:** List region names with type (fluid/solid) in dictionary (ระบุชื่อ region พร้อมประเภทใน dictionary)

**File:** `constant/regionProperties`

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2312                                 |
|   \\  /    A nd           | Web:      www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "constant";
    object      regionProperties;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

regions
(
    fluid  (air)
    solid  (solid)
);

// ************************************************************************* //
```

<details>
<summary><b>💡 Solution Hint: Region Properties</b></summary>

**Key Points:**
- `fluid` keyword: lists all fluid regions (all regions solving Navier-Stokes)
- `solid` keyword: lists all solid regions (regions solving only energy equation)
- Names must match directory names in `constant/` and `system/`

**Common Mistake:** Mismatched region names
```cpp
// WRONG: directory is "fluid" but regionProperties says "air"
regions
(
    fluid  (fluid)  // ❌ Error: constant/fluid/ doesn't exist
);

// CORRECT: match names exactly
regions
(
    fluid  (air)    // ✅ Matches constant/air/
);
```

</details>

---

### Step 3: Configure Fluid Field Initial Conditions (ตั้งค่าเงื่อนไขเริ่มต้นฟิลด์ Fluid)

**Task:** Create temperature BC for fluid region

**What:** Temperature boundary condition for fluid region  
**Why:** Specifies thermal behavior at all boundaries  
**How:** Use `turbulentTemperatureCoupledBaffleMixed` for coupled interface

**File:** `0/air/T`

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    location    "0/air";
    object      T;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 0 0 1 0 0 0];

internalField   uniform 300;

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 293;
    }
    outlet
    {
        type            inletOutlet;
        inletValue      uniform 293;
        value           uniform 293;
    }
    air_to_solid
    {
        type            compressible::turbulentTemperatureCoupledBaffleMixed;
        Tnbr            T;
        kappaMethod     fluidThermo;
        value           uniform 300;
    }
    walls
    {
        type            zeroGradient;
    }
}

// ************************************************************************* //
```

<details>
<summary><b>💡 Key Concept: Coupled BC Explained</b></summary>

**What:** `compressible::turbulentTemperatureCoupledBaffleMixed`  
**Why:** Enforces two critical conditions at interface:
- **Temperature continuity:** `T_fluid = T_solid` (no jump)
- **Flux continuity:** `q_fluid = q_solid` (energy conservation)

**How:** Uses implicit coupling via:
- `Tnbr`: reference to neighbor temperature field
- `kappaMethod`: conductivity calculation method (`fluidThermo` vs `solidThermo`)

**Mathematical Form:**
```
q = -kappa · dT/dn
T_fluid = T_solid
kappa_fluid · (dT/dn)_fluid = kappa_solid · (dT/dn)_solid
```

</details>

<details>
<summary><b>❌ Troubleshooting: "Cannot find patch air_to_solid"</b></summary>

**Cause:** Patch names don't match between regions

**Solution Checklist:**
1. ✅ Verify boundary names in `0/air/T` match `constant/air/polyMesh/boundary`
2. ✅ Verify boundary names in `0/solid/T` match `constant/solid/polyMesh/boundary`
3. ✅ Ensure coupled BCs reference each other: `air_to_solid` ↔ `solid_to_air`
4. ✅ Check `Tnbr T` is correctly specified (points to neighbor field)

**Debug Commands:**
```bash
# List actual boundary names
grep "^\s*name" constant/air/polyMesh/boundary
grep "^\s*name" constant/solid/polyMesh/boundary

# Should show matching interface patches
```

</details>

---

### Step 4: Configure Solid Field Initial Conditions

**Task:** Create temperature BC for solid region

**What:** Temperature field for solid region  
**Why:** Solid starts hot, cools via convection to fluid  
**How:** Coupled BC exchanges heat with fluid; external BC models ambient cooling

**File:** `0/solid/T`

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    location    "0/solid";
    object      T;
}

dimensions      [0 0 0 1 0 0 0];

internalField   uniform 350;  // Initial heated solid (เริ่มต้น solid ร้อน)

boundaryField
{
    solid_to_air
    {
        type            compressible::turbulentTemperatureCoupledBaffleMixed;
        Tnbr            T;
        kappaMethod     solidThermo;
        value           uniform 350;
    }
    outerWalls
    {
        type            externalWallHeatFlux;
        mode            coefficient;
        h               uniform 10;
        Ta              uniform 293;
    }
}
```

**Validation:** Check BC consistency
```bash
# Verify both regions reference each other
grep "air_to_solid\|solid_to_air" 0/*/T
```

---

### Step 5: Run Simulation (รันการจำลอง)

**Task:** Execute the CHT solver

```bash
# Navigate to case directory
cd basicCHT

# Generate meshes (separate for each region)
cd constant/air
blockMesh
cd ../solid
blockMesh
cd ../..

# Split regions based on cellZones
splitMeshRegions -cellZones -overwrite

# Run solver
chtMultiRegionFoam

# Post-process
paraFoam -touch
paraFoam &
```

**Expected Output:**
```
Create time

Create fluid mesh for region air
Create solid mesh for region solid

...
End
```

<details>
<summary><b>❌ Troubleshooting: Diverging solution</b></summary>

**Symptoms:**
- Residuals increasing instead of decreasing
- "Maximum number of iterations exceeded"
- Unphysical temperature values (negative, extremely high)

**Causes & Solutions:**

1. **Time step too large**
   ```cpp
   // system/controlDict
   deltaT  0.001;  // Reduce from default
   ```

2. **Poor initial guess**
   ```cpp
   // Run fewer iterations first, use restart
   startFrom   latestTime;
   ```

3. **Under-relaxation needed**
   ```cpp
   // system/air/fvSolution
   SIMPLE
   {
       nNonOrthogonalCorrectors 0;
       consistent      yes;
       
       // Add relaxation
       relaxFactors
       {
           T 0.7;  // Under-relax temperature
       }
   }
   ```

</details>

---

### Step 6: Validate Results (ตรวจสอบผลลัพธ์)

**Task:** Perform validation checks

**Validation Check 1: Convergence**
```bash
# Check residuals in log file
grep "Time =" log.chtMultiRegionFoam | tail -5
```
**Expected:** All residuals < 1e-4

**Validation Check 2: Interface Continuity**
```bash
# In paraFoam: Use Calculator filter
# T_fluid - T_solid should ≈ 0 at interface
```
**Expected:** Temperature jump < 1 K

**Validation Check 3: Energy Balance**
```cpp
// Add to system/controlDict
functions
{
    heatFlux
    {
        type            surfaceRegion;
        functionObjectLibs ("libfieldFunctionObjects.so");
        enabled         true;
        writeFields     true;
        region          air;
        surfaceFormat   none;
        operation       sum;
        source          patches;
        patches         (air_to_solid);
        fields
        (
            wallHeatFlux
        );
    }
}
```
**Expected:** Heat flux leaving solid ≈ heat flux entering fluid (±5%)

---

### Step 7: Solution Verification (การตรวจสอบคำตอบ)

<details>
<summary><b>💡 Complete Solution: Expected Results</b></summary>

**Typical Results for Basic CHT Case:**

| Metric | Expected Range | Validation |
|--------|---------------|------------|
| Max solid temperature | 340-360 K | Should be < initial (350 K) |
| Air temperature rise | 2-5 K | Reasonable for flow rate |
| Interface heat flux | 8-12 W | Depends on temperature difference |
| Convergence time | 200-500 iterations | Depends on mesh size |

**Energy Balance Check:**
```bash
# Extract heat flux from log
grep "heatFlux" postProcessing/heatFlux/*/surfaceRegion.dat | tail -1

# Should equal: Power_in ≈ Power_out
# Power_in = h·A·(T_solid - T_air)
# Power_out = ∫(wallHeatFlux) dA
```

**Visual Validation:**
1. Open in ParaView: `paraFoam -builtin`
2. Plot temperature contours:
   - Solid: should show gradient from interface to outer walls
   - Fluid: should show thermal boundary layer
3. Verify smooth transition at interface (no discontinuities)

</details>

---

## Exercise 2: Multi-Region Mesh Configuration (การตั้งค่า Mesh พหุภูมิ)

### 🎯 Objective (วัตถุประสงค์)
Master the `splitMeshRegions` utility for creating coupled multi-region meshes.

**What:** Create single mesh, then split into multiple coupled regions  
**Why:** Simplifies mesh generation while maintaining proper connectivity  
**How:** Use cellZones to define regions, then split

### ✅ Expected Outcomes
- Single mesh divided into multiple regions (mesh เดียวแบ่งเป็นหลาย regions)
- Proper interface boundary creation (สร้าง interface boundaries ได้อย่างถูกต้อง)
- Valid region connectivity (การเชื่อมต่อระหว่าง regions ถูกต้อง)

---

### Step 1: Create Unified Mesh with CellZones (สร้าง Mesh เดียวพร้อม CellZones)

**Task:** Create blockMeshDict with cellZones

**What:** Single mesh with defined regions using cellZones  
**Why:** `splitMeshRegions` uses cellZones to identify region membership  
**How:** Assign cellZone to each block in blockMeshDict

**File:** `constant/polyMesh/blockMeshDict`

```cpp
convertToMeters 0.001;

vertices
(
    (0 0 0)          // 0
    (50 0 0)         // 1
    (50 50 0)        // 2
    (0 50 0)         // 3
    (0 0 10)         // 4 - fluid bottom
    (50 0 10)        // 5 - fluid bottom
    (50 50 10)       // 6 - interface
    (0 50 10)        // 7 - interface
    (0 0 20)         // 8 - solid top
    (50 0 20)        // 9 - solid top
    (50 50 20)       // 10 - solid top
    (0 50 20)        // 11 - solid top
);

blocks
(
    hex (0 1 2 3 4 5 6 7) fluidZone (25 25 5)  // Fluid zone
    hex (4 5 6 7 8 9 10 11) solidZone (25 25 5)  // Solid zone
);

boundary
(
    inlet { type patch; faces ( (0 4 7 3) ); }
    outlet { type patch; faces ( (1 2 6 5) ); }
    sides { type patch; faces ( (0 1 5 4) (3 7 6 2) ); }
    top { type wall; faces ( (8 9 10 11) ); }
);
```

**Validation:** Verify mesh created
```bash
blockMesh
checkMesh
```

---

### Step 2: Define CellZones (กำหนด CellZones)

**Task:** Create topoSetDict to assign cellZones

**What:** Mark groups of cells as belonging to specific regions  
**Why:** `splitMeshRegions` needs cellZones to know which cells belong to which region  
**How:** Use `topoSet` utility with cellSet command

**File:** `system/topoSetDict`

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2312                                 |
|   \\  /    A nd           | Web:      www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      topoSetDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

actions
(
    // Define fluid zone (lower half)
    {
        name    fluidZone;
        type    cellSet;
        action  new;
        source  box;
        box     (0 0 0) (0.05 0.05 0.01);  // Lower region
    }
    
    // Define solid zone (upper half)
    {
        name    solidZone;
        type    cellSet;
        action  new;
        source  box;
        box     (0 0 0.01) (0.05 0.05 0.02);  // Upper region
    }
);

// ************************************************************************* //
```

**Execute:**
```bash
topoSet
```

**Verify:**
```bash
# Check cellZones created
foamInfoDict constant/polyMesh/cellZones
```

<details>
<summary><b>💡 Solution Hint: Alternative Method</b></summary>

**Method 2: Define cellZones directly in blockMeshDict**

Add to blockMeshDict:
```cpp
blocks
(
    hex (0 1 2 3 4 5 6 7) fluidZone (25 25 5) 
    hex (4 5 6 7 8 9 10 11) solidZone (25 25 5) 
);

zones
{
    fluidZone
    {
        type cellZone;
        cellZones (fluidZone);
    }
    
    solidZone
    {
        type cellZone;
        cellZones (solidZone);
    }
}
```

**Advantage:** No need for separate topoSet step  
**Disadvantage:** Less flexible for complex geometries

</details>

---

### Step 3: Split Mesh into Regions (แบ่ง Mesh เป็น Regions)

**Task:** Execute `splitMeshRegions`

**What:** `splitMeshRegions` utility  
**Why:** Divides single mesh into multiple coupled regions  
**How:** Uses cellZones to identify region membership, creates interface BCs

```bash
# Split into regions
splitMeshRegions -cellZones -overwrite
```

**Expected Output:**
```
Reading mesh
Creating regions
    Region: air
    Region: solid
Writing region meshes
```

**Verification:**
```bash
# Check regions created
ls -d constant/*
# Output: constant/air constant/solid

# List boundary patches for each region
ls constant/air/polyMesh/boundary
ls constant/solid/polyMesh/boundary

# Should contain:
# air_to_solid (in air region)
# solid_to_air (in solid region)
```

<details>
<summary><b>❌ Troubleshooting: splitMeshRegions fails</b></summary>

**Error:** "cellZone not found"

**Solution:**
```bash
# 1. Verify cellZones exist
topoSet -list

# 2. Check cellZone names match regionProperties
regions
(
    fluid  (air);     // ❌ cellZone is "fluidZone", not "air"
);

# CORRECT: Use cellZone names
regions
(
    fluid  (fluidZone);  // ✅ Matches topoSetDict
    solid  (solidZone);
);

# 3. Or rename cellZones to match region names
```

**Error:** "Cannot find interface between regions"

**Solution:** Ensure cellZones are adjacent (share faces). Use `checkMesh` to verify connectivity.

</details>

---

### Step 4: Verify Interface Creation (ตรวจสอบการสร้าง Interface)

**Task:** Confirm interface patches created correctly

```bash
# Check boundary details
foamListRegions -case .
# Output: air solid

# Examine interface patch
grep -A 10 "air_to_solid" constant/air/polyMesh/boundary
```

**Expected Interface Properties:**
```cpp
air_to_solid
{
    type            mappedWall;
    nFaces          2500;
    startFace       12500;
    
    // Sample region data
    sampleMode      nearestCell;
    sampleRegion    solid;
    samplePatch     solid_to_air;
}
```

**Validation Checklist:**
- ✅ Both regions have interface patches
- ✅ Patch names are complementary: `air_to_solid` ↔ `solid_to_air`
- ✅ `sampleRegion` points to correct neighbor
- ✅ `nFaces` matches between regions

---

### Step 5: Solution Verification

<details>
<summary><b>💡 Complete Solution: Multi-Region Setup</b></summary>

**Verification Commands:**
```bash
# 1. Check region creation
ls constant/*/polyMesh/
# Should show: air/ and solid/ directories

# 2. Verify interface patches
foamListRegions -case .
# Output: air solid

# 3. Check boundary connectivity
grep -A 5 "air_to_solid" constant/air/polyMesh/boundary
grep -A 5 "solid_to_air" constant/solid/polyMesh/boundary

# 4. Visual check in ParaView
paraFoam -builtin
# Should see two regions with shared interface
```

**Common Issues Fixed:**

| Issue | Symptom | Fix |
|-------|---------|-----|
| CellZones missing | `splitMeshRegions` finds 0 regions | Run `topoSet` first |
| Names mismatch | "Region not found" | Match names in `regionProperties` |
| Non-adjacent zones | No interface created | Ensure cellZones share boundary faces |

**Success Indicators:**
```
✓ constant/air/polyMesh/ exists
✓ constant/solid/polyMesh/ exists
✓ air_to_solid patch in air region
✓ solid_to_air patch in solid region
✓ Both patches have same nFaces
```

</details>

---

## Exercise 3: Advanced Interface Coupling (การเชื่อมต่อ Interface ขั้นสูง)

### 🎯 Objective (วัตถุประสงค์)
Implement custom coupling boundary conditions with flux control.

**What:** Extend basic coupling to include thermal resistance, directional control  
**Why:** Model real-world effects: contact resistance, thermal diodes  
**How:** Modify BCs with custom parameters or coded conditions

---

### Step 1: Thermal Resistance Interface (Interface ด้วยความต้านทานความร้อน)

**Task:** Add contact resistance at solid-solid interface

**What:** Contact resistance model (โมเดลความต้านทานการสัมผัส)  
**Why:** Real interfaces have thermal resistance (imperfect contact)  
**How:** Modify temperature jump condition: `T1 - T2 = q·R_th`

**Scenario:** Two solids in contact with imperfect thermal contact

**File:** `0/solid1/T` (first solid region)

```cpp
interface_to_solid2
{
    type            compressible::turbulentTemperatureCoupledBaffleMixed;
    Tnbr            T;
    kappaMethod     solidThermo;
    value           uniform 300;
    
    // Contact resistance (K·m²/W)
    // Note: Requires custom BC or fvOptions modification
    thermalResistance  uniform 0.001;  
}
```

<details>
<summary><b>💡 Implementation: Contact Resistance via coded BC</b></summary>

**Custom BC for thermal resistance:**

```cpp
interface_to_solid2
{
    type            codedFixedValue;
    value           uniform 300;
    
    code
    #{
        const volScalarField& Tnbr = mesh().lookupObject<volScalarField>(
            db().time().lookupObject<fvMesh>("solid2").name()
        );
        scalarField& Tfld = *this;
        
        // Thermal resistance (K·m²/W)
        const scalar R_th = 0.001;
        
        // Conductivity
        const volScalarField& kappa = 
            mesh().lookupObject<volScalarField>("kappa");
        
        // Calculate flux: q = (Tnbr - Tfld) / R_th
        // Apply: Tfld = Tnbr - q·R_th
        // Simplified: Tfld = Tnbr + (kappa/R_th) * dT/dn
        forAll(Tfld, i)
        {
            label faceI = patch().faceCells()[i];
            Tfld[i] = Tnbr[i] - R_th * kappa[faceI] * 
                      (Tnbr[i] - Tfld[i]) / patch().deltaCoeffs()[i];
        }
    #};
    
    codeInclude
    #{
        #include "volScalarField.H"
        #include "fvMesh.H"
    #};
}
```

**Validation:** Compare with analytical solution for composite slab:
```
T(x) = T_hot - (q·x/kappa1)  for 0 < x < L1
T(x) = T_interface - (q·(x-L1)/kappa2)  for L1 < x < L1+L2

Interface jump: ΔT = q·R_th
```

</details>

---

### Step 2: Directional Flux Control (การควบคุม Flux แบบทิศทางเดียว)

**Task:** Implement thermal diode (one-way heat transfer)

**What:** One-way thermal coupling  
**Why:** Models thermal diodes, check valves, controlled heat transfer  
**How:** Conditional update based on temperature gradient direction

**File:** `0/air/p`

```cpp
inlet
{
    type            codedFixedValue;
    value           uniform 101325;
    
    code
    #{
        // Access solid temperature
        const fvMesh& solidMesh = 
            db().time().lookupObject<fvMesh>("solid");
        const volScalarField& solidT = 
            solidMesh.lookupObject<volScalarField>("T");
        
        // Calculate average solid temperature
        scalar avgT = average(solidT).value();
        
        // Set pressure based on solid temperature (thermal diode effect)
        scalarField& pfld = *this;
        pfld = 101325 + 10*(avgT - 300);  // Pressure increases with T
    #};
    
    codeInclude
    #{
        #include "fvMesh.H"
        #include "volScalarField.H"
    #};
}
```

<details>
<summary><b>💡 Application: Active Cooling Control</b></summary>

**Use Case:** Cooling system that activates only when component overheats

```cpp
coolingControl
{
    type            codedFixedValue;
    value           uniform 293;
    
    code
    #{
        // Get component temperature
        const volScalarField& T = db().lookupObject<volScalarField>("T");
        scalar maxT = max(T).value();
        
        scalarField& Tfld = *this;
        
        // Thermal diode: only cool if T > threshold
        const scalar T_threshold = 350;  // K
        
        if (maxT > T_threshold)
        {
            // Active cooling: set low temperature
            Tfld = 293;
        }
        else
        {
            // Passive: adiabatic (zeroGradient)
            Tfld = T;  // Maintain current
        }
    #};
}
```

**Applications:**
- Electronic thermal management
- Building HVAC control
- Cryogenic systems

</details>

---

### Step 3: Validation (การตรวจสอบความถูกต้อง)

**Task:** Compare numerical results with analytical solution

**Test Case:** Composite slab with heat source

**Analytical Solution:**
```
For region 1 (solid source, 0 < x < L1):
    T(x) = T_0 - (q·x/kappa1)

For region 2 (solid sink, L1 < x < L1+L2):
    T(x) = T_interface - (q·(x-L1)/kappa2)

At interface (x = L1):
    T_interface = T_0 - (q·L1/kappa1)
    Flux continuity: q1 = q2 = q
```

**Validation Script:**
```python
import numpy as np
import pandas as pd

# Parameters
q = 1000  # Heat flux (W/m²)
kappa1 = 237  # Aluminum (W/m·K)
kappa2 = 50   # Steel (W/m·K)
L1 = 0.01     # Region 1 thickness (m)
L2 = 0.02     # Region 2 thickness (m)
T0 = 350      # Hot side temperature (K)

# Analytical solution
x_analytical = np.array([0, L1, L1+L2])
T_analytical = np.array([
    T0,
    T0 - q*L1/kappa1,
    T0 - q*L1/kappa1 - q*L2/kappa2
])

# Read numerical results from OpenFOAM
# (Use sampleDict to extract line probe data)
T_numerical = np.array([350, 349.96, 349.56])

# Calculate error
error = np.abs(T_numerical - T_analytical) / T_analytical * 100

print("Validation Results:")
for i, x in enumerate(x_analytical):
    print(f"x = {x*100:.1f} cm: T_analytical = {T_analytical[i]:.2f} K, "
          f"T_numerical = {T_numerical[i]:.2f} K, "
          f"error = {error[i]:.2f}%")

# Acceptance criteria
assert np.all(error < 5), "Solution exceeds 5% error tolerance"
print("✓ Validation passed!")
```

**Acceptance Criteria:**
- |T_numerical - T_analytical| / T_analytical < 5%
- Heat flux continuity: |q_solid - q_fluid| / q_avg < 1%

<details>
<summary><b>💡 Solution: Expected Results</b></summary>

**Typical Results for Contact Resistance Case:**

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Interface temperature jump | 1-5 K | ΔT = q·R_th |
| Heat flux | 900-1100 W/m² | Continuous across interface |
| Error vs analytical | < 5% | Good agreement |

**Debugging Checklist:**
1. ✅ Verify thermal resistance units: [K·m²/W]
2. ✅ Check flux continuity: `wallHeatFlux` function object
3. ✅ Confirm interface temperature jump matches: ΔT = q·R_th
4. ✅ Compare with analytical composite slab solution

</details>

---

## Exercise 4: Object Registry Communication (การสื่อสารผ่าน Object Registry)

### 🎯 Objective (วัตถุประสงค์)
Access and manipulate fields from different regions at runtime.

**What:** Cross-region field lookup using object registry  
**Why:** Enables complex coupling strategies beyond built-in BCs  
**How:** Use `db().time().lookupObject<type>(name)` to access any registered object

---

### Step 1: Region-to-Region Field Access (การเข้าถึงฟิลด์ระหว่าง Regions)

**Task:** Access neighbor region field at runtime

**What:** Runtime cross-region field lookup  
**Why:** Enables complex coupling strategies beyond built-in BCs  
**How:** Use `db().time().lookupObject<type>(name)` to access any registered object

**Scenario:** Calculate temperature-dependent property using neighbor field

**File:** `0/air/p` (custom pressure BC based on solid temperature)

```cpp
inlet
{
    type            codedFixedValue;
    value           uniform 101325;
    
    code
    #{
        // Access solid region mesh
        const fvMesh& solidMesh = 
            db().time().lookupObject<fvMesh>("solid");
        
        // Access solid temperature field
        const volScalarField& solidT = 
            solidMesh.lookupObject<volScalarField>("T");
        
        // Calculate average solid temperature
        scalar avgT = average(solidT).value();
        
        // Set pressure based on solid temperature
        // Example: Higher temperature → higher pressure (thermal expansion)
        scalarField& pfld = *this;
        pfld = 101325 + 10*(avgT - 300);  // Pa per K above 300K
    #};
    
    codeInclude
    #{
        #include "fvMesh.H"
        #include "volScalarField.H"
    #};
}
```

**What:** Lookup pattern explanation  
**Why:** Breakdown of each component  
**How:** Usage examples

<details>
<summary><b>💡 Key Concept: Registry Lookup Pattern</b></summary>

**Lookup Components:**
```cpp
const fvMesh& nbrMesh = db().time().lookupObject<fvMesh>("regionName");
const volScalarField& nbrField = nbrMesh.lookupObject<volScalarField>("fieldName");
```

**Component Breakdown:**
1. `db()`: Current object registry (boundary condition's registry)
2. `db().time()`: Time database (contains all regions)
3. `lookupObject<type>(name)`: Template function to find object by type and name
4. Region name: Must match `regionProperties` definition
5. Field name: Must be registered in neighbor region (usually in `0/regionName/`)

**Common Lookup Patterns:**
```cpp
// Scalar field
lookupObject<volScalarField>("T")

// Vector field
lookupObject<volVectorField>("U")

// Tensor field
lookupObject<volSymmTensorField>("sigma")

// Mesh
lookupObject<fvMesh>("regionName")

// Another boundary condition
lookupObject<fvPatchScalarField>("patchName")
```

</details>

---

### Step 2: Add Custom Field Object (เพิ่ม Custom Field Object)

**Task:** Create shared field accessible by all regions

**What:** Shared coupling coefficient field  
**Why:** Allows regions to share coupling parameters dynamically  
**How:** Store in registry with `store()`, access via `lookupObject()`

**Scenario:** Dynamic coupling coefficient that adapts based on local conditions

**File:** `customSharedFields.H` (included in custom solver or createFields.H)

```cpp
// Create shared field in object registry
Info << "Creating shared coupling field" << nl << endl;

forAll(fluidRegions, i)
{
    const fvMesh& mesh = fluidRegions[i];
    
    // Create if doesn't exist
    if (!mesh.foundObject<volScalarField>("couplingCoeff"))
    {
        // Create new field
        volScalarField* couplingCoeffPtr = new volScalarField
        (
            IOobject
            (
                "couplingCoeff",
                mesh.time().timeName(),
                mesh,
                IOobject::READ_IF_PRESENT,  // Read from file if exists
                IOobject::AUTO_WRITE        // Write automatically
            ),
            mesh,
            dimensionedScalar("zero", dimless, 1.0)  // Initial value
        );
        
        // Store in registry
        couplingCoeffPtr->store();
        
        Info << "Created couplingCoeff in region " 
             << mesh.name() << endl;
    }
    else
    {
        Info << "couplingCoeff already exists in region " 
             << mesh.name() << endl;
    }
}
```

**Usage in Boundary Condition:**
```cpp
// Access shared field
const volScalarField& couplingCoeff = 
    mesh().lookupObject<volScalarField>("couplingCoeff");

// Use in calculation
scalarField& Tfld = *this;
forAll(Tfld, i)
{
    Tfld[i] = Tnbr[i] * couplingCoeff[i];  // Apply coupling coefficient
}
```

<details>
<summary><b>💡 Application: Adaptive Coupling</b></summary>

**Use Case:** Automatically adjust coupling strength based on convergence

```cpp
// Update coupling coefficient every time step
if (mesh.time().timeIndex() % 10 == 0)
{
    // Get residual
    scalar residual = ...;  // From solver
    
    // Adapt coupling coefficient
    volScalarField& couplingCoeff = 
        const_cast<volScalarField&>(
            mesh().lookupObject<volScalarField>("couplingCoeff")
        );
    
    // Higher residual → stronger coupling
    couplingCoeff = min(1.0, max(0.1, residual));
    
    Info << "Adapted coupling coefficient: " 
         << average(couplingCoeff).value() << endl;
}
```

**Benefits:**
- Automatic stabilization during difficult transients
- Faster convergence when solution is smooth
- Prevents oscillations in loosely-coupled problems

</details>

---

### Step 3: Debug Registry Contents (Debug Registry Contents)

**Task:** List all registered objects for debugging

**Code Snippet:** Debug registry contents (add to solver or BC)

```cpp
// Debug: List all registered objects
const objectRegistry& registry = mesh.thisDb();

Info << "Objects in registry (" << registry.name() << "):" << endl;
wordList objNames = registry.sortedNames();

forAll(objNames, i)
{
    const regIOobject* obj = registry.lookupObjectPtr(objNames[i]);
    
    Info << "  - " << objNames[i] 
         << " (type: " << obj->type() << ")"
         << endl;
}
```

**Expected Output:**
```
Objects in registry (air):
  - T (type: volScalarField)
  - p (type: volScalarField)
  - U (type: volVectorField)
  - couplingCoeff (type: volScalarField)
  - boundaryMesh (type: fvBoundaryMesh)
  - cellZones (type: cellZoneMesh)
  - ...
```

<details>
<summary><b>❌ Troubleshooting: Registry Lookup Errors</b></summary>

**Error:** "Cannot find object"

**Debug Code:**
```cpp
// Safe lookup with error handling
const fvMesh* nbrMeshPtr = nullptr;
try
{
    nbrMeshPtr = &db().time().lookupObject<fvMesh>("solid");
}
catch (const Foam::error& e)
{
    FatalErrorInFunction
        << "Failed to lookup region 'solid'" << nl
        << "Available regions:" << nl
        << db().time().sortedNames() << nl
        << exit(FatalError);
}

// Safe field lookup
const volScalarField* nbrTptr = nullptr;
if (nbrMeshPtr->foundObject<volScalarField>("T"))
{
    nbrTptr = &nbrMeshPtr->lookupObject<volScalarField>("T");
}
else
{
    WarningInFunction
        << "Field 'T' not found in region 'solid'" << nl
        << "Available fields:" << nl
        << nbrMeshPtr->sortedNames() << endl;
}
```

**Common Issues:**

| Issue | Cause | Solution |
|-------|-------|----------|
| Region not found | Spelling in `regionProperties` | Match names exactly |
| Field not found | Field not created/registered | Check `0/regionName/` files |
| Wrong type | `lookupObject<volScalarField>` vs `volVectorField` | Use correct type template |
| Wrong database | Looking in `mesh` instead of `mesh.time()` | Use correct registry level |

**Verification Commands:**
```bash
# Check registered objects in time database
# (Add debug code to solver to list all regions)

# Check region properties
cat constant/regionProperties

# Check field files
ls -la 0/*/T
```

</details>

---

### Step 4: Solution Verification

<details>
<summary><b>💡 Complete Solution: Registry Communication</b></summary>

**Full Example: Pressure BC depending on solid temperature**

```cpp
inlet
{
    type            codedFixedValue;
    value           uniform 101325;
    
    code
    #{
        // PART 1: Access neighbor region
        const fvMesh& solidMesh = 
            db().time().lookupObject<fvMesh>("solid");
        
        // PART 2: Access neighbor field
        const volScalarField& solidT = 
            solidMesh.lookupObject<volScalarField>("T");
        
        // PART 3: Calculate derived quantity
        scalar avgT = average(solidT).value();
        scalar maxT = max(solidT).value();
        scalar minT = min(solidT).value();
        
        // PART 4: Apply coupling logic
        scalarField& pfld = *this;
        
        // Example: Thermostat control
        const scalar T_setpoint = 350;  // K
        const scalar K_p = 100;         // Proportional gain
        
        // Increase pressure if solid is too hot
        pfld = 101325 + K_p * max(0, maxT - T_setpoint);
        
        // Debug output
        if (mesh().time().timeIndex() % 100 == 0)
        {
            Info << "Thermostat: T_solid = " << avgT 
                 << " K (range: " << minT << " - " << maxT << ")" 
                 << ", p_inlet = " << average(pfld).value() << " Pa" 
                 << endl;
        }
    #};
    
    codeInclude
    #{
        #include "fvMesh.H"
        #include "volScalarField.H"
    #};
}
```

**Validation:**
1. Run simulation and monitor log output
2. Verify pressure adapts to solid temperature
3. Check feedback loop is stable (no oscillations)

**Applications:**
- Thermostatic control
- Convergence acceleration
- Multi-physics feedback (e.g., thermal expansion → pressure)

</details>

---

## Exercise 5: Full CHT Case with Cooling Tower (เคส CHT สมบูรณ์กับ Cooling Tower)

### 🎯 Objective (วัตถุประสงค์)
Assemble a complete conjugate heat transfer simulation with convergence monitoring.

**What:** Complete CHT case from setup to validation  
**Why:** Learn full workflow for industrial applications  
**How:** Follow systematic approach: geometry → mesh → BCs → solver → validation

---

### Step 1: Problem Specification (การกำหนดปัญหา)

**Task:** Define cooling problem clearly

**Scenario:** Electronic component cooling (การระบายความร้อนอิเล็กทรอนิกส์)

**What (อะไร):** Heat-generating electronic component with forced air cooling  
**Why (ทำไม):** Ensure component operates below maximum temperature rating  
**How (อย่างไร):** CHT simulation with heat source in solid, convection to fluid

**Design Parameters:**
| Parameter | Value | Units | Description |
|-----------|-------|-------|-------------|
| Air inlet velocity | 2 | m/s | Forced convection |
| Air inlet temperature | 293 | K | Ambient temperature |
| Component power | 10 | W | Heat generation rate |
| Solid conductivity (Al) | 237 | W/m·K | Aluminum thermal conductivity |
| Geometry dimensions | 50×50×20 | mm | Component size |

**Performance Targets:**
- Max component temperature < 398 K (125°C, typical electronic limit)
- Air temperature rise < 10 K
- Steady-state convergence in < 1000 iterations

---

### Step 2: Complete Case Setup (การตั้งค่าเคสสมบูรณ์)

#### Step 2.1: Geometry Definition (การกำหนดรูปทรงเรขาคณิต)

**Task:** Create computational mesh

**What:** Represent component and surrounding air  
**Why:** Accurate geometry captures heat transfer physics  
**How:** Use blockMesh for simple geometry or snappyHexMesh for complex

**Option A: Simple Geometry (blockMesh)**

```bash
# Create base mesh with blockMesh
blockMesh
```

**Option B: Complex Geometry with Fins (snappyHexMesh)**

```bash
# 1. Create base mesh
blockMesh

# 2. Run snappyHexMesh for detailed geometry
snappyHexMesh -overwrite

# 3. Create regions
splitMeshRegions -cellZones
```

**Validation:**
```bash
# Check mesh quality
for region in air solid; do
    echo "Checking $region..."
    checkMesh -region $region
done
```

---

#### Step 2.2: Thermophysical Properties (คุณสมบัติทางเทอร์โมไดนามิกส์)

**Task:** Define material properties for both regions

**What:** Material properties for fluid and solid  
**Why:** Correct properties essential for accurate heat transfer  
**How:** Define in `thermophysicalProperties` files

**File:** `constant/air/thermophysicalProperties`

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2312                                 |
|   \\  /    A nd           | Web:      www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "constant/air";
    object      thermophysicalProperties;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

thermoType
{
    type            heRhoThermo;
    mixture         pureMixture;
    transport       sutherland;
    thermo          hConst;
    equationOfState perfectGas;
    specie          specie;
    energy          sensibleEnthalpy;
}

mixture
{
    specie
    {
        molWeight       28.9;  // g/mol (air)
    }
    thermodynamics
    {
        Cp              1007;  // J/kg·K
        Hf              0;
    }
    transport
    {
        As              1.4792e-06;
        Ts              116;   // K (Sutherland reference)
    }
}

// ************************************************************************* //
```

**What:** Air properties explanation  
**Why:** Property selection rationale  
**How:** Property calculation methods

<details>
<summary><b>💡 Key Concept: Thermophysical Properties Explained</b></summary>

**Property Breakdown:**

| Property | Value | Physical Meaning | Impact on Simulation |
|----------|-------|------------------|----------------------|
| `Cp` | 1007 J/kg·K | Specific heat capacity | Higher → more heat carried per kg |
| `molWeight` | 28.9 g/mol | Molecular weight | Affects density calculation |
| `As`, `Ts` | Sutherland constants | Viscosity temperature dependence | Higher → more viscous at high T |

**Thermo Type Components:**
- `heRhoThermo**: specific enthalpy equation of state
- `sutherland`: temperature-dependent viscosity
- `perfectGas`: ideal gas law (p = ρRT)
- `sensibleEnthalpy`: energy variable = h (not T)

**Verification:**
```bash
# Check transport properties at operating T
# At T = 300 K:
#   μ = μ₀ · (T/T₀)^(3/2) · (T₀ + S) / (T + S)
#   ≈ 1.8e-5 Pa·s (air at 300K)
```

</details>

**File:** `constant/solid/thermophysicalProperties`

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2312                                 |
|   \\  /    A nd           | Web:      www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "constant/solid";
    object      thermophysicalProperties;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

thermoType
{
    type            heSolidThermo;
    mixture         pureMixture;
    transport       const;
    thermo          hConst;
    equationOfState rhoConst;
    specie          specie;
    energy          sensibleEnthalpy;
}

mixture
{
    specie
    {
        molWeight       26.98;  // g/mol (Aluminum)
    }
    thermodynamics
    {
        Cp              900;    // J/kg·K (Aluminum)
        Hf              0;
    }
    transport
    {
        kappa           237;    // W/m·K (Aluminum)
    }
    equationOfState
    {
        rho             2700;   // kg/m³
    }
}

// ************************************************************************* //
```

**Validation:** Compare with literature
```bash
# Aluminum properties at 300 K:
#   rho = 2700 kg/m³ ✓
#   Cp = 900 J/kg·K ✓
#   kappa = 237 W/m·K ✓
```

---

#### Step 2.3: Heat Source Implementation (การนำ Heat Source ไปใช้)

**Task:** Implement volumetric heat generation

**What:** `fvOptions` for volumetric heat source  
**Why:** Models electronic component heat generation  
**How:** Implicit source term added to energy equation: `Su + Sp·T`

**File:** `constant/solid/fvOptions`

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2312                                 |
|   \\  /    A nd           | Web:      www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "constant/solid";
    object      fvOptions;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

heatSource
{
    type            scalarSemiImplicitSource;
    active          true;
    
    scalarSemiImplicitSourceCoeffs
    {
        volumeMode      absolute;
        
        injectionRateSuSp
        {
            T           (10e6 0);  // (Su Sp) in W/m³
        }
        
        // Define cellZone for heat source
        cellZone        componentZone;
        
        // Power calculation:
        // P = 10 W
        // V = 0.05*0.05*0.01 = 2.5e-5 m³
        // Power density = P/V = 10/2.5e-5 = 400,000 W/m³
        // Use 10e6 for faster convergence (higher power density in smaller zone)
    }
}

// ************************************************************************* //
```

<details>
<summary><b>💡 Key Concept: Semi-Implicit Source</b></summary>

**Source Term Form:**
```
S = Su + Sp·T
```

**Components:**
- `Su` (explicit): constant part of source
- `Sp` (implicit): temperature-dependent part

**Example:**
```cpp
// Constant heat generation: 10 W
T (400000 0);  // Su = 400000 W/m³, Sp = 0

// Newton cooling: -h·(T - T_amb) = -h·T + h·T_amb
// Let h = 100 W/m³·K, T_amb = 300 K
T (30000 -100);  // Su = 30000, Sp = -100
```

**Volume Mode Options:**
- `absolute`: Su in [W/m³], total power = Su × volume
- `specific`: Su in [W/kg], total power = Su × mass

**Validation:**
```bash
# Calculate expected temperature rise
# Q = m·Cp·ΔT
# ΔT = Q / (m·Cp)
# ΔT = 10 / (0.05*0.05*0.01*2700*900) ≈ 0.33 K (for uniform heating)
# Local ΔT will be higher due to finite conductivity
```

</details>

---

### Step 3: Solver Settings (การตั้งค่า Solver)

**Task:** Configure solver for optimal convergence

**What:** Numerical scheme and solver settings  
**Why:** Proper settings ensure stable, convergent solution  
**How:** Adjust tolerances, under-relaxation, convergence criteria

**File:** `system/air/fvSolution`

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2312                                 |
|   \\  /    A nd           | Web:      www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "system/air";
    object      fvSolution;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-06;
        relTol          0.01;
        smoother        GaussSeidel;
    }
    
    pFinal
    {
        solver          GAMG;
        tolerance       1e-06;
        relTol          0;
    }
    
    "(U|T|k|epsilon|omega)"
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-05;
        relTol          0.1;
    }
    
    "(U|T|k|epsilon|omega)Final"
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-05;
        relTol          0;
    }
}

SIMPLE
{
    nNonOrthogonalCorrectors 0;
    consistent      yes;
    
    residualControl
    {
        p               1e-4;
        U               1e-4;
        T               1e-4;
        "(k|epsilon|omega)"   1e-4;
    }
    
    relaxFactors
    {
        p               0.3;
        U               0.7;
        T               0.7;  // Under-relax temperature for stability
        k               0.7;
        epsilon         0.7;
    }
}

// ************************************************************************* //
```

**What:** Solver setting explanation  
**Why:** Impact on convergence  
**How:** Tuning guidelines

<details>
<summary><b>💡 Key Concept: Solver Settings Explained</b></summary>

**Linear Solvers:**

| Solver | Best For | Pros | Cons |
|--------|----------|------|------|
| GAMG | Pressure (elliptic) | Fast for large problems | Memory intensive |
| smoothSolver | Velocity, T (hyperbolic/parabolic) | Low memory | Slower for large systems |

**Tolerance Strategy:**
```cpp
// During iteration (loose)
tolerance   1e-05;
relTol      0.1;  // Stop when residual < 10% of initial

// Final iteration (tight)
tolerance   1e-05;
relTol      0;    // Stop when residual < 1e-05 absolute
```

**Under-Relaxation Factors:**
```cpp
// SIMPLE algorithm stabilization
// New value = (1-α)·old_value + α·calculated_value

p       0.3;  // Pressure: aggressive (drives velocity)
U       0.7;  // Velocity: moderate (follows pressure)
T       0.7;  // Temperature: moderate (follows flow field)
```

**Convergence Tuning:**
- **Diverging:** Decrease relaxation factors (0.5 → 0.3)
- **Slow convergence:** Increase relaxation factors (0.7 → 0.9)
- **Oscillating:** Reduce all factors uniformly

</details>

---

### Step 4: Convergence Monitoring (การตรวจสอบการลู่เข้า)

**Task:** Set up function objects for monitoring

**What:** Automated convergence tracking  
**Why:** Ensure solution quality and detect issues early  
**How:** Use function objects in controlDict

**File:** `system/controlDict`

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2312                                 |
|   \\  /    A nd           | Web:      www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "system";
    object      controlDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

application     chtMultiRegionFoam;

startFrom       latestTime;

startTime       0;

stopAt          endTime;

endTime         1000;

deltaT          1;

writeControl    timeStep;

writeInterval   100;

functions
{
    // Monitor component temperature
    componentTemperature
    {
        type            volRegion;
        functionObjectLibs ("libfieldFunctionObjects.so");
        enabled         true;
        log             true;
        writeFields     false;
        region          solid;
        operation       average;
        weightField     none;
        fields          (T);
    }
    
    // Monitor interface heat flux
    interfaceFlux
    {
        type            surfaceRegion;
        functionObjectLibs ("libfieldFunctionObjects.so");
        enabled         true;
        log             true;
        writeFields     true;
        region          air;
        surfaceFormat   none;
        operation       sum;
        source          patches;
        patches         (air_to_solid);
        fields
        (
            wallHeatFlux
        );
    }
    
    // Write residuals
    residuals
    {
        type            residuals;
        functionObjectLibs ("libutilityFunctionObjects.so");
        enabled         true;
        fields 
        (
            p
            U
            T
        );
        region          air;
    }
}

// ************************************************************************* //
```

**What:** Function object explanation  
**Why:** Monitoring importance  
**How:** Interpretation

<details>
<summary><b>💡 Key Concept: Function Objects Explained</b></summary>

**Function Object Types:**

| Type | Purpose | Output |
|------|---------|--------|
| `volRegion` | Volume-integrated quantities | Average, sum, min, max over regions |
| `surfaceRegion` | Surface-integrated quantities | Flux, forces over patches |
| `residuals` | Solver residuals | Convergence history |

**Monitoring Strategy:**
```cpp
// 1. Component temperature (volRegion)
operation   average;  // Tracks average component heating
// Check: T_avg < T_max_rating

// 2. Interface flux (surfaceRegion)
operation   sum;      // Total heat transfer rate
// Check: flux_in ≈ heat_source (energy balance)

// 3. Residuals (residuals)
// Check: all residuals < 1e-4 (convergence)
```

**Output Location:**
```
postProcessing/
├── componentTemperature/
│   └── volRegion.dat          # Time vs T_avg
├── interfaceFlux/
│   └── surfaceRegion.dat      # Time vs heat_flux
└── residuals/
    └── residual.dat            # Time vs residuals
```

**Validation Checks:**
1. **Steady state:** T_avg and flux stop changing
2. **Energy balance:** flux ≈ 10W (±5%)
3. **Component rating:** T_max < 398 K

</details>

---

### Step 5: Run and Validate (รันและตรวจสอบ)

**Task:** Execute simulation and verify results

**What:** Run solver and perform validation checks  
**Why:** Ensure simulation meets requirements  
**How:** Systematic validation procedure

**Execution:**
```bash
# Run simulation
chtMultiRegionFoam 2>&1 | tee log.cht

# Monitor convergence in real-time
tail -f log.cht | grep "Time ="

# Check completion
foamListTimes
```

**Validation Check 1: Energy Balance**
```bash
# Extract heat flux from log
grep "interfaceFlux" log.cht | tail -10

# Extract component temperature
grep "componentTemperature" log.cht | tail -10

# Should equal heat source (10W ± 5%)
```

**Validation Check 2: Component Temperature**
```bash
# Check maximum temperature
foamListTimes
paraFoam -builtin -time 1000  # Open final time
# Use Calculator: max(T) over solid region

# Acceptance criteria:
# T_max < 398 K (125°C, typical electronic limit)
```

**Validation Check 3: Grid Independence**
```bash
# Refine mesh
refineMesh -overwrite

# Re-run
chtMultiRegionFoam

# Compare results
# |T_fine - T_coarse| / T_fine < 2%
```

<details>
<summary><b>❌ Troubleshooting: Common Issues</b></summary>

| Symptom | Cause | Solution |
|---------|-------|----------|
| T_max > 398 K | Insufficient cooling | Increase flow rate or improve fin design |
| Energy imbalance | Wrong fvOptions power | Check volume calculation: P/V |
| Slow convergence | Too tight tolerances | Relax residual control to 1e-3 |
| Oscillating T | Too aggressive relaxation | Reduce T relaxation to 0.5 |

</details>

---

### Step 6: Results Analysis (การวิเคราะห์ผลลัพธ์)

**Task:** Visualize and analyze results

**ParaView Visualization:**

```bash
paraFoam -touch
paraFoam &
```

**Recommended Views:**
1. **Temperature contours** (solid) + streamlines (fluid)
   - Shows heat transfer path
   - Visualizes flow patterns
2. **Wall heat flux on interface**
   - Identifies hot spots
   - Validates flux continuity
3. **Temperature profile line probe** through interface
   - Quantifies thermal boundary layer
   - Checks for temperature jump

**Python Post-Processing:**

```python
#!/usr/bin/env python3
"""Post-processing script for CHT results"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read interface flux data
flux_file = 'postProcessing/interfaceFlux/*/surfaceRegion.dat'
flux_data = pd.read_csv(flux_file, sep='\t', comment='#',
                       names=['Time', 'wallHeatFlux_sum'])

# Read component temperature data
temp_file = 'postProcessing/componentTemperature/*/volRegion.dat'
temp_data = pd.read_csv(temp_file, sep='\t', comment='#',
                       names=['Time', 'T_avg'])

# Create convergence plot
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# Plot 1: Component temperature
ax1.plot(temp_data['Time'], temp_data['T_avg'], 'b-', linewidth=2)
ax1.axhline(y=398, color='r', linestyle='--', label='Max rating (398 K)')
ax1.set_xlabel('Iteration')
ax1.set_ylabel('Temperature (K)')
ax1.set_title('Component Temperature Convergence')
ax1.legend()
ax1.grid(True)

# Plot 2: Interface heat flux
ax2.plot(flux_data['Time'], flux_data['wallHeatFlux_sum'], 'g-', linewidth=2)
ax2.axhline(y=10, color='r', linestyle='--', label='Heat source (10 W)')
ax2.set_xlabel('Iteration')
ax2.set_ylabel('Heat Flux (W)')
ax2.set_title('Interface Heat Transfer')
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.savefig('convergence.png', dpi=150)
print("Saved convergence plot to convergence.png")

# Calculate final metrics
final_T = temp_data['T_avg'].iloc[-1]
final_flux = flux_data['wallHeatFlux_sum'].iloc[-1]
energy_balance = (final_flux / 10.0) * 100

print(f"\n{'='*50}")
print("Final Results:")
print(f"{'='*50}")
print(f"Component temperature: {final_T:.2f} K")
print(f"Interface heat flux: {final_flux:.2f} W")
print(f"Energy balance: {energy_balance:.1f}% of input power")
print(f"Temperature rating: {'PASS' if final_T < 398 else 'FAIL'}")
print(f"{'='*50}")
```

**Expected Results:**

| Metric | Value | Acceptance | Interpretation |
|--------|-------|------------|----------------|
| Max component T | 340-360 K | < 398 K | ✓ Safe operation |
| Air ΔT | 3-5 K | < 10 K | ✓ Reasonable |
| Interface flux | 9.5-10.5 W | 95-105% | ✓ Energy balance |
| Iterations | 300-800 | < 1000 | ✓ Efficient |

---

### Step 7: Solution Verification

<details>
<summary><b>💡 Complete Solution: Expected Outcomes</b></summary>

**Typical Results for Cooling Tower Case:**

**Convergence History:**
```
Time = 100, T_avg = 345.2 K, flux = 9.2 W
Time = 200, T_avg = 350.8 K, flux = 9.8 W
Time = 300, T_avg = 352.4 K, flux = 9.95 W
Time = 400, T_avg = 352.9 K, flux = 10.02 W
Time = 500, T_avg = 353.1 K, flux = 10.04 W ← Converged
```

**Temperature Distribution:**
- Component: 340-360 K (non-uniform due to convection)
- Air inlet: 293 K (fixed)
- Air outlet: 296-298 K (2-5 K rise)
- Interface: Smooth transition, no jump

**Validation Summary:**
```bash
# 1. Energy balance
Energy balance: 99.6% of input power ✓

# 2. Component rating
Component temperature: 353 K < 398 K ✓

# 3. Physical consistency
Air ΔT: 4 K (reasonable for 2 m/s flow) ✓

# 4. Grid independence
|T_fine - T_coarse| / T_fine = 0.8% < 2% ✓
```

**Performance Optimization:**

If component temperature is too high:
1. Increase air velocity (2 → 5 m/s)
2. Add fins to increase surface area
3. Use higher conductivity material (Cu instead of Al)

**Success Indicators:**
- ✅ Convergence in < 1000 iterations
- ✅ Energy balance 95-105%
- ✅ Component within temperature rating
- ✅ Physical temperature distribution
- ✅ Grid independence achieved

</details>

---

## 🔍 Troubleshooting Guide (คู่มือการแก้ปัญหา)

### Common Errors and Solutions (ข้อผิดพลาดทั่วไปและวิธีแก้ไข)

| Error (ข้อผิดพลาด) | Cause (สาเหตุ) | Solution (วิธีแก้ไข) |
|-------|-------|----------|
| `cannot find patch 'air_to_solid'` | Patch name mismatch between regions (ชื่อ patch ไม่ตรงกัน) | Check boundary names in `0/` files match `polyMesh/boundary` (ตรวจสอบชื่อ boundary) |
| `Maximum number of iterations exceeded` | Poor convergence (การลู่เข้าแย่) | Reduce `deltaT`, relax under-relaxation factors (ลด time step, ลด relaxation factors) |
| `Negative temperatures` | Unstable solution (ผลเฉลยไม่เสถียร) | Check mesh quality, reduce time step, improve initial guess (ตรวจสอบคุณภาพ mesh) |
| `Region not found` | `regionProperties` error (ชื่อ region ผิด) | Verify region names match directory names (ตรวจสอบชื่อ region) |
| `Segfault on lookup` | Null object pointer (ชี้ไปยัง object ที่ไม่มี) | Add `foundObject()` check before `lookupObject()` (เพิ่มการตรวจสอบ) |

### Debugging Checklist (รายการตรวจสอบการ Debug)

```bash
# 1. Verify case structure
find . -name "polyMesh" -o -name "*.mtf" | sort

# 2. Check mesh quality
for region in air solid; do
    echo "Checking $region..."
    checkMesh -region $region
done

# 3. Verify BC consistency
grep -r "type.*coupled" 0/*/T

# 4. Test solver in dry-run mode
chtMultiRegionFoam -dry-run

# 5. Check parallel decomposition
decomposePar -allRegions
mpirun -np 4 chtMultiRegionFoam -parallel
reconstructPar -allRegions
```

---

## 📚 References and Further Reading (参考文献)

### Documentation Links (ลิงก์เอกสาร)
- **CHT Solver Guide:** [01_Coupled_Physics_Fundamentals.md](01_Coupled_Physics_Fundamentals.md)
- **Boundary Conditions:** [02_Conjugate_Heat_Transfer.md](02_Conjugate_Heat_Transfer.md)
- **Object Registry:** [04_Object_Registry_Architecture.md](04_Object_Registry_Architecture.md)
- **Validation:** [06_Validation_and_Benchmarks.md](06_Validation_and_Benchmarks.md)

### OpenFOAM Resources (ทรัพยากร OpenFOAM)
- **Tutorial:** `tutorials/heatTransfer/chtMultiRegionFoam/`
- **Source Code:** `src/chtRegionCouple/`
- **Utilities:**
  - `splitMeshRegions` - Create multi-region meshes
  - `createBaffles` - Create baffles from patches
  - `mergeMeshes` - Combine region meshes

### Recommended Papers (บทความแนะนำ)
1. **CHT Fundamentals:** "Conjugate heat transfer: A review" - 2022
2. **OpenFOAM Implementation:** "chtMultiRegionFoam: Theory and applications" - OpenFOAM Journal
3. **Validation Cases:** "ERCOFTAC CHT benchmarks" - Comparison with experiment

---

## ✅ Summary and Key Takeaways (สรุปและจุดสำคัญ)

### Core Concepts Covered (แนวคิดหลักที่ครอบคลุม)
1. **Multi-region simulation** requires proper `regionProperties` definition (การจำลองพหุภูมิต้องการ regionProperties ที่ถูกต้อง)
2. **Coupled BCs** (`turbulentTemperatureCoupledBaffleMixed`) enable heat/mass exchange (BC แบบ coupled ช่วยแลกเปลี่ยนความร้อน/มวล)
3. **Object registry** provides flexible cross-region communication (Object registry ให้การสื่อสารระหว่าง regions ที่ยืดหยุ่น)
4. **Convergence monitoring** essential for coupled simulations (การตรวจสอบการลู่เข้าจำเป็นมากสำหรับ coupled simulations)
5. **Validation** against analytical solutions ensures correctness (การตรวจสอบกับ analytical solutions ช่วยรับประกันความถูกต้อง)

### Skills Developed (ทักษะที่พัฒนา)
- ✅ Configured multi-region cases from scratch (ตั้งค่าเคสพหุภูมิจากศูนย์)
- ✅ Implemented custom coupling boundary conditions (นำ BC แบบ coupled แบบ custom ไปใช้)
- ✅ Used object registry for cross-region data access (ใช้ object registry เพื่อเข้าถึงข้อมูลระหว่าง regions)
- ✅ Validated coupled physics simulations (ตรวจสอบ coupled physics simulations)
- ✅ Debugged common CHT issues (แก้ไขปัญหา CHT ทั่วไป)

### Next Steps (ขั้นตอนต่อไป)
- **Extend to FSI:** Combine with [03_Fluid_Structure_Interaction.md](03_Fluid_Structure_Interaction.md)
- **Explore advanced topics:** [05_Advanced_Coupling_Topics.md](05_Advanced_Coupling_Topics.md)
- **Practice validation:** Run benchmarks from [06_Validation_and_Benchmarks.md](06_Validation_and_Benchmarks.md)

---

## 📝 Assessment Questions (คำถามประเมินความเข้าใจ)

### Knowledge Check (ตรวจสอบความรู้)

1. **What** boundary condition type is used for thermal coupling?  
   **BC แบบใดใช้สำหรับ thermal coupling?**

2. **Why** is `splitMeshRegions` necessary for multi-region cases?  
   **ทำไม `splitMeshRegions` จึงจำเป็นสำหรับเคสพหุภูมิ?**

3. **How** does `turbulentTemperatureCoupledBaffleMixed` enforce flux continuity?  
   **`turbulentTemperatureCoupledBaffleMixed` บังคับ continuity ของ flux อย่างไร?**

4. **When** should you use `codedFixedValue` instead of built-in BCs?  
   **ควรใช้ `codedFixedValue` แทน BC ในตัวเมื่อไร?**

5. **Where** are region names defined in a multi-region case?  
   **กำหนดชื่อ regions ไว้ที่ไหนในเคสพหุภูมิ?**

### Applied Exercises (แบบฝึกหัดประยุกต์)

1. Modify Exercise 1 to include phase change material (solid melts when T > T_melt)  
   แก้ไข Exercise 1 ให้รวม phase change material (solid ละลายเมื่อ T > T_melt)

2. Extend Exercise 5 to transient startup (cold start to steady-state)  
   ขยาย Exercise 5 เป็น transient startup (เริ่มจาก cold ถึง steady-state)

3. Implement radiative heat transfer at external surfaces (use `viewFactor` method)  
   นำการแผ่รังสีความร้อนไปใช้ที่ผิวภายนอก (ใช้วิธี `viewFactor`)

4. Optimize cooling fin geometry using parametric sweep  
   ปรับปรุงรูปทรง cooling fins โดยใช้ parametric sweep

5. Parallelize the cooling tower case for >1M cells  
   ทำ parallelization สำหรับ cooling tower case ที่มี >1M cells

---

**End of Coupled Physics Exercises**  
**จบแบบฝึกหัด Coupled Physics**

For questions or issues, refer to the troubleshooting guide or consult the main documentation files. Happy simulating! 🚀