# Domain Decomposition

การแบ่ง Domain สำหรับ Parallel

---

## Overview

> **Decomposition** = Split mesh for parallel computing

<!-- IMAGE: IMG_07_001 -->
<!-- 
Purpose: เพื่อแสดงหลักการ "Domain Decomposition" ในงาน Parallel Computing. ภาพนี้ต้องโชว์การหั่น Mesh ก้อนใหญ่ให้กลายเป็นชิ้นย่อยๆ (Sub-domains) ตามจำนวน Processor และต้องเน้น "Halo Layer" หรือ "Processor Boundary" ซึ่งเป็นบริเวณที่ต้องมีการสื่อสารข้อมูลกัน
Prompt: "Parallel Computing Decomposition Visualization. **Main Object:** A complex 3D Mesh (e.g., Engine Block or Airfoil). **Decomposition:** The mesh is sliced into 4 colored zones (Red, Blue, Green, Yellow), each representing a CPU Core. **Exploded View:** The zones are slightly pulled apart to reveal the internal 'Processor Patches'. **Detail:** Zoom in to a boundary gap showing 'Halo Cells' sending data packets (arrows) across the gap. Label: 'MPI Communication'. STYLE: High-tech grid visualization, distinct zone colors, futuristic data flow aesthetics."
-->
![IMG_07_001: Domain Decomposition and Parallel Processing](../images/IMG_07_001.png)
> **Obsidian:** ![[IMG_07_001.jpg]]

---

## 1. Decomposition Methods

| Method | Use |
|--------|-----|
| scotch | Auto-balanced |
| simple | Regular domains |
| hierarchical | Multi-level |

---

## 2. Setup

```cpp
// system/decomposeParDict
numberOfSubdomains 8;
method scotch;
```

---

## 3. Simple Method

```cpp
method simple;
simpleCoeffs
{
    n (4 2 1);  // x y z splits
}
```

---

## 4. Run

```bash
# Decompose
decomposePar -force

# Check
ls -la processor*/constant/

# Run parallel
mpirun -np 8 simpleFoam -parallel
```

---

## 5. Reconstruct

```bash
# All times
reconstructPar

# Latest only
reconstructPar -latestTime
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Split | decomposePar |
| Check | ls processor* |
| Merge | reconstructPar |

---

## 🧠 Concept Check

<details>
<summary><b>1. scotch ดีอย่างไร?</b></summary>

**Auto-balances** cells across processors
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)