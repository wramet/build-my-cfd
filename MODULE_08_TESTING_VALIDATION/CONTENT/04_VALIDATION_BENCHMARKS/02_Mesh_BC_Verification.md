# Mesh and Boundary Condition Verification

การตรวจสอบคุณภาพ Mesh และเงื่อนไขขอบเขต (Boundary Conditions)

---

## Learning Objectives

เมื่ออ่านจบบทนี้ คุณจะสามารถ:
- **แยกความแตกต่าง** ระหว่าง verification (ตรวจสอบความถูกต้องของโค้ดและ mesh) กับ validation (ตรวจสอบความถูกต้องทางฟิสิกส์)
- **ประเมินคุณภาพ mesh** โดยใช้ `checkMesh` และตีความผลลัพธ์ได้อย่างถูกต้อง
- **ตรวจสอบความสอดคล้อง** ของ boundary conditions ทั้งหมดใน case
- **วิเคราะห์และแก้ไข** ปัญหา mesh quality และ BC errors
- **ดำเนินการ mesh independence study** เพื่อยืนยันความถูกต้องของผลลัพธ์

---

## Overview

### What is Mesh and BC Verification?

**Verification** คือการยืนยันว่า mesh และ boundary conditions ถูกต้องตามข้อกำหนดทางเทคนิค ก่อนที่จะดำเนินการจำลอง (simulation) ซึ่งแตกต่างจาก **validation** ที่ตรวจสอบความถูกต้องทางฟิสิกส์ของผลลัพธ์ การ verification ที่ดีช่วยป้องกัน:
- **การใช้เวลาฟุ่มเฟือย** ในการ run simulation ที่ผิดพลาด
- **การ diverge** ของ solver เนื่องจาก mesh quality ที่ไม่ดี
- **ผลลัพธ์ที่ไม่ถูกต้อง** จาก boundary conditions ที่ไม่สอดคล้องกัน

### Why Mesh Quality Matters

คุณภาพของ mesh ส่งผลกระทบโดยตรงต่อ:
- **ความแม่นยำ** ของคำตอบ (solution accuracy)
- **เสถียรภาพ** ของการคำนวณ (numerical stability)
- **ความเร็ว** ในการลู่เข้าของผลเฉลย (convergence rate)

Mesh ที่มีคุณภาพไม่ดีอาจทำให้:
- Gradient คำนวณได้ไม่ถูกต้อง
- Solver diverge หรือไม่ลู่เข้า
- ผลลัพธ์มีความคลาดเคลื่อนสูง แม้จะใช้เวลาคำนวณนาน

### How This Module Works

เราจะเรียนรู้ขั้นตอน verification ที่เป็นระบบ ตั้งแต่:
1. **ตรวจสอบคุณภาพ mesh** ด้วยเครื่องมือ `checkMesh`
2. **ตรวจสอบ BC consistency** ทั้งหมดใน case directory
3. **แก้ไขปัญหาที่พบ** อย่างเป็นระบบ
4. **ยืนยัน mesh independence** ก่อนวิเคราะห์ผลลัพธ์จริง

---

## 1. Mesh Quality Fundamentals

### 1.1 Understanding Mesh Metrics

เครื่องมือ `checkMesh` ใน OpenFOAM ประเมินคุณภาพ mesh โดยใช้หลาย metrics:

| Metric | Definition | Acceptable Limit | Critical Limit |
|--------|------------|------------------|----------------|
| **Non-orthogonality** | ความไม่ตั้งฉากของ face vectors | < 70° | < 85° |
| **Skewness** | ความเบ้ของ cell จากจุด ideal | < 4 | < 5 |
| **Aspect ratio** | สัดส่วนความยาว/ความกว้างของ cell | < 1000 | > 1000 |
| **Concavity** | ความโค้งของ cell edges | < 80° | > 80° |

> **💡 Physics Insight:** Non-orthogonality สูงทำให้การประมาณค่า gradient มี error เพราะ assumption พื้นฐานของ finite volume method คือ face ควรตั้งฉากกับเส้นเชื่อมระหว่าง cell centers

### 1.2 Running checkMesh

```bash
# Basic mesh check
checkMesh

# Detailed output with all checks
checkMesh -allGeometry -allTopology

# Check specific mesh region
checkMesh -region regionName

# Write mesh statistics to file
checkMesh > log.checkMesh
```

**คำอธิบาย:**
- `-allGeometry`: ตรวจสอบ metrics ทางเรขาคณิตทั้งหมด
- `-allTopology`: ตรวจสอบ topology ของ mesh (connectedness, holes)
- `-region`: สำหรับ multi-region cases (conjugate heat transfer)

---

## 2. Interpreting checkMesh Output

### 2.1 Good Mesh Example

```
Checking geometry...
    Overall domain bounding box (0 0 0) (1 1 1)
    Mesh has 3 geometric zones (fluid solid porous)

Checking mesh quality...
    Max aspect ratio = 15.2 OK.
    Max non-orthogonality = 45.3 OK.
    Max skewness = 1.1 OK.
    Min volume = 1.2e-08 OK.
    Max volume = 3.5e-06 OK.
    Min face area = 4.3e-06 OK.
    
Mesh OK.
```

**ตีความ:** Mesh นี้ผ่านทุก criteria สามารถใช้งานได้ทันที

### 2.2 Mesh with Warnings

```
Checking mesh quality...
    Max aspect ratio = 1250 **WARNING** (cells: 1.23%)
    Max non-orthogonality = 68.5 OK.
    
    <<Checking consistency of faces>>
        ***High aspect ratio cells found, percentage: 1.23%
```

**ตีความและแนวทางแก้ไข:**
- **Aspect ratio warning:** พิจารณา re-mesh หรือใช้ `refineMesh` ในบริเวณที่มีปัญหา
- 1.23% ของ cells มีปัญหา → อาจใช้ได้ถ้าไม่อยู่ในบริเวณสำคัญ (high gradient zones)

### 2.3 Mesh with Errors

```
Checking mesh quality...
    Max non-orthogonality = 87.3 ***ERROR***
    
    ***Number of non-orthogonality errors: 3471
    ***Number of severely non-orthogonal faces: 8921
    
    <<Checking for holes>>
        ***Found 12 holes in mesh
```

**ตีความและแนวทางแก้ไข:**
- **Non-orthogonality > 85°:** ต้องแก้ไขก่อน run simulation
  - ใช้ `snappyHexMesh` ด้วย `nSmoothSurface` เพิ่ม
  - ลด cell skewness ด้วย `mergeTolerance` ปรับ
- **Holes:** mesh ไม่ continuous ต้อง regenerate

### 2.4 Warnings vs Errors Summary

| Status | Meaning | Action |
|--------|---------|--------|
| **OK** | Metric within safe limits | Proceed |
| **WARNING** | Metric outside typical range | Monitor, consider fixing |
| ***ERROR*** | Metric beyond solver capability | Must fix before simulation |

---

## 3. Boundary Condition Verification

### 3.1 BC Structure in OpenFOAM

Boundary conditions ใน OpenFOAM ถูกกำหนดใน directory `0/` หรือ `0.org/`:

```
0/
├── U           # Velocity field
├── p           # Pressure field
├── T           # Temperature (if heat transfer)
├── k           # Turbulence kinetic energy
├── epsilon     # Turbulence dissipation
└── omega       # Specific dissipation rate (k-omega)
```

แต่ละไฟล์มีโครงสร้าง:
```cpp
dimensions      [0 1 -1 0 0 0 0];  // SI units: m/s

internalField   uniform (0 0 0);   // Initial field values

boundaryField
{
    inlet                           // Patch name จาก constant/polyMesh/boundary
    {
        type            fixedValue;  // BC type
        value           uniform (10 0 0);  // BC value
    }
    
    outlet
    {
        type            zeroGradient;
    }
}
```

### 3.2 Visual BC Inspection

```bash
# Export to VTK format สำหรับ visualization
foamToVTK -fields '(U p k epsilon)' -time 0

# เปิดใน ParaView
paraview --data=VTK/0_*.vtk
```

**วิธีตรวจสอบใน ParaView:**
1. **เปิด boundary surfaces:** เลือก `Mesh Parts` → `Boundary Patches`
2. **ตรวจสอบ patch names:** ตรงกับ `constant/polyMesh/boundary` หรือไม่
3. **ตรวจสอบค่า:** ใช้ `Surface Licorice` หรือ `Glyph` เพื่อดู field values
4. **ตรวจสอบ continuity:** ใช้ `Contour` เพื่อดู gradients ที่ boundaries

> **💡 Physics Insight:** ตรวจสอบว่า velocity inlet และ pressure outlet สอดคล้องกัน ถ้าให้ velocity inlet สูง แต่ pressure outlet เป็น fixedValue อาจทำให้ mass imbalance

### 3.3 Common BC Issues

| Symptom | Root Cause | Fix |
|---------|------------|-----|
| **Solver diverges ทันที** | Wrong BC type (ต้องการ `zeroGradient` แต่ใส่ `fixedValue`) | ตรวจสอบ BC types ใน `0/` files |
| **Field not found** | Patch name mismatch ระหว่าง `0/` และ `constant/polyMesh/boundary` | เช็คชื่อ patches ให้ตรงกันทุก field |
| **Dimension error** | Field dimensions ผิด (เช่น pressure เป็น `[1 -1 -2 0 0]` แทน `[0 2 -2 0 0 0 0]`) | แก้ `dimensions` ใน `0/` files |
| **Unphysical results** | Initial conditions หรือ boundary values ผิด | ตรวจสอบค่าที่ให้สอดคล้องกับ physics |
| **Patch not found** | Missing patch in `boundary` file | รัน `createPatch` utilities หรือแก้ `blockMeshDict` |

---

## 4. Automated BC Consistency Check

### 4.1 Checking Patch Consistency

สคริปต์นี้ตรวจสอบว่าทุก field มี patches เหมือนกัน:

```bash
#!/bin/bash
# checkBCConsistency.sh - ตรวจสอบความสอดคล้องของ BC patches

set -e  # Stop on error

echo "=== BC Consistency Check ==="

# หา patches จาก boundary file
BOUNDARY_FILE="constant/polyMesh/boundary"
if [ ! -f "$BOUNDARY_FILE" ]; then
    echo "Error: $BOUNDARY_FILE not found. Run blockMesh/snappyHexMesh first."
    exit 1
fi

# Extract patch names from boundary file
PATCHES=$(grep -A 1 "^\s*[A-Za-z]" "$BOUNDARY_FILE" | grep -v "^\s*$" | grep -v "type" | grep -v "nFaces" | grep -v "startFace" | sed 's/^\s*//' | sed 's/\s*$//' | grep -v "^$")

echo "Found patches in boundary file:"
echo "$PATCHES"
echo ""

# Check each field file
FIELD_COUNT=0
MISMATCH_COUNT=0

for field_file in 0/*; do
    if [ -f "$field_file" ]; then
        FIELD_COUNT=$((FIELD_COUNT + 1))
        field_name=$(basename "$field_file")
        
        echo "Checking $field_name..."
        
        # Extract patches from field file
        FIELD_PATCHES=$(grep -E "^\s*[A-Za-z]" "$field_file" | grep -v "dimensions" | grep -v "internalField" | grep -v "boundaryField" | grep -v "}" | sed 's/^\s*//' | sed 's/\s*$//' | grep -v "^$")
        
        # Check for missing patches
        for patch in $PATCHES; do
            if ! echo "$FIELD_PATCHES" | grep -q "^$patch$"; then
                echo "  ⚠️  Missing patch '$patch' in $field_name"
                MISMATCH_COUNT=$((MISMATCH_COUNT + 1))
            fi
        done
        
        # Check for extra patches
        for fpatch in $FIELD_PATCHES; do
            if ! echo "$PATCHES" | grep -q "^$fpatch$"; then
                echo "  ⚠️  Extra patch '$fpatch' in $field_name (not in boundary file)"
                MISMATCH_COUNT=$((MISMATCH_COUNT + 1))
            fi
        done
    fi
done

echo ""
echo "=== Summary ==="
echo "Checked $FIELD_COUNT field files"
echo "Found $MISMATCH_COUNT inconsistencies"

if [ $MISMATCH_COUNT -eq 0 ]; then
    echo "✅ All BCs are consistent!"
    exit 0
else
    echo "❌ Please fix BC inconsistencies before running solver."
    exit 1
fi
```

**การใช้งาน:**
```bash
chmod +x checkBCConsistency.sh
./checkBCConsistency.sh
```

**คำอธิบายการทำงาน:**
1. อ่านชื่อ patches จาก `constant/polyMesh/boundary` (คือ "truth source")
2. เปรียบเทียบกับ patches ในแต่ละ field file ใน `0/`
3. รายงาน patches ที่หายไปหรือเกิน
4. Return exit code 0 ถ้าผ่าน, 1 ถี่มีปัญหา

### 4.2 Checking BC Types Compatibility

สคริปต์ตรวจสอบว่า BC types เหมาะสมกับ physics:

```bash
#!/bin/bash
# checkBCTypes.sh - ตรวจสอบความเหมาะสมของ BC types

echo "=== BC Type Compatibility Check ==="

# Check for incompressible solver BCs
if grep -q "application.*simpleFoam\|pimpleFoam\|icoFoam" system/controlDict; then
    echo "Detected incompressible solver..."
    
    # Check pressure boundary (should be fixedFluxPressure or zeroGradient at walls)
    if grep -A 2 "type.*fixedValue" 0/p | grep -q "inlet\|outlet"; then
        echo "⚠️  Warning: fixedValue on pressure at inlet/outlet may cause issues"
        echo "   Consider using zeroGradient or fixedFluxPressure"
    fi
fi

# Check for turbulence model BCs
if [ -f "0/k" ] && [ -f "0/epsilon" ]; then
    echo "Checking turbulence BCs..."
    
    # Wall functions require specific BC types
    if grep -q "type.*kqRWallFunction\|epsilonWallFunction" 0/k; then
        echo "ℹ️  Using wall functions - ensure y+ ≈ 30-300"
    fi
fi

echo "✅ BC type check complete"
```

---

## 5. Mesh Independence Study

### 5.1 What is Mesh Independence?

**Mesh independence** คือสถานะที่ผลลัพธ์ (velocity, pressure, forces) ไม่เปลี่ยนแปลงอย่างมีนัยสำคัญเมื่อเพิ่มความละเอียดของ mesh เป็นหลักฐานว่าคำตอบได้ลู่เข้าสู่ค่า "mesh-independent" ที่เชื่อถือได้

### 5.2 Systematic Mesh Independence Procedure

**Step 1: Create Multiple Mesh Resolutions**

```bash
#!/bin/bash
# createMeshes.sh - สร้าง meshes หลาย resolutions

# Base case
blockMesh

# Refined meshes (2x, 4x refinement)
for refinement in 1 2 3; do
    echo "Creating mesh level $refinement..."
    
    # Copy base mesh
    cp -r 1.e5/processor* 1.e$((refinement+5))/ 2>/dev/null || true
    
    # Refine using refineMesh
    refineMesh -overwrite -dict "system/refineMeshDict.level$refinement"
    
    # Rename for clarity
    mv 1.e5 1.e$((refinement+5))
    
    # Reconstruct if parallel
    reconstructParMesh -constant
done

echo "Created meshes: 1.e5, 1.e6, 1.e7, 1.e8 (cells)"
```

**Step 2: Run Simulations**

```bash
#!/bin/bash
# runMeshStudy.sh - Run simulations on all meshes

for mesh_level in 1.e5 1.e6 1.e7 1.e8; do
    echo "Running simulation on mesh $mesh_level..."
    
    # Copy case directory
    cp -r case_base case_$mesh_level
    
    # Link mesh
    ln -s ../1.e5 case_$mesh_level/1.e5
    
    # Run solver (capture output)
    simpleFoam > case_$mesh_level/log.simpleFoam 2>&1
    
    # Check convergence
    if ! grep -q "Finalising parallel run" case_$mesh_level/log.simpleFoam; then
        echo "⚠️  Warning: Case $mesh_level did not converge properly"
    fi
done

echo "All simulations complete"
```

**Step 3: Extract Results**

```python
#!/usr/bin/env python3
# extractMeshResults.py - Extract key quantities for comparison

import os
import pandas as pd
import re

def extract_force(log_file):
    """Extract force coefficients from log file"""
    with open(log_file, 'r') as f:
        content = f.read()
    
    # Extract Cd, Cl (example for aerodynamics)
    cd_match = re.search(r'Cd\s*=\s*([\d.]+)', content)
    cl_match = re.search(r'Cl\s*=\s*([\d.]+)', content)
    
    return {
        'Cd': float(cd_match.group(1)) if cd_match else None,
        'Cl': float(cl_match.group(1)) if cl_match else None
    }

# Collect results
results = []
for mesh_level in ['1e5', '1e6', '1e7', '1e8']:
    case_dir = f'case_{mesh_level}'
    log_file = f'{case_dir}/log.simpleFoam'
    
    if os.path.exists(log_file):
        data = extract_force(log_file)
        data['mesh_level'] = mesh_level
        data['cells'] = int(float(mesh_level))
        results.append(data)

# Save to CSV
df = pd.DataFrame(results)
df.to_csv('mesh_convergence_results.csv', index=False)
print(df)
```

**Step 4: Analyze Convergence**

```python
#!/usr/bin/env python3
# plotMeshConvergence.py - Visualize mesh convergence

import pandas as pd
import matplotlib.pyplot as plt

# Read data
df = pd.read_csv('mesh_convergence_results.csv')

# Plot Cd vs mesh size
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

# Left: Absolute values
ax1.plot(df['cells'], df['Cd'], 'o-', label='Cd')
ax1.plot(df['cells'], df['Cl'], 's-', label='Cl')
ax1.set_xscale('log')
ax1.set_xlabel('Number of Cells')
ax1.set_ylabel('Coefficient Value')
ax1.legend()
ax1.grid(True)
ax1.set_title('Mesh Convergence: Coefficients')

# Right: Relative change (Richardson extrapolation reference)
ref_Cd = df['Cd'].iloc[-1]  # Finest mesh as reference
ref_Cl = df['Cl'].iloc[-1]

df['Cd_rel_error'] = abs((df['Cd'] - ref_Cd) / ref_Cd) * 100
df['Cl_rel_error'] = abs((df['Cl'] - ref_Cl) / ref_Cl) * 100

ax2.plot(df['cells'], df['Cd_rel_error'], 'o-', label='Cd error')
ax2.plot(df['cells'], df['Cl_rel_error'], 's-', label='Cl error')
ax2.set_xscale('log')
ax2.set_yscale('log')
ax2.set_xlabel('Number of Cells')
ax2.set_ylabel('Relative Error [%]')
ax2.legend()
ax2.grid(True)
ax2.set_title('Mesh Convergence: Relative Error')

plt.tight_layout()
plt.savefig('mesh_convergence.png', dpi=150)
print("✅ Plot saved to mesh_convergence.png")

# Calculate Grid Convergence Index (GCI)
if len(df) >= 3:
    r21 = df['cells'].iloc[2] / df['cells'].iloc[1]
    r32 = df['cells'].iloc[1] / df['cells'].iloc[0]
    
    epsilon21 = abs(df['Cd'].iloc[2] - df['Cd'].iloc[1])
    epsilon32 = abs(df['Cd'].iloc[1] - df['Cd'].iloc[0])
    
    # Simplified GCI (full formulation requires order of accuracy p)
    GCI_21 = 1.5 * epsilon21 / (r21 - 1)
    GCI_32 = 1.5 * epsilon32 / (r32 - 1)
    
    print(f"\nGCI (coarse → medium): {GCI_32:.2e}")
    print(f"GCI (medium → fine): {GCI_21:.2e}")
```

### 5.3 Interpreting Mesh Independence Results

| Criterion | Acceptable Threshold | Action |
|-----------|---------------------|--------|
| **Change in key variables** < 1% between successive meshes | Converged | Use coarser mesh for efficiency |
| **Change in key variables** 1-5% | Approaching convergence | Consider finer mesh for critical regions |
| **Change in key variables** > 5% | Not converged | Must refine mesh or check physics |

> **💡 Practical Tip:** เริ่มจาก coarse mesh เพื่อ identify issues อย่างรวดเร็ว แล้วค่อย refine บริเวณที่มี high gradients (boundary layers, shocks, wakes) ด้วย adaptive mesh refinement

---

## 6. Quick Reference Tools

| Tool | Purpose | Common Options |
|------|---------|----------------|
| `checkMesh` | Mesh quality diagnostics | `-allGeometry -allTopology` |
| `foamToVTK` | Export for visualization | `-fields '(U p)' -time 0` |
| `renumberMesh` | Reduce bandwidth, speed up solver | `-overwrite` |
| `refineMesh` | Uniformly refine mesh | `-dict system/refineMeshDict` |
| `refineHexMesh` | Directional refinement | `-dirs '(1 1 0)'` |
| `createPatch` | Create/modify boundary patches | `-overwrite` |
| `topoSet` | Manipulate cell sets | `-dict system/topoSetDict` |

---

## Key Takeaways

✅ **Verification vs Validation:**
- **Verification** คือการตรวจสอบความถูกต้องของ mesh และ BC (ตาม spec)
- **Validation** คือการตรวจสอบความถูกต้องทางฟิสิกส์ของผลลัพธ์

✅ **Mesh Quality Essentials:**
- Non-orthogonality < 70° (warning), < 85° (hard limit)
- Skewness < 4 (warning), aspect ratio < 1000
- ใช้ `checkMesh -allGeometry` เพื่อ full diagnostics

✅ **BC Verification:**
- ตรวจสอบ patch names ตรงกันทุก field (`0/` vs `constant/polyMesh/boundary`)
- ตรวจสอบ BC types เหมาะสมกับ physics (wall functions, inlets, outlets)
- ใช้ `foamToVTK` + ParaView เพื่อ visual inspection

✅ **Mesh Independence:**
- Run 3+ mesh resolutions และ check convergence
- < 1% change = mesh independent
- < 5% change = acceptable for most engineering applications

✅ **Automated Checks:**
- ใช้ scripts สำหรับ BC consistency และ mesh study
- Log outputs สำหรับ reproducibility และ debugging

---

## Concept Check

### Scenario-Based Questions

<details>
<summary><b>1. คุณรัน checkMesh และได้ผลลัพธ์: "Max non-orthogonality = 78.5 WARNING". คุณควรทำอย่างไร?</b></summary>

**ตอบ:** 
- **อย่า** run solver ทันที - solver อาจ diverge
- **แก้ไข mesh:** ใช้ `snappyHexMesh` ด้วย `nSmoothSurface 3` เพื่อ smooth geometry, หรือเพิ่ม `nCellsBetweenLevels` เพื่อลับ gradual refinement
- **หลังแก้:** รัน `checkMesh` ใหม่จนกว่าจะ < 70°
- **ถ้าไม่สามารถแก้ได้:** ลองใช้ solvers ที่รองรับ higher non-orthogonality (เพิ่ม `nNonOrthogonalCorrectors` ใน `fvSolution`)

**💡 Concept:** Non-orthogonality สูงทำให้ interpolation scheme มี error ซึ่งอาจทำให้ pressure-velocity coupling ล้มเหลว
</details>

<details>
<summary><b>2. Case ของคุณมี patches: inlet, outlet, walls, แต่ในไฟล์ 0/p ไม่มี patch "walls". จะเกิดอะไรขึ้นเมื่อรัน solver?</b></summary>

**ตอบ:**
- **OpenFOAM error:** "Cannot find patch 'walls' in field file '0/p'" หรือ "patch 'walls' not found in boundaryField"
- **Solver จะหยุดทันที** ก่อนเริ่ม time stepping
- **แก้ไข:** เพิ่ม patch "walls" ใน `0/p` ด้วย BC type ที่เหมาะสม (เช่น `zeroGradient` สำหรับ incompressible flow)

**💡 Concept:** ทุก field ใน `0/` ต้องมี patches **เหมือนกันหมด** กับที่ระบุใน `constant/polyMesh/boundary`
</details>

<details>
<summary><b>3. คุณทำ mesh independence study และพบว่า Cd เปลี่ยนจาก 1.24 (mesh 1e5 cells) → 1.18 (1e6) → 1.16 (1e7). ควรใช้ mesh ไหน?</b></summary>

**ตอบ:**
- **Analysis:**
  - 1e5 → 1e6: Δ = (1.24-1.18)/1.18 = **5.1%** change
  - 1e6 → 1e7: Δ = (1.18-1.16)/1.16 = **1.7%** change
- **Recommendation:** 
  - **Mesh 1e6 cells** มีการเปลี่ยนแปลง < 2% จาก mesh ที่ละเอียดกว่า → **ใช้ 1e6 cells** เพราะ:
    - ประหยัดเวลาคำนวณเทียบกับ 1e7
    - Error < 2% อยู่ในช่วงที่ยอมรับได้ทางวิศวกรรม
  - ถ้าต้องการความแม่นยำสูงมาก (< 1%) → ใช้ 1e7 cells
- **สรุป:** Mesh 1e6 เป็น "sweet spot" ระหว่าง accuracy และ computational cost

**💡 Concept:** Mesh independence เป็นการแลกเปลี่ยนระหว่าง accuracy กับ computational resources - ไม่จำเป็นต้องใช้ mesh ละเอียดที่สุดเสมอไป
</details>

<details>
<summary><b>4. Pressure field ของคุณมี dimensions `[0 2 -2 0 0 0 0]` แต่คุณใช้ incompressible solver (simpleFoam). จะเกิดปัญหาอะไร?</b></summary>

**ตอบ:**
- **Dimensional inconsistency:** Incompressible solvers ใน OpenFOAM ใช้ **kinematic pressure** (p/ρ) มี units `[0 2 -2 0 0 0 0]` (m²/s²)
- **Problem:** ถ้าคุณใส่ pressure ด้วย units `[1 -1 -2 0 0 0 0]` (Pa = kg/(m·s²)) → solver จะ **divide ด้วย density** โดยอัตโนมัติ ทำให้ค่าผิด
- **แก้ไข:** ตรวจสอบ dimensions ใน `0/p`:
  - **Incompressible:** `[0 2 -2 0 0 0 0]` (kinematic pressure)
  - **Compressible:** `[1 -1 -2 0 0 0 0]` (static pressure)
- **💡 Concept:** ตรวจสอบ dimensions ทุกครั้ง - error ที่สุขุมมักมาจาก unit inconsistency

**Example fix:**
```cpp
// ถ้าใช้ compressible solver แต่อยากใส่ pressure in Pa:
dimensions      [1 -1 -2 0 0 0 0];
internalField   uniform 101325;  // Atmospheric pressure in Pa

// ถ้าใช้ incompressible solver (p/ρ):
dimensions      [0 2 -2 0 0 0 0];
internalField   uniform 0;       // Gauge pressure / density
```
</details>

---

## Related Documents

- **Verification Fundamentals:** [02_Mesh_BC_Verification.md](02_Mesh_BC_Verification.md)
- **Physical Validation:** [01_Physical_Validation.md](01_Physical_Validation.md) (ตรวจสอบความถูกต้องทางฟิสิกส์ของผลลัพธ์หลัง verification)
- **Validation Benchmarks:** [04_VALIDATION_BENCHMARKS/](../04_VALIDATION_BENCHMARKS/) (benchmark cases สำหรับ physical validation)
- **Code Verification (MMS):** [02a_Method_of_Manufactured_Solutions_MMS.md](02a_Method_of_Manufactured_Solutions_MMS.md) (verification of solver correctness)
- **Richardson Extrapolation:** [02b_Richardson_Extrapolation_GCI.md](02b_Richardson_Extrapolation_GCI.md) (formal mesh convergence analysis)