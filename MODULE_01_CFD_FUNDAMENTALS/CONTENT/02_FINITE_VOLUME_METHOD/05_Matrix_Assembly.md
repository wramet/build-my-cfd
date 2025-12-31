# Matrix Assembly and Linear Solvers

กระบวนการแปลง PDE → ระบบสมการเชิงเส้น $[A][\phi] = [b]$

> **ทำไมต้องสนใจ Matrix Assembly?**
> - **Debug ได้ถูกจุด:** เข้าใจ matrix = เข้าใจว่า discretization scheme ทำงานอย่างไร
> - **แก้ปัญหา divergence:** รู้ทันทีว่า diagonal dominance หายไปไหน
> - **เลือก solver ได้เหมาะสม:** แต่ละ equation ต้องการ solver ที่ต่างกัน
> - **ปรับ performance:** ทราบว่า tolerance/relaxation ส่งผลอย่างไร
> - **Custom source terms:** เขียน semi-implicit source ได้ถูกต้อง
> - **fvm vs fvc mastery:** เข้าใจว่าอะไรควรเป็น implicit หรือ explicit

---

## Prerequisites

⚠️ **ควรอ่านก่อน:**
- [02_Fundamental_Concepts.md](02_Fundamental_Concepts.md) — FVM Theory Foundation และ general transport equation
- [03_Spatial_Discretization.md](03_Spatial_Discretization.md) — Diffusion/Convection coefficients และ non-orthogonal correction
- [04_Temporal_Discretization.md](04_Temporal_Discretization.md) — Temporal contribution และ CFL

---

## Learning Objectives

หลังจากอ่านบทนี้ คุณจะสามารถ:
- **คำนวณ** coefficient แต่ละตัวใน matrix ($a_P$, $a_N$, $b_P$) จาก discretization terms ทุกประเภท
- **อธิบาย** โครงสร้าง sparse matrix และทำไม OpenFOAM เลือกใช้ LDU format
- **เลือก** linear solver ที่เหมาะสมกับแต่ละประเภทสมการ (GAMG vs PBiCGStab)
- **แก้ปัญหา** matrix instability และ solver divergence อย่างเป็นระบบ
- **ปรับแต่ง** relaxation factors, tolerance, และ solver settings อย่างมีหลักการ
- **เขียน** semi-implicit source terms ที่ stable
- **แยกแยะ** ได้อย่างชัดเจนว่าควรใช้ `fvm::` หรือ `fvc::` สำหรับแต่ละ term

---

## Part 1: Matrix Assembly Overview

### 1.1 หนึ่ง Cell = หนึ่งสมการ

หลัง Discretization ทุก Cell จะได้สมการ:

$$a_P \phi_P + \sum_{N} a_N \phi_N = b_P$$

> **💡 คิดแบบนี้:**
> แต่ละ cell มี "สมการตัวเอง" ที่บอกว่า:
> "ค่าที่ฉัน ($\phi_P$) ขึ้นกับค่าที่เพื่อนบ้าน ($\phi_N$) และ sources ($b_P$)"

เมื่อรวมทุก Cell → ได้ระบบ:

$$[A][\phi] = [b]$$

| Component | มาจาก | ทำไมสำคัญ | ลักษณะ |
|-----------|-------|----------|---------|
| $a_P$ (Diagonal) | ddt, diffusion, convection, source | ต้องใหญ่พอ → stability | ติดบวก, ใหญ่สุด |
| $a_N$ (Off-diagonal) | diffusion, convection ที่ Neighbors | เชื่อม cells เข้าด้วยกัน | ติดลบ (diffusion) หรือผสม (convection) |
| $b_P$ (Source/RHS) | Explicit terms, BCs, old time values | "ข้อมูลที่รู้แล้ว" | Known values |

### 1.2 Diagonal Dominance: Key to Stability

**Definition:** สมการมี diagonal dominance ถ้า:

$$|a_P| \geq \sum_{N} |a_N|$$

> **⚠️ Critical:** Diagonal dominance เป็นเงื่อนไข **สำคัญที่สุด** สำหรับ convergence ของ iterative solvers

**ทำไมสำคัญ:**
- Guarantees solver converge (สำหรับ M-matrices)
- ลด oscillation ใน solution
- เพิ่ม robustness ของ nonlinear iteration
- เป็นเป้าหมายของ relaxation strategies

**Visualizing Diagonal Dominance:**

```
Matrix [A] สำหรับ 3-cell system:
┌─────────────────────────────────────┐
│ a_P₁  a_N₁→₂  a_N₁→₃ │   Row 1: |a₁| ≥ |a₁₂| + |a₁₃|
│ a_N₂→₁  a_P₂  a_N₂→₃ │   Row 2: |a₂| ≥ |a₂₁| + |a₂₃|
│ a_N₃→₁  a_N₃→₂  a_P₃ │   Row 3: |a₃| ≥ |a₃₁| + |a₃₂|
└─────────────────────────────────────┘

Good Diagonal Dominance:
[ 10.0   -2.0   -1.5 ]  →  |10| > |−2| + |−1.5| = 3.5 ✅
[ -1.5   12.0  -2.0 ]  →  |12| > |−1.5| + |−2| = 3.5 ✅
[ -1.0   -1.8   9.0 ]  →  |9| > |−1| + |−1.8| = 2.8 ✅

Poor Diagonal Dominance (UNSTABLE):
[ 2.0   -1.5   -1.0 ]  →  |2| < |−1.5| + |−1| = 2.5 ❌
[ -1.2   1.8   -1.0 ]  →  |1.8| < |−1.2| + |−1| = 2.2 ❌
```

---

## Part 2: Sparse Matrix Structure - Visualized

### 2.1 ทำมาที่ไหน?

Matrix $[A]$ มีโครงสร้าง **Sparse** เพราะ:
- แต่ละ Cell เชื่อมต่อกับ **Neighbors เท่านั้น** (ไม่ใช่ทุก Cell)
- Non-zero entries ≈ 6-20 ต่อแถว (3D hexahedral mesh)
- Storing only non-zeros → memory O(N) แทน O(N²)

### 2.2 ASCII Visualization: 1D Mesh

```
1D Mesh Example (5 cells):
┌─────┬─────┬─────┬─────┬─────┐
│  0  │  1  │  2  │  3  │  4  │
└─────┴─────┴─────┴─────┴─────┘
  └───────┘       └───────┘
    neighbors       neighbors

Corresponding Matrix [A] (5×5):
Cell 0: [●    ○    ○    ○    ○ ]   ← Diagonal (a_P) + 1 neighbor (a_N)
Cell 1: [●    ●    ○    ○    ○ ]   ← Diagonal (a_P) + 2 neighbors
Cell 2: [○    ●    ●    ●    ○ ]   ← Diagonal (a_P) + 2 neighbors
Cell 3: [○    ○    ●    ●    ● ]   ← Diagonal (a_P) + 2 neighbors
Cell 4: [○    ○    ○    ●    ● ]   ← Diagonal (a_P) + 1 neighbor

Legend: ● = Non-zero, ○ = Zero (not stored)
```

### 2.3 ASCII Visualization: 2D Structured Mesh

```
5×5 Mesh (25 cells):
    Cell connectivity pattern:
     0───1───2───3───4
     │   │   │   │   │
     5───6───7───8───9
     │   │   │   │   │
    10──11──12──13───14
     │   │   │   │   │
    15──16──17──18───19
     │   │   │   │   │
    20──21──22──23───24

Matrix Structure (25×25):
Row 0:  ● ● ○ ○ ○  ● ○ ○ ○ ○  ○ ○ ○ ○ ○  ○ ○ ○ ○ ○  ○ ○ ○ ○ ○
Row 1:  ● ● ● ○ ○  ○ ● ○ ○ ○  ○ ○ ○ ○ ○  ○ ○ ○ ○ ○  ○ ○ ○ ○ ○
Row 2:  ○ ● ● ● ○  ○ ○ ● ○ ○  ○ ○ ○ ○ ○  ○ ○ ○ ○ ○  ○ ○ ○ ○ ○
Row 6:  ● ○ ○ ○ ○  ● ● ● ○ ○  ● ○ ○ ○ ○  ○ ○ ○ ○ ○  ○ ○ ○ ○ ○
Row 12: ○ ○ ● ○ ○  ○ ● ● ● ○  ○ ● ● ● ○  ○ ○ ○ ○ ○  ○ ○ ○ ○ ○
...
Row 24: ○ ○ ○ ○ ○  ○ ○ ○ ○ ○  ○ ○ ○ ○ ○  ○ ○ ○ ○ ●  ○ ○ ● ● ●

Pattern: Interior cells = 5 non-zeros, Edge cells = 3-4 non-zeros
         Corner cells = 2-3 non-zeros
```

### 2.4 ASCII Visualization: 3D Connectivity

```
3D Hexahedral Mesh (Cell P with 6 neighbors):
              N (top)
               │
               │
    W ──────── P ──────── E
               │
               │
              S (bottom)

     (front/rear faces not shown for clarity)

Matrix [A] for Cell P:
        N  S  E  W  Fr Re  (neighbors)
Row P: [● ● ● ● ● ●]  ← 6 non-zeros + diagonal
        ↓
    Only 7 entries stored out of N_total_cells possible!
```

### 2.5 ทำไม Sparse สำคัญ?

| แง่มุม | Dense Matrix | Sparse Matrix |
|---------|--------------|---------------|
| **Memory** | O(N²) → 1M cells = 10¹² entries ❌ | O(N) → 1M cells = ~6M entries ✅ |
| **Computation** | O(N²) operations | O(N) operations |
| **Speed** | ช้ามาก | เร็วมาก (iterative solvers) |
| **Format** | 2D array | CSR, CSC, LDU (OpenFOAM) |

**Memory Comparison Example:**

```
Problem: 1 million cells (1,000,000)

Dense Matrix Storage:
- Size: N² = (10⁶)² = 10¹² entries
- Assuming double precision (8 bytes): 8 × 10¹² bytes = 8 TB ❌

Sparse Matrix Storage (LDU):
- Non-zeros per cell ≈ 7 (1 diagonal + 6 neighbors)
- Total: 7 × 10⁶ entries
- Memory: 7 × 10⁶ × 8 bytes = 56 MB ✅

Savings: 8 TB → 56 MB = 142,857× less memory!
```

### 2.6 OpenFOAM's LDU Format

OpenFOAM ใช้ **LDU (Lower-Diagonal-Upper)** format:

```cpp
// LDU Storage for a mesh with N cells
scalarField L;    // Lower triangular coefficients (owner→neighbour)
scalarField D;    // Diagonal coefficients
scalarField U;    // Upper triangular coefficients (neighbour→owner)

labelList l;      // Addressing: L[i] connects cell owner[i] to neighbour[i]
labelList u;      // Addressing: U[i] connects cell owner[i] to neighbour[i]
```

**Memory Layout:**

```
Cell Connectivity:
    Owner cells:  [0, 0, 1, 1, 2, ...]
    Neighbour:    [1, 3, 2, 4, 5, ...]

Coefficients (size = nFaces):
    Lower:  [L₀, L₁, L₂, L₃, L₄, ...]  // Owner→Neighbour
    Upper:  [U₀, U₁, U₂, U₃, U₄, ...]  // Neighbour→Owner (Lᵢ = Uᵢ for symmetric)
    Diagonal: [D₀, D₁, D₂, D₃, ...]    // size = nCells
```

**Example: 2D Mesh (4 cells)**

```
Mesh:
┌───┬───┐
│ 0 │ 1 │
├───┼───┤
│ 2 │ 3 │
└───┴───┘

Faces:
- Face 0: between cell 0 (owner) and cell 1 (neighbour)
- Face 1: between cell 0 (owner) and cell 2 (neighbour)
- Face 2: between cell 1 (owner) and cell 3 (neighbour)
- Face 3: between cell 2 (owner) and cell 3 (neighbour)

LDU Storage:
owner:     [0, 0, 1, 2]
neighbour: [1, 2, 3, 3]
Lower:     [L₀, L₁, L₂, L₃]  // 4 entries (one per face)
Upper:     [U₀, U₁, U₂, U₃]  // 4 entries (one per face)
Diagonal:  [D₀, D₁, D₂, D₃]  // 4 entries (one per cell)

Matrix [A]:
┌─────────────────┐
│ D₀   U₀   L₁   0 │  Row 0
│ L₀   D₁    0   U₂│  Row 1
│ L₁    0   D₂   U₃│  Row 2
│  0   L₂   L₃   D₃│  Row 3
└─────────────────┘
```

**Advantages:**
- เก็บเฉพาะ non-zeros → memory efficient
- Symmetric matrix: L = U (เก็บชุดเดียว)
- ออกแบบมาสำหรับ FVM connectivity
- รวดเร็วสำหรับ matrix-vector multiplication

> **💡 นั่นคือเหตุผล:** OpenFOAM ใช้ iterative solvers (GAMG, PBiCGStab) ไม่ใช่ direct solvers (LU, QR)

---

## Part 3: Coefficient Calculations - Complete Guide

### 3.1 สรุป: Term → Coefficient Mapping

| Term | $a_P$ (Diagonal) | $a_N$ (Off-diagonal) | $b_P$ (Source) | Stability Effect |
|------|-----------------|---------------------|---------------|------------------|
| **Temporal** | $+\frac{\rho V}{\Delta t}$ | — | $+\frac{\rho V}{\Delta t} \phi^n$ | ✅ เพิ่ม diagonal dominant |
| **Diffusion** | $-\sum a_N$ | $-\frac{D_f A_f}{d_{PN}}$ | — | ✅ สร้าง diagonal dominant |
| **Convection** | $-\sum a_N$ | Upwind: $\max(-\Phi_f, 0)$ | — | ⚠️ อาจลด diagonal dominant |
| **Source (explicit)** | — | — | $S_u V$ | ⚠️ ไม่มีผลต่อ diagonal |
| **Source (implicit)** | $+S_p V$ | — | $S_u V$ | ✅ เพิ่ม diagonal (ถ้า $S_p < 0$) |

### 3.2 Temporal Term (Implicit Euler)

$$\frac{\partial \phi}{\partial t} \rightarrow a_P += \frac{\rho V}{\Delta t}, \quad b_P += \frac{\rho V}{\Delta t} \phi^n$$

**ทำมาจากไหน?** ดู [04_Temporal_Discretization.md](04_Temporal_Discretization.md) สำหรับ temporal schemes

**ทำไมช่วย Stability?**
- เพิ่ม $\frac{\rho V}{\Delta t}$ เข้า diagonal → diagonal ใหญ่ขึ้น
- $\Delta t$ เล็ก → contribution มาก → stable มากขึ้น
- นี่คือเหตุผลว่าทำไม **ลด $\Delta t$ ช่วยแก้ divergence**

#### 3.2.1 ตัวอย่างการคำนวณ (Step-by-Step)

**Problem:** 1D transient heat conduction

สมมติ:
- $\rho = 1000$ kg/m³
- $V = 0.001$ m³ (cell volume)
- $\Delta t = 0.01$ s
- $\phi^n = 300$ K (old time value)

**Step 1: คำนวณ temporal coefficient**
$$a_P^{temp} = \frac{\rho V}{\Delta t} = \frac{1000 \times 0.001}{0.01} = 100$$

**Step 2: คำนวณ source contribution**
$$b_P^{temp} = a_P^{temp} \times \phi^n = 100 \times 300 = 30000$$

→ Temporal term เพิ่ม diagonal 100 (ช่วย stability มาก!)

#### 3.2.2 Temporal Contribution สำหรับ Schemes ต่างๆ

| Scheme | $a_P$ Contribution | $b_P$ Contribution | Stability |
|--------|-------------------|-------------------|-----------|
| **Euler (1st)** | $\frac{\rho V}{\Delta t}$ | $\frac{\rho V}{\Delta t} \phi^n$ | ✅ สูงมาก |
| **backward (2nd)** | $\frac{3\rho V}{2\Delta t}$ | $\frac{4\rho V}{2\Delta t} \phi^n - \frac{\rho V}{2\Delta t} \phi^{n-1}$ | ✅ สูง |
| **Crank-Nicolson** | $\frac{\rho V}{2\Delta t}$ | $\frac{\rho V}{2\Delta t} \phi^n$ + explicit terms | ⚠️ ปานกลาง |

> **Note:** backward scheme ให้ diagonal contribution มากกว่า Euler → stable กว่า

#### 3.2.3 Visualizing Temporal Contribution

```
Effect of Δt on Diagonal Dominance:

┌─────────────────────────────────────────────────────────────┐
│                    Temporal Contribution to a_P             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  a_P contribution                                            │
│     ↑                                                        │
│ 1000─┤           ● (Δt = 0.001 s)                            │
│      │           :  Very high diagonal → Very stable        │
│  500─┤       ●   :                                          │
│      │       :   :  (Δt = 0.002 s)                          │
│  100─┤   ●   :   :  Good diagonal → Stable                  │
│      │   :   :   :                                          │
│   50─┤ ● :   :   :  (Δt = 0.02 s)                           │
│      │ : :   :   :  Low diagonal → May be unstable          │
│   10─┼─┼┼───┼───┼───→ Δt                                    │
│      └───────────────────────────────                       │
│        0.001  0.01   0.1    1.0                             │
│                                                             │
│ Rule: Δt ↓ = a_P ↑ = Stability ↑                            │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 Diffusion Term (Central Difference)

$$\nabla \cdot (D \nabla \phi) \rightarrow a_N = -\frac{D_f A_f}{d_{PN}}, \quad a_P = -\sum_N a_N$$

**ทำมาจากไหน?** ดู [03_Spatial_Discretization.md](03_Spatial_Discretization.md) สำหรับ non-orthogonal correction

#### 3.3.1 ตัวอย่างการคำนวณ (Step-by-Step)

**Problem:** 2D steady-state heat conduction ใน Cell P ที่มี 4 neighbors

```
       N (d = 0.01 m, T = 310 K)
       |
       |  D = 50 W/m·K
       |
W ----- P ----- E  (d = 0.01 m each)
       |         T = 290 K
       |
       S (T = 285 K)

Cell P: T = 300 K (initial guess)
- Face area A_f = 0.01 m² (ทุก face)
- Distance d_PN = 0.01 m (ทุก neighbor)
```

**Step 1: คำนวณ $a_N$ สำหรับแต่ละ neighbor**

$$a_N = -\frac{D A_f}{d_{PN}} = -\frac{50 \times 0.01}{0.01} = -50$$

→ ทุก neighbor ได้ $a_N = -50$ (ติดลบเสมอสำหรับ diffusion!)

**Step 2: คำนวณ $a_P$**

$$a_P^{diff} = -\sum_N a_N = -(-50 - 50 - 50 - 50) = 200$$

**Step 3: ตรวจสอบ Diagonal Dominance**

$$|a_P| = 200 > \sum |a_N| = 4 \times 50 = 200$$

→ Borderline diagonal dominant ($|a_P| = \sum |a_N|$)

**ทำไม Diffusion ดีสำหรับ Stability?**
- $a_N < 0$ เสมอ (ติดลบ)
- $a_P = -\sum a_N > 0$ (เป็นบวก)
- → **Diagonal Dominant** → Stable!

#### 3.3.2 Non-Orthogonal Correction Effect

เมื่อ mesh ไม่ orthogonal → diffusion term แตกเป็น 2 ส่วน:

**Explicit correction:**
$$a_P^{orth} = -\sum a_N^{orth}$$
$$b_P^{correct} = \sum D_f (\nabla \phi)_f \cdot \mathbf{k}$$

→ Correction term ไปที่ RHS → **ลด stability** ถ้ามุมเบี่ยงเบนมาก

**Implicit correction:**
- เพิ่ม iteration ภายใน time step (`nNonOrthogonalCorrectors`)
- ทำให้ solution converge ช้าลง

**Visualizing Non-Orthogonal Mesh Effect:**

```
Orthogonal Mesh (θ = 0°):
    Cell P         Cell N
      ●─────────────●
      │             │
      d_PN ⟂ S_f    │

Matrix contribution:
- a_N = -DA/d (simple)
- No correction needed

Non-Orthogonal Mesh (θ = 60°):
    Cell N
      ●
     ╱  │
    ╱   │d
   ╱ θ  │
  ●─────■
Cell P  Face

Matrix contribution:
- a_N = -DA/d (orthogonal part)
- b_P += D·(∇φ)·k (correction to RHS)
→ Less stable, needs more iterations
```

### 3.4 Convection Term (Upwind Scheme)

$$\nabla \cdot (\phi \mathbf{u}) \rightarrow a_N = \max(-\Phi_f, 0)$$

โดย $\Phi_f = \mathbf{u}_f \cdot \mathbf{S}_f$ (face flux)

**ทำมาจากไหน?** ดู [03_Spatial_Discretization.md](03_Spatial_Discretization.md) สำหรับ convection schemes

#### 3.4.1 ตัวอย่างการคำนวณ (Step-by-Step)

**Problem:** 1D convection ของ scalar T ไปทางบวก

```
Flow direction: →

    W       P       E
    ●───────■───────●
   T_W     T_P     T_E
           ↑
    Face f (between P and E)

Given:
- u_f = 10 m/s (velocity at face)
- A_f = 0.01 m² (face area)
- Flow ไปทางบวก (จาก W → P → E)
```

**Step 1: คำนวณ Face Flux**

$$\Phi_f = u_f A_f = 10 \times 0.01 = 0.1 \text{ m³/s}$$

**Step 2: คำนวณ $a_N$ สำหรับแต่ละ neighbor**

สำหรับ upwind:
- ถ้า $\Phi_f > 0$ (flow ไปทางบวก): ใช้ค่า upstream (W สำหรับ face W-P, P สำหรับ face P-E)
- ถ้า $\Phi_f < 0$ (flow ไปทางลบ): ใช้ค่า upstream (P สำหรับ face W-P, E สำหรับ face P-E)

**สำหรับ Cell P:**
- Face ด้านซ้าย (W-P): $\Phi_f > 0$ → information มาจาก W → $a_W = \Phi_f = 0.1$
- Face ด้านขวา (P-E): $\Phi_f > 0$ → information ไปที่ E → $a_E = \max(-0.1, 0) = 0$

$$a_W^{conv} = 0.1, \quad a_E^{conv} = 0$$

**Step 3: คำนวณ $a_P$**

$$a_P^{conv} = -\sum_N a_N = -(0.1 + 0) = -0.1$$

⚠️ **Problem:** $a_P = -0.1$ (ติดลบ!) → Unstable!

**แก้ไข:** ต้องเพิ่ม temporal term หรือ diffusion term เพื่อให้ $a_P > 0$

#### 3.4.2 Convection Schemes และผลต่อ Matrix

| Scheme | $a_N$ Formula | Diagonal Effect | Boundedness |
|--------|--------------|-----------------|-------------|
| **Upwind** | $\max(-\Phi_f, 0)$ | Moderate | ✅ Bounded |
| **Linear** | $\alpha \Phi_f$ (symmetric) | May reduce dominance | ❌ Unbounded |
| **Linear Upwind** | Upwind + gradient correction | Better accuracy | ✅ Bounded |
| **TVD/Limited** | Blended with limiter | Adaptive | ✅ Bounded |

**Practical Rule:** เมื่อใช้ higher-order schemes → ลด relaxation เพื่อรักษา stability

**Visualizing Convection Scheme Effects:**

```
Upwind Scheme (Flow →):
    W       P       E
    ●───────■───────●
   T_W     T_P     T_E

Face W-P: Φ_f > 0 → use T_W
    a_W = +Φ_f (positive!)
    a_P contribution = -Φ_f (negative!)

Face P-E: Φ_f > 0 → use T_P
    a_E = 0 (no dependence on E)
    a_P contribution = 0

Result: a_P may become negative → UNSTABLE without temporal/diffusion
```

### 3.5 Combined Example: Convection-Diffusion with Temporal

**Problem:** 1D transient convection-diffusion ของ T

```
    W       P       E
    ●───────■───────●
   T_W     T_P     T_E

Given:
- u = 1 m/s, A = 0.01 m²
- D = 0.1 m²/s, d = 0.01 m
- ρ = 1000 kg/m³, V = 0.001 m³
- Δt = 0.01 s
- T_W = 100°C, T_E = 50°C, T_Pⁿ = 75°C
```

**Step 1: Temporal Contribution**

$$a_P^{temp} = \frac{\rho V}{\Delta t} = \frac{1000 \times 0.001}{0.01} = 100$$
$$b_P^{temp} = a_P^{temp} \times T_P^n = 100 \times 75 = 7500$$

**Step 2: Convection Contribution (Upwind)**

$$\Phi_f = u A = 1 \times 0.01 = 0.01$$

$$a_W^{conv} = \Phi_f = 0.01$$
$$a_E^{conv} = \max(-\Phi_f, 0) = 0$$
$$a_P^{conv} = -0.01$$

**Step 3: Diffusion Contribution (Central)**

$$a_N^{diff} = -\frac{D A}{d} = -\frac{0.1 \times 0.01}{0.01} = -0.1$$

$$a_W^{diff} = -0.1$$
$$a_E^{diff} = -0.1$$
$$a_P^{diff} = -(-0.1 - 0.1) = 0.2$$

**Step 4: Combine All**

$$a_W = 0.01 - 0.1 = -0.09$$
$$a_E = 0 - 0.1 = -0.1$$
$$a_P = 100 - 0.01 + 0.2 = 100.19$$
$$b_P = 7500$$

**Step 5: Check Diagonal Dominance**

$$|a_P| = 100.19, \quad \sum |a_N| = |-0.09| + |-0.1| = 0.19$$

→ **Very diagonal dominant!** (Ratio = 0.19/100.19 = 0.002)

**Step 6: Solve**

$$100.19 T_P - 0.09 T_W - 0.1 T_E = 7500$$

$$T_P = \frac{7500 + 0.09 \times 100 + 0.1 \times 50}{100.19} = 75.3°C$$

→ Temporal term ช่วยให้ stable มาก!

**Visualizing Combined Contributions:**

```
Coefficient Contributions to Cell P:
┌────────────────────────────────────────────────────┐
│                                                    │
│  a_P = 100.19                                      │
│    ↑                                               │
│    │  ┌────────────────────┐                       │
│    │  │ Temporal:   +100.00│ (98.9% - Dominant!)  │
│    │  │ Diffusion:   +0.20 │ (0.2%)               │
│    │  │ Convection:  -0.01 │ (0.01% - negative!)  │
│    │  └────────────────────┘                       │
│                                                    │
│  Off-diagonals:                                   │
│    a_W = -0.09 (convection + diffusion)            │
│    a_E = -0.10 (diffusion only)                    │
│                                                    │
│  Diagonal Dominance Ratio: 0.19/100.19 = 0.002     │
│  → Very stable!                                    │
└────────────────────────────────────────────────────┘
```

---

## Part 4: fvm vs fvc - The Critical Distinction

### 4.1 ความแตกต่างที่สำคัญที่สุด

| Prefix | ชื่อเต็ม | ผลลัพธ์ | ใช้เมื่อ | Matrix Effect |
|--------|---------|---------|---------|---------------|
| `fvm::` | Finite Volume Method | → Matrix ($a_P$, $a_N$) | Unknown (กำลังหา) | ✅ เพิ่ม coefficients |
| `fvc::` | Finite Volume Calculus | → Field (ตัวเลขทันที) | Known (รู้ค่าแล้ว) | ❌ ไปที่ RHS ($b_P$) |

> **ทำไมต้องแยก?**
> - **fvm:** $\phi$ ยังไม่รู้ → ต้องเก็บเป็น coefficient ใน matrix
> - **fvc:** $\phi$ รู้แล้ว → คำนวณเป็นตัวเลขได้เลย → ใส่ source

### 4.2 Decision Tree: fvm or fvc?

```
Is this variable being solved in the current equation?
│
├─ YES → Use fvm:: (implicit, builds matrix)
│         └─ Example: fvm::ddt(U), fvm::div(phi, U)
│
└─ NO  → Use fvc:: (explicit, goes to RHS)
          └─ Example: fvc::grad(p), fvc::curl(U)
```

### 4.3 ตัวอย่าง: Momentum Equation

$$\rho\frac{\partial \mathbf{u}}{\partial t} + \nabla \cdot (\rho \mathbf{u} \mathbf{u}) = -\nabla p + \nabla \cdot (\mu \nabla \mathbf{u})$$

```cpp
fvVectorMatrix UEqn
(
    fvm::ddt(rho, U)              // U ไม่รู้ → เข้า Diagonal (a_P += ρV/Δt)
  + fvm::div(phi, U)              // U ไม่รู้ → เข้า Diagonal + Off-diagonal
  - fvm::laplacian(mu, U)         // U ไม่รู้ → เข้า Diagonal + Off-diagonal
 ==
    -fvc::grad(p)                 // p รู้แล้ว → คำนวณเป็น Source vector
);
```

**ทำไม `fvc::grad(p)`?**
- p มาจาก pressure correction (SIMPLE/PISO) = รู้ค่าแล้วจาก iteration ก่อนหน้า
- ใส่เป็น explicit source ใน RHS
- ไม่สามารถใช้ `fvm::grad(p)` เพราะ gradient operator ไม่สร้าง symmetric matrix

### 4.4 Matrix Implications Summary

| Operator | fvm:: (Implicit) | fvc:: (Explicit) | Matrix Effect |
|----------|------------------|------------------|---------------|
| `ddt(ρ, φ)` | ✅ | ✅ | fvm: $a_P += \frac{\rho V}{\Delta t}$, $b_P += \frac{\rho V}{\Delta t} \phi^n$ |
| `div(φ, U)` | ✅ | ✅ | fvm: $a_P, a_N$ เพิธ, fvc: คำนวณเป็นเลข |
| `laplacian(Γ, φ)` | ✅ | ✅ | fvm: $a_P, a_N$ เพิธ, fvc: คำนวณเป็นเลข |
| `grad(φ)` | ❌ | ✅ | **ไม่มี fvm::grad** — gradient ไม่สร้าง symmetric matrix |
| `curl(φ)` | ❌ | ✅ | **ไม่มี fvm::curl** — เหมือนกัน |
| `div(φ)` | ❌ | ✅ | fvc ใช้คำนวณ divergence ของ known flux field |

> **⚠️ หมายเหตุ:** ไม่มี `fvm::grad()` เพราะ $\nabla \phi$ ไม่ linearize กับ $\phi$ ได้ดี และไม่ได้สร้าง M-matrix

### 4.5 When to Use Which?

```cpp
// ✅ CORRECT: fvm for unknown, fvc for known
fvScalarMatrix TEqn
(
    fvm::ddt(T)              // Unknown: T
  + fvm::div(phi, T)         // Unknown: T
  - fvm::laplacian(k, T)     // Unknown: T
 ==
    fvc::div(phi, T_old)     // Known: T_old (explicit convection for test)
);

// ❌ WRONG: fvc for unknown (unstable!)
fvScalarMatrix TEqn
(
    fvc::ddt(T)              // Bad! No matrix for time derivative
  + fvc::div(phi, T)         // Bad! No matrix for convection
);

// ⚠️ CONTEXT-DEPENDENT: Pressure in momentum equation
// In SIMPLE/PISO algorithms:
fvVectorMatrix UEqn
(
    fvm::ddt(U)
  + fvm::div(phi, U)
  - fvm::laplacian(nu, U)
 ==
    -fvc::grad(p)  // p is "known" from previous corrector iteration
);
```

### 4.6 Performance Implications

| Approach | Matrix Size | Solver Cost | Stability | ใช้เมื่อ |
|----------|-------------|-------------|-----------|----------|
| **All fvm** | เต็ม | สูง | สูง | Coupled solvers |
| **Mixed fvm/fvc** | ปานกลาง | ปานกลาง | ปานกลาง | Segregated (SIMPLE/PISO) |
| **All fvc** | ไม่มี | ต่ำ | ต่ำมาก | Explicit methods |

---

## Part 5: Boundary Conditions - Matrix Effects

### 5.1 ประเภท BC และผลต่อ Coefficients

| BC Type | ความหมาย | ผลต่อ $a_P$ | ผลต่อ $a_N$ | ผลต่อ $b_P$ | OpenFOAM |
|---------|-----------|-------------|-------------|-------------|----------|
| **fixedValue** | Dirichlet: ค่าคงที่ | แก้ไข | ลบ neighbor | เพิ่มค่า BC | `fixedValue` |
| (Dirichlet) | $\phi = \phi_{bc}$ | $a_P \leftarrow \sum a_N$ | 0 | $b_P += \sum a_N \phi_{bc}$ | |
| **zeroGradient** | Neumann: gradient = 0 | — | — | — | `zeroGradient` |
| (Neumann) | $\partial \phi / \partial n = 0$ | ไม่เปลี่ยน | ไม่มี off-diag | ไม่เปลี่ยน | |
| **mixed** | ผสม Dirichlet + Neumann | แก้ไข | แก้ไข | เพิ่มค่า BC | `mixed` |
| **calculated** | คำนวณจาก BC อื่น | — | — | — | `calculated` |
| **fixedFluxPressure** | Fixed gradient | แก้ไข | — | เพิ่มค่า BC | `fixedFluxPressure` |
| **codedFixedValue** | User-coded | แก้ไข | ลบ neighbor | เพิ่มค่า BC | `codedFixedValue` |

### 5.2 ตัวอย่าง: fixedValue

**Physical:** Inlet velocity U = (10 0 0) m/s

```cpp
// 0/U
boundaryField
{
    inlet
    {
        type    fixedValue;
        value   uniform (10 0 0);
    }
}
```

**Matrix Effect (Implicit):**

ก่อน BC (interior cell):
$$a_P U_P + a_W U_W + a_E U_E = b_P$$

หลัง BC (neighbor W เป็น boundary):
- $U_W$ ถูกกำหนด = 10 m/s → move to RHS
- $a_W \leftarrow 0$ (ไม่มี off-diagonal)
- $a_P \leftarrow a_P + a_W$ (diagonal ใหญ่ขึ้น)
- $b_P \leftarrow b_P + a_W \times 10$ (BC contribution)

$$a_P' U_P + a_E U_E = b_P'$$

โดยที่:
- $a_P' = a_P + a_W$
- $b_P' = b_P + a_W \times 10$

**Visualizing fixedValue BC Effect:**

```
Before BC (interior cell with neighbor W):
┌─────────────────────────────────────────┐
│ Row P:  [a_W]  [a_P]      [a_E]  [b_P] │
│         ●      ●          ●      ●     │
│                                          │
│ Equation: a_W·U_W + a_P·U_P + a_E·U_E = b_P│
└─────────────────────────────────────────┘

After BC (W is fixedValue boundary):
┌─────────────────────────────────────────┐
│ Row P:  [0]    [a_P+a_W]   [a_E]  [b_P']│
│         ○      ●          ●      ●     │
│                                          │
│ Equation: (a_P+a_W)·U_P + a_E·U_E =      │
│           b_P + a_W·U_W_BC               │
│                                          │
│ Effect:                                  │
│ • Diagonal INCREASED (more stable!)      │
│ • Off-diagonal REMOVED (fewer couplings) │
└─────────────────────────────────────────┘
```

### 5.3 ตัวอย่าง: zeroGradient

**Physical:** Outlet — ปล่อยไหลอิสระ

```cpp
// 0/T
boundaryField
{
    outlet
    {
        type            zeroGradient;
    }
}
```

**Matrix Effect:**

- $\partial T / \partial n = 0$ → $T_{boundary} = T_P$ → ไม่ต้องเพิ่ม term
- Off-diagonal ที่ boundary ถูกลบออก
- Diagonal ไม่เปลี่ยน

### 5.4 BC Impact on Diagonal Dominance

| BC Type | Effect on Diagonal | Stability Impact |
|---------|-------------------|------------------|
| **fixedValue** | ✅ เพิ่ม ($a_P += \sum a_N$) | **Improves** |
| **zeroGradient** | — ไม่เปลี่ยน | Neutral |
| **mixed** | ⚠️ ขึ้นกับ weight | Variable |
| **inletOutlet** | ⚠️ ขึ้นกับ flow direction | Variable |

> **💡 Key Insight:** fixedValue BC เพิ่ม diagonal dominant (ดีสำหรับ stability) แต่ zeroGradient ไม่เปลี่ยน matrix

### 5.5 BC Implementation in OpenFOAM Matrix

```cpp
// ใน fvMatrix assembly, fixedValue BC จะถูกจัดการดังนี้:
// 1. Internal coefficients ถูกคำนวณปกติ
// 2. BC entries ถูกแก้ไข:

// Before BC (internal face):
// a_P[owner] += coeff
// a_N[owner] += coeff

// After BC (boundary face with fixedValue):
// a_P[owner] += coeff      // Diagonal increases
// a_N[owner] = 0           // Off-diagonal removed
// b_P[owner] += coeff * value_bc  // BC value added to RHS
```

---

## Part 6: Source Terms - Explicit vs Semi-Implicit

### 6.1 Explicit Source (พื้นฐาน)

```cpp
fvScalarMatrix TEqn
(
    fvm::ddt(T)
  + fvm::div(phi, T)
  - fvm::laplacian(k, T)
 ==
    Q   // Heat source (explicit)
);
```

**Matrix Effect:** Q ไปที่ RHS ($b_P$) เท่านั้น

$$a_P T_P + \sum a_N T_N = b_P + Q V$$

**ข้อเสีย:** ไม่เพิ่ม diagonal → ลด stability

### 6.2 Semi-Implicit Source (แนะนำ!)

$$S = S_u + S_p \cdot \phi$$

โดยที่:
- $S_u$ = explicit part (ไป RHS)
- $S_p$ = implicit coefficient (ไป diagonal)

```cpp
fvScalarMatrix TEqn
(
    fvm::ddt(T)
  + fvm::div(phi, T)
  - fvm::laplacian(k, T)
 ==
    Su                       // Explicit part → b_P
  + fvm::Sp(Sp, T)          // Implicit part → a_P
);
```

**Matrix Effect:**

$$a_P' T_P + \sum a_N T_N = b_P'$$

โดยที่:
- $a_P' = a_P - S_p V$ (ลบ because $S_p T_P$ ถูกย้ายไป LHS)
- $b_P' = b_P + S_u V$

### 6.3 ตัวอย่าง: Heat Generation with Temperature Dependence

**Problem:** Chemical reaction สร้างความร้อน $S = Q_0 - k T$

- $Q_0 = 1000$ W/m³ (constant heat generation)
- $k = 10$ W/m³K (temperature-dependent loss)
- $V = 0.001$ m³

**Explicit source (ไม่ดี):**

```cpp
volScalarField Q = 1000 - 10*T;

fvScalarMatrix TEqn
(
    fvm::ddt(T) - fvm::laplacian(k, T) == Q
);
```

→ $Q$ ถูกคำนวณจาก $T$ รอบก่อน → **unstable** ถ้า $Q$ ใหญ่

**Semi-implicit source (ดี):**

```cpp
fvScalarMatrix TEqn
(
    fvm::ddt(T) - fvm::laplacian(k, T)
 ==
    1000                   // Su = 1000
  - fvm::Sp(10, T)        // Sp = -10 (implicit)
);
```

**Matrix Effect:**

$$a_P' = a_P - (-10) V = a_P + 10 \times 0.001 = a_P + 0.01$$

→ Diagonal **ใหญ่ขึ้น** → **stable ขึ้น!**

**Visualizing Semi-Implicit Source Effect:**

```
Source Term: S = 1000 - 10·T

Explicit Implementation:
┌────────────────────────────────────────┐
│ Equation: a_P·T_P = b_P + (1000 - 10·T)│
│                                        │
│ Matrix: [a_P] [T_P] = [b_P + 1000]    │
│                        (no -10·T term) │
│                                        │
│ → Diagonal UNCHANGED                   │
│ → May be unstable if source is large   │
└────────────────────────────────────────┘

Semi-Implicit Implementation:
┌────────────────────────────────────────┐
│ Equation: a_P·T_P = b_P + 1000 - 10·T  │
│          (a_P + 10)·T_P = b_P + 1000   │
│                                        │
│ Matrix: [a_P + 10] [T_P] = [b_P + 1000]│
│            ↑                           │
│         Diagonal INCREASED!            │
│                                        │
│ → More STABLE                          │
└────────────────────────────────────────┘
```

### 6.4 ทำไม Semi-Implicit ดีกว่า?

| แง่มุม | Explicit Source | Semi-Implicit Source |
|---------|----------------|---------------------|
| **Stability** | ❌ ไม่เพิ่ม diagonal | ✅ เพิ่ม diagonal (ถ้า $S_p < 0$) |
| **Accuracy** | ⚠️ Depends on $\Delta t$ | ✅ Unconditionally stable |
| **Speed** | ✅ ไม่ต้อง recompute | ⚠️ ต้อง recompute matrix |
| **ใช้เมื่อ** | Sources เล็กๆ | Sources ใหญ่หรือมี $S_p \phi$ |

**Rule:** ถ้า source มี term ที่ proportional กับ $\phi$ → ใช้ `fvm::Sp()`!

### 6.5 OpenFOAM Source Functions

| Function | Purpose | Matrix Effect |
|----------|---------|---------------|
| `fvm::Sp(ρ, φ)` | Semi-implicit source coefficient | เพิ่ม diagonal |
| `fvm::Su(Su, φ)` | Explicit source (same as just Su) | RHS only |
| `fvOptions(φ)` | Framework for sources | Depends on option |

---

## Part 7: Linear Solvers - Selection and Tuning

### 7.1 Solver Selection Guide

| Solver | Matrix Type | ใช้กับ | Algorithm | Speed | Stability | Memory |
|--------|-------------|--------|-----------|-------|-----------|--------|
| **GAMG** | Symmetric | p (pressure), T (diffusion-dominated) | Multigrid | ⚡⚡⚡ เร็วมาก | ✅ ดี | ต่ำ |
| **PCG** | Symmetric PD | p (alternative), diffusion | Conjugate Gradient | ⚡⚡ เร็ว | ✅ ดีมาก | ต่ำ |
| **PBiCGStab** | Asymmetric | U, k, ε, ω | Stabilized Bi-CG | ⚡ ปานกลาง | ✅ ดี | ปานกลาง |
| **smoothSolver** | Any | เล็ก/ง่าย | Gauss-Seidel | 🐢 ช้า | ✅ ดีมาก | ต่ำมาก |
| **biCGStab** | Asymmetric | General | Bi-Conjugate Gradient | ⚡ ปานกลาง | ⚠️ อาจ diverge | ปานกลาง |

### 7.2 ทำไม GAMG เร็วสำหรับ Pressure?

**GAMG** = Geometric Algebraic Multigrid

**ไอเดีย:** แก้สมการบน multiple grid resolutions

```
Fine Grid (1M cells)     →  Slow แก้ high-freq error
        ↓ restrict
Coarse Grid (250K cells)  →  Medium แก้ mid-freq error
        ↓ restrict
Coarser Grid (62K cells)  →  Fast แก้ low-freq error
        ↓ restrict
Coarsest (15K cells)      →  Very fast แก้ global error
        ↓ prolongate
...  going back up with corrections
```

**ทำงาน:**
1. **Pre-smoothing:** ลด high-freq error บน fine grid (Gauss-Seidel)
2. **Restriction:** ส่ง residual ไป coarse grid
3. **Coarse solve:** แก้ low-freq error บน coarse grid
4. **Prolongation:** ส่ง correction กลับไป fine grid
5. **Post-smoothing:** ลด remaining high-freq error

**ทำไมเหมาะกับ Pressure:**
- Pressure equation = Laplacian (elliptic) → information travels globally
- PCG: ลด error ทีละ frequency → ต้อง iterate มาก
- GAMG: ลด error ทุก frequency พร้อมกัน → converge เร็วมาก

**Visualizing GAMG Multigrid:**

```
V-Cycle in GAMG:

Level 3 (Finest, 1M cells):
┌─────────────────────────────────────┐
│ Smooth: Gauss-Seidel (reduce high-freq)│
│ Residual: r = b - Ax                  │
│ Restrict: Send r to coarser grid      │
└─────────────────────────────────────┘
              ↓
Level 2 (250K cells):
┌─────────────────────────────────────┐
│ Smooth: Gauss-Seidel                  │
│ Residual: r = b - Ax                  │
│ Restrict: Send r to coarser grid      │
└─────────────────────────────────────┘
              ↓
Level 1 (62K cells):
┌─────────────────────────────────────┐
│ Smooth: Gauss-Seidel                  │
│ Solve: Direct or many iterations     │
│ Prolongate: Send correction up       │
└─────────────────────────────────────┘
              ↑
Level 2 (250K cells):
┌─────────────────────────────────────┐
│ Correct: x_new = x_old + correction  │
│ Smooth: Gauss-Seidel                 │
│ Prolongate: Send correction up       │
└─────────────────────────────────────┘
              ↑
Level 3 (Finest):
┌─────────────────────────────────────┐
│ Correct: x_new = x_old + correction  │
│ Smooth: Final smoothing             │
│ → Converged solution!                │
└─────────────────────────────────────┘

Result: O(N) complexity instead of O(N²)!
```

### 7.3 ตั้งค่าใน `system/fvSolution`

```cpp
solvers
{
    p
    {
        solver          GAMG;               // Multigrid for Laplacian
        smoother        GaussSeidel;        // Pre/post-smoothing
        tolerance       1e-06;              // Absolute convergence (residual < 1e-6)
        relTol          0.01;               // Relative (stop after 100x reduction)

        // GAMG-specific
        nPreSweeps      1;                  // Pre-smoothing iterations
        nPostSweeps     2;                  // Post-smoothing iterations
        nFinestSweeps   2;                  // Extra sweeps on finest level

        cacheAgglomeration on;              // Cache agglomeration (faster repeat runs)
        nCellsInCoarsestLevel 50;           // Min cells on coarsest level

        // Alternative smoothers
        // smoother        DIC;               // Diagonal Incomplete Cholesky
        // smoother        DICGaussSeidel;    // Hybrid
    }

    pFinal
    {
        $p;                                 // Copy settings from p entry
        relTol          0;                  // ต้อง converge ถึง tolerance
    }

    U
    {
        solver          PBiCGStab;          // For asymmetric matrix
        preconditioner  DILU;               // Diagonal Incomplete LU

        tolerance       1e-05;
        relTol          0.1;                // ยอมแค่ลด 10 เท่า

        // PBiCGStab-specific
        minIter         0;
        maxIter         1000;
    }

    k
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-06;
        relTol          0.1;
    }

    T
    {
        solver          GAMG;               // If diffusion-dominated
        tolerance       1e-06;
        relTol          0.01;
    }
}
```

### 7.4 Tolerance vs relTol

| Parameter | ความหมาย | ตั้งค่าอย่างไร | ตัวอย่าง |
|-----------|----------|----------------|----------|
| `tolerance` | Absolute residual | ตาม accuracy ที่ต้องการ | 1e-6 (pressure) |
| `relTol` | Relative reduction | Intermediate: 0.1, Final: 0 | 0.01 → ลด 100 เท่า |

**Convergence criteria:** Solver จะหยุดเมื่อ:
```
initial_residual * relTol < tolerance
```

**ตัวอย่าง:**
- Initial residual = 1e-2
- `relTol` = 0.01
- `tolerance` = 1e-6

Stop when: `1e-2 * 0.01 = 1e-4` (ถึง 1e-4 ก็พอแล้ว!)

แต่ถ้า `relTol = 0`:
Stop when: `current_residual < 1e-6` (ต้องถึง 1e-6 จริงๆ)

**Visualizing Convergence Criteria:**

```
Convergence with relTol = 0.01, tolerance = 1e-6:

Initial residual: 1.0e-2
┌────────────────────────────────────────┐
│ Residual                                │
│     ↓                                  │
│ 1e-2 ┤●                                │
│      │ │                               │
│ 1e-3 ┤─┼─●                             │
│      │ │ │                             │
│ 1e-4 ┤─┼──┼────●  ← Stop! (1e-2 × 0.01) │
│      │ │ │    │                        │
│ 1e-5 ┤─┼──┼────┼────                   │
│      │ │ │    │                        │
│ 1e-6 ┤─┼──┼────┼────●  ← tolerance     │
│      └─┴──┴────┴────→ Iterations        │
│        1   5   10  15                  │
└────────────────────────────────────────┘

With relTol = 0 (must reach tolerance):
┌────────────────────────────────────────┐
│ Residual                                │
│     ↓                                  │
│ 1e-2 ┤●                                │
│      │                                 │
│ ...  │ (many more iterations)          │
│      │                                 │
│ 1e-6 ┤───────────────────────● ← Stop! │
│      └───────────────────────→ Iters   │
└────────────────────────────────────────┘
```

### 7.5 Preconditioners for Asymmetric Solvers

| Preconditioner | Full Name | Speed | Memory | เหมาะกับ |
|----------------|-----------|-------|--------|-----------|
| **DILU** | Diagonal ILU | เร็ว | ต่ำ | General purpose |
| **FDIC** | Fast DIC | เร็วมาก | ต่ำ | Structured meshes |
| **DIC** | Diagonal IC | เร็ว | ต่ำ | Symmetric positive definite |
| **GAMG** | (as preconditioner) | ปานกลาง | สูง | Large systems |

---

## Part 8: Under-Relaxation - Stability vs Speed

### 8.1 ทำไมต้องใช้?

**ปัญหา:** SIMPLE/PISO algorithms ไม่ stable ถ้าใช้ค่าใหม่ทั้งหมด

**ทางออก:** ผสมค่าเก่ากับค่าใหม่

$$\phi_{new} = \alpha \cdot \phi_{calculated} + (1-\alpha) \cdot \phi_{old}$$

โดยที่:
- $\alpha$ = relaxation factor (0 < α ≤ 1)
- $\alpha$ ต่ำ = เปลี่ยนช้า → stable แต่ converge ช้า
- $\alpha$ สูง = เปลี่ยนเร็ว → converge เร็ว แต่อาจ oscillate

### 8.2 ตั้งค่าใน `system/fvSolution`

```cpp
relaxationFactors
{
    fields
    {
        p       0.3;    // Pressure: ค่อยๆ เปลี่ยน (sensitive)
    }
    equations
    {
        U       0.7;    // Velocity: เปลี่ยนเร็วกว่าได้
        k       0.7;    // Turbulence kinetic energy
        epsilon 0.7;    // Dissipation rate
        omega   0.7;    // Specific dissipation rate
    }
}
```

### 8.3 ทำไม p ใช้ค่าต่ำ (0.3)?

| Field | α แนะนำ | เหตุผล |
|-------|----------|---------|
| **p** | 0.2 - 0.3 | Pressure correction โดนเกินไป (over-correction) → oscillate |
| **U** | 0.6 - 0.8 | Velocity ถูก pressure "บังคับ" → stable กว่า |
| **k, ε, ω** | 0.7 - 0.8 | Turbulence fields มี diffusion มาก → stable |

**ค่าต่ำ = "ค่อยๆ เชื่อ"** → stable แต่ช้าหน่อย

### 8.4 Relaxation ใน Matrix Terms

OpenFOAM implement relaxation ผ่าน matrix modification:

```cpp
// สมการดั้งเดิม: a_P φ_P + Σ a_N φ_N = b_P

// หลัง relaxation (α):
// a_P/α φ_P + Σ a_N φ_N = b_P + (1/α - 1) a_P φ_P_old
```

ผล:
- Diagonal ($a_P$) ใหญ่ขึ้น (หารด้วย α < 1)
→ **Diagonal dominant มากขึ้น** → stable

**Visualizing Relaxation Effect:**

```
Effect of Relaxation on Matrix Coefficients:

No Relaxation (α = 1.0):
┌────────────────────────────────────────┐
│ Equation: a_P·φ_P = b_P                 │
│                                         │
│ Matrix: [a_P] [φ_P] = [b_P]            │
│         ↑                               │
│    Diagonal (original)                  │
└────────────────────────────────────────┘

With Relaxation (α = 0.7):
┌────────────────────────────────────────┐
│ Equation: (a_P/0.7)·φ_P = b_P + 0.43·a_P·φ_P_old │
│                                         │
│ Matrix: [a_P/0.7] [φ_P] = [b_P + ...]  │
│            ↑                           │
│    Diagonal INCREASED by 43%            │
│    (10 → 14.3)                          │
│                                         │
│ → More diagonal dominance = More stable │
└────────────────────────────────────────┘

Rule: α ↓ = Diagonal ↑ = Stability ↑ (but slower)
```

### 8.5 PIMPLE Algorithm Relaxation

```cpp
PIMPLE
{
    nOuterCorrectors 2;      // PISO-like iterations

    // Transient simulation with relaxation
    nCorrectors      2;
    nNonOrthogonalCorrectors 0;

    // Relaxation factors (for transient)
    relaxationFactors
    {
        fields
        {
            p       0.3;
        }
        equations
        {
            U       0.7;
        }
    }
}
```

**Note:** PIMPLE combines PISO (transient) + SIMPLE (under-relaxation)

---

## Part 9: Debugging Matrix Problems

### 9.1 Checklist การแก้ปัญหา Matrix

| Symptom | สาเหตุที่เป็นไปได้ | วิธีตรวจสอบ | วิธีแก้ |
|---------|------------------|---------------|---------|
| **Divergence immediately** | Matrix ไม่ stable | Check diagonal dominance | ลด `deltaT`, เปลี่ยนเป็น upwind |
| **Residuals oscillate** | Over-correction | Check relaxation factors | ลด relaxation (0.7 → 0.5) |
| **Slow convergence** | Matrix ill-conditioned | Check condition number | เปลี่ยน solver (PBiCGStab → GAMG) |
| **Negative values** | Undershoot | Check boundedness | เปลิยนเป็น upwind/limitedLinear |
| **"Maximum iterations exceeded"** | Solver ไม่ converge | Check tolerance | เพิ่ม tolerance, เพิ่ม maxIter |
| **Very small residuals but no change** | Under-relaxation มากเกินไป | Check field values | เพิ่ม relaxation |

### 9.2 Problem 1: Immediate Divergence

```
--> FOAM FATAL ERROR: Maximum number of iterations exceeded
```

**สาเหตุ:** Matrix ไม่ stable พอ

**ลองทำ (ตามลำดับ):**

1. **ลด `deltaT`** → เพิ่ม temporal contribution ใน diagonal
   ```cpp
   deltaT  0.0001;  // ลดจาก 0.001
   // หรือใช้ adjustable time step
   adjustTimeStep yes;
   maxCo 0.3;      // Courant < 0.3
   ```

2. **ลด `relTol`** → converge แน่นขึ้น
   ```cpp
   solvers
   {
       U { relTol 0.01; }  // ลดจาก 0.1
   }
   ```

3. **ลด relaxation** → เปลี่ยนช้าลง
   ```cpp
   relaxationFactors
   {
       equations { U 0.5; }  // ลดจาก 0.7
   }
   ```

4. **เปลี่ยน convection scheme** → เปลี่ยนเป็น upwind
   ```cpp
   divSchemes
   {
       div(phi,U)  Gauss upwind;  // เปลี่ยนจาก linear
   }
   ```

5. **ตรวจสอบ BCs** — ต้องไม่ conflict
   ```bash
   # ตรวจสอบว่า mass balance ถูกต้อง
   postProcess -func 'patchFlowRate(name=inlet)'
   postProcess -func 'patchFlowRate(name=outlet)'
   ```

### 9.3 Problem 2: Slow Convergence

**สาเหตุ:** Solver ไม่ efficient หรือ tolerance เข้มไป

**ลองทำ:**

1. **เปลี่ยน solver** (สำหรับ pressure)
   ```cpp
   solvers
   {
       p { solver PBiCGStab; }  // แก้เป็น
       p { solver GAMG; }       // เร็วกว่ามาก
   }
   ```

2. **เพิ่ม `relTol`** สำหรับ intermediate iterations
   ```cpp
   solvers
   {
       p { relTol 0.1; }   // เพิ่มจาก 0.01
       pFinal { relTol 0; } // Final iteration ยัง converge เต็มที่
   }
   ```

3. **เปลี่ยน preconditioner** (สำหรับ asymmetric matrix)
   ```cpp
   solvers
   {
       U { preconditioner DILU; }   // ดี
       U { preconditioner FDIC; }   // ลองตัวนี้
   }
   ```

### 9.4 Problem 3: Check Residuals

```bash
foamLog log.simpleFoam
gnuplot residuals
```

**Residual ที่ดี:**
- ลดลงอย่างต่อเนื่อง (monotonic decrease)
- ลดได้ 4-6 orders of magnitude
- ไม่ oscillate

**Residual ที่ไม่ดี:**
- Oscillate → ลด relaxation
- Plateau → เปลี่ยน solver/scheme
- Increase → divergence แน่ๆ

### 9.5 Problem 4: Diagonal Dominance Check

**วิธีตรวจสอบ (คร่าวๆ):**

```cpp
// ใน custom solver code ของคุณ
scalar maxDiag = max(UEqn.A()).value();
scalar minDiag = min(UEqn.A()).value();
scalar avgOffDiag = average(sum(abs(UEqn.H()))).value();

Info << "Diagonal range: " << minDiag << " ~ " << maxDiag << endl;
Info << "Avg off-diagonal: " << avgOffDiag << endl;

Info << "Diagonal dominance ratio: "
     << avgOffDiag / maxDiag << endl;
```

**Result:**
- Ratio < 0.5: ดีมาก (very dominant)
- Ratio 0.5 - 0.9: ดี (acceptable)
- Ratio > 0.9: อันตราย (near loss of dominance)
- Ratio > 1.0: Unstable (แน่ๆ)

### 9.6 Problem 5: Negative Values

**อาการ:** k < 0, epsilon < 0, T < 0

**สาเหตุ:** Higher-order schemes ทำ undershoot

**การแก้:**

```cpp
// ❌ ผิด — ใช้ linear กับ turbulence
div(phi,k)      Gauss linear;
div(phi,epsilon) Gauss linear;

// ✅ ถูก — ใช้ upwind เสมอ
div(phi,k)      Gauss upwind;
div(phi,epsilon) Gauss upwind;
div(phi,omega)  Gauss upwind;

// ✅ ถูก — ใช้ limited scheme กับ scalar
div(phi,T)      Gauss limitedLinear 1;
```

> **💡 Rule:** k, ε, ω **ต้องใช้ upwind** เสมอ — เพื่อรักษา boundedness

### 9.7 Debugging Workflow

```
[Simulation Problem]
        │
        ├── Immediate divergence?
        │     ├── Check Initial Conditions → Set reasonable values
        │     └── Use potentialFoam for initial flow field
        │
        ├── Oscillating residuals?
        │     ├── Reduce p relaxation: 0.3 → 0.2
        │     └── Reduce U relaxation: 0.7 → 0.5
        │
        ├── Slow convergence?
        │     ├── Pressure: PBiCGStab → GAMG
        │     └── Increase relTol: 0.01 → 0.1
        │
        ├── Negative values?
        │     ├── Turbulence: upwind
        │     └── Scalar: limitedLinear
        │
        └── Still problems?
              ├── checkMesh
              └── Fix non-orthogonality
```

---

## Part 10: Advanced Topics

### 10.1 Matrix Condition Number

**Definition:**

$$\kappa(A) = \|A\| \cdot \|A^{-1}\| = \frac{|\lambda_{max}|}{|\lambda_{min}|}$$

- $\kappa \approx 1$: ดีมาก (well-conditioned)
- $\kappa \approx 100$: ยอมรับได้
- $\kappa > 1000$: ill-conditioned → converge ยาก

**Factors affecting condition number:**
- High aspect ratio cells → increases $\kappa$
- Large differences in coefficients → increases $\kappa$
- Small diagonal dominance → increases $\kappa$

### 10.2 Matrix Preconditioning Techniques

**Jacobi Preconditioning:**
```cpp
M = diag(A)
Solve M^{-1} A x = M^{-1} b
```

**Gauss-Seidel:**
```cpp
M = D + L  // Diagonal + Lower
Solve M^{-1} A x = M^{-1} b
```

**Incomplete LU (ILU):**
```cpp
A ≈ L U  // Factorization without fill-in
Solve M^{-1} A x = M^{-1} b where M = L U
```

### 10.3 Coupled vs Segregated Solvers

| Approach | Description | Pros | Cons | Solvers |
|----------|-------------|------|------|---------|
| **Segregated** | Solve each variable separately | Memory efficient | Slow convergence (SIMPLE iterations) | simpleFoam, pisoFoam |
| **Coupled** | Solve U and p simultaneously | Fast convergence | High memory | coupled solver, buoyantFoam |

### 10.4 Matrix-Free Methods

สำหรับ very large problems:

- **Matrix-free GMRES:** ไม่เก็บ matrix explicitly
- **Krylov subspace methods:** ใช้ matrix-vector products เท่านั้น
- **Application:** DNS, LES ที่มี cells หลายสิบล้าน

---

## Visual Diagram: Matrix Assembly Flow

```
PDE Equation
      │
      ├── Temporal Term → a_P += ρV/Δt, b_P += ρV/Δt·φⁿ
      │
      ├── Diffusion Term → a_N = -DA/d, a_P = -Σa_N
      │
      ├── Convection Term → a_N = max(-Φf, 0), a_P = -Σa_N
      │
      ├── Source Term → Semi-implicit: a_P -= Sp·V, b_P += Su·V
      │
      └── Boundary Conditions
            ├── fixedValue → a_P += ΣaN_b, b_P += ΣaN_b·φ_bc
            └── zeroGradient → No change
      │
      ↓
Sum All Contributions
      │
      ↓
[a_P φ_P + ΣaN φ_N = b_P]  for each cell
      │
      ↓
Assemble Global Matrix [A][φ] = [b]
      │
      ↓
Apply Sparse Structure (LDU format)
      │
      ↓
Iterative Solver (GAMG/PBiCGStab)
      │
      ├── Not converged → Apply relaxation → Update solution → Repeat
      │
      └── Converged → Next time step/iteration
```

---

## Concept Check

### 1. คำนวณ coefficient สำหรับ diffusion term (Step-by-Step)

**Problem:** 2D steady-state heat conduction ใน Cell P

Given:
- D = 100 W/m·K (thermal conductivity)
- Cell P มี 4 neighbors (N, S, E, W)
- Face area A_f = 0.02 m² (ทุก face)
- Distance d_PN = 0.005 m (ทุก neighbor)

**Solution:**

Step 1: คำนวณ $a_N$ สำหรับแต่ละ neighbor
$$a_N = -\frac{D A_f}{d_{PN}} = -\frac{100 \times 0.02}{0.005} = -400$$

Step 2: คำนวณ $a_P$
$$a_P = -\sum_N a_N = -(-400 \times 4) = 1600$$

Step 3: ตรวจสอบ diagonal dominance
$$|a_P| = 1600 > \sum |a_N| = 1600$$

→ Borderline diagonal dominant (เท่ากับพอดี)

---

### 2. fvm กับ fvc ต่างกันอย่างไร? ใช้เมื่อไหร่?

| | fvm | fvc |
|-|-----|-----|
| Output | Matrix coefficients ($a_P$, $a_N$) | Field values (ตัวเลข) |
| ใช้กับ | Unknown (กำลังจะหา) | Known (รู้แล้ว) |
| Matrix Effect | เพิ่ม coefficients | ไปที่ RHS ($b_P$) |
| ตัวอย่าง | `fvm::ddt(U)`, `fvm::div(phi, U)` | `fvc::grad(p)`, `fvc::div(phi)` |

**Rule:** ถ้าตัวแปรอยู่ใน LHS ของสมการที่กำลัง solve → ใช้ fvm

---

### 3. ทำไม GAMG เร็วกว่า PCG สำหรับ pressure?

**GAMG** = Geometric Algebraic Multigrid

- **PCG:** ลด error ทีละ frequency → ต้อง iterate มาก
- **GAMG:** ลด error ทุก frequency พร้อมกัน (coarse grid จัดการ low frequency)

Pressure = Laplacian equation → information ต้องเดินทางไกล (elliptic)
GAMG "เห็น" ทั้งโดเมนจาก coarse grid → converge เร็วมาก

**Speed:** GAMG > PCG ≈ 5-10x faster สำหรับ large problems

---

### 4. relaxation 0.3 กับ 0.7 ต่างกันอย่างไร?

$$\phi_{new} = \alpha \cdot \phi_{calculated} + (1-\alpha) \cdot \phi_{old}$$

| α | การเปลี่ยนแปลง | Stability | Speed |
|---|---------------|-----------|-------|
| 0.3 | เปลี่ยน 30% | สูง | ช้า |
| 0.7 | เปลี่ยน 70% | ต่ำ | เร็ว |

- **Pressure (α=0.3):** sensitive → ต้องค่อยๆ เปลี่ยน
- **Velocity (α=0.7):** stable กว่า → เปลี่ยนเร็วได้

**Matrix Effect:** α ต่ำ = diagonal ใหญ่ขึ้น (หารด้วย α)

---

### 5. ทำไมลด Δt ช่วยแก้ divergence?

Temporal term เพิ่ม diagonal:
$$a_P += \frac{\rho V}{\Delta t}$$

$\Delta t$ เล็ก → $\frac{\rho V}{\Delta t}$ ใหญ่ → diagonal dominant มากขึ้น → stable

**ตัวอย่าง:**
- Δt = 0.01 s → $a_P += 100$
- Δt = 0.001 s → $a_P += 1000$ (ใหญ่ขึ้น 10x!)

---

### 6. Semi-implicit source ทำไมช่วย stability?

$$S = S_u + S_p \cdot \phi$$

ถ้า $S_p < 0$ (เช่น reaction $S = -k\phi$):

**Explicit:**
$$a_P \phi_P + \sum a_N \phi_N = b_P + S V$$

**Semi-implicit:**
$$a_P' \phi_P + \sum a_N \phi_N = b_P'$$

โดยที่:
- $a_P' = a_P - S_p V = a_P - (-k) V = a_P + k V$ → **ใหญ่ขึ้น!**
- $b_P' = b_P + S_u V$

→ Diagonal dominant มากขึ้น → **stable ขึ้น**

---

### 7. Boundary conditions ทำอะไรกับ matrix?

| BC Type | Matrix Effect |
|---------|--------------|
| **fixedValue** | $a_P \leftarrow a_P + \sum a_N$ (diagonal ใหญ่ขึ้น) |
| | $a_N \leftarrow 0$ (ลบ off-diagonal) |
| | $b_P \leftarrow b_P + \sum a_N \phi_{bc}$ |
| **zeroGradient** | ไม่เปลี่ยน matrix |
| **mixed** | ผสม fixedValue + zeroGradient |

→ fixedValue เพิ่ม diagonal dominant (ดีสำหรับ stability)

---

### 8. สรุป: ทุก term ใน PDE ไปที่ไหนใน matrix?

| PDE Term | $a_P$ | $a_N$ | $b_P$ | Stability |
|----------|-------|-------|-------|-----------|
| $\frac{\partial \phi}{\partial t}$ | $+\frac{\rho V}{\Delta t}$ | — | $+\frac{\rho V}{\Delta t} \phi^n$ | ✅ |
| $\nabla \cdot (D \nabla \phi)$ | $-\sum a_N$ | $-\frac{DA}{d}$ | — | ✅ |
| $\nabla \cdot (\phi \mathbf{u})$ | $-\sum a_N$ | $\max(-\Phi_f, 0)$ | — | ⚠️ |
| $S_u$ | — | — | $+S_u V$ | ⚠️ |
| $S_p \phi$ | $+S_p V$ | — | $+S_u V$ | ✅ (ถ้า $S_p < 0$) |
| fixedValue BC | $+\sum a_N$ | 0 | $+\sum a_N \phi_{bc}$ | ✅ |
| zeroGradient BC | — | — | — | — |

---

## Summary: Key Takeaways

| แนวคิด | สิ่งที่ต้องจำ |
|---------|--------------|
| **Sparse Matrix** | Non-zero เฉพาะ neighbors → O(N) memory → Iterative solvers |
| **Temporal** | $a_P += \frac{\rho V}{\Delta t}$ → ลด Δt = ช่วย stability |
| **Diffusion** | $a_N < 0$ เสมอ → Diagonal dominant → Stable |
| **Convection** | Upwind → $a_N$ มาจาก upstream → อาจลด diagonal dominant |
| **fvm vs fvc** | fvm → matrix (unknown), fvc → RHS (known) |
| **GAMG** | Multigrid → ลด error ทุก frequency → เร็วมากสำหรับ pressure |
| **Relaxation** | α ต่ำ → diagonal ใหญ่ขึ้น → stable แต่ช้า |
| **Semi-Implicit** | $S_p < 0$ → เพิ่ม diagonal → stable |
| **BCs** | fixedValue → เพิ่ม diagonal, zeroGradient → ไม่เปลี่ยน |
| **Debug** | Check diagonal dominance, residuals, relaxation, mesh quality |

---

## Related Documentation

### Within This Module
- **Previous:** [04_Temporal_Discretization.md](04_Temporal_Discretization.md) — Temporal Schemes และ CFL
- **Next:** [06_OpenFOAM_Implementation.md](06_OpenFOAM_Implementation.md) — Implementation ใน OpenFOAM
- **Fundamentals:** [02_Fundamental_Concepts.md](02_Fundamental_Concepts.md) — FVM Theory Foundation
- **Spatial:** [03_Spatial_Discretization.md](03_Spatial_Discretization.md) — Convection/Diffusion Schemes

### Cross-Module References
- **Advanced:** [../../../05_OPENFOAM_PROGRAMMING/CONTENT/06_MATRICES_LINEARALGEBRA/00_Overview.md](../../../05_OPENFOAM_PROGRAMMING/CONTENT/06_MATRICES_LINEARALGEBRA/00_Overview.md) — OpenFOAM Matrix Classes
- **Troubleshooting:** [07_Best_Practices.md](07_Best_Practices.md) — Debugging และ Best Practices

---

## Further Reading

### OpenFOAM Source Code
- `src/finiteVolume/fvMatrices/` — fvMatrix implementation
- `src/matrices/lduMatrix/` — Sparse matrix storage (LDU format)
- `src/OpenFOAM/matrices/` — Linear algebra classes
- `src/finiteVolume/fvMatrices/fvScalarMatrix/` — Scalar matrix operations
- `src/finiteVolume/fvMatrices/fvVectorMatrix/` — Vector matrix operations

### Recommended Papers
1. Saad, Y. (2003). *Iterative Methods for Sparse Linear Systems* (2nd ed.). SIAM.
2. Ferziger, J. H., & Perić, M. (2002). *Computational Methods for Fluid Dynamics* (3rd ed.). Springer. (Chapter 5: Discretization)
3. Jasak, H. (1996). *Error Analysis and Estimation for the Finite Volume Method* (PhD Thesis). Imperial College London.
4. Wesseling, P. (2001). *Principles of Computational Fluid Dynamics*. Springer. (Chapter 4: The pressure correction method)

### Online Resources
- [OpenFOAM User Guide: System/fvSolution](https://www.openfoam.com/documentation/user-guide/fvSolution.php)
- [CFD Online: Linear Solvers](https://www.cfd-online.com/Wiki/Linear_solvers)
- [OpenFOAM CFD: fvMatrix Source Documentation](https://www.openfoam.com/documentation/guide/)

### Practice Exercises
ดู [08_Exercises.md](08_Exercises.md) สำหรับ:
- Matrix coefficient calculation exercises
- Solver selection problems
- Debugging scenarios
- Semi-implicit source implementation practice