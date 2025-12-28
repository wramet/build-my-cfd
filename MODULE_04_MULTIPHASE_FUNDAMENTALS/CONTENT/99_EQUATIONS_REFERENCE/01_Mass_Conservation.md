# Mass Conservation Equations

สมการอนุรักษ์มวลสำหรับ Multiphase Flow

---

## 1. General Form

$$\frac{\partial(\alpha_k \rho_k)}{\partial t} + \nabla \cdot (\alpha_k \rho_k \mathbf{u}_k) = \sum_{l \neq k} \dot{m}_{lk}$$

| Term | Meaning |
|------|---------|
| $\frac{\partial(\alpha_k \rho_k)}{\partial t}$ | Mass storage |
| $\nabla \cdot (\alpha_k \rho_k \mathbf{u}_k)$ | Convection |
| $\dot{m}_{lk}$ | Mass transfer from l to k |

---

## 2. Constraint

$$\sum_k \alpha_k = 1$$

All phases must fill the volume.

---

## 3. Incompressible Form

For constant $\rho_k$:

$$\frac{\partial \alpha_k}{\partial t} + \nabla \cdot (\alpha_k \mathbf{u}_k) = \frac{\dot{m}_k}{\rho_k}$$

---

## 4. Without Mass Transfer

$$\frac{\partial \alpha_k}{\partial t} + \nabla \cdot (\alpha_k \mathbf{u}_k) = 0$$

---

## 5. VOF Form

$$\frac{\partial \alpha}{\partial t} + \nabla \cdot (\alpha \mathbf{U}) + \nabla \cdot (\alpha(1-\alpha)\mathbf{U}_r) = 0$$

Last term = interface compression.

---

## 6. OpenFOAM Implementation

```cpp
fvScalarMatrix alphaEqn
(
    fvm::ddt(alpha)
  + fvm::div(phi, alpha)
 ==
    massTransferSource
);

alphaEqn.solve();
alpha.max(0);
alpha.min(1);
```

---

## 7. Normalization

After solving all α equations:

```cpp
sumAlpha = sum(phases);
forAll(phases, i)
{
    phases[i] /= sumAlpha;  // Ensure sum = 1
}
```

---

## Quick Reference

| Form | Equation |
|------|----------|
| General | $\partial(\alpha\rho)/\partial t + \nabla \cdot (\alpha\rho U) = \dot{m}$ |
| Incompressible | $\partial\alpha/\partial t + \nabla \cdot (\alpha U) = 0$ |
| VOF | + compression term |

---

## Concept Check

<details>
<summary><b>1. ทำไมต้อง normalize α?</b></summary>

เพื่อให้ **Σα = 1** เสมอ — numerical errors อาจทำให้ drift
</details>

<details>
<summary><b>2. Interface compression คืออะไร?</b></summary>

Term เพิ่มเติมใน VOF ที่ **sharpen** interface โดยการเพิ่ม flux ที่ interface
</details>

<details>
<summary><b>3. $\dot{m}_{lk}$ source มาจากไหน?</b></summary>

จาก **phase change models** เช่น evaporation, condensation, reaction
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Momentum Conservation:** [02_Momentum_Conservation.md](02_Momentum_Conservation.md)
- **Energy Conservation:** [03_Energy_Conservation.md](03_Energy_Conservation.md)