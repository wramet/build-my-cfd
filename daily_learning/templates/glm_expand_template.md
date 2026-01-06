# GLM 4.7 Content Expansion Template

## Purpose
รับ **Technical Skeleton** จาก DeepSeek R1 แล้ว **Expand** เป็น Full "Hardcore" Lesson ที่มี:
- รายละเอียดครบถ้วน
- Code snippets เต็มรูปแบบ
- คำอธิบายเชิงลึก
- Mermaid diagrams
- Engineering Thai + English bilingual

## Input
JSON skeleton จาก DeepSeek R1

## Output Structure

### 1. Frontmatter (YAML)
```yaml
---
tags: [cfd-engine, evaporator, day-{N}]
date: 2026-01-{DD}
aliases: [{Title}]
difficulty: hardcore
topic: {Topic}
project: CFD Engine Development (90 Days)
---
```

### 2. Main Title
```markdown
# {Title}
## CFD Engine Development - 2026-01-{DD}
```

### 3. วัตถุประสงค์การเรียนรู้ (Learning Objectives)
**Format:**
```markdown
## วัตถุประสงค์การเรียนรู้ (Learning Objectives)

After this lesson, you will be able to:
- **{Verb Thai} ({Verb English})** {Topic description} ({Equation if applicable})
- **{Verb Thai} ({Verb English})** {Topic description}
- ...
```

**Requirements:**
- 4-6 objectives ต่อบทเรียน
- แต่ละ objective ต้องมี:
  - Action verb (เข้าใจ/Understand, ออกแบบ/Design, Implement, ทดสอบ/Test)
  - Topic ที่เฉพาะเจาะจง
  - สมการหรือ code ที่เกี่ยวข้อง (ถ้ามี)

### 4. Table of Contents
```markdown
## Table of Contents
- [[#1. Theory and Design Decisions|1. Theory and Design]]
- [[#2. Reference: OpenFOAM Implementation|2. OpenFOAM Reference]]
- [[#3. Your Engine: Class Design|3. Your Class Design]]
- [[#4. Your Engine: Implementation|4. Implementation]]
- [[#5. Build and Test|5. Build and Test]]
- [[#6. Concept Checks|6. Concept Checks]]
```

### 5. Section 1: ทฤษฎีและข้อตัดสินใจในการออกแบบ

**Sub-sections ที่ต้องมี:**

#### 1.1 พื้นฐานทางคณิตศาสตร์ (Mathematical Foundation)
- สมการหลักพร้อม LaTeX formatting
- คำอธิบายแต่ละ variable
- Physical meaning ของแต่ละเทอม
- **Callout boxes** สำหรับ warnings/tips

**Example:**
```markdown
#### Continuity Equation with Phase Change

$$
\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho U) = 0
$$

For incompressible phases with phase change:

$$
\nabla \cdot U = \dot{m} \left( \frac{1}{\rho_v} - \frac{1}{\rho_l} \right)
$$

Where:
- $\dot{m}$ = mass transfer rate per unit volume [kg/m³·s]
- $\rho_v$ = vapor density [kg/m³]
- $\rho_l$ = liquid density [kg/m³]

> [!WARNING] **ผลกระทบที่สำคัญ (Critical Implication)**
> เทอมทางด้านขวา **ไม่เป็นศูนย์ (NOT zero)**!
```

#### 1.2 ข้อตัดสินใจในการออกแบบ (Design Decisions)
- ตารางเปรียบเทียบ trade-offs
- เหตุผลในการเลือกแนวทาง
- **Common PITFALLS** table

#### 1.3 คอนเซปต์หลัก (Key Concepts)
- นิยามและช่วงค่า
- ตารางสรุป

### 6. Section 2: อ้างอิง OpenFOAM Implementation

**Sub-sections ที่ต้องมี:**

#### 2.1 แนวทางของ OpenFOAM
- ตาราง Key Classes และ Location
- วิธีที่ OpenFOAM implement

#### 2.2 ข้อมูลเชิงลึก (Key Insights)
**Format 2 คอลัมน์:**
- สิ่งที่เราเรียนรู้ได้ (What We Can LEARN)
- สิ่งที่เราจะทำต่างออกไป (What We Do DIFFERENTLY)

#### 2.3 ตัวอย่างโค้ด (Code Snippets)
**Requirements:**
- 3-5 snippets ต่อบทเรียน
- แต่ละ snippet ต้องมี:
  - File location comment
  - Code block with syntax highlighting
  - "What This Does" explanation
  - "Key Takeaway for Your Engine" callout

**Example:**
```markdown
#### Snippet 1: Pressure Equation with Phase Change Source

**File:** `applications/solvers/multiphase/interPhaseChangeFoam/interPhaseChangeFoam.C`

```cpp
// Reference: OpenFOAM v2112, interPhaseChangeFoam.C
while (pimple.correct())
{
    // Calculate mass transfer rate - CRITICAL expansion term!
    volScalarField::Internal mDotAlpha
    (
        phaseChangeModel->mDotAlpha()
    );

    // Pressure equation with phase change source
    fvScalarMatrix pEqn
    (
        fvm::laplacian(rAUf, p)
      == fvc::div(phiHbyA)
      + mDotAlpha      // <-- PHASE CHANGE SOURCE TERM
    );
    
    pEqn.solve();
}
``​`

**What This Does:**
1. Computes mass transfer rate from phase change model
2. Adds `mDotAlpha` as source term in pressure equation
3. Accounts for volume expansion when liquid → vapor

> [!TIP] **Key Takeaway for Your Engine**
> Pressure equation **MUST** include expansion source term
```

### 7. Section 3: การออกแบบ Class ของ Engine คุณ

**Sub-sections ที่ต้องมี:**

#### 3.1 แผนภาพคลาส (Class Diagram)
**Mermaid classDiagram** ที่แสดง:
- Classes ทั้งหมด
- Relationships (inheritance, composition)
- Key methods และ member variables

**Example:**
```markdown
```mermaid
classDiagram
    class Mesh {
        +int nCells
        +int nFaces
        +Vector~3~* cellCenters
        +readMesh(filename)
        +getCellNeighbors(cellId)
    }

    class Field {
        <<abstract>>
        +string name
        +Mesh* mesh
        +scalar* data
    }

    class Solver {
        +Mesh* mesh
        +ScalarField* p
        +VectorField* U
        +solveMomentum()
        +solvePressure()
    }

    Field <|-- ScalarField
    Field <|-- VectorField
    Solver *-- Mesh
    Solver *-- ScalarField
``​`
```

#### 3.2 รายละเอียดคลาส (Class Specifications)
**สำหรับแต่ละ class:**
- วัตถุประสงค์ (Purpose)
- ตาราง Member Variables
- Key Methods พร้อม signature

#### 3.3 เหตุผลในการออกแบบ (Design Rationale)
- ทำไมถึงออกแบบแบบนี้?
- ความแตกต่างจาก OpenFOAM
- Trade-offs ที่ยอมรับ

### 8. Section 4: Implementation

**Sub-sections ที่ต้องมี:**

#### 4.1 ไฟล์ Header (.H)
- Complete header file
- Comments อธิบายแต่ละส่วน

#### 4.2 ไฟล์ Implementation (.C)
- Complete implementation
- **Minimum 300-500 lines** of commented code
- ทุก method ต้องมี implementation

#### 4.3 บันทึกการ Implement (Implementation Notes)
- Critical implementation details
- How to avoid divergence
- Memory management
- Common bugs และ prevention

### 9. Section 5: Build and Test

**Sub-sections ที่ต้องมี:**

#### 5.1 คำแนะนำการ Build
- Prerequisites table
- CMakeLists.txt
- Build commands
- Common build issues table

#### 5.2 Unit Tests
- Test framework setup
- 5-8 test functions ต่อบทเรียน
- Complete test code

#### 5.3 การตรวจสอบความถูกต้อง (Validation)
- Validation strategy
- Analytical benchmark case
- Expected results table
- Validation script

### 10. Section 6: Concept Checks

**Format:**
```markdown
### คำถาม 1: {Question in Thai}

> **คำตอบ:**
> {Detailed answer with:}
> - Bullet points for key concepts
> - Equations where relevant
> - Implementation notes
> - Code references
```

**Requirements:**
- 4-6 questions ต่อบทเรียน
- คำตอบต้องละเอียด (5-10 บรรทัดขึ้นไป)
- อ้างอิง code หรือ equation

### 11. Section 7-8: References and Related Days

```markdown
## 7. เอกสารอ้างอิง (References)
- OpenFOAM Source: $FOAM_SRC
- "The Finite Volume Method in CFD" - Moukalled et al.
- CFD-Online Wiki

## 8. บทเรียนที่เกี่ยวข้อง (Related Days)
- ก่อนหน้า: [[{Previous Day}]]
- ถัดไป: [[{Next Day}]]
- See also: [[90_day_roadmap]], [[CFD_basics]]
```

---

## Quality Checklist for GLM Output

- [ ] ความยาวรวม ≥ 1500 บรรทัด
- [ ] Learning Objectives: 4-6 items
- [ ] Theory sections: สมการครบ + คำอธิบาย
- [ ] OpenFOAM snippets: 3-5 ตัวอย่าง
- [ ] Class diagram: Mermaid complete
- [ ] Implementation code: ≥ 300 lines
- [ ] Unit tests: 5-8 tests
- [ ] Concept checks: 4-6 questions + detailed answers
- [ ] Callouts: WARNING, TIP, INFO, IMPORTANT
- [ ] Tables: Trade-offs, Pitfalls, Variables
- [ ] Bilingual headers: Thai + English
- [ ] Wiki-links: [[]] format ใน TOC

---

## Prompt Template for GLM

```
คุณคือ CFD Professor ที่กำลังเขียน "Hardcore" learning material

**Input:** JSON skeleton จาก DeepSeek R1 (แนบด้านล่าง)

**Your Task:**
Expand skeleton เป็น Full Lesson ตาม template ด้านบน โดย:

1. **Theory Section:**
   - ขยายทุก equation ให้มีคำอธิบายละเอียด
   - เพิ่ม physical meaning
   - ใส่ WARNING/TIP callouts

2. **OpenFOAM Reference:**
   - เขียน code snippets เต็มรูปแบบ
   - อธิบาย "What This Does" ทุก snippet
   - เปรียบเทียบกับ Your Engine

3. **Class Design:**
   - สร้าง Mermaid classDiagram
   - ระบุ member variables และ methods ครบ
   - อธิบาย design rationale

4. **Implementation:**
   - เขียน C++ code เต็ม (Header + Implementation)
   - Comment ทุกส่วนสำคัญ
   - ระบุ CRITICAL implementation details

5. **Build & Test:**
   - CMakeLists.txt
   - Unit tests ครบ
   - Validation case

6. **Concept Checks:**
   - ขยายคำตอบให้ละเอียด
   - อ้างอิง code line numbers

**Output:**
Markdown file ที่พร้อมใช้งาน - ครบทุก section ตาม template

**JSON Skeleton:**
{R1_OUTPUT_JSON}
```
