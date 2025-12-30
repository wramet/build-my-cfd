# แบบฝึกหัด Finite Volume Method

แบบฝึกหัดเชิงปฏิบัติเพื่อฝึกทักษะ Discretization และการตั้งค่า OpenFOAM

> **ทำไมต้องทำแบบฝึกหัด?**
> - ฝึกคำนวณ **matrix, flux, Peclet number** ด้วยตัวเอง → เข้าใจ underlying math ลึกขึ้น
> - ฝึก **debug** mesh quality และ divergence จาก log files จริง → troubleshooting skills
> - เตรียมพร้อมสำหรับโปรเจคจริง → ลดเวลา trial-and-error

---

## โครงสร้างแบบฝึกหัด

แบบฝึกหัดแบ่งเป็น 4 ระดับความยาก:

```
Level 1: Theory Fundamentals        → แบบฝึกหัด 0-2
Level 2: Numerical Calculations     → แบบฝึกหัด 3-5
Level 3: OpenFOAM Debugging         → แบบฝึกหัด 6-8
Level 4: Complete Case Setup        → Mini-project
```

**Prerequisites:** ควรอ่าน [02_Fundamental_Concepts.md](02_Fundamental_Concepts.md) และ [03_Spatial_Discretization.md](03_Spatial_Discretization.md) ก่อน

---

## LEVEL 1: Theory Fundamentals

### แบบฝึกหัด 0: Warm-up Quiz

ทดสอบความเข้าใจพื้นฐานก่อนเริ่มแบบฝึกหัด

---

#### Q1: Finite Volume Method discretizes domain into:
- [ ] A) Nodes
- [ ] B) Elements  
- [x] C) Control volumes
- [ ] D) Faces

<details>
<summary><b>คำตอบและคำอธิบาย</b></summary>

**Correct: C) Control volumes**

FVM แบ่ง domain เป็น control volumes (cells) และ apply conservation laws บนแต่ละ cell:
$$\int_V \frac{\partial \phi}{\partial t} dV + \oint_A \mathbf{F} \cdot d\mathbf{A} = \int_V S dV$$

**ความแตกต่าง:**
- FDM: ใช้ nodes (grid points)
- FEM: ใช้ elements และ shape functions
- FVM: ใช้ volumes และ fluxes across faces
</details>

---

#### Q2: ใน 1D steady-state diffusion สมการ discretized สำหรับ cell P คือ:
- [ ] A) $\phi_E + 2\phi_P + \phi_W = 0$
- [x] B) $-\phi_W + 2\phi_P - \phi_E = 0$
- [ ] C) $\phi_E - \phi_P = 0$
- [ ] D) $\phi_P - \phi_W = 0$

<details>
<summary><b>คำตอบและคำอธิบาย</b></summary>

**Correct: B) $-\phi_W + 2\phi_P - \phi_E = 0$**

Derivation:
$$\frac{d^2\phi}{dx^2} = 0$$

Central difference:
$$\frac{\phi_E - 2\phi_P + \phi_W}{\Delta x^2} = 0$$

Multiply by $\Delta x^2$:
$$\phi_E - 2\phi_P + \phi_W = 0$$

Rearrange to standard form $a_P \phi_P + \sum a_{nb} \phi_{nb} = b$:
$$-\phi_W + 2\phi_P - \phi_E = 0$$

Coefficients: $a_W = -1, a_P = 2, a_E = -1$
</details>

---

#### Q3: Peclet number สูง (Pe > 10) แสดงว่า:
- [ ] A) Diffusion dominates
- [x] B) Convection dominates
- [ ] C) ต้องใช้ Central Differencing
- [ ] D) Mesh ละเอียดพอ

<details>
<summary><b>คำตอบและคำอธิบาย</b></summary>

**Correct: B) Convection dominates**

Peclet number:
$$Pe = \frac{\rho u L}{\Gamma} = \frac{\text{Convection}}{\text{Diffusion}}$$

| Pe Range | Dominant | Recommended Scheme |
|----------|----------|-------------------|
| < 0.1 | Diffusion | `Gauss linear` (Central) |
| 0.1 - 10 | Both | `Gauss linearUpwind` or TVD |
| > 10 | Convection | `Gauss upwind` or High-resolution TVD |

**Common mistake:** ใช้ Central Differencing เมื่อ Pe > 2 →  oscillation/unstable
</details>

---

#### Q4: สมการ $[A][\phi] = [b]$ ใน OpenFOAM ถูกสร้างโดย:
- [ ] A) `fvm::div(phi, U)` เท่านั้น
- [ ] B) `fvc::div(phi, U)` เท่านั้น
- [x] C) `fvm::` terms → matrix, `fvc::` terms → source vector
- [ ] D) Manual matrix assembly

<details>
<summary><b>คำตอบและคำอธิบาย</b></summary>

**Correct: C) `fvm::` → matrix, `fvc::` → source**

**fvm (finite volume matrix):** Implicit → contributes to $[A]$ and $[b]$
```cpp
fvm::ddt(T) + fvm::div(phi, T) - fvm::laplacian(DT, T)
```
→ Creates matrix coefficients $a_P, a_{nb}$

**fvc (finite volume calculus):** Explicit → contributes to $[b]$ only
```cpp
fvc::div(phi, T)  // Uses previous iterate values
fvc::grad(p)      // Explicit gradient
```

**Example:**
```cpp
solve(fvm::ddt(T) + fvm::div(phi, T) - fvm::laplacian(DT, T) == fvc::div(phi, T_old));
```
→ Implicit terms in matrix, explicit term in source
</details>

---

#### Q5: Non-orthogonal mesh ต้องการ:
- [ ] A) Non-orthogonal correctors เท่านั้น
- [ ] B) Limited schemes เท่านั้น
- [x] C) Non-orthogonal correctors + limited schemes
- [ ] D) ไม่ต้องการอะไร

<details>
<summary><b>คำตอบและคำอธิบาย</b></summary>

**Correct: C) Non-orthogonal correctors + limited schemes**

**Problem:** Face normal $\mathbf{n}$ ไม่ parallel กับ vector $\mathbf{d}_{PN}$ ระหว่าง cell centers

**Solution 1: Non-orthogonal correction** (in `fvSolution`)
```cpp
SIMPLE
{
    nNonOrthogonalCorrectors 3;  // Iteratively correct
}
```

**Solution 2: Limited schemes** (in `fvSchemes`)
```cpp
laplacianSchemes
{
    default Gauss linear limited 0.5;  // Limit correction
}
```

**Threshold:** Max non-orthogonality > 70° → ต้องใช้ทั้งสอง
</details>

---

### แบบฝึกหัด 1: Matrix Assembly Practice

เขียน matrix coefficients สำหรับ 1D steady diffusion

---

#### โจทย์

สมการ Diffusion 1D แบบ steady-state:
$$\frac{d^2\phi}{dx^2} = 0, \quad 0 \leq x \leq 3$$

**Parameters:**
| Parameter | Value |
|-----------|-------|
| Number of cells | 3 |
| Cell size | $\Delta x = 1$ m |
| Boundary conditions | $\phi_0 = 0$, $\phi_4 = 100$ |

**Mesh Layout:**
```
  φ₀=0  |   φ₁  |   φ₂  |   φ₃  |  φ₄=100
       x=0    x=1    x=2    x=3    x=4
       |<--1-->|<--1-->|<--1-->|
```

---

#### ภารกิจ

1. Discretize สมการสำหรับ cell 1, 2, 3 โดยใช้ Central Difference
2. เขียนในรูป $a_P \phi_P + a_W \phi_W + a_E \phi_E = b$
3. สร้าง matrix $[A][\phi] = [b]$ สำหรับ unknowns $\phi_1, \phi_2, \phi_3$
4. แก้หาค่า $\phi_1, \phi_2, \phi_3$

---

<details>
<summary><b>เฉลย: Step-by-step</b></summary>

**Step 1: Discretization**

Central difference สำหรับ cell $P$:
$$\frac{d^2\phi}{dx^2} \approx \frac{\phi_E - 2\phi_P + \phi_W}{\Delta x^2} = 0$$

Multiply by $\Delta x^2$:
$$\phi_E - 2\phi_P + \phi_W = 0$$

Rearrange:
$$-\phi_W + 2\phi_P - \phi_E = 0$$

**Step 2: Apply to each cell**

For Cell 1 ($P=1, W=0, E=2$):
$$-\phi_0 + 2\phi_1 - \phi_2 = 0$$
$$-\mathbf{0} + 2\phi_1 - \phi_2 = 0$$  (BC: $\phi_0 = 0$)

For Cell 2 ($P=2, W=1, E=3$):
$$-\phi_1 + 2\phi_2 - \phi_3 = 0$$

For Cell 3 ($P=3, W=2, E=4$):
$$-\phi_2 + 2\phi_3 - \phi_4 = 0$$
$$-\phi_2 + 2\phi_3 - \mathbf{100} = 0$$  (BC: $\phi_4 = 100$)

**Step 3: Matrix form**

$$
\begin{bmatrix}
2 & -1 & 0 \\
-1 & 2 & -1 \\
0 & -1 & 2
\end{bmatrix}
\begin{bmatrix}
\phi_1 \\
\phi_2 \\
\phi_3
\end{bmatrix}
=
\begin{bmatrix}
0 \\
0 \\
100
\end{bmatrix}
$$

**Coefficients:**
| Cell | $a_W$ | $a_P$ | $a_E$ | $b$ |
|------|-------|-------|-------|-----|
| 1    | -     | 2     | -1    | 0   |
| 2    | -1    | 2     | -1    | 0   |
| 3    | -1    | 2     | -     | 100 |

**Step 4: Solve**

From row 1: $2\phi_1 - \phi_2 = 0$ → $\phi_2 = 2\phi_1$

Substitute into row 2:
$$-\phi_1 + 2(2\phi_1) - \phi_3 = 0$$
$$3\phi_1 = \phi_3$$

From row 3:
$$-\phi_2 + 2\phi_3 = 100$$
$$-(2\phi_1) + 2(3\phi_1) = 100$$
$$4\phi_1 = 100$$
$$\phi_1 = 25$$

Therefore:
$$\phi_2 = 50, \quad \phi_3 = 75$$

**Verification:** Linear profile $\phi(x) = 25x$ ✓
- $\phi(1) = 25$ ✓
- $\phi(2) = 50$ ✓
- $\phi(3) = 75$ ✓
</details>

---

### แบบฝึกหัด 2: Face Flux Calculation

เปรียบที convection schemes สำหรับ face flux

---

#### โจทย์

กำหนด face ระหว่าง cell P และ cell N:

| Parameter | Value |
|-----------|-------|
| $\phi_P$ (upwind) | 10 |
| $\phi_N$ (downwind) | 20 |
| Velocity $u$ | 1 m/s (flow P → N) |
| Density $\rho$ | 1 kg/m³ |
| Face area $A_f$ | 1 m² |

คำนวณ Convective Mass Flux:
$$F = \rho \mathbf{u} \cdot \mathbf{A}_f \phi_f$$

โดยใช้:
- a) Central Differencing Scheme (CDS)
- b) Upwind Differencing Scheme (UDS)
- c) Linear Upwind Stabilized Transport (LUST)

---

<details>
<summary><b>เฉลย</b></summary>

**a) Central Differencing (CDS):**

$$\phi_f^{\text{CDS}} = \frac{\phi_P + \phi_N}{2} = \frac{10 + 20}{2} = 15$$

$$F_{\text{CDS}} = \rho u A_f \phi_f^{\text{CDS}} = 1 \times 1 \times 1 \times 15 = 15 \text{ units}$$

**b) Upwind Differencing (UDS):**

Since $u > 0$ (flow from P to N):
$$\phi_f^{\text{UDS}} = \phi_P = 10$$

$$F_{\text{UDS}} = 1 \times 1 \times 1 \times 10 = 10 \text{ units}$$

**c) LUST (Linear Upwind):**

LUST = blend of CDS + UDS:
$$\phi_f^{\text{LUST}} = \lambda \phi_f^{\text{CDS}} + (1-\lambda) \phi_f^{\text{UDS}}$$

Typical $\lambda = 0.75$:
$$\phi_f^{\text{LUST}} = 0.75 \times 15 + 0.25 \times 10 = 13.75$$

$$F_{\text{LUST}} = 13.75 \text{ units}$$

---

**Comparison:**

| Scheme | $\phi_f$ | Flux $F$ | Accuracy | Stability |
|--------|----------|----------|----------|-----------|
| CDS    | 15       | 15       | 2nd order | Unstable if Pe > 2 |
| UDS    | 10       | 10       | 1st order | Always stable |
| LUST   | 13.75    | 13.75    | ~1.5 order | Generally stable |

**Key insight:** Difference between CDS and UDS is 50%! → **Scheme choice matters**
</details>

---

## LEVEL 2: Numerical Calculations

### แบบฝึกหัด 3: Peclet Number & Scheme Selection

กำหนด convection scheme ที่เหมาะสมจาก flow conditions

---

#### โจทย์

Case A: Laminar flow in pipe
- Velocity: $u = 0.1$ m/s
- Kinematic viscosity: $\nu = 1 \times 10^{-6}$ m²/s
- Mesh size: $\Delta x = 0.01$ m

Case B: Turbulent flow in channel
- Velocity: $u = 5$ m/s
- Eddy viscosity: $\nu_t = 1 \times 10^{-3}$ m²/s
- Mesh size: $\Delta x = 0.001$ m

**ภารกิจ:** คำนวณ Peclet number และเลือก convection scheme

---

<details>
<summary><b>เฉลย</b></summary>

**Case A: Laminar Pipe Flow**

$$Pe = \frac{u \Delta x}{\nu} = \frac{0.1 \times 0.01}{1 \times 10^{-6}} = 1000$$

**Analysis:** $Pe \gg 2$ → Convection dominates

**Recommended scheme:**
```cpp
divSchemes
{
    div(phi,U)  Gauss upwind;              // Most stable
    // OR
    div(phi,U)  Gauss vanLeerV;            // TVD, sharper gradients
    // OR
    div(phi,U)  Gauss linearUpwind grad(U); // 2nd order upwind
}
```

**Case B: Turbulent Channel Flow**

$$Pe = \frac{u \Delta x}{\nu_t} = \frac{5 \times 0.001}{1 \times 10^{-3}} = 5$$

**Analysis:** $Pe = 5$ → Intermediate convection

**Recommended scheme:**
```cpp
divSchemes
{
    div(phi,U)  Gauss linearUpwind grad(U); // Good balance
    // OR
    div(phi,U)  Gauss limitedLinearV 1;     // TVD with limiter
    // OR for high accuracy:
    div(phi,U)  Gauss SFCD;                  // Self-filtered central
}
```

---

**Decision Tree:**

```
Calculate Pe
    |
    v
Pe < 2 ──────────────→ Gauss linear (CDS)
    |
    v
2 ≤ Pe ≤ 10 ─────────→ Gauss linearUpwind or TVD
    |
    v
Pe > 10 ─────────────→ Gauss upwind or high-res TVD
```

**Quick reference table:**

| Flow Type | Typical Pe | Scheme | OpenFOAM keyword |
|-----------|------------|--------|------------------|
| Laminar, low Re | < 1 | Central | `Gauss linear` |
| Laminar, moderate Re | 1-10 | Linear Upwind | `Gauss linearUpwind` |
| Turbulent, coarse mesh | > 10 | Upwind | `Gauss upwind` |
| Turbulent, fine mesh | 5-20 | TVD | `Gauss vanLeer` |
| Shocks, sharp gradients | > 20 | High-res TVD | `Gauss SUPERBEE` |

**Note:** สำหรับ scalar transport (T, k, epsilon) ให้ใช้ schemes ที่ stable กว่า velocity:
```cpp
div(phi,k)      Gauss upwind;
div(phi,epsilon) Gauss upwind;
```
</details>

---

### แบบฝึกหัด 4: Under-relaxation Factor Calculation

กำหนด under-relaxation factors สำหรับ steady-state simulation

---

#### โจทย์

Steady-state turbulent flow simulation diverges หลังจาก 100 iterations

**Current settings:**
```cpp
relaxationFactors
{
    fields
    {
        p       0.3;
    }
    equations
    {
        U       0.7;
        k       0.7;
        epsilon 0.7;
    }
}
```

**Last iteration residuals:**
```
time step continuity errors : sum local = 5.2e-2
Uncoupled solver residuals:
    p = 0.0012
    U = 0.0085
    k = 0.0023
    epsilon = 0.0156
```

**ภารกิจ:** ปรับ under-relaxation factors ให้ simulation converge

---

<details>
<summary><b>เฉลย</b></summary>

**Diagnosis:**
- Residuals oscillate ไม่ลง → **instability**
- `epsilon` residual สูงที่สุด (0.0156) → **turbulence equations ไม่ stable**
- Continuity error 5.2e-2 → pressure-velocity coupling ไม่ดี

**Strategy:** ลด relaxation factors (เพิ่ม stability)

**Recommended adjustment:**

```cpp
relaxationFactors
{
    fields
    {
        p       0.2;    // ลดจาก 0.3 (pressure coupling)
    }
    equations
    {
        U       0.5;    // ลดจาก 0.7
        k       0.5;    // ลดจาก 0.7
        epsilon 0.3;    // ลดมากที่สุด (sensitive)
    }
}
```

**Explanation:**

| Variable | Old α | New α | Reason |
|----------|-------|-------|--------|
| p | 0.3 | 0.2 | Pressure-velocity coupling critical |
| U | 0.7 | 0.5 | Reduce momentum oscillation |
| k | 0.7 | 0.5 | Couple with U |
| ε | 0.7 | 0.3 | Most sensitive, needs strongest relaxation |

**Under-relaxation formula:**
$$\phi^{n+1} = \alpha \phi^* + (1-\alpha)\phi^n$$

Where $\phi^*$ คือค่าจาก solver iteration ปัจจุบัน

**Trade-off:**
- α ต่ำ → Stable แต่ converge ช้า
- α สูง → Converge เร็ว แต่ risk divergence

**Adaptive strategy:** เริ่มด้วย α ต่ำ แล้วค่อยๆ เพิ่ม:
```cpp
// Initial 100 iterations
relaxationFactors { p 0.2; U 0.5; }
// After residuals drop to 1e-3
relaxationFactors { p 0.3; U 0.7; }
```

**Convergence criteria:**
```cpp
SIMPLE
{
    residualControl
    {
        p       1e-4;
        U       1e-4;
        k       1e-5;
        epsilon 1e-5;
    }
}
```
</details>

---

### แบบฝึกหัด 5: Matrix Sparsity Pattern

วิเคราะห์ matrix structure สำหรับ 2D mesh

---

#### โจทย์

2D structured mesh 4×4 cells (16 cells total)

```
  y
  ↑
4 | 13 14 15 16
3 |  9 10 11 12
2 |  5  6  7  8
1 |  1  2  3  4
  +------------→ x
    1  2  3  4
```

Discretized equation สำหรับ cell P:
$$a_P \phi_P + a_W \phi_W + a_E \phi_E + a_S \phi_S + a_N \phi_N = b$$

**ภารกิจ:**
1. เขียน nonzero pattern สำหรับ row 6 (cell 6)
2. คำนวณจำนวน nonzero entries ใน matrix ทั้งหมด
3. ประมาณการ sparsity ratio (nonzero / total)

---

<details>
<summary><b>เฉลย</b></summary>

**Step 1: Row 6 nonzero pattern**

Cell 6 has 4 neighbors:
- West: cell 5
- East: cell 7
- South: cell 2
- North: cell 10

$$a_6 \phi_6 + a_5 \phi_5 + a_7 \phi_7 + a_2 \phi_2 + a_{10} \phi_{10} = b_6$$

**Nonzero entries in row 6:** $\{2, 5, 6, 7, 10\}$

**Visualization:**
```
Row 6: [0 0 1 0 0 1 1 0 0 0 0 1 0 0 0 0] [b₆]
        ^     ^     ^  ^        ^
        2     5     6  7        10
```

---

**Step 2: Total nonzero count**

**Interior cells (9 cells: 2,3,5,6,7,9,10,11,14,15):**
- Each has 5 nonzeros (P + 4 neighbors)
- Total: 9 × 5 = 45

**Edge cells (6 cells: 1,4,8,13,16):**
- Each has 4 nonzeros (P + 3 neighbors)
- Total: 6 × 4 = 24

**Corner cells (4 cells: 1,4,13,16):**
- Each has 3 nonzeros (P + 2 neighbors)
- Total: 4 × 3 = 12

**Total nonzero entries:** 45 + 24 + 12 = **81**

---

**Step 3: Sparsity ratio**

Matrix size: 16 × 16 = 256 total entries

$$\text{Sparsity} = 1 - \frac{\text{nonzero}}{\text{total}} = 1 - \frac{81}{256} = 0.68$$

**Matrix is 68% sparse** (32% filled)

---

**General formula for 3D structured mesh:**

For $N_x \times N_y \times N_z$ mesh:
- Interior cells: 7 nonzeros each (P + 6 neighbors)
- Face cells: 6 nonzeros
- Edge cells: 5 nonzeros
- Corner cells: 4 nonzeros

**Sparsity ≈ 1 - 7/N** for large N in 3D

**Implication:** Sparse matrix solvers (GAMG, PBiCGStab) exploit this pattern!
</details>

---

## LEVEL 3: OpenFOAM Debugging

### แบบฝึกหัด 6: Diagnose Divergence from Log File

อ่านและวิเคราะห์ log file เพื่อหาสาเหตุ divergence

---

#### โจทย์

SimpleFoam simulation diverges หลังจาก 45 iterations

**Log file excerpt:**
```
Time = 1

smoothSolver:  Solving for Ux, Initial residual = 0.00254, Final residual = 1.24e-05, No Iterations 5
smoothSolver:  Solving for Uy, Initial residual = 0.00312, Final residual = 2.15e-05, No Iterations 5
smoothSolver:  Solving for Uz, Initial residual = 0.00189, Final residual = 9.87e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00876, Final residual = 7.65e-05, No Iterations 12
GAMG:  Solving for p, Initial residual = 0.00654, Final residual = 5.43e-05, No Iterations 10
time step continuity errors : sum local = 3.2e-02, global = 1.5e-03, cumulative = 2.8e-02
...
[Iterations 20-40: residuals decreasing gradually]
...
Time = 45

smoothSolver:  Solving for Ux, Initial residual = 0.12450, Final residual = 0.00876, No Iterations 100
smoothSolver:  Solving for Uy, Initial residual = 0.14560, Final residual = 0.00912, No Iterations 100
smoothSolver:  Solving for Uz, Initial residual = 0.09870, Final residual = 0.00765, No Iterations 100
GAMG:  Solving for p, Initial residual = 0.45670, Final residual = 0.03450, No Iterations 50
GAMG:  Solving for p, Initial residual = 0.54320, Final residual = 0.04560, No Iterations 50
time step continuity errors : sum local = 1.5e+10, global = 3.2e+08, cumulative = 8.9e+12

--> FOAM FATAL ERROR:
    Maximum number of iterations exceeded
```

**checkMesh output:**
```
Mesh failed checks:
    Non-orthogonality: Max = 78.5 deg (average = 45.2 deg)
    Skewness: Max = 0.85 (average = 0.45)
    Aspect ratio: Max = 12.5
```

**ภารกิจ:** วินิจฉัยปัญหาและแนะนำการแก้ไข

---

<details>
<summary><b>เฉลย: Diagnostic Process</b></summary>

**Step 1: Analyze residual pattern**

**Iteration 1-40:** Converging well
- U residuals: ~0.003 → ~0.001 ✓
- p residuals: ~0.009 → ~0.005 ✓
- Continuity error: ~0.03 (acceptable)

**Iteration 45:** Sudden divergence
- U residuals: 0.124 (40x increase!)
- p residuals: 0.456 (50x increase!)
- Continuity: 1.5e+10 (explosion!)

**Diagnosis:** **Catastrophic divergence** → numerical instability

---

**Step 2: Check mesh quality**

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Non-orthogonality | 78.5° | > 70° | **FAIL** |
| Skewness | 0.85 | > 0.6 | **FAIL** |
| Aspect ratio | 12.5 | > 10 | **FAIL** |

**Root cause:** **Poor mesh quality** ทั้ง 3 metrics

---

**Step 3: Identify failure mechanism**

High non-orthogonality (78.5°) → incorrect face flux interpolation

High skewness (0.85) → cell center not representative

High aspect ratio (12.5) → stiffness in matrix equations

**Combined:** → Matrix becomes ill-conditioned → solver diverges

---

**Step 4: Solutions (in priority order)**

**Solution 1: Improve mesh** (RECOMMENDED)

```cpp
// In blockMeshDict/snappyHexMeshDict
maxNonOrthogonality 65;  // Stricter than current 78.5
maxSkewness          0.5;  // Stricter than current 0.85
maxAspectRatio       5;    // Stricter than current 12.5
```

**Solution 2: Add numerical corrections** (if mesh cannot be improved)

```cpp
// system/fvSolution
SIMPLE
{
    nNonOrthogonalCorrectors 3;  // Add non-orthogonal correction
    nCorrectors 2;                // Increase pressure iterations
}

relaxationFactors
{
    fields
    {
        p       0.15;  // Reduce from 0.3
    }
    equations
    {
        U       0.3;   // Reduce from 0.7
    }
}
```

**Solution 3: Use more stable schemes**

```cpp
// system/fvSchemes
gradSchemes
{
    default         Gauss linear;  // Change from leastSquares
}

laplacianSchemes
{
    default         Gauss linear limited 0.333;  // Add limiter
}

divSchemes
{
    div(phi,U)      Gauss upwind;  // Degrade from linearUpwind
}
```

---

**Step 5: Verification**

After applying fixes, monitor convergence:

```
Expect:
- U residuals: < 0.01 after ~100 iterations
- p residuals: < 0.01 after ~100 iterations  
- Continuity error: < 1e-3
- No residual spikes
```

**Decision tree:**

```
Mesh quality OK?
    YES → Check relaxation factors
    NO  → Remesh OR add corrections

Still diverging?
    YES → Degrade schemes (upwind)
    NO  → Monitor convergence
```
</details>

---

### แบบฝึกหัด 7: Transient Simulation Stability

กำหนด time step และ Courant number สำหรับ transient simulation

---

#### โจทย์

PimpleFoam simulation สำหรับ vortex shedding หลัง cylinder

**Parameters:**
- Diameter: D = 0.1 m
- Velocity: U∞ = 1 m/s
- Mesh size: Δx = 0.001 m (near wall)
- Kinematic viscosity: ν = 1e-5 m²/s

**Current settings:**
```cpp
application     pimpleFoam;

startFrom       latestTime;

startTime       0;

stopAt          endTime;

endTime         10;

deltaT          0.01;

writeControl    timeStep;

writeInterval   100;
```

**Problem:** Simulation crashes หลังจาก t = 2.5s

```
Time = 2.5

Courant number mean: 2.3, max: 15.7
--> FOAM FATAL ERROR:
    Maximum Courant number > 1
```

**ภารกิจ:** แก้ไข `controlDict` และ `fvSolution` ให้ simulation stable

---

<details>
<summary><b>เฉลย</b></summary>

**Diagnosis:**

Current Courant numbers:
- Mean: 2.3 (should be < 1)
- Max: 15.7 (way too high!)

**Current time step:** Δt = 0.01s

**Local velocity near cylinder:** U ≈ 2 m/s (acceleration)

**Local mesh:** Δx = 0.001 m

**Actual Co:**
$$Co = \frac{U \Delta t}{\Delta x} = \frac{2 \times 0.01}{0.001} = 20$$

**Problem:** Time step ใหญ่เกินไป!

---

**Solution 1: Reduce time step** (EASIEST)

Target max Co < 1:

$$\Delta t_{max} = \frac{Co_{max} \cdot \Delta x_{min}}{U_{max}} = \frac{1 \times 0.001}{2} = 0.0005 s$$

```cpp
// system/controlDict
deltaT      0.0005;  // Reduce from 0.01

// Optional: Use adaptive time stepping
adjustTimeStep yes;

maxCo        0.8;    // Target max Courant number
maxAlphaCo   0.8;    // For VoF simulations

// Time step control
maxDeltaT    0.001;  // Upper limit
```

**With adaptive time stepping:**
```cpp
controlDict
{
    application     pimpleFoam;
    
    startFrom       latestTime;
    startTime       0;
    endTime         10;
    
    deltaT          0.0001;  // Initial time step
    
    adjustTimeStep  yes;
    maxCo           0.8;
    
    writeControl    timeStep;
    writeInterval   1000;  // Write less frequently
}
```

---

**Solution 2: Use PIMPLE outer correctors** (for accuracy)

```cpp
// system/fvSolution
PIMPLE
{
    nOuterCorrectors    2;      // Increase for stability
    nCorrectors         2;      // Pressure correctors
    nNonOrthogonalCorrectors 1;
    
    momentumPredictor  yes;
    
    // Convergence criteria
    residualControl
    {
        p               1e-4;
        U               1e-4;
    }
}

relaxationFactors
{
    equations
    {
        U               0.9;    // Less relaxation for transient
        p               0.9;
    }
}
```

---

**Solution 3: Optimize schemes**

```cpp
// system/fvSchemes
ddtSchemes
{
    default         backward;  // 2nd order, more accurate
}

gradSchemes
{
    default         cellLimited Gauss linear 1;
}

divSchemes
{
    default         none;
    
    // For transient: use bounded schemes
    div(phi,U)      Gauss linearUpwind grad(U);
    div(phi,k)      Gauss upwind;  // Stable for turbulence
    div(phi,epsilon) Gauss upwind;
}

laplacianSchemes
{
    default         Gauss linear limited 0.5;
}
```

---

**Verification:**

After changes, check Co numbers:

```
Time = 0.5

Courant number mean: 0.23, max: 0.67  ← Acceptable!
deltaT = 0.00067                        ← Auto-adjusted

PIMPLE: iteration 1
    p residuals: 0.0023 → 0.00012
    U residuals: 0.0045 → 0.00023
```

**Guidelines:**

| Simulation type | Recommended max Co | Reason |
|----------------|-------------------|--------|
| Steady-state | N/A | No time dependence |
| Transient (explicit) | < 0.5 | Strict stability |
| Transient (implicit) | < 1.0 | Moderate stability |
| Transient (PIMPLE) | < 0.8 | Balance accuracy/speed |

**Performance vs Accuracy trade-off:**

| Δt | Co | Speed | Accuracy | Stability |
|----|----|-------|----------|-----------|
| 0.0001 | 0.2 | Slow | High | Very stable |
| 0.0005 | 0.8 | Medium | Good | Stable |
| 0.001 | 1.5 | Fast | Poor | Unstable |

**Recommendation:** Start with Δt = 0.0005 and adaptive time stepping
</details>

---

### แบบฝึกหัด 8: Boundary Condition Debugging

วินิจฉัยปัญหาจาก boundary conditions ที่ไม่ถูกต้อง

---

#### โจทย์

Scalar transport simulation สำหรับ temperature

**Geometry:** 2D channel 1m × 0.1m

**Boundary conditions in `0/T`:**
```cpp
dimensions      [0 0 0 1 0 0 0];

internalField   uniform 300;

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 350;
    }
    
    outlet
    {
        type            zeroGradient;
    }
    
    walls
    {
        type            fixedValue;
        value           uniform 300;
    }
    
    frontAndBack
    {
        type            empty;
    }
}
```

**Problem:** Temperature values explode to 1e6 after 10 iterations

**Log file:**
```
Time = 10

smoothSolver:  Solving for T, Initial residual = 1.0e+02, Final residual = 8.5e+01
```

**ภารกิจ:** หาสาเหตุและแก้ไข boundary conditions

---

<details>
<summary><b>เฉลย</b></summary>

**Step 1: Check boundary condition consistency**

**Flow direction:** inlet → outlet

**Boundaries:**
- Inlet: T = 350 K (fixed) ✓
- Outlet: zeroGradient ✓ (flow exits)
- Walls: T = 300 K (fixed) ✓

**Physical setup:**
```
350 K ────────► zeroGradient
  │                      │
  │   Flow              │
  │                      │
300 K ─────────────── 300 K
```

**Potential issue:** Fixed temperature on all walls + inlet → **over-constrained**

---

**Step 2: Verify mesh and field**

Check `checkMesh`:
```bash
checkMesh
```
→ Mesh OK

Check `T` field after first iteration:
```bash
paraFoam
```
→ Temperature shows oscillations near walls

**Diagnosis:** Conflicting boundary conditions create **discontinuity**

---

**Step 3: Identify problem**

**At corners (inlet-wall):**
- Inlet condition: T = 350 K
- Wall condition: T = 300 K
- Corner cell: Which value to use?

**Result:** Numerical conflict → solver instability

---

**Solution 1: Use gradient boundary at walls** (PHYSICALLY CORRECT)

```cpp
// 0/T
walls
{
    type            zeroGradient;  // Adiabatic walls
    
    // OR if heat flux is known:
    // type            externalWallHeatFlux;
    // q               uniform 0;  // W/m²
}
```

**Physical reasoning:**
- Adiabatic walls → no heat transfer → dT/dn = 0
- Temperature evolves by convection only

---

**Solution 2: Use mixed boundary condition** (if heat transfer)

```cpp
walls
{
    type            externalWallHeatFlux;
    mode            coefficient;
    
    h               uniform 10;    // Heat transfer coeff [W/m²K]
    Ta              uniform 300;   // Ambient temp [K]
    
    // q = h * (T_wall - T_ambient)
    thickness       uniform 0.01;  // Wall thickness [m]
    kappa           uniform 0.5;   // Thermal conductivity [W/mK]
}
```

---

**Solution 3: Relax the transition at corners** (if fixed BC needed)

```cpp
// 0/T
inlet
{
    type            fixedValue;
    value           uniform 350;
}

walls
{
    type            fixedValue;
    
    // Smooth transition near inlet
    value           uniform 300;
    
    // OR use coded condition
    type            codedFixedValue;
    value           uniform 300;
    
    code
    #{
        const scalarField& C = patch().Cf();
        scalarField& T = *this;
        
        forAll(T, i)
        {
            scalar x = C[i].x();
            if (x < 0.01)  // Near inlet
            {
                T[i] = 350 - 50 * (x / 0.01);  // Linear ramp
            }
            else
            {
                T[i] = 300;
            }
        }
    #};
}
```

---

**Step 4: Verify fix**

After applying zeroGradient at walls:

```
Time = 100

smoothSolver:  Solving for T, Initial residual = 0.0045, Final residual = 2.3e-06
Temperature range: min = 300 K, max = 350 K  ← Physical!
```

---

**General BC Debugging Checklist:**

| Issue | Symptom | Fix |
|-------|---------|-----|
| Fixed-fixed conflict | Oscillation/residual spike | Change one to gradient |
| Wrong gradient type | Wrong physics | Check type (zeroGradient vs fixedGradient) |
| Missing boundary | Error "cannot find BC" | Add all patches in `boundary` file |
| Inconsistent dimensions | Compilation error | Check `[0 0 0 1 0 0 0]` format |

**Common BC combinations:**

| Patch | Velocity | Pressure | Scalar |
|-------|----------|----------|--------|
| Inlet | fixedValue | zeroGradient | fixedValue |
| Outlet | zeroGradient | fixedValue | zeroGradient |
| Wall | noSlip | zeroGradient | zeroGradient/fixedValue |
| Symmetry | symmetry | symmetry | symmetry |
</details>

---

## LEVEL 4: Complete Case Setup

### Mini-Project: Laminar Backward Facing Step

Setup complete OpenFOAM case ตั้งแต่เริ่มจนถึง converge

---

#### 问题描述

**Geometry:** Backward-facing step (classic CFD benchmark)

```
        ┌───────────────────────── Outlet
        │                       │
        │   Recirculation      │
Inlet   │   zone               │
  ─────→┴──────────────────────┘
        ↑
      Step (h = 0.01 m)
```

**Parameters:**
- Inlet height: h = 0.01 m (step height)
- Channel height: H = 0.02 m (after expansion)
- Channel length: L = 0.3 m
- Inlet velocity: U_in = 0.5 m/s (uniform)
- Fluid: Air (ν = 1.5e-5 m²/s)
- Reynolds number: Re_h = U_in × h / ν ≈ 333

**Physics:**
- Laminar flow (Re < 1000)
- Recirculation zone after step
- Reattachment length: L_r ≈ 7h (expected)

---

#### ภารกิจ

1. **Setup mesh** (ใช้ blockMesh)
2. **Define boundary conditions** สำหรับ U, p, T
3. **Configure schemes and solvers** ใน fvSchemes/fvSolution
4. **Run simulation** จน converge
5. **Validate results** (compare reattachment length)

---

<details>
<summary><b>Complete Solution</b></summary>

---

## PART 1: Mesh Generation

**`system/blockMeshDict`:**

```cpp
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

scale   0.01;  // Scale to cm (all units in cm)

vertices
(
    (0 0 0)           // 0: Inlet bottom (before step)
    (0 1 0)           // 1: Inlet top (before step)
    (0 1 0)           // 2: Step top-left
    (0 2 0)           // 3: Inlet top (after step)
    (30 0 0)          // 4: Outlet bottom
    (30 1 0)          // 5: Step top-right
    (30 1 0)          // 6: Step outlet-right
    (30 2 0)          // 7: Outlet top
    
    (0 0 0.1)         // 8: Front (z+) 
    (0 1 0.1)         // 9
    (0 1 0.1)         // 10
    (0 2 0.1)         // 11
    (30 0 0.1)        // 12
    (30 1 0.1)        // 13
    (30 1 0.1)        // 14
    (30 2 0.1)        // 15
);

blocks
(
    // Block 0: Inlet section (before step)
    hex (0 1 1 0 8 9 9 8) (50 10 1) simpleGrading (1 1 1)
    
    // Block 1: After step, lower section
    hex (4 5 5 4 12 13 13 12) (150 10 1) simpleGrading (1 1 1)
    
    // Block 2: After step, upper section  
    hex (5 6 7 5 13 14 15 13) (150 10 1) simpleGrading (1 1 1)
);

boundary
(
    inlet
    {
        type patch;
        faces
        (
            (0 8 9 1)
        );
    }
    
    outlet
    {
        type patch;
        faces
        (
            (4 12 13 5)
            (5 13 14 6)
            (6 14 15 7)
        );
    }
    
    walls
    {
        type wall;
        faces
        (
            (1 9 8 0)           // Inlet top
            (0 4 12 8)          // Bottom wall (after step)
            (0 8 12 4)          // Bottom (redundant, blockMesh handles)
            (1 2 10 9)          // Step vertical face
            (2 3 11 10)         // Inlet top (after step)
            (3 7 15 11)         // Top wall
        );
    }
    
    frontAndBack
    {
        type empty;
        faces
        (
            (0 1 9 8)
            (4 5 13 12)
            (5 6 14 13)
            (6 7 15 14)
        );
    }
);

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
```

**Mesh quality check:**
```bash
blockMesh
checkMesh
```

Expected output:
```
Mesh OK
    Non-orthogonality: < 10°
    Aspect ratio: < 5
```

---

## PART 2: Boundary Conditions

**`0/U`:**
```cpp
dimensions      [0 1 -1 0 0 0 0];

internalField   uniform (0 0 0);

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform (0.5 0 0);  // 0.5 m/s in x-direction
    }
    
    outlet
    {
        type            zeroGradient;
    }
    
    walls
    {
        type            noSlip;
    }
    
    frontAndBack
    {
        type            empty;
    }
}
```

**`0/p`:**
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
        value           uniform 0;  // Gauge pressure = 0
    }
    
    walls
    {
        type            zeroGradient;
    }
    
    frontAndBack
    {
        type            empty;
    }
}
```

**Optional: `0/T` (for thermal simulation)**
```cpp
dimensions      [0 0 0 1 0 0 0];

internalField   uniform 300;

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 300;
    }
    
    outlet
    {
        type            zeroGradient;
    }
    
    walls
    {
        type            fixedValue;
        value           uniform 310;  // Heated walls
    }
    
    frontAndBack
    {
        type            empty;
    }
}
```

---

## PART 3: Numerical Schemes

**`system/fvSchemes`:**
```cpp
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvSchemes;
}

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

ddtSchemes
{
    default         steadyState;
}

gradSchemes
{
    default         Gauss linear;
}

divSchemes
{
    default         none;
    
    // Laminar flow: Re = 333, mesh refined → use linearUpwind
    div(phi,U)      Gauss linearUpwind grad(U);
    
    // If turbulent:
    // div(phi,k)      Gauss upwind;
    // div(phi,epsilon) Gauss upwind;
}

laplacianSchemes
{
    default         Gauss linear corrected;
}

interpolationSchemes
{
    default         linear;
}

snGradSchemes
{
    default         corrected;
}

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
```

---

**`system/fvSolution`:**
```cpp
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvSolution;
}

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-06;
        relTol          0.1;
        
        smoother        GaussSeidel;
        
        nPreSweeps      0;
        nPostSweeps     2;
        cacheAgglomeration on;
        agglomerator    faceAreaPair;
        nCellsInCoarsestLevel 10;
        mergeLevels     1;
    }
    
    pFinal
    {
        $p;
        relTol          0;
    }
    
    U
    {
        solver          smoothSolver;
        smoother        GaussSeidel;
        tolerance       1e-05;
        relTol          0.1;
    }
    
    T
    {
        solver          smoothSolver;
        smoother        GaussSeidel;
        tolerance       1e-05;
        relTol          0.1;
    }
}

SIMPLE
{
    nNonOrthogonalCorrectors 0;
    
    residualControl
    {
        p               1e-5;
        U               1e-5;
        // T               1e-6;
    }
}

relaxationFactors
{
    fields
    {
        p               0.3;
    }
    equations
    {
        U               0.7;
        T               0.7;
    }
}

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
```

---

**`system/controlDict`:**
```cpp
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      controlDict;
}

application     simpleFoam;

startFrom       startTime;

startTime       0;

stopAt          endTime;

endTime         1000;

deltaT          1;

writeControl    timeStep;

writeInterval   100;

purgeWrite      0;

writeFormat     ascii;

writePrecision  6;

writeCompression off;

timeFormat      general;

graphFormat     raw;

runTimeModifiable yes;

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
```

---

## PART 4: Run Simulation

**Step 1: Initialize case**
```bash
# Create mesh
blockMesh

# Check mesh
checkMesh

# (Optional) Decompose for parallel run
decomposePar
```

**Step 2: Run solver**
```bash
# Serial
simpleFoam

# OR parallel (4 cores)
mpirun -np 4 simpleFoam -parallel
```

**Step 3: Monitor convergence**
```bash
# Monitor residuals
tail -f log.simpleFoam

# Expected output:
# Time = 100
# smoothSolver: Solving for Ux, Initial residual = 0.0045, Final residual = 2.3e-06
# smoothSolver: Solving for Uy, Initial residual = 0.0032, Final residual = 1.8e-06
# GAMG: Solving for p, Initial residual = 0.0234, Final residual = 1.2e-06
# time step continuity errors: sum local = 1.5e-05, global = 2.3e-07
```

**Step 4: Visualize**
```bash
# Reconstruct (if parallel)
reconstructPar

# Open in ParaView
paraFoam
```

---

## PART 5: Validation

**Expected results:**

1. **Recirculation zone:** Behind step
   - U_x < 0 near wall (backflow)
   
2. **Reattachment length:** L_r ≈ 7h = 0.07 m
   - Measured from step to where U_x = 0 at wall

3. **Velocity profile:**
   ```
   U_max at y = H (top wall)
   U ≈ 0 at y = 0 (bottom wall, recirculation)
   ```

**Validation steps:**

**In ParaView:**
1. Plot U_x contour along centerline
2. Use "Plot Over Line" to extract velocity profile
3. Measure reattachment length

**Compare with literature:**
| Re | L_r/h (expected) | L_r/h (OpenFOAM) | Error |
|----|------------------|------------------|-------|
| 333 | ~7 | ? | < 10% |

**Common issues and fixes:**

| Issue | Symptom | Fix |
|-------|---------|-----|
| No recirculation | U_x > 0 everywhere | Mesh too coarse, refine near step |
| Early reattachment | L_r < 5h | Outlet too close, extend domain |
| Divergence | Residuals spike | Reduce relaxation factors |

---

## PART 6: Extensions

**1. Grid convergence study:**
```bash
# Refine mesh
refineMesh '("0.01 0.02 0")'  # Refine x-direction

# Run again and compare L_r
```

**2. Transient simulation:**
```cpp
// Change to pimpleFoam
// In controlDict:
ddtSchemes { default backward; }
// In fvSolution:
PIMPLE { nOuterCorrectors 2; }
```

**3. Add turbulence:**
```bash
# Switch to kOmegaSST model
# In constant/turbulenceProperties:
simulationType  RAS;
RAS
{
    RASModel        kOmegaSST;
    turbulence      on;
}
```

**4. Heat transfer:**
```bash
# Use buoyantSimpleFoam
# Add temperature BCs (see Part 2)
# Monitor Nusselt number
```

---

## Summary Checklist

- [ ] Mesh generated with `blockMesh`
- [ ] Mesh quality OK (`checkMesh`)
- [ ] Boundary conditions defined (U, p, T)
- [ ] Schemes configured (`fvSchemes`)
- [ ] Solvers configured (`fvSolution`)
- [ ] Simulation converges (residuals < 1e-5)
- [ ] Recirculation zone observed
- [ ] Reattachment length measured
- [ ] Results validated against literature

**Expected completion time:** 2-3 hours

**Learning outcomes:**
- Complete OpenFOAM case setup workflow
- Boundary condition selection
- Scheme selection for laminar flow
- Convergence monitoring
- Validation against benchmark data
</details>

---

## Additional Resources

### Cross-References

- **Mesh fundamentals:** [02_Fundamental_Concepts.md](02_Fundamental_Concepts.md)
- **Spatial discretization:** [03_Spatial_Discretization.md](03_Spatial_Discretization.md)
- **Temporal discretization:** [04_Temporal_Discretization.md](04_Temporal_Discretization.md)
- **OpenFOAM implementation:** [06_OpenFOAM_Implementation.md](06_OpenFOAM_Implementation.md)
- **Troubleshooting:** [07_Best_Practices.md](07_Best_Practices.md)

### External References

1. **OpenFOAM User Guide:** Section 4 - Mesh generation and boundary conditions
2. **Jasak's PhD Thesis:** Chapter 3 - Finite Volume discretization
3. **Ferziger & Peric:** Computational Methods for Fluid Dynamics - Chapter 6-8

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [07_Best_Practices.md](07_Best_Practices.md) — Best Practices
- **กลับไปที่:** [00_Overview.md](00_Overview.md) — Module Overview