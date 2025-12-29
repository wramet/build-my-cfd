# ParaView Visualization

การใช้ ParaView

---

## Overview

> **ParaView** = Standard CFD visualization

<!-- IMAGE: IMG_07_004 -->
<!-- 
Purpose: เพื่อแนะนำหน้าตา (Interface) ของ ParaView ให้กับผู้เริ่มต้น. ภาพนี้ต้องชี้จุดสำคัญ 4 จุด: 1. Pipeline Browser 2. Properties Panel 3. 3D Viewport 4. Toolbar. พร้อมโชว์ตัวอย่างการ Visualize แบบ Contour หรือ Streamlines ที่สวยงาม
Prompt: "Mockup of ParaView User Interface. **Central Viewport:** A stunning 3D visualization of aerodynamic flow around a car (Streamlines + Pressure Surface). **Sidebar (Left):** 'Pipeline Browser' showing loaded modules. **Panel (Bottom-Left):** 'Properties' with 'Apply' button highlighted green. **Toolbar (Top):** Icons for 'Slice', 'Clip', 'Glyph'. **Annotations:** Callout bubbles pointing to key areas: 1. Load Data 2. Filters 3. Render View. STYLE: Clean UI mockup, high-resolution aesthetic, dark theme."
-->
![[IMG_07_004.jpg]]

---

## 1. Open Case

```bash
touch case.foam
paraview case.foam
```

---

## 2. Common Views

| Filter | Use |
|--------|-----|
| Slice | Cut plane |
| Contour | Iso-surfaces |
| Glyph | Vectors |
| Streamline | Flow paths |

---

## 3. Basic Workflow

1. Open case.foam
2. Apply (green button)
3. Select field
4. Choose filter
5. Save screenshot

---

## 4. Screenshots

```
File > Save Screenshot
# Choose resolution, format
```

---

## 5. Animation

```
File > Save Animation
# All time steps as video
```

---

## Quick Reference

| Action | Menu |
|--------|------|
| Slice | Filters > Common |
| Contour | Filters > Common |
| Save | File > Save Screenshot |

---

## 🧠 Concept Check

<details>
<summary><b>1. case.foam ใช้ทำไม?</b></summary>

**Marker file** ให้ ParaView รู้จัก case
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **Python:** [02_Python_Plotting.md](02_Python_Plotting.md)