# Validation and Benchmarks

การ Validate และ Benchmark Coupled Simulations

---

## Overview

> Validate coupled physics against **known solutions**

---

## 1. CHT Benchmarks

| Case | Description |
|------|-------------|
| Heated plate | 1D analytical |
| Cylinder in cross-flow | Experimental |
| Electronic cooling | Industry |

---

## 2. Analytical Validation

```cpp
// 1D steady conduction
// T(x) = Thot - (Thot - Tcold) * x / L

scalar Tanalytic = Thot - (Thot - Tcold) * x / L;
scalar error = mag(T - Tanalytic);
```

---

## 3. Interface Heat Flux

```cpp
// Calculate interface heat flux
surfaceScalarField heatFlux = fvc::snGrad(T) * kappa;

// Compare with expected
Info << "Heat flux: " << gSum(heatFlux * mesh.magSf()) << endl;
```

---

## 4. Conservation Check

```cpp
// Heat balance
scalar Qin = gSum(heatFlux.boundaryField()[inletI] * mesh.magSf());
scalar Qout = gSum(heatFlux.boundaryField()[outletI] * mesh.magSf());

scalar imbalance = mag(Qin + Qout) / max(mag(Qin), SMALL);
Info << "Imbalance: " << imbalance * 100 << "%" << endl;
```

---

## 5. Grid Convergence

```bash
# Run with different meshes
for level in coarse medium fine; do
    ./Allrun.$level
    postProcess -func 'probes'
done

# Check Richardson extrapolation
python3 checkConvergence.py
```

---

## 6. Error Metrics

| Metric | Formula |
|--------|---------|
| L2 | √(Σ(sim - ref)²/N) |
| L∞ | max(|sim - ref|) |
| Relative | |sim - ref|/|ref| |

---

## Quick Reference

| Check | Method |
|-------|--------|
| Accuracy | Analytical comparison |
| Conservation | Flux balance |
| Convergence | Grid study |
| Interface | Heat flux match |

---

## Concept Check

<details>
<summary><b>1. Validation vs Verification?</b></summary>

- **Validation**: Matches physics?
- **Verification**: Code correct?
</details>

<details>
<summary><b>2. Conservation check ทำอย่างไร?</b></summary>

**Compare heat in vs out** — should balance
</details>

<details>
<summary><b>3. Grid convergence ทำไม?</b></summary>

**Verify mesh-independent** results
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Exercises:** [07_Exercises.md](07_Exercises.md)
