# Project Organization

การจัดระเบียบโปรเจค

---

## Learning Objectives

เป้าหมายการเรียนรู้

After completing this section, you will be able to:

- **Design** efficient OpenFOAM project directory structures
- **Apply** consistent naming conventions for cases, scripts, and results
- **Create** reusable case templates to streamline workflow
- **Organize** scripts logically by function (run/post/utils)

หลังจากส่วนนี้ คุณจะสามารถ:

- **ออกแบบ** โครงสร้างไดเรกทอรีโปรเจค OpenFOAM ที่มีประสิทธิภาพ
- **ประยุกต์** รูปแบบการตั้งชื่อที่สอดคล้องกัน
- **สร้าง** เทมเพลตกรณีศึกษาที่ใช้ซ้ำได้
- **จัดระเบียบ** สคริปต์ตามหน้าที่การทำงาน

---

## What: Project Organization Components

อะไร: องค์ประกอบการจัดระเบียบโปรเจค

### 1. Directory Structure

โครงสร้างไดเรกทอรี

```
project/
├── cases/
│   ├── baseline/           # Reference simulation
│   └── parametric/         # Parameter variations
├── mesh/                   # Mesh files and dictionaries
├── scripts/
│   ├── run/               # Execution scripts
│   ├── post/              # Post-processing scripts
│   └── utils/             # Utility functions
├── results/               # Processed data and plots
└── docs/                  # Documentation and reports
```

### 2. Naming Convention

รูปแบบการตั้งชื่อ

| Type | Convention | Example |
|------|------------|---------|
| **Cases** | `descriptive_name` | `windTurbine_baseline`, `pipeFlow_re1000` |
| **Scripts** | `action_target.sh` | `runSimulation.sh`, `extractForces.py` |
| **Results** | `case_metric.csv` | `turbine_drag.csv`, `flowRate_data.csv` |

### 3. Case Template Structure

โครงสร้างเทมเพลตกรณีศึกษา

```
template/
├── 0/                      # Initial/boundary conditions
├── constant/               # Physical properties, mesh, transport
├── system/                 # Solver control, numerical schemes
├── Allrun                  # Automated execution script
├── Allclean                # Cleanup script
└── README.md               # Case documentation
```

### 4. Scripts Organization

การจัดระเบียบสคริปต์

```
scripts/
├── run/
│   ├── runSimulation.sh
│   └── batchRun.sh
├── post/
│   ├── extractData.py
│   └── plotResults.py
└── utils/
    ├── cleanAll.sh
    └── checkMesh.sh
```

---

## Why: Organization Matters

ทำไม: ความสำคัญของการจัดระเบียบ

### Good vs Bad Organization Patterns

รูปแบบการจัดระเบียบที่ดีและไม่ดี

| ❌ Bad Organization | ✅ Good Organization |
|---------------------|----------------------|
| `case1/`, `case2/`, `test/` | `baseline/`, `parametric_re100/`, `parametric_re200/` |
| `script.sh`, `script2.sh`, `final.sh` | `runSimulation.sh`, `extractData.py`, `plotResults.py` |
| All files in one folder | Logical separation (cases/, scripts/, results/) |
| No documentation | README.md in every case |
| Hardcoded paths | Relative paths, portable structure |

### Benefits of Good Organization

ประโยชน์ของการจัดระเบียบที่ดี

1. **Efficiency**: Find files instantly without searching
2. **Reproducibility**: Clear structure enables easy reconstruction
3. **Collaboration**: Team members understand project layout
4. **Scalability**: Easy to add new cases without chaos
5. **Automation**: Predictable paths simplify scripting

ประสิทธิภาพ ความสามารถในการทำซ้ำ การทำงานร่วมกัน การขยายขนาด และการทำงานอัตโนมัติ

---

## How: Implementation Guidelines

อย่างไร: แนวทางการปฏิบัติ

### Step 1: Create Base Structure

สร้างโครงสร้างพื้นฐาน

```bash
mkdir -p cases/{baseline,parametric}
mkdir -p mesh scripts/{run,post,utils} results docs
```

### Step 2: Build Template Case

สร้างเทมเพลตกรณีศึกษา

```bash
# Create template with minimal case structure
cp -r1$FOAM_TUTORIALS/incompressible/simpleFoam/pitzDaily template/
cd template
# Customize with your standard settings
```

### Step 3: Write Reusable Scripts

เขียนสคริปต์ที่ใช้ซ้ำได้

**scripts/run/runSimulation.sh:**
```bash
#!/bin/bash
# Usage: runSimulation.sh <caseName>
CASE_DIR=../../cases/$1
cd1$CASE_DIR
blockMesh
simpleFoam
```

### Step 4: Document Conventions

บันทึกมาตรฐานการใช้งาน

Create `docs/namingConventions.md` with team standards.

---

## Quick Reference

ข้อมูลอ้างอิงรวดเร็ว

| Folder | Purpose | Content |
|--------|---------|---------|
| **cases/** | Simulation cases | Baseline, parametric studies |
| **mesh/** | Mesh resources | Geometry files, blockMeshDict |
| **scripts/run/** | Execution | Run simulations, batch jobs |
| **scripts/post/** | Post-processing | Data extraction, plotting |
| **scripts/utils/** | Utilities | Mesh checking, cleanup |
| **results/** | Outputs | CSV data, figures, reports |
| **docs/** | Documentation | Notes, conventions, reports |

---

## Key Takeaways

สรุปสิ่งสำคัญ

**✓ Structure**: Use consistent `cases/mesh/scripts/results/docs` hierarchy  
**✓ Naming**: Apply `descriptive_name` convention for clarity  
**✓ Templates**: Create reusable case templates with Allrun/Allclean  
**✓ Scripts**: Organize by function (run/post/utils)  
**✓ Documentation**: Include README.md in every case  
**✓ Paths**: Use relative paths for portability  

โครงสร้าง การตั้งชื่อ เทมเพลต การจัดระเบียบสคริปต์ เอกสาร และเส้นทางแบบ relative

---

## 🧠 Concept Check

ทดสอบความเข้าใจ

<details>
<summary><b>1. What is the purpose of a template case?</b></summary>

**Reusability** — Copy template and modify specific settings instead of starting from scratch each time. Ensures consistency across all cases.

**การใช้งานซ้ำได้** — คัดลอกเทมเพลตและปรับเปลี่ยนการตั้งค่าเฉพาะแทนการเริ่มจากศูนย์ทุกครั้ง รับประกันความสอดคล้องกันของกรณีศึกษาทั้งหมด
</details>

<details>
<summary><b>2. Why separate scripts into run/, post/, and utils/?</b></summary>

**Logical organization** — Groups scripts by function, making them easier to find and maintain. Separates execution from post-processing and utilities.

**การจัดระเบียบตามตรรกะ** — จัดกลุ่มสคริปต์ตามหน้าที่ ทำให้ค้นหาและบำรุงรักษาง่าย แยกการดำเนินการจากการประมวลผลภายหลังและเครื่องมืออรรถประโยชน์
</details>

<details>
<summary><b>3. ทำไมการตั้งชื่อสคริปต์ด้วยรูปแบบ action_target จึงสำคัญ?</b></summary>

**ความชัดเจน** — ทำให้ทราบทันทีว่าสคริปต์ทำอะไร เช่น `runSimulation.sh` บอกว่าใช้รันซิมูเลชัน แต่ `script.sh` ไม่บอกวัตถุประสงค์
</details>

---

## 📖 Related Documents

เอกสารที่เกี่ยวข้อง

- **Overview:** [00_Overview.md](00_Overview.md)
- **Next:** [02_Documentation_Practices.md](02_Documentation_Practices.md) — Document your organized project properly