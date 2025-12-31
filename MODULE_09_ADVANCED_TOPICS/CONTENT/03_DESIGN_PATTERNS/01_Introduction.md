# Design Patterns - Pattern Fundamentals

บรรยายพื้นฐานของ Design Patterns (Pattern Fundamentals)

---

## 🎯 Learning Objectives

- ทำความเข้าใจความหมายและองค์ประกอบของ Design Pattern
- จำแนกประเภทของ patterns ได้ถูกต้อง (Creational, Structural, Behavioral)
- เข้าใจหลักการและวัตถุประสงค์ของแต่ละ category
- สามารถเลือก pattern ที่เหมาะสมกับปัญหาได้
- เข้าใจ pattern selection criteria และ trade-offs

---

## 📋 Prerequisites

- **พื้นฐาน C++:** Classes, inheritance, virtual functions
- **ความเข้าใจ OOP:** Encapsulation, polymorphism
- **ประสบการณ์ OpenFOAM:** เคยใช้ Model::New(), functionObjects มาก่อน
- **Module ที่แนะนำ:** 
  - [01_Template_Programming](../../MODULE_09_ADVANCED_TOPICS/CONTENT/01_TEMPLATE_PROGRAMMING/00_Overview.md)
  - [02_Inheritance_Polymorphism](../../MODULE_09_ADVANCED_TOPICS/CONTENT/02_INHERITANCE_POLYMORPHISM/00_Overview.md)

---

## 📖 Overview

### What are Design Patterns?

**Design Pattern** คือ **reusable solution** สำหรับ **common design problems** ที่เกิดขึ้นซ้ำๆ ใน software design

```
┌─────────────────────────────────────────────────┐
│           Design Pattern = Solution             │
├─────────────────────────────────────────────────┤
│  • ไม่ใช่ code ที่ copy-paste ได้ทันที        │
│  • เป็น template/blueprint ของ solution         │
│  • สามารถ adapt ให้เข้ากับ context ได้        │
│  • มีชื่อและความหมายที่ standard            │
└─────────────────────────────────────────────────┘
```

### Why Use Patterns?

| Aspect | Benefit | Context |
|--------|---------|---------|
| **Proven Solutions** | ได้รับการทดสอบแล้วใน production systems | ลดความเสี่ยงในการออกแบบ |
| **Common Vocabulary** | ใช้ชื่อ pattern สื่อสารกัน | "ใช้ Factory ที่นี่" → เข้าใจทันที |
| **Maintainability** | Structure ชัดเจน | ง่ายต่อการแก้ไขและ extend |
| **Flexibility** | แยกส่วนที่เปลี่ยนแปลงได้ | ง่ายต่อการเพิ่ม variants |
| **Documentation** | Pattern เป็นเอกสารประกอบ | บอก intent ของ design |

### How to Apply Patterns?

1. **Identify Problem:** ระบุปัญหาที่เจอ (ขยาย, รักษา, coupling สูง)
2. **Select Pattern:** เลือก pattern ที่แก้ปัญหานั้น
3. **Adapt Solution:** ปรับให้เข้ากับ context ของ OpenFOAM
4. **Verify:** ตรวจสอบว่าแก้ปัญหาจริงหรือไม่

---

## 📚 Main Content

---

## 1. Pattern Classification

Design patterns ถูกจัดแบ่งเป็น **3 main categories** ตาม **purpose** ของ pattern:

```
┌─────────────────────────────────────────────────────────────┐
│                  Design Pattern Categories                   │
├──────────────────┬──────────────────┬──────────────────────┤
│   Creational     │    Structural    │     Behavioral       │
├──────────────────┼──────────────────┼──────────────────────┤
│  Focus: Creation │  Focus: Structure│  Focus: Interaction  │
│  of objects      │  of classes      │  & responsibility    │
├──────────────────┼──────────────────┼──────────────────────┤
│  • Factory       │  • Adapter       │  • Strategy          │
│  • Singleton     │  • Bridge        │  • Observer          │
│  • Builder       │  • Composite     │  • Template Method   │
│  • Prototype     │  • Facade        │  • Command           │
├──────────────────┼──────────────────┼──────────────────────┤
│  Hides creation  │  Composes        │  Defines             │
│  logic           │  structures      │  communication       │
└──────────────────┴──────────────────┴──────────────────────┘
```

---

## 2. Creational Patterns (รูปแบบการสร้าง)

### Purpose
**ยุบงาน (abstract) การสร้าง object** ทำให้ระบบไม่ต้องรู้ว่า object ถูกสร้างอย่างไร

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Decoupling** | แยก code ที่ใช้ object ออกจาก code ที่สร้าง object |
| **Configuration-Driven** | สร้าง object จาก config/data ไม่ใช่ hardcode |
| **Type Flexibility** | เปลี่ยน type ได้โดยไม่แก้ code ที่ใช้ |

### Common Creational Patterns

#### 2.1 Factory Method
- **Intent:** กำหนด interface สำหรับสร้าง object แต่ปล่อยให้ subclasses decide สร้างอะไร
- **OpenFOAM Context:** `Model::New(dict)` - สร้าง model จาก typeName

#### 2.2 Abstract Factory
- **Intent:** interface สำหรับสร้าง families ของ related objects
- **OpenFOAM Context:** สร้าง sets ของ related boundary conditions

#### 2.3 Singleton
- **Intent:** รับประกันว่า class มีได้ instance เดียว
- **OpenFOAM Context:** `Time` database, objectRegistry

#### 2.4 Builder
- **Intent:** สร้าง complex objects ทีละ step
- **OpenFOAM Context:** สร้าง mesh ด้วย blockMesh, snappyHexMesh

#### 2.5 Prototype
- **Intent:** สร้าง objects โดย clone จาก prototype
- **OpenFOAM Context:** clone boundary conditions

### When to Use Creational Patterns?

| Scenario | Recommended Pattern |
|----------|---------------------|
| สร้าง object จาก dictionary/config | **Factory** |
| มี type selection จาก user | **Factory** |
| ต้องการ single instance | **Singleton** |
| สร้าง complex object หลาย steps | **Builder** |
| clone objects บ่อยๆ | **Prototype** |

---

## 3. Structural Patterns (รูปแบบโครงสร้าง)

### Purpose
**จัดโครงสร้าง classes** เพื่อ:
- จัดกลุ่ม objects เป็น larger structures
- ทำให้ interfaces ที่แตกต่างทำงานร่วมกันได้
- ลด coupling ระหว่าง components

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Composition** | รวม objects เพื่อสร้าง functionality |
| **Interface Adaptation** | แปลง interfaces ให้ compatible |
| **Decoupling** | แยก abstraction จาก implementation |

### Common Structural Patterns

#### 3.1 Adapter
- **Intent:** แปลง interface ของ class หนึ่งให้เข้ากับ interface ที่ client ต้องการ
- **OpenFOAM Context:** ทำให้ external libraries integrate กับ OpenFOAM

#### 3.2 Bridge
- **Intent:** แยก abstraction ออกจาก implementation เพื่อให้เปลี่ยนแปลงได้独立
- **OpenFOAM Context:** แยก interface ของ solver จาก implementation ที่แตกต่าง

#### 3.3 Composite
- **Intent:** รวม objects ให้ทำงานเหมือน single object
- **OpenFOAM Context:** mesh boundary conditions (patch ประกอบด้วย faces)

#### 3.4 Facade
- **Intent:** ให้ simplified interface ของ complex subsystem
- **OpenFOAM Context:** `fvSolution`, `fvSchemes` เป็น facade สำหรับ complex solver settings

#### 3.5 Proxy
- **Intent:** ให้ placeholder/representative สำหรับ object อื่น
- **OpenFOAM Context:** lazy evaluation, access control

### When to Use Structural Patterns?

| Scenario | Recommended Pattern |
|----------|---------------------|
| ต้องการ integrate ระบบเดิมที่ interface ไม่ตรง | **Adapter** |
| แยก interface จาก implementation | **Bridge** |
| จัดการ hierarchies ของ objects | **Composite** |
| ลดความซับซ้อนของ subsystem | **Facade** |
| ควบคุม access หรือ lazy load | **Proxy** |

---

## 4. Behavioral Patterns (รูปแบบพฤติกรรม)

### Purpose
**จัดการ communication และ responsibility** ระหว่าง objects

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Algorithm Encapsulation** | ซ่อน implementation ของ algorithm |
| **Event Handling** | จัดการ reactions ต่อ events |
| **Behavior Extension** | เพิ่ม/เปลี่ยน behavior ได้อย่างยืดหยุ่น |

### Common Behavioral Patterns

#### 4.1 Strategy
- **Intent:** กำหนด family ของ algorithms ทำให้ interchangeable
- **OpenFOAM Context:** `fvSchemes` - สลับ discretization schemes ได้

#### 4.2 Observer
- **Intent:** กำหนด one-to-many dependency เมื่อ object เปลี่ยน → dependents ได้รับแจ้ง
- **OpenFOAM Context:** `functionObjects` - monitor และ react ต่อ solver state

#### 4.3 Template Method
- **Intent:** กำหนด skeleton ของ algorithm ปล่อยให้ subclasses implement บาง steps
- **OpenFOAM Context:** `solver::run()` - กำหนด workflow ของ time loop

#### 4.4 Command
- **Intent:** แปลง requests เป็น objects
- **OpenFOAM Context:** functionObject commands

#### 4.5 Iterator
- **Intent:** ให้ access ไปยัง elements ของ aggregate โดยไม่เปิด暴露 representation
- **OpenFOAM Context:** mesh iterators (`forAll()`, cell loops)

#### 4.6 State
- **Intent:** ทำให้ object เปลี่ยน behavior เมื่อ state เปลี่ยน
- **OpenFOAM Context:** solver states (initial, running, finished)

### When to Use Behavioral Patterns?

| Scenario | Recommended Pattern |
|----------|---------------------|
| มีหลาย algorithms ที่ต้องสลับได้ | **Strategy** |
| ต้องการ reactions ต่อ events | **Observer** |
| มี algorithm skeleton ที่เหมือนกัน | **Template Method** |
| ต้องการ queue/log commands | **Command** |
| ต้องการ traverse collections | **Iterator** |
| behavior เปลี่ยนตาม state | **State** |

---

## 5. Pattern Selection Framework

### Decision Tree

``                    เริ่มต้น
                        │
        ┌───────────────┴───────────────┐
        │       What Problem?          │
        └───────────────┬───────────────┘
                        │
    ┌───────────────────┼───────────────────┐
    │                   │                   │
    │               Creational?          Structural?       Behavioral?
    │                   │                   │                   │
    │           ┌───────┴───────┐   ┌───────┴───────┐   ┌───────┴───────┐
    │           │               │   │               │   │               │
    │       Object          Interface         Object          Communication
    │       Creation        Mismatch         Composition     Responsibilities
    │           │               │               │               │
    │       Factory          Adapter          Composite       Strategy
    │       Builder          Bridge           Facade          Observer
    │       Singleton        Proxy                            Template
    │                                                        Command
    │                                                        Iterator
    └                                                        State
```

### Selection Criteria Matrix

| Problem Dimension | Creational | Structural | Behavioral |
|-------------------|------------|------------|------------|
| **Flexibility** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Complexity** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Performance** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Maintainability** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **OpenFOAM Fit** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 6. Pattern Fundamentals in OpenFOAM

### Why Patterns Matter in OpenFOAM?

OpenFOAM เป็น framework ที่ต้องการ:
- **Extensibility:** เพิ่ม models, schemes, boundary conditions ได้
- **Configurability:** เลือก implementations จาก dictionaries
- **Modularity:** แยก physics จาก numerics จาก I/O

ดังนั้น patterns จึงถูกนำมาใช้อย่างแพร่หลาย

### Core Patterns in OpenFOAM Architecture

| Pattern | Usage in OpenFOAM | Frequency |
|---------|-------------------|-----------|
| **Factory** | RTOS, Model::New() | ⭐⭐⭐⭐⭐ |
| **Strategy** | discretization schemes | ⭐⭐⭐⭐⭐ |
| **Observer** | functionObjects | ⭐⭐⭐⭐ |
| **Template Method** | solver workflows | ⭐⭐⭐⭐ |
| **Facade** | dictionary systems | ⭐⭐⭐ |
| **Composite** | mesh structures | ⭐⭐⭐ |

---

## 🎯 Key Takeaways

### Core Concepts
1. **Design Pattern** = Reusable solution สำหรับ common problems ไม่ใช่ code ที่ copy-paste
2. **3 Categories** ของ patterns:
   - **Creational:** จัดการ object creation
   - **Structural:** จัดโครงสร้าง classes
   - **Behavioral:** จัดการ communication & responsibility

### Pattern Selection
3. เลือก pattern ตาม **problem type**:
   - Object creation → Creational
   - Structure/composition → Structural
   - Behavior/interaction → Behavioral

### OpenFOAM Context
4. OpenFOAM ใช้ patterns อย่างแพร่หลายเพื่อ **extensibility** และ **configurability**
5. ที่สำคัญที่สุด: **Factory** (RTOS) และ **Strategy** (schemes, models)

### Design Principles
6. Patterns คือ **tools** ไม่ใช่ goals — ใช้เมื่อแก้ปัญหาจริง
7. Over-engineering → ใช้ pattern เกินไป → code ซับซ้อน
8. Patterns guarantee **structure**, ไม่ guarantee **performance**

---

## 📋 Quick Reference

### Pattern Categories Summary

| Category | Focus | Key Benefit | Common Use |
|----------|-------|-------------|------------|
| **Creational** | Object creation | Decoupling creation from use | Model::New(), RTOS |
| **Structural** | Class composition | Flexible structures | Adapters, Facades |
| **Behavioral** | Object interaction | Encapsulate behavior | Schemes, functionObjects |

### Selection Guide

```
Need to create objects from config? → Factory
Need interchangeable algorithms? → Strategy
Need to react to events? → Observer
Have algorithm skeleton? → Template Method
Need to integrate incompatible interfaces? → Adapter
```

---

## 🧠 Concept Check

<details>
<summary><b>1. Design Pattern คืออะไร? (What is a Design Pattern?)</b></summary>

**Design Pattern** คือ reusable solution สำหรับ common design problems
- เป็น template/blueprint ไม่ใช่ code ที่ copy-paste
- มีชื่อและความหมายที่ standard
- สามารถ adapt ให้เข้ากับ context ได้

</details>

<details>
<summary><b>2. Design patterns แบ่งเป็นกี่ categories และอะไรบ้าง?</b></summary>

แบ่งเป็น **3 categories** ตาม purpose:
- **Creational:** จัดการ object creation (Factory, Singleton, Builder)
- **Structural:** จัดโครงสร้าง classes (Adapter, Composite, Facade)
- **Behavioral:** จัดการ communication (Strategy, Observer, Template Method)

</details>

<details>
<summary><b>3. Creational patterns ใช้ทำอะไร? และมีตัวอย่างใน OpenFOAM อะไรบ้าง?</b></summary>

**Purpose:** Abstract object creation ทำให้ไม่ต้องรู้ว่า object ถูกสร้างอย่างไร

**OpenFOAM Examples:**
- `autoPtr<turbulenceModel> turb = turbulenceModel::New(dict);` (Factory)
- `Time` database (Singleton)
- mesh construction (Builder)

</details>

<details>
<summary><b>4. Structural patterns แตกต่างจาก Creational patterns อย่างไร?</b></summary>

| Aspect | Creational | Structural |
|--------|------------|------------|
| **Focus** | Object creation | Class composition |
| **Purpose** | Decouple creation | Compose structures |
| **Example** | Factory | Adapter, Composite |

</details>

<details>
<summary><b>5. Behavioral patterns ใช้ในสถานการณ์ไหน?</b></summary>

ใช้เมื่อต้องจัดการ:
- **Communication:** วิธี objects สื่อสารกัน (Observer)
- **Algorithms:** วิธี encapsulate/interchange algorithms (Strategy)
- **Workflows:** วิธี define algorithm skeletons (Template Method)

**OpenFOAM Examples:**
- `fvSchemes` → Strategy
- `functionObjects` → Observer
- `solver::run()` → Template Method

</details>

<details>
<summary><b>6. Patterns guarantee performance ไหม?</b></summary>

**ไม่** — Design patterns focus on **structure** และ **maintainability**:
- ✅ Organize code ให้ชัดเจน
- ✅ ทำให้ extend ได้ง่าย
- ❌ ไม่ guarantee ว่าจะเร็วขึ้น
- ❌ บาง patterns อาจมี overhead (เช่น virtual calls)

</details>

<details>
<summary><b>7. เลือก pattern อย่างไร? (How to select a pattern?)</b></summary>

ใช้ **problem-driven approach**:
1. **Identify problem:** ปัญหาที่เจอ (coupling สูง, ยากต่อการ extend)
2. **Match category:**
   - Object creation → Creational
   - Structure issues → Structural
   - Behavior issues → Behavioral
3. **Select specific pattern:** เลือก pattern ที่แก้ปัญหานั้น
4. **Verify:** ตรวจสอบว่าแก้ปัญหาจริง

</details>

---

## 📖 Related Documents

### Within This Module
- **Overview:** [00_Overview.md](00_Overview.md) — High-level summary และ pattern map
- **Factory Pattern:** [02_Factory_Pattern.md](02_Factory_Pattern.md) — Deep dive into Factory
- **Strategy Pattern:** [03_Strategy_Pattern.md](03_Strategy_Pattern.md) — Deep dive into Strategy
- **Pattern Synergy:** [04_Pattern_Synergy.md](04_Pattern_Synergy.md) — Pattern combinations

### Prerequisite Modules
- **Template Programming:** [../../MODULE_09_ADVANCED_TOPICS/CONTENT/01_TEMPLATE_PROGRAMMING/00_Overview.md](../../MODULE_09_ADVANCED_TOPICS/CONTENT/01_TEMPLATE_PROGRAMMING/00_Overview.md)
- **Inheritance & Polymorphism:** [../../MODULE_09_ADVANCED_TOPICS/CONTENT/02_INHERITANCE_POLYMORPHISM/00_Overview.md](../../MODULE_09_ADVANCED_TOPICS/CONTENT/02_INHERITANCE_POLYMORPHISM/00_Overview.md)

### Further Reading
- **Design Patterns:** Elements of Reusable Object-Oriented Software (Gang of Four)
- **OpenFOAM Code:** `$FOAM_SRC/OpenFOAM/db/RunTimeSelection/` — RTOS implementation