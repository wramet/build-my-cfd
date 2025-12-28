# Verification and Validation (V&V) Principles

หลักการตรวจสอบความถูกต้องของการจำลอง CFD

---

## Overview

| Term | Question | Method |
|------|----------|--------|
| **Verification** | "Are we solving the equations right?" | Code testing, MMS, grid studies |
| **Validation** | "Are we solving the right equations?" | Comparison with experiments |

```mermaid
flowchart LR
    A[Physical Reality] --> B[Math Model]
    B --> C[Numerical Solution]
    C --> D[Code Implementation]
    D -.->|Verification| C
    C -.->|Validation| A
```

---

## 1. Error Types

$$\varepsilon_{total} = \varepsilon_{discretization} + \varepsilon_{iteration} + \varepsilon_{round-off}$$

| Error Type | Source | Control |
|------------|--------|---------|
| Discretization | Mesh size, scheme order | Refine mesh |
| Iteration | Solver tolerance | Lower tolerance |
| Round-off | Floating-point | Usually negligible |

---

## 2. Mesh Independence Study

### Three-Grid Method

1. Create 3 meshes: coarse ($h_1$), medium ($h_2$), fine ($h_3$)
2. Refinement ratio: $r = h_i/h_{i+1} > 1.3$
3. Run same settings on each mesh

### Observed Order of Convergence

$$p = \frac{\log\left(\frac{f_3 - f_2}{f_2 - f_1}\right)}{\log(r)}$$

### Richardson Extrapolation

$$f_{exact} \approx f_1 + \frac{f_1 - f_2}{r^p - 1}$$

### Grid Convergence Index (GCI)

$$GCI_{fine} = F_s \frac{|f_1 - f_2|/|f_1|}{r^p - 1} \times 100\%$$

- $F_s = 1.25$ for 3-grid study
- Target: GCI < 5%

---

## 3. Error Norms

| Norm | Formula | Use |
|------|---------|-----|
| $L_1$ | $\frac{\int |f - f_{ref}| dV}{\int dV}$ | Average error |
| $L_2$ | $\sqrt{\frac{\int (f - f_{ref})^2 dV}{\int dV}}$ | RMS error |
| $L_\infty$ | $\max |f - f_{ref}|$ | Maximum error |

---

## 4. Wall Resolution ($y^+$)

$$y^+ = \frac{u_\tau y}{\nu}, \quad u_\tau = \sqrt{\frac{\tau_w}{\rho}}$$

| $y^+$ Range | Region | Model |
|-------------|--------|-------|
| < 5 | Viscous sublayer | Low-Re model |
| 5-30 | Buffer layer | Avoid |
| 30-300 | Log-law region | Wall functions |

### Check $y^+$ in OpenFOAM

```bash
postProcess -func yPlus
```

---

## 5. Validation Metrics

### RMSE

$$RMSE = \sqrt{\frac{1}{N}\sum_{i=1}^N (y_i^{CFD} - y_i^{exp})^2}$$

### Coefficient of Determination

$$R^2 = 1 - \frac{\sum(y_i - \hat{y}_i)^2}{\sum(y_i - \bar{y})^2}$$

Target: $R^2 > 0.95$, RMSE < experimental uncertainty

---

## 6. Best Practices

1. **Verify first**: Check code with MMS or analytical solutions
2. **Systematic refinement**: Uniform mesh refinement
3. **Blind validation**: Don't tune parameters to match data
4. **Document everything**: Record all V&V activities
5. **Quantify uncertainty**: Report GCI, error bounds

---

## 7. OpenFOAM Tools

| Tool | Purpose |
|------|---------|
| `checkMesh` | Mesh quality metrics |
| `postProcess -func residuals` | Convergence history |
| `yPlus` | Wall resolution check |
| `probes` | Point data extraction |

---

## Concept Check

<details>
<summary><b>1. Verification กับ Validation ต่างกันอย่างไร?</b></summary>

- **Verification**: ตรวจว่าโค้ดแก้สมการถูกต้องไหม (เทียบกับ analytical solution)
- **Validation**: ตรวจว่าแบบจำลองตรงกับความเป็นจริงไหม (เทียบกับ experiment)
</details>

<details>
<summary><b>2. ทำไมต้องทำ mesh independence study?</b></summary>

เพื่อให้มั่นใจว่าผลลัพธ์ไม่ขึ้นกับ mesh resolution — ถ้า mesh ละเอียดขึ้นแล้วผลไม่เปลี่ยน แสดงว่า discretization error ต่ำพอ
</details>

<details>
<summary><b>3. $y^+ \approx 1$ vs $y^+ \approx 30$ ใช้กับ model ต่างกันอย่างไร?</b></summary>

- **$y^+ \approx 1$**: Wall-resolved models (low-Re k-ω)
- **$y^+ \approx 30-300$**: Wall functions (standard k-ε)

ต้องเลือกให้ตรงกับ turbulence model ที่ใช้
</details>

---

## Related Documents

- **บทก่อนหน้า:** [00_Overview.md](00_Overview.md)
- **บทถัดไป:** [02_Mesh_Independence.md](02_Mesh_Independence.md)