# แบบฝึกหัด: Lid-Driven Cavity

แบบฝึกหัดสำหรับฝึกใช้งาน OpenFOAM

---

## Exercise 1: Basic Simulation

### โจทย์

รัน cavity case สำหรับ Re = 100

**Tasks:**
1. Copy tutorial case
2. Run simulation
3. Visualize results in ParaView

<details>
<summary><b>คำตอบ</b></summary>

```bash
# 1. Setup
cp -r $FOAM_TUTORIALS/incompressible/icoFoam/cavity/cavity myCase
cd myCase

# 2. Check ν for Re=100
cat constant/transportProperties
# nu = 0.01 → Re = 1×1/0.01 = 100 ✓

# 3. Mesh
blockMesh
checkMesh

# 4. Run
icoFoam > log.icoFoam 2>&1

# 5. Visualize
paraFoam
```

</details>

---

## Exercise 2: Change Reynolds Number

### โจทย์

เปลี่ยน Re จาก 100 เป็น 400 และ 1000

<details>
<summary><b>คำตอบ</b></summary>

**Re = 400:**
```cpp
// constant/transportProperties
nu [0 2 -1 0 0 0 0] 0.0025;  // Re = 1/0.0025 = 400
```

**Re = 1000:**
```cpp
nu [0 2 -1 0 0 0 0] 0.001;   // Re = 1/0.001 = 1000
```

**Note:** สำหรับ Re สูง อาจต้อง:
- เพิ่ม mesh resolution
- ลด time step
- เพิ่ม endTime

</details>

---

## Exercise 3: Mesh Refinement

### โจทย์

เปลี่ยน mesh จาก 20×20 เป็น 40×40 และเปรียบเทียบผลลัพธ์

<details>
<summary><b>คำตอบ</b></summary>

```cpp
// constant/polyMesh/blockMeshDict
blocks
(
    hex (0 1 2 3 4 5 6 7) (40 40 1) simpleGrading (1 1 1)
);
```

```bash
blockMesh
checkMesh
icoFoam > log.icoFoam 2>&1
```

**ผลที่คาดหวัง:**
- Vortex center ใกล้เคียง reference มากขึ้น
- Velocity profiles เรียบกว่า
- Run time นานขึ้น

</details>

---

## Exercise 4: Time Step Sensitivity

### โจทย์

ทดสอบ deltaT = 0.001, 0.005, 0.01 สำหรับ Re = 100

<details>
<summary><b>คำตอบ</b></summary>

```cpp
// system/controlDict
deltaT    0.001;  // หรือ 0.005 หรือ 0.01
endTime   0.5;
```

| deltaT | CFL (approx) | Stability |
|--------|--------------|-----------|
| 0.001 | ~0.02 | Very stable |
| 0.005 | ~0.1 | Stable |
| 0.01 | ~0.2 | OK for this case |

</details>

---

## Exercise 5: Discretization Schemes

### โจทย์

เปรียบเทียบ `Gauss linear` vs `Gauss upwind` สำหรับ convection term

<details>
<summary><b>คำตอบ</b></summary>

**Gauss linear (2nd order):**
```cpp
divSchemes
{
    div(phi,U)  Gauss linear;
}
```

**Gauss upwind (1st order):**
```cpp
divSchemes
{
    div(phi,U)  Gauss upwind;
}
```

| Scheme | Accuracy | Stability | Numerical Diffusion |
|--------|----------|-----------|---------------------|
| linear | 2nd order | May oscillate | Low |
| upwind | 1st order | Stable | High |

</details>

---

## Exercise 6: Validation

### โจทย์

Extract centerline velocity profiles และเปรียบเทียบกับ Ghia et al.

<details>
<summary><b>คำตอบ</b></summary>

**1. Add sample function:**
```cpp
// system/controlDict (in functions block)
sample1
{
    type        sets;
    libs        (sampling);
    writeControl writeTime;
    setFormat   raw;
    
    sets
    (
        verticalCenterline
        {
            type    uniform;
            axis    y;
            start   (0.5 0 0.05);
            end     (0.5 1 0.05);
            nPoints 100;
        }
    );
    fields (U);
}
```

**2. Post-process:**
```bash
postProcess -func sample1 -latestTime
```

**3. Data location:**
```
postProcessing/sample1/0.5/verticalCenterline_U.raw
```

</details>

---

## Exercise 7: Parallel Run

### โจทย์

รัน cavity case แบบ parallel บน 4 cores

<details>
<summary><b>คำตอบ</b></summary>

**1. Create decomposeParDict:**
```cpp
// system/decomposeParDict
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      decomposeParDict;
}

numberOfSubdomains 4;
method          simple;

simpleCoeffs
{
    n           (2 2 1);
    delta       0.001;
}
```

**2. Run:**
```bash
decomposePar
mpirun -np 4 icoFoam -parallel > log.icoFoam 2>&1
reconstructPar
```

</details>

---

## Exercise 8: Higher Re (Turbulent)

### โจทย์

สำหรับ Re = 10000 ต้องใช้ solver และ setup อะไร?

<details>
<summary><b>คำตอบ</b></summary>

Re = 10000 เป็น turbulent → ต้องใช้:

**1. Solver:** `pimpleFoam` (ไม่ใช่ `icoFoam`)

**2. Turbulence model:**
```cpp
// constant/turbulenceProperties
simulationType  RAS;
RAS
{
    RASModel        kEpsilon;
    turbulence      on;
    printCoeffs     on;
}
```

**3. Additional BCs:**
```cpp
// 0/k, 0/epsilon, 0/nut
```

**4. Wall functions:**
```cpp
// 0/nut
wall { type nutkWallFunction; value uniform 0; }
```

**5. Finer mesh:** ต้องการ y+ ≈ 30-300 สำหรับ wall functions

</details>

---

## Exercise 9: Debugging

### โจทย์

Simulation diverges — หาสาเหตุและแก้ไข

```
FOAM FATAL ERROR:
Maximum number of iterations exceeded
```

<details>
<summary><b>คำตอบ</b></summary>

**Possible causes & solutions:**

1. **Time step too large:**
   ```cpp
   deltaT  0.001;  // ลดลง
   ```

2. **Mesh quality:**
   ```bash
   checkMesh  # ดู non-orthogonality, skewness
   ```

3. **Scheme unstable:**
   ```cpp
   div(phi,U)  Gauss upwind;  // เปลี่ยนจาก linear
   ```

4. **BC mismatch:**
   - ตรวจสอบ patch names ให้ตรงกับ blockMeshDict
   - ตรวจสอบ U-p consistency

5. **Under-relaxation:**
   ```cpp
   relaxationFactors
   {
       fields { p 0.3; }
       equations { U 0.7; }
   }
   ```

</details>

---

## Concept Check

<details>
<summary><b>1. ถ้าต้องการ Re = 500 ต้องกำหนด ν เท่าไหร่?</b></summary>

$$\nu = \frac{UL}{Re} = \frac{1 \times 1}{500} = 0.002 \text{ m}^2/\text{s}$$

```cpp
nu [0 2 -1 0 0 0 0] 0.002;
```
</details>

<details>
<summary><b>2. Mesh 40×40 มี cells ทั้งหมดกี่ cells?</b></summary>

40 × 40 × 1 = 1600 cells (quasi-2D)
</details>

<details>
<summary><b>3. ทำไม parallel run ต้อง reconstructPar?</b></summary>

เพราะ `decomposePar` แบ่ง mesh ออกเป็น subdomains แยกกัน → หลัง run ต้อง `reconstructPar` เพื่อรวม results กลับเป็น single domain สำหรับ post-processing
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [05_Expected_Results.md](05_Expected_Results.md) — Results
- **กลับสู่:** [00_Overview.md](00_Overview.md) — Overview