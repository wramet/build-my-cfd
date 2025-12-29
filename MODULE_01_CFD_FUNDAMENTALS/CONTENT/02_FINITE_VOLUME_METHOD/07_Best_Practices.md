# Best Practices

แนวปฏิบัติสำหรับ CFD Simulation ที่เสถียร แม่นยำ และมีประสิทธิภาพ

> **ทำไมต้องมี Best Practices?**
> - หลายปัญหา CFD มี "กับดัก" ที่คนเริ่มต้นมักพลาด
> - Settings ที่ถูกต้องช่วยประหยัดเวลาและทรัพยากรมหาศาล
> - เรียนรู้จากประสบการณ์คนอื่น ดีกว่า trial-and-error

---

## Mesh Quality

### คุณภาพที่ต้องตรวจสอบ

| Parameter | Target | Critical | ทำไมสำคัญ |
|-----------|--------|----------|----------|
| Non-orthogonality | < 50° | > 70° | Gradient คำนวณผิด → diffusion ผิด |
| Skewness | < 0.5 | > 0.6 | Interpolation error → oscillation |
| Aspect Ratio | < 10 | > 100 | Cell ยาวเกิน → numerical diffusion สูง |
| Expansion Ratio | < 1.3 | > 1.5 | Cell โตเร็ว → error สะสม |

**ตรวจสอบ:**
```bash
checkMesh
```

**อ่านผลลัพธ์:**
```
Mesh OK.                            # ✅ ผ่าน
***Max aspect ratio = 150, ...      # ⚠️ มีปัญหา
```

### การแก้ไข

```cpp
// system/fvSolution — เพิ่ม non-orthogonal corrections
SIMPLE
{
    nNonOrthogonalCorrectors 2;  // 0 สำหรับ ortho, 2-3 สำหรับ non-ortho
}
```

**ทำไมต้อง correction?**
- Mesh เบี้ยว → gradient operator ผิด
- Correction วน iterate จนกว่าจะถูกต้อง

---

## Scheme Selection

### Temporal (ddtSchemes)

| Scheme | Order | Stability | ใช้เมื่อ | ทำไม |
|--------|-------|-----------|---------|------|
| `Euler` | 1 | ดีมาก | เริ่มต้น, general | ง่าย stable |
| `backward` | 2 | ดี | ต้องการ accuracy | แม่นยำกว่า |
| `CrankNicolson 0.5` | 2 | ปานกลาง | Waves | เก็บ energy ดี |

**Rule of thumb:**
1. เริ่มด้วย `Euler`
2. Stable แล้วค่อยเปลี่ยน `backward`

### Convection (divSchemes)

> **ทำไม Convection สำคัญที่สุด?**
> - Convection term คือ "ตัวร้าย" หลักที่ทำให้ diverge
> - เลือก scheme ตาม Peclet number (Pe = convection/diffusion)

| Pe (Peclet) | Scheme | เหตุผล |
|-------------|--------|--------|
| < 2 | `Gauss linear` | Diffusion ครอบงำ → ใช้ accurate scheme ได้ |
| 2-10 | `Gauss linearUpwind` | Balance ระหว่าง accuracy และ stability |
| > 10 | `Gauss upwind` | Convection ครอบงำ → ต้อง stable |

**Turbulence (k, ε, ω):** ใช้ `Gauss upwind` เสมอ
- **ทำไม?** ค่าต้อง > 0 เสมอ → higher-order อาจทำให้ลบ → blow up

### Diffusion (laplacianSchemes)

```cpp
laplacianSchemes
{
    default         Gauss linear corrected;   // Standard (ortho mesh)
    // หรือ
    default         Gauss linear limited 0.5; // High non-ortho (> 60°)
}
```

**ทำไม `limited`?**
- `corrected` อาจ unstable สำหรับ mesh เบี้ยวมาก
- `limited` จำกัด correction → stable กว่าแต่ accuracy ลดลง

### Gradient (gradSchemes)

```cpp
gradSchemes
{
    default         Gauss linear;                // Standard เร็ว
    grad(U)         cellLimited Gauss linear 1;  // Limited กัน overshoot
}
```

**ทำไม limit gradient?**
- Gradient extremes อาจทำให้ค่า bound ผิด (เช่น T < 0)

---

## Solver Settings

### Solver Selection

| Field | Solver | Preconditioner | ทำไม |
|-------|--------|----------------|------|
| p | `GAMG` | GaussSeidel | Multigrid เร็วสุดสำหรับ Laplacian |
| U | `PBiCGStab` | DILU | Asymmetric matrix (convection) |
| k, ε | `PBiCGStab` | DILU | เหมือน U |
| T | `PBiCGStab` | DILU | เหมือน U |

### Tolerance Guide

| Field | tolerance | relTol | ทำไม |
|-------|-----------|--------|------|
| p | 1e-6 | 0.01 | Pressure ต้องแม่น → ส่งผลต่อ continuity |
| pFinal | 1e-6 | 0 | ต้อง converge จริงๆ (ไม่ใช่แค่ 100x reduction) |
| U | 1e-5 | 0.1 | หย่อนกว่า p ได้ (อัพเดทถี่) |
| k, ε | 1e-6 | 0.1 | Turbulence ต้องแม่นพอสมควร |

**relTol คืออะไร?**
- `relTol 0.01` = หยุดเมื่อ residual ลด 100 เท่าจากตอนเริ่ม iteration นั้น
- `relTol 0` = ต้องถึง tolerance จริงๆ

### Relaxation Factors

| Field | Steady (SIMPLE) | Transient (PIMPLE) | ทำไม |
|-------|-----------------|-------------------|------|
| p | 0.3 | 0.7-1.0 | Steady: ลดการ oscillate |
| U | 0.7 | 0.9-1.0 | Transient: ต้องแม่นต่อ time step |
| k, ε | 0.7 | 0.9-1.0 | — |

**ทำไม steady ใช้ relaxation ต่ำ?**
- SIMPLE ไม่ exact → ค่าใหม่อาจผิดมาก
- Relaxation "ขัดขวาง" การเปลี่ยนแปลงเร็วเกินไป

---

## Boundary Conditions

### Velocity

| Location | Type | ทำไม |
|----------|------|------|
| Inlet | `fixedValue` | กำหนด U ที่รู้ |
| Outlet | `zeroGradient` หรือ `inletOutlet` | ปล่อยไหลอิสระ |
| Wall | `noSlip` | ของไหลติดผนัง |

### Pressure

| Location | Type | ทำไม |
|----------|------|------|
| Inlet | `zeroGradient` | ปล่อย p ปรับตัว (U กำหนดแล้ว) |
| Outlet | `fixedValue` | Reference point สำหรับ p |
| Wall | `zeroGradient` | ไม่มี pressure flux ผ่านผนัง |

### Turbulence Wall Functions

| y+ Range | Wall Function | ทำไม |
|----------|---------------|------|
| < 5 | Low-Re model | Resolve viscous sublayer |
| 30-300 | `kqRWallFunction`, `epsilonWallFunction` | Log-law region → wall function ใช้ได้ |
| > 300 | **ผิด!** | Mesh หยาบเกินไป → refine |

**ทำไม 5-30 หลีกเลี่ยง?**
- Buffer layer: ไม่ตรงกับสมมติฐานใด
- ผลลัพธ์ไม่น่าเชื่อถือ

### การคำนวณ y+ และ Cell Size ใกล้ผนัง

**Step 1: ประมาณ Friction Velocity (u_τ)**

$$u_\tau = \sqrt{\frac{\tau_w}{\rho}} = \frac{U \sqrt{C_f}}{2^{1/2}}$$

โดยที่ $C_f$ (skin friction coefficient) สำหรับ turbulent pipe flow:
$$C_f \approx 0.079 \cdot Re^{-0.25}$$

**Step 2: คำนวณ y+ จากระยะห่างผนัง (y)**

$$y^+ = \frac{y \cdot u_\tau}{\nu}$$

**Step 3: กลับคำนวณขนาด cell ที่ต้องการ**

ถ้าต้องการ $y^+ = 30$:
$$y = \frac{30 \cdot \nu}{u_\tau}$$

**ตัวอย่าง:**
- ความเร็ว $U = 10$ m/s
- ความหนืด kinematic $\nu = 1.5 \times 10^{-5}$ m²/s (air)
- ความยาวลักษณะ $L = 1$ m
- $Re = \frac{10 \times 1}{1.5 \times 10^{-5}} \approx 666,667$

$$C_f \approx 0.079 \times (666,667)^{-0.25} \approx 0.0042$$
$$u_\tau = \frac{10 \times \sqrt{0.0042}}{1.414} \approx 0.46 \text{ m/s}$$
$$y_{y+=30} = \frac{30 \times 1.5 \times 10^{-5}}{0.46} \approx 0.00098 \text{ m} \approx 1 \text{ mm}$$

ดังนั้น cell size แรกแรกผนังควรเป็น **~1 mm** สำหรับกรณีนี้

---

## Convergence Monitoring

### Residual Targets

| Field | Initial | Final | ลดกี่ order |
|-------|---------|-------|------------|
| p | 1e-2 | 1e-5 | 3+ |
| U | 1e-2 | 1e-5 | 3+ |
| k, ε | 1e-2 | 1e-5 | 3+ |

**ทำไม 3+ orders?**
- น้อยกว่า 3: อาจไม่ converge จริง
- มากกว่า 5-6: อาจ waste compute time

### ตรวจสอบ

```cpp
// system/controlDict
functions
{
    residuals
    {
        type            residuals;
        libs            (utilityFunctionObjects);
        writeControl    timeStep;
        fields          (p U k epsilon);
    }
}
```

```bash
# วิเคราะห์ log
foamLog log.simpleFoam
gnuplot residuals.gp
```

**สัญญาณที่ดี:**
- Residual ลดอย่างต่อเนื่อง (monotonic)
- ไม่มี oscillation

**สัญญาณอันตราย:**
- Residual เพิ่มขึ้น → กำลังจะ diverge
- Oscillate รอบค่าคงที่ → ไม่ converge

---

## Troubleshooting

### Divergence

| สาเหตุ | ตรวจสอบอย่างไร | การแก้ไข |
|--------|----------------|---------|
| Δt ใหญ่เกินไป | `Co >> 1` | ลด `deltaT`, ตั้ง `maxCo 0.5` |
| Relaxation สูงเกินไป | ลอง conservative values | ลด p=0.2, U=0.5 |
| Mesh ไม่ดี | `checkMesh` | Fix non-ortho, skewness |
| BC ไม่ถูกต้อง | ตรวจ inlet/outlet pairing | ดู [BC Selection Guide](../03_BOUNDARY_CONDITIONS/03_Selection_Guide_Which_BC_to_Use.md) |
| Scheme ไม่เสถียร | ดู scheme choice | เปลี่ยนเป็น upwind |

### Converge ช้า

| สาเหตุ | การแก้ไข |
|--------|---------|
| Relaxation ต่ำเกินไป | เพิ่ม p=0.4, U=0.8 |
| Solver tolerance | เพิ่ม relTol (0.01 → 0.1) |
| Initial conditions | เดิม fields จาก similar case |
| ใช้ SIMPLE + transient mesh | เปลี่ยนเป็น PIMPLE |

### Accuracy ต่ำ

| สาเหตุ | การแก้ไข |
|--------|---------|
| Numerical diffusion | เปลี่ยน upwind → linearUpwind |
| Mesh หยาบ | Refine mesh (mesh independence study) |
| BCs ผิด | ตรวจสอบ physics |

---

## Parallel Computing

### Setup

```cpp
// system/decomposeParDict
numberOfSubdomains  8;
method              scotch;  // Automatic load balancing
```

**ทำไม scotch?**
- อัตโนมัติ จัดการ complex geometry ได้
- Balance cells ต่อ processor ดี

### Run

```bash
decomposePar                         # แบ่ง mesh
mpirun -np 8 simpleFoam -parallel    # รัน parallel
reconstructPar                        # รวมผลลัพธ์
```

### Guidelines

| Condition | Recommendation |
|-----------|----------------|
| Cells ต่อ processor | 10,000-50,000 |
| Complex geometry | ใช้ `scotch` |
| Structured mesh | ใช้ `hierarchical` |
| Small case (< 100k cells) | อาจไม่คุ้มค่า parallel |

**ทำไม 10k-50k?**
- น้อยเกินไป: Communication overhead > Compute gain
- มากเกินไป: ไม่ใช้ประโยชน์ processors เต็มที่

---

## Pre-Run Checklist

✅ `checkMesh` passes with no errors
✅ BCs consistent (p zeroGradient where U fixed, etc.)
✅ Initial fields reasonable (ไม่ใช่ 0 ทั้งหมดถ้าไม่เหมาะสม)
✅ Time step gives Co < 1 (transient) หรือ stable residuals (steady)
✅ Schemes appropriate for flow regime
✅ Solver tolerances set correctly
✅ Relaxation factors reasonable (0.3-0.7 for SIMPLE)

---

## Concept Check

<details>
<summary><b>1. Mesh non-orthogonality สูง (60°) ต้องทำอย่างไร?</b></summary>

1. **เพิ่ม corrections:**
   ```cpp
   SIMPLE { nNonOrthogonalCorrectors 2; }
   ```
2. **ใช้ limited Laplacian:**
   ```cpp
   laplacianSchemes { default Gauss linear limited 0.5; }
   ```
3. **ลอง leastSquares gradient:**
   ```cpp
   gradSchemes { default leastSquares; }
   ```
</details>

<details>
<summary><b>2. Simulation diverge ทันทีที่เริ่ม ควรตรวจอะไร?</b></summary>

**ตามลำดับ:**
1. **Initial conditions:** ค่า 0 ที่ไม่ควรเป็น 0? (เช่น p ใน compressible)
2. **Boundary conditions:** consistent pairing? (inlet U fixed → outlet p fixed)
3. **Time step:** ใหญ่เกินไป? → ลอง Δt เล็กลง 10x
4. **Mesh quality:** `checkMesh` → fix issues
</details>

<details>
<summary><b>3. Residual ลดลงแล้วหยุด ไม่ลดต่อ ทำอย่างไร?</b></summary>

1. **ตรวจ mass balance:** `postProcess -func 'patchFlowRate(name=inlet)'`
2. **ดู field monitoring:** อาจ converged แล้ว (ค่าไม่เปลี่ยน)
3. **Tighten tolerances:** ลด relTol
4. **ตรวจ BCs:** อาจมี conflict (เช่น fixedValue ทุกที่)
</details>

<details>
<summary><b>4. ทำไมลด relaxation ช่วย divergence?</b></summary>

**เหตุผล:**
- ค่า relaxation ต่ำ = เชื่อค่าใหม่น้อย → เปลี่ยนช้า
- ป้องกัน overcorrection ที่ทำให้ oscillate
- Trade-off: stable แต่ converge ช้าลง
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [06_OpenFOAM_Implementation.md](06_OpenFOAM_Implementation.md) — OpenFOAM Implementation
- **บทถัดไป:** [08_Exercises.md](08_Exercises.md) — แบบฝึกหัด
- **BC Guide:** [03_Selection_Guide_Which_BC_to_Use.md](../03_BOUNDARY_CONDITIONS/03_Selection_Guide_Which_BC_to_Use.md)