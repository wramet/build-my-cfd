# Visualization - Overview

ภาพรวมการแสดงผลข้อมูล CFD

---

## 🎯 Learning Objectives
เป้าหมายการเรียนรู้

After completing this module, you will be able to:
หลังจากจบโมดูลนี้ คุณจะสามารถ:

- Choose appropriate visualization tools for different CFD analysis tasks
- Select 3D visualization workflows using ParaView for interactive exploration
- Create custom 2D plots and perform data extraction with Python
- Apply advanced rendering techniques in Blender for professional presentations
- Produce publication-quality animations from OpenFOAM simulations
- Integrate multiple tools in efficient visualization pipelines

---

## 📋 Prerequisites
ความรู้พื้นฐานที่ต้องการ

**Required Knowledge:**
- Basic OpenFOAM case structure familiarity (see [MODULE_02 Basics](../../MODULE_02_OPENFOAM_BASICS/))
- Understanding of CFD result fields (velocity U, pressure p, turbulence k/epsilon)
- Basic Python scripting ability
- Familiarity with Linux command line

**Recommended Preparation:**
- Completed at least one simple OpenFOAM simulation (cavity, pipeFlow)
- Basic understanding of vector/tensor field visualization concepts
- Experience with plotting tools (matplotlib, gnuplot, or similar)

---

## 📖 Module Overview
ภาพรวมโมดูล

> **Visualization** = Transform raw CFD data into actionable insights through visual representation
> 
> **การแสดงผล** = แปลงข้อมูล CFD ดิบให้เป็นข้อมูลเชิงลึกผ่านการแสดงผลแบบภาพ

### What: Progressive Visualization Learning Path
เนื้อหา: เส้นทางการเรียนรู้การแสดงผลแบบขั้นบันได

This module follows a structured progression from basic analysis to professional presentation:

| Stage | Focus | Tool | Goal |
|-------|-------|------|------|
| **Level 1** | Interactive 3D Analysis | ParaView | Quick insight into flow features |
| **Level 2** | Data Extraction & Custom Plots | Python | Quantitative analysis, publication graphs |
| **Level 3** | Advanced Rendering | Blender | High-quality still images, lighting effects |
| **Level 4** | Animation Production | ParaView + Python + FFmpeg | Professional videos, time-evolution visualization |

### Why: Tool Selection Strategy
ทำไม: กลยุทธ์การเลือกเครื่องมือ

Understanding **when to use each tool** prevents wasted effort:

- **ParaView**: Use for initial exploration, 3D flow visualization, quick animations
  - Best for: Interactive investigation, understanding 3D structures, identifying regions of interest
  - Limitations: Limited customization for publication-quality figures
  
- **Python**: Use for quantitative analysis, custom 2D plots, batch processing
  - Best for: Publication graphs, data extraction, automated report generation
  - Limitations: 3D capabilities less intuitive than ParaView

- **Blender**: Use for cinematic-quality rendering, presentations, client deliverables
  - Best for: Professional still images, complex lighting, realistic materials
  - Limitations: Steeper learning curve, overkill for quick analysis

- **Combined Workflows**: ParaView → Python → Blender → FFmpeg
  - Best for: Complete visualization pipelines from analysis to final output
  - Example: Extract data in ParaView → Process in Python → Render in Blender → Animate with FFmpeg

### How: Module Structure
อย่างไร: โครงสร้างโมดูล

| File | Topic | Est. Reading Time | Practical Work |
|------|-------|-------------------|----------------|
| **01_ParaView_Visualization.md** | Interactive 3D visualization, basic animation | 25 min | 2-3 hours |
| **02_Python_Plotting.md** | Data extraction, matplotlib plotting, automation | 20 min | 1-2 hours |
| **03_Blender_Rendering.md** | Advanced rendering, lighting, materials | 30 min | 3-5 hours |
| **04_Animation_Techniques.md** | Professional video production, compositing | 25 min | 2-4 hours |

---

## 🛠️ Tool Comparison Matrix
เมทริกซ์เปรียบเทียบเครื่องมือ

<details>
<summary><b>Interactive Tool Selection Guide</b> คลิกเพื่อดูเมทริกซ์เปรียบเทียบ</summary>

| Feature | ParaView | Python (matplotlib) | Blender | Combined |
|---------|----------|---------------------|---------|----------|
| **3D Visualization** | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐ Basic | ⭐⭐⭐⭐⭐ Excellent | - |
| **2D Plotting** | ⭐⭐ Limited | ⭐⭐⭐⭐⭐ Excellent | ⭐ Not applicable | - |
| **Data Analysis** | ⭐⭐ Basic | ⭐⭐⭐⭐⭐ Excellent | ⭐ Not applicable | - |
| **Animation Quality** | ⭐⭐⭐ Good | ⭐⭐ Basic | ⭐⭐⭐⭐⭐ Excellent | - |
| **Learning Curve** | ⭐⭐ Moderate | ⭐⭐⭐ Easy (if Python known) | ⭐⭐⭐⭐⭐ Steep | ⭐⭐⭐⭐⭐ Complex |
| **Speed for Quick Analysis** | ⭐⭐⭐⭐⭐ Very Fast | ⭐⭐⭐ Moderate | ⭐ Slow | ⭐ Slow |
| **Publication Quality** | ⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐⭐ Excellent | - |
| **Batch Processing** | ⭐⭐ Limited | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐ Possible | ⭐⭐⭐⭐⭐ Excellent |
| **Best Use Case** | Interactive exploration, 3D understanding | Quantitative analysis, publication graphs | Professional presentations, client deliverables | Complete analysis-to-presentation workflows |

</details>

---

## 📁 Module Contents Detail
รายละเอียดเนื้อหาในโมดูล

### 1. ParaView Visualization (01_ParaView_Visualization.md)
การแสดงผล 3 มิติด้วย ParaView

**What You'll Learn:**
- Opening OpenFOAM cases with `.foam` file
- Creating contours, vector fields, streamlines
- Using filters for derived quantities (vorticity, Q-criterion)
- Basic animation creation
- Exporting screenshots and data

**Key Concepts:**
- VTK pipeline architecture
- Time-series data handling
- Camera manipulation and lighting basics

**Cross-Reference:** For Python integration with ParaView, see §4 in 02_Python_Plotting.md

---

### 2. Python Plotting & Data Extraction (02_Python_Plotting.md)
การสร้างกราฟและดึงข้อมูลด้วย Python

**What You'll Learn:**
- Extracting probe data from OpenFOAM
- Creating time-history plots with matplotlib
- Plotting spatial profiles along lines
- Batch processing multiple cases
- Automating report generation

**Key Concepts:**
- Using `foamListTimes`, `sampleDict` utilities
- NumPy arrays for CFD data
- Custom styling for publication

**Cross-Reference:** For advanced rendering of plots in Blender, see 03_Blender_Rendering.md §5

---

### 3. Blender Advanced Rendering (03_Blender_Rendering.md)
การเรนเดอร์คุณภาพสูงด้วย Blender

**What You'll Learn:**
- Importing ParaView exports (OBJ, VTK)
- Setting up cinematic lighting
- Applying realistic materials (fluids, solids)
- Camera tracking and composition
- Render settings for high-quality output

**Key Concepts:**
- Eevee vs Cycles render engines
- Node-based material system
- Environment lighting and HDRIs

**Cross-Reference:** For animation basics in ParaView, see 01_ParaView_Visualization.md §6

---

### 4. Animation Techniques (04_Animation_Techniques.md)
เทคนิคการสร้างอนิเมชัน

**What You'll Learn:**
- Creating smooth camera paths
- Time-series data animation
- Combining ParaView and Blender animations
- FFmpeg post-processing
- Adding annotations and overlays

**Key Concepts:**
- Keyframe interpolation
- Video codecs and compression
- Compositing multiple layers

**Cross-Reference:** For Python automation of animations, see 02_Python_Plotting.md §7

---

## 🚀 Quick Start
เริ่มต้นอย่างรวดเร็ว

### Open Case in Different Tools

| Tool | Command/Action | File |
|------|----------------|------|
| **ParaView** | File → Open → Select `case.foam` | `case.foam` |
| **Python** | Import `PyFoam` or read raw data | `postProcessing/` |
| **gnuplot** | `plot "file.dat"` | Custom sampled data |

### Typical Workflow Example
ตัวอย่างเวิร์กโฟลว์ทั่วไป

```
Simulation Complete
    ↓
[ParaView] Explore 3D flow, identify regions of interest
    ↓
[Python] Extract quantitative data, create comparison plots
    ↓
[Blender] Render key frames for presentation
    ↓
[FFmpeg] Assemble final animation with annotations
```

---

## 📤 Common Output Formats
รูปแบบไฟล์ส่งออกทั่วไป

| Output Type | Recommended Format | Quality | Use Case |
|-------------|-------------------|---------|----------|
| **Still Images** | PNG (screenshots) | Medium | Quick analysis |
| | PDF, SVG (vector) | High | Publications |
| **3D Scenes** | OBJ, STL | High | Blender import |
| **Animations** | MP4 (H.264) | High | Presentations |
| | GIF | Low | Web sharing |
| **Data Files** | CSV, DAT | - | Excel/Python analysis |
| **Figures** | PDF, EPS | High | LaTeX papers |

---

## ⚠️ Common Pitfalls
ข้อผิดพลาดที่พบบ่อย

| Pitfall | Symptom | Solution | Reference |
|---------|---------|----------|-----------|
| **Wrong time directory selected** | Shows wrong timestep data | Use "Update Time" button or check time directories | ParaView §3.2 |
| **Mesh not visible** | Blank viewport | Check "Mesh Regions" in Properties panel | ParaView §2.1 |
| **Plot scaling issues** | Graphs distorted | Set equal aspect ratio with `ax.set_aspect('equal')` | Python §4.3 |
| **Too much data** | Slow rendering, crashes | Use fewer timesteps or clip region | ParaView §3.5 |
| **Blender import fails** | Missing textures | Export with correct scale from ParaView | Blender §2.2 |
| **Animation jumpy** | Not smooth | Use more timesteps or interpolation | Animation §3.1 |

---

## 💡 Key Takeaways
สรุปสิ่งสำคัญ

1. **Start with ParaView** for 3D understanding before detailed analysis
2. **Combine tools**—each has strengths: ParaView (3D) + Python (2D) + Blender (quality)
3. **Batch processing** with Python saves time for repetitive tasks
4. **Plan your visualization** before running simulations—save appropriate data
5. **Publication vs presentation**—different goals require different approaches
6. **Automation** is key for reproducible, consistent results

---

## 🎯 Practice Exercises
แบบฝึกหัด

### Beginner
1. Open the `cavity` tutorial case in ParaView and create velocity contours
2. Extract probe data at a point and plot velocity vs time in Python
3. Create a simple animation of flow development

### Intermediate
4. Automate plot generation for 5 different mesh densities
5. Render a publication-quality figure using Blender lighting
6. Create a side-by-side comparison animation (two cases)

### Advanced
7. Build a complete pipeline: ParaView → Python → Blender → FFmpeg
8. Create an automated report generation script
9. Produce a client-ready presentation video with annotations

---

## 🧠 Concept Check
ทดสอบความเข้าใจ

<details>
<summary><b>1. Which tool for this task?</b> ควรใช้เครื่องมือไหน</summary>

**Scenario:** You need to create a publication graph comparing velocity profiles from 3 different turbulence models

**Answer:** Use **Python**
- Extract line probes for each case
- Plot on same axes with matplotlib
- Style for publication (line types, colors, legend)
- Save as PDF/SVG for LaTeX

</details>

<details>
<summary><b>2. ParaView or Blender?</b> เลือกอะไรดี</summary>

**Scenario:** Your supervisor needs to understand the 3D vortex structures quickly

**Answer:** Start with **ParaView**
- Interactive exploration is faster
- Can rotate, zoom, change views instantly
- If needed for presentation, then export to Blender for final rendering

</details>

<details>
<summary><b>3. When to combine tools?</b> ควรใช้ร่วมกันเมื่อไหร่</summary>

**Scenario:** Conference presentation with high-quality video + data plots

**Answer:** Use **combined workflow**
1. ParaView: Explore and identify key features
2. Python: Extract data for quantitative plots
3. Blender: Render high-quality 3D frames
4. FFmpeg: Compose final video with both 3D animation and data plots

</details>

---

## 🔗 Cross-References
เอกสารที่เกี่ยวข้อง

### Within This Module
- **ParaView Basics:** [01_ParaView_Visualization.md](01_ParaView_Visualization.md) - Opening cases, creating visualizations
- **Python Integration:** [02_Python_Plotting.md](02_Python_Plotting.md) - Data extraction, automation
- **Advanced Rendering:** [03_Blender_Rendering.md](03_Blender_Rendering.md) - Professional-quality output
- **Animation Production:** [04_Animation_Techniques.md](04_Animation_Techniques.md) - Video creation workflow

### Related Modules
- **OpenFOAM Basics:** [MODULE_02](../../MODULE_02_OPENFOAM_BASICS/) - Understanding case structure
- **Post-Processing:** [MODULE_05](../../MODULE_05_OPENFOAM_PROGRAMMING/) - Custom function objects
- **Turbulence Modeling:** [MODULE_04](../../MODULE_04_TURBULENCE_MODELING/) - Interpreting turbulence fields

### External Resources
- [ParaView Documentation](https://docs.paraview.org/)
- [Matplotlib Gallery](https://matplotlib.org/stable/gallery/)
- [Blender Manual](https://docs.blender.org/manual/en/latest/)

---

## 📚 Additional Resources
แหล่งข้อมูลเพิ่มเติม

### Sample Datasets
- [OpenFOAM Tutorials](https://github.com/OpenFOAM/OpenFOAM-dev/tree/master/tutorials)
- [ParaView Example Data](https://www.paraview.org/files/data/)

### Keyboard Shortcut Cheatsheets
- **ParaView:** Common shortcuts (Ctrl+R=Reset, Ctrl+S=Save State, Space=Play)
- **Blender:** Essential shortcuts (G=Grab, R=Rotate, Tab=Edit Mode)

### Troubleshooting FAQ
See Appendix A in each chapter for common issues and solutions