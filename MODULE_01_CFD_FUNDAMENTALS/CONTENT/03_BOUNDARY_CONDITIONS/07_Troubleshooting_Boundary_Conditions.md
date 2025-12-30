# Troubleshooting Boundary Conditions

การวินิจฉัยและแก้ปัญหาที่เกิดจาก BC

---

## 🎯 Learning Objectives

หลังจากศึกษาบทนี้ คุณจะสามารถ:

1. **วินิจฉัยปัญหา BC** จาก error messages และ symptoms ที่พบบ่อย
2. **แยกแยะสาเหตุ** ระหว่าง BC issues, mesh problems, และ solver instability
3. **ใช้ diagnostic commands** ตรวจสอบสถานะ BCs อย่างเป็นระบบ
4. **แก้ปัญหา divergence** ที่ inlet, outlet, และ walls ได้อย่างถูกต้อง
5. **จัดการ backflow, pressure drift, และ turbulence instability** อย่างมีประสิทธิภาพ
6. **ตรวจสอบ y+** และเลือก wall function ที่เหมาะสมกับ mesh resolution

---

## 🔍 What: BC Troubleshooting Fundamentals

**BC Troubleshooting** คือกระบวนการระบุและแก้ไขปัญหาที่เกิดจาก Boundary Conditions ที่ผิดพลาด หรือไม่เหมาะสมกับปัญหา:

> **⚠️ สถิติสำคัญ:** ส่วนใหญ่ของ CFD failures (60-80%) มาจาก BC ผิด — ไม่ใช่ mesh หรือ solver

**ความท้าทายหลัก:**
- **Misleading errors:** "Maximum iterations exceeded" อาจมาจาก BC ผิด ไม่ใช่ linear solver
- **Coupling issues:** U-p coupling, turbulence-velocity coupling
- **Subtle errors:** Patch names, dimensions, value formats

---

## 💡 Why: Troubleshooting Strategy

### ทำไม BC Troubleshooting สำคัญ?

| Aspect | Impact | Consequence |
|--------|--------|-------------|
| **Simulation failures** | 60-80% จาก BC ผิด | เสียเวลา debug นาน |
| **Misleading errors** | Error messages หลอกตา | แก้ผิที่ → เสียเวลา |
| **Non-physical results** | BC ผิด แต่ converge | ผลลัพธ์ไร้ความหมาย |
| **Time savings** | Diagnostic workflow | Solve problems 10x faster |

### Diagnostic Mindset

```
Error Occurs
    ↓
Is it BC-related?
├─ Yes → Identify symptom → Find cause → Apply fix
└─ No  → Check mesh → Check solver → Check numerics
```

---

## 🛠️ How: Symptom-Based Quick Reference

### Quick Diagnosis Table

| Symptom | Most Likely BC Cause | Quick Fix |
|---------|---------------------|-----------|
| **"Maximum iterations exceeded"** | Over-specified U-p coupling | Change p to zeroGradient at inlet |
| **Negative velocity at outlet** | Backflow instability | Use inletOutlet instead of zeroGradient |
| **Pressure drift (monotonic rise/fall)** | No pressure reference | Add fixedValue p at one boundary |
| **Velocity ≠ 0 at wall** | Wrong wall BC | Use noSlip or fixedValue (0 0 0) |
| **k or ε becomes negative** | Turbulence instability | Use bounded schemes + relaxation |
| **NaN in turbulence fields** | Negative viscosity/production | Check initial conditions, bounds |
| **High residuals at inlet** | BC conflict | Verify U-p consistency |
| **Solution blows up immediately** | Catastrophic BC error | Check patch names, dimensions, values |

---

## 🔧 Troubleshooting Flowchart

```
                    ┌─────────────────────────┐
                    │  Simulation Error?      │
                    └───────────┬─────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │  Check Error Message    │
                    └───────────┬─────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
      ┌───────▼──────┐  ┌──────▼───────┐  ┌─────▼──────┐
      │Divergence?   │  │Backflow?     │  │Drift?      │
      └───────┬──────┘  └──────┬───────┘  └─────┬──────┘
              │                 │                 │
      ┌───────▼──────┐  ┌──────▼───────┐  ┌─────▼──────┐
      │Check U-p     │  │Outlet BC     │  │Pressure    │
      │at inlet      │  │inletOutlet?  │  │Reference?  │
      │              │  │              │  │            │
      │• U fixedValue│  │• zeroGradient│  │• Add       │
      │  p zeroGrad  │  │  → inletOutlet│  │  fixedValue│
      │              │  │• Extend      │  │  at outlet │
      └──────────────┘  │  domain      │  └────────────┘
                        └──────────────┘
              │                 │                 │
              └─────────────────┼─────────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │  Verify Fix:           │
                    │  • Check residuals     │
                    │  • Monitor field range │
                    │  • Verify physics      │
                    └─────────────────────────┘
```

---

## 🚨 Common Problems & Solutions

### Problem 1: Divergence at Inlet

**What:** Solver fails to converge, maximum iterations exceeded

**Symptoms:**
```
FOAM FATAL ERROR:
Maximum number of iterations exceeded
```
- Residuals spike at inlet
- High velocity fluctuations

**Causes & Solutions:**

| Cause | Solution | Code Fix |
|-------|----------|----------|
| **Over-specified U-p** | p เป็น zeroGradient | See below |
| **Velocity too high** | ลด inlet velocity | Ramp up gradually |
| **Turbulence inconsistency** | ปรับ k, ε ให้สอดคล้อง | Use formulas from [05_Common_BCs.md](05_Common_Boundary_Conditions_in_OpenFOAM.md) |
| **Poor initial conditions** | Initialize properly | `potentialFoam` first |

```cpp
// ❌ WRONG: Over-specified
inlet
{
    type    fixedValue;        // U
    value   uniform (10 0 0);
}

inlet
{
    type    fixedValue;        // p
    value   uniform 0;
}

// ✅ CORRECT: Well-posed
inlet
{
    type    fixedValue;        // U
    value   uniform (10 0 0);
}

inlet
{
    type    zeroGradient;      // p
}
```

**Why:** กำหนดทั้ง U และ p ที่ inlet → ปัญหา well-posedness

**Cross-reference:** ดู U-p coupling ใน [05_Common_Boundary_Conditions_in_OpenFOAM.md](05_Common_Boundary_Conditions_in_OpenFOAM.md)

---

### Problem 2: Backflow at Outlet

**What:** Flow re-enters domain through outlet

**Symptoms:**
- Negative velocity at outlet patches
- Solution becomes unstable
- Oscillating residuals

**Causes & Solutions:**

| Cause | Solution | Code Fix |
|-------|----------|----------|
| **Outlet too close** | ขยาย domain | Move outlet 10× characteristic length |
| **zeroGradient BC** | ใช้ inletOutlet | See below |
| **Pressure-driven reverse** | ใช้ pressureInletOutletVelocity | Calculates U from ∇p |

```cpp
// ❌ PROBLEMATIC: Doesn't handle backflow
outlet
{
    type    zeroGradient;
}

// ✅ BETTER: Handles backflow
outlet
{
    type        inletOutlet;
    inletValue  uniform (0 0 0);    // Value IF flow reverses
    value       uniform (10 0 0);   // Initial guess
}

// ✅ BEST: Backflow from pressure
outlet
{
    type    pressureInletOutletVelocity;
    value   uniform (10 0 0);
}
```

**Why:** `zeroGradient` = ∂U/∂n = 0 ทุกกรณี → ไม่รู้จัก backflow

**Cross-reference:** ดู outlet BCs ใน [05_Common_Boundary_Conditions_in_OpenFOAM.md](05_Common_Boundary_Conditions_in_OpenFOAM.md)

---

### Problem 3: High Velocity at Wall

**What:** Wall velocity ≠ 0

**Symptoms:**
- Unrealistic velocity near walls
- Slip behavior when should stick
- Wrong skin friction

**Causes & Solutions:**

```cpp
// ❌ WRONG: Wall acts like slip
wall
{
    type    zeroGradient;
}

// ✅ CORRECT: No-slip condition
wall
{
    type    noSlip;
}

// หรือ equivalent:
wall
{
    type    fixedValue;
    value   uniform (0 0 0);
}
```

**Why:** ของไหลจริงมี viscosity → "ติด" ผนัง (no-slip)

**Cross-reference:** ดู wall BCs ใน [05_Common_Boundary_Conditions_in_OpenFOAM.md](05_Common_Boundary_Conditions_in_OpenFOAM.md)

---

### Problem 4: Pressure Drifting

**What:** Pressure increases/decreases monotonically, never stabilizes

**Symptoms:**
- p เพิ่มหรือลดเรื่อยๆ
- ไม่ converge แม้ residuals ต่่างๆ จะต่อ
- Solution depends on initial guess

**Causes & Solutions:**

| Cause | Solution | Code Fix |
|-------|----------|----------|
| **No pressure reference** | Add fixedValue | See below |
| **All Neumann BCs** | Add at least one Dirichlet | pRefCell or outlet p |

```cpp
// Option 1: Fixed value at outlet (most common)
outlet
{
    type    fixedValue;
    value   uniform 0;      // Gauge pressure = 0
}

// Option 2: Reference cell in fvSolution
SIMPLE
{
    pRefCell    0;          // Cell index
    pRefValue   0;          // Reference pressure value
}

// Option 3: For transonic/compressible
outlet
{
    type    totalPressure;
    p0      uniform 101325; // Pa (absolute)
    gamma   1.4;
}
```

**Why:** Poisson equation สำหรับ pressure ต้องมี reference point อย่างน้อย 1 จุด

---

### Problem 5: Turbulence Instability

**What:** k หรือ ε กลายเป็นลบ, NaN ปรากฏ

**Symptoms:**
```
FOAM WARNING:
negative k ... in file ...
```
- Turbulence viscosity → ∞
- Simulation blows up

**Causes & Solutions:**

| Cause | Solution | Code Fix |
|-------|----------|----------|
| **Unbounded schemes** | Use upwind | See below |
| **No relaxation** | Add under-relaxation | factors 0.3-0.5 |
| **Bad initial conditions** | Initialize properly | Set k, ε from formulas |
| **Production >> dissipation** | Check mesh quality | Refine high-shear regions |

```cpp
// ✅ FIX 1: Bounded schemes
divSchemes
{
    div(phi,k)      Gauss upwind;       // NOT linear!
    div(phi,epsilon) Gauss upwind;
}

// ✅ FIX 2: Relaxation factors
relaxationFactors
{
    equations
    {
        k       0.5;
        epsilon 0.5;
        omega   0.5;
    }
}

// ✅ FIX 3: Bounds in fvOptions (optional)
boundK
{
    type    bounded;    // Prevents negative values
    field   k;
    min     1e-10;
}
```

**Why:** Linear schemes ไม่ preserve boundedness → ค่าติดลบได้

**Cross-reference:** ดู turbulence BC calculation ใน [05_Common_Boundary_Conditions_in_OpenFOAM.md](05_Common_Boundary_Conditions_in_OpenFOAM.md)

---

### Problem 6: y+ Outside Valid Range

**What:** Wall shear stress ผิด, velocity profile ใกล้ผนังไม่สมเหตุสมผล

**Diagnosis:**
```bash
postProcess -func yPlus
```

**y+ Ranges & Solutions:**

| y+ Range | Issue | Solution | Wall Function |
|----------|-------|----------|---------------|
| **< 5** | Using standard wall functions | Switch to low-Re | `nutLowReWallFunction` |
| **5-30** | ❌ Buffer layer | **AVOID!** | Re-mesh required |
| **30-300** | ✅ Valid for standard | Use standard | `nutkWallFunction` |
| **> 300** | Mesh too coarse | Refine mesh | `nutkWallFunction` |

```cpp
// ✅ SOLUTION 1: Low-Re treatment (y+ < 5)
wall
{
    type    nutLowReWallFunction;
    value   uniform 0;
}

// ✅ SOLUTION 2: Standard wall functions (30 < y+ < 300)
wall
{
    type    nutkWallFunction;
    value   uniform 0;
}

// ✅ SOLUTION 3: All y+ (robust)
wall
{
    type    nutUSpaldingWallFunction;    // From [06_Advanced_BCs.md](06_Advanced_Boundary_Conditions.md)
    value   uniform 0;
}
```

**Why:** Buffer layer (5 < y+ < 30) ไม่มี wall function ที่ถูกต้อง — viscous sublayer และ log-law ต่างก็ให้ความผิดพลาดสูง

**Cross-reference:** ดู wall functions ใน [06_Advanced_Boundary_Conditions.md](06_Advanced_Boundary_Conditions.md)

---

## 🔍 Diagnostic Commands

### Check BC Types

```bash
# List all boundary patches
foamListBoundaryPatches

# Show detailed BC info
foamInfoBCs
```

### Verify Patch Names

```bash
# Show patch names in BC files
grep -A 5 boundaryField 0/U

# Compare with mesh definition
diff <(grep -A 5 boundaryField 0/U | grep "^\s*[^ ]* {$" | sed 's/ {$//') \
     <(grep "^\s*[a-zA-Z]" constant/polyMesh/boundary | grep -v "^\s*$" | grep -v "^\s*//")
```

### Mesh Quality

```bash
# Full mesh check
checkMesh

# Specific checks
checkMesh -allGeometry -allTopology

# Mesh stats
foamListTimes
```

### Monitor Residuals

```bash
# Generate logs
foamLog log.simpleFoam

# Plot residuals
gnuplot residuals.gp

# Real-time monitoring
tail -f log.simpleFoam | grep "Solving for"
```

### Field Range Checks

```bash
# Min/max values
postProcess -func "fieldMinMax(U)"

# Check for NaN/negative
postProcess -func "fieldMinMax(k)"
postProcess -func "fieldMinMax(epsilon)"
```

### Boundary Values

```bash
# Sample values at boundaries
sample -dict system/sampleDict

# Paraview inspection
paraFoam -builtin
```

---

## ❌ Common Mistakes

### Mistake 1: Patch Name Mismatch

```cpp
// ❌ WRONG: Case-sensitive mismatch
// constant/polyMesh/boundary has "inlet"
// But 0/U uses "Inlet" (capital I)
boundaryField
{
    Inlet { ... }    // ❌ Won't match!
    inlet { ... }    // ✅ Correct
}
```

**How to avoid:**
```bash
# Copy exact names from mesh
grep -E "^\s*[a-zA-Z]" constant/polyMesh/boundary
```

---

### Mistake 2: Missing BC for Patch

```cpp
// ❌ WRONG: "sides" patch missing
boundaryField
{
    inlet  { ... }
    outlet { ... }
    // sides → FATAL ERROR!
}

// ✅ CORRECT: All patches present
boundaryField
{
    inlet  { ... }
    outlet { ... }
    sides  { ... }
}
```

**How to avoid:**
```bash
# Verify all patches have BCs
foamListBoundaryPatches | wc -l
grep -c "^\s*[a-zA-Z].*{$" 0/U
```

---

### Mistake 3: Dimension Errors

```cpp
// ❌ WRONG: Dimension doesn't match value type
dimensions [0 1 -1 0 0 0 0];   // velocity [m/s]
value uniform 10;              // ≠ vector!

// ✅ CORRECT: Vector value
dimensions [0 1 -1 0 0 0 0];
value uniform (10 0 0);        // vector

// ✅ CORRECT: Scalar value
dimensions [0 2 -2 0 0 0 0];   // pressure [Pa]
value uniform 100000;          // scalar
```

**Common dimensions:**
- Velocity: `[0 1 -1 0 0 0 0]` → vector `(Ux Uy Uz)`
- Pressure: `[0 2 -2 0 0 0 0]` → scalar
- Temperature: `[0 0 0 1 0 0 0]` → scalar
- k (TKE): `[0 2 -2 0 0 0 0]` → scalar

---

### Mistake 4: Value Consistency

```cpp
// ❌ UNNECESSARY: zeroGradient doesn't use value
outlet
{
    type  zeroGradient;
    value uniform 0;    // Not needed (but harmless)
}

// ✅ NECESSARY: fixedValue requires value
outlet
{
    type  fixedValue;
    value uniform 0;    // Required!
}

// ❌ MISSING: inletOutlet needs inletValue
outlet
{
    type        inletOutlet;
    value       uniform (10 0 0);
    // inletValue → REQUIRED if backflow occurs!
}

// ✅ COMPLETE: All required values
outlet
{
    type        inletOutlet;
    inletValue  uniform (0 0 0);    // Required!
    value       uniform (10 0 0);   // Initial guess
}
```

---

## ✅ Debugging Checklist

### Before Running

- [ ] Patch names match `constant/polyMesh/boundary` exactly (case-sensitive)
- [ ] Every patch has BC defined in all field files (U, p, T, k, ε, ω, nut)
- [ ] U and p coupling is consistent (not both fixedValue at same boundary)
- [ ] At least one pressure reference (fixedValue or pRefCell)
- [ ] Dimensions match field type (velocity = vector, pressure = scalar)
- [ ] Value format correct (vector vs scalar)
- [ ] Turbulence BCs consistent with model (k-ε, k-ω, etc.)
- [ ] y+ in valid range for chosen wall function

### After Error

- [ ] Check error message for specific BC mentions
- [ ] Identify symptom from Quick Diagnosis Table
- [ ] Verify mesh quality with `checkMesh`
- [ ] Monitor field ranges for NaN/negative values
- [ ] Check residuals for problematic boundaries
- [ ] Verify U-p coupling at inlet/outlet
- [ ] Confirm pressure reference exists
- [ ] Validate y+ is appropriate

### Verification

- [ ] Mass balance: $\sum \dot{m}_{in} \approx \sum \dot{m}_{out}$
- [ ] Residuals < 1e-4 for all variables
- [ ] Field ranges physically reasonable
- [ ] No backflow at outlets (or handled correctly)
- [ ] Wall behavior matches physics (no-slip, heat transfer)

---

## 📚 Concept Check

<details>
<summary><b>1. ทำไม buffer layer (5 < y+ < 30) ควรหลีกเลี่ยง?</b></summary>

**เหตุผล:**
- ไม่มี wall function ที่ถูกต้องสำหรับ region นี้
- **Viscous sublayer model** (y+ < 5) ให้ความผิดพลาดสูง
- **Log-law model** (y+ > 30) ให้ความผิดพลาดสูง
- Buffer layer คือ transition zone ที่ทั้งสอง model ต่างก็ fail

**Solution:** Re-mesh to get y+ < 5 (low-Re) หรือ y+ > 30 (wall functions)

**Cross-reference:** ดู wall function decision tree ใน [06_Advanced_Boundary_Conditions.md](06_Advanced_Boundary_Conditions.md)
</details>

<details>
<summary><b>2. Over-specification คืออะไร และเกิดจากอะไร?</b></summary>

**Over-specification** คือการกำหนด BC มากเกินไปที่ boundary เดียวหรือทั่วทั้ง domain:

**ตัวอย่าง:**
```cpp
// ❌ Over-specified at inlet
inlet
{
    type    fixedValue;    // U
    value   uniform (10 0 0);
}

inlet
{
    type    fixedValue;    // p
    value   uniform 0;
}
```

**ผลกระทบ:**
- Solver ไม่สามารถหา consistent solution
- Divergence หรือ instability
- Pressure-velocity coupling เสีย

**แก้ไข:** กำหนด U (Dirichlet) + p (Neumann) หรือกลับกัน

**Cross-reference:** ดู U-p coupling ใน [05_Common_Boundary_Conditions_in_OpenFOAM.md](05_Common_Boundary_Conditions_in_OpenFOAM.md)
</details>

<details>
<summary><b>3. Under-specification คืออะไร และเกิดจากอะไร?</b></summary>

**Under-specification** คือการกำหนด BC ไม่พอ:

**ตัวอย่าง:**
```cpp
// ❌ Under-specified: No pressure reference
inlet  { type fixedValue; value uniform (10 0 0); }  // U
outlet { type zeroGradient; }                        // U
inlet  { type zeroGradient; }                        // p
outlet { type zeroGradient; }                        // p
```

**ผลกระทบ:**
- Pressure "floats" (drifts)
- Solution depends on initial guess
- May not converge uniquely

**แก้ไข:** Add at least one pressure reference:
```cpp
outlet { type fixedValue; value uniform 0; }  // p
```

**Cross-reference:** ดู pressure BCs ใน [05_Common_Boundary_Conditions_in_OpenFOAM.md](05_Common_Boundary_Conditions_in_OpenFOAM.md)
</details>

<details>
<summary><b>4. inletOutlet เหมาะกับ outlet ที่มี backflow อย่างไร?</b></summary>

**Mechanism:**
- **Flow OUT:** Uses zeroGradient (∂U/∂n = 0)
- **Flow IN:** Uses `inletValue` instead of extrapolated value

```cpp
outlet
{
    type        inletOutlet;
    inletValue  uniform (0 0 0);    // Applied IF φ < 0
    value       uniform (10 0 0);   // Initial/current value
}
```

**เหนือกว่า zeroGradient:**
- `zeroGradient`: Always extrapolates → unstable with backflow
- `inletOutlet`: Adaptive → handles reverse flow gracefully

**สำหรับ pressure-driven backflow:**
```cpp
// Better: Calculate U from pressure field
outlet { type pressureInletOutletVelocity; }
```

**Cross-reference:** ดู outlet BC comparison ใน [05_Common_Boundary_Conditions_in_OpenFOAM.md](05_Common_Boundary_Conditions_in_OpenFOAM.md)
</details>

<details>
<summary><b>5. ทำไมต้องใช้ upwind schemes สำหรับ k และ ε?</b></summary>

**ปัญหา linear schemes:**
- Linear (central differencing) ไม่ preserve boundedness
- ค่าติดลบสามารถ propagate → k, ε → negative → νt → ∞

**Upwind advantages:**
- Bounded: ค่าไม่ติดลบ
- Stable: แม้ใน high-gradient regions
- Trade-off: Numerical diffusion (accuracy ↓, stability ↑)

```cpp
// ✅ Bounded
divSchemes
{
    div(phi,k)      Gauss upwind;
    div(phi,epsilon) Gauss upwind;
}

// ❌ Unbounded (use only with high-quality mesh + low Re)
divSchemes
{
    div(phi,k)      Gauss linear;
}
```

**Cross-reference:** ดู turbulence BCs ใน [05_Common_Boundary_Conditions_in_OpenFOAM.md](05_Common_Boundary_Conditions_in_OpenFOAM.md)
</details>

---

## 📌 Key Takeaways

### ✅ Core Diagnostic Principles

1. **Most CFD failures = BC problems** (60-80%)
2. **Error messages are often misleading** — "Maximum iterations" มัก = BC conflict
3. **Symptom-based diagnosis** คือ key — ดูตาราง Quick Diagnosis
4. **Systematic workflow** = แก้ปัญหาเร็ว 10x

### ✅ Common BC Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Over-specified U-p | Divergence at inlet | p → zeroGradient |
| Under-specified p | Pressure drift | Add p reference |
| Wrong wall BC | U ≠ 0 at wall | Use noSlip |
| Backflow instability | Negative U outlet | inletOutlet |
| y+ in buffer layer | Wrong skin friction | Re-mesh |
| Unbounded schemes | Negative k/ε | Use upwind |

### ✅ Best Practices

1. **Before running:**
   - Verify patch names match mesh
   - Check all fields have BCs
   - Confirm U-p coupling
   - Add pressure reference

2. **Troubleshooting workflow:**
   - Identify symptom → Find cause → Apply fix
   - Use diagnostic commands systematically
   - Verify with field range checks

3. **Verification:**
   - Mass balance check
   - Residuals < 1e-4
   - Physical consistency

### ✅ Quick Reference

| Problem | Command | Fix |
|---------|---------|-----|
| BC verification | `foamListBoundaryPatches` | Check patch names |
| Mesh quality | `checkMesh` | Fix mesh issues |
| NaN detection | `postProcess -func "fieldMinMax(k)"` | Fix initial conditions |
| y+ check | `postProcess -func yPlus` | Choose wall function |
| Residuals | `foamLog log.simpleFoam` | Identify problematic BC |

---

## 🔗 Cross-References

### Related Files in This Module
- **Previous:** [06_Advanced_Boundary_Conditions.md](06_Advanced_Boundary_Conditions.md) — Advanced BC types
- **Foundation:** [05_Common_Boundary_Conditions_in_OpenFOAM.md](05_Common_Boundary_Conditions_in_OpenFOAM.md) — Basic BC syntax and usage
- **Selection Guide:** [03_Selection_Guide_Which_BC_to_Use.md](03_Selection_Guide_Which_BC_to_Use.md) — Decision trees for BC selection
- **Mathematics:** [04_Mathematical_Formulation.md](04_Mathematical_Formulation.md) — BC theory

### Prerequisite Knowledge
- **Classification:** [02_Fundamental_Classification.md](02_Fundamental_Classification.md) — Dirichlet, Neumann, Robin
- **Introduction:** [01_Introduction.md](01_Introduction.md) — BC fundamentals

### Next Steps
- **Practice:** [08_Exercises.md](08_Exercises.md) — Hands-on BC troubleshooting exercises

---

**หัวข้อถัดไป:** [08_Exercises.md](08_Exercises.md) — แบบฝึกหัดปฏิบัติการ BC troubleshooting