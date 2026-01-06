# DeepSeek V3 Content Expansion Template

## Purpose
รับ **Technical Skeleton** จาก DeepSeek R1 แล้ว **Expand** เป็น Full "Hardcore" Lesson

## CRITICAL: Content Length Requirements

> [!IMPORTANT]
> **เนื้อหาต้องยาวอย่างน้อย 1500 บรรทัด**
> - Theory Section: 300+ บรรทัด
> - OpenFOAM Reference: 400+ บรรทัด (รวม code snippets)
> - Class Design: 200+ บรรทัด
> - Implementation: 400+ บรรทัด (C++ code)
> - Build & Test: 150+ บรรทัด
> - Concept Checks: 100+ บรรทัด

---

## Output Structure (8 Main Sections)

### 1. Frontmatter + Title
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

### 2. วัตถุประสงค์การเรียนรู้ (Learning Objectives)
- **4-6 objectives** แต่ละอันมี:
  - Action verb (เข้าใจ/Understand, ออกแบบ/Design, Implement, ทดสอบ/Test)
  - Topic ที่เฉพาะเจาะจง
  - สมการหรือ code ที่เกี่ยวข้อง

### 3. Section 1: ทฤษฎี (Theory) - 300+ บรรทัด
**Sub-sections ที่ต้องมี:**

#### 1.1 พื้นฐานทางคณิตศาสตร์
- สมการหลักพร้อม LaTeX
- คำอธิบายแต่ละ variable (ตาราง)
- Physical meaning
- **WARNING/TIP callouts**

#### 1.2 ข้อตัดสินใจในการออกแบบ
- ตาราง trade-offs
- เหตุผลในการเลือกแนวทาง

#### 1.3 คอนเซปต์หลัก
- นิยามและช่วงค่า
- ตารางสรุป
- **Common PITFALLS table**

### 4. Section 2: OpenFOAM Reference - 400+ บรรทัด
**ต้องมี 3-5 code snippets แต่ละอันประกอบด้วย:**

```markdown
#### Snippet N: {Title}

**File:** `{path/to/file.C}`

```cpp
// Reference: OpenFOAM vXXXX
// Lines XX-XX (simplified for clarity)

// ACTUAL CODE HERE - minimum 20-30 lines per snippet
// Include comments explaining each part
```

**What This Does:**
1. {Point 1}
2. {Point 2}
3. {Point 3}

> [!TIP] **Key Takeaway for Your Engine**
> {Important lesson to apply}
```

**เปรียบเทียบ:**
- สิ่งที่เราเรียนรู้ได้ (What We Can LEARN) - 5+ points
- สิ่งที่เราจะทำต่างออกไป (What We Do DIFFERENTLY) - Table

### 5. Section 3: Class Design - 200+ บรรทัด
**ต้องมี:**

#### Mermaid Class Diagram (Complete)
```mermaid
classDiagram
    class ClassName {
        +Type memberVar
        +Type methodName()
    }
    // All classes with relationships
```

#### Class Specifications (For each class)
- วัตถุประสงค์ (Purpose)
- ตาราง Member Variables (Name | Type | Purpose)
- Key Methods พร้อม signature

#### Design Rationale
- ทำไมถึงออกแบบแบบนี้?
- ความแตกต่างจาก OpenFOAM (Table)

### 6. Section 4: Implementation - 400+ บรรทัด
**ต้องมี:**

#### 4.1 ไฟล์ Header (.H)
- Complete header file (100+ lines)
- Comments อธิบายแต่ละส่วน

#### 4.2 ไฟล์ Implementation (.C)
- Complete implementation (250+ lines)
- ทุก method ต้องมี implementation
- CRITICAL: ต้อง implement expansion term ในสมการ pressure

#### 4.3 Implementation Notes
- Critical implementation details
- How to avoid divergence
- Common bugs table

### 7. Section 5: Build & Test - 150+ บรรทัด
**ต้องมี:**

#### 5.1 Build Instructions
- Prerequisites table
- CMakeLists.txt (complete)
- Build commands
- Common issues table

#### 5.2 Unit Tests
- 5-8 test functions
- Complete test code
- Expected output

#### 5.3 Validation
- Analytical benchmark
- Expected results table

### 8. Section 6: Concept Checks - 100+ บรรทัด
**4-6 questions แต่ละอันมี:**

```markdown
### คำถาม N: {Question in Thai}

> **คำตอบ:**
> {Detailed answer - minimum 10 lines}
> - Bullet points for key concepts
> - Equations where relevant
> - Implementation notes
> - Code references
```

### 9. References & Related Days
- เอกสารอ้างอิง (3-5 references)
- บทเรียนที่เกี่ยวข้อง (Previous/Next/See also)

---

## Callout Types to Use

```markdown
> [!WARNING] **Title**
> Critical information - ถ้าทำผิดจะมีปัญหา

> [!TIP] **Title**
> Best practice หรือ optimization

> [!INFO] **Title**
> Background context

> [!IMPORTANT] **Title**
> Key concept ที่ต้องจำ
```

---

## Format Checklist

- [ ] ความยาวรวม ≥ 1500 บรรทัด
- [ ] Learning Objectives: 4-6 items
- [ ] Theory: สมการครบ + LaTeX valid
- [ ] OpenFOAM snippets: 3-5 ตัวอย่าง (20+ lines each)
- [ ] Class diagram: Mermaid complete
- [ ] Implementation code: ≥ 300 lines total
- [ ] Unit tests: 5-8 tests
- [ ] Concept checks: 4-6 questions + detailed answers
- [ ] Callouts: WARNING, TIP, INFO, IMPORTANT
- [ ] Tables: Trade-offs, Pitfalls, Variables
- [ ] Bilingual headers: Thai + English

---

## Prompt for V3

```
คุณคือ CFD Professor ที่กำลังเขียน "Hardcore" learning material

**CRITICAL REQUIREMENT:**
เนื้อหาต้องยาวอย่างน้อย 1500 บรรทัด - นี่คือข้อบังคับที่ต้องทำตาม

**Input:** JSON skeleton จาก R1 Analysis

**Your Task:**
Expand skeleton เป็น Full Lesson โดย:

1. **Theory Section (300+ lines):**
   - ขยายทุก equation ให้มีคำอธิบายละเอียด
   - เพิ่ม physical meaning
   - ใส่ WARNING/TIP callouts
   - ตาราง variables

2. **OpenFOAM Reference (400+ lines):**
   - 3-5 code snippets (20+ lines each)
   - อธิบาย "What This Does" ทุก snippet
   - เปรียบเทียบกับ Your Engine

3. **Class Design (200+ lines):**
   - Complete Mermaid classDiagram
   - ระบุ member variables และ methods ครบ
   - อธิบาย design rationale

4. **Implementation (400+ lines):**
   - C++ code เต็ม (Header + Implementation)
   - Comment ทุกส่วนสำคัญ
   - ระบุ CRITICAL implementation details

5. **Build & Test (150+ lines):**
   - CMakeLists.txt complete
   - Unit tests 5-8 functions
   - Validation case

6. **Concept Checks (100+ lines):**
   - 4-6 questions
   - คำตอบละเอียด (10+ lines each)

**JSON Skeleton:**
{R1_OUTPUT}

**Output:**
Complete Markdown file - ALL sections - minimum 1500 lines
```
