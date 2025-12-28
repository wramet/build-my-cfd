# Mesh and BC Verification

การตรวจสอบ Mesh และ Boundary Conditions

---

## Overview

> Verify mesh quality และ BC correctness ก่อน run simulation

---

## 1. Mesh Quality Checks

```bash
# Check mesh
checkMesh

# Key metrics
# - Non-orthogonality: < 70°
# - Skewness: < 4
# - Aspect ratio: < 1000
```

---

## 2. checkMesh Output

```
Checking geometry...
    Overall domain bounding box (0 0 0) (1 1 1)
    Mesh has 3 geometric zones

Checking mesh quality...
    Max aspect ratio = 15 OK.
    Max non-orthogonality = 45 OK.
    Max skewness = 1.5 OK.
    
Mesh OK.
```

---

## 3. Boundary Condition Verification

```cpp
// Check BC types
foamToVTK -fields '(U p)'

// In ParaView: verify field values at boundaries
```

---

## 4. Common BC Issues

| Issue | Fix |
|-------|-----|
| Wrong type | Check `0/` files |
| Missing patch | Check `boundary` file |
| Dimension mismatch | Check field dimensions |
| Value error | Check initial values |

---

## 5. BC Consistency Check

```bash
#!/bin/bash
# Check all fields have same patches

patches=$(grep -E "^\s+type" 0/U | wc -l)

for field in 0/*; do
    n=$(grep -E "^\s+type" $field | wc -l)
    if [ $n -ne $patches ]; then
        echo "Mismatch: $field"
    fi
done
```

---

## 6. Verify Mesh Independence

```bash
# Run with different mesh sizes
for n in 20 40 80; do
    blockMesh -dict system/blockMeshDict.$n
    simpleFoam > log.$n
done

# Compare results
python3 plotMeshConvergence.py
```

---

## Quick Reference

| Tool | Purpose |
|------|---------|
| `checkMesh` | Mesh quality |
| `foamToVTK` | Visualize |
| `renumberMesh` | Improve ordering |
| `refineMesh` | Refine cells |

---

## Concept Check

<details>
<summary><b>1. Non-orthogonality limit?</b></summary>

**< 70°** for most solvers, **< 85°** with correctors
</details>

<details>
<summary><b>2. Mesh independence ทดสอบอย่างไร?</b></summary>

**Run with multiple mesh sizes**, check results converge
</details>

<details>
<summary><b>3. BC ผิดจะเกิดอะไร?</b></summary>

**Wrong solution** หรือ **divergence**
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Physical Validation:** [01_Physical_Validation.md](01_Physical_Validation.md)