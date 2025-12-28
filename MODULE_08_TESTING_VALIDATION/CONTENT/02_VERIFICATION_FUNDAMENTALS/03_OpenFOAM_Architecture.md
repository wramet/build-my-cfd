# OpenFOAM Architecture for Testing

สถาปัตยกรรม OpenFOAM สำหรับ Testing

---

## Overview

> เข้าใจ architecture เพื่อทดสอบได้อย่างมีประสิทธิภาพ

---

## 1. Code Organization

```
OpenFOAM/
├── src/           # Core libraries
│   ├── OpenFOAM/  # Primitives
│   ├── finiteVolume/
│   └── meshTools/
├── applications/
│   ├── solvers/
│   └── utilities/
└── test/          # Test code
```

---

## 2. Key Classes for Testing

| Class | Test Focus |
|-------|------------|
| `volScalarField` | Field operations |
| `fvMesh` | Mesh validity |
| `fvMatrix` | Linear system |
| `Time` | Time stepping |

---

## 3. Testing Entry Points

```cpp
// Test field operations
volScalarField T(...);
volScalarField T2 = sqr(T);

// Test matrix
fvScalarMatrix Teqn(fvm::laplacian(alpha, T));
solve(Teqn);

// Test mesh
checkMesh
```

---

## 4. RTS Testing

```cpp
// Test model selection
autoPtr<turbulenceModel> turb = turbulenceModel::New(dict);

// Verify correct type created
if (turb->type() != "kEpsilon")
{
    FatalError << "Wrong model";
}
```

---

## 5. Boundary Condition Testing

```cpp
// Test BC application
T.correctBoundaryConditions();

// Verify values at boundary
forAll(T.boundaryField()[patchI], faceI)
{
    ASSERT_NEAR(T.boundaryField()[patchI][faceI], expected, tol);
}
```

---

## 6. Parallel Testing

```bash
# Test decomposition
decomposePar

# Run parallel
mpirun -np 4 simpleFoam -parallel

# Check results match serial
reconstructPar
diff -r serial_results parallel_results
```

---

## Quick Reference

| Component | Test |
|-----------|------|
| Field | Create, operations |
| Mesh | checkMesh |
| Solver | Convergence |
| BC | correctBoundaryConditions |
| Parallel | Compare with serial |

---

## Concept Check

<details>
<summary><b>1. ทำไมต้องเข้าใจ architecture?</b></summary>

**Know what to test** และ how to access internals
</details>

<details>
<summary><b>2. RTS testing ทำอย่างไร?</b></summary>

**Create object, verify type** and behavior
</details>

<details>
<summary><b>3. Parallel testing ทำไม?</b></summary>

**Results should match serial** — verify decomposition correct
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Introduction:** [01_Introduction.md](01_Introduction.md)