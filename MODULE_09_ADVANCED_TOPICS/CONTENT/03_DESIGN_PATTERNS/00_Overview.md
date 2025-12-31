# Design Patterns - Overview

ภาพรวม Design Patterns ใน OpenFOAM

---

## 🎯 Learning Objectives

After completing this module, you will be able to:
- **Understand** the role of design patterns in OpenFOAM architecture
- **Identify** key patterns used throughout OpenFOAM (Factory, Strategy, Observer, etc.)
- **Apply** pattern knowledge to read and write better OpenFOAM code
- **Recognize** how patterns enable extensibility and maintainability
- **Navigate** the module structure to deepen your understanding

---

## 📋 Prerequisites

Before starting this module, you should have:
- **Basic C++ knowledge** (classes, inheritance, polymorphism)
- **OpenFOAM familiarity** (solvers, boundary conditions, dictionaries)
- **Understanding** of `fvSchemes` and `fvSolution` structure
- **Exposure** to `New()` and `autoPtr` in OpenFOAM code

---

## 📖 Overview (3W Framework)

### WHAT - Design Patterns คืออะไร?

**Design Patterns** คือ โซลูชันมาตรฐาน (proven solutions) สำหรับปัญหาที่เกิดขึ้นซ้ำๆ ในการออกแบบซอฟต์แวร์ ซึ่ง:

- ไม่ใช่โค้ดที่เขียนเสร็จแล้ว (not ready-made code)
- เป็นเทมเพลตและแนวทาง (templates and guidelines)
- อิงจากประสบการณ์และแนวปฏิบัติที่ดี (best practices)
- สื่อสารระหว่างนักพัฒนาด้วยภาษาที่เข้าใจตรงกัน

### WHY - ทำไมต้อง Design Patterns?

ใน OpenFOAM การใช้ Design Patterns ช่วย:

- **Decoupling** ลดการพึ่งพาระหว่างส่วนต่างๆ ของโค้ด
- **Extensibility** ทำให้เพิ่มโมเดล/เมธอดใหม่ได้โดยไม่แก้โค้ดเดิม
- **Maintainability** โครงสร้างชัดเจน อ่านและดูแลรักษาง่าย
- **Reusability** ใช้โค้ดซ้ำในบริบทต่างๆ ได้
- **Consistency** สถาปัตยกรรมสอดคล้องกันทั้งระบบ

### HOW - ใช้อย่างไรใน OpenFOAM?

OpenFOAM นำ Design Patterns มาใช้ในระดับสถาปัตยกรรม:

```cpp
// Factory: Create models without knowing concrete types
autoPtr<turbulenceModel> turb = turbulenceModel::New(mesh);

// Strategy: Select algorithms via dictionary
schemes.set("div(phi,U)", word("Gauss linear"));

// Observer: Function objects monitor simulation
functions { fieldAverage { type fieldAverage; } }

// Singleton: Single instance of Time, mesh registries
const Time& runTime = Time::New();
```

---

## 📚 Key Patterns in OpenFOAM

### 1. Factory Pattern

**Purpose:** Create objects without specifying exact concrete types

**OpenFOAM Use:**
- Turbulence models (`kEpsilon`, `kOmegaSST`, `SpalartAllmaras`)
- RAS/LES models from dictionary
- Boundary condition creation

```cpp
// User code doesn't know which model is used
autoPtr<turbulenceModel> turb = turbulenceModel::New(dict);

// Works with any turbulence model
turb->correct();  // Polymorphic call
```

---

### 2. Strategy Pattern

**Purpose:** Define interchangeable algorithms

**OpenFOAM Use:**
- Discretization schemes (`Gauss linear`, `upwind`, `QUICK`)
- Linear solvers (`GAMG`, `PCG`, `smoothSolver`)
- Time integration schemes (`Euler`, `backward`, `CrankNicolson`)

```cpp
// Selectable via dictionary
fvSchemes
{
    divSchemes
    {
        div(phi,U)  Gauss linear;      // Can change at runtime
        div(phi,k)  Gauss upwind;
    }
}
```

---

### 3. Template Method Pattern

**Purpose:** Define algorithm skeleton, defer steps to subclasses

**OpenFOAM Use:**
- Solver execution loop
- Time step integration structure

```cpp
class solver
{
public:
    void run()
    {
        initialize();       // Override in derived
        while (loop())
        {
            solve();        // Override in derived
            postProcess();  // Default or override
        }
    }
    
protected:
    virtual void initialize() = 0;
    virtual void solve() = 0;
    virtual void postProcess() {}
};
```

---

### 4. Observer Pattern

**Purpose:** Notify subscribers of events automatically

**OpenFOAM Use:**
- **Function objects** (`fieldAverage`, `probes`, `forces`)
- Registered observers called at each time step
- Monitoring and data collection

```cpp
// controlDict
functions
{
    fieldAverage 
    { 
        type fieldAverage; 
        fields (U p);
    }
    
    probes 
    { 
        type probes;
        probeLocations ((0 0 0));
    }
}

// Automatically called by Time::run()
```

---

### 5. Singleton Pattern

**Purpose:** Ensure single instance, global access

**OpenFOAM Use:**
- `Time` object registry
- `mesh` object registry
- Global databases (transport properties, thermophysical models)

```cpp
// Single Time instance for entire simulation
const Time& runTime = Time::New();

// Global mesh registry
const fvMesh& mesh = ...;

// Access from anywhere via reference
Info << "Time = " << runTime.timeName() << endl;
```

---

### 6. Run-Time Selection (RTS) System

**Purpose:** OpenFOAM's unique combination of Factory + Strategy + Registry

**Key Features:**
- Dictionary-driven object creation
- Automatic type registration
- Extensible without modifying core code

```cpp
// RTS enables this architecture
autoPtr<viscosityModel> visc = viscosityModel::New(dict);

// New models can be added dynamically:
// 1. Inherit from viscosityModel
// 2. Register with TypeName("myModel")
// 3. Appears in dictionary choices automatically
```

---

## 🗂️ Module Structure

| File | Content | Focus |
|------|---------|-------|
| **00_Overview.md** | This file | High-level summary of all patterns |
| **01_Introduction.md** | Pattern Fundamentals | Theory, classification, when to use |
| **02_Factory_Pattern.md** | Factory Deep Dive | `New()`, `autoPtr`, RTS mechanics |
| **03_Strategy_Pattern.md** | Strategy Deep Dive | Schemes, solvers, run-time selection |
| **04_Synergy.md** | Pattern Combinations | How patterns work together |
| **05_Performance.md** | Performance Analysis | Overhead, optimization trade-offs |
| **06_Exercise.md** | Practical Exercise | Hands-on implementation practice |

---

## 📋 Quick Reference

| Pattern | OpenFOAM Example | Key Method |
|---------|------------------|------------|
| **Factory** | `turbulenceModel::New(dict)` | `New()` |
| **Strategy** | `fvSchemes` selection | Dictionary-based |
| **Template Method** | Solver loop structure | Virtual methods |
| **Observer** | `functionObjects` | `execute()`, `write()` |
| **Singleton** | `Time`, `mesh` registries | `New()`, global access |
| **RTS** | Model creation system | `TypeName`, `New()` |

---

## ✅ Key Takeaways

### Core Concepts

1. **Design Patterns เป็นภาษาสื่อสาร** 
   - ช่วยนักพัฒนาเข้าใจสถาปัตยกรรมเดียวกัน
   - ลดเวลาเรียนรู้โค้ดที่ซับซ้อน

2. **OpenFOAM ใช้ Patterns อย่างแพร่หลาย**
   - Factory/Strategy: Model creation and configuration
   - Observer: Function objects and monitoring
   - Singleton: Global registries
   - Template Method: Solver structure

3. **RTS คือหัวใจของ OpenFOAM**
   - รวมหลาย pattern เข้าด้วยกัน
   - ทำให้ระบบขยายได้อย่างยืดหยุ่น
   - ไม่ต้องแก้โค้ดตัวเดิมเพื่อเพิ่มฟีเจอร์ใหม่

4. **เข้าใจ Patterns = เข้าใจ OpenFOAM**
   - อ่านโค้ดเข้าใจเร็วขึ้น
   - แก้บั๊กได้ง่ายขึ้น
   - เขียนโค้ดที่สอดคล้องกับสถาปัตยกรรม
   - ขยายระบบได้อย่างมีประสิทธิภาพ

### When to Use Each Pattern

| Situation | Pattern |
|-----------|---------|
| Create objects from dictionary | Factory + RTS |
| Need interchangeable algorithms | Strategy |
| Monitor/collect data during run | Observer |
| Define algorithm structure | Template Method |
| Single global instance needed | Singleton |

---

## 🧠 Concept Check

<details>
<summary><b>1. Factory pattern ช่วยอะไรใน OpenFOAM?</b></summary>

**Decouple creation from usage** — ผู้ใช้โค้ดไม่ต้องรู้ว่าสร้างโมเดลชนิดใด ทำให้เปลี่ยนโมเดลได้โดยไม่ต้องแก้โค้ด แค่แก้ dictionary

</details>

<details>
<summary><b>2. Strategy pattern ต่างจาก inheritance อย่างไร?</b></summary>

**Strategy** คือ อัลกอริทึมเป็นวัตถุแยกตัว (objects) เปลี่ยนได้ระหว่าง runtime  
**Inheritance** คือ ความสามารถคงที่ตาม class hierarchy ไม่เปลี่ยนได้หลัง compile

</details>

<details>
<summary><b>3. Function objects ใช้ pattern ไหน?</b></summary>

**Observer Pattern** — ลงทะเบียนเป็น observer กับ Time object และถูกเรียกอัตโนมัติทุก time step

</details>

<details>
<summary><b>4. Run-Time Selection (RTS) คืออะไร?</b></summary>

**ระบบเฉพาะของ OpenFOAM** ที่รวม Factory + Strategy + Registry เข้าด้วยกัน ทำให้:
- สร้าง object จาก dictionary ได้ (`New(dict)`)
- เลือก type ได้ระหว่าง runtime
- เพิ่ม type ใหม่ได้โดยไม่แก้ core code

</details>

<details>
<summary><b>5. Template Method ใช้ที่ไหนใน OpenFOAM?</b></summary>

**Solver loop structure** — กำหนดโครงร่างการวน loop (initialize → solve → converge) และให้ derived classes implement รายละเอียด

</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

### Within This Module

- **Pattern Fundamentals:** [01_Introduction.md](01_Introduction.md) — ทฤษฎีและการจำแนก patterns
- **Factory Deep Dive:** [02_Factory_Pattern.md](02_Factory_Pattern.md) — รายละเอียดและตัวอย่าง
- **Strategy Deep Dive:** [03_Strategy_Pattern.md](03_Strategy_Pattern.md) — Schemes และ solvers

### Related Modules

- **Module 5 - OpenFOAM Programming:** RTS mechanics, virtual methods, polymorphism
- **Module 6 - Advanced Physics:** How patterns enable complex model integration
- **Module 8 - Testing:** Testing pattern-based architectures

### External References

- **Design Patterns: Elements of Reusable Object-Oriented Software** (Gang of Four)
- **OpenFOAM Programmer's Guide** — Run-time selection system
- **OpenFOAM Source Code** — `$FOAM_SRC/OpenFOAM/db/RunTimeSelection/`