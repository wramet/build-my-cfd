# Mathematical Formulations

การวิเคราะห์มิติขั้นสูงใน OpenFOAM — Buckingham π และ Non-Dimensionalization

> **ทำไมบทนี้สำคัญ?**
> - เข้าใจ **theory** เบื้องหลัง dimension analysis
> - ใช้ **Buckingham π theorem** หา dimensionless groups
> - เข้าใจ **non-dimensionalization** สำหรับ numerical stability

---

## Overview

> **💡 Dimensional Analysis = ค้นหา physics invariants**
>
> ทุก physical law ต้อง dimensionally consistent
> Dimensionless groups (Re, Fr, Nu) capture essential physics

---

## 1. Buckingham π Theorem

### Principle

$$\Pi_m = \prod_{i=1}^n Q_i^{b_{im}}$$

ถ้ามีตัวแปร $n$ ตัว และมิติพื้นฐาน $k$ มิติ → หากลุ่มไร้มิติได้ $n - k$ กลุ่ม

### Example: Pipe Flow

| Variable | Dimension |
|----------|-----------|
| Δp | $[ML^{-1}T^{-2}]$ |
| ρ | $[ML^{-3}]$ |
| μ | $[ML^{-1}T^{-1}]$ |
| U | $[LT^{-1}]$ |
| D | $[L]$ |

**Dimensionless groups:**
- Reynolds: $Re = \frac{\rho UD}{\mu}$
- Euler: $Eu = \frac{\Delta p}{\rho U^2}$

---

## 2. dimensionSet Class

```cpp
// 7 dimensions: [M, L, T, Θ, I, N, J]
dimensionSet(1, -1, -2, 0, 0, 0, 0)  // Pressure [Pa]
dimensionSet(0, 1, -1, 0, 0, 0, 0)   // Velocity [m/s]
dimensionSet(1, -3, 0, 0, 0, 0, 0)   // Density [kg/m³]
```

### Common Dimensions

| Quantity | dimensionSet | Unit |
|----------|--------------|------|
| Pressure | `[1 -1 -2 0 0 0 0]` | Pa |
| Velocity | `[0 1 -1 0 0 0 0]` | m/s |
| Density | `[1 -3 0 0 0 0 0]` | kg/m³ |
| Viscosity | `[1 -1 -1 0 0 0 0]` | Pa·s |

---

## 3. Non-Dimensionalization

### Navier-Stokes (Dimensional)

$$\rho \frac{\partial \mathbf{u}}{\partial t} + \nabla \cdot (\rho \mathbf{u} \mathbf{u}) = -\nabla p + \nabla \cdot (\mu \nabla \mathbf{u})$$

### Navier-Stokes (Dimensionless)

$$\frac{\partial \tilde{\mathbf{u}}}{\partial \tilde{t}} + \tilde{\nabla} \cdot (\tilde{\mathbf{u}} \tilde{\mathbf{u}}) = -\tilde{\nabla} \tilde{p} + \frac{1}{Re} \tilde{\nabla}^2 \tilde{\mathbf{u}}$$

### Reference Scales

| Quantity | Scale |
|----------|-------|
| Length | $L_{ref}$ |
| Velocity | $U_{ref}$ |
| Pressure | $\rho U_{ref}^2$ |
| Time | $L_{ref}/U_{ref}$ |

---

## 4. Similarity

### Reynolds Similarity

$$Re_{model} = Re_{prototype} = \frac{\rho U L}{\mu}$$

### Key Dimensionless Numbers

| Number | Formula | Meaning |
|--------|---------|---------|
| Re | $\frac{\rho UL}{\mu}$ | Inertia/Viscosity |
| Fr | $\frac{U}{\sqrt{gL}}$ | Inertia/Gravity |
| We | $\frac{\rho U^2 L}{\sigma}$ | Inertia/Surface tension |
| Ma | $\frac{U}{c}$ | Velocity/Sound speed |

---

## 5. Tensor Dimensional Analysis

### Newtonian Constitutive

$$\boldsymbol{\tau} = \mu \dot{\boldsymbol{\gamma}}$$

| Tensor | Dimension |
|--------|-----------|
| Stress τ | $[ML^{-1}T^{-2}]$ |
| Strain rate γ̇ | $[T^{-1}]$ |
| Viscosity μ | $[ML^{-1}T^{-1}]$ |

Check: $\mu \cdot \dot{\gamma} = [ML^{-1}T^{-1}][T^{-1}] = [ML^{-1}T^{-2}]$ ✓

---

## 6. OpenFOAM Implementation

```cpp
// Create dimensioned scalar
dimensionedScalar rho("rho", dimDensity, 1000);
dimensionedScalar nu("nu", dimViscosity, 1e-6);

// Dimension checking automatic
dimensionedScalar Re = rho * U * L / (rho * nu);
// Re is dimensionless ✓

// Error if mismatch
// p + U;  // Compile error: dimension mismatch
```

### Predefined Dimensions

| Alias | Definition |
|-------|------------|
| `dimless` | `[0 0 0 0 0 0 0]` |
| `dimLength` | `[0 1 0 0 0 0 0]` |
| `dimTime` | `[0 0 1 0 0 0 0]` |
| `dimMass` | `[1 0 0 0 0 0 0]` |
| `dimVelocity` | `[0 1 -1 0 0 0 0]` |
| `dimPressure` | `[1 -1 -2 0 0 0 0]` |

---

## Quick Reference

| Task | Method |
|------|--------|
| Create dimensioned scalar | `dimensionedScalar("name", dims, value)` |
| Check if dimensionless | `dims.dimensionless()` |
| Get dimensions | `field.dimensions()` |
| Override check | `dimensionSet::checking(false)` |

---

## 🧠 Concept Check

<details>
<summary><b>1. ทำไมต้องใช้ 7 base dimensions?</b></summary>

เพราะเป็น **SI base units** ที่ครอบคลุมทุกปริมาณทางฟิสิกส์ (Mass, Length, Time, Temperature, Current, Mole, Luminous Intensity)
</details>

<details>
<summary><b>2. Non-dimensionalization ช่วยอะไร?</b></summary>

- **ปรับปรุง numerical stability** (values ≈ O(1))
- **ลด parameters** ในสมการ (เหลือแค่ Re, Fr, etc.)
- **ช่วย similarity analysis**
</details>

<details>
<summary><b>3. OpenFOAM ตรวจ dimension เมื่อไหร่?</b></summary>

**Compile-time** สำหรับ type mismatch และ **run-time** สำหรับ arithmetic operations
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Exercises:** [08_Exercises.md](08_Exercises.md)