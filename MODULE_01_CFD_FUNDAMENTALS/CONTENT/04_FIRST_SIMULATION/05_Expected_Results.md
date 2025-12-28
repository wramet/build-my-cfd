# Expected Results & Validation

การตรวจสอบความถูกต้องของผลลัพธ์

---

## Flow Pattern

### Primary Vortex

| Re | Center (x/L, y/L) | Stream Function ψ_max |
|----|-------------------|----------------------|
| 100 | (0.617, 0.734) | -0.1034 |
| 400 | (0.555, 0.606) | -0.1139 |
| 1000 | (0.531, 0.563) | -0.1179 |

*Reference: Ghia et al. (1982)*

### Secondary Vortices (Re ≥ 400)

| Re | Bottom-Right (BR) | Bottom-Left (BL) |
|----|-------------------|------------------|
| 400 | (0.89, 0.12) | (0.03, 0.04) |
| 1000 | (0.86, 0.11) | (0.08, 0.08) |

---

## Velocity Profiles

### u-velocity at x = 0.5 (Vertical Centerline)

**Re = 100:**
```
y/L     u/U (Ghia)
0.0000  0.00000
0.0547  -0.03717
0.0625  -0.04192
0.0703  -0.04775
0.1016  -0.06434
0.1719  -0.10150
0.2813  -0.15662
0.4531  -0.21090
0.5000  -0.20581
0.6172  -0.13641
0.7344   0.00332
0.8516   0.23151
0.9531   0.68717
0.9609   0.73722
0.9688   0.78871
0.9766   0.84123
1.0000   1.00000
```

### v-velocity at y = 0.5 (Horizontal Centerline)

**Re = 100:**
```
x/L     v/U (Ghia)
0.0000  0.00000
0.0625  0.09233
0.0703  0.10091
0.0781  0.10890
0.0938  0.12317
0.1563  0.16077
0.2266  0.17507
0.2344  0.17527
0.5000  0.05454
0.8047  -0.24533
0.8594  -0.22445
0.9063  -0.16914
0.9453  -0.10313
0.9531  -0.08864
0.9609  -0.07391
0.9688  -0.05906
1.0000  0.00000
```

---

## Validation Approach

### 1. Visual Check

**ใน ParaView:**
- Streamlines ควรแสดง clockwise rotation
- Primary vortex ควรอยู่ใกล้ center
- ไม่มี spurious oscillations

### 2. Quantitative Comparison

**Extract centerline data:**
```cpp
// system/sampleDict
sets
(
    verticalCenterline
    {
        type    uniform;
        axis    y;
        start   (0.5 0 0.05);
        end     (0.5 1 0.05);
        nPoints 50;
    }
    horizontalCenterline
    {
        type    uniform;
        axis    x;
        start   (0 0.5 0.05);
        end     (1 0.5 0.05);
        nPoints 50;
    }
);
fields (U);
```

```bash
postProcess -func sample -latestTime
```

### 3. Python Validation Script

```python
import numpy as np
import matplotlib.pyplot as plt

# Ghia et al. data for Re=100
ghia_y = [0, 0.0547, 0.0625, 0.0703, 0.1016, 0.1719, 
          0.2813, 0.4531, 0.5, 0.6172, 0.7344, 0.8516, 
          0.9531, 0.9609, 0.9688, 0.9766, 1.0]
ghia_u = [0, -0.03717, -0.04192, -0.04775, -0.06434, 
          -0.1015, -0.15662, -0.2109, -0.20581, -0.13641, 
          0.00332, 0.23151, 0.68717, 0.73722, 0.78871, 
          0.84123, 1.0]

# Load OpenFOAM data
data = np.loadtxt('postProcessing/sample1/0.5/verticalCenterline_U.raw')
of_y = data[:, 1]
of_u = data[:, 3]  # Ux component

# Plot comparison
plt.figure(figsize=(8, 6))
plt.plot(of_u, of_y, 'b-', label='OpenFOAM')
plt.plot(ghia_u, ghia_y, 'ro', label='Ghia et al.')
plt.xlabel('u/U')
plt.ylabel('y/L')
plt.legend()
plt.grid(True)
plt.savefig('validation.png')
plt.show()
```

---

## Error Metrics

### L2 Norm Error

$$E_{L2} = \sqrt{\frac{\sum_{i=1}^{N}(u_i^{CFD} - u_i^{ref})^2}{N}}$$

**Acceptable range:** < 5% for coarse mesh, < 1% for fine mesh

### Max Error

$$E_{max} = \max_i |u_i^{CFD} - u_i^{ref}|$$

---

## Grid Convergence Study

| Grid | Cells | L2 Error (%) |
|------|-------|--------------|
| 10×10 | 100 | ~15% |
| 20×20 | 400 | ~5% |
| 40×40 | 1600 | ~2% |
| 80×80 | 6400 | ~1% |

---

## Common Issues

| Issue | Possible Cause | Solution |
|-------|----------------|----------|
| Vortex off-center | Not converged | Longer endTime |
| Poor validation | Mesh too coarse | Refine mesh |
| Oscillations | Scheme unstable | Use upwind |
| Slow convergence | Large time step | Reduce deltaT |

---

## Concept Check

<details>
<summary><b>1. ทำไมต้อง validate กับ Ghia et al.?</b></summary>

เพราะเป็น benchmark reference ที่ได้รับการยอมรับในวงการ CFD — ใช้ high-resolution methods และมี data ที่ละเอียด
</details>

<details>
<summary><b>2. Grid convergence study ทำไปทำไม?</b></summary>

เพื่อตรวจสอบว่า error มาจาก mesh resolution หรือ physics — ถ้า error ลดลงเมื่อ mesh fine ขึ้น แสดงว่า approach ถูกต้อง
</details>

<details>
<summary><b>3. L2 error < 5% ถือว่าดีไหม?</b></summary>

สำหรับ engineering applications ถือว่ายอมรับได้ แต่สำหรับ research อาจต้องการ < 1%
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [04_Step-by-Step_Tutorial.md](04_Step-by-Step_Tutorial.md) — Tutorial
- **บทถัดไป:** [06_Exercises.md](06_Exercises.md) — Exercises