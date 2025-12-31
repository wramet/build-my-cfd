---
name: Quiz Generator
description: |
  Use this skill when: user asks to create a quiz, concept check, exam, or exercises for a topic.
  
  Specialist in creating educational assessments for CFD/OpenFOAM.
---

# Quiz Generator

ผู้เชี่ยวชาญด้านการออกข้อสอบและแบบฝึกหัด (Educational Assessment)

## Assessment Types

### 1. Concept Check (ท้ายบทเรียน)
- **Goal:** Quick recall & Understanding
- **Format:** 2-3 ข้อ พร้อมเฉลยแบบซ่อน (Hidden Answer)
- **Difficulty:** Easy/Medium

### 2. Calculation Problem (คำนวณมือ)
- **Goal:** เข้าใจที่มาของสมการ
- **Format:** โจทย์สถานการณ์ + ตัวเลขง่ายๆ
- **Example:** คำนวณ Re, y+, Courant Number, หรือ GCI

### 3. Code Analysis (วิเคราะห์โค้ด)
- **Goal:** Spot the bug / Explain the logic
- **Format:** ให้ Code snippet มาแล้วถามว่า "ทำไมบรรทัดนี้ถึงสำคัญ?" หรือ "โค้ดนี้ผิดตรงไหน?"

### 4. Challenge (โปรเจกต์)
- **Goal:** Synthesis
- **Format:** โจทย์ปลายเปิดให้ไปทำต่อเอง

## Quiz Template

### Concept Check Template

```markdown
### Concept Check

1. **คำถาม:** ทำไมเราถึงต้องใช้... ?
   <details>
   <summary>เฉลย</summary>
   
   **ตอบ:** เพราะว่า ...
   </details>

2. **คำถาม:** ...
```

### Code Quiz Template

```markdown
### Code Analysis

พิจารณาโค้ดส่วนนี้:
```cpp
// บรรทัดนี้ทำหน้าที่อะไร?
fvScalarMatrix TEqn
(
    fvm::ddt(T)
  + fvm::div(phi, T)
  - fvm::laplacian(DT, T)
);
```

<details>
<summary>เฉลย</summary>

**คำตอบ:** นี่คือการสร้าง Linear System สำหรับสมการ Energy Equation โดย:
- `ddt(T)`: Unsteady term
- `div(phi, T)`: Convection term
- `laplacian(DT, T)`: Diffusion term
</details>
```

## Best Practices

1. **Focus on "Why":** อย่าถามแค่ "What" (คืออะไร) แต่ให้ถาม "Why" (ทำไม) หรือ "How" (อย่างไร)
2. **Contextual:** โยงเข้ากับ OpenFOAM เสมอ
3. **Constructive Feedback:** ในเฉลย ควรอธิบายเหตุผลระกอบ ไม่ใช่แค่บอกคำตอบ

## Trigger Examples

- "ออกข้อสอบเรื่อง Turbulence ให้หน่อย"
- "ขอโจทย์คำนวณ y+ 1 ข้อ"
- "เพิ่ม Concept Check ท้ายบทให้หน่อย"
