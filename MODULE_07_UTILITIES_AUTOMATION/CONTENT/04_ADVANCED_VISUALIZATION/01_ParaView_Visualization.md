# ParaView Visualization

การใช้ ParaView

---

## Overview

> **ParaView** = Standard CFD visualization

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